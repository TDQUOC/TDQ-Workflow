#!/usr/bin/env python3
"""TDQ Archify Adapter Module.

Facade and CLI orchestration module for diagram generation, model bridge,
document binding, master bundle publishing, status freshness, and verification.

Strictly stdlib-only. All functions have cyclomatic complexity <= 10.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any, Optional, Union

import utf8_io  # noqa: F401 - Force UTF-8 on entrypoints

# Direct re-exports from delivery module (no getattr / sys.modules wrappers)
from archify_delivery import (
    FinalizeResult,
    atomic_delivery,
    build_finalize_command,
    check_environment,
    execute_finalize,
    find_archify_root,
    get_archify_bin,
    open_artifact,
    run_finalize,
)

# Imports from model and evidence module
from archify_model import (
    VALID_COMPONENT_TYPES,
    VALID_EVIDENCE_KINDS,
    VALID_VIEW_TYPES,
    graph_coverage,
    graphify_to_archify,
    validate_model,
)

# Imports from artifacts and lifecycle module
from archify_artifacts import (
    BINDING_END,
    BINDING_START,
    bind_document,
    build_manifest,
    check_binding,
    check_manifest,
    document_digest,
    mark_stale,
    publish_bundle,
    source_fingerprint,
    _hash_file,
    _is_within,
)


def test_bridge() -> bool:
    """Self-test graphify_to_archify conversion."""
    sample = {"directed": True, "nodes": [{"id": "n1", "label": "Node 1"}], "links": []}
    ir = graphify_to_archify(sample)
    assert ir.get("schema_version") == 1, "schema_version must be 1"
    assert ir.get("diagram_type") == "architecture", "diagram_type must be architecture"
    return True


def _get_git_dirty_files(project_root: Path) -> list[str]:
    """Parse git status --porcelain -z safely handling raw Unicode and rename tokens."""
    proc = subprocess.run(
        ["git", "status", "--porcelain", "-z"],
        cwd=str(project_root),
        capture_output=True,
        timeout=15,
        check=False,
    )
    if proc.returncode != 0:
        err = proc.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(f"git status failed: {err}")

    raw_bytes = proc.stdout
    parts = raw_bytes.split(b"\0")
    dirty_files: list[str] = []
    i = 0
    while i < len(parts):
        token = parts[i]
        if not token:
            i += 1
            continue
        if len(token) > 3:
            status_code = token[:2]
            path_bytes = token[3:]
            path_str = path_bytes.decode("utf-8", errors="surrogateescape").replace("\\", "/")
            dirty_files.append(path_str)
            if b"R" in status_code or b"C" in status_code:
                i += 1
        i += 1
    return dirty_files


def _is_path_matched(file_rel: str, source_paths: list[str]) -> bool:
    """Check if a relative file path matches any source path or directory prefix."""
    for sp in source_paths:
        sp_norm = sp.rstrip("/\\").replace("\\", "/")
        if file_rel == sp_norm or file_rel.startswith(sp_norm + "/"):
            return True
    return False


def _verify_committed_revision(project_root: Path, validated_model: dict, model_file: Path) -> bool:
    """Validate git HEAD revision and dirty working tree for committed evidence."""
    evidence_kind = validated_model.get("evidence_kind", "working-tree")
    if evidence_kind != "committed":
        return True

    expected_rev = validated_model.get("revision", "")
    repo_rev = validated_model.get("repository", {}).get("revision", "")
    if repo_rev and expected_rev.lower() != repo_rev.lower():
        sys.stderr.write(
            f"Error: Master committed revision '{expected_rev}' mismatch repository.revision '{repo_rev}'\n"
        )
        return False

    try:
        rev_proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=15,
            check=False,
        )
        if rev_proc.returncode != 0:
            sys.stderr.write(f"Error: git rev-parse HEAD failed: {rev_proc.stderr}\n")
            return False
        actual_rev = rev_proc.stdout.strip()
        if actual_rev.lower() != expected_rev.lower():
            sys.stderr.write(
                f"Error: Git revision mismatch: model asserts {expected_rev} but HEAD is {actual_rev}\n"
            )
            return False
    except Exception as exc:
        sys.stderr.write(f"Error checking git revision: {exc}\n")
        return False

    try:
        dirty_files = _get_git_dirty_files(project_root)
        source_paths = validated_model.get("source_paths") or []
        model_rel = ""
        try:
            model_rel = model_file.relative_to(project_root).as_posix()
        except ValueError:
            pass

        relevant_dirty: list[str] = []
        for fp in dirty_files:
            if source_paths:
                if _is_path_matched(fp, source_paths):
                    relevant_dirty.append(fp)
            else:
                if not (
                    fp.startswith("docs/architecture")
                    or fp.startswith("docs/tdq")
                    or fp.startswith("logs")
                    or fp == model_rel
                    or fp.endswith(".lock")
                ):
                    relevant_dirty.append(fp)

        if relevant_dirty:
            sys.stderr.write(
                f"Error: Working tree is dirty ({len(relevant_dirty)} source files modified: {relevant_dirty[:3]}). "
                f"Committed evidence requires a clean git status.\n"
            )
            return False
    except Exception as exc:
        sys.stderr.write(f"Error checking git dirty status: {exc}\n")
        return False

    return True


def _verify_candidate_confinement(model_file: Path, views: list[dict]) -> bool:
    """Ensure all view candidates are confined within model parent directory and exist."""
    model_parent = model_file.parent.resolve()
    for v in views:
        cand_rel = v.get("candidate", "")
        cand_abs = (model_parent / cand_rel).resolve()
        try:
            cand_abs.relative_to(model_parent)
        except ValueError:
            sys.stderr.write(
                f"Error: View '{v.get('id')}' candidate escapes model parent directory: {cand_rel}\n"
            )
            return False
        if not cand_abs.is_file():
            sys.stderr.write(
                f"Error: Candidate file for view '{v.get('id')}' not found: {cand_abs}\n"
            )
            return False
    return True


def _verify_master_sources(model: dict, project_root: Path) -> bool:
    """Reject missing, escaping or out-of-range flow evidence before rendering."""
    root = project_root.resolve()
    try:
        for flow in model.get("master", {}).get("flows", []):
            for step in flow.get("steps", []):
                for source in step.get("sources", []):
                    path = (root / source["path"].replace("\\", "/")).resolve()
                    path.relative_to(root)
                    with path.open("r", encoding="utf-8") as stream:
                        line_count = sum(1 for _ in stream)
                    if source.get("end_line", source["line"]) > line_count:
                        raise ValueError(f"Source line range exceeds file: {source['path']}")
    except (OSError, ValueError) as exc:
        sys.stderr.write(f"Error: Master flow evidence invalid: {exc}\n")
        return False
    return True


def _render_views_to_staging(
    views: list[dict],
    model_parent: Path,
    staging_dir: Path,
    project_root: Path,
    quality: str = "showcase",
) -> tuple[list[dict], dict[str, str], dict[str, Any]]:
    """Render all native views into staging directory via delivery."""
    rendered_views: list[dict] = []
    child_files: dict[str, str] = {}
    receipts: dict[str, Any] = {}

    for v in views:
        vid = v["id"]
        vtype = v["type"]
        cand_abs = (model_parent / v["candidate"]).resolve()
        view_filename = f"{vid}.html"
        view_out = staging_dir / view_filename

        res = run_finalize(
            diagram_type=vtype,
            candidate_path=cand_abs,
            output_path=view_out,
            quality=quality,
            repo_root=project_root,
        )
        if not res.status or not view_out.is_file():
            raise RuntimeError(f"Failed to finalize view '{vid}': {res.receipt}")

        v_hash = _hash_file(view_out)
        child_files[view_filename] = v_hash
        receipts[vid] = res.receipt

        cand_bundle_name = f"{vid}.candidate.json"
        cand_bundle_path = staging_dir / cand_bundle_name
        cand_bundle_path.write_text(cand_abs.read_text(encoding="utf-8"), encoding="utf-8")
        child_files[cand_bundle_name] = _hash_file(cand_bundle_path)

        rendered_views.append({
            "id": vid,
            "type": vtype,
            "summary": v.get("summary", ""),
            "file": view_filename,
            "hash": v_hash,
        })

    return rendered_views, child_files, receipts


def _generate_index_html(validated_model: dict, rendered_views: list[dict]) -> str:
    """Generate index HTML with escaped text labels, dashboard layout, and relative links."""
    escaped_title = html.escape(str(validated_model.get("title", "Master Architecture")))
    escaped_rev = html.escape(str(validated_model.get("revision", "N/A")))
    escaped_kind = html.escape(str(validated_model.get("evidence_kind", "unknown")))
    coverage = validated_model.get("coverage", {})
    repo_info = validated_model.get("repository") or {}
    escaped_repo_url = html.escape(str(repo_info.get("url", "")))
    modules_list = coverage.get("modules", [])
    module_pills = " ".join(
        f'<span class="module-pill">{html.escape(str(m.get("id", "")))} · {html.escape(str(m.get("status", "selected")))}</span>'
        for m in modules_list if isinstance(m, dict)
    )

    table_rows = []
    for rv in rendered_views:
        row = (
            f"<tr>"
            f"<td><strong>{html.escape(rv['id'])}</strong></td>"
            f"<td><span class=\"type-badge\">{html.escape(rv['type'])}</span></td>"
            f"<td>{html.escape(rv['summary'])}</td>"
            f"<td><a class=\"view-btn\" href=\"{html.escape(rv['file'])}\">View Diagram</a></td>"
            f"</tr>"
        )
        table_rows.append(row)
    inventory_html = "\n".join(table_rows)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escaped_title}</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; background: #f8fafc; color: #0f172a; line-height: 1.6; }}
    .portal-header {{ background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #f8fafc; padding: 3rem 2rem; border-bottom: 1px solid #334155; }}
    .container {{ max-width: 1160px; margin: 0 auto; padding: 2rem; }}
    h1 {{ margin: 0 0 0.5rem 0; font-size: 2.25rem; letter-spacing: -0.02em; }}
    .subtitle {{ color: #94a3b8; margin: 0; font-size: 1.05rem; }}
    .meta-box {{ background: #ffffff; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04); margin-bottom: 2rem; }}
    .meta-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; }}
    .meta-item {{ background: #f8fafc; padding: 0.85rem 1rem; border-radius: 8px; border: 1px solid #e2e8f0; font-size: 0.95rem; }}
    .module-bar {{ margin-top: 1rem; display: flex; flex-wrap: wrap; gap: 0.5rem; }}
    .module-pill {{ background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; padding: 0.25rem 0.65rem; border-radius: 999px; font-size: 0.82rem; font-weight: 600; }}
    h2 {{ font-size: 1.4rem; margin: 1.5rem 0 1rem 0; color: #0f172a; }}
    table {{ border-collapse: collapse; width: 100%; background: #ffffff; border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04); }}
    th, td {{ border-bottom: 1px solid #e2e8f0; padding: 1rem 1.25rem; text-align: left; }}
    th {{ background: #f1f5f9; font-weight: 600; color: #334155; font-size: 0.9rem; }}
    tr:last-child td {{ border-bottom: none; }}
    .type-badge {{ background: #f1f5f9; color: #334155; padding: 0.2rem 0.6rem; border-radius: 6px; font-size: 0.85rem; font-weight: 500; }}
    .view-btn {{ display: inline-block; background: #2563eb; color: #ffffff; padding: 0.45rem 0.95rem; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 0.9rem; }}
    .view-btn:hover {{ background: #1d4ed8; text-decoration: none; }}
  </style>
</head>
<body>
  <header class="portal-header">
    <div class="container" style="padding: 0;">
      <h1>{escaped_title}</h1>
      <p class="subtitle">Interactive Master Architecture Portal · Verified by TDQ-Workflow &amp; Archify</p>
    </div>
  </header>
  <main class="container">
    <div class="meta-box">
      <div class="meta-grid">
        <div class="meta-item"><strong>Evidence Kind:</strong> {escaped_kind}</div>
        <div class="meta-item"><strong>Revision:</strong> {escaped_rev}</div>
        <div class="meta-item"><strong>Repository:</strong> {escaped_repo_url or 'N/A'}</div>
        <div class="meta-item"><strong>Coverage:</strong> {len(coverage.get('modules', []))} modules, {len(coverage.get('excluded', []))} excluded, {len(coverage.get('unknown', []))} unknown</div>
      </div>
      <div class="module-bar">{module_pills}</div>
    </div>
    <h2>Views Inventory</h2>
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Type</th>
          <th>Summary</th>
          <th>Artifact</th>
        </tr>
      </thead>
      <tbody>
        {inventory_html}
      </tbody>
    </table>
  </main>
</body>
</html>"""


