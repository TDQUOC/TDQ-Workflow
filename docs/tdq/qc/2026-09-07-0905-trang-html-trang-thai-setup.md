# QC — Trang trạng thái setup TDQ-Workflow
Ngày: 2026-09-07 · Plan: ../plan/2026-09-07-0905-trang-html-trang-thai-setup.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Người chấm: agent `tdq-qc-tester` (độc lập, không viết code này). Mọi dòng dưới đây là lệnh
tự chạy lại, không lấy lại kết quả của người implement.

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Trang tự chứa | `python3 -m unittest discover -s tests -t tests -p 'test_setup_status_render.py' -k TuChua` + grep thẻ tải tài nguyên trên trang thật | `Ran 4 tests … OK`; 0 thẻ `<script/link/img/…>`, 0 `src=`/`href=`, 0 `@import`/`url(`, 1 `<style>` nội tuyến | PASS |
| Q2 | Không rò bí mật | `python3 -m unittest discover -s tests -t tests -p 'test_setup_status.py' -k CheBiMat`; `grep -c 'tvly-dev-[A-Za-z0-9]' setup_status.html` | `Ran 5 tests … OK`; grep trả `0`; nguồn thật CÓ khoá (`grep -c 'tvly-dev-' ~/.claude.json` = 2) nên hàng rào được kích hoạt thật, trang hiện `tavilyApiKey=***` | PASS |
| Q3 | Khai báo ≠ thực nhận | `python3 -m unittest discover -s tests -t tests -p 'test_setup_status_render.py' -k KhaiBao` | `Ran 4 tests … OK` (fixture 14 khai / 13 sống, nêu đúng tên server chết) | PASS |
| Q4 | Đủ 4 khối | `grep -c 'data-khoi=' setup_status.html` | `4` | PASS |
| Q5 | Trung thực khi thiếu | `PATH=/usr/bin:/bin python3 scripts/setup_status.py; echo $?` | `EXIT=0`, vẫn ra file; trang có 3 ô `chưa cài` + 2 ô `không đọc được` | PASS |
| Q6 | Giới hạn skill built-in | `grep -c 'skill built-in' setup_status.html` | `1` | PASS |
| Q7 | Log service | `TDQ_LOG=0 python3 scripts/setup_status.py 2>…; wc -c` và diff HTML | `0` byte stderr; mặc định 28 dòng log, 20 dòng có ISO timestamp; HTML hai lần chạy giống nhau sau khi chuẩn hoá số đo ms (diff = 0 dòng) | PASS |
| Q8 | Không bẩn git | `git status --porcelain \| grep -c setup_status.html` | `0` | PASS |
| Q9 | Test tất định | `PATH=/usr/bin:/bin python3 -m unittest discover -s tests -t tests -p 'test_setup_status_render.py'` | `Ran 15 tests … OK` với agent-lsp/lumen/ollama/graphify đều absent | PASS |
| Q10 | Không hồi quy | `python3 -m unittest discover -s tests -t tests -p 'test_*.py'` | `Ran 1583 tests … FAILED (failures=290, errors=4, skipped=14)` — đúng bằng nền | PASS |
| Q11 | QC độc lập | — | LEADER TỰ CHẤM (mục này là kết luận về chính báo cáo này) | — |
| QC-F1 | Suite tổng | như Q10 | 1583 ca · failures=290 · errors=4 · skipped=14 — bằng đúng nền `290/4`; 0 ca đỏ mang tên `setup_status` | PASS |
| QC-F2 | Hồi quy vùng chạm | unittest discover từng module | `test_setup_status.py` Ran 35 OK · `test_setup_status_render.py` Ran 15 OK · `test_bao_cao_da_nen_tang.py` Ran 13 OK · `test_tdq_lsp.py` Ran 49 OK · `test_skill_inventory.py` Ran 24 OK · `test_context_surface.py` Ran 15 OK · KHÔNG CÓ TEST: `.gitignore` | PASS |
| QC-F3 | Ràng buộc kiến trúc | 4 lệnh, xem §Bằng chứng | file mới đều trong `scripts/` · không import `hooks/` · state chỉ đọc (`sha`+`mtime` của `state.json` không đổi sau khi chạy) · docstring/log tiếng Anh, chữ HTML tiếng Việt | PASS |
| QC-F4 | Clean code | — | LEADER TỰ CHẤM | — |
| Đ1 | Đối chiếu state | `python3 scripts/tdq_state.py get` vs khối state trên trang | slug `2026-09-07-0905-trang-html-trang-thai-setup` · lane `full` · phase `qc` · `implement_mode main` — khớp 8/8 khoá | PASS |
| Đ2 | Đối chiếu 7 bậc | `python3 scripts/tdq_lsp.py check` vs bảng bậc trên trang | 7/7 bậc ĐẠT ở cả hai nơi, chuỗi chi tiết từng bậc trùng nguyên văn | PASS |
| BM | Bảo mật repo public | 5 lệnh grep, xem §Bằng chứng | 0 chuỗi `tvly`, 0 `sk-…`, 0 `ghp_`, 0 `Bearer`, 0 `key=`/`token=` chưa che; file nằm ngoài git | PASS |

