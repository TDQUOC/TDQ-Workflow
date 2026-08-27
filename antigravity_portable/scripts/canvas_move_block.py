#!/usr/bin/env python3
"""Move an existing block on the Excalidraw canvas into a chapter of the document.

Why this script instead of calling `update_element`: on the canvas server in use
(127.0.0.1:17739), `update_element` returns "success" with a bumped version while the
`x/y/width/height/text` attributes do NOT change — reproduced twice. What works is delete
then recreate. This script does exactly that, and at the same time:

- reassigns ids under the `ch<N>-` prefix so the checking script knows which chapter an element belongs to,
- remaps every id reference (`containerId`, `boundElements`, `startBinding`,
    `endBinding`, `frameId`) onto the new ids,
- translates the coordinates and centres the block inside the 2640px chapter frame,
- renames the outer frame to `ch<N>-frame` and the title to `ch<N>-title`.

Stdlib only.
"""

import argparse
import json
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:17739"
CHAPTER_X = 40
CHAPTER_W = 1240   # A4 portrait @150dpi
PAD = 20


def api(path, method="GET", payload=None):
    url = f"{BASE}{path}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    if data:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode("utf-8")
    return json.loads(body) if body else {}


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


def select(elements, region):
    """Pick the elements whose CENTRE lies inside the source region (x0,y0,x1,y1)."""
    x0, y0, x1, y1 = region
    picked = []
    for el in elements:
        bx0, by0, bx1, by1 = bbox(el)
        cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
        if x0 <= cx <= x1 and y0 <= cy <= y1:
            picked.append(el)
    return picked


def pick_frame(picked):
    """The outer frame = the rectangle with the largest area."""
    rects = [e for e in picked if e.get("type") == "rectangle"]
    if not rects:
        return None
    return max(rects, key=lambda e: (e.get("width", 0) or 0) * (e.get("height", 0) or 0))


def pick_title(picked, frame_id):
    """The title = the free text with the largest fontSize, not a bound label."""
    texts = [
        e
        for e in picked
        if e.get("type") == "text" and not e.get("containerId") and e["id"] != frame_id
    ]
    if not texts:
        return None
    return max(texts, key=lambda e: e.get("fontSize", 0) or 0)


def plan_move(elements, chapter, region, target_y, new_title):
    """Precompute the move of ONE block against the scene SNAPSHOT passed in.

    Returns `(picked, new_elements)`. Kept apart from the writing step so several blocks can be
    computed against one single snapshot — computing-then-writing one at a time lets a block
    already moved to its new position fall into the source region of the next one and be dragged along.
    """
    picked = select(elements, region)
    if not picked:
        raise SystemExit(f"No element found inside the region {region}")

    frame = pick_frame(picked)
    if frame is None:
        raise SystemExit("No outer frame (rectangle) found in the block")
    title = pick_title(picked, frame["id"])

    boxes = [bbox(e) for e in picked]
    min_x = min(b[0] for b in boxes)
    min_y = min(b[1] for b in boxes)
    max_x = max(b[2] for b in boxes)
    max_y = max(b[3] for b in boxes)
    content_w = max_x - min_x
    content_h = max_y - min_y

    # Centre the content across the chapter width; the outer frame spans the whole 2640px.
    dx = CHAPTER_X + (CHAPTER_W - content_w) / 2 - min_x
    dy = target_y + PAD - min_y
    frame_h = content_h + 2 * PAD

    id_map = {}
    for i, el in enumerate(picked):
        if el["id"] == frame["id"]:
            id_map[el["id"]] = f"ch{chapter}-frame"
        elif title is not None and el["id"] == title["id"]:
            id_map[el["id"]] = f"ch{chapter}-title"
        else:
            id_map[el["id"]] = f"ch{chapter}-e{i:03d}"

    def remap(old):
        return id_map.get(old, old)

    new_elements = []
    for el in picked:
        e = json.loads(json.dumps(el))  # deep copy
        e["id"] = id_map[el["id"]]
        e["x"] = float(el.get("x", 0)) + dx
        e["y"] = float(el.get("y", 0)) + dy
        if el["id"] == frame["id"]:
            e["x"] = CHAPTER_X
            e["y"] = target_y
            e["width"] = CHAPTER_W
            e["height"] = frame_h
        if title is not None and el["id"] == title["id"] and new_title:
            e["text"] = new_title
            # widen for a longer title: factor 0.75 for accented text
            need = len(new_title) * float(e.get("fontSize", 20) or 20) * 0.75
            e["width"] = max(float(e.get("width", 0) or 0), need)
        if e.get("containerId"):
            e["containerId"] = remap(e["containerId"])
        if e.get("frameId"):
            e["frameId"] = remap(e["frameId"])
        if isinstance(e.get("boundElements"), list):
            e["boundElements"] = [
                {**b, "id": remap(b["id"])} if isinstance(b, dict) and "id" in b else b
                for b in e["boundElements"]
            ]
        for key in ("startBinding", "endBinding"):
            b = e.get(key)
            if isinstance(b, dict) and b.get("elementId"):
                e[key] = {**b, "elementId": remap(b["elementId"])}
        for key in ("createdAt", "updatedAt", "version", "versionNonce", "updated"):
            e.pop(key, None)
        new_elements.append(e)

    print(f"Chapter {chapter}: {len(picked)} element(s)")
    print(f"  source content x[{min_x:.0f},{max_x:.0f}] y[{min_y:.0f},{max_y:.0f}]")
    print(f"  shift dx={dx:.0f} dy={dy:.0f} · new frame y={target_y} height {frame_h:.0f}")
    print(f"  khung: {frame['id']} → ch{chapter}-frame")
    if title is not None:
        print(f"  title: {title['id']} → ch{chapter}-title = {new_title!r}")
    return picked, new_elements


def write_moves(batches):
    """Write several moves: delete every old copy FIRST, then recreate them all."""
    old_ids = [el["id"] for picked, _ in batches for el in picked]
    new_elements = [e for _, news in batches for e in news]
    for el_id in old_ids:
        api(f"/api/elements/{el_id}", method="DELETE")
    res = api("/api/elements/batch", method="POST", payload={"elements": new_elements})
    print(f"Deleted {len(old_ids)}, recreated {res.get('count', 0)} element(s)")
    if res.get("count") != len(old_ids):
        print(f"✗ COUNT MISMATCH: deleted {len(old_ids)}, created {res.get('count')}")
        return 1
    return 0


def move_block(chapter, region, target_y, new_title, dry_run=False):
    elements = api("/api/elements")["elements"]
    batch = plan_move(elements, chapter, region, target_y, new_title)
    if dry_run:
        print("  (dry-run, nothing written)")
        return 0
    return write_moves([batch])


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--chapter", type=int, required=True)
    p.add_argument("--region", required=True, help="x0,y0,x1,y1 of the source region")
    p.add_argument("--target-y", type=float, required=True)
    p.add_argument("--title", required=True, help="new title, must start with '<N>. '")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)

    if not args.title.startswith(f"{args.chapter}. "):
        p.error(f"the title must start with '{args.chapter}. '")
    region = tuple(float(v) for v in args.region.split(","))
    if len(region) != 4:
        p.error("--region needs exactly 4 numbers")
    return move_block(args.chapter, region, args.target_y, args.title, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
