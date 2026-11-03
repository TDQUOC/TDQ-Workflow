# QUICK — Siết chặt cổng duyệt buộc dùng lệnh hoặc cấu trúc đầy đủ

**Ngày:** 2026-10-11 · Brief: ../brief/2026-10-11-1327-siet-chat-cong-duyet-lenh.md · Lane: quick
**Trạng thái:** HOÀN THÀNH
**Ước tính sẽ dùng skill:** không có

## Phạm vi
- Trong:
  1. `hooks/scripts/prompt_context.py`: Xoá `ACTION_APPROVAL` và logic cho phép dùng động từ trần làm lệnh duyệt.
  2. `skills/tdq-conventions/references/approval.md`: Cập nhật luật quay lại yêu cầu 2 thành phần (động từ + tân ngữ) hoặc phím tắt `a`.
  3. `tests/test_prompt_context.py`: Xoá class test `TestActionApprovalSentences` hoặc điều chỉnh nó để verify việc từ chối các câu động từ trần.
  4. Đảm bảo line count và drift luật 0.00%.
- NGOÀI: Các từ khoá trong regex `AGREE` và `OBJECT` vẫn giữ nguyên (nghĩa là "tiến hành plan", "làm đi cái này" vẫn hợp lệ vì đủ 2 thành phần).
- Bỏ B0: đã có tiền lệ sửa regex duyệt trong `prompt_context.py`.
- Bỏ B2: không dùng lib ngoài.

## Task
- [x] **T1** Xoá `ACTION_APPROVAL` trong codebase — Test: `pytest tests/test_prompt_context.py -q` <!-- Chạm: `hooks/scripts/prompt_context.py`, `tests/test_prompt_context.py` -->
- [x] **T2** Xoá/cập nhật mục "Natural action phrases" ở `approval.md` — Test: `pytest tests/test_luat_skill.py -q` <!-- Chạm: `skills/tdq-conventions/references/approval.md` -->
- [x] **T3** Kiểm tra token budget và không làm trôi luật — Test: `pytest tests/test_doc_lint.py tests/test_docs_consistency.py -q` <!-- Chạm: `docs/tdq/token-budget.json` -->

## Definition of Done
- Mã Python `looks_like_approval` không còn chấp nhận các động từ độc lập như "làm đi", "tiến hành đi" nếu không kèm `cái này/đó` hoặc `spec/plan/quick`.
- Tờ trình `approval.md` đã được dọn sạch phần "Natural action phrases".
- Test suite pass 100%, drift = 0.00%.

## QC
- [x] DoD 1: `looks_like_approval` từ chối các câu động từ độc lập không kèm đối tượng/đại từ (ĐẠT).
- [x] DoD 2: `skills/tdq-conventions/references/approval.md` đã gỡ bỏ mục "Natural action phrases as approval" (ĐẠT).
- [x] DoD 3: Test suite pass 100%, luật giữ 0.00% drift (ĐẠT).
- Mức QC: `full` — DoD + test của từng task đều PASS. Kết quả: 3/3 DoD ĐẠT.