## Bằng chứng

### Lỗi cú pháp trong chính các dòng DoD (không phải lỗi code)

Repo này KHÔNG có pytest và test import `from helper import ROOT`, nên dạng
`python3 -m unittest tests.test_xxx` không chạy được. Chạy nguyên văn Q1/Q2/Q3/Q9:

```
ModuleNotFoundError: No module named 'helper'
FAILED (errors=1)
```

Thêm nữa, các mẫu `-k` trong DoD không khớp tên ca nào — lớp test đặt tên CamelCase:

```
python3 -m unittest discover -s tests -t tests -p 'test_setup_status_render.py' -k tu_chua
Ran 0 tests in 0.000s
NO TESTS RAN
```

Bảng sửa (đã chạy lại bằng bản sửa và chấm theo kết quả đó):

| DoD | Lệnh sai | Lệnh đúng |
|---|---|---|
| Q1 | `python3 -m unittest tests.test_setup_status_render -k tu_chua` | `python3 -m unittest discover -s tests -t tests -p 'test_setup_status_render.py' -k TuChua` |
| Q2 | `python3 -m unittest tests.test_setup_status -k mask` | `… -p 'test_setup_status.py' -k CheBiMat` |
| Q3 | `python3 -m unittest tests.test_setup_status_render -k khai_bao` | `… -p 'test_setup_status_render.py' -k KhaiBao` |
| Q9 | `python3 -m unittest tests.test_setup_status_render` | `… -p 'test_setup_status_render.py'` |
| T5.2 + plan | `python3 scripts/tdq_state.py show` | `python3 scripts/tdq_state.py get` — `show` KHÔNG tồn tại: `Invalid command: show` |

Các dòng `-k` trong T1.1–T1.4, T2.2 của plan hỏng y hệt.

### Q1
```
Ran 4 tests in 0.000s
OK
```
Trang thật: `grep -coE '<(script|link|img|iframe|source|video|audio|embed|object)\b'` → `0`;
`grep -coE '(src|href)='` → `0`; `grep -coE '@import|url\('` → `0`; `grep -c '<style>'` → `1`.

### Q2
```
Ran 5 tests in 0.000s
OK
```
Trên trang sinh thật: `grep -c 'tvly-dev-[A-Za-z0-9]' setup_status.html` → `0`.
Khối MCP hiện `https://mcp.tavily.com/mcp/?tavilyApiKey=*** (HTTP)` cho cả `tavily-primary`
và `tavily-backup` — che đúng, giữ tên tham số. Nguồn thật có khoá (đếm được 2 chỗ trong
`~/.claude.json`), nên đây là hàng rào chạy thật chứ không phải PASS rỗng.

### Q3
```
Ran 4 tests in 0.000s
OK
```

