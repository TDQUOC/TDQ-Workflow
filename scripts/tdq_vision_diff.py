#!/usr/bin/env python3
"""Visual regression diff engine and dual report generator (Markdown + Interactive HTML).

Compares a design reference image (--source or --figma-url) against a rendered screenshot (--dist)
using Pillow:
  1. Canvas Padding / Letterboxing (`normalize_canvas`) so aspect ratios never distort.
  2. Dynamic region masking (`apply_ignore_mask` via `--ignore-boxes`).
  3. Subpixel antialiasing tolerance (`--color-tolerance`) and grid-connected bounding box
     clustering (`find_bounding_boxes`) labeled `[1]`, `[2]`, ...
  4. Outputs `diff_highlight.png`, `metrics.json`, `rounds_history.json`, `<slug>.md`, and a
     zero-dependency interactive `<slug>.html` report (Before/After Split Slider, Overlay
     Onion-Skin & Blink 2Hz, Interactive Bounding Box Explorer, and Multi-round Progress Timeline).

Exit codes:
  0 - Visual diff passed (mismatch_rate <= threshold)
  1 - Visual diff failed (mismatch_rate > threshold; reports still generated for auto-fix loop)
  2 - Invalid CLI arguments or unreadable input image files
  3 - Missing FIGMA_TOKEN or failed Figma REST API access (triggers human-in-the-loop pause)
"""
from __future__ import annotations

