# BRIEF — Kiểm bộ workflow chạy được ở máy khác và trên Linux/Windows
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> Mở thêm request check xem đã support ổn cho codex agy ,… ở máy khác chưa. Nếu như linux
> hoặc window vẫn sẽ có xử lí ổn để hoạt động ổn không bị lỗi

**Cách tôi đọc yêu cầu này**

- **Mục tiêu:** trả lời được bằng bằng chứng, không phải bằng phỏng đoán, cho hai câu hỏi:
  (1) bộ workflow — nhất là 3 bundle portable cho Codex CLI, Antigravity CLI (agy), Claude Code
  — mang sang MÁY KHÁC thì cài và chạy trơn hay còn vướng gì; (2) trên LINUX và WINDOWS thì
  còn chỗ nào hỏng, và sửa thế nào cho hết.
- **Phạm vi đoán:** `scripts/`, `hooks/`, 3 thư mục bundle portable, `scripts/build_portable.py`,
  `scripts/tdq_checkportable.py`, README của từng bundle. Không đụng nội dung luật của skill.
- **Chỗ chưa rõ, phải hỏi:**
  1. Windows có tính cả Git Bash / WSL không, hay phải chạy được ở PowerShell thuần (cmd.exe)?
     Hai đáp án này ra hai khối lượng việc rất khác nhau.
  2. Có máy Linux/Windows thật để chạy thử không, hay chỉ kiểm bằng đọc code + test giả lập
     trên macOS? Không có máy thật thì kết luận chỉ tới mức "không thấy lỗi", không tới mức
     "đã chạy được".
  3. Chỉ BÁO CÁO chỗ hỏng, hay SỬA luôn trong request này?

**Ba tín hiệu tôi đã thấy trước khi phân tích sâu** (mới là dấu hiệu, chưa phải kết luận):

- `hooks/hooks.json` gọi thẳng `python3` ở cả 5 hook. Windows thường không có `python3` trên
  PATH — chỉ có `python` hoặc trình khởi chạy `py`. Đây là chỗ nghi ngờ số một.
- `tdq_checkportable.py check` trên bundle agy đang tự nêu: `hooks.json` còn một dấu `~` chưa
  bung, mà agy cần đường dẫn tuyệt đối.
- Không có đường dẫn tuyệt đối cứng nào trong `scripts/` + `hooks/` (đếm được 0), và chỉ 1 chỗ
  đọc `sys.platform` — nghĩa là code hầu như không phân biệt hệ điều hành. Đó có thể là điểm
  mạnh (không có nhánh riêng cho macOS) hoặc điểm yếu (chưa từng xử lý khác biệt của Windows).

## Hiểu & kiến thức

### B0 — Kiểm kê năng lực

| Việc cần | Có sẵn thứ gì | Phán quyết |
|---|---|---|
| Kiểm bundle khớp manifest | `scripts/tdq_checkportable.py` | DÙNG — nhưng chính nó có 1 lỗi, xem phát hiện P2 |
| Dựng lại bundle từ một nguồn | `scripts/build_portable.py` | DÙNG — nơi sinh ra mọi `command` của hook |
| Rà tên lệnh/luật trong tài liệu | `scripts/doc_lint.py`, `scripts/i18n_check.py` | DÙNG |
| Quét mã nguồn theo cú pháp | `ast` của Python | DÙNG — đếm chính xác hơn grep |
| Tra tài liệu host | WebSearch | DÙNG — Codex CLI và agy đều đổi nhanh |
| Chạy thử trên Linux/Windows | không có máy | KHÔNG CÓ — user đã chọn 3a, kết luận dừng ở mức đọc mã |

### Số đo trên mã nguồn hiện tại

Quét bằng `ast` (không phải grep) trên toàn bộ `scripts/` + `hooks/`:

- `open()` chế độ văn bản KHÔNG khai `encoding=`: **0/0**. Đây là điểm mạnh thật — đọc file
  tiếng Việt trên Windows sẽ không vỡ vì code page.
