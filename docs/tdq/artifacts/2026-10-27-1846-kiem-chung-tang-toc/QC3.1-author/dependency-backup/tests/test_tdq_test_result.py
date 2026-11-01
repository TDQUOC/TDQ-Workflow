"""Test result contracts using real unittest results and minimal JUnit XML."""
import io
from copy import deepcopy
import os
import sys
import unittest
import xml.etree.ElementTree as ET

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tdq_test_result as results  # noqa: E402
import tdq_test_manifest as manifests  # noqa: E402


def junit(cases, **counters):
    suite = ET.fromstring("<testsuite>" + cases + "</testsuite>")
    counts = {"tests": len(list(suite)), "failures": 0,
              "errors": 0, "skipped": 0}
    for case in suite:
        for tag, counter in (("failure", "failures"), ("error", "errors"),
                             ("skipped", "skipped")):
            counts[counter] += len(case.findall(tag))
    counts.update(counters)
    suite.attrib.update({key: str(value) for key, value in counts.items()})
    return ET.tostring(suite, encoding="unicode")


def run_case(method, *, module="test_sample", setup=None):
    attributes = {"test_value": method, "__module__": module}
    if setup is not None:
        attributes["setUpClass"] = classmethod(setup)
    case = type("Sample", (unittest.TestCase,), attributes)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(case)
    return unittest.TextTestRunner(stream=io.StringIO()).run(suite)


def fail_test(case):
    case.assertEqual(1, 2)


class UnittestResultTest(unittest.TestCase):
    def parse(self, result, inventory=("test_sample.py",), **kwargs):
        return results.from_unittest_result(result, inventory, **kwargs)

    def test_success_count_and_contract(self):
        actual = self.parse(run_case(lambda case: None))
        self.assertEqual(actual, {
            "status": "PASS", "backend": "unittest", "tests_run": 1,
            "skipped": 0, "failed_modules": [], "failures": [],
            "unmapped_failures": [], "details_complete": True,
            "exit_code": 0, "reason": "Executed tests completed successfully",
        })

    def test_assertion_failure_keeps_module(self):
        actual = self.parse(run_case(fail_test))
        self.assertEqual(actual["status"], "FAIL")
        self.assertEqual(actual["failed_modules"], ["test_sample.py"])
        self.assertEqual(actual["failures"][0]["kind"], "failure")
        self.assertIn("1 != 2", actual["failures"][0]["message"])

    def test_runtime_error(self):
        def broken(case):
            raise ValueError("broken fixture")
        actual = self.parse(run_case(broken))
        self.assertEqual(actual["status"], "ERROR")
        self.assertIn("broken fixture", actual["failures"][0]["message"])

    def test_unexpected_success_is_fail(self):
        method = unittest.expectedFailure(lambda case: None)
        actual = self.parse(run_case(method))
        self.assertEqual(actual["status"], "FAIL")
        self.assertEqual(actual["failures"][0]["kind"], "unexpected_success")
        self.assertEqual(actual["failed_modules"], ["test_sample.py"])

    def test_skip_only_is_incomplete(self):
        method = unittest.skip("fixture skip")(lambda case: None)
        actual = self.parse(run_case(method))
        self.assertEqual((actual["status"], actual["tests_run"],
                          actual["skipped"]), ("INCOMPLETE", 1, 1))

    def test_empty_suite_is_incomplete(self):
        self.assertEqual(self.parse(unittest.TestResult())["status"],
                         "INCOMPLETE")

    def test_failed_import_is_error_even_when_unmapped(self):
        suite = unittest.defaultTestLoader.loadTestsFromName(
            "test_missing_tdq_result_fixture")
        result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
        actual = self.parse(result)
        self.assertEqual(actual["status"], "ERROR")
        self.assertEqual(actual["unmapped_failures"][0]["id"],
                         "test_missing_tdq_result_fixture")
        self.assertFalse(actual["details_complete"])
        mapped = self.parse(result, ["test_missing_tdq_result_fixture.py"])
        self.assertEqual(mapped["failed_modules"],
                         ["test_missing_tdq_result_fixture.py"])

    def test_setup_class_error_maps_nested_module(self):
        def broken_setup(cls):
            raise RuntimeError("setup broke")
        result = run_case(lambda case: None, module="pkg.test_nested",
                          setup=broken_setup)
        actual = self.parse(result, ["pkg/test_nested.py"])
        self.assertEqual(actual["status"], "ERROR")
        self.assertEqual(actual["tests_run"], 0)
        self.assertEqual(actual["failed_modules"], ["pkg/test_nested.py"])

    def test_subtest_parameters_keep_module(self):
        def subtest_failure(case):
            with case.subTest(value="a b::c"):
                case.fail("subtest failed")
        actual = self.parse(run_case(subtest_failure))
        self.assertEqual(actual["failed_modules"], ["test_sample.py"])
        self.assertEqual(actual["tests_run"], 1)

    def test_ambiguous_basename_stays_unmapped(self):
        actual = self.parse(run_case(fail_test),
                            ["a/test_sample.py", "b/test_sample.py"])
        self.assertEqual(actual["status"], "FAIL")
        self.assertEqual(actual["failed_modules"], [])
        self.assertEqual(len(actual["unmapped_failures"]), 1)

    def test_exit_contradiction_does_not_pass(self):
        actual = self.parse(run_case(lambda case: None), exit_code=1)
        self.assertEqual(actual["status"], "INCOMPLETE")
        self.assertFalse(actual["details_complete"])
        actual = self.parse(run_case(fail_test), exit_code=0)
        self.assertEqual(actual["status"], "FAIL")
        self.assertFalse(actual["details_complete"])

    def test_invalid_counts_and_interruption_do_not_pass(self):
        for count in (True, -1, None, float("nan")):
            with self.subTest(count=count):
                result = run_case(lambda case: None)
                result.testsRun = count
                self.assertEqual(self.parse(result)["status"], "INCOMPLETE")
        result = run_case(lambda case: None)
        result.stop()
        self.assertEqual(self.parse(result)["status"], "INCOMPLETE")


