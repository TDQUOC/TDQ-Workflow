"""Module `nhan-doc` — scripts/tdq_mindmap.py: khung CLI, lệnh `sinh`, lệnh `kiem`.

Sơ đồ là DÀN Ý bắt buộc của mỗi feature, nên chính cái sinh ra nó phải được kiểm:
tạo mới thì đúng khuôn hằng, feature đã có thì TUYỆT ĐỐI không ghi đè (mất bản
sống của feature là mất nguồn sự thật), slug sai khuôn thì chặn ngay ở cổng vào.

Lệnh `kiem` là cái gác khuôn: mỗi loại sai một mã luật riêng, in ra theo khuôn
`<file>:<dòng>: [<mã>] <thông điệp>` giống `doc_lint.py`, và phần kiểm tách thành
một hàm thuần để T2.6 (luật lint) gọi lại thay vì chạy lại CLI.
"""
import os
import re
import subprocess
import sys
import tempfile
import unittest

from helper import ROOT

MINDMAP = os.path.join(ROOT, "scripts", "tdq_mindmap.py")

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tdq_mindmap  # noqa: E402  — đọc thẳng hằng khuôn, không chép lại vào test


def run_mindmap(cwd, *args, env=None):
    """Chạy CLI với project = cwd; trả (mã thoát, stdout, stderr)."""
    full_env = dict(os.environ, TDQ_PROJECT_DIR=cwd, **(env or {}))
    proc = subprocess.run(
        [sys.executable, MINDMAP, *args],
        capture_output=True, text=True, env=full_env, timeout=30,
    )
    return proc.returncode, proc.stdout, proc.stderr


class SinhBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cwd = self.tmp.name

    def duong_dan(self, feature):
        return os.path.join(self.cwd, tdq_mindmap.MIND_MAP_DIR_REL, feature + ".md")

    def dat_san(self, feature, noi_dung):
        path = self.duong_dan(feature)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(noi_dung)
        return path


class TestSinhTaoMoi(SinhBase):
    def test_sinh_feature_moi_tra_0_va_tao_file(self):
        code, out, err = run_mindmap(self.cwd, "sinh", "dang-nhap")
        self.assertEqual(code, tdq_mindmap.EXIT_OK, f"stdout={out}\nstderr={err}")
        self.assertTrue(os.path.exists(self.duong_dan("dang-nhap")), out)

    def test_sinh_file_moi_dung_hang_khuon(self):
        run_mindmap(self.cwd, "sinh", "dang-nhap")
        with open(self.duong_dan("dang-nhap"), encoding="utf-8") as f:
            dong = f.read().splitlines()
        self.assertTrue(dong[0].startswith(tdq_mindmap.TITLE_PREFIX), dong[0])
        self.assertTrue(any(tdq_mindmap.BRANCH_LINE_RE.match(d) for d in dong),
                        "thiếu dòng @nhánh trong file vừa sinh")
        self.assertTrue(any(tdq_mindmap.STEP_LINE_RE.match(d) for d in dong),
                        "thiếu dòng bước mẫu trong file vừa sinh")

    def test_sinh_in_duong_dan_file_vua_tao(self):
        code, out, _ = run_mindmap(self.cwd, "sinh", "mua-hang")
        self.assertEqual(code, tdq_mindmap.EXIT_OK, out)
        self.assertIn(os.path.join(tdq_mindmap.MIND_MAP_DIR_REL, "mua-hang.md"), out)


class TestSinhSlugSai(SinhBase):
    def test_sinh_slug_sai_khuon_tra_2(self):
        for slug in ("Dang-Nhap", "dang_nhap", "đăng-nhập", "-dang-nhap",
                     "dang--nhap", "dang-nhap-", "dang nhap", "", "../thoat"):
            with self.subTest(slug=slug):
                code, _, _ = run_mindmap(self.cwd, "sinh", slug)
                self.assertEqual(code, tdq_mindmap.EXIT_SYNTAX, f"slug {slug!r} lọt lưới")

    def test_sinh_slug_sai_khong_tao_file_nao(self):
        run_mindmap(self.cwd, "sinh", "Dang_Nhap")
        thu_muc = os.path.join(self.cwd, tdq_mindmap.MIND_MAP_DIR_REL)
        self.assertFalse(os.path.isdir(thu_muc) and os.listdir(thu_muc),
                         "slug sai mà vẫn ghi file")

    def test_sinh_slug_hop_le_qua_duoc_cong(self):
        for slug in ("dang-nhap", "a", "a1", "mua-hang-nhanh", "v2-thanh-toan"):
            with self.subTest(slug=slug):
                self.assertIsNotNone(tdq_mindmap.SLUG_RE.match(slug))


