"""Module `nhan-doc` — scripts/tdq_mindmap.py: khung CLI, lệnh `sinh`, lệnh `kiem`.

Sơ đồ là DÀN Ý bắt buộc của mỗi feature, nên chính cái sinh ra nó phải được kiểm:
tạo mới thì đúng khuôn hằng, feature đã có thì TUYỆT ĐỐI không ghi đè (mất bản
sống của feature là mất nguồn sự thật), slug sai khuôn thì chặn ngay ở cổng vào.

Lệnh `kiem` là cái gác khuôn: mỗi loại sai một mã luật riêng, in ra theo khuôn
`<file>:<dòng>: [<mã>] <thông điệp>` giống `doc_lint.py`, và phần kiểm tách thành
một hàm thuần để T2.6 (luật lint) gọi lại thay vì chạy lại CLI.
"""
import json
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


# T1.5 — `kiem` takes several paths in one call (`nargs="+"`, same shape as
# doc_lint.py's argv handling), exit code is the worst across all of them:
# 2 (unreadable) beats 1 (violation) beats 0 (clean).
def _broken_branch_line(noi_dung):
    """`noi_dung` with its (single) branch line replaced by an ASCII-only broken
    one — built from BRANCH_KEY only, so this stays ASCII, unlike typing the
    Vietnamese branch line out again."""
    dong = noi_dung.splitlines(keepends=True)
    for i, d in enumerate(dong):
        if tdq_mindmap.BRANCH_LINE_RE.match(d):
            dong[i] = f"{tdq_mindmap.BRANCH_KEY}: broken\n"
            break
    return "".join(dong)


class TestKiemNhieuDuongDan(KiemBase):
    def test_kiem_hai_file_sach_tra_0(self):
        a = self.ghi(SACH, ten="a.md")
        b = self.ghi(SACH, ten="b.md")
        code, out, err = run_mindmap(self.cwd, "kiem", a, b)
        self.assertEqual(code, tdq_mindmap.EXIT_OK, f"stdout={out}\nstderr={err}")

    def test_kiem_mot_sach_mot_loi_tra_1(self):
        sach = self.ghi(SACH, ten="sach.md")
        loi = self.ghi(_broken_branch_line(SACH), ten="loi.md")
        code, out, err = run_mindmap(self.cwd, "kiem", sach, loi)
        self.assertEqual(code, tdq_mindmap.EXIT_VIOLATION, f"stdout={out}\nstderr={err}")
        self.assertIn(tdq_mindmap.RULE_BRANCH_SYNTAX, out)

    def test_kiem_co_file_khong_doc_duoc_tra_2_du_con_lai_sach(self):
        sach = self.ghi(SACH, ten="sach.md")
        khong_co = os.path.join(self.cwd, "khong-ton-tai.md")
        code, out, err = run_mindmap(self.cwd, "kiem", sach, khong_co)
        self.assertEqual(code, tdq_mindmap.EXIT_SYNTAX, f"stdout={out}\nstderr={err}")

    def test_kiem_mot_file_van_giu_hanh_vi_cu(self):
        path = self.ghi(SACH)
        code, out, err = run_mindmap(self.cwd, "kiem", path)
        self.assertEqual(code, tdq_mindmap.EXIT_OK, f"stdout={out}\nstderr={err}")
        self.assertEqual(out.strip(), "", out)

    def test_kiem_ca_hai_file_mau_that_tra_0(self):
        dang_nhap = os.path.join(ROOT, "docs", "tdq", "mind-map", "dang-nhap.md")
        mua_hang = os.path.join(ROOT, "docs", "tdq", "mind-map", "mua-hang.md")
        code, out, err = run_mindmap(ROOT, "kiem", dang_nhap, mua_hang)
        self.assertEqual(code, tdq_mindmap.EXIT_OK, f"stdout={out}\nstderr={err}")


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


# T1.3 — command `doi-chieu`: cross-check every step's `<file>::<function>` location
# in one diagram against the code nodes graphify wrote into `graphify-out/graph.json`.
# The filter is `file_type == "code"` ONLY — never `source_file`+`source_location`,
# which also sit on document nodes and would leak them into the check. Fixtures below
# use plain ASCII step text on purpose, same reason as the lien-he block above.
GRAPH_THAT = {
    "built_at_commit": "deadbeef",
    "nodes": [
        {"file_type": "code", "source_file": "src/login.tsx", "label": "LoginForm.onSubmit()"},
        {"file_type": "code", "source_file": "server/auth.py", "label": "AuthController.login()"},
        {"file_type": "code", "source_file": "server/auth.py", "label": "deny()"},
        {"file_type": "document", "source_file": "src/login.tsx",
         "source_location": "L1", "label": "login.tsx"},
    ],
    "links": [],
}


