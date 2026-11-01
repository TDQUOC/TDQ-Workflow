"""Read-only Q1-Q8 verifier; absent proof fails, never starts tests or benchmarks.

All bindings are {path, sha256}, relative to --root, except mapping (relative to
--evidence). reference_root supplies only the immutable historical inventory,
approval documents and pinned legacy helpers; it never supplies current results.
The plan_at_approval hash is provenance, not a mutable-plan freshness condition.

Populate full_receipt with the guarded production Full receipt binding. Its
stdout TDQ_RESULT marker is authoritative; full_result is an optional byte copy
with the same SHA, required for export. checks.Q*.proofs maps each OBLIGATIONS
key below to concrete passing case IDs/prefixes in the current Full sidecar.

Q3 migrations: before/after test prefixes, reason, classification pure/integration,
assertion_map [{before: anchor ID, after: anchor ID, reason}], work.before/after
{receipt, case_id}. Guarded stdout emits TDQ_SCOPE_WORK {case_id,
source_file_sha256, subprocess_calls, calibration_calls, git_calls}. Historical
before measurements bind the request-start test file, not the current source.
preserved_integration rows contain case_id and work, proving actual calls remain.

Q4: summary binding, summary_pointer (default ''), optional case/module list and
ID/duration field names. Q5: receipt, json/markdown/html bindings, input_sha_pointer
(default /input_sha256); export command must use report --result --out-prefix.

Runtime: runtime_receipt plus runtime binding; guarded stdout must emit
TDQ_SCOPE_RUNTIME {path, sha256}. Payload schema tdq-optimize-runtime/v1 has
source_sha256, scenarios [{name, classification, elapsed_seconds, deadline_seconds,
exit_code, process:{pid,ownership_verified,cleanup_complete}, evidence:[bindings],
facts:{...}}]. Required names: calibration-valid, reject-early, timeout-cleanup,
report-offline. Timeout facts below independently enforce the 2s/8s contract.
Q7 also needs qc binding compatible with legacy verify_qc. Q8 reports contains
roles slow-tests/request, html/markdown/source/browser bindings and numbers
[{source,pointer}]; browser schema is the existing verify_browser contract.

Self-test artifacts are explicitly synthetic validator fixtures, not task proof.
Digest bindings detect accidental mutation, not coordinated malicious rewriting
of the verifier, receipts and all attestations by a privileged author.
"""
import argparse
import ast
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


REQUEST = "2026-11-01-1045-toi-uu-bon-hang-muc"
BASELINE_SHA = "2cdfe6b492528e488ad459f764647c37ac45cba485351ae091b34e95a09481dc"
BASELINE_MAPPING_SHA = "87f4d0d26b07437f6f225de873be721b16f23cef4299459cb0df671c554db9fc"
OLD = "docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/"
HELPER_SHAS = {
    "verify_dod.py": "692cdc93c8f9f485fac1be8078c6930e927372cbf8139af0d08f2d62284c8a89",
    "safe_run.py": "4ea732dea8ce282102db261381d07df080ec5e33f6c9d27308f9444307794913",
}
MODULES = {
    "Q1": ["test_bench.py"],
    "Q2": ["test_codex_cli.py", "test_tdq_test_process.py"],
    "Q3": ["test_bench.py", "test_tdq_test.py", "test_team_mode.py",
           "test_tdq_runtime_bench.py", "test_optimize_contracts.py"],
    "Q4": ["test_tdq_test_report.py"],
    "Q5": ["test_tdq_test_report.py", "test_tdq_runner_integration.py"],
    "Q6": ["test_runtime_contracts.py", "test_optimize_contracts.py"],
    "Q7": ["test_optimize_logging.py", "test_runtime_logging.py"],
    "Q8": ["test_tdq_test_report.py"],
}
OBLIGATIONS = {
    "Q1": ["invalid_before_measurement", "valid_input", "no_new_output"],
    "Q2": ["deadline", "descendants", "home", "unrelated_job", "ownership"],
    "Q3": ["pure_no_work", "integration_preserved"],
    "Q4": ["phase_sum", "no_double_count", "stable_sort", "missing_invalid_duplicate"],
    "Q5": ["offline_export", "atomic_failure", "legacy_result", "verdict_preserved"],
    "Q6": ["compatibility"],
    "Q7": ["default_logging", "logging_off", "no_raw_secrets"],
    "Q8": ["html_escape"],
}
WINDOWS_LIMITATIONS = {
    "tests/test_tdq_test_process.py::test_posix_process_group_cleanup",
    "tests/test_team_mode.py::VaLuoiWorktreeTest::test_git_tu_choi_khong_phai_khoa_thi_khong_dan_nhan_khoa",
}
HELPER = None
POLICY_ADAPTER = None


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def log(message):
    if os.environ.get("TDQ_LOG", "1").lower() not in {"0", "false", "off"}:
        print(f"[{datetime.now(timezone.utc).isoformat()}] scope {message}", file=sys.stderr)


