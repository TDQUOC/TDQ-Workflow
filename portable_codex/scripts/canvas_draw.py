#!/usr/bin/env python3
"""Shared drawing toolkit for the new chapters of the product document.

It packages exactly the conventions settled in the plan so no chapter has to repeat them:

- a chapter frame 1240px wide (A4 portrait @150dpi) at `x = 40`, id `ch<N>-frame`, title `ch<N>-title`
    starting with `"<N>. "` (the script `check_canvas_layout.py` relies on exactly this convention),
- a content card = pastel rectangle + title text + body text, NEVER a bound label on the big
    box (a label gets centred and covers the content),
- text width for accented scripts: `characters of the longest line × fontSize × 0.75`; the `fit`
    helper warns when a line exceeds 70% of the cell width.

Stdlib only. Writes through `POST /api/elements/batch` (`update_element` is banned — rule 7).
"""

import sys

from canvas_move_block import api

X = 40
W = 1240          # A4 portrait @150dpi — settled in spec 2026-08-12-layout-a4-doc
K_VI = 0.75          # width factor for accented text
SAFE = 0.70          # text may take at most 70% of the cell width

PALETTE = [
    ("#e7f5ff", "#1971c2"),   # blue
    ("#ebfbee", "#2f9e44"),   # green
    ("#fff9db", "#e8590c"),   # amber
    ("#f3f0ff", "#6741d9"),   # purple
    ("#ffe3e3", "#c92a2a"),   # red
    ("#e6fcf5", "#0ca678"),   # teal
]


def fit(text, box_w, font_size, where):
    """Warn if any line exceeds 70% of the cell width. Returns `text` itself."""
    limit = box_w * SAFE
    for line in text.split("\n"):
        need = len(line) * font_size * K_VI
        if need > limit:
            print(
                f"  ⚠ {where}: a line of {len(line)} characters needs ~{need:.0f}px, "
                f"over 70% of {box_w}px — shorten it or wrap it",
                file=sys.stderr,
            )
    return text


class Chapter:
    """Collect the elements of one chapter and write them in a single pass."""

    def __init__(self, number, title, y, height, title_color="#1971c2"):
        self.n = number
        self.y = y
        self.height = height
        self.els = [
            {
                "id": f"ch{number}-frame", "type": "rectangle", "x": X, "y": y,
                "width": W, "height": height, "strokeColor": "#1e1e1e",
                "backgroundColor": "transparent", "fillStyle": "solid",
                "strokeWidth": 2, "roughness": 0,
            },
            {
                "id": f"ch{number}-title", "type": "text", "x": X + 40, "y": y + 24,
                "width": 1100, "height": 38, "text": f"{number}. {title}",
                "fontSize": 30, "strokeColor": title_color,
            },
        ]
        self._i = 0

    def _id(self, kind):
        self._i += 1
        return f"ch{self.n}-{kind}{self._i:03d}"

    def text(self, x, y, text, size=16, color="#1e1e1e", width=None):
        width = width or (len(max(text.split("\n"), key=len)) * size * K_VI + 10)
        h = (text.count("\n") + 1) * size * 1.35
        self.els.append({
            "id": self._id("t"), "type": "text", "x": x, "y": y,
            "width": width, "height": h, "text": text,
            "fontSize": size, "strokeColor": color,
        })
        return self

    def card(self, x, y, w, h, head, body, color=0, head_size=20, body_size=16):
        bg, stroke = PALETTE[color % len(PALETTE)]
        fit(head, w - 40, head_size, f"ch{self.n} head {head[:20]!r}")
        fit(body, w - 40, body_size, f"ch{self.n} body {head[:20]!r}")
        self.els.append({
            "id": self._id("box"), "type": "rectangle", "x": x, "y": y,
            "width": w, "height": h, "backgroundColor": bg, "strokeColor": stroke,
            "fillStyle": "solid", "strokeWidth": 2, "roughness": 0,
            "roundness": {"type": 3},
        })
        self.text(x + 20, y + 16, head, head_size, stroke, w - 40)
        self.text(x + 20, y + 16 + head_size * 1.9, body, body_size, "#1e1e1e", w - 40)
        return self

    def arrow(self, x, y, points, color="#495057"):
        self.els.append({
            "id": self._id("a"), "type": "arrow", "x": x, "y": y,
            "points": points, "strokeColor": color, "strokeWidth": 2,
            "roughness": 0, "width": max(p[0] for p in points),
            "height": max(p[1] for p in points),
        })
        return self

    def row(self, count, top, height, gap=24, margin=40):
        """Return the list of (x, w) for `count` cards spread across the chapter width."""
        w = (W - 2 * margin - gap * (count - 1)) / count
        return [(X + margin + i * (w + gap), w) for i in range(count)]

    def stack(self, top, heights, gap=24):
        """ONE-column layout: return the y list for blocks of height `heights` stacked vertically."""
        ys, y = [], top
        for h in heights:
            ys.append(y)
            y += h + gap
        return ys

    def commit(self):
        res = api("/api/elements/batch", method="POST", payload={"elements": self.els})
        n = res.get("count", 0)
        print(f"Chapter {self.n}: created {n}/{len(self.els)} element(s) at y={self.y}")
        return 0 if n == len(self.els) else 1
