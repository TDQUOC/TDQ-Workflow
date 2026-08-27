#!/usr/bin/env python3
"""Render a feature's mind-map (.md) into one self-contained, two-layer HTML page.

Layer 1 ("nghiep-vu", business) is the human-written outline straight from the
diagram file. Layer 2 ("chi-tiet", detail) is built from `graphify-out/graph.json`:
for each step whose location resolves to a code node, it walks the `calls` /
`indirect_call` edges leaving that node, drawn as a small SVG call graph plus a
readable list carrying each callee's docstring first line.

The shape constants (SLUG_RE, BRANCH_LINE_RE, ...), the log service and the pure
`check_diagram` gate all live in tdq_mindmap.py and are imported from there — this
module never re-defines the diagram shape, it only reads it and draws it.

Usage:
    python3 scripts/mindmap_render.py <file.md> [--graph graph.json] [--sau N] [-o out.html]

Exit codes: 0 done · 1 the diagram fails check_diagram · 2 a path could not be
read or written.
Env: TDQ_LOG=0 turns the log service off (on by default, one ISO-timestamped
line to stderr) — same switch as tdq_mindmap.py.
"""
import argparse
import ast
import html
import itertools
import os
import re
import sys

from tdq_mindmap import (
    EXIT_OK,
    EXIT_VIOLATION,
    EXIT_SYNTAX,
    EXIT_UPDATE,  # noqa: F401 — re-exported for callers that expect the full set
    SLUG_RE,  # noqa: F401 — re-exported, not used directly here
    BRANCH_LINE_RE,
    DEPENDS_LINE_RE,
    STEP_LINE_RE,
    LOCATION_RE,
    UNKNOWN_LOCATION,
    MIND_MAP_DIR_REL,
    FILE_SUFFIX,
    TITLE_LINE_RE,
    STEP_HINT_RE,
    STEP_ERROR_MARK,
    build_link_graph,
    mind_map_dir,
    comment_mask,
    check_diagram,
    read_diagram,
    log_enabled,  # noqa: F401 — re-exported, not called directly here
    _log,
    project_dir,
)

# ------------------------------------------------------------------- constants
# Where the code graph lives, relative to the project root — a plain path, not a
# diagram-shape constant, so it is defined here rather than reused from tdq_mindmap.
GRAPH_PATH_REL = os.path.join("graphify-out", "graph.json")

DEPTH_DEFAULT = 1
COLLAPSE_THRESHOLD = 20  # a step with more calls than this starts closed, click to open

# SVG layout, in user units of the viewBox (see the artifact-diagramming skill).
BOX_W, BOX_H = 190, 26
ROW_H = 36
COL_GAP = 70

# User-facing strings (the rendered page is for a Vietnamese reader; only the
# HTML content is Vietnamese, this module's own code/comments stay English).
TEXT_LAYER_BUTTON_TO_DETAIL = "Xem lớp chi tiết"  # i18n-allow
TEXT_LAYER_BUTTON_TO_BUSINESS = "Xem lớp nghiệp vụ"  # i18n-allow
TEXT_DETAIL_WARNING = (
    "Thứ tự dưới đây là thứ tự VIẾT (theo dòng đặt lời gọi trong file), "  # i18n-allow
    "KHÔNG phải thứ tự CHẠY thực tế lúc thực thi."  # i18n-allow
)
TEXT_NOT_IN_GRAPH = "không tìm thấy trong graph.json — hàm chưa được đồ thị hoá"  # i18n-allow
TEXT_UNKNOWN_LOCATION = "chưa rõ vị trí code"  # i18n-allow
TEXT_NO_CALLS = "không gọi hàm nào khác trong phạm vi đã đồ thị hoá"  # i18n-allow
TEXT_ERROR_BRANCH = "nhánh lỗi"  # i18n-allow
TEXT_DEPENDS_HEADING = "Phụ thuộc"  # i18n-allow
TEXT_FIGCAPTION = "Các lời gọi mà `{name}` phát ra, sắp theo thứ tự dòng trong file."  # i18n-allow
TEXT_COLLAPSE_SUMMARY = "{n} lời gọi — bấm để xem"  # i18n-allow

# Strings for the aggregate page (--tong).
TEXT_TONG_TITLE = "Sơ đồ tổng"  # i18n-allow
TEXT_TONG_HEADING_CAY = "Cây nhánh"  # i18n-allow
TEXT_TONG_CHUA_GAN_NHANH = "Chưa gắn nhánh"  # i18n-allow
TEXT_TONG_HEADING_LUOI = "Lưới phụ thuộc"  # i18n-allow
TEXT_TONG_CHUA_CO_SO_DO = "chưa có sơ đồ"  # i18n-allow
TEXT_TONG_KHONG_CO_CANH = "Không có cạnh phụ thuộc nào."  # i18n-allow
TEXT_TONG_CLAIM = ("Lưới phụ thuộc giữa các feature — mỗi mũi tên trỏ từ feature "  # i18n-allow
                    "phụ thuộc sang feature nó cần")  # i18n-allow


class DiagramInvalid(ValueError):
    """The diagram fails check_diagram; carries the violations for the caller to print."""

    def __init__(self, violations):
        self.violations = list(violations)
        super().__init__("diagram has shape violations, cannot render")


# --------------------------------------------------------------- parse (.md)
class Step:
    """One parsed step: its number, whether it is an error branch, and location."""

    __slots__ = ("num", "is_error", "desc", "file", "func", "location_raw")

    def __init__(self, num, is_error, desc, file, func, location_raw):
        self.num = num
        self.is_error = is_error
        self.desc = desc
        self.file = file
        self.func = func
        self.location_raw = location_raw


def parse_diagram(lines):
    """Structured read of an ALREADY-VALID diagram: title, branch, depends, steps.

    Callers must run check_diagram first (render_feature_page does) — this function
    does not re-validate the shape, it only extracts what check_diagram already
    guarantees is well-formed.
    """
    mask = comment_mask(lines)
    title = None
    branch_top = branch_sub = None
    depends = []
    steps = []
    for i, line in enumerate(lines):
        if mask[i]:
            continue
        if title is None:
            found = TITLE_LINE_RE.match(line)
            if found:
                title = found.group("title")
                continue
        found = BRANCH_LINE_RE.match(line)
        if found:
            branch_top, branch_sub = found.group("top"), found.group("sub")
            continue
        found = DEPENDS_LINE_RE.match(line)
        if found:
            depends.append((found.group("feature"), found.group("reason")))
            continue
        if STEP_HINT_RE.match(line):
            found = STEP_LINE_RE.match(line)
            if not found:
                continue
            loc = found.group("location")
            file = func = None
            if loc and loc != UNKNOWN_LOCATION:
                loc_match = LOCATION_RE.match(loc)
                if loc_match:
                    file, func = loc_match.group("file"), loc_match.group("func")
            steps.append(Step(
                int(found.group("num")), found.group("error") == STEP_ERROR_MARK,
                found.group("desc"), file, func, loc))
    return title, branch_top, branch_sub, depends, steps


# ------------------------------------------------------- flow model (business)
# Roles a node can play in the drawn flow. They decide the SHAPE the renderer
# draws, so exactly one is assigned per node; `la_vao`/`la_ra` keep the plain
# entry/exit facts even when the shape is decided by a stronger role.
ROLE_BUOC = "buoc"            # an ordinary step -> rounded rectangle
ROLE_QUYET_DINH = "quyet-dinh"  # a step that owns an error branch -> diamond
ROLE_NHANH_LOI = "nhanh-loi"    # the error branch itself -> rectangle, error colour
ROLE_VAO = "vao"              # first step of the flow -> pill
ROLE_RA = "ra"                # last step of the main flow -> pill

TEXT_CANH_OK = "ok"  # i18n-allow
TEXT_CANH_LOI = "lỗi"  # i18n-allow


