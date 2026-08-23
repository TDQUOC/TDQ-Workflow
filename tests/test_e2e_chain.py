"""E1 — chuỗi end-to-end cả hai lane theo mô hình 0.3.0.

User duyệt bằng chat → Claude ghi nhận bằng `tdq_state.py approve`; hook chỉ
nhắc và ghi sổ turn; Stop đối chiếu lời nhắc với hiệu ứng thật.
Mỗi "turn" mô phỏng bắt đầu bằng prompt_context (xoá sổ turn cũ).
"""
import datetime
import json
import os
import tempfile
import unittest

from helper import (run_hook, load_fixture, read_state, write_file, run_state_cli,
                    decision)

SESSION = "s1"


def today():
    return datetime.date.today().strftime("%Y-%m-%d")


class ChainBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def new_turn(self, prompt="tiếp"):
        payload = load_fixture("prompt.json", cwd=self.cwd, session_id=SESSION)
        payload["prompt"] = prompt
        return run_hook("prompt_context.py", payload)[1]

    def edit(self, rel=None):
        payload = load_fixture("edit_src.json", cwd=self.cwd, session_id=SESSION)
        if rel is not None:
            payload["tool_input"] = {"file_path": os.path.join(self.cwd, rel)}
        return decision(run_hook("edit_gate.py", payload)[1])

    def approve(self, *args):
        return run_state_cli(self.cwd, "approve", *args)

    def stop(self):
        return run_hook("stop_gate.py",
                        load_fixture("stop.json", cwd=self.cwd, session_id=SESSION))


class TestFullLaneChain(ChainBase):
    def test_full_chain(self):
        # 1. intake: init state, lane full
        rc, _, err = run_state_cli(self.cwd, "init", f"{today()}-0900-demo", "full")
        self.assertEqual(rc, 0, err)

        # 2. trước khi duyệt: sửa src vẫn CHẠY được, chỉ kèm lời nhắc
        self.new_turn()
        dec, context = self.edit()
        self.assertEqual(dec, "allow")
        self.assertIn("approve spec", context)

        # 3. spec viết trong docs (im lặng) và đăng ký
        write_file(self.cwd, "docs/tdq/spec/demo.md", "# spec demo\nnoi dung\n")
        run_state_cli(self.cwd, "set", "phase=spec", "spec_file=docs/tdq/spec/demo.md")

        # 4. user nhắn "duyệt spec" → hook gợi đúng lệnh, Claude chạy lệnh đó
        out = self.new_turn("duyệt spec")
        self.assertIn("approve spec", out)
        rc, out, err = self.approve("spec", "--by", "duyệt spec")
        self.assertEqual(rc, 0, err)
        self.assertIn("Recorded", out)

        # 5. vẫn nhắc tiếp: plan chưa duyệt (nhưng không chặn)
        self.new_turn()
        dec, context = self.edit()
        self.assertEqual(dec, "allow")
        self.assertIn("approve plan", context)

        # 6. phase diagram: vẽ sơ đồ, đăng ký, user duyệt từng cái. Đây là cổng cứng —
        # chưa có sơ đồ nào được duyệt thì `set phase=plan` bị từ chối.
        write_file(self.cwd, "docs/tdq/mind-map/demo.md", "# sơ đồ demo\n")
        run_state_cli(self.cwd, "set", "phase=diagram")
        rc, _, err = run_state_cli(self.cwd, "diagram", "add", "docs/tdq/mind-map/demo.md")
        self.assertEqual(rc, 0, err)
        rc, out, err = self.approve("diagram", "docs/tdq/mind-map/demo.md",
                                    "--by", "duyệt sơ đồ")
        self.assertEqual(rc, 0, err)
        self.assertIn("Recorded", out)
        self.assertEqual(read_state(self.cwd)["diagrams"][0]["approved"], True)

        # 7. plan viết + đăng ký; user nhắn "ok plan, mode main"
        write_file(self.cwd, "docs/tdq/plan/demo.md",
                   "# plan demo\nMode thực thi: main — plan 1 task.\n- [ ] T1\n")
        rc, _, err = run_state_cli(self.cwd, "set", "phase=plan",
                                   "plan_file=docs/tdq/plan/demo.md")
        self.assertEqual(rc, 0, err)
        out = self.new_turn("ok plan, mode main")
        self.assertIn("--mode main", out)
        rc, out, err = self.approve("plan", "--mode", "main", "--by", "ok plan, mode main")
        self.assertEqual(rc, 0, err)
        state = read_state(self.cwd)
        self.assertEqual(state["implement_mode"], "main")
        self.assertEqual(state["plan_approved_by"], "ok plan, mode main")
        self.assertIsNotNone(state["plan_sha256"])

        # 8. implement: repo đổi mà chưa log → nhắc TDQ:LOG, và Stop chặn
        run_state_cli(self.cwd, "set", "phase=implement")
        self.new_turn()
        dec, context = self.edit()
        self.assertIn("workinglog", context)
        write_file(self.cwd, "src/app.py", "print('mvp')\n")
        rc, out, _ = self.stop()
        self.assertEqual(json.loads(out)["decision"], "block")

        # 9. append working log (qua công cụ Edit) → Stop im lặng
        log_rel = f"docs/workinglog/{today()}.md"
        write_file(self.cwd, log_rel, "# log\n- entry moi\n")
        self.edit(log_rel)
        rc, out, _ = self.stop()
        self.assertEqual(out, "")

        # 10. duyệt lại lần nữa không phải lỗi
        rc, out, err = self.approve("plan")
        self.assertEqual(rc, 0, err)
        self.assertIn("was already approved at", out)

        state = read_state(self.cwd)
        self.assertTrue(state["spec_approved"] and state["plan_approved"])


class TestQuickLaneChain(ChainBase):
    def test_quick_chain(self):
        rc, _, err = run_state_cli(self.cwd, "init", f"{today()}-0900-hotfix", "quick")
        self.assertEqual(rc, 0, err)

        self.new_turn()
        dec, context = self.edit()
        self.assertEqual(dec, "allow")
        self.assertIn("approve quick", context)

        out = self.new_turn("duyệt quick")
        self.assertIn("approve quick", out)
        rc, out, err = self.approve("quick", "--by", "duyệt quick")
        self.assertEqual(rc, 0, err)
        self.assertEqual(read_state(self.cwd)["quick_approved_by"], "duyệt quick")

        # vẫn nhắc: working log hôm nay chưa có (summary plan quick phải vào đó TRƯỚC)
        self.new_turn()
        dec, context = self.edit()
        self.assertEqual(dec, "allow")
        self.assertIn("workinglog", context)

        write_file(self.cwd, f"docs/workinglog/{today()}.md",
                   "# log\n- plan quick: sua bug X\n")
        self.new_turn()
        dec, context = self.edit()
        self.assertIsNone(dec, context)


if __name__ == "__main__":
    unittest.main()
