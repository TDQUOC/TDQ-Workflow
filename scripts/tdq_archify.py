#!/usr/bin/env python3
"""TDQ Archify Adapter Module.

Provides core functions for integrating Archify engine into TDQ-Workflow:
- find_archify_root: locates the local Archify installation
- check_environment: pre-flight validation of Node.js (>= 18) and Archify
- build_finalize_command: prepares arguments for archify finalize CLI
- run_finalize / execute_finalize: compiles candidate JSON to standalone HTML
- atomic_delivery: safe atomic file writes
- open_artifact: opens generated diagrams in default browser
- graphify_to_archify: converts Graphify graph.json AST data to Archify JSON-IR
- test_bridge: self-tests graphify-to-archify conversion logic
- sync_master: synchronizes codebase master architecture diagram

Strictly stdlib-only.
"""
import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple, Optional, Union


class FinalizeResult(NamedTuple):
    """Result returned by run_finalize."""

    status: bool
    receipt: dict

    def get(self, key, default=None):
        if key == "status":
            return self.status
        if key == "receipt":
            return self.receipt
        return self.receipt.get(key, default)

    def __getitem__(self, item):
        if item == 0:
            return self.status
        if item == 1:
            return self.receipt
        if item == "status":
            return self.status
        if item == "receipt":
            return self.receipt
        return self.receipt[item]


def find_archify_root() -> Optional[str]:
    """Find Archify root directory.

    Search priority:
    1. ARCHIFY_ROOT environment variable
    2. C:\\Users\\admin\\Documents\\archify (or ~/Documents/archify)
    3. Sibling directory ../archify relative to repo root / worktrees
    4. Searches for archify/bin/archify.mjs or bin/archify.mjs
    """
    candidates = []

    env_root = os.environ.get("ARCHIFY_ROOT")
    if env_root:
        candidates.append(Path(env_root))

    # Windows user path & home
    candidates.append(Path(r"C:\Users\admin\Documents\archify"))
    try:
        candidates.append(Path.home() / "Documents" / "archify")
    except Exception:
        pass

    # Sibling relative to this file
    current_file = Path(__file__).resolve()
    repo_root = current_file.parent.parent
    candidates.append(repo_root.parent / "archify")
    # Worktree nested check
    if len(current_file.parents) >= 3:
        candidates.append(current_file.parents[2] / "archify")
    if len(current_file.parents) >= 4:
        candidates.append(current_file.parents[3] / "archify")
    if len(current_file.parents) >= 5:
        candidates.append(current_file.parents[4] / "archify")

    # Current working dir sibling
    try:
        candidates.append(Path.cwd().parent / "archify")
    except Exception:
        pass

    seen = set()
    for cand in candidates:
        try:
            resolved = cand.resolve()
        except Exception:
            resolved = cand

        resolved_str = str(resolved)
        if resolved_str in seen:
            continue
        seen.add(resolved_str)

        if not cand.exists() or not cand.is_dir():
            continue

        # Check for archify/bin/archify.mjs or bin/archify.mjs
        if (cand / "archify" / "bin" / "archify.mjs").is_file():
            return str(cand)
        if (cand / "bin" / "archify.mjs").is_file():
            return str(cand)

    return None


def get_archify_bin(archify_root: Optional[str] = None) -> Optional[Path]:
    """Resolve the archify.mjs executable entry point."""
    root_str = archify_root or find_archify_root()
    if not root_str:
        return None

    root = Path(root_str)
    # Check directly under bin/
    direct_bin = root / "bin" / "archify.mjs"
    if direct_bin.is_file():
        return direct_bin

    # Check under archify/bin/
    nested_bin = root / "archify" / "bin" / "archify.mjs"
    if nested_bin.is_file():
        return nested_bin

    # If root itself points to archify.mjs
    if root.name == "archify.mjs" and root.is_file():
        return root

    return None


def check_environment() -> dict:
    """Pre-flight check for Node.js (>= 18) and Archify installation."""
    node_path = shutil.which("node")
    node_ok = False
    node_version = ""

    if node_path:
        try:
            proc = subprocess.run(
                [node_path, "-v"],
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
            )
            raw_v = proc.stdout.strip()
            node_version = raw_v
            # Extract major version number (e.g. v24.19.0 -> 24)
            match = re.search(r"v?(\d+)", raw_v)
            if match:
                major = int(match.group(1))
                node_ok = major >= 18
        except Exception:
            node_ok = False

    archify_root = find_archify_root()
    archify_bin = get_archify_bin(archify_root) if archify_root else None
    archify_ok = bool(archify_root and archify_bin)

    ready = bool(node_ok and archify_ok)

    return {
        "node_ok": node_ok,
        "node_version": node_version,
        "archify_root": archify_root or "",
        "ready": ready,
    }


