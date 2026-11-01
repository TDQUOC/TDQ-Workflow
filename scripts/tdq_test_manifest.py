"""Case manifests and a pytest sidecar; importing the adapters needs only stdlib."""
from collections import Counter
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import posixpath
import sys
import tempfile


SCHEMA_VERSION = 1
OUTCOMES = ("pass", "fail", "error", "skip", "xfail", "xpass")


def _log(message):
    if os.environ.get("TDQ_LOG", "1").lower() not in {"0", "false", "off"}:
        print(f"[{datetime.now(timezone.utc).isoformat()}] manifest {message}", file=sys.stderr)


def _case_id(value):
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        return None
    filename, separator, remainder = value.partition("::")
    return posixpath.normpath(filename.replace("\\", "/")) + separator + remainder


def _diagnostic(kind, message, nodeid=None):
    return {"kind": kind, "message": message, "nodeid": nodeid}


def _manifest_case_ids(case_ids, issues):
    values = case_ids if isinstance(case_ids, (list, tuple)) else []
    identifiers = [_case_id(value) for value in values]
    if not isinstance(case_ids, (list, tuple)) or None in identifiers:
        issues.append(_diagnostic("invalid_case_id", "Invalid case ID in collection"))
    identifiers = [value for value in identifiers if value is not None]
    for identifier, count in Counter(identifiers).items():
        if count > 1:
            issues.append(_diagnostic("duplicate_case", "Duplicate collected case", identifier))
    return identifiers


def make_manifest(case_ids, *, backend="pytest", selectors=(), scope="selected",
                  diagnostics=(), fingerprint=None):
    """Keep every collected ID, with explicit diagnostics instead of silent deduplication."""
    issues = list(diagnostics) if isinstance(diagnostics, (list, tuple)) else [
        _diagnostic("invalid_manifest", "Diagnostics must be an array")]
    identifiers = _manifest_case_ids(case_ids, issues)
    if not isinstance(selectors, (list, tuple)) or not all(isinstance(x, str) for x in selectors):
        issues.append(_diagnostic("invalid_manifest", "Selectors must be strings"))
        selectors = ()
    return {"schema_version": SCHEMA_VERSION, "backend": backend,
            "selectors": list(selectors), "scope": scope, "case_ids": identifiers,
            "diagnostics": issues, "fingerprint": fingerprint,
            "complete": bool(identifiers) and not issues}


def _manifest_issues(manifest):
    if not isinstance(manifest, dict):
        return ["Manifest is not an object"]
    if type(manifest.get("schema_version")) is not int or manifest["schema_version"] != 1:
        return ["Unsupported manifest schema"]
    if manifest.get("backend") not in ("pytest", "unittest"):
        return ["Unknown manifest backend"]
    if manifest.get("scope") not in ("full", "selected", "direct", "transitive"):
        return ["Unknown manifest scope"]
    rebuilt = make_manifest(manifest.get("case_ids"), backend=manifest.get("backend"),
                            selectors=manifest.get("selectors"), scope=manifest.get("scope"),
                            diagnostics=manifest.get("diagnostics"))
    if not rebuilt["complete"] or manifest.get("complete") is not True:
        return ["Collection is empty, malformed, duplicated, or incomplete"]
    if rebuilt["case_ids"] != manifest["case_ids"]:
        return ["Manifest IDs are not canonical"]
    return []


def _skip_reason(reason):
    """Pytest's display prefix alone is not an explanation for skipping."""
    if not isinstance(reason, str):
        return ""
    if reason.strip() == "Skipped":
        return ""
    return reason.strip().removeprefix("Skipped:").strip()


def _valid_report(report):
    if not isinstance(report, dict):
        return False
    duration = report.get("duration_seconds")
    valid_duration = type(duration) is int or (type(duration) is float and math.isfinite(duration))
    return (report.get("phase") in ("setup", "call", "teardown")
            and report.get("outcome") in OUTCOMES
            and isinstance(report.get("reason"), str)
            and (report.get("outcome") != "skip" or bool(_skip_reason(report["reason"])))
            and valid_duration and duration >= 0)


def _valid_subtest(child):
    return isinstance(child.get("subtest"), dict) and child["phase"] == "call"


def _case_structure_issues(case):
    if not isinstance(case.get("reason"), str):
        return ["Case reason must be text"]
    phases, children = case.get("phases"), case.get("subtests")
    if not isinstance(phases, list) or not isinstance(children, list):
        return ["Case phases and subtests must be arrays"]
    if not phases or not all(_valid_report(report) for report in phases + children):
        return ["Case has missing or invalid phase evidence"]
    if any(report["outcome"] == "skip" for report in phases + children):
        if not _skip_reason(case["reason"]):
            return ["Skipped case has no explanation"]
        if not isinstance(case.get("capability"), str) or not case["capability"].strip():
            return ["Skipped case has no capability provenance"]
    return _case_phase_issues(case, phases, children)


