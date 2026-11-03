"""Request-local values-only telemetry exception; all other legacy guards remain.

Receipt schema and explicit policy bindings distinguish this from strict v1.
Only scalar values are projected; key presence, scalar type and structure remain.
No personal config values are persisted. This is not a cache eligibility policy.
"""
from contextlib import ExitStack
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import sys
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OLD = ROOT / "docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc"
SCHEMA = "tdq-safe-run/telemetry-v1"
POLICY = "claude-pluginUsage-scalar-values/v1"
IGNORED_PATHS = ["/pluginUsage/*/usageCount", "/pluginUsage/*/lastUsedAt"]
PINNED = {"safe_run.py": "4ea732dea8ce282102db261381d07df080ec5e33f6c9d27308f9444307794913",
          "verify_dod.py": "692cdc93c8f9f485fac1be8078c6930e927372cbf8139af0d08f2d62284c8a89"}
CONFIG_NAMES = {".claude/CLAUDE.md", ".claude/settings.json", ".claude.json",
                ".codex/AGENTS.md", ".codex/config.toml", ".codex/auth.json"}


def _load(name, path):
    specification = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


for filename, expected in PINNED.items():
    if hashlib.sha256((OLD / filename).read_bytes()).hexdigest() != expected:
        raise ValueError("Frozen legacy helper changed")
legacy = _load("_tdq_telemetry_frozen_run", OLD / "safe_run.py")
with patch.dict(sys.modules, {"safe_run": legacy}):
    validator = _load("_tdq_telemetry_frozen_validator", OLD / "verify_dod.py")


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def _constant(value):
    raise ValueError("Non-finite JSON constant")


def _finite_float(value):
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("Non-finite JSON number")
    return number


def _project_entry(entry):
    if not isinstance(entry, dict):
        raise ValueError("pluginUsage entries must be objects")
    for key in ("usageCount", "lastUsedAt"):
        if key in entry:
            value = entry[key]
            if type(value) not in (type(None), bool, int, float, str):
                raise ValueError("Telemetry values must be JSON scalars")
            entry[key] = {"$tdq_ignored_scalar_type": type(value).__name__}


def strict_json(content):
    """Reject duplicate object keys and all non-finite JSON numbers."""
    return json.loads(content, object_pairs_hook=_pairs, parse_constant=_constant,
                      parse_float=_finite_float)


def telemetry_projection(content):
    """Return strict parsed config with only approved scalar values projected."""
    result = strict_json(content)
    if not isinstance(result, dict):
        raise ValueError("Protected config must be an object")
    if "pluginUsage" in result:
        if not isinstance(result["pluginUsage"], dict):
            raise ValueError("pluginUsage must be an object")
        for entry in result["pluginUsage"].values():
            _project_entry(entry)
    return result


def implementation_bindings():
    """Bind the excluded adapter, frozen helpers and explicit user approval."""
    paths = [Path(__file__).resolve(), HERE / "telemetry-exception-approved.md"]
    paths.extend(OLD / name for name in sorted(PINNED))
    return {str(path): legacy.file_hash(path) for path in paths}


def config_snapshot(home, audit):
    """Record raw digests plus projected semantic digests, never config values."""
    raw = legacy.config_snapshot(home)
    path = home / ".claude.json"
    semantic = dict(raw)
    audit.append(raw)
    try:
        content = path.read_bytes()
    except FileNotFoundError:
        raw[".claude.json"] = semantic[".claude.json"] = "MISSING"
    else:
        raw[".claude.json"] = hashlib.sha256(content).hexdigest()
        semantic[".claude.json"] = legacy.digest(telemetry_projection(content))
    return semantic


def _receipt_exit(record, audit, before):
    record["config_policy"] = {"id": POLICY, "ignored_paths": IGNORED_PATHS,
                               "presence_and_type_protected": True}
    record["config_raw_before"] = audit[0] if audit else None
    record["config_raw_after"] = audit[1] if len(audit) > 1 else None
    record["policy_before"] = before
    try:
        record["policy_after"] = implementation_bindings()
        if before != record["policy_after"]:
            raise ValueError("Policy implementation changed during command")
    except OSError as error:
        record["policy_after"] = None
        legacy.record_failure(record, "policy_guard", error)
    except ValueError as error:
        legacy.record_failure(record, "policy_guard", error)
    return _STRICT_EXIT(record)


_STRICT_EXIT = legacy.receipt_exit
_STRICT_CONFIG = legacy.config_snapshot