def build_flow_model(steps):
    """Turn the FLAT step list of parse_diagram into `{"nodes", "edges"}`.

    parse_diagram returns `B<n>` and `B<n>!` as two unrelated entries carrying
    the same number; pairing them is this function's whole job. Each `B<n>!`
    becomes a node of its own hanging off `B<n>` by one `loi` edge, and `B<n>`
    is promoted to a decision node. Consecutive main steps are joined by `chinh`
    edges, labelled `ok` only when they leave a decision (an unlabelled arrow
    out of a plain box needs no word).

    Pure data: descriptions are carried through verbatim, and not one HTML or
    SVG character is produced here — that belongs to render_flow_svg.
    """
    main_steps = [s for s in steps if not s.is_error]
    error_steps = [s for s in steps if s.is_error]

    errors_by_num = {}
    for step in error_steps:
        errors_by_num.setdefault(step.num, []).append(step)

    def _node(node_id, step, role, la_vao=False, la_ra=False):
        return {
            "id": node_id, "num": step.num, "is_error": step.is_error,
            "desc": step.desc, "file": step.file, "func": step.func,
            "location_raw": step.location_raw, "role": role,
            "la_vao": la_vao, "la_ra": la_ra,
        }

    nodes, edges = [], []
    seen_nums = set()
    previous_id = None
    for position, step in enumerate(main_steps):
        node_id = "b{}".format(step.num)
        while node_id in seen_nums:  # a repeated number never loses its node
            node_id += "x"
        seen_nums.add(node_id)
        branches = errors_by_num.pop(step.num, [])
        la_vao = position == 0
        la_ra = position == len(main_steps) - 1
        if branches:
            role = ROLE_QUYET_DINH
        elif la_vao:
            role = ROLE_VAO
        elif la_ra:
            role = ROLE_RA
        else:
            role = ROLE_BUOC
        nodes.append(_node(node_id, step, role, la_vao=la_vao, la_ra=la_ra))
        if previous_id is not None:
            previous = next(n for n in nodes if n["id"] == previous_id)
            edges.append({
                "from": previous_id, "to": node_id, "kind": "chinh",
                "label": TEXT_CANH_OK if previous["role"] == ROLE_QUYET_DINH else "",
            })
        previous_id = node_id
        for order, branch in enumerate(branches, start=1):
            branch_id = "{}e{}".format(node_id, order)
            nodes.append(_node(branch_id, branch, ROLE_NHANH_LOI, la_ra=True))
            edges.append({"from": node_id, "to": branch_id, "kind": "loi",
                          "label": TEXT_CANH_LOI})

    # An error branch whose parent step is absent (an older diagram) still gets a
    # node — dropping a line the author wrote would be worse than drawing it alone.
    for num in sorted(errors_by_num):
        for order, branch in enumerate(errors_by_num[num], start=1):
            nodes.append(_node("b{}e{}".format(num, order), branch,
                                ROLE_NHANH_LOI, la_ra=True))

    return {"nodes": nodes, "edges": edges}


# --------------------------------------------------------------- flow layout
# Geometry of the business-layer flow diagram, in viewBox user units. The boxes
# are sized from the TEXT they carry (never the other way round), so no
# description is ever clipped — the figure grows instead.
FLOW_MARGIN = 10
FLOW_BOX_W = 300          # main column
FLOW_ERR_W = 250          # error column, sitting to the right
FLOW_COL_GAP = 70
FLOW_ROW_GAP = 44         # vertical room between rows, enough for an edge label
FLOW_ERR_GAP = 10         # between two error branches of the same step
FLOW_PAD_X, FLOW_PAD_Y = 14, 11
FLOW_FONT = 13
FLOW_LINE_H = 17
FLOW_MIN_H = 42
# Average glyph width for the page font at FLOW_FONT px. Deliberately generous:
# over-estimating the width only makes a box taller, while under-estimating it
# would push text past the border.
FLOW_CHAR_W = 7.2
# A diamond wastes its corners, so its text wraps narrower and its box grows
# taller than a rectangle carrying the same words.
FLOW_DIAMOND_TEXT_RATIO = 0.6
FLOW_DIAMOND_H_RATIO = 1.8


def _max_chars(width):
    """How many glyphs of the page font fit inside a box `width` units wide."""
    return max(1, int((width - 2 * FLOW_PAD_X) / FLOW_CHAR_W))


def wrap_label(text, max_chars):
    """Split `text` into lines of at most `max_chars`, breaking on spaces only.

    Never truncates: a single word longer than `max_chars` keeps its own line at
    full length rather than losing characters. Always returns at least one line,
    so a caller can size a box off `len(...)` without a special case.
    """
    words = (text or "").split()
    if not words:
        return [""]
    lines, current = [], ""
    for word in words:
        candidate = word if not current else current + " " + word
        if len(candidate) <= max_chars or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _flow_box(node):
    """Wrapped lines plus the width/height the node needs to hold them."""
    is_error = node["role"] == ROLE_NHANH_LOI
    is_diamond = node["role"] == ROLE_QUYET_DINH
    width = FLOW_ERR_W if is_error else FLOW_BOX_W
    max_chars = _max_chars(width)
    if is_diamond:
        max_chars = max(1, int(max_chars * FLOW_DIAMOND_TEXT_RATIO))
    lines = wrap_label(node["desc"], max_chars)
    height = 2 * FLOW_PAD_Y + len(lines) * FLOW_LINE_H
    if is_diamond:
        height = height * FLOW_DIAMOND_H_RATIO
    return {"w": width, "h": max(FLOW_MIN_H, round(height)), "lines": lines}


def layout_flow(model):
    """Place every node of a flow model: `{"boxes": {id: {...}}, "width", "height"}`.

    The main flow runs down a single column; the error branch of a step sits in
    a second column to its right, vertically centred on the step it leaves. Each
    row is as tall as the taller of its two sides, so no two boxes can overlap:
    the two columns never share an x range, and rows never share a y range.
    """
    nodes_by_id = {n["id"]: n for n in model["nodes"]}
    branches_of = {}
    for edge in model["edges"]:
        if edge["kind"] == "loi":
            branches_of.setdefault(edge["from"], []).append(edge["to"])
    attached = {i for ids in branches_of.values() for i in ids}

    rows = []  # list[(main_id or None, [branch_id, ...])]
    for node in model["nodes"]:
        if node["role"] == ROLE_NHANH_LOI:
            if node["id"] not in attached:
                rows.append((None, [node["id"]]))  # an orphan branch keeps its row
            continue
        rows.append((node["id"], branches_of.get(node["id"], [])))

    boxes = {}
    err_x = FLOW_MARGIN + FLOW_BOX_W + FLOW_COL_GAP
    y_cursor = FLOW_MARGIN
    has_error_column = False
    for main_id, branch_ids in rows:
        main_size = _flow_box(nodes_by_id[main_id]) if main_id else None
        branch_sizes = [_flow_box(nodes_by_id[i]) for i in branch_ids]
        if branch_sizes:
            has_error_column = True
        branch_total = sum(size["h"] for size in branch_sizes)
        branch_total += FLOW_ERR_GAP * max(0, len(branch_sizes) - 1)
        main_h = main_size["h"] if main_size else 0
        row_h = max(main_h, branch_total)
        if main_size:
            boxes[main_id] = dict(
                main_size, x=FLOW_MARGIN, y=round(y_cursor + (row_h - main_h) / 2))
        branch_y = y_cursor + (row_h - branch_total) / 2
        for branch_id, size in zip(branch_ids, branch_sizes):
            boxes[branch_id] = dict(size, x=err_x, y=round(branch_y))
            branch_y += size["h"] + FLOW_ERR_GAP
        y_cursor += row_h + FLOW_ROW_GAP

    width = FLOW_MARGIN * 2 + FLOW_BOX_W
    if has_error_column:
        width = err_x + FLOW_ERR_W + FLOW_MARGIN
    height = max(0, round(y_cursor - FLOW_ROW_GAP + FLOW_MARGIN))
    return {"boxes": boxes, "width": width, "height": height}


