#!/usr/bin/env python3
"""Rebuild the whole product document at A4 portrait width, 1240px.

How (settled in `docs/tdq/spec/2026-08-12-layout-a4-doc.md`):

- Read the OLD scene, keeping the wording EXACTLY — only rewrapping it to the new width.
- The seven multi-column chapters (1, 3, 6, 8, 11, 12, 13) are folded into ONE column by
    the shared builder: each old card (rectangle + head text + body text) becomes one new
    card 1160px wide.
- The two chapters wide by nature (4, 7) are laid out by hand, vertically, in
  `canvas_a4_ch4_ch7.py`.
- The four blocks already narrow (2, 5, 9, 10) are only MOVED: translated whole into the
    new frame, their content untouched.
- Chapter 0 is the table of contents, regenerated from the real titles of the 13 chapters.

Builds to a FILE first so `check_canvas_layout.py` can inspect it, and only then writes to
the canvas in one delete-then-create pass (`--apply`). Stdlib only.
"""

import argparse
import json
import re
import sys

from canvas_draw import K_VI, PALETTE, SAFE, W, X, fit
from canvas_move_block import api, bbox

# ── page size ─────────────────────────────────────────────────────────────
MARGIN = 40                      # inner margin of the frame
CARD_W = W - 2 * MARGIN          # 1160
PAD = 20                         # inner padding of a card
GAP = 24                         # vertical gap between two cards
CHAPTER_GAP = 120                # gap between two chapter frames
TITLE_BAND = 90                  # the band reserved for the chapter title
BOTTOM = 40

BODY_SIZE = 16
HEAD_SIZE = 20
LINE_H = 1.35


def max_chars(box_w, font_size):
    """Max characters per line, per the rule text ≤ 70% of the cell width (Vietnamese)."""
    return int(box_w * SAFE / (font_size * K_VI))


# A directory-tree line aligns its columns with spaces, so it must NOT be joined and must NOT
# be wrapped by word — only the padding between two columns may be squeezed.
TREE_GLYPHS = ("├", "└", "│", "─")


def is_tree_line(line):
    return any(g in line for g in TREE_GLYPHS)


def squeeze_tree_line(line, limit):
    """Squeeze the padding between two columns so a tree line fits the new width."""
    while len(line) > limit:
        runs = list(re.finditer(r" {3,}", line))
        if not runs:
            break
        m = max(runs, key=lambda r: len(r.group()))
        cut = min(len(m.group()) - 2, len(line) - limit)
        line = line[: m.start()] + " " * (len(m.group()) - cut) + line[m.end():]
    return line[:limit]


def unwrap(text, orig_w, font_size):
    """Re-join the lines that were only broken because they overflowed the OLD cell.

    A line nearly filling the old cell width was broken for lack of room, not on purpose —
    join it with the next line so the new version rewraps it neatly. A short line, an empty
    line, a bullet and a command line keep their break.
    """
    limit = max_chars(orig_w, font_size)
    out = []
    for line in text.split("\n"):
        joinable = (
            out and out[-1].strip()
            and len(out[-1]) >= limit * 0.85
            and line.strip()
            and line.lstrip()[:2] not in ("· ", "- ", "• ", "› ")
            and line[:1] not in (" ", "\t")
            and not is_tree_line(line)
            and not is_tree_line(out[-1])
        )
        if joinable:
            out[-1] = out[-1].rstrip() + " " + line.strip()
        else:
            out.append(line)
    return "\n".join(out)


def rewrap(text, box_w, font_size):
    """Rewrap to the new width, keeping EVERY word as it was.

    Each old line is broken further when too long; the continuation line is indented to line
    up with the content of the original line (bullet `·`, dash, numbering).
    """
    limit = max_chars(box_w, font_size)
    out = []
    for line in text.split("\n"):
        if is_tree_line(line):
            out.append(squeeze_tree_line(line, limit))
            continue
        if len(line) <= limit:
            out.append(line)
            continue
        lead = len(line) - len(line.lstrip())
        rest = line.lstrip()
        indent = " " * lead
        if rest[:2] in ("· ", "- ", "• ", "› "):
            cont = indent + "  "
        else:
            cont = indent
        cur = indent
        for word in rest.split(" "):
            candidate = f"{cur}{word}" if cur.strip() == "" else f"{cur} {word}"
            if len(candidate) > limit and cur.strip():
                out.append(cur)
                cur = f"{cont}{word}"
            else:
                cur = candidate
        if cur.strip():
            out.append(cur)
    return "\n".join(out)


def text_el(eid, x, y, text, size, color, width):
    return {
        "id": eid, "type": "text", "x": x, "y": y,
        "width": width, "height": (text.count("\n") + 1) * size * LINE_H,
        "text": text, "fontSize": size, "strokeColor": color,
    }


