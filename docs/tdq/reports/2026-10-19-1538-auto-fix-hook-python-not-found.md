# REPORT — Tự động xử lý lỗi Python Not Found cho Hook và Auto-Setup trên máy mới (`2026-10-19-1538-auto-fix-hook-python-not-found` · lane full · mode main · 8 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P1: Thêm chuỗi fallback đa nền tảng cho 13 hook command trong `hooks/hooks.json` và cơ chế auto-detect lần đầu chạy plugin trong `session_start.py` · P2: Nâng cấp tìm thư mục Scripts dự phòng & cấu hình User PATH trong `tdq_checkportable.py`, tích hợp auto-check/auto-setup shim `python3` và dry-run hook trong `tdq_setup.py` · P3: Cập nhật `KHOI_HUONG_DAN`, đồng bộ `docs/claude-md-mau.md` và ghim vào `~/.claude/CLAUDE.md` bổ sung nguyên tắc Self-healing · P4: Xây dựng bộ test mới `tests/test_auto_fix_python3_hook.py`, nghiệm thu xanh 100%.
**Kết quả:** 100% hook command có fallback (`python3 ... || py -3 ... || python ...`) · Shim `python3.cmd` và shell script tự động cài đặt chính xác vào thư mục nằm trước Store stub · Hook dry-run kiểm chứng thành công · Máy mới cài plugin tự động kích hoạt `tdq_setup.py --nen` ngay ở session đầu tiên.
**Kiểm:** `python -m unittest tests/test_auto_fix_python3_hook.py` (7/7 tests OK, 0.28s) · Bộ test liên quan trực tiếp và gián tiếp (210+ tests) xanh 100% · `doc_lint` 0 lỗi trên brief/spec/plan/qc/report · Pairing `--pair` khớp hoàn toàn · QC PASS 8/8 mục DoD.
**Đầu ra:** `hooks/hooks.json` · `hooks/scripts/session_start.py` · `scripts/tdq_checkportable.py` · `scripts/tdq_setup.py` · `docs/claude-md-mau.md` · `tests/test_auto_fix_python3_hook.py` · `docs/tdq/qc/2026-10-19-1538-auto-fix-hook-python-not-found.md`.
**Giới hạn:** Không có. Cơ chế tương thích trên cả POSIX shell và Windows cmd.exe.
**Lệch spec chờ duyệt:** không có
**Git:** Chưa commit (nhánh hiện tại: `feature/auto-fix-hook-python-not-found`, nhánh gốc: `main`).

## Thời gian

Request `2026-10-19-1538-auto-fix-hook-python-not-found` · lane full · opened at 2026-10-19T15:46:49+07:00

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 15s | — | 1 |
| analyze | 6 min | — | 1 |
| spec | 4 min | — | 1 |
| plan | 1 min | — | 1 |
| implement | 22 min | — | 1 |
| qc | 1 min | — | 1 |
| report | 48s | — | 1 |
| **Total** | **36 min** | **—** | |
