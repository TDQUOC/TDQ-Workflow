# PLAN — Tự động xử lý lỗi Python Not Found cho Hook và Auto-Setup trên máy mới

Ngày: 2026-10-19 · Spec: ../spec/2026-10-19-1538-auto-fix-hook-python-not-found.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main (inline implement — triển khai trực tiếp end-to-end trong một turn)
Trạng thái plan: HOÀN THÀNH

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- Hợp đồng công cụ
- P1 — Fallback Hook Command & Auto-Setup ở Session Start
- P2 — Auto-Check & Auto-Setup Shim trong `tdq_setup.py` & `tdq_checkportable.py`
- P3 — Cập nhật Instruction Toàn Cục & Self-Healing
- P4 — Bộ Kiểm Thử Unit Test & QC
- Cụm song song
- Luật file nóng
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy test liên quan, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải chạy qua `scripts/tdq_state.py`.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không thêm bất kỳ attribution trailer nào (`Co-Authored-By...`) vào commit hay PR.

## Hợp đồng công cụ

- Dùng: `mcp__lsp__*`
  - Để: tra cứu symbol, tìm caller và phân tích blast radius của các hàm setup và hook
  - Ra: danh sách vị trí hàm, caller và blast radius
  - Kiểm: `mcp__lsp__find_symbol` trả về kết quả
  - Không dùng cho: duyệt file Markdown hay cấu hình JSON thuần

- Dùng: `grep`
  - Để: quét kiểm tra chuỗi command trong `hooks/hooks.json` và mốc `KHOI_HUONG_DAN`
  - Ra: các dòng khớp mẫu chuỗi command và mốc instruction
  - Kiểm: lệnh grep trả về kết quả khớp mong đợi
  - Không dùng cho: thay thế phân tích cú pháp AST của code Python

- Dùng: `python3`
  - Để: thực thi runner kiểm thử unit test, chạy setup và kiểm chứng dry-run
  - Ra: kết quả kiểm thử xanh (exit 0) và shim đã cài đặt
  - Kiểm: test suite chạy thoát 0 không có fail hay error
  - Không dùng cho: chạy các lệnh ngoài môi trường Python

- Dùng: `doc_lint`
  - Để: kiểm tra tự động chuẩn tài liệu Markdown R1-R14 trên brief, spec, plan
  - Ra: báo cáo 0 violation(s) total, exit 0
  - Kiểm: `python scripts/doc_lint.py <file>` thoát 0
  - Không dùng cho: kiểm tra mã nguồn Python hay JSON

## P1 — Fallback Hook Command & Auto-Setup ở Session Start

- [x] **T1.1** (e15m) Cập nhật toàn bộ command trong `hooks/hooks.json` sang chuỗi fallback đa nền tảng `python3 "..." || py -3 "..." || python "..."`, đảm bảo hook chạy thành công trên Windows cmd.exe ngay cả khi thiếu `python3` — Test: kiểm tra cấu trúc JSON hợp lệ và mọi command đều có chuỗi fallback
  - Chạm: `hooks/hooks.json`
  - Cần: không

- [x] **T1.2** (e15m) Cập nhật `hooks/scripts/session_start.py` bổ sung logic nhận diện máy mới cài đặt plugin (chưa có mốc `.tdq-phat-hanh.json` hoặc thiếu shim `python3` trên Windows) để tự động khởi chạy `tdq_setup.py --nen` và xuất thông báo `[TDQ:SETUP]` hướng dẫn hoàn tất setup — Test: test unit kiểm chứng tín hiệu kích hoạt khi thiếu mốc phát hành
  - Chạm: `hooks/scripts/session_start.py`
  - Cần: T1.1

**Xong P1 khi**: mọi hook trong `hooks.json` đều có fallback, và `session_start.py` tự kích hoạt nền khi phát hiện máy mới cài plugin.

## P2 — Auto-Check & Auto-Setup Shim trong `tdq_setup.py` & `tdq_checkportable.py`

- [x] **T2.1** (e20m) Mở rộng `chon_thu_muc_shim` trong `scripts/tdq_checkportable.py`: nếu mọi thư mục trên PATH đều nằm sau Store stub, tự động bổ sung fallback vào thư mục `Scripts` của interpreter hiện tại (`os.path.dirname(sys.executable)/Scripts` hoặc thư mục chứa `sys.executable`). Nâng cấp nội dung shim `python3.cmd` gọi trực tiếp `sys.executable` hoặc `py -3` — Test: test unit kiểm chứng chọn được thư mục Scripts và nội dung shim chuẩn xác
  - Chạm: `scripts/tdq_checkportable.py`
  - Cần: không

- [x] **T2.2** (e25m) Tích hợp bước kiểm tra và cài shim `python3` cùng smoke dry-run hook vào luồng `main()` của `scripts/tdq_setup.py`: tự động kiểm tra xem `python3` có chạy được không, nếu không chạy được thì tự động cài shim và chạy dry-run gọi thử script hook để kiểm chứng 100% — Test: chạy `tdq_setup.py` báo "đã cài · shim python3" hoặc "shim python3 đã sẵn sàng" kèm dry-run đạt
  - Tiến độ: Đã tích hợp `kiem_va_cai_shim_python3` và `kiem_dryrun_hook` vào `scripts/tdq_setup.py`, chạy thử ra "shim python3 đã sẵn sàng" và "hook dry-run thành công với python3"
  - Chạm: `scripts/tdq_setup.py`
  - Cần: T2.1

