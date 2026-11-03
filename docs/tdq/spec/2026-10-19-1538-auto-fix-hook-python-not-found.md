# SPEC — Tự động xử lý lỗi Python Not Found cho Hook và Auto-Setup trên máy mới

Ngày: 2026-10-19 · Bản: 1.0 · Brief: ../brief/2026-10-19-1538-auto-fix-hook-python-not-found.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

## Mục lục

- 1. Mục tiêu & phạm vi
- 1b. Lộ trình
- 2. Đầu ra cụ thể
- 2b. Ranh giới module
- 3. Cách tiếp cận & lý do
- 3b. Năng lực & công cụ
- 4. Yêu cầu bắt buộc
- 5. Ràng buộc & rủi ro
- 6. QC & Definition of Done
- 7. Câu hỏi còn mở

## 1. Mục tiêu & phạm vi

- **Mục tiêu**:
  - Khắc phục triệt để lỗi `SessionStart:resume hook error: Failed with non-blocking status code: Python was not found...` do lệnh `python3` trỏ vào App Execution Alias của Microsoft Store trên Windows mới cài đặt plugin `tdq-workflow`.
  - Thiết lập chuỗi lệnh fallback đa nền tảng trong `hooks/hooks.json` để mọi hook thực thi an toàn ngay từ lần chạy đầu tiên sau lệnh `claude plugin install`.
  - Tích hợp cơ chế **Auto-Check & Auto-Setup `python3`** trực tiếp trong quy trình `scripts/tdq_setup.py`: tự động phát hiện interpreter Python sống (`sys.executable`, `py -3`, `python.exe`), tự sinh shim `python3.cmd` và shell script `python3` vào thư mục PATH khả dụng (nằm trước WindowsApps), và chạy smoke test hook dry-run kiểm chứng 100%.
  - Bổ sung cơ chế tự động nhận diện lần đầu chạy sau khi cài đặt plugin trong `session_start.py`: tự kích hoạt setup nền và hướng dẫn Agent gọi `tdq-setup` để hoàn tất cấu hình.
  - Cập nhật khối hướng dẫn `KHOI_HUONG_DAN` trong `tdq_setup.py` và `~/.claude/CLAUDE.md`: cú pháp setup tương thích đa dạng và nguyên tắc Self-healing tự phục hồi.

- **Trong phạm vi**:
  - `hooks/hooks.json`: cập nhật command chuỗi fallback tương thích đa nền tảng (`python3 "..." || py -3 "..." || python "..."`).
  - `hooks/scripts/session_start.py`: nhận diện phiên làm việc đầu tiên sau `plugin install` hoặc chưa setup mốc phát hành/shim, tự động kích hoạt `tdq_setup.py --nen` và bơm tín hiệu gợi ý Agent gọi `tdq-setup`.
  - `scripts/tdq_setup.py`: bổ sung bước `kiem_va_cai_shim_python3()` và `kiem_dryrun_hook()` vào luồng `main()`, cập nhật `KHOI_HUONG_DAN` với cú pháp đa nền tảng và nguyên tắc Self-healing.
  - `scripts/tdq_checkportable.py`: hoàn thiện logic `chon_thu_muc_shim` để tìm thêm thư mục Scripts của Python hiện tại hoặc User Bin nếu các thư mục PATH khác bị chặn hoặc nằm sau Store stub.
  - Bộ kiểm thử unit test mới: kiểm thử chuỗi fallback hook, kiểm thử tạo shim, kiểm thử smoke test dry-run và kiểm thử chống hồi quy.

- **Ngoài phạm vi**:
  - Không can thiệp sửa đổi các plugin bên ngoài khác ngoài phạm vi TDQ-Workflow.
  - Không tự ý can thiệp cài đặt Python mới từ internet hoặc chỉnh sửa registry hệ thống sâu ngoài phạm vi User Environment.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research code | CÓ (xong) | Khảo sát kỹ `hooks.json`, `tdq_setup.py`, `tdq_checkportable.py`, `session_start.py` |
| Interview | CÓ (xong) | Người dùng đã duyệt phương án 1a, 2a, 3a và yêu cầu auto-setup lần đầu |
| spec | CÓ | Đặc tả chi tiết cơ chế shim, fallback hook và auto-setup |
| plan | CÓ | Lập kế hoạch phân rã 4 cụm công việc cụ thể |
| implement | CÓ | Triển khai Red-Green trọn gói trong 1 turn |
| QC (ultra) | CÓ | Chạy toàn bộ test suite, test shim, test giả lập Store stub |
| report | CÓ | Báo cáo kết quả và xác nhận hoàn tất |

## 2. Đầu ra cụ thể

