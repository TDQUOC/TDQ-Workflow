# QUICK — Cấm plan mode, ép tdq-intake, ghim instruction user

**Ngày:** 2026-10-11 · Brief: ../brief/2026-10-11-0903-cam-plan-mode-ep-intake.md · Lane: quick
**Trạng thái:** HOÀN THÀNH
**Ước tính sẽ dùng skill:** không có

## Phạm vi
- Trong:
  1. Thêm chỉ dẫn cấm tự đổi mode (`EnterPlanMode`) và cấm popup question UI (`AskUserQuestion`) vào `skills/tdq-intake/SKILL.md`, `skills/tdq-conventions/SKILL.md`, `skills/tdq-conventions/references/approval.md`, `user-facing-block.md`.
  2. Bổ sung luật vào `KHOI_HUONG_DAN` của `scripts/tdq_setup.py` để khi chạy setup sẽ tự động ghim vào `~/.claude/CLAUDE.md`.
  3. Cập nhật `docs/notes/user-level-install.md`.
- NGOÀI: Sửa cơ chế runtime khác của CLI.
- Bỏ B0: đã có tiền lệ sửa setup và conventions.
- Bỏ B2: không dùng lib/API ngoài.

## Task
- [x] **T1** Thêm instruction cấm plan mode và cấm popup vào skills/tdq-intake và conventions — Test: `pytest tests/test_luat_skill.py tests/test_skill_shape.py -q` <!-- Chạm: `skills/tdq-intake/SKILL.md`, `skills/tdq-conventions/SKILL.md`, `skills/tdq-conventions/references/approval.md`, `skills/tdq-conventions/references/user-facing-block.md` -->
- [x] **T2** Cập nhật `scripts/tdq_setup.py` (khối ghim instruction user-level) và chạy cập nhật `~/.claude/CLAUDE.md` — Test: `python3 scripts/tdq_setup.py` và kiểm nội dung `~/.claude/CLAUDE.md` <!-- Chạm: `scripts/tdq_setup.py`, `docs/notes/user-level-install.md` -->
- [x] **T3** Cập nhật tests và token budget — Test: `pytest tests/test_luat_gate_chat.py tests/test_doc_lint.py -q` <!-- Chạm: `tests/test_luat_gate_chat.py`, `docs/tdq/token-budget.json` -->

## Definition of Done
- `~/.claude/CLAUDE.md` có ghi rõ: cấm đổi mode, cấm `EnterPlanMode`, cấm popup question, bắt buộc gọi `tdq-intake` khi có request.
- `skills/tdq-intake/SKILL.md` và `skills/tdq-conventions/SKILL.md` có quy định cấm đổi mode và cấm `EnterPlanMode`.
- `tests/test_luat_skill.py` giữ drift = 0%.
- `pytest` toàn bộ test suites chính xanh 100%.

## QC
- [x] DoD 1: `~/.claude/CLAUDE.md` đã được ghim đầy đủ 3 điều rào chắn (ĐẠT)
- [x] DoD 2: `skills/tdq-intake/SKILL.md` và `approval.md` đã có chỉ dẫn cấm EnterPlanMode và ép intake (ĐẠT)
- [x] DoD 3: `test_luat_skill.py` 11 passed, 329 subtests passed, 0.00% drift (ĐẠT)
- [x] DoD 4: Toàn bộ test suites test_luat_skill, test_skill_shape, test_doc_lint, test_luat_gate_chat xanh (ĐẠT)
- Mức QC: `full` — DoD + test của từng task đều PASS. Kết quả: 4/4 DoD ĐẠT.
