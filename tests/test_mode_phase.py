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
        self.assertIn("inline implement", text)
        self.assertIn("sub-agent implement", text)

    def test_mode_row_demands_reason_analysis(self):
        """Cổng mode phải bắt trình phân tích lý do, không chỉ nêu suông tên mode."""
        text = " ".join(tdq_state.PHASE_TABLE["mode"]["checklist"])
        self.assertIn("grounded IN THE PLAN", text)


class ModeLabelTest(unittest.TestCase):
    """Nhãn hiển thị tách khỏi định danh máy, y hệt cặp lane_label/LANE_LABELS."""

    def test_label_for_each_mode(self):
        self.assertEqual(tdq_state.mode_label("main"), "inline implement")
        self.assertEqual(tdq_state.mode_label("subagent"),
                         "sub-agent implement")

    def test_label_is_display_layer_not_validator(self):
        # Mode lạ trả lại nguyên chuỗi, None trả rỗng — in ra xấu còn hơn nổ.
        self.assertEqual(tdq_state.mode_label("xyz"), "xyz")
        self.assertEqual(tdq_state.mode_label(None), "")

    def test_normalize_accepts_old_and_new_names(self):
        cases = {
            "main": "main", "inline": "main", "inline implement": "main",
            "inline-implement": "main", "  INLINE  ": "main",
            "subagent": "subagent", "sub-agent": "subagent",
            "sub agent": "subagent", "sub-agent implement": "subagent",
        }
        for raw, want in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(tdq_state.normalize_mode(raw), want)

    def test_normalize_rejects_junk(self):
        for raw in ("xyz", "", None, 5):
            with self.subTest(raw=raw):
                self.assertIsNone(tdq_state.normalize_mode(raw))


class ApproveFlowTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name
        self.addCleanup(self.tmp.cleanup)
        run(self.cwd, "init", "2026-08-13-0900-thu-mode", "full")
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

    def test_new_mode_name_maps_to_machine_value(self):
        """User gõ nhãn mới ở cổng mode; state vẫn lưu định danh máy cũ."""
        run(self.cwd, "approve", "plan", "--by", "duyệt plan")
        rc, _ = run(self.cwd, "approve", "plan", "--mode", "inline", "--by", "inline")
        self.assertEqual(rc, 0)
        self.assertEqual(read_state(self.cwd)["implement_mode"], "main")

    def test_new_mode_name_as_positional_shortcut(self):
        rc, _ = run(self.cwd, "approve", "plan", "sub-agent", "--by", "sub-agent implement")
        self.assertEqual(rc, 0)
        self.assertEqual(read_state(self.cwd)["implement_mode"], "subagent")

    def test_junk_mode_still_rejected(self):
        # _fail in ra stderr, nên bắt riêng chứ không dùng helper run() (chỉ lấy stdout).
        proc = subprocess.run([sys.executable, STATE_CLI, "approve", "plan",
                               "--mode", "xyz", "--by", "xyz"],
                              capture_output=True, text=True, timeout=30,
                              env=dict(os.environ, TDQ_PROJECT_DIR=self.cwd))
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("Invalid mode", proc.stderr)
        self.assertIsNone(read_state(self.cwd)["implement_mode"])

    def test_next_at_mode_phase_asks_for_mode(self):
        run(self.cwd, "approve", "plan", "--by", "duyệt plan")
        rc, out = run(self.cwd, "next")
        self.assertEqual(rc, 0)
        self.assertIn("phase mode", out)
        self.assertIn("mode", out.lower())


if __name__ == "__main__":
    unittest.main()
