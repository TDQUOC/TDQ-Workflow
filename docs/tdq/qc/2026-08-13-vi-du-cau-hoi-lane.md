# QC — Ví dụ & hướng dẫn thân thiện cho câu hỏi kiểu A/B/C

Plan: ../plan/2026-08-13-vi-du-cau-hoi-lane.md · Spec: ../spec/2026-08-13-vi-du-cau-hoi-lane.md

| # | Hạng mục kiểm | Lệnh/cách kiểm | Kết quả |
|---|---|---|---|
| Q1 | Khối hint `interview.md` đúng khuôn mới | Đọc file | PASS — khối cuối file có 1 dòng nguyên tắc + 1 ví dụ trung tính (`"A"` / "chọn phương án A"), 3 dòng, không gắn cứng lane/mode |
| Q2 | 3 dòng `➤ Duyệt:` đã rà, có kết luận | Đọc `docs/tdq/plan/2026-08-13-vi-du-cau-hoi-lane.md` mục P2 | PASS — T2.1/T2.2/T2.3 đều ghi "**KẾT LUẬN: SỬA**" + lý do, đủ 3 file (tdq-spec, tdq-plan, tdq-intake) |
| Q3 | doc_lint sạch cho các file đã sửa | `python3 scripts/doc_lint.py skills/tdq-intake/references/interview.md skills/tdq-spec/SKILL.md skills/tdq-plan/SKILL.md skills/tdq-intake/SKILL.md` | PASS — exit 0 |
| Q4 | Không phá cấu trúc khuôn A/B/C hiện có | Đọc lại `interview.md` toàn bộ | PASS — các khối khuôn hỏi A/B/C (mục "Hỏi thế nào", "Luật khuôn", câu chốt vòng) không đổi, chỉ đổi đúng khối "Dòng hướng dẫn trả lời" cuối |

## Ghi chú ngoài phạm vi (không phải FAIL)
- `skills/tdq-status/SKILL.md:32` cũng có 1 dòng `➤ Duyệt:` tương tự nhưng KHÔNG thuộc
  phạm vi spec §1 (chỉ liệt kê tdq-spec/tdq-plan/tdq-intake) — cố tình không sửa.

DoD: Q1–Q4 đều PASS.
