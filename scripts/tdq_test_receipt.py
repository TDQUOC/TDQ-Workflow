"""Opt-in receipts: explicit dependency declarations, bounded join, no inferred safety.

Hashes detect corruption, not an attacker able to rewrite project evidence.
The executor owns process isolation and timeout; this module bounds coordination.
"""
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import re
import sys
import time
import uuid

from tdq_test_manifest import reconcile_cases
from tdq_test_result import empty_result
import tdq_test_manifest
import tdq_test_result

SCHEMA_VERSION = 1
POLICY_PATH = Path("docs/tdq/reuse-policy.json")
CACHE_PATH = Path("docs/tdq/cache")
EXCLUDED_DIRS = {".git", ".venv", ".venv-tokens", "node_modules", "__pycache__",
                 ".pytest_cache", ".tdq-worktrees"}
# Nested agent checkouts are generated independent worktrees, not project inputs.
# Keep .claude/settings.json and all other project configuration in the envelope.
GENERATED_PREFIXES = ("docs/tdq/", ".claude/worktrees/", "docs/workinglog/", "docs/working-log/")
GENERATED_FILES = {"docs/architecture/status.json"}


def _log(reason, action):
    if os.environ.get("TDQ_LOG", "1").lower() not in {"0", "false", "off"}:
        print(f"[{datetime.now(timezone.utc).isoformat()}] receipt "
              f"action={action} reason={reason}", file=sys.stderr)


