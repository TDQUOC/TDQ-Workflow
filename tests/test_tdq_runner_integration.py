"""Real runner boundaries: complete mixed collection, isolation, and receipt accounting."""
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

from helper import ROOT
import tdq_test
import tdq_test_report


class RunnerIntegration(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="tdq-runner-")
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name)
        (self.repo / "tests").mkdir()
        (self.repo / "docs/tdq").mkdir(parents=True)
        (self.repo / "docs/tdq/state.json").write_text(json.dumps({
            "active_request": "integration", "phase": "implement"}), encoding="utf-8")

    def source(self, text):
        (self.repo / "tests/test_case.py").write_text(text, encoding="utf-8")

    def run_full(self, **kwargs):
        return tdq_test.chay_tron_bo_result(self.repo, io.StringIO(), **kwargs)

    def cli(self, *args):
        return subprocess.run([sys.executable, str(Path(ROOT, "scripts/tdq_test.py")),
                               "tron-bo", "--repo", str(self.repo), *args],
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=120)

    def test_full_default_collects_mixed_param_and_unittest_cases(self):
        self.source('''import pytest, unittest
@pytest.mark.parametrize("number", [1, 2])
def test_number(number, tmp_path): assert number > 0 and tmp_path.is_dir()
class Sample(unittest.TestCase):
    def test_ok(self): self.assertTrue(True)
''')
        result = self.run_full()
        self.assertEqual(result["tests_run"], 3, result)
        self.assertEqual(result["status"], "PASS", result)
        self.assertTrue(result["coverage"]["complete"])
        self.assertEqual(result["backend"], "pytest")

    def test_full_maps_pytest_suffix_filename_pattern(self):
        self.source("def test_regular(): assert True\n")
        (self.repo / "tests/extra_test.py").write_text(
            "def test_suffix(): assert True\n", encoding="utf-8")
        result = self.run_full()
        self.assertEqual(result["status"], "PASS", result)
        self.assertEqual(result["tests_run"], 2)
        self.assertEqual(result["modules"], ["extra_test.py", "test_case.py"])

    def test_worker_one_and_two_have_same_case_ids_and_persistent_evidence(self):
        self.source("def test_ok(tmp_path):\n    assert tmp_path.is_dir()\n")
        serial = self.run_full(workers=1, fresh=True, reuse="off")
        parallel = self.run_full(workers=2, fresh=True, reuse="off")
        self.assertEqual(serial["manifest"]["case_ids"], parallel["manifest"]["case_ids"])
        for workers, result in ((1, serial), (2, parallel)):
            self.assertEqual(result["status"], "PASS", result)
            self.assertTrue(result["process"]["execution"]["cleanup_complete"])
            self.assertTrue(all(Path(path).is_file() for path in result["evidence_paths"]))
            self.assertTrue(any(path.endswith(".xml") for path in result["evidence_paths"]))
            self.assertEqual(result["run_options"]["workers"], workers)
            self.assertTrue(result["run_options"]["fresh"])
            self.assertEqual(result["run_options"]["reuse"], "off")
            launch = result["process"]["execution"]["launch_options"]
            self.assertEqual(launch["workers"], workers)
            self.assertEqual(launch["numprocesses"], 0 if workers == 1 else workers)
            self.assertEqual(launch["dist"], "no" if workers == 1 else "loadfile")
            self.assertFalse(launch["collect_only"])
            collection = result["process"]["collection"]["launch_options"]
            self.assertEqual(collection["numprocesses"], 0)
            self.assertTrue(collection["collect_only"])
            persisted = json.loads(Path(result["result_artifact"]["path"]).read_text(encoding="utf-8"))
            self.assertEqual(persisted["process"]["execution"]["launch_options"], launch)

    def test_requested_parallel_cannot_certify_actual_serial_launch(self):
        self.source("def test_ok(): assert True\n")
        original = tdq_test._pytest_command
        def serial_command(job, selectors, workers, report, *, collect=False):
            return original(job, selectors, 1, report, collect=collect)
        with mock.patch.object(tdq_test, "_pytest_command", side_effect=serial_command):
            result = self.run_full(workers=2, fresh=True, reuse="off")
        self.assertEqual(result["status"], "INCOMPLETE", result)
        self.assertEqual(result["case_outcomes"][0]["outcome"], "pass")
        self.assertEqual(result["run_options"]["workers"], 2)
        self.assertEqual(result["process"]["execution"]["launch_options"]["workers"], 1)
        self.assertFalse(result["coverage"]["complete"])
        self.assertIn("launch options mismatch", result["reason"])

    def test_collection_launch_mismatch_stops_second_execution(self):
        self.source("def test_ok(): assert True\n")
        original = tdq_test._pytest_command
        def execution_command(job, selectors, workers, report, *, collect=False):
            return original(job, selectors, workers, report, collect=False)
        with mock.patch.object(tdq_test, "_pytest_command", side_effect=execution_command):
            result = self.run_full(workers=1, fresh=True)
        self.assertEqual(result["status"], "INCOMPLETE", result)
        self.assertNotIn("execution", result["process"])
        self.assertFalse(result["process"]["collection"]["launch_options"]["collect_only"])
        self.assertIn("launch options mismatch", result["reason"])

    def test_cli_rejects_worker_conflict_and_invalid_worker_count(self):
        for flags in (("--workers", "0"), ("--workers", "-1"),
                      ("--workers", "2", "--parallel")):
            with self.subTest(flags=flags):
                self.assertEqual(self.cli(*flags).returncode, 2)

    def test_missing_pytest_cannot_certify_full_unittest_fallback(self):
        self.source("import unittest\nclass Sample(unittest.TestCase):\n    def test_ok(self): pass\n")
        with mock.patch.object(tdq_test.importlib.util, "find_spec", return_value=None):
            result = self.run_full()
        self.assertIn(result["status"], ("ERROR", "INCOMPLETE"))

    def test_timeout_preserves_incomplete_and_cleanup(self):
        self.source("import time\ndef test_sleep(): time.sleep(10)\n")
        result = self.run_full(timeout_seconds=1)
        self.assertNotEqual(result["status"], "PASS")
        self.assertFalse(result["details_complete"])
        self.assertTrue(result["process"]["execution"]["timed_out"])
        self.assertTrue(result["process"]["execution"]["cleanup_complete"])

    def test_home_is_private_and_parent_environment_is_unchanged(self):
        parent = os.environ.get("USERPROFILE", os.environ.get("HOME"))
        self.source('''import os
from pathlib import Path
def test_home():
    home = Path.home()
    assert "tdq-" in str(home)
    (home / "runner-private-proof").write_text("fixture")
''')
        result = self.run_full()
        self.assertEqual(result["status"], "PASS", result)
        self.assertEqual(os.environ.get("USERPROFILE", os.environ.get("HOME")), parent)
        self.assertFalse(Path(parent, "runner-private-proof").exists())

    def policy(self):
        source = self.repo / "tests/test_case.py"
        proof = self.repo / "dependency_proof.py"
        proof.write_text("def proof(): return True\n", encoding="utf-8")
        sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
        declaration = {"hermetic": True, "no_network": True, "no_live_clock": True,
                       "no_personal_config": True, "external_inputs": [],
                       "input_paths": ["tests/test_case.py"], "env_names": [],
                       "test_source_sha256": sha(source),
                       "proof": {"test_id": "dependency_proof.py::proof",
                                 "test_path": "dependency_proof.py", "source_sha256": sha(proof)}}
        policy = {"schema_version": 1, "cases": {"tests/test_case.py::test_ok": declaration}}
        (self.repo / "docs/tdq/reuse-policy.json").write_text(json.dumps(policy), encoding="utf-8")

    def test_real_reuse_fresh_and_ledger_execution_counts(self):
        self.source("def test_ok(): assert 1 + 1 == 2\n")
        self.policy()
        environment = dict(os.environ)
        first = self.run_full(reuse="auto", job_kind="correctness", environment=environment)
        second = self.run_full(reuse="auto", job_kind="correctness", environment=environment)
        fresh = self.run_full(reuse="auto", fresh=True, job_kind="correctness", environment=environment)
        self.assertEqual([first["action"], second["action"], fresh["action"]],
                         ["executed", "reused", "executed"])
        self.assertEqual(second["timings"]["execute_seconds"], 0)
        self.assertTrue(second["source_receipt_id"])
        self.assertEqual(tdq_test.dem_repo(self.repo, "integration")["tron_bo"], 2)

    def test_silent_cli_reuses_after_reopening_generated_log(self):
        self.source("def test_ok(): assert True\n")
        self.policy()
        for _ in range(2):
            run = self.cli("--silent", "--reuse", "auto")
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        rows = tdq_test._doc_so(self.repo)
        self.assertEqual([row["action"] for row in rows], ["executed", "reused"])
        self.assertEqual(tdq_test.dem_repo(self.repo, "integration")["tron_bo"], 1)

    def test_partial_environment_override_fingerprints_inherited_values(self):
        self.source("import os\ndef test_ok(): assert os.environ.get('TDQ_FIXTURE_FEATURE') == 'on'\n")
        self.policy()
        path = self.repo / "docs/tdq/reuse-policy.json"
        policy = json.loads(path.read_text(encoding="utf-8"))
        policy["cases"]["tests/test_case.py::test_ok"]["env_names"] = ["TDQ_FIXTURE_FEATURE"]
        path.write_text(json.dumps(policy), encoding="utf-8")
        with mock.patch.dict(os.environ, {"TDQ_FIXTURE_FEATURE": "on"}):
            first = self.run_full(reuse="auto", environment={"TDQ_LOG": "0"})
        with mock.patch.dict(os.environ, {"TDQ_FIXTURE_FEATURE": "off"}):
            second = self.run_full(reuse="auto", environment={"TDQ_LOG": "0"})
        self.assertEqual(first["status"], "PASS", first)
        self.assertEqual(second["action"], "executed", second)
        self.assertEqual(second["status"], "FAIL", second)
        self.assertNotEqual(first["source_before"]["inputs"]["environment_sha256"],
                            second["source_before"]["inputs"]["environment_sha256"])

    def test_post_execution_proof_errors_retain_observed_failures(self):
        self.source("def test_ok(): assert False, 'known assertion'\n")
        secret = "private-credential-must-not-be-logged"
        original_fingerprint = tdq_test._source_fingerprint
        original_exit = tdq_test.IsolatedJob.__exit__
        def fingerprint_after_error(*args):
            if fingerprint.call_count == 2:
                raise OSError(secret)
            return original_fingerprint(*args)
        def cleanup_error(job, *args):
            original_exit(job, *args)
            raise OSError(secret)
        patches = [mock.patch.object(tdq_test, "_source_fingerprint", side_effect=fingerprint_after_error),
                   mock.patch.object(tdq_test, "_persist_result", side_effect=OSError(secret)),
                   mock.patch.object(tdq_test.IsolatedJob, "__exit__", new=cleanup_error)]
        for boundary, patch in zip(("source_after", "persist", "cleanup"), patches):
            with self.subTest(boundary=boundary), patch as fingerprint:
                result = self.run_full()
            self.assertEqual(result["status"], "FAIL", result)
            self.assertEqual(result["failed_modules"], ["test_case.py"])
            self.assertTrue(result["case_outcomes"])
            self.assertIn("execution", result["process"])
            self.assertTrue(result["evidence_paths"])
            self.assertFalse(result["details_complete"])
            self.assertFalse(result["finalization"]["complete"])
            self.assertNotIn(secret, json.dumps(result))
            self.assertEqual(result["finalization"]["error_type"], "OSError")
            self.assertNotIn("result_artifact", result)

    def test_persist_error_cannot_leave_pass_certificate(self):
        self.source("def test_ok(): assert True\n")
        with mock.patch.object(tdq_test, "_persist_result", side_effect=ValueError("cannot serialize")):
            result = self.run_full()
        self.assertEqual(result["status"], "INCOMPLETE", result)
        self.assertFalse(result["coverage"]["complete"])
        self.assertEqual(result["case_outcomes"][0]["outcome"], "pass")
        self.assertNotIn("result_artifact", result)

    def test_fresh_fence_failure_preserves_collection_without_claiming_execution(self):
        self.source("def test_ok(): assert True\n")
        with mock.patch.object(tdq_test.tdq_test_receipt, "run_with_receipt",
                               side_effect=PermissionError("private-fence-credential")):
            result = self.run_full(fresh=True, reuse="off", job_kind="correctness")
        self.assertEqual(result["status"], "ERROR", result)
        self.assertTrue(result["execution_not_started"])
        self.assertEqual(result["timings"]["execute_seconds"], 0)
        self.assertEqual(result["tests_run"], 0)
        self.assertEqual(result["case_outcomes"], [])
        self.assertEqual(result["manifest"]["case_ids"], ["tests/test_case.py::test_ok"])
        self.assertIn("collection", result["process"])
        self.assertNotIn("execution", result["process"])
        self.assertTrue(any(Path(path).name == "collection.json" for path in result["evidence_paths"]))
        self.assertFalse(any(Path(path).name == "execution.json" for path in result["evidence_paths"]))
        self.assertFalse(result["coverage"]["complete"])
        self.assertIn("PermissionError", result["reason"])
        self.assertNotIn("private-fence-credential", json.dumps(result))
        self.assertEqual(tdq_test.dem_repo(self.repo, "integration")["tron_bo"], 1)

    def test_external_runner_implementation_change_invalidates_receipt(self):
        self.source("def test_ok(): assert True\n")
        self.policy()
        temporary = tempfile.TemporaryDirectory(prefix="tdq-plugin-fixture-")
        self.addCleanup(temporary.cleanup)
        plugin = Path(temporary.name, "tdq_test.py")
        plugin.write_text("VERSION = 1\n", encoding="utf-8")
        with mock.patch.object(tdq_test, "__file__", str(plugin)):
            first = self.run_full(reuse="auto")
            plugin.write_text("VERSION = 2\n", encoding="utf-8")
            second = self.run_full(reuse="auto")
            third = self.run_full(reuse="auto")
        self.assertEqual([result["action"] for result in (first, second, third)],
                         ["executed", "executed", "reused"])
        self.assertNotEqual(first["source_before"]["implementation"],
                            second["source_before"]["implementation"])
        self.assertIn("tdq_test_process", second["source_before"]["implementation"])

    def test_public_source_fingerprint_matches_runner_envelope(self):
        self.source("def test_ok(): assert True\n")
        expected = tdq_test.source_fingerprint(self.repo, "integration", environment={"TDQ_LOG": "0"})
        result = self.run_full(environment={"TDQ_LOG": "0"})
        self.assertEqual(result["status"], "PASS", result)
        self.assertEqual(result["source_before"], expected)
        self.assertEqual(result["source_after"], expected)

    def test_receipt_error_after_callback_keeps_known_failure(self):
        self.source("def test_ok(): assert False, 'known assertion'\n")
        def fail_after_callback(project, request, manifest, execute, **kwargs):
            execute()
            raise OSError("receipt publication denied")
        with mock.patch.object(tdq_test.tdq_test_receipt, "run_with_receipt", side_effect=fail_after_callback):
            result = self.run_full(reuse="auto")
        self.assertEqual(result["status"], "FAIL", result)
        self.assertEqual(result["failed_modules"], ["test_case.py"])
        self.assertFalse(result["execution_not_started"])
        self.assertTrue(result["case_outcomes"])
        self.assertIn("execution", result["process"])
        self.assertGreater(result["timings"]["execute_seconds"], 0)
        self.assertFalse(result["details_complete"])

    def test_benchmark_is_explicitly_recorded_and_counted(self):
        self.source("def test_ok(): assert True\n")
        result = self.run_full(job_kind="benchmark", fresh=True, reuse="off")
        self.assertEqual(result["status"], "PASS", result)
        rows = tdq_test._doc_so(self.repo)
        self.assertEqual(rows[-1]["job_classification"], "benchmark")
        self.assertEqual(rows[-1]["kind"], "tron-bo")
        self.assertEqual(tdq_test.dem(rows, "integration")["tron_bo"], 1)

    def test_source_drift_cannot_certify_pass(self):
        self.source('''from pathlib import Path
def test_mutate():
    Path("new_input.py").write_text("changed = True\\n", encoding="utf-8")
''')
        result = self.run_full()
        self.assertEqual(result["status"], "INCOMPLETE", result)
        self.assertFalse(result["details_complete"])
        self.assertNotEqual(result["source_before"], result["source_after"])

    def test_cli_persists_bound_result_and_same_ledger_verdict(self):
        self.source("def test_ok(): assert True\n")
        run = self.cli("--silent", "--workers", "1", "--fresh", "--reuse", "off",
                       "--timeout-seconds", "120")
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        marker = next(line for line in run.stdout.splitlines() if line.startswith("TDQ_RESULT "))
        artifact = json.loads(marker.removeprefix("TDQ_RESULT "))
        raw = Path(artifact["path"]).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), artifact["sha256"])
        result = json.loads(raw)
        row = tdq_test._doc_so(self.repo)[-1]
        self.assertEqual(result["status"], row["status"])
        self.assertEqual(row["result_artifact"], artifact)
        self.assertNotIn("case_outcomes", row)
        self.assertNotIn("source_before", row)
        self.assertNotIn("stdout", row["process"]["execution"])
        self.assertTrue(row["coverage_summary"]["complete"])
        self.assertEqual(result["manifest"]["scope"], "full")
        for evidence in result["evidence"].values():
            self.assertEqual(hashlib.sha256(Path(evidence["path"]).read_bytes()).hexdigest(),
                             evidence["sha256"])

    def test_collection_error_stops_before_any_test_execution(self):
        self.source("def test_invalid(:\n    pass\n")
        result = self.run_full()
        self.assertEqual(result["status"], "ERROR", result)
        self.assertIn("collection", result["process"])
        self.assertNotIn("execution", result["process"])
        self.assertFalse(result["details_complete"])

    def test_concurrent_runner_joins_owner_without_second_execution_count(self):
        self.source("import time\ndef test_ok():\n    time.sleep(0.8)\n    assert 1 + 1 == 2\n")
        self.policy()
        environment = dict(os.environ)
        with ThreadPoolExecutor(max_workers=2) as pool:
            calls = [pool.submit(self.run_full, reuse="auto", environment=environment,
                                 job_kind="correctness") for _ in range(2)]
            results = [call.result(timeout=120) for call in calls]
        self.assertEqual(sorted(result["action"] for result in results), ["executed", "joined"])
        for result in results:
            self.assertEqual(result["status"], "PASS", result)
        joined = next(result for result in results if result["action"] == "joined")
        self.assertEqual(joined["timings"]["execute_seconds"], 0)
        self.assertGreater(joined["timings"]["wait_seconds"], 0)
        self.assertEqual(tdq_test.dem_repo(self.repo, "integration")["tron_bo"], 1)

    def test_ledger_size_does_not_duplicate_full_case_payload(self):
        result = {"status": "PASS", "tests_run": 1,
                  "manifest": {"case_ids": ["case"]}, "case_outcomes": [{"details": "large"}],
                  "source_before": {"key": "before", "inputs": {"files": ["file"]}},
                  "source_after": {"key": "after"}, "result_artifact": {"path": "result.json", "sha256": "digest"}}
        small = len(json.dumps(tdq_test._ledger_result(result)))
        result["manifest"]["case_ids"] *= 10000
        result["case_outcomes"] *= 10000
        result["source_before"]["inputs"]["files"] *= 10000
        large = tdq_test._ledger_result(result)
        self.assertLess(len(json.dumps(large)), small + 32)
        self.assertEqual(large["case_inventory_count"], 10000)
        self.assertEqual(large["result_artifact"], result["result_artifact"])

    def report_cli(self, source, prefix, *flags, env=None):
        return subprocess.run([sys.executable, str(Path(ROOT, "scripts/tdq_test.py")),
                               "report", "--result", str(source), "--out-prefix", str(prefix), *flags],
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=30, env=env)

    def test_fresh_result_persists_one_slow_test_summary(self):
        self.source("def test_ok(): assert 1 + 1 == 2\n")
        summarize = tdq_test_report.summarize_result
        with mock.patch.object(tdq_test_report, "summarize_result", wraps=summarize) as calls:
            result = self.run_full(fresh=True, reuse="off")
            self.assertEqual(result["status"], "PASS", result)
            self.assertIn("slow_tests", result)
            output = io.StringIO()
            with redirect_stdout(output):
                tdq_test._print_result(result, 1.0, "full")
            self.assertEqual(calls.call_count, 1)
        summary = result["slow_tests"]
        persisted = json.loads(Path(result["result_artifact"]["path"]).read_text())
        self.assertEqual(persisted["slow_tests"], summary)
        self.assertEqual(summary["quality"]["status"], "complete")
        self.assertEqual(summary["result_status"], result["status"])
        self.assertEqual(summary["wall_seconds"], result["timings"]["wall_seconds"])
        self.assertEqual(len(summary["top_cases"]), 1)
        self.assertEqual(len(summary["top_modules"]), 1)
        self.assertNotIn("input_sha256", summary)
        self.assertIn("Top20 cases", output.getvalue())
        self.assertIn("Top20 modules", output.getvalue())
        self.assertIn(summary["top_cases"][0]["case_id"], output.getvalue())
        self.assertTrue(output.getvalue().splitlines()[-1].startswith("TDQ_RESULT "))
        expected = hashlib.sha256(Path(tdq_test_report.__file__).read_bytes()).hexdigest()
        self.assertEqual(result["source_before"]["implementation"]["tdq_test_report"]["sha256"], expected)

    def test_offline_cli_accepts_legacy_result_and_dotted_prefix(self):
        source = self.repo / "legacy.json"
        original = json.dumps({"status": "PASS", "exit_code": 0, "schema_version": 2,
                               "tests_run": 7}).encode()
        source.write_bytes(original)
        prefix = self.repo / "summary.v1"
        run = self.report_cli(source, prefix, env={**os.environ, "TDQ_LOG": "0"})
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(source.read_bytes(), original)
        self.assertEqual(run.stderr, "")
        self.assertIn("TDQ_REPORT ", run.stdout)
        for suffix in (".json", ".md", ".html"):
            self.assertTrue((prefix.parent / (prefix.name + suffix)).is_file())
        summary = json.loads((self.repo / "summary.v1.json").read_text())
        self.assertEqual(summary["input_sha256"], hashlib.sha256(original).hexdigest())
        self.assertEqual(summary["result_status"], "PASS")
        self.assertEqual(summary["quality"]["status"], "unavailable")

    def test_offline_dispatch_never_resolves_project_or_launches_runner(self):
        source = self.repo / "offline.json"
        source.write_text(json.dumps({"status": "PASS", "schema_version": 2,
                                      "raw_payload": "PRIVATE_INPUT_PAYLOAD"}), encoding="utf-8")
        original, stamp = source.read_bytes(), source.stat().st_mtime_ns
        state = (self.repo / "docs/tdq/state.json").read_bytes()
        output, errors = io.StringIO(), io.StringIO()
        deny = AssertionError("Offline export must not execute or resolve a project")
        with mock.patch.dict(os.environ), \
                mock.patch.object(tdq_test, "_run_pytest", side_effect=deny), \
                mock.patch.object(tdq_test, "chay_tron_bo_result", side_effect=deny), \
                mock.patch.object(tdq_test.tdq_state, "resolve_project_dir", side_effect=deny), \
                mock.patch.object(tdq_test.subprocess, "Popen", side_effect=deny), \
                redirect_stdout(output), redirect_stderr(errors):
            os.environ.pop("TDQ_LOG", None)
            code = tdq_test.main(["report", "--result", str(source),
                                  "--out-prefix", str(self.repo / "offline-export")])
        self.assertEqual(code, 0, errors.getvalue())
        self.assertEqual(source.read_bytes(), original)
        self.assertEqual(source.stat().st_mtime_ns, stamp)
        self.assertEqual((self.repo / "docs/tdq/state.json").read_bytes(), state)
        self.assertFalse((self.repo / "docs/tdq/.tdq-test.jsonl").exists())
        self.assertNotIn("PRIVATE_INPUT_PAYLOAD", output.getvalue() + errors.getvalue())
        self.assertRegex(errors.getvalue(), r"\[\d{4}-\d\d-\d\dT.*stage=exported")

    def test_saved_failure_real_cli_roundtrip_does_not_execute_again(self):
        counter_dir = tempfile.TemporaryDirectory(prefix="tdq-offline-counter-")
        self.addCleanup(counter_dir.cleanup)
        counter = Path(counter_dir.name) / "executions.txt"
        self.source("from pathlib import Path\ndef test_failure():\n"
                    f"    with Path({str(counter)!r}).open('a') as output: output.write('run\\n')\n"
                    "    assert False, 'fixture failure'\n")
        result = self.run_full(fresh=True, reuse="off")
        self.assertEqual(result["status"], "FAIL", result)
        self.assertEqual(counter.read_text(), "run\n")
        source = Path(result["result_artifact"]["path"])
        original, stamp = source.read_bytes(), source.stat().st_mtime_ns
        ledger = tdq_test._doc_so(self.repo)
        prefix = self.repo / "failure.report"
        run = self.report_cli(source, prefix, env={**os.environ, "TDQ_LOG": "0"})
        self.assertEqual(run.returncode, 1, run.stdout + run.stderr)
        self.assertEqual(run.stderr, "")
        self.assertEqual(counter.read_text(), "run\n")
        self.assertEqual(source.read_bytes(), original)
        self.assertEqual(source.stat().st_mtime_ns, stamp)
        self.assertEqual(tdq_test._doc_so(self.repo), ledger)
        metadata = json.loads(next(line.removeprefix("TDQ_REPORT ")
            for line in run.stdout.splitlines() if line.startswith("TDQ_REPORT ")))
        self.assertEqual(metadata["result_status"], "FAIL")
        self.assertEqual(metadata["input_sha256"], hashlib.sha256(original).hexdigest())
        exported = json.loads((self.repo / "failure.report.json").read_text())
        for key, value in result["slow_tests"].items():
            self.assertEqual(exported[key], value, key)
        self.assertEqual(exported["result_exit_code"], 1)
        for role in ("markdown", "html"):
            artifact = exported["artifacts"][role]
            content = (prefix.parent / artifact["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(content).hexdigest(), artifact["sha256"])
            self.assertIn("FAIL", content.decode())

    def test_silent_cli_keeps_bound_marker_without_top_tables(self):
        self.source("def test_ok(): assert True\n")
        with mock.patch.dict(os.environ, {"TDQ_LOG": "0"}):
            run = self.cli("--silent", "--fresh", "--reuse", "off")
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(run.stderr, "")
        self.assertNotIn("Top20", run.stdout)
        self.assertLessEqual(len(run.stdout.strip().splitlines()), 2)
        marker = next(line.removeprefix("TDQ_RESULT ") for line in run.stdout.splitlines()
                      if line.startswith("TDQ_RESULT "))
        binding = json.loads(marker)
        raw = Path(binding["path"]).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), binding["sha256"])
        self.assertIn("slow_tests", json.loads(raw))

    def test_summary_and_persistence_errors_keep_original_failure(self):
        self.source("def test_bad(): assert False, 'original execution failure'\n")
        for boundary in ("summary", "persist"):
            with self.subTest(boundary=boundary):
                target = tdq_test_report if boundary == "summary" else tdq_test
                name = "summarize_result" if boundary == "summary" else "_persist_result"
                failure = RuntimeError("private summary error") if boundary == "summary" else OSError("write denied")
                with mock.patch.object(target, name, side_effect=failure) as calls:
                    result = self.run_full(fresh=True, reuse="off")
                self.assertEqual(calls.call_count, 1)
                self.assertEqual(result["status"], "FAIL", result)
                self.assertEqual(result["exit_code"], 1)
                self.assertIn("original execution failure", json.dumps(result["failures"]))
                self.assertFalse(result["finalization"]["complete"])
                self.assertNotIn("result_artifact", result)
                self.assertNotIn("slow_tests", result)
                output = io.StringIO()
                with redirect_stdout(output):
                    tdq_test._print_result(result, 0, "full")
                self.assertIn("[TDQ:TEST] FAIL", output.getvalue())
                self.assertNotIn("Top20", output.getvalue())

    def test_report_errors_do_not_publish_success_or_overwrite_input(self):
        source = self.repo / "source.json"
        source.write_text('{"status":"FAIL","exit_code":1}', encoding="utf-8")
        original = source.read_bytes()
        output, errors = io.StringIO(), io.StringIO()
        with redirect_stdout(output), redirect_stderr(errors):
            code = tdq_test.main(["report", "--result", str(source),
                                  "--out-prefix", str(source.with_suffix(""))])
        self.assertEqual(code, 1)
        self.assertEqual(source.read_bytes(), original)
        self.assertNotIn("TDQ_REPORT", output.getvalue())
        self.assertIn("ReportError", errors.getvalue())
        self.assertIn("Output must not overwrite the input result", errors.getvalue())
        output, errors = io.StringIO(), io.StringIO()
        with mock.patch.object(tdq_test_report, "export_report", side_effect=RuntimeError("PRIVATE_EXPORT_PAYLOAD")), \
                redirect_stdout(output), redirect_stderr(errors):
            code = tdq_test.main(["report", "--result", str(source),
                                  "--out-prefix", str(self.repo / "safe")])
        self.assertEqual(code, 1)
        self.assertNotIn("TDQ_REPORT", output.getvalue())
        self.assertIn("RuntimeError", errors.getvalue())
        self.assertNotIn("PRIVATE_EXPORT_PAYLOAD", errors.getvalue())
        self.assertFalse((self.repo / "safe.json").exists())
        self.assertEqual(source.read_bytes(), original)

    def test_report_requires_explicit_output_prefix(self):
        source = self.repo / "source.json"
        source.write_text('{"status":"PASS"}', encoding="utf-8")
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as stopped:
            tdq_test.main(["report", "--result", str(source)])
        self.assertEqual(stopped.exception.code, 2)
        self.assertFalse((self.repo / "slow-tests.json").exists())

    def test_ledger_does_not_duplicate_summary_quality_payload(self):
        result = {"manifest": {"case_ids": ["case"]},
                  "slow_tests": {"quality": {"issues": []}}}
        small = tdq_test._ledger_result(result)
        result["slow_tests"]["quality"]["issues"] = [{"case_id": "case", "reason": "missing"}] * 10000
        self.assertEqual(tdq_test._ledger_result(result), small)
        self.assertNotIn("slow_tests", small)