def _case_phase_issues(case, phases, children):
    if any("subtest" in phase for phase in phases):
        return ["Subtest incorrectly recorded as a parent phase"]
    if not all(_valid_subtest(child) for child in children):
        return ["Subtest context is missing or is outside the call phase"]
    if _phase_issues(case.get("case_id"), phases + children):
        return ["Case has incomplete or duplicate phases"]
    if _aggregate_outcome(phases, children) != case.get("outcome"):
        return ["Case verdict contradicts its phases or subtests"]
    return []


def _observed_cases(outcomes):
    identifiers, counts, issues = [], dict.fromkeys(OUTCOMES, 0), []
    if not isinstance(outcomes, list):
        return identifiers, counts, ["Outcomes must be an array"]
    for case in outcomes:
        if not isinstance(case, dict):
            issues.append("Outcome is not an object")
            continue
        identifier = _case_id(case.get("case_id"))
        if identifier is None or identifier != case.get("case_id"):
            issues.append("Outcome has an invalid/noncanonical case ID")
        else:
            identifiers.append(identifier)
        status = case.get("outcome")
        if not isinstance(status, str) or status not in counts:
            issues.append("Unknown case outcome")
        else:
            counts[status] += 1
        issues.extend(_case_structure_issues(case))
    return identifiers, counts, issues


def _expected_case_ids(manifest):
    expected = manifest.get("case_ids", []) if isinstance(manifest, dict) else []
    if not isinstance(expected, list) or not all(isinstance(item, str) for item in expected):
        return []
    return expected


def reconcile_cases(manifest, outcomes, *, completed, exit_code):
    """Compare exact case identities; a matching count alone never proves coverage."""
    issues = _manifest_issues(manifest)
    expected = _expected_case_ids(manifest)
    observed, counts, observed_issues = _observed_cases(outcomes)
    issues.extend(observed_issues)
    missing, extra = sorted(set(expected) - set(observed)), sorted(set(observed) - set(expected))
    duplicates = sorted(identifier for identifier, count in Counter(observed).items() if count > 1)
    if missing or extra or duplicates:
        issues.append("Missing, extra, or duplicate observed cases")
    if completed is not True or type(exit_code) is not int or exit_code not in (0, 1):
        issues.append("Run did not complete normally")
    return {"expected": expected, "observed": observed, "missing": missing,
            "extra": extra, "duplicates": duplicates, "counts": counts,
            "complete": not issues, "diagnostics": issues}


def _invalid_evidence(message):
    return {"schema_version": SCHEMA_VERSION,
            "manifest": make_manifest([], diagnostics=[_diagnostic("invalid_evidence", message)]),
            "outcomes": [], "completed": False, "exit_code": None}


def load_run_evidence(path):
    """Read a sidecar conservatively; missing/corrupt evidence is explicit incomplete data."""
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as error:
        return _invalid_evidence(f"Cannot read sidecar: {type(error).__name__}")
    if not isinstance(value, dict) or type(value.get("schema_version")) is not int:
        return _invalid_evidence("Invalid sidecar envelope")
    if value["schema_version"] != SCHEMA_VERSION or not isinstance(value.get("manifest"), dict):
        return _invalid_evidence("Unsupported or missing sidecar manifest")
    if not isinstance(value.get("outcomes"), list) or type(value.get("completed")) is not bool:
        return _invalid_evidence("Invalid sidecar outcomes or completion")
    if type(value.get("exit_code")) is not int:
        return _invalid_evidence("Invalid sidecar exit code")
    coverage = reconcile_cases(value["manifest"], value["outcomes"],
                               completed=value["completed"], exit_code=value["exit_code"])
    if coverage["diagnostics"]:
        value["completed"] = False
    return value


def _report_reason(report):
    if getattr(report, "wasxfail", None):
        return str(report.wasxfail)
    reason = str(report.longrepr[-1]) if isinstance(report.longrepr, tuple) else str(report.longrepr or "")
    return _skip_reason(reason) if report.skipped else reason


def _report_outcome(report):
    if getattr(report, "wasxfail", None) is not None:
        return "xfail" if report.skipped else "xpass"
    if report.skipped:
        return "skip"
    if report.failed:
        if str(report.longrepr).startswith("[XPASS(strict)]"):
            return "xpass"
        return "fail" if report.when == "call" else "error"
    return "pass"


def _aggregate_outcome(phases, subtests):
    values = [item["outcome"] for item in phases + subtests]
    for status in ("error", "fail", "xpass"):
        if status in values:
            return status
    for status in ("skip", "xfail"):
        if any(item["outcome"] == status for item in phases):
            return status
    return "pass"