def _alloc_id(base: str, used: set[str]) -> str:
    cand = "".join(c if c.isalnum() or c in "_-" else "-" for c in base).strip("-") or "item"
    if not cand[0].isalpha() or cand.startswith("explainer-"):
        cand = f"m-{cand}"
    out, idx = cand[:90], 1
    while out in used:
        out, idx = f"{cand[:84]}-{idx}", idx + 1
    used.add(out)
    return out


def _step_detail_text(step: dict[str, Any]) -> str:
    refs = [
        f"`{s['path']}:{s['line']}" + (f"-{s['end_line']}`" if s.get("end_line", s["line"]) != s["line"] else "`")
        for s in step.get("sources", [])
    ]
    detail = step.get("detail", "").strip()
    return f"{detail} ({', '.join(refs)})" if detail and refs else (detail or ", ".join(refs))


def _build_master_explainer(validated_model: dict[str, Any], quality: str) -> dict[str, Any]:
    master = validated_model["master"]
    views = validated_model["views"]
    views_by_id = {v["id"]: v for v in views}
    overview_id, flows = master["overview"], master["flows"]
    used = {"answer", "diagram-dialog", "diagram-dialog-title", "toast"} | set(views_by_id)
    used.update(f["id"] for f in flows)
    used.update(s["id"] for f in flows for s in f.get("steps", []))

    overview_view = views_by_id[overview_id]
    overview_blocks: list[dict[str, Any]] = [{
        "id": overview_id,
        "type": "diagram",
        "diagramType": overview_view["type"],
        "source": f"{overview_id}.candidate.json",
    }]
    if flows:
        overview_blocks.append({
            "id": _alloc_id("master-flows", used),
            "type": "steps",
            "items": [
                {k: f[k] for k in ("id", "text", "detail", "target") if f.get(k)}
                for f in flows
            ],
        })
    panels: list[dict[str, Any]] = [{
        "id": _alloc_id(f"{overview_id}-panel", used),
        "title": overview_view.get("summary") or "Overview",
        "blocks": overview_blocks,
    }]
    for v in views:
        vid = v["id"]
        if vid == overview_id or v["type"] == "explainer":
            continue
        blocks: list[dict[str, Any]] = [{
            "id": vid,
            "type": "diagram",
            "diagramType": v["type"],
            "source": f"{vid}.candidate.json",
        }]
        for f in (fl for fl in flows if (fl.get("target") or {}).get("diagram") == vid):
            blocks.append({
                "id": _alloc_id(f"{f['id']}-steps", used),
                "type": "steps",
                "items": [
                    {"id": s["id"], "text": s["text"], "detail": _step_detail_text(s)}
                    for s in f.get("steps", [])
                ],
            })
        panels.append({
            "id": _alloc_id(f"{vid}-panel", used),
            "title": v.get("summary") or vid,
            "blocks": blocks,
        })

    title = str(validated_model.get("title", "Master Architecture"))
    return {
        "schema_version": 1,
        "diagram_type": "explainer",
        "meta": {
            "id": _alloc_id("master-architecture", used),
            "title": title,
            "locale": "en",
            "output": "index.html",
            "quality_profile": quality,
        },
        "answer": {"summary": f"{title} ({validated_model.get('evidence_kind', 'working-tree')})."},
        "panels": panels,
        "sources": [],
    }


