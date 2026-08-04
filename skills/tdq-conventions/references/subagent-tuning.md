# Chọn model & effort cho sub-agent

Mục tiêu: mỗi lần gọi agent, chọn đúng mức "vừa đủ" — không đốt Opus cho việc bọc
script, không ép Haiku làm việc cần suy luận sâu.

## Hai nút chỉnh, hai phạm vi khác nhau

| Nút | Chỉnh ở đâu | Đổi được lúc chạy? |
|---|---|---|
| `model` | frontmatter agent (mặc định) **và** tham số `model` của Agent tool khi gọi | **Có** — tham số lúc gọi đè frontmatter |
| `effort` | **chỉ** frontmatter agent (`low\|medium\|high\|xhigh\|max`) | **Không** — Agent tool chưa có tham số `effort` |

Vì vậy: `effort` là thuộc tính CỐ ĐỊNH của vai; `model` là nút xoay theo từng task.

## Mặc định theo vai (đã ghi vào frontmatter)

| Agent | model | effort | Vì sao |
|---|---|---|---|
| `tdq-implementer` | inherit | high | viết code thật, red→green, sai là hỏng plan |
| `tdq-qc-tester` | inherit | high | phải nghi ngờ và đào biên, không chỉ chạy lại lệnh |
| `tdq-reviewer` | inherit | high | tìm lỗ hổng/mâu thuẫn trong spec-plan là việc suy luận thuần |
| `search-scout` | sonnet | medium | chạy Tavily đi rộng, tổng hợp nông; không cần frontier |
| `search-runner` | haiku | low | bọc `search_task.py`, không tự kết luận |
| `codex-runner` | haiku | low | bọc `external_task.py`, chỉ gọi lệnh + poll + trả report |
| `agy-runner` | haiku | low | như trên |

`inherit` = bám theo model user đang dùng ở phiên chính. Dùng `inherit` cho agent
làm việc chất lượng, dùng model cụ thể cho agent cơ học để chi phí không phụ thuộc
việc user đang bật model nào.

## Luật override `model` khi gọi (tham số Agent tool)

Xoay theo task, theo thứ tự — dừng ở dòng khớp đầu tiên:

| Nếu task | Truyền `model` |
|---|---|
| Thuần cơ học: chạy 1 lệnh, đọc 1 file, trả nguyên văn | `haiku` |
| Tìm/đọc diện rộng rồi tóm tắt, không quyết định gì | `sonnet` |
| Viết code, sửa logic, thiết kế, review, QC | bỏ trống (giữ mặc định của agent) |
| Task khó nhất của plan, hoặc đã thất bại 1 lần với model thấp hơn | `opus` |

Ghi lý do override vào working log khi lệch khỏi mặc định — 1 dòng là đủ.

## Cảnh báo về `effort`

`effort` trong frontmatter **đè lên** mức effort của phiên (env var vẫn cao hơn cả
hai). Đặt `effort: low` cho một agent làm việc chất lượng nghĩa là agent đó nghĩ nông
NGAY CẢ KHI user đang để phiên ở `high`. Chỉ đặt `low` cho agent thuần cơ học.

Muốn effort thật sự thay đổi theo task thì phải tách agent thành nhiều biến thể —
đã cân nhắc và LOẠI (spec 2026-08-04-workflow-linh-hoat §3): gấp đôi số file, dễ lệch.

## Nguồn

- https://code.claude.com/docs/en/sub-agents — bảng trường frontmatter (`model`,
  `effort`; plugin subagent chỉ bỏ qua `permissionMode`/`mcpServers`/`hooks`). Tra 2026-08-04.
- https://code.claude.com/docs/en/model-config — thứ tự ưu tiên effort: env var >
  frontmatter (khi agent active) > mức của phiên > mặc định model. Tra 2026-08-04.
- https://github.com/anthropics/claude-code/issues/43083 — Agent tool chưa có tham số
  `effort` (feature request mở). Tra 2026-08-04.
