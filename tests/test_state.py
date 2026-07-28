"""A3 — tdq_state.py: default schema, CLI, protected keys, atomic write."""
import json
import os
import tempfile
import unittest

import helper
from helper import run_state_cli, read_state, write_state
import tdq_state


class TestState(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def test_load_missing_returns_none(self):
        self.assertIsNone(tdq_state.load(self.cwd))

    def test_default_schema_keys(self):
        state = tdq_state.default_state()
        for key in ("active_request", "lane", "phase", "spec_file", "spec_approved",
                    "spec_sha256", "spec_approved_at", "plan_file", "plan_approved",
                    "plan_sha256", "plan_approved_at", "quick_approved",
                    "quick_approved_at", "implement_mode", "updated_at"):
            self.assertIn(key, state)
        self.assertEqual(state["phase"], "idle")

    def test_cli_init_and_get(self):
        rc, out, _ = run_state_cli(self.cwd, "init", "2026-07-27-demo", "full")
        self.assertEqual(rc, 0)
        state = read_state(self.cwd)
        self.assertEqual(state["active_request"], "2026-07-27-demo")
        self.assertEqual(state["lane"], "full")
        rc, out, _ = run_state_cli(self.cwd, "get", "lane")
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(out), "full")

    def test_cli_set_roundtrip(self):
        run_state_cli(self.cwd, "init", "r1", "full")
        rc, _, _ = run_state_cli(self.cwd, "set", "phase=spec", "spec_file=docs/tdq/spec/x.md")
        self.assertEqual(rc, 0)
        state = read_state(self.cwd)
        self.assertEqual(state["phase"], "spec")
        self.assertEqual(state["spec_file"], "docs/tdq/spec/x.md")

    def test_cli_rejects_protected_keys(self):
        run_state_cli(self.cwd, "init", "r1", "full")
        for pair in ("spec_approved=true", "plan_approved=true", "quick_approved=true",
                     "spec_sha256=abc", "plan_approved_at=now", "implement_mode=main"):
            rc, _, err = run_state_cli(self.cwd, "set", pair)
            self.assertEqual(rc, 1, pair)
            self.assertIn("bảo vệ", err)
        state = read_state(self.cwd)
        self.assertFalse(state["spec_approved"])
        self.assertFalse(state["plan_approved"])
        self.assertFalse(state["quick_approved"])

    def test_cli_rejects_invalid_lane_phase_key(self):
        run_state_cli(self.cwd, "init", "r1")
        self.assertEqual(run_state_cli(self.cwd, "set", "lane=turbo")[0], 1)
        self.assertEqual(run_state_cli(self.cwd, "set", "phase=deploy")[0], 1)
        self.assertEqual(run_state_cli(self.cwd, "set", "nonexistent=1")[0], 1)

    def test_atomic_overwrite_keeps_valid_json(self):
        write_state(self.cwd, active_request="r1", lane="full")
        state = tdq_state.load(self.cwd)
        state["phase"] = "plan"
        tdq_state.save(self.cwd, state)
        with open(os.path.join(self.cwd, "docs", "tdq", "state.json"), encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["phase"], "plan")
        self.assertIsNotNone(data["updated_at"])
        leftovers = [n for n in os.listdir(os.path.join(self.cwd, "docs", "tdq")) if n.startswith(".state-")]
        self.assertEqual(leftovers, [])


if __name__ == "__main__":
    unittest.main()