def build_finalize_command(
    diagram_type: str,
    candidate_path: Union[str, Path],
    output_path: Union[str, Path],
    quality: str = "showcase",
    repo_root: Optional[Union[str, Path]] = None,
    archify_root: Optional[Union[str, Path]] = None,
) -> list[str]:
    """Build the CLI command arguments to execute archify finalize."""
    node_bin = shutil.which("node") or "node"
    bin_script = get_archify_bin(str(archify_root) if archify_root else None)
    if not bin_script:
        raise FileNotFoundError("Archify binary script (archify.mjs) not found")

    cmd = [
        node_bin,
        str(bin_script),
        "finalize",
        diagram_type,
        str(candidate_path),
        str(output_path),
        "--quality",
        quality,
        "--json",
    ]
    if repo_root:
        cmd.extend(["--repo-root", str(repo_root)])
    return cmd


def atomic_delivery(target_path: Union[str, Path], content: Union[str, bytes]) -> Path:
    """Write content atomically using a temporary file and rename."""
    target = Path(target_path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    temp_path = target.with_suffix(f"{target.suffix}.tmp.{os.getpid()}")
    try:
        if isinstance(content, str):
            temp_path.write_text(content, encoding="utf-8")
        else:
            temp_path.write_bytes(content)
        temp_path.replace(target)
        return target
    except Exception:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                pass
        raise


def run_finalize(
    diagram_type: str,
    candidate_path: Union[str, Path],
    output_path: Union[str, Path],
    quality: str = "showcase",
    repo_root: Optional[Union[str, Path]] = None,
    archify_root: Optional[Union[str, Path]] = None,
) -> FinalizeResult:
    """Run archify finalize and return status and receipt JSON."""
    cand = Path(candidate_path).resolve()
    if not cand.is_file():
        return FinalizeResult(
            status=False,
            receipt={"ok": False, "error": f"Candidate file not found: {cand}"},
        )

    out = Path(output_path).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    try:
        cmd = build_finalize_command(
            diagram_type=diagram_type,
            candidate_path=cand,
            output_path=out,
            quality=quality,
            repo_root=repo_root,
            archify_root=archify_root,
        )
    except Exception as e:
        return FinalizeResult(
            status=False,
            receipt={"ok": False, "error": str(e)},
        )

    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)

    receipt = {}
    if proc.stdout:
        raw = proc.stdout.strip()
        try:
            receipt = json.loads(raw)
        except json.JSONDecodeError:
            start = raw.find("{")
            end = raw.rfind("}")
            if start != -1 and end != -1:
                try:
                    receipt = json.loads(raw[start : end + 1])
                except Exception:
                    receipt = {"raw_output": raw}
            else:
                receipt = {"raw_output": raw}

    # Evaluate execution status:
    # Exit 0 or receipt.ok == True is success.
    # If out exists and deliver gate passed, the HTML artifact is successfully delivered.
    delivered = out.is_file() and receipt.get("gates", {}).get("deliver") == "pass"
    if proc.returncode == 0 or receipt.get("ok") is True:
        status = True
    elif delivered:
        status = True
    else:
        status = False

    return FinalizeResult(status=status, receipt=receipt)


execute_finalize = run_finalize


def open_artifact(file_path: Union[str, Path]) -> bool:
    """Safely open an artifact in the default browser."""
    path_obj = Path(file_path).resolve()
    if not path_obj.exists():
        sys.stderr.write(f"Error: File not found: {path_obj}\n")
        return False

    system = platform.system()
    try:
        if system == "Windows":
            subprocess.run(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-NonInteractive",
                    "-Command",
                    f'Start-Process "{path_obj}"',
                ],
                check=False,
            )
            return True
        elif system == "Darwin":
            subprocess.run(["open", str(path_obj)], check=False)
            return True
        else:
            subprocess.run(["xdg-open", str(path_obj)], check=False)
            return True
    except Exception as e:
        sys.stderr.write(f"Failed to open artifact: {e}\n")
        return False


