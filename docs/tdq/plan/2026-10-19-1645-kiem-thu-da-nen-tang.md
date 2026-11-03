# QUICK — Kiểm Thử Đa Nền Tảng Trên macOS và Linux Qua Tailscale

**Ngày:** 2026-10-19 · Brief: ../brief/2026-10-19-1645-kiem-thu-da-nen-tang.md · Lane: quick
**Trạng thái:** HOÀN THÀNH (bởi "duyệt nhanh", muc_qc=full)
**Ước tính sẽ dùng skill:** không có

## Phạm vi
- Trong: Kết nối SSH tới `mbair` (macOS) và `superserver` (Linux); đồng bộ code/test và chạy bộ kiểm thử (`test_an_cua_so_windows.py`, `test_auto_fix_python3_hook.py`, `test_shim_python3.py`, `test_claude_md_core.py`); ghi nhận kết quả QC thực tế.
- NGOÀI: Không cài đặt phần mềm hệ thống mới lên remote host, không can thiệp cấu hình người dùng remote.
- Bỏ B0: Đã có tiền lệ chạy test remote và CI đa nền tảng.
- Bỏ B2: Môi trường Tailscale và SSH key đã sẵn sàng và kiểm chứng kết nối thành công.

## Task
- [x] **T1** Kiểm thử thực tế trên Linux (`superserver` - Ubuntu): chạy bộ test `test_an_cua_so_windows.py` và các test suite cốt lõi — Test: `ssh superserver "python3 -m unittest ..."`
  - Chạm: không (chạy test trên host Linux)
- [x] **T2** Kiểm thử thực tế trên macOS (`mbair` - Apple Silicon): chạy bộ test `test_an_cua_so_windows.py` và các test suite cốt lõi — Test: `ssh mbair "python3 -m unittest ..."`
  - Chạm: không (chạy test trên host macOS)
- [x] **T3** Tổng hợp bằng chứng nghiệm thu đa nền tảng Windows + macOS + Linux vào plan `## QC` — Test: xác nhận 100% test xanh trên cả 3 HĐH
  - Chạm: `docs/tdq/plan/2026-10-19-1645-kiem-thu-da-nen-tang.md`

## Definition of Done
- Q1 Kết nối SSH tới cả 2 máy macOS (`mbair`) và Linux (`superserver`) thành công qua Tailscale
- Q2 Bộ test `tests/test_an_cua_so_windows.py` chạy xanh 100% trên Linux (xác nhận POSIX trả về `{}`)
- Q3 Bộ test `tests/test_an_cua_so_windows.py` chạy xanh 100% trên macOS (xác nhận POSIX trả về `{}`)
- Q4 Toàn bộ các test suite liên quan (`test_auto_fix_python3_hook.py`, `test_shim_python3.py`, `test_claude_md_core.py`) chạy xanh 100% trên Linux và macOS
- Q5 `doc_lint` trên plan và brief đạt 0 lỗi (exit 0)

## QC
- Q1 DoD "Kết nối SSH tới cả 2 máy macOS và Linux thành công qua Tailscale": PASS — SSH key auth tới `mbair` (Darwin arm64) và `superserver` (Ubuntu x86_64) thành công 100%.
- Q2 DoD "Bộ test test_an_cua_so_windows.py chạy xanh 100% trên Linux": PASS — `ssh superserver "python3 -m unittest tests/test_an_cua_so_windows.py"` → Ran 9 tests in 0.007s, OK.
- Q3 DoD "Bộ test test_an_cua_so_windows.py chạy xanh 100% trên macOS": PASS — `ssh mbair "python3 -m unittest tests/test_an_cua_so_windows.py"` → Ran 9 tests in 0.003s, OK.
- Q4 DoD "Toàn bộ các test suite liên quan chạy xanh 100% trên Linux và macOS": PASS — Linux: Ran 34 tests in 0.083s, OK; macOS: Ran 34 tests in 0.131s, OK; Windows: Ran 43 tests in 0.294s, OK.
- Q5 DoD "doc_lint trên plan và brief đạt 0 lỗi (exit 0)": PASS — `python scripts/doc_lint.py docs/tdq/brief/2026-10-19-1645-kiem-thu-da-nen-tang.md docs/tdq/plan/2026-10-19-1645-kiem-thu-da-nen-tang.md` → 0 violation(s), exit 0.
