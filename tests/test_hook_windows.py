"""The six hooks must SURVIVE a turn on every host, Windows included.

This is the test the 0.48.0 suite did not have, and its absence is why the plugin shipped dead
on Windows for an unknown number of releases: every hook died at its first `print` carrying `✓`
or Vietnamese, because Python takes the console encoding from the locale and a stock Windows box
answers cp1252. Nothing in 1907 tests ran a hook the way the host runs one — as a child process
whose stdout is a pipe, with no PYTHONUTF8 in the environment.

So that is exactly what these cases do: spawn each hook as a child, feed it a payload on stdin,
and demand exit 0 with its block intact. The environment is scrubbed of `PYTHONUTF8` and
`PYTHONIOENCODING` on purpose — inheriting them would hide the very bug this file exists to
catch, and the suite would stay green while the product stayed broken.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

from helper import ROOT

HOOKS = os.path.join(ROOT, "hooks", "scripts")

# hook file -> (payload, a fragment its output must carry; "" = only the exit code matters)
CA_KIEM = {
    "session_start.py": ({"hook_event_name": "SessionStart"}, "[TDQ:NEXT]"),
    "subagent_start.py": ({"hook_event_name": "SubagentStart"}, ""),
    "prompt_context.py": ({"hook_event_name": "UserPromptSubmit",
                           "prompt": "một việc nhỏ"}, ""),
    "stop_gate.py": ({"hook_event_name": "Stop"}, ""),
    "edit_gate.py": ({"hook_event_name": "PreToolUse", "tool_name": "Edit",
                      "tool_input": {"file_path": "src/a.py"}}, ""),
    "read_gate.py": ({"hook_event_name": "PreToolUse", "tool_name": "Read",
                      "tool_input": {"file_path": "src/a.py"}}, ""),
    "bash_gate.py": ({"hook_event_name": "PreToolUse", "tool_name": "Bash",
                      "tool_input": {"command": "git commit -m x"}}, ""),
    "search_gate.py": ({"hook_event_name": "PreToolUse", "tool_name": "Grep",
                        "tool_input": {"pattern": "foo"}}, ""),
    "search_observe.py": ({"hook_event_name": "PostToolUse", "tool_name": "mcp__lsp__find_symbol",
                           "tool_input": {"name": "bar"}}, ""),
    "lsp_gate.py": ({"hook_event_name": "PreToolUse", "tool_name": "mcp__lsp__start_lsp",
                     "tool_input": {"root_dir": "c:/repo", "language_id": "python"}}, ""),
    "ask_gate.py": ({"hook_event_name": "PreToolUse", "tool_name": "AskUserQuestion",
                     "tool_input": {"question": "ok?"}}, ""),
}


def moi_truong_nhu_host():
    """The host's environment, minus the two variables that would paper over the bug."""
    env = dict(os.environ)
    env.pop("PYTHONUTF8", None)
    env.pop("PYTHONIOENCODING", None)
    # A hook must never be judged against the machine's own live request.
    env["TDQ_LOG"] = "0"
    return env