import argparse
import base64
from collections import deque
from datetime import datetime
import html
import io
import json
import os
from pathlib import Path
import re
import sys
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.join(ROOT, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
import utf8_io  # noqa: E402,F401 — imported for its side effect: stdout/stderr become UTF-8

from PIL import Image, ImageChops, ImageDraw  # noqa: E402

EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_USAGE = 2
EXIT_FIGMA = 3

RED_BORDER = (255, 32, 32, 255)
RED_TINT = (255, 32, 32, 110)
FIGMA_PAUSE_HINT = (
    'Run: python3 scripts/tdq_state.py pause --loai dau-vao-user '
    '--ly-do "Missing FIGMA_TOKEN or inaccessible Figma URL"'
)


class FigmaAccessError(Exception):
    """Raised when Figma token is missing or Figma REST API fails to export the node image."""


def log_event(message: str) -> None:
    """Write an ISO-8601 timestamped diagnostic message to stderr unless TDQ_LOG=0."""
    if os.environ.get("TDQ_LOG", "1") == "0":
        return
    stamp = datetime.now().replace(microsecond=0).isoformat()
    print(f"[{stamp}] tdq_vision_diff: {message}", file=sys.stderr)


def parse_figma_url(figma_url: str) -> tuple[str, str]:
    """Extract (file_key, node_id) from a Figma design/file/proto URL."""
    parsed = urllib_parse.urlsplit(figma_url.strip())
    match = re.search(r"/(?:design|file|proto)/([A-Za-z0-9]+)", parsed.path)
    if not match:
        raise FigmaAccessError(f"Cannot extract file_key from Figma URL: {figma_url}")
    file_key = match.group(1)
    query = urllib_parse.parse_qs(parsed.query)
    raw_nodes = query.get("node-id", [])
    if not raw_nodes or not raw_nodes[0].strip():
        raise FigmaAccessError(f"Missing node-id query parameter in Figma URL: {figma_url}")
    node_id = urllib_parse.unquote(raw_nodes[0].strip()).replace("-", ":")
    return file_key, node_id


def _open_url_bytes(req_or_url, opener=None) -> bytes:
    """Read raw bytes from a URL or Request using the provided opener or urllib.request.urlopen."""
    open_fn = opener or urllib_request.urlopen
    with open_fn(req_or_url, timeout=30) as response:
        return response.read()


def _resolve_figma_image_url(payload: dict, node_id: str) -> str:
    """Extract the rendered PNG URL for node_id from Figma's JSON payload."""
    images = payload.get("images") or {}
    candidates = (node_id, node_id.replace(":", "-"))
    for key in candidates:
        if images.get(key):
            return str(images[key])
    raise FigmaAccessError(f"Figma API did not return an image URL for node {node_id}")


def fetch_figma_source(
    figma_url: str,
    out_path: Path,
    token: str | None = None,
    opener=None,
) -> Path:
    """Download a reference PNG from Figma REST API into out_path, or raise FigmaAccessError."""
    resolved_token = (token if token is not None else os.environ.get("FIGMA_TOKEN", "")).strip()
    if not resolved_token:
        log_event(f"Missing FIGMA_TOKEN for --figma-url. {FIGMA_PAUSE_HINT}")
        raise FigmaAccessError(f"Missing FIGMA_TOKEN. {FIGMA_PAUSE_HINT}")

    file_key, node_id = parse_figma_url(figma_url)
    encoded_node = urllib_parse.quote(node_id, safe="")
    api_url = f"https://api.figma.com/v1/images/{file_key}?ids={encoded_node}&format=png"
    req = urllib_request.Request(api_url, headers={"X-Figma-Token": resolved_token})
    try:
        raw_json = _open_url_bytes(req, opener=opener)
        payload = json.loads(raw_json.decode("utf-8"))
        image_url = _resolve_figma_image_url(payload, node_id)
        png_bytes = _open_url_bytes(image_url, opener=opener)
    except (urllib_error.URLError, urllib_error.HTTPError, OSError, ValueError, FigmaAccessError) as exc:
        log_event(f"Figma API fetch failed ({exc}). {FIGMA_PAUSE_HINT}")
        raise FigmaAccessError(f"Failed to fetch Figma node image: {exc}") from exc

    target = Path(out_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(png_bytes)
    log_event(f"Fetched Figma node {node_id} from file {file_key} -> {target}")
    return target


def normalize_canvas(
    src_img: Image.Image,
    dist_img: Image.Image,
    fill_color: tuple[int, int, int, int] = (0, 0, 0, 0),
) -> tuple[Image.Image, Image.Image]:
    """Pad both images to a shared (max_w, max_h) RGBA canvas at (0, 0) without resizing."""
    src_rgba = src_img.convert("RGBA")
    dist_rgba = dist_img.convert("RGBA")
    canvas_w = max(src_rgba.width, dist_rgba.width)
    canvas_h = max(src_rgba.height, dist_rgba.height)

    src_canvas = Image.new("RGBA", (canvas_w, canvas_h), fill_color)
    dist_canvas = Image.new("RGBA", (canvas_w, canvas_h), fill_color)
    src_canvas.paste(src_rgba, (0, 0))
    dist_canvas.paste(dist_rgba, (0, 0))
    return src_canvas, dist_canvas


def parse_ignore_boxes(raw: str) -> list[tuple[int, int, int, int]]:
    """Parse 'x,y,w,h;x2,y2,w2,h2' into a list of (x, y, w, h) integer tuples."""
    if not raw or not raw.strip():
        return []
    boxes: list[tuple[int, int, int, int]] = []
    for item in raw.split(";"):
        token = item.strip()
        if not token:
            continue
        parts = [p.strip() for p in token.split(",")]
        if len(parts) != 4:
            raise ValueError(f"Invalid ignore box '{token}'; expected 'x,y,w,h'")
        x, y, w, h = (int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]))
        if w < 0 or h < 0:
            raise ValueError(f"Negative width/height in ignore box '{token}'")
        boxes.append((x, y, w, h))
    return boxes


def apply_ignore_mask(
    diff_mask: Image.Image,
    ignore_boxes: list[tuple[int, int, int, int]] | None,
) -> int:
    """Zero out ignored rectangles on diff_mask in-place and return the count of ignored pixels."""
    if not ignore_boxes:
        return 0
    width, height = diff_mask.size
    ignore_tracker = Image.new("L", (width, height), 0)
    for x, y, w, h in ignore_boxes:
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(width, x + w), min(height, y + h)
        if x1 > x0 and y1 > y0:
            diff_mask.paste(0, (x0, y0, x1, y1))
            ignore_tracker.paste(1, (x0, y0, x1, y1))
    return int(ignore_tracker.histogram()[1])


