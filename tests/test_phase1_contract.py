"""Cross-component contracts through real CLIs and persisted fixture data."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import helper

REQUEST = "2026-10-27-0000-contract"
NEXT_REQUEST = "2026-10-27-0001-contract-next"
START = "2026-10-27T00:00:00+00:00"
END = "2026-10-27T00:00:20+00:00"


class ContractProject(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="tdq-contract-")
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.project = self.base / "project"
        self.home = self.base / "home"
        self.project.mkdir()
        self.home.mkdir()
        # Run the same semantic regressions against an archived baseline.
        scripts = os.environ.get("TDQ_PHASE1_BASELINE_SCRIPTS")
        self.scripts = Path(scripts or Path(helper.ROOT) / "scripts")
        self.env = {**os.environ, "TDQ_PROJECT_DIR": str(self.project),
                    "HOME": str(self.home), "USERPROFILE": str(self.home),
                    "TDQ_KHONG_CHAM_MAY": "1", "TDQ_KHOI_TAO_NEN": "0",
                    "TDQ_LOG": "0"}
        self.history = self.project / "docs" / "tdq" / "timing.jsonl"
        self.ledger = self.project / "docs" / "tdq" / ".tdq-test.jsonl"

    def run_cli(self, script, *arguments):
        return subprocess.run(
            [sys.executable, str(self.scripts / script), *arguments],
            cwd=self.project, env=self.env, capture_output=True,
            text=True, encoding="utf-8", timeout=30)

    def state_cli(self, *arguments):
        result = self.run_cli("tdq_state.py", *arguments)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def initialize(self):
        self.state_cli("init", REQUEST, "full")
        self.state_cli("set", "phase=analyze", "started_at=" + START,
                       "phase_history=" + json.dumps([
                           {"phase": "analyze", "at": START}]))

    def write(self, path, text):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def jsonl(self, path, records):
        return self.write(path, "".join(json.dumps(row) + "\n"
                                       for row in records))

    def rows(self, path):
        return [json.loads(line) for line in path.read_text(
            encoding="utf-8").splitlines() if line.strip()]

    def timing(self, command="show", *arguments):
        result = self.run_cli("tdq_timing.py", command, "--json",
                              "--now", END, *arguments)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def codex_log(self, *, broken=False):
        path = (self.home / ".codex" / "sessions" / "old-folder"
                / "rollout.jsonl")
        records = [
            {"type": "session_meta", "timestamp": START,
             "payload": {"id": "contract-session", "cwd": str(self.project)}},
            {"type": "response_item", "timestamp": "2026-10-27T00:00:02Z",
             "payload": {"type": "function_call", "call_id": "call-1"}},
            {"type": "response_item", "timestamp": "2026-10-27T00:00:07Z",
             "payload": {"type": "function_call_output", "call_id": "call-1"}},
        ]
        self.jsonl(path, records)
        if broken:
            with path.open("a", encoding="utf-8") as stream:
                stream.write("{broken fixture\n")
        return path

    def runner_fixture(self, *, direct=False):
        # This temporary snapshot represents an already approved request.
        self.write(self.project / "docs" / "tdq" / "state.json", json.dumps({
            "active_request": REQUEST, "phase": "implement", "lane": "full"}))
        self.write(self.project / "scripts" / "core.py", "VALUE = 0\n")
        self.write(self.project / "scripts" / "facade.py",
                   "from core import VALUE\n")
        test = ("import os, sys, unittest\n"
                "sys.path.insert(0, os.path.join(os.path.dirname(__file__), "
                "'..', 'scripts'))\n"
                "from facade import VALUE\n"
                "class Contract(unittest.TestCase):\n"
                "    def test_value(self):\n"
                "        self.assertEqual(VALUE, 1)\n")
        self.write(self.project / "tests" / "test_facade.py", test)
        if direct:
            source = ("import unittest\n# core\n"
                      "class Direct(unittest.TestCase):\n"
                      "    def test_ok(self):\n        self.assertEqual(1, 1)\n")
            self.write(self.project / "tests" / "test_direct.py", source)

    def runner(self, command, *arguments):
        return self.run_cli("tdq_test.py", command, "--repo",
                            str(self.project), *arguments)


class Compatibility(ContractProject):
    def test_regression_gap_is_not_model_compute_time(self):
        """Given assistant gaps, when shown, then model time is unavailable."""
        self.initialize()
        directory = self.base / "claude-fixture"
        common = {"type": "assistant", "cwd": str(self.project),
                  "sessionId": "gap-session", "message": {
                      "usage": {"input_tokens": 1}, "content": []}}
        self.jsonl(directory / "gap.jsonl", [
            {**common, "timestamp": START, "requestId": "gap-1"},
            {**common, "timestamp": "2026-10-27T00:02:00Z",
             "requestId": "gap-2"},
        ])
        result = self.run_cli(
            "tdq_timing.py", "show", "--json", "--transcript-dir",
            str(directory), "--now", "2026-10-27T00:03:00Z")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertIsNone(data["model_giay"])
        self.assertEqual(data["schema_version"], 2)
        self.assertEqual(data["treo_tuong_giay"], 180)
        self.assertEqual(data["metrics"]["api_request_seconds"]["quality"],
                         "unavailable")

    def test_v1_history_survives_v2_close_finish_and_new_init(self):
        """Given old history, when closed and reinitialized, then append once."""
        self.initialize()
        legacy = {"slug": "2026-08-01-legacy", "lane": "full",
                  "started_at": "2026-08-01T00:00:00+00:00",
                  "closed_at": "2026-08-01T00:02:00+00:00",
                  "treo_tuong_giay": 120, "model_giay": 60, "phases": []}
        original = (json.dumps(legacy, separators=(",", ":"))
                    + "\r\n").encode("utf-8")
        self.history.write_bytes(original)
        self.codex_log()
        shown = self.timing()
        closed = self.timing("close")
        self.assertEqual(shown, closed)
        self.assertIsNone(closed["model_giay"])
        self.assertEqual(closed["metrics"]["tool_call_seconds"]["seconds"], 5)
        self.assertEqual(closed["metrics"]["tool_call_seconds"]["quality"],
                         "complete")
        self.assertTrue(self.history.read_bytes().startswith(original))
        before_repeat = self.history.read_bytes()
        self.timing("close")
        finished = self.run_cli("tdq_finish.py", "--phase", "idle",
                                "--log", "isolated contract fixture")
        self.assertEqual(finished.returncode, 0, finished.stderr)
        self.state_cli("init", NEXT_REQUEST, "full")
        self.assertEqual(self.history.read_bytes(), before_repeat)
        rows = self.rows(self.history)
        self.assertEqual(rows[0], legacy)
        self.assertEqual(rows[1], closed)
        self.assertEqual(len(rows), 2)

    def test_legacy_formatter_keeps_legacy_estimate_label(self):
        """Given v1 data, when formatted, then its estimate keeps a legacy label."""
        legacy = {"slug": "2026-08-01-legacy", "treo_tuong_giay": 120,
                  "model_giay": 60, "phases": [], "lane": "full",
                  "started_at": "2026-08-01T00:00:00+00:00"}
        code = ("import json,sys; sys.path.insert(0,sys.argv[1]); "
                "import tdq_timing; "
                "print(json.dumps(tdq_timing.bang_markdown("
                "json.loads(sys.argv[2]))))")
        result = subprocess.run(
            [sys.executable, "-c", code, str(self.scripts), json.dumps(legacy)],
            cwd=self.project, env=self.env, capture_output=True,
            text=True, encoding="utf-8", timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        markdown = json.loads(result.stdout)
        self.assertIn("legacy assistant-gap estimate", markdown)
        self.assertIn("1 min", markdown)

    def test_mixed_ledger_keeps_scopes_and_full_failure(self):
        """Given old rows and direct PASS, when run full, then keep its failure."""
        self.runner_fixture(direct=True)
        legacy = {"kind": "tron-bo", "request": REQUEST, "ok": True,
                  "seconds": 1.0, "failed_modules": []}
        original = (json.dumps(legacy) + "\r\n").encode("utf-8")
        self.ledger.write_bytes(original)
        direct = self.runner("vung-cham", "--files", "scripts/core.py")
        self.assertEqual(direct.returncode, 0, direct.stderr)
        direct_row = self.rows(self.ledger)[-1]
        self.assertEqual(direct_row["status"], "PASS")
        self.assertEqual(direct_row["selection_scope"], "direct")
        self.assertEqual(direct_row["modules"], ["test_direct.py"])
        full = self.runner("tron-bo", "--silent")
        self.assertEqual(full.returncode, 1, full.stdout + full.stderr)
        self.assertIn("[TDQ:TEST] FAIL", full.stdout)
        full_row = next(row for row in reversed(self.rows(self.ledger))
                        if row["kind"] == "tron-bo")
        self.assertEqual(full_row["status"], "FAIL")
        self.assertEqual(full_row["selection_scope"], "full")
        self.assertEqual(full_row["failed_modules"], ["test_facade.py"])
        counts = self.runner("so", "--json")
        self.assertEqual(counts.returncode, 0, counts.stderr)
        summary = json.loads(counts.stdout)
        self.assertEqual(summary["tron_bo"], 2)
        self.assertEqual(summary["bo_sot"], 1)
        self.assertEqual(summary["modules_bo_sot"], ["test_facade.py"])
        self.assertEqual(summary["ngan_sach"], 3)
        self.assertTrue(summary["radius_complete"])
        self.assertTrue(self.ledger.read_bytes().startswith(original))


class RunnerRecovery(ContractProject):
    def test_regression_direct_empty_failure_then_repair_keeps_history(self):
        """Given indirect failure, when repaired, then both verdicts persist."""
        self.runner_fixture()
        failed = self.runner("vung-cham", "--files", "scripts/core.py",
                              "--silent")
        self.assertEqual(failed.returncode, 1, failed.stdout + failed.stderr)
        self.assertIn("[TDQ:TEST] FAIL", failed.stdout)
        first = self.rows(self.ledger)[0]
        self.assertEqual(first["selection_scope"], "transitive")
        self.assertEqual(first["failed_modules"], ["test_facade.py"])
        self.assertIs(first["ok"], False)
        original = self.ledger.read_bytes()
        self.write(self.project / "scripts" / "core.py",
                   "VALUE = 1  # repaired fixture\n")
        fixed = self.runner("vung-cham", "--files", "scripts/core.py",
                             "--silent")
        self.assertEqual(fixed.returncode, 0, fixed.stdout + fixed.stderr)
        self.assertIn("[TDQ:TEST] PASS", fixed.stdout)
        rows = self.rows(self.ledger)
        self.assertEqual([row["status"] for row in rows], ["FAIL", "PASS"])
        self.assertEqual(rows[1]["tests_run"], 1)
        self.assertTrue(self.ledger.read_bytes().startswith(original))


class TimingRecovery(ContractProject):
    def test_repaired_transcript_restores_quality_before_persistence(self):
        """Given a broken log, when repaired, then persisted quality recovers."""
        self.initialize()
        self.codex_log(broken=True)
        partial = self.timing()
        self.assertEqual(partial["metrics"]["tool_call_seconds"]["seconds"], 5)
        self.assertEqual(partial["metrics"]["tool_call_seconds"]["quality"],
                         "partial")
        self.assertFalse(self.history.exists())
        source = self.codex_log()
        complete = self.timing("close")
        self.assertEqual(complete["metrics"]["tool_call_seconds"]["seconds"], 5)
        self.assertEqual(complete["metrics"]["tool_call_seconds"]["quality"],
                         "complete")
        self.assertIsNone(complete["metrics"]["api_request_seconds"]["seconds"])
        saved = self.history.read_bytes()
        source.unlink()
        unavailable = self.timing()
        self.assertEqual(unavailable["metrics"]["tool_call_seconds"]["quality"],
                         "unavailable")
        self.assertIsNone(unavailable["model_giay"])
        self.assertEqual(self.history.read_bytes(), saved)
        self.assertEqual(self.rows(self.history), [complete])


if __name__ == "__main__":
    unittest.main()
