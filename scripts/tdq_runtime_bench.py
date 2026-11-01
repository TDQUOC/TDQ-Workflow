"""Finite runtime experiments with persisted evidence and conservative verification.

Full samples execute sequential AB/BA pairs. Fixture experiments are explicitly
simulation; CPU for the complete process tree is unavailable, never wall time.
TDQ_LOG=0 disables metadata-only lifecycle messages. This module never writes state.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import statistics
import subprocess
import sys
import tempfile
import threading
import time
import uuid

import utf8_io  # noqa: F401 -- Configure UTF-8 for CLI streams on Windows.
import tdq_lsp
import tdq_readiness
import tdq_test
import tdq_test_manifest
import tdq_test_receipt
import tdq_test_result
import tdq_transcript
from tdq_test_process import IsolatedJob


SCHEMA = "tdq-runtime-bench/v1"
SCENARIOS = ("process-timeout", "process-cancel", "join", "owner-crash", "freshness", "transcript")
RESOURCE_UNAVAILABLE = {"seconds": None, "quality": "unavailable", "scope": "process-tree",
                        "reason": "No complete tree CPU accounting is exported by the runner"}


def _log(message):
    if os.environ.get("TDQ_LOG", "1") != "0":
        print(f"[{datetime.now(timezone.utc).isoformat()}] runtime-bench: {message}", file=sys.stderr)


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=True, allow_nan=False).encode()).hexdigest()


def _file_sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def _write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False), encoding="utf-8")
    return {"path": str(path.resolve()), "sha256": _file_sha(path)}


def _read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def pair_order(pairs):
    """Return alternating serial/parallel pairs; never schedule them concurrently."""
    if type(pairs) is not int or pairs < 1:
        raise ValueError("pairs must be a positive integer")
    return [(pair + 1, worker) for pair in range(pairs)
            for worker in ((1, 2) if pair % 2 == 0 else (2, 1))]


def performance_summary(baseline, optimized, threshold):
    """Summarize every supplied sample; callers validate evidence before recommending."""
    first, second = statistics.median(baseline), statistics.median(optimized)
    reduction = 1 - second / first if first > 0 else 0
    return {"baseline_median": first, "optimized_median": second,
            "baseline_range": [min(baseline), max(baseline)],
            "optimized_range": [min(optimized), max(optimized)],
            "reduction": reduction, "met": second <= first * (1 - threshold) and second < first}


def source_identity(source):
    """Cross-run projection only; per-job and paired-source comparisons remain exact."""
    inputs = source.get("inputs", {})
    fields = ("schema_version", "project", "request", "runtime", "policy_sha256",
              "implementation", "flags_sha256")
    identity = {key: inputs.get(key) for key in fields}
    excluded = _comparison_exclusions(source)
    identity["files"] = {path: digest for path, digest in inputs.get("files", {}).items() if path not in excluded}
    return identity


def _comparison_exclusions(source):
    request = source.get("inputs", {}).get("request")
    if not isinstance(request, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}-\d{4}-[\w-]+", request):
        return []
    try:
        datetime.strptime(request[:10], "%Y-%m-%d")
    except ValueError:
        return []
    paths = ["docs/tdq/state.json", "docs/tdq/STATE.md", "docs/tdq/.tdq-turn.jsonl",
             "docs/tdq/.tdq-test.log", "docs/tdq/timing.jsonl", "docs/tdq/worktrees.json",
             "docs/tdq/worktrees.md", "docs/architecture/status.json",
             f"docs/workinglog/{request[:10]}.md"]
    paths.extend(f"docs/tdq/{folder}/{request}.{extension}" for folder, extension in
                 (("plan", "md"), ("team", "json"), ("qc", "md"), ("reports", "md"), ("reports", "html")))
    return sorted(paths)


def _comparison_policy(source):
    return {"schema": "tdq-benchmark-source-projection/v1", "scope": "cross-run-only",
            "excluded_files": _comparison_exclusions(source)}


def _source(repo, request, environment):
    return tdq_test.source_fingerprint(repo, request, environment=environment)


def _report(repo, output, kind, environment):
    output = Path(output).resolve()
    request = tdq_readiness.request_id(repo) or "runtime-benchmark"
    report = {"schema": SCHEMA, "kind": kind, "request": request,
              "project": str(Path(repo).resolve()), "samples": [],
              "resource_time": dict(RESOURCE_UNAVAILABLE),
              "environment_sha256": _digest(environment),
              "environment_comparison": "Strict within this run; QC HOME/TMP may intentionally differ",
              "qc_private_environment_keys": ["HOME", "USERPROFILE", "TMP", "TEMP", "TMPDIR",
                                               "APPDATA", "LOCALAPPDATA", "CODEX_HOME"],
              "source": {"before": _source(repo, request, environment)}}
    report["source_comparison"] = _comparison_policy(report["source"]["before"])
    raw = output.parent / ("raw-" + uuid.uuid4().hex[:8])
    raw.mkdir(parents=True, exist_ok=True)
    return report, raw


def write_report(path, report):
    """Persist all samples, including failures, with an integrity digest."""
    unsigned = {key: value for key, value in report.items() if key != "digest"}
    report["digest"] = _digest(unsigned)
    _write(path, report)
    jsonl = Path(path).with_suffix(".samples.jsonl")
    jsonl.write_text("".join(json.dumps(row, ensure_ascii=True) + "\n"
                             for row in report.get("samples", [])), encoding="utf-8")


def _finish(repo, output, report, environment):
    report["source"]["after"] = _source(repo, report["request"], environment)
    report["environment_after_sha256"] = _digest(dict(IsolatedJob(repo).env))
    write_report(output, report)
    checked = verify_report(output)
    report["verification"] = checked
    write_report(output, report)
    _log(f"{report['kind']} {checked['verdict']} samples={len(report['samples'])}")
    return report


def _run(repo, directory, request, environment, *, workers=1, reuse="off", fresh=True):
    return tdq_test.chay_tron_bo_result(
        repo, io.StringIO(), workers=workers, timeout_seconds=1800, reuse=reuse,
        fresh=fresh, request=request, environment=environment, artifact_dir=directory,
        job_kind="benchmark")


def full_pairs(repo, output, *, pairs=3, workers=(1, 2), reuse="off", simulation=False):
    """Run every full sample through the public runner, including its benchmark ledger."""
    if list(workers) != [1, 2] or reuse != "off":
        raise ValueError("Full pairs require workers 1 2 and reuse off")
    environment = dict(IsolatedJob(repo).env)
    report, raw = _report(repo, output, "full-pairs", environment)
    for index, (pair, worker) in enumerate(pair_order(pairs)):
        started = time.time()
        tick = time.perf_counter()
        result = _run(repo, raw / str(index), report["request"], environment, workers=worker)
        row = {"pair": pair, "order": index, "workers": worker, "reuse": "off", "fresh": True,
               "classification": "simulation" if simulation else "real-full-suite",
               "started_at": started, "finished_at": time.time(),
               "wall_seconds": result.get("timings", {}).get("wall_seconds", time.perf_counter() - tick),
               "caller_wall_seconds": time.perf_counter() - tick,
               "action": result.get("action"), "environment_sha256": _digest(environment),
               "source_before": result.get("source_before"), "source_after": result.get("source_after"),
               "timings": result.get("timings", {}), "resource_time": dict(RESOURCE_UNAVAILABLE)}
        artifact = result.get("result_artifact") or _write(raw / f"failure-{index}.json", result)
        row.update(result_path=artifact["path"], result_sha256=artifact["sha256"])
        report["samples"].append(row)
        write_report(output, report)
    report["recommendation"] = {"workers": 1, "reason": "Serial until paired evidence meets threshold"}
    return _finish(repo, output, report, environment)


def create_fixture(repo, *, delay=0):
    """Create a small hermetic synthetic workload; never describe it as real workflow load."""
    repo = Path(repo).resolve()
    (repo / "tests").mkdir(parents=True, exist_ok=True)
    source = repo / "tests/test_case.py"
    source.write_text(
        "import time\nfrom pathlib import Path\n"
        "def test_ok(tmp_path):\n"
        " assert tmp_path.is_dir() and 2 + 2 == 4\n"
        " marker=Path(__file__).resolve().parents[1]/'docs/tdq/cache/executions.txt'\n"
        " marker.parent.mkdir(parents=True,exist_ok=True)\n"
        " with marker.open('a') as stream: stream.write('executed\\n')\n"
        f" time.sleep({float(delay)!r})\n", encoding="utf-8")
    declaration = {"hermetic": True, "no_network": True, "no_live_clock": True,
                   "no_personal_config": True, "external_inputs": [],
                   "input_paths": ["tests/test_case.py"], "env_names": [],
                   "test_source_sha256": _file_sha(source),
                   "proof": {"test_id": "tests/test_case.py::test_ok", "test_path": "tests/test_case.py",
                             "source_sha256": _file_sha(source)}}
    _write(repo / "docs/tdq/reuse-policy.json", {"schema_version": 1,
            "cases": {"tests/test_case.py::test_ok": declaration}})
    return repo


def _business_result(result):
    return {key: result.get(key) for key in ("status", "backend", "tests_run", "skipped", "details_complete",
                                            "failed_modules", "coverage")}


def _cache_sample(group, pair, mode, classification, call, raw):
    started, tick = time.time(), time.perf_counter()
    value, business, stats, inputs, hit = call()
    caller_elapsed = time.perf_counter() - tick
    elapsed = stats.get("call_wall_seconds", caller_elapsed)
    evidence = _write(raw / f"{group}-{pair}-{mode}.json", value)
    return {"group": group, "pair": pair, "mode": mode, "classification": classification,
            "started_at": started, "finished_at": time.time(), "wall_seconds": elapsed,
            "caller_wall_seconds": caller_elapsed,
            "input_sha256": inputs, "business_sha256": _digest(business), "cache_hit": hit,
            "business": business, "timings": stats, "raw_result_path": evidence["path"],
            "raw_result_sha256": evidence["sha256"], "resource_time": dict(RESOURCE_UNAVAILABLE)}


def _reuse_call(repo, raw, request, environment, mode):
    result = _run(repo, raw, request, environment, reuse="off" if mode == "off" else "auto",
                  fresh=mode == "off")
    stats = dict(result.get("timings", {}))
    stats["call_wall_seconds"] = stats.get("wall_seconds", 0)
    return (result, _business_result(result), stats,
            result.get("source_before", {}).get("key"), result.get("action") == "reused")


def _readiness_call(repo, request, mode, fixture):
    stats = {}
    started = time.perf_counter()
    cache_mode = "off" if mode == "off" else "auto"
    if fixture:
        files = [Path(repo) / "tests/test_case.py"]
        def probe():
            return {"syntax_valid": bool(compile(files[0].read_text(), str(files[0]), "exec"))}
        value = tdq_readiness.cached_probe(repo, request, "fixture-syntax", probe,
                                           inputs=files, mode=cache_mode, stats=stats)
    else:
        rows = tdq_lsp.chay_kiem(repo, cache_mode=cache_mode, request=request, stats=stats)
        value = [{"rung": row.so, "ready": row.dat, "warning": row.chi_canh_bao} for row in rows]
    stats["call_wall_seconds"] = time.perf_counter() - started
    stats["scope"] = "Static probe counters; call wall includes live ladder when real"
    source = _source(repo, "readiness-input", {})
    return ({"value": value, "stats": stats, "source": source}, value, stats,
            source["key"], stats.get("hits", 0) > 0)


def _transcript_fixture(repo, destination):
    records = [{"type": "session_meta", "payload": {"id": "benchmark-fixture", "cwd": str(repo)}}]
    for index in range(200):
        for phase, seconds in (("function_call", 0), ("function_call_output", 1)):
            records.append({"type": "response_item", "timestamp": f"2026-10-27T00:00:0{seconds}Z",
                            "payload": {"type": phase, "call_id": str(index), "output": "x" * 1024}})
    destination.write_text("".join(json.dumps(row) + "\n" for row in records), encoding="utf-8")
    return destination


def _transcript_call(repo, sources, request, mode):
    stats, values, hashes = {}, [], []
    for path in sources:
        before = _file_sha(path)
        local = {}
        started = time.perf_counter()
        result = tdq_transcript.read_transcripts(repo, path, cache="off" if mode == "off" else "auto",
                                                 request_id=request, cache_stats=local)
        local["call_wall_seconds"] = time.perf_counter() - started
        after = _file_sha(path)
        _stable_transcript(result, local, before, after)
        local["wait_seconds"] = 0.0  # Transcript cache has no coordination wait.
        local["execute_seconds"] = local.get("parse_seconds", 0.0)
        hashes.append((str(Path(path).resolve()), before))
        result["spans"] = [{**span, "start": span["start"].isoformat(), "end": span["end"].isoformat()}
                           for span in result["spans"]]
        values.append(result)
        for key, value in local.items():
            if isinstance(value, (int, float)):
                stats[key] = stats.get(key, 0) + value
    return ({"value": values, "stats": stats, "inputs": hashes}, values, stats,
            _digest(hashes), stats.get("hits", 0) == len(sources))


def _stable_transcript(result, stats, before, after):
    if before != after or stats.get("unstable") or stats.get("unreadable"):
        raise ValueError("Transcript input is missing or active")
    if not any(source.get("status") == "accepted" for source in result.get("sources", [])):
        raise ValueError("Transcript metadata does not match this project")


def _real_sources(manifest, paths):
    sources = list(paths or [])
    if manifest:
        data = _read(manifest)
        sources.extend(source["path"] for check in data.get("checks", []) for source in check.get("sources", []))
        if not sources:
            raise ValueError("Real transcript manifest contains no source paths")
    return list(dict.fromkeys(sources))


def _cache_group(report, raw, output, group, pairs, callback, classification):
    for pair in range(1, pairs + 1):
        namespace = {"request": report["request"], "run": raw.name, "group": group, "pair": pair}
        request = "b" + _digest(namespace)[:16]
        for mode in (("off", "cold", "warm") if pair % 2 else ("cold", "warm", "off")):
            try:
                row = _cache_sample(group, pair, mode, classification, lambda: callback(request, mode), raw)
            except (OSError, ValueError) as error:
                row = {"group": group, "pair": pair, "mode": mode, "classification": classification,
                       "status": "UNAVAILABLE", "error": type(error).__name__}
            row["namespace"] = {**namespace, "cache_request": request}
            report["samples"].append(row)
            write_report(output, report)


def cache_pairs(repo, output, *, pairs=3, readiness_fixture=False,
                 real_transcript_manifest=None, real_transcripts=()):
    """Measure production cache paths; fixture and real-log samples remain separate."""
    pair_order(pairs)
    sources = _real_sources(real_transcript_manifest, real_transcripts)
    environment = dict(IsolatedJob(repo).env)
    report, raw = _report(repo, output, "cache-pairs", environment)
    transcript = _transcript_fixture(repo, raw / "transcript.jsonl")
    with tempfile.TemporaryDirectory(prefix="tb-") as directory:
        fixture = create_fixture(Path(directory) / "r")
        _cache_group(report, raw, output, "reuse", pairs,
                     lambda request, mode: _reuse_call(fixture, raw / "reuse", request, environment, mode), "simulation")
    _cache_group(report, raw, output, "readiness", pairs,
                 lambda request, mode: _readiness_call(repo, request, mode, readiness_fixture),
                 "simulation" if readiness_fixture else "real-readiness")
    _cache_group(report, raw, output, "transcript-simulation", pairs,
                 lambda request, mode: _transcript_call(repo, [transcript], request, mode), "simulation")
    if sources:
        _cache_group(report, raw, output, "transcript-real", pairs,
                     lambda request, mode: _transcript_call(repo, sources, request, mode), "real-transcripts")
    report["recommendation"] = {"cache_modes": {"reuse": "off", "readiness": "off", "transcript": "off"},
                                "reason": "Keep defaults off; recommendations require measured valid pairs"}
    return _finish(repo, output, report, environment)


def _heartbeat_program(heartbeat):
    return ("import os,time; from pathlib import Path; "
            f"p=Path({str(heartbeat)!r}); temporary=p.with_suffix('.tmp'); "
            "exec('while True:\\n temporary.write_text(str(os.getpid())+\":\"+str(time.time_ns()))"
            "\\n temporary.replace(p)\\n time.sleep(.03)')")


def _read_heartbeat(path):
    try:
        return path.read_text()
    except OSError:
        return ""


def _heartbeat_ready(path, ready, cancel_event, stopped, cancel):
    deadline = time.monotonic() + 3
    while not stopped.is_set() and time.monotonic() < deadline:
        if _read_heartbeat(path):
            ready.set()
            if cancel:
                cancel_event.set()
            return
        stopped.wait(.01)


def _tree_scenario(repo, cancel):
    heartbeat = repo / "heartbeat"
    child = _heartbeat_program(heartbeat)
    code = f"import subprocess,sys,time; subprocess.Popen([sys.executable,'-c',{child!r}]); time.sleep(60)"
    event, ready, stopped = threading.Event(), threading.Event(), threading.Event()
    watcher = threading.Thread(target=_heartbeat_ready, args=(heartbeat, ready, event, stopped, cancel))
    try:
        with IsolatedJob(repo, timeout_seconds=3, cancel_event=event) as job:
            watcher.start()
            result = job.run([sys.executable, "-c", code], phase="runtime-tree")
        before = _read_heartbeat(heartbeat)
        time.sleep(.1)
        after = _read_heartbeat(heartbeat)
        return {"process": result, "ready_observed": ready.is_set(),
                "heartbeat_before": before, "heartbeat_after": after}
    finally:
        stopped.set()
        if watcher.ident is not None:
            watcher.join(timeout=1)


def _profiled_join_call(repo, artifacts, environment, owner_ready, join_ready, facts):
    """Observe real receipt branches; hold the owner until a waiter has joined.

    The profiler is local to this caller thread and never replaces product logic
    or return values. The workload remains a pure fixture without a timed delay.
    """
    def observe(frame, event, argument):
        if event != "call":
            return
        if frame.f_code is tdq_test_receipt._execute_owner.__code__:
            facts["owner_ready_at"] = time.monotonic()
            owner_ready.set()
            if not join_ready.wait(15):
                raise TimeoutError("Join fixture waiter did not enter join branch")
        elif frame.f_code is tdq_test_receipt._joined_result.__code__:
            facts["join_ready_at"] = time.monotonic()
            join_ready.set()
    previous = sys.getprofile()
    sys.setprofile(observe)
    try:
        return _run(repo, artifacts, "runtime-join", environment, reuse="auto", fresh=False)
    finally:
        sys.setprofile(previous)


def _join_scenario(repo, artifacts):
    create_fixture(repo)
    environment = dict(os.environ)
    owner_ready, join_ready, facts = threading.Event(), threading.Event(), {}
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(_profiled_join_call, repo, artifacts, environment, owner_ready, join_ready, facts)
        if not owner_ready.wait(10):
            raise TimeoutError("Join fixture owner did not acquire execution lease")
        second = pool.submit(_profiled_join_call, repo, artifacts, environment, owner_ready, join_ready, facts)
        futures = [first, second]
        results = [future.result() for future in futures]
    count = len((repo / "docs/tdq/cache/executions.txt").read_text().splitlines())
    return {"results": results, "execution_count": count, "handshake": facts}


def _crash_scenario(repo, artifacts):
    create_fixture(repo, delay=2)
    artifacts.mkdir(parents=True, exist_ok=True)
    output = artifacts / "owner.json"
    code = ("import sys,json,os; "
            f"sys.path.insert(0,{str(Path(__file__).parent)!r}); import tdq_test; "
            f"r=tdq_test.chay_tron_bo_result({str(repo)!r},reuse='auto',request='runtime-crash',artifact_dir={str(artifacts)!r}); "
            f"open({str(output)!r},'w').write(json.dumps(r))")
    owner = subprocess.Popen([sys.executable, "-c", code], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        deadline = time.monotonic() + 10
        leases = []
        while not leases and time.monotonic() < deadline:
            leases = list((repo / "docs/tdq/cache").rglob("lease.json"))
            time.sleep(.03)
        if not leases:
            raise ValueError("Owner did not acquire lease")
        owner.kill()
        owner.wait(timeout=5)
        result = _run(repo, artifacts, "runtime-crash", dict(os.environ), reuse="auto", fresh=False)
        return {"owner_pid": owner.pid, "owner_exit_code": owner.returncode, "result": result}
    finally:
        if owner.poll() is None:
            owner.kill()
            owner.wait(timeout=5)


def _freshness_scenario(repo, artifacts):
    create_fixture(repo)
    environment = dict(os.environ)
    first = _run(repo, artifacts, "runtime-fresh", environment, reuse="auto", fresh=False)
    second = _run(repo, artifacts, "runtime-fresh", environment, reuse="auto", fresh=False)
    fresh = _run(repo, artifacts, "runtime-fresh", environment, reuse="auto", fresh=True)
    return {"results": [first, second, fresh]}


def _scenario(name, repo, artifacts):
    repo.mkdir(parents=True, exist_ok=True)
    if name in ("process-timeout", "process-cancel"):
        return _tree_scenario(repo, name == "process-cancel")
    if name == "join":
        return _join_scenario(repo, artifacts)
    if name == "owner-crash":
        return _crash_scenario(repo, artifacts)
    if name == "freshness":
        return _freshness_scenario(repo, artifacts)
    source = _transcript_fixture(repo, repo / "transcript.jsonl")
    values = [_transcript_call(repo, [source], "runtime-transcript", mode) for mode in ("off", "cold", "warm")]
    return {"business": [value[1] for value in values], "warm_hit": values[-1][-1]}


def runtime_smoke(repo, output, *, scenario_timeout=120, scenarios=SCENARIOS):
    """Run each actual scenario in a separately owned process tree with a hard cap."""
    if not 0 < scenario_timeout <= 120:
        raise ValueError("Scenario timeout must be within 0..120 seconds")
    environment = dict(IsolatedJob(repo).env)
    report, raw = _report(repo, output, "runtime-smoke", environment)
    for name in scenarios:
        if name not in SCENARIOS:
            raise ValueError("Unknown runtime scenario")
        destination = raw / (name + ".json")
        started = time.perf_counter()
        with IsolatedJob(repo, timeout_seconds=scenario_timeout) as job:
            process = job.run([sys.executable, str(Path(__file__).resolve()), "_scenario", name,
                               "--project", str(job.root / "r"), "--output", str(destination)], phase=name)
        value = _read(destination) if destination.exists() else {"error": "scenario-output-missing"}
        process_evidence = _write(raw / (name + "-process.json"), process)
        report["samples"].append({"scenario": name, "classification": "simulation",
                                  "deadline_seconds": scenario_timeout,
                                  "elapsed_seconds": time.perf_counter() - started,
                                  "process": process, "scenario_result": value,
                                  "process_evidence": process_evidence,
                                  "evidence": {"path": str(destination),
                                               "sha256": _file_sha(destination) if destination.exists() else None}})
        write_report(output, report)
    report["recommendation"] = {"reason": "Runtime correctness and deadline checks only"}
    return _finish(repo, output, report, environment)


def _bound_json(path, digest, errors):
    try:
        if _file_sha(path) != digest:
            errors.append("Evidence digest mismatch")
            return None
        return _read(path)
    except (OSError, ValueError, TypeError):
        errors.append("Evidence unavailable")
        return None


def _result_parity(result, errors):
    if not isinstance(result, dict):
        errors.append("Result missing")
        return None
    coverage = tdq_test_manifest.reconcile_cases(result.get("manifest"), result.get("case_outcomes"),
                                                completed=result.get("details_complete"), exit_code=result.get("exit_code"))
    if result.get("status") != "PASS" or not coverage["complete"] or coverage["counts"]["pass"] == 0:
        errors.append("Result does not prove complete PASS")
    if result.get("tests_run") != len(set(coverage["observed"])):
        errors.append("Reported case count differs from actual identities")
    _check_evidence_files(result, errors)
    _check_raw_cases(result, errors)
    outcomes = sorted(result.get("case_outcomes", []), key=lambda row: row["case_id"])
    return result.get("backend"), _digest(_without_durations(outcomes))


def _without_durations(value):
    """Case, phase and subtest outcomes must match; measured durations may differ."""
    if isinstance(value, dict):
        return {key: _without_durations(item) for key, item in value.items() if key != "duration_seconds"}
    if isinstance(value, list):
        return [_without_durations(item) for item in value]
    return value


def _check_evidence_files(result, errors):
    for evidence in result.get("evidence", {}).values():
        try:
            if _file_sha(evidence["path"]) != evidence["sha256"]:
                errors.append("Raw runner evidence changed")
        except (OSError, KeyError, TypeError):
            errors.append("Raw runner evidence missing")
    if not result.get("evidence"):
        errors.append("Runner has no persisted raw evidence")


def _check_raw_cases(result, errors):
    sidecars = [entry["path"] for entry in result.get("evidence", {}).values()
                if Path(entry.get("path", "")).name == "execution.json"]
    if len(sidecars) != 1:
        errors.append("Execution sidecar missing or ambiguous")
        return
    raw = tdq_test_manifest.load_run_evidence(sidecars[0])
    for stored, reported in (("manifest", "manifest"), ("outcomes", "case_outcomes"), ("exit_code", "exit_code")):
        if raw.get(stored) != result.get(reported):
            errors.append("Result differs from raw execution cases")
    if raw.get("completed") is not True:
        errors.append("Raw execution is incomplete")
    _check_junit(result, raw, errors)


def _check_junit(result, raw, errors):
    paths = [entry["path"] for entry in result.get("evidence", {}).values()
             if Path(entry.get("path", "")).name == "execution.xml"]
    if len(paths) != 1:
        errors.append("JUnit missing or ambiguous")
        return
    inventory = list({row["case_id"].split("::")[0] for row in raw.get("outcomes", [])})
    actual = tdq_test_result.from_junit_xml(Path(paths[0]).read_text(encoding="utf-8"),
        raw.get("exit_code"), inventory, manifest=raw.get("manifest"),
        outcomes=raw.get("outcomes"), completed=raw.get("completed"))
    if actual.get("status") != "PASS" or actual.get("details_complete") is not True:
        errors.append("JUnit does not reconcile with execution sidecar")


def validate_order(rows, errors):
    """Reject overlaps, missing sample positions and a non-alternating pair order."""
    if len(rows) < 6 or len(rows) % 2:
        errors.append("At least three complete pairs are required")
        return
    expected = pair_order(len(rows) // 2)
    previous_end = -math.inf
    for index, row in enumerate(rows):
        if (row.get("pair"), row.get("workers")) != expected[index] or row.get("order") != index:
            errors.append("Pair order mismatch")
        if row.get("started_at", -math.inf) < previous_end:
            errors.append("Overlapping or reordered samples")
        if row.get("finished_at", -math.inf) <= row.get("started_at", math.inf):
            errors.append("Invalid sample timestamps")
        previous_end = row.get("finished_at", math.inf)


def _verify_full(report, errors):
    rows, parity = report["samples"], None
    validate_order(rows, errors)
    for row in rows:
        result = _bound_json(row.get("result_path"), row.get("result_sha256"), errors)
        current = _result_parity(result, errors)
        if isinstance(result, dict):
            _verify_full_binding(row, result, errors)
        if parity is not None and current != parity:
            errors.append("Case outcome parity mismatch")
        parity = current
        _verify_full_context(row, report, errors)
    first = [row["wall_seconds"] for row in rows if row.get("workers") == 1]
    second = [row["wall_seconds"] for row in rows if row.get("workers") == 2]
    return performance_summary(first, second, .2) if first and second else {}


def _verify_full_context(row, report, errors):
    if row.get("environment_sha256") != report["environment_sha256"]:
        errors.append("Benchmark environment changed")
    if row.get("source_before") != row.get("source_after") or row.get("source_before") != report["source"]["before"]:
        errors.append("Sample source changed")
    if row.get("action") != "executed" or row.get("reuse") != "off" or row.get("fresh") is not True:
        errors.append("Full benchmark must execute fresh")


def _verify_full_binding(row, result, errors):
    _verify_execution_options(row, result, errors)
    for key in ("action", "source_before", "source_after"):
        if row.get(key) != result.get(key):
            errors.append("Sample differs from persisted runner result")
    if row.get("wall_seconds") != result.get("timings", {}).get("wall_seconds"):
        errors.append("Sample wall time differs from runner measurement")
    if row.get("timings") != result.get("timings"):
        errors.append("Sample timing components differ from runner measurement")
    source = result.get("source_before", {}).get("inputs", {})
    if source.get("environment_sha256") != row.get("environment_sha256"):
        errors.append("Effective runner environment differs from sample")
    if result.get("job_classification") != "benchmark":
        errors.append("Full sample was not classified as benchmark")


def _verify_execution_options(row, result, errors):
    workers = row.get("workers")
    expected = {"schema_version": 1, "workers": workers, "reuse": "off", "fresh": True,
                "timeout_seconds": 1800}
    if type(workers) is not int or workers not in (1, 2) or result.get("run_options") != expected:
        errors.append("Requested worker/options differ from persisted runner execution")
    for phase in ("collection", "execution"):
        process = result.get("process", {}).get(phase, {})
        launch = _expected_launch(workers, phase)
        if process.get("launch_options") != launch or process.get("launch_matches_request") is not True:
            errors.append(f"{phase} actual worker launch differs from benchmark label")


def _expected_launch(workers, phase):
    collect = phase == "collection"
    count = 0 if collect or workers == 1 else workers
    return {"schema_version": 1, "backend": "pytest", "valid": True,
            "numprocesses": count, "workers": 1 if count == 0 else count,
            "dist": "no" if count == 0 else "loadfile", "collect_only": collect}


def _cache_business(value, group):
    return _business_result(value) if group == "reuse" else value.get("value")


def _verify_cache_group(group, rows, errors):
    pairs = sorted({row.get("pair") for row in rows})
    if len(pairs) < 3 or pairs != list(range(1, len(pairs) + 1)):
        errors.append("Cache group has fewer than three complete pairs")
    for pair in pairs:
        triple = [row for row in rows if row.get("pair") == pair]
        _verify_cache_triple(group, pair, triple, errors)
    return _cache_performance(rows)


def _cache_performance(rows):
    off, cold, warm = (_mode_times(rows, mode) for mode in ("off", "cold", "warm"))
    if not off or not cold or not warm:
        return {}
    summary = performance_summary(off, warm, 0)
    summary.update(baseline_mode="off", cold_median=statistics.median(cold),
                   cold_range=[min(cold), max(cold)],
                   cold_overhead_seconds=statistics.median(cold) - statistics.median(off))
    return summary


def _mode_times(rows, mode):
    return [row["wall_seconds"] for row in rows if row.get("mode") == mode and "wall_seconds" in row]


def _verify_cache_triple(group, pair, triple, errors):
    expected = ["off", "cold", "warm"] if pair % 2 else ["cold", "warm", "off"]
    if [row.get("mode") for row in triple] != expected:
        errors.append("Cache triple incomplete or reordered")
    signatures, inputs = set(), set()
    for row in triple:
        _verify_cache_row(group, row, signatures, inputs, errors)
    if len(signatures) != 1 or len(inputs) != 1:
        errors.append("Cache business/input parity mismatch")


def _verify_cache_row(group, row, signatures, inputs, errors):
    _verify_namespace(row, errors)
    value = _bound_json(row.get("raw_result_path"), row.get("raw_result_sha256"), errors)
    if value is None:
        return
    business = _cache_business(value, group)
    signature = _digest(business)
    signatures.add(signature)
    inputs.add(row.get("input_sha256"))
    if signature != row.get("business_sha256") or business != row.get("business"):
        errors.append("Cache business digest mismatch")
    expected_hit = row.get("mode") == "warm"
    if row.get("cache_hit") is not expected_hit:
        errors.append("Cache hit does not match cold/off/warm mode")
    _verify_cache_binding(group, row, value, errors)
    if group == "reuse":
        _result_parity(value, errors)
        if row.get("mode") == "warm" and value.get("action") != "reused":
            errors.append("Warm receipt was not reused")


def _verify_namespace(row, errors):
    namespace = row.get("namespace", {})
    original = {key: namespace.get(key) for key in ("request", "run", "group", "pair")}
    if namespace.get("cache_request") != "b" + _digest(original)[:16]:
        errors.append("Cache namespace digest mismatch")
    if namespace.get("group") != row.get("group") or namespace.get("pair") != row.get("pair"):
        errors.append("Cache namespace scope mismatch")


def _verify_cache_binding(group, row, value, errors):
    stats = value.get("stats", {})
    if group == "reuse":
        digest = value.get("source_before", {}).get("key")
        wall = value.get("timings", {}).get("wall_seconds")
        stats = {**value.get("timings", {}), "call_wall_seconds": wall}
    elif group == "readiness":
        digest = value.get("source", {}).get("key")
        wall = value.get("stats", {}).get("call_wall_seconds")
    else:
        digest = _digest(value.get("inputs"))
        wall = value.get("stats", {}).get("call_wall_seconds")
    if digest != row.get("input_sha256") or wall != row.get("wall_seconds"):
        errors.append("Cache input or timing binding mismatch")
    if row.get("timings") != stats:
        errors.append("Cache timing components differ from raw evidence")
    if group != "reuse" and bool(value.get("stats", {}).get("hits")) != row.get("cache_hit"):
        errors.append("Cache hit counters disagree with raw evidence")


def _verify_caches(report, errors):
    groups = {row.get("group") for row in report["samples"]}
    if not {"reuse", "readiness", "transcript-simulation"}.issubset(groups):
        errors.append("Required cache group missing")
    return {group: _verify_cache_group(group, [row for row in report["samples"] if row.get("group") == group], errors)
            for group in sorted(groups)}


def _scenario_valid(name, value, errors):
    if name in ("process-timeout", "process-cancel"):
        return _tree_valid(name, value)
    if name in ("join", "freshness"):
        return _coordination_valid(name, value, errors)
    if name == "owner-crash":
        _result_parity(value.get("result"), errors)
        return value.get("owner_exit_code") not in (None, 0) and value.get("result", {}).get("action") == "executed"
    values = value.get("business", [])
    return len(values) == 3 and values[0] == values[1] == values[2] and value.get("warm_hit") is True


def _tree_valid(name, value):
    process = value.get("process", {})
    flag = "timed_out" if name == "process-timeout" else "cancelled"
    return (process.get(flag) is True and process.get("cleanup_complete") is True
            and value.get("heartbeat_before") == value.get("heartbeat_after")
            and bool(value.get("heartbeat_before")) and value.get("ready_observed") is True)


def _coordination_valid(name, value, errors):
    results = value.get("results", [])
    signatures = [_result_parity(result, errors) for result in results]
    if len(set(signatures)) != 1:
        errors.append("Joined/reused result differs from its owner")
    actions = [result.get("action") for result in results]
    if name == "join":
        return sorted(actions) == ["executed", "joined"] and value.get("execution_count") == 1
    return actions == ["executed", "reused", "executed"]


def _verify_runtime(report, errors):
    if sorted(row.get("scenario") for row in report["samples"]) != sorted(SCENARIOS):
        errors.append("Runtime scenario inventory incomplete")
    checks = [_verify_runtime_sample(row) for row in report["samples"]]
    errors.extend(f"{check['scenario']}: {error}" for check in checks for error in check["errors"])
    return {"met": not errors, "scenario_count": len(report["samples"]), "scenarios": checks}


def _verify_runtime_sample(row):
    errors = []
    _verify_runtime_process(row, errors)
    evidence = row.get("evidence", {})
    value = _bound_json(evidence.get("path"), evidence.get("sha256"), errors)
    if value != row.get("scenario_result") or not isinstance(value, dict):
        errors.append("Scenario evidence mismatch")
    elif not _scenario_valid(row.get("scenario"), value, errors):
        errors.append("Scenario did not prove its expected behavior")
    return {"scenario": row.get("scenario"), "valid": not errors,
            "errors": errors, "facts": _runtime_facts(row)}


def _runtime_facts(row):
    value, process = row.get("scenario_result", {}), row.get("process", {})
    results = value.get("results", [])
    return {"outer_exit": process.get("exit_code"), "outer_reason": process.get("reason"),
            "outer_cleanup": process.get("cleanup_complete"), "elapsed_seconds": row.get("elapsed_seconds"),
            "ready_observed": value.get("ready_observed"),
            "heartbeat_before": value.get("heartbeat_before"), "heartbeat_after": value.get("heartbeat_after"),
            "handshake": value.get("handshake"), "execution_count": value.get("execution_count"),
            "actions": [item.get("action") for item in results],
            "statuses": [item.get("status") for item in results],
            "owner_exit_code": value.get("owner_exit_code"), "warm_hit": value.get("warm_hit"),
            "inner_reason": value.get("process", {}).get("reason"), "error": value.get("error")}


def _verify_runtime_process(row, errors):
    process = row.get("process", {})
    if not 0 < row.get("deadline_seconds", 0) <= 120 or not 0 < row.get("elapsed_seconds", math.inf) <= 120:
        errors.append("Runtime deadline exceeded")
    if process.get("exit_code") != 0 or not process.get("cleanup_complete"):
        errors.append("Scenario process did not complete safely")
    evidence = row.get("process_evidence", {})
    if process != _bound_json(evidence.get("path"), evidence.get("sha256"), errors):
        errors.append("Scenario process evidence mismatch")


def _verify_envelope(report, expected_source, errors):
    if report.get("schema") != SCHEMA or not report.get("samples"):
        errors.append("Unsupported or empty benchmark report")
    unsigned = {key: value for key, value in report.items() if key != "digest"}
    if report.get("digest") != _digest(unsigned):
        errors.append("Report digest mismatch")
    if report.get("environment_sha256") != report.get("environment_after_sha256"):
        errors.append("Benchmark host environment changed")
    _verify_source(report, expected_source, errors)
    for row in report.get("samples", []):
        if "wall_seconds" in row and (not math.isfinite(row["wall_seconds"]) or row["wall_seconds"] <= 0):
            errors.append("Invalid measured wall time")


def _verify_source(report, expected_source, errors):
    source = report.get("source", {})
    before = source.get("before", {})
    if before.get("key") != _digest(before.get("inputs", {})):
        errors.append("Source fingerprint digest mismatch")
    if report.get("source_comparison") != _comparison_policy(before):
        errors.append("Source comparison exclusions differ from exact lifecycle policy")
    if source.get("before") != source.get("after") or not source.get("before"):
        errors.append("Benchmark source changed")
    if expected_source is not None and source_identity(source.get("before", {})) != source_identity(expected_source):
        errors.append("Benchmark source differs from current Full evidence")
    if expected_source is None and source.get("before"):
        current = _source(report["project"], report["request"], {})
        if source_identity(current) != source_identity(source["before"]):
            errors.append("Benchmark source is no longer current")


def _verify_fallback(report, met, errors):
    if met:
        return
    decision = report.get("recommendation", {})
    if not decision.get("reason"):
        errors.append("Fallback reason missing")
    if report.get("kind") == "full-pairs" and decision.get("workers") != 1:
        errors.append("Unsuccessful parallel measurement must retain serial")
    if report.get("kind") == "cache-pairs":
        if decision.get("cache_modes") != {"reuse": "off", "readiness": "off", "transcript": "off"}:
            errors.append("Unsuccessful cache measurement must keep defaults off")


def verify_report(path, *, expected_source=None):
    """Read and verify evidence without executing tests or trusting reported PASS counts."""
    errors, summary = [], {}
    try:
        report = _read(path)
        _verify_envelope(report, expected_source, errors)
        validators = {"full-pairs": _verify_full, "cache-pairs": _verify_caches, "runtime-smoke": _verify_runtime}
        validator = validators.get(report.get("kind"))
        if validator is None:
            errors.append("Unknown benchmark kind")
        else:
            summary = validator(report, errors)
        met = all(value.get("met") for value in summary.values()) if report.get("kind") == "cache-pairs" else summary.get("met")
        verdict = "PERFORMANCE_MET" if met else "FALLBACK_RECORDED"
        _verify_fallback(report, met, errors)
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        errors.append("Malformed or unavailable benchmark evidence")
        verdict = "INVALID"
    return {"valid": not errors, "verdict": "INVALID" if errors else verdict,
            "errors": sorted(set(errors)), "summary": summary}


def main(argv=None):
    """Run or verify a requested bounded experiment; default caches remain off."""
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("full-pairs", "cache-pairs", "runtime-smoke", "_scenario"):
        command = sub.add_parser(name)
        command.add_argument("--project", default=os.getcwd())
        command.add_argument("--output", required=True)
        if name in ("full-pairs", "cache-pairs"):
            command.add_argument("--pairs", type=int, default=3)
        if name == "full-pairs":
            command.add_argument("--workers", nargs=2, type=int, default=[1, 2])
            command.add_argument("--reuse", choices=["off"], default="off")
        if name == "cache-pairs":
            command.add_argument("--real-transcript-manifest")
            command.add_argument("--real-transcript", action="append", default=[])
        if name == "runtime-smoke":
            command.add_argument("--scenario-timeout", type=float, default=120)
        if name == "_scenario":
            command.add_argument("scenario", choices=SCENARIOS)
    verify = sub.add_parser("verify")
    verify.add_argument("path")
    args = parser.parse_args(argv)
    try:
        return _dispatch(args)
    except (ValueError, OSError) as error:
        _log(type(error).__name__)
        return 1


def _dispatch(args):
    if args.command == "verify":
        result = verify_report(args.path)
        print(json.dumps(result))
        return 0 if result["valid"] else 1
    if args.command == "_scenario":
        artifacts = Path(args.output).parent / args.scenario
        _write(args.output, _scenario(args.scenario, Path(args.project), artifacts))
        return 0
    if args.command == "full-pairs":
        report = full_pairs(args.project, args.output, pairs=args.pairs, workers=args.workers, reuse=args.reuse)
    elif args.command == "cache-pairs":
        report = cache_pairs(args.project, args.output, pairs=args.pairs,
                              real_transcript_manifest=args.real_transcript_manifest,
                              real_transcripts=args.real_transcript)
    else:
        report = runtime_smoke(args.project, args.output, scenario_timeout=args.scenario_timeout)
    print(json.dumps(report["verification"]))
    return 0 if report["verification"]["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