def _derive_stable_source_paths(
    project_root: Path,
    dest_dir: Path,
    model_file: Path,
    validated_model: dict,
) -> list[str]:
    """Derive stable project source_paths excluding outputs, dest, and staging directories."""
    dest_rel = dest_dir.resolve().relative_to(project_root).as_posix() if _is_within(dest_dir, project_root) else ""
    model_rel = model_file.resolve().relative_to(project_root).as_posix() if _is_within(model_file, project_root) else ""
    declared = validated_model.get("source_paths")
    base_paths = list(declared) if declared is not None else list(source_fingerprint(project_root).keys())
    model_parent = model_file.parent.resolve()
    extra_abs = [
        *((model_parent / v.get("candidate", "")).resolve() for v in validated_model.get("views", [])),
        *(
            (project_root / src["path"].replace("\\", "/")).resolve()
            for flow in validated_model.get("master", {}).get("flows", [])
            for step in flow.get("steps", [])
            for src in step.get("sources", [])
        ),
    ]
    for p_abs in extra_abs:
        if _is_within(p_abs, project_root):
            base_paths.append(p_abs.relative_to(project_root).as_posix())

    clean = list(dict.fromkeys(
        p for p in base_paths
        if p != model_rel and ".staging" not in p and "staging." not in p
        and not (dest_rel and (p == dest_rel or p.startswith(dest_rel + "/")))
    ))
    return clean if declared is not None else sorted(clean)