def graphify_to_archify(
    graph_json_path: Union[str, Path, dict],
    focus_community: Optional[Union[int, str]] = None,
    max_nodes: int = 25,
) -> dict:
    """Convert Graphify graph.json AST/semantic data to Archify JSON-IR format.

    - Extracts nodes and links
    - Filters by community if focus_community is specified
    - Filters by top-degree nodes if count exceeds max_nodes
    - Generates valid Archify JSON-IR (schema_version 1, architecture diagram_type,
      components with id, label, type, sources, and connections with from, to, label).
    """
    if isinstance(graph_json_path, dict):
        data = graph_json_path
    else:
        path_obj = Path(graph_json_path)
        if not path_obj.is_file():
            raise FileNotFoundError(f"Graph file not found: {path_obj}")
        with open(path_obj, "r", encoding="utf-8") as f:
            data = json.load(f)

    raw_nodes = list(data.get("nodes", []))
    raw_links = list(data.get("links") or data.get("edges") or [])

    # Filter by focus_community if requested
    if focus_community is not None:
        comm_str = str(focus_community)
        raw_nodes = [
            n for n in raw_nodes if str(n.get("community", "")) == comm_str
        ]

    # Calculate degrees for each node
    valid_ids = {str(n.get("id")) for n in raw_nodes if n.get("id")}
    degrees: dict[str, int] = {nid: 0 for nid in valid_ids}

    for link in raw_links:
        src = str(link.get("source") or link.get("from") or "")
        tgt = str(link.get("target") or link.get("to") or "")
        if src in degrees:
            degrees[src] += 1
        if tgt in degrees:
            degrees[tgt] += 1

    # Filter top-degree nodes if exceeding max_nodes
    if len(raw_nodes) > max_nodes:
        raw_nodes.sort(
            key=lambda n: (
                degrees.get(str(n.get("id")), 0),
                str(n.get("label") or n.get("id") or ""),
            ),
            reverse=True,
        )
        raw_nodes = raw_nodes[:max_nodes]

    selected_ids = {str(n.get("id")) for n in raw_nodes if n.get("id")}

    valid_types = {
        "frontend",
        "backend",
        "database",
        "cloud",
        "security",
        "messagebus",
        "external",
    }

    components = []
    for node in raw_nodes:
        nid = str(node.get("id") or "")
        label = str(node.get("label") or nid)

        # Detect component type
        comp_type = "backend"
        declared_type = str(node.get("type") or "").lower()
        if declared_type in valid_types:
            comp_type = declared_type
        elif node.get("external") or node.get("file_type") == "concept":
            comp_type = "external"
        else:
            haystack = f"{nid} {label} {node.get('source_file', '')}".lower()
            if any(k in haystack for k in ("auth", "security", "gate", "permission", "jwt", "crypto")):
                comp_type = "security"
            elif any(k in haystack for k in ("db", "database", "sql", "cache", "redis", "postgres", "store", "model", "repo")):
                comp_type = "database"
            elif any(k in haystack for k in ("queue", "bus", "message", "event", "stream", "kafka", "mq", "pubsub")):
                comp_type = "messagebus"
            elif any(k in haystack for k in ("cloud", "aws", "s3", "gcp", "azure", "cdn", "bucket")):
                comp_type = "cloud"
            elif any(k in haystack for k in ("ui", "frontend", "view", "component", "page", "react", "html", "css", "client")):
                comp_type = "frontend"

        comp: dict[str, Union[str, list]] = {
            "id": nid,
            "type": comp_type,
            "label": label,
        }

        # Handle source file and location
        source_file = node.get("source_file")
        if source_file:
            source_entry: dict[str, Union[str, int]] = {"path": str(source_file)}
            loc_str = str(node.get("source_location") or "")
            line_numbers = re.findall(r"\d+", loc_str)
            if len(line_numbers) == 1:
                line_val = int(line_numbers[0])
                source_entry["startLine"] = line_val
                source_entry["endLine"] = line_val
            elif len(line_numbers) >= 2:
                source_entry["startLine"] = int(line_numbers[0])
                source_entry["endLine"] = int(line_numbers[1])

            comp["sources"] = [source_entry]

        components.append(comp)

    # Connections
    connections = []
    seen_connections = set()
    conn_counter = 1

    for link in raw_links:
        src = str(link.get("source") or link.get("from") or "")
        tgt = str(link.get("target") or link.get("to") or "")
        if src in selected_ids and tgt in selected_ids and src != tgt:
            conn_pair = (src, tgt)
            if conn_pair in seen_connections:
                continue
            seen_connections.add(conn_pair)
            label = str(link.get("relation") or link.get("label") or "depends")
            connections.append({
                "id": f"conn-{conn_counter}",
                "from": src,
                "to": tgt,
                "label": label,
            })
            conn_counter += 1

    title = (
        f"Community {focus_community} Architecture"
        if focus_community is not None
        else "Codebase Architecture"
    )

    return {
        "schema_version": 1,
        "diagram_type": "architecture",
        "meta": {
            "title": title,
            "output": "master.architecture.html",
        },
        "components": components,
        "connections": connections,
    }