def load_helpers(reference):
    """Load only the two pinned legacy artifact implementations."""
    global HELPER
    for filename, expected in HELPER_SHAS.items():
        path = reference / OLD / filename
        require(sha(path) == expected, "Legacy helper changed: " + filename)
        name = "safe_run" if filename == "safe_run.py" else "_tdq_scope_legacy"
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        # safe_run must be installed before verify_dod imports it.
        if filename == "safe_run.py":
            spec.loader.exec_module(module)
    path = reference / OLD / "verify_dod.py"
    spec = importlib.util.spec_from_file_location("_tdq_scope_legacy", path)
    HELPER = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(HELPER)
    return HELPER


def bound(record, root):
    require(isinstance(record, dict), "Missing artifact binding")
    return HELPER.bound_file(record, root)


def guarded_receipt(record, root, current=True):
    """Validate preserved command/stdout/exit and all integrity guards."""
    path = bound(record, root)
    schema = read_json(path).get("schema")
    if schema == "tdq-safe-run/telemetry-v1":
        require(POLICY_ADAPTER is not None, "Telemetry policy adapter is not explicitly bound")
        receipt = POLICY_ADAPTER.validate_receipt(path, root, current=current)
    elif current:
        receipt = HELPER.validate_receipt(path, root)
    else:
        receipt = HELPER.validate_integrity(path)
        HELPER.validate_status(receipt)
    require(type(receipt.get("exit_code")) is int, "Invalid command exit type")
    require(bool(receipt.get("dependency_before"))
            and receipt["dependency_before"] == receipt.get("dependency_after"),
            "Missing or mutated dependency snapshot")
    return path, receipt


def load_policy_adapter(index, reference):
    """Enable only the approved, hash-bound request-local telemetry adapter."""
    global POLICY_ADAPTER
    POLICY_ADAPTER = None
    entry = index.get("receipt_policy")
    if entry is None:
        return
    require(entry.get("schema") == "tdq-safe-run/telemetry-v1"
            and entry.get("id") == "claude-pluginUsage-scalar-values/v1", "Unknown receipt policy")
    path = bound(entry["adapter"], reference)
    approval_note = bound(entry["approval"], reference)
    expected = reference / "docs/tdq/artifacts" / REQUEST
    require(path == (expected / "safe_run_telemetry.py").resolve(), "Unexpected policy adapter path")
    require(approval_note == (expected / "telemetry-exception-approved.md").resolve(), "Unexpected policy approval path")
    specification = importlib.util.spec_from_file_location("_tdq_scope_telemetry", path)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    require(module.SCHEMA == entry["schema"] and module.POLICY == entry["id"], "Adapter policy differs")
    POLICY_ADAPTER = module


def marker(path, prefix):
    rows = [json.loads(line[len(prefix):]) for line in
            (path.parent / "stdout.txt").read_text(encoding="utf-8").splitlines()
            if line.startswith(prefix)]
    require(bool(rows), "Missing output binding: " + prefix)
    return rows