# ------------------------------------------------------- shared SVG primitives
# Every shape the two pages draw goes through these five helpers, so a change of
# look happens in one place. They emit `currentColor` and CSS variables only —
# a hard colour code would break the light/dark palette of the page.
def _num(value):
    """Format a coordinate: integers stay integers, so the markup stays readable."""
    number = float(value)
    return str(int(number)) if number == int(number) else "{:.1f}".format(number)


def _svg_hop(x, y, w, h, extra=""):
    """A rounded rectangle — the shape of an ordinary step."""
    return ('<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" '
            'fill="var(--card)" stroke="currentColor" stroke-width="1.2"{extra}/>').format(
        x=_num(x), y=_num(y), w=_num(w), h=_num(h), extra=extra)


def _svg_hinh_thoi(x, y, w, h, extra=""):
    """A diamond filling the same box — the shape of a step that branches."""
    points = "{cx},{y} {x2},{cy} {cx},{y2} {x},{cy}".format(
        cx=_num(x + w / 2), cy=_num(y + h / 2), x=_num(x), y=_num(y),
        x2=_num(x + w), y2=_num(y + h))
    return ('<polygon points="{points}" fill="var(--card)" stroke="currentColor" '
            'stroke-width="1.2"{extra}/>').format(points=points, extra=extra)


def _svg_vien_thuoc(x, y, w, h, extra=""):
    """A pill (corner radius = half the height) — the entry and exit points."""
    return ('<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" '
            'fill="var(--card)" stroke="currentColor" stroke-width="1.2"{extra}/>').format(
        x=_num(x), y=_num(y), w=_num(w), h=_num(h), r="{:.1f}".format(h / 2), extra=extra)


def _svg_nhan_nhieu_dong(cx, y_center, lines, font=FLOW_FONT, extra=""):
    """A centred multi-line label: one `<tspan>` per line, vertically centred.

    The text is escaped here and nowhere else, so a description containing `<`
    (diagram files legitimately write things like `B<n>`) survives intact.
    """
    if not lines:
        return ""
    first_y = y_center - (len(lines) - 1) * FLOW_LINE_H / 2 + font / 3
    spans = "".join(
        '<tspan x="{cx}" y="{y}">{text}</tspan>'.format(
            cx=_num(cx), y=_num(first_y + i * FLOW_LINE_H), text=html.escape(line))
        for i, line in enumerate(lines))
    return ('<text text-anchor="middle" font-size="{font}" fill="currentColor"{extra}>'
            '{spans}</text>').format(font=font, extra=extra, spans=spans)


def _svg_mui_ten(x1, y1, x2, y2, marker_id, label=None, extra=""):
    """One arrow, optionally carrying a short word beside its middle."""
    parts = ['<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="currentColor" '
             'stroke-width="1.4" marker-end="url(#{mid})"{extra}/>'.format(
                 x1=_num(x1), y1=_num(y1), x2=_num(x2), y2=_num(y2),
                 mid=marker_id, extra=extra)]
    if label:
        parts.append(
            '<text x="{x}" y="{y}" font-size="11" text-anchor="middle" '
            'fill="currentColor">{label}</text>'.format(
                x=_num((x1 + x2) / 2 + 12), y=_num((y1 + y2) / 2 - 3),
                label=html.escape(label)))
    return "".join(parts)


def _svg_marker(marker_id):
    """The arrowhead definition both pages reuse, by id."""
    return ('<defs><marker id="{mid}" markerWidth="8" markerHeight="8" refX="7" '
            'refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="currentColor"/>'
            '</marker></defs>').format(mid=marker_id)


TEXT_FLOW_CLAIM = ("Luồng nghiệp vụ: {buoc} bước chính, {loi} nhánh lỗi — "  # i18n-allow
                    "mũi tên đi từ trên xuống, nhánh lỗi rẽ sang phải")  # i18n-allow


def render_flow_svg(model, layout, marker_suffix="luong"):
    """The business-layer flow figure: shapes by role, arrows labelled by kind.

    Shape convention (one claim per figure, per the artifact-diagramming skill):
    pill = entry and exit, rounded rectangle = an ordinary step or an error
    outcome, diamond = a step that owns an error branch. Returns "" for a model
    with no node at all, so the caller simply prints nothing.
    """
    boxes = layout["boxes"]
    if not boxes:
        return ""
    marker_id = "mui-ten-{}".format(marker_suffix)
    claim = TEXT_FLOW_CLAIM.format(
        buoc=len([n for n in model["nodes"] if n["role"] != ROLE_NHANH_LOI]),
        loi=len([n for n in model["nodes"] if n["role"] == ROLE_NHANH_LOI]))
    parts = [
        '<figure class="flow-fig">',
        '<svg viewBox="0 0 {w} {h}" role="img" aria-label="{claim}">'.format(
            w=_num(layout["width"]), h=_num(layout["height"]), claim=html.escape(claim)),
        _svg_marker(marker_id),
    ]

    for edge in model["edges"]:
        source, target = boxes.get(edge["from"]), boxes.get(edge["to"])
        if source is None or target is None:
            continue
        if edge["kind"] == "loi":  # sideways, into the left edge of the branch box
            x1, y1 = source["x"] + source["w"], source["y"] + source["h"] / 2
            x2, y2 = target["x"], target["y"] + target["h"] / 2
        else:  # straight down the main column
            x1, y1 = source["x"] + source["w"] / 2, source["y"] + source["h"]
            x2, y2 = target["x"] + target["w"] / 2, target["y"]
        parts.append(_svg_mui_ten(x1, y1, x2, y2, marker_id, label=edge["label"] or None))

    for node in model["nodes"]:
        box = boxes.get(node["id"])
        if box is None:
            continue
        role = node["role"]
        extra = ' class="node-loi"' if role == ROLE_NHANH_LOI else ""
        if role == ROLE_QUYET_DINH:
            parts.append(_svg_hinh_thoi(box["x"], box["y"], box["w"], box["h"]))
        elif role in (ROLE_VAO, ROLE_RA):
            parts.append(_svg_vien_thuoc(box["x"], box["y"], box["w"], box["h"]))
        else:
            parts.append(_svg_hop(box["x"], box["y"], box["w"], box["h"], extra=extra))
        parts.append(_svg_nhan_nhieu_dong(
            box["x"] + box["w"] / 2, box["y"] + box["h"] / 2, box["lines"], extra=extra))

    parts.append("</svg>")
    parts.append("<figcaption>{}</figcaption>".format(html.escape(claim + ".")))
    parts.append("</figure>")
    return "".join(parts)


# ------------------------------------------------------------------- graph.json
def load_graph(path):
    """The parsed graph dict, or None when the file is missing/unreadable/corrupt.

    A missing graph is not fatal here: the business layer never needs it, and the
    detail layer degrades to "not found" placeholders for every step instead of
    refusing to render the page at all.
    """
    if not path:
        return None
    try:
        import json
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _node_display_label(node):
    """The label shown to the reader — the node's own label, unchanged (e.g. `foo()`)."""
    return node.get("label") or node.get("norm_label") or node.get("id") or ""


def _node_match_core(node):
    """The bare callable name used to MATCH a node against a step's `func`.

    Stripped of the trailing `()` and a leading `.` (graph labels for methods sit
    as `.method()`, without their class prefix) — this is a matching key only,
    never shown to the reader.
    """
    label = _node_display_label(node)
    core = label[:-2] if label.endswith("()") else label
    return core.lstrip(".")


def _short_name(func):
    return func.rsplit(".", 1)[-1]


def _parse_line(location):
    """`"L123"` -> 123; anything else -> None (sorts last, prints as unknown)."""
    if not location:
        return None
    match = re.match(r"^L(\d+)$", location)
    return int(match.group(1)) if match else None


