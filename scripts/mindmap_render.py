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
    TITLE_LINE_RE,
    STEP_HINT_RE,
    STEP_ERROR_MARK,
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
        '<ol class="steps">{steps}</ol>{depends}'
        '</section>'
    ).format(steps="".join(items), depends=depends_html)


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
figure.call-fig { margin: 10px 0 4px; }
figure.call-fig svg { max-width: 100%; height: auto; display: block; }
figcaption { font-size: 12px; color: var(--muted); margin-top: 4px; }
.step-detail { border-top: 1px solid var(--border); padding: 10px 0; }
details summary { cursor: pointer; color: var(--accent); }
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


# ------------------------------------------------------------------------- CLI
def default_output_path(diagram_path, root=None):
    """`<root>/docs/tdq/mind-map/<slug>.html` from `<anything>/<slug>.md`."""
    slug = os.path.splitext(os.path.basename(diagram_path))[0]
    return os.path.join(root or project_dir(), MIND_MAP_DIR_REL, slug + ".html")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="mindmap_render.py",
        description="Render one feature's mind-map (.md) into a two-layer HTML page.")
    parser.add_argument("file", help="path of the diagram file to render")
    parser.add_argument("--graph", default=None,
                        help="path of graph.json (default: <project>/" + GRAPH_PATH_REL + ")")
    parser.add_argument("--sau", type=int, default=DEPTH_DEFAULT, dest="depth",
                        help="how many hops of calls to follow in the detail layer")
    parser.add_argument("-o", "--out", default=None, help="output .html path")
    return parser


def main(argv):
    args = build_parser().parse_args(argv)
    lines = read_diagram(args.file)
    if lines is None:
        _log("render: cannot read {}".format(args.file))
        print("render: cannot read {}".format(args.file), file=sys.stderr)
        return EXIT_SYNTAX

    root = project_dir()
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
