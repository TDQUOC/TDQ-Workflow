"""Test for Archify freshness integration in tdq_finish.py (T3.3).

Contract coverage:
- Absent manifest -> skip (exit 0)
- Current manifest -> ok (exit 0)
- Stale manifest (source changed, revision changed, child_files changed) -> clear refresh-needed status (exit 0)
- Invalid manifest / error -> fail (exit 1), but worklog MUST still run
- No side effects on dry-run
- Docs/workinglog/tdq/logs changes do not trigger infinite refresh
- Output format and order preserved
- Real fingerprints, no mocking of core hashing
"""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(REPO, "scripts")
SCRIPT = os.path.join(SCRIPTS_DIR, "tdq_finish.py")
sys.path.insert(0, SCRIPTS_DIR)
import archify_artifacts
import tdq_finish


def _setup_git_project(tmp, *, init_tdq=True):
    """Create a temporary git repository with clean commit and initial files."""
    subprocess.run(["git", "init"], cwd=tmp, capture_output=True, check=True, text=True, encoding="utf-8")
    subprocess.run(["git", "config", "user.name", "Test TDQ"], cwd=tmp, capture_output=True, check=True, text=True, encoding="utf-8")
    subprocess.run(["git", "config", "user.email", "tdq@example.com"], cwd=tmp, capture_output=True, check=True, text=True, encoding="utf-8")
    subprocess.run(["git", "config", "core.autocrlf", "false"], cwd=tmp, capture_output=True, check=True, text=True, encoding="utf-8")

    src_dir = os.path.join(tmp, "src")
    docs_dir = os.path.join(tmp, "docs")
    arch_dir = os.path.join(tmp, "docs", "architecture")
    os.makedirs(src_dir, exist_ok=True)
    os.makedirs(arch_dir, exist_ok=True)

    src_file = os.path.join(src_dir, "main.py")
    with open(src_file, "w", encoding="utf-8") as f:
        f.write("# Source file\nprint('hello world')\n")

    doc_file = os.path.join(docs_dir, "spec.md")
    with open(doc_file, "w", encoding="utf-8") as f:
        f.write("# Architecture Spec\n\nSpec content.\n")

    cand_file = os.path.join(arch_dir, "overview.candidate.json")
    with open(cand_file, "w", encoding="utf-8") as f:
        json.dump({"diagram_type": "architecture", "components": [{"id": "c1", "label": "Component 1"}]}, f, indent=2)

    art_file = os.path.join(arch_dir, "index.html")
    with open(art_file, "w", encoding="utf-8") as f:
        f.write("<!DOCTYPE html><html><body><h1>Master Architecture</h1></body></html>\n")

    view_file = os.path.join(arch_dir, "overview.html")
    with open(view_file, "w", encoding="utf-8") as f:
        f.write("<!DOCTYPE html><html><body><h2>Overview View</h2></body></html>\n")

    subprocess.run(["git", "add", "."], cwd=tmp, capture_output=True, check=True, text=True, encoding="utf-8")
    subprocess.run(["git", "commit", "-m", "initial commit"], cwd=tmp, capture_output=True, check=True, text=True, encoding="utf-8")

    rev_proc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp, capture_output=True, check=True, text=True, encoding="utf-8")
    rev = rev_proc.stdout.strip()

    if init_tdq:
        subprocess.run([sys.executable, os.path.join(SCRIPTS_DIR, "tdq_state.py"),
                        "init", "2026-10-24-2348-hoan-thien-archify", "full"],
                       cwd=tmp, capture_output=True, text=True, encoding="utf-8",
                       env={**os.environ, "TDQ_PROJECT_DIR": tmp})

    return {
        "project": tmp,
        "src_file": src_file,
        "doc_file": doc_file,
        "cand_file": cand_file,
        "art_file": art_file,
        "view_file": view_file,
        "revision": rev,
    }


