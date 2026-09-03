# BÁO CÁO TƯƠNG THÍCH — Bộ workflow TDQ ở máy khác, trên Linux và Windows
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Bằng chứng: `2026-09-03-1648-kiem-da-nen-tang-host-bang-chung.md` · Lệnh bạn tự chạy:
`2026-09-03-1648-kiem-da-nen-tang-host-lenh-kiem.md`

**Windows ở đây nghĩa là PowerShell thuần / cmd.exe**, không phải Git Bash và không phải WSL.
Không có máy Linux/Windows thật để chạy thử, nên mức cao nhất báo cáo này được phép nói là
"đọc mã không thấy lỗi" — không chỗ nào trong đây khẳng định phần mềm đã hoạt động ở hai hệ đó.

Mỗi phát hiện mang một **nhãn lớp bằng chứng**: `đọc mã` (đọc thẳng mã nguồn, chắc nhất) ·
`giả lập` (tái hiện cơ chế hỏng trên macOS) · `tài liệu` (đối chiếu tài liệu host, kèm link).

## P1 — Hook gọi thẳng tên lệnh `python3`

- **Nhãn:** đọc mã + giả lập
- **Triệu chứng:** trên Windows, mọi hook im lặng không chạy, hoặc host báo `python3` không
  phải là lệnh. Xem GL1 trong file bằng chứng: `/bin/sh: python3: command not found`.
- **Vị trí:** `hooks/hooks.json:1` (5/5 command) · `portable_codex/.codex/hooks.json:1`
  (5/5 command) · `antigravity_portable/hooks.json:1` (2/2 command) · nơi sinh ra:
  `scripts/build_portable.py:905`
- **Hệ dính:** Windows. Linux hầu hết có `python3`, nên gần như không dính.
- **Mức nguy:** CHẶN ĐƯỜNG. Toàn bộ cơ chế hook chết, mà chết im lặng — host không có cách nào
  báo cho người dùng biết là hook đã không chạy.
- **Cách sửa đề xuất (chọn 1, là quyết định của user ở request sau):** (a) lúc build dò
  `sys.executable` và ghi đường dẫn tuyệt đối vào `command` — chắc nhất nhưng nướng cứng máy
  dựng, cùng bệnh với P3; (b) dùng trình khởi chạy `py -3` trên Windows và `python3` ở nơi khác,
  tức `build_portable.py` phải sinh `command` theo hệ đích; (c) yêu cầu người dùng tự tạo bí
  danh `python3` — rẻ nhất nhưng đẩy lỗi sang người dùng, và im lặng khi họ quên.

## P2 — Cảnh báo "bundle dựng ở máy khác" là mã chết

- **Nhãn:** đọc mã (chạy thật lệnh kiểm để lấy triệu chứng)
- **Triệu chứng:** `tdq_checkportable.py check` luôn in NOTE "unexpanded `~`" kể cả khi không
  `command` nào còn `~`, và **không bao giờ** in được cảnh báo "bundle này dựng dưới thư mục nhà
  của người khác" — đúng ca dùng mà bạn đang hỏi.
- **Vị trí:** `scripts/tdq_checkportable.py:367` (điều kiện `if "~" in noi_dung`) và
  `scripts/tdq_checkportable.py:369` (nhánh `elif` không bao giờ chạy tới).
- **Hệ dính:** mọi hệ. Đây là lỗi logic, không phải lỗi nền tảng.
- **Mức nguy:** CAO. Cổng gác duy nhất cho việc "mang bundle sang máy khác" đang tắt, và nó tắt
  một cách im lặng — người dùng thấy `CLEAN` rồi yên tâm cài.
- **Nguyên nhân gốc:** `noi_dung` là TOÀN BỘ `hooks.json`, mà chuỗi mô tả trong chính file đó có
  nhắc `~/.gemini/config/config.json`. Vế `if` vì thế luôn đúng.
- **Cách sửa đề xuất:** chỉ quét dấu `~` trong các giá trị `command` (parse JSON rồi duyệt), chứ
  không quét văn bản thô của cả file. Sửa mất vài dòng — nhưng 4b chốt request này không sửa.

## P3 — Bundle agy nướng cứng thư mục nhà của máy dựng

- **Nhãn:** đọc mã
- **Triệu chứng:** copy `antigravity_portable/` sang máy người khác thì hook trỏ vào thư mục nhà
  không tồn tại; agy chạy lệnh và nhận exit khác 0, hoặc không chạy gì cả.
- **Vị trí:** `antigravity_portable/hooks.json:1` (command chứa `/Users/truongdinhquoc/...`) ·
  nơi sinh: `scripts/build_portable.py:882` (`goc_agy_tuyet_doi`).
- **Hệ dính:** mọi hệ — đây là lỗi "máy khác", không phải lỗi hệ điều hành. Nặng thêm trên
  Windows vì thư mục nhà còn khác cả dạng đường dẫn (`C:\Users\...`).
- **Mức nguy:** TRUNG BÌNH — có chủ ý và có lý do chính đáng (agy không bung `~` trong
  `command`, bản cũ chết exit 127), nhưng lời dặn "phải dựng lại ở máy đích" chỉ nằm trong
  docstring của `build_portable.py:886-888`, còn `antigravity_portable/README.md` — thứ người ở
  máy khác thật sự đọc — không nói một câu nào về việc đó, cũng không nhắc Windows hay Linux.
  Cộng với P2 (cổng gác đã tắt), người dùng ở máy khác không có bất kỳ cảnh báo nào.
