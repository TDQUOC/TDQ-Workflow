# QUICK — Tự động mở branch khi chỉ thay đổi docs và log

**Ngày:** 2026-10-11 · Brief: ../brief/2026-10-11-1300-tu-dong-mo-nhanh-doc-log.md · Lane: quick
**Trạng thái:** HOÀN THÀNH
**Ước tính sẽ dùng skill:** không có

## Phạm vi
- Trong:
  1. Cập nhật bước 3b trong `skills/tdq-intake/SKILL.md`: cho phép tự động switch branch nếu `git status --porcelain` chỉ chứa docs/log/file tạm.
  2. Cập nhật `skills/tdq-intake/references/nhanh-request.md`: mô tả ngoại lệ doc/log, cập nhật chú thích lệnh và self-check.
  3. Đảm bảo line count và luật anchored 0% drift, kiểm thử toàn bộ test suite.
- NGOÀI: Tự động switch khi có thay đổi trong source code hoặc file ngoài docs/log.
- Bỏ B0: đã có tiền lệ chỉnh sửa quy tắc nhánh request trong intake.
- Bỏ B2: không dùng lib/API ngoài.

## Task
- [x] **T1** Cập nhật bước 3b trong SKILL.md & nhanh-request.md cho phép tự động mở branch khi chỉ đổi doc/log — Test: `pytest tests/test_skill_shape.py tests/test_luat_skill.py -q` <!-- Chạm: `skills/tdq-intake/SKILL.md`, `skills/tdq-intake/references/nhanh-request.md` -->
- [x] **T2** Cập nhật test và kiểm tra toàn diện không drift, token budget hợp lệ — Test: `pytest tests/test_doc_lint.py tests/test_docs_consistency.py -q` <!-- Chạm: `docs/tdq/token-budget.json` -->

## Definition of Done
- Bước 3b của `tdq-intake` và `nhanh-request.md` nêu rõ quy tắc: nếu mọi file uncommitted đều là docs/log thì tự động mở branch và mang theo, không hỏi; nếu có file khác thì DỪNG và hỏi.
- `skills/tdq-intake/SKILL.md` tuân thủ trần số dòng, không làm trôi dòng anchored luật (drift = 0.00%).
- Toàn bộ test suite pass 100%.

## QC
- [x] DoD 1: Quy tắc "chỉ dirty docs/logs thì tự động mang theo" đã được nêu trong bước 3b (SKILL.md) và nhanh-request.md, report-template.md. (ĐẠT)
- [x] DoD 2: `skills/tdq-intake/SKILL.md` vẫn giữ nguyên trần số dòng, không làm trôi dòng luật (ĐẠT - drift = 0.00%).
- [x] DoD 3: Toàn bộ test suite pass 100% (ĐẠT).
- Mức QC: `lite` — Chỉ kiểm tra DoD, không chạy test từng task. Kết quả: 3/3 DoD ĐẠT.