| # | Đầu ra | Vị trí / Đường dẫn | Tiêu chí hoàn thành |
|---|---|---|---|
| 1 | Chuỗi fallback hook an toàn đa nền tảng | `hooks/hooks.json` | Mọi hook command có fallback `python3 ... \|\| py -3 ... \|\| python ...`, chạy an toàn trên Windows cmd mà không báo lỗi nếu thiếu python3 |
| 2 | Auto-Check & Auto-Setup `python3` trong `tdq_setup.py` | `scripts/tdq_setup.py` | Gọi `kiem_va_cai_shim_python3()`, tự động sinh shim nếu thiếu hoặc dính WindowsApps stub, chạy smoke dry-run hook |
| 3 | Mở rộng tìm kiếm thư mục đặt shim | `scripts/tdq_checkportable.py` | Bổ sung fallback thư mục Python Scripts (`os.path.dirname(sys.executable)/Scripts`), đảm bảo luôn tìm được thư mục ghi được |
| 4 | Cơ chế tự động kích hoạt setup lần đầu sau cài đặt | `hooks/scripts/session_start.py` | Phát hiện lần đầu chạy (chưa có mốc phát hành hoặc thiếu shim), tự động kích hoạt nền và thông báo `[TDQ:SETUP]` |
| 5 | Instruction toàn cục tương thích & Self-healing | `KHOI_HUONG_DAN` & `~/.claude/CLAUDE.md` | Hướng dẫn lệnh linh hoạt `python3 / py -3 / python` và bổ sung nguyên tắc Agent tự chạy setup khi gặp lỗi môi trường |
| 6 | Bộ unit test kiểm chứng | thư mục test của repo | Kiểm thử fallback hook, kiểm thử logic chọn thư mục shim, kiểm thử smoke test dry-run với mock stub |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc | Đầu ra §2 |
|---|---|---|---|
| Hook Fallback | `hooks/hooks.json`, `hooks/scripts/session_start.py` | không | 1, 4 |
| Setup & Shim | `scripts/tdq_setup.py`, `scripts/tdq_checkportable.py` | Hook Fallback | 2, 3 |
| Instruction | `scripts/tdq_setup.py`, `~/.claude/CLAUDE.md` | Setup & Shim | 5 |
| Test Suite | thư mục test của repo | Cả 3 module trên | 6 |

## 3. Cách tiếp cận & lý do

- **Chọn giải pháp đa tầng (Defense in Depth)**:
  1. *Tầng phòng vệ tức thì (Zero-day hook execution)*: Cập nhật `hooks/hooks.json` dùng chuỗi fallback `python3 "..." || py -3 "..." || python "..."`. Ngay khi cài đặt plugin qua `claude plugin install`, dù máy chưa hề có shim `python3`, hook `SessionStart` vẫn chạy thành công thông qua `py -3` hoặc `python` mà không bị Store stub làm gãy.
  2. *Tầng tự động kích hoạt lần đầu*: `session_start.py` nhận diện máy mới cài đặt plugin, tự động chạy `tdq_setup.py --nen` trong nền và thông báo mã `[TDQ:SETUP]` để Agent chủ động thực thi kiểm tra 7 bậc.
  3. *Tầng tự động vá triệt để*: `tdq_setup.py` kiểm tra `python3`. Nếu phát hiện `python3` dính stub hoặc lỗi, tự động tạo shim `python3.cmd` và `python3` trỏ thẳng vào interpreter thực tế (`sys.executable` hoặc `py -3`), đặt vào thư mục PATH khả dụng (Scripts của Python hoặc User Bin) trước WindowsApps. Sau đó chạy dry-run kiểm chứng.
  4. *Tầng tự phục hồi (Self-healing)*: Ghim instruction vào `~/.claude/CLAUDE.md` hướng dẫn Agent nếu gặp bất kỳ lỗi nào về `Python was not found`, tự động chạy lệnh setup để vá môi trường.
- **Lý do**: Giải quyết tận gốc vấn đề từ lúc người dùng vừa gõ lệnh cài đặt cho đến suốt quá trình vận hành sau này, không đòi hỏi người dùng phải can thiệp thủ công vào Windows Settings.

## 3b. Năng lực & công cụ

| Năng lực / Công cụ | Có sẵn? | Phán quyết | Lý do / Vai trò |
|---|---|---|---|
| `mcp__lsp__*` | CÓ | DÙNG | Tra cứu symbol, kiểm tra định nghĩa hàm và blast radius |
| `graphify` | CÓ | NỀN | Bản đồ kiến trúc toàn dự án |
| `grep` | CÓ | DÙNG | Quét chuỗi cấu hình hook và instruction |
| `python3` | CÓ | DÙNG | Thực thi test runner, setup và kiểm chứng dry-run |
| `doc_lint` | CÓ | DÙNG | Kiểm tra chuẩn tài liệu Markdown R1-R14 |
| `tdq_devtool_mcp` | CÓ | KHÔNG | khác lĩnh vực — không liên quan đến browser testing |

