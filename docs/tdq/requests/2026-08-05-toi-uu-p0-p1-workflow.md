# REQUEST — Brainstorm + spec triển khai P0+P1 tối ưu workflow & user-level Claude Code

Ngày: 2026-08-05

## Nguyên văn yêu cầu

> okay vậy hãy brainstoming và lập spec P0+P1 để optimize workflow và user-level claude code

## Bối cảnh

Tiếp nối trực tiếp request `2026-08-05-audit-toi-uu-workflow` (đang ở phase `report`,
chưa commit). Request đó đã tạo bảng ưu tiên 26 đề xuất tại
`docs/tdq/knowledge/2026-08-05-audit-toi-uu-workflow.md` mục 9 — user chọn triển khai
nhóm P0 (6 đề xuất) + P1 (13 đề xuất) = 19 đề xuất, KHÔNG làm P2 round này.

## Cách hiểu đầu tiên

- **Mục tiêu**: biến 19 đề xuất P0+P1 (đang chỉ là ý tưởng nêu trong knowledge) thành
  spec cụ thể, đo đếm được, sẵn sàng lập plan/implement ở turn sau.
- **Phạm vi đoán**: gồm cả 2 lớp —
  - *Workflow* (project-level): script (`tdq_state.py`, `bash_gate.py`,
    `external_task.py`, hook `stop_gate.py`/`reminder-codes.md`...), skill
    (`tdq-build`, `tdq-conventions`, `tdq-intake`...).
  - *User-level Claude Code*: `~/.claude/CLAUDE.md` (nguồn `portable/claude-md/CLAUDE.md`),
    có thể cả cấu hình/hook cấp user khác nếu P0/P1 nào chạm tới.
- **"Brainstorm"**: cần mở rộng suy nghĩ hơn 19 dòng gốc (vốn viết rất ngắn ở round
  trước) — cụ thể hoá cách làm, có thể phát hiện thêm phương án/rủi ro chưa thấy lúc
  audit, trước khi chốt spec.
- **Dừng ở spec** — không plan/implement trong request này (giống round trước, user
  thường tách rõ giai đoạn).
- **Chỗ chưa rõ** (cần hỏi ở phase analyze): lane quick hay full; có làm đủ 19/19 hay
  cắt bớt theo effort/rủi ro; P0-4/P0-5 (sửa mâu thuẫn luật) và P1-3 (`stop_gate.py`)
  có cần review kỹ hơn trước khi đưa vào spec vì đụng luật lõi.