def test_bridge() -> bool:
    """Self-test graphify_to_archify conversion with mock in-memory graph data."""
    mock_graph = {
        "nodes": [
            {
                "id": "app_gateway",
                "label": "App Gateway",
                "community": 1,
                "source_file": "src/gateway.py",
                "source_location": "L10-L50",
                "type": "security",
            },
            {
                "id": "order_service",
                "label": "Order Service",
                "community": 1,
                "source_file": "src/order.py",
                "source_location": "L25",
                "type": "backend",
            },
            {
                "id": "order_db",
                "label": "Order Database",
                "community": 1,
                "source_file": "src/db.py",
                "source_location": "L100",
                "type": "database",
            },
            {
                "id": "notification_queue",
                "label": "Notification Queue",
                "community": 2,
                "source_file": "src/queue.py",
                "source_location": "L15",
                "type": "messagebus",
            },
        ],
        "links": [
            {"source": "app_gateway", "target": "order_service", "relation": "routes"},
            {"source": "order_service", "target": "order_db", "relation": "queries"},
            {"source": "order_service", "target": "notification_queue", "relation": "publishes"},
        ],
    }

    # 1. Full conversion test
    ir = graphify_to_archify(mock_graph)
    assert ir["schema_version"] == 1, "schema_version must be 1"
    assert ir["diagram_type"] == "architecture", "diagram_type must be architecture"
    assert len(ir["components"]) == 4, f"expected 4 components, got {len(ir['components'])}"
    assert len(ir["connections"]) == 3, f"expected 3 connections, got {len(ir['connections'])}"

    gw = next(c for c in ir["components"] if c["id"] == "app_gateway")
    assert gw["type"] == "security", f"expected security, got {gw['type']}"
    assert gw["label"] == "App Gateway"
    assert len(gw.get("sources", [])) == 1
    assert gw["sources"][0]["path"] == "src/gateway.py"
    assert gw["sources"][0]["startLine"] == 10
    assert gw["sources"][0]["endLine"] == 50

    ord_svc = next(c for c in ir["components"] if c["id"] == "order_service")
    assert ord_svc["sources"][0]["startLine"] == 25
    assert ord_svc["sources"][0]["endLine"] == 25

    conn0 = next(c for c in ir["connections"] if c["from"] == "app_gateway" and c["to"] == "order_service")
    assert conn0["label"] == "routes"

    # 2. Community filter test
    ir_comm1 = graphify_to_archify(mock_graph, focus_community=1)
    assert len(ir_comm1["components"]) == 3, "expected 3 components for community 1"
    assert len(ir_comm1["connections"]) == 2, "expected 2 connections for community 1"
    assert not any(c["id"] == "notification_queue" for c in ir_comm1["components"])

    # 3. Max nodes filter test
    ir_max2 = graphify_to_archify(mock_graph, max_nodes=2)
    assert len(ir_max2["components"]) == 2, "expected 2 components for max_nodes=2"
    assert any(c["id"] == "order_service" for c in ir_max2["components"])

    print("BRIDGE OK")
    return True


