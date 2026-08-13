# QC — Rút gọn UX câu hỏi chọn lane

Ngày: 2026-08-13 · Spec: ../spec/2026-08-13-ux-cau-hoi-lane.md · Lane: full
QC độc lập: BỎ (đã chốt trong spec §1b — việc nhỏ, thuần văn bản 2 file). Tự QC bằng đọc
lại + `doc_lint.py`.

## Kết quả

| # | Hạng mục | Bằng chứng | Kết quả |
|---|---|---|---|
| Q1 | `SKILL.md` bước 2 không còn yêu cầu in `Cỡ:/Cần:`, dùng "pipeline" | Đọc lại `skills/tdq-intake/SKILL.md` dòng 39-45: dòng `Cỡ:/Cần:` đã bỏ khỏi phần "Trong chat", chuyển thành đánh giá nội bộ; câu hỏi đổi thành "Bạn muốn chạy pipeline nào?" | PASS |
| Q2 | `lane-decision.md` khuôn câu hỏi khớp format đã chốt | Đọc lại `skills/tdq-intake/references/lane-decision.md` mục "Dòng tự nhận định" (không còn "in đúng một dòng này" — đổi thành "tự đánh giá NỘI BỘ ... không in ra chat") và mục "Khuôn câu hỏi" (không có dòng `Cỡ:/Cần:`, câu hỏi dùng "pipeline", có khối giải thích nghĩa 2 pipeline ngay dưới option A/B, giữ khối hint trả lời) | PASS |
| Q3 | `doc_lint.py` pass trên cả 2 file | `python3 scripts/doc_lint.py skills/tdq-intake/SKILL.md skills/tdq-intake/references/lane-decision.md` → exit 0 | PASS |

## Kết luận
3/3 PASS. DoD đạt — không còn mục QC nào FAIL, không cần thêm task fix.