def compute_diff_mask(
    src_norm: Image.Image,
    dist_norm: Image.Image,
    color_tolerance: int = 12,
    ignore_boxes: list[tuple[int, int, int, int]] | None = None,
) -> tuple[Image.Image, int, int]:
    """Compute binary diff mask ('L'), mismatch pixel count, and effective total pixel count."""
    diff_rgba = ImageChops.difference(src_norm.convert("RGBA"), dist_norm.convert("RGBA"))
    r_ch, g_ch, b_ch, a_ch = diff_rgba.split()
    max_rg = ImageChops.lighter(r_ch, g_ch)
    max_ba = ImageChops.lighter(b_ch, a_ch)
    max_delta = ImageChops.lighter(max_rg, max_ba)

    tol = max(0, min(255, int(color_tolerance)))
    lut = [255 if idx > tol else 0 for idx in range(256)]
    diff_mask = max_delta.point(lut, mode="L")

    ignored_pixels = apply_ignore_mask(diff_mask, ignore_boxes)
    mismatch_pixels = int(diff_mask.histogram()[255])
    total_pixels = max(1, (src_norm.width * src_norm.height) - ignored_pixels)
    return diff_mask, mismatch_pixels, total_pixels


def _collect_active_grid_cells(
    diff_mask: Image.Image,
    grid_size: int,
) -> dict[tuple[int, int], tuple[int, int, int, int]]:
    """Map each grid cell (gx, gy) containing diff pixels to its tight pixel box (x0, y0, x1, y1)."""
    width, height = diff_mask.size
    step = max(1, int(grid_size))
    active: dict[tuple[int, int], tuple[int, int, int, int]] = {}
    cols = (width + step - 1) // step
    rows = (height + step - 1) // step

    for gy in range(rows):
        y0 = gy * step
        y1 = min(height, y0 + step)
        for gx in range(cols):
            x0 = gx * step
            x1 = min(width, x0 + step)
            cell_bbox = diff_mask.crop((x0, y0, x1, y1)).getbbox()
            if cell_bbox is not None:
                active[(gx, gy)] = (
                    x0 + cell_bbox[0],
                    y0 + cell_bbox[1],
                    x0 + cell_bbox[2],
                    y0 + cell_bbox[3],
                )
    return active


def _bfs_cluster_bounds(
    start_cell: tuple[int, int],
    active: dict[tuple[int, int], tuple[int, int, int, int]],
    visited: set[tuple[int, int]],
) -> tuple[int, int, int, int]:
    """Run 8-connected BFS from start_cell to compute the union pixel bounds of a cluster."""
    queue = deque([start_cell])
    visited.add(start_cell)
    min_x0, min_y0, max_x1, max_y1 = active[start_cell]

    while queue:
        cx, cy = queue.popleft()
        bx0, by0, bx1, by1 = active[(cx, cy)]
        min_x0, min_y0 = min(min_x0, bx0), min(min_y0, by0)
        max_x1, max_y1 = max(max_x1, bx1), max(max_y1, by1)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                neighbor = (cx + dx, cy + dy)
                if neighbor in active and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
    return min_x0, min_y0, max_x1, max_y1


def find_bounding_boxes(
    diff_mask: Image.Image,
    grid_size: int = 16,
    min_area: int = 16,
) -> list[dict]:
    """Cluster mismatched grid cells via 8-connected BFS and return numbered bounding boxes."""
    active = _collect_active_grid_cells(diff_mask, grid_size=grid_size)
    visited: set[tuple[int, int]] = set()
    raw_boxes: list[tuple[int, int, int, int]] = []

    for cell in sorted(active.keys(), key=lambda item: (item[1], item[0])):
        if cell in visited:
            continue
        x0, y0, x1, y1 = _bfs_cluster_bounds(cell, active, visited)
        w, h = x1 - x0, y1 - y0
        if w * h >= max(1, int(min_area)):
            raw_boxes.append((x0, y0, w, h))

    raw_boxes.sort(key=lambda b: (b[1], b[0]))
    return [
        {"id": idx, "x": x, "y": y, "w": w, "h": h, "area": w * h}
        for idx, (x, y, w, h) in enumerate(raw_boxes, start=1)
    ]