def write_graph(cwd, graph):
    """Write one fake `graphify-out/graph.json` under `cwd` — no git repo needed
    unless a case cares about the `built_at_commit` warning."""
    directory = os.path.join(cwd, "graphify-out")
    os.makedirs(directory, exist_ok=True)
    with open(os.path.join(directory, "graph.json"), "w", encoding="utf-8") as f:
        json.dump(graph, f)


class DoiChieuBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cwd = self.tmp.name

    def ghi(self, noi_dung, ten="so-do.md"):
        path = os.path.join(self.cwd, ten)
        with open(path, "w", encoding="utf-8") as f:
            f.write(noi_dung)
        return path

    def doi_chieu(self, noi_dung, graph=GRAPH_THAT, **kw):
        if graph is not None:
            write_graph(self.cwd, graph)
        return run_mindmap(self.cwd, "doi-chieu", self.ghi(noi_dung), **kw)


class TestDoiChieuLocNodeCode(unittest.TestCase):
    """Q2 (`-k doi_chieu_loc`): the filter is `file_type == "code"` only, and it
    must produce exactly as many rows as the graph carries `file_type == "code"`
    nodes — counted straight from the graph file, not re-derived some other way."""

    def test_doi_chieu_loc_dung_bang_so_node_code_trong_do_thi_that(self):
        graph_file = os.path.join(ROOT, "graphify-out", "graph.json")
        with open(graph_file, encoding="utf-8") as f:
            real_graph = json.load(f)
        code_node_count = sum(
            1 for n in real_graph["nodes"] if n.get("file_type") == "code")
        self.assertGreater(code_node_count, 0, "sample graph is empty, nothing to measure")
        filtered = tdq_mindmap.filter_code_nodes(real_graph)
        self.assertEqual(len(filtered), code_node_count)
        self.assertTrue(all(n.get("file_type") == "code" for n in filtered))

    def test_doi_chieu_loc_khong_lan_node_tai_lieu(self):
        graph = {"nodes": [
            {"file_type": "code", "source_file": "a.py", "source_location": "L1",
             "label": "a.py"},
            {"file_type": "document", "source_file": "a.md", "source_location": "L1",
             "label": "a.md"},
            {"file_type": "rationale", "source_file": "a.py", "source_location": "L2",
             "label": "why"},
        ]}
        filtered = tdq_mindmap.filter_code_nodes(graph)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["file_type"], "code")


class TestDoiChieuKhopHet(DoiChieuBase):
    def test_doi_chieu_moi_cap_khop_tra_0(self):
        code, out, err = self.doi_chieu(
            "B1 · enter email and password (src/login.tsx::LoginForm.onSubmit)\n"
            "B2 · look up the user (server/auth.py::AuthController.login)\n"
            "B2! · wrong password returns a generic error (server/auth.py::deny)\n"
            "B3 · land on the home screen (?)\n")
        self.assertEqual(code, tdq_mindmap.EXIT_OK, f"stdout={out}\nstderr={err}")
        self.assertEqual(out.strip(), "", out)

    def test_doi_chieu_chi_toan_buoc_chua_biet_cung_tra_0(self):
        code, out, _ = self.doi_chieu("B1 · first step (?)\nB2 · second step (?)\n")
        self.assertEqual(code, tdq_mindmap.EXIT_OK, out)