class JunitResultTest(unittest.TestCase):
    PASS_CASE = '<testcase classname="test_sample.Sample" name="test_ok" />'
    FAIL_CASE = ('<testcase classname="test_sample.Sample" '
                 'name="test_value[x-y]">'
                 '<failure message="assertion">1 != 2</failure></testcase>')

    def parse(self, xml, exit_code=0, inventory=("test_sample.py",), **kwargs):
        return results.from_junit_xml(xml, exit_code, inventory, **kwargs)

    def test_success_with_real_nodes(self):
        actual = self.parse(junit(self.PASS_CASE))
        self.assertEqual(actual["status"], "PASS")
        self.assertEqual(actual["tests_run"], 1)
        self.assertTrue(actual["details_complete"])

    def test_classname_without_file_and_parameter_id(self):
        actual = self.parse(junit(self.FAIL_CASE), 1)
        self.assertEqual(actual["status"], "FAIL")
        self.assertEqual(actual["failed_modules"], ["test_sample.py"])
        self.assertEqual(actual["failures"][0]["id"],
                         "test_sample.Sample.test_value[x-y]")
        self.assertTrue(actual["details_complete"])

    def test_summary_node_id_matches_xml_without_duplicate(self):
        actual = self.parse(junit(self.FAIL_CASE), 1, output=(
            "FAILED tests/test_sample.py::Sample::test_value[x-y]"
            " - assertion"))
        self.assertEqual(actual["failed_modules"], ["test_sample.py"])
        self.assertEqual(len(actual["failures"]), 1)
        self.assertTrue(actual["details_complete"])

    def test_file_and_windows_separators_normalize_inventory(self):
        xml = junit('<testcase file="C:\\repo\\tests\\nested\\test_sample.py" '
                    'name="test_bad"><failure>broken</failure></testcase>')
        actual = self.parse(xml, 1, [".\\nested\\test_sample.py"])
        self.assertEqual(actual["failed_modules"], ["nested/test_sample.py"])

    def test_longest_full_module_prefix_wins(self):
        xml = junit('<testcase classname="pkg.test_sample.case.More" name="t">'
                    '<failure>broken</failure></testcase>')
        actual = self.parse(xml, 1, ["pkg/test_sample.py",
                                    "pkg/test_sample/case.py"])
        self.assertEqual(actual["failed_modules"], ["pkg/test_sample/case.py"])

    def test_prefix_match_has_identifier_boundary(self):
        xml = junit('<testcase classname="test_sample_extra.C" name="t">'
                    '<failure>broken</failure></testcase>')
        actual = self.parse(xml, 1)
        self.assertEqual(actual["failed_modules"], [])
        self.assertEqual(len(actual["unmapped_failures"]), 1)

    def test_ambiguous_basename_remains_unmapped(self):
        actual = self.parse(junit(self.FAIL_CASE), 1,
                            ["a/test_sample.py", "b/test_sample.py"])
        self.assertEqual(actual["status"], "FAIL")
        self.assertFalse(actual["details_complete"])
        self.assertEqual(len(actual["unmapped_failures"]), 1)

    def test_collection_error_with_no_classname(self):
        xml = junit('<testcase name="tests/test_sample.py">'
                    '<error message="collection failure">ImportError</error>'
                    '</testcase>')
        actual = self.parse(xml, 2)
        self.assertEqual(actual["status"], "ERROR")
        self.assertEqual(actual["failed_modules"], ["test_sample.py"])

    def test_setup_error_and_assertion_are_both_retained(self):
        error_case = ('<testcase classname="test_sample.Sample" '
                      'name="test_setup">'
                      '<error>setup failure</error></testcase>')
        actual = self.parse(junit(self.FAIL_CASE + error_case), 1)
        self.assertEqual(actual["status"], "ERROR")
        self.assertEqual(len(actual["failures"]), 2)
        self.assertEqual(actual["tests_run"], 2)

    def test_skip_only_and_empty_are_incomplete(self):
        skip = ('<testcase classname="test_sample" name="test_skip">'
                '<skipped message="skip" /></testcase>')
        actual = self.parse(junit(skip))
        self.assertEqual((actual["status"], actual["skipped"]),
                         ("INCOMPLETE", 1))
        self.assertEqual(self.parse(junit(""))["status"], "INCOMPLETE")

    def test_missing_malformed_and_wrong_xml_never_pass(self):
        for xml in (None, "", "<testsuite>", "<other/>", "<testsuites/>"):
            with self.subTest(xml=xml):
                actual = self.parse(xml)
                self.assertEqual(actual["status"], "INCOMPLETE")
                self.assertFalse(actual["details_complete"])

    def test_missing_report_retains_failed_node_id_from_output(self):
        actual = self.parse(None, 1, output=(
            "FAILED tests/test_sample.py::Sample::test_value[x-y]"
            " - AssertionError"))
        self.assertEqual(actual["status"], "FAIL")
        self.assertEqual(actual["failed_modules"], ["test_sample.py"])
        self.assertFalse(actual["details_complete"])

    def test_malformed_report_retains_output_error(self):
        actual = self.parse("<broken", 2, output=(
            "ERROR tests/test_sample.py - ImportError: bad import"))
        self.assertEqual(actual["status"], "ERROR")
        self.assertEqual(actual["failed_modules"], ["test_sample.py"])
        self.assertFalse(actual["details_complete"])

    def test_exit_codes_override_green_report(self):
        expected = {1: "FAIL", 2: "INCOMPLETE", 3: "ERROR", 4: "ERROR",
                    5: "INCOMPLETE", -9: "INCOMPLETE", None: "INCOMPLETE"}
        for exit_code, status in expected.items():
            with self.subTest(exit_code=exit_code):
                actual = self.parse(junit(self.PASS_CASE), exit_code)
                self.assertEqual(actual["status"], status)
                self.assertFalse(actual["details_complete"])

    def test_runner_error_does_not_erase_known_assertion(self):
        actual = self.parse(junit(self.FAIL_CASE), 3)
        self.assertEqual(actual["status"], "ERROR")
        self.assertEqual(actual["failed_modules"], ["test_sample.py"])
        self.assertEqual(len(actual["failures"]), 2)

    def test_zero_exit_cannot_erase_failure(self):
        actual = self.parse(junit(self.FAIL_CASE))
        self.assertEqual(actual["status"], "FAIL")
        self.assertFalse(actual["details_complete"])

    def test_false_missing_or_mismatched_counters_never_pass(self):
        for value in ("true", "NaN", "-1", "1.0", "", "2"):
            with self.subTest(value=value):
                actual = self.parse(junit(self.PASS_CASE, tests=value))
                self.assertEqual(actual["status"], "INCOMPLETE")
                self.assertFalse(actual["details_complete"])
        xml = junit(self.PASS_CASE).replace(' tests="1"', "")
        self.assertEqual(self.parse(xml)["status"], "INCOMPLETE")

    def test_all_declared_counters_are_checked(self):
        for counter in ("failures", "errors", "skipped"):
            with self.subTest(counter=counter):
                xml = junit(self.PASS_CASE, **{counter: 1})
                self.assertEqual(self.parse(xml)["status"], "INCOMPLETE")

    def test_bad_counter_does_not_erase_known_failure(self):
        actual = self.parse(junit(self.FAIL_CASE, failures=0), 1)
        self.assertEqual(actual["status"], "FAIL")
        self.assertFalse(actual["details_complete"])

    def test_nested_suite_totals_are_verified_without_double_count(self):
        xml = ('<testsuites tests="1">' + junit(self.PASS_CASE)
               + '</testsuites>')
        actual = self.parse(xml)
        self.assertEqual((actual["status"], actual["tests_run"]), ("PASS", 1))
        self.assertEqual(self.parse(xml.replace('tests="1"', 'tests="2"', 1))[
            "status"], "INCOMPLETE")

    def test_conflicting_outcomes_keep_error(self):
        xml = junit('<testcase classname="test_sample" name="test_bad">'
                    '<skipped/><error>broken</error></testcase>')
        actual = self.parse(xml, 1)
        self.assertEqual(actual["status"], "ERROR")
        self.assertFalse(actual["details_complete"])

    def test_green_text_cannot_replace_xml(self):
        actual = self.parse(None, output="99 passed in 1.00s")
        self.assertEqual(actual["status"], "INCOMPLETE")
        self.assertEqual(actual["tests_run"], 0)

    def test_output_adds_unreported_error_to_valid_xml(self):
        actual = self.parse(junit(self.PASS_CASE), 0, output=(
            "ERROR tests/test_sample.py::test_other - worker error"))
        self.assertEqual(actual["status"], "ERROR")
        self.assertFalse(actual["details_complete"])

    def test_interruption_exit_is_not_assumed_collection_error(self):
        actual = self.parse(None, 2, output="KeyboardInterrupt")
        self.assertEqual(actual["status"], "INCOMPLETE")
        self.assertEqual(actual["failures"], [])
        actual = self.parse(junit(self.FAIL_CASE), 2)
        self.assertEqual(actual["status"], "FAIL")
        self.assertEqual(actual["failed_modules"], ["test_sample.py"])

    def test_large_counter_is_incomplete_instead_of_crashing(self):
        actual = self.parse(junit(self.PASS_CASE, tests="9" * 5000))
        self.assertEqual(actual["status"], "INCOMPLETE")

    def test_missing_name_cannot_certify_execution(self):
        self.assertEqual(self.parse(junit('<testcase/>'))["status"],
                         "INCOMPLETE")

    def test_unknown_outcome_cannot_be_treated_as_success(self):
        xml = junit('<testcase classname="test_sample" name="test_wrong">'
                    '<unknown_failure>bad</unknown_failure></testcase>')
        self.assertEqual(self.parse(xml)["status"], "INCOMPLETE")

    def test_collection_xml_and_summary_keep_one_failure(self):
        xml = junit('<testcase name="tests/test_sample.py">'
                    '<error>bad import</error></testcase>')
        actual = self.parse(xml, 2, output=(
            "ERROR tests/test_sample.py - bad import"))
        self.assertEqual(actual["status"], "ERROR")
        self.assertEqual(len(actual["failures"]), 1)

    def test_invalid_exit_types_cannot_certify_execution(self):
        for exit_code in (True, False, float("nan")):
            with self.subTest(exit_code=exit_code):
                actual = self.parse(junit(self.PASS_CASE), exit_code)
                self.assertEqual(actual["status"], "INCOMPLETE")


