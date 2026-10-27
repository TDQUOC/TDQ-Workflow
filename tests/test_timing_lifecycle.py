"""Run lifecycle CLIs in isolated projects and preserve timing evidence."""

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import helper  # Sets the script import path and disables machine setup.
import tdq_state
from tdq_transcript import claude_transcript_dir

OLD = "2026-10-27-0000-old-request"
NEW = "2026-10-27-0001-new-request"
START = "2026-10-27T00:00:00+00:00"


class TimingLifecycle(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.project = self.base / "project"
        self.home = self.base / "home"
        self.project.mkdir()
        self.home.mkdir()
        self.env = {"TDQ_PROJECT_DIR": str(self.project), "HOME": str(self.home),
                    "USERPROFILE": str(self.home), "TDQ_KHONG_CHAM_MAY": "1",
                    "TDQ_KHOI_TAO_NEN": "0"}
        self.history = self.project / "docs" / "tdq" / "timing.jsonl"

    def run_cli(self, script, *args):
        return subprocess.run(
            [sys.executable, str(Path(helper.ROOT) / "scripts" / script), *args],
            cwd=self.project, env={**os.environ, **self.env},
            capture_output=True, encoding="utf-8", text=True, timeout=30)

    def state_cli(self, *args):
        result = self.run_cli("tdq_state.py", *args)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def initialize(self):
        self.state_cli("init", OLD, "full")
        history = [{"phase": "analyze", "at": START}]
        self.state_cli("set", "phase=analyze", "started_at=" + START,
                       "phase_history=" + json.dumps(history))

    def write_jsonl(self, path, records):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(json.dumps(row) + "\n" for row in records),
                        encoding="utf-8")
        return path

    def codex(self):
        path = self.home / ".codex" / "sessions" / "2020" / "01" / "01" / "rollout.jsonl"
        return self.write_jsonl(path, [
            {"type": "session_meta", "timestamp": START,
             "payload": {"id": "codex-session", "cwd": str(self.project)}},
            {"type": "response_item", "timestamp": "2026-10-27T00:00:01Z",
             "payload": {"type": "function_call", "call_id": "call"}},
            {"type": "response_item", "timestamp": "2026-10-27T00:00:03Z",
             "payload": {"type": "function_call_output", "call_id": "call"}},
        ])

    def claude(self):
        path = Path(claude_transcript_dir(self.project, self.home)) / "session.jsonl"
        metadata = {"cwd": str(self.project), "sessionId": "claude-session"}
        return self.write_jsonl(path, [
            {**metadata, "type": "api-request", "id": "request", "timestamp": START},
            {**metadata, "type": "assistant", "requestRef": "request", "uuid": "reply",
             "timestamp": "2026-10-27T00:00:05Z",
             "message": {"content": [], "stop_reason": "end_turn"}},
        ])

    def rows(self):
        return [json.loads(line) for line in self.history.read_text(encoding="utf-8").splitlines()]

    def test_init_closes_codex_only_source_before_reset(self):
        self.initialize()
        self.codex()
        self.state_cli("init", NEW, "quick")
        rows = self.rows()
        self.assertEqual([row["slug"] for row in rows], [OLD])
        self.assertEqual(rows[0]["schema_version"], 2)
        self.assertEqual(rows[0]["metrics"]["tool_call_seconds"]["seconds"], 2)
        self.assertEqual(rows[0]["metrics"]["tool_call_seconds"]["quality"], "complete")
        self.assertIsNone(rows[0]["metrics"]["api_request_seconds"]["seconds"])
        self.assertIsNone(rows[0]["model_giay"])
        current = tdq_state.load(str(self.project), heal=False)
        self.assertEqual(current["active_request"], NEW)
        self.assertEqual(current["previous_request"], OLD)
        self.assertEqual(current["lane"], "quick")

    def test_init_closes_claude_source_with_project_metadata(self):
        self.initialize()
        self.claude()
        self.state_cli("init", NEW, "full")
        row = self.rows()[0]
        self.assertEqual(row["metrics"]["api_request_seconds"]["seconds"], 5)
        self.assertEqual(row["sources"][0]["status"], "accepted")

    def test_missing_logs_keep_wall_and_allow_new_request(self):
        self.initialize()
        self.state_cli("init", NEW, "full")
        row = self.rows()[0]
        self.assertGreater(row["treo_tuong_giay"], 0)
        self.assertEqual({metric["quality"] for metric in row["metrics"].values()}, {"unavailable"})
        self.assertEqual({metric["seconds"] for metric in row["metrics"].values()}, {None})
        self.assertEqual(tdq_state.load(str(self.project), heal=False)["active_request"], NEW)

    def test_malformed_log_keeps_partial_evidence_during_init(self):
        self.initialize()
        path = self.codex()
        with path.open("a", encoding="utf-8") as stream:
            stream.write("{broken\n")
        self.state_cli("init", NEW, "full")
        row = self.rows()[0]
        self.assertEqual(row["metrics"]["tool_call_seconds"]["seconds"], 2)
        self.assertEqual(row["metrics"]["tool_call_seconds"]["quality"], "partial")

    def test_finish_idle_uses_auto_source_and_new_init_does_not_duplicate(self):
        self.initialize()
        self.codex()
        finished = self.run_cli("tdq_finish.py", "--phase", "idle", "--log", "lifecycle fixture")
        self.assertEqual(finished.returncode, 0, finished.stderr)
        self.assertEqual(tdq_state.load(str(self.project), heal=False)["phase"], "idle")
        self.assertEqual(self.rows()[0]["metrics"]["tool_call_seconds"]["seconds"], 2)
        before = self.history.read_bytes()
        self.state_cli("init", NEW, "full")
        self.assertEqual(self.history.read_bytes(), before)
        self.assertEqual(len(self.rows()), 1)

    def test_finish_non_idle_leaves_timing_open(self):
        self.initialize()
        self.codex()
        result = self.run_cli("tdq_finish.py", "--phase", "analyze", "--log", "ongoing fixture")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.history.exists())

    def test_empty_project_first_init_has_no_history_to_close(self):
        self.state_cli("init", OLD, "full")
        self.assertFalse(self.history.exists())

    def test_existing_log_setting_is_restored_after_success(self):
        self.initialize()
        self.codex()
        stderr = io.StringIO()
        with patch.dict(os.environ, {**self.env, "TDQ_LOG": "trace"}), contextlib.redirect_stderr(stderr):
            self.assertTrue(tdq_state._dong_so_request_cu(str(self.project)))
            self.assertEqual(os.environ["TDQ_LOG"], "trace")
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(self.rows()[0]["metrics"]["tool_call_seconds"]["seconds"], 2)

    def test_absent_log_setting_is_restored_after_success(self):
        self.initialize()
        self.codex()
        with patch.dict(os.environ, self.env):
            os.environ.pop("TDQ_LOG", None)
            self.assertTrue(tdq_state._dong_so_request_cu(str(self.project)))
            self.assertNotIn("TDQ_LOG", os.environ)

    def test_log_setting_is_restored_after_real_filesystem_error(self):
        self.initialize()
        self.codex()
        self.history.mkdir()
        for setting in (None, "0", "trace"):
            with self.subTest(setting=setting), patch.dict(os.environ, self.env):
                if setting is None:
                    os.environ.pop("TDQ_LOG", None)
                else:
                    os.environ["TDQ_LOG"] = setting
                stderr = io.StringIO()
                with contextlib.redirect_stderr(stderr):
                    self.assertFalse(tdq_state._dong_so_request_cu(str(self.project)))
                self.assertEqual(os.environ.get("TDQ_LOG"), setting)
                if setting == "0":
                    self.assertEqual(stderr.getvalue(), "")
                else:
                    self.assertIn("could not close", stderr.getvalue())
                self.assertTrue(self.history.is_dir())

    def test_init_survives_real_timing_write_error(self):
        self.initialize()
        self.codex()
        self.history.mkdir()
        result = self.state_cli("init", NEW, "full")
        self.assertIn("could not close", result.stderr)
        self.assertEqual(tdq_state.load(str(self.project), heal=False)["active_request"], NEW)
        self.assertTrue(self.history.is_dir())

    def test_close_without_request_does_not_leak_log_setting(self):
        with patch.dict(os.environ, {**self.env, "TDQ_LOG": "trace"}):
            self.assertFalse(tdq_state._dong_so_request_cu(str(self.project)))
            self.assertEqual(os.environ["TDQ_LOG"], "trace")
        self.assertFalse(self.history.exists())


if __name__ == "__main__":
    unittest.main()
