"""Module `render` — scripts/mindmap_render.py: dựng trang HTML hai lớp cho một feature.

Lớp nghiệp vụ đọc thẳng từ file `.md` (khuôn của tdq_mindmap.py). Lớp chi tiết đọc từ
`graph.json`: lần theo cạnh `calls`/`indirect_call` xuất phát từ node của mỗi bước, sắp
theo `source_location` tăng dần, gom các lời gọi trùng dòng vào một hàng, và lấy dòng đầu
docstring (đọc bằng `ast`) làm lời giải thích. Trang phải tự chứa hoàn toàn — không có
tham chiếu mạng nào lọt vào — vì đây là file tĩnh nằm luôn trong repo.
"""
import ast
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import mindmap_render  # noqa: E402 — đọc thẳng module đang kiểm, không chép lại logic vào test
import tdq_mindmap  # noqa: E402 — đọc thẳng hằng khuôn dùng chung

GRAPH_JSON = os.path.join(ROOT, "graphify-out", "graph.json")

DIAGRAM_HOP_LE = [
    "# Đăng nhập",
    "@nhánh: Xác thực > Đăng nhập",
    "",
    "B1 · Nhập email và mật khẩu (app/login.py::on_submit)",
]

DIAGRAM_THIEU_NHANH = [
    "# Đăng nhập",
    "",
    "B1 · Nhập email và mật khẩu (app/login.py::on_submit)",
]


def _graph(nodes, links):
    return {"nodes": nodes, "links": links}


def _node(node_id, source_file, line, label=None):
    return {
        "id": node_id, "file_type": "code",
        "source_file": source_file, "source_location": f"L{line}",
        "label": label or (node_id + "()"),
    }


def _call(source_id, target_id, line, relation="calls"):
    return {"relation": relation, "source": source_id, "target": target_id,
            "source_location": f"L{line}"}


class TestMotFeatureTuChoiSoDoSaiKhuon(unittest.TestCase):
    def test_mot_feature_tu_choi_so_do_sai_khuon(self):
        with self.assertRaises(mindmap_render.DiagramInvalid) as ctx:
            mindmap_render.render_feature_page(DIAGRAM_THIEU_NHANH, "sample.md")
        self.assertTrue(ctx.exception.violations)


class TestMotFeatureHaiLop(unittest.TestCase):
    def test_mot_feature_co_hai_lop_chuyen_duoc(self):
        html = mindmap_render.render_feature_page(DIAGRAM_HOP_LE, "sample.md")
        self.assertIn('id="lop-nghiep-vu"', html)
        self.assertIn('id="lop-chi-tiet"', html)
        self.assertIn("<button", html)
        # Lớp chi tiết ẩn mặc định, chỉ hiện khi bấm nút.
        self.assertRegex(html, r'id="lop-chi-tiet"[^>]*hidden')

    def test_mot_feature_canh_bao_thu_tu_viet(self):
        html = mindmap_render.render_feature_page(DIAGRAM_HOP_LE, "sample.md")
        detail = html.split('id="lop-chi-tiet"', 1)[1]
        self.assertIn("VIẾT", detail)
        self.assertIn("CHẠY", detail)
        # Câu cảnh báo phải nằm ngay đầu lớp chi tiết, trước bất kỳ figure nào.
        canh_bao_idx = detail.find("VIẾT")
        figure_idx = detail.find("<figure")
        self.assertTrue(figure_idx == -1 or canh_bao_idx < figure_idx)


class TestMotFeatureTuChua(unittest.TestCase):
    def test_mot_feature_tu_chua_khong_tham_chieu_ngoai(self):
        html = mindmap_render.render_feature_page(DIAGRAM_HOP_LE, "sample.md")
        self.assertNotIn("http://", html)
        self.assertNotIn("https://", html)
        self.assertIsNone(re.search(r'src="(?!data:)[^"]+"', html))

    def test_mot_feature_theme_du_ba_trang_thai(self):
        html = mindmap_render.render_feature_page(DIAGRAM_HOP_LE, "sample.md")
        self.assertRegex(html, r":root\s*{")
        self.assertIn('@media (prefers-color-scheme: dark)', html)
        self.assertIn(':root:not([data-theme="light"])', html)
        self.assertIn(':root[data-theme="dark"]', html)
        self.assertRegex(html, r"body\s*{[^}]*background:\s*var\(--")


class TestMotFeatureThuTuGomDong(unittest.TestCase):
    def test_mot_feature_thu_tu_calls_theo_source_location(self):
        graph = _graph(
            nodes=[
                _node("mod_runner", "mod.py", 1, "runner()"),
                _node("mod_z", "mod.py", 30, "z()"),
                _node("mod_w", "mod.py", 4, "w()"),
            ],
            # Cố tình khai lệch thứ tự: dòng 20 trước dòng 5.
            links=[
                _call("mod_runner", "mod_z", 20),
                _call("mod_runner", "mod_w", 5),
            ],
        )
        diagram = [
            "# Đăng nhập",
            "@nhánh: Xác thực > Đăng nhập",
            "",
            "B1 · Bước gọi (mod.py::runner)",
        ]
        html = mindmap_render.render_feature_page(diagram, "sample.md", graph=graph)
        detail = html.split('id="lop-chi-tiet"', 1)[1]
        self.assertLess(detail.find("w()"), detail.find("z()"),
                         "lời gọi dòng 5 (w) phải đứng trước dòng 20 (z)")

    def test_mot_feature_gom_dong_trung_line(self):
        graph = _graph(
            nodes=[
                _node("mod_runner", "mod.py", 1, "runner()"),
                _node("mod_x", "mod.py", 10, "x()"),
                _node("mod_y", "mod.py", 12, "y()"),
            ],
            links=[
                _call("mod_runner", "mod_x", 7),
                _call("mod_runner", "mod_y", 7),
            ],
        )
        diagram = [
            "# Đăng nhập",
            "@nhánh: Xác thực > Đăng nhập",
            "",
            "B1 · Bước gọi (mod.py::runner)",
        ]
        html = mindmap_render.render_feature_page(diagram, "sample.md", graph=graph)
        detail = html.split('id="lop-chi-tiet"', 1)[1]
        rows = re.findall(r"<li[^>]*>.*?</li>", detail, re.S)
        gop = [r for r in rows if "x()" in r and "y()" in r]
        self.assertTrue(gop, "x() và y() cùng dòng 7 phải gom vào một hàng <li>")


class TestMotFeatureDocstring(unittest.TestCase):
    def test_mot_feature_docstring_lam_giai_thich(self):
        with tempfile.TemporaryDirectory() as root:
            with open(os.path.join(root, "mod.py"), "w", encoding="utf-8") as f:
                f.write(
                    "def documented():\n"
                    '    """Kiem tra dau vao truoc khi gui di."""\n'
                    "    return 1\n"
                    "\n"
                    "\n"
                    "def undocumented():\n"
                    "    return 2\n"
                )
            graph = _graph(
                nodes=[
                    _node("mod_runner", "mod.py", 20, "runner()"),
                    _node("mod_documented", "mod.py", 1, "documented()"),
                    _node("mod_undocumented", "mod.py", 6, "undocumented()"),
                ],
                links=[
                    _call("mod_runner", "mod_documented", 21),
                    _call("mod_runner", "mod_undocumented", 22),
                ],
            )
            diagram = [
                "# Đăng nhập",
                "@nhánh: Xác thực > Đăng nhập",
                "",
                "B1 · Bước gọi (mod.py::runner)",
            ]
            html = mindmap_render.render_feature_page(
                diagram, "sample.md", graph=graph, project_root=root)
            detail = html.split('id="lop-chi-tiet"', 1)[1]
            self.assertIn("Kiem tra dau vao truoc khi gui di.", detail)
            # Hàm không docstring: chỉ tên trơ, có đánh dấu tô nhạt.
            m = re.search(r'<code[^>]*>undocumented\(\)</code>', detail)
            self.assertIsNotNone(m, detail)
            self.assertIn("dim", m.group(0))


