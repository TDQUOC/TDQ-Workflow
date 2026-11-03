# BRIEF — Tự động xử lý lỗi Python Not Found cho Hook trên máy mới (`2026-10-19-1538-auto-fix-hook-python-not-found`)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

Người dùng phản ánh qua ảnh chụp màn hình thực tế khi cài đặt plugin `tdq-workflow` trên máy mới:
Khi restart Claude Code, hook `SessionStart:resume` báo lỗi:
`Failed with non-blocking status code: Python was not found; run without arguments to install from the Microsoft Store, or disable this shortcut from Settings > Apps > Advanced app settings > App execution aliases`

Nguyên văn yêu cầu:
"okay bây giờ tôi muốn bổ sung thêm là hiện tại rất hay gặp issue này trên máy mới install tdq-workflow tôi muốn setup lại là instruction sẽ có check và setup lại để đảm bảo hook không lỗi, ngoài ra có trong instruction và có cơ chế auto check sau khi cài nhằm đảm bảo hook không lỗi mà không cần người dùng check và báo lỗi"

Phản hồi tiếp theo của người dùng:
"1a 2a 3a và tôi muốn là nếu cài bằng dòng lệnh plugin install thì lần chạy đầu sẽ tự check và gọi skill setup để setup hoạt động ổn"

### Đọc hiểu lần đầu:
- **Mục tiêu**:
  1. Xử lý triệt để lỗi `Python was not found` (do `python3` trỏ vào App Execution Alias của Windows Store hoặc thiếu `python3` trên PATH máy Windows).
  2. Bổ sung cơ chế auto-check và tự động cài shim `python3` trong quy trình `tdq_setup.py`, kiểm chứng hook thực thi thành công 100% trước khi kết thúc setup.
  3. Cập nhật `hooks/hooks.json` với cơ chế fallback tương thích an toàn hoặc wrapper để ngay sau khi người dùng chạy `plugin install`, hook `SessionStart` vẫn thực thi thành công mà không chết vì WindowsApps stub.
  4. Cơ chế tự động kích hoạt setup ở lần chạy đầu tiên: Hook `SessionStart` tự động nhận diện nếu máy mới cài plugin (chưa có mốc setup hoàn chỉnh hoặc thiếu shim), tự động kích hoạt setup và hướng dẫn Agent gọi `tdq-setup` để hoàn tất cấu hình.
  5. Cập nhật instruction (`CLAUDE.md`): Lệnh setup tương thích `python3 / py -3 / python` và quy tắc Self-healing cho Agent.
- **Phạm vi dự kiến**:
  - `hooks/hooks.json` và các script trong `hooks/scripts/` (đặc biệt `session_start.py`).
  - `scripts/tdq_setup.py`, `scripts/tdq_checkportable.py`, `scripts/tdq_ten_lenh.py`.
  - Khối hướng dẫn `KHOI_HUONG_DAN` trong `tdq_setup.py` và `~/.claude/CLAUDE.md`.
  - Bộ unit test kiểm thử shim, fallback hook runner và quy trình setup.

## Hiểu & kiến thức

- **Bản chất lỗi WindowsApps Stub**:
  - Trên Windows 10/11, `%LOCALAPPDATA%\Microsoft\WindowsApps\python3.exe` là alias stub của Microsoft Store. Nếu người dùng cài Python từ python.org (thường chỉ có `python.exe` và `py.exe`) mà chưa tắt alias này hoặc chưa có shim `python3` trước nó trên PATH, mọi lệnh gọi `python3` sẽ kích hoạt stub và thoát với exit code non-zero (49 / 9009) kèm thông báo lỗi.
