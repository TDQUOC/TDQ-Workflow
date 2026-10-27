"""Pure, conservative result adapters for unittest and pytest JUnit reports."""
import posixpath
import re
import unittest
import xml.etree.ElementTree as ET


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


def from_unittest_result(result, inventory, *, exit_code=None):
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
    status = _status(failures, complete, tests_run, skipped, exit_code)
    return _result("unittest", status, tests_run, skipped, failures, complete,
                   exit_code, _reason(status, reasons))


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


def _counter_issues(element):
    counts = _xml_counts(element)
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


def _read_cases(root, inventory):
    failures, skipped, tests_run, issues = [], 0, 0, []
    for case in root.iter():
        if _tag(case) != "testcase":
            continue
        found, skipped_count, outcomes = _case_outcomes(case, inventory)
        failures.extend(found)
        skipped += skipped_count
        tests_run += 1
        if len(outcomes) > 1:
            issues.append("JUnit testcase has contradictory outcomes")
        if not case.get("name"):
            issues.append("JUnit testcase is missing its test name")
        allowed = {"failure", "error", "skipped", "properties",
                   "system-out", "system-err"}
        if any(_tag(child) not in allowed for child in case):
            issues.append("JUnit testcase has an unknown outcome element")
    return failures, tests_run, skipped, issues


def _xml_report(xml_text, inventory):
    if not xml_text:
        return [], 0, 0, ["JUnit report is missing or empty"]
    try:
        root = ET.fromstring(xml_text)
    except (ET.ParseError, TypeError, ValueError) as error:
        return [], 0, 0, [f"JUnit report is malformed: {error}"]
    if _tag(root) not in {"testsuite", "testsuites"}:
        return [], 0, 0, ["Unexpected JUnit root element"]
    suites = [item for item in root.iter() if _tag(item) == "testsuite"]
    failures, tests_run, skipped, issues = _read_cases(root, inventory)
    if not suites:
        issues.append("JUnit report has no test suite")
    for suite in suites:
        issues.extend(_counter_issues(suite))
    if _tag(root) == "testsuites":
        issues.extend(_counter_issues(root))
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


def from_junit_xml(xml_text, exit_code, inventory, *, output=""):
    """Reconcile pytest XML, process exit, and supplemental failure text."""
    inventory = _inventory_paths(inventory)
    failures, tests_run, skipped, issues = _xml_report(xml_text, inventory)
    supplemental = _output_failures(output, inventory)
    if _append_output_failures(failures, supplemental):
        issues.append("Output contains failure details absent from JUnit")
    _reconcile_exit(failures, exit_code, issues)
    complete = not issues
    status = _status(failures, complete, tests_run, skipped, exit_code)
    return _result("pytest", status, tests_run, skipped, failures, complete,
                   exit_code, _reason(status, issues))