def _case_evidence(identifier, reports):
    phases = [item for item in reports if not item.get("subtest")]
    children = [item for item in reports if item.get("subtest")]
    status = _aggregate_outcome(phases, children)
    reasons = [item["reason"] for item in reports if item["outcome"] != "pass" and item["reason"]]
    return {"case_id": identifier, "outcome": status, "reason": "\n".join(dict.fromkeys(reasons)),
            "capability": "runtime-reported" if any(item["outcome"] == "skip" for item in reports) else None,
            "phases": phases, "subtests": children}


def _phase_issues(identifier, reports):
    phases = [item["phase"] for item in reports if not item.get("subtest")]
    if phases.count("setup") != 1 or phases.count("teardown") != 1:
        return [_diagnostic("incomplete_phases", "Missing/duplicate setup or teardown", identifier)]
    setup_passed = any(item["phase"] == "setup" and item["outcome"] == "pass" for item in reports)
    if phases.count("call") != int(setup_passed):
        return [_diagnostic("incomplete_phases", "Missing/duplicate call phase", identifier)]
    return []


def _write_sidecar(path, value):
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=destination.parent,
                                         prefix=destination.name + ".", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(value, stream, ensure_ascii=True, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


class _CaseRecorder:
    def __init__(self, config, output_path):
        self.config = config
        self.output_path = output_path
        self.scope = os.environ.get("TDQ_TEST_SCOPE", "selected")
        self.fingerprint = os.environ.get("TDQ_TEST_FINGERPRINT")
        self.worker = hasattr(config, "workerinput")
        self.identifiers = None
        self.diagnostics = []
        self.reports = {}

    def _collection(self, identifiers):
        normalized = [_case_id(identifier) for identifier in identifiers]
        if self.identifiers is None:
            self.identifiers = normalized
        elif self.identifiers != normalized:
            self.diagnostics.append(_diagnostic("collection_mismatch", "Workers collected different case IDs"))

    def pytest_collection_finish(self, session):
        if session.items:
            self._collection([item.nodeid for item in session.items])

    def pytest_xdist_node_collection_finished(self, node, ids):
        self._collection(ids)

    def pytest_collectreport(self, report):
        if report.failed:
            self.diagnostics.append(_diagnostic("collection_error", str(report.longrepr), report.nodeid))
        elif report.skipped:
            self.diagnostics.append(_diagnostic("collection_skip", str(report.longrepr), report.nodeid))

    def pytest_runtest_logreport(self, report):
        context = getattr(report, "context", None)
        if context is not None and not hasattr(report, "_tdq_subtest_context"):
            # Pytest already stores saferepr strings. Preserve them before xdist
            # reconstructs the context and applies saferepr a second time.
            report._tdq_subtest_context = {
                "message": str(context.msg or ""),
                "parameters": {str(k): v for k, v in context.kwargs.items()},
            }
        result = yield
        if self.worker:
            return result
        identifier = _case_id(report.nodeid)
        record = {"phase": report.when, "outcome": _report_outcome(report),
                  "reason": _report_reason(report), "duration_seconds": report.duration}
        if context is not None:
            record["subtest"] = report._tdq_subtest_context
        self.reports.setdefault(identifier, []).append(record)
        return result

    def pytest_sessionfinish(self, session, exitstatus):
        if self.worker:
            return
        for identifier, reports in self.reports.items():
            self.diagnostics.extend(_phase_issues(identifier, reports))
        manifest = make_manifest(self.identifiers or [], selectors=list(self.config.args),
                                 scope=self.scope,
                                 diagnostics=self.diagnostics,
                                 fingerprint=self.fingerprint)
        outcomes = [_case_evidence(identifier, reports) for identifier, reports in self.reports.items()]
        coverage = reconcile_cases(manifest, outcomes, completed=True, exit_code=int(exitstatus))
        value = {"schema_version": SCHEMA_VERSION, "manifest": manifest,
                 "outcomes": outcomes, "completed": coverage["complete"], "exit_code": int(exitstatus)}
        _write_sidecar(self.output_path, value)
        _log(f"cases={len(outcomes)} complete={value['completed']} exit={int(exitstatus)} action=executed")


def pytest_configure(config):
    """Enable opt-in evidence capture when loaded with ``-p tdq_test_manifest``."""
    output_path = os.environ.pop("TDQ_TEST_MANIFEST_OUTPUT", None)
    if not output_path and not hasattr(config, "workerinput"):
        return
    import pytest
    pytest.hookimpl(optionalhook=True)(_CaseRecorder.pytest_xdist_node_collection_finished)
    pytest.hookimpl(wrapper=True, tryfirst=True)(_CaseRecorder.pytest_runtest_logreport)
    config.pluginmanager.register(_CaseRecorder(config, output_path), "tdq-case-recorder")
