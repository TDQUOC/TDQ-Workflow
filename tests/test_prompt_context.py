"""prompt_context.py — nhắc [TDQ:INTAKE] khi KHÔNG có request mở (spec 2026-08-02).

Định nghĩa đóng: request mở = có active_request VÀ phase != idle.
4 case: (a) state None → chỉ INTAKE; (b) thiếu active_request → chỉ INTAKE;
(c) phase idle còn active_request → NEXT + INTAKE, INTAKE nguyên vẹn, tổng ≤ MAX_CHARS;
(d) phase spec (request mở) → KHÔNG có INTAKE.
"""
import tempfile
import unittest

from helper import run_hook, write_state, tdq_state

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


class TestSignalWritten(unittest.TestCase):
    """T1.1-T1.4 (2026-08-04-approval-gate-bug): looks_like_approval() phải lưu
    lại kết quả vào sổ turn (kind="signal") để bash_gate.py đối chiếu sau."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def _signal_rows(self, session):
        rows = tdq_state.turn_log_read(self.cwd, session=session)
        return [r for r in rows if r.get("kind") == "signal"]

    def test_signal_written_matched_and_unmatched(self):
        write_state(self.cwd, active_request="2026-08-04-x", lane="full",
                    phase="spec", spec_file="docs/tdq/spec/x.md")
        _run(self.cwd, "duyệt spec")
        rows = self._signal_rows("s1")
        self.assertEqual(len(rows), 1, rows)
        row = rows[0]
        self.assertEqual(row.get("event"), "approve_pending")
        self.assertEqual(row.get("target"), "spec")
        self.assertTrue(row.get("matched"))

        _run(self.cwd, "tôi góp ý thêm chỗ này")
        rows2 = self._signal_rows("s1")
        self.assertEqual(len(rows2), 1, rows2)
        self.assertFalse(rows2[0].get("matched"))

    def test_signal_mode_conflict(self):
        write_state(self.cwd, active_request="2026-08-04-x", lane="full",
                    phase="plan", spec_file="docs/tdq/spec/x.md", spec_approved=True,
                    plan_file="docs/tdq/plan/x.md")
        write_file_plan_mode(self.cwd, "docs/tdq/plan/x.md", "subagent")
        _run(self.cwd, "duyệt plan mode main")
        rows = self._signal_rows("s1")
        self.assertTrue(rows)
        row = rows[-1]
        self.assertEqual(row.get("target"), "plan")
        self.assertTrue(row.get("matched"))
        self.assertTrue(row.get("mode_conflict"))


class TestModeNaming(unittest.TestCase):
    """Cổng mode nói bằng nhãn người đọc, nhưng vẫn nhận tên máy cũ."""

    def setUp(self):
        import importlib.util
        import os
        import sys
        hooks = os.path.join(tdq_state.__file__, "..", "..", "hooks", "scripts")
        hooks = os.path.normpath(hooks)
        if hooks not in sys.path:
            sys.path.insert(0, hooks)
        self.common = importlib.import_module("_common")
        spec = importlib.util.spec_from_file_location(
            "pc_under_test", os.path.join(hooks, "prompt_context.py"))
        self.pc = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.pc)

    def test_hint_uses_reader_labels(self):
        hint = self.common.approve_hint("mode", "main")
        self.assertIn("inline", hint)
        self.assertIn("sub-agent", hint)
        # Nhãn của mode ĐỀ XUẤT phải là chữ người đọc, không phải định danh máy.
        self.assertIn(tdq_state.mode_label("main"), hint)

    def test_hint_stays_short_enough_to_survive_truncation(self):
        self.assertLessEqual(len(self.common.approve_hint("mode", "subagent")), 240)

    def test_answer_accepts_old_and_new_names(self):
        for said in ("main", "subagent", "inline", "inline implement", "sub-agent",
                     "chọn sub-agent implement"):
            with self.subTest(said=said):
                self.assertTrue(self.pc.looks_like_approval(said, "mode"), said)

    def test_answer_accepts_option_letters(self):
        """Khuôn cổng mode bảo user nhắn "A"/"B" — hook phải nhận đúng thứ nó mời gõ."""
        for said in ("A", "b", " A ", "chọn A", "B nhé"):
            with self.subTest(said=said):
                self.assertTrue(self.pc.looks_like_approval(said, "mode"), said)

    def test_letter_a_means_plan_mode_and_b_the_other(self):
        self.assertEqual(self.pc.mode_from_answer("A", "subagent"), "subagent")
        self.assertEqual(self.pc.mode_from_answer("B", "subagent"), "main")
        self.assertEqual(self.pc.mode_from_answer("B", "main"), "subagent")
        # Tên mode gõ thẳng vẫn thắng chữ cái.
        self.assertEqual(self.pc.mode_from_answer("inline implement", "subagent"), "main")

    def test_answer_rejects_noise(self):
        for said in ("để tôi xem lại đã", "mainline branch nào?", "inlineable",
                     "Ai làm cũng được", "bạn quyết đi"):
            with self.subTest(said=said):
                self.assertFalse(self.pc.looks_like_approval(said, "mode"), said)


def write_file_plan_mode(cwd, rel, mode):
    import os
    path = os.path.join(cwd, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"Mode thực thi: {mode}\n")


if __name__ == "__main__":
    unittest.main()
