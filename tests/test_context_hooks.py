"""session_start.py + prompt_context.py (0.3.0) — bơm context theo state."""
import datetime
import tempfile
import unittest

import importlib.util
import os

from helper import (HOOKS, run_hook, load_fixture, write_state, write_file,
                    tdq_state)


def now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


class TestSessionStart(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def test_active_request_prints_next_and_rule(self):
        write_state(self.cwd, active_request="2026-07-27-demo", lane="full", phase="spec",
                    spec_file="docs/tdq/spec/x.md")
        rc, out, _ = run_hook("session_start.py", {"cwd": self.cwd, "session_id": "s1"})
        self.assertEqual(rc, 0)
        self.assertIn("[TDQ:NEXT]", out)
        self.assertIn("2026-07-27-demo", out)
        self.assertIn("Việc tiếp theo", out)
        self.assertIn("[TDQ] Luật", out)          # instruction: nghe theo mã của hook
        self.assertLessEqual(len(out.splitlines()), 12)   # trần spec §2.7
        self.assertLessEqual(len(out), 600)

    def test_never_truncated_in_any_phase(self):
        """Trần 600 ký tự không được cắt mất dòng luật hay dòng lệnh."""
        for phase in ("analyze", "spec", "plan", "implement", "qc", "report"):
            with self.subTest(phase=phase):
                write_state(self.cwd, active_request="2026-07-27-mot-request-ten-kha-dai",
                            lane="full", phase=phase, spec_approved=True, plan_approved=True,
                            spec_file="docs/tdq/spec/x.md", plan_file="docs/tdq/plan/x.md")
                rc, out, _ = run_hook("session_start.py", {"cwd": self.cwd, "session_id": "s1"})
                self.assertNotIn("…", out, phase)
                self.assertIn("[TDQ] Luật", out)
                self.assertIn("Lệnh:", out)
                self.assertIn("Xong khi:", out)
                self.assertLessEqual(len(out), 600, phase)
                self.assertLessEqual(len(out.splitlines()), 12, phase)

    def test_no_state_still_guides(self):
        rc, out, _ = run_hook("session_start.py", {"cwd": self.cwd, "session_id": "s1"})
        self.assertEqual(rc, 0)
        self.assertIn("[TDQ:NEXT]", out)          # chưa có request → hướng dẫn mở request
        self.assertLessEqual(len(out.splitlines()), 12)


class TestTruncation(unittest.TestCase):
    """A22 — cắt MAX_CHARS không được đứt giữa inline-code (nửa lệnh = lệnh sai)."""

    @classmethod
    def setUpClass(cls):
        import sys
        sys.path.insert(0, HOOKS)  # prompt_context import _common cạnh nó
        cls.addClassCleanup(sys.path.remove, HOOKS)
        spec = importlib.util.spec_from_file_location(
            "prompt_context_mod", os.path.join(HOOKS, "prompt_context.py"))
        cls.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.mod)

    def test_truncate_backs_off_before_open_backtick(self):
        text = ("x" * 230
                + " chạy `python3 scripts/tdq_state.py approve spec` xong")
        out = self.mod._truncate(text)
        self.assertLessEqual(len(out), 240)
        self.assertEqual(out.count("`") % 2, 0, out)
        self.assertNotIn("`python3", out)

    def test_truncate_short_text_untouched(self):
        self.assertEqual(self.mod._truncate("ngắn"), "ngắn")

    def test_truncate_outside_inline_code_keeps_closed_span(self):
        text = "`cmd ok` " + "y" * 300
        out = self.mod._truncate(text)
        self.assertLessEqual(len(out), 240)
        self.assertIn("`cmd ok`", out)