- `subprocess` có `text=True` mà KHÔNG khai `encoding=`: **18 chỗ** (`tdq_team.py`,
  `tdq_finish.py`, `tdq_eval.py`, `tdq_bench.py`, `tdq_lsp.py`, `context_surface.py`,
  `skill_tokens.py`, `claude_export.py`). Windows giải mã theo code page của máy, không phải
  UTF-8 — đầu ra `git` có tiếng Việt (tên nhánh, câu commit) sẽ mojibake hoặc ném
  `UnicodeDecodeError`.
- Đường dẫn tuyệt đối cứng trong `scripts/` + `hooks/`: **0**. Nhánh riêng theo hệ điều hành:
  **1** (chỉ là một dòng ghi chú trong `claude_export.py`).
- Gọi stdlib chỉ có trên POSIX (`fcntl`, `pwd`, `os.fork`…): **0**.

### Bốn phát hiện, xếp theo mức nguy

**P1 — `python3` là tên lệnh không tồn tại trên Windows.** Cả 5 hook của Claude Code
(`hooks/hooks.json`), toàn bộ hook của bundle Codex (`.codex/hooks.json`) và 2 hook của bundle
agy (`antigravity_portable/hooks.json`) đều gọi thẳng `python3 …`. Windows chỉ có `python` hoặc
trình khởi chạy `py`; `python3` chỉ tồn tại nếu người dùng tự tạo bí danh, hoặc là cái stub của
Microsoft Store mở cửa hàng ứng dụng thay vì chạy Python. Hệ quả: mọi hook im lặng không chạy
hoặc chết ngay từ hook đầu tiên. Đây là lỗi chặn đường, không phải phiền toái.

**P2 — Cảnh báo "bundle dựng ở máy khác" là mã chết.** `tdq_checkportable.py:367` kiểm
`if "~" in noi_dung` trên TOÀN BỘ nội dung `hooks.json`. Chuỗi mô tả trong chính file đó có nhắc
`~/.gemini/config/config.json`, nên điều kiện luôn đúng, và nhánh `elif` ở dòng 369 — nhánh DUY
NHẤT phát hiện "bundle này được dựng dưới thư mục nhà của người khác" — không bao giờ chạy tới.
Đúng ca dùng mà user đang hỏi (mang sang máy khác) lại là ca cảnh báo không nổ. Kiểm chứng:
chạy `tdq_checkportable.py check --root antigravity_portable` trên bundle vừa dựng lại ở chính
máy này vẫn in NOTE "unexpanded `~`", trong khi `hooks.json` không còn `~` nào ở phần `command`.

**P3 — Bundle agy nướng cứng thư mục nhà của máy dựng.** `hooks.json` của agy đang chứa
`/Users/truongdinhquoc/.gemini/config/plugins/…`. Đây là quyết định CÓ CHỦ Ý và có ghi lý do
(`goc_agy_tuyet_doi`, dòng 882–891: agy không bung `~` trong `command`), kèm chỉ dẫn "dựng lại
tại máy đích thay vì copy bundle dựng sẵn". Nhưng chỉ dẫn đó nằm trong docstring của code, còn
`antigravity_portable/README.md` — thứ người ở máy khác thật sự đọc — không nói câu nào về
Windows, Linux hay việc bắt buộc dựng lại. Cộng với P2, người dùng ở máy khác không có gì cảnh
báo họ cả.

**P4 — `check`/`merge` chạy lệnh test bằng `shell=True`.** `tdq_team.py:896` giao lệnh trên
dòng `Test:` cho shell của hệ điều hành. Trên Windows đó là `cmd.exe`, nên một plan viết
`Test: \`python3 -m pytest …\`` — đúng khuôn mà mọi plan trong repo đang dùng — sẽ đỏ vì lý do
sai hoàn toàn (không có `python3`), và `merge` sẽ từ chối nhánh lành lặn. Cùng gốc với P1.

### Điểm chưa xác định, phải hỏi hoặc phải thử

