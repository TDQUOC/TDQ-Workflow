# Interview — 2026-08-04-workflow-linh-hoat

## Vòng 1 (2026-08-04 20:36 → 20:39)

| # | Câu hỏi | Phương án | User chốt (nguyên văn) |
|---|---|---|---|
| Q1 | `tdq-reviewer` bỏ tới đâu? | (1) bỏ gọi mặc định, giữ agent gọi tay; (2) xoá hẳn | **1** — "Q1:1" |
| Q2 | Model/thinking cho sub-agent chọn kiểu gì? | (1) heuristic Claude tự quyết; (2) bảng mapping cố định; (3) mapping + cho lệch có lý do | **1** — "Q2:1" |
| Q3 | Gộp gate tới mức nào? | (1) giữ 2 lần duyệt (spec, rồi plan+mode) nhưng KHÔNG tách turn; (2) gộp còn 1 lần duyệt | **1** — "Q3:1" |
| Q4 | Cấu trúc lane? | (1) giữ quick/full, cho co giãn bên trong; (2) bỏ lane, 1 luồng tự chọn độ nặng | **1** — "Q4:1" |
| Q5 | Được sửa hook approval-gate + `tdq_state.py` không? | có / không | **có** — "Q5L có" |
| Q6 | Sửa yêu cầu #4 (bỏ AskUserQuestion) | — | User đổi ý: **GIỮ interface AskUserQuestion**, nhưng mỗi vòng hỏi phải có **câu cuối "bạn muốn bổ sung thêm gì không"** để trả lời mở |
| Q7 | Lane | quick / full | **full** — "chôt lane full" |

## Vòng 2 (2026-08-04 20:5x)

Căn cứ: `docs/tdq/research/2026-08-04-workflow-linh-hoat.md` mục B.

| # | Câu hỏi | Phương án | User chốt |
|---|---|---|---|
| Q8 | `effort` (thinking) chỉ chỉnh được TĨNH trong frontmatter agent — Agent tool không có tham số `effort`. Làm sao? | (a) chỉ đặt `model`+`effort` mặc định vào frontmatter 7 agent, động thì chỉ đổi `model` lúc gọi; (b) thêm biến thể agent nhẹ/nặng để chọn effort động; (c) chỉ đặt `model`, không đụng `effort` | *(chờ)* |
| Q9 | Bước "quyết lộ trình" (routing) sau interview ghi ở đâu, có gate không? | (a) mục "Lộ trình" trong `knowledge/<slug>.md`, user duyệt chung lúc duyệt spec; (b) thêm trường `route` vào state để hook nhắc đúng bước; (c) chỉ trình bày trong chat, không ghi file | *(chờ)* |
| Q10 | Lane quick sau khi thêm research + interview bắt buộc | (a) quick = 1 file mini-spec+plan gộp, 1 lần duyệt, vẫn có research/interview khi cần; (b) quick tạo đủ `research/` + `questions/` như full, chỉ khác là mini-plan ≤10 dòng; (c) giữ nguyên quick, chỉ thêm "phải web search" | *(chờ)* |
| Q11 | Bổ sung gì thêm không? | — | *(chờ)* |

Giả định đang dùng (nói nếu sai): sẽ sửa cả `~/.claude/CLAUDE.md` mục 9 (bỏ luật
"Spec và plan không lập trong cùng một turn", thêm luật gộp gate + câu hỏi mở),
đồng bộ `portable/workflow/*` và `portable/AGENTS.md` theo skill.
