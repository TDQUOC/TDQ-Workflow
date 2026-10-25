"""Integration and pipeline tests for Archify CLI orchestration (T3.1).

Covers:
- render CLI: with/without document, staging & rollback (last-good preservation on missing doc, engine failure, bind failure)
- fail injection tests: transactional rollback with pre-existing bundle and fresh failure
- bridge CLI: candidate generation + coverage sidecar (.coverage.json) and error handling on empty nodes / invalid scalar
- sync-master CLI:
  * Master model validation (empty, invalid envelope, views)
  * Candidate confinement relative to model parent
  * Git revision and dirty verification for committed evidence (including raw Unicode paths and directory prefixes)
  * Model lacking explicit source_paths derives stable sources without staging self-stale
  * Multi-view native rendering via delivery
  * Safe index.html generation (escaped labels, relative links, revision, coverage)
  * Manifest final-path rebasing (no temp paths leaked, honest receipts)
  * Preserving previous good bundle on failure (no loss/corruption)
  * Child file binding and tampering detection
- status CLI: freshness inspection, child tampering detection
- verify CLI: document binding and manifest freshness verification
- Local Archify real engine smoke: real bound explainer render then verify immediately current
"""
from __future__ import annotations

import html
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

# Ensure scripts dir of current worktree is on sys.path
WORKTREE_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = WORKTREE_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import tdq_archify
import archify_delivery
import archify_artifacts
import archify_model


def _init_git_repo(repo_dir: Path) -> str:
    """Initialize a git repo with a commit and return HEAD revision."""
    subprocess.run(["git", "init"], cwd=str(repo_dir), capture_output=True, timeout=15, check=True)
    subprocess.run(["git", "config", "user.name", "Tester"], cwd=str(repo_dir), capture_output=True, timeout=15, check=True)
    subprocess.run(["git", "config", "user.email", "tester@example.com"], cwd=str(repo_dir), capture_output=True, timeout=15, check=True)
    src_file = repo_dir / "src" / "main.py"
    src_file.parent.mkdir(parents=True, exist_ok=True)
    src_file.write_text("print('hello')\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=str(repo_dir), capture_output=True, timeout=15, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=str(repo_dir), capture_output=True, timeout=15, check=True)
    proc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(repo_dir), capture_output=True, text=True, encoding="utf-8", timeout=15, check=True)
    return proc.stdout.strip()