class TestPromptContext(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def ctx(self, prompt="tiếp tục", session="s1"):
        payload = load_fixture("prompt.json", cwd=self.cwd, session_id=session)
        payload["prompt"] = prompt
        return run_hook("prompt_context.py", payload)

    def assert_budget(self, out):
        self.assertLessEqual(len(out.splitlines()), 3)
        self.assertLessEqual(len(out), 240)

    def test_pending_spec_not_an_approval_prompt(self):
        write_state(self.cwd, active_request="r1", lane="full", phase="spec",
                    spec_file="docs/tdq/spec/x.md")
        rc, out, _ = self.ctx("tiếp tục")
        self.assertEqual(rc, 0)
        self.assertIn("[TDQ:NEXT]", out)
        self.assertIn("[TDQ:APPROVE]", out)
        self.assertIn("KHÔNG rõ", out)
        self.assertIn("HỎI", out)
        self.assert_budget(out)

    def test_pending_spec_with_real_approval(self):
        write_state(self.cwd, active_request="r1", lane="full", phase="spec",
                    spec_file="docs/tdq/spec/x.md")
        rc, out, _ = self.ctx("duyệt spec")
        self.assertIn("approve spec", out)
        self.assertIn("--by", out)
        self.assert_budget(out)

    def test_quick_unapproved(self):
        write_state(self.cwd, active_request="r1", lane="quick")
        rc, out, _ = self.ctx("duyệt quick")
        self.assertIn("approve quick", out)
        self.assertIn("--by", out)

    def test_plan_approval_captures_mode(self):
        write_state(self.cwd, active_request="r1", lane="full", phase="plan",
                    spec_file="docs/tdq/spec/x.md", spec_approved=True,
                    spec_sha256="abc", spec_approved_at=now_iso(),
                    plan_file="docs/tdq/plan/x.md")
        rc, out, _ = self.ctx("duyệt plan mode main")
        self.assertIn("approve plan", out)
        self.assertIn("--mode main", out)

    def test_plan_approval_captures_mode_external(self):
        write_state(self.cwd, active_request="r1", lane="full",
                    spec_approved=True, phase="plan",
                    spec_file="docs/tdq/spec/r1.md", plan_file="docs/tdq/plan/r1.md")
        rc, out, _ = self.ctx("duyệt plan mode external")
        self.assertEqual(rc, 0)
        self.assertIn("--mode external", out)

    def test_plan_approval_without_mode_leaves_placeholder(self):
        write_state(self.cwd, active_request="r1", lane="full", phase="plan",
                    spec_file="docs/tdq/spec/x.md", spec_approved=True,
                    spec_sha256="abc", spec_approved_at=now_iso(),
                    plan_file="docs/tdq/plan/x.md")
        rc, out, _ = self.ctx("duyệt plan")
        self.assertIn("--mode <main|subagent|external>", out)

    def test_quick_approved_only_next_line(self):
        write_state(self.cwd, active_request="r1", lane="quick",
                    quick_approved=True, quick_approved_at=now_iso())
        rc, out, _ = self.ctx()
        self.assertEqual(len(out.splitlines()), 1)
        self.assertIn("[TDQ:NEXT]", out)
        self.assertNotIn("[TDQ:APPROVE]", out)

    def test_no_request_silent(self):
        rc, out, _ = self.ctx()
        self.assertEqual(rc, 0)
        self.assertEqual(out, "")

    def test_full_implement_phase_line(self):
        spec = write_file(self.cwd, "docs/tdq/spec/x.md", "# spec\n")
        write_state(self.cwd, active_request="r1", lane="full", phase="implement",
                    spec_file="docs/tdq/spec/x.md", spec_approved=True,
                    spec_sha256=tdq_state.sha256_file(spec), spec_approved_at=now_iso(),
                    plan_file="docs/tdq/plan/x.md", plan_approved=True,
                    plan_sha256="p", plan_approved_at=now_iso())
        rc, out, _ = self.ctx()
        self.assertIn("phase implement", out)

    def test_next_line_names_open_request_and_project(self):
        write_state(self.cwd, active_request="r1", lane="full", phase="spec",
                    spec_file="docs/tdq/spec/x.md")
        rc, out, _ = self.ctx()
        self.assertIn("r1", out)
        self.assertIn("Project:", out)

    def test_spec_drift_warning(self):
        write_file(self.cwd, "docs/tdq/spec/x.md", "# changed\n")
        write_state(self.cwd, active_request="r1", lane="full", phase="implement",
                    spec_file="docs/tdq/spec/x.md", spec_approved=True,
                    spec_sha256="deadbeef", spec_approved_at=now_iso(),
                    plan_file="docs/tdq/plan/x.md", plan_approved=True,
                    plan_sha256="p", plan_approved_at=now_iso())
        rc, out, _ = self.ctx()
        self.assertIn("sha256 lệch", out)

    def test_clears_previous_turn_rows(self):
        write_state(self.cwd, active_request="r1", lane="quick",
                    quick_approved=True, quick_approved_at=now_iso())
        tdq_state.turn_log_append(self.cwd, "observe", session="s1", event="edit", path="a.py")
        self.ctx(session="s1")
        rows = tdq_state.turn_log_read(self.cwd, session="s1")
        # sổ chỉ còn ảnh chụp đầu turn mới, không còn dấu vết turn trước
        self.assertEqual([r["kind"] for r in rows], ["turn_start"])


if __name__ == "__main__":
    unittest.main()