def render_highlight_image(
    dist_norm: Image.Image,
    diff_mask: Image.Image,
    boxes: list[dict],
) -> Image.Image:
    """Render semi-transparent red tint over diff pixels and draw numbered [1], [2] bounding boxes."""
    base = dist_norm.convert("RGBA").copy()
    tint_alpha = diff_mask.point([RED_TINT[3] if i > 0 else 0 for i in range(256)], mode="L")
    tint_layer = Image.new("RGBA", base.size, (RED_TINT[0], RED_TINT[1], RED_TINT[2], 0))
    tint_layer.putalpha(tint_alpha)
    highlighted = Image.alpha_composite(base, tint_layer)

    draw = ImageDraw.Draw(highlighted)
    for box in boxes:
        x, y, w, h = box["x"], box["y"], box["w"], box["h"]
        x1 = max(x, x + w - 1)
        y1 = max(y, y + h - 1)
        draw.rectangle([x, y, x1, y1], outline=RED_BORDER, width=2)
        label = f"[{box['id']}]"
        badge_w = max(22, 8 * len(label))
        badge_y = y - 14 if y >= 14 else y
        draw.rectangle([x, badge_y, x + badge_w, badge_y + 13], fill=RED_BORDER)
        draw.text((x + 3, badge_y + 1), label, fill=(255, 255, 255, 255))
    return highlighted


def _image_ref_for_html(image_path: Path, out_dir: Path, embed_base64: bool) -> str:
    """Return either a data:image/png;base64 URI or a relative POSIX path from out_dir."""
    if embed_base64:
        with Image.open(image_path) as img:
            buf = io.BytesIO()
            img.save(buf, format="PNG")
        encoded = base64.b64encode(buf.getvalue()).decode("ascii")
        return f"data:image/png;base64,{encoded}"
    try:
        rel = os.path.relpath(image_path, out_dir)
    except ValueError:
        rel = str(image_path)
    return rel.replace("\\", "/")


def _update_rounds_history(out_dir: Path, metrics: dict) -> list[dict]:
    """Update rounds_history.json in out_dir with the current round entry and return sorted history."""
    history_path = out_dir / "rounds_history.json"
    history: list[dict] = []
    if history_path.is_file():
        try:
            loaded = json.loads(history_path.read_text(encoding="utf-8"))
            if isinstance(loaded, list):
                history = [row for row in loaded if isinstance(row, dict)]
        except (OSError, ValueError):
            history = []

    entry = {
        "round": metrics["round"],
        "mismatch_rate": metrics["mismatch_rate"],
        "mismatch_pixels": metrics["mismatch_pixels"],
        "passed": metrics["passed"],
        "box_count": len(metrics["bounding_boxes"]),
    }
    history = [row for row in history if row.get("round") != entry["round"]]
    history.append(entry)
    history.sort(key=lambda item: int(item.get("round", 1)))
    history_path.write_text(json.dumps(history, indent=2) + "\n", encoding="utf-8")
    return history