### Q4 / Q6
```
grep -c 'data-khoi=' setup_status.html      → 4
grep -c 'skill built-in' setup_status.html  → 1
```

### Q5
```
PATH=/usr/bin:/bin python3 scripts/setup_status.py
EXIT=0
/Users/tdq/Documents/ForAgentCode/TDQ-Workflow/setup_status.html
```
`thu_dependency()` khi thiếu binary trả `co=false`, `ban="chưa cài"` kèm `goi_y` cho cả 4 công
cụ; renderer đưa `goi_y` vào cột ghi chú. Không ném exception.

### Q7
```
TDQ_LOG=0 … ; wc -c < log0.txt   → 0
mặc định: 28 dòng, 20 dòng có tiền tố ISO [YYYY-MM-DDTHH:MM:SS+07:00]
```
Mẫu log (đủ độ chi tiết debug — nguồn, mã thoát, thời gian):
```
[2026-09-07T10:44:13+07:00] setup_status: claude mcp list: rc=0 in 4.7s
[2026-09-07T10:44:22+07:00] setup_status: wrote …/setup_status.html in 9.9s
```
HTML hai lần chạy: khác nhau 8 dòng diff, toàn bộ nằm ở số đo median của hook (đo sống,
22.9ms ↔ 23.0ms). Hai lần chạy CÙNG bật log cũng khác đúng 8 dòng như vậy → không phải hiệu
ứng của `TDQ_LOG`. Sau khi chuẩn hoá `…ms` và timestamp: `diff … | wc -l` → `0`.

### Q8 / Bảo mật
```
git status --porcelain | grep -c setup_status.html   → 0
grep -c  'tvly-dev-[A-Za-z0-9]' setup_status.html    → 0
grep -ci 'tvly'                 setup_status.html    → 0
grep -c  'sk-[A-Za-z0-9]\{10\}' setup_status.html    → 0
grep -cE 'ghp_[A-Za-z0-9]{10}|github_pat_'           → 0
grep -ci 'bearer '                                    → 0
grep -oiE '(api)?key=[^&"< ]{4,}' | wc -l             → 0 (chỉ còn dạng ***)
```
KHÔNG có giá trị khoá thật nào được chép vào file này.

### Q9
```
PATH=/usr/bin:/bin  (agent-lsp absent · lumen absent · ollama absent · graphify absent)
Ran 15 tests in 0.001s
OK
```

### Q10 / QC-F1
```
Ran 1583 tests in 81.647s
FAILED (failures=290, errors=4, skipped=14)
```
Bằng đúng nền `failures=290, errors=4`. 4 error đều là ca cũ (`test_doc_dup`, `test_token_audit`,
2 ca loader `test_check_canvas_layout`/`test_team_chong_conflict`).
`grep -cE '^(FAIL|ERROR): .*setup_status'` → `0`.

### QC-F2
```
test_setup_status.py         Ran 35 tests  OK
test_setup_status_render.py  Ran 15 tests  OK
test_bao_cao_da_nen_tang.py  Ran 13 tests  OK
test_tdq_lsp.py              Ran 49 tests  OK
test_skill_inventory.py      Ran 24 tests  OK
test_context_surface.py      Ran 15 tests  OK
KHÔNG CÓ TEST: .gitignore
```

### QC-F3 — ràng buộc kiến trúc (§5 spec)
1. "File code MỚI nằm trong `scripts/` hoặc `hooks/`" → `ls scripts/setup_status.py
   scripts/setup_status_render.py` đều tồn tại, không có file code mới ở nơi khác. **ĐẠT**
2. "`scripts/` không import `hooks/`" → toàn bộ import của 2 file:
   `context_surface, datetime, html, json, os, re, setup_status_render, shutil,
   skill_inventory, subprocess, sys, tdq_lsp, tdq_state`. Không có `hooks`. **ĐẠT**
   (grep bắt được chữ "hook" chỉ trong comment, không phải câu import.)
