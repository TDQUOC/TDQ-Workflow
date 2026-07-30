"""stop_gate.py (0.3.0) — đối chiếu lời nhắc với hiệu ứng thật trong sổ turn.

Điểm CHẶN duy nhất: repo đổi mà working log hôm nay chưa được append.
Không đọc transcript, không tin dòng echo model tự in.
"""
import datetime
import json
import os
import subprocess
import tempfile
import unittest

from helper import run_hook, load_fixture, write_state, tdq_state

SESSION = "s1"


class StopGateBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cwd = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    def stop(self, **overrides):
        payload = load_fixture("stop.json", cwd=self.cwd, session_id=SESSION, **overrides)
        return run_hook("stop_gate.py", payload)

    def today_log(self):
        return f"docs/workinglog/{datetime.date.today().strftime('%Y-%m-%d')}.md"

    def remind(self, code):
        tdq_state.turn_log_append(self.cwd, "remind", session=SESSION, code=code)

    def observe(self, event, **fields):
        tdq_state.turn_log_append(self.cwd, "observe", session=SESSION, event=event, **fields)


class TestStopGate(StopGateBase):
    def test_stop_hook_active_silent(self):
        write_state(self.cwd, active_request="r1", lane="full")
        self.observe("edit", path="src/a.py")
        rc, out, _ = self.stop(stop_hook_active=True)
        self.assertEqual(rc, 0)
        self.assertEqual(out, "")

    def test_no_state_silent(self):
        self.observe("edit", path="src/a.py")
        rc, out, _ = self.stop()
        self.assertEqual(rc, 0)
        self.assertEqual(out, "")

    def test_block_when_repo_changed_without_log(self):
        write_state(self.cwd, active_request="r1", lane="full")
        self.observe("edit", path="src/fresh.py")
        rc, out, _ = self.stop()
        self.assertEqual(rc, 0)
        data = json.loads(out)
        self.assertEqual(data["decision"], "block")
        self.assertIn("docs/workinglog", data["reason"])
        self.assertIn("src/fresh.py", data["reason"])

    def test_silent_after_log_written(self):
        write_state(self.cwd, active_request="r1", lane="full")
        self.observe("edit", path="src/a.py")
        self.observe("edit", path=self.today_log())
        self.observe("log_written", path=self.today_log())
        rc, out, _ = self.stop()
        self.assertEqual(rc, 0)
        self.assertEqual(out, "")

    def test_log_only_edit_is_not_a_repo_change(self):
        """Sửa mỗi working log thì không tự đòi log lần nữa (tránh vòng lặp)."""
        write_state(self.cwd, active_request="r1", lane="full")
        self.observe("edit", path=self.today_log())
        self.observe("log_written", path=self.today_log())
        rc, out, _ = self.stop()
        self.assertEqual(out, "")

    def test_no_edit_no_block(self):
        write_state(self.cwd, active_request="r1", lane="full")
        rc, out, _ = self.stop()
        self.assertEqual(out, "")


class TestStopGateHints(StopGateBase):
    """Mã đã nhắc mà không thấy hiệu ứng → nhắc lại qua additionalContext."""

    def context(self, out):
        return json.loads(out)["hookSpecificOutput"]["additionalContext"]

    def test_next_reminded_but_never_run(self):
        write_state(self.cwd, active_request="r1", lane="full", spec_approved=True,
                    plan_approved=True)
        self.remind("TDQ:NEXT")
        rc, out, _ = self.stop()
        self.assertIn("[TDQ:NEXT]", self.context(out))

    def test_next_reminded_and_run_is_silent(self):
        write_state(self.cwd, active_request="r1", lane="full", spec_approved=True,
                    plan_approved=True)
        self.remind("TDQ:NEXT")
        self.observe("next_run")
        rc, out, _ = self.stop()
        self.assertEqual(out, "")

    def test_state_reminded_but_no_cli_call(self):
        write_state(self.cwd, active_request="r1", lane="full", spec_approved=True,
                    plan_approved=True)
        self.remind("TDQ:STATE")
        rc, out, _ = self.stop()
        self.assertIn("[TDQ:STATE]", self.context(out))

    def test_approve_reminded_and_still_unapproved(self):
        write_state(self.cwd, active_request="r1", lane="full")
        self.remind("TDQ:APPROVE")
        rc, out, _ = self.stop()
        ctx = self.context(out)
        self.assertIn("[TDQ:APPROVE]", ctx)
        self.assertIn("HỎI", ctx)

    def test_approve_reminded_but_now_approved_is_silent(self):
        write_state(self.cwd, active_request="r1", lane="full", spec_approved=True,
                    plan_approved=True, quick_approved=True)
        self.remind("TDQ:APPROVE")
        rc, out, _ = self.stop()
        self.assertEqual(out, "")

    def test_git_reminder_is_repeated(self):
        write_state(self.cwd, active_request="r1", lane="full", spec_approved=True,
                    plan_approved=True)
        self.remind("TDQ:GIT")
        rc, out, _ = self.stop()
        self.assertIn("[TDQ:GIT]", self.context(out))

    def test_budget(self):
        write_state(self.cwd, active_request="r1", lane="full")
        for code in ("TDQ:NEXT", "TDQ:STATE", "TDQ:APPROVE", "TDQ:GIT"):
            self.remind(code)
        rc, out, _ = self.stop()
        ctx = self.context(out)
        self.assertLessEqual(len(ctx.splitlines()), 4)
        self.assertLessEqual(len(ctx), 300)

    def test_block_wins_over_hints(self):
        write_state(self.cwd, active_request="r1", lane="full")
        self.remind("TDQ:GIT")
        self.observe("edit", path="src/a.py")
        rc, out, _ = self.stop()
        self.assertEqual(json.loads(out)["decision"], "block")