def _render_markdown_report(
    slug: str,
    metrics: dict,
    src_ref: str,
    dist_ref: str,
    diff_ref: str,
    history: list[dict],
) -> str:
    """Build the Markdown visual diff report for AI agents and code review."""
    status = "PASS" if metrics["passed"] else "FAIL"
    rate_pct = metrics["mismatch_rate"] * 100.0
    thresh_pct = metrics["threshold"] * 100.0
    w, h = metrics["canvas_size"]
    lines = [
        f"# Visual Diff Report — `{slug}` ({status})",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Status | **{status}** |",
        f"| Round | `{metrics['round']}` |",
        f"| Mismatch Rate | `{rate_pct:.2f}%` ({metrics['mismatch_pixels']} / {metrics['total_pixels']} px) |",
        f"| Threshold | `{thresh_pct:.2f}%` |",
        f"| Color Tolerance | `{metrics['color_tolerance']}` |",
        f"| Canvas Size | `{w}x{h}` |",
        f"| Bounding Boxes | `{len(metrics['bounding_boxes'])}` |",
        "",
        "## Visual Artifacts",
        "",
        "| Source Reference | Rendered Dist | Diff Highlight |",
        "|---|---|---|",
        f"| `{src_ref}` | `{dist_ref}` | `{diff_ref}` |",
        "",
        "## Bounding Boxes (`[1]`, `[2]`, ...)",
        "",
    ]
    if not metrics["bounding_boxes"]:
        lines.append("No mismatch bounding boxes detected.")
    else:
        lines.extend([
            "| Box | Coordinates (`x, y, w, h`) | Area (`px`) |",
            "|---|---|---|",
        ])
        for box in metrics["bounding_boxes"]:
            lines.append(
                f"| `[{box['id']}]` | `{box['x']}, {box['y']}, {box['w']}, {box['h']}` | `{box['area']}` |"
            )

    lines.extend(["", "## Multi-round Progress Timeline", ""])
    lines.extend(["| Round | Mismatch Rate | Boxes | Status |", "|---|---|---|---|"])
    for item in history:
        r_status = "PASS" if item["passed"] else "FAIL"
        lines.append(
            f"| Round {item['round']} | `{item['mismatch_rate'] * 100.0:.2f}%` | "
            f"`{item['box_count']}` | {r_status} |"
        )
    return "\n".join(lines) + "\n"


def _render_html_report(
    slug: str,
    metrics: dict,
    src_uri: str,
    dist_uri: str,
    diff_uri: str,
    history: list[dict],
) -> str:
    """Build the standalone interactive HTML report from a static template."""
    status = "PASS" if metrics["passed"] else "FAIL"
    rate_pct = f"{metrics['mismatch_rate'] * 100.0:.2f}%"
    thresh_pct = f"{metrics['threshold'] * 100.0:.2f}%"
    w, h = metrics["canvas_size"]

    box_rows = []
    overlay_divs = []
    for box in metrics["bounding_boxes"]:
        bid = box["id"]
        bx, by, bw, bh = box["x"], box["y"], box["w"], box["h"]
        left_pct = (bx / max(1, w)) * 100.0
        top_pct = (by / max(1, h)) * 100.0
        width_pct = (bw / max(1, w)) * 100.0
        height_pct = (bh / max(1, h)) * 100.0
        box_rows.append(
            f'<tr class="box-row" data-box-id="{bid}" onclick="focusBox({bid})">'
            f"<td><strong>[{bid}]</strong></td>"
            f"<td>x={bx}, y={by}, w={bw}, h={bh}</td>"
            f"<td>{box['area']} px</td></tr>"
        )
        overlay_divs.append(
            f'<div id="overlay-box-{bid}" class="bbox-overlay" '
            f'style="left:{left_pct:.3f}%;top:{top_pct:.3f}%;width:{width_pct:.3f}%;height:{height_pct:.3f}%;" '
            f'onclick="focusBox({bid})"><span>[{bid}]</span></div>'
        )
    boxes_html = "\n".join(box_rows) or '<tr><td colspan="3">No mismatch regions detected.</td></tr>'
    overlays_html = "\n".join(overlay_divs)

    timeline_items = []
    for item in history:
        r_state = "PASS" if item["passed"] else "FAIL"
        timeline_items.append(
            f'<div class="round-pill {r_state.lower()}">'
            f"<strong>Round {item['round']}</strong>: {item['mismatch_rate'] * 100.0:.2f}% "
            f"({item['box_count']} boxes) &middot; {r_state}</div>"
        )
    timeline_html = "\n".join(timeline_items)
    esc_slug = html.escape(slug)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Vision Test Loop Report - {esc_slug}</title>