class TestSinhCapNhat(SinhBase):
    NOI_DUNG_CU = ("# Đăng nhập\n"
                   "@nhánh: Tài khoản > Đăng nhập\n"
                   "B1 · Nhập email và mật khẩu (src/login.tsx::LoginForm.onSubmit)\n")

    def test_sinh_feature_da_co_tra_3(self):
        self.dat_san("dang-nhap", self.NOI_DUNG_CU)
        code, out, _ = run_mindmap(self.cwd, "sinh", "dang-nhap")
        self.assertEqual(code, tdq_mindmap.EXIT_UPDATE, out)

    def test_sinh_feature_da_co_khong_ghi_de(self):
        path = self.dat_san("dang-nhap", self.NOI_DUNG_CU)
        run_mindmap(self.cwd, "sinh", "dang-nhap")
        with open(path, encoding="utf-8") as f:
            self.assertEqual(f.read(), self.NOI_DUNG_CU, "nội dung cũ bị ghi đè")

    def test_sinh_feature_da_co_in_noi_dung_hien_tai(self):
        self.dat_san("dang-nhap", self.NOI_DUNG_CU)
        _, out, _ = run_mindmap(self.cwd, "sinh", "dang-nhap")
        for dong in self.NOI_DUNG_CU.splitlines():
            self.assertIn(dong, out, "thiếu dòng nội dung hiện tại trên stdout")

    def test_sinh_feature_da_co_in_khuon_cau_trinh_cap_nhat(self):
        self.dat_san("dang-nhap", self.NOI_DUNG_CU)
        _, out, _ = run_mindmap(self.cwd, "sinh", "dang-nhap")
        self.assertIn(tdq_mindmap.UPDATE_PREFACE.format(feature="dang-nhap"), out)


class TestSinhLogService(SinhBase):
    def test_sinh_mac_dinh_co_log_kem_timestamp(self):
        _, _, err = run_mindmap(self.cwd, "sinh", "dang-nhap")
        self.assertRegex(err, r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\] tdq_mindmap: ")

    def test_sinh_tat_log_qua_config(self):
        _, _, err = run_mindmap(self.cwd, "sinh", "dang-nhap", env={"TDQ_LOG": "0"})
        self.assertEqual(err.strip(), "", err)


class TestSinhHangKhuonDungChung(unittest.TestCase):
    """Các task sau (kiem/doi-chieu/xem) import lại đúng những hằng này."""

    def test_sinh_hang_khuon_bat_duoc_dong_that(self):
        self.assertIsNotNone(tdq_mindmap.BRANCH_LINE_RE.match("@nhánh: Tài khoản > Đăng nhập"))
        self.assertIsNone(tdq_mindmap.BRANCH_LINE_RE.match("@nhánh: Tài khoản"))
        khai = tdq_mindmap.DEPENDS_LINE_RE.match(
            "@phụ-thuộc: dang-nhap · cần token phiên do đăng nhập phát ra")
        self.assertEqual(khai.group("feature"), "dang-nhap")
        self.assertIn("token phiên", khai.group("reason"))
        self.assertIsNone(tdq_mindmap.DEPENDS_LINE_RE.match("@phụ-thuộc: dang-nhap"))

    def test_sinh_hang_khuon_doc_duoc_dong_buoc(self):
        buoc = tdq_mindmap.STEP_LINE_RE.match(
            "B4 · Tra người dùng (server/auth.py::AuthController.login)")
        self.assertEqual(buoc.group("num"), "4")
        self.assertEqual(buoc.group("error"), "")
        self.assertEqual(buoc.group("location"), "server/auth.py::AuthController.login")
        loi = tdq_mindmap.STEP_LINE_RE.match("B4! · băm sai thì trả lỗi chung (a.py::deny)")
        self.assertEqual(loi.group("error"), "!")
        chua_biet = tdq_mindmap.STEP_LINE_RE.match("B6 · Vào màn hình chính (?)")
        self.assertEqual(chua_biet.group("location"), tdq_mindmap.UNKNOWN_LOCATION)

    def test_sinh_hang_khuon_tach_duoc_vi_tri(self):
        vi_tri = tdq_mindmap.LOCATION_RE.match("server/auth.py::AuthController.login")
        self.assertEqual(vi_tri.group("file"), "server/auth.py")
        self.assertEqual(vi_tri.group("func"), "AuthController.login")

    def test_sinh_hang_ma_thoat_khong_dam_nhau(self):
        ma = (tdq_mindmap.EXIT_OK, tdq_mindmap.EXIT_VIOLATION,
              tdq_mindmap.EXIT_SYNTAX, tdq_mindmap.EXIT_UPDATE)
        self.assertEqual(ma, (0, 1, 2, 3))