class TestMotFeatureThuGon(unittest.TestCase):
    def test_mot_feature_qua_20_ham_thu_gon(self):
        n = 25
        nodes = [_node("mod_runner", "mod.py", 1, "runner()")]
        links = []
        for i in range(n):
            nodes.append(_node(f"mod_t{i}", "mod.py", 100 + i, f"t{i}()"))
            links.append(_call("mod_runner", f"mod_t{i}", i + 1))
        graph = _graph(nodes=nodes, links=links)
        diagram = [
            "# Đăng nhập",
            "@nhánh: Xác thực > Đăng nhập",
            "",
            "B1 · Bước gọi (mod.py::runner)",
        ]
        html = mindmap_render.render_feature_page(diagram, "sample.md", graph=graph)
        detail = html.split('id="lop-chi-tiet"', 1)[1]
        self.assertIn("<details", detail)
        self.assertNotRegex(detail, r"<details[^>]*\bopen\b")
        self.assertIn(str(n), detail)

    def test_mot_feature_duoi_20_khong_thu_gon(self):
        graph = _graph(
            nodes=[_node("mod_runner", "mod.py", 1, "runner()"),
                   _node("mod_t0", "mod.py", 10, "t0()")],
            links=[_call("mod_runner", "mod_t0", 2)],
        )
        diagram = [
            "# Đăng nhập",
            "@nhánh: Xác thực > Đăng nhập",
            "",
            "B1 · Bước gọi (mod.py::runner)",
        ]
        html = mindmap_render.render_feature_page(diagram, "sample.md", graph=graph)
        detail = html.split('id="lop-chi-tiet"', 1)[1]
        self.assertNotIn("<details", detail)


class TestMotFeatureDoSau(unittest.TestCase):
    def test_mot_feature_do_sau_mac_dinh_va_co_flag(self):
        graph = _graph(
            nodes=[
                _node("mod_a", "mod.py", 1, "a()"),
                _node("mod_b", "mod.py", 10, "b()"),
                _node("mod_c", "mod.py", 20, "c()"),
            ],
            links=[
                _call("mod_a", "mod_b", 2),
                _call("mod_b", "mod_c", 11),
            ],
        )
        diagram = [
            "# Đăng nhập",
            "@nhánh: Xác thực > Đăng nhập",
            "",
            "B1 · Bước gọi (mod.py::a)",
        ]
        html_sau1 = mindmap_render.render_feature_page(diagram, "sample.md", graph=graph)
        detail1 = html_sau1.split('id="lop-chi-tiet"', 1)[1]
        self.assertIn("b()", detail1)
        self.assertNotIn("c()", detail1, "mặc định sâu 1 tầng, không được thấy c()")

        html_sau2 = mindmap_render.render_feature_page(
            diagram, "sample.md", graph=graph, depth=2)
        detail2 = html_sau2.split('id="lop-chi-tiet"', 1)[1]
        self.assertIn("b()", detail2)
        self.assertIn("c()", detail2, "--sau 2 phải lần tới c()")


class TestMotFeatureSvg(unittest.TestCase):
    def test_mot_feature_dung_svg_co_mui_ten_nhan(self):
        graph = _graph(
            nodes=[_node("mod_runner", "mod.py", 1, "runner()"),
                   _node("mod_t0", "mod.py", 10, "t0()")],
            links=[_call("mod_runner", "mod_t0", 7)],
        )
        diagram = [
            "# Đăng nhập",
            "@nhánh: Xác thực > Đăng nhập",
            "",
            "B1 · Bước gọi (mod.py::runner)",
        ]
        html = mindmap_render.render_feature_page(diagram, "sample.md", graph=graph)
        detail = html.split('id="lop-chi-tiet"', 1)[1]
        self.assertIn("<svg", detail)
        self.assertIn('role="img"', detail)
        self.assertIn("aria-label=", detail)
        self.assertIn("marker-end", detail)
        self.assertIn("<figcaption>", detail)
        self.assertIn("L7", detail)

    def test_mot_feature_khong_tim_thay_trong_graph(self):
        graph = _graph(nodes=[], links=[])
        diagram = [
            "# Đăng nhập",
            "@nhánh: Xác thực > Đăng nhập",
            "",
            "B1 · Bước gọi (khong/co/that.py::khong_ton_tai)",
        ]
        html = mindmap_render.render_feature_page(diagram, "sample.md", graph=graph)
        detail = html.split('id="lop-chi-tiet"', 1)[1]
        self.assertNotIn("<figure", detail)


class TestMotFeatureKhongCoGraph(unittest.TestCase):
    def test_mot_feature_khong_co_graph_van_dung_duoc(self):
        html = mindmap_render.render_feature_page(DIAGRAM_HOP_LE, "sample.md", graph=None)
        self.assertIn('id="lop-chi-tiet"', html)


class TestMotFeatureSinhFileThat(unittest.TestCase):
    """Ra: mindmap_render.py sinh được docs/tdq/mind-map/dang-nhap.html thật trong repo."""

    def test_mot_feature_sinh_duoc_file_dang_nhap_html(self):
        noi_dung = "\n".join([
            "# Đăng nhập",
            "@nhánh: Xác thực > Đăng nhập",
            "",
            "B1 · Nhập email và mật khẩu (src/pages/login.tsx::LoginForm.onSubmit)",
            "B2 · Kiểm tra tại chỗ trước khi gửi (src/lib/validators.ts::validateCredentials)",
            "B2! · email sai khuôn hoặc mật khẩu ngắn thì báo lỗi tại ô nhập và dừng "
            "(src/lib/form-ui.ts::showFieldError)",
            "B3 · Gửi yêu cầu qua kênh mã hoá (src/api/auth.ts::authApi.login)",
            "B4 · Tra người dùng và đối chiếu băm mật khẩu "
            "(server/controllers/auth.py::AuthController.login)",
            "B4! · không có người dùng hoặc băm sai thì trả một lỗi chung "
            "(server/controllers/auth.py::deny_login)",
            "B5 · Phát token phiên và token làm mới "
            "(server/services/token.py::TokenService.issue_pair)",
            "B6 · Lưu token và vào màn hình chính (?)",
        ]) + "\n"
        with tempfile.TemporaryDirectory() as tmp:
            nguon = os.path.join(tmp, "dang-nhap.md")
            with open(nguon, "w", encoding="utf-8") as f:
                f.write(noi_dung)

            dich = os.path.join(ROOT, "docs", "tdq", "mind-map", "dang-nhap.html")
            code = mindmap_render.main([nguon, "--graph", GRAPH_JSON, "-o", dich])
            self.assertEqual(code, tdq_mindmap.EXIT_OK)
            self.assertTrue(os.path.exists(dich))
            with open(dich, encoding="utf-8") as f:
                html = f.read()
            self.assertIn("Đăng nhập", html)
            self.assertIn('id="lop-nghiep-vu"', html)
            self.assertIn('id="lop-chi-tiet"', html)
            self.assertNotIn("http://", html)
            self.assertNotIn("https://", html)


