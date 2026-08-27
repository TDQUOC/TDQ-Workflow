"""P2 — giao thức tuân thủ: nhắc có mã, quan sát hiệu ứng, đối chiếu ở Stop.

Nguyên tắc kiểm: hook KHÔNG được tin lời tự khai của model, chỉ tin sự kiện
observe trong sổ turn.
"""
import json
import os
import re
import subprocess
import tempfile
import unittest
from datetime import datetime

from helper import ROOT, decision, load_fixture, run_hook, tdq_state, write_state

SESSION = "sess-test"
TODAY_LOG = os.path.join("docs", "workinglog", datetime.now().strftime("%Y-%m-%d") + ".md")


def rows(cwd, kind=None):
    out = tdq_state.turn_log_read(cwd, session=SESSION)
    return [r for r in out if kind is None or r.get("kind") == kind]


class ProtocolTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name
        self.addCleanup(self.tmp.cleanup)

    def payload(self, fixture, **over):
        return load_fixture(fixture, cwd=self.cwd, session_id=SESSION, **over)

    def full_state(self, **over):
        base = dict(active_request="2026-07-29-0900-demo", lane="full", phase="implement")
        base.update(over)
        return write_state(self.cwd, **base)

    # T2.3 -----------------------------------------------------------
    def test_remind_format_and_dedupe(self):
        self.full_state(spec_approved=True, plan_approved=True)
        payload = self.payload("edit_state_json.json")
        rc, out, _ = run_hook("edit_gate.py", payload)
        self.assertEqual(rc, 0)
        perm, context = decision(out)
        self.assertEqual(perm, "allow")                      # không bao giờ chặn
        self.assertTrue(context.startswith("[TDQ:STATE]"), context)
        self.assertLessEqual(len(context.splitlines()), 3, context)
        self.assertLessEqual(len(context), 200, len(context))
        self.assertIn("✓ [TDQ:STATE]", context)              # có dòng echo hướng dẫn
        self.assertEqual(len([r for r in rows(self.cwd, "remind")
                              if r["code"] == "TDQ:STATE"]), 1)

        rc, out2, _ = run_hook("edit_gate.py", payload)      # lần 2 cùng turn → im lặng
        self.assertEqual(rc, 0)
        self.assertEqual(out2, "")
        self.assertEqual(len([r for r in rows(self.cwd, "remind")
                              if r["code"] == "TDQ:STATE"]), 1)

    # T2.4 -----------------------------------------------------------
    def test_edit_gate_observes(self):
        self.full_state(spec_approved=True, plan_approved=True)
        run_hook("edit_gate.py", self.payload("edit_src.json"))
        events = [(r.get("event"), r.get("path")) for r in rows(self.cwd, "observe")]
        self.assertIn(("edit", "src/a.py"), events)
        self.assertNotIn("log_written", [e for e, _ in events])

        run_hook("edit_gate.py", self.payload(
            "edit_src.json", tool_input={"file_path": TODAY_LOG, "old_string": "a", "new_string": "b"}))
        events = [r.get("event") for r in rows(self.cwd, "observe")]
        self.assertIn("log_written", events)

    # T2.5 -----------------------------------------------------------
    def test_edit_gate_reminders(self):
        self.full_state(spec_approved=False, plan_approved=False)
        rc, out, _ = run_hook("edit_gate.py", self.payload("edit_src.json"))
        perm, context = decision(out)
        self.assertEqual(perm, "allow")
        self.assertTrue(context.startswith("[TDQ:APPROVE]"), context)

        # docs/** không bao giờ bị nhắc duyệt
        tdq_state.turn_log_clear(self.cwd, SESSION)
        rc, out, _ = run_hook("edit_gate.py", self.payload("edit_docs_spec.json"))
        self.assertEqual(out, "")

    def test_edit_gate_log_reminder(self):
        self.full_state(spec_approved=True, plan_approved=True)
        rc, out, _ = run_hook("edit_gate.py", self.payload("edit_src.json"))
        _, context = decision(out)
        self.assertTrue(context.startswith("[TDQ:LOG]"), context)
        self.assertIn(TODAY_LOG, context)

    # T2.6 -----------------------------------------------------------
    def test_bash_gate_observes(self):
        self.full_state()
        run_hook("bash_gate.py", self.payload(
            "bash_cmd.json", tool_input={"command": "python3 scripts/tdq_state.py next"}))
        events = [r.get("event") for r in rows(self.cwd, "observe")]
        self.assertIn("state_cli", events)
        self.assertIn("next_run", events)

        tdq_state.turn_log_clear(self.cwd, SESSION)
        run_hook("bash_gate.py", self.payload(
            "bash_cmd.json", tool_input={"command": "python3 scripts/tdq_state.py set phase=qc"}))
        events = [r.get("event") for r in rows(self.cwd, "observe")]
        self.assertIn("state_cli", events)
        self.assertNotIn("next_run", events)

    # T2.7 -----------------------------------------------------------
    def test_bash_gate_reminders(self):
        cases = [
            ("git checkout -b claude/fix", "TDQ:GIT"),
            ("git worktree add ../codex-wt", "TDQ:GIT"),
            ("git commit -m 'fix\n\nGenerated with Claude'", "TDQ:GIT"),
            ("echo '{}' > docs/tdq/state.json", "TDQ:STATE"),
            ("sed -i '' s/a/b/ docs/tdq/STATE.md", "TDQ:STATE"),
        ]
        for cmd, code in cases:
            with self.subTest(cmd=cmd):
                self.full_state()
                tdq_state.turn_log_clear(self.cwd, SESSION)
                rc, out, _ = run_hook("bash_gate.py", self.payload(
                    "bash_cmd.json", tool_input={"command": cmd}))
                perm, context = decision(out)
                self.assertEqual(perm, "allow", cmd)
                self.assertTrue(context.startswith(f"[{code}]"), f"{cmd} -> {context}")

    def test_bash_gate_silent_on_clean_command(self):
        self.full_state()
        rc, out, _ = run_hook("bash_gate.py", self.payload(
            "bash_cmd.json", tool_input={"command": "git checkout -b fix-hook"}))
        self.assertEqual(out, "")

    # T2.2 + T2.8 ----------------------------------------------------
    def test_prompt_clears_session_rows(self):
        self.full_state(spec_file="docs/tdq/spec/x.md")
        tdq_state.turn_log_append(self.cwd, "remind", session=SESSION, code="TDQ:LOG")
        tdq_state.turn_log_append(self.cwd, "remind", session="khac", code="TDQ:GIT")
        run_hook("prompt_context.py", self.payload("prompt.json", prompt="tiếp"))
        # còn đúng ảnh chụp đầu turn mới + tín hiệu duyệt (2026-08-04), sạch dấu vết turn trước
        self.assertEqual([r["kind"] for r in rows(self.cwd)], ["turn_start", "signal"])
        self.assertEqual(len(tdq_state.turn_log_read(self.cwd, session="khac")), 1)

    def test_approve_signal_and_counterexamples(self):
        approvals = ["duyệt spec", "ok spec", "đồng ý spec", "chốt spec nhé"]
        for prompt in approvals:
            with self.subTest(prompt=prompt):
                self.full_state(phase="spec", spec_file="docs/tdq/spec/x.md")
                rc, out, _ = run_hook("prompt_context.py", self.payload("prompt.json", prompt=prompt))
                self.assertIn("[TDQ:APPROVE] The user just approved spec", out, prompt)
                self.assertIn("approve spec", out)

        counter = ["ok tôi hiểu rồi", "spec này ổn không?", "duyệt chưa?", "ok"]
        for prompt in counter:
            with self.subTest(prompt=prompt):
                self.full_state(phase="spec", spec_file="docs/tdq/spec/x.md")
                rc, out, _ = run_hook("prompt_context.py", self.payload("prompt.json", prompt=prompt))
                self.assertNotIn("The user just approved", out, f"{prompt!r} không được coi là duyệt")
                self.assertIn("NOT clearly an approval", out)

    def test_approve_plan_captures_mode(self):
        self.full_state(phase="plan", spec_file="docs/tdq/spec/x.md", spec_approved=True,
                        plan_file="docs/tdq/plan/x.md")
        rc, out, _ = run_hook("prompt_context.py",
                              self.payload("prompt.json", prompt="duyệt plan mode subagent"))
        self.assertIn("--mode subagent", out)

    # T2.9 -----------------------------------------------------------
    def test_hooks_reuse_next(self):
        self.full_state(phase="qc", spec_approved=True, plan_approved=True,
                        spec_file="docs/tdq/spec/x.md", plan_file="docs/tdq/plan/x.md")
        state = tdq_state.load(self.cwd)
        brief = tdq_state.render_next(self.cwd, state, brief=True)
        rc, out, _ = run_hook("prompt_context.py", self.payload("prompt.json", prompt="tiếp"))
        self.assertIn(brief.split(" · Project:")[0], out)

        rc, out, _ = run_hook("session_start.py", self.payload("prompt.json"))
        self.assertIn("Next:", out)
        self.assertIn("checklist", out)
        self.assertLessEqual(len(out.splitlines()), 12, out)

    def test_session_start_budget(self):
        self.full_state()
        rc, out, _ = run_hook("session_start.py", self.payload("prompt.json"))
        self.assertLessEqual(len(out), 600, len(out))
        self.assertIn("[TDQ] Rule:", out)

    def test_prompt_budget(self):
        self.full_state(phase="spec", spec_file="docs/tdq/spec/x.md")
        rc, out, _ = run_hook("prompt_context.py", self.payload("prompt.json", prompt="duyệt spec"))
        self.assertLessEqual(len(out.splitlines()), 3, out)
        self.assertLessEqual(len(out), 240, len(out))

    # T2.10 ----------------------------------------------------------
    def test_stop_gate_decision_matrix(self):
        def stop(**over):
            return run_hook("stop_gate.py", self.payload("stop.json", **over))

        # 1. stop_hook_active → im lặng tuyệt đối
        self.full_state()
        tdq_state.turn_log_append(self.cwd, "observe", session=SESSION, event="edit", path="src/a.py")
        rc, out, _ = stop(stop_hook_active=True)
        self.assertEqual((rc, out), (0, ""))

        # 2. repo đổi, chưa ghi log → BLOCK
        rc, out, _ = stop()
        self.assertEqual(json.loads(out)["decision"], "block")
        self.assertIn("[TDQ:LOG]", json.loads(out)["reason"])

        # 3. repo đổi + đã ghi log → không block
        tdq_state.turn_log_append(self.cwd, "observe", session=SESSION,
                                  event="log_written", path=TODAY_LOG)
        rc, out, _ = stop()
        self.assertEqual(out, "")

        # 4. chỉ sửa working log → không block
        tdq_state.turn_log_clear(self.cwd, SESSION)
        tdq_state.turn_log_append(self.cwd, "observe", session=SESSION, event="edit",
                                  path=TODAY_LOG)
        rc, out, _ = stop()
        self.assertEqual(out, "")

        # 5. đã nhắc TDQ:NEXT mà không có next_run → nhắc lại, KHÔNG block
        tdq_state.turn_log_clear(self.cwd, SESSION)
        tdq_state.turn_log_append(self.cwd, "remind", session=SESSION, code="TDQ:NEXT")
        rc, out, _ = stop()
        data = json.loads(out)
        self.assertNotIn("decision", data)
        self.assertIn("[TDQ:NEXT]", data["hookSpecificOutput"]["additionalContext"])

        # 6. đã nhắc TDQ:NEXT và đã chạy next → im lặng
        tdq_state.turn_log_append(self.cwd, "observe", session=SESSION, event="next_run")
        rc, out, _ = stop()
        self.assertEqual(out, "")

    def test_stop_gate_budget_and_state_hint(self):
        self.full_state(phase="spec", spec_file="docs/tdq/spec/x.md")
        for code in ("TDQ:NEXT", "TDQ:STATE", "TDQ:APPROVE", "TDQ:GIT"):
            tdq_state.turn_log_append(self.cwd, "remind", session=SESSION, code=code)
        rc, out, _ = run_hook("stop_gate.py", self.payload("stop.json"))
        context = json.loads(out)["hookSpecificOutput"]["additionalContext"]
        self.assertLessEqual(len(context.splitlines()), 4, context)
        self.assertLessEqual(len(context), 300, len(context))

    # T2.11 ----------------------------------------------------------
    def test_no_transcript_no_deny(self):
        """Không đọc transcript ở đâu cả; `deny` chỉ được phép ở đúng một nơi.

        Bản gốc cấm `"deny"` tuyệt đối. Nay lane quick cần chặn thật (TDQ:TICK —
        stop_gate chỉ so vân tay plan đầu/cuối turn nên không bắt được bulk-tick
        trong một turn duy nhất), nên bất biến thu hẹp lại: mọi quyết định deny
        phải đi qua `_common.block()`, không hook nào tự dựng JSON deny riêng.
        """
        # `_common.block()` is the ONE place a Claude Code hook may build a deny. The agy
        # target is a different harness: its `PreToolUse` deny is a real hard block and is the
        # whole point of the antigravity bundle (spec §1), and `build_portable.py` writes agy's
        # `permissions.deny` list. Neither goes anywhere near Claude Code's hook path.
        deny_allowed = {
            os.path.join(ROOT, "hooks", "scripts", "_common.py"),
            os.path.join(ROOT, "hooks", "scripts", "agy_pretooluse_gate.py"),
            os.path.join(ROOT, "scripts", "build_portable.py"),
        }
        hits = []
        for folder in ("hooks", "scripts"):
            for root, _, files in os.walk(os.path.join(ROOT, folder)):
                for name in files:
                    if not name.endswith(".py"):
                        continue
                    path = os.path.join(root, name)
                    with open(path, encoding="utf-8") as f:
                        text = f.read()
                    for pattern in (r"transcript_path", r'"deny"'):
                        if pattern == r'"deny"' and path in deny_allowed:
                            continue
                        if re.search(pattern, text):
                            hits.append(f"{path}: {pattern}")
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