SACH = ("# Đăng nhập\n"
        "@nhánh: Tài khoản > Đăng nhập\n"
        "@phụ-thuộc: mua-hang · giỏ hàng cần phiên do đăng nhập phát ra\n"
        "\n"
        "B1 · Nhập email và mật khẩu (src/login.tsx::LoginForm.onSubmit)\n"
        "B2 · Tra người dùng (server/auth.py::AuthController.login)\n"
        "B2! · Sai mật khẩu thì trả lỗi chung (server/auth.py::deny)\n"
        "B3 · Vào màn hình chính (?)\n")


class KiemBase(unittest.TestCase):
    """Mỗi ca ghi một file tạm rồi chạy `kiem` trên chính đường dẫn đó."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cwd = self.tmp.name

    def ghi(self, noi_dung, ten="so-do.md"):
        path = os.path.join(self.cwd, ten)
        with open(path, "w", encoding="utf-8") as f:
            f.write(noi_dung)
        return path

    def kiem(self, noi_dung, **kw):
        return run_mindmap(self.cwd, "kiem", self.ghi(noi_dung), **kw)

    def ma_luat(self, noi_dung):
        """Tập mã luật mà hàm thuần bắt được — không qua CLI, không qua stdout."""
        return {v.rule for v in tdq_mindmap.check_diagram(noi_dung.splitlines(), "x.md")}


class TestKiemFileSach(KiemBase):
    def test_kiem_file_dung_khuon_tra_0_va_khong_in_vi_pham(self):
        code, out, err = self.kiem(SACH)
        self.assertEqual(code, tdq_mindmap.EXIT_OK, f"stdout={out}\nstderr={err}")
        self.assertEqual(out.strip(), "", out)

    def test_kiem_file_vua_sinh_ra_thi_sach(self):
        run_mindmap(self.cwd, "sinh", "dang-nhap")
        moi = os.path.join(self.cwd, tdq_mindmap.MIND_MAP_DIR_REL, "dang-nhap.md")
        code, out, _ = run_mindmap(self.cwd, "kiem", moi)
        self.assertEqual(code, tdq_mindmap.EXIT_OK, out)


class TestKiemDongTieuDe(KiemBase):
    def test_kiem_thieu_dong_tieu_de_bao_ma_luat_rieng(self):
        thieu = SACH.replace("# Đăng nhập\n", "")
        code, out, _ = self.kiem(thieu)
        self.assertEqual(code, tdq_mindmap.EXIT_VIOLATION, out)
        self.assertIn(tdq_mindmap.RULE_TITLE_MISSING, out)

    def test_kiem_tieu_de_khong_o_dong_dau_van_bi_bat(self):
        self.assertIn(tdq_mindmap.RULE_TITLE_MISSING,
                      self.ma_luat("@nhánh: A > B\n# Đăng nhập\nB1 · x (?)\n"))


class TestKiemDongNhanh(KiemBase):
    def test_kiem_thieu_dong_nhanh_bao_ma_luat_rieng(self):
        thieu = SACH.replace("@nhánh: Tài khoản > Đăng nhập\n", "")
        code, out, _ = self.kiem(thieu)
        self.assertEqual(code, tdq_mindmap.EXIT_VIOLATION, out)
        self.assertIn(tdq_mindmap.RULE_BRANCH_MISSING, out)

    def test_kiem_hai_dong_nhanh_cung_la_vi_pham(self):
        hai = SACH.replace("@nhánh: Tài khoản > Đăng nhập\n",
                           "@nhánh: Tài khoản > Đăng nhập\n@nhánh: Tài khoản > Đăng ký\n")
        code, out, _ = self.kiem(hai)
        self.assertEqual(code, tdq_mindmap.EXIT_VIOLATION, out)
        self.assertIn(tdq_mindmap.RULE_BRANCH_DUPLICATE, out)

    def test_kiem_dong_nhanh_sai_cu_phap_bao_ma_khac_voi_thieu(self):
        sai = SACH.replace("@nhánh: Tài khoản > Đăng nhập\n", "@nhánh: Tài khoản\n")
        ma = self.ma_luat(sai)
        self.assertIn(tdq_mindmap.RULE_BRANCH_SYNTAX, ma)
        self.assertIn(tdq_mindmap.RULE_BRANCH_MISSING, ma)


class TestKiemDongPhuThuoc(KiemBase):
    DONG_CU = "@phụ-thuộc: mua-hang · giỏ hàng cần phiên do đăng nhập phát ra\n"

    def _thay(self, dong_moi):
        return SACH.replace(self.DONG_CU, dong_moi)

    def test_kiem_phu_thuoc_thieu_ten_feature_bi_bat(self):
        code, out, _ = self.kiem(self._thay("@phụ-thuộc: · cần token phiên\n"))
        self.assertEqual(code, tdq_mindmap.EXIT_VIOLATION, out)
        self.assertIn(tdq_mindmap.RULE_DEPENDS_SYNTAX, out)

    def test_kiem_phu_thuoc_thieu_dau_cham_giua_bi_bat(self):
        self.assertIn(tdq_mindmap.RULE_DEPENDS_SYNTAX,
                      self.ma_luat(self._thay("@phụ-thuộc: mua-hang cần token phiên\n")))

    def test_kiem_phu_thuoc_thieu_ly_do_sau_dau_cham_giua_bi_bat(self):
        self.assertIn(tdq_mindmap.RULE_DEPENDS_SYNTAX,
                      self.ma_luat(self._thay("@phụ-thuộc: mua-hang ·\n")))

    def test_kiem_phu_thuoc_dung_khuon_khong_bi_bat(self):
        self.assertNotIn(tdq_mindmap.RULE_DEPENDS_SYNTAX, self.ma_luat(SACH))

    def test_kiem_nhieu_dong_phu_thuoc_deu_hop_le(self):
        nhieu = self._thay(self.DONG_CU + "@phụ-thuộc: gio-hang · cần danh sách món\n")
        self.assertNotIn(tdq_mindmap.RULE_DEPENDS_SYNTAX, self.ma_luat(nhieu))


class TestKiemDongBuoc(KiemBase):
    def test_kiem_buoc_thieu_dau_cham_giua_bi_bat(self):
        sai = SACH.replace("B1 · Nhập email và mật khẩu (src/login.tsx::LoginForm.onSubmit)\n",
                           "B1 Nhập email và mật khẩu (src/login.tsx::LoginForm.onSubmit)\n")
        code, out, _ = self.kiem(sai)
        self.assertEqual(code, tdq_mindmap.EXIT_VIOLATION, out)
        self.assertIn(tdq_mindmap.RULE_STEP_SYNTAX, out)

    def test_kiem_buoc_thieu_vi_tri_bi_bat(self):
        self.assertIn(tdq_mindmap.RULE_STEP_SYNTAX,
                      self.ma_luat("# T\n@nhánh: A > B\nB1 · Nhập email\n"))

    def test_kiem_buoc_vi_tri_sai_khuon_bi_bat(self):
        self.assertIn(tdq_mindmap.RULE_STEP_SYNTAX,
                      self.ma_luat("# T\n@nhánh: A > B\nB1 · Nhập email (src/login.tsx)\n"))

    def test_kiem_buoc_vi_tri_chua_biet_thi_khong_bi_bat(self):
        self.assertNotIn(tdq_mindmap.RULE_STEP_SYNTAX,
                         self.ma_luat("# T\n@nhánh: A > B\nB1 · Nhập email (?)\n"))

    def test_kiem_nhanh_loi_dung_khuon_thi_khong_bi_bat(self):
        self.assertNotIn(tdq_mindmap.RULE_STEP_SYNTAX, self.ma_luat(SACH))


class TestKiemSoBuoc(KiemBase):
    def test_kiem_so_buoc_nhay_coc_bi_bat(self):
        code, out, _ = self.kiem("# T\n@nhánh: A > B\nB1 · x (?)\nB3 · y (?)\n")
        self.assertEqual(code, tdq_mindmap.EXIT_VIOLATION, out)
        self.assertIn(tdq_mindmap.RULE_STEP_ORDER, out)

    def test_kiem_so_buoc_lap_lai_bi_bat(self):
        self.assertIn(tdq_mindmap.RULE_STEP_ORDER,
                      self.ma_luat("# T\n@nhánh: A > B\nB1 · x (?)\nB1 · y (?)\n"))

    def test_kiem_nhanh_loi_khong_co_buoc_goc_bi_bat(self):
        self.assertIn(tdq_mindmap.RULE_STEP_ORDER,
                      self.ma_luat("# T\n@nhánh: A > B\nB1 · x (?)\nB7! · y (?)\n"))

    def test_kiem_so_buoc_lien_tuc_thi_sach(self):
        self.assertNotIn(tdq_mindmap.RULE_STEP_ORDER, self.ma_luat(SACH))


class TestKiemKhuonInVaMaThoat(KiemBase):
    def test_kiem_in_dung_khuon_file_dong_ma_luat(self):
        thieu = SACH.replace("@nhánh: Tài khoản > Đăng nhập\n", "@nhánh: Tài khoản\n")
        path = self.ghi(thieu)
        code, out, _ = run_mindmap(self.cwd, "kiem", path)
        self.assertEqual(code, tdq_mindmap.EXIT_VIOLATION, out)
        self.assertRegex(
            out,
            rf"(?m)^{re.escape(path)}:2: \[{tdq_mindmap.RULE_BRANCH_SYNTAX}\] \S",
            out)

    def test_kiem_in_moi_dong_vi_pham_mot_dong_rieng(self):
        xau = ("# T\n@nhánh: A\n@phụ-thuộc: mua-hang\nB1 · x (?)\nB3 · y (?)\n")
        _, out, _ = self.kiem(xau)
        dong = [d for d in out.splitlines() if d.strip()]
        self.assertGreaterEqual(len(dong), 4, out)
        for d in dong:
            self.assertRegex(d, r"^.+:\d+: \[[A-Z]+\d+\] ")

    def test_kiem_file_khong_doc_duoc_tra_2(self):
        code, _, _ = run_mindmap(self.cwd, "kiem", os.path.join(self.cwd, "khong-co.md"))
        self.assertEqual(code, tdq_mindmap.EXIT_SYNTAX)

    def test_kiem_thu_muc_cung_tra_2(self):
        code, _, _ = run_mindmap(self.cwd, "kiem", self.cwd)
        self.assertEqual(code, tdq_mindmap.EXIT_SYNTAX)


class TestKiemHamThuanChoT26(KiemBase):
    """T2.6 import thẳng hàm này; nó phải thuần: không in, không đọc file, không thoát."""

    def test_kiem_ham_thuan_tra_danh_sach_vi_pham_co_du_truong(self):
        vi_pham = tdq_mindmap.check_diagram("B1 · x (?)\n".splitlines(), "a/b.md")
        self.assertTrue(vi_pham)
        dau = vi_pham[0]
        self.assertEqual(dau.path, "a/b.md")
        self.assertIsInstance(dau.line, int)
        self.assertGreaterEqual(dau.line, 1)
        self.assertIn(dau.rule, tdq_mindmap.ALL_RULES)
        self.assertTrue(dau.message.strip())

    def test_kiem_ham_thuan_file_sach_tra_danh_sach_rong(self):
        self.assertEqual(tdq_mindmap.check_diagram(SACH.splitlines(), "a.md"), [])

    def test_kiem_ham_thuan_khong_in_gi_ra_stdout(self):
        from io import StringIO
        from contextlib import redirect_stdout, redirect_stderr
        ra, loi = StringIO(), StringIO()
        with redirect_stdout(ra), redirect_stderr(loi):
            tdq_mindmap.check_diagram("hỏng\n".splitlines(), "a.md")
        self.assertEqual((ra.getvalue(), loi.getvalue()), ("", ""))

    def test_kiem_vi_pham_in_ra_dung_khuon_doc_lint(self):
        vi_pham = tdq_mindmap.Violation("a/b.md", 7, tdq_mindmap.RULE_TITLE_MISSING, "thiếu")
        self.assertEqual(str(vi_pham), f"a/b.md:7: [{tdq_mindmap.RULE_TITLE_MISSING}] thiếu")

    def test_kiem_moi_ma_luat_deu_rieng_va_cung_tien_to(self):
        self.assertEqual(len(set(tdq_mindmap.ALL_RULES)), len(tdq_mindmap.ALL_RULES))
        for ma in tdq_mindmap.ALL_RULES:
            self.assertTrue(ma.startswith(tdq_mindmap.RULE_PREFIX), ma)


class TestKiemLogService(KiemBase):
    def test_kiem_mac_dinh_co_log_kem_timestamp(self):
        _, _, err = self.kiem(SACH)
        self.assertRegex(err, r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\] tdq_mindmap: ")

    def test_kiem_tat_log_qua_config(self):
        _, _, err = self.kiem(SACH, env={"TDQ_LOG": "0"})
        self.assertEqual(err.strip(), "", err)


# T1.4 — command `lien-he`: cross-check every depends line under one project's
# `docs/tdq/mind-map/` directory against the set of files that actually exist there.
# Fixtures below build feature lines from the shared constants (BRANCH_KEY,
# DEPENDS_KEY, FIELD_SEP, TITLE_PREFIX) instead of typing the Vietnamese keywords
# out — same source of truth as the CLI, and it keeps this new block plain ASCII.
class LienHeBase(unittest.TestCase):
    """Each case writes zero or more feature files, then runs `lien-he` on them."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cwd = self.tmp.name
        self.mindmap_dir = os.path.join(self.cwd, tdq_mindmap.MIND_MAP_DIR_REL)
        os.makedirs(self.mindmap_dir, exist_ok=True)

    def ghi_feature(self, feature, phu_thuoc=()):
        """Write one minimal, shape-valid diagram file for `feature`.

        `phu_thuoc`: an iterable of feature slugs this one depends on — each becomes
        its own depends line, built from the shared constants.
        """
        dong = [
            f"{tdq_mindmap.TITLE_PREFIX}{feature}",
            f"{tdq_mindmap.BRANCH_KEY}: top > sub",
        ]
        for dep in phu_thuoc:
            dong.append(f"{tdq_mindmap.DEPENDS_KEY}: {dep} {tdq_mindmap.FIELD_SEP} "
                        f"needs something from {dep}")
        dong.append("B1 · first step (?)")
        path = os.path.join(self.mindmap_dir, feature + tdq_mindmap.FILE_SUFFIX)
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(dong) + "\n")
        return path

    def lien_he(self, **kw):
        return run_mindmap(self.cwd, "lien-he", **kw)