class Builder:
    """Build the elements of one chapter at the narrow width, computing its height."""

    def __init__(self, number, title):
        self.n = number
        self.title = title
        self.body = []          # inner elements, y measured from 0 of the content area
        self.cursor = 0
        self._i = 0

    def _id(self, kind):
        self._i += 1
        return f"ch{self.n}-{kind}{self._i:03d}"

    def card(self, head, body, color, orig_w=None):
        if orig_w:
            body = unwrap(body, orig_w, BODY_SIZE)
        head = rewrap(head, CARD_W - 2 * PAD, HEAD_SIZE)
        body = rewrap(body, CARD_W - 2 * PAD, BODY_SIZE)
        fit(head, CARD_W - 2 * PAD, HEAD_SIZE, f"ch{self.n} head {head[:24]!r}")
        fit(body, CARD_W - 2 * PAD, BODY_SIZE, f"ch{self.n} body {head[:24]!r}")
        bg, stroke = PALETTE[color % len(PALETTE)]
        head_h = (head.count("\n") + 1) * HEAD_SIZE * LINE_H
        body_h = (body.count("\n") + 1) * BODY_SIZE * LINE_H
        h = PAD + head_h + 10 + body_h + PAD
        y = self.cursor
        self.body.append({
            "id": self._id("box"), "type": "rectangle",
            "x": X + MARGIN, "y": y, "width": CARD_W, "height": h,
            "backgroundColor": bg, "strokeColor": stroke, "fillStyle": "solid",
            "strokeWidth": 2, "roughness": 0, "roundness": {"type": 3},
        })
        self.body.append(text_el(self._id("t"), X + MARGIN + PAD, y + PAD,
                                 head, HEAD_SIZE, stroke, CARD_W - 2 * PAD))
        self.body.append(text_el(self._id("t"), X + MARGIN + PAD,
                                 y + PAD + head_h + 10,
                                 body, BODY_SIZE, "#1e1e1e", CARD_W - 2 * PAD))
        self.cursor = y + h + GAP
        return self

    def note(self, text, size=BODY_SIZE, color="#495057"):
        text = rewrap(text, CARD_W, size)
        fit(text, CARD_W, size, f"ch{self.n} note")
        h = (text.count("\n") + 1) * size * LINE_H
        self.body.append(text_el(self._id("t"), X + MARGIN, self.cursor,
                                 text, size, color, CARD_W))
        self.cursor += h + GAP
        return self

    def height(self):
        return TITLE_BAND + max(0, self.cursor - GAP) + BOTTOM

    def emit(self, top):
        """Return the real elements with absolute y, the frame starting at `top`."""
        h = self.height()
        els = [
            {"id": f"ch{self.n}-frame", "type": "rectangle", "x": X, "y": top,
             "width": W, "height": h, "strokeColor": "#1e1e1e",
             "backgroundColor": "transparent", "fillStyle": "solid",
             "strokeWidth": 2, "roughness": 0},
            text_el(f"ch{self.n}-title", X + MARGIN, top + 26,
                    f"{self.n}. {self.title}", 30, "#1971c2", CARD_W),
        ]
        for el in self.body:
            el = dict(el)
            el["y"] = el["y"] + top + TITLE_BAND
            els.append(el)
        return els, h


# ── reading the old scene ─────────────────────────────────────────────────

def load(path):
    data = json.load(open(path, encoding="utf-8"))
    return data["elements"] if isinstance(data, dict) else data


def chapter_elements(elements, n):
    """The elements of chapter n by centre inside the frame — catches random ids too."""
    frame = next(e for e in elements if e["id"] == f"ch{n}-frame")
    fx0, fy0, fx1, fy1 = bbox(frame)
    out = []
    for el in elements:
        if el["id"] == frame["id"]:
            continue
        x0, y0, x1, y1 = bbox(el)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        if fx0 <= cx <= fx1 and fy0 <= cy <= fy1:
            out.append(el)
    return frame, out


def extract_cards(elements, n):
    """Collect the (head, body) of each old card + the notes standing on their own."""
    frame, els = chapter_elements(elements, n)
    title = next(e["text"] for e in els if e["id"] == f"ch{n}-title")
    rects = [e for e in els if e.get("type") == "rectangle"]
    texts = [e for e in els if e.get("type") == "text" and e["id"] != f"ch{n}-title"]
    cards, used = [], set()
    for rect in sorted(rects, key=lambda e: (round(e["y"]), round(e["x"]))):
        rx0, ry0, rx1, ry1 = bbox(rect)
        inside = []
        for t in texts:
            x0, y0, x1, y1 = bbox(t)
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            if rx0 <= cx <= rx1 and ry0 <= cy <= ry1:
                inside.append(t)
        inside.sort(key=lambda e: (round(e["y"]), round(e["x"])))
        if not inside:
            continue
        used.update(id(t) for t in inside)
        head = inside[0]["text"]
        body = "\n".join(t["text"] for t in inside[1:])
        cards.append((head, body, float(rect.get("width", CARD_W))))
    notes = [t["text"] for t in sorted(texts, key=lambda e: round(e["y"]))
             if id(t) not in used]
    return title.split(". ", 1)[1], cards, notes