class TestRenderCliBinding(unittest.TestCase):
    """Test render CLI sub-command with and without document binding and staging rollback."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir, True)
        self.project_dir = Path(self.temp_dir)
        self.candidate = self.project_dir / "cand.json"
        self.candidate.write_text(json.dumps({"schema_version": 1, "components": []}), encoding="utf-8")
        self.out_html = self.project_dir / "output.html"

    def test_render_without_document_returns_unbound(self):
        """Render without --document reports artifact_unbound and does not claim registered."""
        fake_receipt = {
            "ok": True,
            "status": "pass",
            "artifact": str(self.out_html),
            "gates": {"validate": "pass", "deliver": "pass", "check": "pass", "browser-check": "pass"},
        }
        fake_res = archify_delivery.FinalizeResult(status=True, receipt=fake_receipt)

        def mock_finalize(diagram_type, candidate_path, output_path, **kwargs):
            Path(output_path).write_text("<html>Staged</html>", encoding="utf-8")
            return fake_res

        with mock.patch("tdq_archify.run_finalize", side_effect=mock_finalize):
            with mock.patch.object(
                sys,
                "argv",
                [
                    "tdq_archify.py",
                    "render",
                    "--type", "architecture",
                    "--candidate", str(self.candidate),
                    "--out", str(self.out_html),
                ],
            ):
                with mock.patch("sys.stdout") as mock_out:
                    code = tdq_archify.main()
                    self.assertEqual(code, 0)
                    output = "".join(call.args[0] for call in mock_out.write.call_args_list)
                    data = json.loads(output)
                    self.assertIn("binding", data)
                    self.assertEqual(data["binding"], "unbound")
                    self.assertTrue(self.out_html.is_file())

    def test_render_with_document_creates_manifest_and_binds(self):
        """Render with --document creates manifest beside output and binds document."""
        doc = self.project_dir / "SPEC.md"
        doc.write_text("# Spec Title\n\nSome spec content.\n", encoding="utf-8")

        fake_receipt = {
            "ok": True,
            "status": "pass",
            "artifact": str(self.out_html),
            "gates": {"validate": "pass", "deliver": "pass", "check": "pass", "browser-check": "pass"},
        }
        fake_res = archify_delivery.FinalizeResult(status=True, receipt=fake_receipt)

        def mock_finalize(diagram_type, candidate_path, output_path, **kwargs):
            Path(output_path).write_text("<html>Preview Content</html>", encoding="utf-8")
            return fake_res

        with mock.patch("tdq_archify.run_finalize", side_effect=mock_finalize):
            with mock.patch.object(
                sys,
                "argv",
                [
                    "tdq_archify.py",
                    "render",
                    "--type", "architecture",
                    "--candidate", str(self.candidate),
                    "--out", str(self.out_html),
                    "--document", str(doc),
                    "--request", "req-123",
                    "--lane", "full",
                    "--repo-root", str(self.project_dir),
                ],
            ):
                code = tdq_archify.main()
                self.assertEqual(code, 0)

        manifest_path = self.out_html.with_suffix(".manifest.json")
        self.assertTrue(manifest_path.is_file(), f"Manifest expected at {manifest_path}")

        bound_doc_content = doc.read_text(encoding="utf-8")
        self.assertIn(archify_artifacts.BINDING_START, bound_doc_content)
        self.assertIn(archify_artifacts.BINDING_END, bound_doc_content)

        b_check = archify_artifacts.check_binding(doc, manifest_path)
        self.assertTrue(b_check.get("valid"))
        self.assertEqual(b_check.get("status"), "current")

    def test_render_staging_preserves_previous_artifact_on_missing_doc(self):
        """Missing --document fails before running finalize and preserves existing artifact."""
        self.out_html.write_text("<html>ORIGINAL_GOOD</html>", encoding="utf-8")
        missing_doc = self.project_dir / "nonexistent.md"

        with mock.patch.object(
            sys,
            "argv",
            [
                "tdq_archify.py",
                "render",
                "--type", "architecture",
                "--candidate", str(self.candidate),
                "--out", str(self.out_html),
                "--document", str(missing_doc),
            ],
        ):
            code = tdq_archify.main()
            self.assertNotEqual(code, 0)
            self.assertEqual(self.out_html.read_text(encoding="utf-8"), "<html>ORIGINAL_GOOD</html>")

    def test_render_staging_preserves_previous_artifact_on_engine_failure(self):
        """Engine failure during finalize preserves previous artifact without corruption."""
        self.out_html.write_text("<html>ORIGINAL_GOOD</html>", encoding="utf-8")
        doc = self.project_dir / "SPEC.md"
        doc.write_text("# Title\n", encoding="utf-8")

        failing_res = archify_delivery.FinalizeResult(status=False, receipt={"ok": False, "status": "fail"})
        with mock.patch("tdq_archify.run_finalize", return_value=failing_res):
            with mock.patch.object(
                sys,
                "argv",
                [
                    "tdq_archify.py",
                    "render",
                    "--type", "architecture",
                    "--candidate", str(self.candidate),
                    "--out", str(self.out_html),
                    "--document", str(doc),
                ],
            ):
                code = tdq_archify.main()
                self.assertNotEqual(code, 0)
                self.assertEqual(self.out_html.read_text(encoding="utf-8"), "<html>ORIGINAL_GOOD</html>")

    def test_render_rollback_on_bind_failure_with_existing_bundle(self):
        """Fail injection: if bind_document fails, restores previous HTML, manifest, and document bytes."""
        orig_html_bytes = b"<html>ORIGINAL_PREVIEW_V1</html>"
        orig_manifest_bytes = b'{"version": 1, "status": "old"}'
        orig_doc_bytes = b"# Spec Title\n\nOriginal document text before render.\n"

        self.out_html.write_bytes(orig_html_bytes)
        manifest_path = self.out_html.with_suffix(".manifest.json")
        manifest_path.write_bytes(orig_manifest_bytes)
        doc = self.project_dir / "SPEC.md"
        doc.write_bytes(orig_doc_bytes)

        fake_res = archify_delivery.FinalizeResult(
            status=True,
            receipt={"ok": True, "status": "pass", "artifact": str(self.out_html)},
        )

        def mock_finalize(diagram_type, candidate_path, output_path, **kwargs):
            Path(output_path).write_text("<html>NEW_PREVIEW_V2</html>", encoding="utf-8")
            return fake_res

        with mock.patch("tdq_archify.run_finalize", side_effect=mock_finalize):
            with mock.patch("tdq_archify.bind_document", side_effect=RuntimeError("Simulated bind failure")):
                with mock.patch.object(
                    sys,
                    "argv",
                    [
                        "tdq_archify.py",
                        "render",
                        "--type", "architecture",
                        "--candidate", str(self.candidate),
                        "--out", str(self.out_html),
                        "--document", str(doc),
                        "--repo-root", str(self.project_dir),
                    ],
                ):
                    code = tdq_archify.main()
                    self.assertNotEqual(code, 0)

        self.assertEqual(self.out_html.read_bytes(), orig_html_bytes, "Previous HTML artifact must be restored")
        self.assertEqual(manifest_path.read_bytes(), orig_manifest_bytes, "Previous manifest must be restored")
        self.assertEqual(doc.read_bytes(), orig_doc_bytes, "Original document bytes must be restored")

    def test_render_rollback_on_fresh_failure_leaves_no_artifacts(self):
        """Fail injection: on fresh render failure, leaves no dangling HTML or manifest and restores doc."""
        orig_doc_bytes = b"# Fresh Spec\n\nFresh doc text.\n"
        doc = self.project_dir / "FRESH_SPEC.md"
        doc.write_bytes(orig_doc_bytes)

        manifest_path = self.out_html.with_suffix(".manifest.json")
        self.assertFalse(self.out_html.exists())
        self.assertFalse(manifest_path.exists())

        fake_res = archify_delivery.FinalizeResult(
            status=True,
            receipt={"ok": True, "status": "pass", "artifact": str(self.out_html)},
        )

        def mock_finalize(diagram_type, candidate_path, output_path, **kwargs):
            Path(output_path).write_text("<html>DANGLING_HTML</html>", encoding="utf-8")
            return fake_res

        with mock.patch("tdq_archify.run_finalize", side_effect=mock_finalize):
            with mock.patch("tdq_archify.bind_document", side_effect=RuntimeError("Simulated bind failure")):
                with mock.patch.object(
                    sys,
                    "argv",
                    [
                        "tdq_archify.py",
                        "render",
                        "--type", "architecture",
                        "--candidate", str(self.candidate),
                        "--out", str(self.out_html),
                        "--document", str(doc),
                        "--repo-root", str(self.project_dir),
                    ],
                ):
                    code = tdq_archify.main()
                    self.assertNotEqual(code, 0)

        self.assertFalse(self.out_html.exists(), "Newly created HTML must be deleted on failure")
        self.assertFalse(manifest_path.exists(), "Newly created manifest must be deleted on failure")
        self.assertEqual(doc.read_bytes(), orig_doc_bytes, "Document bytes must be restored")



    def test_render_restore_failure_retains_backup(self):
        """If restoring from backup fails during rollback, backup file is NOT deleted and recovery is logged."""
        orig_html = b"<html>ORIGINAL_GOOD_V1</html>"
        self.out_html.write_bytes(orig_html)
        doc = self.project_dir / "SPEC.md"
        doc.write_text("# Title\n", encoding="utf-8")

        fake_res = archify_delivery.FinalizeResult(
            status=True,
            receipt={"ok": True, "status": "pass", "artifact": str(self.out_html)},
        )

        def mock_finalize(diagram_type, candidate_path, output_path, **kwargs):
            Path(output_path).write_text("<html>STAGED_FAIL</html>", encoding="utf-8")
            return fake_res

        real_replace = os.replace
        def failing_replace(src, dst):
            # Fail only when attempting to restore backup to out_html
            if ".bak." in str(src):
                raise OSError("Simulated filesystem lock during backup restoration")
            return real_replace(src, dst)

        with mock.patch("tdq_archify.run_finalize", side_effect=mock_finalize):
            with mock.patch("tdq_archify.bind_document", side_effect=RuntimeError("Bind failed")):
                with mock.patch("os.replace", side_effect=failing_replace):
                    with mock.patch("sys.stderr") as mock_err:
                        with mock.patch.object(
                            sys,
                            "argv",
                            [
                                "tdq_archify.py",
                                "render",
                                "--type", "architecture",
                                "--candidate", str(self.candidate),
                                "--out", str(self.out_html),
                                "--document", str(doc),
                                "--repo-root", str(self.project_dir),
                            ],
                        ):
                            code = tdq_archify.main()
                            self.assertNotEqual(code, 0)
                            err_output = "".join(call.args[0] for call in mock_err.write.call_args_list)
                            self.assertIn("Backup preserved at:", err_output)

        # Backup file must be preserved on disk
        backup_files = list(self.project_dir.glob(f".bak.{self.out_html.stem}.*.html"))
        self.assertTrue(len(backup_files) >= 1, "Backup file must be preserved on disk when restore fails")
        self.assertEqual(backup_files[0].read_bytes(), orig_html)

    def test_render_receipt_provenance_and_sidecar(self):
        """Successful render produces receipt sidecar, preserves provenance, and provides published path metadata."""
        doc = self.project_dir / "SPEC.md"
        doc.write_text("# Spec\n", encoding="utf-8")
        staged_temp = self.project_dir / "some_temp_staged.html"

        fake_res = archify_delivery.FinalizeResult(
            status=True,
            receipt={
                "ok": True,
                "status": "pass",
                "artifact": {"path": str(staged_temp), "sha256": "abc123"},
                "specification": {"sha256": "cand456"},
                "gates": {"validate": "pass", "deliver": "pass", "check": "pass", "browser-check": "pass"},
            },
        )

        def mock_finalize(diagram_type, candidate_path, output_path, **kwargs):
            Path(output_path).write_text("<html>Final content</html>", encoding="utf-8")
            return fake_res

        with mock.patch("tdq_archify.run_finalize", side_effect=mock_finalize):
            with mock.patch.object(
                sys,
                "argv",
                [
                    "tdq_archify.py",
                    "render",
                    "--type", "architecture",
                    "--candidate", str(self.candidate),
                    "--out", str(self.out_html),
                    "--document", str(doc),
                    "--repo-root", str(self.project_dir),
                ],
            ):
                with mock.patch("sys.stdout") as mock_out:
                    code = tdq_archify.main()
                    self.assertEqual(code, 0)
                    out_json = json.loads("".join(call.args[0] for call in mock_out.write.call_args_list))

        # Receipt sidecar on disk
        receipt_path = self.out_html.with_suffix(".receipt.json")
        self.assertTrue(receipt_path.is_file(), f"Receipt sidecar must exist at {receipt_path}")
        receipt_data = json.loads(receipt_path.read_text(encoding="utf-8"))
        # Honest engine receipt preserved (shows actual staging output)
        self.assertEqual(receipt_data["artifact"]["path"], str(staged_temp))

        # Response contains explicit published path metadata
        self.assertEqual(out_json["published_artifact"], str(self.out_html))
        self.assertEqual(out_json["receipt_path"], str(receipt_path))

        # Manifest contains honest receipt provenance
        manifest_path = self.out_html.with_suffix(".manifest.json")
        man_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(man_data["receipt"]["artifact"]["path"], str(staged_temp))
        self.assertEqual(man_data["artifact_path"], self.out_html.name)


class TestBridgeCliSidecar(unittest.TestCase):
    """Test bridge CLI creates candidate IR, coverage sidecar, and handles errors."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir, True)
        self.graph_file = Path(self.temp_dir) / "graph.json"
        self.out_cand = Path(self.temp_dir) / "candidate.json"
        sample_graph = {
            "directed": True,
            "nodes": [
                {"id": "api", "label": "API Gateway", "type": "security"},
                {"id": "db", "label": "Database", "type": "database"},
                {"id": "worker", "label": "Worker", "type": "backend"},
            ],
            "links": [
                {"source": "api", "target": "db", "relation": "reads"},
            ],
        }
        self.graph_file.write_text(json.dumps(sample_graph), encoding="utf-8")

    def test_bridge_creates_candidate_and_coverage_sidecar(self):
        """CLI bridge writes candidate JSON and .coverage.json sidecar."""
        with mock.patch.object(
            sys,
            "argv",
            [
                "tdq_archify.py",
                "bridge",
                "--graph", str(self.graph_file),
                "--out", str(self.out_cand),
                "--max-nodes", "2",
            ],
        ):
            code = tdq_archify.main()
            self.assertEqual(code, 0)

        self.assertTrue(self.out_cand.is_file())
        cand_data = json.loads(self.out_cand.read_text(encoding="utf-8"))
        self.assertEqual(cand_data["schema_version"], 1)

        sidecar_path = self.out_cand.with_suffix(".coverage.json")
        self.assertTrue(sidecar_path.is_file(), f"Coverage sidecar expected at {sidecar_path}")
        coverage_data = json.loads(sidecar_path.read_text(encoding="utf-8"))
        self.assertIn("total", coverage_data)
        self.assertIn("selected", coverage_data)
        self.assertIn("excluded", coverage_data)
        self.assertIn("inventory", coverage_data)
        self.assertEqual(coverage_data["total"], 3)

    def test_bridge_cli_empty_nodes_fails_without_traceback(self):
        """Bridge with empty nodes exits non-zero without unhandled traceback."""
        empty_graph = Path(self.temp_dir) / "empty.json"
        empty_graph.write_text(json.dumps({"nodes": [], "links": []}), encoding="utf-8")
        out_cand = Path(self.temp_dir) / "out_empty.json"

        with mock.patch.object(
            sys,
            "argv",
            ["tdq_archify.py", "bridge", "--graph", str(empty_graph), "--out", str(out_cand)],
        ):
            code = tdq_archify.main()
            self.assertNotEqual(code, 0)
            self.assertFalse(out_cand.exists())

    def test_bridge_cli_invalid_scalar_fails_without_traceback(self):
        """Bridge with invalid JSON scalar exits non-zero without unhandled traceback."""
        scalar_graph = Path(self.temp_dir) / "scalar.json"
        scalar_graph.write_text(json.dumps("invalid scalar string"), encoding="utf-8")
        out_cand = Path(self.temp_dir) / "out_scalar.json"

        with mock.patch.object(
            sys,
            "argv",
            ["tdq_archify.py", "bridge", "--graph", str(scalar_graph), "--out", str(out_cand)],
        ):
            code = tdq_archify.main()
            self.assertNotEqual(code, 0)
            self.assertFalse(out_cand.exists())