class TestDoiChieuCapLech(DoiChieuBase):
    def test_doi_chieu_co_cap_lech_tra_1(self):
        code, out, err = self.doi_chieu(
            "B1 · enter email (src/login.tsx::LoginForm.onSubmit)\n"
            "B2 · function that does not exist (server/auth.py::khong_ton_tai)\n")
        self.assertEqual(code, tdq_mindmap.EXIT_VIOLATION, f"stdout={out}\nstderr={err}")

    def test_doi_chieu_in_dich_danh_cap_lech(self):
        _, out, _ = self.doi_chieu(
            "B1 · function that does not exist (server/auth.py::khong_ton_tai)\n")
        self.assertIn("server/auth.py", out, out)
        self.assertIn("khong_ton_tai", out, out)

    def test_doi_chieu_file_dung_ham_sai_van_la_lech(self):
        code, out, _ = self.doi_chieu(
            "B1 · wrong function name (server/auth.py::AuthController.dang_xuat)\n")
        self.assertEqual(code, tdq_mindmap.EXIT_VIOLATION, out)

    def test_doi_chieu_buoc_chua_biet_khong_tinh_la_lech(self):
        code, out, _ = self.doi_chieu(
            "B1 · enter email (src/login.tsx::LoginForm.onSubmit)\n"
            "B2 · step whose code is not known yet (?)\n")
        self.assertEqual(code, tdq_mindmap.EXIT_OK, out)


class TestDoiChieuKhongDocDuocDoThi(DoiChieuBase):
    def test_doi_chieu_thieu_graphify_out_tra_3(self):
        code, out, err = self.doi_chieu("B1 · x (?)\n", graph=None)
        self.assertEqual(code, tdq_mindmap.EXIT_UPDATE, f"stdout={out}\nstderr={err}")

    def test_doi_chieu_json_hong_tra_3(self):
        directory = os.path.join(self.cwd, "graphify-out")
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, "graph.json"), "w", encoding="utf-8") as f:
            f.write("{ not valid json")
        code, out, _ = run_mindmap(self.cwd, "doi-chieu", self.ghi("B1 · x (?)\n"))
        self.assertEqual(code, tdq_mindmap.EXIT_UPDATE, out)


class TestDoiChieuFileSoDoKhongDocDuoc(DoiChieuBase):
    def test_doi_chieu_file_khong_ton_tai_tra_2(self):
        write_graph(self.cwd, GRAPH_THAT)
        code, _, _ = run_mindmap(self.cwd, "doi-chieu",
                                 os.path.join(self.cwd, "khong-co.md"))
        self.assertEqual(code, tdq_mindmap.EXIT_SYNTAX)


class TestDoiChieuCanhBaoCommit(DoiChieuBase):
    """A `built_at_commit` different from HEAD only prints a warning — it never
    changes the exit code, and it never re-runs graphify on its own."""

    def _init_git(self):
        subprocess.run(["git", "init", "-q"], cwd=self.cwd, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"],
                       cwd=self.cwd, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=self.cwd, check=True)
        with open(os.path.join(self.cwd, "README.md"), "w", encoding="utf-8") as f:
            f.write("x\n")
        subprocess.run(["git", "add", "."], cwd=self.cwd, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=self.cwd, check=True)

    def test_doi_chieu_commit_khac_head_van_tra_0_neu_khop(self):
        self._init_git()
        code, out, err = self.doi_chieu(
            "B1 · enter email and password (src/login.tsx::LoginForm.onSubmit)\n")
        self.assertEqual(code, tdq_mindmap.EXIT_OK, f"stdout={out}\nstderr={err}")

    def test_doi_chieu_commit_khac_head_co_canh_bao(self):
        self._init_git()
        _, _, err = self.doi_chieu(
            "B1 · enter email and password (src/login.tsx::LoginForm.onSubmit)\n")
        self.assertIn("deadbeef", err, err)

    def test_doi_chieu_khong_phai_git_repo_khong_canh_bao(self):
        code, out, err = self.doi_chieu(
            "B1 · enter email and password (src/login.tsx::LoginForm.onSubmit)\n")
        self.assertEqual(code, tdq_mindmap.EXIT_OK, f"stdout={out}\nstderr={err}")
        self.assertNotIn("deadbeef", err, err)