def _digest(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _write_json(path, value):
    temporary = path.with_name("." + uuid.uuid4().hex + ".tmp")
    try:
        temporary.write_text(json.dumps(value, sort_keys=True, allow_nan=False), encoding="utf-8")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _file_digest(path):
    if path.is_symlink():
        raise ValueError("Symbolic inputs require an explicit external envelope")
    before = path.stat()
    result = hashlib.sha256(path.read_bytes()).hexdigest()
    after = path.stat()
    fields = ("st_ino", "st_dev", "st_size", "st_mtime_ns", "st_ctime_ns")
    if any(getattr(before, field) != getattr(after, field) for field in fields):
        raise ValueError("Input changed while hashing")
    return result


def _excluded(relative):
    return (relative.startswith(GENERATED_PREFIXES) or relative in GENERATED_FILES
            or any(part in EXCLUDED_DIRS for part in Path(relative).parts))


def _input_path(project, relative):
    if not isinstance(relative, str) or not relative:
        raise ValueError("Input path is missing")
    path = project / relative
    if not path.resolve().is_relative_to(project) or Path(relative).is_absolute():
        raise ValueError("Input is outside the declared project")
    if _excluded(path.relative_to(project).as_posix()):
        raise ValueError("Generated or dependency-directory input is not reusable")
    if not path.is_file():
        raise ValueError("Declared input is missing")
    return path


def _policy(project, declarations):
    return _read_json(project / POLICY_PATH) if declarations is None else deepcopy(declarations)


def _check_declaration(project, case_id, declaration):
    required = ("hermetic", "no_network", "no_live_clock", "no_personal_config")
    if not isinstance(declaration, dict) or not all(declaration.get(k) is True for k in required):
        raise ValueError("Case lacks a hermetic dependency declaration")
    if declaration.get("external_inputs") != []:
        raise ValueError("Unknown external inputs")
    source = _input_path(project, case_id.partition("::")[0])
    if _file_digest(source) != declaration.get("test_source_sha256"):
        raise ValueError("Case source no longer matches declaration")
    _check_declared_inputs(project, declaration)
    proof = declaration.get("proof", {})
    path = _input_path(project, proof.get("test_path"))
    if not isinstance(proof.get("test_id"), str) or "::" not in proof["test_id"]:
        raise ValueError("Dependency proof test ID is missing")
    if proof["test_id"].partition("::")[0] != proof["test_path"]:
        raise ValueError("Dependency proof ID and path differ")
    if _file_digest(path) != proof.get("source_sha256"):
        raise ValueError("Dependency proof changed")


def _check_declared_inputs(project, declaration):
    paths = declaration.get("input_paths")
    names = declaration.get("env_names")
    if not isinstance(paths, list) or not paths:
        raise ValueError("Input dependency envelope is empty")
    for name in paths:
        _file_digest(_input_path(project, name))
    if not isinstance(names, list) or not all(isinstance(n, str) for n in names):
        raise ValueError("Environment dependency envelope is malformed")


def check_eligibility(project, manifest, declarations=None):
    """Default-deny any unknown case, stale declaration or external dependency."""
    project = Path(project).resolve()
    policy = _policy(project, declarations)
    if not isinstance(policy, dict) or policy.get("schema_version") != 1:
        return False, "missing_policy"
    identifiers = manifest.get("case_ids", [])
    if not manifest.get("complete") or not identifiers or len(set(identifiers)) != len(identifiers):
        return False, "incomplete_manifest"
    try:
        for case_id in identifiers:
            _check_declaration(project, case_id, policy.get("cases", {}).get(case_id))
    except (OSError, ValueError, TypeError, AttributeError):
        return False, "unproven_dependency_envelope"
    return True, "declared_hermetic_scope"


def _source_files(project):
    files = {}
    for folder, directories, names in os.walk(project, followlinks=False):
        directories[:] = sorted(d for d in directories
                                if not _excluded((Path(folder) / d).relative_to(project).as_posix() + "/"))
        for name in sorted(names):
            path = Path(folder) / name
            relative = path.relative_to(project).as_posix()
            if not _excluded(relative):
                files[relative] = _file_digest(path)
    return files


def _privilege():
    if os.name == "nt":
        import ctypes
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    return os.geteuid() == 0


def _runtime_identity():
    packages = sorted((item.metadata.get("Name", ""), item.version)
                      for item in importlib.metadata.distributions())
    return {"python": sys.version, "executable": str(Path(sys.executable).resolve()),
            "executable_sha256": _file_digest(Path(sys.executable)),
            "os": platform.platform(), "architecture": platform.machine(),
            "privileged": _privilege(), "packages": packages}


def _implementation_identity():
    paths = [Path(__file__), Path(tdq_test_manifest.__file__), Path(tdq_test_result.__file__)]
    return {path.name: {"path": str(path.resolve()), "sha256": _file_digest(path)} for path in paths}


def build_fingerprint(project, request, manifest, *, flags=None, declarations=None,
                      environment=None):
    """Hash content, inventory, dependencies and environment without storing secrets."""
    project = Path(project).resolve()
    policy = _policy(project, declarations)
    env = os.environ if environment is None else environment
    inputs = {"schema_version": SCHEMA_VERSION, "project": str(project), "request": request,
              "files": _source_files(project), "runtime": _runtime_identity(),
              "implementation": _implementation_identity(),
              "manifest": manifest, "flags_sha256": _digest(flags or {}), "policy_sha256": _digest(policy),
              "environment_sha256": _digest(dict(env))}
    inputs = json.loads(json.dumps(inputs, allow_nan=False))
    return {"key": _digest(inputs), "inputs": inputs}


def _windows_identity(pid):
    import ctypes
    from ctypes import wintypes
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    kernel.GetProcessTimes.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4
    handle = kernel.OpenProcess(0x1000, False, pid)
    if not handle:
        return None if ctypes.get_last_error() in (87, 1168) else "unknown"
    try:
        exit_code = wintypes.DWORD()
        if not kernel.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
            return "unknown"
        if exit_code.value != 259:
            return None
        values = [wintypes.FILETIME() for _ in range(4)]
        if not kernel.GetProcessTimes(handle, *(ctypes.byref(value) for value in values)):
            return "unknown"
        return str(values[0].dwHighDateTime << 32 | values[0].dwLowDateTime)
    finally:
        kernel.CloseHandle(handle)


def _process_identity(pid):
    if type(pid) is not int or pid <= 0:
        return "unknown"
    if os.name == "nt":
        return _windows_identity(pid)
    try:
        stat = Path(f"/proc/{pid}/stat").read_text()
        return stat.rsplit(")", 1)[1].split()[19]
    except FileNotFoundError:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return None
        except PermissionError:
            return "unknown"
        return "unknown"
    except (OSError, IndexError):
        return "unknown"


def _owner_dead(owner):
    identity = _process_identity(owner.get("pid"))
    return identity is None or (identity != "unknown" and identity != owner.get("start"))


@contextmanager
def _mutex(directory, deadline):
    with (directory / "guard.lock").open("a+b") as stream:
        if stream.tell() == 0:
            stream.write(b"0")
            stream.flush()
        while True:
            try:
                _lock(stream, False)
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise TimeoutError("Receipt mutex deadline exceeded") from None
                time.sleep(0.02)
        try:
            yield
        finally:
            _lock(stream, True)


def _lock(stream, unlock):
    stream.seek(0)
    if os.name == "nt":
        import msvcrt
        msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK if unlock else msvcrt.LK_NBLCK, 1)
    else:
        import fcntl
        fcntl.flock(stream, fcntl.LOCK_UN if unlock else fcntl.LOCK_EX | fcntl.LOCK_NB)