def _create_valid_manifest(info, *, evidence_kind="committed", child_files=True):
    """Build and write a real, valid schema_version=1 manifest using archify_artifacts.build_manifest."""
    tmp = info["project"]
    receipt = {
        "ok": True,
        "status": "pass",
        "engine": "archify",
        "views_count": 1,
        "index": "index.html",
    }
    manifest = archify_artifacts.build_manifest(
        project=tmp,
        document=info["doc_file"],
        candidate=info["cand_file"],
        artifact=info["art_file"],
        receipt=receipt,
        evidence_kind=evidence_kind,
        revision=info["revision"] if evidence_kind == "committed" else None,
        source_paths=["src/main.py"],
    )
    if child_files and os.path.exists(info["view_file"]):
        manifest["child_files"] = {
            "overview.html": archify_artifacts._hash_file(Path(info["view_file"])),
            "overview.candidate.json": archify_artifacts._hash_file(Path(info["cand_file"])),
        }

    man_path = os.path.join(tmp, "docs", "architecture", "manifest.json")
    with open(man_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    return man_path


def _run_finish(args, project, env=None):
    """Run tdq_finish.py with UTF-8, timeout, and environment isolation."""
    e = {**os.environ, "TDQ_PROJECT_DIR": project}
    if env:
        e.update(env)
    return subprocess.run(
        [sys.executable, SCRIPT] + args,
        cwd=project,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        text=True,
        timeout=30,
        env=e,
    )


class TestStepArchifyUnit(unittest.TestCase):
    """Unit tests for tdq_finish.step_archify directly."""

    def test_missing_manifest_returns_skip(self):
        with tempfile.TemporaryDirectory() as tmp:
            _setup_git_project(tmp)
            res = tdq_finish.step_archify(tmp)
            self.assertEqual(res.name, "archify")
            self.assertEqual(res.status, "skip")
            self.assertIn("no manifest", res.detail)
            status_path = os.path.join(tmp, "docs", "architecture", "status.json")
            self.assertFalse(os.path.exists(status_path))

    def test_current_manifest_returns_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            info = _setup_git_project(tmp)
            _create_valid_manifest(info)
            res = tdq_finish.step_archify(tmp)
            self.assertEqual(res.name, "archify")
            self.assertEqual(res.status, "ok")
            self.assertEqual(res.detail, "current")

            status_path = os.path.join(tmp, "docs", "architecture", "status.json")
            self.assertTrue(os.path.exists(status_path))
            with open(status_path, "r", encoding="utf-8") as sf:
                sdata = json.load(sf)
            self.assertEqual(sdata.get("status"), "current")

    def test_stale_source_change_returns_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            info = _setup_git_project(tmp)
            _create_valid_manifest(info)
            with open(info["src_file"], "w", encoding="utf-8") as f:
                f.write("# Source modified\nprint('modified')\n")

            res = tdq_finish.step_archify(tmp)
            self.assertEqual(res.name, "archify")
            self.assertEqual(res.status, "stale")
            self.assertIn("refresh needed", res.detail)

            status_path = os.path.join(tmp, "docs", "architecture", "status.json")
            with open(status_path, "r", encoding="utf-8") as sf:
                sdata = json.load(sf)
            self.assertEqual(sdata.get("status"), "stale")

    def test_stale_git_revision_returns_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            info = _setup_git_project(tmp)
            _create_valid_manifest(info, evidence_kind="committed")
            subprocess.run(["git", "commit", "--allow-empty", "-m", "second commit"],
                           cwd=tmp, check=True, capture_output=True)

            res = tdq_finish.step_archify(tmp)
            self.assertEqual(res.name, "archify")
            self.assertEqual(res.status, "stale")
            self.assertIn("refresh needed", res.detail)

            status_path = os.path.join(tmp, "docs", "architecture", "status.json")
            with open(status_path, "r", encoding="utf-8") as sf:
                sdata = json.load(sf)
            self.assertEqual(sdata.get("status"), "stale")

    def test_stale_child_files_tampered_returns_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            info = _setup_git_project(tmp)
            _create_valid_manifest(info, child_files=True)
            with open(info["view_file"], "a", encoding="utf-8") as f:
                f.write("<!-- tampered view -->\n")

            res = tdq_finish.step_archify(tmp)
            self.assertEqual(res.name, "archify")
            self.assertEqual(res.status, "stale")
            self.assertIn("refresh needed", res.detail)
            self.assertTrue(any(k in res.detail for k in ("Child file", "digest mismatch", "tampered")))

            status_path = os.path.join(tmp, "docs", "architecture", "status.json")
            with open(status_path, "r", encoding="utf-8") as sf:
                sdata = json.load(sf)
            self.assertEqual(sdata.get("status"), "stale")

    def test_stale_child_files_missing_returns_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            info = _setup_git_project(tmp)
            _create_valid_manifest(info, child_files=True)
            os.remove(info["view_file"])

            res = tdq_finish.step_archify(tmp)
            self.assertEqual(res.name, "archify")
            self.assertEqual(res.status, "stale")
            self.assertIn("refresh needed", res.detail)
            self.assertIn("missing", res.detail)

    def test_invalid_manifest_corrupted_json_returns_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            info = _setup_git_project(tmp)
            man_path = os.path.join(tmp, "docs", "architecture", "manifest.json")
            with open(man_path, "w", encoding="utf-8") as f:
                f.write("{corrupt json...")

            res = tdq_finish.step_archify(tmp)
            self.assertEqual(res.name, "archify")
            self.assertEqual(res.status, "fail")

    def test_invalid_manifest_bad_schema_version_returns_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            info = _setup_git_project(tmp)
            man_path = os.path.join(tmp, "docs", "architecture", "manifest.json")
            with open(man_path, "w", encoding="utf-8") as f:
                json.dump({"schema_version": 999}, f)

            res = tdq_finish.step_archify(tmp)
            self.assertEqual(res.name, "archify")
            self.assertEqual(res.status, "fail")

    def test_manifest_present_import_error_returns_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            info = _setup_git_project(tmp)
            _create_valid_manifest(info)
            from unittest.mock import patch
            with patch.dict("sys.modules", {"archify_artifacts": None}):
                res = tdq_finish.step_archify(tmp)
                self.assertEqual(res.name, "archify")
                self.assertEqual(res.status, "fail")
                self.assertIn("archify_artifacts not available", res.detail)

    def test_malformed_mark_stale_result_returns_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            info = _setup_git_project(tmp)
            _create_valid_manifest(info)
            from unittest.mock import patch
            with patch("archify_artifacts.mark_stale", return_value="not a dict"):
                res = tdq_finish.step_archify(tmp)
                self.assertEqual(res.name, "archify")
                self.assertEqual(res.status, "fail")
                self.assertIn("invalid mark_stale result type", res.detail)

            with patch("archify_artifacts.mark_stale", return_value={"status": "stale", "reasons": "not a list"}):
                res = tdq_finish.step_archify(tmp)
                self.assertEqual(res.name, "archify")
                self.assertEqual(res.status, "fail")
                self.assertIn("invalid reasons type", res.detail)


class TestFinishArchifyIntegration(unittest.TestCase):
    """Integration CLI tests calling tdq_finish.py via subprocess."""

    def test_finish_missing_manifest_skips_and_exits_0(self):
        with tempfile.TemporaryDirectory() as tmp:
            _setup_git_project(tmp)
            r = _run_finish(["--verbose"], tmp)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("archify skip", r.stdout)
            self.assertIn("archify=skip", r.stdout)
            status_path = os.path.join(tmp, "docs", "architecture", "status.json")
            self.assertFalse(os.path.exists(status_path))

    def test_finish_current_manifest_exits_0(self):
        with tempfile.TemporaryDirectory() as tmp:
            info = _setup_git_project(tmp)
            _create_valid_manifest(info)
            r = _run_finish(["--verbose"], tmp)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("archify ok", r.stdout)
            self.assertIn("archify=ok", r.stdout)

            status_path = os.path.join(tmp, "docs", "architecture", "status.json")
            self.assertTrue(os.path.exists(status_path))
            with open(status_path, "r", encoding="utf-8") as sf:
                sdata = json.load(sf)
            self.assertEqual(sdata.get("status"), "current")

    def test_finish_stale_source_change_reports_refresh_needed_and_exits_0(self):
        with tempfile.TemporaryDirectory() as tmp:
            info = _setup_git_project(tmp)
            _create_valid_manifest(info)
            with open(info["src_file"], "w", encoding="utf-8") as f:
                f.write("# Source modified\nprint('new code')\n")

            r = _run_finish([], tmp)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("archify=stale", r.stdout)
            self.assertIn("archify stale (refresh needed:", r.stdout)

            status_path = os.path.join(tmp, "docs", "architecture", "status.json")
            with open(status_path, "r", encoding="utf-8") as sf:
                sdata = json.load(sf)
            self.assertEqual(sdata.get("status"), "stale")

    def test_finish_invalid_manifest_fails_but_worklog_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            info = _setup_git_project(tmp)
            man_path = os.path.join(tmp, "docs", "architecture", "manifest.json")
            with open(man_path, "w", encoding="utf-8") as f:
                f.write("not a valid json")

            log_message = "Crucial worklog entry that must be preserved"
            r = _run_finish(["--log", log_message], tmp)
            self.assertNotEqual(r.returncode, 0, "Invalid manifest must cause finish to fail")
            self.assertIn("archify=fail", r.stdout)
            self.assertIn("archify fail", r.stdout)

            # Worklog must still run despite archify fail
            log_dir = os.path.join(tmp, "docs", "workinglog")
            log_files = os.listdir(log_dir) if os.path.isdir(log_dir) else []
            self.assertEqual(len(log_files), 1, "Working log file must be written")
            with open(os.path.join(log_dir, log_files[0]), "r", encoding="utf-8") as lf:
                content = lf.read()
            self.assertIn(log_message, content)

    def test_finish_dry_run_has_no_side_effects(self):
        with tempfile.TemporaryDirectory() as tmp:
            info = _setup_git_project(tmp)
            _create_valid_manifest(info)

            r = _run_finish(["--dry-run", "--log", "Should not be logged"], tmp)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            non_empty_lines = [l for l in r.stdout.splitlines() if l.strip()]
            self.assertEqual(len(non_empty_lines), 1)

            status_path = os.path.join(tmp, "docs", "architecture", "status.json")
            self.assertFalse(os.path.exists(status_path), "Dry-run must not create status.json")

            log_dir = os.path.join(tmp, "docs", "workinglog")
            self.assertFalse(os.path.exists(log_dir) and bool(os.listdir(log_dir)), "Dry-run must not write logs")

    def test_docs_and_logs_do_not_trigger_infinite_refresh(self):
        with tempfile.TemporaryDirectory() as tmp:
            info = _setup_git_project(tmp)
            _create_valid_manifest(info)

            # Create working log and tdq timing files
            wlog_dir = os.path.join(tmp, "docs", "workinglog")
            os.makedirs(wlog_dir, exist_ok=True)
            with open(os.path.join(wlog_dir, "2026-10-25.md"), "w", encoding="utf-8") as f:
                f.write("# Working log\n")

            tdq_dir = os.path.join(tmp, "docs", "tdq")
            os.makedirs(tdq_dir, exist_ok=True)
            with open(os.path.join(tdq_dir, "timing.jsonl"), "w", encoding="utf-8") as f:
                f.write('{"phase": "qc"}\n')

            logs_dir = os.path.join(tmp, "logs")
            os.makedirs(logs_dir, exist_ok=True)
            with open(os.path.join(logs_dir, "app.log"), "w", encoding="utf-8") as f:
                f.write("Log line\n")

            # Run finish multiple times
            r1 = _run_finish(["--log", "First turn summary"], tmp)
            self.assertEqual(r1.returncode, 0, r1.stdout + r1.stderr)
            self.assertIn("archify=ok", r1.stdout)

            r2 = _run_finish(["--log", "Second turn summary"], tmp)
            self.assertEqual(r2.returncode, 0, r2.stdout + r2.stderr)
            self.assertIn("archify=ok", r2.stdout)

            status_path = os.path.join(tmp, "docs", "architecture", "status.json")
            with open(status_path, "r", encoding="utf-8") as sf:
                sdata = json.load(sf)
            self.assertEqual(sdata.get("status"), "current")

    def test_output_size_under_200_chars_when_current(self):
        with tempfile.TemporaryDirectory() as tmp:
            info = _setup_git_project(tmp)
            _create_valid_manifest(info)

            r = _run_finish([], tmp)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertLessEqual(len(r.stdout.strip()), 200, r.stdout)


if __name__ == "__main__":
    unittest.main()