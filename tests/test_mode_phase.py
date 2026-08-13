"""Phase `mode` — cổng chọn cách thực thi, tách khỏi cổng duyệt plan.

Bốn bất biến:
1. `PHASE_TABLE["mode"]` có đủ 6 trường và nằm đúng chỗ trong PHASE_ORDER.
2. `approve plan` KHÔNG kèm mode là hợp lệ và dừng ở phase `mode`.
3. `approve plan --mode <x>` bỏ qua cổng, vào thẳng `implement`.
4. Trả lời cổng mode sau đó cũng đẩy sang `implement`.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

from helper import ROOT, tdq_state

STATE_CLI = os.path.join(ROOT, "scripts", "tdq_state.py")


def run(cwd, *args):
    proc = subprocess.run([sys.executable, STATE_CLI, *args], capture_output=True,
                          text=True, timeout=30,
                          env=dict(os.environ, TDQ_PROJECT_DIR=cwd))
    return proc.returncode, proc.stdout.strip()


def read_state(cwd):
    with open(os.path.join(cwd, "docs", "tdq", "state.json"), encoding="utf-8") as f:
        return json.load(f)


class ModePhaseTableTest(unittest.TestCase):
    def test_mode_row_is_complete(self):
        row = tdq_state.PHASE_TABLE["mode"]
        for field in ("entry", "action", "cmd", "checklist", "done_when", "forbidden"):
            with self.subTest(field=field):
                self.assertTrue(row.get(field), f"phase mode thiếu trường {field}")

    def test_mode_sits_between_plan_and_implement(self):
        order = tdq_state.PHASE_ORDER
        self.assertEqual(order.index("mode"), order.index("plan") + 1)
        self.assertEqual(order.index("implement"), order.index("mode") + 1)
        self.assertIn("mode", tdq_state.VALID_PHASES)

    def test_plan_row_no_longer_demands_mode(self):
        plan = tdq_state.PHASE_TABLE["plan"]
        self.assertNotIn("--mode", plan["cmd"], "cổng plan vẫn bắt nói mode")
        self.assertIn("--mode", tdq_state.PHASE_TABLE["mode"]["cmd"])

    def test_mode_row_explains_both_modes(self):
        text = " ".join(tdq_state.PHASE_TABLE["mode"]["checklist"])
        self.assertIn("main =", text)
        self.assertIn("subagent =", text)


class ApproveFlowTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name
        self.addCleanup(self.tmp.cleanup)
        run(self.cwd, "init", "2026-08-13-thu-mode", "full")
        run(self.cwd, "approve", "spec", "--by", "duyệt spec")

    def test_approve_plan_without_mode_stops_at_mode_phase(self):
        rc, _ = run(self.cwd, "approve", "plan", "--by", "duyệt plan")
        self.assertEqual(rc, 0)
        state = read_state(self.cwd)
        self.assertTrue(state["plan_approved"])
        self.assertIsNone(state["implement_mode"])
        self.assertEqual(state["phase"], "mode")

    def test_answering_mode_gate_moves_to_implement(self):
        run(self.cwd, "approve", "plan", "--by", "duyệt plan")
        rc, _ = run(self.cwd, "approve", "plan", "--mode", "subagent", "--by", "subagent")
        self.assertEqual(rc, 0)
        state = read_state(self.cwd)
        self.assertEqual(state["implement_mode"], "subagent")
        self.assertEqual(state["phase"], "implement")

    def test_mode_said_inside_approval_skips_the_gate(self):
        rc, _ = run(self.cwd, "approve", "plan", "--mode", "main", "--by", "duyệt plan mode main")
        self.assertEqual(rc, 0)
        state = read_state(self.cwd)
        self.assertEqual(state["implement_mode"], "main")
        self.assertEqual(state["phase"], "implement")

    def test_next_at_mode_phase_asks_for_mode(self):
        run(self.cwd, "approve", "plan", "--by", "duyệt plan")
        rc, out = run(self.cwd, "next")
        self.assertEqual(rc, 0)
        self.assertIn("phase mode", out)
        self.assertIn("mode", out.lower())


if __name__ == "__main__":
    unittest.main()
