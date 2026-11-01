"""Pure, conservative result adapters for unittest and pytest JUnit reports."""
from collections import Counter
import posixpath
import re
import unittest
import xml.etree.ElementTree as ET

import tdq_test_manifest


def _inventory_paths(inventory):
    return sorted({posixpath.normpath(path.replace("\\", "/"))
                   for path in inventory})


def _aliases(module):
    stem = module.removesuffix(".py").replace("/", ".")
    full = stem.removeprefix("tests.")
    return {stem, full, "tests." + full}, full.rsplit(".", 1)[-1]


def _longest_match(matches):
    if not matches:
        return None
    longest = max(score for score, _ in matches)
    modules = {module for score, module in matches if score == longest}
    return next(iter(modules)) if len(modules) == 1 else None


def _identifier_module(identifier, inventory):
    matches = []
    for module in inventory:
        aliases, basename = _aliases(module)
        for alias in aliases:
            if identifier == alias or identifier.startswith(alias + "."):
                matches.append((len(alias), module))
        if identifier == basename or identifier.startswith(basename + "."):
            matches.append((0, module))
    return _longest_match(matches)


def _file_module(filename, inventory):
    normalized = posixpath.normpath(filename.replace("\\", "/"))
    matches = []
    for module in inventory:
        aliases = {module, module.removeprefix("tests/")}
        for alias in aliases:
            if normalized == alias or normalized.endswith("/" + alias):
                matches.append((len(alias), module))
    return _longest_match(matches)


def _module_for(identifier, inventory, filename=""):
    if filename:
        return _file_module(filename, inventory)
    node_file = identifier.partition("::")[0]
    if node_file.endswith(".py"):
        return _file_module(node_file, inventory)
    return _identifier_module(identifier, inventory)


def _failure(identifier, kind, message, inventory, filename=""):
    return {"id": identifier, "kind": kind, "message": message,
            "module": _module_for(identifier, inventory, filename)}


def _result(backend, status, tests_run, skipped, failures, complete,
            exit_code, reason):
    unmapped = [failure for failure in failures if failure["module"] is None]
    return {
        "status": status, "backend": backend, "tests_run": tests_run,
        "skipped": skipped,
        "failed_modules": sorted({failure["module"] for failure in failures
                                  if failure["module"] is not None}),
        "failures": failures, "unmapped_failures": unmapped,
        "details_complete": complete and not unmapped,
        "exit_code": exit_code, "reason": reason,
    }


def empty_result(backend, reason, *, status="INCOMPLETE", exit_code=None):
    """Describe a no-op or aborted run without certifying an empty PASS."""
    if status not in {"SKIP", "INCOMPLETE", "ERROR"}:
        raise ValueError("Empty results cannot certify PASS or assertion FAIL")
    return _result(backend, status, 0, 0, [], status == "SKIP", exit_code,
                   reason)


def _status(failures, complete, tests_run, skipped, exit_code):
    if any(item["kind"] == "error" for item in failures):
        return "ERROR"
    if failures:
        return "FAIL"
    if not complete or exit_code != 0 or tests_run <= skipped:
        return "INCOMPLETE"
    return "PASS"


def _test_id(test):
    if isinstance(test, unittest.loader._FailedTest):
        return test._testMethodName
    identifier = test.id()
    holder = re.fullmatch(r"(?:setUp|tearDown)(?:Class|Module) \((.+)\)",
                          identifier)
    return holder.group(1) if holder else identifier


def _unittest_failures(result, inventory):
    failures = []
    for attribute, kind in (("failures", "failure"), ("errors", "error")):
        for test, message in getattr(result, attribute, []):
            failures.append(_failure(_test_id(test), kind, str(message),
                                     inventory))
    for test in getattr(result, "unexpectedSuccesses", []):
        failures.append(_failure(_test_id(test), "unexpected_success",
                                 "Unexpected success", inventory))
    return failures


def _valid_count(value):
    return (isinstance(value, int) and not isinstance(value, bool)
            and value >= 0)


