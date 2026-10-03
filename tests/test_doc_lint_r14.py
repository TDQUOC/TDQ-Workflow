"""R14: hàng §6 có ngưỡng số phải mang cột `Đo trước` và `Dự phòng nếu trượt` không rỗng."""
import contextlib
import io
import os
import shutil
import sys
import tempfile
import unittest

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import doc_lint  # noqa: E402

TEN_MOI = "2026-10-03-0732-thu.md"
TEN_CU = "2026-09-01-1200-thu.md"

DAU_THIEU = "| # | Hạng mục | Điều kiện PASS |\n|---|---|---|\n"
DAU_DU = ("| # | Hạng mục | Điều kiện PASS | Đo trước | Dự phòng nếu trượt |\n"
          "|---|---|---|---|---|\n")


def _spec(bang):
    return ("# SPEC — thử\n\n## 5. Ràng buộc\n\n| Q1 | ngoài §6 | ≤ 200 MB |\n\n"
            "## 6. QC & Definition of Done\n\n" + bang + "\n## 7. Câu hỏi còn mở\n\nkhông\n")


class TestR14Bat(unittest.TestCase):
    """Hàng có ngưỡng mà thiếu cột / ô rỗng → lỗi."""

    def test_bat_thieu_hai_cot(self):
        loi = doc_lint.r14_loi(_spec(DAU_THIEU + "| Q9 | Installer | ≤ 200 MB |\n"), TEN_MOI)
        self.assertEqual(len(loi), 1)
        so_dong, thong_bao = loi[0]
        self.assertEqual(_spec(DAU_THIEU + "| Q9 | Installer | ≤ 200 MB |\n")
                         .splitlines()[so_dong - 1], "| Q9 | Installer | ≤ 200 MB |")
        self.assertIn("Q9", thong_bao)

    def test_bat_khong_co_dau_bang(self):
        loi = doc_lint.r14_loi(_spec("| Q9 | Installer | ≤ 200 MB |\n"), TEN_MOI)
        self.assertEqual(len(loi), 1)

    def test_bat_o_rong_va_gach(self):
        for do, du in (("—", "giảm gói"), ("212 MB", "—"), ("", "giảm gói"), ("212 MB", "-")):
            bang = DAU_DU + f"| Q9 | Installer | ≤ 200 MB | {do} | {du} |\n"
            self.assertEqual(len(doc_lint.r14_loi(_spec(bang), TEN_MOI)), 1, (do, du))

    def test_bat_do_truoc_khong_co_so(self):
        bang = DAU_DU + "| Q9 | Installer | ≤ 200 MB | ước lượng: ổn | giảm gói |\n"
        self.assertEqual(len(doc_lint.r14_loi(_spec(bang), TEN_MOI)), 1)

    def test_bat_so_kem_don_vi(self):
        for dk in ("tải xong trong 30 giây", "phủ 80%", "tối đa ~5 phút", "không quá 2 lần",
                   "ít nhất 9", "≥ 9 trên 10 hàng", "<= 500 ms", "dưới 3 s"):
            bang = DAU_THIEU + f"| Q2 | thử | {dk} |\n"
            self.assertEqual(len(doc_lint.r14_loi(_spec(bang), TEN_MOI)), 1, dk)


class TestR14DuCot(unittest.TestCase):
    """Đủ hai cột, có số đo → không lỗi."""

    def test_du_cot_khong_loi(self):
        bang = DAU_DU + ("| Q9 | Installer | ≤ 200 MB | 212 MB + ~20 MB | "
                         "bỏ bộ font phụ, ghi lệch |\n")
        self.assertEqual(doc_lint.r14_loi(_spec(bang), TEN_MOI), [])

    def test_du_cot_bang_khong_co_cot_pass_dung_cot_3(self):
        bang = ("| # | Mục | Ngưỡng | Đo trước | Dự phòng nếu trượt |\n|---|---|---|---|---|\n"
                "| Q9 | Installer | ≤ 200 MB | 212 MB | giảm gói |\n"
                "| Q10 | Installer | ≤ 200 MB | — | — |\n")
        loi = doc_lint.r14_loi(_spec(bang), TEN_MOI)
        self.assertEqual(len(loi), 1)
        self.assertIn("Q10", loi[0][1])


