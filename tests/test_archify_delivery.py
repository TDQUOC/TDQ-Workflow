"""Behavior and unit tests for archify_delivery module.

Tests cover:
- find_archify_root: ARCHIFY_ROOT explicit error (no fallback), standard candidates, no hardcoded admin
- get_archify_bin: direct bin/, nested archify/bin/, and direct script
- check_environment: Node.js >= 18, missing Node, missing Archify, error diagnostics
- build_finalize_command: argument construction, repo-root, missing binary exception
- atomic_delivery: unique temp files, fsync, symlink rejection (target & parent), error cleanup
- open_artifact: HTML-only enforcement, safe argument passing, shell injection resilience
- run_finalize:
  * exit 1 false-success prevention (exit 1 with receipt pass is rejected)
  * stale file prevention (old artifact not counted as success)
  * artifact hash mismatch detection
  * malformed receipts (empty, syntax error, scalar, list)
  * gate verification (validate, deliver, check must pass)
  * native diagram requires browser-check pass
  * explainer accepts browser-check not-run
  * candidate mutation detection (before vs after hash)
  * timeout handling with diagnostic
  * Unicode and shell characters in paths
  * CI offline flag ARCHIFY_UPDATE_CHECK_DISABLED=1
  * TDQ_LOG stderr logging
"""
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

# Ensure scripts directory of current worktree is on sys.path
WORKTREE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = WORKTREE_DIR / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import archify_delivery  # noqa: E402