- **Cơ chế Fallback Chuỗi Lệnh Hook (`hooks/hooks.json`)**:
  - Khi Claude Code thực thi lệnh hook dạng `type: "command"` trên Windows cmd.exe: toán tử `||` cho phép fallback nếu lệnh trước thất bại.
  - Cú pháp `python3 "<script>" || py -3 "<script>" || python "<script>"` đảm bảo:
    - Trên Linux/macOS: `python3` thành công ngay lập tức, không chạy tiếp các nhánh sau.
    - Trên Windows: nếu `python3` dính stub hoặc không có, cmd tự động chạy tiếp qua `py -3` hoặc `python`, giúp hook không bao giờ văng lỗi `Python was not found` ngay từ lần khởi động đầu tiên sau khi cài plugin!
- **Cơ chế Tự Động Hóa Shim trong `tdq_setup.py`**:
  - Tự động dò tìm Python interpreter thực tế (`sys.executable`, `py -3`, `python.exe` hợp lệ).
  - Tự động sinh `python3.cmd` và shell script `python3` vào thư mục PATH khả dụng (ví dụ Scripts của Python, User Bin, hoặc thư mục cài Python) đặt TRƯỚC WindowsApps.
  - Tự động chạy smoke dry-run: gọi thử script hook bằng `python3` để kiểm chứng.
- **Cơ chế Tự Động Nhận Diện Lần Đầu Sau `plugin install`**:
  - Trong `session_start.py`: kiểm tra mốc trạng thái setup (`.tdq-san-sang.json`, mốc phát hành, shim `python3`).
  - Nếu phát hiện lần đầu chạy sau khi cài đặt plugin:
    - Tự động kích hoạt quy trình setup nền (`tdq_setup.py --nen`).
    - Bơm chỉ thị rõ ràng vào session prompt để Agent tự động thực hiện hoàn tất setup (gọi skill `tdq-setup`).
- **Instruction Toàn Cục Tự Chữa Lành (`CLAUDE.md`)**:
  - Cung cấp cú pháp chạy setup linh hoạt (`python3/py -3/python {goc}/scripts/tdq_setup.py`).
  - Hướng dẫn Agent: nếu thấy bất kỳ lỗi nào liên quan đến `Python was not found` hoặc hook, tự động chạy lệnh setup để vá môi trường ngay lập tức mà không cần hỏi người dùng.

## Hỏi đáp

1. **Cơ chế Auto-Check & Auto-Setup `python3` trong `tdq_setup.py`:**
   - Lựa chọn: **1a (Đã duyệt)** — Tự động phát hiện interpreter thực tế, tự sinh shim `python3.cmd` + `python3` vào thư mục PATH hợp lệ, chạy smoke dry-run kiểm chứng hook 100%.
2. **Cập nhật Instruction toàn cục (`~/.claude/CLAUDE.md`):**
   - Lựa chọn: **2a (Đã duyệt)** — Cập nhật lệnh setup tương thích (`python3 / py -3 / python`), bổ sung nguyên tắc Self-healing cho Agent.
3. **Mức QC kiểm thử chất lượng:**
   - Lựa chọn: **3a (Đã duyệt)** — Mức `ultra`: Kiểm thử unit test, giả lập WindowsApps stub, smoke test thực tế hook runner.
4. **Yêu cầu bổ sung đặc biệt:**
   - Khi người dùng cài đặt bằng lệnh `claude plugin install`, lần chạy đầu tiên hệ thống phải tự check và tự động gọi skill setup để đảm bảo hoạt động trơn tru.

### Lộ trình

- `spec` → Soạn thảo tài liệu đặc tả kỹ thuật chi tiết (`docs/tdq/spec/2026-10-19-1538-auto-fix-hook-python-not-found.md`).
- `plan` → Lập kế hoạch phân rã công việc từng bước (task-by-task) kèm test kiểm chứng.
- `implement` → Triển khai giải pháp theo quy trình Red-Green trong một turn duy nhất.
- `qc` → Kiểm thử mức `ultra` (toàn bộ test suite, regression, dry-run hook trên Windows).
- `report` → Báo cáo kết quả và xác nhận hoàn tất.
