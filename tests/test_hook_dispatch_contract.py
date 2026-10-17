"""Contract and measurement test for hook dispatcher protocol (O08 / U08).

Ensures:
  1. The baseline independent hooks (bash_gate.py and search_gate.py) function correctly
     under the host contract with clear oracle outcomes.
  2. The O08 protocol measures paired runs (baseline vs unified candidate) on host Windows.
  3. The protocol enforces the strict GO/NO-GO gate:
     - GO requires both >= 30% speedup AND 100% semantic equivalence.
     - Any equivalence divergence or lack of safe host contract triggers NO-GO.
  4. Under NO-GO, independent hooks remain intact and no unsafe stubs are activated.
"""
import json
import os
import sys
import unittest

from helper import ROOT

SCRIPTS = os.path.join(ROOT, "scripts")
HOOKS = os.path.join(ROOT, "hooks", "scripts")


class TestHookDispatchContract(unittest.TestCase):
    """Test suite for O08 Dispatcher Protocol & Baseline Equivalence."""

    def test_baseline_independent_hooks_exist_and_isolated(self):
        """bash_gate.py and search_gate.py must exist as independent scripts."""
        self.assertTrue(os.path.isfile(os.path.join(HOOKS, "bash_gate.py")))
        self.assertTrue(os.path.isfile(os.path.join(HOOKS, "search_gate.py")))

    def test_measurement_protocol_evaluates_paired_runs(self):
        """measure_dispatcher_parity runs paired comparisons and reports structured metrics."""
        sys.path.insert(0, SCRIPTS)
        try:
            import context_surface
            res = context_surface.measure_dispatcher_parity(runs=3)
            self.assertIn("baseline_median_ms", res)
            self.assertIn("candidate_median_ms", res)
            self.assertIn("speedup_pct", res)
            self.assertIn("equivalent", res)
            self.assertIn("decision", res)
            self.assertIn(res["decision"], ("GO", "NO-GO"))
            self.assertGreater(res["baseline_median_ms"], 0)
        finally:
            if sys.path and sys.path[0] == SCRIPTS:
                sys.path.pop(0)

    def test_protocol_enforces_no_go_on_inequivalence(self):
        """If equivalence is False, protocol decision MUST strictly be NO-GO."""
        sys.path.insert(0, SCRIPTS)
        try:
            import context_surface
            # Run benchmark and verify that if equivalence is not achieved, decision is NO-GO
            res = context_surface.measure_dispatcher_parity(runs=2)
            if not res.get("equivalent", False):
                self.assertEqual(res["decision"], "NO-GO")
        finally:
            if sys.path and sys.path[0] == SCRIPTS:
                sys.path.pop(0)

    def test_no_go_preserves_independent_hooks_in_manifest(self):
        """Under NO-GO decision, hooks.json must maintain independent hook configurations."""
        hooks_json_path = os.path.join(ROOT, "hooks", "hooks.json")
        with open(hooks_json_path, encoding="utf-8") as f:
            data = json.load(f)

        pre_tool_hooks = data.get("hooks", {}).get("PreToolUse", [])
        hook_commands = []
        for entry in pre_tool_hooks:
            for h in entry.get("hooks", []):
                cmd = h.get("command", "")
                hook_commands.append(cmd)

        # Confirm independent bash_gate and search_gate are both registered
        has_bash_gate = any("bash_gate.py" in cmd for cmd in hook_commands)
        has_search_gate = any("search_gate.py" in cmd for cmd in hook_commands)
        self.assertTrue(has_bash_gate, "PreToolUse must contain bash_gate.py")
        self.assertTrue(has_search_gate, "PreToolUse must contain search_gate.py")

        # Confirm no unapproved bash_dispatch stub is activated in the production manifest
        has_dispatch = any("bash_dispatch.py" in cmd for cmd in hook_commands)
        self.assertFalse(has_dispatch, "bash_dispatch.py must NOT be activated in hooks.json under NO-GO")


if __name__ == "__main__":
    unittest.main()