class TestLienHeHopLe(LienHeBase):
    def test_lien_he_thu_muc_rong_tra_0(self):
        code, out, err = self.lien_he()
        self.assertEqual(code, tdq_mindmap.EXIT_OK, f"stdout={out}\nstderr={err}")

    def test_lien_he_moi_lien_ket_deu_co_file_tra_0(self):
        self.ghi_feature("dang-nhap")
        self.ghi_feature("mua-hang", phu_thuoc=["dang-nhap"])
        code, out, err = self.lien_he()
        self.assertEqual(code, tdq_mindmap.EXIT_OK, f"stdout={out}\nstderr={err}")


class TestLienHeTroHut(LienHeBase):
    def test_lien_he_tro_toi_feature_khong_co_file_tra_1(self):
        self.ghi_feature("mua-hang", phu_thuoc=["khong-ton-tai"])
        code, out, err = self.lien_he()
        self.assertEqual(code, tdq_mindmap.EXIT_VIOLATION, f"stdout={out}\nstderr={err}")

    def test_lien_he_in_dich_danh_ten_feature_thieu(self):
        self.ghi_feature("mua-hang", phu_thuoc=["khong-ton-tai"])
        _, out, _ = self.lien_he()
        self.assertIn("khong-ton-tai", out, out)

    def test_lien_he_nhieu_feature_thieu_deu_duoc_diem_danh(self):
        self.ghi_feature("mua-hang", phu_thuoc=["mot-thieu", "hai-thieu"])
        code, out, _ = self.lien_he()
        self.assertEqual(code, tdq_mindmap.EXIT_VIOLATION, out)
        self.assertIn("mot-thieu", out, out)
        self.assertIn("hai-thieu", out, out)


