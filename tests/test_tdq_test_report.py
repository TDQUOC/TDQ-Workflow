"""Pure timing data and file publication; no calibration, git or test processes."""
from copy import deepcopy
from contextlib import redirect_stderr, redirect_stdout
import hashlib
from html.parser import HTMLParser
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import helper  # noqa: F401 — adds scripts/ to sys.path
import tdq_test_report as reports


def case(identifier, durations=(1.0, 2.0, 3.0), outcome="pass"):
    return {"case_id": identifier, "outcome": outcome,
            "phases": [{"phase": phase, "outcome": "pass", "duration_seconds": value}
                       for phase, value in zip(("setup", "call", "teardown"), durations)],
            "subtests": []}


def result(cases, status="PASS", wall=100.0):
    return {"status": status, "backend": "pytest", "tests_run": len(cases),
            "case_outcomes": cases, "timings": {"wall_seconds": wall}}


class SummaryTest(unittest.TestCase):
    def test_summary_and_renderers_have_no_io(self):
        payload = result([case("tests/test_pure.py::test_ok")])
        before = deepcopy(payload)
        output, errors = io.StringIO(), io.StringIO()
        forbidden = AssertionError("Pure summary/render must not perform IO")
        with mock.patch.dict(os.environ), redirect_stdout(output), redirect_stderr(errors), \
                mock.patch("builtins.open", side_effect=forbidden), \
                mock.patch("subprocess.Popen", side_effect=forbidden):
            os.environ.pop("TDQ_LOG", None)
            summary = reports.summarize_result(payload)
            rendered = [reports.render_json(summary), reports.render_markdown(summary),
                        reports.render_html(summary)]
        self.assertEqual(payload, before)
        self.assertTrue(all(rendered))
        self.assertEqual(output.getvalue(), "")
        self.assertEqual(errors.getvalue(), "")

    def test_phase_sum_ignores_subtests_and_wall_and_does_not_mutate(self):
        row = case("tests/test_a.py::test_a")
        row["subtests"] = [{"phase": "call", "duration_seconds": 500.0}]
        payload = result([row])
        before = deepcopy(payload)
        summary = reports.summarize_result(payload)
        self.assertEqual(summary["top_cases"][0]["duration_seconds"], 6.0)
        self.assertEqual(summary["top_modules"][0]["duration_seconds"], 6.0)
        self.assertEqual(summary["execution_phase_seconds"], 6.0)
        self.assertEqual(summary["wall_seconds"], 100.0)
        self.assertEqual(payload, before)

    def test_top20_ties_sort_by_full_identifier(self):
        rows = [case(f"tests/test_{index:02d}.py::test_x") for index in reversed(range(25))]
        summary = reports.summarize_result(result(rows))
        self.assertEqual(len(summary["top_cases"]), 20)
        self.assertEqual([row["case_id"] for row in summary["top_cases"]],
                         sorted(row["case_id"] for row in rows)[:20])
        self.assertEqual([row["module"] for row in summary["top_modules"]],
                         sorted(row["case_id"].split("::")[0] for row in rows)[:20])

    def test_missing_duration_is_unranked_not_zero(self):
        missing = case("tests/test_missing.py::test_x")
        missing["phases"][1].pop("duration_seconds")
        summary = reports.summarize_result(result([missing, case("tests/test_ok.py::test_ok")]))
        self.assertEqual(summary["quality"]["status"], "partial")
        self.assertEqual([row["case_id"] for row in summary["top_cases"]],
                         ["tests/test_ok.py::test_ok"])
        self.assertIsNone(summary["execution_phase_seconds"])
        self.assertTrue(summary["quality"]["unranked_cases"])

    def test_duplicate_id_is_not_added_or_overwritten(self):
        identifier = "tests/test_dup.py::test_x"
        summary = reports.summarize_result(result([
            case(identifier), case(identifier, (10, 20, 30)), case("tests/test_ok.py::test_ok")]))
        self.assertEqual(summary["quality"]["status"], "partial")
        self.assertNotIn(identifier, [row["case_id"] for row in summary["top_cases"]])
        self.assertNotIn("tests/test_dup.py", [row["module"] for row in summary["top_modules"]])

    def test_incomplete_module_is_not_ranked_as_a_complete_total(self):
        missing = case("tests/test_a.py::test_missing")
        missing["phases"][1].pop("duration_seconds")
        summary = reports.summarize_result(result([
            missing, case("tests/test_a.py::test_valid"), case("tests/test_b.py::test_valid")]))
        self.assertEqual(summary["known_execution_phase_seconds"], 12.0)
        self.assertEqual([row["module"] for row in summary["top_modules"]], ["tests/test_b.py"])
        self.assertEqual(summary["quality"]["unranked_modules"][0]["known_duration_seconds"], 6.0)

    def test_invalid_duration_is_unavailable_without_fabricated_zero(self):
        for value in (None, -1, float("nan"), float("inf"), -float("inf"), True, "2", 10 ** 400):
            with self.subTest(kind=type(value).__name__, value=str(value)):
                summary = reports.summarize_result(result([case("tests/test_a.py::test_x", (1, value, 3))]))
                self.assertEqual(summary["quality"]["status"], "unavailable")
                self.assertEqual(summary["top_cases"], [])
                self.assertIsNone(summary["execution_phase_seconds"])
                self.assertIsNone(summary["known_execution_phase_seconds"])
                json.loads(reports.render_json(summary))

    def test_missing_duplicate_and_embedded_subtest_phases_are_unranked(self):
        for kind in ("missing", "duplicate", "embedded", "bad_phase", "not_array"):
            with self.subTest(kind=kind):
                row = case("tests/test_a.py::test_x")
                if kind == "missing":
                    row["phases"].pop()
                elif kind == "duplicate":
                    row["phases"].append(deepcopy(row["phases"][1]))
                elif kind == "embedded":
                    row["phases"][1]["subtest"] = {"parameters": {"value": 1}}
                elif kind == "bad_phase":
                    row["phases"][1]["phase"] = []
                else:
                    row["phases"] = "not phases"
                summary = reports.summarize_result(result([row]))
                self.assertEqual(summary["quality"]["status"], "unavailable")
                self.assertTrue(summary["quality"]["issues"])
                self.assertEqual(summary["top_cases"], [])

    def test_skipped_setup_has_no_invented_call_duration(self):
        row = case("tests/test_a.py::test_skip", outcome="skip")
        row["phases"] = [row["phases"][0], row["phases"][2]]
        row["phases"][0]["outcome"] = "skip"
        summary = reports.summarize_result(result([row]))
        self.assertEqual(summary["quality"]["status"], "complete")
        self.assertEqual(summary["execution_phase_seconds"], 4.0)

    def test_zero_is_valid_only_when_measured_and_wall_is_independent(self):
        summary = reports.summarize_result(result([case("tests/test_a.py::test_x", (0, 0, 0))], wall=-1))
        self.assertEqual(summary["quality"]["status"], "complete")
        self.assertEqual(summary["execution_phase_seconds"], 0.0)
        self.assertIsNone(summary["wall_seconds"])
        self.assertEqual(summary["wall_quality"], "invalid")

    def test_legacy_and_malformed_cases_are_preserved_as_unavailable_quality(self):
        payloads = [{"status": "FAIL", "tests_run": 7}, result([]),
                    result([None, "not a case", {}, {"case_id": "::test_x"}])]
        for payload in payloads:
            with self.subTest(payload=payload):
                summary = reports.summarize_result(payload)
                self.assertEqual(summary["quality"]["status"], "unavailable")
                self.assertIsNone(summary["execution_phase_seconds"])
                self.assertTrue(summary["quality"]["issues"])
                self.assertEqual(summary["result_status"], payload["status"])

    def test_result_status_exit_code_and_json_are_not_replaced_by_quality(self):
        for status, code in (("FAIL", 1), ("ERROR", 2), ("INCOMPLETE", None)):
            with self.subTest(status=status):
                payload = result([case("tests/test_a.py::test_x")], status=status)
                payload["exit_code"] = code
                summary = reports.summarize_result(payload)
                self.assertEqual(summary["quality"]["status"], "complete")
                self.assertEqual(summary["result_status"], status)
                self.assertEqual(summary["result_exit_code"], code)
                self.assertEqual(json.loads(reports.render_json(summary))["result_status"], status)
                self.assertIn(status, reports.render_markdown(summary))
                self.assertIn(">" + status + "<", reports.render_html(summary))

    def test_invalid_input_schema_is_an_error(self):
        for payload in ([], {}, {"status": []}, {"status": "PASS", "schema_version": 99},
                        {"status": "PASS", "schema_version": True}, {"status": "PASS", "case_outcomes": {}}):
            with self.subTest(payload=payload), self.assertRaises(reports.ReportError):
                reports.summarize_result(payload)

    def test_sort_is_stable_and_duration_overflow_is_not_ranked(self):
        rows = [case("tests/test_a.py::b", (1, 2, 3)), case("tests/test_a.py::a", (1, 2, 3)),
                case("tests/test_b.py::slow", (4, 5, 6))]
        self.assertEqual(reports.summarize_result(result(rows)), reports.summarize_result(result(list(reversed(rows)))))
        summary = reports.summarize_result(result([case("tests/test_a.py::huge", (1e308, 1e308, 1e308))]))
        self.assertEqual(summary["quality"]["status"], "unavailable")
        self.assertIsNone(summary["execution_phase_seconds"])


