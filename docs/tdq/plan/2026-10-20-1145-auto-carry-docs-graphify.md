# QUICK — Tự động mang theo & merge docs và graphify khi đổi nhánh

**Ngày:** 2026-10-20 · Brief: ../brief/2026-10-20-1145-auto-carry-docs-graphify.md · Lane: quick
**Trạng thái:** ĐÃ DUYỆT
**Ước tính sẽ dùng skill:** không có

## Phạm vi
- Trong: Mở rộng vùng tự động mang theo / commit / merge cho cả `docs/**`, `*.md`, `logs/**`, `*.log`, `graphify-out/**` khi mở nhánh hoặc merge; cập nhật `tdq-intake`, `nhanh-request.md`, `report-template.md`, `KHOI_HUONG_DAN`.
- NGOÀI: Không tự động commit khi có dirty ở mã nguồn (`scripts/`, `hooks/`, `tests/`...).

## Task
- [x] **T1** Cập nhật quy tắc mở nhánh tự động mang theo docs & graphify trong `skills/tdq-intake/SKILL.md` và `skills/tdq-intake/references/nhanh-request.md` — Test: `doc_lint` PASS.
  - Chạm: `skills/tdq-intake/SKILL.md`, `skills/tdq-intake/references/nhanh-request.md`
- [x] **T2** Cập nhật quy tắc merge tự động mang theo / commit docs & graphify trong `skills/tdq-build/references/report-template.md` — Test: `doc_lint` PASS.
  - Chạm: `skills/tdq-build/references/report-template.md`
- [x] **T3** Bổ sung quy tắc tự động mang theo docs & graphify vào `KHOI_HUONG_DAN` trong `scripts/tdq_setup.py` và đồng bộ `CLAUDE.md` — Test: `test_tu_khoi_tao.py` PASS.
  - Chạm: `scripts/tdq_setup.py`

## QC
- [x] Q1 Mở nhánh intake bước 3b tự động mang theo dirty nếu chỉ thuộc docs hoặc graphify-out.
- [x] Q2 Merge report bước 11 tự động commit / mang theo dirty docs hoặc graphify-out mà không hỏi.
- [x] Q3 `CLAUDE.md` và `KHOI_HUONG_DAN` ghi nhận rõ quy tắc auto-carry zone.
