"""Archify model and evidence module.

Provides:
- graphify_to_archify: Convert Graphify graph to pure Archify architecture IR.
- graph_coverage: Compute coverage inventory, directed flag, filter reasons, and unproven relationships.
- validate_model: Validate Master model envelope per TDQ-Archify contract.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable, Optional, Union

VALID_EVIDENCE_KINDS = frozenset({"committed", "working-tree", "planned", "partial"})

VALID_COMPONENT_TYPES = frozenset({
    "frontend",
    "backend",
    "database",
    "cloud",
    "security",
    "messagebus",
    "external",
})

VALID_VIEW_TYPES = frozenset({
    "architecture",
    "workflow",
    "sequence",
    "dataflow",
    "lifecycle",
    "erd",
    "tree",
    "class",
    "timeline",
    "waterfall",
    "explainer",
})


# ---------------------------------------------------------------------------
# Path & ID utilities
# ---------------------------------------------------------------------------

def _is_safe_relative_path(path_str: str) -> bool:
    """Check if a path is safe and relative (no absolute paths, drive letters, or .. traversal)."""
    if not path_str or not isinstance(path_str, str):
        return False
    clean = path_str.strip()
    if not clean or "\0" in clean or ":" in clean:
        return False
    norm = clean.replace("\\", "/")
    if norm.startswith("/"):
        return False
    return ".." not in norm.split("/")


def _clean_id_string(raw_id: str, fallback_prefix: str, count: int) -> str:
    """Clean raw ID to match ^[a-zA-Z][a-zA-Z0-9_-]*$."""
    cleaned = re.sub(r"[^a-zA-Z0-9_-]", "_", str(raw_id).strip())
    if not cleaned:
        return f"{fallback_prefix}_{count}"
    if not re.match(r"^[a-zA-Z]", cleaned):
        return f"n_{cleaned}"
    return cleaned


def _disambiguate_id(candidate: str, existing_ids: set[str]) -> str:
    """Ensure candidate ID does not collide with existing IDs."""
    if candidate not in existing_ids:
        return candidate
    suffix = 2
    while f"{candidate}_{suffix}" in existing_ids:
        suffix += 1
    return f"{candidate}_{suffix}"


def _sanitize_id(raw_id: str, existing_ids: set[str], fallback_prefix: str = "node") -> str:
    """Sanitize raw id to match Archify id pattern ^[a-zA-Z][a-zA-Z0-9_-]*$ with stable deduplication."""
    cleaned = _clean_id_string(raw_id, fallback_prefix, len(existing_ids) + 1)
    return _disambiguate_id(cleaned, existing_ids)


# ---------------------------------------------------------------------------
# Source reference utilities
# ---------------------------------------------------------------------------

def _parse_line_numbers(loc_str: str) -> tuple[Optional[int], Optional[int]]:
    """Parse line and end_line from source_location string; rejects reverse ranges."""
    nums = [int(n) for n in re.findall(r"\d+", str(loc_str)) if int(n) >= 1]
    if not nums:
        return None, None
    if len(nums) == 1:
        return nums[0], nums[0]
    if nums[1] < nums[0]:
        raise ValueError(
            f"Invalid reverse line range in location '{loc_str}': end_line ({nums[1]}) < line ({nums[0]})"
        )
    return nums[0], nums[1]


def _extract_source_lines(node: dict[str, Any]) -> tuple[Optional[int], Optional[int]]:
    """Extract line and end_line from node or location, rejecting invalid or reverse ranges."""
    line_val = node.get("line")
    end_line_val = node.get("end_line")
    if line_val is None and node.get("source_location"):
        line_val, end_line_val = _parse_line_numbers(str(node["source_location"]))

    if line_val is None:
        return None, None

    line_int = int(line_val)
    if line_int < 1:
        raise ValueError(f"line must be >= 1, got {line_int}")

    if end_line_val is None:
        return line_int, None

    end_int = int(end_line_val)
    if end_int < 1:
        raise ValueError(f"end_line must be >= 1, got {end_int}")
    if end_int < line_int:
        raise ValueError(f"end_line ({end_int}) cannot be less than line ({line_int})")
    return line_int, end_int


def _build_source_reference(node: dict[str, Any], raw_id: str) -> Optional[dict[str, Any]]:
    """Build a valid source reference dictionary or return None."""
    src_file = node.get("source_file") or node.get("path") or node.get("file")
    if not src_file:
        return None
    src_path = str(src_file).replace("\\", "/").strip()
    if not _is_safe_relative_path(src_path):
        raise ValueError(f"Invalid source path in node '{raw_id}': {src_path}")

    entry: dict[str, Any] = {"path": src_path}
    line, end_line = _extract_source_lines(node)
    if line is not None:
        entry["line"] = line
        if end_line is not None:
            entry["end_line"] = end_line
    if node.get("source_label"):
        entry["label"] = str(node["source_label"])[:48]
    return entry


# ---------------------------------------------------------------------------
# Repository validation
# ---------------------------------------------------------------------------

def _check_repo_url_and_rev(repository: dict[str, Any]) -> None:
    """Validate url and 40-hex revision fields."""
    url = repository.get("url")
    if not url or not isinstance(url, str):
        raise ValueError("repository.url must be a non-empty string")
    rev = repository.get("revision")
    if not rev or not isinstance(rev, str) or not re.match(r"^[a-fA-F0-9]{40}$", rev):
        raise ValueError(f"repository.revision must be a 40-character hex SHA, got '{rev}'")


def _check_repo_options(repository: dict[str, Any]) -> None:
    """Validate optional link_mode and provider fields."""
    link_mode = repository.get("link_mode")
    if link_mode is not None and link_mode not in ("web", "local-only"):
        raise ValueError(f"repository.link_mode must be 'web' or 'local-only', got '{link_mode}'")
    provider = repository.get("provider")
    if provider is not None and provider not in ("github", "gitee", "gitlab"):
        raise ValueError(f"repository.provider must be github/gitee/gitlab, got '{provider}'")


def _validate_repository(repository: Any) -> None:
    """Validate repository dictionary against Archify common schema."""
    if not isinstance(repository, dict):
        raise ValueError("repository must be a dictionary")
    _check_repo_url_and_rev(repository)
    _check_repo_options(repository)


def _validate_evidence_and_repo(evidence_kind: str, repository: Optional[dict]) -> None:
    """Validate evidence_kind and corresponding repository requirements."""
    if evidence_kind not in VALID_EVIDENCE_KINDS:
        raise ValueError(
            f"Invalid evidence_kind '{evidence_kind}'. Must be one of {sorted(VALID_EVIDENCE_KINDS)}"
        )
    if evidence_kind == "committed":
        if repository is None:
            raise ValueError(f"repository is required when evidence_kind is '{evidence_kind}'")
        _validate_repository(repository)
    elif repository is not None:
        _validate_repository(repository)


# ---------------------------------------------------------------------------
# Graph loading & filtering helpers
# ---------------------------------------------------------------------------

def _load_graph_data(graph_json_path: Union[str, Path, dict]) -> dict[str, Any]:
    """Load graph data from dict or file path."""
    if isinstance(graph_json_path, dict):
        return graph_json_path
    path_obj = Path(graph_json_path)
    if not path_obj.is_file():
        raise FileNotFoundError(f"Graph file not found: {path_obj}")
    with open(path_obj, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in graph file {path_obj}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Graph data must be a JSON object (dict)")
    return data


def _extract_raw_nodes(data: dict[str, Any], selected_ids: Optional[Iterable[str]]) -> list[dict[str, Any]]:
    """Extract and validate raw nodes list from graph, checking for duplicate raw IDs."""
    raw_nodes = list(data.get("nodes", []))
    if not raw_nodes:
        raise ValueError("Graph contains no nodes")

    if selected_ids is not None:
        selected_set = {str(sid) for sid in selected_ids}
        raw_nodes = [n for n in raw_nodes if str(n.get("id")) in selected_set]
        if not raw_nodes:
            raise ValueError("No nodes match the specified selected_ids")

    seen_raw_ids: set[str] = set()
    for n in raw_nodes:
        nid = str(n.get("id") or "")
        if nid:
            if nid in seen_raw_ids:
                raise ValueError(f"Duplicate node id found in graph: '{nid}'")
            seen_raw_ids.add(nid)

    return raw_nodes


def _filter_nodes_by_community(
    nodes: list[dict[str, Any]],
    community: Optional[Union[int, str]],
) -> list[dict[str, Any]]:
    """Filter nodes by focus_community if provided."""
    if community is None:
        return nodes
    comm_str = str(community)
    filtered = [n for n in nodes if str(n.get("community", "")) == comm_str]
    if not filtered:
        raise ValueError(f"No nodes found for focus_community {community}")
    return filtered


def _calculate_node_degrees(nodes: list[dict[str, Any]], links: list[dict[str, Any]]) -> dict[str, int]:
    """Calculate degree for each node in nodes list."""
    degrees: dict[str, int] = {str(n.get("id")): 0 for n in nodes if n.get("id")}
    for link in links:
        s = str(link.get("source") or link.get("from") or "")
        t = str(link.get("target") or link.get("to") or "")
        if s in degrees:
            degrees[s] += 1
        if t in degrees:
            degrees[t] += 1
    return degrees


def _filter_nodes_by_max(
    nodes: list[dict[str, Any]],
    links: list[dict[str, Any]],
    max_nodes: Optional[int],
) -> list[dict[str, Any]]:
    """Filter top-degree nodes if max_nodes is specified."""
    if max_nodes is None or len(nodes) <= max_nodes:
        return nodes
    if not isinstance(max_nodes, int) or max_nodes <= 0:
        raise ValueError("max_nodes must be a positive integer")
    degrees = _calculate_node_degrees(nodes, links)
    sorted_nodes = sorted(
        nodes,
        key=lambda n: (-degrees.get(str(n.get("id")), 0), str(n.get("id") or "")),
    )
    return sorted_nodes[:max_nodes]


# ---------------------------------------------------------------------------
# Component & Grid Layout construction
# ---------------------------------------------------------------------------

def _determine_component_type(node: dict[str, Any]) -> tuple[str, bool]:
    """Determine component type and whether it was defaulted."""
    raw_type = str(node.get("type") or "").strip().lower()
    if raw_type in VALID_COMPONENT_TYPES:
        return raw_type, False
    if node.get("external") is True or node.get("file_type") == "concept":
        return "external", False
    return "backend", True


def _build_component(
    node: dict[str, Any],
    cid: str,
    evidence_kind: str,
    has_repo: bool,
) -> dict[str, Any]:
    """Build a single component dictionary."""
    comp_type, defaulted = _determine_component_type(node)
    raw_id = str(node.get("id") or cid)
    label = str(node.get("label") or raw_id)
    comp: dict[str, Any] = {"id": cid, "type": comp_type, "label": label}

    if node.get("sublabel"):
        comp["sublabel"] = str(node["sublabel"])
    elif defaulted:
        comp["sublabel"] = "topology candidate"

    if node.get("tag"):
        comp["tag"] = str(node["tag"])

    if evidence_kind == "committed" and has_repo:
        source_ref = _build_source_reference(node, raw_id)
        if source_ref:
            comp["sources"] = [source_ref]
    return comp


def _build_components_list(
    nodes: list[dict[str, Any]],
    evidence_kind: str,
    has_repo: bool,
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    """Build sanitized components list and id_map."""
    id_map: dict[str, str] = {}
    existing_cids: set[str] = set()
    components: list[dict[str, Any]] = []

    for i, node in enumerate(nodes):
        raw_id = str(node.get("id") or f"node_{i+1}")
        cid = _sanitize_id(raw_id, existing_cids)
        existing_cids.add(cid)
        id_map[raw_id] = cid
        components.append(_build_component(node, cid, evidence_kind, has_repo))

    return components, id_map


def _calculate_grid_cols(n_comp: int) -> int:
    """Calculate grid column count based on component count."""
    if n_comp <= 4:
        return max(1, n_comp)
    if n_comp <= 9:
        return 3
    if n_comp <= 16:
        return 4
    return min(6, 12)


def _build_grid_layout(components: list[dict[str, Any]]) -> dict[str, Any]:
    """Assign row/col to components and return grid layout descriptor."""
    cols = _calculate_grid_cols(len(components))
    for i, comp in enumerate(components):
        comp["row"] = i // cols
        comp["col"] = i % cols

    return {
        "mode": "grid",
        "cols": cols,
        "gapX": 40,
        "gapY": 40,
        "cellW": 160,
        "cellH": 80,
    }


# ---------------------------------------------------------------------------
# Connections & Meta construction
# ---------------------------------------------------------------------------

def _link_key(link: dict[str, Any], key1: str, key2: str) -> str:
    """Extract string value from link using key1 or fallback to key2."""
    val = link.get(key1)
    if val is not None:
        return str(val)
    return str(link.get(key2, ""))


def _extract_valid_endpoints(
    link: dict[str, Any],
    id_map: dict[str, str],
    selected_cids: set[str],
) -> Optional[tuple[str, str]]:
    """Extract mapped source and target IDs if valid, directed, and distinct."""
    if link.get("directed") is False:
        return None
    s = id_map.get(_link_key(link, "source", "from"))
    t = id_map.get(_link_key(link, "target", "to"))
    if not s or not t:
        return None
    if s == t:
        return None
    if s not in selected_cids:
        return None
    if t not in selected_cids:
        return None
    return s, t


def _build_connections(
    links: list[dict[str, Any]],
    id_map: dict[str, str],
    selected_cids: set[str],
    is_directed: bool,
) -> list[dict[str, Any]]:
    """Build connections list for directed graphs only."""
    if not is_directed:
        return []
    connections: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    conn_counter = 1

    for link in links:
        endpoints = _extract_valid_endpoints(link, id_map, selected_cids)
        if endpoints is None or endpoints in seen:
            continue
        seen.add(endpoints)
        rel = str(link.get("relation") or link.get("label") or "calls")
        connections.append({
            "id": f"conn_{conn_counter}",
            "from": endpoints[0],
            "to": endpoints[1],
            "label": rel,
        })
        conn_counter += 1

    return connections


def _build_meta(
    data: dict[str, Any],
    focus_community: Optional[Union[int, str]],
    evidence_kind: str,
    repository: Optional[dict],
) -> dict[str, Any]:
    """Build metadata envelope for Archify IR."""
    if focus_community is not None:
        title = f"Community {focus_community} Architecture"
        out_name = f"community_{focus_community}.architecture.html"
    else:
        title = str(data.get("title") or "Codebase Architecture")
        out_name = "master.architecture.html"

    meta: dict[str, Any] = {"title": title, "output": out_name}
    if evidence_kind == "committed" and repository is not None:
        meta["repository"] = repository
    return meta


# ---------------------------------------------------------------------------
# Public API 1: graphify_to_archify
# ---------------------------------------------------------------------------

def graphify_to_archify(
    graph_json_path: Union[str, Path, dict],
    focus_community: Optional[Union[int, str]] = None,
    max_nodes: Optional[int] = None,
    *,
    repository: Optional[dict] = None,
    evidence_kind: str = "working-tree",
    selected_ids: Optional[Iterable[str]] = None,
) -> dict:
    """Convert Graphify graph to pure Archify architecture IR."""
    _validate_evidence_and_repo(evidence_kind, repository)
    data = _load_graph_data(graph_json_path)
    raw_nodes = _extract_raw_nodes(data, selected_ids)
    raw_links = list(data.get("links") or data.get("edges") or [])

    nodes = _filter_nodes_by_community(raw_nodes, focus_community)
    nodes = _filter_nodes_by_max(nodes, raw_links, max_nodes)

    components, id_map = _build_components_list(nodes, evidence_kind, repository is not None)
    layout = _build_grid_layout(components)
    selected_cids = {c["id"] for c in components}
    connections = _build_connections(raw_links, id_map, selected_cids, bool(data.get("directed", False)))
    meta = _build_meta(data, focus_community, evidence_kind, repository)

    return {
        "schema_version": 1,
        "diagram_type": "architecture",
        "meta": meta,
        "layout": layout,
        "components": components,
        "connections": connections,
    }


# ---------------------------------------------------------------------------
# Public API 2: graph_coverage
# ---------------------------------------------------------------------------

def _link_to_unproven(link: dict[str, Any], reason: str) -> dict[str, str]:
    """Map link to unproven relationship entry."""
    s = str(link.get("source") or link.get("from") or "")
    t = str(link.get("target") or link.get("to") or "")
    rel = str(link.get("relation") or link.get("label") or "related")
    return {"source": s, "target": t, "relation": rel, "reason": reason}


def _collect_unproven_relationships(links: list[dict[str, Any]], is_directed: bool) -> list[dict[str, str]]:
    """Collect relationships lacking proven direction."""
    if not is_directed:
        return [_link_to_unproven(link, "undirected_graph") for link in links]
    return [
        _link_to_unproven(link, "unproven_direction")
        for link in links
        if link.get("directed") is False
    ]


def graph_coverage(
    graph: Union[dict, str, Path],
    selected_ids: Iterable[str],
) -> dict:
    """Compute graph coverage inventory, directed flag, filter reasons, and unproven relationships.

    Contract:
    - Selected node status is 'selected' (unverified in raw topology), not 'verified'.
    """
    data = _load_graph_data(graph)
    raw_nodes = list(data.get("nodes", []))
    raw_links = list(data.get("links") or data.get("edges") or [])
    is_directed = bool(data.get("directed", False))

    selected_set = {str(sid) for sid in selected_ids}
    all_node_ids = [str(n.get("id")) for n in raw_nodes if n.get("id")]

    total = len(all_node_ids)
    selected_in_graph = [nid for nid in all_node_ids if nid in selected_set]
    selected = len(selected_in_graph)
    excluded = total - selected
    excluded_ids = [nid for nid in all_node_ids if nid not in selected_set]

    filter_reasons = {str(n.get("id")): "excluded_or_unselected" for n in raw_nodes if str(n.get("id")) not in selected_set}
    unproven = _collect_unproven_relationships(raw_links, is_directed)
    unknown = [
        {"kind": "relationship", "source": r["source"], "target": r["target"], "relation": r["relation"], "reason": r["reason"]}
        for r in unproven
    ]

    # Contract: 'selected' / 'unverified', NOT 'verified' merely from raw graph
    modules = [
        {"id": nid, "status": "selected" if nid in selected_set else "excluded"}
        for nid in all_node_ids
    ]

    return {
        "total": total,
        "selected": selected,
        "excluded": excluded,
        "directed": is_directed,
        "selected_ids": sorted(selected_in_graph),
        "excluded_ids": sorted(excluded_ids),
        "filter_reasons": filter_reasons,
        "unproven_relationships": unproven,
        "unknown": unknown,
        "modules": modules,
        "inventory": {
            "total_nodes": total,
            "selected_nodes": selected,
            "excluded_nodes": excluded,
            "directed": is_directed,
        },
    }


# ---------------------------------------------------------------------------
# Public API 3: validate_model & helpers
# ---------------------------------------------------------------------------

def _validate_model_header(model: dict[str, Any]) -> str:
    """Validate schema_version, title, and evidence_kind."""
    schema_version = model.get("schema_version")
    if schema_version != 1:
        raise ValueError(f"schema_version must be 1, got {schema_version}")

    title = model.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("title must be a non-empty string")

    evidence_kind = model.get("evidence_kind")
    if evidence_kind not in VALID_EVIDENCE_KINDS:
        raise ValueError(
            f"Invalid evidence_kind '{evidence_kind}'. Must be one of {sorted(VALID_EVIDENCE_KINDS)}"
        )
    return str(evidence_kind)


def _validate_committed_repo_and_rev(revision: Any, repository: Any) -> None:
    """Validate committed revision and repository matching requirements."""
    if not revision or not isinstance(revision, str) or not re.match(r"^[a-fA-F0-9]{40}$", revision):
        raise ValueError(f"Committed model requires a 40-character hex revision, got '{revision}'")
    if not repository or not isinstance(repository, dict):
        raise ValueError("Committed model requires a repository object")
    _validate_repository(repository)
    if repository.get("revision") != revision:
        raise ValueError(
            f"repository.revision ({repository.get('revision')}) must equal envelope revision ({revision}) for committed model"
        )


def _validate_optional_repo_and_rev(revision: Any, repository: Any) -> None:
    """Validate optional revision and repository."""
    if revision is not None:
        if not isinstance(revision, str) or not re.match(r"^[a-fA-F0-9]{40}$", revision):
            raise ValueError(f"revision must be a 40-character hex SHA if specified, got '{revision}'")
    if repository is not None:
        _validate_repository(repository)


def _validate_revision_and_repo(evidence_kind: str, revision: Any, repository: Any) -> None:
    """Validate revision and repository based on evidence_kind."""
    if evidence_kind == "committed":
        _validate_committed_repo_and_rev(revision, repository)
    else:
        _validate_optional_repo_and_rev(revision, repository)


def _validate_source_paths(source_paths: Any) -> None:
    """Validate source_paths list."""
    if source_paths is None:
        return
    if not isinstance(source_paths, list):
        raise ValueError("source_paths must be a list of paths")
    for sp in source_paths:
        if not _is_safe_relative_path(sp):
            raise ValueError(f"source_paths contains unsafe or absolute path: '{sp}'")


def _validate_coverage_dict(coverage: Any) -> None:
    """Validate coverage dictionary."""
    if coverage is None:
        return
    if not isinstance(coverage, dict):
        raise ValueError("coverage must be a dictionary")
    if not any(k in coverage for k in ("modules", "unknown", "excluded", "total", "inventory")):
        raise ValueError("coverage must define modules, unknown, or excluded")


def _validate_view_id_and_type(v: dict[str, Any], seen_ids: set[str]) -> str:
    """Validate view ID and diagram type."""
    vid = v.get("id")
    if not vid or not isinstance(vid, str) or not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9_-]*", vid):
        raise ValueError(f"Invalid view id: '{vid}'")
    if vid in seen_ids:
        raise ValueError(f"Duplicate view id: '{vid}'")
    seen_ids.add(vid)

    vtype = v.get("type")
    if vtype not in VALID_VIEW_TYPES:
        raise ValueError(
            f"Invalid view type '{vtype}' in view '{vid}'. Must be one of {sorted(VALID_VIEW_TYPES)}"
        )
    return vid


def _validate_view_candidate(v: dict[str, Any], vid: str, seen_candidates: set[str]) -> None:
    """Validate view candidate path safety and format."""
    cand = v.get("candidate")
    if not cand or not isinstance(cand, str):
        raise ValueError(f"View '{vid}' missing candidate path")
    if not cand.endswith(".json"):
        raise ValueError(f"View '{vid}' candidate must be a .json file: '{cand}'")
    if not _is_safe_relative_path(cand):
        raise ValueError(f"View '{vid}' candidate path escapes root or contains path traversal: '{cand}'")
    if cand in seen_candidates:
        raise ValueError(f"Duplicate candidate path: '{cand}'")
    seen_candidates.add(cand)


def _validate_single_view(v: Any, seen_ids: set[str], seen_candidates: set[str]) -> None:
    """Validate one view entry."""
    if not isinstance(v, dict):
        raise ValueError("Each view must be a dictionary")
    vid = _validate_view_id_and_type(v, seen_ids)
    _validate_view_candidate(v, vid, seen_candidates)


def _validate_views_list(views: Any) -> None:
    """Validate views list."""
    if not isinstance(views, list) or len(views) == 0:
        raise ValueError("views must be a non-empty list of view objects")
    seen_ids: set[str] = set()
    seen_candidates: set[str] = set()
    for v in views:
        _validate_single_view(v, seen_ids, seen_candidates)


def _validate_flow_item(item: Any, seen_ids: set[str], allowed: set[str]) -> None:
    """Cards and detail steps share Archify's document-wide ID namespace."""
    if not isinstance(item, dict) or set(item) - allowed:
        raise ValueError("Invalid flow/step fields")
    item_id = item.get("id")
    if (not isinstance(item_id, str) or len(item_id) > 100
            or not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9_-]*", item_id) or item_id in seen_ids):
        raise ValueError(f"Invalid or duplicate flow/step id: {item_id!r}")
    seen_ids.add(item_id)
    if not isinstance(item.get("text"), str) or not item["text"].strip():
        raise ValueError("Flow/step text must be non-empty")
    if "detail" in item and (not isinstance(item["detail"], str) or not item["detail"].strip()):
        raise ValueError("Flow/step detail must be non-empty text")


