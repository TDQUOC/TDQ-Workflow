#!/usr/bin/env python3
"""Read-only evidence verifier. Never executes tests, model calls or receipt commands.

Receipt protocol tdq-scope-observation/v1 (paths relative to --root):
  slug, kind (regression/full/runtime/review/lint), status=PASS, exit_code=0,
  paid_model_calls=0, timed_out=false, failures=[], command=[observed argv],
  source_files={path:sha256}, source_sha256=digest(source_files),
  result={path,sha256}, stdout={path,sha256}.
The digested stdout must contain exactly one 'TDQ_SCOPE_RESULT <JSON binding>'
matching result. Index observations bind receipts by path+sha256; null is pending,
never PASS. Index source_files/source_sha256 lock the current required input scope.

Regression result: status=PASS, exit_code=0, source_sha256, cases=[{id,status,
assertions:int>0}], junit={path,sha256}. IDs are classname::name in raw JUnit.
coverage maps EVERY index condition to [{observation:<role>,case_id:<id>}].
Each required test file must be named in at least one regression command.
Full result: existing tdq_test.py executed/full JSON with execution.xml/json;
checked by pinned validate_full_payload, plus current source_before/after hashes.
Runtime result: status/exit/source_sha256/paid_model_calls/timed_out/failures,
scenarios=[{name,status,exit_code,elapsed_seconds,deadline_seconds,process:
{pid,ownership_verified,cleanup_complete}}]. Review result: status/source_sha256,
reviewer_id, implementer_id (different), independent=true, open_findings=[],
reviewed_conditions covering Q1..Q10. Lint result: status/exit/source_sha256,
violations=0, files covering spec and skill-eval.md.

Hashes detect stale or contradictory evidence, not coordinated forgery of all
receipts, raw outputs and index. Review identity/coverage is an auditable attestation.
Self-test fixtures are synthetic, temporary, and never task evidence.
"""
from __future__ import annotations

import argparse
from contextlib import redirect_stderr
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

SLUG = "2026-11-01-1854-eval-chat-luong-skill"
ART = f"docs/tdq/artifacts/{SLUG}/"
EXPECTED_MANIFEST_DIGEST = "9dc2d3cb0e1099a49caf3320daff5ef80251ed32077afd40a895bdba9ce79aa5"
BASELINE_SHA = "9023737aa10544a83b97f055a45f62ec3a823e31b2e1a4eebe8ec21d12505e76"
BASELINE_SOURCE_SHA = "0cd51a6147c6bbb1fcd7c4299f0c754518f78444c6fe5f90b53f1b272e3c7497"
CHECKS = tuple(f"Q{i}" for i in range(1, 11))
LEGACY = "docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/"
FULL_VALIDATOR_SHA = "692cdc93c8f9f485fac1be8078c6930e927372cbf8139af0d08f2d62284c8a89"
SAFE_RUN_SHA = "4ea732dea8ce282102db261381d07df080ec5e33f6c9d27308f9444307794913"


