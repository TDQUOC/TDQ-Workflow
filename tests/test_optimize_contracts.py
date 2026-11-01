"""Cross-layer identity and execution of the actually generated portable report."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from helper import ROOT
import build_portable
import tdq_test_manifest as manifests
import tdq_test_report as reports


RUNNER_SCRIPT = Path(ROOT, "scripts/tdq_test.py")
MIXED_SOURCE = '''import pytest, unittest
def test_pass(): assert 2 + 3 == 5
def test_fail(): assert False, "mixed fixture failure"
def test_skip(): pytest.skip("mixed fixture skip")
class Legacy(unittest.TestCase):
    def test_children(self):
        with self.subTest(scenario="good"): self.assertTrue(True)
        with self.subTest(scenario="bad"): self.fail("mixed subtest failure")
'''


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def mixed_artifact(tmp_path_factory):
    # Share immutable bytes only; every consumer gets private parsed/output data.
    project = tmp_path_factory.mktemp("mixed-report-contract")
    (project / "tests").mkdir()
    (project / "tests/test_case.py").write_text(MIXED_SOURCE, encoding="utf-8")
    run = subprocess.run([sys.executable, str(RUNNER_SCRIPT), "tron-bo", "--repo", str(project),
                          "--workers", "1", "--fresh", "--reuse", "off", "--silent"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace",
                         timeout=45, env={**os.environ, "TDQ_LOG": "0"})
    assert run.returncode == 1, run.stdout + run.stderr
    marker = json.loads(next(line.removeprefix("TDQ_RESULT ") for line in run.stdout.splitlines()
                             if line.startswith("TDQ_RESULT ")))
    raw = Path(marker["path"]).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == marker["sha256"]
    return raw, project


def test_mixed_identity_and_legacy_verdict_survive_summary_and_export(mixed_artifact, tmp_path):
    raw, project = mixed_artifact
    result = json.loads(raw)
    expected = {"tests/test_case.py::test_pass", "tests/test_case.py::test_fail",
                "tests/test_case.py::test_skip", "tests/test_case.py::Legacy::test_children"}
    assert set(result["manifest"]["case_ids"]) == expected
    assert {row["case_id"] for row in result["case_outcomes"]} == expected
    assert result["status"] == "FAIL" and result["backend"] == "pytest"
    assert result["tests_run"] == 4 and result["skipped"] == 1
    assert result["failed_modules"] == ["test_case.py"]
    assert result["coverage"]["complete"] and result["details_complete"]
    parent = next(row for row in result["case_outcomes"] if "Legacy::" in row["case_id"])
    assert [row["outcome"] for row in parent["subtests"]] == ["pass", "fail"]
    evidence = next(row for row in result["evidence"].values()
                    if Path(row["path"]).name == "execution.json")
    assert digest(evidence["path"]) == evidence["sha256"]
    sidecar = manifests.load_run_evidence(evidence["path"])
    assert sidecar["manifest"]["case_ids"] == result["manifest"]["case_ids"]
    assert {row["case_id"] for row in sidecar["outcomes"]} == expected
    assert "slow_tests" in result, "Fresh mixed execution must retain its derived summary"
    assert result["slow_tests"]["result_status"] == "FAIL"
    assert result["slow_tests"]["case_count"] == 4
    assert {row["case_id"] for row in result["slow_tests"]["top_cases"]} == expected
    rows = [json.loads(line) for line in (project / "docs/tdq/.tdq-test.jsonl").read_text().splitlines()]
    assert rows[-1]["status"] == "FAIL" and rows[-1]["ok"] is False
    assert rows[-1]["tests_run"] == 4 and "slow_tests" not in rows[-1]
    source = tmp_path / "mixed-result.json"
    source.write_bytes(raw)
    exported = reports.export_report(source, tmp_path / "mixed-report")
    summary = json.loads(Path(exported["outputs"]["json"]["path"]).read_text())
    assert source.read_bytes() == raw
    assert summary["input_sha256"] == hashlib.sha256(raw).hexdigest()
    for key, value in result["slow_tests"].items():
        assert summary[key] == value, key
    assert not (project / "docs/tdq/state.json").exists()


def test_generated_portable_report_runs_outside_project_without_jobs(mixed_artifact, tmp_path):
    raw, project = mixed_artifact
    bundle = Path(build_portable.sinh_ban_antigravity(ROOT, str(tmp_path / "bundle")))
    outside = tmp_path / "outside"
    outside.mkdir()
    source, prefix = outside / "input.json", outside / "portable-report.v1"
    source.write_bytes(raw)
    ledger = (project / "docs/tdq/.tdq-test.jsonl").read_bytes()
    environment = {**os.environ, "PYTHONPATH": "", "PYTHONDONTWRITEBYTECODE": "1",
                   "TDQ_LOG": "0", "TDQ_PROJECT_DIR": str(outside / "nonexistent-project")}
    bootstrap = '''import json,runpy,sys
launches = []
def audit(event, args):
    if event in {"subprocess.Popen", "os.system", "os.posix_spawn", "os.fork", "os.exec"}:
        launches.append(event)
sys.addaudithook(audit)
sys.argv = sys.argv[1:]
try:
    runpy.run_path(sys.argv[0], run_name="__main__")
except SystemExit:
    print("TDQ_PACKAGED_PROCESS_EVENTS " + json.dumps(launches), flush=True)
    raise
'''
    run = subprocess.run([sys.executable, "-c", bootstrap, str(bundle / "scripts/tdq_test.py"), "report",
                          "--result", str(source), "--out-prefix", str(prefix)],
                         cwd=outside, env=environment, capture_output=True, text=True,
                         encoding="utf-8", errors="replace", timeout=30)
    assert run.returncode == 1, run.stdout + run.stderr  # Source FAIL is preserved.
    assert run.stderr == ""
    marker = json.loads(next(line.removeprefix("TDQ_REPORT ") for line in run.stdout.splitlines()
                             if line.startswith("TDQ_REPORT ")))
    assert marker["result_status"] == "FAIL"
    events = json.loads(next(line.removeprefix("TDQ_PACKAGED_PROCESS_EVENTS ")
        for line in run.stdout.splitlines() if line.startswith("TDQ_PACKAGED_PROCESS_EVENTS ")))
    assert events == [], events
    assert marker["input_sha256"] == hashlib.sha256(raw).hexdigest()
    assert source.read_bytes() == raw
    assert {path.name for path in outside.iterdir()} == {
        "input.json", "portable-report.v1.json", "portable-report.v1.md", "portable-report.v1.html"}
    assert (project / "docs/tdq/.tdq-test.jsonl").read_bytes() == ledger
    assert not (bundle / "docs/tdq/state.json").exists()
    assert not (outside / "docs").exists()
    for binding in marker["outputs"].values():
        assert digest(binding["path"]) == binding["sha256"]
    packaged = json.loads((outside / "portable-report.v1.json").read_text())
    assert packaged["result_status"] == "FAIL" and packaged["case_count"] == 4
    # Portable text copying normalizes line endings on the target platform.
    assert (bundle / "scripts/tdq_test_report.py").read_text(encoding="utf-8") == Path(
        ROOT, "scripts/tdq_test_report.py").read_text(encoding="utf-8")