class TestSyncMasterPipeline(unittest.TestCase):
    """Test sync-master CLI pipeline with model validation, views, index HTML, and publish."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir, True)
        self.repo_dir = Path(self.temp_dir)
        self.rev = _init_git_repo(self.repo_dir)

        self.models_dir = self.repo_dir / "models"
        self.models_dir.mkdir(parents=True, exist_ok=True)

        self.cand1 = self.models_dir / "overview.json"
        self.cand1.write_text(json.dumps({"schema_version": 1, "diagram_type": "architecture", "components": []}), encoding="utf-8")

        self.cand2 = self.models_dir / "flow.json"
        self.cand2.write_text(json.dumps({"schema_version": 1, "diagram_type": "workflow", "steps": []}), encoding="utf-8")

        self.model_path = self.models_dir / "master.model.json"
        self.model_data = {
            "schema_version": 1,
            "title": "Master Architecture <Test & Escape>",
            "evidence_kind": "committed",
            "revision": self.rev,
            "repository": {
                "url": "https://example.invalid/repo.git",
                "revision": self.rev,
                "link_mode": "local-only",
            },
            "source_paths": ["src/main.py"],
            "coverage": {
                "modules": [{"id": "main", "status": "verified"}],
                "unknown": [],
                "excluded": [],
            },
            "views": [
                {"id": "overview", "type": "architecture", "candidate": "overview.json", "summary": "Overview View <Escaped>"},
                {"id": "flow", "type": "workflow", "candidate": "flow.json", "summary": "Workflow View"},
            ],
        }
        self.model_path.write_text(json.dumps(self.model_data), encoding="utf-8")

    def _mock_run_finalize_builder(self):
        """Helper to create a run_finalize mock that writes HTML output."""
        def fake_run_finalize(diagram_type, candidate_path, output_path, **kwargs):
            out_p = Path(output_path)
            out_p.parent.mkdir(parents=True, exist_ok=True)
            out_p.write_text(f"<html>{diagram_type} content</html>", encoding="utf-8")
            return archify_delivery.FinalizeResult(
                status=True,
                receipt={
                    "ok": True,
                    "status": "pass",
                    "artifact": str(out_p),
                    "gates": {"validate": "pass", "deliver": "pass", "check": "pass", "browser-check": "pass"},
                },
            )
        return fake_run_finalize

    def test_sync_master_empty_or_invalid_model_fails(self):
        """Empty or invalid model file must fail and not publish."""
        empty_model = self.models_dir / "empty.json"
        empty_model.write_text("", encoding="utf-8")
        out_dir = self.repo_dir / "docs" / "architecture"

        with mock.patch.object(
            sys,
            "argv",
            ["tdq_archify.py", "sync-master", "--model", str(empty_model), "--project", str(self.repo_dir)],
        ):
            code = tdq_archify.main()
            self.assertNotEqual(code, 0)
            self.assertFalse(out_dir.exists())

    def test_sync_master_candidate_confinement_relative_to_model_parent(self):
        """Candidate path escaping model parent directory must fail."""
        bad_model = self.models_dir / "bad_confinement.model.json"
        bad_data = dict(self.model_data)
        bad_data["views"] = [
            {"id": "escaped", "type": "architecture", "candidate": "../outside.json", "summary": "Escaped"}
        ]
        bad_model.write_text(json.dumps(bad_data), encoding="utf-8")

        with mock.patch.object(
            sys,
            "argv",
            ["tdq_archify.py", "sync-master", "--model", str(bad_model), "--project", str(self.repo_dir)],
        ):
            code = tdq_archify.main()
            self.assertNotEqual(code, 0)

    def test_sync_master_committed_fails_when_git_dirty(self):
        """When evidence_kind is committed, dirty working tree on sources must fail."""
        (self.repo_dir / "src" / "main.py").write_text("print('dirty')\n", encoding="utf-8")

        with mock.patch.object(
            sys,
            "argv",
            ["tdq_archify.py", "sync-master", "--model", str(self.model_path), "--project", str(self.repo_dir)],
        ):
            code = tdq_archify.main()
            self.assertNotEqual(code, 0)

    def test_sync_master_committed_fails_when_repo_revision_mismatches(self):
        """When evidence_kind is committed, mismatch between revision and repository.revision must fail."""
        bad_model = self.models_dir / "mismatch_rev.model.json"
        bad_data = dict(self.model_data)
        bad_data["repository"] = dict(self.model_data["repository"])
        bad_data["repository"]["revision"] = "0000000000000000000000000000000000000000"
        bad_model.write_text(json.dumps(bad_data), encoding="utf-8")

        with mock.patch.object(
            sys,
            "argv",
            ["tdq_archify.py", "sync-master", "--model", str(bad_model), "--project", str(self.repo_dir)],
        ):
            code = tdq_archify.main()
            self.assertNotEqual(code, 0)

    def test_sync_master_unicode_source_path_and_source_dir_dirty(self):
        """Dirty checking detects modifications on Unicode source paths and directory prefix."""
        unicode_src = self.repo_dir / "src" / "kiến_trúc.py"
        unicode_src.write_text("print('arch')\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=str(self.repo_dir), capture_output=True, timeout=15, check=True)
        subprocess.run(["git", "commit", "-m", "add unicode src"], cwd=str(self.repo_dir), capture_output=True, timeout=15, check=True)
        rev = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(self.repo_dir), capture_output=True, text=True, encoding="utf-8", timeout=15, check=True).stdout.strip()

        model_data = dict(self.model_data)
        model_data["revision"] = rev
        model_data["repository"] = {"url": "https://example.invalid/repo.git", "revision": rev, "link_mode": "local-only"}
        model_data["source_paths"] = ["src"]
        model_file = self.models_dir / "unicode.model.json"
        model_file.write_text(json.dumps(model_data), encoding="utf-8")

        # Dirty modification on Unicode file
        unicode_src.write_text("print('modified arch')\n", encoding="utf-8")

        with mock.patch.object(
            sys,
            "argv",
            ["tdq_archify.py", "sync-master", "--model", str(model_file), "--project", str(self.repo_dir)],
        ):
            code = tdq_archify.main()
            self.assertNotEqual(code, 0, "Dirty Unicode file in source directory 'src' must trigger failure")

    def test_sync_master_model_lacking_source_paths_status_current(self):
        """Model lacking source_paths derives stable sources without staging directory self-stale."""
        out_dir = self.repo_dir / "docs" / "architecture"
        model_data = dict(self.model_data)
        model_data["evidence_kind"] = "working-tree"
        del model_data["source_paths"]
        model_data.pop("revision", None)
        model_data.pop("repository", None)

        model_file = self.models_dir / "no_source_paths.model.json"
        model_file.write_text(json.dumps(model_data), encoding="utf-8")

        with mock.patch("tdq_archify.run_finalize", side_effect=self._mock_run_finalize_builder()):
            with mock.patch.object(
                sys,
                "argv",
                ["tdq_archify.py", "sync-master", "--model", str(model_file), "--project", str(self.repo_dir), "--out", str(out_dir)],
            ):
                code = tdq_archify.main()
                self.assertEqual(code, 0)

        # Status CLI must report current immediately (no self-stale from staging)
        with mock.patch.object(sys, "argv", ["tdq_archify.py", "status", "--project", str(self.repo_dir)]):
            self.assertEqual(tdq_archify.main(), 0)

    def test_sync_master_builds_all_views_index_and_manifest(self):
        """sync-master renders all views, builds index HTML with escaped labels, and rebases manifest."""
        out_dir = self.repo_dir / "docs" / "architecture"

        with mock.patch("tdq_archify.run_finalize", side_effect=self._mock_run_finalize_builder()):
            with mock.patch.object(
                sys,
                "argv",
                [
                    "tdq_archify.py",
                    "sync-master",
                    "--model", str(self.model_path),
                    "--project", str(self.repo_dir),
                    "--out", str(out_dir),
                ],
            ):
                code = tdq_archify.main()
                self.assertEqual(code, 0)

        index_html = out_dir / "index.html"
        manifest_json = out_dir / "manifest.json"
        self.assertTrue(index_html.is_file())
        self.assertTrue(manifest_json.is_file())

        self.assertTrue((out_dir / "overview.html").is_file())
        self.assertTrue((out_dir / "flow.html").is_file())

        content = index_html.read_text(encoding="utf-8")
        self.assertIn("overview.html", content)
        self.assertIn("flow.html", content)
        self.assertIn(html.escape("Master Architecture <Test & Escape>"), content)
        self.assertIn(html.escape("Overview View <Escaped>"), content)
        self.assertNotIn("<Test & Escape>", content)

        manifest_data = json.loads(manifest_json.read_text(encoding="utf-8"))
        self.assertNotIn("tmp", manifest_data["artifact_path"])
        self.assertNotIn("staging", manifest_data["artifact_path"])
        self.assertEqual(manifest_data["artifact_path"], "docs/architecture/index.html")

        self.assertIn("child_files", manifest_data)
        self.assertIn("overview.html", manifest_data["child_files"])
        self.assertIn("flow.html", manifest_data["child_files"])

        res = archify_artifacts.check_manifest(self.repo_dir, manifest_json)
        self.assertEqual(res["status"], "current")

    def test_sync_master_preserves_previous_good_bundle_on_failure(self):
        """Failure during sync-master retains existing good bundle at destination."""
        out_dir = self.repo_dir / "docs" / "architecture"

        with mock.patch("tdq_archify.run_finalize", side_effect=self._mock_run_finalize_builder()):
            with mock.patch.object(
                sys,
                "argv",
                ["tdq_archify.py", "sync-master", "--model", str(self.model_path), "--project", str(self.repo_dir)],
            ):
                self.assertEqual(tdq_archify.main(), 0)

        initial_index_content = (out_dir / "index.html").read_text(encoding="utf-8")

        failing_finalize = mock.Mock(return_value=archify_delivery.FinalizeResult(status=False, receipt={"ok": False, "status": "fail"}))
        with mock.patch("tdq_archify.run_finalize", failing_finalize):
            with mock.patch.object(
                sys,
                "argv",
                ["tdq_archify.py", "sync-master", "--model", str(self.model_path), "--project", str(self.repo_dir)],
            ):
                code = tdq_archify.main()
                self.assertNotEqual(code, 0)

        self.assertTrue((out_dir / "index.html").is_file())
        self.assertEqual((out_dir / "index.html").read_text(encoding="utf-8"), initial_index_content)


class TestStatusAndVerifyCli(unittest.TestCase):
    """Test status and verify CLI sub-commands and child tampering detection."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir, True)
        self.repo_dir = Path(self.temp_dir)
        self.rev = _init_git_repo(self.repo_dir)

        self.models_dir = self.repo_dir / "models"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.cand1 = self.models_dir / "overview.json"
        self.cand1.write_text(json.dumps({"schema_version": 1, "diagram_type": "architecture", "components": []}), encoding="utf-8")
        self.model_path = self.models_dir / "master.model.json"
        self.model_data = {
            "schema_version": 1,
            "title": "Master",
            "evidence_kind": "working-tree",
            "source_paths": ["src/main.py"],
            "coverage": {"modules": []},
            "views": [{"id": "overview", "type": "architecture", "candidate": "overview.json"}],
        }
        self.model_path.write_text(json.dumps(self.model_data), encoding="utf-8")

        def fake_finalize(diagram_type, candidate_path, output_path, **kwargs):
            out_p = Path(output_path)
            out_p.parent.mkdir(parents=True, exist_ok=True)
            out_p.write_text("<html>view content</html>", encoding="utf-8")
            return archify_delivery.FinalizeResult(status=True, receipt={"ok": True, "status": "pass"})

        with mock.patch("tdq_archify.run_finalize", side_effect=fake_finalize):
            with mock.patch.object(
                sys,
                "argv",
                ["tdq_archify.py", "sync-master", "--model", str(self.model_path), "--project", str(self.repo_dir)],
            ):
                self.assertEqual(tdq_archify.main(), 0)

    def test_status_cli_current(self):
        """CLI status reports current and exits 0 when bundle is unmodified."""
        with mock.patch.object(sys, "argv", ["tdq_archify.py", "status", "--project", str(self.repo_dir)]):
            code = tdq_archify.main()
            self.assertEqual(code, 0)

    def test_status_cli_detects_child_tampering(self):
        """Modifying a child file causes status to detect tampering and return non-zero."""
        child_view = self.repo_dir / "docs" / "architecture" / "overview.html"
        child_view.write_text("<html>TAMPERED</html>", encoding="utf-8")

        with mock.patch.object(sys, "argv", ["tdq_archify.py", "status", "--project", str(self.repo_dir)]):
            code = tdq_archify.main()
            self.assertNotEqual(code, 0)

    def test_status_cli_detects_child_missing(self):
        """Deleting a child file causes status to report missing and return non-zero."""
        child_view = self.repo_dir / "docs" / "architecture" / "overview.html"
        child_view.unlink()

        with mock.patch.object(sys, "argv", ["tdq_archify.py", "status", "--project", str(self.repo_dir)]):
            code = tdq_archify.main()
            self.assertNotEqual(code, 0)

    def test_verify_cli_success_and_stale(self):
        """CLI verify checks binding and manifest, exiting non-zero when stale."""
        spec_dir = self.repo_dir / "docs" / "tdq" / "spec"
        spec_dir.mkdir(parents=True, exist_ok=True)
        doc = spec_dir / "SPEC.md"
        doc.write_text("# Spec Content\n", encoding="utf-8")
        out_html = spec_dir / "preview.html"

        fake_res = archify_delivery.FinalizeResult(
            status=True,
            receipt={
                "ok": True,
                "status": "pass",
                "artifact": str(out_html),
                "gates": {"validate": "pass", "deliver": "pass", "check": "pass", "browser-check": "pass"},
            },
        )

        def mock_finalize(diagram_type, candidate_path, output_path, **kwargs):
            Path(output_path).write_text("<html>preview</html>", encoding="utf-8")
            return fake_res

        with mock.patch("tdq_archify.run_finalize", side_effect=mock_finalize):
            with mock.patch.object(
                sys,
                "argv",
                [
                    "tdq_archify.py",
                    "render",
                    "--type", "architecture",
                    "--candidate", str(self.cand1),
                    "--out", str(out_html),
                    "--document", str(doc),
                    "--project", str(self.repo_dir),
                ],
            ):
                code_render = tdq_archify.main()
                self.assertEqual(code_render, 0)

        manifest_path = out_html.with_suffix(".manifest.json")
        self.assertTrue(manifest_path.is_file())

        with mock.patch.object(
            sys,
            "argv",
            ["tdq_archify.py", "verify", "--document", str(doc), "--manifest", str(manifest_path), "--project", str(self.repo_dir)],
        ):
            code = tdq_archify.main()
            self.assertEqual(code, 0)

        doc.write_text("# Corrupted Content\n" + doc.read_text(encoding="utf-8"), encoding="utf-8")
        with mock.patch.object(
            sys,
            "argv",
            ["tdq_archify.py", "verify", "--document", str(doc), "--manifest", str(manifest_path), "--project", str(self.repo_dir)],
        ):
            code = tdq_archify.main()
            self.assertNotEqual(code, 0)


