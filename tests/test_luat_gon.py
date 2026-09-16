"""Test bộ đọc–lọc thân luật tinh gọn ở hooks/scripts/luat_gon.py.

T2.1: `doc_than_luat(goc)` lấy khối giữa cặp marker `luat-gon` trong
skills/tdq-build/references/rules/chung.md (thiếu marker → chuỗi rỗng + một dòng cảnh báo,
cấm ném lỗi); `loc_than_luat(than, muc_gat)` lọc theo bốn mức `lite|full|ultra|off`, mức lạ
/ rỗng / None đều ra y như `full` (fail-closed — không có suy luận nào chọn được `off`).
"""
import io
import os
import sys
import unittest
from contextlib import redirect_stderr

from helper import HOOKS, ROOT

sys.path.insert(0, HOOKS)
import luat_gon  # noqa: E402

# Ba tiêu đề `###` là mốc lọc; chép nguyên văn từ chung.md của T1.1.
MUC_BANG_CUONG_DO = "### Intensity table"
MUC_VI_DU = "### RIGHT / WRONG for this law"
MUC_ULTRA = "### Extra at level ultra"


class DocThanLuat(unittest.TestCase):
    def test_doc_tu_repo_that(self):
        than = luat_gon.doc_than_luat(ROOT)
        self.assertTrue(than, "phải đọc được thân luật từ repo thật")
        self.assertNotIn("luat-gon:bat-dau", than, "khối trả về không được chứa marker")
        for bac in range(1, 8):
            self.assertIn(f"| {bac} |", than, f"thân luật thiếu bậc {bac}")
        self.assertIn("Make it run first, refactor after", than, "thiếu món 8")

    def test_thieu_marker_ra_rong_va_canh_bao(self):
        goc = self.tam_thoi("# chung.md không có marker nào\n")
        loi = io.StringIO()
        with redirect_stderr(loi):
            than = luat_gon.doc_than_luat(goc)
        self.assertEqual(than, "", "thiếu marker thì phải trả chuỗi rỗng")
        self.assertEqual(len(loi.getvalue().strip().splitlines()), 1,
                         "thiếu marker thì cảnh báo đúng một dòng")

    def test_thieu_file_ra_rong_khong_nem_loi(self):
        loi = io.StringIO()
        with redirect_stderr(loi):
            than = luat_gon.doc_than_luat(os.path.join(ROOT, "khong-ton-tai"))
        self.assertEqual(than, "", "thiếu file thì phải trả chuỗi rỗng, không ném lỗi")
        self.assertTrue(loi.getvalue().strip(), "thiếu file vẫn phải cảnh báo một dòng")

    def tam_thoi(self, noi_dung):
        """Dựng một gốc project giả chỉ có chung.md, trả về đường dẫn gốc."""
        import tempfile
        goc = tempfile.mkdtemp()
        thu_muc = os.path.join(goc, "skills", "tdq-build", "references", "rules")
        os.makedirs(thu_muc)
        with open(os.path.join(thu_muc, "chung.md"), "w", encoding="utf-8") as f:
            f.write(noi_dung)
        return goc


class LocThanLuat(unittest.TestCase):
    def setUp(self):
        self.than = luat_gon.doc_than_luat(ROOT)
        self.assertTrue(self.than, "cần thân luật thật để lọc")

    def test_bon_muc_ra_bon_ket_qua_khac_nhau(self):
        ra = {m: luat_gon.loc_than_luat(self.than, m)
              for m in ("off", "lite", "full", "ultra")}
        self.assertEqual(ra["off"], "", "`off` phải trả rỗng")
        dai = {m: len(v.splitlines()) for m, v in ra.items()}
        self.assertLess(dai["off"], dai["lite"], "off phải ngắn hơn lite")
        self.assertLess(dai["lite"], dai["full"], "lite phải ngắn hơn full")
        self.assertLess(dai["full"], dai["ultra"], "full phải ngắn hơn ultra")

    def test_lite_cat_bang_cuong_do_va_vi_du(self):
        ra = luat_gon.loc_than_luat(self.than, "lite")
        self.assertNotIn(MUC_BANG_CUONG_DO, ra, "lite phải cắt bảng cường độ")
        self.assertNotIn(MUC_VI_DU, ra, "lite phải cắt ví dụ RIGHT/WRONG")
        self.assertNotIn(MUC_ULTRA, ra, "lite không được giữ mục riêng của ultra")

    def test_full_giu_bang_va_vi_du_nhung_bo_muc_ultra(self):
        ra = luat_gon.loc_than_luat(self.than, "full")
        self.assertIn(MUC_BANG_CUONG_DO, ra, "full phải giữ bảng cường độ")
        self.assertIn(MUC_VI_DU, ra, "full phải giữ ví dụ RIGHT/WRONG")
        self.assertNotIn(MUC_ULTRA, ra, "mục riêng của ultra chỉ hiện ở mức ultra")

    def test_ultra_giu_tat_ca(self):
        ra = luat_gon.loc_than_luat(self.than, "ultra")
        for muc in (MUC_BANG_CUONG_DO, MUC_VI_DU, MUC_ULTRA):
            self.assertIn(muc, ra, f"ultra phải giữ {muc}")

    def test_muc_la_rong_none_deu_ve_full(self):
        nhu_full = luat_gon.loc_than_luat(self.than, "full")
        for muc in ("xyz", "", None, "OFF ", "review", 7):
            with self.subTest(muc=muc):
                self.assertEqual(luat_gon.loc_than_luat(self.than, muc), nhu_full,
                                 f"mức {muc!r} phải xử như `full`")

    def test_moi_muc_khac_off_deu_du_7_bac(self):
        for muc in ("lite", "full", "ultra"):
            ra = luat_gon.loc_than_luat(self.than, muc)
            for bac in range(1, 8):
                with self.subTest(muc=muc, bac=bac):
                    self.assertIn(f"| {bac} |", ra, f"mức {muc} mất bậc {bac}")

    def test_moi_muc_khac_off_giu_hai_phan_quyet_cua_user(self):
        for muc in ("lite", "full", "ultra"):
            ra = luat_gon.loc_than_luat(self.than, muc)
            with self.subTest(muc=muc):
                self.assertIn("log service", ra, f"mức {muc} mất luật log service")
                self.assertIn("No exemption", ra, f"mức {muc} mất luật test không miễn trừ")

    def test_than_rong_thi_moi_muc_deu_rong(self):
        for muc in ("lite", "full", "ultra", "off", None):
            with self.subTest(muc=muc):
                self.assertEqual(luat_gon.loc_than_luat("", muc), "")


if __name__ == "__main__":
    unittest.main()
