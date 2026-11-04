"""Unit tests for archify_model module.

Tests cover:
- graphify_to_archify:
  * Pure Archify IR envelope (schema_version=1, diagram_type="architecture")
  * Explicit grid layout (row, col, layout.mode="grid", cols)
  * Default backend component type and 'topology candidate' sublabel
  * No inferred role heuristics from filenames
  * Undirected graph produces no inferred directed call connections
  * Directed graph produces valid connections with from, to, label
  * Focus community filtering
  * Max nodes deterministic degree-based filtering
  * Working-tree and planned evidence kinds do not attach committed sources
  * Committed evidence kind with repository attaches sources with path, line, end_line
  * Source location parsing (L10-L40, L50)
  * Node ID sanitization and stability (matching ^[a-zA-Z][a-zA-Z0-9_-]*$)
  * Error cases: empty graph, missing file, invalid evidence_kind, missing repository
- graph_coverage:
  * Total, selected, excluded counts and inventory
  * Directed flag reflection
  * Unproven relationships for undirected graphs and undirected links
  * Modules inventory with verified vs excluded status
- validate_model:
  * Valid committed model envelope
  * Valid working-tree and planned model envelopes
  * Invalid schema_version, title, evidence_kind
  * Committed missing 40-hex revision or repository
  * Safe relative source_paths validation (rejecting absolute paths, .. traversals, drive letters)
  * Safe view candidates (ending in .json, rejecting path traversal or absolute paths)
  * Duplicate view IDs and duplicate candidate paths
  * Invalid view diagram types
- Real Archify engine validation:
  * Validates generated candidate JSON against local Archify validate CLI
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Add scripts directory to path for imports
_CURRENT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _CURRENT_DIR.parent
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import archify_model  # noqa: E402


class TestGraphifyToArchify(unittest.TestCase):
    """Test suite for graphify_to_archify conversion."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir, True)

        self.sample_undirected_graph = {
            "directed": False,
            "nodes": [
                {
                    "id": "src/auth_service.py",
                    "label": "Auth Service",
                    "community": 1,
                    "source_file": "src/auth_service.py",
                    "source_location": "L10-L40",
                },
                {
                    "id": "order_api",
                    "label": "Order API",
                    "community": 1,
                    "source_file": "src/order_api.py",
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
                    "id": "payment_gateway",
                    "label": "Payment Gateway",
                    "community": 2,
                    "external": True,
                },
            ],
            "links": [
                {"source": "frontend_app", "target": "src/auth_service.py", "relation": "authenticates"},
                {"source": "frontend_app", "target": "order_api", "relation": "places_order"},
                {"source": "order_api", "target": "postgres_db", "relation": "writes"},
                {"source": "order_api", "target": "kafka_stream", "relation": "publishes"},
                {"source": "order_api", "target": "payment_gateway", "relation": "calls"},
            ],
        }

        self.sample_directed_graph = dict(self.sample_undirected_graph)
        self.sample_directed_graph["directed"] = True

    def test_valid_graph_conversion_envelope(self):
        """Verifies pure Archify IR envelope conforms to schema_version 1 and architecture diagram_type."""
        ir = archify_model.graphify_to_archify(self.sample_undirected_graph)
        self.assertEqual(ir["schema_version"], 1)
        self.assertEqual(ir["diagram_type"], "architecture")
        self.assertIn("meta", ir)
        self.assertEqual(ir["meta"]["output"], "master.architecture.html")
        self.assertEqual(ir["meta"]["title"], "Codebase Architecture")
        self.assertIn("layout", ir)
        self.assertIn("components", ir)
        self.assertIn("connections", ir)
        self.assertEqual(len(ir["components"]), 7)

    def test_explicit_grid_layout(self):
        """Verifies explicit grid layout is generated with row and col coordinates."""
        ir = archify_model.graphify_to_archify(self.sample_undirected_graph)
        layout = ir["layout"]
        self.assertEqual(layout["mode"], "grid")
        self.assertGreaterEqual(layout["cols"], 1)
        self.assertLessEqual(layout["cols"], 12)
        self.assertGreaterEqual(layout["cellW"], 40)
        self.assertGreaterEqual(layout["cellH"], 24)

        for comp in ir["components"]:
            self.assertIn("row", comp)
            self.assertIn("col", comp)
            self.assertIsInstance(comp["row"], int)
            self.assertIsInstance(comp["col"], int)
            self.assertGreaterEqual(comp["row"], 0)
            self.assertGreaterEqual(comp["col"], 0)

    def test_no_inferred_role_from_filename(self):
        """Contract: do not infer role/domain from filename; default untyped components to backend."""
        untyped_graph = {
            "directed": False,
            "nodes": [
                {
                    "id": "crypto_jwt_security",
                    "label": "Crypto Security Handler",
                    "source_file": "src/security_auth_crypto.py",
                }
            ],
        }
        ir = archify_model.graphify_to_archify(untyped_graph)
        comp = ir["components"][0]
        # Should be backend (default), NOT security
        self.assertEqual(comp["type"], "backend")
        # Sublabel should indicate topology candidate
        self.assertEqual(comp["sublabel"], "topology candidate")

    def test_declared_component_types_preserved(self):
        """Verifies explicitly declared component types and external flags are preserved."""
        ir = archify_model.graphify_to_archify(self.sample_undirected_graph)
        type_by_id = {c["label"]: c["type"] for c in ir["components"]}
        self.assertEqual(type_by_id["Web Client"], "frontend")
        self.assertEqual(type_by_id["Postgres DB"], "database")
        self.assertEqual(type_by_id["Kafka Event Bus"], "messagebus")
        self.assertEqual(type_by_id["AWS S3"], "cloud")
        self.assertEqual(type_by_id["Payment Gateway"], "external")

    def test_undirected_graph_no_inferred_directed_calls(self):
        """Contract: undirected graph produces no inferred directed call connections."""
        ir = archify_model.graphify_to_archify(self.sample_undirected_graph)
        self.assertEqual(ir["connections"], [])

    def test_directed_graph_connections(self):
        """Directed graph produces valid directed connections."""
        ir = archify_model.graphify_to_archify(self.sample_directed_graph)
        self.assertEqual(len(ir["connections"]), 5)
        for conn in ir["connections"]:
            self.assertIn("id", conn)
            self.assertIn("from", conn)
            self.assertIn("to", conn)
            self.assertIn("label", conn)

    def test_focus_community_filter(self):
        """Filters nodes and title by focus_community."""
        ir = archify_model.graphify_to_archify(self.sample_undirected_graph, focus_community=1)
        self.assertEqual(len(ir["components"]), 3)
        self.assertIn("Community 1", ir["meta"]["title"])
        self.assertEqual(ir["meta"]["output"], "community_1.architecture.html")

    def test_max_nodes_filter_stable(self):
        """Limits nodes to top-degree nodes deterministically."""
        ir = archify_model.graphify_to_archify(self.sample_directed_graph, max_nodes=3)
        self.assertEqual(len(ir["components"]), 3)
        comp_ids = {c["id"] for c in ir["components"]}
        # order_api has the highest degree (4) and must be included
        self.assertIn("order_api", comp_ids)

    def test_working_tree_evidence_no_committed_sources(self):
        """Contract: working-tree evidence kind must not attach committed sources or meta repository."""
        ir = archify_model.graphify_to_archify(
            self.sample_undirected_graph,
            evidence_kind="working-tree",
        )
        self.assertNotIn("repository", ir["meta"])
        for comp in ir["components"]:
            self.assertNotIn("sources", comp)

    def test_planned_evidence_no_sources(self):
        """Contract: planned evidence kind must not attach sources."""
        ir = archify_model.graphify_to_archify(
            self.sample_undirected_graph,
            evidence_kind="planned",
        )
        for comp in ir["components"]:
            self.assertNotIn("sources", comp)

    def test_committed_evidence_sources_line_end_line(self):
        """Contract: committed evidence kind with repository attaches sources with path, line, end_line."""
        repo = {
            "url": "https://github.com/example/project.git",
            "revision": "a" * 40,
            "link_mode": "local-only",
        }
        ir = archify_model.graphify_to_archify(
            self.sample_undirected_graph,
            evidence_kind="committed",
            repository=repo,
        )
        self.assertEqual(ir["meta"]["repository"], repo)

        auth_comp = next(c for c in ir["components"] if c["label"] == "Auth Service")
        self.assertIn("sources", auth_comp)
        source = auth_comp["sources"][0]
        self.assertEqual(source["path"], "src/auth_service.py")
        self.assertEqual(source["line"], 10)
        self.assertEqual(source["end_line"], 40)
        # Upstream schema must not contain startLine or endLine
        self.assertNotIn("startLine", source)
        self.assertNotIn("endLine", source)

    def test_source_location_parsing(self):
        """Tests parsing of single line (L50) and line range (L10-L40)."""
        repo = {
            "url": "https://github.com/example/project.git",
            "revision": "b" * 40,
        }
        ir = archify_model.graphify_to_archify(
            self.sample_undirected_graph,
            evidence_kind="committed",
            repository=repo,
        )
        order_comp = next(c for c in ir["components"] if c["id"] == "order_api")
        source = order_comp["sources"][0]
        self.assertEqual(source["line"], 50)
        self.assertEqual(source["end_line"], 50)

    def test_id_sanitization_and_stability(self):
        """Tests that node IDs with slashes and special characters are sanitized to valid Archify IDs."""
        ir = archify_model.graphify_to_archify(self.sample_directed_graph)
        # 'src/auth_service.py' should be sanitized to 'src_auth_service_py'
        cids = {c["id"] for c in ir["components"]}
        self.assertIn("src_auth_service_py", cids)

        # Connection to src/auth_service.py must use sanitized ID
        conn = next(c for c in ir["connections"] if c["to"] == "src_auth_service_py")
        self.assertEqual(conn["from"], "frontend_app")

    def test_empty_graph_raises_value_error(self):
        """Empty graph or graph with 0 nodes raises ValueError."""
        with self.assertRaises(ValueError):
            archify_model.graphify_to_archify({"nodes": []})

    def test_missing_file_raises_file_not_found(self):
        """Nonexistent file raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            archify_model.graphify_to_archify(Path(self.temp_dir) / "nonexistent.json")

    def test_invalid_evidence_kind_raises_value_error(self):
        """Invalid evidence_kind raises ValueError."""
        with self.assertRaises(ValueError):
            archify_model.graphify_to_archify(self.sample_undirected_graph, evidence_kind="bogus")

    def test_current_evidence_kind_rejected(self):
        """'current' is freshness status, not a valid evidence_kind, and must be rejected."""
        with self.assertRaises(ValueError):
            archify_model.graphify_to_archify(self.sample_undirected_graph, evidence_kind="current")

    def test_duplicate_raw_node_ids_raises_value_error(self):
        """Graph with duplicate raw node IDs raises ValueError."""
        dup_graph = {
            "directed": False,
            "nodes": [
                {"id": "service_a", "label": "Service A"},
                {"id": "service_a", "label": "Service A duplicate"},
            ],
        }
        with self.assertRaises(ValueError):
            archify_model.graphify_to_archify(dup_graph)

    def test_colliding_sanitized_ids_disambiguated(self):
        """Distinct raw IDs that sanitize to the same string are stably disambiguated."""
        colliding_graph = {
            "directed": False,
            "nodes": [
                {"id": "service.a", "label": "Service A Dot"},
                {"id": "service_a", "label": "Service A Underscore"},
            ],
        }
        ir = archify_model.graphify_to_archify(colliding_graph)
        cids = [c["id"] for c in ir["components"]]
        self.assertEqual(len(cids), 2)
        self.assertEqual(len(set(cids)), 2)
        self.assertEqual(cids[0], "service_a")
        self.assertEqual(cids[1], "service_a_2")

    def test_reverse_line_range_rejected(self):
        """Line ranges specified in reverse order (end < start) raise ValueError."""
        repo = {
            "url": "https://github.com/example/project.git",
            "revision": "c" * 40,
        }
        graph = {
            "directed": False,
            "nodes": [
                {
                    "id": "module_x",
                    "label": "Module X",
                    "source_file": "src/x.py",
                    "line": 100,
                    "end_line": 20,
                }
            ],
        }
        with self.assertRaises(ValueError):
            archify_model.graphify_to_archify(graph, evidence_kind="committed", repository=repo)

        loc_graph = {
            "directed": False,
            "nodes": [
                {
                    "id": "module_y",
                    "label": "Module Y",
                    "source_file": "src/y.py",
                    "source_location": "L50-L10",
                }
            ],
        }
        with self.assertRaises(ValueError):
            archify_model.graphify_to_archify(loc_graph, evidence_kind="committed", repository=repo)

    def test_committed_without_repository_raises_value_error(self):
        """Committed evidence_kind without repository raises ValueError."""
        with self.assertRaises(ValueError):
            archify_model.graphify_to_archify(self.sample_undirected_graph, evidence_kind="committed")


class TestGraphCoverage(unittest.TestCase):
    """Test suite for graph_coverage inventory and reporting."""

    def setUp(self):
        self.graph_undirected = {
            "directed": False,
            "nodes": [
                {"id": "node_a"},
                {"id": "node_b"},
                {"id": "node_c"},
            ],
            "links": [
                {"source": "node_a", "target": "node_b", "relation": "depends"},
                {"source": "node_b", "target": "node_c", "relation": "uses"},
            ],
        }

        self.graph_directed = {
            "directed": True,
            "nodes": [
                {"id": "node_a"},
                {"id": "node_b"},
            ],
            "links": [
                {"source": "node_a", "target": "node_b", "relation": "calls"},
            ],
        }

    def test_coverage_counts_and_inventory(self):
        """Verifies total, selected, and excluded counts."""
        cov = archify_model.graph_coverage(self.graph_undirected, selected_ids=["node_a", "node_b"])
        self.assertEqual(cov["total"], 3)
        self.assertEqual(cov["selected"], 2)
        self.assertEqual(cov["excluded"], 1)
        self.assertFalse(cov["directed"])
        self.assertEqual(cov["selected_ids"], ["node_a", "node_b"])
        self.assertEqual(cov["excluded_ids"], ["node_c"])
        self.assertIn("node_c", cov["filter_reasons"])

    def test_coverage_undirected_graph_unproven_relationships(self):
        """Undirected graph relationships are captured in unproven_relationships and unknown."""
        cov = archify_model.graph_coverage(self.graph_undirected, selected_ids=["node_a", "node_b"])
        self.assertEqual(len(cov["unproven_relationships"]), 2)
        self.assertEqual(len(cov["unknown"]), 2)
        self.assertEqual(cov["unproven_relationships"][0]["reason"], "undirected_graph")

    def test_coverage_directed_graph(self):
        """Directed graph reflects directed=True and empty unproven_relationships when all are directed."""
        cov = archify_model.graph_coverage(self.graph_directed, selected_ids=["node_a", "node_b"])
        self.assertTrue(cov["directed"])
        self.assertEqual(cov["unproven_relationships"], [])

    def test_coverage_modules_inventory(self):
        """Verifies modules inventory status reflects 'selected' (unverified) vs 'excluded'."""
        cov = archify_model.graph_coverage(self.graph_undirected, selected_ids=["node_a"])
        modules = {m["id"]: m["status"] for m in cov["modules"]}
        self.assertEqual(modules["node_a"], "selected")
        self.assertEqual(modules["node_b"], "excluded")
        self.assertEqual(modules["node_c"], "excluded")


class TestValidateModel(unittest.TestCase):
    """Test suite for validate_model master envelope validation."""

    def setUp(self):
        self.valid_committed_model = {
            "schema_version": 1,
            "title": "Kiến trúc dự án",
            "evidence_kind": "committed",
            "revision": "a" * 40,
            "repository": {
                "url": "https://example.invalid/team/repo.git",
                "revision": "a" * 40,
                "link_mode": "local-only",
            },
            "source_paths": ["src/main.py", "scripts/app.py"],
            "coverage": {
                "modules": [{"id": "app", "status": "verified"}],
                "unknown": [],
                "excluded": [],
            },
            "views": [
                {
                    "id": "overview",
                    "type": "architecture",
                    "candidate": "overview.json",
                    "summary": "Bản đồ module",
                }
            ],
        }

    def test_valid_committed_model(self):
        """Valid committed model passes validation and is returned unchanged."""
        validated = archify_model.validate_model(self.valid_committed_model)
        self.assertEqual(validated["schema_version"], 1)
        self.assertEqual(validated["title"], "Kiến trúc dự án")

    def test_valid_working_tree_model(self):
        """Valid working-tree model passes validation without requiring repository."""
        model = dict(self.valid_committed_model)
        model["evidence_kind"] = "working-tree"
        del model["repository"]
        model["revision"] = None
        validated = archify_model.validate_model(model)
        self.assertEqual(validated["evidence_kind"], "working-tree")

    def test_valid_planned_model(self):
        """Valid planned model passes validation."""
        model = dict(self.valid_committed_model)
        model["evidence_kind"] = "planned"
        del model["repository"]
        del model["revision"]
        validated = archify_model.validate_model(model)
        self.assertEqual(validated["evidence_kind"], "planned")

    def test_invalid_schema_version(self):
        """schema_version != 1 raises ValueError."""
        model = dict(self.valid_committed_model, schema_version=2)
        with self.assertRaises(ValueError):
            archify_model.validate_model(model)

    def test_missing_or_empty_title(self):
        """Missing or empty title raises ValueError."""
        model = dict(self.valid_committed_model, title="   ")
        with self.assertRaises(ValueError):
            archify_model.validate_model(model)

    def test_invalid_evidence_kind(self):
        """Invalid evidence_kind raises ValueError."""
        model = dict(self.valid_committed_model, evidence_kind="unknown_kind")
        with self.assertRaises(ValueError):
            archify_model.validate_model(model)

    def test_model_with_current_evidence_kind_rejected(self):
        """Model with evidence_kind='current' raises ValueError because current is freshness status."""
        model = dict(self.valid_committed_model, evidence_kind="current")
        with self.assertRaises(ValueError):
            archify_model.validate_model(model)

    def test_committed_missing_revision_or_non_40_hex(self):
        """Committed model with missing or invalid hex revision raises ValueError."""
        model1 = dict(self.valid_committed_model, revision="short")
        with self.assertRaises(ValueError):
            archify_model.validate_model(model1)

        model2 = dict(self.valid_committed_model)
        del model2["revision"]
        with self.assertRaises(ValueError):
            archify_model.validate_model(model2)

    def test_committed_missing_repository(self):
        """Committed model missing repository raises ValueError."""
        model = dict(self.valid_committed_model)
        del model["repository"]
        with self.assertRaises(ValueError):
            archify_model.validate_model(model)

    def test_committed_repository_revision_mismatch_raises_value_error(self):
        """Committed model where repository.revision != revision raises ValueError."""
        model = dict(self.valid_committed_model)
        model["repository"] = dict(model["repository"], revision="b" * 40)
        with self.assertRaises(ValueError):
            archify_model.validate_model(model)

    def test_source_paths_absolute_or_traversal(self):
        """source_paths containing absolute paths or .. traversals raises ValueError."""
        model1 = dict(self.valid_committed_model, source_paths=["/etc/passwd"])
        with self.assertRaises(ValueError):
            archify_model.validate_model(model1)

        model2 = dict(self.valid_committed_model, source_paths=["../outside.py"])
        with self.assertRaises(ValueError):
            archify_model.validate_model(model2)

        model3 = dict(self.valid_committed_model, source_paths=["C:\\Windows\\system32"])
        with self.assertRaises(ValueError):
            archify_model.validate_model(model3)

    def test_empty_views(self):
        """Empty views list raises ValueError."""
        model = dict(self.valid_committed_model, views=[])
        with self.assertRaises(ValueError):
            archify_model.validate_model(model)

    def test_duplicate_view_ids(self):
        """Duplicate view IDs raise ValueError."""
        views = [
            {"id": "overview", "type": "architecture", "candidate": "view1.json"},
            {"id": "overview", "type": "architecture", "candidate": "view2.json"},
        ]
        model = dict(self.valid_committed_model, views=views)
        with self.assertRaises(ValueError):
            archify_model.validate_model(model)

    def test_duplicate_view_candidates(self):
        """Duplicate candidate paths raise ValueError."""
        views = [
            {"id": "overview", "type": "architecture", "candidate": "shared.json"},
            {"id": "details", "type": "workflow", "candidate": "shared.json"},
        ]
        model = dict(self.valid_committed_model, views=views)
        with self.assertRaises(ValueError):
            archify_model.validate_model(model)

    def test_view_candidate_path_traversal_or_absolute(self):
        """Candidate path escaping root raises ValueError."""
        views1 = [{"id": "v1", "type": "architecture", "candidate": "../view.json"}]
        model1 = dict(self.valid_committed_model, views=views1)
        with self.assertRaises(ValueError):
            archify_model.validate_model(model1)

        views2 = [{"id": "v2", "type": "architecture", "candidate": "/root/view.json"}]
        model2 = dict(self.valid_committed_model, views=views2)
        with self.assertRaises(ValueError):
            archify_model.validate_model(model2)

    def test_invalid_view_type(self):
        """Invalid view type raises ValueError."""
        views = [{"id": "v1", "type": "unsupported_diagram", "candidate": "v.json"}]
        model = dict(self.valid_committed_model, views=views)
        with self.assertRaises(ValueError):
            archify_model.validate_model(model)

    def test_view_candidate_non_json(self):
        """Candidate path not ending in .json raises ValueError."""
        views = [{"id": "v1", "type": "architecture", "candidate": "view.xml"}]
        model = dict(self.valid_committed_model, views=views)
        with self.assertRaises(ValueError):
            archify_model.validate_model(model)


class TestMasterFlowContract(unittest.TestCase):
    def setUp(self):
        self.model = {
            "schema_version": 1, "title": "Master", "evidence_kind": "working-tree",
            "views": [
                {"id": "overview", "type": "architecture", "candidate": "overview.json"},
                {"id": "detail", "type": "workflow", "candidate": "detail.json"},
            ],
            "master": {"overview": "overview", "flows": [{
                "id": "flow", "text": "Read source", "target": {"diagram": "detail"},
                "steps": [{"id": "read", "text": "Read file", "sources": [
                    {"path": "src/main.py", "line": 1, "end_line": 2},
                ]}],
            }]},
        }

    def test_valid_master_preserves_native_target(self):
        self.assertIs(archify_model.validate_model(self.model), self.model)
        self.assertEqual(self.model["master"]["flows"][0]["target"], {"diagram": "detail"})

    def test_missing_diagram_target_rejected(self):
        self.model["master"]["flows"][0]["target"]["diagram"] = "missing"
        with self.assertRaisesRegex(ValueError, "target"):
            archify_model.validate_model(self.model)

    def test_master_overview_must_exist(self):
        self.model["master"]["overview"] = "missing"
        with self.assertRaisesRegex(ValueError, "overview"):
            archify_model.validate_model(self.model)

    def test_card_and_step_ids_share_namespace(self):
        for invalid in ("overview", "flow", "read\n", "../read", 3):
            with self.subTest(invalid=invalid):
                self.model["master"]["flows"][0]["steps"][0]["id"] = invalid
                with self.assertRaisesRegex(ValueError, "id"):
                    archify_model.validate_model(self.model)

    def test_step_requires_evidence_or_explicit_unknown(self):
        step = self.model["master"]["flows"][0]["steps"][0]
        del step["sources"]
        with self.assertRaisesRegex(ValueError, "sources|chưa xác minh"):
            archify_model.validate_model(self.model)
        step["detail"] = "chưa xác minh"
        self.assertIs(archify_model.validate_model(self.model), self.model)

    def test_invalid_evidence_rejected(self):
        for source in ({"path": "../secret", "line": 1},
                       {"path": "C:/secret", "line": 1},
                       {"path": "src/main.py", "line": 0},
                       {"path": "src/main.py", "line": True},
                       {"path": "src/main.py", "line": 3, "end_line": 2},
                       {"path": "src/main.py", "lines": [1, 2]},
                       "src/main.py"):
            with self.subTest(source=source):
                self.model["master"]["flows"][0]["steps"][0]["sources"] = [source]
                with self.assertRaisesRegex(ValueError, "source"):
                    archify_model.validate_model(self.model)

    def test_unverified_flow_has_no_click_target_or_steps(self):
        flow = self.model["master"]["flows"][0]
        del flow["target"]
        with self.assertRaises(ValueError):
            archify_model.validate_model(self.model)
        del flow["steps"]
        flow["detail"] = "chưa xác minh"
        self.assertIs(archify_model.validate_model(self.model), self.model)

    def test_target_must_be_diagram_only_and_not_overview(self):
        for target in ({"diagram": "overview"}, {"diagram": "detail", "node": "fake"},
                       {"diagram": "detail", "candidate": "other.json"}, None, "detail"):
            with self.subTest(target=target):
                self.model["master"]["flows"][0]["target"] = target
                with self.assertRaisesRegex(ValueError, "target"):
                    archify_model.validate_model(self.model)

    def test_docs_only_master_has_no_invented_flows(self):
        self.model["master"]["flows"] = []
        self.assertIs(archify_model.validate_model(self.model), self.model)

    def test_legacy_six_views_unchanged(self):
        del self.model["master"]
        self.model["views"] = [
            {"id": kind, "type": kind, "candidate": f"{kind}.json"}
            for kind in ("architecture", "workflow", "sequence", "dataflow", "lifecycle", "erd")
        ]
        self.assertIs(archify_model.validate_model(self.model), self.model)
        self.assertEqual(len(self.model["views"]), 6)

    def test_malformed_master_rejected(self):
        for master in (None, [], {}, {"overview": "overview"},
                       {"overview": [], "flows": []},
                       {"overview": "overview", "flows": None},
                       {"overview": "overview", "flows": [None]},
                       {"overview": "overview", "flows": [], "typo": True}):
            with self.subTest(master=master):
                model = dict(self.model, master=master)
                with self.assertRaises(ValueError):
                    archify_model.validate_model(model)

    def test_malformed_flow_and_step_rejected(self):
        for location, key, value in (
            ("flow", "id", "bad/id"), ("flow", "text", " "),
            ("flow", "detail", []), ("flow", "target", {"diagram": []}),
            ("flow", "steps", []), ("flow", "steps", {}),
            ("step", "text", None), ("step", "sources", {}),
            ("step", "sources", []), ("step", "typo", True),
        ):
            with self.subTest(location=location, key=key, value=value):
                model = json.loads(json.dumps(self.model))
                flow = model["master"]["flows"][0]
                item = flow if location == "flow" else flow["steps"][0]
                item[key] = value
                with self.assertRaises(ValueError):
                    archify_model.validate_model(model)

    def test_master_view_ids_reject_trailing_newline(self):
        self.model["views"][0]["id"] = "overview\n"
        self.model["master"]["overview"] = "overview\n"
        with self.assertRaisesRegex(ValueError, "id"):
            archify_model.validate_model(self.model)


class TestRealArchifySchemaValidation(unittest.TestCase):
    """Validation test using real local Archify validate CLI."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir, True)

        # Locate archify binary
        archify_bin = Path(r"C:\Users\admin\Documents\archify\archify\bin\archify.mjs")
        if not archify_bin.is_file():
            self.skipTest(f"Archify CLI not found at {archify_bin}")
        self.archify_bin = archify_bin

        if not shutil.which("node"):
            self.skipTest("Node.js is not available on PATH")

    def test_archify_real_validate_undirected_architecture(self):
        """Verifies graphify_to_archify output passes real archify validate CLI."""
        graph = {
            "directed": False,
            "nodes": [
                {"id": "auth_service", "type": "backend", "label": "Auth Service"},
                {"id": "order_service", "type": "backend", "label": "Order Service"},
                {"id": "database", "type": "database", "label": "Postgres Database"},
            ],
            "links": [
                {"source": "auth_service", "target": "order_service", "relation": "authenticates"},
                {"source": "order_service", "target": "database", "relation": "persists"},
            ],
        }
        ir = archify_model.graphify_to_archify(graph)

        cand_file = Path(self.temp_dir) / "candidate.architecture.json"
        cand_file.write_text(json.dumps(ir, indent=2), encoding="utf-8")

        env = os.environ.copy()
        env["ARCHIFY_UPDATE_CHECK_DISABLED"] = "1"

        cmd = [
            "node",
            str(self.archify_bin),
            "validate",
            "architecture",
            str(cand_file),
            "--json",
        ]
        proc = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, f"archify validate failed:\nStdout: {proc.stdout}\nStderr: {proc.stderr}")

        receipt = json.loads(proc.stdout)
        self.assertTrue(receipt.get("ok"), f"Receipt ok was not True: {receipt}")

    def test_archify_real_validate_directed_architecture(self):
        """Verifies directed graph output with connections passes real archify validate CLI."""
        graph = {
            "directed": True,
            "nodes": [
                {"id": "gateway", "type": "backend", "label": "API Gateway"},
                {"id": "worker", "type": "backend", "label": "Background Worker"},
            ],
            "links": [
                {"source": "gateway", "target": "worker", "relation": "dispatches"},
            ],
        }
        ir = archify_model.graphify_to_archify(graph)

        cand_file = Path(self.temp_dir) / "directed.architecture.json"
        cand_file.write_text(json.dumps(ir, indent=2), encoding="utf-8")

        env = os.environ.copy()
        env["ARCHIFY_UPDATE_CHECK_DISABLED"] = "1"

        cmd = [
            "node",
            str(self.archify_bin),
            "validate",
            "architecture",
            str(cand_file),
            "--json",
        ]
        proc = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, f"archify validate failed:\nStdout: {proc.stdout}\nStderr: {proc.stderr}")

        receipt = json.loads(proc.stdout)
        self.assertTrue(receipt.get("ok"), f"Receipt ok was not True: {receipt}")


if __name__ == "__main__":
    unittest.main()