def sync_master(
    graph_path: Optional[Union[str, Path]] = None,
    out_path: Optional[Union[str, Path]] = None,
    max_nodes: int = 25,
) -> bool:
    """Sync graphify-out/graph.json to docs/architecture/master.architecture.json."""
    if graph_path:
        target_graph = Path(graph_path)
    else:
        current_file = Path(__file__).resolve()
        candidates = [
            Path("graphify-out/graph.json"),
            current_file.parent.parent / "graphify-out" / "graph.json",
        ]
        target_graph = None
        for cand in candidates:
            if cand.is_file():
                target_graph = cand
                break

    if not target_graph or not target_graph.is_file():
        sys.stderr.write(f"Warning: Graph file not found: {target_graph or 'graphify-out/graph.json'}, skipping sync.\n")
        return False

    if out_path:
        target_out = Path(out_path)
    else:
        current_file = Path(__file__).resolve()
        repo_root = current_file.parent.parent
        target_out = repo_root / "docs" / "architecture" / "master.architecture.json"

    ir = graphify_to_archify(target_graph, max_nodes=max_nodes)
    content = json.dumps(ir, indent=2, ensure_ascii=False)
    atomic_delivery(target_out, content)
    print(f"Master architecture JSON synchronized: {target_out}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="TDQ Archify Adapter CLI — orchestrate diagram generation and environment pre-flight."
    )
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # check
    subparsers.add_parser("check", help="Check Node.js and Archify environment")

    # render
    render_parser = subparsers.add_parser(
        "render", help="Render diagram to standalone HTML via finalize"
    )
    render_parser.add_argument(
        "--type",
        required=True,
        help="Diagram type (workflow, architecture, sequence, ...)",
    )
    render_parser.add_argument(
        "--candidate", required=True, help="Path to input candidate JSON"
    )
    render_parser.add_argument(
        "--out", required=True, help="Path to output HTML artifact"
    )
    render_parser.add_argument(
        "--quality",
        default="showcase",
        choices=["standard", "showcase"],
        help="Rendering quality",
    )
    render_parser.add_argument(
        "--repo-root", default=None, help="Root path of target repository"
    )

    # open
    open_parser = subparsers.add_parser(
        "open", help="Open artifact safely in default browser"
    )
    open_parser.add_argument("file_path", help="Path to file to open")

    # bridge
    bridge_parser = subparsers.add_parser(
        "bridge", help="Convert Graphify graph.json to Archify JSON-IR"
    )
    bridge_parser.add_argument(
        "--graph", required=True, help="Path to input graph.json"
    )
    bridge_parser.add_argument(
        "--out", required=True, help="Path to output architecture JSON-IR"
    )
    bridge_parser.add_argument(
        "--community", default=None, help="Filter by community id"
    )
    bridge_parser.add_argument(
        "--max-nodes", type=int, default=25, help="Maximum number of nodes (default: 25)"
    )

    # test-bridge
    subparsers.add_parser(
        "test-bridge", help="Self-test graphify-to-archify conversion logic"
    )

    # sync-master
    sync_parser = subparsers.add_parser(
        "sync-master", help="Sync graphify-out/graph.json to master architecture JSON"
    )
    sync_parser.add_argument(
        "--graph", default=None, help="Path to input graph.json (default: auto-detect)"
    )
    sync_parser.add_argument(
        "--out", default=None, help="Path to output JSON (default: docs/architecture/master.architecture.json)"
    )
    sync_parser.add_argument(
        "--max-nodes", type=int, default=25, help="Maximum number of nodes (default: 25)"
    )

    args = parser.parse_args()

    if args.command == "check":
        res = check_environment()
        print(json.dumps(res, indent=2))
        return 0 if res.get("ready") else 1

    elif args.command == "render":
        result = run_finalize(
            diagram_type=args.type,
            candidate_path=args.candidate,
            output_path=args.out,
            quality=args.quality,
            repo_root=args.repo_root,
        )
        print(json.dumps(result.receipt, indent=2))
        return 0 if result.status else 1

    elif args.command == "open":
        ok = open_artifact(args.file_path)
        return 0 if ok else 1

    elif args.command == "bridge":
        ir = graphify_to_archify(
            graph_json_path=args.graph,
            focus_community=args.community,
            max_nodes=args.max_nodes,
        )
        content = json.dumps(ir, indent=2, ensure_ascii=False)
        atomic_delivery(args.out, content)
        print(f"Archify JSON-IR generated: {args.out}")
        return 0

    elif args.command == "test-bridge":
        try:
            ok = test_bridge()
            return 0 if ok else 1
        except Exception as e:
            sys.stderr.write(f"Test failed: {e}\n")
            return 1

    elif args.command == "sync-master":
        ok = sync_master(
            graph_path=args.graph,
            out_path=args.out,
            max_nodes=args.max_nodes,
        )
        return 0 if ok else 1

    else:
        parser.print_help()
        return 2


if __name__ == "__main__":
    sys.exit(main())
