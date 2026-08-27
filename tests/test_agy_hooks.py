"""agy_pretooluse_gate.py / agy_stop_gate.py — hook thật cho Antigravity CLI (agy).

Khác `bash_gate.py`/`stop_gate.py` của Claude Code (chỉ nhắc): `PreToolUse` của agy trả
`decision: "deny"` là chặn cứng thật, `Stop` trả `decision: "continue"` ép loop không dừng
sớm — 2 hook này port lại đúng các điều kiện đã có, không phát minh điều kiện mới.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

from helper import HOOKS as HOOKS_DIR, run_hook, write_state, write_file

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "hooks", "scripts"))


def agy(script, payload_dict):
    return run_hook(script, payload_dict)


def parsed(out):
    """JSON output của agy hook (schema phẳng, khác hookSpecificOutput của Claude Code)."""
    if not out:
        return {}
    return json.loads(out)


# ------------------------------------------------------- PreToolUse (T1.1/T1.2)

# 4 hình dạng field-path khả dĩ cho lệnh shell trong payload PreToolUse của agy — schema
# thật chưa được tài liệu hoá chính xác (xem research Truy vấn 2), hook phải thử cả 4.
def _shapes(cmd):
    return [
        {"tool_input": {"command": cmd}},
        {"toolInput": {"command": cmd}},
        {"input": {"command": cmd}},
        {"command": cmd},
    ]


class TestAgyPreToolUseDeny(unittest.TestCase):
    def test_deny_banned_branch_name_every_field_shape(self):
        for payload in _shapes("git checkout -b antigravity-x"):
            rc, out, _ = agy("agy_pretooluse_gate.py", payload)
            self.assertEqual(rc, 0, payload)
            data = parsed(out)
            self.assertEqual(data.get("decision"), "deny", payload)
            self.assertIn("antigravity-x", data.get("reason", ""))

    def test_deny_worktree_add_with_banned_name(self):
        _, out, _ = agy("agy_pretooluse_gate.py",
                         {"tool_input": {"command": "git worktree add ../claude-wt"}})
        data = parsed(out)
        self.assertEqual(data.get("decision"), "deny")

    def test_deny_state_json_write_redirect(self):
        _, out, _ = agy("agy_pretooluse_gate.py",
                         {"tool_input": {"command": "echo '{}' > docs/tdq/state.json"}})
        data = parsed(out)
        self.assertEqual(data.get("decision"), "deny")
        self.assertIn("tdq_state.py", data.get("reason", ""))

    def test_deny_state_json_write_sed_i(self):
        _, out, _ = agy("agy_pretooluse_gate.py", {"tool_input": {
            "command": "sed -i '' 's/false/true/' docs/tdq/state.json"}})
        self.assertEqual(parsed(out).get("decision"), "deny")

    def test_deny_state_json_write_python_open(self):
        _, out, _ = agy("agy_pretooluse_gate.py", {"tool_input": {
            "command": "python3 -c \"open('docs/tdq/state.json','w').write('{}')\""}})
        self.assertEqual(parsed(out).get("decision"), "deny")

    def test_allow_state_json_read_cat(self):
        rc, out, _ = agy("agy_pretooluse_gate.py",
                          {"tool_input": {"command": "cat docs/tdq/state.json"}})
        self.assertEqual(rc, 0)
        self.assertEqual(parsed(out), {})

    def test_allow_state_json_read_python_open_no_mode(self):
        _, out, _ = agy("agy_pretooluse_gate.py", {"tool_input": {
            "command": "python3 -c \"open('docs/tdq/state.json').read()\""}})
        self.assertEqual(parsed(out), {})

    def test_allow_state_json_read_sed_n(self):
        _, out, _ = agy("agy_pretooluse_gate.py",
                         {"tool_input": {"command": "sed -n '1,5p' docs/tdq/state.json"}})
        self.assertEqual(parsed(out), {})

    def test_allow_branch_name_containing_word_not_at_start(self):
        _, out, _ = agy("agy_pretooluse_gate.py",
                         {"tool_input": {"command": "git checkout -b fix-antigravity-docs"}})
        self.assertEqual(parsed(out), {})

    def test_allow_unrelated_command(self):
        rc, out, _ = agy("agy_pretooluse_gate.py", {"tool_input": {"command": "ls -la"}})
        self.assertEqual(rc, 0)
        self.assertEqual(parsed(out), {})

    def test_allow_empty_payload_no_crash(self):
        rc, out, _ = agy("agy_pretooluse_gate.py", {})
        self.assertEqual(rc, 0)
        self.assertEqual(out, "")

    def test_allow_malformed_stdin_no_crash(self):
        proc_rc, _, _ = run_hook("agy_pretooluse_gate.py", {})
        self.assertEqual(proc_rc, 0)


# ------------------------------------------------------- Stop (T1.3/T1.4)

class StopBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def stop(self, **payload):
        payload.setdefault("cwd", self.cwd)
        return agy("agy_stop_gate.py", payload)

    def plan(self, rel, content):
        return write_file(self.cwd, rel, content)


PLAN_ONE_OPEN = """# Plan
- [ ] **T1.1** (e5m) làm gì đó — Test: x
"""
PLAN_ALL_DONE = """# Plan
- [x] **T1.1** (e5m) làm gì đó — Test: x
"""


class TestAgyStopGate(StopBase):
    def test_no_state_silent(self):
        rc, out, _ = self.stop()
        self.assertEqual(rc, 0)
        self.assertEqual(out, "")

    def test_continue_when_plan_unfinished(self):
        write_state(self.cwd, active_request="r1", lane="full", phase="implement",
                    plan_file="docs/tdq/plan/p.md")
        self.plan("docs/tdq/plan/p.md", PLAN_ONE_OPEN)
        _, out, _ = self.stop()
        data = parsed(out)
        self.assertEqual(data.get("decision"), "continue")
        self.assertIn("TDQ:UNFINISHED", data.get("reason", ""))

    def test_silent_when_plan_all_done(self):
        write_state(self.cwd, active_request="r1", lane="full", phase="implement",
                    plan_file="docs/tdq/plan/p.md")
        self.plan("docs/tdq/plan/p.md", PLAN_ALL_DONE)
        _, out, _ = self.stop()
        self.assertEqual(parsed(out), {})

    def test_silent_when_phase_not_implement(self):
        write_state(self.cwd, active_request="r1", lane="full", phase="qc",
                    plan_file="docs/tdq/plan/p.md")
        self.plan("docs/tdq/plan/p.md", PLAN_ONE_OPEN)
        _, out, _ = self.stop()
        self.assertEqual(parsed(out), {})

    def test_streak_steps_down_after_max(self):
        write_state(self.cwd, active_request="r1", lane="full", phase="implement",
                    plan_file="docs/tdq/plan/p.md")
        self.plan("docs/tdq/plan/p.md", PLAN_ONE_OPEN)
        seen_continue = False
        last_decision = None
        for _ in range(5):
            _, out, _ = self.stop()
            last_decision = parsed(out).get("decision")
            if last_decision == "continue":
                seen_continue = True
            else:
                break
        self.assertTrue(seen_continue)
        # Đủ MAX_STREAK lần liên tiếp cùng sha plan không tiến triển → hạ xuống, thôi chặn.
        self.assertNotEqual(last_decision, "continue")

    def test_streak_resets_when_plan_progresses(self):
        write_state(self.cwd, active_request="r1", lane="full", phase="implement",
                    plan_file="docs/tdq/plan/p.md")
        self.plan("docs/tdq/plan/p.md", PLAN_ONE_OPEN)
        self.stop()
        self.stop()
        self.plan("docs/tdq/plan/p.md", PLAN_ALL_DONE)
        _, out, _ = self.stop()
        self.assertEqual(parsed(out), {})

    def test_no_crash_on_alternate_cwd_field_name(self):
        # No "cwd" key, only an alternate name — must still resolve to the temp dir, not fall
        # back to os.getcwd() (which would read the REAL project's own state.json).
        rc, out, _ = agy("agy_stop_gate.py", {"workingDirectory": self.cwd})
        self.assertEqual(rc, 0)
        self.assertEqual(parsed(out), {})

    def test_no_crash_on_malformed_stdin(self):
        # Truly broken JSON on stdin (not just an empty payload) — run with an explicit `cwd`
        # process argument so a working-directory fallback, if it ever triggered, could never
        # reach outside the temp dir into the real project's own state.json.
        proc = subprocess.run(
            [sys.executable, os.path.join(HOOKS_DIR, "agy_stop_gate.py")],
            input="not json", capture_output=True, text=True, timeout=30, cwd=self.cwd)
        self.assertEqual(proc.returncode, 0)


# ------------------------------------------------------- log service (T5.1)

class TestAgyLogService(unittest.TestCase):
    """Mỗi lần chặn phải in 1 dòng stderr có timestamp nêu case; TDQ_LOG=0 thì im."""

    def _pre(self, env):
        return run_hook("agy_pretooluse_gate.py",
                        {"tool_input": {"command": "git checkout -b antigravity-x"}}, env=env)

    def test_pretooluse_logs_case_when_denying(self):
        _, out, err = self._pre({"TDQ_LOG": "1"})
        self.assertEqual(parsed(out).get("decision"), "deny")
        self.assertIn("TDQ:GIT", err)
        self.assertRegex(err, r"^\[\d{4}-\d{2}-\d{2}T")

    def test_pretooluse_silent_with_log_off(self):
        _, out, err = self._pre({"TDQ_LOG": "0"})
        self.assertEqual(parsed(out).get("decision"), "deny")
        self.assertEqual(err, "")

    def test_pretooluse_state_case_named_in_log(self):
        _, _, err = run_hook("agy_pretooluse_gate.py",
                             {"tool_input": {"command": "echo '{}' > docs/tdq/state.json"}},
                             env={"TDQ_LOG": "1"})
        self.assertIn("TDQ:STATE", err)

    def test_no_log_when_allowing(self):
        _, _, err = run_hook("agy_pretooluse_gate.py",
                             {"tool_input": {"command": "ls -la"}}, env={"TDQ_LOG": "1"})
        self.assertEqual(err, "")


class TestAgyStopLogService(StopBase):
    def _blocked(self, env):
        write_state(self.cwd, active_request="r1", lane="full", phase="implement",
                    plan_file="docs/tdq/plan/p.md")
        self.plan("docs/tdq/plan/p.md", PLAN_ONE_OPEN)
        return run_hook("agy_stop_gate.py", {"cwd": self.cwd}, env=env)

    def test_stop_logs_case_when_continuing(self):
        _, out, err = self._blocked({"TDQ_LOG": "1"})
        self.assertEqual(parsed(out).get("decision"), "continue")
        self.assertIn("TDQ:UNFINISHED", err)
        self.assertRegex(err, r"^\[\d{4}-\d{2}-\d{2}T")

    def test_stop_silent_with_log_off(self):
        _, out, err = self._blocked({"TDQ_LOG": "0"})
        self.assertEqual(parsed(out).get("decision"), "continue")
        self.assertEqual(err, "")


if __name__ == "__main__":
    unittest.main()