3. "Chỉ `tdq_state.py` được ghi `state.json`" → chạy `python3 scripts/setup_status.py` rồi so
   `shasum` và `stat -f %m` của `docs/tdq/state.json`: `sha before==after: YES; mtime same: YES`.
   Code đọc bằng `tdq_state.load(ROOT, heal=False)` (dòng 279), lệnh ghi duy nhất là
   `f.write(html)` vào `setup_status.html` (dòng 470). **ĐẠT**
4. "docstring/log trong `scripts/` tiếng Anh, chữ user theo `doc_lang`" → quét AST: mọi docstring
   module/hàm viết tiếng Anh; 5 chỗ có dấu tiếng Việt đều là trích DẪN nguyên văn chuỗi hiển thị
   (`"chưa cài"`, `"không đọc được"`) nằm trong câu tiếng Anh. Log stderr 100% tiếng Anh. Chữ
   trên HTML tiếng Việt. **ĐẠT**

### Không placeholder
```
grep -nEi 'TODO|FIXME|XXX|placeholder|NotImplemented' scripts/setup_status*.py tests/test_setup_status*.py
(không dòng nào)
```

### Đ1 — đối chiếu state
`python3 scripts/tdq_state.py get` (lưu ý: plan ghi `show`, lệnh đó không tồn tại):
```
"active_request": "2026-09-07-0905-trang-html-trang-thai-setup"  "lane": "full"  "phase": "qc"
"implement_mode": "main"  "loai_request": "feature"  "nhanh_request": "feature/trang-trang-thai-setup"
```
Khối state trên trang in đúng 8 khoá đó, kể cả `spec_approved`/`plan_approved` = True. KHỚP.

### Đ2 — đối chiếu 7 bậc
`python3 scripts/tdq_lsp.py check` → `Tổng: 7/7 bậc ĐẠT`. Bảng "Thang 7 bậc của agent-lsp" trên
trang có đúng 7 hàng, cả 7 đều `ĐẠT`, chi tiết trùng nguyên văn (bậc 1 `0.19.2`, bậc 2
`4 server đã đăng ký`, bậc 3 `đủ cho 2 ngôn ngữ: HTML, Python`, bậc 4 `1 mục trong allow`,
bậc 5 `ollama đang chạy, có qwen3-embedding:0.6b`, bậc 6 `không plugin nào chèn thứ tự tìm kiếm
khác`, bậc 7 `2 ngôn ngữ đều có file mốc ở gốc dự án`). KHỚP.

## Thăm dò ngoài happy path (không thuộc DoD, ghi lại cho leader)

### P1 — `mask_secrets()` chỉ che tham số query-string (TRUNG BÌNH, tiềm ẩn)
`_RE_THAM_SO` (scripts/setup_status.py:86-87) bắt buộc có `?` hoặc `&` đứng trước, nên các dạng
khoá khác đi thẳng vào HTML. Chứng minh bằng khoá GIẢ:
```
'/usr/bin/mcpx --api-key=<khoá giả> - Connected'  → KHÔNG che
'/usr/bin/mcpx --token <khoá giả>'                → KHÔNG che
'TAVILY_API_KEY=<khoá giả> /usr/bin/mcpx'         → KHÔNG che
```
Hôm nay trang KHÔNG rò (Q2 PASS thật) vì server Tavily trên máy này dùng URL query-string.
Nhưng cột "Địa chỉ / lệnh" lấy nguyên dòng `claude mcp list`, mà server MCP kiểu stdio rất hay
truyền khoá bằng cờ `--api-key=` hoặc biến môi trường. Spec §5 hứa "che mọi giá trị đứng sau
`key=`/`apikey=`/`token=`" — hàng rào hiện hẹp hơn lời hứa.

