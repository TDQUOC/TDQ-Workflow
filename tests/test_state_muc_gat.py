"""Test khoá `muc_gat` trong scripts/tdq_state.py (T2.2).

Bốn giá trị `lite|full|ultra|off`; khoá trống hay giá trị lạ đều ra `full` (fail-closed —
chỉ user đặt được `off`); đọc/ghi qua `tdq_state.py set muc_gat=<giá trị>`; mức hiện tại
phải hiện trên mặt trạng thái user đọc (`next` và docs/tdq/STATE.md), không dựng mặt hiển
thị thứ hai.
"""
import json
import os
import tempfile
import unittest

from helper import read_state, run_state_cli, write_state
import tdq_state


class MacDinhVaChuanHoa(unittest.TestCase):
    def test_default_state_la_full(self):
        self.assertEqual(tdq_state.default_state()["muc_gat"], "full")

    def test_bon_gia_tri_hop_le_giu_nguyen(self):
        for muc in ("lite", "full", "ultra", "off"):
            with self.subTest(muc=muc):
                self.assertEqual(tdq_state.normalize_muc_gat(muc), muc)

    def test_gia_tri_la_rong_none_ve_full(self):
        for raw in ("xyz", "review", "", None, 7, [], "  "):
            with self.subTest(raw=raw):
                self.assertEqual(tdq_state.normalize_muc_gat(raw), "full")

    def test_hoa_thuong_va_khoang_trang_van_nhan(self):
        for raw in (" OFF ", "Ultra", "LITE"):
            with self.subTest(raw=raw):
                self.assertEqual(tdq_state.normalize_muc_gat(raw), raw.strip().lower())

    def test_khoa_thieu_trong_file_state_doc_ra_full(self):
        with tempfile.TemporaryDirectory() as cwd:
            os.makedirs(os.path.join(cwd, "docs", "tdq"))
            with open(os.path.join(cwd, "docs", "tdq", "state.json"), "w",
                      encoding="utf-8") as f:
                json.dump({"phase": "implement"}, f)
            self.assertEqual(tdq_state.muc_gat_hieu_luc(read_state(cwd)), "full")

    def test_gia_tri_rac_trong_file_state_doc_ra_full(self):
        with tempfile.TemporaryDirectory() as cwd:
            write_state(cwd, muc_gat="xyz")
            self.assertEqual(tdq_state.muc_gat_hieu_luc(read_state(cwd)), "full")


class QuaCLI(unittest.TestCase):
    def test_set_roi_get_doc_lai_dung_gia_tri(self):
        with tempfile.TemporaryDirectory() as cwd:
            write_state(cwd, active_request="r", lane="full", phase="implement")
            ma, _, loi = run_state_cli(cwd, "set", "muc_gat=off")
            self.assertEqual(ma, 0, loi)
            self.assertEqual(run_state_cli(cwd, "get", "muc_gat")[1], "off")

    def test_set_gia_tri_la_ve_full_chu_khong_bao_loi(self):
        with tempfile.TemporaryDirectory() as cwd:
            write_state(cwd, active_request="r", lane="full", phase="implement")
            ma, _, loi = run_state_cli(cwd, "set", "muc_gat=xyz")
            self.assertEqual(ma, 0, f"giá trị lạ phải về full, không fail: {loi}")
            self.assertEqual(run_state_cli(cwd, "get", "muc_gat")[1], "full")

    def test_next_in_muc_gat_hien_tai(self):
        with tempfile.TemporaryDirectory() as cwd:
            write_state(cwd, active_request="r", lane="full", phase="implement",
                        muc_gat="ultra")
            ma, ra, loi = run_state_cli(cwd, "next")
            self.assertEqual(ma, 0, loi)
            self.assertIn("ultra", ra, "dòng mức gắt phải có trong đầu ra `next`")

    def test_state_md_co_dong_muc_gat(self):
        with tempfile.TemporaryDirectory() as cwd:
            write_state(cwd, active_request="r", lane="full", phase="implement")
            run_state_cli(cwd, "set", "muc_gat=lite")
            with open(os.path.join(cwd, "docs", "tdq", "STATE.md"),
                      encoding="utf-8") as f:
                mat = f.read()
            self.assertIn("lite", mat, "STATE.md phải phơi mức gắt hiện tại")


if __name__ == "__main__":
    unittest.main()
