"""Service diagnostics stay useful without exposing operation payloads."""
import datetime
import hashlib
import io
import json
import runpy
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import tdq_readiness as readiness
import tdq_test as runner
import tdq_test_receipt as receipts
import tdq_transcript as transcript
from tdq_test_manifest import make_manifest
from tdq_test_process import IsolatedJob
from tdq_test_result import from_case_evidence


SECRET = "runtime-secret-fixture-8a531"
RAW = "raw-prompt-and-tool-output-91fb2"


@pytest.fixture(params=[True, False], ids=["default-on", "disabled"])
def logging_enabled(request, monkeypatch):
    if request.param:
        monkeypatch.delenv("TDQ_LOG", raising=False)
    else:
        monkeypatch.setenv("TDQ_LOG", "0")
    return request.param


def assert_service_log(text, enabled, expected):
    assert SECRET not in text and RAW not in text
    if not enabled:
        assert text == ""
        return
    assert text
    for line in text.splitlines():
        assert line.startswith("["), line
        stamp, message = line[1:].split("] ", 1)
        assert datetime.datetime.fromisoformat(stamp).utcoffset() is not None
        assert message
    for token in expected:
        assert token in text


def test_readiness_cold_warm_and_mutation_log_metadata(
        tmp_path, capsys, logging_enabled):
    source = tmp_path / "input.py"
    source.write_text(SECRET, encoding="utf-8")
    calls = []

    def probe():
        calls.append(1)
        return {"available": True, "private_payload": RAW}

    cold, warm, changed = {}, {}, {}
    options = {"inputs": [source], "mode": "auto", "environment": {"TOKEN": SECRET}}
    first = readiness.cached_probe(tmp_path, "logging", "static", probe, stats=cold, **options)
    second = readiness.cached_probe(tmp_path, "logging", "static", probe, stats=warm, **options)
    source.write_text(SECRET + "changed", encoding="utf-8")
    third = readiness.cached_probe(tmp_path, "logging", "static", probe, stats=changed, **options)
    assert first == second == third and len(calls) == 2
    assert cold["probe_calls"] == changed["probe_calls"] == 1
    assert warm["hits"] == 1 and warm["probe_calls"] == 0
    assert warm["execute_seconds"] == warm["wait_seconds"] == 0
    assert cold["execute_seconds"] >= 0 and warm["verify_seconds"] > 0
    assert_service_log(capsys.readouterr().err, logging_enabled,
                       ["readiness executed-static", "reused-static", "verify_seconds="])


def test_transcript_cold_warm_invalid_record_logs_no_raw_payload(
        tmp_path, capsys, logging_enabled):
    source = tmp_path / "session.jsonl"
    records = [
        {"type": "session_meta", "payload": {"cwd": str(tmp_path), "id": SECRET}},
        {"type": "response_item", "timestamp": "2026-10-27T00:00:00Z",
         "payload": {"type": "function_call", "call_id": "call-1", "arguments": RAW}},
        {"type": "response_item", "timestamp": "2026-10-27T00:00:01Z",
         "payload": {"type": "function_call_output", "call_id": "call-1", "output": RAW}},
    ]
    source.write_text("".join(json.dumps(row) + "\n" for row in records), encoding="utf-8")
    cold, warm = {}, {}
    options = {"cache": "auto", "request_id": "logging"}
    first = transcript.read_transcripts(tmp_path, source, cache_stats=cold, **options)
    second = transcript.read_transcripts(tmp_path, source, cache_stats=warm, **options)
    assert first == second and warm["hits"] == 1
    assert cold["parse_seconds"] > 0 and warm["parse_seconds"] == 0
    assert warm["bytes_hashed"] == source.stat().st_size
    with source.open("a", encoding="utf-8") as stream:
        stream.write("{invalid:" + RAW + "\n")
    broken = transcript.read_transcripts(tmp_path, source, **options)
    assert broken != first
    assert_service_log(capsys.readouterr().err, logging_enabled,
                       ["transcript-cache: miss:", "hit: content-verified", "transcript:", "counters="])