### P2 — cột "thực nhận" bỏ qua dòng `[error]` của chính `agent-lsp doctor` (TRUNG BÌNH)
Chạy lại doctor với đúng `args`+`env` của server `lsp`: 14 dòng `Status:  ok`, trang ghi
"khai báo 14 · khởi động được 14". Nhưng cùng output đó có 3 dòng:
```
[error] LSP server omnisharp … exited with error
[error] LSP server vscode-eslint-language-server … exited with error after 1s
[error] LSP server yaml-language-server … exited with error
```
và một lần chạy trả `rc=2` (lần khác `rc=0` → doctor chập chờn). Trang không đọc `returncode`
(`_run_tool` lưu vào khoá `ma` nhưng `_doc_doctor` không dùng). Spec §3 lấy đúng ca "csharp-ls
khai đủ 14 nhưng chết ngay lần hỏi đầu" làm lý do tồn tại của cột này, nên bỏ qua 3 dòng
`[error]` làm cột "thực nhận" lạc quan hơn sự thật.

### P3 — lệnh cài agent-lsp gợi ý SAI (THẤP)
`scripts/setup_status.py:57` ghi `npm install -g @agent-lsp/cli`. Lệnh đúng nằm ngay trong repo:
`scripts/tdq_lsp.py:38` `INSTALL_AGENT_LSP = "curl -fsSL https://raw.githubusercontent.com/
blackwell-systems/agent-lsp/main/install.sh | sh"`, đúng như `skills/tdq-lsp-setup/SKILL.md`
bước 1. Máy trắng làm theo trang sẽ cài hụt. Cũng là lặp hằng số (DRY).

### P4 — renderer vỡ khi dict sai kiểu (THẤP, không chạm spec)
`render({})` và `render({'workflow':None,…})` đều ra trang 4 khối bình thường (tốt). Nhưng
`render({'workflow':123})` ném `AttributeError: 'int' object has no attribute 'get'`. Chỉ
`thu_tat_ca()` cấp dữ liệu và hình dạng đã cố định bởi `khung_du_lieu()`, nên không phải lỗi
thực thi — ghi lại cho đầy đủ.

### P5 — thoát HTML đúng
`render()` với tên server `<script>alert(1)</script>` → chuỗi thô không xuất hiện trong HTML.

### P6 — nguồn hỏng vẫn trung thực
Trỏ `CAU_HINH_CLAUDE` vào file rác và vào file không tồn tại:
```
không đọc được …/bad.json: Expecting value: line 1 column 1 (char 0)
không đọc được /no/such/file.json: [Errno 2] No such file or directory: …
```
Không ném exception, không đoán giá trị.

## Kết luận

**PASS** — Q1–Q10 PASS, QC-F1/F2/F3 PASS, hai mục đối chiếu (state, 7 bậc) KHỚP, kiểm bảo mật
sạch (0 khoá rò, file ngoài git).

Cần leader xử lý trước khi đóng request:
1. Sửa 5 dòng lệnh sai cú pháp trong plan (bảng ở §Bằng chứng) — chúng đang FAIL/NO-TESTS-RAN
   khi chạy nguyên văn, dù code xanh.
2. P1 (mở rộng `mask_secrets` sang dạng cờ và biến môi trường) và P2 (đọc `[error]`/returncode
   của doctor) — cả hai đụng đúng lời hứa của spec.
3. P3 — sửa lệnh cài agent-lsp về `INSTALL_AGENT_LSP` của `tdq_lsp.py`.

Q11 và QC-F4: LEADER TỰ CHẤM.

---

# QC vòng 2 — sau khi leader xử lý các mục agent nêu

Người chấm: leader (main mode). Vòng 1 ở trên PASS toàn bộ DoD; vòng này chấm lại sau 6 task
fix `QC1.1`–`QC1.6` trong plan.

## Xử lý 4 khuyết tật agent nêu