class GraphIndex:
    """Nodes by id, and outgoing calls/indirect_call edges by source id — built once."""

    def __init__(self, graph):
        self.nodes = {}
        self.calls_by_source = {}
        if not graph:
            return
        for node in graph.get("nodes", []):
            if node.get("file_type") == "code":
                self.nodes[node.get("id")] = node
        for link in graph.get("links", []):
            if link.get("relation") not in ("calls", "indirect_call"):
                continue
            source = link.get("source")
            self.calls_by_source.setdefault(source, []).append(
                (_parse_line(link.get("source_location")), link.get("target")))

    def find_node_id(self, file, func):
        """The id of the code node at `file` whose name matches `func`, or None."""
        name = _short_name(func)
        for node_id, node in self.nodes.items():
            if node.get("source_file") != file:
                continue
            core = _node_match_core(node)
            if core == func or core == name:
                return node_id
        return None


# ------------------------------------------------------------- docstring lookup
def _module_ast(cache, root, source_file):
    """Parsed AST of one source file, cached per render call; None if unusable."""
    if source_file in cache:
        return cache[source_file]
    tree = None
    if source_file and source_file.endswith(".py"):
        try:
            with open(os.path.join(root, source_file), encoding="utf-8") as f:
                tree = ast.parse(f.read())
        except (OSError, SyntaxError, UnicodeDecodeError):
            tree = None
    cache[source_file] = tree
    return tree


def docstring_first_line(cache, root, source_file, line_no):
    """First line of the docstring of the function defined at `line_no`, or None."""
    tree = _module_ast(cache, root, source_file)
    if tree is None or line_no is None:
        return None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.lineno == line_no:
            doc = ast.get_docstring(node)
            if not doc:
                return None
            first = doc.strip().splitlines()[0].strip()
            return first or None
    return None


# ------------------------------------------------------------------ call tree
class CallNode:
    """One function in a step's call tree: itself, plus its own callees (line, CallNode)."""

    __slots__ = ("node_id", "label", "found", "explanation", "children")

    def __init__(self, node_id, label, found, explanation, children):
        self.node_id = node_id
        self.label = label
        self.found = found
        self.explanation = explanation
        self.children = children  # list[(line, CallNode)], sorted by line


def build_call_tree(index, doc_cache, project_root, node_id, label, depth_remaining, visited):
    """Recurse up to `depth_remaining` hops of calls/indirect_call from `node_id`."""
    node = index.nodes.get(node_id) if node_id else None
    found = node is not None
    explanation = None
    if found:
        explanation = docstring_first_line(
            doc_cache, project_root, node.get("source_file"), _parse_line(node.get("source_location")))
    children = []
    if found and depth_remaining > 0 and node_id not in visited:
        calls = sorted(
            index.calls_by_source.get(node_id, []),
            key=lambda c: (c[0] if c[0] is not None else float("inf"), c[1]))
        for line, target_id in calls:
            target_node = index.nodes.get(target_id)
            target_label = _node_display_label(target_node) if target_node else target_id
            child = build_call_tree(
                index, doc_cache, project_root, target_id if target_node else None,
                target_label, depth_remaining - 1, visited | {node_id})
            children.append((line, child))
    return CallNode(node_id, label, found, explanation, children)


def count_calls(call_node):
    """Total number of callees anywhere under `call_node` (root excluded)."""
    return sum(1 + count_calls(child) for _, child in call_node.children)


# ------------------------------------------------------------------------- SVG
def _layout(call_node, level, y_top, boxes, edges, counter):
    leaves = max(1, sum(_leaf_count(child) for _, child in call_node.children))
    height = leaves * ROW_H
    y_center = y_top + height / 2
    box_id = "c{}".format(next(counter))
    boxes.append({"id": box_id, "level": level, "y": y_center,
                  "label": call_node.label, "found": call_node.found})
    y_cursor = y_top
    for line, child in call_node.children:
        child_height = _leaf_count(child) * ROW_H
        child_id = _layout(child, level + 1, y_cursor, boxes, edges, counter)
        edges.append({"from": box_id, "to": child_id,
                      "label": "L{}".format(line) if line else "?"})
        y_cursor += child_height
    return box_id


def _leaf_count(call_node):
    if not call_node.children:
        return 1
    return sum(_leaf_count(child) for _, child in call_node.children)


def render_svg(call_node, step_num):
    """A small self-contained call-graph figure: boxes and labelled arrows.

    Follows the artifact-diagramming mechanics: sized viewBox, currentColor so it
    reads in both themes, a <marker> arrowhead, role="img" + aria-label, one figure
    for one claim (what this step calls, in the order it is written).
    """
    boxes, edges = [], []
    _layout(call_node, 0, 0, boxes, edges, itertools.count())
    max_level = max(b["level"] for b in boxes)
    total_height = max(_leaf_count(call_node) * ROW_H, ROW_H)
    width = (max_level + 1) * (BOX_W + COL_GAP) - COL_GAP + 10
    marker_id = "seotenmuiten-b{}".format(step_num)
    claim = ("Lời gọi phát ra từ bước B{}, sắp theo thứ tự dòng trong file"  # i18n-allow
              .format(step_num))
    parts = [
        '<figure class="call-fig">',
        '<svg viewBox="0 0 {w} {h}" role="img" aria-label="{claim}">'.format(
            w=width, h=total_height, claim=html.escape(claim)),
        '<defs><marker id="{mid}" markerWidth="8" markerHeight="8" refX="7" refY="4" '
        'orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="currentColor"/></marker></defs>'
        .format(mid=marker_id),
    ]
    pos = {b["id"]: b for b in boxes}
    for edge in edges:
        a, b = pos[edge["from"]], pos[edge["to"]]
        x1 = a["level"] * (BOX_W + COL_GAP) + BOX_W
        y1 = a["y"]
        x2 = b["level"] * (BOX_W + COL_GAP)
        y2 = b["y"]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2 - 4
        parts.append(
            '<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="currentColor" '
            'stroke-width="1.5" marker-end="url(#{mid})"/>'.format(
                x1=x1, y1=y1, x2=x2, y2=y2, mid=marker_id))
        parts.append(
            '<text x="{mx}" y="{my}" font-size="11" text-anchor="middle" '
            'fill="currentColor">{label}</text>'.format(
                mx=mx, my=my, label=html.escape(edge["label"])))
    for b in boxes:
        x = b["level"] * (BOX_W + COL_GAP)
        y = b["y"] - BOX_H / 2
        dim = ' class="dim"' if not b["found"] else ""
        parts.append(
            '<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="none" '
            'stroke="currentColor"{dim}/>'.format(x=x, y=y, w=BOX_W, h=BOX_H, dim=dim))
        parts.append(
            '<text x="{tx}" y="{ty}" font-size="12" fill="currentColor"{dim}>{label}</text>'
            .format(tx=x + 8, ty=b["y"] + 4, dim=dim, label=html.escape(b["label"][:26])))
    parts.append("</svg>")
    parts.append("<figcaption>{}</figcaption>".format(html.escape(claim + ".")))
    parts.append("</figure>")
    return "".join(parts)


# ------------------------------------------------------------------- HTML build
def _render_calls_list(call_node):
    """Grouped-by-line, readable list under the figure: name(s), docstring or dim."""
    rows = []
    for line, group in itertools.groupby(call_node.children, key=lambda c: c[0]):
        targets = [child for _, child in group]
        items = []
        for target in targets:
            dim = "" if target.explanation else ' class="dim"'
            items.append('<code{dim}>{name}</code>{expl}'.format(
                dim=dim, name=html.escape(target.label),
                expl=" — " + html.escape(target.explanation) if target.explanation else ""))
        loc_label = "L{}".format(line) if line else "?"
        rows.append("<li><span class=\"loc\">{loc}</span> → {items}</li>".format(
            loc=html.escape(loc_label), items=", ".join(items)))
    return "<ul class=\"calls-list\">{}</ul>".format("".join(rows))


