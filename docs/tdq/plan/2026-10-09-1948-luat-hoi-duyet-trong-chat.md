# QUICK — Ghi luật hỏi/duyệt trong chat vào từng phase

**Ngày:** 2026-10-09 · Brief: ../brief/2026-10-09-1948-luat-hoi-duyet-trong-chat.md · Lane: quick
**Trạng thái:** CHỜ DUYỆT
**Ước tính sẽ dùng skill:** không có

## Phạm vi
- Trong: 1 dòng luật vào 5 điểm hỏi/duyệt (intake lane-decision, spec, plan, mode-gate, commit).
- NGOÀI: đổi hành vi `ask_gate.py` (giữ remind — user đã chốt 2026-10-03); bản portable/export.
- Vòng scope: BỎ — yêu cầu trỏ vào hành vi cụ thể trong file cụ thể, không dấu hiệu mở scope.
- Bỏ B0: đã có report chạm cùng thư mục skill (2026-09-01-2122, 2026-09-03-1220).
- Bỏ B2: không yếu tố ngoài repo (không lib/API/version lạ).

## Task
- [x] **T1** Thêm 1 dòng luật vào các điểm hỏi/duyệt — Test: grep đếm trúng các file sửa <!-- Chạm: `skills/tdq-conventions/SKILL.md`, `skills/tdq-conventions/references/approval.md`, `skills/tdq-conventions/references/user-facing-block.md`, `skills/tdq-intake/references/interview.md`, `skills/tdq-spec/SKILL.md`, `skills/tdq-plan/SKILL.md` -->
- [x] **T2** Kiểm chống trôi (luật skill + doc_dup + shape + doc_lint) — Test: `pytest tests/test_luat_skill.py tests/test_doc_dup.py tests/test_skill_shape.py tests/test_ask_gate.py tests/test_doc_lint.py -q` xanh

## Definition of Done
- `grep -rln "user-facing-block" skills/tdq-spec skills/tdq-plan skills/tdq-build skills/tdq-intake` trúng ≥ 5 file
- Không file nào nhắc `AskUserQuestion` như lựa chọn (`grep -rn "AskUserQuestion" skills/*/SKILL.md` rỗng)
- `pytest tests/test_luat_skill.py tests/test_doc_dup.py -q` xanh, không vi phạm `doc_dup.py`

## QC
- [x] DoD 1: `grep -rln "user-facing-block" skills/tdq-spec skills/tdq-plan skills/tdq-build skills/tdq-intake` → 5 file trúng (ĐẠT)
- [x] DoD 2: `grep -rn "AskUserQuestion" skills/*/SKILL.md` → 0 dòng (ĐẠT)
- [x] DoD 3: `pytest tests/test_luat_skill.py tests/test_doc_dup.py tests/test_skill_shape.py tests/test_ask_gate.py tests/test_doc_lint.py -q` → 119 passed, 331 subtests passed (ĐẠT)
- Mức QC: `lite` — chỉ kiểm các dòng DoD, không chạy runtime test. Kết quả: 3/3 DoD ĐẠT.
