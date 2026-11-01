"""Case coverage and real pytest reports, including distributed subtests."""
import json
from copy import deepcopy
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from helper import ROOT
import tdq_test_manifest as manifest
import tdq_test_result as results
import tdq_test_receipt as receipts


def outcome(case_id, status="pass"):
    return {"case_id": case_id, "outcome": status, "reason": "fixture",
            "capability": None,
            "phases": [{"phase": phase, "outcome": status if phase == "call" else "pass",
                        "reason": "fixture", "duration_seconds": 0.0}
                       for phase in ("setup", "call", "teardown")], "subtests": []}


class CoverageTest(unittest.TestCase):
    def test_skip_requires_reason_in_case_and_phase_and_capability(self):
        passing = outcome("test_a.py::test_pass")
        skipped = outcome("test_a.py::test_skip", "skip")
        skipped["capability"] = "runtime-reported"
        expected = manifest.make_manifest([passing["case_id"], skipped["case_id"]])
        self.assertTrue(manifest.reconcile_cases(expected, [passing, skipped], completed=True, exit_code=0)["complete"])
        for location in ("case", "phase", "capability"):
            for value in ("", " \n\t", None):
                changed = deepcopy(skipped)
                if location == "phase":
                    changed["phases"][1]["reason"] = value
                else:
                    changed["reason" if location == "case" else "capability"] = value
                with self.subTest(location=location, value=value):
                    coverage = manifest.reconcile_cases(expected, [passing, changed], completed=True, exit_code=0)
                    self.assertFalse(coverage["complete"], coverage)

    def test_blank_subtest_skip_cannot_hide_inside_passing_parent(self):
        parent = outcome("test_a.py::test_parent")
        parent["capability"] = "runtime-reported"
        child = {**parent["phases"][1], "outcome": "skip", "reason": "Skipped",
                 "subtest": {"message": None, "parameters": {"value": 1}}}
        parent["subtests"] = [child]
        expected = manifest.make_manifest([parent["case_id"]])
        self.assertFalse(manifest.reconcile_cases(expected, [parent], completed=True, exit_code=0)["complete"])
        child["reason"] = "optional device unavailable"
        self.assertTrue(manifest.reconcile_cases(expected, [parent], completed=True, exit_code=0)["complete"])

    def test_preserves_parameter_text_and_normalizes_only_path(self):
        case_id = r"tests\test_sample.py::Group::test_value[a\b::c]"
        actual = manifest.make_manifest([case_id], scope="full", fingerprint="abc")
        self.assertEqual(actual["case_ids"],
                         [r"tests/test_sample.py::Group::test_value[a\b::c]"])
        self.assertTrue(actual["complete"])
        self.assertEqual(actual["fingerprint"], "abc")

    def test_duplicate_and_collection_error_are_not_complete(self):
        actual = manifest.make_manifest(["test_a.py::test_a"] * 2)
        self.assertFalse(actual["complete"])
        actual = manifest.make_manifest(["test_a.py::test_a"], diagnostics=[
            {"kind": "collection_error", "message": "import failed"}])
        self.assertFalse(actual["complete"])

    def test_missing_extra_duplicate_and_bad_outcome_fail_closed(self):
        expected = manifest.make_manifest(["test_a.py::test_a", "test_a.py::test_b"])
        for observed in ([outcome("test_a.py::test_a")],
                         [outcome("test_a.py::test_a"), outcome("test_a.py::test_c")],
                         [outcome("test_a.py::test_a")] * 2,
                         [outcome("test_a.py::test_a", "unknown"),
                          outcome("test_a.py::test_b")]):
            with self.subTest(observed=observed):
                actual = manifest.reconcile_cases(expected, observed,
                                                  completed=True, exit_code=0)
                self.assertFalse(actual["complete"])

    def test_equal_sets_do_not_certify_interrupted_or_invalid_exit(self):
        expected = manifest.make_manifest(["test_a.py::test_a"])
        for completed, code in ((False, 0), (True, 2), (True, True), (True, None)):
            with self.subTest(completed=completed, code=code):
                actual = manifest.reconcile_cases(expected, [outcome("test_a.py::test_a")],
                                                  completed=completed, exit_code=code)
                self.assertFalse(actual["complete"])

    def test_malformed_sidecar_is_an_explicit_nonpassing_result(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary, "sidecar.json")
            for content in ("{", "{}", "[]", '{"schema_version": true}'):
                path.write_text(content, encoding="utf-8")
                actual = manifest.load_run_evidence(path)
                self.assertFalse(actual["completed"])
                self.assertFalse(actual["manifest"]["complete"])

    def test_phase_corruption_cannot_certify_matching_case_ids(self):
        expected = manifest.make_manifest(["test_a.py::test_a"])
        for change in ("missing", "duplicate", "contradiction", "bad_duration", "bad_schema"):
            observed = outcome("test_a.py::test_a")
            if change == "missing":
                observed["phases"].pop()
            elif change == "duplicate":
                observed["phases"].append(dict(observed["phases"][1]))
            elif change == "contradiction":
                observed["phases"][1]["outcome"] = "fail"
            elif change == "bad_duration":
                observed["phases"][0]["duration_seconds"] = float("nan")
            else:
                observed["subtests"] = [None]
            with self.subTest(change=change):
                actual = manifest.reconcile_cases(expected, [observed], completed=True, exit_code=0)
                self.assertFalse(actual["complete"])


class PytestPluginTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="tdq-cases-")
        self.addCleanup(temporary.cleanup)
        self.project = Path(temporary.name)

    def run_fixture(self, source, workers=0, extra_args=()):
        (self.project / "test_cases.py").write_text(source, encoding="utf-8")
        path = self.project / f"evidence-{workers}.json"
        self.xml_path = self.project / f"junit-{workers}.xml"
        environment = dict(os.environ, PYTHONPATH=os.path.join(ROOT, "scripts"),
                           TDQ_TEST_MANIFEST_OUTPUT=str(path),
                           TDQ_TEST_SCOPE="full", TDQ_TEST_FINGERPRINT="fixture-input",
                           PYTEST_DISABLE_PLUGIN_AUTOLOAD="1", TDQ_LOG="0")
        command = [sys.executable, "-m", "pytest", "-q", "-p", "tdq_test_manifest",
                   "-p", "xdist.plugin", "-n", str(workers), "--dist=loadfile",
                   "--junitxml=" + str(self.xml_path), *extra_args, str(self.project)]
        process = subprocess.run(command, cwd=self.project, env=environment,
                                 capture_output=True, text=True, encoding="utf-8",
                                 errors="replace", timeout=45)
        self.assertTrue(path.exists(), process.stdout + process.stderr)
        return process, manifest.load_run_evidence(path)

    def test_real_mixed_param_subtest_skip_xfail_xpass_serial_and_parallel(self):
        source = '''import pytest, unittest
@pytest.mark.parametrize("value", ["a::b", "c.d"])
def test_param(value): assert value
@pytest.mark.skip(reason="requires offline capability")
def test_skip(): pass
@pytest.mark.xfail(reason="known failure")
def test_xfail(): assert False
@pytest.mark.xfail(reason="unexpected fix", strict=False)
def test_xpass(): pass
class Sample(unittest.TestCase):
    def test_sub(self):
        for value in [1, 2]:
            with self.subTest(value=value): self.assertGreater(value, 0)
'''
        inventories = []
        for workers in (0, 2):
            process, evidence = self.run_fixture(source, workers)
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
            parsed = results.from_junit_xml(self.xml_path.read_text(encoding="utf-8"),
                evidence["exit_code"], ["test_cases.py"], manifest=evidence["manifest"],
                outcomes=evidence["outcomes"], completed=evidence["completed"])
            self.assertEqual(parsed["status"], "FAIL", parsed)
            self.assertTrue(parsed["coverage"]["complete"], parsed)
            self.assertEqual(parsed["tests_run"], 6)
            self.assertEqual(parsed["coverage"]["counts"],
                             {"pass": 3, "fail": 0, "error": 0,
                              "skip": 1, "xfail": 1, "xpass": 1})
            children = [c for c in evidence["outcomes"] if c["case_id"].endswith("test_sub")]
            self.assertEqual(len(children[0]["subtests"]), 2)
            inventories.append(evidence["manifest"]["case_ids"])
        self.assertEqual(inventories[0], inventories[1])

    def test_real_blank_skip_is_incomplete_and_cannot_certify_reuse(self):
        for expression, valid in (("pytest.skip()", False),
                                  ("pytest.skip('  ')", False),
                                  ("raise __import__('unittest').SkipTest('')", False),
                                  ("raise __import__('unittest').SkipTest('optional device unavailable')", True),
                                  ("pytest.skip('reason: offline capability unavailable')", True)):
            with self.subTest(expression=expression):
                process, evidence = self.run_fixture("import pytest\ndef test_pass(): assert 1 == 1\n"
                                                    "def test_skip(): " + expression + "\n")
                self.assertEqual(process.returncode, 0)
                parsed = results.from_junit_xml(self.xml_path.read_text(encoding="utf-8"),
                    process.returncode, ["test_cases.py"], manifest=evidence["manifest"],
                    outcomes=evidence["outcomes"], completed=evidence["completed"])
                self.assertEqual(parsed["status"], "PASS" if valid else "INCOMPLETE", parsed)
                self.assertEqual(parsed["details_complete"], valid)
                forged = deepcopy(parsed)
                forged.update(status="PASS", details_complete=True)
                forged["coverage"]["complete"] = True
                self.assertEqual(receipts._valid_terminal_result(forged, evidence["manifest"], False), valid)

    def test_subtest_metadata_matches_serial_and_two_workers(self):
        message = 'message "quoted" \\ path'
        values = ["marketplace.json", "'quoted'", r"directory\file", 17,
                  [1, "'two'", r"x\y"], {"nested": [r"a\b", "'value'"]}]
        source = f'''import pytest, unittest
MESSAGE = {message!r}
VALUES = {values!r}
def test_values(subtests):
    for value in VALUES:
        with subtests.test(msg=MESSAGE, value=value): pass
class Sample(unittest.TestCase):
    def test_unittest_values(self):
        for value in VALUES:
            with self.subTest(msg=MESSAGE, value=value): pass
def test_children(request):
    for state in ("pass", "fail", "skip", "xfail"):
        with request.getfixturevalue("subtests").test(msg=MESSAGE, state=state):
            if state == "fail": assert False, "child failure"
            if state == "skip": pytest.skip("optional child capability")
            if state == "xfail": pytest.xfail("known child issue")
@pytest.mark.skip(reason="optional parent capability")
def test_skip(): pass
@pytest.mark.xfail(reason="known parent issue")
def test_xfail(): assert False
@pytest.mark.xfail(reason="unexpected parent fix", strict=False)
def test_xpass(): pass
'''
        observations = []
        for workers in (0, 2):
            process, evidence = self.run_fixture(source, workers)
            self.assertEqual(process.returncode, 1, process.stdout + process.stderr)
            coverage = manifest.reconcile_cases(
                evidence["manifest"], evidence["outcomes"],
                completed=evidence["completed"], exit_code=evidence["exit_code"])
            self.assertTrue(coverage["complete"], coverage)
            self.assertEqual(coverage["counts"], {
                "pass": 2, "fail": 1, "error": 0,
                "skip": 1, "xfail": 1, "xpass": 1})
            observations.append({case["case_id"].split("::")[-1]: case
                                 for case in evidence["outcomes"]})
        for cases in observations:
            for case in cases.values():
                for report in case["phases"] + case["subtests"]:
                    report.pop("duration_seconds")
        self.assertEqual(observations[0], observations[1])
        for name in ("test_values", "test_unittest_values"):
            case = observations[0][name]
            self.assertTrue(all("subtest" not in phase for phase in case["phases"]))
            self.assertEqual([child["phase"] for child in case["subtests"]],
                             ["call"] * len(values))
            self.assertEqual([child["subtest"] for child in case["subtests"]],
                             [{"message": message, "parameters": {"value": repr(value)}}
                              for value in values])
        children = observations[0]["test_children"]["subtests"]
        self.assertEqual([child["outcome"] for child in children],
                         ["pass", "fail", "skip", "xfail"])
        self.assertEqual([child["subtest"] for child in children],
                         [{"message": message, "parameters": {"state": repr(state)}}
                          for state in ("pass", "fail", "skip", "xfail")])

    def test_real_setup_teardown_and_subtest_failures_are_preserved(self):
        source = '''import pytest, unittest
@pytest.fixture
def broken(): raise RuntimeError("setup failure")
@pytest.fixture
def finalizer():
    yield
    raise RuntimeError("teardown failure")
def test_setup(broken): pass
def test_teardown(finalizer): pass
class Sample(unittest.TestCase):
    def test_sub(self):
        with self.subTest(value=1): self.fail("child failed")
'''
        process, evidence = self.run_fixture(source)
        self.assertEqual(process.returncode, 1)
        parsed = results.from_junit_xml(self.xml_path.read_text(encoding="utf-8"),
            evidence["exit_code"], ["test_cases.py"], manifest=evidence["manifest"],
            outcomes=evidence["outcomes"], completed=evidence["completed"])
        self.assertEqual(parsed["status"], "ERROR")
        self.assertEqual(parsed["tests_run"], 3)
        self.assertEqual(parsed["coverage"]["counts"]["error"], 2)
        self.assertEqual(parsed["coverage"]["counts"]["fail"], 1)
        self.assertTrue(parsed["details_complete"], parsed)

    def test_real_collection_error_never_certifies_pass(self):
        _, evidence = self.run_fixture("raise RuntimeError('broken collection')")
        self.assertFalse(evidence["manifest"]["complete"])
        parsed = results.from_case_evidence(evidence["manifest"], evidence["outcomes"],
                                            evidence["exit_code"], ["test_cases.py"],
                                            completed=evidence["completed"])
        self.assertEqual(parsed["status"], "ERROR")
        self.assertFalse(parsed["details_complete"])

    def test_nested_pytest_does_not_inherit_output_destination(self):
        source = '''import os, subprocess, sys
def test_outer(tmp_path):
    assert "TDQ_TEST_MANIFEST_OUTPUT" not in os.environ
    nested = tmp_path / "test_inner.py"
    nested.write_text("def test_inner(): pass\\n")
    result = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p",
                             "tdq_test_manifest", str(nested)], capture_output=True)
    assert result.returncode == 0
'''
        for workers in (0, 2):
            process, evidence = self.run_fixture(source, workers)
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
            self.assertEqual(evidence["manifest"]["case_ids"], ["test_cases.py::test_outer"])
            self.assertTrue(evidence["completed"], evidence)

    def test_workers_with_different_collection_fail_closed(self):
        source = '''import os, pytest
@pytest.mark.parametrize("value", [os.environ.get("PYTEST_XDIST_WORKER", "main")])
def test_value(value): pass
'''
        process, evidence = self.run_fixture(source, workers=2)
        self.assertNotEqual(process.returncode, 0)
        self.assertFalse(evidence["completed"])
        self.assertTrue(any(item["kind"] == "collection_mismatch"
                            for item in evidence["manifest"]["diagnostics"]))

    def test_strict_xpass_retains_explicit_xpass_outcome(self):
        _, evidence = self.run_fixture('''import pytest
@pytest.mark.xfail(reason="unexpected fix", strict=True)
def test_value(): pass
''')
        self.assertEqual(evidence["outcomes"][0]["outcome"], "xpass")
        parsed = results.from_junit_xml(self.xml_path.read_text(encoding="utf-8"),
            evidence["exit_code"], ["test_cases.py"], manifest=evidence["manifest"],
            outcomes=evidence["outcomes"], completed=evidence["completed"])
        self.assertEqual(parsed["status"], "FAIL")
        self.assertTrue(parsed["details_complete"], parsed)

    def test_real_call_failure_plus_teardown_and_multiple_subtests_match_xml(self):
        source = '''import pytest, unittest
@pytest.fixture
def finalizer():
    yield
    raise RuntimeError("teardown broke")
def test_both(finalizer): assert False, "call broke"
class Sample(unittest.TestCase):
    def test_children(self):
        for value in (1, 2):
            with self.subTest(value=value): self.fail("child failed")
        with self.subTest(value=3): self.skipTest("child capability")
'''
        process, evidence = self.run_fixture(source)
        parsed = results.from_junit_xml(self.xml_path.read_text(encoding="utf-8"),
            process.returncode, ["test_cases.py"], manifest=evidence["manifest"],
            outcomes=evidence["outcomes"], completed=evidence["completed"])
        self.assertEqual(parsed["status"], "ERROR", parsed)
        self.assertTrue(parsed["details_complete"], parsed)
        self.assertTrue(parsed["coverage"]["complete"], parsed)