class TestLocalArchifyRealEngineSmoke(unittest.TestCase):
    """Smoke test against real local Archify installation at ~/Documents/archify if available."""

    def test_local_archify_explainer_smoke(self):
        """If real Archify is installed, run explainer finalize smoke without mocking."""
        env = archify_delivery.check_environment()
        if not env.get("ready"):
            self.skipTest(f"Real Archify not ready: {env.get('error')}")

        temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, temp_dir, True)
        cand_path = Path(temp_dir) / "explainer.candidate.json"
        out_html = Path(temp_dir) / "explainer.html"

        candidate_ir = {
            "schema_version": 1,
            "diagram_type": "explainer",
            "meta": {
                "id": "explainer_smoke",
                "title": "Explainer Smoke",
            },
            "answer": {
                "summary": "This is a smoke test explainer summary.",
            },
            "panels": [
                {
                    "id": "panel_1",
                    "title": "Panel 1",
                    "blocks": [
                        {
                            "id": "block_1",
                            "type": "prose",
                            "text": "Detailed text content for block 1.",
                        }
                    ],
                }
            ],
            "sources": [],
        }
        cand_path.write_text(json.dumps(candidate_ir), encoding="utf-8")

        result = archify_delivery.run_finalize(
            diagram_type="explainer",
            candidate_path=cand_path,
            output_path=out_html,
            quality="showcase",
            timeout=120,
        )

        self.assertTrue(result.status, f"Explainer smoke failed: {result.receipt}")
        self.assertTrue(out_html.is_file(), f"Output HTML not generated: {out_html}")
        receipt = result.receipt
        self.assertEqual(receipt.get("status"), "pass")
        self.assertEqual(receipt.get("gates", {}).get("validate"), "pass")
        self.assertEqual(receipt.get("gates", {}).get("deliver"), "pass")
        self.assertEqual(receipt.get("gates", {}).get("check"), "pass")

    def test_real_bound_explainer_render_then_verify_current(self):
        """Real Archify engine explainer render with document binding then verify immediately current."""
        env = archify_delivery.check_environment()
        if not env.get("ready"):
            self.skipTest(f"Real Archify not ready: {env.get('error')}")

        temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, temp_dir, True)
        project_root = Path(temp_dir)
        _init_git_repo(project_root)

        spec_dir = project_root / "docs" / "tdq" / "spec"
        spec_dir.mkdir(parents=True, exist_ok=True)
        doc_path = spec_dir / "sample.spec.md"
        doc_path.write_text("# Sample Spec\n\nExplainer preview specification.\n", encoding="utf-8")

        cand_path = spec_dir / "sample.explainer.candidate.json"
        candidate_ir = {
            "schema_version": 1,
            "diagram_type": "explainer",
            "meta": {
                "id": "explainer_bound",
                "title": "Explainer Bound Preview",
            },
            "answer": {
                "summary": "Bound explainer preview for project architecture.",
            },
            "panels": [
                {
                    "id": "panel_bound",
                    "title": "Overview Panel",
                    "blocks": [
                        {
                            "id": "block_bound",
                            "type": "prose",
                            "text": "Detailed explanation of architecture components.",
                        }
                    ],
                }
            ],
            "sources": [],
        }
        cand_path.write_text(json.dumps(candidate_ir), encoding="utf-8")
        out_html = spec_dir / "sample-preview.html"

        # 1. Render real explainer diagram with document binding
        with mock.patch.object(
            sys,
            "argv",
            [
                "tdq_archify.py",
                "render",
                "--type", "explainer",
                "--candidate", str(cand_path),
                "--out", str(out_html),
                "--document", str(doc_path),
                "--project", str(project_root),
            ],
        ):
            code_render = tdq_archify.main()
            self.assertEqual(code_render, 0)

        self.assertTrue(out_html.is_file())
        manifest_path = out_html.with_suffix(".manifest.json")
        self.assertTrue(manifest_path.is_file())

        # 2. Verify document and manifest immediately current
        with mock.patch.object(
            sys,
            "argv",
            [
                "tdq_archify.py",
                "verify",
                "--document", str(doc_path),
                "--manifest", str(manifest_path),
                "--project", str(project_root),
            ],
        ):
            code_verify = tdq_archify.main()
            self.assertEqual(code_verify, 0, "Real bound explainer must verify as current immediately")


if __name__ == "__main__":
    unittest.main()
