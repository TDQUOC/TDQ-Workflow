"""B5 — stop_gate.py: block end-of-turn when repo changed but working log stale."""
import datetime
import json
import os
import tempfile
import time
import unittest

from helper import run_hook, load_fixture, write_state, write_file


class TestStopGate(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def stop(self, **overrides):
        return run_hook("stop_gate.py", load_fixture("stop.json", cwd=self.cwd, **overrides))

    def today_log(self):
        return f"docs/workinglog/{datetime.date.today().strftime('%Y-%m-%d')}.md"

    def test_stop_hook_active_silent(self):
        write_state(self.cwd, active_request="r1", lane="full")
        write_file(self.cwd, "src/a.py")
        rc, out, _ = self.stop(stop_hook_active=True)
        self.assertEqual(rc, 0)
        self.assertEqual(out, "")

    def test_no_state_silent(self):
        write_file(self.cwd, "src/a.py")
        rc, out, _ = self.stop()
        self.assertEqual(rc, 0)
        self.assertEqual(out, "")

    def test_block_when_change_after_log(self):
        write_state(self.cwd, active_request="r1", lane="full")
        log = write_file(self.cwd, self.today_log(), "# log\n")
        old = time.time() - 300
        os.utime(log, (old, old))
        write_file(self.cwd, "src/fresh.py", "print('x')\n")
        rc, out, _ = self.stop()
        self.assertEqual(rc, 0)
        data = json.loads(out)
        self.assertEqual(data["decision"], "block")
        self.assertIn("docs/workinglog", data["reason"])

    def test_silent_when_log_is_newest(self):
        write_state(self.cwd, active_request="r1", lane="full")
        src = write_file(self.cwd, "src/a.py")
        old = time.time() - 300
        os.utime(src, (old, old))
        write_file(self.cwd, self.today_log(), "# log moi nhat\n")
        rc, out, _ = self.stop()
        self.assertEqual(rc, 0)
        self.assertEqual(out, "")


if __name__ == "__main__":
    unittest.main()