class SauHookSongTest(unittest.TestCase):
    """One case per hook. A dead hook costs the whole turn, so exit 0 is the floor."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def chay(self, ten_hook, payload):
        day_du = dict(payload, session_id="s1", cwd=self.tmp.name)
        return subprocess.run(
            [sys.executable, os.path.join(HOOKS, ten_hook)],
            input=json.dumps(day_du), capture_output=True, text=True,
            encoding="utf-8", errors="replace", env=moi_truong_nhu_host(), timeout=120)

    def test_moi_hook_thoat_0(self):
        for ten_hook, (payload, _) in CA_KIEM.items():
            with self.subTest(hook=ten_hook):
                proc = self.chay(ten_hook, payload)
                self.assertEqual(proc.returncode, 0,
                                 f"{ten_hook} died:\n{proc.stderr[-800:]}")

    def test_khong_hook_nao_no_vi_encoding(self):
        """The exact failure that shipped: UnicodeEncodeError on the first non-ASCII print."""
        for ten_hook, (payload, _) in CA_KIEM.items():
            with self.subTest(hook=ten_hook):
                proc = self.chay(ten_hook, payload)
                self.assertNotIn("UnicodeEncodeError", proc.stderr)
                self.assertNotIn("UnicodeDecodeError", proc.stderr)

    def test_khoi_tdq_ra_nguyen_ven(self):
        for ten_hook, (payload, manh) in CA_KIEM.items():
            if not manh:
                continue
            with self.subTest(hook=ten_hook):
                proc = self.chay(ten_hook, payload)
                self.assertIn(manh, proc.stdout)

    def test_session_start_giu_duoc_tieng_viet_va_dau_tick(self):
        """Output must survive the pipe as UTF-8 — mojibake is a silent kind of dead."""
        proc = self.chay("session_start.py", {"hook_event_name": "SessionStart"})
        self.assertIn("✓", proc.stdout)

    def test_payload_hong_khong_giet_hook_nao(self):
        """A malformed payload is a bad turn, never a dead session."""
        for ten_hook in CA_KIEM:
            with self.subTest(hook=ten_hook):
                proc = subprocess.run(
                    [sys.executable, os.path.join(HOOKS, ten_hook)],
                    input="{not json", capture_output=True, text=True,
                    encoding="utf-8", errors="replace",
                    env=moi_truong_nhu_host(), timeout=120)
                self.assertEqual(proc.returncode, 0, ten_hook)

    def test_bash_gate_powershell_parity(self):
        """PowerShell commands receive the exact same git/ai trace inspection as Bash (O03)."""
        proc = self.chay("bash_gate.py", {
            "hook_event_name": "PreToolUse",
            "tool_name": "PowerShell",
            "tool_input": {"command": "git commit -m 'feat: test co-authored-by: claude'"}
        })
        self.assertEqual(proc.returncode, 0)
        self.assertIn("TDQ:GIT", proc.stdout + proc.stderr)

    def test_opencode_tdq_workflow_wrapper_filtered(self):
        """Injected <TDQ_WORKFLOW> wrapper from OpenCode is stripped before checking approval (O03)."""
        sys.path.insert(0, HOOKS)
        try:
            import prompt_context
            # Prompt that only has approval words INSIDE wrapper is NOT an approval
            p_wrapped_only = "<TDQ_WORKFLOW>Quy tắc: duyệt spec khi sẵn sàng</TDQ_WORKFLOW>\n\nHãy giải thích code này"
            self.assertFalse(prompt_context.looks_like_approval(p_wrapped_only, "spec"))

            # Prompt that has approval OUTSIDE wrapper IS an approval
            p_real_approve = "<TDQ_WORKFLOW>Chỉ dẫn hệ thống</TDQ_WORKFLOW>\n\nduyệt spec"
            self.assertTrue(prompt_context.looks_like_approval(p_real_approve, "spec"))
        finally:
            if sys.path and sys.path[0] == HOOKS:
                sys.path.pop(0)

    def test_quote_path_in_build_portable_antigravity(self):
        """Antigravity hook commands must quote script paths to survive spaces on Windows (O03)."""
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        try:
            import build_portable
            out_file = os.path.join(self.tmp.name, "hooks.json")
            build_portable._sinh_hooks_agy(out_file, nen_tang="win32", goc_cai="C:/Program Files/My Plugin")
            with open(out_file, encoding="utf-8") as f:
                data = json.load(f)
            hooks = data.get("hooks", {})
            found = False
            for hook_list in hooks.values():
                for h_entry in hook_list:
                    for h in h_entry.get("hooks", []):
                        cmd = h.get("command", "")
                        if "agy_pretooluse_gate.py" in cmd:
                            found = True
                            self.assertIn('"C:/Program Files/My Plugin/hooks/scripts/agy_pretooluse_gate.py"', cmd)
            self.assertTrue(found, "Did not find agy_pretooluse_gate hook in antigravity hooks")
        finally:
            if sys.path and sys.path[0] == os.path.join(ROOT, "scripts"):
                sys.path.pop(0)

    def test_utf8_io_switches_stdin(self):
        """force_utf8 must be able to switch stdin encoding as well (O03)."""
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        try:
            import utf8_io
            class FakeStream:
                def __init__(self, enc):
                    self.encoding = enc
                    self.reconfigured = False
                def reconfigure(self, encoding, errors=None):
                    del errors
                    self.encoding = encoding
                    self.reconfigured = True

            fake_in = FakeStream("cp1252")
            fake_out = FakeStream("utf-8")
            fake_err = FakeStream("utf-8")
            changed = utf8_io.force_utf8(out=fake_out, err=fake_err, inp=fake_in)
            self.assertEqual(changed, 1)
            self.assertTrue(fake_in.reconfigured)
            self.assertEqual(fake_in.encoding, "utf-8")
        finally:
            if sys.path and sys.path[0] == os.path.join(ROOT, "scripts"):
                sys.path.pop(0)


if __name__ == "__main__":
    unittest.main()
