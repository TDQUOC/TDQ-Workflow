"""Hook nhắc `[TDQ:ASK]` — `hooks/scripts/ask_gate.py` (T3.1, yêu cầu 2026-10-03-0732).

Ca gốc: agent dừng giữa implement bằng `AskUserQuestion` để hỏi nâng ngưỡng installer — một câu
hỏi TRONG lượt, nên cổng Stop không thấy. User chọn: chỉ nhắc, không chặn.

Chạy riêng từng nhóm bằng `-k`: `nhac`, `im`, `khong_chan`, `log`.
"""
import io
import json
import os
import sys
import tempfile
import unittest

from helper import ROOT, run_hook

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tdq_state  # noqa: E402

HOOK = "ask_gate.py"
PHIEN = "phien-thu-ask-gate"


class BaseHoi(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cwd = self.tmp.name
        os.makedirs(os.path.join(self.cwd, "docs", "tdq"), exist_ok=True)

    def dat_phase(self, phase, **them):
        state = tdq_state.default_state()
        state.update({"active_request": "2026-10-03-0000-thu", "lane": "full", "phase": phase,
                      "spec_approved": True, "plan_approved": True,
                      "implement_mode": "main"}, **them)
        with io.open(os.path.join(self.cwd, "docs", "tdq", "state.json"), "w",
                     encoding="utf-8") as fh:
            json.dump(state, fh)

    def goi(self, log="0"):
        payload = {"hook_event_name": "PreToolUse", "tool_name": "AskUserQuestion",
                   "tool_input": {"questions": []}, "session_id": PHIEN, "cwd": self.cwd}
        rc, out, err = run_hook(HOOK, payload, env={"TDQ_PROJECT_DIR": self.cwd, "TDQ_LOG": log})
        self.assertEqual(rc, 0, err)
        return out, err


class Nhac(BaseHoi):
    def test_nhac_o_implement(self):
        self.dat_phase("implement")
        out, _ = self.goi()
        ra = json.loads(out)["hookSpecificOutput"]
        self.assertIn("[TDQ:ASK]", ra["additionalContext"])
        self.assertIn("lech add", ra["additionalContext"])
        self.assertIn("pause --loai", ra["additionalContext"], "dòng thứ hai không được bị cắt")

    def test_nhac_o_qc(self):
        self.dat_phase("qc")
        self.assertIn("[TDQ:ASK]", self.goi()[0])

    def test_nhac_mot_lan_moi_luot(self):
        self.dat_phase("implement")
        self.assertTrue(self.goi()[0])
        self.assertEqual(self.goi()[0], "", "nhắc lần hai trong cùng lượt là đốt token vô ích")


class Im(BaseHoi):
    def test_im_o_spec_va_analyze(self):
        for phase in ("analyze", "spec", "plan", "report", "idle"):
            self.dat_phase(phase)
            self.assertEqual(self.goi()[0], "", phase)

    def test_im_khi_da_khai_pause(self):
        self.dat_phase("implement", implement_pause={"loai": "dau-vao-user", "ly_do": "cần API key"})
        self.assertEqual(self.goi()[0], "")

    def test_im_khi_khong_co_state(self):
        self.assertEqual(self.goi()[0], "")


class KhongChan(BaseHoi):
    def test_khong_chan_khong_co_quyet_dinh_quyen(self):
        """User chọn chỉ nhắc; và một "allow" có thể trả lời thay câu hỏi — nên không có cả hai."""
        self.dat_phase("implement")
        ra = json.loads(self.goi()[0])["hookSpecificOutput"]
        self.assertNotIn("permissionDecision", ra)

    def test_khong_chan_ma_co_trong_danh_sach_dong(self):
        sys.path.insert(0, os.path.join(ROOT, "hooks", "scripts"))
        import _common
        self.assertIn("TDQ:ASK", _common.CODES)


class Log(BaseHoi):
    def test_log_tat_duoc(self):
        self.dat_phase("implement")
        self.assertEqual(self.goi(log="0")[1], "")

    def test_log_bat_mac_dinh_co_timestamp(self):
        self.dat_phase("implement")
        self.assertRegex(self.goi(log="1")[1], r"\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\] ask_gate")


if __name__ == "__main__":
    unittest.main()