def approval(index, reference):
    load_policy_adapter(index, reference)
    for filename, expected in HELPER_SHAS.items():
        require(sha(bound(index["helpers"][filename], reference)) == expected,
                "Helper index binding differs")
    entry = index["approval"]
    bound(entry["spec"], reference)
    manifest = read_json(bound(entry["preview_manifest"], reference))
    html = bound(entry["preview_html"], reference)
    bound(entry["candidate"], reference)
    require(entry["mode"] == "subagent", "Execution mode differs from approval")
    require(manifest["request"] == REQUEST, "Preview belongs to another request")
    require(manifest["document_digest"] == entry["document_digest"], "Spec binding differs")
    require(manifest["artifact_digest"] == sha(html), "Preview HTML binding differs")
    require(manifest["candidate_digest"] == entry["candidate_digest"], "Candidate binding differs")


def case_mapping(index, evidence, reference):
    baseline = read_json(bound(index["baseline"], reference))
    require(index["baseline"]["sha256"] == BASELINE_SHA, "Historical inventory changed")
    mapping = read_json(bound(index["mapping"], evidence))
    require(mapping["schema"] == "tdq-case-mapping/v1", "Unknown mapping schema")
    require(mapping["request"] == REQUEST, "Wrong mapping request")
    require(digest(mapping["baseline"]) == BASELINE_MAPPING_SHA, "Assertion baseline changed")
    old = mapping["baseline"]["case_ids"]
    require(len(old) == len(set(old)) == 3602, "Baseline must have 3602 unique cases")
    require(old == sorted(baseline["manifest"]["case_ids"]), "Historical case IDs differ")
    return mapping


def full_result(index, evidence, root):
    path, receipt = guarded_receipt(index["full_receipt"], root)
    require(path.is_relative_to(evidence.resolve()), "Full receipt is outside this request")
    command = receipt["command"]
    require(any(Path(arg).name == "tdq_test.py" for arg in command), "Not the production runner")
    require("tron-bo" in command and "--fresh" in command, "Not a fresh Full")
    for flag, expected in (("--workers", "1"), ("--reuse", "off")):
        require(flag in command and command[command.index(flag) + 1] == expected,
                "Full must explicitly use " + flag + " " + expected)
    markers = marker(path, "TDQ_RESULT ")
    require(len(markers) == 1, "Ambiguous Full result")
    result = read_json(bound(markers[0], root))
    HELPER.validate_full_payload(result, root)
    return result, receipt, markers[0]


def matches(prefix, case_id):
    return case_id == prefix or case_id.startswith(prefix + "[")


def passing(prefix, outcomes):
    cases = [case for name, case in outcomes.items() if matches(prefix, name)]
    require(bool(cases), "Required regression missing: " + prefix)
    for case in cases:
        HELPER.require_pass(case)


def regressions(check, entry, result, root):
    outcomes = {case["case_id"]: case for case in result["case_outcomes"]}
    declared = []
    for filename in MODULES[check]:
        relative = "tests/" + filename
        declared.extend(HELPER.declared_cases(root / relative, relative))
    for prefix in declared:
        if prefix in WINDOWS_LIMITATIONS and sys.platform == "win32":
            continue  # Full validation still requires an explicit capability/reason.
        passing(prefix, outcomes)
    proofs = entry.get("proofs", {})
    for obligation in OBLIGATIONS[check]:
        selected = proofs.get(obligation)
        require(isinstance(selected, list) and bool(selected), "Missing proof: " + obligation)
        for prefix in selected:
            require(any(matches(item, prefix) for item in declared), "Proof is not a declared case")
            passing(prefix, outcomes)
    return {"regressions": len(declared), "obligations": len(OBLIGATIONS[check])}


def assertion_nodes(function):
    for node in ast.walk(function):
        target = getattr(node, "func", None)
        name = getattr(target, "attr", "") or getattr(target, "id", "")
        if isinstance(node, ast.Assert):
            yield node
        elif isinstance(node, ast.Call) and (name.startswith("assert") or name in ("raises", "warns")):
            yield node