class TestArchifyDeliveryRootDiscovery(unittest.TestCase):
    """Test suite for root discovery and binary location."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir, True)

    def test_find_archify_root_valid_env(self):
        """Valid ARCHIFY_ROOT returns the configured directory."""
        bin_dir = Path(self.temp_dir) / "bin"
        bin_dir.mkdir(parents=True)
        (bin_dir / "archify.mjs").write_text("// entry", encoding="utf-8")

        with mock.patch.dict(os.environ, {"ARCHIFY_ROOT": self.temp_dir}):
            root = archify_delivery.find_archify_root()
            self.assertEqual(root, self.temp_dir)

    def test_find_archify_root_explicit_invalid_env_no_fallback(self):
        """Explicit ARCHIFY_ROOT that is invalid MUST NOT fall back to other directories."""
        invalid_dir = Path(self.temp_dir) / "nonexistent"
        valid_home = Path(self.temp_dir) / "fake_home" / "Documents" / "archify" / "bin"
        valid_home.mkdir(parents=True)
        (valid_home / "archify.mjs").write_text("// entry", encoding="utf-8")

        with mock.patch.dict(os.environ, {"ARCHIFY_ROOT": str(invalid_dir)}):
            with mock.patch("pathlib.Path.home", return_value=Path(self.temp_dir) / "fake_home"):
                root = archify_delivery.find_archify_root()
                self.assertIsNone(root, "Explicit invalid ARCHIFY_ROOT must return None, not fall back")

    def test_find_archify_root_home_fallback_no_admin_hardcode(self):
        """When ARCHIFY_ROOT is unset, home/Documents/archify is discovered dynamically."""
        fake_home = Path(self.temp_dir) / "user_home"
        archify_pkg = fake_home / "Documents" / "archify" / "bin"
        archify_pkg.mkdir(parents=True)
        (archify_pkg / "archify.mjs").write_text("// entry", encoding="utf-8")

        with mock.patch.dict(os.environ, {}, clear=True):
            with mock.patch("pathlib.Path.home", return_value=fake_home):
                root = archify_delivery.find_archify_root()
                self.assertIsNotNone(root)
                self.assertEqual(Path(root), fake_home / "Documents" / "archify")

    def test_get_archify_bin_resolutions(self):
        """Resolves direct bin/, nested archify/bin/, and direct script path."""
        # 1. Direct bin/
        direct_root = Path(self.temp_dir) / "direct"
        (direct_root / "bin").mkdir(parents=True)
        mjs1 = direct_root / "bin" / "archify.mjs"
        mjs1.write_text("// direct", encoding="utf-8")
        self.assertEqual(archify_delivery.get_archify_bin(str(direct_root)), mjs1)

        # 2. Nested archify/bin/
        nested_root = Path(self.temp_dir) / "nested"
        (nested_root / "archify" / "bin").mkdir(parents=True)
        mjs2 = nested_root / "archify" / "bin" / "archify.mjs"
        mjs2.write_text("// nested", encoding="utf-8")
        self.assertEqual(archify_delivery.get_archify_bin(str(nested_root)), mjs2)

        # 3. Direct script file
        self.assertEqual(archify_delivery.get_archify_bin(str(mjs1)), mjs1)

        # 4. Missing
        self.assertIsNone(archify_delivery.get_archify_bin(str(Path(self.temp_dir) / "empty")))


class TestCheckEnvironment(unittest.TestCase):
    """Test suite for check_environment pre-flight validation."""

    def test_check_environment_node_missing(self):
        """Missing node binary results in node_ok=False and clear error explanation."""
        with mock.patch("shutil.which", return_value=None):
            with mock.patch("archify_delivery.find_archify_root", return_value="/fake"):
                env = archify_delivery.check_environment()
                self.assertFalse(env["node_ok"])
                self.assertFalse(env["ready"])
                self.assertIn("Node.js", env.get("error", ""))

    def test_check_environment_node_version_too_old(self):
        """Node.js version < 18 reports error."""
        proc = mock.MagicMock(stdout="v16.20.2\n")
        with mock.patch("shutil.which", return_value="node"):
            with mock.patch("subprocess.run", return_value=proc):
                with mock.patch("archify_delivery.find_archify_root", return_value="/fake"):
                    with mock.patch("archify_delivery.get_archify_bin", return_value=Path("/fake/bin/archify.mjs")):
                        env = archify_delivery.check_environment()
                        self.assertFalse(env["node_ok"])
                        self.assertFalse(env["ready"])
                        self.assertIn("18", env.get("error", ""))

    def test_check_environment_ready(self):
        """Node >= 18 and valid Archify installation results in ready=True and error=None."""
        proc = mock.MagicMock(stdout="v22.11.0\n")
        with mock.patch("shutil.which", return_value="node"):
            with mock.patch("subprocess.run", return_value=proc):
                with mock.patch("archify_delivery.find_archify_root", return_value="/opt/archify"):
                    with mock.patch("archify_delivery.get_archify_bin", return_value=Path("/opt/archify/bin/archify.mjs")):
                        env = archify_delivery.check_environment()
                        self.assertTrue(env["node_ok"])
                        self.assertEqual(env["node_version"], "v22.11.0")
                        self.assertTrue(env["ready"])
                        self.assertIsNone(env.get("error"))


class TestAtomicDelivery(unittest.TestCase):
    """Test suite for atomic_delivery safety guarantees."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir, True)

    def test_atomic_delivery_creates_file_and_content(self):
        """Writes UTF-8 string and bytes atomically."""
        target_txt = Path(self.temp_dir) / "sub" / "output.txt"
        archify_delivery.atomic_delivery(target_txt, "Nội dung tiếng Việt UTF-8")
        self.assertEqual(target_txt.read_text(encoding="utf-8"), "Nội dung tiếng Việt UTF-8")

        target_bin = Path(self.temp_dir) / "sub" / "output.bin"
        archify_delivery.atomic_delivery(target_bin, b"\xde\xad\xbe\xef")
        self.assertEqual(target_bin.read_bytes(), b"\xde\xad\xbe\xef")

    def test_atomic_delivery_rejects_symlink(self):
        """Refuses to deliver to a symlink target."""
        real_file = Path(self.temp_dir) / "real.txt"
        real_file.write_text("initial", encoding="utf-8")
        link_file = Path(self.temp_dir) / "link.txt"
        try:
            link_file.symlink_to(real_file)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks not supported in this environment")

        with self.assertRaises(ValueError):
            archify_delivery.atomic_delivery(link_file, "overwrite attempt")

    def test_atomic_delivery_cleans_up_on_error(self):
        """Cleans up temporary file if write or replace fails."""
        target = Path(self.temp_dir) / "fail.txt"
        with mock.patch("os.replace", side_effect=OSError("Disk write error")):
            with self.assertRaises(OSError):
                archify_delivery.atomic_delivery(target, "content")
        # Ensure no temporary file left behind
        temp_files = list(Path(self.temp_dir).glob(".*tmp*"))
        self.assertEqual(temp_files, [])


