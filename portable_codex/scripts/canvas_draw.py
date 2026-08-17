#!/usr/bin/env python3
"""Bộ dựng hình dùng chung cho các chương mới của product document.

Gói lại đúng những quy ước đã chốt trong plan để không phải lặp ở mỗi chương:

- khung chương rộng 1240px (khổ A4 dọc @150dpi) tại `x = 40`, id `ch<N>-frame`, tiêu đề `ch<N>-title`
  bắt đầu bằng `"<N>. "` (script `check_canvas_layout.py` dựa vào đúng quy ước này),
- thẻ nội dung = rectangle nền pastel + text tiêu đề + text thân, KHÔNG dùng bound
  label trên hộp lớn (label sẽ bị canh giữa và đè lên nội dung),
- bề rộng chữ tiếng Việt: `số ký tự dòng dài nhất × fontSize × 0.75`; hàm `fit`
  cảnh báo khi một dòng vượt 70% bề rộng ô.

Chỉ stdlib. Ghi bằng `POST /api/elements/batch` (cấm `update_element` — luật 7).
"""

import sys

from canvas_move_block import api

X = 40
W = 1240          # khổ A4 dọc @150dpi — chốt ở spec 2026-08-12-layout-a4-doc
K_VI = 0.75          # hệ số bề rộng cho chữ có dấu
SAFE = 0.70          # chữ chỉ được chiếm tối đa 70% bề rộng ô

PALETTE = [
    ("#e7f5ff", "#1971c2"),   # xanh dương
    ("#ebfbee", "#2f9e44"),   # xanh lá
    ("#fff9db", "#e8590c"),   # vàng cam
    ("#f3f0ff", "#6741d9"),   # tím
    ("#ffe3e3", "#c92a2a"),   # đỏ
    ("#e6fcf5", "#0ca678"),   # ngọc
]


def fit(text, box_w, font_size, where):
    """Cảnh báo nếu có dòng vượt quá 70% bề rộng ô. Trả về chính `text`."""
    limit = box_w * SAFE
    for line in text.split("\n"):
        need = len(line) * font_size * K_VI
        if need > limit:
            print(
                f"  ⚠ {where}: dòng {len(line)} ký tự cần ~{need:.0f}px, "
                f"quá 70% của {box_w}px — rút ngắn hoặc xuống dòng",
                file=sys.stderr,
            )
    return text


class Chapter:
    """Gom element của một chương rồi ghi một lượt."""

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
        """Trả danh sách (x, w) cho `count` thẻ dàn đều hết bề ngang chương."""
        w = (W - 2 * margin - gap * (count - 1)) / count
        return [(X + margin + i * (w + gap), w) for i in range(count)]

    def stack(self, top, heights, gap=24):
        """Bố cục MỘT cột: trả danh sách y cho các khối cao `heights` xếp dọc."""
        ys, y = [], top
        for h in heights:
            ys.append(y)
            y += h + gap
        return ys

    def commit(self):
        res = api("/api/elements/batch", method="POST", payload={"elements": self.els})
        n = res.get("count", 0)
        print(f"Chương {self.n}: tạo {n}/{len(self.els)} phần tử tại y={self.y}")
        return 0 if n == len(self.els) else 1
