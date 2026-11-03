# QUESTIONS — Interview request instruction-hardening-7b

Ngày: 2026-07-28 · 2 vòng, 7 câu · Trạng thái: **hết câu hỏi làm đổi kết quả**

## Vòng 0 — intake

| # | Câu hỏi | User chọn |
|---|---|---|
| 0.1 | Lane? | **full** |
| 0.2 | Cho sửa `~/.claude/CLAUDE.md` §10 (còn luật gate cứng)? | **Có** — tôi trình nội dung mới trước khi ghi đè |
| 0.3 | Gộp các mục rà soát T2–T4, C1–C5, D1–D2 vào request này? | **Gộp hết** |

## Vòng 1

| # | Câu hỏi | User chọn |
|---|---|---|
| 1.1 | "7B cũng đi được" là ẩn dụ hay chạy model nhỏ thật? | **Thật: chạy model nhỏ** |
| 1.2 | Cơ chế buộc tuân theo hook? | **Echo + Stop kiểm** — hook nhắc kèm mã ngắn, agent phải in dòng xác nhận đã thực thi, Stop hook soát transcript và nhắc lại nếu thiếu |
| 1.3 | Kiến trúc skill? | **"thực hiện 3 + 1"** = gộp bớt số skill **và** mỗi skill thân gọn + `references/` |
| 1.4 | Thêm lệnh deterministic? | **Có: `tdq_state.py next`** |

## Vòng 2

| # | Câu hỏi | User chọn |
|---|---|---|
| 2.1 | Model nhỏ chạy ở đâu? | **Cả hai** — giữ plugin Claude Code + sinh bản portable cho agent khác; logic chung dồn vào `tdq_state.py` |
| 2.2 | Nghiệm thu "model yếu đi đúng" thế nào? | **Lint tự viết** — script chấm chất lượng doc, chạy trong test suite; không tải model 7B |
| 2.3 | Gộp skill ra sao? | **9 → 5**: intake(start+analyze) · spec · plan · build(implement+qc+report) · status; conventions giữ riêng làm nền |
| 2.4 | `next` in ra gì? | **Tiếng Việt + checklist** copy được vào câu trả lời để tick |

## Giả định tôi tự chốt (nói rõ để bạn bác nếu sai)

- **A1.** Bản portable nằm trong plugin tại `portable/AGENTS.md` + `portable/workflow/*.md`; dùng bằng cách copy vào project đích. Không tự động cài.
- **A2.** Version tiếp theo là **0.3.0** (đổi tên skill = breaking đối với thói quen gõ slash command).
- **A3.** Tên skill mới: `tdq-intake`, `tdq-spec`, `tdq-plan`, `tdq-build`, `tdq-status`, `tdq-conventions`. `tdq-start`/`tdq-analyze`/`tdq-implement`/`tdq-qc`/`tdq-report`/`tdq-approve` biến mất; `~/.claude/CLAUDE.md` và README cập nhật theo.
- **A4.** Lint chất lượng doc chạy như một test trong `tests/` (không cần CI riêng).
