# REPORT — Trình bày thân thiện ở mọi chỗ giao tiếp với user

Ngày: 2026-08-13 · Lane: full · Mode: main · Plan: ../plan/2026-08-13-trinh-bay-than-thien-duyet.md

## Đã làm

- Thêm khuôn chung `skills/tdq-conventions/references/user-facing-block.md` (5 thành phần,
  cấm emoji, xưng "bạn", luôn có đường dẫn file đầy đủ) và bản portable tương ứng.
- Áp khuôn cho cả 7 chỗ nói với user: hỏi pipeline, interview, duyệt spec, duyệt plan,
  chọn cách chạy, duyệt chế độ nhanh, hỏi commit cuối request.
- Thêm phase `mode` thật vào `tdq_state.py` (`VALID_PHASES`, `PHASE_ORDER`, `PHASE_TABLE`).
  `approve plan` không kèm `--mode` nay dừng ở phase `mode`; kèm `--mode` thì vào thẳng
  `implement`. Hook `_common.py` và `prompt_context.py` có gợi ý riêng cho cổng này.
- Đồng bộ tài liệu kéo theo: `phases.md` (hai bản), `portable/workflow/03-plan.md`,
  `plan-template.md` (hai bản), `docs/claude-md-mau.md` §6 và `~/.claude/CLAUDE.md` §6.

## Kết quả kiểm

8/8 hạng mục DoD PASS, bằng chứng ở `docs/tdq/qc/2026-08-13-trinh-bay-than-thien-duyet.md`.
Full suite: `520 passed, 206 subtests passed`.

## Lưu ý

- Ba test đỏ theo sau thay đổi đã sửa đúng bản chất: `test_state` chuyển khẳng định
  `main`/`subagent` từ hàng `plan` sang hàng `mode`; `claude-md-mau.md` và description của
  `tdq-plan` được nén lại cho vừa trần byte và trần token.
- Working log, spec/brief/report cũ vẫn còn chuỗi "duyệt plan kèm mode" — đó là sổ ghi
  lịch sử, cố ý giữ nguyên.
- Chưa commit gì. Không có commit gỡ chặn nào trong lượt build này.