def _namespace(project, request, cache_dir):
    allowed = project / CACHE_PATH
    root = allowed if cache_dir is None else Path(cache_dir).resolve()
    if not root.is_relative_to(allowed):
        raise ValueError("Receipt cache must remain under project docs/tdq/cache")
    namespace = root / ("r-" + _digest({"project": str(project), "request": request})[:16])
    if os.name == "nt" and not str(namespace).startswith("\\\\?\\"):
        return Path("\\\\?\\" + str(namespace))
    return namespace


def _pass_header(result, manifest):
    if not isinstance(result, dict) or result.get("manifest") != manifest:
        return False
    if result.get("status") != "PASS" or result.get("details_complete") is not True:
        return False
    if type(result.get("exit_code")) is not int or result["exit_code"] != 0:
        return False
    if result.get("failures") or result.get("unmapped_failures"):
        return False
    return True


def _passed(result, manifest):
    if not _pass_header(result, manifest):
        return False
    coverage = reconcile_cases(manifest, result.get("case_outcomes"), completed=True,
                               exit_code=result["exit_code"])
    counts = coverage["counts"]
    return (coverage["complete"] and counts["pass"] > 0
            and result.get("coverage") == coverage
            and result.get("tests_run") == len(coverage["observed"])
            and not any(counts[k] for k in ("fail", "error", "xpass")))


def read_receipt(path, fingerprint, *, allow_failure=False, nonce=None):
    """Validate terminal proof and content digests; legacy or corrupt means miss."""
    receipt = _read_json(Path(path))
    commit = _read_json(Path(path).with_suffix(".committed.json"))
    if not isinstance(receipt, dict) or commit != {"nonce": receipt.get("nonce"),
                                                   "receipt_sha256": receipt.get("sha256")}:
        return None
    try:
        return _check_receipt(receipt, fingerprint, allow_failure, nonce)
    except (ValueError, TypeError, KeyError):
        return None


def _receipt_envelope(receipt, fingerprint, nonce):
    if not isinstance(receipt, dict) or receipt.get("schema_version") != SCHEMA_VERSION:
        return False
    signature = receipt.get("sha256")
    unsigned = {key: value for key, value in receipt.items() if key != "sha256"}
    if signature != _digest(unsigned) or receipt.get("key") != fingerprint["key"]:
        return False
    if receipt.get("terminal") is not True or (nonce and receipt.get("nonce") != nonce):
        return False
    if receipt.get("before") != fingerprint:
        return False
    return True


def _check_receipt(receipt, fingerprint, allow_failure, nonce):
    if not _receipt_envelope(receipt, fingerprint, nonce):
        return None
    if not _valid_evidence(receipt.get("evidence")):
        return None
    result = receipt.get("result")
    if not _valid_terminal_result(result, fingerprint["inputs"]["manifest"], allow_failure):
        return None
    if receipt.get("after") != fingerprint and (not allow_failure or result["status"] == "PASS"):
        return None
    cases = _read_json(Path(receipt["evidence"][0]["path"]))
    if cases != {"manifest": result.get("manifest"), "case_outcomes": result.get("case_outcomes")}:
        return None
    return receipt


