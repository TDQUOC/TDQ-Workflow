#!/usr/bin/env python3
"""The two chapters wide by nature, laid out by hand, vertically, for the A4 1240px page.

- Chapter 4: the 8 state-machine nodes stacked VERTICALLY (they used to run 2550px across)
    + the 21-field schema table folded into ONE column.
- Chapter 7: the sequence diagram keeps all 6 lanes, squeezed to ~193px per lane. A message
    label sits ABOVE its arrow and is left-aligned on the start point — NO bound label is used,
    because an orphan bound label gets re-laid-out by the frontend and drifts out of the frame.

The wording stays exactly as in the 2640px version, only the layout changes.
"""

from canvas_a4_rebuild import (BODY_SIZE, CARD_W, GAP, MARGIN, Builder,
                               text_el)
from canvas_draw import W, X

# ── Chapter 4 ─────────────────────────────────────────────────────────────

STATES = [
    ("no_state", "vào khi: chưa mở request", "→ có active_request + lane"),  # i18n-allow
    ("analyze", "vào khi: chế độ chuyên sâu, đã mở request", "→ hết câu hỏi đổi kết quả"),  # i18n-allow
    ("spec", "vào khi: đã phân tích xong", "→ spec_approved = true"),  # i18n-allow
    ("plan", "vào khi: spec_approved = true", "→ plan_approved + có mode"),  # i18n-allow
    ("implement", "vào khi: đã chốt mode thực thi", "→ mọi task tick [x]"),  # i18n-allow
    ("qc", "vào khi: đã implement xong", "→ mọi mục QC PASS, có bằng chứng"),  # i18n-allow
    ("report", "vào khi: QC đã PASS", "→ report ghi xong, đã hỏi commit"),  # i18n-allow
    ("idle", "vào khi: xong hoặc chưa mở request", "→ có request mới"),  # i18n-allow
]

SCHEMA = [
    ("schema_version", "phiên bản schema, hiện là 3"),  # i18n-allow
    ("active_request", "slug request đang mở"),  # i18n-allow
    ("previous_request", "slug request liền trước"),  # i18n-allow
    ("lane", "quick | full"),
    ("phase", "pha hiện tại trong VALID_PHASES"),  # i18n-allow
    ("spec_file", "đường dẫn file spec"),  # i18n-allow
    ("spec_approved", "user đã duyệt spec chưa"),  # i18n-allow
    ("spec_sha256", "vân tay spec lúc duyệt, đổi sau đó sẽ bị cảnh báo"),  # i18n-allow
    ("spec_approved_at", "thời điểm duyệt spec"),  # i18n-allow
    ("spec_approved_by", "NGUYÊN VĂN câu user nhắn để duyệt spec"),  # i18n-allow
    ("plan_file", "đường dẫn file plan"),  # i18n-allow
    ("plan_approved", "user đã duyệt plan chưa"),  # i18n-allow
    ("plan_sha256", "vân tay plan lúc duyệt"),  # i18n-allow
    ("plan_approved_at", "thời điểm duyệt plan"),  # i18n-allow
    ("plan_approved_by", "NGUYÊN VĂN câu user nhắn để duyệt plan"),  # i18n-allow
    ("quick_approved", "duyệt cho chế độ nhanh"),  # i18n-allow
    ("quick_approved_at", "thời điểm duyệt quick"),  # i18n-allow
    ("quick_approved_by", "NGUYÊN VĂN câu duyệt quick"),  # i18n-allow
    ("quick_qc_skipped", "true chỉ khi user nói RÕ bỏ QC"),  # i18n-allow
    ("implement_mode", "main | subagent — do user chốt lúc duyệt plan"),  # i18n-allow
    ("updated_at", "lần ghi state gần nhất"),  # i18n-allow
]

ARROW_DOWN = "#1971c2"


def build_ch4():
    b = Builder(4, "State machine & schema state.json (v3)")

    # the 8 phases stacked vertically, an arrow joining two neighbouring cards
    for i, (name, enter, leave) in enumerate(STATES):
        b.card(name, f"{enter}\n{leave}", i)
        if i < len(STATES) - 1:
            # the arrow takes exactly the GAP between two cards
            top = b.cursor - GAP
            b.body.append({
                "id": b._id("a"), "type": "arrow",
                "x": X + W / 2, "y": top + 2,
                "points": [[0, 0], [0, GAP - 4]],
                "width": 0, "height": GAP - 4,
                "strokeColor": ARROW_DOWN, "strokeWidth": 2, "roughness": 0,
            })

    b.note("Nhánh chế độ nhanh (express): no_state → quick (gộp spec+plan ≤40 dòng, duyệt 1 lần) "  # i18n-allow
           "→ implement → QC (bật mặc định) → idle. VALID_PHASES trong "  # i18n-allow
           "scripts/tdq_state.py dòng 32 gồm 7 phase; no_state là trạng thái suy ra "  # i18n-allow
           "khi state.json chưa có active_request.")  # i18n-allow

    schema_body = "\n".join(f"{k:<18} {v}" for k, v in SCHEMA)
    b.card("Schema docs/tdq/state.json — schema_version 3, 21 field "
           "(chỉ ghi qua scripts/tdq_state.py, cấm sửa tay)",  # i18n-allow
           schema_body, 3)

    b.note("Đọc trạng thái: python3 scripts/tdq_state.py next  ·  "  # i18n-allow
           "Ghi: init / set / approve  ·  Hook TDQ:STATE nhắc ngay khi có ai "  # i18n-allow
           "định sửa thẳng state.json.")  # i18n-allow
    return b


