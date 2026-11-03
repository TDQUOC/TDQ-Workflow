# BRIEF — Ngăn chặn cửa sổ Console Command Prompt bật lên trên Windows khi chạy công cụ và hook

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

"okay bây giờ mở request check issue này giúp tôi, khi chạy graphify hay những cái khác thuognwf xuyên có cửa sổ command chạy lên là tại sao hãy check giúp tôi và báo cho tôi" (kèm hình ảnh cửa sổ popup `C:\Users\quanghau\AppData\Roaming\Python\Python314\Scripts\graphify.exe`).

### Đọc hiểu lần đầu
- **Mục tiêu**: Điều tra nguyên nhân gốc rễ và xử lý triệt để hiện tượng cửa sổ Command Prompt (`cmd.exe` / `graphify.exe` console window) tự động bật lên màn hình (popup/flashing console window) khi Claude Code hoặc TDQ Workflow thực thi lệnh/công cụ nền như `graphify`, git, hoặc các hook subprocess trên Windows.
- **Phạm vi dự kiến**:
  - Cơ chế spawn tiến trình con (subprocess) trên Windows: Khi Python gọi `subprocess.Popen` / `subprocess.run` thực thi các file thực thi dòng lệnh (`.exe`, `.cmd`, `.bat`) từ môi trường không gắn console tương tác (hoặc môi trường GUI của IDE), nếu không cấu hình cờ cấm tạo cửa sổ (`creationflags=subprocess.CREATE_NO_WINDOW` hoặc `STARTUPINFO.dwFlags |= STARTF_USESHOWWINDOW; wShowWindow = SW_HIDE`), Windows sẽ tự động tạo cửa sổ Console mới (`conhost.exe`) và chớp nháy đè lên màn hình người dùng.
  - Rà soát các vị trí trong TDQ Workflow gọi `graphify` (như trong `scripts/tdq_finish.py`, `scripts/tdq_setup.py`, `scripts/tdq_graphify.py`, `hooks/scripts/...`), các hook nền `tdq_setup.py --nen`, các lời gọi git, python subprocess.
  - Bổ sung cấu hình `creationflags` / flags ẩn cửa sổ console chuẩn hóa trên Windows cho mọi subprocess nội bộ.
- **Điểm chưa rõ**:
  - Đã xác định rõ: hiện tượng xảy ra khi `tdq_finish.py` (chạy cuối mỗi turn có code đổi), `tdq_lsp.py` (chạy kiểm tra bậc 7 graphify), `tdq_setup.py` (build nền & smoke test) gọi subprocess mà thiếu cờ `CREATE_NO_WINDOW`.

## Hiểu & kiến thức

### Nguyên nhân kỹ thuật chính xác
1. **Cơ chế quản lý Console Window của Windows Subsystem**:
   - Trên Windows, một file thực thi dòng lệnh (như `graphify.exe`, `git.exe`, `cmd.exe`, `python.exe`) được compile với subsystem `IMAGE_SUBSYSTEM_WINDOWS_CUI` (Console User Interface).
   - Khi một tiến trình cha (chạy từ GUI của VS Code, IDE, hoặc tiến trình hook/worker không sở hữu Console Window trực tiếp) gọi API `CreateProcess` (thông qua Python `subprocess.run` / `subprocess.Popen` / `os.system`), nếu không truyền cờ `CREATE_NO_WINDOW` (`0x08000000`), Windows sẽ tự động cấp phát một cửa sổ Console Host mới (`conhost.exe`) cho tiến trình con.
   - Cửa sổ này hiển thị tiêu đề là đường dẫn đầy đủ của file nhị phân đang chạy (như ảnh người dùng chụp: `C:\Users\quanghau\AppData\Roaming\Python\Python314\Scripts\graphify.exe`), xuất hiện chớp nháy đè lên giao diện người dùng rồi tắt khi tiến trình kết thúc.

2. **Các điểm phát sinh trong TDQ Workflow**:
   - `scripts/tdq_finish.py`: Hàm `_run()` chạy ở cuối mỗi turn có thay đổi file code gọi `_run(["graphify", "extract", ".", "--code-only"], ...)` bằng `subprocess.run(...)` thuần túy, không có cờ `creationflags=CREATE_NO_WINDOW`. Đây là nguyên nhân trực tiếp nhất khiến cửa sổ `graphify.exe` nhảy lên màn hình liên tục mỗi khi code xong một lượt!
   - `scripts/tdq_lsp.py`: Hàm `_run()` thực thi các probe kiểm tra `graphify god-nodes`, `agent-lsp doctor` thiếu cờ `creationflags`.
   - `scripts/tdq_setup.py`: Luồng kiểm tra dry-run `kiem_dryrun_hook` và `kiem_va_cai_shim_python3` gọi `subprocess.run(..., shell=True)` thiếu cờ ẩn cửa sổ.
   - `scripts/tdq_state.py`, `scripts/setup_status.py`, `hooks/scripts/stop_batch_checker.py`: Các lời gọi `subprocess.run` cần được bảo vệ để không nhấp nháy cửa sổ git hay cmd.

3. **Giải pháp kiến trúc**:
   - Định nghĩa hàm dùng chung `tham_so_subprocess_an_cua_so(nen_tang=None)` trong `scripts/tdq_ten_lenh.py` (nguồn sự thật duy nhất cho OS utils), trả về `{"creationflags": subprocess.CREATE_NO_WINDOW}` khi chạy trên Windows và `{}` trên POSIX.
   - Cập nhật hàm `_run()` trong `scripts/tdq_finish.py` và `scripts/tdq_lsp.py` tích hợp `tham_so_subprocess_an_cua_so()`.
   - Bổ sung cờ ẩn cửa sổ vào các lời gọi `subprocess.run` trong `scripts/tdq_setup.py`, `scripts/setup_status.py`, `hooks/scripts/stop_batch_checker.py`.
   - Xây dựng bộ test `tests/test_an_cua_so_windows.py` kiểm chứng:
     + Hàm helper trả về đúng cờ `CREATE_NO_WINDOW` (`0x08000000`) trên Windows và dict rỗng trên POSIX.
     + Các hàm `_run` trong `tdq_finish.py` và `tdq_lsp.py` luôn áp dụng cờ ẩn cửa sổ trên Windows.
     + Không gây ảnh hưởng đến luồng bắt lỗi, timeout hay stdout/stderr.

## Hỏi đáp

- Người dùng đã chọn Option 1a: Express pipeline (quick lane). Mini spec/plan được thiết lập để triển khai ngay trong 1 gate duyệt.