def _valid_terminal_result(result, manifest, allow_failure):
    if not isinstance(result, dict):
        return False
    if result.get("status") == "PASS" or not allow_failure:
        return _passed(result, manifest)
    return result.get("status") in {"FAIL", "ERROR", "INCOMPLETE", "SKIP"}


def _valid_evidence(evidence):
    if not isinstance(evidence, list) or not evidence:
        return False
    try:
        return all(_file_digest(Path(item["path"])) == item["sha256"] for item in evidence)
    except (OSError, ValueError, KeyError, TypeError):
        return False


def _decorate(result, action, reason, receipt_path, verify, wait, execute):
    output = deepcopy(result)
    output.update(action=action, source_receipt_id=str(receipt_path) if receipt_path else None,
                  receipt_reason=reason)
    output["timings"] = {"verify_seconds": verify, "wait_seconds": wait,
                         "execute_seconds": execute}
    _log(reason, action)
    return output


def _execute_direct(execute, reason, verify=0):
    started = time.monotonic()
    result = execute()
    return _decorate(result, "executed", reason, None, verify, 0, time.monotonic() - started)


def _invalidated(namespace, receipt):
    marker = _read_json(namespace / "invalidated.json")
    if not (namespace / "invalidated.json").exists():
        return False
    if not isinstance(marker, dict) or not isinstance(marker.get("at"), (int, float)):
        return True
    return receipt["started"] <= marker["at"]


def _invalidate(namespace, reason):
    namespace.mkdir(parents=True, exist_ok=True)
    _write_json(namespace / "invalidated.json", {"at": time.time(), "reason": reason})


def _fresh(execute, namespace, manifest):
    # Fence old proofs before executing: a failed write must never leave a new
    # known failure hidden behind an older reusable PASS in another process.
    if namespace.exists():
        try:
            _invalidate(namespace, "fresh_requested")
        except (OSError, ValueError, TypeError) as error:
            raise OSError("invalidation_failed: " + type(error).__name__) from error
    return _execute_direct(execute, "fresh")


def _latest(directory, namespace, fingerprint):
    latest = _read_json(directory / "latest.json")
    if isinstance(latest, dict) and _valid_nonce(latest.get("nonce")):
        path = directory / (latest["nonce"] + ".json")
        receipt = read_receipt(path, fingerprint)
        if receipt and not _invalidated(namespace, receipt):
            return "reused", receipt, path
    return None


def _existing_lease(directory, fingerprint):
    path = directory / "lease.json"
    if not path.exists():
        return None
    lease = _read_json(path)
    if not isinstance(lease, dict) or not _valid_nonce(lease.get("nonce")):
        return "joined", None, None
    if lease.get("key") != fingerprint["key"]:
        return "unknown", None, None
    if not _owner_dead(lease):
        return "joined", lease, None
    _write_json(directory / (lease["nonce"] + ".abandoned.json"), lease)
    return None


def _claim(directory, namespace, fingerprint, deadline):
    with _mutex(directory, deadline):
        existing = _latest(directory, namespace, fingerprint) or _existing_lease(directory, fingerprint)
        if existing:
            return existing
        owner = {"pid": os.getpid(), "start": _process_identity(os.getpid()),
                 "nonce": uuid.uuid4().hex, "claimed": time.time(), "key": fingerprint["key"]}
        if owner["start"] in (None, "unknown"):
            return "unknown", None, None
        _write_json(directory / "lease.json", owner)
        return "owner", owner, None


def _valid_nonce(value):
    return isinstance(value, str) and re.fullmatch("[0-9a-f]{32}", value) is not None


def _join(directory, owner, fingerprint, deadline):
    if not isinstance(owner, dict) or not isinstance(owner.get("nonce"), str):
        return empty_result("receipt", "Lease owner cannot be verified"), None
    path = directory / (owner["nonce"] + ".json")
    while time.monotonic() < deadline:
        receipt = read_receipt(path, fingerprint, allow_failure=True, nonce=owner["nonce"])
        if receipt:
            return receipt["result"], path
        if _owner_dead(owner):
            return empty_result("receipt", "Owner died while caller was joined"), None
        time.sleep(min(0.05, max(0, deadline - time.monotonic())))
    return empty_result("receipt", "Join deadline exceeded"), None


