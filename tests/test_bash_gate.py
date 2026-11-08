"""B3 — bash_gate.py: NHẮC (allow + additionalContext) về quy ước git và state.json,
không bao giờ chặn lệnh."""
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

from helper import HOOKS, decision, load_fixture, run_hook, tdq_state, write_state


class TestBashGate(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def bash(self, command):
        # session riêng cho mỗi lệnh: hook dedupe 1 lần/mã/turn, dùng chung
        # session sẽ khiến lệnh thứ hai im lặng và test hiểu nhầm là bỏ sót.
        payload = load_fixture("bash_cmd.json", cwd=self.cwd, session_id=command[:40])
        payload["tool_input"] = {"command": command}
        return run_hook("bash_gate.py", payload)

    def subagent_bash(self, command, phase="analyze"):
        write_state(self.cwd, active_request="r1", lane="full", phase=phase)
        payload = load_fixture("bash_cmd.json", cwd=self.cwd, session_id="ultra-" + command[:30])
        payload["agent_id"] = "agent-ultra"
        payload["agent_type"] = "Explore"
        payload["tool_input"] = {"command": command}
        return run_hook("bash_gate.py", payload)

    def test_ultracode_subagent_source_shell_write_denied_before_implement(self):
        for command in ("echo x > src/a.py", "Set-Content src/a.py x", "cp a skills/x.md"):
            with self.subTest(command=command):
                self.assertEqual(decision(self.subagent_bash(command)[1])[0], "deny")

    def test_ultracode_subagent_docs_report_write_allowed(self):
        self.assertNotIn("deny", self.subagent_bash("Set-Content docs/tdq/artifacts/r1/agent-ultra.md report")[1])

    def test_ultracode_read_commands_with_redirect_noise_are_allowed(self):
        for command in ("python -m pytest -q 2>&1 | tail -5", "ls > /dev/null",
                        "Get-ChildItem 2>$null", "grep -n 'cp' README.md"):
            with self.subTest(command=command):
                self.assertNotIn("deny", self.subagent_bash(command)[1])

    def test_ultracode_docs_text_does_not_mask_source_write(self):
        command = "echo x > src/a.py; type docs/tdq/artifacts/r1/agent-ultra.md"
        self.assertEqual(decision(self.subagent_bash(command)[1])[0], "deny")

    def test_ultracode_additional_mutators_are_denied(self):
        for command in ("rm -rf src", "sed -i s/a/b/ src/a.py", "Remove-Item src/a.py",
                        "New-Item src/a.py", "python -c \"open('src/a.py','w')\""):
            with self.subTest(command=command):
                self.assertEqual(decision(self.subagent_bash(command)[1])[0], "deny")

    def test_ultracode_subagent_implement_keeps_existing_gate_behavior(self):
        self.assertNotIn("deny", self.subagent_bash("echo x > src/a.py", phase="implement")[1])

    def assert_remind(self, command, needle=None):
        rc, out, _ = self.bash(command)
        self.assertEqual(rc, 0, command)
        dec, context = decision(out)
        self.assertEqual(dec, "allow", command)  # nhắc, KHÔNG chặn
        self.assertNotIn('"deny"', out, command)
        self.assertTrue(context, command)
        if needle:
            self.assertIn(needle, context)

    def assert_silent(self, command):
        rc, out, _ = self.bash(command)
        self.assertEqual(rc, 0, command)
        self.assertEqual(out, "", command)

    def test_remind_banned_branch_names(self):
        self.assert_remind("git checkout -b claude/fix-login", "convention")
        self.assert_remind("git switch -c gemini-x")
        self.assert_remind("git branch codex_feature")
        self.assert_remind("git worktree add ../antigravity-wt")
        self.assert_remind("git worktree add -b Claude-task ../wt")

    def test_silent_normal_branch(self):
        self.assert_silent("git checkout -b feature/tdq")
        self.assert_silent("git switch -c fix/login-timeout")
        self.assert_silent("git branch release-0.1")

    def test_remind_ai_commit_messages(self):
        self.assert_remind('git commit -m "fix: login (generated with Claude)"')
        self.assert_remind('git commit -m "feat: x" -m "Co-Authored-By: Claude <noreply@anthropic.com>"')
        self.assert_remind('git commit -m "chore: được tạo cùng với Claude"')

    def test_silent_normal_commit(self):
        self.assert_silent('git commit -m "fix: login timeout khi token het han"')

    def test_remind_state_json_writes(self):
        self.assert_remind("echo '{}' > docs/tdq/state.json", "tdq_state.py")
        self.assert_remind("echo '{}' > docs/tdq/STATE.md", "tdq_state.py")
        self.assert_remind("echo x >> docs/tdq/state.json")
        self.assert_remind("sed -i '' 's/false/true/' docs/tdq/state.json")
        self.assert_remind("cat a.json | tee docs/tdq/state.json")
        self.assert_remind("cp other.json docs/tdq/state.json")
        self.assert_remind("mv other.json docs/tdq/state.json")
        self.assert_remind('python3 -c "open(\'docs/tdq/state.json\',\'w\').write(\'{}\')"')

    def test_silent_state_json_reads(self):
        """ĐỌC state.json không được kích nhắc TDQ:STATE (nhắc đó dành cho lệnh GHI).

        Kiểm theo mã nhắc chứ không theo "hook im hoàn toàn": từ 2026-08-19 `cat`
        không giới hạn còn kích TDQ:OUTPUT, và đó là nhắc khác, đúng việc của nó.
        """
        for cmd in ("cat docs/tdq/state.json", "jq .phase docs/tdq/state.json"):
            rc, out, _ = self.bash(cmd)
            self.assertEqual(rc, 0, cmd)
            self.assertNotIn("TDQ:STATE", out, cmd)

    def test_silent_plain_commands(self):
        self.assert_silent("ls -la")
        self.assert_silent("python3 -m unittest discover tests")
        self.assert_silent("git status")

    def test_state_cli_approve_is_never_blocked(self):
        # lệnh ghi state ĐÚNG cách (qua CLI) không được nhắc gì cả
        self.assert_silent('python3 scripts/tdq_state.py approve plan --mode main --by "duyệt plan"')

    def test_observes_state_cli_and_next(self):
        self.bash("python3 scripts/tdq_state.py next")
        rows = tdq_state.turn_log_read(self.cwd, session="python3 scripts/tdq_state.py next")
        events = [r.get("event") for r in rows if r.get("kind") == "observe"]
        self.assertIn("state_cli", events)
        self.assertIn("next_run", events)

    def test_observes_set_without_next(self):
        cmd = "python3 scripts/tdq_state.py set phase=qc"
        self.bash(cmd)
        rows = tdq_state.turn_log_read(self.cwd, session=cmd[:40])
        events = [r.get("event") for r in rows if r.get("kind") == "observe"]
        self.assertIn("state_cli", events)
        self.assertNotIn("next_run", events)

    def _signal(self, session, target, matched, mode_conflict=False):
        tdq_state.turn_log_append(self.cwd, "signal", session=session,
                                  event="approve_pending", target=target,
                                  matched=matched, mode_conflict=mode_conflict)

    def _pre_remind(self, session, code):
        tdq_state.turn_log_append(self.cwd, "remind", session=session, code=code)

    def _turn_start(self, session):
        """What prompt_context writes at every user prompt — proof the prompt hook ran."""
        tdq_state.turn_log_append(self.cwd, "turn_start", session=session)

    def assert_deny(self, command, needle=None):
        rc, out, _ = self.bash(command)
        self.assertEqual(rc, 0, command)
        self.assertEqual(decision(out)[0], "deny", command)
        if needle:
            self.assertIn(needle, out)

    def test_approve_reminds_when_signal_mismatch_without_prompt_hook(self):
        # No turn_start: a host without UserPromptSubmit — keep the reminder, never deadlock.
        cmd = 'python3 scripts/tdq_state.py approve spec --by "duyệt spec"'
        self._signal(cmd[:40], "spec", matched=False)
        self.assert_remind(cmd, "TDQ:APPROVE")

    def test_approve_denied_when_signal_mismatch(self):
        cmd = 'python3 scripts/tdq_state.py approve spec --by "duyệt spec"'
        self._turn_start(cmd[:40])
        self._signal(cmd[:40], "spec", matched=False)
        self.assert_deny(cmd, "TDQ:APPROVE")

    def test_approve_denied_without_any_signal_play3clone(self):
        # play3clone 2026-11-08: the user typed "1a" while no gate was pending → no signal row;
        # the agent then ran `approve spec --by "duyet spec"` in that same turn.
        cmd = 'python3 scripts/tdq_state.py approve spec --by "duyet spec"'
        self._turn_start(cmd[:40])
        self.assert_deny(cmd, "TDQ:APPROVE")

    def test_one_prompt_opens_one_gate(self):
        # "duyệt spec" matched spec — it must not also carry `approve plan` in the same turn.
        cmd = 'python3 scripts/tdq_state.py approve plan --by "duyet plan"'
        self._turn_start(cmd[:40])
        self._signal(cmd[:40], "spec", matched=True)
        self.assert_deny(cmd, "TDQ:APPROVE")

    def test_approve_silent_when_signal_matched(self):
        cmd = 'python3 scripts/tdq_state.py approve plan --mode main --by "duyệt plan mode main"'
        self._turn_start(cmd[:40])
        self._signal(cmd[:40], "plan", matched=True, mode_conflict=False)
        self.assert_silent(cmd)

    def test_approve_plan_accepts_mode_gate_signal(self):
        cmd = 'python3 scripts/tdq_state.py approve plan --mode main --by "main"'
        self._turn_start(cmd[:40])
        self._signal(cmd[:40], "mode", matched=True)
        self.assert_silent(cmd)

    def test_quick_aliases_map_to_quick_signal(self):
        for alias in ("nhanh", "express"):
            with self.subTest(alias=alias):
                cmd = f'python3 scripts/tdq_state.py approve {alias} --by "duyệt nhanh {alias}"'
                self._turn_start(cmd[:40])
                self._signal(cmd[:40], "quick", matched=True)
                self.assert_silent(cmd)

    def test_setphase_denied_when_signal_mismatch(self):
        cmd_a = "python3 scripts/tdq_state.py set phase=plan"
        self._turn_start(cmd_a[:40])
        self._signal(cmd_a[:40], "spec", matched=False)
        self.assert_deny(cmd_a, "TDQ:APPROVE")

        cmd_b = "python3 scripts/tdq_state.py set phase=implement"
        self._turn_start(cmd_b[:40])
        self._signal(cmd_b[:40], "plan", matched=False)
        self.assert_deny(cmd_b, "TDQ:APPROVE")

    def test_setphase_silent_when_signal_matched(self):
        cmd = "python3 scripts/tdq_state.py set phase=plan"
        self._turn_start(cmd[:40])
        self._signal(cmd[:40], "spec", matched=True, mode_conflict=False)
        self.assert_silent(cmd)

    def test_setphase_fix_round_after_plan_approved_not_denied(self):
        # QC/report → rejected deviation → `set phase=implement`: plan was approved long ago,
        # no gate pending, so prompt_context wrote no signal. Must not be denied.
        write_state(self.cwd, active_request="r1", lane="full", phase="report",
                    spec_approved=True, plan_approved=True)
        cmd = "python3 scripts/tdq_state.py set phase=implement"
        self._turn_start(cmd[:40])
        self.assert_silent(cmd)

    def test_failopen_no_signal_row(self):
        # No turn_start either: host without the prompt hook — stays silent as before.
        cmd = 'python3 scripts/tdq_state.py approve spec --by "duyệt spec"'
        self.assert_silent(cmd)

    def test_approve_not_swallowed_by_prior_edit_gate_remind(self):
        cmd = 'python3 scripts/tdq_state.py approve spec --by "duyệt spec"'
        self._turn_start(cmd[:40])
        self._pre_remind(cmd[:40], "TDQ:APPROVE")
        self._signal(cmd[:40], "spec", matched=False)
        self.assert_deny(cmd, "TDQ:APPROVE")


class TestBashGateSingleTurnRead(unittest.TestCase):
    """P0-3 — 1 invoke `main()` chỉ đọc `.tdq-turn.jsonl` đúng 1 lần, dù cả
    `_check_signal_mismatch` lẫn `remind()` đều cần dữ liệu sổ turn."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, HOOKS)
        cls.addClassCleanup(sys.path.remove, HOOKS)
        spec = importlib.util.spec_from_file_location(
            "bash_gate_mod", os.path.join(HOOKS, "bash_gate.py"))
        cls.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.mod)
        # bash_gate đọc sổ turn qua `_common.turn_rows`, mà `_common` đã bind
        # `turn_log_read` ngay lúc import (from-import). Patch trên `tdq_state`
        # không còn tác dụng — phải patch đúng module giữ tên đã bind.
        cls.common = sys.modules["_common"]

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def test_main_reads_turn_log_once(self):
        cmd = ('git checkout -b claude/x && python3 scripts/tdq_state.py approve plan '
               '--mode main --by "duyệt plan mode main"')
        session = cmd[:40]
        # signal khớp (matched=True) để _check_signal_mismatch KHÔNG remind_force/exit
        # sớm — phải đi tiếp tới nhánh branch-name để remind() cũng cần đọc sổ turn.
        tdq_state.turn_log_append(self.cwd, "signal", session=session,
                                  event="approve_pending", target="plan",
                                  matched=True, mode_conflict=False)
        payload = {"cwd": self.cwd, "session_id": session,
                   "tool_input": {"command": cmd}}

        real_read = self.common.turn_log_read
        calls = []

        def counting_read(cwd, session=None):
            calls.append(1)
            return real_read(cwd, session=session)

        stdin = io.StringIO(json.dumps(payload))
        stdout = io.StringIO()
        with mock.patch.object(self.common, "turn_log_read", side_effect=counting_read), \
             mock.patch.object(sys, "stdin", stdin), \
             mock.patch.object(sys, "stdout", stdout):
            with self.assertRaises(SystemExit):
                self.mod.main()
        self.assertEqual(len(calls), 1)


class TestNhacTranOutput(unittest.TestCase):
    """TDQ:OUTPUT — nhắc khi lệnh Bash đổ nguyên file/lịch sử vào context.

    Vì sao đáng nhắc: mỗi output tool bị model đọc lại ở MỌI API call còn lại của
    phiên (carry-cost). Một lần `cat` file 2.000 token ở giữa phiên 300 call tốn gấp
    hàng trăm lần chính nó. Nhắc chứ không chặn — có ca đổ nguyên file là đúng.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def bash(self, command):
        payload = load_fixture("bash_cmd.json", cwd=self.cwd, session_id=command[:40])
        payload["tool_input"] = {"command": command}
        return run_hook("bash_gate.py", payload)

    def assert_nhac(self, command):
        rc, out, _ = self.bash(command)
        self.assertEqual(rc, 0, command)
        dec, context = decision(out)
        self.assertEqual(dec, "allow", command)
        self.assertNotIn('"deny"', out, command)
        self.assertIn("TDQ:OUTPUT", context, command)

    def assert_im(self, command):
        rc, out, _ = self.bash(command)
        self.assertEqual(rc, 0, command)
        self.assertNotIn("TDQ:OUTPUT", out, command)

    def test_nhac_khi_do_nguyen_file_hoac_lich_su(self):
        self.assert_nhac("cat scripts/token_audit.py")
        self.assert_nhac("git log")
        self.assert_nhac("git diff")
        self.assert_nhac("ls -R skills")

    def test_im_khi_da_co_gioi_han(self):
        self.assert_im("cat scripts/token_audit.py | head -50")
        self.assert_im("git log --oneline -n 20")
        self.assert_im("git diff --stat")
        self.assert_im("git diff --name-only")
        self.assert_im("sed -n '1,40p' scripts/token_audit.py")
        self.assert_im("head -30 README.md")
        self.assert_im("grep -c TODO scripts/token_audit.py")

    def test_im_khi_cat_la_de_GHI_file_chu_khong_phai_doc(self):
        """`cat > f <<EOF` là ghi file — nhắc ở đây chỉ tạo nhiễu."""
        self.assert_im("cat > /tmp/x.md <<'EOF'\nnội dung\nEOF")
        self.assert_im("cat <<'EOF' > /tmp/x.md\nnội dung\nEOF")

    def test_im_voi_lenh_thuong(self):
        self.assert_im("python3 -m pytest tests/test_bash_gate.py -q")
        self.assert_im("ls skills")
        self.assert_im("git status")

    def test_khong_bao_gio_chan(self):
        for cmd in ("cat a.md", "git log", "ls -R ."):
            rc, out, _ = self.bash(cmd)
            self.assertEqual(rc, 0, cmd)
            self.assertNotIn('"deny"', out, cmd)


if __name__ == "__main__":
    unittest.main()