def from_unittest_result(result, inventory, *, exit_code=None, manifest=None,
                         outcomes=None, completed=None):
    """Normalize a completed unittest TestResult without reading any files."""
    failures = _unittest_failures(result, _inventory_paths(inventory))
    count = getattr(result, "testsRun", None)
    skipped = len(getattr(result, "skipped", []))
    complete = _valid_count(count)
    tests_run = count if complete else 0
    reasons = [] if complete else ["Invalid unittest test count"]
    if skipped > tests_run or getattr(result, "shouldStop", False):
        complete = False
        reasons.append("Incomplete unittest run or inconsistent skip count")
    successful = result.wasSuccessful()
    if not successful and not failures:
        complete = False
        reasons.append("Unittest reported failure without failure details")
    if exit_code is None:
        exit_code = 0 if successful else 1
    if (exit_code == 0) != successful:
        complete = False
        reasons.append("Exit code contradicts unittest result")
    expected_failures = len(getattr(result, "expectedFailures", []))
    status = _status(failures, complete, tests_run, skipped + expected_failures, exit_code)
    legacy = _result("unittest", status, tests_run, skipped, failures, complete,
                     exit_code, _reason(status, reasons))
    return _with_case_evidence(legacy, manifest, outcomes, inventory, completed)


def _tag(element):
    return element.tag.rsplit("}", 1)[-1]


def _case_outcomes(case, inventory):
    classname = case.get("classname", "")
    name = case.get("name", "")
    identifier = ".".join(part for part in (classname, name) if part)
    filename = case.get("file", "")
    if filename and not classname:
        identifier = filename + "::" + name
    failures = []
    outcomes = [child for child in case
                if _tag(child) in {"failure", "error", "skipped"}]
    for outcome in outcomes:
        kind = _tag(outcome)
        if kind == "skipped":
            continue
        message = "\n".join(filter(None, (outcome.get("message"),
                                          outcome.text)))
        failures.append(_failure(identifier, kind, message, inventory,
                                 filename))
    skipped = sum(_tag(item) == "skipped" for item in outcomes)
    return failures, skipped, outcomes


def _xml_counts(element):
    cases = [child for child in element.iter() if _tag(child) == "testcase"]
    counts = {"tests": len(cases), "failures": 0, "errors": 0, "skipped": 0}
    for case in cases:
        for child in case:
            key = {"failure": "failures", "error": "errors",
                   "skipped": "skipped"}.get(_tag(child))
            if key:
                counts[key] += 1
    return counts


def _counter_issues(element, expected=None):
    counts = _xml_counts(element)
    if expected is not None:
        keys = {_xml_case_key(case) for case in element.iter() if _tag(case) == "testcase"}
        counts["tests"] = sum(expected.get(key, {}).get("tests", 1) for key in keys)
    issues = []
    required = _tag(element) == "testsuite"
    for key, actual in counts.items():
        declared = element.get(key)
        if declared is None and not required:
            continue
        if declared is None or re.fullmatch(r"[0-9]+", declared) is None:
            issues.append(f"Missing or invalid JUnit {key} counter")
        elif (declared.lstrip("0") or "0") != str(actual):
            issues.append(f"JUnit {key} counter contradicts testcase nodes")
    return issues


def _read_cases(root, inventory, structured=False):
    failures, skipped, tests_run, issues = [], 0, 0, []
    for case in root.iter():
        if _tag(case) != "testcase":
            continue
        found, skipped_count, outcomes = _case_outcomes(case, inventory)
        failures.extend(found)
        skipped += skipped_count
        tests_run += 1
        if len(outcomes) > 1 and not structured:
            issues.append("JUnit testcase has contradictory outcomes")
        if not case.get("name"):
            issues.append("JUnit testcase is missing its test name")
        allowed = {"failure", "error", "skipped", "properties",
                   "system-out", "system-err"}
        if any(_tag(child) not in allowed for child in case):
            issues.append("JUnit testcase has an unknown outcome element")
    return failures, tests_run, skipped, issues


