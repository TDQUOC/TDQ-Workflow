"""B5 — stop_gate.py: block end-of-turn when repo changed but working log stale."""
import datetime
import json
import os
import tempfile
import time
import unittest

from helper import run_hook, load_fixture, write_state, write_file, write_transcript

INVITE = "➤ Để duyệt: gõ /tdq-workflow:tdq-approve {t} · Góp ý: nhắn trực tiếp"


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


class TestStopGateInvite(unittest.TestCase):
    """Dòng mời duyệt chỉ được phép tới tay user khi state đỡ được nó."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name
        # transcript nằm ngoài project (giống thực tế: ~/.claude/projects/...)
        self._ttmp = tempfile.TemporaryDirectory()
        self.tdir = self._ttmp.name
        # log mới nhất -> loại trừ nhánh chặn vì working log cũ
        write_file(self.cwd, f"docs/workinglog/{datetime.date.today():%Y-%m-%d}.md", "# log\n")

    def tearDown(self):
        self._tmp.cleanup()
        self._ttmp.cleanup()

    def stop(self, invite_target, **overrides):
        tp = write_transcript(self.tdir, "Plan xong.\n" + INVITE.format(t=invite_target))
        return run_hook("stop_gate.py",
                        load_fixture("stop.json", cwd=self.cwd, transcript_path=tp, **overrides))

    def blocked(self, out):
        self.assertTrue(out, "expected a block decision, got silence")
        data = json.loads(out)
        self.assertEqual(data["decision"], "block")
        return data["reason"]

    def test_block_invite_without_request(self):
        rc, out, _ = self.stop("quick")
        self.assertEqual(rc, 0)
        self.assertIn("chưa có request", self.blocked(out).lower())

    def test_block_invite_wrong_lane(self):
        write_state(self.cwd, active_request="r1", lane="full")
        rc, out, _ = self.stop("quick")
        self.assertEqual(rc, 0)
        self.assertIn("lane", self.blocked(out).lower())

    def test_block_invite_plan_not_registered(self):
        write_state(self.cwd, active_request="r1", lane="full", spec_approved=True)
        rc, out, _ = self.stop("plan")
        self.assertEqual(rc, 0)
        self.assertIn("plan", self.blocked(out).lower())

    def test_silent_when_invite_valid(self):
        write_state(self.cwd, active_request="r1", lane="quick")
        rc, out, _ = self.stop("quick")
        self.assertEqual(rc, 0)
        self.assertEqual(out, "")

    def test_silent_when_already_approved_and_no_invite(self):
        write_state(self.cwd, active_request="r1", lane="quick", quick_approved=True)
        tp = write_transcript(self.tdir, "Đã implement xong, không mời duyệt gì cả.")
        rc, out, _ = run_hook("stop_gate.py",
                              load_fixture("stop.json", cwd=self.cwd, transcript_path=tp))
        self.assertEqual(rc, 0)
        self.assertEqual(out, "")


if __name__ == "__main__":
    unittest.main()
