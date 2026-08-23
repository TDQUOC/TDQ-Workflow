"""Module `nhan-doc` — scripts/tdq_mindmap.py: khung CLI + lệnh `sinh`.

Sơ đồ là DÀN Ý bắt buộc của mỗi feature, nên chính cái sinh ra nó phải được kiểm:
tạo mới thì đúng khuôn hằng, feature đã có thì TUYỆT ĐỐI không ghi đè (mất bản
sống của feature là mất nguồn sự thật), slug sai khuôn thì chặn ngay ở cổng vào.
"""
import os
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


if __name__ == "__main__":
    unittest.main()