def _render_step_detail(call_node, step_num):
    if not call_node.found:
        return '<p class="muted">{}</p>'.format(html.escape(TEXT_NOT_IN_GRAPH))
    if not call_node.children:
        return '<p class="muted">{}</p>'.format(html.escape(TEXT_NO_CALLS))
    body = render_svg(call_node, step_num) + _render_calls_list(call_node)
    total = count_calls(call_node)
    if total > COLLAPSE_THRESHOLD:
        summary = html.escape(TEXT_COLLAPSE_SUMMARY.format(n=total))
        return '<details><summary>{summary}</summary>{body}</details>'.format(
            summary=summary, body=body)
    return body


def _render_location_tag(step):
    if step.file is None and step.func is None:
        if step.location_raw == UNKNOWN_LOCATION:
            return '<span class="muted">({})</span>'.format(html.escape(TEXT_UNKNOWN_LOCATION))
        return ""
    return '<code>{}::{}</code>'.format(html.escape(step.file), html.escape(step.func))


def _render_business_layer(title, branch_top, branch_sub, depends, steps):
    model = build_flow_model(steps)
    flow_svg = render_flow_svg(model, layout_flow(model))
    flow_html = '<div class="flow-wrap">{}</div>'.format(flow_svg) if flow_svg else ""
    _log("render: so do luong — {} node, {} canh".format(
        len(model["nodes"]), len(model["edges"])))
    items = []
    for step in steps:
        error_tag = ' <span class="err">[{}]</span>'.format(html.escape(TEXT_ERROR_BRANCH)) \
            if step.is_error else ""
        items.append(
            '<li class="step{err_cls}"><strong>B{num}{err_mark}</strong> · '
            '{desc}{err_tag} {loc}</li>'.format(
                err_cls=" is-error" if step.is_error else "",
                num=step.num, err_mark="!" if step.is_error else "",
                desc=html.escape(step.desc), err_tag=error_tag,
                loc=_render_location_tag(step)))
    depends_html = ""
    if depends:
        depends_items = "".join(
            '<li><code>{feature}</code> — {reason}</li>'.format(
                feature=html.escape(feature), reason=html.escape(reason))
            for feature, reason in depends)
        depends_html = '<h2>{heading}</h2><ul class="depends">{items}</ul>'.format(
            heading=html.escape(TEXT_DEPENDS_HEADING), items=depends_items)
    return (
        '<section id="lop-nghiep-vu">'
        '{flow}<ol class="steps">{steps}</ol>{depends}'
        '</section>'
    ).format(flow=flow_html, steps="".join(items), depends=depends_html)


def _render_detail_layer(index, doc_cache, project_root, steps, depth):
    figures = []
    for step in steps:
        if step.file is None or step.func is None:
            continue
        node_id = index.find_node_id(step.file, step.func)
        call_node = build_call_tree(
            index, doc_cache, project_root, node_id, step.func, depth, frozenset())
        figures.append(
            '<div class="step-detail"><h3>B{num}{mark} · <code>{loc}</code></h3>{body}</div>'
            .format(num=step.num, mark="!" if step.is_error else "",
                    loc=html.escape("{}::{}".format(step.file, step.func)),
                    body=_render_step_detail(call_node, step.num)))
    return (
        '<section id="lop-chi-tiet" hidden>'
        '<p class="canh-bao">{warning}</p>{figures}'
        '</section>'
    ).format(warning=html.escape(TEXT_DETAIL_WARNING), figures="".join(figures))


STYLE = """
* { box-sizing: border-box; }
:root {
  --bg: #fbfbf9; --fg: #1c1c1a; --muted: #6b6b64; --border: #d8d8d2;
  --card: #eceae4; --err: #a32020; --accent: #1d5f8a;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #16171a; --fg: #e8e8e4; --muted: #9a9a92; --border: #33343a;
    --card: #23252b; --err: #e08a8a; --accent: #7ab6dd;
  }
}
:root[data-theme="dark"] {
  --bg: #16171a; --fg: #e8e8e4; --muted: #9a9a92; --border: #33343a;
  --card: #23252b; --err: #e08a8a; --accent: #7ab6dd;
}
body {
  margin: 0; padding: 24px 18px 60px; background: var(--bg); color: var(--fg);
  font: 15px/1.55 ui-sans-serif, -apple-system, "Segoe UI", Roboto, sans-serif;
}
main { max-width: 900px; margin: 0 auto; }
h1 { font-size: 20px; margin: 0 0 6px; }
h2, h3 { font-size: 15px; margin: 20px 0 8px; }
.nhanh { color: var(--muted); font-size: 13px; margin: 0 0 16px; }
button { font: inherit; padding: 6px 12px; border: 1px solid var(--border);
  border-radius: 6px; background: var(--card); color: var(--fg); cursor: pointer; }
[hidden] { display: none !important; }
ol.steps, ul.calls-list, ul.depends { list-style: none; margin: 0; padding-left: 0; }
li.step { border-left: 2px solid var(--border); padding: 6px 0 6px 12px; margin-bottom: 2px; }
li.step.is-error { border-left-color: var(--err); }
.err { color: var(--err); font-size: 12px; }
.muted, .canh-bao { color: var(--muted); }
.canh-bao { border: 1px solid var(--border); background: var(--card); border-radius: 6px;
  padding: 8px 12px; font-size: 13px; margin: 0 0 16px; }
code { background: var(--card); border-radius: 4px; padding: 1px 5px; font-size: 13px; }
code.dim, .dim { opacity: .55; }
.calls-list li { padding: 2px 0; font-size: 13px; }
.loc { color: var(--accent); font-weight: 600; margin-right: 4px; }
.flow-wrap { overflow-x: auto; max-width: 100%; border: 1px solid var(--border);
  border-radius: 8px; background: var(--bg); padding: 14px 12px; margin: 0 0 18px; }
figure.flow-fig { margin: 0; }
figure.flow-fig svg { display: block; height: auto; max-width: 100%; }
figure.flow-fig .node-loi { color: var(--err); }
figure.call-fig { margin: 10px 0 4px; }
figure.call-fig svg { max-width: 100%; height: auto; display: block; }
figcaption { font-size: 12px; color: var(--muted); margin-top: 4px; }
.step-detail { border-top: 1px solid var(--border); padding: 10px 0; }
details summary { cursor: pointer; color: var(--accent); }
"""

# Extra rules for the aggregate page only (render_total_page) — appended to STYLE
# rather than duplicating its tokens, so both pages share one palette/theme block.
STYLE_TONG = """
section { margin-bottom: 28px; }
.cay-nhanh, .cay-nhanh ul { list-style: none; margin: 0; padding-left: 16px; }
.cay-nhanh { padding-left: 0; }
.cay-nhanh > li { margin-bottom: 6px; }
.cay-nhanh a { color: var(--accent); text-decoration: none; }
.cay-nhanh a:hover, .cay-nhanh a:focus-visible { text-decoration: underline; }
.grid-wrap, .cay-wrap { overflow-x: auto; max-width: 100%; border: 1px solid var(--border);
  border-radius: 6px; padding: 12px; margin: 8px 0; }
.cay-fig { margin: 0; }
.cay-fig svg { display: block; height: auto; max-width: 100%; }
.cay-fig a { color: var(--accent); text-decoration: none; }
.cay-fig a:hover rect, .cay-fig a:focus-visible rect { stroke-width: 2; }
.grid-fig { margin: 0; }
.grid-fig svg { display: block; height: auto; }
.danh-sach-canh { list-style: none; padding-left: 0; margin: 8px 0 0; font-size: 13px; }
.danh-sach-canh li { padding: 2px 0; }
"""

