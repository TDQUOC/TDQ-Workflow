#!/usr/bin/env python3
"""Kiểm hình học một scene Excalidraw dùng làm product document nhiều chương.

Quy ước bố cục mà script này kiểm (chốt trong
`docs/tdq/spec/2026-08-12-hoan-thien-doc-excalidraw.md`):

- Mỗi chương N có đúng một khung `ch<N>-frame` (rectangle) và một tiêu đề
  `ch<N>-title` (text) bắt đầu bằng chuỗi `"<N>. "`.
- Chương 0 là mục lục; mỗi dòng mục lục là text `toc-<N>` trỏ tới chương N.
- Mọi phần tử khác phải nằm TRỌN trong khung của đúng một chương.

Không phụ thuộc package ngoài — chỉ stdlib, đúng nguyên tắc "0 package ngoài"
của repo.
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

# Phần tử nằm lệch dưới ngưỡng này coi như khớp — bù sai số làm tròn của
# frontend khi ước lượng bề rộng chữ.
TOL = 1.0


def load_elements(source):
    """Đọc danh sách element từ file JSON hoặc từ server đang chạy."""
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
    """{số chương: element khung}."""
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
    print(f"Tìm thấy {len(nums)} chương (chưa tính mục lục ch0).")
    for n in nums:
        print(f"  {n:>2}. {titles.get(n, '<THIẾU TIÊU ĐỀ>')}")
    if nums != list(range(1, expected + 1)):
        problems.append(
            f"số chương không liên tục 1..{expected}: thấy {nums}"
        )
    for n in nums:
        title = titles.get(n)
        if title is None:
            problems.append(f"chương {n} thiếu element ch{n}-title")
        elif not title.startswith(f"{n}. "):
            problems.append(
                f"tiêu đề chương {n} không bắt đầu bằng '{n}. ': {title!r}"
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
                problems.append(f"khung chương {na} và {nb} chồng lấn")
    print(f"Đã so {len(items) * (len(items) - 1) // 2} cặp khung.")
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
            problems.append(f"{el['id']}: tâm không nằm trong khung chương nào")
            continue
        checked += 1
        if not contains(bbox(frames[owner]), box):
            problems.append(
                f"{el['id']}: tràn ra ngoài khung chương {owner} "
                f"(element {box}, khung {bbox(frames[owner])})"
            )
        m = TITLE_RE.match(el["id"]) or re.match(r"^ch(\d+)-", el["id"])
        if m and int(m.group(1)) != owner:
            problems.append(
                f"{el['id']}: id thuộc chương {m.group(1)} nhưng nằm trong khung chương {owner}"
            )
    print(f"Đã kiểm {checked} phần tử nằm trong khung.")
    return problems


def check_order(elements):
    frames = collect_frames(elements)
    problems = []
    nums = sorted(n for n in frames)
    for a, b in zip(nums, nums[1:]):
        ya = bbox(frames[a])[1]
        yb = bbox(frames[b])[1]
        if not ya < yb:
            problems.append(f"chương {a} (y={ya}) không nằm trên chương {b} (y={yb})")
    print(f"Đã so thứ tự dọc của {len(nums)} khung.")
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
            problems.append(f"mục lục thiếu dòng cho chương {n}")
        elif title.strip() not in toc[n].strip():
            problems.append(
                f"dòng mục lục {n} ({toc[n]!r}) không khớp tiêu đề thật ({title!r})"
            )
    extra = set(toc) - set(titles)
    for n in sorted(extra):
        problems.append(f"mục lục có dòng {n} nhưng không có chương {n}")
    print(f"Đã đối chiếu {len(titles)} tiêu đề với {len(toc)} dòng mục lục.")
    return problems


def check_width(elements, expected_width):
    """Mọi khung chương phải rộng đúng khổ đã chốt (A4 dọc @150dpi = 1240px)."""
    frames = collect_frames(elements)
    problems = []
    for n, frame in sorted(frames.items()):
        w = float(frame.get("width", 0) or 0)
        if abs(w - expected_width) > TOL:
            problems.append(
                f"khung chương {n} rộng {w:g}px, khổ chốt là {expected_width:g}px"
            )
    print(f"Đã đo bề ngang {len(frames)} khung, khổ chốt {expected_width:g}px.")
    return problems


# Excalidraw mặc định cỡ chữ 20 (M) khi element không ghi `fontSize`.
DEFAULT_FONT_SIZE = 20


def check_fontsize(elements, minimum):
    """Không phần tử chữ nào nhỏ hơn ngưỡng đọc được."""
    problems = []
    checked = 0
    for el in elements:
        if el.get("type") != "text":
            continue
        checked += 1
        size = float(el.get("fontSize", DEFAULT_FONT_SIZE) or DEFAULT_FONT_SIZE)
        if size < minimum - TOL:
            problems.append(f"{el['id']}: cỡ chữ {size:g} < ngưỡng {minimum:g}")
    print(f"Đã đo cỡ chữ {checked} phần tử text, ngưỡng {minimum:g}.")
    return problems


def report_prefix(elements):
    counter = collections.Counter(el["id"].split("-")[0] for el in elements)
    for prefix, count in sorted(counter.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"{prefix:24} {count}")
    return []


def report_region(elements):
    """Đếm phần tử theo khung chương — bền hơn đếm theo prefix id vì bound
    label do frontend sinh mang id ngẫu nhiên."""
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
            counter["ngoài mọi khung"] += 1
    for key in sorted(counter, key=lambda k: (isinstance(k, str), k)):
        label = f"chương {key}" if isinstance(key, int) else key
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

# Phép kiểm cần một tham số lấy từ chính cờ dòng lệnh cùng tên; các phép kiểm
# còn lại chỉ nhận danh sách element.
ARG_FROM_FLAG = {"width", "fontsize"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "scene",
        help="đường dẫn file scene .excalidraw, hoặc URL /api/elements của canvas đang chạy",
    )
    parser.add_argument("--chapters", action="store_true", help="đủ N chương, số liên tục")
    parser.add_argument(
        "--width",
        type=float,
        help="mọi khung chương rộng đúng số px này (khổ A4 dọc @150dpi = 1240)",
    )
    parser.add_argument("--overlap", action="store_true", help="không khung nào chồng lấn")
    parser.add_argument("--contain", action="store_true", help="mọi phần tử nằm trọn trong khung")
    parser.add_argument("--order", action="store_true", help="thứ tự dọc khớp số chương")
    parser.add_argument("--toc", action="store_true", help="mục lục khớp tiêu đề thật")
    parser.add_argument(
        "--fontsize",
        type=float,
        help="không phần tử text nào có cỡ chữ nhỏ hơn số này",
    )
    parser.add_argument("--count-by-prefix", action="store_true", help="đếm phần tử theo prefix id")
    parser.add_argument("--count-by-region", action="store_true", help="đếm phần tử theo khung chương")
    parser.add_argument("--expect", type=int, default=13, help="số chương mong đợi (mặc định 13)")
    args = parser.parse_args(argv)

    selected = [name for name in CHECKS if getattr(args, name) is not None
                and getattr(args, name) is not False]
    if not selected:
        parser.error("phải chọn ít nhất một phép kiểm")

    elements = load_elements(args.scene)
    print(f"Đọc {len(elements)} phần tử từ {args.scene}\n")

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
        print(f"FAIL — {len(all_problems)} vấn đề.")
        return 1
    print("PASS — mọi phép kiểm đã chọn đều đạt.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
