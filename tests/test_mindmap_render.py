"""Module `render` — scripts/mindmap_render.py: dựng trang HTML hai lớp cho một feature.

Lớp nghiệp vụ đọc thẳng từ file `.md` (khuôn của tdq_mindmap.py). Lớp chi tiết đọc từ
`graph.json`: lần theo cạnh `calls`/`indirect_call` xuất phát từ node của mỗi bước, sắp
theo `source_location` tăng dần, gom các lời gọi trùng dòng vào một hàng, và lấy dòng đầu
docstring (đọc bằng `ast`) làm lời giải thích. Trang phải tự chứa hoàn toàn — không có
tham chiếu mạng nào lọt vào — vì đây là file tĩnh nằm luôn trong repo.
"""
import ast
import os
import re
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


if __name__ == "__main__":
    unittest.main()