SCRIPT = """
document.addEventListener('DOMContentLoaded', function () {
  var btn = document.getElementById('btn-lop');
  var nghiepVu = document.getElementById('lop-nghiep-vu');
  var chiTiet = document.getElementById('lop-chi-tiet');
  if (!btn) { return; }
  btn.addEventListener('click', function () {
    var showDetail = chiTiet.hasAttribute('hidden');
    if (showDetail) {
      chiTiet.removeAttribute('hidden');
      nghiepVu.setAttribute('hidden', '');
    } else {
      chiTiet.setAttribute('hidden', '');
      nghiepVu.removeAttribute('hidden');
    }
    btn.textContent = showDetail ? BTN_TO_BUSINESS : BTN_TO_DETAIL;
  });
});
"""


def render_feature_page(lines, diagram_path, graph=None, depth=DEPTH_DEFAULT, project_root=None):
    """Build the full two-layer HTML page for one feature. Pure: no file I/O.

    Raises DiagramInvalid when check_diagram(lines, diagram_path) finds any
    violation — the single gate every caller (CLI here, and the future `xem`
    command in tdq_mindmap.py) goes through, so an out-of-shape diagram never
    reaches a page.
    """
    violations = check_diagram(lines, diagram_path)
    if violations:
        raise DiagramInvalid(violations)

    title, branch_top, branch_sub, depends, steps = parse_diagram(lines)
    root = project_root or project_dir()
    index = GraphIndex(graph)
    doc_cache = {}

    business = _render_business_layer(title, branch_top, branch_sub, depends, steps)
    detail = _render_detail_layer(index, doc_cache, root, steps, depth)
    branch_line = "{} &gt; {}".format(html.escape(branch_top or ""), html.escape(branch_sub or "")) \
        if branch_top else ""

    script = SCRIPT.replace(
        "BTN_TO_BUSINESS", "'{}'".format(TEXT_LAYER_BUTTON_TO_BUSINESS)
    ).replace(
        "BTN_TO_DETAIL", "'{}'".format(TEXT_LAYER_BUTTON_TO_DETAIL)
    )

    return (
        '<!doctype html>\n<html lang="vi">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>{title}</title>\n<style>{style}</style>\n</head>\n<body>\n'
        '<main>\n<header>\n<h1>{title}</h1>\n<p class="nhanh">{branch}</p>\n'
        '<button id="btn-lop" type="button">{btn}</button>\n</header>\n'
        '{business}\n{detail}\n</main>\n<script>{script}</script>\n</body>\n</html>\n'
    ).format(
        title=html.escape(title or ""), style=STYLE, branch=branch_line,
        btn=html.escape(TEXT_LAYER_BUTTON_TO_DETAIL), business=business, detail=detail,
        script=script,
    )


# --------------------------------------------------------------- total page (--tong)
def collect_total_data(root=None):
    """Every on-disk feature under mind_map_dir(root), parsed for the aggregate page.

    I/O only — reads each diagram file and runs it through parse_diagram (the
    same parser render_feature_page uses), so this never re-derives the file
    shape on its own. A file that check_diagram would reject (e.g. missing the
    branch line, like an old pre-shape sample) still gets an entry — its
    branch_top stays None and render_total_page sorts it into the
    "unclassified" bucket instead of dropping it.

    Returns {slug: {"title", "branch_top", "branch_sub", "depends", "exists": True}}.
    """
    directory = mind_map_dir(root)
    features = {}
    if not os.path.isdir(directory):
        return features
    for name in sorted(os.listdir(directory)):
        if not name.endswith(FILE_SUFFIX):
            continue
        slug = name[:-len(FILE_SUFFIX)]
        lines = read_diagram(os.path.join(directory, name))
        if lines is None:
            continue
        title, branch_top, branch_sub, depends, _steps = parse_diagram(lines)
        features[slug] = {
            "title": title or slug, "branch_top": branch_top, "branch_sub": branch_sub,
            "depends": depends, "exists": True,
        }
    return features


def _feature_levels(features):
    """Longest-path depth of each slug: 0 with no depends, else 1 + its deepest dep.

    A slug caught in a cycle (should already be rejected by `lien-he`, but this
    function must never hang on one) simply settles at level 0 for the edge that
    closes the loop, via the `visiting` guard below.
    """
    levels = {}

    def level_of(slug, visiting):
        if slug in levels:
            return levels[slug]
        info = features.get(slug)
        if info is None or slug in visiting:
            return 0
        deps = [dep for dep, _reason in info["depends"]]
        if not deps:
            levels[slug] = 0
            return 0
        lv = 1 + max(level_of(dep, visiting | {slug}) for dep in deps)
        levels[slug] = lv
        return lv

    for slug in features:
        level_of(slug, frozenset())
    return levels


def _grid_label(slug, info):
    """The text of one grid box: the slug, marked when it has no diagram yet."""
    if info.get("exists"):
        return slug
    return "{} ({})".format(slug, TEXT_TONG_CHUA_CO_SO_DO)


def _layout_grid(features):
    """`(positions, columns)` — positions keyed by slug, columns keyed by level.

    Each position carries its own `w`/`h`/`lines`: the box is sized from the
    wrapped label rather than the label being cut to fit a fixed box, so a long
    slug makes its box taller and never loses a character. Rows inside a column
    are stacked by real height, which is what keeps two boxes from overlapping.
    """
    levels = _feature_levels(features)
    columns = {}
    for slug in sorted(features):
        columns.setdefault(levels[slug], []).append(slug)
    positions = {}
    for level, slugs in sorted(columns.items()):
        y_cursor = float(FLOW_MARGIN)
        for slug in slugs:
            lines = wrap_label(_grid_label(slug, features[slug]), _max_chars(BOX_W))
            height = max(BOX_H, len(lines) * FLOW_LINE_H + 2 * FLOW_PAD_Y)
            positions[slug] = {
                "x": level * (BOX_W + COL_GAP) + FLOW_MARGIN, "y": y_cursor,
                "level": level, "w": BOX_W, "h": height, "lines": lines,
            }
            y_cursor += height + BRANCH_ROW_GAP
    return positions, columns


def _render_dependency_svg(features, positions, columns, marker_suffix="luoi"):
    """Boxes for every feature (dashed + dim when it has no file yet) and one
    arrow per depends edge, pointing at the dependency.

    Drawn with the same `_svg_*` helpers as the feature page's flow diagram, so
    both pages share one shape vocabulary and one arrowhead definition. Nothing
    is truncated: the box was sized around the wrapped label in _layout_grid.
    """
    if not positions:
        return ""
    max_level = max(columns)
    width = (max_level + 1) * (BOX_W + COL_GAP) - COL_GAP + FLOW_MARGIN * 2
    height = max(pos["y"] + pos["h"] for pos in positions.values()) + FLOW_MARGIN
    marker_id = "mui-ten-{}".format(marker_suffix)
    parts = [
        '<figure class="grid-fig">',
        '<svg viewBox="0 0 {w} {h}" role="img" aria-label="{claim}">'.format(
            w=_num(width), h=_num(height), claim=html.escape(TEXT_TONG_CLAIM)),
        _svg_marker(marker_id),
    ]
    for slug in sorted(features):
        for dep, _reason in features[slug]["depends"]:
            a, b = positions.get(slug), positions.get(dep)
            if a is None or b is None:
                continue
            parts.append(_svg_mui_ten(a["x"], a["y"] + a["h"] / 2,
                                      b["x"] + b["w"], b["y"] + b["h"] / 2, marker_id))
    for slug, pos in positions.items():
        missing = not features[slug]["exists"]
        dash = ' stroke-dasharray="4 3"' if missing else ""
        dim = ' class="dim"' if missing else ""
        parts.append(_svg_hop(pos["x"], pos["y"], pos["w"], pos["h"], dash))
        parts.append(_svg_nhan_nhieu_dong(pos["x"] + pos["w"] / 2, pos["y"] + pos["h"] / 2,
                                          pos["lines"], font=12, extra=dim))
    parts.append("</svg>")
    parts.append("<figcaption>{}</figcaption>".format(html.escape(TEXT_TONG_CLAIM + ".")))
    parts.append("</figure>")
    return "".join(parts)