| Khuyết tật agent nêu | Phán quyết | Việc đã làm |
|---|---|---|
| P1 — `mask_secrets()` chỉ che query string, cờ CLI và biến môi trường lọt | ĐÚNG | QC1.1: thêm `_RE_CO_LENH` và `_RE_BIEN_MT`; giá trị dùng `[^\s&]+` chứ không `\S+` để không nuốt tham số kế; regex biến môi trường không bỏ qua hoa/thường (tên biến viết HOA) để không đụng `apiKey=` vốn đã do lớp query-string lo. 3 ca mới |
| P2 — cột "thực nhận" bỏ qua `[error]` và returncode của doctor | **BÁC một nửa** | Đo 3 lần liên tiếp: `Summary: 14 ok, 0 failed` và `rc=0` đứng yên, còn dòng `[error] ... exited with error after 0s` mỗi lần một tập server khác nhau (4 → 7 → 5 dòng, `pyright`/`clangd`/`omnisharp`/`css`… đổi liên tục). Đó là nhiễu lúc đóng tiến trình, đếm là "chết" sẽ báo hỏng SAI. Thay bằng QC1.2: đối chiếu chéo `Summary` + returncode với số đếm theo từng server, lệch thì cảnh báo; và một dòng trên trang nói rõ dòng `[error]` không tính là chết |
| P3 — lệnh cài agent-lsp sai (`npm install -g @agent-lsp/cli`) | ĐÚNG | QC1.3: lấy `tdq_lsp.INSTALL_AGENT_LSP`, thêm ca ghim để không chép tay lại |
| P4 — `render()` ném `AttributeError` khi dict sai kiểu | ĐÚNG | QC1.4: `_dict()`/`_danh_sach()` chặn ở 4 hàm dựng khối |

Thêm 5 dòng lệnh kiểm sai cú pháp trong plan (agent nêu) đã sửa: Q1/Q2/Q3/Q9 đổi sang dạng
`discover`, mẫu `-k` sửa hoa/thường (`TuChua`, `CheBiMat`, `KhaiBaoVaThucNhan`), `tdq_state.py
show` → `get`.

## Bug do chính bản vá sinh ra, QC bắt được (QC1.6)

QC1.2 lần đầu dùng `re.search` với regex neo `^` mà không có cờ `re.M`, nên chỉ khớp khi
`Summary:` nằm đúng đầu chuỗi. Fixture test lại đúng như vậy → **test xanh giả**, còn trang
sinh thật hiện dòng cảnh báo sai "không thấy dòng Summary của `agent-lsp doctor` để đối chiếu".
Bắt được vì có bước sinh trang thật rồi soi lại, chứ không tin test. Đã thêm `re.M` và một ca
đặt `Summary` ở cuối output; trang sinh lại: không còn cảnh báo.

## Chấm lại DoD sau fix

| # | Lệnh | Kết quả | PASS/FAIL |
|---|---|---|---|
| Q1 | `... -p 'test_setup_status_render.py' -k TuChua` | `Ran 4 tests … OK` | PASS |
| Q2 | `... -p 'test_setup_status.py' -k CheBiMat` | `Ran 8 tests … OK` (5 → 8 ca) | PASS |
| Q3 | `... -p 'test_setup_status_render.py' -k KhaiBaoVaThucNhan` | `Ran 6 tests … OK` (4 → 6 ca) | PASS |
| Q4 | `grep -c 'data-khoi=' setup_status.html` | `4` | PASS |
| Q5 | `PATH=/usr/bin:/bin python3 scripts/setup_status.py; echo $?` | `exit=0` | PASS |
| Q6 | `grep -c 'skill built-in' setup_status.html` | `1` | PASS |
| Q7 | `TDQ_LOG=0 ... 2>/tmp/tdq-log0.txt >/dev/null; wc -c < /tmp/tdq-log0.txt` | `0` | PASS |
| Q8 | `git status --porcelain \| grep -c setup_status.html` | `0` | PASS |
| Q9 | `... -p 'test_setup_status_render.py'` | `Ran 21 tests … OK` (15 → 21 ca) | PASS |
| Q10 | `python3 -m unittest discover -s tests -t tests -p 'test_*.py'` | `Ran 1599 tests … FAILED (failures=290, errors=4, skipped=14)`; `diff` danh sách ca đỏ với nền = rỗng | PASS |
| Q11 | chính file này | vòng 1 PASS toàn bộ + vòng 2 xử lý hết mục agent nêu | PASS |
| BM | `grep -cE 'tvly-dev-[A-Za-z0-9]\|sk-[A-Za-z0-9]{10}\|ghp_[A-Za-z0-9]' setup_status.html` | `0`; trang hiện `tavilyApiKey=***` | PASS |