def _build_and_publish_manifest(
    project_root: Path,
    dest_dir: Path,
    staging_dir: Path,
    model_file: Path,
    validated_model: dict,
    rendered_views: list[dict],
    child_files: dict[str, str],
    receipts: dict[str, Any],
    source_paths: Optional[list[str]] = None,
    pre_sources: Optional[dict[str, str]] = None,
    pre_model_hash: Optional[str] = None,
) -> Path:
    """Construct aggregate manifest, rebase final paths, and publish bundle atomically."""
    staging_index = staging_dir / "index.html"
    if source_paths is None:
        source_paths = _derive_stable_source_paths(project_root, dest_dir, model_file, validated_model)
    if pre_model_hash is not None and _hash_file(model_file) != pre_model_hash:
        raise RuntimeError("Master model modified during render")
    if pre_sources is not None and source_fingerprint(project_root, paths=source_paths) != pre_sources:
        raise RuntimeError("Source or candidate modified during render")

    aggregate_receipt = {
        "ok": True,
        "status": "pass",
        "engine": "archify",
        "views_count": len(rendered_views),
        "index": "index.html",
    }

    raw_manifest = build_manifest(
        project=project_root,
        document=model_file,
        candidate=model_file,
        artifact=staging_index,
        receipt=aggregate_receipt,
        evidence_kind=validated_model.get("evidence_kind", "working-tree"),
        revision=validated_model.get("revision"),
        coverage=validated_model.get("coverage", {}),
        source_paths=source_paths,
        source_files=pre_sources,
    )

    final_art_rel = (dest_dir / "index.html").resolve().relative_to(project_root).as_posix()
    raw_manifest["artifact_path"] = final_art_rel
    raw_manifest["child_files"] = child_files
    raw_manifest["views"] = rendered_views
    raw_manifest["view_receipts"] = receipts

    staging_manifest = staging_dir / "manifest.json"
    staging_manifest.write_text(json.dumps(raw_manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    published_index = publish_bundle(staging=staging_dir, destination=dest_dir)
    readback = check_manifest(project_root, dest_dir / "manifest.json")
    if readback.get("status") != "current":
        raise RuntimeError(f"Post-publish readback not current: {readback.get('reasons')}")
    return published_index


def _sync_legacy_graph(graph_path: Union[str, Path], out_path: Optional[Union[str, Path]], max_nodes: int) -> bool:
    """Fallback sync for legacy graph.json conversion calls."""
    target_graph = Path(graph_path)
    if not target_graph.is_file():
        sys.stderr.write(f"Warning: Graph file not found: {target_graph}, skipping sync.\n")
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


def _resolve_sync_paths(
    model: Optional[Union[str, Path]],
    project: Optional[Union[str, Path]],
    out: Optional[Union[str, Path]],
) -> Optional[tuple[Path, Path, Path]]:
    """Resolve project_root, dest_dir, and model_file paths safely."""
    project_root = Path(project).resolve() if project else Path.cwd().resolve()
    if not project_root.is_dir():
        sys.stderr.write(f"Error: Project root directory not found: {project_root}\n")
        return None

    if out is not None:
        raw_out = Path(out)
        dest_dir = raw_out.resolve() if raw_out.is_absolute() else (project_root / raw_out).resolve()
    else:
        dest_dir = (project_root / "docs" / "architecture").resolve()

    if model is None:
        default_model = project_root / "docs" / "architecture" / "master.model.json"
        if default_model.is_file():
            model_file = default_model
        else:
            sys.stderr.write("Error: Master model path not provided and default not found.\n")
            return None
    else:
        raw_m = Path(model)
        model_file = raw_m.resolve() if raw_m.is_absolute() else (project_root / raw_m).resolve()

    if not model_file.is_file():
        sys.stderr.write(f"Error: Master model file not found: {model_file}\n")
        return None

    return project_root, dest_dir, model_file


def _load_and_validate_model(model_file: Path) -> Optional[dict]:
    """Read and validate Master model file."""
    try:
        content = model_file.read_text(encoding="utf-8")
        if not content.strip():
            sys.stderr.write(f"Error: Master model file is empty: {model_file}\n")
            return None
        model_data = json.loads(content)
        return validate_model(model_data)
    except Exception as exc:
        sys.stderr.write(f"Error: Master model validation failed: {exc}\n")
        return None


def sync_master(
    model: Optional[Union[str, Path]] = None,
    project: Optional[Union[str, Path]] = None,
    out: Optional[Union[str, Path]] = None,
    *,
    graph_path: Optional[Union[str, Path]] = None,
    out_path: Optional[Union[str, Path]] = None,
    max_nodes: int = 25,
    quality: str = "showcase",
) -> bool:
    """Synchronize Master architecture bundle."""
    if graph_path is not None and model is None:
        return _sync_legacy_graph(graph_path, out_path, max_nodes)

    paths = _resolve_sync_paths(model, project, out)
    if paths is None:
        return False
    project_root, dest_dir, model_file = paths

    validated_model = _load_and_validate_model(model_file)
    if validated_model is None:
        return False

    if not _verify_committed_revision(project_root, validated_model, model_file):
        return False

    views = validated_model.get("views", [])
    if not _verify_candidate_confinement(model_file, views):
        return False
    if not _verify_master_sources(validated_model, project_root):
        return False

    dest_dir.parent.mkdir(parents=True, exist_ok=True)
    staging_dir = dest_dir.parent / f".staging.{uuid.uuid4().hex}"
    staging_dir.mkdir(parents=True, exist_ok=True)

    try:
        source_paths = _derive_stable_source_paths(project_root, dest_dir, model_file, validated_model)
        pre_sources = source_fingerprint(project_root, paths=source_paths)
        pre_model_hash = _hash_file(model_file)

        rendered_views, child_files, receipts = _render_views_to_staging(
            views, model_file.parent.resolve(), staging_dir, project_root, quality
        )

        index_out = staging_dir / "index.html"
        if "master" in validated_model:
            master_cand = staging_dir / "master.candidate.json"
            master_cand.write_text(
                json.dumps(_build_master_explainer(validated_model, quality), indent=2),
                encoding="utf-8",
            )
            res = run_finalize(
                diagram_type="explainer",
                candidate_path=master_cand,
                output_path=index_out,
                quality=quality,
                repo_root=project_root,
            )
            if not res.status or not index_out.is_file():
                raise RuntimeError(f"Failed to finalize master explainer: {res.receipt}")
            child_files["master.candidate.json"] = _hash_file(master_cand)
            receipts["master"] = res.receipt
        else:
            index_out.write_text(_generate_index_html(validated_model, rendered_views), encoding="utf-8")

        published_index = _build_and_publish_manifest(
            project_root, dest_dir, staging_dir, model_file,
            validated_model, rendered_views, child_files, receipts,
            source_paths=source_paths, pre_sources=pre_sources, pre_model_hash=pre_model_hash,
        )
        print(f"Master architecture published: {published_index}")
        return True
    except Exception as exc:
        sys.stderr.write(f"Error during sync_master: {exc}\n")
        if staging_dir.exists():
            shutil.rmtree(staging_dir, ignore_errors=True)
        return False


def check_master_status(project: Optional[Union[str, Path]] = None) -> dict:
    """Inspect status of Master architecture bundle, freshness, and child tampering."""
    project_root = Path(project).resolve() if project else Path.cwd().resolve()
    manifest_path = project_root / "docs" / "architecture" / "manifest.json"
    if not manifest_path.is_file():
        return {
            "status": "absent",
            "reasons": [f"Master manifest not found: {manifest_path}"],
        }

    res = check_manifest(project_root, manifest_path)
    status_val = res.get("status", "invalid")
    reasons = list(res.get("reasons", []))

    try:
        man_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        child_files = man_data.get("child_files", {})
        bundle_dir = manifest_path.parent
        for child_name, exp_hash in child_files.items():
            child_file = bundle_dir / child_name
            if not child_file.is_file():
                reasons.append(f"Child file missing: {child_name}")
                if status_val == "current":
                    status_val = "stale"
            else:
                act_hash = _hash_file(child_file)
                if act_hash.lower() != exp_hash.lower():
                    reasons.append(f"Child file tampered: {child_name} (expected {exp_hash}, got {act_hash})")
                    if status_val == "current":
                        status_val = "stale"
    except Exception as exc:
        reasons.append(f"Error reading manifest child files: {exc}")
        status_val = "invalid"

    return {
        "status": status_val,
        "reasons": reasons,
        "manifest_path": manifest_path.relative_to(project_root).as_posix(),
    }


def verify_document_and_manifest(
    document: Union[str, Path],
    manifest: Union[str, Path],
    project: Optional[Union[str, Path]] = None,
) -> dict:
    """Verify document binding and manifest freshness."""
    project_root = Path(project).resolve() if project else Path.cwd().resolve()
    doc_path = Path(document)
    if not doc_path.is_absolute():
        doc_path = (project_root / doc_path).resolve()
    man_path = Path(manifest)
    if not man_path.is_absolute():
        man_path = (project_root / man_path).resolve()

    if not doc_path.is_file():
        return {"status": "invalid", "reasons": [f"Document not found: {doc_path}"]}
    if not man_path.is_file():
        return {"status": "invalid", "reasons": [f"Manifest not found: {man_path}"]}

    b_res = check_binding(doc_path, man_path)
    m_res = check_manifest(project_root, man_path)

    reasons: list[str] = []
    if not b_res.get("valid") or b_res.get("status") != "current":
        reasons.extend(b_res.get("reasons", []))
    if m_res.get("status") != "current":
        reasons.extend(m_res.get("reasons", []))

    try:
        man_data = json.loads(man_path.read_text(encoding="utf-8"))
        child_files = man_data.get("child_files", {})
        bundle_dir = man_path.parent
        for child_name, exp_hash in child_files.items():
            child_file = bundle_dir / child_name
            if not child_file.is_file():
                reasons.append(f"Child file missing: {child_name}")
            else:
                act_hash = _hash_file(child_file)
                if act_hash.lower() != exp_hash.lower():
                    reasons.append(f"Child file tampered: {child_name}")
    except Exception:
        pass

    if "invalid" in (b_res.get("status"), m_res.get("status")):
        status_val = "invalid"
    elif reasons:
        status_val = "stale"
    else:
        status_val = "current"

    return {
        "status": status_val,
        "reasons": reasons,
        "binding": b_res,
        "manifest": m_res,
    }


def handle_check(args: argparse.Namespace) -> int:
    """Handle CLI check sub-command."""
    try:
        res = check_environment()
        print(json.dumps(res, indent=2))
        return 0 if res.get("ready") else 1
    except Exception as exc:
        sys.stderr.write(f"Error checking environment: {exc}\n")
        return 1


def _prepare_render_paths(args: argparse.Namespace) -> tuple[Path, Path, Path, Optional[Path], Optional[bytes]]:
    """Validate inputs and resolve project_root, cand_path, out_path, doc_path."""
    project_root = Path(args.repo_root).resolve() if args.repo_root else Path.cwd().resolve()
    if not project_root.is_dir():
        raise FileNotFoundError(f"Project root not found: {project_root}")

    cand_path = Path(args.candidate)
    if not cand_path.is_absolute():
        cand_path = (project_root / cand_path).resolve()
    if not cand_path.is_file():
        raise FileNotFoundError(f"Candidate file not found: {cand_path}")

    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = (project_root / out_path).resolve()

    doc_path = None
    doc_original_bytes = None
    if args.document:
        doc_path = Path(args.document)
        if not doc_path.is_absolute():
            doc_path = (project_root / doc_path).resolve()
        if not doc_path.is_file():
            raise FileNotFoundError(f"Document file not found: {doc_path}")
        doc_original_bytes = doc_path.read_bytes()

    return project_root, cand_path, out_path, doc_path, doc_original_bytes


def _promote_staged_artifacts(temp_out: Path, out_path: Path) -> list[Path]:
    """Promote staged HTML artifact and any matching engine sidecars to final destination."""
    promoted: list[Path] = []
    temp_dir = temp_out.parent
    temp_prefix = temp_out.stem

    os.replace(temp_out, out_path)
    promoted.append(out_path)

    for item in temp_dir.glob(f"{temp_prefix}*"):
        if item.is_file() and item != temp_out:
            suffix = item.name[len(temp_prefix):]
            dest_item = out_path.parent / f"{out_path.stem}{suffix}"
            try:
                os.replace(item, dest_item)
                promoted.append(dest_item)
            except Exception:
                pass
    return promoted


def _deliver_render_manifest(
    project_root: Path,
    doc_path: Path,
    cand_path: Path,
    out_path: Path,
    manifest_path: Path,
    receipt: dict,
    evidence_kind: str,
    request: Optional[str],
    lane: Optional[str],
) -> None:
    """Build manifest with outputs excluded from source_paths, deliver atomically, and bind doc."""
    all_sources = source_fingerprint(project_root)
    excluded_rel = set()
    for p in (out_path, manifest_path, cand_path, doc_path, out_path.with_suffix(".receipt.json")):
        if _is_within(p, project_root):
            excluded_rel.add(p.resolve().relative_to(project_root).as_posix())

    clean_sources = [s for s in all_sources.keys() if s not in excluded_rel]

    manifest = build_manifest(
        project=project_root,
        document=doc_path,
        candidate=cand_path,
        artifact=out_path,
        receipt=receipt,
        evidence_kind=evidence_kind,
        request=request,
        lane=lane,
        source_paths=clean_sources,
    )
    atomic_delivery(manifest_path, json.dumps(manifest, indent=2, ensure_ascii=False))
    bind_document(doc_path, manifest_path)


def _rollback_render_transaction(
    had_out: bool,
    backup_out: Path,
    out_path: Path,
    had_manifest: bool,
    backup_manifest: Path,
    manifest_path: Path,
    had_receipt: bool,
    backup_receipt: Path,
    receipt_path: Path,
    doc_path: Optional[Path],
    doc_original_bytes: Optional[bytes],
    temp_out: Path,
) -> None:
    """Full transactional rollback. NEVER deletes backup if restore fails; reports recovery path."""
    if had_out:
        if backup_out.is_file():
            try:
                os.replace(backup_out, out_path)
            except Exception as exc:
                sys.stderr.write(
                    f"Warning: Failed to restore {out_path} from backup. "
                    f"Backup preserved at: {backup_out} (error: {exc})\n"
                )
    else:
        if out_path.exists():
            try:
                out_path.unlink()
            except Exception:
                pass

    if had_manifest:
        if backup_manifest.is_file():
            try:
                os.replace(backup_manifest, manifest_path)
            except Exception as exc:
                sys.stderr.write(
                    f"Warning: Failed to restore {manifest_path} from backup. "
                    f"Backup preserved at: {backup_manifest} (error: {exc})\n"
                )
    else:
        if manifest_path.exists():
            try:
                manifest_path.unlink()
            except Exception:
                pass

    if had_receipt:
        if backup_receipt.is_file():
            try:
                os.replace(backup_receipt, receipt_path)
            except Exception as exc:
                sys.stderr.write(
                    f"Warning: Failed to restore {receipt_path} from backup. "
                    f"Backup preserved at: {backup_receipt} (error: {exc})\n"
                )
    else:
        if receipt_path.exists():
            try:
                receipt_path.unlink()
            except Exception:
                pass

    if doc_path and doc_original_bytes is not None:
        try:
            doc_path.write_bytes(doc_original_bytes)
        except Exception as exc:
            sys.stderr.write(f"Warning: Failed to restore document content: {exc}\n")

    if temp_out.exists():
        try:
            temp_out.unlink()
        except Exception:
            pass


def handle_render(args: argparse.Namespace) -> int:
    """Handle CLI render sub-command with staging, full transactional rollback, and structured error handling.

    Preserves existing output artifact, manifest, and document if document is missing or finalize/bind fails.
    On fresh failure, deletes newly staged artifacts and restores document bytes.
    Binds document only after successful artifact publication.
    Explicitly excludes candidate and output files from source fingerprinting to prevent self-stale.
    """
    try:
        project_root, cand_path, out_path, doc_path, doc_original_bytes = _prepare_render_paths(args)
    except FileNotFoundError as fnf:
        sys.stderr.write(f"Error: {fnf}\n")
        return 1
    except Exception as exc:
        sys.stderr.write(f"Error validating render arguments: {exc}\n")
        return 1

    out_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path = out_path.with_suffix(".manifest.json")
    receipt_path = out_path.with_suffix(".receipt.json")

    temp_out = out_path.parent / f".tmp.{out_path.stem}.{uuid.uuid4().hex}.html"
    backup_out = out_path.parent / f".bak.{out_path.stem}.{uuid.uuid4().hex}.html"
    backup_manifest = out_path.parent / f".bak.{manifest_path.stem}.{uuid.uuid4().hex}.json"
    backup_receipt = out_path.parent / f".bak.{receipt_path.stem}.{uuid.uuid4().hex}.json"

    had_out = out_path.is_file()
    had_manifest = manifest_path.is_file()
    had_receipt = receipt_path.is_file()

    try:
        result = run_finalize(
            diagram_type=args.type,
            candidate_path=cand_path,
            output_path=temp_out,
            quality=args.quality,
            repo_root=project_root,
        )

        if not result.status or not temp_out.is_file():
            if temp_out.exists():
                temp_out.unlink()
            print(json.dumps(result.receipt if isinstance(result.receipt, dict) else {"ok": False}, indent=2))
            return 1

        receipt = dict(result.receipt) if isinstance(result.receipt, dict) else {}

        if had_out:
            shutil.copy2(out_path, backup_out)
        if had_manifest:
            shutil.copy2(manifest_path, backup_manifest)
        if had_receipt:
            shutil.copy2(receipt_path, backup_receipt)

        _promote_staged_artifacts(temp_out, out_path)
        atomic_delivery(receipt_path, json.dumps(receipt, indent=2, ensure_ascii=False))

        response = dict(receipt)
        response["published_artifact"] = str(out_path)
        response["artifact_path"] = str(out_path)
        response["receipt_path"] = str(receipt_path)

        if not doc_path:
            response["binding"] = "unbound"
            response["binding_status"] = "artifact_unbound"
            if had_out and backup_out.exists():
                backup_out.unlink()
            print(json.dumps(response, indent=2))
            return 0

        _deliver_render_manifest(
            project_root=project_root,
            doc_path=doc_path,
            cand_path=cand_path,
            out_path=out_path,
            manifest_path=manifest_path,
            receipt=receipt,
            evidence_kind=args.evidence_kind or "planned",
            request=args.request,
            lane=args.lane,
        )

        if had_out and backup_out.exists():
            backup_out.unlink()
        if had_manifest and backup_manifest.exists():
            backup_manifest.unlink()
        if had_receipt and backup_receipt.exists():
            backup_receipt.unlink()

        response["binding"] = "bound"
        response["binding_status"] = "registered"
        response["manifest_path"] = str(manifest_path)
        response["document_bound"] = str(doc_path)
        print(json.dumps(response, indent=2))
        return 0

    except Exception as proc_exc:
        _rollback_render_transaction(
            had_out=had_out,
            backup_out=backup_out,
            out_path=out_path,
            had_manifest=had_manifest,
            backup_manifest=backup_manifest,
            manifest_path=manifest_path,
            had_receipt=had_receipt,
            backup_receipt=backup_receipt,
            receipt_path=receipt_path,
            doc_path=doc_path,
            doc_original_bytes=doc_original_bytes,
            temp_out=temp_out,
        )
        sys.stderr.write(f"Error during render publication: {proc_exc}\n")
        return 1


def handle_open(args: argparse.Namespace) -> int:
    """Handle CLI open sub-command."""
    try:
        ok = open_artifact(args.file_path)
        return 0 if ok else 1
    except Exception as exc:
        sys.stderr.write(f"Error opening artifact: {exc}\n")
        return 1


def handle_bridge(args: argparse.Namespace) -> int:
    """Handle CLI bridge sub-command with structured error handling."""
    try:
        ir = graphify_to_archify(
            graph_json_path=args.graph,
            focus_community=args.community,
            max_nodes=args.max_nodes,
            evidence_kind=args.evidence_kind,
        )
        content = json.dumps(ir, indent=2, ensure_ascii=False)
        atomic_delivery(args.out, content)

        selected_ids = [c["id"] for c in ir.get("components", []) if c.get("id")]
        cov = graph_coverage(args.graph, selected_ids=selected_ids)
        sidecar_path = Path(args.out).with_suffix(".coverage.json")
        atomic_delivery(sidecar_path, json.dumps(cov, indent=2, ensure_ascii=False))

        print(f"Archify JSON-IR generated: {args.out}")
        print(f"Coverage sidecar generated: {sidecar_path}")
        return 0
    except (ValueError, OSError, json.JSONDecodeError, FileNotFoundError) as exc:
        sys.stderr.write(f"Error during bridge conversion: {exc}\n")
        return 1
    except Exception as exc:
        sys.stderr.write(f"Unexpected error during bridge conversion: {exc}\n")
        return 1


def handle_test_bridge(args: argparse.Namespace) -> int:
    """Handle CLI test-bridge sub-command."""
    try:
        ok = test_bridge()
        return 0 if ok else 1
    except Exception as exc:
        sys.stderr.write(f"Test failed: {exc}\n")
        return 1


def handle_sync_master(args: argparse.Namespace) -> int:
    """Handle CLI sync-master sub-command with structured error handling."""
    try:
        ok = sync_master(
            model=args.model,
            project=args.project,
            out=args.out,
            graph_path=args.graph,
            max_nodes=args.max_nodes,
            quality=args.quality,
        )
        return 0 if ok else 1
    except (ValueError, OSError, json.JSONDecodeError, FileNotFoundError) as exc:
        sys.stderr.write(f"Error during sync-master: {exc}\n")
        return 1
    except Exception as exc:
        sys.stderr.write(f"Unexpected error during sync-master: {exc}\n")
        return 1


def handle_status(args: argparse.Namespace) -> int:
    """Handle CLI status sub-command."""
    try:
        res = check_master_status(project=args.project)
        print(json.dumps(res, indent=2))
        return 0 if res.get("status") == "current" else 1
    except Exception as exc:
        sys.stderr.write(f"Error inspecting status: {exc}\n")
        return 1


def handle_verify(args: argparse.Namespace) -> int:
    """Handle CLI verify sub-command."""
    try:
        res = verify_document_and_manifest(
            document=args.document,
            manifest=args.manifest,
            project=args.project,
        )
        print(json.dumps(res, indent=2))
        return 0 if res.get("status") == "current" else 1
    except Exception as exc:
        sys.stderr.write(f"Error during verify: {exc}\n")
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="TDQ Archify Adapter CLI — orchestrate diagram generation, model bridge, and bundle lifecycle."
    )
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # check
    subparsers.add_parser("check", help="Check Node.js and Archify environment")

    # render
    render_parser = subparsers.add_parser(
        "render", help="Render diagram to standalone HTML via finalize"
    )
    render_parser.add_argument(
        "--type", required=True, help="Diagram type (workflow, architecture, sequence, ...)"
    )
    render_parser.add_argument(
        "--candidate", required=True, help="Path to input candidate JSON"
    )
    render_parser.add_argument(
        "--out", required=True, help="Path to output HTML artifact"
    )
    render_parser.add_argument(
        "--quality", default="showcase", choices=["standard", "showcase"], help="Rendering quality"
    )
    render_parser.add_argument(
        "--repo-root", "--project", dest="repo_root", default=None, help="Root path of target repository"
    )
    render_parser.add_argument(
        "--document", default=None, help="Path to document to bind (markdown)"
    )
    render_parser.add_argument(
        "--request", default=None, help="Request slug (e.g. 2026-10-24-2348-hoan-thien-archify)"
    )
    render_parser.add_argument(
        "--lane", default=None, help="Lane identifier (full, quick)"
    )
    render_parser.add_argument(
        "--evidence-kind", default="planned", help="Evidence kind (planned, working-tree, committed, partial)"
    )

    # open
    open_parser = subparsers.add_parser(
        "open", help="Open artifact safely in default browser"
    )
    open_parser.add_argument("file_path", help="Path to file to open")

    # bridge
    bridge_parser = subparsers.add_parser(
        "bridge", help="Convert Graphify graph.json to Archify JSON-IR and coverage sidecar"
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
    bridge_parser.add_argument(
        "--evidence-kind", default="working-tree", help="Evidence kind (default: working-tree)"
    )

    # test-bridge
    subparsers.add_parser(
        "test-bridge", help="Self-test graphify-to-archify conversion logic"
    )

    # sync-master
    sync_parser = subparsers.add_parser(
        "sync-master", help="Synchronize master architecture bundle"
    )
    sync_parser.add_argument(
        "--model", default=None, help="Path to master model JSON (default: docs/architecture/master.model.json)"
    )
    sync_parser.add_argument(
        "--project", default=None, help="Target project root directory"
    )
    sync_parser.add_argument(
        "--out", default=None, help="Output destination directory (default: docs/architecture)"
    )
    sync_parser.add_argument(
        "--quality", default="showcase", choices=["standard", "showcase"], help="Rendering quality"
    )
    sync_parser.add_argument(
        "--graph", default=None, help="Path to input graph.json (legacy mode)"
    )
    sync_parser.add_argument(
        "--max-nodes", type=int, default=25, help="Maximum number of nodes (legacy mode)"
    )

    # status
    status_parser = subparsers.add_parser(
        "status", help="Inspect status and freshness of master architecture"
    )
    status_parser.add_argument(
        "--project", default=None, help="Target project root directory"
    )

    # verify
    verify_parser = subparsers.add_parser(
        "verify", help="Verify document binding and manifest integrity"
    )
    verify_parser.add_argument(
        "--document", required=True, help="Path to document file (markdown)"
    )
    verify_parser.add_argument(
        "--manifest", required=True, help="Path to manifest JSON file"
    )
    verify_parser.add_argument(
        "--project", default=None, help="Target project root directory"
    )

    args = parser.parse_args()

    handlers = {
        "check": handle_check,
        "render": handle_render,
        "open": handle_open,
        "bridge": handle_bridge,
        "test-bridge": handle_test_bridge,
        "sync-master": handle_sync_master,
        "status": handle_status,
        "verify": handle_verify,
    }

    handler = handlers.get(args.command)
    if handler is not None:
        return handler(args)

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