def _validate_step_sources(step: dict) -> None:
    """Use native common.schema source references, not explainer source lines."""
    sources = step.get("sources", [])
    if not isinstance(sources, list):
        raise ValueError("Step sources must be a list")
    if not sources and step.get("detail", "").strip().casefold() != "chưa xác minh":
        raise ValueError("Step needs sources or detail 'chưa xác minh'")
    for source in sources:
        if not isinstance(source, dict) or set(source) - {"path", "line", "end_line"}:
            raise ValueError("Invalid step source fields")
        path = source.get("path")
        if not isinstance(path, str) or not _is_safe_relative_path(path):
            raise ValueError("Invalid step source path")
        line = source.get("line")
        end = source.get("end_line", line)
        if type(line) is not int or type(end) is not int or line < 1 or end < line:
            raise ValueError("Invalid step source line range")


def _validate_master(model: dict) -> None:
    """Optional master maps native card targets to views/candidates; legacy views stay valid.

    master = {overview: view_id, flows: [{id, text, detail?, target: {diagram: view_id},
              steps: [{id, text, detail?, sources: [{path, line, end_line?}]}]}]}.
    A flow without evidence has only id/text/detail='chưa xác minh', never a target.
    Sources are project-relative; filesystem checks happen before sync renders.
    """
    if "master" not in model:
        return
    master = model["master"]
    if not isinstance(master, dict) or set(master) != {"overview", "flows"}:
        raise ValueError("master requires overview and flows")
    views = {view["id"]: view for view in model["views"]}
    overview = master["overview"]
    if not isinstance(overview, str) or overview not in views or views[overview]["type"] != "architecture":
        raise ValueError("master.overview must reference an architecture view")
    if not isinstance(master["flows"], list):
        raise ValueError("master.flows must be a list")
    seen_ids = set(views)
    for flow in master["flows"]:
        _validate_flow_item(flow, seen_ids, {"id", "text", "detail", "target", "steps"})
        if "target" not in flow:
            if "steps" in flow or flow.get("detail", "").strip().casefold() != "chưa xác minh":
                raise ValueError("Flow without target must say 'chưa xác minh' and omit steps")
            continue
        target = flow["target"]
        if not isinstance(target, dict) or set(target) != {"diagram"}:
            raise ValueError("Flow target must contain only diagram")
        diagram = target["diagram"]
        if (not isinstance(diagram, str) or diagram not in views or diagram == overview
                or views[diagram]["type"] == "explainer"):
            raise ValueError("Flow target must reference a native detail view")
        steps = flow.get("steps")
        if not isinstance(steps, list) or not steps:
            raise ValueError("Flow target requires non-empty steps")
        for step in steps:
            _validate_flow_item(step, seen_ids, {"id", "text", "detail", "sources"})
            _validate_step_sources(step)


def validate_model(model: dict) -> dict:
    """Validate Master model envelope per contract."""
    if not isinstance(model, dict):
        raise ValueError("Model must be a dictionary")

    evidence_kind = _validate_model_header(model)
    _validate_revision_and_repo(evidence_kind, model.get("revision"), model.get("repository"))
    _validate_source_paths(model.get("source_paths"))
    _validate_coverage_dict(model.get("coverage"))
    _validate_views_list(model.get("views"))
    _validate_master(model)
    return model
