"""B4 — session_start.py + prompt_context.py: context injection per state."""
import datetime
import tempfile
import unittest

from helper import run_hook, load_fixture, write_state, write_file
import tdq_state


def now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


class TestSessionStart(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def test_active_request_max_3_lines(self):
        write_state(self.cwd, active_request="2026-07-27-demo", lane="full", phase="spec",
                    spec_file="docs/tdq/spec/x.md")
        rc, out, _ = run_hook("session_start.py", {"cwd": self.cwd})
        self.assertEqual(rc, 0)
        self.assertIn("[TDQ]", out)
        self.assertLessEqual(len(out.splitlines()), 3)
        self.assertIn("tdq-approve spec", out)

    def test_no_state_silent(self):
        rc, out, _ = run_hook("session_start.py", {"cwd": self.cwd})
        self.assertEqual(rc, 0)
        self.assertEqual(out, "")


class TestPromptContext(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def ctx(self):
        return run_hook("prompt_context.py", load_fixture("prompt.json", cwd=self.cwd))

    def test_full_pending_spec_approval(self):
        write_state(self.cwd, active_request="r1", lane="full", phase="spec",
                    spec_file="docs/tdq/spec/x.md")
        rc, out, _ = self.ctx()
        self.assertEqual(rc, 0)
        self.assertLessEqual(len(out.splitlines()), 1)
        self.assertIn("tdq-approve spec", out)

    def test_quick_unapproved(self):
        write_state(self.cwd, active_request="r1", lane="quick")
        rc, out, _ = self.ctx()
        self.assertIn("quick", out)

    def test_quick_approved_silent(self):
        write_state(self.cwd, active_request="r1", lane="quick",
                    quick_approved=True, quick_approved_at=now_iso())
        rc, out, _ = self.ctx()
        self.assertEqual(out, "")

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
        self.assertIn("Phase implement", out)

    def test_spec_drift_warning(self):
        write_file(self.cwd, "docs/tdq/spec/x.md", "# changed\n")
        write_state(self.cwd, active_request="r1", lane="full", phase="implement",
                    spec_file="docs/tdq/spec/x.md", spec_approved=True,
                    spec_sha256="deadbeef", spec_approved_at=now_iso(),
                    plan_file="docs/tdq/plan/x.md", plan_approved=True,
                    plan_sha256="p", plan_approved_at=now_iso())
        rc, out, _ = self.ctx()
        self.assertIn("sha256 lệch", out)


if __name__ == "__main__":
    unittest.main()
