"""Benchmark arithmetic is tested separately from real production API samples."""
import copy
import json
from pathlib import Path
import sys
import threading
import time
import uuid

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import tdq_runtime_bench as bench


def test_pair_order_and_threshold():
    assert bench.pair_order(3) == [(1, 1), (1, 2), (2, 2), (2, 1), (3, 1), (3, 2)]
    summary = bench.performance_summary([10, 12, 11], [8, 7, 8], .2)
    assert summary["met"]
    assert summary["reduction"] == pytest.approx(1 - 8 / 11)
    assert bench.performance_summary([10, 10, 10], [8, 8, 8], .2)["met"]
    assert not bench.performance_summary([1, 1, 1], [2, 2, 2], .2)["met"]


def test_missing_or_corrupt_report_fails_closed(tmp_path):
    path = tmp_path / "missing.json"
    assert not bench.verify_report(path)["valid"]
    path.write_text('{bad')
    assert not bench.verify_report(path)["valid"]


def test_warm_faster_than_cold_but_slower_than_off_is_not_a_gain():
    rows = [{"mode": mode, "wall_seconds": seconds}
            for _ in range(3) for mode, seconds in (("off", 5), ("cold", 10), ("warm", 8))]
    result = bench._cache_performance(rows)
    assert not result["met"]
    assert result["baseline_median"] == 5 and result["cold_median"] == 10
    assert result["cold_overhead_seconds"] == 5


