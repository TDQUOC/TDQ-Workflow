# BRIEF — lane nhanh: pha analyze + ngưỡng B0/B1/B2

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> 1b 2A

Trả lời hai câu chốt cuối turn trước: 1b = CHƯA commit; 2A = mở request gộp, vừa làm pha
analyze cho lane nhanh (kết quả phân tích 2103) vừa áp ngưỡng B0/B1/B2 (kết quả phân tích 2122).

Đọc lần đầu:

- Mục tiêu: biến hai report phân tích thành thay đổi thật trong workflow.
- Phần 1 — lane nhanh có pha `analyze`: khoá state, bảng pha, `phase_key`, `CONG_THEO_LANE`,
  brief tách file. Thiết kế đã có sẵn ở `docs/tdq/report/2026-09-01-2103-lane-nhanh-co-pha-analyze.md`.
- Phần 2 — ngưỡng ba bước: B1 đọc code luôn luôn (nói rõ là LSP + lumen song song), B0 kiểm kê
  chỉ khi vùng chưa có tiền lệ, B2 research chỉ khi có ẩn số ngoài. Nguồn:
  `docs/tdq/report/2026-09-01-2122-lane-nhanh-kiem-ke-nang-luc.md`.
- Phạm vi đoán: `scripts/tdq_state.py`, `hooks/scripts/prompt_context.py`,
  `skills/tdq-intake/SKILL.md` + `references/quick-lane.md`,
  `skills/tdq-conventions/references/phases.md`, `tests/`, 3 bundle portable, CHANGELOG.
- Chỗ chưa rõ — đây là điểm chặn, phải hỏi trước:
  1. Phương án 2a (pha analyze có tên + brief riêng, KHÔNG thêm cổng duyệt) hay 2c (thêm cổng
     duyệt phân tích)? Câu trước user chỉ chốt "mở request gộp", chưa chốt cái này. Report
     2103 đề xuất 2a.
  2. Ngưỡng B0/B1/B2 viết thành luật chữ trong skill, hay có cả cơ chế chặn/nhắc trong hook?
  3. Ước ~2,5 giờ (2c) hoặc ~1,2 giờ (2a) cộng phần ngưỡng — chạy lane nào.

## Hiểu & kiến thức

(chờ pha analyze)

## Hỏi đáp

(chờ pha analyze)