class TestR14TonTai(unittest.TestCase):
    """Phép tồn tại / vắng mặt, số phiên bản, mã Q → không phải ngưỡng."""

    def test_ton_tai_khong_phai_nguong(self):
        for dk in ("≥ 1 test", "0 failure", "= 0 dòng", "bản 0.56.0", "Q3 và Q4 xanh",
                   "exit ≠ 0", "4 loại được nhận", "`≤ 200 MB` trong ví dụ",
                   "trên 103 spec cũ → 0 lỗi R14", "a -> 5 b", "1 dòng"):
            bang = DAU_THIEU + f"| Q3 | thử | {dk} |\n"
            self.assertEqual(doc_lint.r14_loi(_spec(bang), TEN_MOI), [], dk)

    def test_ton_tai_ngoai_muc_6_khong_xet(self):
        self.assertEqual(doc_lint.r14_loi(_spec(DAU_THIEU), TEN_MOI), [])


class TestR14Moc(unittest.TestCase):
    """Spec trước mốc slug → im; spec hiện tại → qua."""

    def test_moc_slug_cu_im(self):
        van = _spec(DAU_THIEU + "| Q9 | Installer | ≤ 200 MB |\n")
        self.assertEqual(doc_lint.r14_loi(van, TEN_CU), [])
        self.assertEqual(doc_lint.r14_loi(van, "2026-10-03-0731-thu.md"), [])
        self.assertEqual(len(doc_lint.r14_loi(van, "docs/tdq/spec/" + TEN_MOI)), 1)

    def test_moc_spec_hien_tai_qua(self):
        duong = os.path.join(ROOT, "docs", "tdq", "spec",
                             "2026-10-03-0732-do-truoc-lam-mot-turn.md")
        with open(duong, encoding="utf-8") as f:
            self.assertEqual(doc_lint.r14_loi(f.read(), duong), [])

    def test_moc_chi_nhanh_spec(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)
        van = _spec(DAU_THIEU + "| Q9 | Installer | ≤ 200 MB |\n")
        for nhanh, mong in (("spec", 1), ("plan", 0)):
            thu_muc = os.path.join(tmp, "docs", "tdq", nhanh)
            os.makedirs(thu_muc)
            duong = os.path.join(thu_muc, TEN_MOI)
            with open(duong, "w", encoding="utf-8") as f:
                f.write(van)
            with contextlib.redirect_stderr(io.StringIO()):
                loi = [d for d in doc_lint.lint_file(duong) if "[R14]" in d]
            self.assertEqual(len(loi), mong, nhanh)


class TestR14Log(unittest.TestCase):
    """R14 ghi một dòng log có giờ ISO; TDQ_LOG=0 tắt."""

    def setUp(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)
        thu_muc = os.path.join(tmp, "docs", "tdq", "spec")
        os.makedirs(thu_muc)
        self.duong = os.path.join(thu_muc, TEN_MOI)
        with open(self.duong, "w", encoding="utf-8") as f:
            f.write(_spec(DAU_THIEU + "| Q9 | Installer | ≤ 200 MB |\n"))
        cu = os.environ.get("TDQ_LOG")
        self.addCleanup(lambda: os.environ.__setitem__("TDQ_LOG", cu) if cu is not None
                        else os.environ.pop("TDQ_LOG", None))

    def _chay(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            doc_lint.lint_file(self.duong)
        return [d for d in err.getvalue().splitlines() if "R14" in d]

    def test_log_mot_dong_iso(self):
        os.environ["TDQ_LOG"] = "1"
        dong = self._chay()
        self.assertEqual(len(dong), 1)
        self.assertRegex(dong[0], r"^\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\] doc_lint: R14")

    def test_log_tat(self):
        os.environ["TDQ_LOG"] = "0"
        self.assertEqual(self._chay(), [])


if __name__ == "__main__":
    unittest.main()