def _capture_evidence(directory, nonce, result):
    path = directory / (nonce + ".cases.json")
    _write_json(path, {"manifest": result.get("manifest"),
                       "case_outcomes": result.get("case_outcomes")})
    paths = [path] + [Path(item) for item in result.get("evidence_paths", [])]
    return [{"path": str(item.resolve()), "sha256": _file_digest(item)} for item in paths]


def _publish(directory, owner, before, after, result, evidence, started, deadline):
    receipt = {"schema_version": SCHEMA_VERSION, "terminal": True, "key": before["key"],
               "nonce": owner["nonce"], "owner": owner, "started": started,
               "finished": time.time(), "before": before, "after": after,
               "result": result, "evidence": evidence}
    receipt["sha256"] = _digest(receipt)
    path = directory / (owner["nonce"] + ".json")
    with _mutex(directory, max(deadline, time.monotonic() + 5)):
        lease = _read_json(directory / "lease.json")
        if lease != owner:
            raise RuntimeError("Lease ownership changed; refusing publication")
        _write_json(path, receipt)
        _write_json(directory / "latest.json", {"nonce": owner["nonce"]})
        (directory / "lease.json").unlink()
        # No reader may treat a prepared receipt as terminal before publication
        # and lease cleanup finish. This marker is the final state mutation.
        _write_json(path.with_suffix(".committed.json"),
                    {"nonce": owner["nonce"], "receipt_sha256": receipt["sha256"]})
    return path


def _proof_error(result, error):
    output = deepcopy(result)
    if output.get("status") not in {"FAIL", "ERROR"}:
        output["status"] = "ERROR"
    reason = "Evidence finalization raised " + type(error).__name__
    output["reason"] = output.get("reason", "") + "; " + reason
    output.update(details_complete=False, evidence_complete=False, evidence_error=reason)
    if isinstance(output.get("coverage"), dict):
        output["coverage"]["complete"] = False
        output["coverage"].setdefault("diagnostics", []).append(reason)
    return output


def _release_owned_lease(context, owner):
    try:
        with _mutex(context["directory"], time.monotonic() + 1):
            lease = context["directory"] / "lease.json"
            if _read_json(lease) == owner:
                lease.unlink()
    except (OSError, ValueError):
        _log("owned_lease_cleanup_unavailable", "executed")


def _finalization_failure(context, owner, result, error, started):
    path = context["directory"] / (owner["nonce"] + ".json")
    committed = read_receipt(path, context["before"], allow_failure=True, nonce=owner["nonce"])
    if committed:
        # For example, unlocking the mutex may fail after the marker is durable.
        # All readers and the owner must keep the already committed verdict.
        return committed["result"], path, committed["after"]
    result = _proof_error(result, error)
    try:
        _invalidate(context["namespace"], "owner_evidence_incomplete")
        minimal = dict(result, evidence_paths=[])
        evidence = _capture_evidence(context["directory"], owner["nonce"], minimal)
        path = _publish(context["directory"], owner, context["before"], None,
                        result, evidence, started, context["deadline"])
        return result, path, None
    except (OSError, ValueError, TypeError, RuntimeError):
        committed = read_receipt(path, context["before"], allow_failure=True, nonce=owner["nonce"])
        if committed:
            return committed["result"], path, committed["after"]
        _release_owned_lease(context, owner)
        return result, None, None


def _execute_owner(context, execute, owner, verify_seconds, waited):
    started, clock = time.time(), time.monotonic()
    cancelled = False
    try:
        result = execute()
    except (Exception, KeyboardInterrupt) as error:
        cancelled = isinstance(error, KeyboardInterrupt)
        result = empty_result("receipt", "Execution raised " + type(error).__name__, status="ERROR")
    elapsed = time.monotonic() - clock
    verifying = time.monotonic()
    try:
        after = context["fingerprint"]()
        if after != context["before"]:
            result = _stale_result(result, "inputs_changed_during_execution")
        evidence = _capture_evidence(context["directory"], owner["nonce"], result)
        if not _passed(result, context["manifest"]):
            _invalidate(context["namespace"], "owner_nonpass")
        path = _publish(context["directory"], owner, context["before"], after, result, evidence,
                        started, context["deadline"])
    except (OSError, ValueError, TypeError, RuntimeError) as error:
        result, path, after = _finalization_failure(context, owner, result, error, started)
    reason = "cancelled" if cancelled else "cache_miss"
    if result.get("evidence_error"):
        reason = "evidence_incomplete"
    elif after != context["before"]:
        reason = "inputs_changed_during_execution"
    return _decorate(result, "executed", reason, path,
                     verify_seconds + time.monotonic() - verifying, waited, elapsed)


