"""Unit tests for tdq_archify adapter module.

Tests cover:
- find_archify_root & get_archify_bin
- check_environment (Node >= 18 check, missing Node, missing Archify)
- build_finalize_command (quality, json, repo-root flags)
- graphify_to_archify (AST parsing, community filtering, max_nodes, sources)
- open_artifact (platform-specific browser opening)
- cli execution (check, test-bridge, bridge, render, sync-master)
- atomic_delivery and run_finalize execution
"""
import io
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

from helper import ROOT

sys.path.insert(0, os.path.join(ROOT, "scripts"))
import tdq_archify  # noqa: E402


class TestFindArchifyRoot(unittest.TestCase):
    """Test suite for find_archify_root and get_archify_bin."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir, True)

    def test_find_archify_root_via_env(self):
        """ARCHIFY_ROOT environment variable pointing to a valid installation."""
        bin_dir = Path(self.temp_dir) / "bin"
        bin_dir.mkdir(parents=True)
        mjs_file = bin_dir / "archify.mjs"
        mjs_file.write_text("// test archify entry", encoding="utf-8")

        with mock.patch.dict(os.environ, {"ARCHIFY_ROOT": self.temp_dir}):
            root = tdq_archify.find_archify_root()
            self.assertEqual(root, self.temp_dir)

    def test_find_archify_root_via_nested_bin(self):
        """ARCHIFY_ROOT containing archify/bin/archify.mjs."""
        bin_dir = Path(self.temp_dir) / "archify" / "bin"
        bin_dir.mkdir(parents=True)
        mjs_file = bin_dir / "archify.mjs"
        mjs_file.write_text("// test archify entry", encoding="utf-8")

        with mock.patch.dict(os.environ, {"ARCHIFY_ROOT": self.temp_dir}):
            root = tdq_archify.find_archify_root()
            self.assertEqual(root, self.temp_dir)

    def test_find_archify_root_not_found(self):
        """Returns None when no candidate directories contain archify.mjs."""
        with mock.patch.dict(os.environ, {"ARCHIFY_ROOT": ""}, clear=True):
            with mock.patch("pathlib.Path.exists", return_value=False):
                root = tdq_archify.find_archify_root()
                self.assertIsNone(root)

    def test_get_archify_bin_direct(self):
        """Resolve archify.mjs under direct bin/."""
        bin_dir = Path(self.temp_dir) / "bin"
        bin_dir.mkdir(parents=True)
        mjs_file = bin_dir / "archify.mjs"
        mjs_file.write_text("// direct", encoding="utf-8")

        resolved = tdq_archify.get_archify_bin(self.temp_dir)
        self.assertEqual(resolved, mjs_file)

    def test_get_archify_bin_nested(self):
        """Resolve archify.mjs under archify/bin/."""
        bin_dir = Path(self.temp_dir) / "archify" / "bin"
        bin_dir.mkdir(parents=True)
        mjs_file = bin_dir / "archify.mjs"
        mjs_file.write_text("// nested", encoding="utf-8")

        resolved = tdq_archify.get_archify_bin(self.temp_dir)
        self.assertEqual(resolved, mjs_file)

    def test_get_archify_bin_none_when_missing(self):
        """Returns None if archify.mjs does not exist in root."""
        resolved = tdq_archify.get_archify_bin(self.temp_dir)
        self.assertIsNone(resolved)


class TestCheckEnvironment(unittest.TestCase):
    """Test suite for check_environment pre-flight validation."""

    def test_check_environment_no_node(self):
        """When Node.js is not installed, node_ok and ready must be False."""
        with mock.patch("shutil.which", return_value=None):
            with mock.patch("tdq_archify.find_archify_root", return_value=None):
                env = tdq_archify.check_environment()
                self.assertFalse(env["node_ok"])
                self.assertEqual(env["node_version"], "")
                self.assertFalse(env["ready"])

    def test_check_environment_old_node(self):
        """When Node.js version is < 18, node_ok must be False."""
        mock_proc = mock.MagicMock(stdout="v16.14.2\n")
        with mock.patch("shutil.which", return_value="node"):
            with mock.patch("subprocess.run", return_value=mock_proc):
                with mock.patch("tdq_archify.find_archify_root", return_value="/opt/archify"):
                    with mock.patch("tdq_archify.get_archify_bin", return_value=Path("/opt/archify/bin/archify.mjs")):
                        env = tdq_archify.check_environment()
                        self.assertFalse(env["node_ok"])
                        self.assertIn("16", env["node_version"])
                        self.assertFalse(env["ready"])

    def test_check_environment_valid_node_and_archify(self):
        """When Node >= 18 and Archify is installed, ready must be True."""
        mock_proc = mock.MagicMock(stdout="v20.10.0\n")
        with mock.patch("shutil.which", return_value="node"):
            with mock.patch("subprocess.run", return_value=mock_proc):
                with mock.patch("tdq_archify.find_archify_root", return_value="/opt/archify"):
                    with mock.patch("tdq_archify.get_archify_bin", return_value=Path("/opt/archify/bin/archify.mjs")):
                        env = tdq_archify.check_environment()
                        self.assertTrue(env["node_ok"])
                        self.assertEqual(env["node_version"], "v20.10.0")
                        self.assertEqual(env["archify_root"], "/opt/archify")
                        self.assertTrue(env["ready"])

    def test_check_environment_valid_node_missing_archify(self):
        """When Node >= 18 but Archify is missing, ready must be False."""
        mock_proc = mock.MagicMock(stdout="v22.5.0\n")
        with mock.patch("shutil.which", return_value="node"):
            with mock.patch("subprocess.run", return_value=mock_proc):
                with mock.patch("tdq_archify.find_archify_root", return_value=None):
                    env = tdq_archify.check_environment()
                    self.assertTrue(env["node_ok"])
                    self.assertFalse(env["ready"])


class TestBuildFinalizeCommand(unittest.TestCase):
    """Test suite for build_finalize_command argument construction."""

    def test_build_finalize_command_success(self):
        """Verify command arguments match CLI contract."""
        fake_bin = Path("/tmp/archify/bin/archify.mjs")
        with mock.patch("shutil.which", return_value="node"):
            with mock.patch("tdq_archify.get_archify_bin", return_value=fake_bin):
                cmd = tdq_archify.build_finalize_command(
                    diagram_type="architecture",
                    candidate_path="candidate.json",
                    output_path="out.html",
                    quality="showcase",
                )
                self.assertEqual(cmd[0], "node")
                self.assertEqual(cmd[1], str(fake_bin))
                self.assertEqual(cmd[2], "finalize")
                self.assertEqual(cmd[3], "architecture")
                self.assertEqual(cmd[4], "candidate.json")
                self.assertEqual(cmd[5], "out.html")
                self.assertIn("--quality", cmd)
                self.assertEqual(cmd[cmd.index("--quality") + 1], "showcase")
                self.assertIn("--json", cmd)

    def test_build_finalize_command_with_repo_root(self):
        """Verify --repo-root is appended when specified."""
        fake_bin = Path("/tmp/archify/bin/archify.mjs")
        with mock.patch("shutil.which", return_value="node"):
            with mock.patch("tdq_archify.get_archify_bin", return_value=fake_bin):
                cmd = tdq_archify.build_finalize_command(
                    diagram_type="architecture",
                    candidate_path="candidate.json",
                    output_path="out.html",
                    repo_root="/repo",
                )
                self.assertIn("--repo-root", cmd)
                self.assertEqual(cmd[cmd.index("--repo-root") + 1], "/repo")

    def test_build_finalize_command_missing_archify_bin(self):
        """Raises FileNotFoundError when archify binary cannot be located."""
        with mock.patch("tdq_archify.get_archify_bin", return_value=None):
            with self.assertRaises(FileNotFoundError):
                tdq_archify.build_finalize_command(
                    diagram_type="architecture",
                    candidate_path="candidate.json",
                    output_path="out.html",
                )


class TestGraphifyToArchify(unittest.TestCase):
    """Test suite for graphify_to_archify parser and JSON-IR structure."""

    def setUp(self):
        self.sample_graph = {
            "nodes": [
                {
                    "id": "auth_svc",
                    "label": "Auth Service",
                    "community": 1,
                    "source_file": "src/auth.py",
                    "source_location": "L10-L40",
                    "type": "security",
                },
                {
                    "id": "order_api",
                    "label": "Order API",
                    "community": 1,
                    "source_file": "src/order.py",
                    "source_location": "L50",
                    "type": "backend",
                },
                {
                    "id": "postgres_db",
                    "label": "Postgres DB",
                    "community": 1,
                    "source_file": "src/db.py",
                    "source_location": "L100",
                    "type": "database",
                },
                {
                    "id": "frontend_app",
                    "label": "Web Client",
                    "community": 2,
                    "source_file": "frontend/app.tsx",
                    "type": "frontend",
                },
                {
                    "id": "kafka_stream",
                    "label": "Kafka Event Bus",
                    "community": 2,
                    "type": "messagebus",
                },
                {
                    "id": "s3_storage",
                    "label": "AWS S3",
                    "community": 2,
                    "type": "cloud",
                },
                {
                    "id": "third_party_api",
                    "label": "Payment Gateway",
                    "community": 2,
                    "external": True,
                },
            ],
            "links": [
                {"source": "frontend_app", "target": "auth_svc", "relation": "authenticates"},
                {"source": "frontend_app", "target": "order_api", "relation": "places_order"},
                {"source": "order_api", "target": "postgres_db", "relation": "writes"},
                {"source": "order_api", "target": "kafka_stream", "relation": "publishes"},
                {"source": "order_api", "target": "third_party_api", "relation": "calls"},
            ],
        }

    def test_valid_json_ir_structure(self):
        """Verifies schema_version, diagram_type, components, connections, and meta."""
        ir = tdq_archify.graphify_to_archify(self.sample_graph)
        self.assertEqual(ir["schema_version"], 1)
        self.assertEqual(ir["diagram_type"], "architecture")
        self.assertIn("meta", ir)
        self.assertEqual(ir["meta"]["output"], "master.architecture.html")
        self.assertIsInstance(ir["components"], list)
        self.assertIsInstance(ir["connections"], list)
        self.assertEqual(len(ir["components"]), 7)
        self.assertEqual(len(ir["connections"]), 5)

    def test_sources_and_line_number_parsing(self):
        """Tests line range L10-L40 vs single line L50 parsing."""
        ir = tdq_archify.graphify_to_archify(self.sample_graph)
        auth = next(c for c in ir["components"] if c["id"] == "auth_svc")
        self.assertEqual(len(auth["sources"]), 1)
        self.assertEqual(auth["sources"][0]["path"], "src/auth.py")
        self.assertEqual(auth["sources"][0]["startLine"], 10)
        self.assertEqual(auth["sources"][0]["endLine"], 40)

        order = next(c for c in ir["components"] if c["id"] == "order_api")
        self.assertEqual(order["sources"][0]["startLine"], 50)
        self.assertEqual(order["sources"][0]["endLine"], 50)

    def test_type_heuristics_and_mappings(self):
        """Tests type categorization for frontend, cloud, messagebus, external."""
        ir = tdq_archify.graphify_to_archify(self.sample_graph)
        type_by_id = {c["id"]: c["type"] for c in ir["components"]}
        self.assertEqual(type_by_id["frontend_app"], "frontend")
        self.assertEqual(type_by_id["kafka_stream"], "messagebus")
        self.assertEqual(type_by_id["s3_storage"], "cloud")
        self.assertEqual(type_by_id["third_party_api"], "external")

    def test_focus_community_filter(self):
        """Filters nodes and links to only those belonging to focus_community."""
        ir_comm1 = tdq_archify.graphify_to_archify(self.sample_graph, focus_community=1)
        comp_ids = {c["id"] for c in ir_comm1["components"]}
        self.assertEqual(comp_ids, {"auth_svc", "order_api", "postgres_db"})
        # Only order_api -> postgres_db is within community 1
        self.assertEqual(len(ir_comm1["connections"]), 1)
        self.assertEqual(ir_comm1["connections"][0]["from"], "order_api")
        self.assertEqual(ir_comm1["connections"][0]["to"], "postgres_db")
        self.assertIn("Community 1", ir_comm1["meta"]["title"])

    def test_max_nodes_filter(self):
        """Limits output to top-degree nodes when total exceeds max_nodes."""
        ir = tdq_archify.graphify_to_archify(self.sample_graph, max_nodes=3)
        self.assertEqual(len(ir["components"]), 3)
        # order_api has degree 4 (order_api -> postgres, kafka, payment, and frontend -> order_api)
        comp_ids = {c["id"] for c in ir["components"]}
        self.assertIn("order_api", comp_ids)

    def test_graphify_from_file(self):
        """Verifies loading graph from JSON file on disk."""
        temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, temp_dir, True)
        file_path = Path(temp_dir) / "graph.json"
        file_path.write_text(json.dumps(self.sample_graph), encoding="utf-8")

        ir = tdq_archify.graphify_to_archify(file_path)
        self.assertEqual(len(ir["components"]), 7)

    def test_graphify_file_not_found(self):
        """Raises FileNotFoundError when graph file does not exist."""
        with self.assertRaises(FileNotFoundError):
            tdq_archify.graphify_to_archify("nonexistent_graph_file.json")


class TestOpenArtifact(unittest.TestCase):
    """Test suite for open_artifact browser launcher."""

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        self.temp_file.close()
        self.addCleanup(os.unlink, self.temp_file.name)

    def test_open_artifact_not_found(self):
        """Returns False when target artifact file does not exist."""
        ok = tdq_archify.open_artifact("missing_file.html")
        self.assertFalse(ok)

    def test_open_artifact_windows(self):
        """Verifies powershell Start-Process invocation on Windows."""
        with mock.patch("platform.system", return_value="Windows"):
            with mock.patch("subprocess.run") as mock_run:
                ok = tdq_archify.open_artifact(self.temp_file.name)
                self.assertTrue(ok)
                mock_run.assert_called_once()
                args = mock_run.call_args[0][0]
                self.assertEqual(args[0], "powershell.exe")
                self.assertIn("Start-Process", args[4])

    def test_open_artifact_darwin(self):
        """Verifies open command invocation on macOS (Darwin)."""
        with mock.patch("platform.system", return_value="Darwin"):
            with mock.patch("subprocess.run") as mock_run:
                ok = tdq_archify.open_artifact(self.temp_file.name)
                self.assertTrue(ok)
                mock_run.assert_called_once()
                args = mock_run.call_args[0][0]
                self.assertEqual(args[0], "open")

    def test_open_artifact_linux(self):
        """Verifies xdg-open command invocation on Linux."""
        with mock.patch("platform.system", return_value="Linux"):
            with mock.patch("subprocess.run") as mock_run:
                ok = tdq_archify.open_artifact(self.temp_file.name)
                self.assertTrue(ok)
                mock_run.assert_called_once()
                args = mock_run.call_args[0][0]
                self.assertEqual(args[0], "xdg-open")

    def test_open_artifact_subprocess_failure(self):
        """Returns False when subprocess raises an exception."""
        with mock.patch("platform.system", return_value="Linux"):
            with mock.patch("subprocess.run", side_effect=OSError("Exec failed")):
                ok = tdq_archify.open_artifact(self.temp_file.name)
                self.assertFalse(ok)


class TestCliCommands(unittest.TestCase):
    """Test suite for CLI sub-command execution."""

    def test_cli_check_success(self):
        """CLI 'check' exits with code 0 when ready is True."""
        mock_env = {"node_ok": True, "node_version": "v20.0.0", "ready": True}
        with mock.patch("tdq_archify.check_environment", return_value=mock_env):
            with mock.patch.object(sys, "argv", ["tdq_archify.py", "check"]):
                code = tdq_archify.main()
                self.assertEqual(code, 0)

    def test_cli_check_failure(self):
        """CLI 'check' exits with code 1 when ready is False."""
        mock_env = {"node_ok": False, "node_version": "", "ready": False}
        with mock.patch("tdq_archify.check_environment", return_value=mock_env):
            with mock.patch.object(sys, "argv", ["tdq_archify.py", "check"]):
                code = tdq_archify.main()
                self.assertEqual(code, 1)

    def test_cli_test_bridge(self):
        """CLI 'test-bridge' executes self-test and returns 0 on success."""
        with mock.patch("tdq_archify.test_bridge", return_value=True):
            with mock.patch.object(sys, "argv", ["tdq_archify.py", "test-bridge"]):
                code = tdq_archify.main()
                self.assertEqual(code, 0)

    def test_cli_test_bridge_failure(self):
        """CLI 'test-bridge' returns 1 when test_bridge raises an error."""
        with mock.patch("tdq_archify.test_bridge", side_effect=AssertionError("Mismatch")):
            with mock.patch.object(sys, "argv", ["tdq_archify.py", "test-bridge"]):
                code = tdq_archify.main()
                self.assertEqual(code, 1)

    def test_cli_render(self):
        """CLI 'render' calls run_finalize and handles status."""
        fake_res = tdq_archify.FinalizeResult(status=True, receipt={"ok": True})
        with mock.patch("tdq_archify.run_finalize", return_value=fake_res):
            with mock.patch.object(
                sys,
                "argv",
                [
                    "tdq_archify.py",
                    "render",
                    "--type",
                    "architecture",
                    "--candidate",
                    "cand.json",
                    "--out",
                    "out.html",
                ],
            ):
                code = tdq_archify.main()
                self.assertEqual(code, 0)

    def test_cli_bridge(self):
        """CLI 'bridge' runs graphify_to_archify and atomic_delivery."""
        temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, temp_dir, True)
        graph_file = Path(temp_dir) / "graph.json"
        graph_file.write_text(json.dumps({"nodes": [], "links": []}), encoding="utf-8")
        out_file = Path(temp_dir) / "out.json"

        with mock.patch.object(
            sys,
            "argv",
            [
                "tdq_archify.py",
                "bridge",
                "--graph",
                str(graph_file),
                "--out",
                str(out_file),
            ],
        ):
            code = tdq_archify.main()
            self.assertEqual(code, 0)
            self.assertTrue(out_file.is_file())


class TestUtilities(unittest.TestCase):
    """Test atomic_delivery, sync_master, and test_bridge built-in runner."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir, True)

    def test_atomic_delivery_str_and_bytes(self):
        """atomic_delivery safely writes text and binary payloads."""
        file_txt = Path(self.temp_dir) / "nested" / "test.txt"
        tdq_archify.atomic_delivery(file_txt, "hello world")
        self.assertEqual(file_txt.read_text(encoding="utf-8"), "hello world")

        file_bin = Path(self.temp_dir) / "nested" / "test.bin"
        tdq_archify.atomic_delivery(file_bin, b"\x00\x01\x02")
        self.assertEqual(file_bin.read_bytes(), b"\x00\x01\x02")

    def test_run_test_bridge_builtin(self):
        """test_bridge self-test function returns True."""
        self.assertTrue(tdq_archify.test_bridge())

    def test_sync_master_with_mock_graph(self):
        """sync_master converts graph and outputs to target JSON path."""
        graph_path = Path(self.temp_dir) / "graph.json"
        out_path = Path(self.temp_dir) / "master.architecture.json"
        graph_path.write_text(json.dumps({"nodes": [{"id": "n1"}], "links": []}), encoding="utf-8")

        ok = tdq_archify.sync_master(graph_path=graph_path, out_path=out_path)
        self.assertTrue(ok)
        self.assertTrue(out_path.is_file())
        data = json.loads(out_path.read_text(encoding="utf-8"))
        self.assertEqual(data["schema_version"], 1)

    def test_sync_master_missing_graph(self):
        """sync_master gracefully skips and returns False if graph.json is absent."""
        missing = Path(self.temp_dir) / "not_there.json"
        ok = tdq_archify.sync_master(graph_path=missing)
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
