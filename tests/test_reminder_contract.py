"""Hợp đồng Formatter denial lặp theo reason/evidence/turn — O07 (T4.4).

Quy tắc:
1. First occurrence hoặc new reason/evidence: phát toàn bộ hướng dẫn remediation đầy đủ.
2. Repeat occurrence trong cùng turn: phát bản rút gọn (tiết kiệm token/bytes) nhưng
   bảo toàn phương thức gỡ (actionable recovery).
3. Không bao giờ biến deny thành allow; luôn giữ permissionDecision="deny".
4. Mọi lần chặn đều ghi sự kiện kind="block" vào turn ledger (không xóa, không bỏ qua).
5. Khi sang turn mới (turn log cleared): đếm lặp được reset về 0.
6. Tương thích hoàn toàn với cơ chế readiness breaker và exit code 0.
"""
import io
import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
HOOKS = os.path.join(ROOT, "hooks", "scripts")
SCRIPTS = os.path.join(ROOT, "scripts")
if HOOKS not in sys.path:
    sys.path.insert(0, HOOKS)
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

import _common
import tdq_state
from helper import run_hook


class ReminderContractTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name
        self.addCleanup(self.tmp.cleanup)
        self.session = "test-session-reminder"

    def _call_block(self, code, lines, day_du=True):
        payload = {"cwd": self.cwd, "session_id": self.session, "hook_event_name": "PreToolUse"}
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            with self.assertRaises(SystemExit) as cm:
                _common.block(self.cwd, payload, code, lines, day_du=day_du)
            self.assertEqual(cm.exception.code, 0)
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout
        return json.loads(output)["hookSpecificOutput"]

    def test_first_denial_emits_full_remediation(self):
        lines = [
            "Chặn tìm code trước khi hỏi tầng khái niệm (spec 2026-10-03-0015 §3).",
            "Chạy graphify hoặc LSP trước:",
            '  graphify query "câu hỏi"',
            "Hoặc gọi LSP find_symbol/find_references trước.",
        ]
        out = self._call_block("TDQ:SEARCH", lines, day_du=True)
        self.assertEqual(out["permissionDecision"], "deny")
        reason = out["permissionDecisionReason"]
        self.assertIn("[TDQ:SEARCH]", reason)
        self.assertNotIn("(lặp)", reason)
        self.assertIn("Chặn tìm code trước khi hỏi", reason)
        self.assertIn("graphify query", reason)

    def test_repeat_denial_same_turn_is_shortened_and_preserves_recovery(self):
        lines = [
            "Chặn tìm code trước khi hỏi tầng khái niệm (spec 2026-10-03-0015 §3).",
            "Chạy graphify hoặc LSP trước:",
            '  graphify query "câu hỏi"',
            "Hoặc gọi LSP find_symbol/find_references trước.",
        ]
        out1 = self._call_block("TDQ:SEARCH", lines, day_du=True)
        out2 = self._call_block("TDQ:SEARCH", lines, day_du=True)
        out3 = self._call_block("TDQ:SEARCH", lines, day_du=True)

        reason1 = out1["permissionDecisionReason"]
        reason2 = out2["permissionDecisionReason"]
        reason3 = out3["permissionDecisionReason"]

        # Quyết định không đổi: luôn luôn là deny
        self.assertEqual(out1["permissionDecision"], "deny")
        self.assertEqual(out2["permissionDecision"], "deny")
        self.assertEqual(out3["permissionDecision"], "deny")

        # Lần 2 và lần 3 mang nhãn lặp
        self.assertIn("(lặp)", reason2)
        self.assertIn("(lặp x3)", reason3)

        # Lần 2 ngắn hơn lần 1 (tiết kiệm bytes/token)
        self.assertLess(len(reason2), len(reason1))
        self.assertLess(len(reason3), len(reason1))

        # Nhưng vẫn bảo toàn hành động gỡ (recovery path)
        self.assertIn("graphify query", reason2)
        self.assertIn("Gỡ nhanh:", reason2)

    def test_repeat_denial_records_block_event_in_ledger_with_metadata(self):
        lines = ["Đang bị chặn vì vi phạm luật.", "Chạy lệnh fix."]
        self._call_block("TDQ:TICK", lines)
        self._call_block("TDQ:TICK", lines)

        rows = tdq_state.turn_log_read(self.cwd, session=self.session)
        block_rows = [r for r in rows if r.get("kind") == "block"]
        self.assertEqual(len(block_rows), 2)
        self.assertEqual(block_rows[0]["repeat_count"], 0)
        self.assertEqual(block_rows[1]["repeat_count"], 1)
        self.assertEqual(block_rows[0]["code"], "TDQ:TICK")
        self.assertEqual(block_rows[1]["code"], "TDQ:TICK")

    def test_new_reason_or_evidence_emits_full_remediation(self):
        lines_a = ["Lý do A.", "Chạy cách A."]
        lines_b = ["Lý do B hoàn toàn mới.", "Chạy cách B."]

        out_a = self._call_block("TDQ:LSP", lines_a)
        out_b = self._call_block("TDQ:LSP", lines_b)

        # Lý do B là new evidence, nên không bị đánh dấu (lặp) và được phát đầy đủ
        self.assertNotIn("(lặp)", out_a["permissionDecisionReason"])
        self.assertNotIn("(lặp)", out_b["permissionDecisionReason"])
        self.assertIn("Lý do B hoàn toàn mới", out_b["permissionDecisionReason"])

    def test_different_code_in_same_turn_emits_full_remediation(self):
        lines1 = ["Chặn code 1.", "Fix 1."]
        lines2 = ["Chặn code 2.", "Fix 2."]

        out1 = self._call_block("TDQ:SEARCH", lines1)
        out2 = self._call_block("TDQ:DOC", lines2)

        self.assertNotIn("(lặp)", out1["permissionDecisionReason"])
        self.assertNotIn("(lặp)", out2["permissionDecisionReason"])

    def test_turn_clear_resets_repetition_state(self):
        lines = ["Chặn luật.", "Lệnh gỡ."]
        self._call_block("TDQ:SEARCH", lines)
        out2 = self._call_block("TDQ:SEARCH", lines)
        self.assertIn("(lặp)", out2["permissionDecisionReason"])

        # Sang turn mới
        tdq_state.turn_log_clear(self.cwd, session=self.session)

        out3 = self._call_block("TDQ:SEARCH", lines)
        # Reset về 0: full remediation
        self.assertNotIn("(lặp)", out3["permissionDecisionReason"])

    def test_day_du_false_trim_preserves_cap(self):
        lines = [
            "Chặn do chưa tick task trong kế hoạch.",
            "Lệnh: tick task bằng cách cập nhật kế hoạch.",
            "Ghi chú: tiếp tục implement sau khi tick.",
        ]
        out1 = self._call_block("TDQ:TICK", lines, day_du=False)
        out2 = self._call_block("TDQ:TICK", lines, day_du=False)

        reason1 = out1["permissionDecisionReason"]
        reason2 = out2["permissionDecisionReason"]

        self.assertLessEqual(len(reason1), _common.MAX_REMIND_CHARS)
        self.assertLessEqual(len(reason2), _common.MAX_REMIND_CHARS)
        self.assertLessEqual(len(reason1.splitlines()), _common.MAX_REMIND_LINES)
        self.assertLessEqual(len(reason2.splitlines()), _common.MAX_REMIND_LINES)


