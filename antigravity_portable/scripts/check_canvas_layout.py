#!/usr/bin/env python3
"""Check the geometry of an Excalidraw scene used as a multi-chapter product document.

The layout rules this script checks (settled in
`docs/tdq/spec/2026-08-12-hoan-thien-doc-excalidraw.md`):

- Every chapter N has exactly one frame `ch<N>-frame` (rectangle) and one title
    `ch<N>-title` (text) starting with the string `"<N>. "`.
- Chapter 0 is the table of contents; each TOC line is a text `toc-<N>` pointing at chapter N.
- Every other element must sit WHOLLY inside the frame of exactly one chapter.

No external package — stdlib only, per the repo's "0 external package" principle.
"""

import argparse
import collections
import json
import re
import sys
import urllib.request

FRAME_RE = re.compile(r"^ch(\d+)-frame$")
TITLE_RE = re.compile(r"^ch(\d+)-title$")
TOC_RE = re.compile(r"^toc-(\d+)$")

# An element out of place by less than this threshold counts as matching — it absorbs the
# rounding error of the frontend when it estimates text width.
TOL = 1.0


def load_elements(source):
    """Read the element list from a JSON file or from a running server."""
    if source.startswith("http://") or source.startswith("https://"):
        with urllib.request.urlopen(source, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    else:
        with open(source, encoding="utf-8") as fh:
            data = json.load(fh)
    if isinstance(data, dict):
        data = data.get("elements", [])
    return [e for e in data if isinstance(e, dict) and e.get("id")]


def bbox(el):
    x = float(el.get("x", 0))
    y = float(el.get("y", 0))
    w = float(el.get("width", 0) or 0)
    h = float(el.get("height", 0) or 0)
    if el.get("type") in ("arrow", "line") and el.get("points"):
        xs = [float(p[0]) for p in el["points"]]
        ys = [float(p[1]) for p in el["points"]]
        return (x + min(xs), y + min(ys), x + max(xs), y + max(ys))
    return (x, y, x + w, y + h)


def center(el):
    x0, y0, x1, y1 = bbox(el)
    return ((x0 + x1) / 2, (y0 + y1) / 2)


def boxes_overlap(a, b):
    return a[0] < b[2] - TOL and b[0] < a[2] - TOL and a[1] < b[3] - TOL and b[1] < a[3] - TOL


def contains(outer, inner):
    return (
        inner[0] >= outer[0] - TOL
        and inner[1] >= outer[1] - TOL
        and inner[2] <= outer[2] + TOL
        and inner[3] <= outer[3] + TOL
    )


def collect_frames(elements):
    """{chapter number: frame element}."""
    frames = {}
    for el in elements:
        m = FRAME_RE.match(el["id"])
        if m:
            frames[int(m.group(1))] = el
    return frames


def collect_titles(elements):
    titles = {}
    for el in elements:
        m = TITLE_RE.match(el["id"])
        if m:
            titles[int(m.group(1))] = el.get("text", "")
    return titles


def check_chapters(elements, expected):
    frames = collect_frames(elements)
    titles = collect_titles(elements)
    problems = []
    nums = sorted(n for n in frames if n >= 1)
    print(f"Found {len(nums)} chapter(s) (the ch0 table of contents not counted).")
    for n in nums:
        print(f"  {n:>2}. {titles.get(n, '<TITLE MISSING>')}")
    if nums != list(range(1, expected + 1)):
        problems.append(
            f"chapter numbers are not continuous 1..{expected}: found {nums}"
        )
    for n in nums:
        title = titles.get(n)
        if title is None:
            problems.append(f"chapter {n} is missing element ch{n}-title")
        elif not title.startswith(f"{n}. "):
            problems.append(
                f"the title of chapter {n} does not start with '{n}. ': {title!r}"
            )
    return problems


def check_overlap(elements):
    frames = collect_frames(elements)
    problems = []
    items = sorted(frames.items())
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            na, ea = items[i]
            nb, eb = items[j]
            if boxes_overlap(bbox(ea), bbox(eb)):
                problems.append(f"the frames of chapter {na} and {nb} overlap")
    print(f"Compared {len(items) * (len(items) - 1) // 2} frame pair(s).")
    return problems


def check_contain(elements):
    frames = collect_frames(elements)
    problems = []
    checked = 0
    for el in elements:
        if FRAME_RE.match(el["id"]):
            continue
        box = bbox(el)
        cx, cy = center(el)
        owner = None
        for n, frame in frames.items():
            fx0, fy0, fx1, fy1 = bbox(frame)
            if fx0 <= cx <= fx1 and fy0 <= cy <= fy1:
                owner = n
                break
        if owner is None:
            problems.append(f"{el['id']}: its centre is inside no chapter frame")
            continue
        checked += 1
        if not contains(bbox(frames[owner]), box):
            problems.append(
                f"{el['id']}: spills outside the frame of chapter {owner} "
                f"(element {box}, khung {bbox(frames[owner])})"
            )
        m = TITLE_RE.match(el["id"]) or re.match(r"^ch(\d+)-", el["id"])
        if m and int(m.group(1)) != owner:
            problems.append(
                f"{el['id']}: the id belongs to chapter {m.group(1)} but it sits in the frame of chapter {owner}"
            )
    print(f"Checked {checked} element(s) for containment.")
    return problems


def check_order(elements):
    frames = collect_frames(elements)
    problems = []
    nums = sorted(n for n in frames)
    for a, b in zip(nums, nums[1:]):
        ya = bbox(frames[a])[1]
        yb = bbox(frames[b])[1]
        if not ya < yb:
            problems.append(f"chapter {a} (y={ya}) does not sit above chapter {b} (y={yb})")
    print(f"Compared the vertical order of {len(nums)} frame(s).")
    return problems


def check_toc(elements):
    titles = collect_titles(elements)
    toc = {}
    for el in elements:
        m = TOC_RE.match(el["id"])
        if m:
            toc[int(m.group(1))] = el.get("text", "")
    problems = []
    for n, title in sorted(titles.items()):
        if n not in toc:
            problems.append(f"the table of contents has no line for chapter {n}")
        elif title.strip() not in toc[n].strip():
            problems.append(
                f"TOC line {n} ({toc[n]!r}) does not match the real title ({title!r})"
            )
    extra = set(toc) - set(titles)
    for n in sorted(extra):
        problems.append(f"the table of contents has line {n} but there is no chapter {n}")
    print(f"Matched {len(titles)} title(s) against {len(toc)} TOC line(s).")
    return problems


def check_width(elements, expected_width):
    """Every chapter frame must be exactly the settled page width (A4 portrait @150dpi = 1240px)."""
    frames = collect_frames(elements)
    problems = []
    for n, frame in sorted(frames.items()):
        w = float(frame.get("width", 0) or 0)
        if abs(w - expected_width) > TOL:
            problems.append(
                f"the frame of chapter {n} is {w:g}px wide, the settled page is {expected_width:g}px"
            )
    print(f"Measured the width of {len(frames)} frame(s), settled page {expected_width:g}px.")
    return problems


# Excalidraw defaults to font size 20 (M) when an element records no `fontSize`.
DEFAULT_FONT_SIZE = 20


def check_fontsize(elements, minimum):
    """No text element may be smaller than the readable threshold."""
    problems = []
    checked = 0
    for el in elements:
        if el.get("type") != "text":
            continue
        checked += 1
        size = float(el.get("fontSize", DEFAULT_FONT_SIZE) or DEFAULT_FONT_SIZE)
        if size < minimum - TOL:
            problems.append(f"{el['id']}: font size {size:g} < threshold {minimum:g}")
    print(f"Measured the font size of {checked} text element(s), threshold {minimum:g}.")
    return problems


def report_prefix(elements):
    counter = collections.Counter(el["id"].split("-")[0] for el in elements)
    for prefix, count in sorted(counter.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"{prefix:24} {count}")
    return []


def report_region(elements):
    """Count elements per chapter frame — sturdier than counting by id prefix because a bound
    label generated by the frontend carries a random id."""
    frames = collect_frames(elements)
    counter = collections.Counter()
    for el in elements:
        if FRAME_RE.match(el["id"]):
            continue
        cx, cy = center(el)
        placed = False
        for n, frame in sorted(frames.items()):
            fx0, fy0, fx1, fy1 = bbox(frame)
            if fx0 <= cx <= fx1 and fy0 <= cy <= fy1:
                counter[n] += 1
                placed = True
                break
        if not placed:
            counter["outside every frame"] += 1
    for key in sorted(counter, key=lambda k: (isinstance(k, str), k)):
        label = f"chapter {key}" if isinstance(key, int) else key
        print(f"{label:24} {counter[key]}")
    return []


CHECKS = {
    "chapters": check_chapters,
    "width": check_width,
    "overlap": check_overlap,
    "contain": check_contain,
    "order": check_order,
    "toc": check_toc,
    "fontsize": check_fontsize,
    "count_by_prefix": report_prefix,
    "count_by_region": report_region,
}

# One check needs a parameter taken from the command-line flag of the same name; the other
# checks only take the element list.
ARG_FROM_FLAG = {"width", "fontsize"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "scene",
        help="path to the .excalidraw scene file, or the /api/elements URL of a running canvas",
    )
    parser.add_argument("--chapters", action="store_true", help="N chapters present, numbers continuous")
    parser.add_argument(
        "--width",
        type=float,
        help="every chapter frame is exactly this many px wide (A4 portrait @150dpi = 1240)",
    )
    parser.add_argument("--overlap", action="store_true", help="no two frames overlap")
    parser.add_argument("--contain", action="store_true", help="every element sits wholly inside a frame")
    parser.add_argument("--order", action="store_true", help="the vertical order matches the chapter numbers")
    parser.add_argument("--toc", action="store_true", help="the table of contents matches the real titles")
    parser.add_argument(
        "--fontsize",
        type=float,
        help="no text element has a font size smaller than this",
    )
    parser.add_argument("--count-by-prefix", action="store_true", help="count elements by id prefix")
    parser.add_argument("--count-by-region", action="store_true", help="count elements by chapter frame")
    parser.add_argument("--expect", type=int, default=13, help="how many chapters are expected (default 13)")
    args = parser.parse_args(argv)

    selected = [name for name in CHECKS if getattr(args, name) is not None
                and getattr(args, name) is not False]
    if not selected:
        parser.error("pick at least one check")

    elements = load_elements(args.scene)
    print(f"Read {len(elements)} element(s) from {args.scene}\n")

    all_problems = []
    for name in selected:
        print(f"── {name} ──")
        fn = CHECKS[name]
        if name == "chapters":
            problems = fn(elements, args.expect)
        elif name in ARG_FROM_FLAG:
            problems = fn(elements, getattr(args, name))
        else:
            problems = fn(elements)
        for p in problems:
            print(f"  ✗ {p}")
        if not problems:
            print("  ✓ PASS")
        print()
        all_problems.extend(problems)

    if all_problems:
        print(f"FAIL — {len(all_problems)} problem(s).")
        return 1
    print("PASS — every selected check holds.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