# ── Chapter 7 ─────────────────────────────────────────────────────────────

LANES = ["👤 User", "🤖 Claude\nAgent", "🪣 Hooks", "⚙ tdq_state\n.py",
         "📄 Docs", "🌐 tavily/\ngraphify"]

MESSAGES = [
    (0, 1, "1. Gửi request"),  # i18n-allow
    (1, 2, "2. UserPromptSubmit"),
    (2, 1, "3. bơm context state"),  # i18n-allow
    (1, 5, "4. tavily research (nếu cần)"),  # i18n-allow
    (1, 0, "5. Hỏi lại nếu còn mơ hồ"),  # i18n-allow
    (0, 1, "6. Trả lời"),  # i18n-allow
    (1, 4, "7. Viết spec"),  # i18n-allow
    (1, 0, "8. Trình spec, chờ duyệt"),  # i18n-allow
    (0, 1, '9. "duyệt spec"'),  # i18n-allow
    (1, 3, "10. approve spec"),
    (1, 4, "11. Viết plan + mode"),  # i18n-allow
    (0, 1, "12. duyệt plan + mode"),  # i18n-allow
    (1, 3, "13. approve plan --mode"),
    (1, 2, "14. Edit/Write → edit_gate"),
    (1, 4, "15. QC + Report + log"),
    (1, 5, "16. graphify extract"),
    (1, 2, "17. Stop → stop_gate"),
    (1, 3, "18. set phase=idle"),
    (1, 0, "19. Báo hoàn tất"),  # i18n-allow
]

LANE_W = CARD_W / len(LANES)          # ~193px
HEAD_H = 56
MSG_STEP = 48
LABEL_SIZE = 14


def build_ch7():
    b = Builder(7, "Sequence diagram — trình tự 1 request")  # i18n-allow
    b.note("User ↔ Claude Agent ↔ Hooks ↔ tdq_state.py ↔ Docs ↔ tavily/graphify")

    top = b.cursor
    left = X + MARGIN
    centers = [left + LANE_W * (i + 0.5) for i in range(len(LANES))]

    # lane head
    for i, name in enumerate(LANES):
        x = left + LANE_W * i
        b.body.append({
            "id": b._id("box"), "type": "rectangle",
            "x": x + 3, "y": top, "width": LANE_W - 6, "height": HEAD_H,
            "backgroundColor": "#e7f5ff", "strokeColor": "#1971c2",
            "fillStyle": "solid", "strokeWidth": 2, "roughness": 0,
            "roundness": {"type": 3},
        })
        b.body.append(text_el(b._id("t"), x + 10, top + 10, name,
                              LABEL_SIZE, "#1971c2", LANE_W - 20))

    # body
    body_top = top + HEAD_H + 16
    total = len(MESSAGES) * MSG_STEP + 10

    for i in range(len(LANES)):
        b.body.append({
            "id": b._id("l"), "type": "line",
            "x": centers[i], "y": body_top,
            "points": [[0, 0], [0, total]], "width": 0, "height": total,
            "strokeColor": "#adb5bd", "strokeWidth": 1, "roughness": 0,
            "strokeStyle": "dashed",
        })

    for k, (src, dst, label) in enumerate(MESSAGES):
        y = body_top + 24 + k * MSG_STEP
        x0, x1 = centers[src], centers[dst]
        # the label sits ABOVE the arrow, left-aligned on the left point, clamped inside the frame
        lw = len(label) * LABEL_SIZE * 0.62 + 8
        lx = min(min(x0, x1) + 6, X + W - MARGIN - lw)
        b.body.append(text_el(b._id("t"), lx, y - 20, label,
                              LABEL_SIZE, "#1e1e1e", lw))
        b.body.append({
            "id": b._id("a"), "type": "arrow",
            "x": x0, "y": y, "points": [[0, 0], [x1 - x0, 0]],
            "width": abs(x1 - x0), "height": 0,
            "strokeColor": "#495057", "strokeWidth": 2, "roughness": 0,
        })

    b.cursor = body_top + total + GAP
    b.note("Mỗi mũi tên là một lần agent gọi ra ngoài hoặc hook chạy. "  # i18n-allow
           "Hai điểm người dùng phải nhắn tay: bước 9 (duyệt spec) và "  # i18n-allow
           "bước 12 (duyệt plan kèm mode).", size=BODY_SIZE)  # i18n-allow
    return b
