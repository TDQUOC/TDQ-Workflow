# QUICK — Xử lý dứt điểm cửa sổ command console chớp nháy trên Windows

**Ngày:** 2026-10-20 · Brief: ../brief/2026-10-20-1230-fix-chop-nhay-console-windows.md · Lane: quick
**Trạng thái:** ĐÃ DUYỆT
**Ước tính sẽ dùng skill:** không có

## Phạm vi
- Trong: Thêm cờ `CREATE_NO_WINDOW = 0x08000000` cho 100% các điểm gọi `subprocess.run` và `subprocess.Popen` trên Windows trong `session_start.py`, `tdq_state.py`, `tdq_team.py`, `tdq_test.py`, `codex_edit_gate.py`, `tdq_devtool_mcp.py`.
- NGOÀI: Không thay đổi logic nghiệp vụ của các script, chỉ bổ sung cờ ẩn cửa sổ trên Windows.

## Task
- [x] **T1** Thêm cờ `CREATE_NO_WINDOW` cho tiến trình nền trong `hooks/scripts/session_start.py` và hook `hooks/scripts/codex_edit_gate.py` — Test: test hook dryrun và kiểm tra creationflags PASS.
  - Chạm: `hooks/scripts/session_start.py`, `hooks/scripts/codex_edit_gate.py`
- [x] **T2** Cập nhật `_git()` và subprocess trong `scripts/tdq_state.py`, `scripts/tdq_team.py`, `scripts/tdq_test.py`, `scripts/tdq_devtool_mcp.py` dùng cờ ẩn cửa sổ — Test: unit test git calls PASS.
  - Chạm: `scripts/tdq_state.py`, `scripts/tdq_team.py`, `scripts/tdq_test.py`, `scripts/tdq_devtool_mcp.py`
- [x] **T3** Viết bộ test `tests/test_no_window_flags.py` kiểm chứng tĩnh và động các hàm gọi subprocess trên Windows đều mang cờ ẩn cửa sổ — Test: `py -3 tests/test_no_window_flags.py` PASS 100%.
  - Chạm: `tests/test_no_window_flags.py`

## QC
- [x] Q1 `session_start.py` và `codex_edit_gate.py` chạy trên Windows không cấp phát console window (có cờ 0x08000000).
- [x] Q2 Các lệnh git và subprocess trong `tdq_state.py`, `tdq_team.py`, `tdq_test.py` đều gắn cờ ẩn cửa sổ.
- [x] Q3 `tests/test_no_window_flags.py` và toàn bộ test suite liên quan PASS 100%.