<style>
  body {{ font-family: system-ui, -apple-system, sans-serif; margin: 0; padding: 24px; background: #0f172a; color: #e2e8f0; }}
  h1, h2 {{ margin-top: 0; }}
  .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }}
  .badge {{ padding: 6px 12px; border-radius: 6px; font-weight: 700; }}
  .badge.pass {{ background: #166534; color: #dcfce7; }}
  .badge.fail {{ background: #991b1b; color: #fee2e2; }}
  .panel {{ background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 16px; margin-bottom: 20px; }}
  .controls {{ display: flex; flex-wrap: wrap; gap: 16px; align-items: center; margin-bottom: 12px; }}
  .stage {{ position: relative; max-width: 100%; overflow: hidden; border: 1px solid #475569; background: #020617; }}
  .stage img {{ display: block; width: 100%; height: auto; user-select: none; }}
  .clip-layer {{ position: absolute; inset: 0; overflow: hidden; }}
  .bbox-overlay {{ position: absolute; border: 2px solid #ef4444; box-sizing: border-box; cursor: pointer; transition: box-shadow 0.2s, transform 0.2s; }}
  .bbox-overlay span {{ background: #ef4444; color: #fff; font-size: 11px; font-weight: 700; padding: 1px 4px; }}
  .bbox-overlay.active {{ box-shadow: 0 0 0 4px #facc15, 0 0 18px #ef4444; z-index: 10; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th, td {{ padding: 8px 10px; border-bottom: 1px solid #334155; text-align: left; }}
  tr.box-row {{ cursor: pointer; }}
  tr.box-row:hover, tr.box-row.active {{ background: #334155; }}
  .timeline {{ display: flex; gap: 12px; flex-wrap: wrap; }}
  .round-pill {{ padding: 8px 12px; border-radius: 8px; background: #334155; }}
  .round-pill.pass {{ border-left: 4px solid #22c55e; }}
  .round-pill.fail {{ border-left: 4px solid #ef4444; }}
  button {{ background: #2563eb; color: #fff; border: none; padding: 6px 12px; border-radius: 6px; cursor: pointer; }}
</style>
</head>
<body>
  <div class="header">
    <h1>Vision Test Loop Report &mdash; {esc_slug}</h1>
    <span class="badge {status.lower()}">{status} &middot; {rate_pct} (threshold {thresh_pct})</span>
  </div>

  <div class="panel">
    <h2>Multi-round Progress Timeline</h2>
    <div class="timeline">{timeline_html}</div>
  </div>

  <div class="panel">
    <h2>Before/After Split Slider &amp; Overlay Onion-Skin</h2>
    <div class="controls">
      <label>Before/After Split Slider:
        <input id="split-slider" type="range" min="0" max="100" value="50" oninput="updateSplit(this.value)">
      </label>
      <label>Overlay Onion-Skin Opacity:
        <input id="onion-slider" type="range" min="0" max="100" value="0" oninput="updateOnion(this.value)">
      </label>
      <button id="blink-btn" type="button" onclick="toggleBlink()">Blink 2Hz</button>
    </div>
    <div id="compare-stage" class="stage" data-canvas="{w}x{h}">
      <img id="dist-img" src="{dist_uri}" alt="Rendered Dist">
      <div id="source-clip" class="clip-layer" style="clip-path: inset(0 50% 0 0);">
        <img id="src-img" src="{src_uri}" alt="Design Source">
      </div>
      <div id="onion-layer" class="clip-layer" style="opacity: 0; pointer-events: none;">
        <img src="{diff_uri}" alt="Diff Highlight Overlay">
      </div>
      {overlays_html}
    </div>
  </div>

  <div class="panel">
    <h2>Interactive Bounding Box Explorer</h2>
    <table>
      <thead><tr><th>Box ID</th><th>Coordinates</th><th>Area</th></tr></thead>
      <tbody>{boxes_html}</tbody>
    </table>
  </div>

<script>
  let blinkTimer = null;
  let blinkState = false;
  function updateSplit(val) {{
    const rightInset = 100 - Number(val);
    document.getElementById('source-clip').style.clipPath = 'inset(0 ' + rightInset + '% 0 0)';
  }}
  function updateOnion(val) {{
    document.getElementById('onion-layer').style.opacity = String(Number(val) / 100);
  }}
  function toggleBlink() {{
    if (blinkTimer) {{
      clearInterval(blinkTimer);
      blinkTimer = null;
      updateSplit(document.getElementById('split-slider').value);
      return;
    }}
    blinkTimer = setInterval(function() {{
      blinkState = !blinkState;
      document.getElementById('source-clip').style.clipPath = blinkState ? 'inset(0 0% 0 0)' : 'inset(0 100% 0 0)';
    }}, 500);
  }}
  function focusBox(id) {{
    document.querySelectorAll('.bbox-overlay, .box-row').forEach(function(el) {{ el.classList.remove('active'); }});
    const overlay = document.getElementById('overlay-box-' + id);
    const row = document.querySelector('.box-row[data-box-id="' + id + '"]');
    if (overlay) {{
      overlay.classList.add('active');
      overlay.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
    }}
    if (row) {{ row.classList.add('active'); }}
  }}
</script>
</body>
</html>
"""


def write_reports(
    out_dir: Path,
    slug: str,
    metrics: dict,
    highlight_img: Image.Image,
    src_path: Path,
    dist_path: Path,
    embed_base64: bool = False,
) -> dict[str, Path]:
    """Write diff_highlight.png, metrics.json, rounds_history.json, <slug>.md, and <slug>.html."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    diff_path = out_dir / "diff_highlight.png"
    metrics_path = out_dir / "metrics.json"
    md_path = out_dir / f"{slug}.md"
    html_path = out_dir / f"{slug}.html"

    highlight_img.save(diff_path, format="PNG")
    metrics_path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    history = _update_rounds_history(out_dir, metrics)

    src_rel = _image_ref_for_html(src_path, out_dir, embed_base64=False)
    dist_rel = _image_ref_for_html(dist_path, out_dir, embed_base64=False)
    diff_rel = _image_ref_for_html(diff_path, out_dir, embed_base64=False)

    md_content = _render_markdown_report(slug, metrics, src_rel, dist_rel, diff_rel, history)
    md_path.write_text(md_content, encoding="utf-8")

    src_uri = _image_ref_for_html(src_path, out_dir, embed_base64=embed_base64)
    dist_uri = _image_ref_for_html(dist_path, out_dir, embed_base64=embed_base64)
    diff_uri = _image_ref_for_html(diff_path, out_dir, embed_base64=embed_base64)
    html_content = _render_html_report(slug, metrics, src_uri, dist_uri, diff_uri, history)
    html_path.write_text(html_content, encoding="utf-8")

    return {
        "diff_highlight": diff_path,
        "metrics": metrics_path,
        "markdown": md_path,
        "html": html_path,
    }


def _build_parser() -> argparse.ArgumentParser:
    """Create the argument parser for tdq_vision_diff CLI."""
    parser = argparse.ArgumentParser(
        prog="tdq_vision_diff.py",
        description="Compare design source vs rendered dist image and generate visual diff reports.",
    )
    parser.add_argument("--source", default="", help="Path to reference design image (PNG/JPG).")
    parser.add_argument("--figma-url", default="", help="Figma node URL to fetch reference image.")
    parser.add_argument("--dist", required=True, help="Path to rendered screenshot image.")
    parser.add_argument("--out-dir", required=True, help="Directory for output reports and artifacts.")
    parser.add_argument("--slug", default="vision-report", help="Report filename slug.")
    parser.add_argument("--threshold", type=float, default=0.02, help="Max allowed mismatch_rate (0..1).")
    parser.add_argument("--color-tolerance", type=int, default=12, help="Per-channel delta tolerance (0..255).")
    parser.add_argument("--ignore-boxes", default="", help="Semicolon-separated x,y,w,h regions to ignore.")
    parser.add_argument("--grid-size", type=int, default=16, help="Grid cell size in px for clustering.")
    parser.add_argument("--min-area", type=int, default=16, help="Minimum bounding box area in px.")
    parser.add_argument("--embed-base64", action="store_true", help="Embed images as Base64 data URIs in HTML.")
    parser.add_argument("--round", type=int, default=1, help="Current auto-fix iteration number.")
    return parser


def _resolve_source_path(args: argparse.Namespace, out_dir: Path) -> Path:
    """Resolve local --source path or fetch from --figma-url."""
    if args.figma_url:
        fetched_path = Path(args.source) if args.source else (out_dir / "figma_source.png")
        return fetch_figma_source(args.figma_url, fetched_path)
    if not args.source:
        raise ValueError("Either --source or --figma-url must be provided.")
    src_path = Path(args.source)
    if not src_path.is_file():
        raise FileNotFoundError(f"Source image not found: {src_path}")
    return src_path


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint returning EXIT_PASS (0), EXIT_FAIL (1), EXIT_USAGE (2), or EXIT_FIGMA (3)."""
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return EXIT_USAGE if exc.code != 0 else EXIT_PASS

    out_dir = Path(args.out_dir)
    dist_path = Path(args.dist)

    try:
        src_path = _resolve_source_path(args, out_dir)
    except FigmaAccessError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_FIGMA
    except (ValueError, FileNotFoundError, OSError) as exc:
        log_event(f"Input resolution error: {exc}")
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_USAGE

    if not dist_path.is_file():
        log_event(f"Rendered dist image not found: {dist_path}")
        print(f"ERROR: Rendered dist image not found: {dist_path}", file=sys.stderr)
        return EXIT_USAGE

    try:
        ignore_boxes = parse_ignore_boxes(args.ignore_boxes)
        with Image.open(src_path) as src_raw, Image.open(dist_path) as dist_raw:
            src_norm, dist_norm = normalize_canvas(src_raw, dist_raw)
    except (ValueError, OSError) as exc:
        log_event(f"Failed to load images or parse ignore boxes: {exc}")
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_USAGE

    diff_mask, mismatch_pixels, total_pixels = compute_diff_mask(
        src_norm,
        dist_norm,
        color_tolerance=args.color_tolerance,
        ignore_boxes=ignore_boxes,
    )
    mismatch_rate = round(mismatch_pixels / max(1, total_pixels), 6)
    boxes = find_bounding_boxes(diff_mask, grid_size=args.grid_size, min_area=args.min_area)
    highlight_img = render_highlight_image(dist_norm, diff_mask, boxes)
    passed = mismatch_rate <= args.threshold

    metrics = {
        "passed": passed,
        "mismatch_rate": mismatch_rate,
        "mismatch_pixels": mismatch_pixels,
        "total_pixels": total_pixels,
        "threshold": args.threshold,
        "color_tolerance": args.color_tolerance,
        "round": args.round,
        "canvas_size": [src_norm.width, src_norm.height],
        "bounding_boxes": boxes,
        "ignore_boxes": [list(b) for b in ignore_boxes],
    }
    paths = write_reports(
        out_dir=out_dir,
        slug=args.slug,
        metrics=metrics,
        highlight_img=highlight_img,
        src_path=src_path,
        dist_path=dist_path,
        embed_base64=args.embed_base64,
    )
    log_event(
        f"round={args.round} canvas={src_norm.width}x{src_norm.height} "
        f"mismatch_rate={mismatch_rate:.4f} threshold={args.threshold:.4f} "
        f"boxes={len(boxes)} passed={passed} report={paths['markdown']}"
    )
    return EXIT_PASS if passed else EXIT_FAIL


if __name__ == "__main__":
    sys.exit(main())
