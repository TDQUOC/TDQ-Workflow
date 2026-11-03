# Report — Fix dòng giải thích pipeline gây rối khi đọc lại tóm tắt

Ngày: 2026-08-13 · Spec: ../spec/2026-08-13-fix-dong-giai-thich-lane.md · Plan: ../plan/2026-08-13-fix-dong-giai-thich-lane.md

## Đã làm
Ban đầu đoán nhầm lỗi nằm ở khuôn câu hỏi lane thật (`lane-decision.md`) — đọc code sửa
lại: lỗi thật nằm ở cách Claude trình "Tóm tắt spec/plan" trong chat khi đầu ra CHÍNH LÀ
một khuôn/mẫu văn bản — tự ý chép nguyên khối mẫu (gồm cả 2 giải thích express/deep) làm
ví dụ, dù lane của request đó đã chốt xong, gây cảm giác "hỏi lại lane" khi đọc lại.

Sửa: thêm 1 câu quy ước vào mỗi file:
- `skills/tdq-spec/SKILL.md` bước 4: cần trích khuôn/mẫu trong tóm tắt spec → gắn nhãn
  "(khuôn mẫu — áp dụng cho các lần hỏi sau, không phải câu hỏi của turn này)".
- `skills/tdq-plan/SKILL.md` bước 5: quy ước tương tự cho tóm tắt plan.

Không đổi: `lane-decision.md` (khuôn thật không có lỗi), `tdq-conventions/SKILL.md`
(user giới hạn phạm vi đúng spec + plan).

## QC
3/3 PASS (`docs/tdq/qc/2026-08-13-fix-dong-giai-thich-lane.md`):
- Q1: `tdq-spec/SKILL.md` khớp yêu cầu — PASS.
- Q2: `tdq-plan/SKILL.md` khớp yêu cầu — PASS.
- Q3: `doc_lint.py` cả 2 file → exit 0 — PASS.

## Giới hạn còn lại
Chỉ áp cho spec/plan; nếu vấn đề tương tự phát sinh ở report/brief, cần mở request mới
(user đã chốt giới hạn phạm vi này).

Git: chưa commit.
