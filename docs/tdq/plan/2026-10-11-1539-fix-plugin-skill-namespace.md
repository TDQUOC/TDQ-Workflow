# PLAN — Khắc phục lỗi Unknown skill tdq-intake do thiếu namespace plugin

Ngày: 2026-10-11 · Spec: ../spec/2026-10-11-1539-fix-plugin-skill-namespace.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — Các task sửa đổi văn bản hướng dẫn và hook string gắn liền nhau, thực hiện tuần tự an toàn nhất (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Setup & Instructions
- P2 — Hook Prompt Context
- P3 — Verification & Token Budget
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Mỗi bước: `tdq_test.py vung-cham`; trọn bộ chỉ ở QC.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — Setup & Instructions
- [x] **T1.1** (e5m) Cập nhật `KHOI_HUONG_DAN` trong `scripts/tdq_setup.py` và `docs/notes/user-level-install.md` thêm tiền tố namespace `tdq-workflow:tdq-intake` (hoặc `tdq-intake`) — Test: `pytest tests/test_auto_update_setup.py -q`
  - Chạm: `scripts/tdq_setup.py`, `docs/notes/user-level-install.md`
- [x] **T1.2** (e5m) Đồng bộ instruction vào `~/.claude/CLAUDE.md` — Test: `python scripts/tdq_setup.py`

**Xong P1 khi**: `scripts/tdq_setup.py`, `docs/notes/user-level-install.md` và `~/.claude/CLAUDE.md` có đầy đủ tiền tố namespace plugin.

## P2 — Hook Prompt Context
- [x] **T2.1** (e5m) Cập nhật dòng nhắc `[TDQ:INTAKE]` trong `hooks/scripts/prompt_context.py` chỉ định rõ `tdq-workflow:tdq-intake (or tdq-intake)` và kiểm tra độ dài không vượt trần — Test: `pytest tests/test_prompt_context.py -q`
  - Chạm: `hooks/scripts/prompt_context.py`, `tests/test_prompt_context.py`

**Xong P2 khi**: Hook nhắc nhở đúng namespace và toàn bộ test trong `test_prompt_context.py` pass.

## P3 — Verification & Token Budget
- [x] **T3.1** (e5m) Chạy `scripts/token_budget.py` và kiểm tra toàn bộ test suite pass 100% — Test: `pytest tests/test_doc_lint.py tests/test_docs_consistency.py tests/test_luat_skill.py tests/test_skill_shape.py tests/test_prompt_context.py -q`
  - Chạm: `docs/tdq/token-budget.json`

**Xong P3 khi**: Toàn bộ test suite pass, 0% drift, token budget cập nhật hợp lệ.

## Definition of Done
- [x] DoD 1: `KHOI_HUONG_DAN` trong `scripts/tdq_setup.py` và `~/.claude/CLAUDE.md` chứa `tdq-workflow:tdq-intake`.
- [x] DoD 2: Hook `prompt_context.py` nhắc đúng chuỗi `tdq-workflow:tdq-intake (or tdq-intake)` và test `test_prompt_context.py` pass.
- [x] DoD 3: Toàn bộ test suite pass, drift mốc luật giữ 0.00%.