def _snapshot(home, audit):
    # config_snapshot calls the original function, avoiding recursive override.
    with patch.object(legacy, "config_snapshot", _STRICT_CONFIG):
        return config_snapshot(home, audit)


def run_command(command, label, evidence, timeout, root, protected_home=None,
                archify_chrome=None):
    """Reuse the frozen runner with a scoped, explicitly tagged config policy."""
    audit, before = [], implementation_bindings()
    with ExitStack() as stack:
        stack.enter_context(patch.object(legacy, "SCHEMA", SCHEMA))
        stack.enter_context(patch.object(legacy, "config_snapshot", lambda home: _snapshot(home, audit)))
        stack.enter_context(patch.object(legacy, "receipt_exit", lambda row: _receipt_exit(row, audit, before)))
        return legacy.run_command(command, label, Path(evidence), timeout, Path(root),
                                  protected_home, archify_chrome)


def _validate_audit(receipt):
    expected = {"id": POLICY, "ignored_paths": IGNORED_PATHS,
                "presence_and_type_protected": True}
    if receipt.get("config_policy") != expected:
        raise ValueError("Unknown or missing config exception policy")
    bindings = implementation_bindings()
    if receipt.get("policy_before") != bindings or receipt.get("policy_after") != bindings:
        raise ValueError("Missing, stale or changed policy implementation/approval binding")
    for phase in ("before", "after"):
        _validate_phase_audit(receipt.get("config_raw_" + phase), receipt.get("config_" + phase))


def _validate_digest(checksum):
    if not isinstance(checksum, str) or (checksum != "MISSING" and not re.fullmatch("[0-9a-f]{64}", checksum)):
        raise ValueError("Invalid raw/semantic config digest")


def _validate_phase_audit(raw, semantic):
    if (not isinstance(raw, dict) or not isinstance(semantic, dict)
            or set(raw) != CONFIG_NAMES or set(semantic) != CONFIG_NAMES):
        raise ValueError("Missing raw/semantic config audit")
    for name, checksum in raw.items():
        _validate_digest(checksum)
        _validate_digest(semantic[name])
        if name != ".claude.json" and checksum != semantic[name]:
            raise ValueError("Projection changed a non-telemetry config file")
        if (checksum == "MISSING") != (semantic[name] == "MISSING"):
            raise ValueError("Config presence differs between raw and semantic audit")


def validate_receipt(path, root, current=True):
    """Validate the exception policy and all frozen successful receipt guards."""
    path = Path(path)
    content = path.read_bytes()
    parsed = strict_json(content)
    with patch.object(validator, "SCHEMA", SCHEMA):
        receipt = validator.validate_integrity(path)
        if path.read_bytes() != content or receipt != parsed:
            raise ValueError("Receipt changed while validating")
        _validate_audit(receipt)
        validator.validate_status(receipt)
    if type(receipt.get("exit_code")) is not int or receipt["exit_code"] != 0:
        raise ValueError("Invalid command exit code")
    if type(receipt.get("harness_exit_code")) is not int or receipt["harness_exit_code"] != 0:
        raise ValueError("Harness did not pass")
    if not receipt.get("dependency_before") or receipt["dependency_before"] != receipt.get("dependency_after"):
        raise ValueError("Missing or changed dependency snapshot")
    if receipt.get("capture") != {"stdout.txt": "complete", "stderr.txt": "complete"}:
        raise ValueError("Incomplete command capture")
    if not {"stdout.txt", "stderr.txt"}.issubset(receipt["artifacts"]):
        raise ValueError("Missing command output digests")
    if current and receipt["source_before"] != legacy.source_snapshot(Path(root)):
        raise ValueError("Stale or changed source fingerprint")
    return receipt


def main():
    """Keep frozen CLI/normal-user dispatch, pointing relaunch at this adapter."""
    original_run = legacy.run_command
    # Use the original from inside run_command while main's dispatch calls us.
    def dispatch_run(*args, **kwargs):
        with patch.object(legacy, "run_command", original_run):
            return run_command(*args, **kwargs)
    def self_test(evidence, root):
        return dispatch_run([sys.executable, str(HERE / "test_safe_run_telemetry.py")],
                            "telemetry-self-test", evidence, 120, root)[0]
    with patch.object(legacy, "__file__", str(Path(__file__).resolve())), \
            patch.object(legacy, "run_command", dispatch_run), \
            patch.object(legacy, "self_test", self_test):
        return legacy.main()


if __name__ == "__main__":
    raise SystemExit(main())
