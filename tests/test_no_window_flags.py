"""Tests ensuring all subprocess calls on Windows enforce CREATE_NO_WINDOW to eliminate console flashing."""
import os
import sys
import unittest

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tdq_ten_lenh  # noqa: E402


class NoWindowFlagsTests(unittest.TestCase):
    def test_tdq_ten_lenh_an_cua_so_windows(self):
        flags = tdq_ten_lenh.tham_so_subprocess_an_cua_so("win32")
        self.assertIn("creationflags", flags)
        self.assertEqual(flags["creationflags"], 0x08000000)

    def test_tdq_ten_lenh_an_cua_so_posix(self):
        self.assertEqual(tdq_ten_lenh.tham_so_subprocess_an_cua_so("linux"), {})
        self.assertEqual(tdq_ten_lenh.tham_so_subprocess_an_cua_so("darwin"), {})

    def test_session_start_popen_creationflags(self):
        path = os.path.join(ROOT, "hooks", "scripts", "session_start.py")
        with open(path, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("0x08000000", content)
        self.assertIn("CREATE_NO_WINDOW", content)

    def test_codex_edit_gate_subprocess_creationflags(self):
        path = os.path.join(ROOT, "hooks", "scripts", "codex_edit_gate.py")
        with open(path, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("0x08000000", content)
        self.assertIn("CREATE_NO_WINDOW", content)

    def test_tdq_state_git_creationflags(self):
        path = os.path.join(ROOT, "scripts", "tdq_state.py")
        with open(path, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("0x08000000", content)
        self.assertIn("CREATE_NO_WINDOW", content)

    def test_tdq_team_git_chay_subprocess(self):
        path = os.path.join(ROOT, "scripts", "tdq_team.py")
        with open(path, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("tdq_ten_lenh.chay_subprocess", content)
        # Verify no raw unflagged subprocess.run remains in tdq_team.py
        self.assertNotIn("subprocess.run([", content)

    def test_tdq_test_git_chay_subprocess(self):
        path = os.path.join(ROOT, "scripts", "tdq_test.py")
        with open(path, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("tdq_ten_lenh.chay_subprocess", content)

    def test_tdq_devtool_mcp_launch_chrome_flags(self):
        path = os.path.join(ROOT, "scripts", "tdq_devtool_mcp.py")
        with open(path, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("0x08000000", content)


if __name__ == "__main__":
    unittest.main()