class TestDoiChieuHamThuan(unittest.TestCase):
    """`cross_check_diagram` must stay pure: no print, no read, no sys.exit — so
    another module (the renderer) can import it straight."""

    def test_doi_chieu_ham_thuan_tra_danh_sach_cap_lech(self):
        lech = tdq_mindmap.cross_check_diagram(
            "B1 · x (a.py::khong_co)\n".splitlines(),
            {"nodes": [{"file_type": "code", "source_file": "a.py", "label": "co()"}]})
        self.assertEqual(lech, [(1, "a.py", "khong_co")])

    def test_doi_chieu_ham_thuan_khop_tra_danh_sach_rong(self):
        lech = tdq_mindmap.cross_check_diagram(
            "B1 · x (a.py::co)\n".splitlines(),
            {"nodes": [{"file_type": "code", "source_file": "a.py", "label": "co()"}]})
        self.assertEqual(lech, [])

    def test_doi_chieu_ham_thuan_khong_in_gi_khong_thoat(self):
        from io import StringIO
        from contextlib import redirect_stdout, redirect_stderr
        ra, loi = StringIO(), StringIO()
        with redirect_stdout(ra), redirect_stderr(loi):
            tdq_mindmap.cross_check_diagram(
                "B1 · x (a.py::khong_co)\n".splitlines(), {"nodes": []})
        self.assertEqual((ra.getvalue(), loi.getvalue()), ("", ""))


class TestDoiChieuLogService(DoiChieuBase):
    def test_doi_chieu_mac_dinh_co_log_kem_timestamp(self):
        _, _, err = self.doi_chieu("B1 · x (?)\n")
        self.assertRegex(err, r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\] tdq_mindmap: ")

    def test_doi_chieu_tat_log_qua_config(self):
        _, _, err = self.doi_chieu("B1 · x (?)\n", env={"TDQ_LOG": "0"})
        self.assertEqual(err.strip(), "", err)


# T2.3 — command `xem`: wires tdq_mindmap's CLI to mindmap_render.render_feature_page.
# The rendering logic itself lives entirely in mindmap_render.py — these tests only
# check the wiring: exit codes and that the right file lands on disk.
# ASCII on purpose (same reason as the doi-chieu/lien-he fixtures above): built from
# the shared constants instead of typing the Vietnamese keywords out.
SO_DO_DUNG = (f"{tdq_mindmap.TITLE_PREFIX}Login\n"
              f"{tdq_mindmap.BRANCH_KEY}: Account {tdq_mindmap.BRANCH_SEP} Login\n"
              "B1 · enter email and password (?)\n")

SO_DO_SAI = "B1 · missing title and branch line (?)\n"


class XemBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cwd = self.tmp.name

    def ghi(self, noi_dung, ten="dang-nhap.md"):
        path = os.path.join(self.cwd, ten)
        with open(path, "w", encoding="utf-8") as f:
            f.write(noi_dung)
        return path

    def xem(self, *args, **kw):
        return run_mindmap(self.cwd, "xem", *args, **kw)


class TestXemGhiXong(XemBase):
    def test_xem_so_do_dung_tra_0_va_ghi_file(self):
        path = self.ghi(SO_DO_DUNG)
        code, out, err = self.xem(path)
        self.assertEqual(code, tdq_mindmap.EXIT_OK, f"stdout={out}\nstderr={err}")
        out_path = os.path.join(self.cwd, tdq_mindmap.MIND_MAP_DIR_REL, "dang-nhap.html")
        self.assertTrue(os.path.exists(out_path), out)

    def test_xem_file_ghi_ra_la_html_hop_le_toi_thieu(self):
        path = self.ghi(SO_DO_DUNG)
        self.xem(path)
        out_path = os.path.join(self.cwd, tdq_mindmap.MIND_MAP_DIR_REL, "dang-nhap.html")
        with open(out_path, encoding="utf-8") as f:
            noi_dung = f.read()
        self.assertIn("<!doctype html>", noi_dung)
        self.assertIn("Login", noi_dung)


class TestXemSoDoSaiKhuon(XemBase):
    def test_xem_so_do_sai_khuon_tra_1(self):
        path = self.ghi(SO_DO_SAI)
        code, out, err = self.xem(path)
        self.assertEqual(code, tdq_mindmap.EXIT_VIOLATION, f"stdout={out}\nstderr={err}")

    def test_xem_so_do_sai_khuon_in_vi_pham(self):
        path = self.ghi(SO_DO_SAI)
        _, out, _ = self.xem(path)
        self.assertIn(tdq_mindmap.RULE_TITLE_MISSING, out)

    def test_xem_so_do_sai_khuon_khong_ghi_file(self):
        path = self.ghi(SO_DO_SAI)
        self.xem(path)
        out_path = os.path.join(self.cwd, tdq_mindmap.MIND_MAP_DIR_REL, "dang-nhap.html")
        self.assertFalse(os.path.exists(out_path), "wrote a file despite the shape violation")


