"""Test contract cho approval CLI, descriptor snapshot, version, và validation (O01 / U01)."""
import json
import os
import tempfile
import unittest

from helper import run_state_cli, read_state, write_state
import tdq_state


class TestApprovalContract(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name
        self.spec_file = os.path.join(self.cwd, "docs", "tdq", "spec", "2026-10-17-1000-demo.md")
        self.plan_file = os.path.join(self.cwd, "docs", "tdq", "plan", "2026-10-17-1000-demo.md")
        os.makedirs(os.path.dirname(self.spec_file), exist_ok=True)
        os.makedirs(os.path.dirname(self.plan_file), exist_ok=True)
        with open(self.spec_file, "w", encoding="utf-8") as f:
            f.write("# SPEC\n\n## 1. Mục tiêu\nNội dung spec\n")
        with open(self.plan_file, "w", encoding="utf-8") as f:
            f.write("# PLAN\n\n## 1. Công việc\nNội dung plan\n")

    def tearDown(self):
        self._tmp.cleanup()

    def _init_full(self):
        run_state_cli(self.cwd, "init", "2026-10-17-1000-demo", "full")
        run_state_cli(self.cwd, "set", f"spec_file=docs/tdq/spec/2026-10-17-1000-demo.md")
        run_state_cli(self.cwd, "set", f"plan_file=docs/tdq/plan/2026-10-17-1000-demo.md")

    def test_approve_refuses_when_no_active_request(self):
        rc, out, err = run_state_cli(self.cwd, "approve", "spec", "--strict", "--by", "duyệt spec")
        self.assertNotEqual(rc, 0)
        self.assertIn("No TDQ request is open", err)
        state = read_state(self.cwd)
        self.assertFalse((state or {}).get("spec_approved", False))

    def test_approve_refuses_wrong_lane(self):
        run_state_cli(self.cwd, "init", "2026-10-17-1000-demo", "quick")
        rc, out, err = run_state_cli(self.cwd, "approve", "spec", "--strict", "--by", "duyệt spec")
        self.assertNotEqual(rc, 0)
        self.assertIn("lane quick", err)
        state = read_state(self.cwd)
        self.assertFalse(state["spec_approved"])

    def test_approve_plan_refuses_before_spec_approved(self):
        self._init_full()
        rc, out, err = run_state_cli(self.cwd, "approve", "plan", "--strict", "--mode", "main", "--by", "duyệt plan")
        self.assertNotEqual(rc, 0)
        self.assertIn("no spec approval is recorded", err)
        state = read_state(self.cwd)
        self.assertFalse(state["plan_approved"])

    def test_approve_refuses_unregistered_file(self):
        run_state_cli(self.cwd, "init", "2026-10-17-1000-demo", "full")
        rc, out, err = run_state_cli(self.cwd, "approve", "spec", "--strict", "--by", "duyệt spec")
        self.assertNotEqual(rc, 0)
        self.assertIn("spec_file is not registered", err)
        state = read_state(self.cwd)
        self.assertFalse(state["spec_approved"])

    def test_approve_refuses_missing_or_unreadable_file(self):
        run_state_cli(self.cwd, "init", "2026-10-17-1000-demo", "full")
        run_state_cli(self.cwd, "set", "spec_file=docs/tdq/spec/nonexistent.md")
        rc, out, err = run_state_cli(self.cwd, "approve", "spec", "--strict", "--by", "duyệt spec")
        self.assertNotEqual(rc, 0)
        self.assertIn("Cannot read", err)
        state = read_state(self.cwd)
        self.assertFalse(state["spec_approved"])

    def test_approve_refuses_hash_mismatch(self):
        self._init_full()
        rc, out, err = run_state_cli(
            self.cwd, "approve", "spec", "--by", "duyệt spec",
            "--expected-sha", "0000000000000000000000000000000000000000000000000000000000000000"
        )
        self.assertNotEqual(rc, 0)
        self.assertIn("mismatch", err.lower())
        state = read_state(self.cwd)
        self.assertFalse(state["spec_approved"])

    def test_approve_records_descriptor_with_snapshot_and_expected_sha(self):
        self._init_full()
        expected_sha = tdq_state.sha256_noi_dung(self.spec_file)
        rc, out, err = run_state_cli(
            self.cwd, "approve", "spec", "--by", "duyệt spec",
            "--expected-sha", expected_sha
        )
        self.assertEqual(rc, 0, err)
        state = read_state(self.cwd)
        self.assertTrue(state["spec_approved"])
        self.assertEqual(state["spec_sha256"], expected_sha)
        self.assertIn("spec_descriptor", state)
        desc = state["spec_descriptor"]
        self.assertEqual(desc["target"], "spec")
        self.assertEqual(desc["request"], "2026-10-17-1000-demo")
        self.assertEqual(desc["lane"], "full")
        self.assertEqual(desc["file"], "docs/tdq/spec/2026-10-17-1000-demo.md")
        self.assertEqual(desc["sha256"], expected_sha)
        self.assertEqual(desc["by"], "duyệt spec")
        self.assertEqual(desc["assurance"], "cli-verified")
        self.assertEqual(desc["version"], 1)

    def test_reapproval_during_qc_is_permitted(self):
        self._init_full()
        run_state_cli(self.cwd, "approve", "spec", "--by", "duyệt spec")
        run_state_cli(self.cwd, "approve", "plan", "--mode", "main", "--by", "duyệt plan")
        run_state_cli(self.cwd, "set", "phase=qc")
        with open(self.spec_file, "a", encoding="utf-8") as f:
            f.write("\n## 7. Cập nhật trong lúc QC\nThêm ghi chú\n")
        new_sha = tdq_state.sha256_noi_dung(self.spec_file)
        rc, out, err = run_state_cli(self.cwd, "approve", "spec", "--by", "re-approve spec trong qc")
        self.assertEqual(rc, 0, err)
        state = read_state(self.cwd)
        self.assertEqual(state["spec_sha256"], new_sha)
        self.assertEqual(state["spec_descriptor"]["version"], 2)


if __name__ == "__main__":
    unittest.main()
