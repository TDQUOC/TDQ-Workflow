"""Khoá `muc_qc` — mức độ QC của request (yêu cầu 2026-09-23-1148).

Vì sao khoá bằng test chứ không bằng tài liệu: mức QC quyết định phase `qc` chạy bao nhiêu phép
kiểm. Một giá trị rác lọt qua mà im lặng hạ mức xuống thấp nhất thì request vẫn tuyên bố "xong"
trong khi chưa chạy gì — hỏng đúng kiểu không ai thấy. Nên luật fail-closed (mọi thứ không hợp lệ
đều ra `full`) phải có phép kiểm riêng, y như `muc_gat` từ 0.48.0.

Ba nhóm chạy riêng được bằng `-k`: `chuan_hoa`, `hien_thi`, `log`.
"""
import json
import os
import sys
import tempfile
import unittest

from helper import ROOT, run_state_cli, write_state  # noqa: F401

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tdq_state  # noqa: E402


class ChuanHoaTest(unittest.TestCase):
    """`normalize_muc_qc` — fail-closed về `full`."""

    def test_chuan_hoa_giu_nguyen_gia_tri_hop_le(self):
        for muc in ("lite", "full", "ultra", "off"):
            with self.subTest(muc=muc):
                self.assertEqual(tdq_state.normalize_muc_qc(muc), muc)

    def test_chuan_hoa_bo_hoa_thuong_va_khoang_trang(self):
        self.assertEqual(tdq_state.normalize_muc_qc("  ULTRA "), "ultra")

    def test_chuan_hoa_gia_tri_la_ve_full(self):
        """Giá trị rác KHÔNG được ném lỗi — nó phải hạ cánh ở mức an toàn nhất, không phải mức
        thấp nhất. Ném lỗi ở đây là chặn cả lệnh `set` của user vì một chữ gõ nhầm."""
        for rac in ("", "   ", "kylanh", "FULLL", "1", "lite;off"):
            with self.subTest(rac=rac):
                self.assertEqual(tdq_state.normalize_muc_qc(rac), "full")

    def test_chuan_hoa_kieu_sai_ve_full(self):
        for rac in (None, 3, ["lite"], {"muc": "lite"}, True):
            with self.subTest(rac=repr(rac)):
                self.assertEqual(tdq_state.normalize_muc_qc(rac), "full")

    def test_chuan_hoa_state_thieu_khoa_ve_full(self):
        self.assertEqual(tdq_state.muc_qc_hieu_luc(None), "full")
        self.assertEqual(tdq_state.muc_qc_hieu_luc({}), "full")
        self.assertEqual(tdq_state.muc_qc_hieu_luc({"muc_qc": "lite"}), "lite")

    def test_chuan_hoa_khoa_co_trong_schema_mac_dinh_full(self):
        mac_dinh = tdq_state.default_state()
        self.assertEqual(mac_dinh["muc_qc"], "full")
        self.assertGreaterEqual(mac_dinh["schema_version"], 6,
                                "thêm khoá mà không tăng schema thì state cũ không ai nhận ra")

    def test_chuan_hoa_hai_thang_doc_lap(self):
        """`muc_gat` và `muc_qc` dùng chung bộ từ nhưng là hai khoá rời — đặt cái này không được
        kéo cái kia đi theo."""
        state = dict(tdq_state.default_state(), muc_gat="ultra", muc_qc="lite")
        self.assertEqual(tdq_state.muc_gat_hieu_luc(state), "ultra")
        self.assertEqual(tdq_state.muc_qc_hieu_luc(state), "lite")