class TestXemKhongDocDuocFileVao(XemBase):
    def test_xem_file_vao_khong_ton_tai_tra_2(self):
        code, _, _ = self.xem(os.path.join(self.cwd, "khong-co.md"))
        self.assertEqual(code, tdq_mindmap.EXIT_SYNTAX)


@unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0,
                  "root ignores directory permissions, cannot simulate this case")
class TestXemKhongGhiDuocFileRa(XemBase):
    def test_xem_thu_muc_dich_chi_doc_tra_2(self):
        path = self.ghi(SO_DO_DUNG)
        mindmap_dir = os.path.join(self.cwd, tdq_mindmap.MIND_MAP_DIR_REL)
        os.makedirs(mindmap_dir, exist_ok=True)
        os.chmod(mindmap_dir, 0o500)
        self.addCleanup(os.chmod, mindmap_dir, 0o700)
        code, out, err = self.xem(path)
        self.assertEqual(code, tdq_mindmap.EXIT_SYNTAX, f"stdout={out}\nstderr={err}")


class TestXemTong(XemBase):
    """T2.8: `xem --tong` calls straight into mindmap_render's own aggregate
    builder (T2.2) instead of stopping at the argparse flag (T2.3)."""

    def ghi_mind_map(self, ten, noi_dung):
        directory = os.path.join(self.cwd, tdq_mindmap.MIND_MAP_DIR_REL)
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, ten), "w", encoding="utf-8") as f:
            f.write(noi_dung)

    def test_xem_tong_khong_bi_argparse_tu_choi(self):
        code, out, err = self.xem("--tong")
        self.assertNotIn("the following arguments are required", err, err)
        self.assertNotIn("usage:", err, err)

    def test_xem_tong_tra_0_va_ghi_index_html(self):
        self.ghi_mind_map("dang-nhap.md", SO_DO_DUNG)
        code, out, err = self.xem("--tong")
        self.assertEqual(code, tdq_mindmap.EXIT_OK, f"stdout={out}\nstderr={err}")
        out_path = os.path.join(self.cwd, tdq_mindmap.MIND_MAP_DIR_REL, "index.html")
        self.assertTrue(os.path.exists(out_path), out)

    def test_xem_tong_index_html_gom_dung_feature(self):
        self.ghi_mind_map("dang-nhap.md", SO_DO_DUNG)
        self.xem("--tong")
        out_path = os.path.join(self.cwd, tdq_mindmap.MIND_MAP_DIR_REL, "index.html")
        with open(out_path, encoding="utf-8") as f:
            noi_dung = f.read()
        self.assertIn("Login", noi_dung)

    def test_xem_tong_khong_co_feature_van_tra_0(self):
        code, out, err = self.xem("--tong")
        self.assertEqual(code, tdq_mindmap.EXIT_OK, f"stdout={out}\nstderr={err}")
        out_path = os.path.join(self.cwd, tdq_mindmap.MIND_MAP_DIR_REL, "index.html")
        self.assertTrue(os.path.exists(out_path), out)


@unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0,
                  "root ignores directory permissions, cannot simulate this case")
class TestXemTongKhongGhiDuocFileRa(XemBase):
    def test_xem_tong_thu_muc_dich_chi_doc_tra_2(self):
        mindmap_dir = os.path.join(self.cwd, tdq_mindmap.MIND_MAP_DIR_REL)
        os.makedirs(mindmap_dir, exist_ok=True)
        os.chmod(mindmap_dir, 0o500)
        self.addCleanup(os.chmod, mindmap_dir, 0o700)
        code, out, err = self.xem("--tong")
        self.assertEqual(code, tdq_mindmap.EXIT_SYNTAX, f"stdout={out}\nstderr={err}")


class TestXemLogService(XemBase):
    def test_xem_mac_dinh_co_log_kem_timestamp(self):
        path = self.ghi(SO_DO_DUNG)
        _, _, err = self.xem(path)
        self.assertRegex(err, r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\] tdq_mindmap: ")

    def test_xem_tat_log_qua_config(self):
        path = self.ghi(SO_DO_DUNG)
        _, _, err = self.xem(path, env={"TDQ_LOG": "0"})
        self.assertEqual(err.strip(), "", err)


if __name__ == "__main__":
    unittest.main()