class TestTongCanhPhuThuocThat(unittest.TestCase):
    def test_tong_gom_hai_feature_va_ve_canh_that(self):
        features = {
            "dang-nhap": {
                "title": "Đăng nhập", "branch_top": "Tài khoản", "branch_sub": "Đăng nhập",
                "depends": [], "exists": True,
            },
            "mua-hang": {
                "title": "Mua hàng", "branch_top": "Thương mại", "branch_sub": "Mua hàng",
                "depends": [("dang-nhap", "cần token phiên do đăng nhập phát ra")],
                "exists": True,
            },
        }
        html = mindmap_render.render_total_page(features)
        self.assertIn("Đăng nhập", html)
        self.assertIn("Mua hàng", html)
        self.assertIn("cần token phiên do đăng nhập phát ra", html)
        self.assertIn("marker-end", html)
        self.assertIn('class="grid-wrap"', html)


class TestTongGomTheoNhanh(unittest.TestCase):
    """QC1.1 — DoD Q7: trang tổng phải GOM feature theo `@nhánh`, không chỉ liệt kê tên.

    Khẳng định cả ba mức: tên nhánh cha, tên nhánh con, và ô chứa của nhóm chưa
    gắn nhánh — feature thiếu `@nhánh` không được biến mất khỏi bản đồ tổng.
    """

    def test_tong_gom_theo_nhanh_cha_con_va_nhom_chua_gan(self):
        features = {
            "dang-nhap": {
                "title": "Đăng nhập", "branch_top": "Tài khoản", "branch_sub": "Xác thực",
                "depends": [], "exists": True,
            },
            "doi-mat-khau": {
                "title": "Đổi mật khẩu", "branch_top": "Tài khoản", "branch_sub": "Xác thực",
                "depends": [], "exists": True,
            },
            "mua-hang": {
                "title": "Mua hàng", "branch_top": "Thương mại", "branch_sub": "Mua hàng",
                "depends": [], "exists": True,
            },
            "cu-khong-nhanh": {
                "title": "Feature cũ", "branch_top": None, "branch_sub": None,
                "depends": [], "exists": True,
            },
        }
        page = mindmap_render.render_total_page(features)
        self.assertIn('class="cay-nhanh"', page)
        # Nhánh cha in đậm, mỗi tên đúng MỘT lần dù có hai feature cùng nhánh.
        self.assertIn("<strong>Tài khoản</strong>", page)
        self.assertIn("<strong>Thương mại</strong>", page)
        self.assertEqual(page.count("<strong>Tài khoản</strong>"), 1,
                         "hai feature cùng nhánh cha phải gom vào một ô, không lặp tên nhánh")
        # Nhánh con là một tầng riêng, và hai feature cùng nhánh con nằm chung ô đó.
        cha = page.split("<strong>Tài khoản</strong>", 1)[1]
        cha = cha.split("<strong>Thương mại</strong>", 1)[0]
        self.assertIn("Xác thực", cha)
        self.assertIn("Đăng nhập", cha)
        self.assertIn("Đổi mật khẩu", cha)
        self.assertNotIn("Mua hàng", cha, "feature nhánh khác không được lọt vào nhánh Tài khoản")
        # Feature không khai `@nhánh` vẫn hiện, trong nhóm chưa gắn nhánh.
        self.assertIn(mindmap_render.TEXT_TONG_CHUA_GAN_NHANH, page)
        chua_gan = page.split(mindmap_render.TEXT_TONG_CHUA_GAN_NHANH, 1)[1]
        self.assertIn("Feature cũ", chua_gan)


class TestTongTroHut(unittest.TestCase):
    def test_tong_feature_tro_toi_chua_co_file(self):
        features = {
            "mua-hang": {
                "title": "Mua hàng", "branch_top": "Thương mại", "branch_sub": "Mua hàng",
                "depends": [("khong-ton-tai", "phụ thuộc một feature chưa vẽ")],
                "exists": True,
            },
        }
        html = mindmap_render.render_total_page(features)
        self.assertIn("khong-ton-tai", html)
        self.assertIn("chưa có sơ đồ", html)
        self.assertIn("phụ thuộc một feature chưa vẽ", html)
        # Vẫn phải vẽ được cạnh thật cùng lúc — trỏ hụt không được làm rớt cạnh khác.
        self.assertIn("marker-end", html)


class TestTongTuChuaVaTheme(unittest.TestCase):
    def test_tong_tu_chua_va_theme_du_ba_trang_thai(self):
        features = {
            "dang-nhap": {
                "title": "Đăng nhập", "branch_top": "Tài khoản", "branch_sub": "Đăng nhập",
                "depends": [], "exists": True,
            },
        }
        html = mindmap_render.render_total_page(features)
        self.assertNotIn("http://", html)
        self.assertNotIn("https://", html)
        self.assertIsNone(re.search(r'src="(?!data:)[^"]+"', html))
        self.assertRegex(html, r":root\s*{")
        self.assertIn('@media (prefers-color-scheme: dark)', html)
        self.assertIn(':root:not([data-theme="light"])', html)
        self.assertIn(':root[data-theme="dark"]', html)
        self.assertRegex(html, r"body\s*{[^}]*background:\s*var\(--")
        self.assertIn("overflow-x: auto", html)


class TestTongDocTuThuMuc(unittest.TestCase):
    def test_tong_thu_thap_du_lieu_tu_thu_muc_that(self):
        with tempfile.TemporaryDirectory() as tmp:
            mind_map_dir = os.path.join(tmp, "docs", "tdq", "mind-map")
            os.makedirs(mind_map_dir)
            with open(os.path.join(mind_map_dir, "dang-nhap.md"), "w", encoding="utf-8") as f:
                f.write("\n".join(DIAGRAM_HOP_LE) + "\n")
            with open(os.path.join(mind_map_dir, "mua-hang.md"), "w", encoding="utf-8") as f:
                f.write("\n".join([
                    "# Mua hàng",
                    "@nhánh: Thương mại > Mua hàng",
                    "@phụ-thuộc: dang-nhap · cần token phiên do đăng nhập phát ra",
                    "",
                    "B1 · Đặt hàng (app/order.py::place)",
                ]) + "\n")
            features = mindmap_render.collect_total_data(root=tmp)
            self.assertEqual(set(features), {"dang-nhap", "mua-hang"})
            self.assertEqual(features["mua-hang"]["depends"],
                              [("dang-nhap", "cần token phiên do đăng nhập phát ra")])
            self.assertTrue(features["dang-nhap"]["exists"])


class TestTongSinhFileThat(unittest.TestCase):
    """Ra: mindmap_render.py sinh được docs/tdq/mind-map/index.html thật từ chính thư mục đó."""

    def test_tong_sinh_duoc_index_html_tu_thu_muc_that(self):
        with tempfile.TemporaryDirectory() as tmp:
            dich = os.path.join(tmp, "index.html")
            code = mindmap_render.main(["--tong", "-o", dich])
            self.assertEqual(code, tdq_mindmap.EXIT_OK)
            self.assertTrue(os.path.exists(dich))
            with open(dich, encoding="utf-8") as f:
                html = f.read()
            self.assertIn("Đăng nhập", html)
            self.assertIn("Mua hàng", html)
            self.assertIn("cần token phiên do đăng nhập phát ra", html)
            self.assertNotIn("http://", html)
            self.assertNotIn("https://", html)


RENDER = os.path.join(ROOT, "scripts", "mindmap_render.py")


def run_render(cwd, *args, env=None):
    """Chạy CLI với project = cwd; trả (mã thoát, stdout, stderr)."""
    full_env = dict(os.environ, TDQ_PROJECT_DIR=cwd, **(env or {}))
    proc = subprocess.run(
        [sys.executable, RENDER, *args],
        capture_output=True, text=True, env=full_env, timeout=30,
    )
    return proc.returncode, proc.stdout, proc.stderr