def _render_edge_list(features):
    """The same edges as the SVG, spelled out as text — every reason legible
    without hovering, and readable by a screen reader or a text search alike.
    """
    rows = []
    for slug in sorted(features):
        info = features[slug]
        if not info["exists"]:
            continue
        for dep, reason in info["depends"]:
            dep_info = features.get(dep, {"exists": False})
            dep_label = dep if dep_info.get("exists") else "{} ({})".format(
                dep, TEXT_TONG_CHUA_CO_SO_DO)
            rows.append(
                '<li><code>{a}</code> &rarr; <code>{b}</code> — {reason}</li>'.format(
                    a=html.escape(slug), b=html.escape(dep_label), reason=html.escape(reason)))
    if not rows:
        return '<p class="muted">{}</p>'.format(html.escape(TEXT_TONG_KHONG_CO_CANH))
    return '<ul class="danh-sach-canh">{}</ul>'.format("".join(rows))


def _render_branch_tree(features):
    """Top branch -> sub branch -> feature, general down to the business page —
    nested <ul>s with a link to that feature's own rendered page.

    A feature with no usable branch (an old file predating the shape, or one
    that fails check_diagram) still needs to be visible, so it lands in one
    "unclassified" bucket instead of disappearing from the total map.
    """
    tree = {}
    unclassified = []
    for slug in sorted(features):
        info = features[slug]
        if not info["exists"]:
            continue
        if not info.get("branch_top"):
            unclassified.append((slug, info))
            continue
        tree.setdefault(info["branch_top"], {}).setdefault(
            info.get("branch_sub") or "", []).append((slug, info))

    def _feature_li(slug, info):
        return '<li><a href="{slug}.html">{title}</a></li>'.format(
            slug=slug, title=html.escape(info["title"]))

    parts = ['<ul class="cay-nhanh">']
    for top in sorted(tree):
        parts.append('<li><strong>{}</strong><ul>'.format(html.escape(top)))
        for sub in sorted(tree[top]):
            parts.append('<li>{}<ul>'.format(html.escape(sub)))
            parts.extend(_feature_li(slug, info) for slug, info in tree[top][sub])
            parts.append('</ul></li>')
        parts.append('</ul></li>')
    if unclassified:
        parts.append('<li><em>{}</em><ul>'.format(html.escape(TEXT_TONG_CHUA_GAN_NHANH)))
        parts.extend(_feature_li(slug, info) for slug, info in unclassified)
        parts.append('</ul></li>')
    parts.append('</ul>')
    return "".join(parts)


KIND_NHANH_TONG = "nhanh-tong"
KIND_NHANH_CON = "nhanh-con"
KIND_FEATURE = "feature"


def build_branch_model(features):
    """Turn the `{slug: info}` map of collect_total_data into a 3-tier tree.

    Returns `{"nodes": [...], "edges": [...]}` — pure data, no markup, so the
    layout and the SVG can be tested apart from it.

    A node is `{"id", "kind", "label", "slug", "href", "thieu_file", "col"}`:
    `kind` is one of KIND_NHANH_TONG / KIND_NHANH_CON / KIND_FEATURE and `col`
    is that tier's column index (0, 1, 2). Only a feature node carries `slug`;
    only a feature whose diagram file exists carries an `href`, because a link
    to a page that was never rendered is a dead link, not a shortcut.

    A feature with no branch line — an old file predating the shape, or a slug
    that only ever appeared as another feature's dependency target — lands under one
    single "unclassified" top branch instead of vanishing from the map.
    """
    tree = {}
    unclassified = []
    for slug in sorted(features):
        info = features[slug]
        if not info.get("branch_top"):
            unclassified.append((slug, info))
            continue
        tree.setdefault(info["branch_top"], {}).setdefault(
            info.get("branch_sub") or "", []).append((slug, info))

    nodes = []
    edges = []

    def _them_feature(parent_id, slug, info):
        exists = bool(info.get("exists"))
        nodes.append({
            "id": "f-" + slug, "kind": KIND_FEATURE, "col": 2,
            "label": info.get("title") or slug, "slug": slug,
            "href": (slug + ".html") if exists else None,
            "thieu_file": not exists,
        })
        edges.append({"from": parent_id, "to": "f-" + slug})

    for i, top in enumerate(sorted(tree)):
        top_id = "t{}".format(i)
        nodes.append({"id": top_id, "kind": KIND_NHANH_TONG, "col": 0, "label": top,
                      "slug": None, "href": None, "thieu_file": False})
        for j, sub in enumerate(sorted(tree[top])):
            sub_id = "{}s{}".format(top_id, j)
            nodes.append({"id": sub_id, "kind": KIND_NHANH_CON, "col": 1, "label": sub,
                          "slug": None, "href": None, "thieu_file": False})
            edges.append({"from": top_id, "to": sub_id})
            for slug, info in tree[top][sub]:
                _them_feature(sub_id, slug, info)

    if unclassified:
        top_id = "t-chua-gan"
        nodes.append({"id": top_id, "kind": KIND_NHANH_TONG, "col": 0,
                      "label": TEXT_TONG_CHUA_GAN_NHANH, "slug": None, "href": None,
                      "thieu_file": False})
        for slug, info in unclassified:
            _them_feature(top_id, slug, info)

    return {"nodes": nodes, "edges": edges}


BRANCH_COL_W = (180, 210, 250)   # box width per tier: top branch, sub branch, feature
BRANCH_COL_GAP = 56
BRANCH_ROW_GAP = 12

TEXT_CAY_CLAIM = ("Cây nhánh: {tong} nhánh tổng, {con} nhánh con, {feature} feature — "  # i18n-allow
                  "ô nét đứt là feature chưa có sơ đồ")  # i18n-allow


def layout_branch_tree(model):
    """Place every node of build_branch_model on a 3-column canvas.

    Returns `{"boxes": {id: {"x","y","w","h","lines"}}, "width", "height"}`.

    Leaves are stacked top to bottom in model order and a parent is centred on
    the span of its own children, so a column never reuses another column's x
    range and two boxes of one column never share a y range — the same
    non-overlap invariant layout_flow relies on, reached the same way.
    """
    nodes = {n["id"]: n for n in model["nodes"]}
    children = {}
    for edge in model["edges"]:
        children.setdefault(edge["from"], []).append(edge["to"])
    has_parent = {edge["to"] for edge in model["edges"]}
    roots = [n["id"] for n in model["nodes"] if n["id"] not in has_parent]

    boxes = {}
    for node_id, node in nodes.items():
        width = BRANCH_COL_W[node["col"]]
        lines = wrap_label(node["label"], _max_chars(width))
        boxes[node_id] = {
            "x": sum(BRANCH_COL_W[:node["col"]]) + node["col"] * BRANCH_COL_GAP + FLOW_MARGIN,
            "y": 0.0, "w": width,
            "h": max(FLOW_MIN_H, len(lines) * FLOW_LINE_H + 2 * FLOW_PAD_Y),
            "lines": lines,
        }

    cursor = [float(FLOW_MARGIN)]

    def _place(node_id):
        """Depth-first: leaves take the next free row, a parent centres on them."""
        kids = children.get(node_id, [])
        box = boxes[node_id]
        if not kids:
            box["y"] = cursor[0]
            cursor[0] += box["h"] + BRANCH_ROW_GAP
            return box["y"], box["y"] + box["h"]
        spans = [_place(kid) for kid in kids]
        top, bottom = spans[0][0], spans[-1][1]
        box["y"] = (top + bottom) / 2 - box["h"] / 2
        return min(top, box["y"]), max(bottom, box["y"] + box["h"])

    for root in roots:
        _place(root)

    width = FLOW_MARGIN * 2 + sum(BRANCH_COL_W) + BRANCH_COL_GAP * 2
    height = max([FLOW_MARGIN] + [b["y"] + b["h"] + FLOW_MARGIN for b in boxes.values()])
    return {"boxes": boxes, "width": width, "height": height}


