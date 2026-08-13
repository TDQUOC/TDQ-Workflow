# Report — Rút gọn UX câu hỏi chọn lane

Ngày: 2026-08-13 · Spec: ../spec/2026-08-13-ux-cau-hoi-lane.md · Plan: ../plan/2026-08-13-ux-cau-hoi-lane.md

## Đã làm
Sửa cách trình bày câu hỏi chọn lane trong `tdq-intake`, theo đúng 4 câu chốt của user:
- `skills/tdq-intake/SKILL.md` bước 2: bỏ yêu cầu in dòng `Cỡ:/Cần:` ra chat (giữ làm căn
  cứ nội bộ), đổi câu hỏi user sang "Bạn muốn chạy pipeline nào?".
- `skills/tdq-intake/references/lane-decision.md`: mục "Dòng tự nhận định" chuyển thành
  đánh giá nội bộ; mục "Khuôn câu hỏi" viết lại — bỏ dòng Cỡ/Cần, dùng "pipeline", thêm
  khối giải thích ngắn nghĩa 2 pipeline ngay dưới option A/B, giữ khối hint trả lời có sẵn.
- Không đổi: `references/interview.md` (dùng chung mọi câu hỏi khác), thuật ngữ `lane`
  trong code/state/CLI (`tdq_state.py`, khoá `lane` trong `state.json`).

## QC
3/3 PASS (`docs/tdq/qc/2026-08-13-ux-cau-hoi-lane.md`):
- Q1: `SKILL.md` khớp yêu cầu — PASS.
- Q2: `lane-decision.md` khớp format mới — PASS.
- Q3: `doc_lint.py` cả 2 file → exit 0 — PASS.

## Giới hạn còn lại
Không có — thuần đổi văn bản/UX, không runtime, không rủi ro tương thích (thuật ngữ nội
bộ giữ nguyên).

Git: chưa commit.
