"""P2/T2.12 — hook không bao giờ làm hỏng tool call (spec §4.7).

Mọi hook × mọi trạng thái xấu: exit 0, không stack trace, stdout hoặc rỗng hoặc
JSON hợp lệ.
"""
import os
import tempfile
import unittest

from helper import run_hook, tdq_state, write_state

HOOKS = ["session_start.py", "prompt_context.py", "edit_gate.py", "bash_gate.py", "stop_gate.py"]
BASE = {
    "session_start.py": {"hook_event_name": "SessionStart"},
    "prompt_context.py": {"hook_event_name": "UserPromptSubmit", "prompt": "tiếp"},
    "edit_gate.py": {"hook_event_name": "PreToolUse", "tool_name": "Edit",
                     "tool_input": {"file_path": "src/a.py"}},
    "bash_gate.py": {"hook_event_name": "PreToolUse", "tool_name": "Bash",
                     "tool_input": {"command": "ls"}},
    "stop_gate.py": {"hook_event_name": "Stop", "stop_hook_active": False},
}


class ResilienceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name
        self.addCleanup(self.tmp.cleanup)

    def test_corrupt_state(self):
        os.makedirs(os.path.join(self.cwd, "docs", "tdq"))
        with open(tdq_state.state_path(self.cwd), "w", encoding="utf-8") as f:
            f.write("{ hong")
        for script in HOOKS:
            with self.subTest(script=script):
                payload = dict(BASE[script], cwd=self.cwd, session_id="s")
                rc, out, err = run_hook(script, payload)
                self.assertEqual(rc, 0, err)
                self.assertNotIn("Traceback", err)

    def test_readonly_docs_dir(self):
        write_state(self.cwd, active_request="r", lane="full", phase="implement")
        tdq_dir = os.path.join(self.cwd, "docs", "tdq")
        os.chmod(tdq_dir, 0o500)
        self.addCleanup(os.chmod, tdq_dir, 0o700)
        for script in HOOKS:
            with self.subTest(script=script):
                payload = dict(BASE[script], cwd=self.cwd, session_id="s")
                rc, out, err = run_hook(script, payload)
                self.assertEqual(rc, 0, err)
                self.assertNotIn("Traceback", err)

    def test_missing_payload_keys(self):
        write_state(self.cwd, active_request="r", lane="full", phase="implement")
        for script in HOOKS:
            with self.subTest(script=script):
                for payload in ({}, {"cwd": self.cwd}, {"cwd": self.cwd, "tool_input": None}):
                    rc, out, err = run_hook(script, payload)
                    self.assertEqual(rc, 0, f"{script}: {err}")
                    self.assertNotIn("Traceback", err, f"{script}: {err}")

    def test_invalid_json_stdin(self):
        import subprocess
        import sys
        from helper import HOOKS as HOOK_DIR
        for script in HOOKS:
            with self.subTest(script=script):
                proc = subprocess.run([sys.executable, os.path.join(HOOK_DIR, script)],
                                      input="khong-phai-json", capture_output=True,
                                      text=True, timeout=30)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertNotIn("Traceback", proc.stderr)


if __name__ == "__main__":
    unittest.main()