Đối chiếu lại trên trang sinh thật sau fix: state `2026-09-07-0905-trang-html-trang-thai-setup ·
full · qc` khớp `tdq_state.py get`; 7/7 bậc khớp `tdq_lsp.py check`; khối LSP ghi `Khai báo 14
language server · khởi động được 14`, không còn dòng cảnh báo sai.

## QC-F4 — clean code (leader tự chấm)

| Câu hỏi | Trả lời | Ghi chú |
|---|---|---|
| SRP — mỗi hàm một lý do đổi? | **có** | Lớp thu và lớp kết xuất tách hẳn hai file; trong lớp thu mỗi nguồn một hàm `thu_*`/`_nguon_*`, mỗi bộ đọc output một hàm `_doc_*`; `_doi_chieu_doctor` tách riêng khỏi `_doc_doctor` đúng vì nó là việc khác (đối chiếu, không phải phân tích) |
| OCP — thêm một ca là thêm một dòng dữ liệu? | **có, sau khi sửa** | Ban đầu KHÔNG: thêm khối cho trang phải sửa cả `KHOI` lẫn thân `render()`. QC1.5 gộp thành bảng 4 cột (mã, tiêu đề, khoá dữ liệu, hàm dựng); có ca test vá `KHOI` thêm một dòng và khẳng định trang ra 5 khối mà `render()` không đổi. Thêm công cụ dependency và thêm từ khoá bí mật vốn đã là một dòng dữ liệu |
| LSP — mọi nhánh `return` cùng kiểu, cùng hợp đồng lỗi? | **có** | Không có kế thừa. `_run_tool` luôn trả dict 8 khoá kể cả khi thiếu binary / quá hạn / `OSError`; `_thu_mot_nguon` luôn trả đúng kiểu mặc định của nguồn; `_doi_chieu_doctor` luôn trả `str` (`""` = khớp) |
| ISP — tham số nào cũng được dùng? | **có** | Đã soi lại `_run_tool(binary, args, goi_y, timeout, env)` — cả 5 đều dùng; `render(du_lieu)` một tham số |
| DIP — đi qua cửa chung sẵn có? | **có, sau khi sửa** | Mọi lệnh ngoài đi qua `_run_tool`; state đọc qua `tdq_state`, skill qua `skill_inventory`, hook qua `context_surface`, bậc qua `tdq_lsp` — không tự dựng lại. Vi phạm duy nhất là lệnh cài agent-lsp chép tay, đã sửa ở QC1.3 để lấy `tdq_lsp.INSTALL_AGENT_LSP` |

Không câu nào "không" còn lại. Hai câu từng "không" (OCP, DIP) đã sửa CODE, không sửa câu trả lời.

`ruff`/lint tự động: **chưa kiểm** — máy này chưa cài `ruff`, không ghi PASS cho thứ chưa chạy.

## Kết luận vòng 2

**PASS toàn bộ** — Q1–Q11, QC-F1..F4, hai mục đối chiếu và kiểm bảo mật đều PASS. Suite 1599 ca,
`failures=290 errors=4` bằng đúng nền, `diff` danh sách ca đỏ với nền rỗng. 6 task fix
`QC1.1`–`QC1.6` đã tick trong plan.

Nợ kỹ thuật ghi vào báo cáo: `.gitignore` KHÔNG CÓ TEST (chỉ được kiểm gián tiếp qua Q8), và
`ruff` chưa cài nên chưa có lint tự động.