def _xml_report(xml_text, inventory, expected=None):
    if not xml_text:
        return [], 0, 0, ["JUnit report is missing or empty"]
    try:
        root = ET.fromstring(xml_text)
    except (ET.ParseError, TypeError, ValueError) as error:
        return [], 0, 0, [f"JUnit report is malformed: {error}"]
    if _tag(root) not in {"testsuite", "testsuites"}:
        return [], 0, 0, ["Unexpected JUnit root element"]
    suites = [item for item in root.iter() if _tag(item) == "testsuite"]
    failures, tests_run, skipped, issues = _read_cases(root, inventory, expected is not None)
    if expected is not None:
        issues.extend(_junit_parity_issues(root, expected))
    if not suites:
        issues.append("JUnit report has no test suite")
    for suite in suites:
        issues.extend(_counter_issues(suite, expected))
    if _tag(root) == "testsuites":
        issues.extend(_counter_issues(root, expected))
    return failures, tests_run, skipped, issues


def _output_failures(output, inventory):
    failures = []
    for line in output.splitlines():
        match = re.match(r"^\s*(FAILED|ERROR)\s+(.+)$", line)
        if not match:
            continue
        identifier, _, message = match.group(2).partition(" - ")
        kind = "failure" if match.group(1) == "FAILED" else "error"
        failures.append(_failure(identifier.strip(), kind, message,
                                 inventory))
    return failures


def _summary_identity(identifier):
    return (identifier.replace("\\", "/").replace("::", ".")
            .replace(".py.", ".").removesuffix(".py").replace("/", ".")
            .removeprefix("tests.").rstrip("."))


def _append_output_failures(failures, supplemental):
    known = {(_summary_identity(item["id"]), item["kind"])
             for item in failures}
    added = False
    for item in supplemental:
        # XML and summary may describe one failure using different IDs.
        identity = (_summary_identity(item["id"]), item["kind"])
        if identity not in known:
            failures.append(item)
            known.add(identity)
            added = True
    return added


def _exit_failure(exit_code):
    if not _valid_count(exit_code):
        return None
    if exit_code == 1:
        return "failure", "Pytest reported test failure (exit 1)"
    if exit_code in {3, 4}:
        return "error", f"Pytest runner/usage error (exit {exit_code})"
    return None


def _retain_exit_failure(failures, exit_code, issues):
    known_exit = _exit_failure(exit_code)
    if known_exit and not failures:
        kind, message = known_exit
        failures.append({"id": "<pytest>", "kind": kind,
                         "message": message, "module": None})
        issues.append("Pytest exit has no corresponding JUnit failure detail")
    elif known_exit and known_exit[0] == "error":
        if not any(item["kind"] == "error" for item in failures):
            failures.append({"id": "<pytest>", "kind": "error",
                             "message": known_exit[1], "module": None})
            issues.append("Pytest runner error has no JUnit error detail")


def _reconcile_exit(failures, exit_code, issues):
    _retain_exit_failure(failures, exit_code, issues)
    if exit_code == 0 and failures:
        issues.append("Exit code contradicts reported failure")
    completed_exits = {0, 1}
    if any(item["kind"] == "error" for item in failures):
        completed_exits.add(2)
    if not _valid_count(exit_code) or exit_code not in completed_exits:
        issues.append(f"Pytest did not complete a test run (exit {exit_code})")


def _reason(status, issues):
    if issues:
        return "; ".join(dict.fromkeys(issues))
    return {"PASS": "Executed tests completed successfully",
            "FAIL": "Test failure or unexpected success",
            "ERROR": "Test collection, fixture, or runner error",
            "INCOMPLETE": "No non-skipped test execution"}[status]


def _xml_case_key(case):
    return case.get("classname", ""), case.get("name", "")


def _junit_case_key(identifier):
    # Match pytest's mangle_test_address without normalizing parameter contents.
    address, bracket, parameters = identifier.partition("[")
    names = address.split("::")
    names[0] = names[0].replace("/", ".").removesuffix(".py")
    names[-1] += bracket + parameters
    illegal = "[^\\u0009\\u000a\\u000d\\u0020-\\u007e\\u0080-\\ud7ff\\ue000-\\ufffd\\U00010000-\\U0010ffff]"
    name = re.sub(illegal, lambda match: f"#x{ord(match.group()):02X}", names[-1])
    return ".".join(names[:-1]), name


