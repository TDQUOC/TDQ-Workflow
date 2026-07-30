"""P2 — sổ turn docs/tdq/.tdq-turn.jsonl (T2.1, T2.2)."""
import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

from helper import load_fixture, run_hook, tdq_state


class TurnLedgerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name
        self.addCleanup(self.tmp.cleanup)

    def _raw(self, rows):
        path = tdq_state.turn_log_path(self.cwd)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

    def test_append_read_and_stale_skip(self):
        tdq_state.turn_log_append(self.cwd, "remind", session="s1", code="TDQ:LOG")
        tdq_state.turn_log_append(self.cwd, "observe", session="s1", event="edit", path="a.py")
        tdq_state.turn_log_append(self.cwd, "observe", session="s2", event="edit", path="b.py")
        rows = tdq_state.turn_log_read(self.cwd, session="s1")
        self.assertEqual(len(rows), 2)
        self.assertEqual({r["kind"] for r in rows}, {"remind", "observe"})
        self.assertEqual(len(tdq_state.turn_log_read(self.cwd, session="s2")), 1)

        old = (datetime.now(timezone.utc) - timedelta(hours=7)).astimezone().isoformat(timespec="seconds")
        self._raw([{"ts": old, "session": "s1", "kind": "remind", "code": "TDQ:LOG"}])
        self.assertEqual(tdq_state.turn_log_read(self.cwd, session="s1"), [])

    def test_bad_lines_ignored(self):
        path = tdq_state.turn_log_path(self.cwd)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write("khong-phai-json\n\n[1,2]\n")
            f.write(json.dumps({"ts": tdq_state.now_iso(), "session": "s1",
                                "kind": "observe", "event": "edit"}) + "\n")
        self.assertEqual(len(tdq_state.turn_log_read(self.cwd, session="s1")), 1)

    def test_missing_file_is_empty(self):
        self.assertEqual(tdq_state.turn_log_read(self.cwd, session="s1"), [])

    def test_append_never_raises(self):
        blocked = os.path.join(self.cwd, "ro")
        os.makedirs(os.path.join(blocked, "docs", "tdq"))
        os.chmod(os.path.join(blocked, "docs", "tdq"), 0o500)
        self.addCleanup(os.chmod, os.path.join(blocked, "docs", "tdq"), 0o700)
        tdq_state.turn_log_append(blocked, "remind", session="s1", code="TDQ:LOG")  # không raise

    def test_clear_only_current_session(self):
        tdq_state.turn_log_append(self.cwd, "remind", session="s1", code="TDQ:LOG")
        tdq_state.turn_log_append(self.cwd, "remind", session="s2", code="TDQ:GIT")
        tdq_state.turn_log_clear(self.cwd, "s1")
        self.assertEqual(tdq_state.turn_log_read(self.cwd, session="s1"), [])
        self.assertEqual(len(tdq_state.turn_log_read(self.cwd, session="s2")), 1)


class TurnStartRowTest(unittest.TestCase):
    """T2.1 — prompt_context phải chụp trạng thái đĩa ngay khi mở turn."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = self.tmp.name
        self.addCleanup(self.tmp.cleanup)

    def _run(self, session="s1"):
        payload = load_fixture("prompt.json", cwd=self.cwd, session_id=session)
        return run_hook("prompt_context.py", payload)

    def _starts(self, session="s1"):
        return [r for r in tdq_state.turn_log_read(self.cwd, session=session)
                if r.get("kind") == "turn_start"]

    def test_prompt_context_writes_turn_start(self):
        rc, _, err = self._run()
        self.assertEqual(rc, 0, err)
        rows = self._starts()
        self.assertEqual(len(rows), 1, rows)
        self.assertEqual(set(rows[0]) & {"log_rel", "log_sha", "repo_sha"},
                         {"log_rel", "log_sha", "repo_sha"})
        self.assertEqual(rows[0]["log_rel"], tdq_state.today_log_rel())

    def test_turn_start_is_reset_each_turn(self):
        self._run()
        self._run()
        self.assertEqual(len(self._starts()), 1)

    def test_turn_start_scoped_to_session(self):
        self._run(session="s1")
        self._run(session="s2")
        self.assertEqual(len(self._starts("s1")), 1)
        self.assertEqual(len(self._starts("s2")), 1)


if __name__ == "__main__":
    unittest.main()