class TestStopGateDiskEffects(StopGateBase):
    """P3 (0.3.1) — hiệu ứng THẬT trên đĩa, không chỉ tin sổ turn.

    Sổ turn chỉ ghi được hành động đi qua tool Edit/Write. Mọi thay đổi qua shell
    trước đây vô hình → vừa chặn oan (log ghi bằng `cat >>`) vừa bỏ lọt (sửa repo
    bằng `sed -i`). Nhóm test này khoá cả hai chiều.
    """

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.cwd, capture_output=True, timeout=30)

    def snapshot(self):
        """Giả lập prompt_context: chụp trạng thái đĩa lúc mở turn."""
        tdq_state.turn_log_append(self.cwd, "turn_start", session=SESSION,
                                  **tdq_state.turn_snapshot(self.cwd))

    def write(self, rel, content="x\n", mode="w"):
        path = os.path.join(self.cwd, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, mode, encoding="utf-8") as f:
            f.write(content)
        return path

    # --------------------------------------------------- chiều 1: chặn oan
    def test_shell_append_log_not_blocked(self):
        """Bug gốc: log append bằng shell → không có `log_written` → chặn oan."""
        write_state(self.cwd, active_request="r1", lane="full")
        self.write(self.today_log(), "# log\n")
        self.snapshot()
        self.observe("edit", path="src/a.py")
        self.write(self.today_log(), "\n## 02:00 — việc\n", mode="a")   # không qua Edit
        rc, out, _ = self.stop()
        self.assertEqual(rc, 0)
        self.assertEqual(out, "", "log đã append thật mà vẫn bị chặn")

    def test_shell_created_log_not_blocked(self):
        """Log hôm nay chưa tồn tại đầu turn, được tạo bằng shell trong turn."""
        write_state(self.cwd, active_request="r1", lane="full")
        self.snapshot()
        self.observe("edit", path="src/a.py")
        self.write(self.today_log(), "# log\n")
        rc, out, _ = self.stop()
        self.assertEqual(out, "")

    def test_untouched_log_still_blocks(self):
        """Có ảnh chụp nhưng log KHÔNG đổi → vẫn phải chặn."""
        write_state(self.cwd, active_request="r1", lane="full")
        self.write(self.today_log(), "# log\n")
        self.snapshot()
        self.observe("edit", path="src/a.py")
        rc, out, _ = self.stop()
        self.assertEqual(json.loads(out)["decision"], "block")

    def test_non_git_repo_log_via_shell_not_blocked(self):
        """Không phải git repo → repo_sha None, nhưng chiều log vẫn vá được."""
        write_state(self.cwd, active_request="r1", lane="full")
        self.write(self.today_log(), "# log\n")
        self.snapshot()
        self.assertIsNone(tdq_state.repo_status_digest(self.cwd))
        self.observe("edit", path="src/a.py")
        self.write(self.today_log(), "x\n", mode="a")
        rc, out, _ = self.stop()
        self.assertEqual(out, "")

    # --------------------------------------------------- chiều 2: bỏ lọt
    def test_shell_only_change_is_blocked(self):
        """Sửa repo hoàn toàn bằng shell (không `observe` nào) → phải chặn."""
        self.git("init", "-q")
        write_state(self.cwd, active_request="r1", lane="full")
        self.snapshot()
        self.write(os.path.join("src", "a.py"), "print(1)\n")
        rc, out, _ = self.stop()
        data = json.loads(out)
        self.assertEqual(data["decision"], "block")
        self.assertIn("src/a.py", data["reason"])

    def test_shell_change_with_shell_log_is_silent(self):
        self.git("init", "-q")
        write_state(self.cwd, active_request="r1", lane="full")
        self.snapshot()
        self.write(os.path.join("src", "a.py"), "print(1)\n")
        self.write(self.today_log(), "# log\n")
        rc, out, _ = self.stop()
        self.assertEqual(out, "")

    def test_state_bookkeeping_alone_does_not_block(self):
        """Chỉ ghi state/sổ turn thì không phải "đổi repo" — tránh chặn oan mới."""
        self.git("init", "-q")
        write_state(self.cwd, active_request="r1", lane="full")
        self.snapshot()
        write_state(self.cwd, active_request="r1", lane="full", phase="spec")
        rc, out, _ = self.stop()
        self.assertEqual(out, "")

    def test_clean_git_repo_no_block(self):
        self.git("init", "-q")
        write_state(self.cwd, active_request="r1", lane="full")
        self.snapshot()
        rc, out, _ = self.stop()
        self.assertEqual(out, "")

    # --------------------------------------------------- fallback & resilience
    def test_no_snapshot_behaves_like_030(self):
        write_state(self.cwd, active_request="r1", lane="full")
        self.observe("edit", path="src/a.py")
        rc, out, _ = self.stop()
        self.assertEqual(json.loads(out)["decision"], "block")

    def test_malformed_turn_start_row(self):
        write_state(self.cwd, active_request="r1", lane="full")
        tdq_state.turn_log_append(self.cwd, "turn_start", session=SESSION,
                                  log_rel=123, log_sha=[], repo_sha={})
        self.observe("edit", path="src/a.py")
        rc, out, err = self.stop()
        self.assertEqual(rc, 0, err)
        self.assertNotIn("Traceback", err)   # log service được phép in, crash thì không
        self.assertEqual(json.loads(out)["decision"], "block")

    def test_last_turn_start_row_wins(self):
        """0.3.2 — sổ turn còn sót dòng cũ (turn_log_clear hụt) thì phải lấy ảnh
        chụp MỚI NHẤT; lấy dòng đầu là so với baseline có thể cũ tới 6 giờ."""
        write_state(self.cwd, active_request="r1", lane="full")
        self.write(self.today_log(), "# log\n")
        self.snapshot()                      # ảnh chụp sót lại của turn TRƯỚC
        self.write(self.today_log(), "x\n", mode="a")   # log của turn TRƯỚC
        self.snapshot()                      # ảnh chụp của turn NÀY
        self.observe("edit", path="src/a.py")
        rc, out, _ = self.stop()
        self.assertIn("[TDQ:LOG]", out)      # turn này chưa ghi log → vẫn phải chặn


