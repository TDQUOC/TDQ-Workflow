"""B3 — bash_gate.py: NHẮC (allow + additionalContext) về quy ước git và state.json,
không bao giờ chặn lệnh."""
import tempfile
import unittest

from helper import run_hook, load_fixture, decision, tdq_state


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
        self.assert_remind("git checkout -b claude/fix-login", "quy ước")
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
        self.assert_silent("cat docs/tdq/state.json")
        self.assert_silent("jq .phase docs/tdq/state.json")

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

    def test_approve_reminds_when_signal_mismatch(self):
        cmd = 'python3 scripts/tdq_state.py approve spec --by "duyệt spec"'
        self._signal(cmd[:40], "spec", matched=False)
        self.assert_remind(cmd, "TDQ:APPROVE")

    def test_approve_silent_when_signal_matched(self):
        cmd = 'python3 scripts/tdq_state.py approve plan --mode main --by "duyệt plan mode main"'
        self._signal(cmd[:40], "plan", matched=True, mode_conflict=False)
        self.assert_silent(cmd)

    def test_setphase_reminds_when_signal_mismatch(self):
        cmd_a = "python3 scripts/tdq_state.py set phase=plan"
        self._signal(cmd_a[:40], "spec", matched=False)
        self.assert_remind(cmd_a, "TDQ:APPROVE")

        cmd_b = "python3 scripts/tdq_state.py set phase=implement"
        self._signal(cmd_b[:40], "plan", matched=False)
        self.assert_remind(cmd_b, "TDQ:APPROVE")

    def test_setphase_silent_when_signal_matched(self):
        cmd = "python3 scripts/tdq_state.py set phase=plan"
        self._signal(cmd[:40], "spec", matched=True, mode_conflict=False)
        self.assert_silent(cmd)

    def test_failopen_no_signal_row(self):
        cmd = 'python3 scripts/tdq_state.py approve spec --by "duyệt spec"'
        self.assert_silent(cmd)

    def test_approve_not_swallowed_by_prior_edit_gate_remind(self):
        cmd = 'python3 scripts/tdq_state.py approve spec --by "duyệt spec"'
        self._pre_remind(cmd[:40], "TDQ:APPROVE")
        self._signal(cmd[:40], "spec", matched=False)
        self.assert_remind(cmd, "TDQ:APPROVE")


if __name__ == "__main__":
    unittest.main()
