"""B1 — approve_gate.py: validate by state + registered detail file."""
import tempfile
import unittest

from helper import run_hook, load_fixture, write_state, read_state, write_file
import tdq_state


def approve(cwd, arg):
    return run_hook("approve_gate.py", load_fixture("approve.json", cwd=cwd, command_args=arg))


class TestApproveGate(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def test_green_spec_sets_detail(self):
        write_state(self.cwd, active_request="r1", lane="full", phase="spec",
                    spec_file="docs/tdq/spec/x.md")
        path = write_file(self.cwd, "docs/tdq/spec/x.md", "# spec noi dung\n")
        rc, out, err = approve(self.cwd, "spec")
        self.assertEqual(rc, 0, err)
        self.assertIn("APPROVED SPEC", out)
        state = read_state(self.cwd)
        self.assertTrue(state["spec_approved"])
        self.assertEqual(state["spec_sha256"], tdq_state.sha256_file(path))
        self.assertIsNotNone(state["spec_approved_at"])

    def test_red_plan_before_spec(self):
        write_state(self.cwd, active_request="r1", lane="full", phase="plan",
                    plan_file="docs/tdq/plan/x.md")
        write_file(self.cwd, "docs/tdq/plan/x.md")
        rc, _, err = approve(self.cwd, "plan")
        self.assertEqual(rc, 2)
        self.assertIn("thứ tự", err)
        self.assertFalse(read_state(self.cwd)["plan_approved"])

    def test_red_spec_file_missing(self):
        write_state(self.cwd, active_request="r1", lane="full",
                    spec_file="docs/tdq/spec/missing.md")
        rc, _, err = approve(self.cwd, "spec")
        self.assertEqual(rc, 2)
        self.assertIn("không tồn tại", err)
        self.assertFalse(read_state(self.cwd)["spec_approved"])

    def test_red_spec_file_empty(self):
        write_state(self.cwd, active_request="r1", lane="full",
                    spec_file="docs/tdq/spec/empty.md")
        write_file(self.cwd, "docs/tdq/spec/empty.md", "")
        rc, _, err = approve(self.cwd, "spec")
        self.assertEqual(rc, 2)
        self.assertIn("rỗng", err)

    def test_red_spec_not_registered(self):
        write_state(self.cwd, active_request="r1", lane="full")
        rc, _, err = approve(self.cwd, "spec")
        self.assertEqual(rc, 2)
        self.assertIn("đăng ký", err)

    def test_red_no_active_request(self):
        rc, _, err = approve(self.cwd, "spec")
        self.assertEqual(rc, 2)
        self.assertIn("request", err.lower())

    def test_red_already_approved(self):
        write_state(self.cwd, active_request="r1", lane="full",
                    spec_file="docs/tdq/spec/x.md", spec_approved=True,
                    spec_approved_at="2026-07-27T10:00:00+07:00")
        write_file(self.cwd, "docs/tdq/spec/x.md")
        rc, _, err = approve(self.cwd, "spec")
        self.assertEqual(rc, 2)
        self.assertIn("rồi", err)

    def test_green_plan_after_spec(self):
        write_state(self.cwd, active_request="r1", lane="full", phase="plan",
                    spec_file="docs/tdq/spec/x.md", spec_approved=True,
                    spec_sha256="abc", spec_approved_at="2026-07-27T10:00:00+07:00",
                    plan_file="docs/tdq/plan/x.md")
        write_file(self.cwd, "docs/tdq/spec/x.md")
        write_file(self.cwd, "docs/tdq/plan/x.md", "# plan\n")
        rc, out, err = approve(self.cwd, "plan")
        self.assertEqual(rc, 0, err)
        self.assertIn("APPROVED PLAN", out)
        state = read_state(self.cwd)
        self.assertTrue(state["plan_approved"])
        self.assertIsNotNone(state["plan_sha256"])

    def test_green_quick(self):
        write_state(self.cwd, active_request="r1", lane="quick")
        rc, out, err = approve(self.cwd, "quick")
        self.assertEqual(rc, 0, err)
        self.assertIn("workinglog", out)
        self.assertTrue(read_state(self.cwd)["quick_approved"])

    def test_red_quick_wrong_lane(self):
        write_state(self.cwd, active_request="r1", lane="full")
        rc, _, err = approve(self.cwd, "quick")
        self.assertEqual(rc, 2)
        self.assertIn("lane", err)
        self.assertFalse(read_state(self.cwd)["quick_approved"])

    def test_red_bad_argument(self):
        write_state(self.cwd, active_request="r1", lane="full")
        rc, _, err = approve(self.cwd, "banana")
        self.assertEqual(rc, 2)
        self.assertIn("Cách dùng", err)


if __name__ == "__main__":
    unittest.main()
