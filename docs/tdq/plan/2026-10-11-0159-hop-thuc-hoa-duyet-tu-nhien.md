# QUICK — Hợp thức hóa câu duyệt tự nhiên (làm đi, tiến hành)

**Ngày:** 2026-10-11 · Brief: ../brief/2026-10-11-0159-hop-thuc-hoa-duyet-tu-nhien.md · Lane: quick
**Trạng thái:** HOÀN THÀNH
**Ước tính sẽ dùng skill:** không có

## Phạm vi
- Trong: Nhận diện câu hành động trần ("làm đi", "tiến hành đi"...) cho spec/plan; chặn khi có confirm hoặc cổng có câu hỏi (mode/quick).
- NGOÀI: Đổi cơ chế soft gate sang hard gate trong edit_gate.py.
- Bỏ B0: đã có tiền lệ sửa prompt_context và approval.md (2026-08-04, 2026-09-03).
- Bỏ B2: không dùng lib/API bên ngoài.

## Task
- [x] **T1** Bổ sung regex câu hành động và chặn confirm trong prompt_context.py — Test: `pytest tests/test_prompt_context.py -q` <!-- Chạm: `hooks/scripts/prompt_context.py` -->
- [x] **T2** Cập nhật luật trong approval.md (giữ nguyên neo luật) — Test: `pytest tests/test_luat_skill.py tests/test_doc_lint.py -q` <!-- Chạm: `skills/tdq-conventions/references/approval.md` -->
- [x] **T3** Viết test case cho câu duyệt tự nhiên và case có confirm trong test_prompt_context.py — Test: `pytest tests/test_prompt_context.py -q` <!-- Chạm: `tests/test_prompt_context.py` -->

## Definition of Done
- `looks_like_approval("làm đi", "plan")` và `"spec"` trả về True
- `looks_like_approval("làm đi", "mode")` và `"quick"` trả về False (do đang có câu hỏi mode/QC)
- `looks_like_approval("làm đi nhưng confirm lại X", "plan")` trả về False
- `pytest tests/test_prompt_context.py tests/test_luat_skill.py tests/test_doc_lint.py -q` xanh

## QC
- [x] DoD 1: `looks_like_approval` trả về True cho `spec`, `plan` với câu hành động (ĐẠT)
- [x] DoD 2: `looks_like_approval("làm đi", "mode")` và `"quick"` trả về False (ĐẠT)
- [x] DoD 3: `looks_like_approval("làm đi nhưng confirm lại X", "plan")` trả về False (ĐẠT)
- [x] DoD 4: Toàn bộ test suites test_prompt_context, test_luat_skill, test_doc_lint xanh 100% (ĐẠT)
- Mức QC: `full` — DoD + test của từng task đều PASS. Kết quả: 4/4 DoD ĐẠT.

