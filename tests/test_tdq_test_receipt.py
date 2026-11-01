"""Actual cache, file mutation, and process-concurrency receipt checks."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from copy import deepcopy
from contextlib import contextmanager

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import tdq_test_receipt as receipts
from tdq_test_manifest import make_manifest
from tdq_test_result import from_case_evidence


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixture(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    source = project / "test_case.py"
    source.write_text("def test_ok():\n    assert 1 + 1 == 2\n", encoding="utf-8")
    (project / "proof.py").write_text("def test_dependency():\n    assert 1 + 1 == 2\n")
    manifest = make_manifest(["test_case.py::test_ok"])
    declarations = {"schema_version": 1, "cases": {
        manifest["case_ids"][0]: {"hermetic": True, "test_source_sha256": sha(source),
        "input_paths": ["test_case.py"], "env_names": [], "external_inputs": [],
        "no_network": True, "no_live_clock": True, "no_personal_config": True,
        "proof": {"test_id": "proof.py::test_dependency", "test_path": "proof.py",
                  "source_sha256": sha(project / "proof.py")}}}}
    return project, manifest, declarations


def result_for(manifest, outcome="pass"):
    case = {"case_id": manifest["case_ids"][0], "outcome": outcome,
            "reason": "fixture", "capability": None, "subtests": [],
            "phases": [{"phase": phase, "outcome": outcome if phase == "call" else "pass",
                        "reason": "fixture", "duration_seconds": 0.001}
                       for phase in ("setup", "call", "teardown")]}
    return from_case_evidence(manifest, [case], 0 if outcome == "pass" else 1,
                              ["test_case.py"])


def test_eligible_second_call_reuses_complete_case_evidence(tmp_path):
    project, manifest, declarations = fixture(tmp_path)
    calls = []
    def execute():
        calls.append(1)
        return result_for(manifest)
    first = receipts.run_with_receipt(project, "request", manifest, execute,
                                     reuse="auto", declarations=declarations)
    saved = json.loads(Path(first["source_receipt_id"]).read_text())
    assert receipts._passed(saved["result"], manifest), saved["result"]
    fingerprint = receipts.build_fingerprint(project, "request", manifest, declarations=declarations)
    assert receipts.read_receipt(first["source_receipt_id"], fingerprint), saved
    second = receipts.run_with_receipt(project, "request", manifest, execute,
                                      reuse="auto", declarations=declarations)
    assert len(calls) == 1
    assert first["action"] == "executed"
    assert second["action"] == "reused"
    assert second["status"] == "PASS"


def run(project, manifest, declarations, execute=None, **options):
    options.setdefault("timeout_seconds", 3)
    return receipts.run_with_receipt(project, "request", manifest,
        execute or (lambda: result_for(manifest)), reuse="auto",
        declarations=declarations, environment={}, **options)


@pytest.mark.parametrize("mutation", ["source", "untracked", "docs", "config", "lock", "remove", "fixture"])
def test_content_and_file_list_invalidate(tmp_path, mutation):
    project, manifest, policy = fixture(tmp_path)
    extra = project / "input.txt"
    extra.write_text("old")
    first = run(project, manifest, policy)
    if mutation == "remove":
        extra.unlink()
    elif mutation == "source":
        (project / "test_case.py").write_text("def test_ok():\n    assert 2 + 2 == 4\n")
    else:
        target = project / {"untracked": "new.py", "docs": "docs/spec.md", "config": "config.json",
                            "lock": "requirements.lock", "fixture": "input.txt"}[mutation]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("changed")
    second = run(project, manifest, policy)
    assert second["action"] == "executed"
    assert first["source_receipt_id"] != second["source_receipt_id"]


@pytest.mark.parametrize("field", ["packages", "python", "os", "architecture", "privileged", "executable_sha256"])
def test_runtime_dimensions_invalidate(tmp_path, monkeypatch, field):
    project, manifest, policy = fixture(tmp_path)
    identity = receipts._runtime_identity()
    monkeypatch.setattr(receipts, "_runtime_identity", lambda: deepcopy(identity))
    first = receipts.build_fingerprint(project, "request", manifest, declarations=policy, environment={})
    identity[field] = "changed"
    second = receipts.build_fingerprint(project, "request", manifest, declarations=policy, environment={})
    assert first["key"] != second["key"]


@pytest.mark.parametrize("dimension", ["request", "environment", "flags", "manifest", "schema", "project"])
def test_identity_selection_flags_and_secret_env_invalidate(tmp_path, monkeypatch, dimension):
    project, manifest, policy = fixture(tmp_path)
    arguments = {"project": project, "request": "request", "manifest": manifest,
                 "declarations": policy, "environment": {"SECRET_TOKEN": "private-value"}}
    first = receipts.build_fingerprint(**arguments)
    assert "private-value" not in json.dumps(first)
    if dimension == "schema":
        monkeypatch.setattr(receipts, "SCHEMA_VERSION", 2)
    elif dimension == "project":
        alternate = tmp_path / "alternate"
        alternate.mkdir()
        arguments["project"] = alternate
    elif dimension == "manifest":
        arguments["manifest"] = {**manifest, "scope": "full"}
    else:
        arguments[dimension] = {"changed": "value"} if dimension != "request" else "another"
    second = receipts.build_fingerprint(**arguments)
    assert first["key"] != second["key"]


@pytest.mark.parametrize("bad", ["unknown_case", "proof_changed", "external", "network", "clock", "personal", "generated_input"])
def test_default_deny_dependency_envelope(tmp_path, bad):
    project, manifest, policy = fixture(tmp_path)
    declaration = policy["cases"][manifest["case_ids"][0]]
    if bad == "unknown_case":
        manifest["case_ids"].append("test_case.py::new_test")
    elif bad == "proof_changed":
        (project / "proof.py").write_text("changed")
    elif bad == "external":
        declaration["external_inputs"] = ["https://example.invalid"]
    elif bad == "generated_input":
        declaration["input_paths"] = ["docs/tdq/.tdq-test.jsonl"]
    else:
        declaration[{"network": "no_network", "clock": "no_live_clock", "personal": "no_personal_config"}[bad]] = False
    actual = run(project, manifest, policy)
    assert actual["action"] == "executed"
    assert actual["source_receipt_id"] is None
    assert actual["receipt_reason"] == "unproven_dependency_envelope"


def test_missing_policy_off_and_fresh_do_not_consult_lease(tmp_path, monkeypatch):
    project, manifest, policy = fixture(tmp_path)
    run(project, manifest, policy)
    def forbidden(*args, **kwargs):
        raise AssertionError("Cache lookup/lease forbidden")
    monkeypatch.setattr(receipts, "_claim", forbidden)
    assert run(project, manifest, policy, fresh=True)["action"] == "executed"
    assert run(project, manifest, None)["receipt_reason"] == "missing_policy"
    actual = receipts.run_with_receipt(project, "request", manifest, lambda: result_for(manifest))
    assert actual["receipt_reason"] == "reuse_off"


def test_optional_policy_file_is_usable_activation(tmp_path):
    project, manifest, policy = fixture(tmp_path)
    target = project / receipts.POLICY_PATH
    target.parent.mkdir(parents=True)
    target.write_text(json.dumps(policy))
    assert run(project, manifest, None)["action"] == "executed"
    assert run(project, manifest, None)["action"] == "reused"


@pytest.mark.parametrize("kind", ["receipt_digest", "evidence_digest", "missing_evidence", "legacy", "missing_phases", "fake_count", "missing_commit"])
def test_corrupted_or_incomplete_evidence_cannot_reuse(tmp_path, kind):
    project, manifest, policy = fixture(tmp_path)
    first = run(project, manifest, policy)
    path = Path(first["source_receipt_id"])
    receipt = json.loads(path.read_text())
    if kind == "missing_commit":
        path.with_suffix(".committed.json").unlink()
    elif kind == "receipt_digest":
        receipt["sha256"] = "fake"
    elif kind in ("missing_evidence", "evidence_digest"):
        evidence = Path(receipt["evidence"][0]["path"])
        evidence.unlink()
        if kind == "evidence_digest":
            evidence.write_text("tampered")
    elif kind == "legacy":
        receipt = {"status": "PASS"}
    else:
        if kind == "missing_phases":
            receipt["result"]["case_outcomes"][0]["phases"] = []
        else:
            receipt["result"]["tests_run"] = 999
        receipt["sha256"] = receipts._digest({k: v for k, v in receipt.items() if k != "sha256"})
        # Keep the publication binding valid to exercise semantic validation.
        path.with_suffix(".committed.json").write_text(json.dumps(
            {"nonce": receipt["nonce"], "receipt_sha256": receipt["sha256"]}))
    path.write_text(json.dumps(receipt))
    assert run(project, manifest, policy)["action"] == "executed"


def test_mid_execution_input_change_disqualifies_receipt(tmp_path):
    project, manifest, policy = fixture(tmp_path)
    def execute():
        (project / "config.json").write_text("mutation")
        return result_for(manifest)
    first = run(project, manifest, policy, execute)
    assert first["receipt_reason"] == "inputs_changed_during_execution"
    assert first["status"] == "INCOMPLETE"
    assert run(project, manifest, policy)["action"] == "executed"


@pytest.mark.parametrize("outcome", ["fail", "xpass", "skip", "xfail"])
def test_nonpass_and_all_skip_are_never_reused(tmp_path, outcome):
    project, manifest, policy = fixture(tmp_path)
    first = run(project, manifest, policy, lambda: result_for(manifest, outcome))
    assert first["status"] != "PASS"
    assert run(project, manifest, policy)["action"] == "executed"
    assert Path(first["source_receipt_id"]).is_file()


def test_fresh_failure_invalidates_older_pass(tmp_path):
    project, manifest, policy = fixture(tmp_path)
    run(project, manifest, policy)
    failed = run(project, manifest, policy, lambda: result_for(manifest, "fail"), fresh=True)
    assert failed["status"] == "FAIL"
    assert run(project, manifest, policy)["action"] == "executed"


def test_cancel_keeps_error_and_releases_own_lease(tmp_path):
    project, manifest, policy = fixture(tmp_path)
    def cancel():
        raise KeyboardInterrupt()
    actual = run(project, manifest, policy, cancel)
    assert actual["status"] == "ERROR"
    assert actual["receipt_reason"] == "cancelled"
    assert not (Path(actual["source_receipt_id"]).parent / "lease.json").exists()
    assert run(project, manifest, policy)["action"] == "executed"


def _worker(config_path, output_path, mode, delay):
    config = json.loads(Path(config_path).read_text())
    project = Path(config["project"])
    marker = project / "docs/tdq/artifacts/calls.txt"
    marker.parent.mkdir(parents=True, exist_ok=True)
    def execute():
        with marker.open("a") as stream:
            stream.write(str(os.getpid()) + "\n")
        if mode == "crash":
            os._exit(31)
        time.sleep(float(delay))
        if mode == "cancel":
            raise KeyboardInterrupt()
        return result_for(config["manifest"], mode)
    result = run(project, config["manifest"], config["policy"], execute,
                 flags=config.get("flags", {}), timeout_seconds=config.get("timeout", 10))
    Path(output_path).write_text(json.dumps(result))


def start_worker(tmp_path, project, manifest, policy, mode="pass", delay=1.0, flags=None, timeout=10):
    identifier = str(time.time_ns())
    config = tmp_path / (identifier + ".config.json")
    output = tmp_path / (identifier + ".output.json")
    config.write_text(json.dumps({"project": str(project), "manifest": manifest,
                                 "policy": policy, "flags": flags or {}, "timeout": timeout}))
    process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--worker",
                                str(config), str(output), mode, str(delay)],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return process, output


def wait_started(project):
    marker = project / "docs/tdq/artifacts/calls.txt"
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        if marker.exists() and marker.stat().st_size:
            return marker
        time.sleep(0.02)
    raise AssertionError("Owner did not begin execution")


@pytest.mark.parametrize("outcome", ["pass", "fail", "cancel"])
def test_two_real_callers_join_one_execution_preserve_verdict(tmp_path, outcome):
    project, manifest, policy = fixture(tmp_path)
    owner, first = start_worker(tmp_path, project, manifest, policy, outcome, 1.5)
    marker = wait_started(project)
    waiter, second = start_worker(tmp_path, project, manifest, policy, outcome)
    assert owner.wait(timeout=10) == 0
    assert waiter.wait(timeout=10) == 0
    a, b = json.loads(first.read_text()), json.loads(second.read_text())
    assert a["action"] == "executed" and b["action"] == "joined"
    assert a["status"] == b["status"] == ("ERROR" if outcome == "cancel" else outcome.upper())
    assert len(marker.read_text().splitlines()) == 1
    assert b["timings"]["execute_seconds"] == 0
    assert b["timings"]["wait_seconds"] > 0


def test_crashed_owner_is_recovered_after_confirmed_death(tmp_path):
    project, manifest, policy = fixture(tmp_path)
    owner, _ = start_worker(tmp_path, project, manifest, policy, "crash")
    marker = wait_started(project)
    assert owner.wait(timeout=10) == 31
    actual = run(project, manifest, policy)
    assert actual["action"] == "executed" and actual["status"] == "PASS"
    assert list(Path(actual["source_receipt_id"]).parent.glob("*.abandoned.json"))
    assert len(marker.read_text().splitlines()) == 1


def test_live_owner_timeout_does_not_steal_or_kill(tmp_path):
    project, manifest, policy = fixture(tmp_path)
    owner, output = start_worker(tmp_path, project, manifest, policy, delay=1.5)
    wait_started(project)
    start = time.monotonic()
    actual = run(project, manifest, policy, timeout_seconds=0.3)
    assert actual["status"] == "INCOMPLETE" and actual["action"] == "joined"
    assert time.monotonic() - start < 1
    assert owner.poll() is None
    assert owner.wait(timeout=10) == 0
    assert json.loads(output.read_text())["status"] == "PASS"


def test_different_worker_flags_do_not_join(tmp_path):
    project, manifest, policy = fixture(tmp_path)
    owner, _ = start_worker(tmp_path, project, manifest, policy, delay=1, flags={"workers": 1})
    wait_started(project)
    actual = run(project, manifest, policy, flags={"workers": 2})
    assert actual["action"] == "executed"
    assert owner.wait(timeout=10) == 0


def test_expired_timestamp_alone_cannot_steal_live_lease(tmp_path):
    project, manifest, policy = fixture(tmp_path)
    owner, output = start_worker(tmp_path, project, manifest, policy, delay=1.5)
    wait_started(project)
    lease = next((project / receipts.CACHE_PATH).rglob("lease.json"))
    content = json.loads(lease.read_text())
    # Inspect age semantics without changing the owner's immutable nonce/start record.
    content["claimed"] = 0
    assert not receipts._owner_dead(content)
    assert owner.wait(timeout=10) == 0
    assert json.loads(output.read_text())["status"] == "PASS"


def test_logs_are_timestamped_and_switchable_without_secret(tmp_path, capsys, monkeypatch):
    project, manifest, policy = fixture(tmp_path)
    run(project, manifest, policy)
    output = capsys.readouterr().err
    assert "receipt action=executed" in output and "T" in output
    monkeypatch.setenv("TDQ_LOG", "0")
    run(project, manifest, policy)
    assert capsys.readouterr().err == ""


def test_own_outputs_do_not_invalidate_inputs(tmp_path):
    project, manifest, policy = fixture(tmp_path)
    first = run(project, manifest, policy)
    ledger = project / "docs/tdq/.tdq-test.jsonl"
    ledger.write_text('{"result":"old"}\n')
    artifact = project / "docs/tdq/artifacts/output.json"
    artifact.parent.mkdir(parents=True)
    artifact.write_text('{}')
    second = run(project, manifest, policy)
    assert second["action"] == "reused"
    assert first["source_receipt_id"] == second["source_receipt_id"]


@pytest.mark.parametrize("corruption", ["partial_json", "malformed", "unknown_owner"])
def test_unverifiable_lease_is_not_overwritten(tmp_path, monkeypatch, corruption):
    project, manifest, policy = fixture(tmp_path)
    before = receipts.build_fingerprint(project, "request", manifest, declarations=policy, environment={})
    namespace = receipts._namespace(project, "request", None)
    directory = namespace / before["key"][:32]
    directory.mkdir(parents=True)
    lease = directory / "lease.json"
    payload = {"pid": os.getpid(), "start": "unknown", "nonce": "a" * 32,
               "key": before["key"], "claimed": 0}
    if corruption == "unknown_owner":
        monkeypatch.setattr(receipts, "_process_identity", lambda pid: "unknown")
    text = '{"pid":' if corruption == "partial_json" else json.dumps([] if corruption == "malformed" else payload)
    lease.write_text(text)
    def forbidden():
        raise AssertionError("Unverified owner lease must not execute")
    actual = run(project, manifest, policy, forbidden, timeout_seconds=0.2)
    assert actual["status"] == "INCOMPLETE"
    assert lease.read_text() == text


def test_deleted_external_evidence_is_a_miss(tmp_path):
    project, manifest, policy = fixture(tmp_path)
    external = tmp_path / "external-evidence.json"
    external.write_text('{"actual":"fixture"}')
    def execute():
        return {**result_for(manifest), "evidence_paths": [str(external)]}
    first = run(project, manifest, policy, execute)
    assert first["status"] == "PASS"
    external.unlink()
    assert run(project, manifest, policy)["action"] == "executed"


def test_evidence_capture_failure_preserves_error_and_unlocks(tmp_path):
    project, manifest, policy = fixture(tmp_path)
    actual = run(project, manifest, policy,
                 lambda: {**result_for(manifest), "evidence_paths": [str(tmp_path / "missing")]})
    assert actual["status"] == "ERROR"
    assert not (Path(actual["source_receipt_id"]).parent / "lease.json").exists()


def test_flags_values_are_not_written_as_plaintext(tmp_path):
    project, manifest, policy = fixture(tmp_path)
    actual = run(project, manifest, policy, flags={"api_key": "private-credential"})
    assert "private-credential" not in Path(actual["source_receipt_id"]).read_text()


def test_warm_lookup_rechecks_inputs_after_receipt_validation(tmp_path, monkeypatch):
    project, manifest, policy = fixture(tmp_path)
    calls = []
    def execute():
        calls.append(1)
        return result_for(manifest)
    run(project, manifest, policy, execute)
    original = receipts._latest
    def mutate_after_lookup(*args):
        actual = original(*args)
        (project / "config.json").write_text("changed during lookup")
        return actual
    monkeypatch.setattr(receipts, "_latest", mutate_after_lookup)
    result = run(project, manifest, policy, execute)
    assert result["status"] == "INCOMPLETE"
    assert result["source_receipt_id"] is None
    assert len(calls) == 1


@pytest.mark.parametrize("mutation", ["file", "environment", "manifest"])
@pytest.mark.parametrize("outcome", ["pass", "fail"])
def test_real_join_rechecks_inputs_before_returning_owner_pass(tmp_path, monkeypatch, mutation, outcome):
    project, manifest, policy = fixture(tmp_path)
    owner, output = start_worker(tmp_path, project, manifest, policy, mode=outcome, delay=1)
    wait_started(project)
    environment = {}
    original = receipts._join
    def mutate_after_join(*args):
        result = original(*args)
        assert result[0]["status"] == outcome.upper()
        if mutation == "file":
            (project / "config.json").write_text("changed after owner completion")
        elif mutation == "environment":
            environment["TDQ_REQUEST"] = "changed request environment"
        else:
            manifest["scope"] = "full"
        return result
    monkeypatch.setattr(receipts, "_join", mutate_after_join)
    def forbidden():
        raise AssertionError("Joined caller must never execute a retry")
    actual = receipts.run_with_receipt(project, "request", manifest, forbidden,
        reuse="auto", declarations=policy, environment=environment, timeout_seconds=4)
    assert actual["status"] == ("FAIL" if outcome == "fail" else "INCOMPLETE")
    assert actual["source_receipt_id"] is None
    assert actual["action"] == "joined"
    assert owner.wait(timeout=5) == 0
    assert json.loads(output.read_text())["status"] == outcome.upper()


def test_owner_input_mutation_preserves_known_failure(tmp_path):
    project, manifest, policy = fixture(tmp_path)
    def execute():
        (project / "config.json").write_text("changed")
        return result_for(manifest, "fail")
    actual = run(project, manifest, policy, execute)
    assert actual["status"] == "FAIL"
    assert actual["failures"]
    assert actual["details_complete"] is False


@pytest.mark.parametrize("timeout", [float("nan"), float("inf"), float("-inf"), 0, -1, True, None, "1"])
@pytest.mark.parametrize("reuse,fresh", [("off", False), ("auto", False), ("off", True)])
def test_invalid_deadline_rejected_before_hash_lock_or_callback(tmp_path, monkeypatch, timeout, reuse, fresh):
    def forbidden(*args, **kwargs):
        raise AssertionError("Invalid deadline reached work")
    monkeypatch.setattr(receipts, "check_eligibility", forbidden)
    monkeypatch.setattr(receipts, "build_fingerprint", forbidden)
    monkeypatch.setattr(receipts, "_namespace", forbidden)
    with pytest.raises(ValueError):
        receipts.run_with_receipt(tmp_path, "request", {}, forbidden,
                                  reuse=reuse, fresh=fresh, timeout_seconds=timeout)


@pytest.mark.parametrize("outcome", ["pass", "fail", "error"])
@pytest.mark.parametrize("stage", ["hash", "capture", "publish"])
def test_finalize_fault_preserves_case_and_process_provenance(tmp_path, monkeypatch, outcome, stage):
    project, manifest, policy = fixture(tmp_path)
    original = result_for(manifest, outcome)
    original["process"] = {"execution": {"pid": 123, "reason": "exited"}}
    def broken(*args, **kwargs):
        raise OSError("storage unavailable")
    def execute():
        target = {"hash": "build_fingerprint", "capture": "_capture_evidence", "publish": "_publish"}[stage]
        monkeypatch.setattr(receipts, target, broken)
        return deepcopy(original)
    actual = run(project, manifest, policy, execute)
    assert actual["status"] == ("ERROR" if outcome == "pass" else outcome.upper())
    for key in ("failures", "failed_modules", "case_outcomes", "process", "manifest"):
        assert actual[key] == original[key]
    assert actual["details_complete"] is False
    assert actual["coverage"]["complete"] is False
    assert actual["evidence_error"]
    assert not list((project / receipts.CACHE_PATH).rglob("lease.json"))


def test_join_cannot_read_terminal_pass_before_commit_marker(tmp_path, monkeypatch):
    project, manifest, policy = fixture(tmp_path)
    fingerprint = receipts.build_fingerprint(project, "request", manifest, declarations=policy, environment={})
    original = receipts._write_json
    observed = []
    def inspect_write(path, value):
        original(path, value)
        if isinstance(value, dict) and value.get("terminal") is True:
            observed.append(receipts.read_receipt(path, fingerprint, allow_failure=True))
    monkeypatch.setattr(receipts, "_write_json", inspect_write)
    actual = run(project, manifest, policy)
    assert observed == [None]
    assert receipts.read_receipt(actual["source_receipt_id"], fingerprint)


def test_fresh_off_failure_revokes_old_pass(tmp_path):
    project, manifest, policy = fixture(tmp_path)
    run(project, manifest, policy)
    failed = receipts.run_with_receipt(project, "request", manifest,
        lambda: result_for(manifest, "fail"), fresh=True, reuse="off", environment={})
    assert failed["status"] == "FAIL"
    assert run(project, manifest, policy)["action"] == "executed"


def test_fresh_invalidation_fault_blocks_before_callback(tmp_path, monkeypatch):
    project, manifest, policy = fixture(tmp_path)
    run(project, manifest, policy)
    def broken(*args):
        raise OSError("cannot write invalidation")
    monkeypatch.setattr(receipts, "_invalidate", broken)
    called = []
    with pytest.raises(OSError, match="invalidation_failed"):
        run(project, manifest, policy, lambda: called.append(1), fresh=True)
    assert called == []


def test_fresh_without_previous_namespace_does_not_write_unneeded_fence(tmp_path, monkeypatch):
    project, manifest, policy = fixture(tmp_path)
    def forbidden(*args):
        raise AssertionError("No prior receipt to fence")
    monkeypatch.setattr(receipts, "_invalidate", forbidden)
    assert run(project, manifest, policy, fresh=True)["status"] == "PASS"


@pytest.mark.parametrize("fault", ["latest.json", "commit"])
def test_partial_publication_fault_never_exposes_pass(tmp_path, monkeypatch, fault):
    project, manifest, policy = fixture(tmp_path)
    before = receipts.build_fingerprint(project, "request", manifest, declarations=policy, environment={})
    original = receipts._write_json
    prepared = []
    def broken(path, value):
        if path.name == fault or (fault == "commit" and path.name.endswith(".committed.json")):
            raise OSError("publication unavailable")
        original(path, value)
        if isinstance(value, dict) and value.get("terminal"):
            prepared.append(path)
    monkeypatch.setattr(receipts, "_write_json", broken)
    result = run(project, manifest, policy)
    assert result["status"] == "ERROR"
    assert result["source_receipt_id"] is None
    assert prepared
    assert all(receipts.read_receipt(path, before, allow_failure=True) is None for path in prepared)


def test_release_error_after_commit_keeps_same_terminal_verdict(tmp_path, monkeypatch):
    project, manifest, policy = fixture(tmp_path)
    original = receipts._mutex
    @contextmanager
    def release_error(directory, deadline):
        with original(directory, deadline):
            yield
        if list(directory.glob("*.committed.json")):
            raise OSError("mutex release reported late failure")
    monkeypatch.setattr(receipts, "_mutex", release_error)
    result = run(project, manifest, policy)
    assert result["status"] == "PASS"
    before = receipts.build_fingerprint(project, "request", manifest, declarations=policy, environment={})
    saved = receipts.read_receipt(result["source_receipt_id"], before)
    assert saved["result"]["status"] == result["status"]
    assert result["receipt_reason"] == "cache_miss"


def test_external_project_fingerprint_binds_validator_implementation(tmp_path, monkeypatch):
    project, manifest, policy = fixture(tmp_path)
    identity = {"tdq_test_receipt.py": "implementation-v1"}
    monkeypatch.setattr(receipts, "_implementation_identity", lambda: dict(identity), raising=False)
    first = receipts.build_fingerprint(project, "request", manifest, declarations=policy, environment={})
    assert "scripts/tdq_test_receipt.py" not in first["inputs"]["files"]
    identity["tdq_test_receipt.py"] = "implementation-v2"
    second = receipts.build_fingerprint(project, "request", manifest, declarations=policy, environment={})
    assert first["key"] != second["key"]


def test_implementation_identity_hashes_loaded_receipt_and_direct_dependencies():
    actual = receipts._implementation_identity()
    assert set(actual) == {"tdq_test_receipt.py", "tdq_test_manifest.py", "tdq_test_result.py"}
    for record in actual.values():
        assert sha(Path(record["path"])) == record["sha256"]


def test_nested_claude_worktree_is_generated_but_project_settings_are_inputs(tmp_path):
    project, manifest, policy = fixture(tmp_path)
    nested = project / ".claude/worktrees/agent/test_copy.py"
    nested.parent.mkdir(parents=True)
    nested.write_text("copy = 1")
    settings = project / ".claude/settings.json"
    settings.write_text('{"configured":1}')
    first = receipts.build_fingerprint(project, "request", manifest, declarations=policy, environment={})
    nested.write_text("copy = 2")
    second = receipts.build_fingerprint(project, "request", manifest, declarations=policy, environment={})
    assert first == second
    settings.write_text('{"configured":2}')
    third = receipts.build_fingerprint(project, "request", manifest, declarations=policy, environment={})
    assert second["key"] != third["key"]
    policy["cases"][manifest["case_ids"][0]]["input_paths"] = [".claude/worktrees/agent/test_copy.py"]
    assert receipts.check_eligibility(project, manifest, policy)[0] is False


if __name__ == "__main__" and sys.argv[1:2] == ["--worker"]:
    _worker(*sys.argv[2:])