def _stale_result(result, reason):
    output = deepcopy(result)
    if output.get("status") not in {"FAIL", "ERROR"}:
        output["status"] = "INCOMPLETE"
    output["details_complete"] = False
    output["reason"] = reason
    if isinstance(output.get("coverage"), dict):
        output["coverage"]["complete"] = False
        output["coverage"].setdefault("diagnostics", []).append(reason)
    return output


def _recheck_current(context, result):
    try:
        if context["fingerprint"]() == context["before"]:
            return result, True
    except (OSError, ValueError, TypeError):
        _log("post_lookup_fingerprint_unavailable", "verify")
    return _stale_result(result, "inputs_changed_after_lookup_or_wait"), False


def _cached(context, execute, verify_started):
    directory = context["directory"]
    directory.mkdir(parents=True, exist_ok=True)
    wait_start = time.monotonic()
    action, value, path = _claim(directory, context["namespace"], context["before"], context["deadline"])
    verified = wait_start - verify_started
    if action == "reused":
        result, current = _recheck_current(context, value["result"])
        reason = "valid_terminal_receipt" if current else "inputs_changed_after_lookup"
        return _decorate(result, action, reason, path if current else None,
                         time.monotonic() - verify_started, 0, 0)
    if action == "unknown":
        return _execute_direct(execute, "owner_identity_unavailable", verified)
    if action == "joined":
        return _joined_result(context, value, verified, wait_start)
    return _execute_owner(context, execute, value, verified, time.monotonic() - wait_start)


def _joined_result(context, owner, verified, wait_start):
    result, path = _join(context["directory"], owner, context["before"], context["deadline"])
    waited = time.monotonic() - wait_start
    verifying = time.monotonic()
    result, current = _recheck_current(context, result)
    reason = "joined_owner" if path and current else "join_incomplete"
    return _decorate(result, "joined", reason, path if current else None,
                     verified + time.monotonic() - verifying, waited, 0)


def run_with_receipt(project, request, manifest, execute, *, reuse="off", fresh=False,
                     flags=None, declarations=None, environment=None,
                     timeout_seconds=1800, cache_dir=None):
    """Execute, reuse, or join one scope; the callback owns execution timeout."""
    valid_timeout = type(timeout_seconds) in (int, float)
    if not valid_timeout or not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be finite and positive")
    if reuse not in ("off", "auto"):
        raise ValueError("Invalid reuse mode or timeout")
    if fresh:
        namespace = _namespace(Path(project).resolve(), request, cache_dir)
        return _fresh(execute, namespace, manifest)
    if reuse == "off":
        return _execute_direct(execute, "reuse_off")
    project = Path(project).resolve()
    namespace = _namespace(project, request, cache_dir)
    started = time.monotonic()
    eligible, reason = check_eligibility(project, manifest, declarations)
    if not eligible:
        return _execute_direct(execute, reason, time.monotonic() - started)
    def fingerprint():
        return build_fingerprint(project, request, manifest, flags=flags,
                                 declarations=declarations, environment=environment)
    try:
        before = fingerprint()
    except (OSError, ValueError):
        return _execute_direct(execute, "unstable_inputs", time.monotonic() - started)
    context = {"namespace": namespace, "directory": namespace / before["key"][:32],
               "before": before, "fingerprint": fingerprint, "manifest": manifest,
               "deadline": started + timeout_seconds}
    try:
        return _cached(context, execute, started)
    except TimeoutError:
        result = empty_result("receipt", "Receipt coordination deadline exceeded")
        return _decorate(result, "joined", "coordination_timeout", None,
                         0, time.monotonic() - started, 0)