- **Cách sửa đề xuất:** không đổi cách nướng (nó đúng), mà (a) sửa P2 để cổng gác nổ thật, và
  (b) thêm vào README của bundle agy một dòng "bundle này gắn với máy dựng, phải chạy lại
  `build_portable.py` ở máy đích".

## P4 — `check`/`merge` chạy lệnh test qua `shell=True`

- **Nhãn:** đọc mã
- **Triệu chứng:** trên Windows, `tdq_team.py check <task>` chạy dòng `Test:` bằng cmd.exe. Mọi
  plan trong repo đang viết `Test: python3 -m pytest ...`, nên test đỏ vì lý do sai hoàn toàn
  (không có `python3`), và `merge` từ chối một nhánh thực ra lành lặn.
- **Vị trí:** `scripts/tdq_team.py:896` (`subprocess.run(lenh, shell=True, ...)`).
- **Hệ dính:** Windows. Trên Linux `shell=True` là `/bin/sh`, hành xử giống macOS.
- **Mức nguy:** CAO trong chế độ sub-agent implement, VÔ HẠI trong chế độ inline.
- **Cách sửa đề xuất:** cùng gốc với P1 — khi tên lệnh `python3` được giải quyết thì P4 tự hết.
  Ngoài ra `shell=True` còn kéo theo cú pháp shell khác nhau (`&&`, `2>&1`, dấu nháy) giữa
  cmd.exe và sh; nếu muốn chắc, dòng `Test:` nên giới hạn ở một lệnh đơn không toán tử shell.

## Điểm mạnh — những chỗ ĐÃ an toàn, đừng sửa nhầm

Số liệu lấy từ `python3 tools_kiem/dem_da_nen_tang.py`, chạy lại lúc nào cũng ra được.

- `open()` chế độ văn bản thiếu `encoding=`: **0**. Toàn bộ `scripts/` + `hooks/` đọc file bằng
  UTF-8 tường minh, nên tài liệu tiếng Việt không vỡ vì code page của Windows. Đây là nửa khó
  nhất của bài toán encoding, và nó đã đúng sẵn.
- Import stdlib chỉ có trên POSIX (`fcntl`, `pwd`, `grp`, `termios`, `tty`, `resource`): **0**.
  Không module nào sẽ ném `ImportError` ngay dòng đầu trên Windows.
- **Đường dẫn tuyệt đối cứng trong `scripts/` + `hooks/`: 0**, và chỉ **1** chỗ đọc
  `sys.platform` (`scripts/claude_export.py:436`, thuần trang trí). Mã gần như không phân biệt
  hệ điều hành — nghĩa là không có nhánh macOS nào phải gỡ, chỉ có vài chỗ chung phải làm đúng.
- **`os.chmod`: 2 chỗ** (`scripts/build_portable.py:738` và `:966`). Trên Windows lệnh này gần
  như vô nghĩa nhưng KHÔNG ném lỗi, nên nó chỉ là ghi chú, không phải phát hiện.

## Chưa chốt được — chỉ máy thật mới trả lời

Ba điểm dưới đây KHÔNG phải phát hiện, mà là câu hỏi còn mở. Mỗi điểm nối tới một lệnh trong
file lệnh kiểm để bạn tự chạy.

- **C1 — Console encoding trên Windows khi stdout là pipe.** Đếm được **18** chỗ gọi `subprocess` có `text=True` mà không khai `encoding=`, và **0** chỗ trong repo đặt
  `PYTHONUTF8`/`PYTHONIOENCODING` hay gọi `sys.stdout.reconfigure`. Cả 8 file trong
  `hooks/scripts/` đều chứa ký tự ngoài ASCII. Giả lập GL2/GL3 cho thấy cơ chế này ném
  `UnicodeEncodeError` thật — nhưng Python 3.15 đã bật UTF-8 mode mặc định, và bản Python trên
  máy bạn quyết định kết quả. Vì vậy CHƯA chốt được đây là lỗi hay không. Kiểm bằng **L4** và
  **L5**.
- **C2 — Đường dẫn plugin của agy.** Repo dùng `~/.gemini/config/plugins/<tên>/`. Tài liệu công
  khai lại nói `~/.gemini/antigravity-cli/plugins/<tên>/hooks.json`
  (nguồn: [Where does Antigravity look for Hooks?](https://atamel.dev/posts/2026/07-16_where_agy_hooks/),
  [Plugins & Skills — Antigravity Docs](https://antigravity.google/docs/cli/plugins/)). Đường
  dẫn hiện tại từng được đối chiếu với một bản cài agy 1.1.11 thật (request 2026-09-03-1440),
  nên tôi KHÔNG sửa theo bài blog — hai nguồn lệch nhau thì phải hỏi máy thật. Kiểm bằng **L7**.
- **C3 — Hook Codex trên Windows native.** Codex CLI chạy được PowerShell thuần với sandbox
  AppContainer (nguồn: [Windows sandbox — OpenAI](https://developers.openai.com/codex/windows)),
  nhưng có báo cáo hook Windows native làm hỏng dấu nháy JSON khi truyền qua tham số dòng lệnh
  (nguồn: [issue #2811](https://github.com/Yeachan-Heo/oh-my-codex/issues/2811)). Hook của TDQ
  đọc JSON từ **stdin** chứ không qua tham số, nên nhiều khả năng không dính — nhưng "nhiều khả
  năng" không phải là bằng chứng. Kiểm bằng **L6**.