def render_branch_svg(model, layout, marker_suffix="cay"):
    """The branch tree as one figure: top branch → sub branch → feature.

    A feature that has a rendered page is wrapped in an `<a href>` so the box
    itself is the link; a feature with no diagram file yet is drawn dashed and
    dimmed and carries no link, because a link to a page nobody rendered is a
    dead link. Returns "" for an empty model.
    """
    nodes = model["nodes"]
    if not nodes:
        return ""
    boxes = layout["boxes"]
    marker_id = "mui-ten-{}".format(marker_suffix)
    dem = {KIND_NHANH_TONG: 0, KIND_NHANH_CON: 0, KIND_FEATURE: 0}
    for node in nodes:
        dem[node["kind"]] = dem.get(node["kind"], 0) + 1
    claim = TEXT_CAY_CLAIM.format(tong=dem[KIND_NHANH_TONG], con=dem[KIND_NHANH_CON],
                                  feature=dem[KIND_FEATURE])

    parts = [
        '<figure class="cay-fig">',
        '<svg viewBox="0 0 {w} {h}" role="img" aria-label="{claim}">'.format(
            w=_num(layout["width"]), h=_num(layout["height"]), claim=html.escape(claim)),
        _svg_marker(marker_id),
    ]
    for edge in model["edges"]:
        a, b = boxes[edge["from"]], boxes[edge["to"]]
        parts.append(_svg_mui_ten(a["x"] + a["w"], a["y"] + a["h"] / 2,
                                  b["x"], b["y"] + b["h"] / 2, marker_id))
    for node in nodes:
        box = boxes[node["id"]]
        extra = ' stroke-dasharray="4 3"' if node["thieu_file"] else ""
        label_extra = ' class="dim"' if node["thieu_file"] else ""
        shape = _svg_hop(box["x"], box["y"], box["w"], box["h"], extra)
        label = _svg_nhan_nhieu_dong(box["x"] + box["w"] / 2, box["y"] + box["h"] / 2,
                                     box["lines"], extra=label_extra)
        if node.get("href"):
            parts.append('<a href="{href}">{shape}{label}</a>'.format(
                href=html.escape(node["href"]), shape=shape, label=label))
        else:
            parts.append(shape)
            parts.append(label)
    parts.append("</svg>")
    parts.append("<figcaption>{}</figcaption>".format(html.escape(claim + ".")))
    parts.append("</figure>")
    return "".join(parts)


def render_total_page(features):
    """Build the self-contained aggregate HTML page: branch tree + dependency grid.

    Pure: `features` is already-parsed data (see collect_total_data), no file I/O
    here. A depends target with no entry in `features` is filled in as a missing
    stub via `build_link_graph` — the same pure grid function `lien-he` uses —
    so this never re-derives which slugs are dangling on its own.
    """
    feature_deps = {slug: [dep for dep, _reason in info["depends"]]
                     for slug, info in features.items()}
    missing = build_link_graph(feature_deps)["missing"]
    full = dict(features)
    for slug in missing:
        full.setdefault(slug, {"title": None, "branch_top": None, "branch_sub": None,
                                "depends": [], "exists": False})

    positions, columns = _layout_grid(full)
    branch_model = build_branch_model(full)
    branch_svg = render_branch_svg(branch_model, layout_branch_tree(branch_model))
    branch_wrap = '<div class="cay-wrap">{}</div>'.format(branch_svg) if branch_svg else ""
    _log("render tong: cay nhanh — {} node, {} canh".format(
        len(branch_model["nodes"]), len(branch_model["edges"])))
    branch_tree = branch_wrap + _render_branch_tree(full)
    grid_svg = _render_dependency_svg(full, positions, columns)
    edge_list = _render_edge_list(full)
    style = STYLE + STYLE_TONG

    return (
        '<!doctype html>\n<html lang="vi">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>{title}</title>\n<style>{style}</style>\n</head>\n<body>\n'
        '<main>\n<header>\n<h1>{title}</h1>\n</header>\n'
        '<section id="cay-nhanh"><h2>{h_cay}</h2>{tree}</section>\n'
        '<section id="luoi-phu-thuoc"><h2>{h_luoi}</h2>'
        '<div class="grid-wrap">{svg}</div>{edges}</section>\n'
        '</main>\n</body>\n</html>\n'
    ).format(
        title=html.escape(TEXT_TONG_TITLE), style=style,
        h_cay=html.escape(TEXT_TONG_HEADING_CAY), tree=branch_tree,
        h_luoi=html.escape(TEXT_TONG_HEADING_LUOI), svg=grid_svg, edges=edge_list,
    )


def default_total_output_path(root=None):
    """`<root>/docs/tdq/mind-map/index.html` — the aggregate page's fixed name."""
    return os.path.join(root or project_dir(), MIND_MAP_DIR_REL, "index.html")


# ------------------------------------------------------------------------- CLI
def default_output_path(diagram_path, root=None):
    """`<root>/docs/tdq/mind-map/<slug>.html` from `<anything>/<slug>.md`."""
    slug = os.path.splitext(os.path.basename(diagram_path))[0]
    return os.path.join(root or project_dir(), MIND_MAP_DIR_REL, slug + ".html")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="mindmap_render.py",
        description="Render one feature's mind-map (.md) into a two-layer HTML page.")
    parser.add_argument("file", nargs="?", default=None,
                        help="path of the diagram file to render (omit when using --tong)")
    parser.add_argument("--tong", action="store_true",
                        help="render the aggregate map of every feature under "
                             "docs/tdq/mind-map/ instead of a single feature")
    parser.add_argument("--graph", default=None,
                        help="path of graph.json (default: <project>/" + GRAPH_PATH_REL + ")")
    parser.add_argument("--sau", type=int, default=DEPTH_DEFAULT, dest="depth",
                        help="how many hops of calls to follow in the detail layer")
    parser.add_argument("-o", "--out", default=None, help="output .html path")
    return parser


def _write_html(html_text, out_path):
    """Shared write step for both render modes; the exit code the caller returns."""
    try:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html_text)
        return EXIT_OK
    except OSError as exc:
        _log("render: cannot write {} ({})".format(out_path, exc))
        print("render: cannot write {} ({})".format(out_path, exc), file=sys.stderr)
        return EXIT_SYNTAX


def main(argv):
    args = build_parser().parse_args(argv)
    root = project_dir()

    if args.tong:
        features = collect_total_data(root)
        html_text = render_total_page(features)
        out_path = args.out or default_total_output_path(root)
        code = _write_html(html_text, out_path)
        if code == EXIT_OK:
            _log("render: wrote {} — {} feature(s)".format(out_path, len(features)))
            print("render: wrote {} — {} feature(s)".format(out_path, len(features)))
        return code

    if not args.file:
        print("render: either FILE or --tong is required", file=sys.stderr)
        return EXIT_SYNTAX

    lines = read_diagram(args.file)
    if lines is None:
        _log("render: cannot read {}".format(args.file))
        print("render: cannot read {}".format(args.file), file=sys.stderr)
        return EXIT_SYNTAX

    graph_path = args.graph or os.path.join(root, GRAPH_PATH_REL)
    graph = load_graph(graph_path)

    try:
        html_text = render_feature_page(lines, args.file, graph=graph, depth=args.depth, project_root=root)
    except DiagramInvalid as exc:
        for violation in exc.violations:
            print(violation)
        _log("render: {} — {} violation(s), refusing to render".format(
            args.file, len(exc.violations)))
        return EXIT_VIOLATION

    out_path = args.out or default_output_path(args.file, root)
    try:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html_text)
    except OSError as exc:
        _log("render: cannot write {} ({})".format(out_path, exc))
        print("render: cannot write {} ({})".format(out_path, exc), file=sys.stderr)
        return EXIT_SYNTAX

    _log("render: wrote {} from {}".format(out_path, args.file))
    print("render: wrote {}".format(out_path))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