def _junit_event(report):
    status = report["outcome"]
    if status == "pass":
        return "pass" if report["phase"] == "call" else None
    if status == "xpass":
        return "failure" if report["reason"].startswith("[XPASS(strict)]") else "pass"
    return {"fail": "failure", "error": "error", "skip": "skip", "xfail": "xfail"}[status]


def _junit_case_model(case):
    reports = case["phases"] + case["subtests"]
    events = Counter(event for report in reports if (event := _junit_event(report)) is not None)
    teardown_error = any(item["phase"] == "teardown" and item["outcome"] == "error"
                         for item in case["phases"])
    call_failure = any(item["phase"] == "call" and _junit_event(item) == "failure" for item in reports)
    # Pytest emits a second node for call failure + teardown error, otherwise
    # teardown error shares the existing node and reduces its event counter once.
    split = teardown_error and call_failure
    correction = int(teardown_error and not split and sum(events.values()) > 1)
    tests = sum(events.values()) - correction
    events.pop("pass", None)
    return {"tags": events, "rows": 2 if split else 1, "tests": tests,
            "file": case["case_id"].partition("::")[0]}


def _junit_expected(manifest, outcomes, completed, exit_code):
    if manifest is None and outcomes is None:
        return None, []
    coverage = tdq_test_manifest.reconcile_cases(manifest, outcomes,
        completed=completed if completed is not None else True, exit_code=exit_code)
    if not coverage["complete"]:
        return None, []  # The authoritative adapter already rejects incomplete evidence.
    expected = {}
    for case in outcomes:
        key = _junit_case_key(case["case_id"])
        if key in expected:
            return None, ["JUnit case identity is ambiguous after pytest serialization"]
        expected[key] = _junit_case_model(case)
    return expected, []


def _junit_tags(cases):
    tags = Counter()
    for case in cases:
        for child in case:
            tag = _tag(child)
            if tag == "skipped":
                tags["xfail" if child.get("type") == "pytest.xfail" else "skip"] += 1
            elif tag in {"error", "failure"}:
                tags[tag] += 1
    return tags


def _junit_parity_issues(root, expected):
    observed = {}
    for case in root.iter():
        if _tag(case) == "testcase":
            observed.setdefault(_xml_case_key(case), []).append(case)
    issues = []
    if observed.keys() != expected.keys():
        issues.append("JUnit/sidecar case identities differ (missing or extra cases)")
    for key in observed.keys() & expected.keys():
        model = expected[key]
        if len(observed[key]) != model["rows"]:
            issues.append("JUnit/sidecar testcase multiplicity differs: " + repr(key))
        if _junit_tags(observed[key]) != model["tags"]:
            issues.append("JUnit/sidecar outcomes differ: " + repr(key))
        for case in observed[key]:
            if case.get("file") and _file_module(case.get("file"), [model["file"]]) is None:
                issues.append("JUnit file contradicts case identity: " + repr(key))
    return issues


def from_junit_xml(xml_text, exit_code, inventory, *, output="", manifest=None,
                   outcomes=None, completed=None):
    """Reconcile pytest XML, process exit, and supplemental failure text."""
    inventory = _inventory_paths(inventory)
    expected, parity_issues = _junit_expected(manifest, outcomes, completed, exit_code)
    failures, tests_run, skipped, issues = _xml_report(xml_text, inventory, expected)
    issues.extend(parity_issues)
    supplemental = _output_failures(output, inventory)
    if _append_output_failures(failures, supplemental):
        issues.append("Output contains failure details absent from JUnit")
    _reconcile_exit(failures, exit_code, issues)
    complete = not issues
    status = _status(failures, complete, tests_run, skipped, exit_code)
    legacy = _result("pytest", status, tests_run, skipped, failures, complete,
                     exit_code, _reason(status, issues))
    return _with_case_evidence(legacy, manifest, outcomes, inventory, completed,
                               reconciled_junit=expected is not None and not issues)


