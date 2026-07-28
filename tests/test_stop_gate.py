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

    def stop(self, invite_target, body="Plan xong.", **overrides):
        tp = write_transcript(self.tdir, body + "\n" + INVITE.format(t=invite_target))
        return run_hook("stop_gate.py",
                        load_fixture("stop.json", cwd=self.cwd, transcript_path=tp, **overrides))

    def stop_text(self, text, **overrides):
        # log là file mới nhất -> loại nhánh chặn "repo đổi mà chưa log"
        write_file(self.cwd, f"docs/workinglog/{datetime.date.today():%Y-%m-%d}.md", "# log\n")
        tp = write_transcript(self.tdir, text)
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

    def test_command_mentioned_in_body_is_not_an_invite(self):
        # Nhắc TÊN LỆNH trong thân plan (vd mô tả cú pháp mới) không phải lời mời
        # duyệt — chỉ dòng bắt đầu bằng "➤ Để duyệt:" mới tính.
        write_state(self.cwd, active_request="r1", lane="quick")
        body = "Bước 4: đổi dòng mời thành `/tdq-workflow:tdq-approve plan main|subagent`."
        rc, out, _ = self.stop("quick", body=body)
        self.assertEqual(rc, 0)
        self.assertEqual(out, "")

    def test_block_plan_invite_without_mode(self):
        # Lane full, plan đã đăng ký: dòng mời duyệt plan phải kèm mode cho user chọn.
        write_state(self.cwd, active_request="r1", lane="full", spec_approved=True,
                    plan_file="docs/tdq/plan/p.md")
        write_file(self.cwd, "docs/tdq/plan/p.md", "# plan\n")
        rc, out, _ = self.stop_text(
            "Plan xong.\n➤ Để duyệt: gõ /tdq-workflow:tdq-approve plan · Góp ý: nhắn trực tiếp")
        self.assertEqual(rc, 0)
        self.assertIn("mode", self.blocked(out).lower())

    def test_block_invite_when_plan_file_has_no_mode_proposal(self):
        # Bắt sớm ở turn trình plan, thay vì để user gõ lệnh rồi mới trượt.
        write_state(self.cwd, active_request="r1", lane="full", spec_approved=True,
                    plan_file="docs/tdq/plan/p.md")
        write_file(self.cwd, "docs/tdq/plan/p.md", "# plan\n- [ ] t1\n")
        rc, out, _ = self.stop_text(
            "Plan xong.\n➤ Để duyệt: gõ /tdq-workflow:tdq-approve plan main|subagent · "
            "Góp ý: nhắn trực tiếp")
        self.assertEqual(rc, 0)
        reason = self.blocked(out)
        self.assertIn("đề xuất mode", reason.lower())
        self.assertIn("docs/tdq/plan/p.md", reason)

    def test_silent_plan_invite_with_mode(self):
        write_state(self.cwd, active_request="r1", lane="full", spec_approved=True,
                    plan_file="docs/tdq/plan/p.md")
        write_file(self.cwd, "docs/tdq/plan/p.md", "# plan\nĐề xuất mode: **main**\n")
        rc, out, _ = self.stop_text(
            "Plan xong.\n➤ Để duyệt: gõ /tdq-workflow:tdq-approve plan main|subagent · "
            "Góp ý: nhắn trực tiếp")
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
