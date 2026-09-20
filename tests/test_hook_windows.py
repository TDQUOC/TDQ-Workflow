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
    "bash_gate.py": ({"hook_event_name": "PreToolUse", "tool_name": "Bash",
                      "tool_input": {"command": "git commit -m x"}}, ""),
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


if __name__ == "__main__":
    unittest.main()
