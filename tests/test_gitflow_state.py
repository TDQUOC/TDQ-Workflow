"""State phải nhớ được nhánh git của request (spec §2 đầu ra 1).

Ba khoá mới — `loai_request`, `nhanh_goc`, `nhanh_request` — là chỗ duy nhất workflow ghi lại
nhánh nào đã mở cho request nào. Mất chúng thì bước 10 của khuôn báo cáo không biết merge về
đâu. Bộ test này khoá cả ba, khoá số hiệu schema, và khoá lời hứa "không cần mã chuyển đổi":
một file state schema 4 dựng tay phải nạp lên nguyên vẹn.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "scripts"))

import tdq_state  # noqa: E402

KHOA_MOI = ("loai_request", "nhanh_goc", "nhanh_request")
SCHEMA = 5


class BaKhoaMoiTest(unittest.TestCase):
    def test_ba_khoa_moi_va_schema_5(self):
        mac_dinh = tdq_state.default_state()
        for khoa in KHOA_MOI:
            with self.subTest(khoa=khoa):
                self.assertIn(khoa, mac_dinh, f"default_state() thiếu khoá {khoa}")
                self.assertIsNone(mac_dinh[khoa], f"{khoa} phải mặc định là None")
        self.assertEqual(mac_dinh["schema_version"], SCHEMA)


class DocSchema4Test(unittest.TestCase):
    """File state schema 4 dựng tay: nạp lên không mất khoá nào, ba khoá mới nhận mặc định."""

    def test_doc_schema_4_khong_mat_khoa(self):
        cu = {
            "schema_version": 4,
            "active_request": "2026-01-01-0000-request-cu",
            "lane": "full",
            "phase": "implement",
            "spec_approved": True,
            "spec_approved_by": "duyệt spec",
            "implement_mode": "main",
            "phase_history": [{"phase": "spec", "at": "2026-01-01T00:00:00+07:00"}],
        }
        with tempfile.TemporaryDirectory() as thu_muc:
            duong = os.path.join(thu_muc, tdq_state.STATE_REL)
            os.makedirs(os.path.dirname(duong), exist_ok=True)
            with open(duong, "w", encoding="utf-8") as f:
                json.dump(cu, f)
            nap = tdq_state.load(thu_muc)
        self.assertIsNotNone(nap, "không nạp được state schema 4")
        for khoa, gia_tri in cu.items():
            if khoa in ("schema_version", "phase_history"):
                continue
            with self.subTest(khoa=khoa):
                self.assertEqual(nap[khoa], gia_tri, f"nạp state schema 4 làm mất {khoa}")
        self.assertEqual(nap["schema_version"], SCHEMA, "schema_version phải được nâng lên 5")
        for khoa in KHOA_MOI:
            with self.subTest(khoa=khoa):
                self.assertIsNone(nap[khoa], f"{khoa} phải nhận mặc định khi file cũ không có")


class GhiDocQuaCliTest(unittest.TestCase):
    """Ghi state CHỈ qua CLI — nên ba khoá mới phải đi qua được đúng đường đó."""

    def _chay(self, thu_muc, *doi_so):
        moi_truong = dict(os.environ, TDQ_PROJECT_DIR=thu_muc)
        return subprocess.run(
            [sys.executable, os.path.join(GOC, "scripts", "tdq_state.py"), *doi_so],
            capture_output=True, text=True, encoding="utf-8", env=moi_truong, cwd=thu_muc)

    def test_ghi_doc_qua_cli(self):
        with tempfile.TemporaryDirectory() as thu_muc:
            khoi = self._chay(thu_muc, "init", "2026-09-05-0833-thu", "full")
            self.assertEqual(khoi.returncode, 0, khoi.stderr)
            ghi = self._chay(thu_muc, "set", "loai_request=feature",
                             "nhanh_goc=main", "nhanh_request=feature/thu-nghiem")
            self.assertEqual(ghi.returncode, 0, ghi.stderr)
            nap = tdq_state.load(thu_muc)
        self.assertEqual(nap["loai_request"], "feature")
        self.assertEqual(nap["nhanh_goc"], "main")
        self.assertEqual(nap["nhanh_request"], "feature/thu-nghiem")

    def test_ghi_doc_qua_cli_khoa_la_van_bi_tu_choi(self):
        """Khoá ngoài schema vẫn phải bị từ chối — thêm khoá mới không được nới hàng rào."""
        with tempfile.TemporaryDirectory() as thu_muc:
            self._chay(thu_muc, "init", "2026-09-05-0833-thu", "full")
            xau = self._chay(thu_muc, "set", "nhanh_bia_dat=abc")
        self.assertNotEqual(xau.returncode, 0, "khoá ngoài schema lẽ ra phải bị từ chối")


if __name__ == "__main__":
    unittest.main()