def test_missing_real_log_preserves_all_unavailable_samples(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    output = tmp_path / "unavailable.json"
    report = {"request": "audit", "samples": []}
    bench._cache_group(report, raw, output, "transcript-real", 3,
        lambda request, mode: bench._transcript_call(tmp_path, [tmp_path / "missing.jsonl"], request, mode),
        "real-transcripts")
    assert len(report["samples"]) == 9
    assert all(row["status"] == "UNAVAILABLE" for row in report["samples"])
    assert all(row["classification"] == "real-transcripts" for row in report["samples"])
    assert len(output.with_suffix(".samples.jsonl").read_text().splitlines()) == 9
    errors = []
    bench._verify_cache_group("transcript-real", report["samples"], errors)
    assert errors


def test_empty_real_manifest_is_not_replaced_with_simulation(tmp_path):
    manifest = tmp_path / "real.json"
    manifest.write_text('{"checks": []}')
    with pytest.raises(ValueError, match="no source paths"):
        bench._real_sources(manifest, [])


def test_semantic_parity_keeps_subtests_but_ignores_duration():
    first = {"subtests": [{"outcome": "pass", "duration_seconds": 1, "subtest": {"x": "1"}}]}
    second = copy.deepcopy(first)
    second["subtests"][0]["duration_seconds"] = 2
    assert bench._without_durations(first) == bench._without_durations(second)
    second["subtests"][0]["outcome"] = "skip"
    assert bench._without_durations(first) != bench._without_durations(second)


def test_full_fixture_runs_six_real_jobs_and_binds_raw_evidence(tmp_path):
    repo = bench.create_fixture(tmp_path / "fixture")
    output = repo / "docs/tdq/artifacts/full.json"
    report = bench.full_pairs(repo, output, pairs=3, simulation=True)
    verified = bench.verify_report(output)
    assert verified["valid"], verified
    assert len(report["samples"]) == 6
    assert {row["classification"] for row in report["samples"]} == {"simulation"}
    assert all(row["action"] == "executed" for row in report["samples"])
    assert all(Path(row["result_path"]).is_file() for row in report["samples"])
    assert report["resource_time"]["seconds"] is None
    qc_source = copy.deepcopy(report["source"]["before"])
    qc_source["inputs"]["environment_sha256"] = "different-private-home"
    assert bench.verify_report(output, expected_source=qc_source)["valid"]
    qc_source["inputs"]["implementation"] = {"changed": "module"}
    assert not bench.verify_report(output, expected_source=qc_source)["valid"]
    source = repo / "tests/test_case.py"
    original_source = source.read_bytes()
    source.write_bytes(original_source + b"\n# changed after measurement\n")
    assert not bench.verify_report(output)["valid"]
    source.write_bytes(original_source)
    for field, value in (("wall_seconds", .00001), ("environment_sha256", "changed")):
        forged = copy.deepcopy(report)
        forged["samples"][0][field] = value
        bench.write_report(output, forged)
        assert not bench.verify_report(output)["valid"]
    forged = copy.deepcopy(report)
    forged["samples"].pop()
    bench.write_report(output, forged)
    assert not bench.verify_report(output)["valid"]
    bench.write_report(output, report)
    raw = Path(report["samples"][0]["result_path"])
    stored = json.loads(raw.read_text())
    forged_result = {**stored, "tests_run": 9999}
    evidence = bench._write(raw, forged_result)
    forged = copy.deepcopy(report)
    forged["samples"][0]["result_sha256"] = evidence["sha256"]
    bench.write_report(output, forged)
    assert not bench.verify_report(output)["valid"]
    bench._write(raw, stored)
    bench.write_report(output, report)
    raw.write_text(raw.read_text() + " ")
    assert not bench.verify_report(output)["valid"]


def test_source_environment_or_order_forgery_rejected(tmp_path, monkeypatch):
    # This validator fixture is explicitly synthetic, never performance evidence.
    source = {"key": "x", "inputs": {"files": {}, "project": "p", "runtime": {},
                                      "policy_sha256": "p", "environment_sha256": "env"}}
    rows = [{"pair": pair, "workers": workers, "order": index,
             "started_at": index * 2., "finished_at": index * 2. + 1.,
             "wall_seconds": 1., "environment_sha256": "env"}
            for index, (pair, workers) in enumerate(bench.pair_order(3))]
    errors = []
    bench.validate_order(rows, errors)
    assert not errors
    rows[2]["started_at"] = 0
    bench.validate_order(rows, errors)
    assert errors
    assert bench.source_identity(source) == bench.source_identity({
        **source, "inputs": {**source["inputs"], "environment_sha256": "private-home-change"}})
    assert bench.source_identity(source) != bench.source_identity({
        **source, "inputs": {**source["inputs"], "files": {"changed": "sha"}}})


def test_cross_run_projection_only_ignores_exact_current_lifecycle_metadata():
    request = "2026-10-27-1846-kiem-chung-tang-toc"
    plan = f"docs/tdq/plan/{request}.md"
    source = {"inputs": {"request": request, "files": {plan: "old", "docs/guide.md": "guide"}}}
    ticked = copy.deepcopy(source)
    ticked["inputs"]["files"][plan] = "ticked"
    assert source != ticked  # Strict job/receipt source comparison still detects it.
    assert bench.source_identity(source) == bench.source_identity(ticked)
    for path in ("docs/guide.md", "docs/tdq/plan/another-request.md", "docs/tdq/spec/" + request + ".md",
                 "scripts/runner.py", "docs/workinglog/2026-10-28.md", "docs/architecture/design.md"):
        changed = copy.deepcopy(source)
        changed["inputs"]["files"][path] = "changed"
        assert bench.source_identity(source) != bench.source_identity(changed), path
    assert bench._comparison_exclusions({"inputs": {"request": "../../escape"}}) == []


def test_six_actual_serial_jobs_cannot_be_relabeled_as_parallel(tmp_path, monkeypatch):
    original = bench._run
    def force_serial(*args, **kwargs):
        return original(*args, **{**kwargs, "workers": 1})
    monkeypatch.setattr(bench, "_run", force_serial)
    repo = bench.create_fixture(tmp_path / "fixture")
    report = bench.full_pairs(repo, repo / "docs/tdq/artifacts/mislabeled.json", simulation=True)
    assert not report["verification"]["valid"], report["verification"]


def test_cache_fixture_triples_have_parity_and_real_warm_hits(tmp_path):
    repo = bench.create_fixture(tmp_path / "fixture")
    output = repo / "docs/tdq/artifacts/cache.json"
    report = bench.cache_pairs(repo, output, pairs=3, readiness_fixture=True)
    verified = bench.verify_report(output)
    assert verified["valid"], verified
    assert len(report["samples"]) == 27
    warm = [row for row in report["samples"] if row["mode"] == "warm"]
    assert len(warm) == 9
    assert all(row["cache_hit"] for row in warm)
    assert {row["classification"] for row in report["samples"]} == {"simulation"}
    report["samples"][0]["business_sha256"] = "forged"
    bench.write_report(output, report)
    assert not bench.verify_report(output)["valid"]


def test_runtime_process_timeout_has_owned_descendant_evidence(tmp_path):
    repo = bench.create_fixture(tmp_path / "fixture")
    output = repo / "docs/tdq/artifacts/runtime.json"
    report = bench.runtime_smoke(repo, output, scenario_timeout=20,
                                 scenarios=["process-timeout"])
    assert report["samples"][0]["scenario_result"]["process"]["timed_out"]
    assert report["samples"][0]["scenario_result"]["process"]["cleanup_complete"]
    assert not bench.verify_report(output)["valid"]  # Full scenario inventory required.


def test_heartbeat_survives_kill_during_next_write(tmp_path):
    heartbeat, gap = tmp_path / "heartbeat", tmp_path / "gap"
    prefix = f'''from pathlib import Path
import time
original = Path.write_text
writes = 0
def interrupted(path, value, *args, **kwargs):
 global writes
 if path.name in ('heartbeat', 'heartbeat.tmp'):
  writes += 1
  if writes == 2:
   with path.open('w'): pass
   original(Path({str(gap)!r}), 'writing')
   time.sleep(60)
 return original(path, value, *args, **kwargs)
Path.write_text = interrupted
'''
    cancel = threading.Event()
    def watch():
        deadline = time.monotonic() + 5
        while not gap.exists() and time.monotonic() < deadline:
            time.sleep(.01)
        cancel.set()
    watcher = threading.Thread(target=watch)
    watcher.start()
    with bench.IsolatedJob(tmp_path, timeout_seconds=10, cancel_event=cancel) as job:
        result = job.run([sys.executable, "-c", prefix + bench._heartbeat_program(heartbeat)], phase="interrupted-write")
    watcher.join(timeout=6)
    assert gap.is_file() and result["cancelled"] and result["cleanup_complete"]
    assert heartbeat.read_text(), {"process": result, "heartbeat": heartbeat.read_text()}


def test_join_remains_joined_when_second_caller_arrives_late(tmp_path, monkeypatch):
    original_fixture, original_run = bench.create_fixture, bench._run
    monkeypatch.setattr(bench, "create_fixture", lambda repo, **kwargs: original_fixture(repo))
    finished, lock, calls = threading.Event(), threading.Lock(), []
    def delayed(*args, **kwargs):
        with lock:
            number = len(calls)
            calls.append(number)
        if number:
            finished.wait(5)
        try:
            return original_run(*args, **kwargs)
        finally:
            if not number:
                finished.set()
    monkeypatch.setattr(bench, "_run", delayed)
    result = bench._join_scenario(tmp_path, tmp_path / "docs/tdq/artifacts")
    actions = [row.get("action") for row in result["results"]]
    assert sorted(actions) == ["executed", "joined"], {"actions": actions, "facts": result.get("handshake")}


def test_runtime_all_scenarios_use_real_processes_and_persist_proof(tmp_path):
    repo = bench.create_fixture(tmp_path / "fixture")
    output = repo / "docs/tdq/artifacts/runtime-all.json"
    report = bench.runtime_smoke(repo, output, scenario_timeout=30)
    verified = bench.verify_report(output)
    artifact = Path(__file__).resolve().parents[1] / "docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc"
    diagnostic = artifact / ("runtime-" + uuid.uuid4().hex[:8] + ".json")
    bench._write(diagnostic, {"schema": "tdq-runtime-test-attempt/v1", "verification": verified,
                             "report_digest": report["digest"], "facts": [bench._runtime_facts(row) for row in report["samples"]]})
    assert verified["valid"], {"diagnostic": str(diagnostic), "verification": verified}
    assert verified["verdict"] == "PERFORMANCE_MET"
    assert {row["scenario"] for row in report["samples"]} == set(bench.SCENARIOS)
    assert all(row["elapsed_seconds"] < 30 for row in report["samples"])
    report["samples"][0]["elapsed_seconds"] = 121
    bench.write_report(output, report)
    assert not bench.verify_report(output)["valid"]


def test_invalid_limits_are_usage_errors(tmp_path):
    with pytest.raises(ValueError):
        bench.pair_order(0)
    with pytest.raises(ValueError):
        bench.runtime_smoke(tmp_path, tmp_path / "x.json", scenario_timeout=121)
    assert bench.main(["verify", str(tmp_path / "missing.json")]) == 1


import unittest


class TestTdqRuntimeBenchAdapter(unittest.TestCase):
    """unittest discovery adapter for test_tdq_runtime_bench."""

    def test_pair_order_and_threshold(self):
        test_pair_order_and_threshold()

    def test_semantic_parity_keeps_subtests_but_ignores_duration(self):
        test_semantic_parity_keeps_subtests_but_ignores_duration()

    def test_warm_faster_than_cold_but_slower_than_off_is_not_a_gain(self):
        test_warm_faster_than_cold_but_slower_than_off_is_not_a_gain()

    def test_cross_run_projection_only_ignores_exact_current_lifecycle_metadata(self):
        test_cross_run_projection_only_ignores_exact_current_lifecycle_metadata()

    def test_full_pytest_suite(self):
        test_file = str(Path(__file__).resolve())
        ret = pytest.main(["-q", test_file, "-k", "not test_full_pytest_suite"])
        self.assertEqual(ret, 0, "pytest benchmark suite failed")