def _case_failures(outcomes, inventory):
    failures = []
    if not isinstance(outcomes, list):
        return failures
    kinds = {"fail": "failure", "error": "error", "xpass": "unexpected_success"}
    for case in outcomes:
        if not isinstance(case, dict) or not isinstance(case.get("outcome"), str):
            continue
        if case["outcome"] not in kinds:
            continue
        identifier = case.get("case_id")
        if not isinstance(identifier, str):
            identifier = "<unknown-case>"
        failures.append(_failure(identifier, kinds[case["outcome"]],
                                 str(case.get("reason") or case["outcome"]), inventory))
    return failures


def _collection_failures(manifest, inventory):
    if not isinstance(manifest, dict) or not isinstance(manifest.get("diagnostics"), list):
        return []
    failures = []
    for diagnostic in manifest["diagnostics"]:
        if isinstance(diagnostic, dict) and diagnostic.get("kind") == "collection_error":
            identifier = diagnostic.get("nodeid") or "<collection>"
            failures.append(_failure(str(identifier), "error",
                                     str(diagnostic.get("message", "Collection error")), inventory))
    return failures


def from_case_evidence(manifest, outcomes, exit_code, inventory, *, completed=True):
    """Certify a job from exact identities and outcomes, without JUnit's lossy XPASS encoding."""
    inventory = _inventory_paths(inventory)
    coverage = tdq_test_manifest.reconcile_cases(manifest, outcomes,
                                                completed=completed, exit_code=exit_code)
    failures = _case_failures(outcomes, inventory) + _collection_failures(manifest, inventory)
    issues = list(coverage["diagnostics"])
    # Pytest deliberately exits zero for non-strict XPASS; TDQ still rejects it.
    only_xpass = failures and all(item["kind"] == "unexpected_success" for item in failures)
    if not (exit_code == 0 and type(exit_code) is int and only_xpass):
        _reconcile_exit(failures, exit_code, issues)
    complete = coverage["complete"] and not issues
    counts = coverage["counts"]
    tests_run = len(set(coverage["observed"]))
    status = _status(failures, complete, tests_run,
                     tests_run - counts["pass"], exit_code)
    backend = manifest.get("backend", "pytest") if isinstance(manifest, dict) else "pytest"
    actual = _result(backend, status, tests_run, counts["skip"], failures,
                     complete, exit_code, _reason(status, issues))
    actual.update(manifest=manifest, case_outcomes=outcomes, coverage=coverage,
                  action="executed", source_receipt_id=None,
                  timings={"verify_seconds": 0.0, "wait_seconds": 0.0,
                           "execute_seconds": 0.0})
    return actual


def _retain_legacy_failures(actual, legacy, reconciled_junit=False):
    added = _append_output_failures(actual["failures"], legacy["failures"])
    if added and not reconciled_junit:
        actual["details_complete"] = False
        actual["coverage"]["complete"] = False
        actual["coverage"]["diagnostics"].append("Legacy failures absent from case evidence")
    actual["failed_modules"] = sorted({item["module"] for item in actual["failures"]
                                       if item["module"] is not None})
    actual["unmapped_failures"] = [item for item in actual["failures"] if item["module"] is None]
    # Missing completion evidence cannot erase an already observed failure.
    # Preserve ERROR from either source; the caller only supplies FAIL/ERROR.
    if actual["status"] != "ERROR":
        actual["status"] = legacy["status"]


def _with_case_evidence(legacy, manifest, outcomes, inventory, completed, *, reconciled_junit=False):
    if manifest is None and outcomes is None:
        return legacy
    actual = from_case_evidence(manifest, outcomes, legacy["exit_code"], inventory,
                                completed=completed if completed is not None else True)
    if legacy["status"] in {"FAIL", "ERROR"}:
        _retain_legacy_failures(actual, legacy, reconciled_junit)
    if not legacy["details_complete"] or actual["unmapped_failures"]:
        actual["details_complete"] = False
        actual["coverage"]["complete"] = False
        actual["reason"] += "; Legacy report incomplete: " + legacy["reason"]
        if actual["status"] == "PASS":
            actual["status"] = "INCOMPLETE"
    return actual