class TestStopGateNoFalseBlock(StopGateBase):
    """0.3.2 — chặn oan do chính vân tay repo.

    0.3.1 so vân tay TOÀN repo nhưng chỉ loại trừ sổ sách lúc ĐẶT TÊN, nên hook
    tự append `.tdq-turn.jsonl` sau khi chụp baseline là đủ làm vân tay đổi →
    file bẩn có sẵn bị lôi ra làm vật tế thần, kể cả trong turn read-only.
    """

    git = TestStopGateDiskEffects.git
    snapshot = TestStopGateDiskEffects.snapshot
    write = TestStopGateDiskEffects.write

    def dirty_repo(self):
        write_state(self.cwd, active_request="r1", lane="full")
        self.git("init", "-q")
        self.write("a.py", "dở dang từ turn trước\n")
        self.write(self.today_log(), "# log\n")
        self.snapshot()

    def test_readonly_turn_with_dirty_repo_not_blocked(self):
        self.dirty_repo()
        self.remind("TDQ:NEXT")
        self.observe("next_run")
        rc, out, _ = self.stop()
        self.assertEqual(rc, 0)
        self.assertNotIn("[TDQ:LOG]", out)

    def test_state_write_only_turn_not_blocked(self):
        self.dirty_repo()
        self.write("docs/tdq/STATE.md", "# state\nphase: plan\n")
        self.observe("state_cli")
        rc, out, _ = self.stop()
        self.assertNotIn("[TDQ:LOG]", out)

    def test_touch_untracked_not_blocked(self):
        """Ghi đè y hệt byte / `touch` không phải là thay đổi repo."""
        self.dirty_repo()
        path = self.write("scratch.txt", "same\n")
        self.snapshot()
        st = os.stat(path)
        os.utime(path, ns=(st.st_atime_ns + 10 ** 9, st.st_mtime_ns + 10 ** 9))
        rc, out, _ = self.stop()
        self.assertNotIn("[TDQ:LOG]", out)

    def test_real_change_still_blocked(self):
        """Không hồi quy: sửa file thật bằng shell vẫn phải chặn."""
        self.dirty_repo()
        self.write("src/new.py", "print(1)\n")
        rc, out, _ = self.stop()
        self.assertIn("[TDQ:LOG]", out)
        self.assertIn("src/new.py", out)

    def test_block_logs_to_stderr(self):
        """§6 — quyết định chặn phải có dấu vết debug được."""
        self.dirty_repo()
        self.write("src/new.py", "print(1)\n")
        rc, out, err = self.stop()
        self.assertIn("[TDQ:LOG]", out)
        self.assertIn("stop_gate", err)

    def test_tdq_log_0_silences_stderr(self):
        self.dirty_repo()
        self.write("src/new.py", "print(1)\n")
        payload = load_fixture("stop.json", cwd=self.cwd, session_id=SESSION)
        rc, out, err = run_hook("stop_gate.py", payload, env={"TDQ_LOG": "0"})
        self.assertIn("[TDQ:LOG]", out)
        self.assertEqual(err, "")


if __name__ == "__main__":
    unittest.main()
