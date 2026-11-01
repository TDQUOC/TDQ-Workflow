#!/usr/bin/env python3
"""Fail-closed verifier for 2026-11-01-1854-eval-chat-luong-skill (O1-O7, Q1-Q10).

Validates evidence-index.json, Archify preview binding, analysis-baseline.json,
and DoD checks Q1-Q10 without invoking any paid LLM model.
"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any
import unittest


SLUG = "2026-11-01-1854-eval-chat-luong-skill"
EXPECTED_MANIFEST_DIGEST = "9dc2d3cb0e1099a49caf3320daff5ef80251ed32077afd40a895bdba9ce79aa5"
EXPECTED_DOC_DIGEST = "fcdc850cfd5df3713a9683786c61cc711bb9a84a451edd0400f58d7b70802dc9"
EXPECTED_HTML_DIGEST = "a2632cc8a2d30915507aeedfc94ae176642f517132164a0423f7e79050b5fdc5"
EXPECTED_BASELINE_SOURCE_SHA = "0cd51a6147c6bbb1fcd7c4299f0c754518f78444c6fe5f90b53f1b272e3c7497"
EXPECTED_OUTPUT_KEYS = tuple(f"O{i}" for i in range(1, 8))
EXPECTED_DOD_KEYS = tuple(f"Q{i}" for i in range(1, 11))
IDENTITY_PROBE_FIELDS = ("model", "host", "permission_profile", "scorer_version")
BINDING_START = "<!-- tdq-archify-binding:start -->"
BINDING_END = "<!-- tdq-archify-binding:end -->"


def _log_enabled() -> bool:
    for var in ("TDQ_LOG", "TDQ_EVAL_LOG"):
        if os.environ.get(var, "1").strip().lower() in {"0", "false", "off"}:
            return False
    return True


def log(message: str, stream: Any = None) -> None:
    if _log_enabled():
        target = stream if stream is not None else sys.stderr
        stamp = datetime.now(timezone.utc).isoformat()
        print(f"[{stamp}] verify_scope: {message}", file=target)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def read_json(path: Path) -> Any:
    require(path.is_file(), f"Missing JSON file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_confined(root: Path, rel_path: str) -> Path:
    require(isinstance(rel_path, str) and bool(rel_path.strip()), "Empty relative path")
    raw = Path(rel_path)
    require(not raw.is_absolute() and ".." not in raw.parts, f"Unsafe path: {rel_path}")
    resolved_root = root.resolve()
    full = (resolved_root / raw).resolve()
    try:
        full.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"Path escapes root: {rel_path}") from exc
    return full


def compute_document_digest(spec_path: Path) -> tuple[str, str]:
    require(spec_path.is_file(), f"Missing spec file: {spec_path}")
    content = spec_path.read_text(encoding="utf-8")
    require(content.count(BINDING_START) == 1 and content.count(BINDING_END) == 1,
            "Spec must contain exactly one Archify binding block")
    start_idx = content.find(BINDING_START)
    end_idx = content.find(BINDING_END)
    require(start_idx < end_idx, "Inverted Archify binding markers")
    binding_body = content[start_idx + len(BINDING_START):end_idx]
    match = re.search(r"manifest_digest:\s*([0-9a-fA-F]{64})", binding_body)
    require(match is not None, "Missing 64-hex manifest_digest in spec binding block")
    stripped = content[:start_idx] + content[end_idx + len(BINDING_END):]
    doc_digest = hashlib.sha256(stripped.encode("utf-8")).hexdigest()
    return doc_digest, match.group(1).lower()


def extract_output_files(entry: Any) -> list[str]:
    if isinstance(entry, list):
        return entry
    if isinstance(entry, dict):
        return entry.get("required_files") or entry.get("files") or []
    return []


def verify_evidence_index(index: dict[str, Any]) -> dict[str, Any]:
    require(isinstance(index, dict), "evidence-index root must be a dict")
    require(index.get("slug") == SLUG, f"Unexpected slug: {index.get('slug')}")
    require(index.get("preview_manifest_digest") == EXPECTED_MANIFEST_DIGEST,
            "preview_manifest_digest does not match approved manifest digest")
    for field in ("spec_path", "preview_html", "preview_manifest", "baseline_path"):
        require(isinstance(index.get(field), str) and bool(index[field].strip()),
                f"Missing required index field: {field}")
    outputs = index.get("outputs")
    require(isinstance(outputs, dict), "outputs must be a dict")
    for key in EXPECTED_OUTPUT_KEYS:
        files = extract_output_files(outputs.get(key))
        require(isinstance(files, list) and bool(files), f"Output {key} has no mapped files")
    dod = index.get("dod_checks")
    require(isinstance(dod, dict), "dod_checks must be a dict")
    for key in EXPECTED_DOD_KEYS:
        item = dod.get(key)
        require(isinstance(item, dict), f"Missing dod_checks entry: {key}")
        require(bool(item.get("description")), f"Missing description for {key}")
        require(isinstance(item.get("required_files"), list) and bool(item["required_files"]),
                f"Missing required_files for {key}")
        require(isinstance(item.get("conditions"), list) and bool(item["conditions"]),
                f"Missing conditions for {key}")
    return {"outputs": len(outputs), "dod_checks": len(dod)}


def verify_archify_binding(root: Path, index: dict[str, Any]) -> dict[str, Any]:
    spec_path = resolve_confined(root, index["spec_path"])
    html_path = resolve_confined(root, index["preview_html"])
    manifest_path = resolve_confined(root, index["preview_manifest"])
    require(spec_path.is_file(), f"Spec file missing: {spec_path}")
    require(html_path.is_file(), f"Preview HTML missing: {html_path}")
    require(manifest_path.is_file(), f"Preview manifest missing: {manifest_path}")

    actual_manifest_sha = sha256_file(manifest_path)
    expected_manifest_sha = index["preview_manifest_digest"].lower()
    require(actual_manifest_sha == expected_manifest_sha,
            f"Manifest SHA mismatch: {actual_manifest_sha} != {expected_manifest_sha}")

    doc_digest, bound_manifest_sha = compute_document_digest(spec_path)
    require(bound_manifest_sha == actual_manifest_sha,
            f"Spec binding manifest_digest mismatch: {bound_manifest_sha} != {actual_manifest_sha}")

    manifest_data = read_json(manifest_path)
    require(manifest_data.get("request") == SLUG, "Preview manifest belongs to another request")
    require(manifest_data.get("document_digest") == doc_digest,
            "Preview manifest document_digest does not match spec content")
    actual_html_sha = sha256_file(html_path)
    require(manifest_data.get("artifact_digest") == actual_html_sha,
            "Preview manifest artifact_digest does not match preview HTML")
    if index.get("spec_sha256"):
        require(sha256_file(spec_path) == index["spec_sha256"], "Spec file SHA-256 changed")
    return {
        "manifest_digest": actual_manifest_sha,
        "document_digest": doc_digest,
        "artifact_digest": actual_html_sha,
    }


def verify_baseline(root: Path, index: dict[str, Any]) -> dict[str, Any]:
    baseline_path = resolve_confined(root, index["baseline_path"])
    require(baseline_path.is_file(), f"Missing baseline file: {baseline_path}")
    if index.get("baseline_sha256"):
        require(sha256_file(baseline_path) == index["baseline_sha256"],
                "analysis-baseline.json SHA-256 mismatch")
    data = read_json(baseline_path)
    require(data.get("kind") == "offline-source-diagnostic-not-agent-eval",
            "Invalid analysis-baseline kind")
    require(data.get("paid_model_calls") == 0, "Baseline diagnostic must have 0 paid model calls")
    require(data.get("historical_record_count") == 60, "Expected 60 historical records in baseline")
    require(data.get("missing_cost_result") == 0.0, "Baseline missing_cost_result probe must be 0.0")
    source_sha = data.get("source_sha256", "")
    require(bool(re.match(r"^[0-9a-f]{64}$", str(source_sha))), "Invalid baseline source_sha256")
    if index.get("baseline_source_sha256"):
        require(source_sha == index["baseline_source_sha256"], "Baseline source_sha256 mismatch")
    probes = data.get("mismatched_identity_probes", [])
    require(isinstance(probes, list) and len(probes) == 4, "Expected 4 mismatched_identity_probes")
    fields = [row.get("changed_field") for row in probes if isinstance(row, dict)]
    require(set(fields) == set(IDENTITY_PROBE_FIELDS), f"Unexpected probe fields: {fields}")
    require(all(row.get("accepted") is True for row in probes),
            "Baseline diagnostic probes must record pre-fix accepted=True")
    return {"source_sha256": source_sha, "probes": len(probes)}


def verify_runtime_payload(payload: dict[str, Any], expected_source_sha: str | None = None) -> dict[str, Any]:
    require(isinstance(payload, dict), "Runtime payload must be a JSON object")
    status = payload.get("status") or payload.get("verdict") or "PASS"
    require(status == "PASS", f"Runtime status is not PASS: {status}")
    require(payload.get("exit_code", 0) == 0, "False PASS: non-zero top-level exit_code")
    require(payload.get("timed_out", False) is False, "False PASS: timed_out is True")
    require(payload.get("paid_model_calls", 0) == 0, "Runtime checks must not make paid model calls")
    require(not payload.get("failures"), "False PASS: failures list is non-empty")
    if expected_source_sha is not None:
        require(payload.get("source_sha256") == expected_source_sha,
                f"Stale source SHA: {payload.get('source_sha256')} != {expected_source_sha}")
    scenarios = payload.get("scenarios")
    require(isinstance(scenarios, list) and bool(scenarios), "Missing runtime scenarios")
    names = [row.get("name") for row in scenarios if isinstance(row, dict)]
    require(len(names) == len(scenarios) and len(set(names)) == len(names),
            "Duplicate or unnamed runtime scenarios")
    for row in scenarios:
        _verify_scenario_row(row)
    return {"scenarios": len(scenarios), "paid_model_calls": 0}


def _verify_scenario_row(row: dict[str, Any]) -> None:
    require(row.get("exit_code") == 0, f"Scenario {row.get('name')} failed with non-zero exit_code")
    require(row.get("status", "PASS") in {"PASS", "passed", "ok"},
            f"Scenario {row.get('name')} has non-passing status")
    elapsed = row.get("elapsed_seconds", row.get("duration_seconds", 0.0))
    deadline = row.get("deadline_seconds", row.get("timeout_seconds", 120.0))
    require(isinstance(elapsed, (int, float)) and math.isfinite(elapsed) and 0 <= elapsed <= 120,
            f"Scenario {row.get('name')} elapsed_seconds out of bounds: {elapsed}")
    require(isinstance(deadline, (int, float)) and 0 < deadline <= 120 and elapsed <= deadline,
            f"Scenario {row.get('name')} exceeded deadline: {elapsed} > {deadline}")
    proc = row.get("process")
    if isinstance(proc, dict):
        require(proc.get("ownership_verified", True) is True, "Process ownership not verified")
        require(proc.get("cleanup_complete", True) is True, "Process cleanup incomplete")


def require_files_exist(root: Path, rel_paths: list[str]) -> list[Path]:
    resolved: list[Path] = []
    for rel in rel_paths:
        path = resolve_confined(root, rel)
        require(path.is_file() and path.stat().st_size > 0, f"Required file missing or empty: {rel}")
        resolved.append(path)
    return resolved


def run_pytest_files(root: Path, rel_test_files: list[str]) -> dict[str, Any]:
    if not rel_test_files:
        return {"test_files": 0}
    require_files_exist(root, rel_test_files)
    with tempfile.TemporaryDirectory(prefix="tdq-scope-pytest-") as tmp_state:
        env = os.environ.copy()
        env["TDQ_PROJECT_DIR"] = tmp_state
        cmd = [sys.executable, "-m", "pytest", "-q", *rel_test_files]
        proc = subprocess.run(
            cmd,
            cwd=str(root),
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
            check=False,
        )
    require(proc.returncode == 0,
            f"pytest failed for {rel_test_files} (exit {proc.returncode}): {(proc.stdout + proc.stderr)[-400:]}")
    return {"test_files": len(rel_test_files), "exit_code": proc.returncode}


def load_module_from(root: Path, rel_path: str, module_name: str) -> Any:
    file_path = resolve_confined(root, rel_path)
    require(file_path.is_file(), f"Module file missing: {rel_path}")
    scripts_dir = str((root / "scripts").resolve())
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    require(spec is not None and spec.loader is not None, f"Cannot load spec for {rel_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def check_pure_core_ast(contract_path: Path) -> None:
    source = contract_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(contract_path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [alias.name.split(".")[0] for alias in node.names]
            require("subprocess" not in names and "hooks" not in names,
                    f"Pure core must not import subprocess or hooks: {names}")
        elif isinstance(node, ast.ImportFrom) and node.module:
            top = node.module.split(".")[0]
            require(top not in {"subprocess", "hooks"},
                    f"Pure core must not import from {top}")


def _probe_classifier(mod: Any) -> bool:
    for fn_name in ("classify_targets", "classify_target", "classify_change", "phan_loai_target"):
        fn = getattr(mod, fn_name, None)
        if callable(fn):
            arg_skill = ["skills/tdq-build/SKILL.md"] if fn_name.endswith("s") else "skills/tdq-build/SKILL.md"
            arg_doc = ["README.md"] if fn_name.endswith("s") else "README.md"
            try:
                res_skill = fn(arg_skill)
                res_doc = fn(arg_doc)
                require(res_skill != res_doc, f"{fn_name} did not distinguish skill target from README.md")
                return True
            except TypeError:
                continue
    return False


def _verify_q1(root: Path) -> dict[str, Any]:
    contract_path = resolve_confined(root, "scripts/tdq_eval_contract.py")
    check_pure_core_ast(contract_path)
    source = contract_path.read_text(encoding="utf-8")
    for token in ("skills", "hooks", "mechanism", "agent-effectiveness"):
        require(token in source, f"tdq_eval_contract.py missing expected Q1 token: {token}")
    mod = load_module_from(root, "scripts/tdq_eval_contract.py", "_tdq_eval_contract_q1")
    probed = _probe_classifier(mod)
    return {"pure_core": True, "classifier_probed": probed}


def _verify_q2(root: Path, index: dict[str, Any]) -> dict[str, Any]:
    baseline_info = verify_baseline(root, index)
    source = resolve_confined(root, "scripts/tdq_eval_contract.py").read_text(encoding="utf-8")
    required_tokens = (
        "model",
        "host",
        "permission_profile",
        "scorer_version",
        "corpus_version",
        "check_set",
        "cache_profile",
        "historical_unverified",
    )
    for token in required_tokens:
        require(token in source, f"tdq_eval_contract.py missing Q2 identity token: {token}")
    load_module_from(root, "scripts/tdq_eval_contract.py", "_tdq_eval_contract_q2")
    return {"baseline_probes": baseline_info["probes"], "identity_tokens": len(required_tokens)}


def _verify_q3(root: Path) -> dict[str, Any]:
    source = resolve_confined(root, "scripts/tdq_eval_contract.py").read_text(encoding="utf-8")
    required_tokens = (
        "trigger_accuracy",
        "outcome_quality",
        "efficiency_metrics",
        "unavailable",
        "observed_usage",
        "rate_estimate",
        "provider_billed",
    )
    for token in required_tokens:
        require(token in source, f"tdq_eval_contract.py missing Q3 metric token: {token}")
    load_module_from(root, "scripts/tdq_eval_contract.py", "_tdq_eval_contract_q3")
    return {"metric_tokens": len(required_tokens)}


def _verify_q4(root: Path) -> dict[str, Any]:
    source = resolve_confined(root, "scripts/tdq_eval_hosts.py").read_text(encoding="utf-8")
    for token in ("claude", "codex", "OwnedProcessJob", "tdq_transcript"):
        require(token.lower() in source.lower(),
                f"tdq_eval_hosts.py missing Q4 host/isolation token: {token}")
    return {"hosts": ["claude", "codex"]}


def _verify_q5(root: Path) -> dict[str, Any]:
    corpus_data = read_json(resolve_confined(root, "evals/skill-quality/corpus.json"))
    require(isinstance(corpus_data, dict), "corpus.json must be a JSON object")
    corpus_text = json.dumps(corpus_data)
    require("dev" in corpus_text and "holdout" in corpus_text,
            "corpus.json must define dev and holdout splits")
    eval_src = resolve_confined(root, "scripts/tdq_eval.py").read_text(encoding="utf-8")
    skill_eval_src = resolve_confined(root, "scripts/tdq_skill_eval.py").read_text(encoding="utf-8")
    combined = eval_src + "\n" + skill_eval_src
    require("rescore_append_only" in combined, "Missing rescore_append_only support")
    require("AB" in combined and "BA" in combined, "Missing balanced AB/BA scheduling")
    return {"corpus_valid": True}


def _verify_q6(root: Path) -> dict[str, Any]:
    contract_src = resolve_confined(root, "scripts/tdq_eval_contract.py").read_text(encoding="utf-8")
    cli_src = resolve_confined(root, "scripts/tdq_skill_eval.py").read_text(encoding="utf-8")
    combined = contract_src + "\n" + cli_src
    for verdict in ("KEEP", "TRIM", "DROP", "INCONCLUSIVE"):
        require(verdict in combined, f"Missing recommendation verdict: {verdict}")
    return {"verdicts": ["KEEP", "TRIM", "DROP", "INCONCLUSIVE"]}


def _verify_q7(root: Path) -> dict[str, Any]:
    bp = load_module_from(root, "scripts/build_portable.py", "_tdq_build_portable_q7")
    excluded_files = set(getattr(bp, "EXCLUDE_FILES", ())) | set(getattr(bp, "RELEASE_EXCLUDE_FILES", ()))
    excluded_scripts = set(getattr(bp, "RELEASE_EXCLUDE_SCRIPTS", ()))
    excluded_dirs = set(getattr(bp, "EXCLUDE_DIRS", ())) | set(getattr(bp, "RELEASE_EXCLUDE_DIRS", ()))
    shipped = ("tdq_eval_contract.py", "tdq_eval_hosts.py", "tdq_skill_eval.py")
    for name in shipped:
        require(name not in excluded_files and name not in excluded_scripts,
                f"{name} must not be excluded in build_portable.py")
    require("tdq_eval.py" in excluded_files or "tdq_eval.py" in excluded_scripts,
            "Legacy tdq_eval.py must remain excluded from portable release")
    require("tests" in excluded_dirs and "evals" in set(getattr(bp, "RELEASE_EXCLUDE_DIRS", ())),
            "tests and evals must remain excluded from release dirs")
    return {"shipped_eval_scripts": list(shipped)}


def _verify_q8(root: Path) -> dict[str, Any]:
    state_src = resolve_confined(root, "scripts/tdq_state.py").read_text(encoding="utf-8")
    for token in ("WAIVED_USER", "INCOMPLETE"):
        require(token in state_src, f"tdq_state.py missing workflow gate status: {token}")
    return {"workflow_gate_tokens": ["WAIVED_USER", "INCOMPLETE"]}


def _verify_q9(root: Path) -> dict[str, Any]:
    runtime_path = resolve_confined(
        root, f"docs/tdq/artifacts/{SLUG}/runtime.json"
    )
    runtime_data = read_json(runtime_path)
    runtime_summary = verify_runtime_payload(runtime_data)
    _verify_independent_review(root)
    return runtime_summary


def _verify_independent_review(root: Path) -> None:
    artifact_dir = resolve_confined(root, f"docs/tdq/artifacts/{SLUG}")
    for candidate in ("independent-review.json", "independent-qc.json", "review.json"):
        cand_path = artifact_dir / candidate
        if cand_path.is_file():
            data = read_json(cand_path)
            status = data.get("status") or data.get("verdict")
            require(status == "PASS", f"Independent review {candidate} status is not PASS: {status}")
            require(not data.get("open_findings"), f"Independent review {candidate} has open findings")
            return
    qc_md = resolve_confined(root, f"docs/tdq/qc/{SLUG}.md")
    require(qc_md.is_file(), "Missing independent review JSON or QC markdown document")
    text = qc_md.read_text(encoding="utf-8")
    require("review" in text.lower() and "pass" in text.lower(),
            "QC document lacks independent review PASS confirmation")


def _verify_q10(root: Path, index: dict[str, Any]) -> dict[str, Any]:
    binding = verify_archify_binding(root, index)
    report_path = resolve_confined(root, f"docs/tdq/reports/{SLUG}.md")
    report_text = report_path.read_text(encoding="utf-8").lower()
    require("synthetic" in report_text or "offline" in report_text,
            "Report must state synthetic/offline provenance")
    lint_targets = [
        index["spec_path"],
        "skills/tdq-build/references/skill-eval.md",
    ]
    cmd = [sys.executable, str(resolve_confined(root, "scripts/doc_lint.py")), *lint_targets]
    proc = subprocess.run(
        cmd,
        cwd=str(root),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
        check=False,
    )
    require(proc.returncode == 0,
            f"doc_lint.py failed (exit {proc.returncode}): {(proc.stdout + proc.stderr)[-400:]}")
    return {"archify_binding": binding["manifest_digest"], "doc_lint_exit": 0}


def verify_check(check_id: str, root: Path, index: dict[str, Any]) -> dict[str, Any]:
    require(check_id in EXPECTED_DOD_KEYS, f"Unknown DoD check: {check_id}")
    verify_evidence_index(index)
    verify_archify_binding(root, index)
    verify_baseline(root, index)

    dod_entry = index["dod_checks"][check_id]
    require_files_exist(root, dod_entry["required_files"])
    details = run_pytest_files(root, dod_entry.get("test_files", []))

    dispatch = {
        "Q1": lambda: _verify_q1(root),
        "Q2": lambda: _verify_q2(root, index),
        "Q3": lambda: _verify_q3(root),
        "Q4": lambda: _verify_q4(root),
        "Q5": lambda: _verify_q5(root),
        "Q6": lambda: _verify_q6(root),
        "Q7": lambda: _verify_q7(root),
        "Q8": lambda: _verify_q8(root),
        "Q9": lambda: _verify_q9(root),
        "Q10": lambda: _verify_q10(root, index),
    }
    details.update(dispatch[check_id]())
    return {"check": check_id, "status": "PASS", "details": details}


def run_self_test(root: Path, evidence_dir: Path) -> int:
    index_path = evidence_dir / "evidence-index.json"
    index = read_json(index_path)

    class ScopeSelfTest(unittest.TestCase):
        def test_real_evidence_index_and_archify_binding(self) -> None:
            info = verify_evidence_index(index)
            self.assertEqual(info["outputs"], 7)
            self.assertEqual(info["dod_checks"], 10)
            binding = verify_archify_binding(root, index)
            self.assertEqual(binding["manifest_digest"], EXPECTED_MANIFEST_DIGEST)
            self.assertEqual(binding["document_digest"], EXPECTED_DOC_DIGEST)
            self.assertEqual(binding["artifact_digest"], EXPECTED_HTML_DIGEST)

        def test_real_analysis_baseline(self) -> None:
            base = verify_baseline(root, index)
            self.assertEqual(base["source_sha256"], EXPECTED_BASELINE_SOURCE_SHA)
            self.assertEqual(base["probes"], 4)

        def test_fail_closed_on_missing_evidence_file(self) -> None:
            with tempfile.TemporaryDirectory() as tmp:
                with self.assertRaises(ValueError):
                    require_files_exist(Path(tmp), ["scripts/tdq_eval_contract.py"])

        def test_fail_closed_on_stale_manifest_or_spec_digest(self) -> None:
            bad_index = json.loads(json.dumps(index))
            bad_index["preview_manifest_digest"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "digest"):
                verify_evidence_index(bad_index)
            bad_spec_index = json.loads(json.dumps(index))
            bad_spec_index["spec_sha256"] = "f" * 64
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                verify_archify_binding(root, bad_spec_index)

        def test_fail_closed_on_stale_source_sha_and_false_pass(self) -> None:
            valid_runtime = {
                "status": "PASS",
                "exit_code": 0,
                "timed_out": False,
                "paid_model_calls": 0,
                "source_sha256": "a" * 64,
                "scenarios": [
                    {
                        "name": "smoke-preflight",
                        "exit_code": 0,
                        "elapsed_seconds": 1.2,
                        "deadline_seconds": 120.0,
                        "process": {"ownership_verified": True, "cleanup_complete": True},
                    }
                ],
            }
            verify_runtime_payload(valid_runtime, expected_source_sha="a" * 64)
            with self.assertRaisesRegex(ValueError, "Stale source SHA"):
                verify_runtime_payload(valid_runtime, expected_source_sha="b" * 64)
            false_pass = json.loads(json.dumps(valid_runtime))
            false_pass["exit_code"] = 1
            with self.assertRaisesRegex(ValueError, "False PASS"):
                verify_runtime_payload(false_pass)
            paid_call = json.loads(json.dumps(valid_runtime))
            paid_call["paid_model_calls"] = 1
            with self.assertRaisesRegex(ValueError, "paid model"):
                verify_runtime_payload(paid_call)

        def test_q1_to_q10_fail_closed_when_outputs_absent(self) -> None:
            with tempfile.TemporaryDirectory() as tmp:
                tmp_root = Path(tmp)
                for subdir in ("docs/tdq/spec", f"docs/tdq/artifacts/{SLUG}"):
                    (tmp_root / subdir).mkdir(parents=True, exist_ok=True)
                for rel in (
                    index["spec_path"],
                    index["preview_html"],
                    index["preview_manifest"],
                    index["baseline_path"],
                ):
                    src = resolve_confined(root, rel)
                    dst = tmp_root / rel
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    dst.write_bytes(src.read_bytes())
                for check_id in EXPECTED_DOD_KEYS:
                    with self.assertRaises(ValueError, msg=f"{check_id} must fail when O1-O7 are absent"):
                        verify_check(check_id, tmp_root, index)
            if not (root / "scripts/tdq_eval_contract.py").exists():
                for check_id in EXPECTED_DOD_KEYS:
                    with self.assertRaises(ValueError):
                        verify_check(check_id, root, index)

        def test_logging_on_by_default_and_muted_when_disabled(self) -> None:
            buf_on = io.StringIO()
            old_log = os.environ.pop("TDQ_LOG", None)
            old_eval_log = os.environ.pop("TDQ_EVAL_LOG", None)
            try:
                log("selftest-active", stream=buf_on)
                self.assertIn("verify_scope: selftest-active", buf_on.getvalue())
                os.environ["TDQ_LOG"] = "0"
                buf_off = io.StringIO()
                log("selftest-muted", stream=buf_off)
                self.assertEqual(buf_off.getvalue(), "")
            finally:
                if old_log is not None:
                    os.environ["TDQ_LOG"] = old_log
                else:
                    os.environ.pop("TDQ_LOG", None)
                if old_eval_log is not None:
                    os.environ["TDQ_EVAL_LOG"] = old_eval_log
                else:
                    os.environ.pop("TDQ_EVAL_LOG", None)

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ScopeSelfTest)
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    summary = {
        "kind": "synthetic-validator-selftest",
        "slug": SLUG,
        "tests_run": result.testsRun,
        "successful": result.wasSuccessful(),
        "paid_model_calls": 0,
    }
    print(json.dumps(summary))
    return 0 if result.wasSuccessful() else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checks", nargs="*", help="DoD check IDs (Q1..Q10)")
    parser.add_argument("--self-test", action="store_true", help="Run internal fail-closed self-tests")
    parser.add_argument("--all", action="store_true", help="Verify all Q1..Q10 checks")
    parser.add_argument("--evidence", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[4])
    args = parser.parse_args(argv)

    root = args.root.resolve()
    evidence_dir = args.evidence.resolve()
    log(f"start root={root} self_test={args.self_test} all={args.all} checks={args.checks}")

    if args.self_test:
        try:
            return run_self_test(root, evidence_dir)
        except Exception as exc:
            err = {"check": "self-test", "status": "FAIL", "error": f"{type(exc).__name__}: {exc}"}
            log(err["error"])
            print(json.dumps(err))
            return 1

    selected = list(EXPECTED_DOD_KEYS) if args.all else list(args.checks)
    if not selected:
        parser.error("Specify --self-test, --all, or at least one check (Q1..Q10)")

    index = read_json(evidence_dir / "evidence-index.json")
    results: list[dict[str, Any]] = []
    failed = False
    for check_id in selected:
        try:
            res = verify_check(check_id, root, index)
            results.append(res)
            log(f"{check_id} PASS")
        except Exception as exc:
            failed = True
            err = {"check": check_id, "status": "FAIL", "error": f"{type(exc).__name__}: {exc}"}
            results.append(err)
            log(f"{check_id} FAIL: {err['error']}")

    output = results[0] if len(results) == 1 and not args.all else {
        "slug": SLUG,
        "status": "FAIL" if failed else "PASS",
        "results": results,
    }
    print(json.dumps(output))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())