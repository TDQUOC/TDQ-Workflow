# QUICK — Quyền tự quyết cổng LSP, cài dependency & bảo toàn qua compact

**Ngày:** 2026-10-20 · Brief: ../brief/2026-10-20-1200-tu-quyet-lsp-gate.md · Lane: quick
**Trạng thái:** ĐÃ DUYỆT
**Ước tính sẽ dùng skill:** không có

## Phạm vi
- Trong: Trao quyền tự quyết LSP cho Agent: tự áp dụng `--bo-qua-lsp` cho docs/research; tự setup, sửa kịch bản hoặc bỏ qua an toàn cho develop; tự tìm và cài dependency LSP còn thiếu; tiêm `LSP-Autonomy` vào khối `[TDQ:ANCHOR]` bảo toàn sau compact; ghim vào `CLAUDE.md`, `tdq-intake`, `uu-tien-tim-kiem.md`, `tdq_state.py`.
- NGOÀI: Không hạ bậc kiểm tra tìm kiếm (vẫn ưu tiên gọi LSP khi code).

## Task
- [x] **T1** Cập nhật quy tắc tự quyết LSP trong `skills/tdq-intake/SKILL.md` (bước 1b, 3) và `skills/tdq-intake/references/kiem-lsp-hieu-ung.md` — Test: `doc_lint` PASS.
  - Chạm: `skills/tdq-intake/SKILL.md`, `skills/tdq-intake/references/kiem-lsp-hieu-ung.md`
- [x] **T2** Cập nhật quyền tự động search & install LSP dependency trong `skills/tdq-setup/references/uu-tien-tim-kiem.md` — Test: `doc_lint` PASS.
  - Chạm: `skills/tdq-setup/references/uu-tien-tim-kiem.md`
- [x] **T3** Cập nhật `KHOI_HUONG_DAN` trong `scripts/tdq_setup.py` (tự quyết LSP & cài dependency) và `scripts/tdq_state.py`, đồng bộ `CLAUDE.md` — Test: `test_tu_khoi_tao.py` PASS.
  - Chạm: `scripts/tdq_setup.py`, `scripts/tdq_state.py`
- [x] **T4** Tiêm nguyên tắc `LSP-Autonomy` vào khối `[TDQ:ANCHOR]` trong `hooks/scripts/session_start.py` để bảo toàn quy tắc sau khi compact — Test: unit test anchor block PASS.
  - Chạm: `hooks/scripts/session_start.py`

## QC
- [x] Q1 `tdq-intake` và `kiem-lsp-hieu-ung.md` trao quyền tự quyết `--bo-qua-lsp` cho Agent, không dừng hỏi người dùng.
- [x] Q2 `uu-tien-tim-kiem.md` và `KHOI_HUONG_DAN` ghi nhận quyền tự động search & install dependency LSP còn thiếu.
- [x] Q3 `CLAUDE.md` đồng bộ điều luật tự quyết LSP và tự cài dependency.
- [x] Q4 `[TDQ:ANCHOR]` chứa chỉ dẫn `LSP-Autonomy` bảo toàn sau compact.