class EmptyResultTest(unittest.TestCase):
    def test_noop_is_skip_without_a_pass(self):
        actual = results.empty_result("none", "Docs only", status="SKIP",
                                      exit_code=0)
        self.assertEqual(actual["status"], "SKIP")
        self.assertEqual(actual["tests_run"], 0)

    def test_timeout_and_runner_error_stay_nonpassing(self):
        actual = results.empty_result("pytest", "Timed out")
        self.assertEqual(actual["status"], "INCOMPLETE")
        self.assertFalse(actual["details_complete"])
        actual = results.empty_result("unittest", "Runner broke",
                                      status="ERROR")
        self.assertEqual(actual["status"], "ERROR")

    def test_empty_constructor_rejects_pass(self):
        with self.assertRaises(ValueError):
            results.empty_result("pytest", "No tests", status="PASS")


class CaseEvidenceTest(unittest.TestCase):
    def parse(self, status, *, exit_code=0):
        manifest = manifests.make_manifest(["test_sample.py::Sample::test_ok"])
        outcomes = [{"case_id": manifest["case_ids"][0], "outcome": status,
                     "reason": "fixture reason", "capability": None,
                     "phases": [{"phase": phase, "outcome": status if phase == "call" else "pass",
                                 "reason": "fixture reason", "duration_seconds": 0.0}
                                for phase in ("setup", "call", "teardown")], "subtests": []}]
        return results.from_case_evidence(manifest, outcomes, exit_code, ["test_sample.py"])

    def test_additive_keys_keep_legacy_contract_and_explicit_accounting(self):
        actual = self.parse("pass")
        self.assertEqual(actual["status"], "PASS")
        self.assertTrue(actual["details_complete"])
        self.assertEqual(actual["tests_run"], 1)
        self.assertEqual(actual["action"], "executed")
        self.assertIsNone(actual["source_receipt_id"])
        self.assertEqual(actual["timings"]["wait_seconds"], 0)
        self.assertTrue(actual["coverage"]["complete"])

    def test_skip_and_xfail_only_do_not_certify_pass(self):
        for status in ("skip", "xfail"):
            with self.subTest(status=status):
                actual = self.parse(status)
                self.assertEqual(actual["status"], "INCOMPLETE")
                self.assertEqual(actual["coverage"]["counts"]["pass"], 0)

    def test_xpass_is_failure_even_when_pytest_exit_is_zero(self):
        actual = self.parse("xpass")
        self.assertEqual(actual["status"], "FAIL")
        self.assertTrue(actual["details_complete"], actual)
        self.assertEqual(actual["failures"][0]["kind"], "unexpected_success")

    def test_missing_evidence_cannot_become_pass_via_green_junit(self):
        manifest = manifests.make_manifest(["test_sample.py::Sample::test_ok"])
        actual = results.from_junit_xml(junit(JunitResultTest.PASS_CASE), 0,
                                        ["test_sample.py"], manifest=manifest, outcomes=[])
        self.assertEqual(actual["status"], "INCOMPLETE")
        self.assertFalse(actual["coverage"]["complete"])

    def test_interrupted_sidecar_keeps_known_output_failure(self):
        manifest = manifests.make_manifest(["tests/test_backend.py::T::test_ok"],
                                            selectors=["tests"], scope="full")
        for label, expected in (("FAILED", "FAIL"), ("ERROR", "ERROR")):
            with self.subTest(label=label):
                actual = results.from_junit_xml(
                    None, None, ["test_backend.py"],
                    output=f"{label} tests/test_backend.py::T::test_bad - known failure",
                    manifest=manifest, outcomes=[], completed=False)
                self.assertEqual(actual["status"], expected)
                self.assertFalse(actual["details_complete"])
                self.assertFalse(actual["coverage"]["complete"])
                self.assertEqual(actual["failed_modules"], ["test_backend.py"])
                self.assertIn("known failure", actual["failures"][0]["message"])

    def test_actual_error_dominates_supplemental_assertion_failure(self):
        error = self.parse("error", exit_code=1)
        actual = results.from_junit_xml(
            None, None, ["test_sample.py"],
            output="FAILED tests/test_sample.py::Sample::test_other - known assertion",
            manifest=error["manifest"], outcomes=error["case_outcomes"], completed=False)
        self.assertEqual(actual["status"], "ERROR")
        self.assertEqual({failure["kind"] for failure in actual["failures"]},
                         {"error", "failure"})
        self.assertFalse(actual["details_complete"])

    def test_junit_failure_cannot_be_hidden_by_passing_sidecar(self):
        passing = self.parse("pass")
        xml = junit('<testcase classname="test_sample.Sample" name="test_ok">'
                    '<failure>unreported failure</failure></testcase>')
        actual = results.from_junit_xml(xml, 1, ["test_sample.py"],
                                        manifest=passing["manifest"],
                                        outcomes=passing["case_outcomes"])
        self.assertEqual(actual["status"], "FAIL")
        self.assertFalse(actual["details_complete"])

    def test_legacy_unittest_expected_failure_is_not_executed_pass(self):
        actual = results.from_unittest_result(
            run_case(unittest.expectedFailure(fail_test)), ["test_sample.py"])
        self.assertEqual(actual["status"], "INCOMPLETE")

    def test_malformed_outcome_never_throws_or_certifies_pass(self):
        manifest = manifests.make_manifest(["test_sample.py::test_ok"])
        for outcome in (None, [], {"outcome": []}, {"case_id": 7, "outcome": "error"}):
            with self.subTest(outcome=outcome):
                actual = results.from_case_evidence(manifest, [outcome], 0, ["test_sample.py"])
                self.assertNotEqual(actual["status"], "PASS")


