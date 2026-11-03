# QUICK — Ẩn Cửa Sổ Console Command Prompt Trên Windows

**Ngày:** 2026-10-19 · Brief: ../brief/2026-10-19-1630-an-cua-so-popup-cmd-windows.md · Lane: quick
**Trạng thái:** ĐÃ DUYỆT (bởi "duyệt nhanh", muc_qc=full)
**Ước tính sẽ dùng skill:** không có

## Phạm vi
- Trong: Thêm helper `tham_so_subprocess_an_cua_so` vào `tdq_ten_lenh.py`; cập nhật `_run` trong `tdq_finish.py`, `tdq_lsp.py`; bảo vệ subprocess trong `tdq_setup.py`, `setup_status.py`, `stop_batch_checker.py`; viết test.
- NGOÀI: Không sửa đổi mã nguồn nhị phân `graphify.exe`, không đổi logic nghiệp vụ timeout hay stdout/stderr.
- Bỏ B0: Đã có tiền lệ chỉnh sửa subprocess và OS helper trong `tdq_ten_lenh.py`.
- Bỏ B2: Hành vi cờ `CREATE_NO_WINDOW` (`0x08000000`) của Windows API đã chuẩn hóa trong tài liệu Microsoft/Python.

## Task
- [x] **T1** Thêm hàm helper `tham_so_subprocess_an_cua_so(nen_tang=None)` vào `scripts/tdq_ten_lenh.py` trả về cờ `CREATE_NO_WINDOW` trên Windows — Test: `tests/test_an_cua_so_windows.py`
  - Chạm: `scripts/tdq_ten_lenh.py`
- [x] **T2** Cập nhật `_run()` trong `scripts/tdq_finish.py` và `scripts/tdq_lsp.py` tích hợp `tham_so_subprocess_an_cua_so()` để triệt tiêu popup `graphify.exe` và probe — Test: `tests/test_an_cua_so_windows.py`
  - Chạm: `scripts/tdq_finish.py`, `scripts/tdq_lsp.py`
- [x] **T3** Áp dụng cờ ẩn cửa sổ vào các lời gọi `subprocess.run` trong `scripts/tdq_setup.py`, `scripts/setup_status.py`, `hooks/scripts/stop_batch_checker.py` — Test: `tests/test_an_cua_so_windows.py`
  - Chạm: `scripts/tdq_setup.py`, `scripts/setup_status.py`, `hooks/scripts/stop_batch_checker.py`
- [x] **T4** Viết bộ unit test `tests/test_an_cua_so_windows.py` kiểm chứng helper và toàn bộ wrapper subprocess không bật cửa sổ — Test: `python -m unittest tests/test_an_cua_so_windows.py`
  - Chạm: `tests/test_an_cua_so_windows.py`

## Definition of Done
- Q1 `tham_so_subprocess_an_cua_so()` trả về `{"creationflags": 0x08000000}` trên Windows và `{}` trên POSIX
- Q2 `tdq_finish._run` và `tdq_lsp._run` truyền đúng cờ ẩn cửa sổ vào `subprocess.run`
- Q3 Các subprocess trong `tdq_setup.py`, `setup_status.py`, `stop_batch_checker.py` có cờ `CREATE_NO_WINDOW`
- Q4 Toàn bộ unit test trong `tests/test_an_cua_so_windows.py` và test liên quan chạy xanh 100%
- Q5 `doc_lint` trên plan và brief đạt 0 lỗi (exit 0)

## QC
- Q1 DoD "tham_so_subprocess_an_cua_so() trả về creationflags trên Windows và rỗng trên POSIX": PASS — `python -m unittest tests.test_an_cua_so_windows.HelperAnCuaSoTest` → Ran 4 tests, OK
- Q2 DoD "tdq_finish._run và tdq_lsp._run truyền đúng cờ ẩn cửa sổ": PASS — `python -m unittest tests.test_an_cua_so_windows.SubprocessRunWrappersTest.test_tdq_finish_run_co_an_cua_so_tren_windows tests.test_an_cua_so_windows.SubprocessRunWrappersTest.test_tdq_lsp_run_co_an_cua_so_tren_windows` → Ran 2 tests, OK
- Q3 DoD "Các subprocess trong tdq_setup.py, setup_status.py, stop_batch_checker.py có cờ CREATE_NO_WINDOW": PASS — `python -m unittest tests.test_an_cua_so_windows.SubprocessRunWrappersTest` → Ran 5 tests, OK
- Q4 DoD "Toàn bộ unit test trong tests/test_an_cua_so_windows.py và test liên quan chạy xanh 100%": PASS — `python -m unittest tests/test_an_cua_so_windows.py tests/test_auto_fix_python3_hook.py tests/test_shim_python3.py` → Ran 31 tests in 0.308s, OK
- Q5 DoD "doc_lint trên plan và brief đạt 0 lỗi (exit 0)": PASS — `python scripts/doc_lint.py docs/tdq/brief/2026-10-19-1630-an-cua-so-popup-cmd-windows.md docs/tdq/plan/2026-10-19-1630-an-cua-so-popup-cmd-windows.md` → 0 violation(s) total, exit 0
