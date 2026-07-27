"""B3 — bash_gate.py: git naming bans, AI commit-msg bans, state.json write bans."""
import tempfile
import unittest

from helper import run_hook, load_fixture, decision


class TestBashGate(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def bash(self, command):
        payload = load_fixture("bash_cmd.json", cwd=self.cwd)
        payload["tool_input"] = {"command": command}
        return run_hook("bash_gate.py", payload)

    def assert_deny(self, command, needle=None):
        rc, out, _ = self.bash(command)
        self.assertEqual(rc, 0, command)
        dec, reason = decision(out)
        self.assertEqual(dec, "deny", command)
        if needle:
            self.assertIn(needle, reason)

    def assert_allow(self, command):
        rc, out, _ = self.bash(command)
        self.assertEqual(rc, 0, command)
        self.assertEqual(out, "", command)

    def test_deny_banned_branch_names(self):
        self.assert_deny("git checkout -b claude/fix-login")
        self.assert_deny("git switch -c gemini-x")
        self.assert_deny("git branch codex_feature")
        self.assert_deny("git worktree add ../antigravity-wt")
        self.assert_deny("git worktree add -b Claude-task ../wt")

    def test_allow_normal_branch(self):
        self.assert_allow("git checkout -b feature/tdq")
        self.assert_allow("git switch -c fix/login-timeout")
        self.assert_allow("git branch release-0.1")

    def test_deny_ai_commit_messages(self):
        self.assert_deny('git commit -m "fix: login (generated with Claude)"')
        self.assert_deny('git commit -m "feat: x" -m "Co-Authored-By: Claude <noreply@anthropic.com>"')
        self.assert_deny('git commit -m "chore: được tạo cùng với Claude"')

    def test_allow_normal_commit(self):
        self.assert_allow('git commit -m "fix: login timeout khi token het han"')

    def test_deny_state_json_writes(self):
        self.assert_deny("echo '{}' > docs/tdq/state.json", "state.json")
        self.assert_deny("echo x >> docs/tdq/state.json")
        self.assert_deny("sed -i '' 's/false/true/' docs/tdq/state.json")
        self.assert_deny("cat a.json | tee docs/tdq/state.json")
        self.assert_deny("cp other.json docs/tdq/state.json")
        self.assert_deny("mv other.json docs/tdq/state.json")
        self.assert_deny('python3 -c "open(\'docs/tdq/state.json\',\'w\').write(\'{}\')"')

    def test_allow_state_json_reads(self):
        self.assert_allow("cat docs/tdq/state.json")
        self.assert_allow("jq .phase docs/tdq/state.json")

    def test_allow_plain_commands(self):
        self.assert_allow("ls -la")
        self.assert_allow("python3 -m unittest discover tests")
        self.assert_allow("git status")


if __name__ == "__main__":
    unittest.main()
