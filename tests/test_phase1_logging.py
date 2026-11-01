"""Lock the runtime log contract through isolated, real CLI processes."""

import datetime
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import helper

SCRIPTS = Path(helper.ROOT) / "scripts"
START = "2026-10-27T00:00:00+00:00"
END = "2026-10-27T00:00:20+00:00"
LOG_LINE = re.compile(r"^\[([^\]]+)\] \S")
PASSING_TEST = (
    "import unittest\n"
    "class Contract(unittest.TestCase):\n"
    "    def test_arithmetic(self):\n"
    "        self.assertEqual(2 + 3, 5)\n"
)


class Phase1Logging(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="tdq-log-contract-")
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.project = self.base / "project"
        self.home = self.base / "home"
        self.project.mkdir()
        self.home.mkdir()
        self.env = dict(os.environ, TDQ_PROJECT_DIR=str(self.project),
                        HOME=str(self.home), USERPROFILE=str(self.home),
                        TDQ_KHONG_CHAM_MAY="1", TDQ_KHOI_TAO_NEN="0")
        self.env.pop("TDQ_LOG", None)
        self.ledger = self.project / "docs" / "tdq" / ".tdq-test.jsonl"
        self._state("init", "2026-10-27-0000-logging", "full")
        history = [{"phase": "analyze", "at": START}]
        self._state("set", "phase=analyze", "started_at=" + START,
                    "phase_history=" + json.dumps(history))

    def _run(self, script, *args, log=None):
        env = self.env.copy()
        if log is not None:
            env["TDQ_LOG"] = log
        return subprocess.run(
            [sys.executable, str(SCRIPTS / script), *args],
            cwd=self.project, env=env, capture_output=True,
            encoding="utf-8", text=True, timeout=30)

    def _state(self, *args):
        result = self._run("tdq_state.py", *args, log="0")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def _write(self, relative, content):
        path = self.project / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def _timing(self, command, *, log=None, source=None):
        args = [command, "--json", "--project", str(self.project),
                "--now", END]
        if source is not None:
            args += ["--transcript-dir", str(source)]
        return self._run("tdq_timing.py", *args, log=log)

    def _runner(self, path, *, log=None):
        return self._run(
            "tdq_test.py", "vung-cham", "--repo", str(self.project),
            "--silent", "--khong-ep-tron-bo", "--files", path, log=log)

    def _json(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertIsInstance(payload, dict)
        return payload

    def _assert_timestamped(self, result):
        self.assertTrue(result.stderr, "Default logging must be enabled")
        for line in result.stderr.splitlines():
            match = LOG_LINE.match(line)
            self.assertIsNotNone(match, line)
            timestamp = datetime.datetime.fromisoformat(match[1])
            self.assertIsNotNone(timestamp.tzinfo, line)
        self.assertNotRegex(result.stdout, r"(?m)^\[\d{4}-\d{2}-\d{2}T")

    def _assert_runner_log(self, result, log, scope, status, tests_run):
        self.assertEqual(result.returncode, 0 if status == "PASS" else 1,
                         result.stdout + result.stderr)
        self.assertIn("[TDQ:TEST] " + status, result.stdout)
        lines = self.ledger.read_text(encoding="utf-8").splitlines()
        row = json.loads(lines[-1])
        self.assertEqual(row["selection_scope"], scope)
        self.assertEqual(row["status"], status)
        self.assertEqual(row["tests_run"], tests_run)
        self.assertTrue(row["reason"])
        if log == "0":
            self.assertEqual(result.stderr, "")
        else:
            self._assert_timestamped(result)
            for field in ("scope=" + scope, "status=" + status,
                          "tests_run=" + str(tests_run),
                          "fallback=" + row["fallback"],
                          "reason=" + row["reason"]):
                self.assertIn(field, result.stderr)
        return row

    def _malformed_source(self):
        records = [
            {"type": "session_meta", "timestamp": START,
             "payload": {"id": "fixture", "cwd": str(self.project)}},
            {"type": "response_item", "timestamp": START,
             "payload": {"type": "function_call", "call_id": "call"}},
            {"type": "response_item", "timestamp": END,
             "payload": {"type": "function_call_output", "call_id": "call",
                         "output": "fixture-tool-content"}},
        ]
        source = self._write(
            "transcripts/fixture.jsonl",
            "".join(json.dumps(row) + "\n" for row in records) + "{broken\n")
        return source.parent

    def _indirect_failure(self):
        self._write("scripts/core.py", "VALUE = 0\n")
        self._write("scripts/facade.py", "from core import VALUE\n")
        self._write("tests/test_facade.py", (
            "import os, sys, unittest\n"
            "sys.path.insert(0, os.path.join(os.path.dirname(__file__), "
            "'..', 'scripts'))\n"
            "from facade import VALUE\n"
            "class Contract(unittest.TestCase):\n"
            "    def test_value(self):\n"
            "        self.assertEqual(VALUE, 1)\n"))

    def test_timing_missing_source_logs_reason_and_clean_json(self):
        for command in ("show", "status", "close"):
            with self.subTest(command=command):
                result = self._timing(command)
                payload = self._json(result)
                self._assert_timestamped(result)
                self.assertIn("no transcript source found", result.stderr)
                self.assertIn("timing unavailable", result.stderr)
                for metric in payload["metrics"].values():
                    self.assertIsNone(metric["seconds"])
                    self.assertEqual(metric["quality"], "unavailable")
                    self.assertTrue(metric["reason"])

    def test_timing_log_off_preserves_missing_source_json(self):
        for command in ("show", "status", "close"):
            with self.subTest(command=command):
                enabled = self._json(self._timing(command))
                disabled = self._timing(command, log="0")
                self.assertEqual(self._json(disabled), enabled)
                self.assertEqual(disabled.stderr, "")

    def test_timing_malformed_source_logs_counter_not_raw_content(self):
        result = self._timing("show", source=self._malformed_source())
        payload = self._json(result)
        self._assert_timestamped(result)
        self.assertIn("malformed_lines", result.stderr)
        self.assertNotIn("fixture-tool-content", result.stderr)
        self.assertNotIn("{broken", result.stderr)
        metric = payload["metrics"]["tool_call_seconds"]
        self.assertEqual(metric["quality"], "partial")
        self.assertIn("malformed_lines", metric["reason"])
        self.assertEqual(metric["seconds"], 20)

    def test_timing_log_off_preserves_partial_source_json(self):
        source = self._malformed_source()
        enabled = self._json(self._timing("show", source=source))
        result = self._timing("show", source=source, log="0")
        self.assertEqual(self._json(result), enabled)
        self.assertEqual(result.stderr, "")

    def test_runner_transitive_fallback_logs_failure_reason(self):
        self._indirect_failure()
        for log in (None, "0"):
            with self.subTest(log=log):
                result = self._runner("scripts/core.py", log=log)
                row = self._assert_runner_log(
                    result, log, "transitive", "FAIL", 1)
                self.assertEqual(row["fallback"],
                                 "direct selection empty; transitive fallback")
                self.assertEqual(row["failed_modules"], ["test_facade.py"])

    def test_runner_full_fallback_logs_success_reason(self):
        self._write("scripts/uncovered.py", "VALUE = 0\n")
        self._write("tests/test_arithmetic.py", PASSING_TEST)
        for log in (None, "0"):
            with self.subTest(log=log):
                result = self._runner("scripts/uncovered.py", log=log)
                row = self._assert_runner_log(result, log, "full", "PASS", 1)
                self.assertEqual(row["fallback"],
                                 "source has no selected tests; full fallback")

    def test_runner_no_tests_logs_incomplete_reason(self):
        self._write("scripts/uncovered.py", "VALUE = 0\n")
        for log in (None, "0"):
            with self.subTest(log=log):
                result = self._runner("scripts/uncovered.py", log=log)
                row = self._assert_runner_log(
                    result, log, "full", "INCOMPLETE", 0)
                self.assertEqual(row["reason"], "No test modules")

    def test_ledger_json_stays_clean_with_default_and_disabled_logs(self):
        self._write("scripts/uncovered.py", "VALUE = 0\n")
        self._write("tests/test_arithmetic.py", PASSING_TEST)
        self.assertEqual(self._runner("scripts/uncovered.py").returncode, 0)
        enabled = self._run("tdq_test.py", "so", "--repo", str(self.project),
                            "--json")
        payload = self._json(enabled)
        self._assert_timestamped(enabled)
        self.assertIn("tdq_test: so request=", enabled.stderr)
        disabled = self._run("tdq_test.py", "so", "--repo", str(self.project),
                             "--json", log="0")
        self.assertEqual(self._json(disabled), payload)
        self.assertEqual(disabled.stderr, "")

    def test_ledger_malformed_data_keeps_warning_off_json_stdout(self):
        self.ledger.write_text("{broken\n", encoding="utf-8")
        enabled = self._run("tdq_test.py", "so", "--repo", str(self.project),
                            "--json")
        payload = self._json(enabled)
        self._assert_timestamped(enabled)
        self.assertIn("warning:", enabled.stderr)
        disabled = self._run("tdq_test.py", "so", "--repo", str(self.project),
                             "--json", log="0")
        self.assertEqual(self._json(disabled), payload)
        self.assertEqual(disabled.stderr, "")


if __name__ == "__main__":
    unittest.main()
