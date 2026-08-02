"""prompt_context.py — nhắc [TDQ:INTAKE] khi KHÔNG có request mở (spec 2026-08-02).

Định nghĩa đóng: request mở = có active_request VÀ phase != idle.
4 case: (a) state None → chỉ INTAKE; (b) thiếu active_request → chỉ INTAKE;
(c) phase idle còn active_request → NEXT + INTAKE, INTAKE nguyên vẹn, tổng ≤ MAX_CHARS;
(d) phase spec (request mở) → KHÔNG có INTAKE.
"""
import tempfile
import unittest

from helper import run_hook, write_state

MAX_CHARS = 240
INTAKE = "[TDQ:INTAKE]"


def _run(cwd, prompt="câu hỏi bất kỳ"):
    rc, out, err = run_hook("prompt_context.py", {
        "hook_event_name": "UserPromptSubmit", "cwd": cwd,
        "session_id": "s1", "prompt": prompt})
    return rc, out


class TestIntakeReminder(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def _intake_line(self, out):
        lines = [l for l in out.splitlines() if l.startswith(INTAKE)]
        self.assertEqual(len(lines), 1, out)
        return lines[0]

    def test_a_no_state_prints_only_intake(self):
        rc, out = _run(self.cwd)
        self.assertEqual(rc, 0)
        line = self._intake_line(out)
        self.assertNotIn("[TDQ:NEXT]", out)
        self.assertLessEqual(len(line), 160, line)
        self.assertNotIn("…", line)

    def test_b_state_without_active_request_prints_only_intake(self):
        write_state(self.cwd, active_request=None, lane="full", phase="idle")
        rc, out = _run(self.cwd)
        self.assertEqual(rc, 0)
        self._intake_line(out)
        self.assertNotIn("[TDQ:NEXT]", out)

    def test_c_idle_with_active_request_prints_next_and_intake(self):
        write_state(self.cwd, active_request="2026-08-02-demo", lane="full", phase="idle")
        rc, out = _run(self.cwd)
        self.assertEqual(rc, 0)
        self.assertIn("[TDQ:NEXT]", out)
        line = self._intake_line(out)
        # INTAKE phải nguyên vẹn (không bị _truncate cắt) và tổng ≤ trần
        self.assertNotIn("…", line)
        self.assertLessEqual(len(line), 160, line)
        self.assertLessEqual(len(out), MAX_CHARS, out)

    def test_d_open_request_has_no_intake(self):
        write_state(self.cwd, active_request="2026-08-02-demo", lane="full",
                    phase="spec", spec_file="docs/tdq/spec/x.md")
        rc, out = _run(self.cwd)
        self.assertEqual(rc, 0)
        self.assertNotIn(INTAKE, out)
        self.assertIn("[TDQ:NEXT]", out)


if __name__ == "__main__":
    unittest.main()