class SearchGateDenialRepeatTest(unittest.TestCase):
    """Kiểm chứng tích hợp qua search_gate.py thật."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name
        self.addCleanup(self.tmp.cleanup)
        os.makedirs(os.path.join(self.cwd, "docs", "tdq"), exist_ok=True)
        with open(os.path.join(self.cwd, "docs", "tdq", "state.json"), "w", encoding="utf-8") as f:
            json.dump({"active_request": "2026-10-17-test-repeat", "phase": "implement"}, f)

    def test_search_gate_allows_free_search_in_analyze_phase(self):
        with open(os.path.join(self.cwd, "docs", "tdq", "state.json"), "w", encoding="utf-8") as f:
            json.dump({"active_request": "2026-10-17-test-repeat", "phase": "analyze"}, f)
        payload = {
            "session_id": "test-search-analyze",
            "cwd": self.cwd,
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": 'grep -rn "fileHandle" .'},
        }
        rc, out, _ = run_hook("search_gate.py", payload, env={"TDQ_PROJECT_DIR": self.cwd, "TDQ_LOG": "0"})
        self.assertEqual(rc, 0)
        self.assertEqual(out.strip(), "")

    def test_search_gate_repeat_denial_shorter_and_preserves_recovery(self):
        payload = {
            "session_id": "test-search-repeat",
            "cwd": self.cwd,
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": 'grep -rn "fileHandle" .'},
        }
        rc1, out1, _ = run_hook("search_gate.py", payload, env={"TDQ_PROJECT_DIR": self.cwd, "TDQ_LOG": "0"})
        rc2, out2, _ = run_hook("search_gate.py", payload, env={"TDQ_PROJECT_DIR": self.cwd, "TDQ_LOG": "0"})

        self.assertEqual(rc1, 0)
        self.assertEqual(rc2, 0)

        goi1 = json.loads(out1)["hookSpecificOutput"]
        goi2 = json.loads(out2)["hookSpecificOutput"]

        self.assertEqual(goi1["permissionDecision"], "deny")
        self.assertEqual(goi2["permissionDecision"], "deny")

        reason1 = goi1["permissionDecisionReason"]
        reason2 = goi2["permissionDecisionReason"]

        self.assertIn("TDQ:SEARCH", reason1)
        self.assertIn("TDQ:SEARCH", reason2)
        self.assertIn("(lặp)", reason2)
        self.assertLess(len(reason2), len(reason1))


if __name__ == "__main__":
    unittest.main()