def definitions(root, paths):
    values = {}
    for relative in paths:
        tree = ast.parse((root / relative).read_text(encoding="utf-8-sig"))
        candidates = [(relative + "::" + node.name, node) for node in tree.body
                      if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")]
        for cls in [node for node in tree.body if isinstance(node, ast.ClassDef)]:
            candidates.extend((relative + "::" + cls.name + "::" + node.name, node)
                              for node in cls.body if isinstance(node, ast.FunctionDef)
                              and node.name.startswith("test_"))
        for prefix, function in candidates:
            anchors = {prefix + "#assertion-" + str(i + 1): digest(ast.dump(node, include_attributes=False))
                       for i, node in enumerate(assertion_nodes(function))}
            values[prefix] = {"code": digest(ast.dump(function, include_attributes=False)),
                              "assertions": anchors}
    return values


def assertion_mapping(row, baseline, current):
    old, new = row["before"], row["after"]
    require(old in baseline and new in current and row.get("reason"), "Invalid case migration")
    pairs = row.get("assertion_map", [])
    original = {item["id"]: item["sha256"] for item in baseline[old]["assertions"]}
    require(Counter(item["before"] for item in pairs) == Counter(original.keys()), "Lost/duplicate assertion anchor")
    require(len({item["after"] for item in pairs}) == len(pairs), "Assertions collapsed many-to-one")
    for item in pairs:
        actual = current[new]["assertions"].get(item["after"])
        require(actual is not None, "Mapped assertion does not exist in source")
        require(actual == original[item["before"]] or item.get("reason"), "Unexplained assertion translation")


def work_count(record, case_id, root, expected_sha, current):
    path, receipt = guarded_receipt(record["receipt"], root, current=current)
    rows = [row for row in marker(path, "TDQ_SCOPE_WORK ") if row.get("case_id") == case_id]
    require(len(rows) == 1, "Missing/duplicate subprocess observation")
    row = rows[0]
    relative = case_id.split("::")[0]
    require(receipt["source_before"]["files"].get(relative) == expected_sha,
            "Observation was recorded against another test source")
    require(row.get("source_file_sha256") == expected_sha, "Work counter source differs")
    counts = [row.get(name) for name in ("subprocess_calls", "calibration_calls", "git_calls")]
    require(all(type(value) is int and value >= 0 for value in counts), "Invalid work counts")
    return counts


def changed_case(row, baseline, current, result, root, sources):
    assertion_mapping(row, baseline, current)
    passing(row["after"], {case["case_id"]: case for case in result["case_outcomes"]})
    relative = row["before"].split("::")[0]
    before = work_count(row["work"]["before"], row["before"], root, sources[relative], False)
    after = work_count(row["work"]["after"], row["after"], root,
                       sha(root / row["after"].split("::")[0]), True)
    require(row["classification"] in {"pure", "integration"}, "Unknown migration purpose")
    if row["classification"] == "pure":
        require(before[0] > 0 and after == [0, 0, 0], "Pure case still performs work or has no measured reduction")
    else:
        require(after[0] > 0, "Integration proof no longer uses a subprocess")


def verify_mapping(mapping, result, root):
    baseline = mapping["baseline"]["assertion_baseline"]
    current = definitions(root, baseline["source_files"])
    old = baseline["definitions"]
    changed = {key for key, value in old.items()
               if key not in current or current[key]["code"] != value["code_sha256"]}
    rows = mapping["migrations"]
    require(bool(rows), "No explicit test-work mapping")
    require(len({row["before"] for row in rows}) == len(rows), "Duplicate case mapping")
    require(changed <= {row["before"] for row in rows}, "Changed test lacks assertion mapping")
    for row in rows:
        changed_case(row, old, current, result, root, baseline["source_files"])
    integration = mapping.get("preserved_integration", [])
    require(bool(integration), "No preserved real integration proof")
    for row in integration:
        counts = work_count(row["work"], row["case_id"], root,
                            sha(root / row["case_id"].split("::")[0]), True)
        require(counts[0] > 0, "Integration has no actual process work")
    return {"changed_tests": len(changed), "migrations": len(rows)}


def inventory(mapping, result):
    current = set(result["manifest"]["case_ids"])
    missing = set(mapping["baseline"]["case_ids"]) - current
    remapped = set()
    for row in mapping["migrations"]:
        old = [case for case in missing if matches(row["before"], case)]
        for name in old:
            target = row["after"] + name[len(row["before"]):]
            require(target in current and target not in remapped and row.get("reason"), "Invalid inventory remap")
            remapped.add(target)
        missing.difference_update(old)
    require(not missing, "Missing baseline cases: " + str(sorted(missing)[:5]))
    return {"baseline_cases": 3602, "current_cases": len(current), "remapped": len(remapped)}


def pointer(value, path):
    require(isinstance(path, str) and (not path or path.startswith("/")), "Invalid JSON pointer")
    for part in path.split("/")[1:]:
        key = part.replace("~1", "/").replace("~0", "~")
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def expected_rankings(result):
    cases, modules, incomplete = [], defaultdict(float), set()
    for case in result["case_outcomes"]:
        phases = case.get("phases", [])
        durations = [item.get("duration_seconds") for item in phases]
        module = case["case_id"].split("::")[0]
        valid = bool(phases) and all(type(value) in (int, float)
                                    and math.isfinite(value) and value >= 0 for value in durations)
        if valid:
            total = sum(durations)
            cases.append((case["case_id"], total))
            modules[module] += total
        else:
            incomplete.add(module)
    complete_modules = [(key, value) for key, value in modules.items() if key not in incomplete]
    order = lambda row: (-row[1], row[0])
    return sorted(cases, key=order)[:20], sorted(complete_modules, key=order)[:20], bool(incomplete)


def compare_ranking(actual, expected, identifier, duration):
    require(isinstance(actual, list) and len(actual) == len(expected), "Top20 size differs")
    for row, (name, seconds) in zip(actual, expected):
        require(row.get(identifier) == name, "Top20 ID/order differs")
        value = row.get(duration)
        require(type(value) in (int, float) and math.isfinite(value)
                and math.isclose(value, seconds, rel_tol=1e-9, abs_tol=1e-9), "Phase duration sum differs")


def summary(entry, result, root):
    value = pointer(read_json(bound(entry["summary"], root)), entry.get("summary_pointer", ""))
    cases, modules, partial = expected_rankings(result)
    compare_ranking(pointer(value, entry.get("case_list_pointer", "/top_cases")), cases,
                    entry.get("case_id_key", "case_id"), entry.get("duration_key", "duration_seconds"))
    compare_ranking(pointer(value, entry.get("module_list_pointer", "/top_modules")), modules,
                    entry.get("module_id_key", "module"), entry.get("duration_key", "duration_seconds"))
    quality = pointer(value, entry.get("quality_pointer", "/quality/status"))
    require(quality == ("partial" if partial else "complete"), "Summary quality contradicts raw durations")
    return {"top_cases": len(cases), "top_modules": len(modules), "quality": quality}


def exported(entry, index, original, root):
    input_path = bound(index["full_result"], root)
    require(sha(input_path) == original["sha256"], "Export input is not the exact Full result copy")
    _, receipt = guarded_receipt(entry["receipt"], root)
    command = receipt["command"]
    require("report" in command and "--result" in command and "--out-prefix" in command, "Not an offline report command")
    selected = HELPER.contained(root, command[command.index("--result") + 1])
    require(selected == input_path, "Export command used another input")
    prefix = HELPER.contained(root, command[command.index("--out-prefix") + 1])
    for role, suffix in (("json", ".json"), ("markdown", ".md"), ("html", ".html")):
        require(bound(entry[role], root) == prefix.with_suffix(suffix), "Export output prefix differs")
    data = read_json(bound(entry["json"], root))
    require(pointer(data, entry.get("input_sha_pointer", "/input_sha256")) == sha(input_path), "Export JSON input SHA differs")
    for role in ("markdown", "html"):
        require(sha(input_path) in bound(entry[role], root).read_text(encoding="utf-8"), "Export lacks input provenance")
    return {"input_sha256": sha(input_path)}


def runtime(index, root):
    path, receipt = guarded_receipt(index["runtime_receipt"], root)
    require(any(Path(arg).name == "runtime_checks.py" for arg in receipt["command"]), "Wrong runtime command")
    markers = marker(path, "TDQ_SCOPE_RUNTIME ")
    require(len(markers) == 1 and markers[0] == index["runtime"], "Runtime output binding differs")
    data = read_json(bound(index["runtime"], root))
    require(data["schema"] == "tdq-optimize-runtime/v1", "Unknown runtime schema")
    require(data["source_sha256"] == receipt["source_before"]["sha256"], "Runtime source differs")
    rows = data.get("scenarios", [])
    require(bool(rows) and len({row["name"] for row in rows}) == len(rows), "Missing/duplicate scenarios")
    for row in rows:
        runtime_row(row, root)
    return {row["name"]: row for row in rows}


def runtime_row(row, root):
    elapsed, limit = row["elapsed_seconds"], row["deadline_seconds"]
    require(type(elapsed) in (int, float) and math.isfinite(elapsed) and 0 <= elapsed <= 120,
            "Runtime exceeded 120s or has invalid duration")
    require(type(limit) in (int, float) and 0 < limit <= 120 and elapsed <= limit, "Runtime deadline differs")
    require(type(row["exit_code"]) is int and row["exit_code"] == 0, "Runtime scenario failed")
    require(row["classification"] in {"fixture-process", "real-process", "simulation"}, "Missing workload classification")
    process = row["process"]
    require(type(process["pid"]) is int and process["pid"] > 0, "Missing process identity")
    require(process["ownership_verified"] is True and process["cleanup_complete"] is True, "Unowned process or incomplete cleanup")
    require(bool(row.get("evidence")), "No raw runtime evidence")
    for record in row["evidence"]:
        bound(record, root)


def timeout_facts(row):
    facts = row["facts"]
    require(facts.get("timeout_seconds") == 2 and row["elapsed_seconds"] <= 8, "2s timeout exceeded 8s including cleanup")
    require(facts.get("ready_observed") is True and bool(facts.get("descendants_observed")), "No live descendant handshake")
    require(facts.get("descendants_alive_after") == [], "Descendants remain alive")
    require(facts.get("home_existed_before") is True and facts.get("home_exists_after") is False, "Job HOME cleanup unproven")
    require(bool(facts.get("unrelated_before")) and facts["unrelated_before"] == facts.get("unrelated_after"), "Another job changed")


def runtime_contracts(scenarios, root):
    required = {"calibration-valid", "reject-early", "timeout-cleanup", "report-offline"}
    require(required <= set(scenarios), "Runtime scenario missing")
    timeout_facts(scenarios["timeout-cleanup"])
    valid = scenarios["calibration-valid"]["facts"]
    require(type(valid.get("measurement_calls")) is int and valid["measurement_calls"] > 0
            and valid.get("output_exists") is True, "Valid calibration never measured/wrote output")
    rejected = scenarios["reject-early"]["facts"]
    require(rejected.get("measurement_calls") == 0 and rejected.get("new_output_files") == []
            and type(rejected.get("command_exit_code")) is int
            and rejected["command_exit_code"] != 0, "Early rejection did work or succeeded")
    offline = scenarios["report-offline"]["facts"]
    source = bound(offline["input"], root)
    require(offline.get("runner_calls") == 0 and offline.get("input_sha256") == sha(source),
            "Offline report ran tests or changed its input")
    outputs = [bound(record, root) for record in offline.get("outputs", [])]
    require(len(outputs) == 3 and {path.suffix for path in outputs} == {".json", ".md", ".html"},
            "Offline runtime did not publish all three formats")


def report_browser(entry, root, original):
    html = bound(entry["html"], root)
    markdown = bound(entry["markdown"], root).read_text(encoding="utf-8")
    source = bound(entry["source"], root)
    require(sha(source) == original["sha256"], "Report input source differs")
    page = HELPER.read_page(html)
    text = " ".join(page.text)
    require(sha(source) in text and sha(source) in markdown, "Report lacks provenance")
    HELPER.verify_links(html, page, root)
    HELPER.verify_browser(entry["browser"], html, root)
    views = read_json(bound(entry["browser"], root))["views"]
    require(len(views) == 2, "Exactly two browser viewports required")
    for view in views:
        expected = (1440, 900) if view["name"] == "desktop" else (375, 812)
        require((view["viewport"]["width"], view["viewport"]["height"]) == expected, "Wrong browser dimensions")
        observation = read_json(bound(view["observation"], root))
        require(observation["viewport"] == view["viewport"], "DOM viewport differs")
    require(bool(entry.get("numbers")), "No numeric report bindings")
    for item in entry["numbers"]:
        value = pointer(read_json(bound(item["source"], root)), item["pointer"])
        require(type(value) in (int, float) and str(value) in text and str(value) in markdown, "Report numeric binding differs")


def verify(check, index, evidence, root, reference):
    """Certify one Q only from source-bound raw evidence and concrete assertions."""
    require(index["schema"] == "tdq-scope-evidence/v1" and index["request"] == REQUEST, "Wrong scope index")
    approval(index, reference)
    mapping = case_mapping(index, evidence, reference)
    result, receipt, original = full_result(index, evidence, root)
    entry = index["checks"][check]
    details = regressions(check, entry, result, root)
    details.update(inventory(mapping, result))
    if check == "Q2":
        timeout_facts(runtime(index, root)["timeout-cleanup"])
    if check == "Q3":
        details.update(verify_mapping(mapping, result, root))
    if check == "Q4":
        details.update(summary(entry, result, root))
    if check == "Q5":
        details.update(exported(entry, index, original, root))
    if check == "Q7":
        scenarios = runtime(index, root)
        runtime_contracts(scenarios, root)
        details["reviewer"] = HELPER.verify_qc(entry, root)
    if check == "Q8":
        reports = entry.get("reports", [])
        require({row["role"] for row in reports} == {"slow-tests", "request"} and len(reports) == 2, "Both HTML reports need proof")
        for row in reports:
            report_browser(row, root, original)
    details["source_sha256"] = receipt["source_before"]["sha256"]
    return {"check": check, "status": "PASS", "details": details}


def self_test(evidence):
    """Exercise real validators using explicitly synthetic, disposable artifacts."""
    class ValidatorTests(unittest.TestCase):
        def setUp(self):
            self.temp = tempfile.TemporaryDirectory(prefix="scope-selftest-", dir=evidence)
            self.addCleanup(self.temp.cleanup)
            self.root = Path(self.temp.name)
            self.snapshot = {"sha256": "synthetic-source", "files": {}}
            self.receipt_path = self.root / "receipt.json"
            (self.root / "stdout.txt").write_text("synthetic capture\n", encoding="utf-8")
            self.receipt = {"schema": "tdq-safe-run/v1", "exit_code": 0, "verdict": "PASS",
                            "elevated": False, "timed_out": False,
                            "config_before": {"synthetic": "same"}, "config_after": {"synthetic": "same"},
                            "source_before": self.snapshot, "source_after": self.snapshot,
                            "dependency_before": {"synthetic": "same"}, "dependency_after": {"synthetic": "same"},
                            "failures": [], "isolation": {"cleanup": "complete"},
                            "artifacts": {"stdout.txt": sha(self.root / "stdout.txt")}}
            self.save_receipt()

        def save_receipt(self):
            unsigned = {key: value for key, value in self.receipt.items() if key != "sha256"}
            self.receipt["sha256"] = digest(unsigned)
            self.receipt_path.write_text(json.dumps(self.receipt), encoding="utf-8")
            self.binding = {"path": "receipt.json", "sha256": sha(self.receipt_path)}

        def validated(self):
            with patch.object(HELPER, "source_snapshot", return_value=self.snapshot):
                return guarded_receipt(self.binding, self.root)

        def test_valid_receipt_control(self):
            self.assertEqual(self.validated()[1]["verdict"], "PASS")

        def test_missing_receipt(self):
            self.receipt_path.unlink()
            with self.assertRaises(OSError):
                self.validated()

        def test_stale_source(self):
            self.receipt["source_before"] = self.receipt["source_after"] = {"sha256": "old-source"}
            self.save_receipt()
            with self.assertRaisesRegex(ValueError, "Stale"):
                self.validated()

        def test_dependency_mutation(self):
            self.receipt["dependency_after"] = {"synthetic": "changed"}
            self.save_receipt()
            with self.assertRaisesRegex(ValueError, "dependency"):
                self.validated()

        def test_raw_capture_mutation(self):
            (self.root / "stdout.txt").write_text("mutated", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "digest"):
                self.validated()

        def test_false_pass_receipt(self):
            self.receipt["exit_code"] = 1
            self.save_receipt()
            with self.assertRaises(ValueError):
                self.validated()

        def test_valid_raw_full_control(self):
            result = HELPER.simulated_full(self.root)
            HELPER.validate_full_payload(result, self.root)

        def test_false_pass_payload(self):
            result = HELPER.simulated_full(self.root)
            (self.root / "execution.xml").write_text('<testsuite><testcase classname="tests.test_simulation" name="test_example"><failure>actual failure</failure></testcase></testsuite>', encoding="utf-8")
            result["evidence"]["execution.xml"]["sha256"] = sha(self.root / "execution.xml")
            with self.assertRaises(ValueError):
                HELPER.validate_full_payload(result, self.root)

        def test_raw_full_mutation(self):
            result = HELPER.simulated_full(self.root)
            (self.root / "execution.json").write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "changed"):
                HELPER.validate_full_payload(result, self.root)

        def test_missing_browser(self):
            html = self.root / "page.html"
            html.write_text("<html>synthetic browser control</html>", encoding="utf-8")
            with self.assertRaises(OSError):
                HELPER.verify_browser({"path": "missing-browser.json", "sha256": "0" * 64}, html, self.root)

        def test_timeout_budget_not_self_declared_pass(self):
            with self.assertRaisesRegex(ValueError, "8s"):
                timeout_facts({"elapsed_seconds": 30.16, "status": "PASS", "facts": {"timeout_seconds": 2}})

        def test_missing_binding_is_not_pass(self):
            with self.assertRaisesRegex(ValueError, "Missing"):
                guarded_receipt(None, self.root)

        def test_dropped_assertion_mapping(self):
            baseline = {"old": {"assertions": [{"id": "old#a1", "sha256": "assertion"}]}}
            current = {"new": {"assertions": {"new#a1": "assertion"}}}
            row = {"before": "old", "after": "new", "reason": "move", "assertion_map": []}
            with self.assertRaisesRegex(ValueError, "Lost"):
                assertion_mapping(row, baseline, current)

        def test_valid_assertion_mapping_control(self):
            baseline = {"old": {"assertions": [{"id": "old#a1", "sha256": "assertion"}]}}
            current = {"new": {"assertions": {"new#a1": "assertion"}}}
            row = {"before": "old", "after": "new", "reason": "move",
                   "assertion_map": [{"before": "old#a1", "after": "new#a1"}]}
            assertion_mapping(row, baseline, current)

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ValidatorTests)
    result = unittest.TextTestRunner(verbosity=2, stream=sys.stdout).run(suite)
    print(json.dumps({"kind": "synthetic-validator-selftest", "tests_run": result.testsRun,
                      "successful": result.wasSuccessful(), "task_evidence": False}))
    return 0 if result.wasSuccessful() else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("check", nargs="?", choices=sorted(MODULES))
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--evidence", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument("--reference-root", type=Path)
    args = parser.parse_args()
    if not args.check and not args.self_test:
        parser.error("a Q check or --self-test is required")
    try:
        evidence = args.evidence.resolve()
        index = read_json(evidence / "evidence-index.json")
        reference = (args.reference_root or Path(index["reference_root"])).resolve()
        load_helpers(reference)
        if args.self_test:
            return self_test(evidence)
        output = verify(args.check, index, evidence, args.root.resolve(), reference)
    except (OSError, ValueError, KeyError, TypeError, IndexError, ImportError) as error:
        output = {"check": args.check, "status": "FAIL", "error": type(error).__name__ + ": " + str(error)}
        log(output["error"])
        print(json.dumps(output))
        return 1
    print(json.dumps(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