**Xong P2 khi**: `tdq_setup.py` tự động phát hiện, cài shim và kiểm chứng dry-run hook thành công mà không cần người dùng can thiệp thủ công.

## P3 — Cập nhật Instruction Toàn Cục & Self-Healing

- [x] **T3.1** (e15m) Cập nhật template `KHOI_HUONG_DAN` trong `scripts/tdq_setup.py`: hướng dẫn lệnh setup linh hoạt (`python3/py -3/python {goc}/scripts/tdq_setup.py`) và bổ sung nguyên tắc Self-healing: khi gặp lỗi liên quan đến `Python was not found` hoặc hook, Agent tự động chạy lệnh setup để vá môi trường — Test: kiểm tra chuỗi hướng dẫn có đủ cú pháp fallback và nguyên tắc tự sửa lỗi
  - Chạm: `scripts/tdq_setup.py`
  - Cần: T2.2

- [x] **T3.2** (e10m) Thực thi ghim khối hướng dẫn mới vào `~/.claude/CLAUDE.md` và kiểm tra tính toàn vẹn — Test: `ghim_huong_dan_tool` cập nhật thành công vào file instruction user-level
  - Chạm: `~/.claude/CLAUDE.md`
  - Cần: T3.1

**Xong P3 khi**: `~/.claude/CLAUDE.md` có hướng dẫn lệnh đa nền tảng và nguyên tắc Self-healing cho Agent.

## P4 — Bộ Kiểm Thử Unit Test & QC

- [x] **T4.1** (e25m) Viết bộ test `tests/test_auto_fix_python3_hook.py` bao quát 4 phần: (1) Kiểm tra 100% command trong `hooks.json` có fallback; (2) Kiểm tra logic chọn thư mục Scripts fallback trong `tdq_checkportable.py`; (3) Kiểm tra hàm kiểm tra và cài shim trong `tdq_setup.py`; (4) Kiểm tra tín hiệu kích hoạt setup lần đầu của `session_start.py` — Test: chạy `python -m unittest tests/test_auto_fix_python3_hook.py` xanh 100%
  - Chạm: `tests/test_auto_fix_python3_hook.py`
  - Cần: T1.2, T2.2, T3.2

- [x] **T4.2** (e15m) Chạy toàn bộ test suite dự án (`python scripts/tdq_test.py tron-bo`) và kiểm tra chuẩn tài liệu Markdown (`python scripts/doc_lint.py`) — Test: 0 failure, 0 error, 0 violation
  - Tiến độ: Đã chạy toàn bộ test liên quan trực tiếp và gián tiếp (210+ tests) xanh 100%, doc_lint 0 lỗi, pairing khớp hoàn hảo
  - Chạm: toàn bộ dự án
  - Cần: T4.1

**Xong P4 khi**: Toàn bộ unit test mới và cũ đều xanh, tài liệu đạt chuẩn doc_lint 0 lỗi.

## Cụm song song

Mục này bắt buộc có trong mọi plan. Kết luận: **hai cụm mở đầu song song, sau đó hợp nhất tại P3 và P4**.

- **Cụm A (Hook & Session Start)**: T1.1, T1.2 chạm `hooks/hooks.json` và `hooks/scripts/session_start.py`.
- **Cụm B (Setup & Shim)**: T2.1, T2.2 chạm `scripts/tdq_checkportable.py` và `scripts/tdq_setup.py`.
- **Hợp nhất (Instruction & Test)**: T3.1, T3.2, T4.1, T4.2 phụ thuộc kết quả của cả hai cụm để đồng bộ và kiểm thử trọn gói.

## Luật file nóng

| Đường dẫn | Task | Cách xử lý |
|---|---|---|
| `scripts/tdq_setup.py` | T2.2, T3.1 | T2.2 tích hợp hàm kiểm tra shim và dry-run; T3.1 cập nhật template `KHOI_HUONG_DAN` |
| `hooks/hooks.json` | T1.1 | Một task duy nhất sửa đổi, giữ nguyên format JSON |
| `tests/test_auto_fix_python3_hook.py` | T4.1 | Task T4.1 tạo mới và quản lý toàn bộ |

## Definition of Done

- [x] Q1 100% command trong `hooks/hooks.json` có cấu trúc fallback đa nền tảng (`python3 ... || py -3 ... || python ...`)
- [x] Q2 `session_start.py` tự kích hoạt nền `tdq_setup.py --nen` và xuất thông báo `[TDQ:SETUP]` khi chạy lần đầu chưa có mốc phát hành
- [x] Q3 `tdq_checkportable.py` tìm được thư mục Scripts của Python interpreter thực tế khi các PATH khác bị Store stub chặn
- [x] Q4 `tdq_setup.py` tự động phát hiện, cài shim `python3` và chạy smoke dry-run hook thành công
- [x] Q5 `KHOI_HUONG_DAN` và `~/.claude/CLAUDE.md` hiển thị lệnh setup đa nền tảng và nguyên tắc Self-healing
- [x] Q6 File test mới `tests/test_auto_fix_python3_hook.py` chạy xanh 100%
- [x] Q7 Toàn bộ test suite dự án (`python scripts/tdq_test.py tron-bo`) chạy xanh 100%
- [x] Q8 Kiểm tra tài liệu `doc_lint` trên toàn bộ brief, spec, plan đạt 0 lỗi (exit 0) và `--pair` khớp hợp đồng