def build_generic(elements, n):
    title, cards, notes = extract_cards(elements, n)
    b = Builder(n, title)
    for i, (head, body, orig_w) in enumerate(cards):
        b.card(head, body, i, orig_w=orig_w - 2 * PAD)
    for note in notes:
        b.note(note)
    return b


# ── moving the 4 already-narrow chapters whole ────────────────────────────

def build_moved(elements, n, top):
    """Translate the whole block of chapter n into the new frame starting at `top`."""
    _, els = chapter_elements(elements, n)
    xs = [bbox(e)[0] for e in els]
    ys = [bbox(e)[1] for e in els]
    x1s = [bbox(e)[2] for e in els]
    y1s = [bbox(e)[3] for e in els]
    min_x, min_y, max_x, max_y = min(xs), min(ys), max(x1s), max(y1s)
    cw, chh = max_x - min_x, max_y - min_y
    if cw > W - 2 * MARGIN:
        raise SystemExit(f"chapter {n}: the block is {cw:.0f}px wide, it does not fit the {W}px page")
    dx = X + (W - cw) / 2 - min_x
    dy = top + MARGIN - min_y
    out = [{
        "id": f"ch{n}-frame", "type": "rectangle", "x": X, "y": top,
        "width": W, "height": chh + 2 * MARGIN, "strokeColor": "#1e1e1e",
        "backgroundColor": "transparent", "fillStyle": "solid",
        "strokeWidth": 2, "roughness": 0,
    }]
    for el in els:
        e = dict(el)
        e["x"] = float(e.get("x", 0)) + dx
        e["y"] = float(e.get("y", 0)) + dy
        for key in ("createdAt", "updatedAt", "version", "versionNonce", "updated"):
            e.pop(key, None)
        out.append(e)
    return out, chh + 2 * MARGIN


# ── table of contents ─────────────────────────────────────────────────────

def build_toc(titles, top):
    lines = ["0. Mục lục"] + [f"{n}. {t}" for n, t in sorted(titles.items())]  # i18n-allow
    els = []
    y = top + TITLE_BAND
    for i, line in enumerate(lines):
        els.append(text_el(f"toc-{i}", X + MARGIN, y, line, 18, "#1e1e1e", CARD_W))
        y += 18 * 1.9
    h = TITLE_BAND + len(lines) * 18 * 1.9 + BOTTOM
    frame = {"id": "ch0-frame", "type": "rectangle", "x": X, "y": top,
             "width": W, "height": h, "strokeColor": "#1e1e1e",
             "backgroundColor": "transparent", "fillStyle": "solid",
             "strokeWidth": 2, "roughness": 0}
    title = text_el("ch0-title", X + MARGIN, top + 26, "0. Mục lục", 30,  # i18n-allow
                    "#1971c2", CARD_W)
    return [frame, title] + els, h


# ── assembling the whole document ─────────────────────────────────────────

GENERIC = (1, 3, 6, 8, 11, 12, 13)
MOVED = (2, 5, 9, 10)
HANDMADE = (4, 7)


def build_all(old_path, handmade):
    old = load(old_path)
    titles = {}
    for n in range(1, 14):
        t = next(e["text"] for e in old if e["id"] == f"ch{n}-title")
        titles[n] = t.split(". ", 1)[1]
    for n, b in handmade.items():
        titles[n] = b.title

    builders = {n: build_generic(old, n) for n in GENERIC}
    builders.update(handmade)

    out = []
    toc_els, toc_h = build_toc(titles, 0)
    out += toc_els
    y = toc_h + CHAPTER_GAP
    for n in range(1, 14):
        if n in MOVED:
            els, h = build_moved(old, n, y)
        else:
            els, h = builders[n].emit(y)
        out += els
        y += h + CHAPTER_GAP
    return out, y


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--old", default="docs/diagrams/_backup-a4-2026-08-12.excalidraw")
    ap.add_argument("--out", default="docs/diagrams/_a4-draft.excalidraw")
    ap.add_argument("--apply", action="store_true",
                    help="wipe the canvas and write the new version (default: only build the file)")
    args = ap.parse_args(argv)

    from canvas_a4_ch4_ch7 import build_ch4, build_ch7
    handmade = {4: build_ch4(), 7: build_ch7()}

    els, total_h = build_all(args.old, handmade)
    json.dump({"type": "excalidraw", "version": 2, "source": "tdq-a4-rebuild",
               "elements": els, "appState": {"viewBackgroundColor": "#ffffff"},
               "files": {}},
              open(args.out, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"Built {len(els)} element(s), total height {total_h:.0f}px → {args.out}")

    if not args.apply:
        print("Nothing written to the canvas yet. Check the file first, then re-run with --apply.")
        return 0

    old_ids = [e["id"] for e in api("/api/elements")["elements"]]
    for eid in old_ids:
        api(f"/api/elements/{eid}", method="DELETE")
    print(f"Deleted {len(old_ids)} old element(s).")
    res = api("/api/elements/batch", method="POST", payload={"elements": els})
    n = res.get("count", 0)
    print(f"Created {n}/{len(els)} element(s).")
    return 0 if n == len(els) else 1


if __name__ == "__main__":
    sys.exit(main())