- **Console encoding trên Windows khi stdout là pipe.** Cả 8 file trong `hooks/scripts/` đều
  chứa ký tự ngoài ASCII, và không chỗ nào trong repo đặt `PYTHONUTF8`/`PYTHONIOENCODING` hay
  gọi `sys.stdout.reconfigure`. Khi host chạy hook và bắt stdout bằng pipe, Python trên Windows
  dùng code page của locale chứ không phải UTF-8. Tôi CHƯA khẳng định được đây là lỗi thật vì
  chưa chạy trên Windows — cần một lần chạy thật để chốt. Đây là ứng viên số một cho danh sách
  "phải thử".
- **Đường dẫn plugin của agy.** Repo đang dùng `~/.gemini/config/plugins/<tên>/`. Tài liệu công
  khai tôi tra được hôm nay lại nói `~/.gemini/antigravity-cli/plugins/<tên>/hooks.json`
  (nguồn: [Where does Antigravity look for Hooks?](https://atamel.dev/posts/2026/07-16_where_agy_hooks/),
  [Plugins & Skills — Google Antigravity Docs](https://antigravity.google/docs/cli/plugins/)).
  Request 2026-09-03-1440 nói đường dẫn hiện tại đã đối chiếu với một bản cài agy 1.1.11 thật.
  Hai nguồn lệch nhau → phải xác minh lại, không tự sửa theo bài blog.
- **Codex trên Windows native.** Codex CLI 2026 chạy được PowerShell thuần với sandbox
  AppContainer (nguồn: [Windows sandbox — OpenAI](https://developers.openai.com/codex/windows)),
  nhưng có báo cáo hook Windows native làm hỏng dấu nháy JSON khi truyền qua tham số dòng lệnh
  (nguồn: [issue #2811](https://github.com/Yeachan-Heo/oh-my-codex/issues/2811)). Hook của TDQ
  đọc JSON từ stdin chứ không qua tham số, nên có thể không dính — nhưng đây là điều phải thử,
  không phải điều được suy ra.

### Lộ trình

Lane `full`, nhưng đầu ra là TÀI LIỆU chứ không phải mã (user chọn 4b: chỉ báo cáo, sửa để
request sau). Các phase chạy: `analyze` → `spec` → `diagram` → `plan` → `implement` → `qc` →
`report`. Phase `diagram` KHÔNG bỏ: luồng cần vẽ là "một hook chạy từ lúc host gọi tới lúc trả
quyết định", vì đó chính là luồng mà P1 và câu hỏi console encoding cùng cắt ngang; có sơ đồ thì
mới chỉ được chính xác chỗ nào đứt trên Windows.

Phase `implement` ở request này KHÔNG sửa mã sản phẩm. Nó sinh ra: (1) một báo cáo tương thích
đa nền tảng, xếp hạng phát hiện kèm cách sửa đề xuất cho từng cái; (2) một danh sách lệnh để
user tự chạy trên máy Linux và Windows, mỗi lệnh nêu rõ "thấy gì là đạt, thấy gì là hỏng".

## Hỏi đáp

**Hỏi 1 — chọn pipeline nào?** → **1a**: chế độ chuyên sâu (deep).

**Hỏi 2 — Windows tính tới đâu?** → **2b**: phải chạy được ở PowerShell thuần / cmd.exe, không
được viện tới Git Bash hay WSL. Đây là ràng buộc nặng nhất của request và là lý do P1 nhảy lên
mức chặn đường: dưới Git Bash thì `python3` thường có, dưới PowerShell thuần thì không.

**Hỏi 3 — có máy Linux/Windows thật không?** → **3a**: không có. Vậy mọi kết luận trong request
này dừng ở mức "đọc mã và đối chiếu tài liệu"; chỗ nào cần chạy thật mới chốt được thì phải nói
thẳng là chưa chốt, và đi vào danh sách lệnh để user tự chạy.

**Hỏi 4 — request này dừng ở đâu?** → **4b**: CHỈ BÁO CÁO. Không sửa mã sản phẩm trong request
này, kể cả những chỗ sửa rất nhanh như P2.