## 4. Yêu cầu bắt buộc

1. **Khả năng tương thích chéo nền tảng (Cross-platform)**:
   - Chuỗi lệnh trong `hooks/hooks.json` phải thực thi đúng trên cả Windows (cmd.exe), macOS (zsh/bash) và Linux (bash/sh).
2. **Không làm gãy các hook hiện có**:
   - Mọi hook argument, stdin/stdout format (`SessionStart`, `UserPromptSubmit`, `PreToolUse`, `Stop`) phải được bảo toàn nguyên vẹn.
3. **An toàn PATH và tính Bền vững (Idempotency)**:
   - Việc ghi shim `python3.cmd` không ghi đè nếu nội dung đã chuẩn xác, không tạo file rác trong các thư mục tạm (`temp`, `tmp`).
4. **Không thêm attribution trailer**:
   - Tuyệt đối tuân thủ quy tắc git commit và PR sạch, không thêm bất kỳ trailer ngoài nào.

## 5. Ràng buộc & rủi ro

- **Rủi ro cú pháp shell trong hooks.json**:
  - *Nguy cơ*: Toán tử `||` có thể bị diễn giải khác nhau giữa cmd.exe trên Windows và sh trên POSIX.
  - *Giải pháp*: Cú pháp `cmd1 || cmd2` là chuẩn POSIX và cũng là chuẩn toán tử điều kiện của cmd.exe. Trên POSIX, nếu `cmd1` (python3) thành công với exit code 0 thì `cmd2` không bao giờ được gọi. Trên Windows, nếu `cmd1` trả về lỗi (exit code != 0), cmd tự động thực thi `cmd2`. Ta sẽ bổ sung unit test kiểm chứng hành vi này.
- **Rủi ro quyền ghi thư mục PATH trên Windows**:
  - *Nguy cơ*: Người dùng không có quyền Admin để ghi vào `C:\Program Files`.
  - *Giải pháp*: Fallback ghi shim vào thư mục `Scripts` của Python người dùng (thường nằm trong `AppData\Local\Programs\Python` hoặc `venv`), nơi người dùng luôn có toàn quyền ghi.

## 6. QC & Definition of Done

Mức QC: **ultra** (Đã chốt với người dùng).

| # | Hạng mục kiểm tra | Điều kiện PASS | Đo trước | Dự phòng nếu trượt |
|---|---|---|---|---|
| QC-1 | Cấu trúc chuỗi fallback trong `hooks.json` | 100% các hook command đều có cơ chế fallback `py -3` / `python` | 0% (hiện tại gọi cứng python3) | Ghi nhận lỗi cú pháp và điều chỉnh định dạng command |
| QC-2 | Auto-Check & Auto-Setup trong `tdq_setup.py` | `tdq_setup.py` tự động phát hiện, cài đặt shim và kiểm chứng dry-run thành công | Chưa có bước này trong setup | Bổ sung hàm cài shim độc lập có log chi tiết |
| QC-3 | Mở rộng tìm thư mục shim trong `tdq_checkportable.py` | Tìm được thư mục hợp lệ ngay cả khi PATH không có thư mục nào trước Store stub | Bị chặn nếu mọi PATH nằm sau Store stub | Fallback vào thư mục Scripts của interpreter hiện hành |
| QC-4 | Tự động kích hoạt setup lần đầu trong `session_start.py` | Xuất hiện tín hiệu `[TDQ:SETUP]` khi chạy lần đầu chưa có mốc phát hành | Chưa có logic nhận diện này | Bổ sung biến kiểm tra mốc phát hành `.tdq-phat-hanh.json` |
| QC-5 | Cập nhật `KHOI_HUONG_DAN` & `CLAUDE.md` | Instruction hiển thị lệnh tương thích đa nền tảng và nguyên tắc Self-healing | Đang hiển thị lệnh cứng `python3` | Cập nhật template chuỗi KHOI_HUONG_DAN |
| QC-6 | Toàn bộ unit test mới & cũ | ĐẠT 100% test suite (`python scripts/tdq_test.py tron-bo`) | Đang ĐẠT trên nhánh chính | Sửa lỗi hồi quy trước khi chuyển phase |
| QC-7 | Kiểm tra chuẩn tài liệu Markdown (`doc_lint.py`) | 0 vi phạm (exit 0) trên toàn bộ spec, brief, plan | Đang ĐẠT 0 lỗi | Sửa format theo đúng luật R1-R14 |

## 7. Câu hỏi còn mở

(Không còn câu hỏi mở nào. Mọi phương án đã được làm rõ và thống nhất với người dùng).
