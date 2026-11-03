# BRIEF — Xử Lý Dứt Điểm Cửa Sổ Command Console Chớp Nháy Trên Windows (`2026-10-20-1230-fix-chop-nhay-console-windows`)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

"mở request làm dứt điểm đi"
(Yêu cầu xử lý triệt để hiện tượng cửa sổ command / console chớp nháy hoặc bật lên khi thực thi các script nền và hook của TDQ Workflow trên Windows)

## Hiểu & kiến thức

### 1. Phân tích nguyên nhân gốc rễ
Trên hệ điều hành Windows, mọi tiến trình con dòng lệnh (conhost.exe / cmd.exe) được khởi chạy qua `subprocess.run` hoặc `subprocess.Popen` sẽ **mặc định tự động cấp phát và hiển thị một cửa sổ console ngắn trên màn hình**, trừ khi được truyền cờ `creationflags = subprocess.CREATE_NO_WINDOW` (giá trị `0x08000000`).

Rà soát toàn bộ codebase phát hiện 5 vị trí cốt lõi đang gọi trực tiếp `subprocess.run` / `Popen` mà thiếu cờ này:
1. `hooks/scripts/session_start.py` (dòng 172): Kích hoạt tiến trình nền `tdq_setup.py --nen` dùng cờ `0x00000008 | 0x00000200` (`DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP`), thiếu `0x08000000` (`CREATE_NO_WINDOW`).
2. `scripts/tdq_state.py` (dòng 636 & 1572): Các lệnh `_git()` kiểm tra status/rev-parse và kiểm tra Codex CLI gọi trực tiếp `subprocess.run` thiếu `creationflags`.
3. `scripts/tdq_team.py` (dòng 804, 819, 1210): Các lệnh `_git()` và `chay_test_task()` gọi `subprocess.run` trực tiếp thiếu `creationflags`.
4. `scripts/tdq_test.py` (dòng 521): Lệnh gọi `git` kiểm tra thay đổi vùng chạm thiếu `creationflags`.
5. `hooks/scripts/codex_edit_gate.py` (dòng 213) & `scripts/tdq_devtool_mcp.py` (dòng 276): Gọi subprocess con thiếu `CREATE_NO_WINDOW`.

### 2. Giải pháp kỹ thuật
- Đồng bộ hóa toàn bộ các điểm gọi subprocess sử dụng `tdq_ten_lenh.tham_so_subprocess_an_cua_so()` hoặc `tdq_ten_lenh.chay_subprocess()`.
- Tại các vị trí dùng `Popen` tiến trình nền (`session_start.py`, `tdq_devtool_mcp.py`), kết hợp cờ `0x08000000` vào `creationflags`.
- Đảm bảo 100% các cuộc gọi tiến trình con trên Windows hoàn toàn vô hình (silent & no console flashing).

## Hỏi đáp
- Không có câu hỏi mở. Giải pháp tập trung vá cờ `CREATE_NO_WINDOW` cho tất cả các điểm trên.