class TestRenderLogService(unittest.TestCase):
    """T4.1: cả hai chế độ CLI của mindmap_render.py (một feature và --tong) đều
    phải in log timestamp qua đúng log service của tdq_mindmap.py (import lại,
    không định nghĩa bản thứ hai) và tắt được qua cùng biến TDQ_LOG."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cwd = self.tmp.name
        self.path = os.path.join(self.cwd, "dang-nhap.md")
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("\n".join(DIAGRAM_HOP_LE) + "\n")

    def test_render_mot_feature_co_log_kem_timestamp(self):
        _, out, err = run_render(self.cwd, self.path)
        self.assertRegex(err, r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\] tdq_mindmap: ", out)

    def test_render_mot_feature_tat_log_qua_config(self):
        _, _, err = run_render(self.cwd, self.path, env={"TDQ_LOG": "0"})
        self.assertEqual(err.strip(), "", err)

    def test_render_tong_co_log_kem_timestamp(self):
        _, out, err = run_render(self.cwd, "--tong")
        self.assertRegex(err, r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\] tdq_mindmap: ", out)

    def test_render_tong_tat_log_qua_config(self):
        _, _, err = run_render(self.cwd, "--tong", env={"TDQ_LOG": "0"})
        self.assertEqual(err.strip(), "", err)


# ---------------------------------------------------------------- sơ đồ luồng
# P1 — tầng dựng mô hình luồng: từ danh sách Step phẳng ra node + cạnh, gom
# `B<n>` với `B<n>!` cùng số thành một cặp quyết định. Tầng này thuần dữ liệu:
# không được sinh một thẻ SVG/HTML nào.

THE_SVG_TAGS = ("<svg", "<rect", "<polygon", "<text", "<tspan", "<line",
                "<figure", "<marker", "<figcaption", "<a ")


def _steps(*dong):
    """Danh sách Step từ vài dòng sơ đồ — đi qua đúng parse_diagram thật."""
    lines = ["# Thử", "@nhánh: Nhóm > Con", ""] + list(dong)
    return mindmap_render.parse_diagram(lines)[4]


class TestFlowModelCapQuyetDinh(unittest.TestCase):
    """T1.1: `B<n>` có `B<n>!` đi kèm phải ra 1 node quyết định + 1 node nhánh lỗi
    + đúng 1 cạnh nhãn `lỗi` nối hai node đó."""

    def test_flow_model_gom_cap_quyet_dinh(self):
        steps = _steps(
            "B1 · Mở giỏ (a.py::mo)",
            "B2 · Đọc token (a.py::doc)",
            "B2! · không có token thì sang màn đăng nhập (a.py::day)",
            "B3 · Gửi đơn (a.py::gui)",
        )
        model = mindmap_render.build_flow_model(steps)
        vai = {n["id"]: n["role"] for n in model["nodes"]}
        self.assertEqual(len(model["nodes"]), 4)
        self.assertEqual(vai["b2"], mindmap_render.ROLE_QUYET_DINH)
        loi = [n for n in model["nodes"] if n["role"] == mindmap_render.ROLE_NHANH_LOI]
        self.assertEqual(len(loi), 1)
        canh_loi = [e for e in model["edges"] if e["kind"] == "loi"]
        self.assertEqual(len(canh_loi), 1)
        self.assertEqual(canh_loi[0]["from"], "b2")
        self.assertEqual(canh_loi[0]["to"], loi[0]["id"])
        self.assertEqual(canh_loi[0]["label"], mindmap_render.TEXT_CANH_LOI)

    def test_flow_model_nhan_ok_chi_khi_roi_node_quyet_dinh(self):
        steps = _steps(
            "B1 · Mở giỏ (a.py::mo)",
            "B2 · Đọc token (a.py::doc)",
            "B2! · không có token thì dừng (a.py::day)",
            "B3 · Gửi đơn (a.py::gui)",
        )
        model = mindmap_render.build_flow_model(steps)
        nhan = {(e["from"], e["to"]): e["label"]
                for e in model["edges"] if e["kind"] == "chinh"}
        self.assertEqual(nhan[("b1", "b2")], "")
        self.assertEqual(nhan[("b2", "b3")], mindmap_render.TEXT_CANH_OK)

    def test_flow_model_vai_vao_va_ra(self):
        steps = _steps(
            "B1 · Mở giỏ (a.py::mo)",
            "B2 · Đọc token (a.py::doc)",
            "B2! · không có token thì dừng (a.py::day)",
            "B3 · Gửi đơn (a.py::gui)",
        )
        model = mindmap_render.build_flow_model(steps)
        theo_id = {n["id"]: n for n in model["nodes"]}
        self.assertEqual(theo_id["b1"]["role"], mindmap_render.ROLE_VAO)
        self.assertEqual(theo_id["b3"]["role"], mindmap_render.ROLE_RA)
        # Node nhánh lỗi cũng là một điểm ra của luồng.
        loi = [n for n in model["nodes"] if n["role"] == mindmap_render.ROLE_NHANH_LOI]
        self.assertTrue(loi[0]["la_ra"])

    def test_flow_model_giu_nguyen_mo_ta_va_vi_tri(self):
        steps = _steps("B1 · Mở giỏ hàng ngay (a.py::mo)")
        model = mindmap_render.build_flow_model(steps)
        node = model["nodes"][0]
        self.assertEqual(node["desc"], "Mở giỏ hàng ngay")
        self.assertEqual(node["file"], "a.py")
        self.assertEqual(node["func"], "mo")

    def test_flow_model_du_lieu_thuan_khong_the_svg(self):
        """Tầng mô hình không được sinh thẻ SVG/HTML nào — kể cả khi mô tả của
        bước có chứa dấu `<` hợp lệ của tài liệu (ví dụ `B<n>`)."""
        steps = _steps("B1 · Gom B<n> với B<n>! cùng số (a.py::gom)")
        model = mindmap_render.build_flow_model(steps)
        phang = repr(model)
        for tag in THE_SVG_TAGS:
            self.assertNotIn(tag, phang)
        # …nhưng mô tả gốc phải còn nguyên từng ký tự.
        self.assertEqual(model["nodes"][0]["desc"], "Gom B<n> với B<n>! cùng số")


class TestFlowModelBien(unittest.TestCase):
    """T1.2: ba ca biên của tầng mô hình đều ra mô hình hợp lệ, không ngoại lệ."""

    def test_flow_model_bien_mot_buoc_khong_canh(self):
        model = mindmap_render.build_flow_model(_steps("B1 · Chỉ một bước (a.py::x)"))
        self.assertEqual(len(model["nodes"]), 1)
        self.assertEqual(model["edges"], [])
        # Một bước vừa là điểm vào vừa là điểm ra.
        self.assertTrue(model["nodes"][0]["la_vao"])
        self.assertTrue(model["nodes"][0]["la_ra"])

    def test_flow_model_bien_moi_buoc_deu_co_nhanh_loi(self):
        model = mindmap_render.build_flow_model(_steps(
            "B1 · Bước một (a.py::a)",
            "B1! · hỏng một (a.py::a2)",
            "B2 · Bước hai (a.py::b)",
            "B2! · hỏng hai (a.py::b2)",
        ))
        vai = [n["role"] for n in model["nodes"]]
        self.assertEqual(vai.count(mindmap_render.ROLE_QUYET_DINH), 2)
        self.assertEqual(vai.count(mindmap_render.ROLE_NHANH_LOI), 2)
        self.assertEqual(len([e for e in model["edges"] if e["kind"] == "loi"]), 2)

    def test_flow_model_bien_nhieu_nhanh_loi_cung_mot_so(self):
        model = mindmap_render.build_flow_model(_steps(
            "B1 · Bước một (a.py::a)",
            "B1! · hỏng kiểu một (a.py::a1)",
            "B1! · hỏng kiểu hai (a.py::a2)",
        ))
        loi = [n for n in model["nodes"] if n["role"] == mindmap_render.ROLE_NHANH_LOI]
        self.assertEqual(len(loi), 2)
        self.assertEqual(len({n["id"] for n in loi}), 2, "hai node nhánh lỗi phải khác id")
        self.assertEqual(len([e for e in model["edges"] if e["kind"] == "loi"]), 2)

    def test_flow_model_bien_khong_buoc_nao(self):
        model = mindmap_render.build_flow_model([])
        self.assertEqual(model["nodes"], [])
        self.assertEqual(model["edges"], [])

    def test_flow_model_bien_nhanh_loi_mo_coi(self):
        """`B<n>!` không có `B<n>` đi kèm (sơ đồ cũ) vẫn ra node, không ngoại lệ."""
        model = mindmap_render.build_flow_model(_steps("B1! · chỉ có nhánh lỗi (a.py::x)"))
        self.assertEqual(len(model["nodes"]), 1)
        self.assertEqual(model["nodes"][0]["role"], mindmap_render.ROLE_NHANH_LOI)


class TestWrapLabel(unittest.TestCase):
    """T2.1: ngắt mô tả theo ranh giới từ, KHÔNG cắt cụt một ký tự nào."""

    def test_wrap_label_khong_mat_ky_tu(self):
        text = "Dựng mô hình luồng gom bước thường với bước lỗi thành cặp quyết định"
        dong = mindmap_render.wrap_label(text, 20)
        self.assertEqual(" ".join(dong), text, "ghép lại phải ra đúng câu gốc")

    def test_wrap_label_moi_dong_khong_qua_gioi_han(self):
        text = "một hai ba bốn năm sáu bảy tám chín mười"
        for dong in mindmap_render.wrap_label(text, 12):
            self.assertLessEqual(len(dong), 12, dong)

    def test_wrap_label_tu_dai_hon_mot_dong_van_giu_nguyen(self):
        dai = "siêu-dài-không-có-khoảng-trắng-nào-cả"
        dong = mindmap_render.wrap_label(dai, 10)
        self.assertEqual(dong, [dai], "từ dài hơn dòng không được cắt cụt")

    def test_wrap_label_chuoi_rong(self):
        self.assertEqual(mindmap_render.wrap_label("", 10), [""])


class TestLayoutFlow(unittest.TestCase):
    """T2.2: mỗi node có x/y/w/h/lines, cao theo số dòng, nhánh lỗi sang cột phải."""

    def _layout(self, *dong):
        model = mindmap_render.build_flow_model(_steps(*dong))
        return model, mindmap_render.layout_flow(model)

    def test_layout_flow_du_toa_do_va_kich_thuoc(self):
        _model, bo_cuc = self._layout(
            "B1 · Mở giỏ (a.py::mo)",
            "B2 · Gửi đơn (a.py::gui)",
        )
        for node_id in ("b1", "b2"):
            o = bo_cuc["boxes"][node_id]
            for khoa in ("x", "y", "w", "h", "lines"):
                self.assertIn(khoa, o)
            self.assertGreater(o["w"], 0)
            self.assertGreater(o["h"], 0)
            self.assertTrue(o["lines"])
        self.assertGreater(bo_cuc["width"], 0)
        self.assertGreater(bo_cuc["height"], 0)

    def test_layout_flow_luong_chinh_mot_cot_doc(self):
        _model, bo_cuc = self._layout(
            "B1 · Mở giỏ (a.py::mo)",
            "B2 · Đọc token (a.py::doc)",
            "B3 · Gửi đơn (a.py::gui)",
        )
        b1, b2, b3 = (bo_cuc["boxes"][i] for i in ("b1", "b2", "b3"))
        self.assertEqual(b1["x"], b2["x"])
        self.assertEqual(b2["x"], b3["x"])
        self.assertLess(b1["y"], b2["y"])
        self.assertLess(b2["y"], b3["y"])

    def test_layout_flow_nhanh_loi_sang_phai_va_ngang_hang(self):
        model, bo_cuc = self._layout(
            "B1 · Mở giỏ (a.py::mo)",
            "B2 · Đọc token (a.py::doc)",
            "B2! · không có token thì dừng (a.py::day)",
            "B3 · Gửi đơn (a.py::gui)",
        )
        loi_id = [n["id"] for n in model["nodes"]
                  if n["role"] == mindmap_render.ROLE_NHANH_LOI][0]
        b2, loi = bo_cuc["boxes"]["b2"], bo_cuc["boxes"][loi_id]
        self.assertGreaterEqual(loi["x"], b2["x"] + b2["w"],
                                 "node nhánh lỗi phải nằm hẳn sang cột phải")
        # Ngang hàng: tâm dọc của hai hộp lệch nhau không quá nửa chiều cao hộp lỗi.
        tam_b2 = b2["y"] + b2["h"] / 2
        tam_loi = loi["y"] + loi["h"] / 2
        self.assertLessEqual(abs(tam_b2 - tam_loi), loi["h"] / 2 + 1)

    def test_layout_flow_mo_ta_dai_cho_hop_cao_hon(self):
        _m1, ngan = self._layout("B1 · Ngắn (a.py::x)")
        dai_text = ("Bước này có một mô tả rất dài, dài hơn hẳn một dòng, "
                    "để bắt buộc bộ ngắt dòng phải xuống nhiều dòng liên tiếp")
        _m2, dai = self._layout("B1 · {} (a.py::x)".format(dai_text))
        self.assertGreater(dai["boxes"]["b1"]["h"], ngan["boxes"]["b1"]["h"])
        self.assertGreater(len(dai["boxes"]["b1"]["lines"]),
                           len(ngan["boxes"]["b1"]["lines"]))

    def test_layout_flow_khong_buoc_nao(self):
        bo_cuc = mindmap_render.layout_flow({"nodes": [], "edges": []})
        self.assertEqual(bo_cuc["boxes"], {})
        self.assertGreaterEqual(bo_cuc["width"], 0)


def _giao_nhau(a, b):
    """Hai hình chữ nhật bao có giao nhau thật sự không (chạm cạnh thì không)."""
    return (a["x"] < b["x"] + b["w"] and b["x"] < a["x"] + a["w"]
            and a["y"] < b["y"] + b["h"] and b["y"] < a["y"] + a["h"])


class TestLayoutKhongChongLan(unittest.TestCase):
    """T2.3: khoá điều kiện bất biến — không cặp hộp nào chồng lấn, trên cả sơ đồ
    thật lẫn ba ca biên."""

    def _kiem(self, steps, ten):
        bo_cuc = mindmap_render.layout_flow(mindmap_render.build_flow_model(steps))
        hop = list(bo_cuc["boxes"].items())
        for i in range(len(hop)):
            for j in range(i + 1, len(hop)):
                self.assertFalse(
                    _giao_nhau(hop[i][1], hop[j][1]),
                    "{}: {} chồng lấn {}".format(ten, hop[i][0], hop[j][0]))

    def test_layout_khong_chong_lan_tren_so_do_that(self):
        thu_muc = os.path.join(ROOT, "docs", "tdq", "mind-map")
        files = [f for f in sorted(os.listdir(thu_muc)) if f.endswith(".md")]
        self.assertGreaterEqual(len(files), 5, "phải có ít nhất 5 sơ đồ thật để kiểm")
        for name in files:
            lines = tdq_mindmap.read_diagram(os.path.join(thu_muc, name))
            self._kiem(mindmap_render.parse_diagram(lines)[4], name)

    def test_layout_khong_chong_lan_ca_bien(self):
        self._kiem(_steps("B1 · Chỉ một bước (a.py::x)"), "một bước")
        self._kiem(_steps(
            "B1 · Bước một (a.py::a)",
            "B1! · hỏng một (a.py::a2)",
            "B2 · Bước hai (a.py::b)",
            "B2! · hỏng hai (a.py::b2)",
        ), "mọi bước đều có nhánh lỗi")
        hai_muoi_tu = " ".join("từ{}".format(i) for i in range(20))
        self._kiem(_steps(
            "B1 · {} (a.py::a)".format(hai_muoi_tu),
            "B1! · {} (a.py::a2)".format(hai_muoi_tu),
            "B2 · {} (a.py::b)".format(hai_muoi_tu),
        ), "mô tả 20 từ")


MA_MAU_CUNG = re.compile(r"(#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\()")


class TestSvgHelper(unittest.TestCase):
    """T3.1: bộ helper hình dạng dùng chung — chỉ `currentColor` và biến `--*`,
    không một mã màu cứng nào lọt vào hình."""

    def test_svg_helper_hop_bo_goc(self):
        ra = mindmap_render._svg_hop(1, 2, 30, 40)
        self.assertIn("<rect", ra)
        self.assertIn('x="1"', ra)
        self.assertIn('width="30"', ra)
        self.assertIn("rx=", ra)

    def test_svg_helper_hinh_thoi_bon_dinh(self):
        ra = mindmap_render._svg_hinh_thoi(0, 0, 100, 50)
        self.assertIn("<polygon", ra)
        diem = re.search(r'points="([^"]+)"', ra).group(1).split()
        self.assertEqual(len(diem), 4, "hình thoi phải đúng 4 đỉnh")
        self.assertIn("50,0", diem)     # đỉnh trên
        self.assertIn("100,25", diem)   # đỉnh phải
        self.assertIn("50,50", diem)    # đỉnh dưới
        self.assertIn("0,25", diem)     # đỉnh trái

    def test_svg_helper_vien_thuoc_bo_goc_bang_nua_chieu_cao(self):
        ra = mindmap_render._svg_vien_thuoc(0, 0, 100, 40)
        self.assertIn("<rect", ra)
        self.assertIn('rx="20', ra)

    def test_svg_helper_nhan_nhieu_dong_moi_dong_mot_tspan(self):
        ra = mindmap_render._svg_nhan_nhieu_dong(50, 20, ["một", "hai", "ba"])
        self.assertEqual(ra.count("<tspan"), 3)
        self.assertIn("một", ra)
        self.assertIn("ba", ra)

    def test_svg_helper_nhan_thoat_ky_tu_html(self):
        ra = mindmap_render._svg_nhan_nhieu_dong(0, 0, ["gom B<n> & B<n>!"])
        self.assertIn("B&lt;n&gt;", ra)
        self.assertIn("&amp;", ra)

    def test_svg_helper_mui_ten_co_marker_va_nhan(self):
        ra = mindmap_render._svg_mui_ten(0, 0, 0, 40, "mid1", label="ok")
        self.assertIn("<line", ra)
        self.assertIn("marker-end=\"url(#mid1)\"", ra)
        self.assertIn(">ok<", ra)

    def test_svg_helper_khong_ma_mau_cung(self):
        ra = "".join([
            mindmap_render._svg_hop(0, 0, 10, 10),
            mindmap_render._svg_hinh_thoi(0, 0, 10, 10),
            mindmap_render._svg_vien_thuoc(0, 0, 10, 10),
            mindmap_render._svg_nhan_nhieu_dong(0, 0, ["x"]),
            mindmap_render._svg_mui_ten(0, 0, 0, 1, "m", label="ok"),
        ])
        self.assertIsNone(MA_MAU_CUNG.search(ra), ra)


class TestRenderFlowSvg(unittest.TestCase):
    """T3.2: sơ đồ luồng — đúng hình dạng theo vai, đủ cơ chế SVG chuẩn, và
    không mất một ký tự nào của mô tả."""

    def _ve(self, *dong):
        model = mindmap_render.build_flow_model(_steps(*dong))
        return mindmap_render.render_flow_svg(model, mindmap_render.layout_flow(model))

    def test_render_flow_svg_du_co_che_chuan(self):
        svg = self._ve(
            "B1 · Mở giỏ (a.py::mo)",
            "B2 · Gửi đơn (a.py::gui)",
        )
        self.assertIn("<figure", svg)
        self.assertIn("<svg", svg)
        self.assertRegex(svg, r'viewBox="0 0 \d+ \d+"')
        self.assertIn('role="img"', svg)
        self.assertIn("aria-label=", svg)
        self.assertIn("<marker", svg)
        self.assertIn("marker-end", svg)
        self.assertIn("<figcaption>", svg)

    def test_render_flow_svg_hinh_dang_theo_vai(self):
        svg = self._ve(
            "B1 · Mở giỏ (a.py::mo)",
            "B2 · Có token không (a.py::doc)",
            "B2! · không có token thì dừng (a.py::day)",
            "B3 · Gửi đơn (a.py::gui)",
        )
        # Bước có nhánh lỗi -> hình thoi; bước thường và nhánh lỗi -> hộp.
        self.assertIn("<polygon", svg)
        self.assertEqual(svg.count("<polygon"), 1)
        self.assertIn("<rect", svg)

    def test_render_flow_svg_diem_vao_ra_la_vien_thuoc(self):
        svg = self._ve(
            "B1 · Mở giỏ (a.py::mo)",
            "B2 · Bước giữa (a.py::giua)",
            "B3 · Gửi đơn (a.py::gui)",
        )
        rx = re.findall(r'<rect[^>]*rx="([\d.]+)"', svg)
        self.assertIn("21.0", [str(float(v)) for v in rx],
                      "điểm vào/ra phải bo góc bằng nửa chiều cao (viên thuốc)")

    def test_render_flow_svg_nhan_canh_ok_va_loi(self):
        svg = self._ve(
            "B1 · Mở giỏ (a.py::mo)",
            "B2 · Có token không (a.py::doc)",
            "B2! · không có token thì dừng (a.py::day)",
            "B3 · Gửi đơn (a.py::gui)",
        )
        self.assertIn(">ok<", svg)
        self.assertIn(">lỗi<", svg)

    def test_render_flow_svg_khong_mat_ky_tu_mo_ta(self):
        mo_ta = ("Bước này mang một mô tả rất dài để chắc chắn bộ ngắt dòng phải "
                 "xuống dòng nhiều lần mà vẫn giữ đủ từng chữ một")
        svg = self._ve("B1 · {} (a.py::x)".format(mo_ta))
        chu_trong_svg = " ".join(re.findall(r"<tspan[^>]*>([^<]*)</tspan>", svg))
        for tu in mo_ta.split():
            self.assertIn(tu, chu_trong_svg, "mất từ: " + tu)

    def test_render_flow_svg_khong_ma_mau_cung(self):
        svg = self._ve(
            "B1 · Mở giỏ (a.py::mo)",
            "B1! · hỏng thì dừng (a.py::x)",
        )
        self.assertIsNone(MA_MAU_CUNG.search(svg), svg)

    def test_render_flow_svg_so_do_rong(self):
        svg = mindmap_render.render_flow_svg({"nodes": [], "edges": []},
                                             mindmap_render.layout_flow(
                                                 {"nodes": [], "edges": []}))
        self.assertEqual(svg, "", "sơ đồ không bước nào thì không vẽ hình")


class TestBusinessLayer(unittest.TestCase):
    """T3.3: sơ đồ đứng TRƯỚC danh sách bước, danh sách và khối phụ thuộc giữ nguyên."""

    DIAGRAM = [
        "# Mua hàng",
        "@nhánh: Thương mại > Mua hàng",
        "@phụ-thuộc: dang-nhap · cần token phiên do đăng nhập phát ra",
        "",
        "B1 · Bấm đặt hàng (a.py::mo)",
        "B2 · Đọc token phiên (a.py::doc)",
        "B2! · không có token thì sang màn đăng nhập (a.py::day)",
        "B3 · Gửi đơn (a.py::gui)",
    ]

    def test_business_layer_so_do_dung_truoc_danh_sach(self):
        html = mindmap_render.render_feature_page(self.DIAGRAM, "sample.md")
        nghiep_vu = html.split('id="lop-nghiep-vu"', 1)[1].split('id="lop-chi-tiet"', 1)[0]
        self.assertIn("<figure", nghiep_vu)
        self.assertIn('<ol class="steps">', nghiep_vu)
        self.assertLess(nghiep_vu.find("<figure"), nghiep_vu.find('<ol class="steps">'),
                        "sơ đồ phải nằm trên danh sách bước")

    def test_business_layer_giu_nguyen_danh_sach_va_phu_thuoc(self):
        html = mindmap_render.render_feature_page(self.DIAGRAM, "sample.md")
        nghiep_vu = html.split('id="lop-nghiep-vu"', 1)[1].split('id="lop-chi-tiet"', 1)[0]
        danh_sach = nghiep_vu.split('<ol class="steps">', 1)[1]
        for mo_ta in ("Bấm đặt hàng", "Đọc token phiên",
                      "không có token thì sang màn đăng nhập", "Gửi đơn"):
            self.assertIn(mo_ta, danh_sach)
        self.assertIn("nhánh lỗi", danh_sach)
        self.assertIn("cần token phiên do đăng nhập phát ra", nghiep_vu)

    def test_business_layer_co_khoi_cuon_ngang(self):
        html = mindmap_render.render_feature_page(self.DIAGRAM, "sample.md")
        self.assertIn("overflow-x: auto", html)
        self.assertIn("max-width: 100%", html)

    def test_business_layer_van_tu_chua(self):
        html = mindmap_render.render_feature_page(self.DIAGRAM, "sample.md")
        self.assertNotIn("http://", html)
        self.assertNotIn("https://", html)
        self.assertIsNone(re.search(r'<script\s+src=', html))
        self.assertIsNone(re.search(r'<link\s+href=', html))


def _features(*rows):
    """`(slug, top, sub, exists)` rows → the shape collect_total_data returns."""
    out = {}
    for slug, top, sub, exists in rows:
        out[slug] = {"title": slug.replace("-", " "), "branch_top": top,
                     "branch_sub": sub, "depends": [], "exists": exists}
    return out


class TestBranchModel(unittest.TestCase):
    """T4.1: cây nhánh tổng → nhánh con → feature ra node/cạnh thuần."""

    FEATURES = _features(
        ("mua-hang", "Thương mại", "Mua hàng", True),
        ("dang-nhap", "Thương mại", "Phiên", True),
        ("bao-cao", "Vận hành", "Báo cáo", True),
    )

    def test_branch_model_ba_tang_node(self):
        model = mindmap_render.build_branch_model(self.FEATURES)
        theo_tang = {}
        for node in model["nodes"]:
            theo_tang.setdefault(node["kind"], []).append(node["label"])
        self.assertEqual(sorted(theo_tang["nhanh-tong"]), ["Thương mại", "Vận hành"])
        self.assertEqual(sorted(theo_tang["nhanh-con"]), ["Báo cáo", "Mua hàng", "Phiên"])
        self.assertEqual(len(theo_tang["feature"]), 3)

    def test_branch_model_canh_noi_dung_tang(self):
        model = mindmap_render.build_branch_model(self.FEATURES)
        by_id = {n["id"]: n for n in model["nodes"]}
        cap = {(by_id[e["from"]]["label"], by_id[e["to"]]["label"]) for e in model["edges"]}
        self.assertIn(("Thương mại", "Mua hàng"), cap)
        self.assertIn(("Thương mại", "Phiên"), cap)
        self.assertIn(("Vận hành", "Báo cáo"), cap)
        self.assertIn(("Mua hàng", "mua hang"), cap)
        # mỗi node trừ node gốc có đúng một cạnh vào
        vao = [e["to"] for e in model["edges"]]
        self.assertEqual(len(vao), len(set(vao)))

    def test_branch_model_feature_co_href(self):
        model = mindmap_render.build_branch_model(self.FEATURES)
        for node in model["nodes"]:
            if node["kind"] == "feature":
                self.assertEqual(node["href"], node["slug"] + ".html")
                self.assertFalse(node["thieu_file"])
            else:
                self.assertIsNone(node["href"])

    def test_branch_model_thieu_file_khong_href(self):
        features = dict(self.FEATURES)
        features.update(_features(("chua-ve", None, None, False)))
        model = mindmap_render.build_branch_model(features)
        thieu = [n for n in model["nodes"] if n.get("slug") == "chua-ve"]
        self.assertEqual(len(thieu), 1)
        self.assertTrue(thieu[0]["thieu_file"])
        self.assertIsNone(thieu[0]["href"])

    def test_branch_model_chua_gan_nhanh_vao_mot_ro(self):
        features = _features(("le-loi", None, None, True))
        model = mindmap_render.build_branch_model(features)
        tong = [n for n in model["nodes"] if n["kind"] == "nhanh-tong"]
        self.assertEqual(len(tong), 1)
        self.assertEqual(tong[0]["label"], mindmap_render.TEXT_TONG_CHUA_GAN_NHANH)
        self.assertTrue(any(n["kind"] == "feature" for n in model["nodes"]))

    def test_branch_model_rong_tra_ve_rong(self):
        model = mindmap_render.build_branch_model({})
        self.assertEqual(model["nodes"], [])
        self.assertEqual(model["edges"], [])


class TestCayNhanhSvg(unittest.TestCase):
    """T4.2: cây nhánh vẽ thành SVG, ô feature bọc link, ô thiếu file nét đứt."""

    FEATURES = _features(
        ("mua-hang", "Thương mại", "Mua hàng", True),
        ("dang-nhap", "Thương mại", "Phiên", True),
        ("bao-cao", "Vận hành", "Báo cáo rất dài để chắc chắn phải ngắt dòng", True),
    )

    def _svg(self, features):
        model = mindmap_render.build_branch_model(features)
        return model, mindmap_render.render_branch_svg(
            model, mindmap_render.layout_branch_tree(model))

    def test_cay_nhanh_svg_moi_feature_boc_link(self):
        _model, svg = self._svg(self.FEATURES)
        for slug in ("mua-hang", "dang-nhap", "bao-cao"):
            self.assertIn('<a href="{}.html"'.format(slug), svg)

    def test_cay_nhanh_svg_thieu_file_net_dut_khong_link(self):
        features = dict(self.FEATURES)
        features.update(_features(("chua-ve", None, None, False)))
        _model, svg = self._svg(features)
        self.assertNotIn('<a href="chua-ve.html"', svg)
        self.assertIn("stroke-dasharray", svg)
        self.assertIn("dim", svg)

    def test_cay_nhanh_svg_du_chu_khong_cat_cut(self):
        _model, svg = self._svg(self.FEATURES)
        chu = re.sub(r"<[^>]+>", " ", svg)
        for tu in "Báo cáo rất dài để chắc chắn phải ngắt dòng".split():
            self.assertIn(tu, chu)
        for nhan in ("Thương", "Vận", "hành", "Phiên"):
            self.assertIn(nhan, chu)

    def test_cay_nhanh_svg_khong_chong_lan(self):
        model = mindmap_render.build_branch_model(self.FEATURES)
        layout = mindmap_render.layout_branch_tree(model)
        hop = list(layout["boxes"].values())
        for i in range(len(hop)):
            for j in range(i + 1, len(hop)):
                a, b = hop[i], hop[j]
                self.assertFalse(_giao_nhau(a, b),
                                 "hai ô chồng lên nhau: {} và {}".format(a, b))

    def test_cay_nhanh_svg_khong_ma_mau_cung(self):
        _model, svg = self._svg(self.FEATURES)
        self.assertIsNone(MA_MAU_CUNG.search(svg), "SVG không được chứa mã màu cứng")

    def test_cay_nhanh_svg_rong_tra_ve_rong(self):
        model = mindmap_render.build_branch_model({})
        self.assertEqual(
            mindmap_render.render_branch_svg(model, mindmap_render.layout_branch_tree(model)), "")

    def test_cay_nhanh_svg_danh_sach_link_cu_nam_duoi_so_do(self):
        html = mindmap_render.render_total_page(self.FEATURES)
        khoi = html.split('id="cay-nhanh"', 1)[1].split('id="luoi-phu-thuoc"', 1)[0]
        self.assertIn("<figure", khoi)
        self.assertIn('<ul class="cay-nhanh">', khoi)
        self.assertLess(khoi.find("<figure"), khoi.find('<ul class="cay-nhanh">'),
                        "sơ đồ phải đứng trên danh sách link cũ")
        for slug in ("mua-hang", "dang-nhap", "bao-cao"):
            self.assertIn('href="{}.html"'.format(slug), khoi)


class TestLuoiPhuThuoc(unittest.TestCase):
    """T4.3: lưới phụ thuộc dùng chung helper, không cắt cụt nhãn."""

    SLUG_DAI = "mot-feature-co-ten-rat-dai-de-kiem-tra-viec-cat-cut-nhan"

    def _features(self):
        features = _features(
            ("mua-hang", "Thương mại", "Mua hàng", True),
            (self.SLUG_DAI, "Thương mại", "Dài", True),
        )
        features["mua-hang"]["depends"] = [(self.SLUG_DAI, "cần dữ liệu của nó")]
        return features

    def test_luoi_phu_thuoc_khong_cat_cut_nhan(self):
        html = mindmap_render.render_total_page(self._features())
        svg = html.split('class="grid-wrap"', 1)[1].split("</figure>", 1)[0]
        chu = re.sub(r"<[^>]+>", " ", svg)
        chu = " ".join(chu.split())
        for tu in self.SLUG_DAI.split("-"):
            self.assertIn(tu, chu)

    def test_luoi_phu_thuoc_du_o_va_du_canh(self):
        features = self._features()
        html = mindmap_render.render_total_page(features)
        svg = html.split('class="grid-wrap"', 1)[1].split("</figure>", 1)[0]
        self.assertEqual(svg.count("<rect"), len(features))
        self.assertEqual(svg.count("<line"), 1)

    def test_luoi_phu_thuoc_dung_helper_chung(self):
        html = mindmap_render.render_total_page(self._features())
        svg = html.split('class="grid-wrap"', 1)[1].split("</figure>", 1)[0]
        self.assertIn('rx="6"', svg)                 # _svg_hop
        self.assertIn("<tspan", svg)                 # _svg_nhan_nhieu_dong
        self.assertIn('marker-end="url(#mui-ten-', svg)
        self.assertIsNone(MA_MAU_CUNG.search(svg))

    def test_luoi_phu_thuoc_giu_danh_sach_canh(self):
        html = mindmap_render.render_total_page(self._features())
        self.assertIn("cần dữ liệu của nó", html)
        self.assertIn('<ul class="danh-sach-canh">', html)


class TestLogServiceSoDo(unittest.TestCase):
    """T5.1: mỗi lần dựng sơ đồ in một dòng stderr nêu số node và số cạnh."""

    SO_DEM = re.compile(r"(\d+) node, (\d+) canh")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cwd = self.tmp.name
        self.path = os.path.join(self.cwd, "dang-nhap.md")
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("\n".join(DIAGRAM_HOP_LE) + "\n")

    def test_log_service_trang_feature_neu_so_node_va_canh(self):
        _, _, err = run_render(self.cwd, self.path)
        khop = self.SO_DEM.search(err)
        self.assertIsNotNone(khop, err)
        self.assertGreater(int(khop.group(1)), 0)
        self.assertGreaterEqual(int(khop.group(2)), int(khop.group(1)) - 1)

    def test_log_service_trang_tong_neu_so_node_va_canh(self):
        _, _, err = run_render(self.cwd, "--tong")
        self.assertIsNotNone(self.SO_DEM.search(err), err)

    def test_log_service_tat_qua_bien_moi_truong(self):
        _, _, err = run_render(self.cwd, self.path, env={"TDQ_LOG": "0"})
        self.assertIsNone(self.SO_DEM.search(err), err)


class TestSoDoThat(unittest.TestCase):
    """T5.2: dựng lại mọi file sơ đồ thật và trang tổng — không mất bước nào,
    không cạnh phụ thuộc nào, không thẻ nào trỏ ra ngoài."""

    def _files(self):
        thu_muc = os.path.join(ROOT, "docs", "tdq", "mind-map")
        files = [f for f in sorted(os.listdir(thu_muc)) if f.endswith(".md")]
        self.assertGreaterEqual(len(files), 5, "phải có ít nhất 5 sơ đồ thật để kiểm")
        return thu_muc, files

    def test_so_do_that_moi_buoc_con_trong_trang(self):
        thu_muc, files = self._files()
        for name in files:
            with self.subTest(file=name):
                lines = tdq_mindmap.read_diagram(os.path.join(thu_muc, name))
                steps = mindmap_render.parse_diagram(lines)[4]
                trang = mindmap_render.render_feature_page(lines, os.path.join(thu_muc, name))
                so_do = trang.split('id="lop-nghiep-vu"', 1)[1].split("</figure>", 1)[0]
                chu = " ".join(re.sub(r"<[^>]+>", " ", so_do).split())
                for step in steps:
                    for tu in step.desc.split():
                        self.assertIn(html.unescape(tu), html.unescape(chu),
                                      "mất chữ {!r} của bước B{}".format(tu, step.num))

    def test_so_do_that_khong_the_tro_ra_ngoai(self):
        thu_muc, files = self._files()
        trang_tong = mindmap_render.render_total_page(
            mindmap_render.collect_total_data(ROOT))
        for name in files:
            lines = tdq_mindmap.read_diagram(os.path.join(thu_muc, name))
            trang_tong += mindmap_render.render_feature_page(
                lines, os.path.join(thu_muc, name))
        self.assertIsNone(re.search(r"<script\s+src=", trang_tong))
        self.assertIsNone(re.search(r"<link\s+href=", trang_tong))
        self.assertNotIn("http://", trang_tong)
        self.assertNotIn("https://", trang_tong)

    def test_so_do_that_trang_tong_du_canh_phu_thuoc(self):
        features = mindmap_render.collect_total_data(ROOT)
        trang = mindmap_render.render_total_page(features)
        for slug, info in features.items():
            for dep, reason in info["depends"]:
                self.assertIn(html.escape(reason), trang,
                              "mất lý do phụ thuộc {} → {}".format(slug, dep))

    def test_so_do_that_cli_exit_0(self):
        thu_muc, files = self._files()
        with tempfile.TemporaryDirectory() as tmp:
            dich = os.path.join(tmp, "docs", "tdq", "mind-map")
            os.makedirs(dich)
            for name in files:
                shutil.copy(os.path.join(thu_muc, name), os.path.join(dich, name))
            for name in files:
                code, _out, err = run_render(tmp, os.path.join(dich, name))
                self.assertEqual(code, 0, err)
            code, _out, err = run_render(tmp, "--tong")
            self.assertEqual(code, 0, err)


if __name__ == "__main__":
    unittest.main()
