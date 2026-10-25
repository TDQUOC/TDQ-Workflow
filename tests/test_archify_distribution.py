# tests/test_archify_distribution.py
"""Tests for Archify distribution, setup, portability, agent-first configuration,
and runtime packaging closure.

Requirements covered:
- Setup/root portability from alternate directory with explicit ARCHIFY_ROOT.
- Strict rejection without fallback when explicit ARCHIFY_ROOT is invalid.
- Direct (bin/archify.mjs) vs nested (archify/bin/archify.mjs) package root layouts.
- Portability with spaces and unicode diacritics in path.
- Absence matrix: missing Node.js, Node.js < 18, missing Archify engine without crashing.
- No hard-coded admin paths in discovery or setup.
- Agent-first architecture: no active endpoint AI client or scanner network calls.
- Offline execution: ARCHIFY_UPDATE_CHECK_DISABLED=1.
- Diagram type browser gate policy: explainer accepts not-run; native requires pass.
- Runtime packaging closure: all Archify modules and their transitive dependencies
  are retained on release branches.
"""

import hashlib
import inspect
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

# Ensure scripts directory is on sys.path
ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import archify_delivery
import build_portable
import tdq_setup


class TestArchifyDiscoveryAndPortability(unittest.TestCase):
    """Tests for engine root discovery and path portability."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp_dir = Path(self._tmp.name)
        self._orig_env = os.environ.get("ARCHIFY_ROOT")

    def tearDown(self):
        if self._orig_env is not None:
            os.environ["ARCHIFY_ROOT"] = self._orig_env
        else:
            os.environ.pop("ARCHIFY_ROOT", None)
        self._tmp.cleanup()

    def test_explicit_archify_root_alternate_directory(self):
        """Explicit ARCHIFY_ROOT in alternate directory outside repo is discovered correctly."""
        alt_root = self.tmp_dir / "alternate_tools" / "archify_engine"
        bin_dir = alt_root / "bin"
        bin_dir.mkdir(parents=True)
        archify_mjs = bin_dir / "archify.mjs"
        archify_mjs.write_text("// dummy archify engine\n", encoding="utf-8")

        os.environ["ARCHIFY_ROOT"] = str(alt_root)
        discovered_root = archify_delivery.find_archify_root()
        self.assertEqual(discovered_root, str(alt_root))

        bin_path = archify_delivery.get_archify_bin(discovered_root)
        self.assertIsNotNone(bin_path)
        self.assertEqual(bin_path, archify_mjs)

    def test_invalid_archify_root_no_fallback(self):
        """When ARCHIFY_ROOT is explicitly set but invalid, return None immediately without fallback."""
        invalid_path = str(self.tmp_dir / "nonexistent" / "fake_archify")
        os.environ["ARCHIFY_ROOT"] = invalid_path

        discovered = archify_delivery.find_archify_root()
        self.assertIsNone(discovered, "Explicit invalid ARCHIFY_ROOT must return None without fallback")

        env_status = archify_delivery.check_environment()
        self.assertFalse(env_status["ready"])
        self.assertIn("not a valid Archify root", env_status.get("error", ""))

    def test_package_root_direct_layout(self):
        """Direct layout: root/bin/archify.mjs."""
        direct_root = self.tmp_dir / "archify_direct"
        (direct_root / "bin").mkdir(parents=True)
        bin_file = direct_root / "bin" / "archify.mjs"
        bin_file.write_text("// direct layout\n", encoding="utf-8")

        os.environ["ARCHIFY_ROOT"] = str(direct_root)
        discovered = archify_delivery.find_archify_root()
        self.assertEqual(discovered, str(direct_root))
        self.assertEqual(archify_delivery.get_archify_bin(discovered), bin_file)

    def test_package_root_nested_layout(self):
        """Nested layout: root/archify/bin/archify.mjs."""
        nested_root = self.tmp_dir / "archify_nested_repo"
        (nested_root / "archify" / "bin").mkdir(parents=True)
        bin_file = nested_root / "archify" / "bin" / "archify.mjs"
        bin_file.write_text("// nested layout\n", encoding="utf-8")

        os.environ["ARCHIFY_ROOT"] = str(nested_root)
        discovered = archify_delivery.find_archify_root()
        self.assertEqual(discovered, str(nested_root))
        self.assertEqual(archify_delivery.get_archify_bin(discovered), bin_file)

    def test_path_with_spaces_and_diacritics(self):
        """Paths with spaces and Vietnamese diacritics must work without encoding errors."""
        unicode_root = self.tmp_dir / "thư mục có khoảng trắng và dấu tiếng Việt" / "archify"
        (unicode_root / "bin").mkdir(parents=True)
        bin_file = unicode_root / "bin" / "archify.mjs"
        bin_file.write_text("// unicode path\n", encoding="utf-8")

        os.environ["ARCHIFY_ROOT"] = str(unicode_root)
        discovered = archify_delivery.find_archify_root()
        self.assertEqual(discovered, str(unicode_root))
        self.assertEqual(archify_delivery.get_archify_bin(discovered), bin_file)

    def test_no_hardcoded_admin_in_delivery_and_setup(self):
        """Verify that neither archify_delivery nor tdq_setup contains hard-coded user 'admin'."""
        delivery_src = inspect.getsource(archify_delivery)
        self.assertNotIn("Users\\admin", delivery_src)
        self.assertNotIn("Users/admin", delivery_src)

        setup_src = inspect.getsource(tdq_setup.kiem_tra_archify)
        self.assertNotIn("Users\\admin", setup_src)
        self.assertNotIn("Users/admin", setup_src)


class TestAbsenceAndVersions(unittest.TestCase):
    """Tests handling of absent dependencies and incompatible versions without network calls."""

    def setUp(self):
        self._orig_env = os.environ.get("ARCHIFY_ROOT")
        os.environ.pop("ARCHIFY_ROOT", None)

    def tearDown(self):
        if self._orig_env is not None:
            os.environ["ARCHIFY_ROOT"] = self._orig_env
        else:
            os.environ.pop("ARCHIFY_ROOT", None)

    def test_node_missing_absence(self):
        """When Node.js is missing from PATH, reports not ready with clear error, no network attempt."""
        with mock.patch("shutil.which", return_value=None):
            env_status = archify_delivery.check_environment()
            self.assertFalse(env_status["node_ok"])
            self.assertFalse(env_status["ready"])
            self.assertIn("Node.js executable not found in PATH", env_status.get("error", ""))

            ok, detail = tdq_setup.kiem_tra_archify()
            self.assertFalse(ok)
            self.assertIn("Node.js", detail)

    def test_node_version_too_old(self):
        """When Node.js is < 18, reports version incompatibility."""
        fake_proc = mock.Mock()
        fake_proc.stdout = "v16.19.1\n"
        with mock.patch("shutil.which", return_value="/usr/local/bin/node"):
            with mock.patch("subprocess.run", return_value=fake_proc):
                env_status = archify_delivery.check_environment()
                self.assertFalse(env_status["node_ok"])
                self.assertFalse(env_status["ready"])
                self.assertIn("< 18", env_status.get("error", ""))

                ok, detail = tdq_setup.kiem_tra_archify()
                self.assertFalse(ok)
                self.assertIn("18", detail)

    def test_node_version_18_and_above(self):
        """When Node.js is >= 18, node_ok is True."""
        for ver in ("v18.0.0", "v20.10.0", "v22.5.0"):
            fake_proc = mock.Mock()
            fake_proc.stdout = f"{ver}\n"
            with mock.patch("shutil.which", return_value="/usr/bin/node"):
                with mock.patch("subprocess.run", return_value=fake_proc):
                    with mock.patch.object(archify_delivery, "find_archify_root", return_value="/opt/archify"):
                        with mock.patch.object(archify_delivery, "get_archify_bin", return_value=Path("/opt/archify/bin/archify.mjs")):
                            env_status = archify_delivery.check_environment()
                            self.assertTrue(env_status["node_ok"])
                            self.assertEqual(env_status["node_version"], ver)
                            self.assertTrue(env_status["ready"])

    def test_archify_engine_absent(self):
        """When Node.js >= 18 is present but Archify engine is absent, report clear guidance without auto-install."""
        fake_proc = mock.Mock()
        fake_proc.stdout = "v20.10.0\n"
        with mock.patch("shutil.which", return_value="/usr/bin/node"):
            with mock.patch("subprocess.run", return_value=fake_proc):
                with mock.patch.object(archify_delivery, "find_archify_root", return_value=None):
                    env_status = archify_delivery.check_environment()
                    self.assertTrue(env_status["node_ok"])
                    self.assertFalse(env_status["ready"])
                    self.assertIn("Archify root directory not found", env_status.get("error", ""))

                    ok, detail = tdq_setup.kiem_tra_archify()
                    self.assertFalse(ok)
                    self.assertIn("ARCHIFY_ROOT", detail)


class TestAgentFirstConfigurationAndOffline(unittest.TestCase):
    """Tests for agent-first configuration: no AI client, offline CI flag."""

    def test_no_remote_ai_client_imports_or_calls(self):
        """Ensure archify modules do not instantiate remote AI/LLM clients."""
        for mod in (archify_delivery, tdq_setup):
            src = inspect.getsource(mod)
            self.assertNotIn("import openai", src)
            self.assertNotIn("from openai import", src)
            self.assertNotIn("import anthropic", src)
            self.assertNotIn("from anthropic import", src)

    def test_offline_update_check_disabled(self):
        """Finalize execution sets ARCHIFY_UPDATE_CHECK_DISABLED=1 to run offline."""
        with tempfile.TemporaryDirectory() as td:
            cand = Path(td) / "candidate.json"
            cand.write_text(json.dumps({"title": "Test"}), encoding="utf-8")
            out = Path(td) / "output.html"

            captured_env = {}

            def fake_run(cmd, **kwargs):
                nonlocal captured_env
                captured_env = kwargs.get("env", {})
                res = mock.Mock()
                res.returncode = 1
                res.stdout = ""
                res.stderr = ""
                return res

            with mock.patch("shutil.which", return_value="node"):
                with mock.patch.object(archify_delivery, "get_archify_bin", return_value=Path(td) / "bin" / "archify.mjs"):
                    with mock.patch("subprocess.run", side_effect=fake_run):
                        archify_delivery.run_finalize(
                            diagram_type="architecture",
                            candidate_path=cand,
                            output_path=out,
                            archify_root=td,
                        )
            self.assertEqual(captured_env.get("ARCHIFY_UPDATE_CHECK_DISABLED"), "1")


class TestDiagramTypeBrowserGate(unittest.TestCase):
    """Tests for browser gate policy by diagram type: native requires pass; explainer accepts not-run."""

    def _make_receipt(self, browser_gate_status, out_path, cand_path):
        cand_bytes = cand_path.read_bytes()
        cand_sha = hashlib.sha256(cand_bytes).hexdigest()
        out_bytes = out_path.read_bytes()
        out_sha = hashlib.sha256(out_bytes).hexdigest()

        return {
            "ok": True,
            "status": "pass",
            "gates": {
                "validate": "pass",
                "deliver": "pass",
                "check": "pass",
                "browser-check": browser_gate_status,
            },
            "specification": {"sha256": cand_sha},
            "artifact": {
                "path": str(out_path.resolve()),
                "sha256": out_sha,
                "bytes": len(out_bytes),
            },
            "diagnostics": [],
        }

    def test_explainer_accepts_browser_check_not_run(self):
        """Explainer diagrams accept 'not-run' for browser-check."""
        with tempfile.TemporaryDirectory() as td:
            cand = Path(td) / "explainer.json"
            cand.write_text(json.dumps({"type": "explainer"}), encoding="utf-8")
            out = Path(td) / "explainer.html"
            out.write_text("<html>explainer</html>", encoding="utf-8")

            receipt = self._make_receipt("not-run", out, cand)
            fake_proc = mock.Mock()
            fake_proc.returncode = 0
            fake_proc.stdout = json.dumps(receipt)
            fake_proc.stderr = ""

            with mock.patch("shutil.which", return_value="node"):
                with mock.patch.object(archify_delivery, "get_archify_bin", return_value=Path(td) / "bin" / "archify.mjs"):
                    with mock.patch("subprocess.run", return_value=fake_proc):
                        result = archify_delivery.run_finalize(
                            diagram_type="explainer",
                            candidate_path=cand,
                            output_path=out,
                            archify_root=td,
                        )
            self.assertTrue(result.status, f"Explainer should pass with not-run: {result.receipt}")

    def test_native_diagram_requires_browser_check_pass(self):
        """Native diagram types (architecture, sequence, etc.) require browser-check to pass."""
        with tempfile.TemporaryDirectory() as td:
            cand = Path(td) / "architecture.json"
            cand.write_text(json.dumps({"type": "architecture"}), encoding="utf-8")
            out = Path(td) / "architecture.html"
            out.write_text("<html>arch</html>", encoding="utf-8")

            # 1. 'not-run' must fail on native diagrams
            receipt_not_run = self._make_receipt("not-run", out, cand)
            fake_proc_not_run = mock.Mock()
            fake_proc_not_run.returncode = 0
            fake_proc_not_run.stdout = json.dumps(receipt_not_run)
            fake_proc_not_run.stderr = ""

            with mock.patch("shutil.which", return_value="node"):
                with mock.patch.object(archify_delivery, "get_archify_bin", return_value=Path(td) / "bin" / "archify.mjs"):
                    with mock.patch("subprocess.run", return_value=fake_proc_not_run):
                        result = archify_delivery.run_finalize(
                            diagram_type="architecture",
                            candidate_path=cand,
                            output_path=out,
                            archify_root=td,
                        )
            self.assertFalse(result.status, "Native diagram must fail when browser-check is not-run")

            # 2. 'pass' must succeed on native diagrams
            receipt_pass = self._make_receipt("pass", out, cand)
            fake_proc_pass = mock.Mock()
            fake_proc_pass.returncode = 0
            fake_proc_pass.stdout = json.dumps(receipt_pass)
            fake_proc_pass.stderr = ""

            with mock.patch("shutil.which", return_value="node"):
                with mock.patch.object(archify_delivery, "get_archify_bin", return_value=Path(td) / "bin" / "archify.mjs"):
                    with mock.patch("subprocess.run", return_value=fake_proc_pass):
                        result_pass = archify_delivery.run_finalize(
                            diagram_type="architecture",
                            candidate_path=cand,
                            output_path=out,
                            archify_root=td,
                        )
            self.assertTrue(result_pass.status, "Native diagram must succeed when browser-check passes")


class TestRuntimePackagingClosure(unittest.TestCase):
    """Tests for runtime packaging closure of Archify modules."""

    def test_archify_modules_included_in_release(self):
        """Verify all four Archify integration modules are included in the release filter."""
        archify_modules = (
            "scripts/tdq_archify.py",
            "scripts/archify_delivery.py",
            "scripts/archify_model.py",
            "scripts/archify_artifacts.py",
        )
        for rel_path in archify_modules:
            self.assertTrue(
                build_portable.la_duong_dan_release(rel_path),
                f"Archify module {rel_path} must be included in release branch",
            )

    def test_runtime_closure_integrity(self):
        """Verify transitive closure from all runtime entrypoints is complete."""
        scripts_dir = str(SCRIPTS_DIR)
        all_py = {f[:-3] for f in os.listdir(scripts_dir) if f.endswith(".py")}
        entrypoints = {"tdq_setup", "tdq_state", "tdq_finish", "tdq_archify"} & all_py

        closure = build_portable.tinh_bao_dong_import(scripts_dir, diem_vao=entrypoints)
        for mod in closure:
            self.assertTrue(
                build_portable.la_duong_dan_release(f"scripts/{mod}.py"),
                f"Module {mod} in entrypoints closure must be kept in release",
            )
            self.assertNotIn(
                f"{mod}.py",
                build_portable.RELEASE_EXCLUDE_SCRIPTS,
                f"Module {mod} in closure must not be in RELEASE_EXCLUDE_SCRIPTS",
            )


if __name__ == "__main__":
    unittest.main()