def receipt_fixture(project):
    source = project / "test_case.py"
    source.write_text("def test_ok():\n    assert 2 + 3 == 5\n", encoding="utf-8")
    proof = project / "proof.py"
    proof.write_text("def test_dependency():\n    assert 2 + 3 == 5\n", encoding="utf-8")
    case_id = "test_case.py::test_ok"
    manifest = make_manifest([case_id])
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    declaration = {"hermetic": True, "test_source_sha256": digest(source),
                   "input_paths": [source.name], "env_names": ["TOKEN"], "external_inputs": [],
                   "no_network": True, "no_live_clock": True, "no_personal_config": True,
                   "proof": {"test_id": "proof.py::test_dependency", "test_path": proof.name,
                             "source_sha256": digest(proof)}}
    calls = []

    def execute():
        runpy.run_path(str(source))["test_ok"]()
        calls.append(1)
        case = {"case_id": case_id, "outcome": "pass", "reason": RAW,
                "capability": None, "subtests": [],
                "phases": [{"phase": phase, "outcome": "pass", "reason": RAW,
                            "duration_seconds": 0} for phase in ("setup", "call", "teardown")]}
        return from_case_evidence(manifest, [case], 0, [source.name])

    policy = {"schema_version": 1, "cases": {case_id: declaration}}
    return manifest, policy, execute, calls


def test_receipt_execution_reuse_fresh_logs_actions_and_separates_timing(
        tmp_path, capsys, logging_enabled):
    manifest, policy, execute, calls = receipt_fixture(tmp_path)
    options = {"reuse": "auto", "declarations": policy, "environment": {"TOKEN": SECRET}}
    first = receipts.run_with_receipt(tmp_path, "logging", manifest, execute, **options)
    second = receipts.run_with_receipt(tmp_path, "logging", manifest, execute, **options)
    third = receipts.run_with_receipt(tmp_path, "logging", manifest, execute, fresh=True, **options)
    assert [row["action"] for row in (first, second, third)] == ["executed", "reused", "executed"]
    assert len(calls) == 2 and all(row["status"] == "PASS" for row in (first, second, third))
    assert second["source_receipt_id"] == first["source_receipt_id"]
    assert second["timings"]["execute_seconds"] == second["timings"]["wait_seconds"] == 0
    assert second["timings"]["verify_seconds"] > 0
    assert first["timings"]["execute_seconds"] > 0
    assert_service_log(capsys.readouterr().err, logging_enabled,
                       ["receipt action=executed reason=", "action=reused reason="])


@pytest.mark.parametrize("failure", [False, True], ids=["exit-zero", "exit-nonzero"])
def test_process_logs_facts_not_captured_child_payload(
        tmp_path, capsys, logging_enabled, failure):
    command = [sys.executable, "-c",
               "import os,sys; print(os.environ['TOKEN']); print('" + RAW
               + "',file=sys.stderr); sys.exit(" + str(int(failure)) + ")"]
    with IsolatedJob(tmp_path, timeout_seconds=10, env={"TOKEN": SECRET}) as job:
        result = job.run(command, phase="execution")
    assert result["reason"] == "exited" and result["exit_code"] == int(failure)
    assert result["cleanup_complete"]
    assert SECRET in result["stdout"] and RAW in result["stderr"]
    assert result["wall_seconds"] == result["duration_seconds"]
    assert result["execute_seconds"] + result["cleanup_seconds"] == pytest.approx(result["wall_seconds"])
    assert_service_log(capsys.readouterr().err, logging_enabled,
                       ["tdq_test_process reason=", "exit_code=", "wall=", "cleanup="])


def test_runner_proof_error_logs_safe_reason_and_keeps_failure_evidence(
        tmp_path, capsys, monkeypatch, logging_enabled):
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_case.py").write_text("def test_fail():\n    assert False\n", encoding="utf-8")

    def unavailable(*args):
        raise OSError("credential=" + SECRET + " " + RAW)

    monkeypatch.setattr(runner, "_persist_result", unavailable)
    result = runner.chay_tron_bo_result(
        tmp_path, stream=io.StringIO(), request="logging", job_kind="correctness",
        timeout_seconds=30, environment={"TOKEN": SECRET})
    assert result["status"] == "FAIL" and result["tests_run"] == 1
    assert not result["details_complete"] and result["case_outcomes"]
    assert result["finalization"]["error_type"] == "OSError"
    ledger = json.loads((tmp_path / "docs/tdq/.tdq-test.jsonl").read_text(encoding="utf-8"))
    assert ledger["status"] == "FAIL" and ledger["action"] == "executed"
    assert ledger["timings"] == result["timings"]
    assert result["timings"]["wait_seconds"] == 0
    assert result["timings"]["execute_seconds"] > 0
    assert result["timings"]["collection_seconds"] > 0
    assert result["timings"]["wall_seconds"] >= sum(
        result["timings"][field] for field in ("verify_seconds", "execute_seconds", "collection_seconds"))
    assert_service_log(capsys.readouterr().err, logging_enabled,
                       ["receipt action=executed reason=", "status=FAIL", "reason="])
