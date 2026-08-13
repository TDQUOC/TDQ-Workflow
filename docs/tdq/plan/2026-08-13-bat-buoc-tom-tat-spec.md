# PLAN (quick) — Bắt buộc in tóm tắt spec/plan trước dòng Duyệt

Ngày: 2026-08-13 · Brief: ../brief/2026-08-13-bat-buoc-tom-tat-spec.md · Lane: quick
Trạng thái: HOÀN THÀNH

## Phạm vi
- Trong: thêm 1 câu tự-kiểm ngay TRƯỚC dòng `➤ Duyệt:` ở bước "Trình bày & DỪNG" của
  `skills/tdq-spec/SKILL.md` (bước 4) và `skills/tdq-plan/SKILL.md` (bước 5) — buộc tự
  soát đã in đủ tóm tắt (không chỉ câu thông báo suông) trước khi kết thúc turn.
- Ngoài: đổi cơ chế hook (`stop_gate.py`…), đổi khuôn/độ dài tóm tắt hiện có, đụng
  `tdq-intake` (chế độ nhanh không có bước tóm tắt tương tự theo mẫu này).

## Task
- [x] **T1** Thêm câu tự-kiểm vào `skills/tdq-spec/SKILL.md` bước 4, ngay trước dòng
  `➤ Duyệt:` — Test: đọc lại, câu tự-kiểm nêu rõ "phải thấy tóm tắt thật (mục tiêu/đầu
  ra/DoD/rủi ro), không phải câu thông báo suông"; `doc_lint.py skills/tdq-spec/SKILL.md` exit 0
- [x] **T2** Thêm câu tự-kiểm tương tự vào `skills/tdq-plan/SKILL.md` bước 5, ngay
  trước dòng `➤ Duyệt:` — Test: đọc lại, đúng tinh thần T1 (điều chỉnh nội dung tóm
  tắt theo plan: số phase/task, mode, DoD); `doc_lint.py skills/tdq-plan/SKILL.md` exit 0
- [x] **T3** doc_lint gộp 2 file — Test:
  `python3 scripts/doc_lint.py skills/tdq-spec/SKILL.md skills/tdq-plan/SKILL.md`

## DoD
| # | Kiểm | PASS khi | Kết quả |
|---|---|---|---|
| Q1 | Đọc `tdq-spec/SKILL.md` bước 4 | Có câu tự-kiểm trước dòng Duyệt, đúng tinh thần user chốt (2A) | PASS — dòng 33: "Tự kiểm trước khi in dòng Duyệt: tin nhắn phải CHỨA tóm tắt thật — không được thay bằng câu thông báo suông..." |
| Q2 | Đọc `tdq-plan/SKILL.md` bước 5 | Có câu tự-kiểm trước dòng Duyệt, đúng tinh thần user chốt (2A) | PASS — dòng 62: cùng câu tự-kiểm, áp cho tóm tắt plan |
| Q3 | `doc_lint.py` cả 2 file | Exit 0 | PASS — `python3 scripts/doc_lint.py skills/tdq-spec/SKILL.md skills/tdq-plan/SKILL.md` → exit 0 |

## QC
BẬT (mặc định) — 3/3 mục DoD PASS, xem cột "Kết quả" trên. Không có unit test code
(việc thuần văn bản 2 file skill).

Năng lực: không có (thuần sửa văn bản 2 file skill).