class SetCliTest(unittest.TestCase):
    """Đặt mức qua CLI — đường DUY NHẤT được ghi state."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name
        self.addCleanup(self._tmp.cleanup)
        write_state(self.cwd, active_request="2026-09-23-1148-thu", lane="full", phase="analyze")

    def _doc_state(self):
        with open(os.path.join(self.cwd, "docs", "tdq", "state.json"), encoding="utf-8") as f:
            return json.load(f)

    def test_chuan_hoa_set_ghi_duoc_ba_muc(self):
        for muc in ("lite", "full", "ultra"):
            with self.subTest(muc=muc):
                rc, _, err = run_state_cli(self.cwd, "set", f"muc_qc={muc}")
                self.assertEqual(rc, 0, err)
                self.assertEqual(self._doc_state()["muc_qc"], muc)

    def test_chuan_hoa_set_gia_tri_la_thanh_full_chu_khong_bao_loi(self):
        rc, _, err = run_state_cli(self.cwd, "set", "muc_qc=kylanh")
        self.assertEqual(rc, 0, err)
        self.assertEqual(self._doc_state()["muc_qc"], "full")

    def test_chuan_hoa_off_dat_tay_duoc(self):
        """`off` là giá trị hợp lệ nhưng KHÔNG bao giờ được bày ra trong danh sách hỏi user
        (quyết định 2026-09-23). Đặt tay thì phải chạy."""
        rc, _, err = run_state_cli(self.cwd, "set", "muc_qc=off")
        self.assertEqual(rc, 0, err)
        self.assertEqual(self._doc_state()["muc_qc"], "off")


class HienThiTest(unittest.TestCase):
    """Mức QC phải ĐỌC ĐƯỢC ở đầu ra state, nếu không user không biết request đang ở mức nào."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def test_hien_thi_next_co_dong_muc_qc_o_moi_phase(self):
        for phase in ("idle", "analyze", "spec", "plan", "mode", "implement", "qc", "report"):
            with self.subTest(phase=phase):
                write_state(self.cwd, active_request="2026-09-23-1148-thu", lane="full",
                            phase=phase, muc_qc="ultra")
                rc, out, err = run_state_cli(self.cwd, "next")
                self.assertEqual(rc, 0, err)
                self.assertIn("QC level: ultra", out)

    def test_hien_thi_hai_thang_la_hai_dong_rieng(self):
        """Gộp chung một dòng là mời user nhầm hai thang với nhau."""
        write_state(self.cwd, active_request="2026-09-23-1148-thu", lane="full", phase="spec",
                    muc_gat="lite", muc_qc="ultra")
        _, out, _ = run_state_cli(self.cwd, "next")
        dong = [d for d in out.splitlines() if "level:" in d]
        self.assertEqual(len(dong), 2, out)
        self.assertIn("Lean level: lite", out)
        self.assertIn("QC level: ultra", out)

    def test_hien_thi_get_tra_ve_khoa(self):
        write_state(self.cwd, active_request="2026-09-23-1148-thu", lane="full", phase="spec",
                    muc_qc="lite")
        rc, out, _ = run_state_cli(self.cwd, "get", "muc_qc")
        self.assertEqual(rc, 0)
        self.assertEqual(out.strip(), "lite")

    def test_hien_thi_state_md_co_o_muc_qc(self):
        write_state(self.cwd, active_request="2026-09-23-1148-thu", lane="full", phase="spec",
                    muc_qc="lite")
        run_state_cli(self.cwd, "set", "muc_qc=lite")
        with open(os.path.join(self.cwd, "docs", "tdq", "STATE.md"), encoding="utf-8") as f:
            self.assertIn("| QC level | lite |", f.read())


class LogTest(unittest.TestCase):
    """Log service bật mặc định, tắt bằng TDQ_LOG=0 — yêu cầu đứng của repo."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name
        self.addCleanup(self._tmp.cleanup)
        write_state(self.cwd, active_request="2026-09-23-1148-thu", lane="full", phase="analyze")

    def test_log_bat_mac_dinh_co_timestamp(self):
        _, _, err = run_state_cli(self.cwd, "set", "muc_qc=ultra")
        self.assertRegex(err, r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
        self.assertIn("muc_qc: full → ultra", err, "log phải nói mức đổi từ gì sang gì")

    def test_log_khong_keu_khi_muc_khong_doi(self):
        """Đặt lại đúng mức đang có thì im — log chỉ ghi khi mức THẬT SỰ đổi."""
        run_state_cli(self.cwd, "set", "muc_qc=lite")
        _, _, err = run_state_cli(self.cwd, "set", "muc_qc=lite")
        self.assertNotIn("muc_qc:", err)

    def test_log_tat_duoc_bang_bien_moi_truong(self):
        import os as _os
        import subprocess
        import sys as _sys
        moi_truong = dict(_os.environ, TDQ_PROJECT_DIR=self.cwd, TDQ_LOG="0")
        proc = subprocess.run(
            [_sys.executable, _os.path.join(ROOT, "scripts", "tdq_state.py"),
             "set", "muc_qc=lite"],
            capture_output=True, encoding="utf-8", errors="replace", env=moi_truong, timeout=30)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stderr.strip(), "", "TDQ_LOG=0 phải im hoàn toàn")


if __name__ == "__main__":
    unittest.main()