class JunitSidecarParityTest(unittest.TestCase):
    def sidecar(self, names=("test_ok",), status="pass"):
        template = CaseEvidenceTest().parse(status)
        outcomes = []
        for name in names:
            case = deepcopy(template["case_outcomes"][0])
            case["case_id"] = "test_sample.py::Sample::" + name
            outcomes.append(case)
        return manifests.make_manifest([case["case_id"] for case in outcomes]), outcomes

    def parse(self, xml, names=("test_ok",), status="pass", exit_code=0):
        manifest, outcomes = self.sidecar(names, status)
        return results.from_junit_xml(xml, exit_code, ["test_sample.py"],
                                     manifest=manifest, outcomes=outcomes)

    def test_missing_extra_duplicate_or_different_xml_cases_are_incomplete(self):
        cases = JunitResultTest.PASS_CASE
        for xml, names in ((junit(cases), ("test_ok", "test_other")),
                           (junit(cases * 2), ("test_ok",)),
                           (junit(cases.replace("test_ok", "test_other")), ("test_ok",)),
                           (junit(cases.replace("Sample", "Other")), ("test_ok",))):
            with self.subTest(xml=xml, names=names):
                result = self.parse(xml, names)
                self.assertEqual(result["status"], "INCOMPLETE", result)
                self.assertFalse(result["details_complete"])
                self.assertFalse(result["coverage"]["complete"])

    def test_skip_or_xfail_xml_cannot_certify_sidecar_pass(self):
        for kind in ("pytest.skip", "pytest.xfail"):
            xml = junit('<testcase classname="test_sample.Sample" name="test_ok">'
                        f'<skipped type="{kind}"/></testcase>')
            result = self.parse(xml)
            self.assertEqual(result["status"], "INCOMPLETE", result)
            self.assertFalse(result["coverage"]["complete"])

    def test_xml_pass_cannot_hide_skipped_sidecar_case_in_mixed_run(self):
        manifest, outcomes = self.sidecar(("test_ok", "test_other"))
        outcomes[1]["outcome"] = "skip"
        outcomes[1]["phases"][1]["outcome"] = "skip"
        xml = junit(JunitResultTest.PASS_CASE + JunitResultTest.PASS_CASE.replace("test_ok", "test_other"))
        result = results.from_junit_xml(xml, 0, ["test_sample.py"], manifest=manifest, outcomes=outcomes)
        self.assertEqual(result["status"], "INCOMPLETE", result)

    def test_parameter_text_is_exact_not_a_prefix_or_dotted_alias(self):
        for name in ("test_ok[a::b.c]", "test_ok[a/b]", "test_ok[a\\b]"):
            xml = junit('<testcase classname="test_sample.Sample" name="' + name + '"/>')
            self.assertEqual(self.parse(xml, (name,))["status"], "PASS")
            self.assertEqual(self.parse(xml, (name + "other",))["status"], "INCOMPLETE")

    def test_known_error_dominates_xml_identity_mismatch(self):
        xml = junit(JunitResultTest.PASS_CASE.replace("test_ok", "test_other"))
        result = self.parse(xml, status="error", exit_code=1)
        self.assertEqual(result["status"], "ERROR")
        self.assertTrue(result["failures"])
        self.assertFalse(result["coverage"]["complete"])

    def test_xunit1_file_metadata_must_agree_with_exact_case_identity(self):
        xml = JunitResultTest.PASS_CASE.replace('<testcase ', '<testcase file="C:/repo/tests/test_sample.py" ')
        self.assertEqual(self.parse(junit(xml))["status"], "PASS")
        result = self.parse(junit(xml.replace('tests/test_sample.py', 'tests/test_other.py')))
        self.assertEqual(result["status"], "INCOMPLETE", result)