class TestLienHeVongLap(LienHeBase):
    def test_lien_he_vong_lap_ba_feature_tra_3(self):
        self.ghi_feature("a", phu_thuoc=["b"])
        self.ghi_feature("b", phu_thuoc=["c"])
        self.ghi_feature("c", phu_thuoc=["a"])
        code, out, err = self.lien_he()
        self.assertEqual(code, tdq_mindmap.EXIT_UPDATE, f"stdout={out}\nstderr={err}")

    def test_lien_he_in_dung_chuoi_vong_lap(self):
        self.ghi_feature("a", phu_thuoc=["b"])
        self.ghi_feature("b", phu_thuoc=["c"])
        self.ghi_feature("c", phu_thuoc=["a"])
        _, out, _ = self.lien_he()
        self.assertRegex(out, r"a\s*->\s*b\s*->\s*c\s*->\s*a", out)


class TestLienHeHamThuan(unittest.TestCase):
    """`build_link_graph` must stay pure: no print, no sys.exit, data in/data out —
    so a later task (the total-map render) can import it straight."""

    def test_lien_he_ham_thuan_do_thi_sach_tra_rong(self):
        do_thi = tdq_mindmap.build_link_graph({"dang-nhap": [], "mua-hang": ["dang-nhap"]})
        self.assertEqual(do_thi["missing"], [])
        self.assertIsNone(do_thi["cycle"])

    def test_lien_he_ham_thuan_bat_duoc_ten_thieu(self):
        do_thi = tdq_mindmap.build_link_graph({"mua-hang": ["khong-ton-tai"]})
        self.assertEqual(do_thi["missing"], ["khong-ton-tai"])
        self.assertIsNone(do_thi["cycle"])

    def test_lien_he_ham_thuan_bat_duoc_vong_lap(self):
        do_thi = tdq_mindmap.build_link_graph({"a": ["b"], "b": ["c"], "c": ["a"]})
        self.assertEqual(do_thi["missing"], [])
        self.assertIsNotNone(do_thi["cycle"])
        self.assertEqual(do_thi["cycle"][0], do_thi["cycle"][-1])
        self.assertEqual(set(do_thi["cycle"]), {"a", "b", "c"})

    def test_lien_he_ham_thuan_khong_in_gi_khong_thoat(self):
        from io import StringIO
        from contextlib import redirect_stdout, redirect_stderr
        ra, loi = StringIO(), StringIO()
        with redirect_stdout(ra), redirect_stderr(loi):
            tdq_mindmap.build_link_graph({"a": ["z"], "b": ["b"]})
        self.assertEqual((ra.getvalue(), loi.getvalue()), ("", ""))


class TestLienHeLogService(LienHeBase):
    def test_lien_he_mac_dinh_co_log_kem_timestamp(self):
        self.ghi_feature("dang-nhap")
        _, _, err = self.lien_he()
        self.assertRegex(err, r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\] tdq_mindmap: ")

    def test_lien_he_tat_log_qua_config(self):
        self.ghi_feature("dang-nhap")
        _, _, err = self.lien_he(env={"TDQ_LOG": "0"})
        self.assertEqual(err.strip(), "", err)


if __name__ == "__main__":
    unittest.main()