def log(message):
    if os.environ.get("TDQ_LOG", "1") != "0":
        print(f"[{datetime.now(timezone.utc).isoformat()}] DEBUG verify_scope: {message}", file=sys.stderr)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def sha256_file(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_confined(root, relative):
    require(isinstance(relative, str) and bool(relative), "Missing path")
    raw = Path(relative)
    require(not raw.is_absolute() and ".." not in raw.parts and "\\" not in relative,
            "Unsafe relative path")
    target = (root / raw).resolve()
    require(target.is_relative_to(root.resolve()), "Path escapes root")
    return target


def bound(root, binding):
    require(isinstance(binding, dict), "Missing artifact binding")
    expected = binding.get("sha256")
    require(isinstance(expected, str) and re.fullmatch(r"[a-f0-9]{64}", expected), "Missing SHA-256")
    path = resolve_confined(root, binding.get("path"))
    require(path.is_file(), f"Missing evidence: {binding.get('path')}")
    require(sha256_file(path) == expected, f"Stale artifact SHA: {binding['path']}")
    return path


def source_scope(root, files, expected, required):
    require(isinstance(files, dict) and bool(files), "Missing source files")
    require(set(required) <= set(files), "Source scope omits required inputs")
    require(digest(files) == expected, "Source digest mismatch")
    for relative, value in files.items():
        bound(root, {"path": relative, "sha256": value})
    return expected


def exact_zero(value, name):
    require(type(value) is int and value == 0, f"Missing/nonzero integer {name}")


def verify_evidence_index(index):
    require(index.get("schema") == "tdq-scope-evidence/v2", "Unknown index schema")
    require(index.get("slug") == SLUG, "Wrong request")
    require(set(index["outputs"]) == {f"O{i}" for i in range(1, 8)}, "Missing outputs")
    require(set(index["dod_checks"]) == set(CHECKS), "Missing DoD checks")
    for entry in index["outputs"].values():
        require(isinstance(entry, list) and bool(entry), "Empty output mapping")
    for entry in index["dod_checks"].values():
        require(entry.get("description") and entry.get("conditions") and entry.get("required_files"),
                "Incomplete DoD definition")


def verify_archify_binding(root, index):
    require(index["preview_manifest_digest"] == EXPECTED_MANIFEST_DIGEST, "Unapproved manifest digest")
    manifest_path = bound(root, {"path": index["preview_manifest"], "sha256": EXPECTED_MANIFEST_DIGEST})
    spec = bound(root, {"path": index["spec_path"], "sha256": index["spec_sha256"]})
    manifest = read_json(manifest_path)
    text = spec.read_text(encoding="utf-8")
    start, end = "<!-- tdq-archify-binding:start -->", "<!-- tdq-archify-binding:end -->"
    require(text.count(start) == text.count(end) == 1, "Missing/duplicate Archify binding")
    a, b = text.index(start), text.index(end)
    require(a < b, "Inverted binding")
    body = text[a:b]
    require(f"<!-- manifest_digest: {EXPECTED_MANIFEST_DIGEST} -->" in body, "Stale binding digest")
    require(f"<!-- manifest: {manifest_path.name} -->" in body, "Wrong manifest binding path")
    doc_digest = hashlib.sha256((text[:a] + text[b + len(end):]).encode()).hexdigest()
    require(manifest["document_digest"] == doc_digest, "Stale spec document digest")
    require(manifest["request"] == SLUG and manifest["evidence_kind"] == "planned", "Wrong preview scope")
    require(manifest["document_path"] == index["spec_path"] and
            manifest["artifact_path"] == index["preview_html"], "Preview path mismatch")
    bound(root, {"path": index["preview_html"], "sha256": manifest["artifact_digest"]})


def verify_baseline(root, index):
    require(index["baseline_sha256"] == BASELINE_SHA, "Baseline pin changed")
    data = read_json(bound(root, {"path": index["baseline_path"], "sha256": BASELINE_SHA}))
    require(data["kind"] == "offline-source-diagnostic-not-agent-eval", "Wrong baseline kind")
    require(data["source_sha256"] == BASELINE_SOURCE_SHA, "Stale baseline source")
    exact_zero(data["paid_model_calls"], "paid_model_calls")
    require(data["historical_record_count"] == 60 and data["missing_cost_result"] == 0.0, "Baseline probe changed")
    probes = data["mismatched_identity_probes"]
    require(len(probes) == 4 and {p["changed_field"] for p in probes} ==
            {"model", "host", "permission_profile", "scorer_version"}, "Missing baseline probes")
    require(all(p["accepted"] is True for p in probes), "Baseline diagnostic changed")


def verify_runtime_payload(payload, expected_source_sha=None):
    require(expected_source_sha is not None, "Missing current source SHA")
    require(payload.get("status") == "PASS", "Runtime missing PASS")
    exact_zero(payload.get("exit_code"), "exit_code")
    exact_zero(payload.get("paid_model_calls"), "paid_model_calls")
    require(payload.get("timed_out") is False and payload.get("failures") == [], "Runtime incomplete/failed")
    require(payload.get("source_sha256") == expected_source_sha, "Stale source SHA")
    rows = payload.get("scenarios")
    require(isinstance(rows, list) and bool(rows), "Missing scenarios")
    names = set()
    for row in rows:
        name = row.get("name")
        require(isinstance(name, str) and name and name not in names, "Missing/duplicate scenario")
        names.add(name)
        require(row.get("status") == "PASS", "Scenario not PASS")
        exact_zero(row.get("exit_code"), "scenario exit_code")
        elapsed, deadline = row.get("elapsed_seconds"), row.get("deadline_seconds")
        require(type(elapsed) in (int, float) and math.isfinite(elapsed) and elapsed >= 0, "Invalid elapsed")
        require(type(deadline) in (int, float) and math.isfinite(deadline) and
                0 < deadline <= 120 and elapsed <= deadline, "Invalid/exceeded deadline")
        process = row.get("process", {})
        require(type(process.get("pid")) is int and process["pid"] > 0, "Missing PID")
        require(process.get("ownership_verified") is True and process.get("cleanup_complete") is True,
                "Unproven ownership/cleanup")


def verify_review(data, expected):
    require(data.get("status") == "PASS" and data.get("source_sha256") == expected, "Stale/failed review")
    reviewer, author = data.get("reviewer_id"), data.get("implementer_id")
    require(isinstance(reviewer, str) and reviewer.strip() and isinstance(author, str) and
            author.strip() and reviewer != author and data.get("independent") is True, "Missing independent review identity")
    require(data.get("open_findings") == [], "Missing/open review findings")
    require(set(CHECKS) <= set(data.get("reviewed_conditions", [])), "Review scope incomplete")


def regression_cases(root, result):
    """Compare observed cases against raw JUnit, never source text or PASS prose."""
    exact_zero(result.get("exit_code"), "result exit_code")
    rows = result.get("cases")
    require(isinstance(rows, list) and bool(rows), "Missing executed cases")
    xml = ET.parse(bound(root, result.get("junit")))
    raw = {}
    for node in xml.iter("testcase"):
        key = node.get("classname", "") + "::" + node.get("name", "")
        require(key not in raw and not any(c.tag in {"failure", "error", "skipped"} for c in node),
                "Duplicate/non-pass JUnit case")
        raw[key] = node
    require(len(raw) == len(rows), "Case inventory mismatch")
    cases = set()
    for row in rows:
        key = row.get("id")
        require(key in raw and key not in cases and row.get("status") == "PASS", "Missing/non-pass case")
        require(type(row.get("assertions")) is int and row["assertions"] > 0, "No observed assertions")
        cases.add(key)
    require(cases == set(raw), "Incomplete raw case coverage")
    return cases


def load_full_validator(root):
    """Reuse only offline Full parsing; validate_receipt calls git, so not used."""
    files = (("safe_run", "safe_run.py", SAFE_RUN_SHA),
             ("_scope_full_validator", "verify_dod.py", FULL_VALIDATOR_SHA))
    module = None
    for name, filename, expected in files:
        path = bound(root, {"path": LEGACY + filename, "sha256": expected})
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load module {name} from {path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    if module is None:
        raise ImportError("Failed to load full validator module")
    return module


def verify_full(root, result, required):
    exact_zero(result.get("exit_code"), "Full exit_code")
    require(result.get("evidence"), "Full missing raw evidence")
    snapshot = result.get("source_before")
    require(isinstance(snapshot, dict) and snapshot == result.get("source_after"), "Missing/mutated Full source")
    files = snapshot.get("files")
    if files is None and isinstance(snapshot.get("inputs"), dict):
        files = snapshot["inputs"].get("files")
    expected = snapshot.get("sha256") or (digest(files) if files else None)
    source_scope(root, files, expected, required)
    # Existing checker reparses execution.xml and execution.json, compares coverage.
    load_full_validator(root).validate_full_payload(result, root)


def observation(root, binding, kind, files, expected):
    receipt = read_json(bound(root, binding))
    require(receipt.get("schema") == "tdq-scope-observation/v1" and receipt.get("slug") == SLUG,
            "Unknown observation schema/request")
    require(receipt.get("kind") == kind and receipt.get("status") == "PASS", "Wrong/non-pass observation")
    exact_zero(receipt.get("exit_code"), "observed exit_code")
    exact_zero(receipt.get("paid_model_calls"), "paid_model_calls")
    require(receipt.get("timed_out") is False and receipt.get("failures") == [], "Incomplete observation")
    require(receipt.get("source_files") == files and receipt.get("source_sha256") == expected, "Stale observation source")
    command = receipt.get("command")
    require(isinstance(command, list) and command and all(isinstance(x, str) and x for x in command),
            "Missing observed command")
    output = bound(root, receipt.get("stdout")).read_text(encoding="utf-8")
    markers = [json.loads(line[len("TDQ_SCOPE_RESULT "):]) for line in output.splitlines()
               if line.startswith("TDQ_SCOPE_RESULT ")]
    require(markers == [receipt.get("result")], "Missing/ambiguous observed result binding")
    result = read_json(bound(root, receipt.get("result")))
    require(result.get("status") == "PASS", "False PASS result")
    if kind != "full":
        require(result.get("source_sha256") == expected, "Stale result source")
    return receipt, result


def verify_check(check_id, root, index):
    require(check_id in CHECKS, "Unknown DoD check")
    verify_evidence_index(index)
    verify_archify_binding(root, index)
    verify_baseline(root, index)
    entry = index["dod_checks"][check_id]
    files, expected = entry.get("source_files"), entry.get("source_sha256")
    required = set(entry["required_files"] + entry["test_files"])
    for output in entry["outputs"]:
        required.update(index["outputs"][output])
    # Generated evidence cannot be its own source hash (receipt/index self-cycle).
    inputs = {p for p in required if not p.startswith("docs/tdq/artifacts/")}
    for relative in required:
        require(resolve_confined(root, relative).is_file(), "Missing required file: " + relative)
    source_scope(root, files, expected, inputs)
    declarations = entry.get("required_artifacts")
    require(isinstance(declarations, dict) and declarations.get("regression") == "regression", "Missing artifact roles")
    results, commands, cases = {}, [], {}
    for role, kind in declarations.items():
        receipt, result = observation(root, entry.get("observations", {}).get(role), kind, files, expected)
        results[kind] = result
        commands.append(receipt["command"])
        if kind == "regression":
            cases[role] = regression_cases(root, result)
        elif kind == "runtime":
            require(receipt["result"]["path"] == ART + "runtime.json", "Wrong runtime result path")
            verify_runtime_payload(result, expected)
        elif kind == "review":
            verify_review(result, expected)
        elif kind == "full":
            require("tron-bo" in receipt["command"] and "--fresh" in receipt["command"], "Not a fresh Full command")
            verify_full(root, result, {p for p in inputs if not p.startswith("docs/tdq/")})
        elif kind == "lint":
            exact_zero(result.get("exit_code"), "lint exit_code")
            exact_zero(result.get("violations"), "lint violations")
            require({index["spec_path"], "skills/tdq-build/references/skill-eval.md"} <= set(result.get("files", [])), "Lint scope incomplete")
        else:
            raise ValueError("Unknown artifact role")
    require(all(any(path in cmd for cmd in commands) for path in entry["test_files"]), "Missing regression commands")
    for condition in entry["conditions"]:
        proofs = entry.get("coverage", {}).get(condition)
        require(isinstance(proofs, list) and proofs, "Missing coverage: " + condition)
        for proof in proofs:
            require(proof.get("case_id") in cases.get(proof.get("observation"), set()), "Coverage case not executed")
    if check_id == "Q9":
        require({"full", "runtime", "review"} <= set(results), "Missing Full/runtime/review evidence")
    if check_id == "Q10":
        require("lint" in results, "Missing lint evidence")
    return {"check": check_id, "status": "PASS", "conditions": len(entry["conditions"])}


def run_self_test(root, evidence):
    index = read_json(evidence / "evidence-index.json")

    class Tests(unittest.TestCase):
        def setUp(self):
            self.runtime = {"status": "PASS", "exit_code": 0, "paid_model_calls": 0,
                            "timed_out": False, "failures": [], "source_sha256": "a" * 64,
                            "scenarios": [{"name": "synthetic", "status": "PASS", "exit_code": 0,
                                           "elapsed_seconds": 1, "deadline_seconds": 120,
                                           "process": {"pid": 1, "ownership_verified": True, "cleanup_complete": True}}]}

        def test_approved_bindings(self):
            verify_evidence_index(index)
            verify_archify_binding(root, index)
            verify_baseline(root, index)

        def test_runtime_positive_control(self):
            verify_runtime_payload(self.runtime, "a" * 64)

        def test_missing_runtime_fields(self):
            for field in self.runtime:
                data = dict(self.runtime)
                del data[field]
                with self.subTest(field=field), self.assertRaises(ValueError):
                    verify_runtime_payload(data, "a" * 64)

        def test_missing_scenario_fields(self):
            for field in self.runtime["scenarios"][0]:
                data = json.loads(json.dumps(self.runtime))
                del data["scenarios"][0][field]
                with self.subTest(field=field), self.assertRaises(ValueError):
                    verify_runtime_payload(data, "a" * 64)

        def test_bool_is_not_number(self):
            for field in ("exit_code", "paid_model_calls"):
                data = dict(self.runtime, **{field: False})
                with self.subTest(field=field), self.assertRaises(ValueError):
                    verify_runtime_payload(data, "a" * 64)
            for field in ("exit_code", "elapsed_seconds", "deadline_seconds"):
                data = json.loads(json.dumps(self.runtime))
                data["scenarios"][0][field] = False
                with self.subTest(field=field), self.assertRaises(ValueError):
                    verify_runtime_payload(data, "a" * 64)

        def test_stale_source_and_false_pass(self):
            with self.assertRaises(ValueError):
                verify_runtime_payload(self.runtime, "b" * 64)
            for value in (1, None, False):
                with self.subTest(exit_code=value), self.assertRaises(ValueError):
                    verify_runtime_payload(dict(self.runtime, exit_code=value), "a" * 64)

        def test_review_identity_required(self):
            data = {"status": "PASS", "source_sha256": "a" * 64, "open_findings": [],
                    "independent": True, "reviewed_conditions": list(CHECKS)}
            with self.assertRaises(ValueError):
                verify_review(data, "a" * 64)
            data.update(reviewer_id="reviewer", implementer_id="author")
            verify_review(data, "a" * 64)
            data["reviewer_id"] = "author"
            with self.assertRaises(ValueError):
                verify_review(data, "a" * 64)

        def test_full_requires_raw_evidence(self):
            with self.assertRaisesRegex(ValueError, "raw evidence"):
                verify_full(root, {"status": "PASS", "exit_code": 0}, set())

        def test_missing_and_stale_bound_file(self):
            with tempfile.TemporaryDirectory() as tmp:
                base = Path(tmp)
                with self.assertRaises(ValueError):
                    bound(base, {"path": "missing", "sha256": "0" * 64})
                path = base / "source.py"
                path.write_text("# synthetic", encoding="utf-8")
                files = {"source.py": sha256_file(path)}
                source_scope(base, files, digest(files), {"source.py"})
                path.write_text("# changed", encoding="utf-8")
                with self.assertRaises(ValueError):
                    source_scope(base, files, digest(files), {"source.py"})

        def test_observation_and_junit_positive_and_false_pass(self):
            with tempfile.TemporaryDirectory() as tmp:
                base = Path(tmp)
                def save(name, text):
                    path = base / name
                    path.write_text(text, encoding="utf-8")
                    return {"path": name, "sha256": sha256_file(path)}
                junit = save("cases.xml", '<testsuite><testcase classname="synthetic" name="test_one"/></testsuite>')
                result = {"status": "PASS", "exit_code": 0, "source_sha256": digest({"a": "b"}),
                          "cases": [{"id": "synthetic::test_one", "status": "PASS", "assertions": 1}], "junit": junit}
                result_binding = save("result.json", json.dumps(result))
                stdout = save("stdout.txt", "TDQ_SCOPE_RESULT " + json.dumps(result_binding))
                receipt = {"schema": "tdq-scope-observation/v1", "slug": SLUG, "kind": "regression",
                           "status": "PASS", "exit_code": 0, "paid_model_calls": 0, "timed_out": False,
                           "failures": [], "command": ["python", "synthetic.py"], "source_files": {"a": "b"},
                           "source_sha256": result["source_sha256"], "result": result_binding, "stdout": stdout}
                binding = save("receipt.json", json.dumps(receipt))
                _, actual = observation(base, binding, "regression", {"a": "b"}, result["source_sha256"])
                self.assertEqual(regression_cases(base, actual), {"synthetic::test_one"})
                for field in ("command", "result", "stdout", "source_sha256", "exit_code"):
                    broken = dict(receipt)
                    del broken[field]
                    binding = save("receipt.json", json.dumps(broken))
                    with self.subTest(field=field), self.assertRaises((ValueError, KeyError)):
                        observation(base, binding, "regression", {"a": "b"}, result["source_sha256"])
                result["junit"] = save("cases.xml", '<testsuite><testcase classname="synthetic" name="test_one"><failure/></testcase></testsuite>')
                with self.assertRaises(ValueError):
                    regression_cases(base, result)

        def test_token_only_files_cannot_certify_any_q(self):
            with tempfile.TemporaryDirectory() as tmp:
                base = Path(tmp)
                for entry in index["outputs"].values():
                    for relative in entry:
                        path = resolve_confined(base, relative)
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_text("# PASS review skills hooks claude codex KEEP TRIM DROP INCONCLUSIVE", encoding="utf-8")
                for key in ("spec_path", "preview_html", "preview_manifest", "baseline_path"):
                    resolve_confined(base, index[key]).write_bytes(resolve_confined(root, index[key]).read_bytes())
                for check in CHECKS:
                    with self.subTest(check=check), self.assertRaises((ValueError, OSError)):
                        verify_check(check, base, index)

        def test_no_subprocess_launches(self):
            with patch("subprocess.Popen", side_effect=AssertionError("Subprocess forbidden")), \
                    patch("os.system", side_effect=AssertionError("Shell forbidden")):
                for check in CHECKS:
                    pending = json.loads(json.dumps(index))
                    pending["dod_checks"][check]["observations"] = {}
                    with self.subTest(check=check), self.assertRaises((ValueError, OSError)):
                        verify_check(check, root, pending)
                verify_runtime_payload(self.runtime, "a" * 64)

        def test_logging(self):
            with patch.dict(os.environ, {"TDQ_LOG": "1"}), redirect_stderr(io.StringIO()) as out:
                log("synthetic")
                self.assertRegex(out.getvalue(), r"\[\d{4}-\d\d-\d\dT.*DEBUG verify_scope")
            with patch.dict(os.environ, {"TDQ_LOG": "0"}), redirect_stderr(io.StringIO()) as out:
                log("synthetic")
                self.assertEqual(out.getvalue(), "")

    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    print(json.dumps({"kind": "synthetic-validator-selftest", "tests_run": result.testsRun,
                      "failures": len(result.failures), "errors": len(result.errors), "task_evidence": False}))
    return 0 if result.wasSuccessful() else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("check", nargs="?", choices=CHECKS)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument("--evidence", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    log("read-only verification started")
    try:
        if args.self_test:
            return run_self_test(args.root, args.evidence)
        require(args.all or args.check, "Select Q1..Q10, --all or --self-test")
        index = read_json(args.evidence / "evidence-index.json")
        results = []
        for check in CHECKS if args.all else [args.check]:
            try:
                results.append(verify_check(check, args.root, index))
            except (ValueError, KeyError, TypeError, OSError) as exc:
                results.append({"check": check, "status": "FAIL", "error": str(exc)})
        print(json.dumps(results, ensure_ascii=True))
        return int(any(row["status"] != "PASS" for row in results))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