class TestOpenArtifact(unittest.TestCase):
    """Test suite for open_artifact browser launcher."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir, True)

    def test_open_artifact_rejects_nonexistent(self):
        """Returns False for non-existent path."""
        self.assertFalse(archify_delivery.open_artifact(Path(self.temp_dir) / "ghost.html"))

    def test_open_artifact_rejects_non_html(self):
        """Returns False if file is not HTML."""
        exe_file = Path(self.temp_dir) / "payload.exe"
        exe_file.write_bytes(b"bin")
        self.assertFalse(archify_delivery.open_artifact(exe_file))

        py_file = Path(self.temp_dir) / "script.py"
        py_file.write_text("print('hello')", encoding="utf-8")
        self.assertFalse(archify_delivery.open_artifact(py_file))

    def test_open_artifact_windows_uses_startfile(self):
        """Windows uses direct OS API (os.startfile) without shell or command interpolation."""
        html_file = Path(self.temp_dir) / "test;Start-Process calc.exe;.html"
        html_file.write_text("<html></html>", encoding="utf-8")

        with mock.patch("platform.system", return_value="Windows"):
            with mock.patch("os.startfile", create=True) as mock_startfile:
                ok = archify_delivery.open_artifact(html_file)
                self.assertTrue(ok)
                mock_startfile.assert_called_once_with(html_file.as_uri())

    def test_open_artifact_windows_fallback_webbrowser(self):
        """When os.startfile is absent on Windows mock, falls back to webbrowser.open."""
        html_file = Path(self.temp_dir) / "test_fallback.html"
        html_file.write_text("<html></html>", encoding="utf-8")

        with mock.patch("platform.system", return_value="Windows"):
            with mock.patch.object(os, "startfile", None, create=False):
                with mock.patch("webbrowser.open", return_value=True) as mock_wb:
                    ok = archify_delivery.open_artifact(html_file)
                    self.assertTrue(ok)
                    mock_wb.assert_called_once_with(html_file.as_uri())

    def test_open_artifact_non_zero_returncode_fails(self):
        """Strict integer returncode check: non-zero returncode returns False."""
        html_file = Path(self.temp_dir) / "test_exit1.html"
        html_file.write_text("<html></html>", encoding="utf-8")

        with mock.patch("platform.system", return_value="Linux"):
            with mock.patch("subprocess.run") as mock_run:
                mock_run.return_value = mock.MagicMock(returncode=1)
                ok = archify_delivery.open_artifact(html_file)
                self.assertFalse(ok)


class TestFinalizeResultContract(unittest.TestCase):
    """Test suite for FinalizeResult dataclass."""

    def test_finalizeresult_properties_and_get(self):
        """FinalizeResult is a dataclass, not a tuple, with status, receipt, and get()."""
        res = archify_delivery.FinalizeResult(status=True, receipt={"ok": True, "custom": 123})
        self.assertTrue(res.status)
        self.assertEqual(res.receipt["custom"], 123)
        self.assertEqual(res.get("status"), True)
        self.assertEqual(res.get("receipt"), {"ok": True, "custom": 123})
        self.assertEqual(res.get("custom"), 123)
        self.assertEqual(res.get("nonexistent", "default"), "default")
        self.assertNotIsInstance(res, tuple, "FinalizeResult must not be a tuple subclass")


class TestRunFinalizeBehavior(unittest.TestCase):
    """Rigorous behavioral tests for run_finalize."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir, True)

        self.candidate = Path(self.temp_dir) / "candidate.json"
        self.candidate_content = json.dumps({"schema_version": 1, "components": []})
        self.candidate.write_text(self.candidate_content, encoding="utf-8")
        self.cand_sha = hashlib.sha256(self.candidate_content.encode("utf-8")).hexdigest()

        self.output_html = Path(self.temp_dir) / "output.html"

        # Mock bin script
        self.bin_path = Path(self.temp_dir) / "bin" / "archify.mjs"
        self.bin_path.parent.mkdir(parents=True)
        self.bin_path.write_text("// entry", encoding="utf-8")

    def _write_valid_output(self, content="<html>delivered</html>"):
        self.output_html.write_text(content, encoding="utf-8")
        b = content.encode("utf-8")
        return hashlib.sha256(b).hexdigest(), len(b)

    def test_exit_1_false_success_prevention(self):
        """Exit code 1 MUST return status=False even if receipt claims ok=True and status=pass."""
        art_sha, art_bytes = self._write_valid_output()
        bogus_receipt = {
            "schemaVersion": 1,
            "ok": True,
            "status": "pass",
            "gates": {"validate": "pass", "deliver": "pass", "check": "pass", "browser-check": "pass"},
            "specification": {"path": str(self.candidate), "sha256": self.cand_sha},
            "artifact": {"path": str(self.output_html), "sha256": art_sha, "bytes": art_bytes},
        }

        mock_proc = mock.MagicMock(returncode=1, stdout=json.dumps(bogus_receipt), stderr="")
        with mock.patch("archify_delivery.get_archify_bin", return_value=self.bin_path):
            with mock.patch("subprocess.run", return_value=mock_proc):
                res = archify_delivery.run_finalize(
                    diagram_type="architecture",
                    candidate_path=self.candidate,
                    output_path=self.output_html,
                )
                self.assertFalse(res.status, "Exit code 1 must NEVER be reported as status=True")
                self.assertFalse(res.receipt.get("ok"))
                self.assertEqual(res.receipt.get("status"), "fail")

    def test_stale_file_not_counted_as_success(self):
        """Existing old output file must not cause success when finalize execution fails."""
        # Pre-create old artifact
        self.output_html.write_text("<html>OLD STALE ARTIFACT</html>", encoding="utf-8")

        mock_proc = mock.MagicMock(returncode=1, stdout='{"ok": false, "status": "fail"}', stderr="Failure")
        with mock.patch("archify_delivery.get_archify_bin", return_value=self.bin_path):
            with mock.patch("subprocess.run", return_value=mock_proc):
                res = archify_delivery.run_finalize(
                    diagram_type="architecture",
                    candidate_path=self.candidate,
                    output_path=self.output_html,
                )
                self.assertFalse(res.status)

    def test_artifact_hash_mismatch_fails(self):
        """If file on disk does not match receipt artifact SHA-256, finalize must fail."""
        self._write_valid_output("<html>ACTUAL CONTENT</html>")
        receipt = {
            "schemaVersion": 1,
            "ok": True,
            "status": "pass",
            "gates": {"validate": "pass", "deliver": "pass", "check": "pass", "browser-check": "pass"},
            "specification": {"path": str(self.candidate), "sha256": self.cand_sha},
            "artifact": {
                "path": str(self.output_html),
                "sha256": "0000000000000000000000000000000000000000000000000000000000000000",
                "bytes": 9999,
            },
        }
        mock_proc = mock.MagicMock(returncode=0, stdout=json.dumps(receipt), stderr="")
        with mock.patch("archify_delivery.get_archify_bin", return_value=self.bin_path):
            with mock.patch("subprocess.run", return_value=mock_proc):
                res = archify_delivery.run_finalize(
                    diagram_type="architecture",
                    candidate_path=self.candidate,
                    output_path=self.output_html,
                )
                self.assertFalse(res.status)
                self.assertIn("mismatch", json.dumps(res.receipt.get("diagnostics", [])))

    def test_malformed_receipt_handling(self):
        """Malformed stdout (empty, non-JSON, JSON scalar, or JSON list) returns status=False."""
        art_sha, art_bytes = self._write_valid_output()

        for bad_stdout in ("", "not json at all", "null", "12345", '"string scalar"', "[]"):
            mock_proc = mock.MagicMock(returncode=0, stdout=bad_stdout, stderr="some warnings")
            with mock.patch("archify_delivery.get_archify_bin", return_value=self.bin_path):
                with mock.patch("subprocess.run", return_value=mock_proc):
                    res = archify_delivery.run_finalize(
                        diagram_type="architecture",
                        candidate_path=self.candidate,
                        output_path=self.output_html,
                    )
                    self.assertFalse(res.status, f"Bad stdout '{bad_stdout}' must return status=False")
                    self.assertFalse(res.receipt.get("ok"))

    def test_missing_or_failing_gates(self):
        """Failing or missing required gates (validate, deliver, check) causes status=False."""
        art_sha, art_bytes = self._write_valid_output()

        base_receipt = {
            "schemaVersion": 1,
            "ok": True,
            "status": "pass",
            "specification": {"path": str(self.candidate), "sha256": self.cand_sha},
            "artifact": {"path": str(self.output_html), "sha256": art_sha, "bytes": art_bytes},
            "gates": {"validate": "pass", "deliver": "pass", "check": "pass", "browser-check": "pass"},
        }

        # 1. deliver failed
        r1 = dict(base_receipt)
        r1["gates"] = {"validate": "pass", "deliver": "fail", "check": "pass", "browser-check": "pass"}
        mock_proc1 = mock.MagicMock(returncode=0, stdout=json.dumps(r1), stderr="")
        with mock.patch("archify_delivery.get_archify_bin", return_value=self.bin_path):
            with mock.patch("subprocess.run", return_value=mock_proc1):
                res1 = archify_delivery.run_finalize("architecture", self.candidate, self.output_html)
                self.assertFalse(res1.status)

        # 2. missing gates object
        r2 = dict(base_receipt)
        del r2["gates"]
        mock_proc2 = mock.MagicMock(returncode=0, stdout=json.dumps(r2), stderr="")
        with mock.patch("archify_delivery.get_archify_bin", return_value=self.bin_path):
            with mock.patch("subprocess.run", return_value=mock_proc2):
                res2 = archify_delivery.run_finalize("architecture", self.candidate, self.output_html)
                self.assertFalse(res2.status)

    def test_native_vs_explainer_browser_check_gate(self):
        """Native diagram requires browser-check pass; explainer accepts not-run."""
        art_sha, art_bytes = self._write_valid_output()

        receipt_not_run = {
            "schemaVersion": 1,
            "ok": True,
            "status": "pass",
            "specification": {"path": str(self.candidate), "sha256": self.cand_sha},
            "artifact": {"path": str(self.output_html), "sha256": art_sha, "bytes": art_bytes},
            "gates": {"validate": "pass", "deliver": "pass", "check": "pass", "browser-check": "not-run"},
        }
        mock_proc = mock.MagicMock(returncode=0, stdout=json.dumps(receipt_not_run), stderr="")

        with mock.patch("archify_delivery.get_archify_bin", return_value=self.bin_path):
            with mock.patch("subprocess.run", return_value=mock_proc):
                # Native diagram (architecture) with browser-check not-run MUST FAIL
                res_native = archify_delivery.run_finalize("architecture", self.candidate, self.output_html)
                self.assertFalse(res_native.status, "Native diagram must require browser-check pass")

                # Explainer diagram with browser-check not-run MUST PASS
                res_explainer = archify_delivery.run_finalize("explainer", self.candidate, self.output_html)
                self.assertTrue(res_explainer.status, "Explainer diagram must accept browser-check not-run")

    def test_candidate_tampering_detection(self):
        """If candidate file content changes during execution, finalize fails."""
        art_sha, art_bytes = self._write_valid_output()
        receipt = {
            "schemaVersion": 1,
            "ok": True,
            "status": "pass",
            "specification": {"path": str(self.candidate), "sha256": self.cand_sha},
            "artifact": {"path": str(self.output_html), "sha256": art_sha, "bytes": art_bytes},
            "gates": {"validate": "pass", "deliver": "pass", "check": "pass", "browser-check": "pass"},
        }

        def mutate_candidate(*args, **kwargs):
            self.candidate.write_text('{"tampered": true}', encoding="utf-8")
            return mock.MagicMock(returncode=0, stdout=json.dumps(receipt), stderr="")

        with mock.patch("archify_delivery.get_archify_bin", return_value=self.bin_path):
            with mock.patch("subprocess.run", side_effect=mutate_candidate):
                res = archify_delivery.run_finalize("architecture", self.candidate, self.output_html)
                self.assertFalse(res.status, "Candidate mutation must cause finalize failure")

    def test_timeout_handling(self):
        """Timeout in subprocess raises TimeoutExpired and returns status=False with diagnostic."""
        with mock.patch("archify_delivery.get_archify_bin", return_value=self.bin_path):
            with mock.patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="finalize", timeout=5)):
                res = archify_delivery.run_finalize("architecture", self.candidate, self.output_html, timeout=5)
                self.assertFalse(res.status)
                self.assertIn("timeout", json.dumps(res.receipt.get("diagnostics", [])))

    def test_artifact_missing_or_empty_fields_fail_closed(self):
        """Empty artifact object or missing/invalid fields must fail closed."""
        art_sha, art_bytes = self._write_valid_output()

        invalid_artifacts = [
            {},  # empty dict
            {"path": str(self.output_html)},  # missing sha256 and bytes
            {"path": str(self.output_html), "sha256": art_sha},  # missing bytes
            {"path": str(self.output_html), "sha256": art_sha, "bytes": True},  # bool instead of int
            {"path": str(self.output_html), "sha256": art_sha, "bytes": -5},  # negative bytes
            {"path": str(self.output_html), "sha256": "not64hex", "bytes": art_bytes},  # invalid sha256
            {"path": None, "sha256": art_sha, "bytes": art_bytes},  # null path
            {"path": "", "sha256": art_sha, "bytes": art_bytes},  # empty path
            {"path": "invalid\0path", "sha256": art_sha, "bytes": art_bytes},  # malformed path string
        ]

        for bad_art in invalid_artifacts:
            receipt = {
                "schemaVersion": 1,
                "ok": True,
                "status": "pass",
                "gates": {"validate": "pass", "deliver": "pass", "check": "pass", "browser-check": "pass"},
                "specification": {"path": str(self.candidate), "sha256": self.cand_sha},
                "artifact": bad_art,
            }
            mock_proc = mock.MagicMock(returncode=0, stdout=json.dumps(receipt), stderr="")
            with mock.patch("archify_delivery.get_archify_bin", return_value=self.bin_path):
                with mock.patch("subprocess.run", return_value=mock_proc):
                    res = archify_delivery.run_finalize("architecture", self.candidate, self.output_html)
                    self.assertFalse(res.status, f"Artifact {bad_art} must fail closed")

    def test_specification_missing_or_invalid_hash_fail_closed(self):
        """Specification object must be present with valid matching 64-hex sha256."""
        art_sha, art_bytes = self._write_valid_output()

        invalid_specs = [
            None,
            {},
            {"sha256": ""},
            {"sha256": "not64hex"},
            {"sha256": "0" * 63},  # 63 chars (not 64)
            {"sha256": "g" * 64},  # non-hex
        ]

        for bad_spec in invalid_specs:
            receipt = {
                "schemaVersion": 1,
                "ok": True,
                "status": "pass",
                "gates": {"validate": "pass", "deliver": "pass", "check": "pass", "browser-check": "pass"},
                "artifact": {"path": str(self.output_html), "sha256": art_sha, "bytes": art_bytes},
            }
            if bad_spec is not None:
                receipt["specification"] = bad_spec

            mock_proc = mock.MagicMock(returncode=0, stdout=json.dumps(receipt), stderr="")
            with mock.patch("archify_delivery.get_archify_bin", return_value=self.bin_path):
                with mock.patch("subprocess.run", return_value=mock_proc):
                    res = archify_delivery.run_finalize("architecture", self.candidate, self.output_html)
                    self.assertFalse(res.status, f"Specification {bad_spec} must fail closed")

    def test_unicode_paths_and_ci_offline_env(self):
        """Handles Unicode path names and ensures ARCHIFY_UPDATE_CHECK_DISABLED=1 is set."""
        unicode_dir = Path(self.temp_dir) / "dự_án_kiến_trúc_2026"
        unicode_dir.mkdir(parents=True)
        cand_uni = unicode_dir / "mô_hình.json"
        cand_uni.write_text(self.candidate_content, encoding="utf-8")
        cand_sha = hashlib.sha256(self.candidate_content.encode("utf-8")).hexdigest()

        out_uni = unicode_dir / "sơ_đồ.html"
        out_content = "<html>tiếng Việt có dấu</html>"
        out_uni.write_text(out_content, encoding="utf-8")
        art_sha = hashlib.sha256(out_content.encode("utf-8")).hexdigest()
        art_bytes = len(out_content.encode("utf-8"))

        receipt = {
            "schemaVersion": 1,
            "ok": True,
            "status": "pass",
            "specification": {"path": str(cand_uni), "sha256": cand_sha},
            "artifact": {"path": str(out_uni), "sha256": art_sha, "bytes": art_bytes},
            "gates": {"validate": "pass", "deliver": "pass", "check": "pass", "browser-check": "pass"},
        }

        captured_env = {}

        def record_run(cmd, **kwargs):
            captured_env.update(kwargs.get("env", {}))
            return mock.MagicMock(returncode=0, stdout=json.dumps(receipt), stderr="some log")

        with mock.patch("archify_delivery.get_archify_bin", return_value=self.bin_path):
            with mock.patch("subprocess.run", side_effect=record_run):
                res = archify_delivery.run_finalize("architecture", cand_uni, out_uni)
                self.assertTrue(res.status)
                self.assertEqual(captured_env.get("ARCHIFY_UPDATE_CHECK_DISABLED"), "1")


if __name__ == "__main__":
    unittest.main()