class _Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags, self.ids = [], []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        identifier = dict(attrs).get("id")
        if identifier:
            self.ids.append(identifier)


class RenderTest(unittest.TestCase):
    def test_html_and_markdown_escape_identifiers_outcomes_and_unsafe_links(self):
        identifier = 'tests/<script>alert("secret")</script>.py::test[<img src=x onerror=1>|`\n]'
        payload = result([case(identifier, outcome='<svg onload="x">')], status="FAIL")
        summary = reports.summarize_result(payload)
        summary["input_href"] = "javascript:alert(1)"
        page = reports.render_html(summary)
        parsed = _Page()
        parsed.feed(page)
        self.assertTrue(page.startswith("<!DOCTYPE html>"))
        self.assertNotIn("script", parsed.tags)
        self.assertNotIn("img", parsed.tags)
        self.assertNotIn("svg", parsed.tags)
        self.assertEqual(len(parsed.ids), len(set(parsed.ids)))
        self.assertNotIn('href="javascript:', page)
        self.assertIn("&lt;script&gt;", page)
        self.assertIn("overflow-x:auto", page)
        markdown = reports.render_markdown(summary)
        self.assertNotIn("<script>", markdown)
        self.assertIn("&lt;script&gt;", markdown)
        self.assertIn("\\|", markdown)
        self.assertIn("\\`", markdown)

    def test_default_logging_is_timestamped_metadata_only_and_can_be_disabled(self):
        payload = result([case("tests/SECRET_PAYLOAD.py::test_x")])
        default, quiet = io.StringIO(), io.StringIO()
        with tempfile.TemporaryDirectory(prefix="tdq-report-logging-") as directory:
            source, prefix = Path(directory) / "input.json", Path(directory) / "output"
            source.write_text(json.dumps(payload), encoding="utf-8")
            with mock.patch.dict(os.environ, {}, clear=False), redirect_stderr(default):
                os.environ.pop("TDQ_LOG", None)
                reports.export_report(source, prefix)
            with mock.patch.dict(os.environ, {"TDQ_LOG": "0"}), redirect_stderr(quiet):
                reports.export_report(source, prefix)
        self.assertRegex(default.getvalue(), r"\[\d{4}-\d{2}-\d{2}T")
        self.assertIn("stage=summary", default.getvalue())
        self.assertNotIn("SECRET_PAYLOAD", default.getvalue())
        self.assertEqual(quiet.getvalue(), "")


class ExportTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="tdq-report-unit-")
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name)
        self.source = self.folder / "input #result.json"
        payload = result([case("tests/test_a.py::test_x")], status="FAIL")
        payload["exit_code"] = 1
        self.source.write_text(json.dumps(payload), encoding="utf-8")
        self.original = self.source.read_bytes()
        self.prefix = self.folder / "timing"
        self.paths = {role: self.prefix.with_suffix(suffix)
                      for role, suffix in (("markdown", ".md"), ("html", ".html"), ("json", ".json"))}

    def old_outputs(self):
        values = {}
        for role, path in self.paths.items():
            values[path] = ("previous " + role).encode()
            path.write_bytes(values[path])
        return values

    def assert_old_outputs(self, values):
        self.assertEqual({path: path.read_bytes() for path in values}, values)
        self.assertEqual(list(self.folder.glob(".tdq-report-*")), [])

    def test_one_summary_export_binds_external_sha_and_never_runs_processes(self):
        expected = hashlib.sha256(self.original).hexdigest()
        with mock.patch.object(reports, "summarize_result", wraps=reports.summarize_result) as summarize, \
                mock.patch("subprocess.Popen", side_effect=AssertionError("offline export started a process")):
            exported = reports.export_report(self.source, self.prefix, expected_sha256=expected)
        summarize.assert_called_once()
        self.assertEqual(self.source.read_bytes(), self.original)
        self.assertEqual(exported["result_status"], "FAIL")
        self.assertEqual(exported["input_sha256"], expected)
        data = json.loads(self.paths["json"].read_text(encoding="utf-8"))
        self.assertEqual(data, exported["summary"])
        self.assertEqual(data["result_exit_code"], 1)
        self.assertEqual(data["input_sha256"], expected)
        self.assertNotIn("json", data["artifacts"])
        for role in ("markdown", "html"):
            text = self.paths[role].read_text(encoding="utf-8")
            self.assertIn(expected, text)
            self.assertEqual(hashlib.sha256(self.paths[role].read_bytes()).hexdigest(), data["artifacts"][role]["sha256"])
        self.assertEqual(self.paths["markdown"].read_text(encoding="utf-8"), reports.render_markdown(data))
        self.assertEqual(self.paths["html"].read_text(encoding="utf-8"), reports.render_html(data))
        self.assertIn("input%20%23result.json", data["input_href"])

    def test_digest_schema_and_input_overwrite_errors_keep_old_outputs(self):
        old = self.old_outputs()
        with self.assertRaises(reports.ReportError):
            reports.export_report(self.source, self.prefix, expected_sha256="0" * 64)
        self.assert_old_outputs(old)
        with self.assertRaises(reports.ReportError):
            reports.export_report(self.source, self.source.with_suffix(""))
        self.assertEqual(self.source.read_bytes(), self.original)
        self.source.write_text("[]", encoding="utf-8")
        with self.assertRaises(reports.ReportError):
            reports.export_report(self.source, self.prefix)
        self.assert_old_outputs(old)

    def test_staging_io_error_preserves_existing_outputs(self):
        old = self.old_outputs()
        with mock.patch.object(reports.os, "fsync", side_effect=OSError("disk failure")), self.assertRaises(OSError):
            reports.export_report(self.source, self.prefix)
        self.assert_old_outputs(old)

    def test_mid_commit_failure_restores_old_bundle(self):
        old = self.old_outputs()
        replace = reports.os.replace
        failed = False

        def fail_once(source, destination):
            nonlocal failed
            if Path(destination) == self.paths["html"] and not failed:
                failed = True
                raise PermissionError("publish denied")
            return replace(source, destination)

        with mock.patch.object(reports.os, "replace", side_effect=fail_once), self.assertRaises(OSError):
            reports.export_report(self.source, self.prefix)
        self.assertTrue(failed)
        self.assert_old_outputs(old)

    def test_new_bundle_is_removed_after_publish_failure(self):
        replace = reports.os.replace

        def deny_html(source, destination):
            if Path(destination) == self.paths["html"]:
                raise PermissionError("publish denied")
            return replace(source, destination)

        with mock.patch.object(reports.os, "replace", side_effect=deny_html), self.assertRaises(OSError):
            reports.export_report(self.source, self.prefix)
        self.assertFalse(any(path.exists() for path in self.paths.values()))
        self.assertEqual(list(self.folder.glob(".tdq-report-*")), [])

    def test_interrupt_after_replace_restores_old_bundle(self):
        old = self.old_outputs()
        replace = reports.os.replace
        interrupted = False

        def interrupt_once(source, destination):
            nonlocal interrupted
            answer = replace(source, destination)
            if Path(destination) == self.paths["html"] and not interrupted:
                interrupted = True
                raise KeyboardInterrupt()
            return answer

        with mock.patch.object(reports.os, "replace", side_effect=interrupt_once), self.assertRaises(KeyboardInterrupt):
            reports.export_report(self.source, self.prefix)
        self.assert_old_outputs(old)

    def test_input_mutation_during_staging_cannot_publish_a_report(self):
        old = self.old_outputs()
        stage = reports._stage_bytes
        changed = False

        def mutate_once(destination, content):
            nonlocal changed
            temporary = stage(destination, content)
            if not changed:
                changed = True
                self.source.write_text('{"status":"ERROR"}', encoding="utf-8")
            return temporary

        with mock.patch.object(reports, "_stage_bytes", side_effect=mutate_once), self.assertRaisesRegex(reports.ReportError, "changed"):
            reports.export_report(self.source, self.prefix)
        self.assert_old_outputs(old)

    def test_json_commit_marker_is_published_last(self):
        replace = reports.os.replace
        destinations = []

        def record(source, destination):
            destinations.append(Path(destination).suffix)
            return replace(source, destination)

        with mock.patch.object(reports.os, "replace", side_effect=record):
            reports.export_report(self.source, self.prefix)
        self.assertEqual(destinations, [".md", ".html", ".json"])

    def test_dotted_prefix_preserves_entire_name(self):
        for name in ("T1.3-summary", "summary.v1"):
            with self.subTest(name=name):
                prefix = self.folder / name
                exported = reports.export_report(self.source, prefix)
                for role, suffix in (("json", ".json"), ("markdown", ".md"), ("html", ".html")):
                    destination = prefix.parent / (prefix.name + suffix)
                    self.assertTrue(destination.is_file(), destination)
                    self.assertEqual(Path(exported["outputs"][role]["path"]), destination)
