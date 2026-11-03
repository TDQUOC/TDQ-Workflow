# SPEC — Sửa bộ workflow TDQ chạy đủ tính năng trên Windows

Ngày: 2026-09-20 · Bản: 1.1 · Brief: ../brief/2026-09-20-1823-sua-tdq-chay-windows.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT LẠI (bản 1.1 — đổi cách tiếp cận N2)

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

- Mục tiêu: bộ TDQ-Workflow chạy đủ tính năng trên Windows 11 — cả 6 hook sống, mọi script in
  được tiếng Việt, mọi lệnh mà hook và skill đưa ra đều gõ được trên máy Windows, và bộ test
  1907 ca không còn ca nào đỏ vì nền tảng.
- Trong phạm vi:
  - N1 — encoding stdout/stderr cho 40 entry point của `scripts/` và `hooks/scripts/`.
  - N2 — tên lệnh interpreter: `hooks/hooks.json` sinh lại theo hệ điều hành; máy Windows cài
    một shim `python3` để 96 chuỗi lệnh trong `skills/**/*.md` chạy được nguyên văn; hook in
    thêm một dòng quy ước làm lưới an toàn khi máy chưa cài shim.
  - N3 — test harness set `USERPROFILE` cạnh `HOME` ở 6 file test.
  - N4 — chuẩn hoá dấu chéo ở biên xuất của `kiem_no_marker`, `context_surface` và sổ turn.
  - Dọn test đỏ: cài `codex`, `graphify`, `anthropic-tokenizer`, `pytest` rồi chạy thật.
  - `docs/tdq/audit/skill-index.json` hết mang đường dẫn tuyệt đối của một máy.
  - Ba drift: `docs/claude-md-mau.md` vượt trần 3500 byte · `index.md` nhắc thừa `bash.md` ·
    `setup_status` trả model khác test mong.
  - Layout mới của Claude Code: `~/.claude/skills/synced/<uuid>/<tên>/SKILL.md` và
    `~/.claude/plugins/` không còn `installed_plugins.json`.
  - Hai cải thiện lớp tìm kiếm theo phán quyết `1a`: thêm `.lumenignore`, và thêm luật
    "không mở file trước khi hỏi `find_references`".
  - Bump version, ghi CHANGELOG, dựng lại 3 bundle portable.
- NGOÀI phạm vi:
  - Đổi thứ hạng các lớp trong bảng `uu-tien-tim-kiem.md` — phán quyết `1a` giữ nguyên bảng.
  - Hỗ trợ PowerShell thuần làm shell chạy hook: chưa có bằng chứng host dùng shell nào, và
    cách sinh lại `hooks.json` theo hệ đã tránh được câu hỏi đó.
  - Sửa `agent-lsp` hay `lumen` — công cụ ngoài, chỉ cấu hình chứ không vá.
  - WSL và Windows ARM64.
  - Sửa 96 chuỗi `python3` trong `skills/**/*.md`: bản 1.0 chọn cách này, bản 1.1 bỏ — lý do
    ở §3.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | tài liệu hook Windows đã tra ở analyze; phần còn lại chỉ thực nghiệm mới chốt được |
| Interview | CÓ | đã chạy 3 vòng, hết câu đổi được kết quả |
| spec | CÓ | khung bất biến, và việc này đụng cả ba tầng luật, CLI, hook |
| plan | CÓ | khung bất biến; mỗi task một test |
| implement | CÓ | khung bất biến |
| Chia việc cho subagent | BỎ | N1 chạm gần hết `scripts/` và `hooks/`, cắt song song là chuốc conflict |
| QC độc lập (agent) | CÓ | mốc đỏ xanh phải do một lượt chạy độc lập xác nhận |
| Rà soát sâu | CÓ | N2 chạm gần hết tầng luật và bắt dựng lại 3 bundle portable |
| report | CÓ | khung bất biến |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Module ép UTF-8 dùng chung | `scripts/utf8_io.py` | gọi hai lần liên tiếp không đổi thêm trạng thái, và không ném lỗi khi luồng đã là UTF-8 |
| 2 | Mọi entry point ép UTF-8 | 40 file có `__main__` trong `scripts/`, `hooks/scripts/` | chạy từng file dưới code page cp1252, không file nào ném `UnicodeEncodeError` |
| 3 | Sáu hook sống trên Windows | `hooks/hooks.json` | mỗi hook nhận JSON qua stdin, thoát 0, in đúng khối `[TDQ:*]` của phase hiện tại |
| 4 | Lệnh trong tầng luật gõ được trên Windows | `scripts/tdq_ten_lenh.py`, `scripts/tdq_checkportable.py`, `hooks/scripts/session_start.py` | trên Windows đã cài shim, gõ nguyên văn `python3 scripts/tdq_state.py next` chạy được ở cả ba shell; chưa cài shim thì header hook in dòng quy ước |
| 5 | Test harness chạy đúng trên Windows | 6 file test set `HOME` | test quét vào thư mục tạm, không chạm `~/.claude` thật của máy |
| 6 | Biên xuất dùng dấu chéo xuôi | `scripts/kiem_no_marker.py`, `scripts/context_surface.py`, sổ turn | đường dẫn in ra và ghi ra giống nhau trên cả ba hệ |
| 7 | Kho skill-index hết gắn với một máy | `docs/tdq/audit/skill-index.json` | dựng lại trên máy khác không sinh diff đường dẫn |
| 8 | Bộ test không còn ca đỏ vì nền tảng | `tests/` | một lượt chạy đầy đủ trên Windows: 0 fail, 0 error |
| 9 | Kiểm kê năng lực thấy skill trên đĩa | `scripts/skill_inventory.py`, `scripts/tdq_lsp.py` | bảng B0 liệt kê được skill ở layout `synced/`, không còn dòng báo rỗng |
| 10 | Lớp tìm kiếm bớt nhiễu và có luật dùng đúng | `.lumenignore`, `skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md` | kết quả lumen không còn bản sao portable; luật mới có đủ ba mục |
| 11 | Ba bundle portable khớp nguồn | `portable_claude/`, `portable_codex/`, `antigravity_portable/` | bản dựng lại được công cụ kiểm portable báo sạch |
| 12 | Phát hành | `.claude-plugin/plugin.json`, `CHANGELOG.md` | version tăng, CHANGELOG có mục mới, file vẫn dưới trần 500 dòng |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| M1 runtime | `scripts/`, `hooks/` | không | 1, 2, 3, 6, 9 |
| M2 luật | `skills/` | M1 | 10 |
| M3 test | `tests/` | M1, M2 | 5, 8 |
| M4 bundle | `portable_claude/`, `portable_codex/`, `antigravity_portable/` | M1, M2 | 11 |
| M5 cấu hình và phát hành | `.gitignore`, `.lumenignore`, `docs/claude-md-mau.md`, `docs/tdq/audit/skill-index.json`, `.claude-plugin/plugin.json`, `CHANGELOG.md` | M1 | 7, 10, 12 |

## 3. Cách tiếp cận & lý do

- Chọn (N1): một module `scripts/utf8_io.py` ép `sys.stdout` và `sys.stderr` sang UTF-8 với
  `errors="replace"`, nạp vào hai chỗ dùng chung là `scripts/tdq_state.py` và
  `hooks/scripts/_common.py`, rồi thêm một dòng import vào 22 entry point còn lại.
- Vì: đo được 18 trong 40 entry point đã đi qua một trong hai file đó, nên hai chỗ nạp gánh
  được 45 phần trăm mà không đụng file nào khác. Dùng `errors="replace"` để một ký tự lạ không
  giết hook, vì hook chết là mất cả lượt làm việc.
- Đã loại: đặt biến môi trường `PYTHONUTF8=1` — vì nó nằm ngoài repo, mỗi máy phải tự đặt, và
  đo được rằng tiến trình con bị tước biến thì đỏ trở lại.
- Đã loại: viết `sys.stdout.reconfigure` thẳng vào 40 file — 40 bản chép tay sẽ lệch nhau.

- Chọn (N2, `hooks.json`): giữ cơ chế `build_portable.py --sinh-hook-claude --he-dich <os>`
  sinh lại theo hệ, đúng phán quyết `1b` của user.
- Vì: `hooks.json` không có trường điều kiện theo hệ điều hành, và tài liệu Claude Code không
  nói Windows chạy shell form bằng shell nào. Một chuỗi có `||` chạy được trên `cmd.exe` nhưng
  là lỗi cú pháp trên PowerShell 5.1.
- Đã loại: shim `py -3 ... || python3 ...` — đặt cược vào shell chưa xác minh được.
- Đã loại: trỏ thẳng vào đường dẫn `.py` rồi dựa vào shebang — đo trên máy user thấy `.py`
  không có file association và `.PY` không nằm trong `PATHEXT`, nên chết trên Windows.

- Chọn (N2, 96 chuỗi tĩnh): KHÔNG sửa chuỗi nào. Máy Windows cài một shim `python3` đặt ở thư
  mục đứng đầu PATH, cộng một dòng quy ước in trong header hook làm lưới an toàn khi máy chưa
  cài shim. Đây là phán quyết `1c` của user ở vòng 4.
- Vì: bản 1.0 chọn placeholder do hook bung ra, và cách đó KHÔNG thực hiện được. Claude Code đọc
  thẳng `skills/**/SKILL.md` từ đĩa để nạp vào context; hook chỉ chèn thêm được context ở
  `SessionStart` và `UserPromptSubmit`, không rewrite được nội dung file mà model đọc. Placeholder
  vì thế phải do chính model tự thay — đúng thứ soul nguyên tắc 3 cấm khi viết cho model yếu nhất.
- Đo trước khi chọn, trên máy user: shim gồm hai file một dòng đặt tại thư mục đứng đầu PATH làm
  `python3 --version` chạy đúng ở Git Bash, `cmd.exe` và PowerShell, và lệnh thật
  `python3 scripts/tdq_state.py get phase` chạy nguyên văn không sửa gì.
- Đã loại: đổi 96 chuỗi sang placeholder — không thực hiện được như trên, lại chạm gần hết tầng
  luật và bắt dựng lại 3 bundle portable.
- Đã loại: chỉ thêm một dòng nhắc, không shim — để lại 96 chỗ mà model phải tự quy đổi.

- Chọn (N3): set cả `HOME` và `USERPROFILE` trong harness test.
- Vì: `ntpath.expanduser` không đọc `HOME`; chỉ set `HOME` là test quét vào `~/.claude` thật.

- Chọn (N4): chuẩn hoá sang dấu chéo xuôi tại biên xuất, theo đúng lối đã có sẵn trong repo ở
  `build_portable.py` và `claude_export.py`.
- Vì: hai cổng chặn `edit_gate` và `stop_gate` đã dùng `os.sep` nhất quán nên không hỏng; chỗ
  lệch chỉ nằm ở chuỗi in ra và chuỗi ghi vào sổ.

- Chọn (lớp tìm kiếm): thêm `.lumenignore` loại ba bundle portable, và thêm luật cấm mở file
  trước khi hỏi `find_references`.
- Vì: đo được trên máy user — bỏ bản sao portable thì mục tiêu thật lên hạng 4 và hạng 1, còn
  mở sẵn file làm `find_references` rơi từ 6 file xuống 1 file.

## 3b. Năng lực & công cụ

Chép từ brief mục `### Năng lực dùng được`. Phân vân → DÙNG.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | skill khung đang chạy, đã mở request và chạy analyze |
| tdq-spec | plugin:tdq-workflow | NỀN | skill khung đang chạy, đang viết chính file này |
| tdq-plan | plugin:tdq-workflow | NỀN | skill khung sẽ chạy ngay sau cổng duyệt spec |
| tdq-build | plugin:tdq-workflow | NỀN | skill khung của implement, QC và report |
| tdq-conventions | plugin:tdq-workflow | NỀN | luật chung mọi phase đều nạp |
| tdq-lsp-setup | plugin:tdq-workflow | DÙNG | đầu ra 10 — sửa `uu-tien-tim-kiem.md` và cấu hình lumen |
| tdq-lean | plugin:tdq-workflow | DÙNG | soi over-engineer ở đầu ra 1 và 4, hai chỗ dễ làm quá tay |
| Đã xét 3 skill khác | project/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: timestamp, đủ chi tiết debug, tắt hoặc giảm được qua config.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code viết ra bám 5 nguyên tắc SOLID theo `skills/tdq-conventions/references/clean-code.md`,
  và bám rule ngôn ngữ trong `skills/tdq-build/references/rules/`.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ, chép từ `docs/kien-truc.md`:

- "`hooks/` được gọi `scripts/`; `scripts/` không được import `hooks/`" — việc này chạm ở
  `scripts/utf8_io.py`, nên module mới phải nằm trong `scripts/` để `hooks/scripts/_common.py`
  nạp được.
- "File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/`" — chạm ở `scripts/utf8_io.py`.
- "`skills/` chỉ được nhắc tên lệnh của `scripts/`, cấm chép nội dung script vào skill" —
  chạm ở đầu ra 4: placeholder phải là tên lệnh, không phải thân script.
- "ngôn ngữ chia 3 tầng — luật trong `skills/`, chú thích và docstring của `hooks/` cùng
  `scripts/`, và chuỗi máy in ra đều viết TIẾNG ANH cố định" — chạm ở mọi file của M1 và M2.
- "`CHANGELOG.md` giữ dưới trần 500 dòng của `doc_lint` R6" — chạm ở đầu ra 12.
- "Chỉ `scripts/tdq_state.py` được ghi `docs/tdq/state.json`" — chạm ở M1, không được nới.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Không biết Windows chạy shell form bằng shell nào | hook có thể vẫn chết sau khi sửa | cài plugin vào một project nháp rồi quan sát hook có in ra không, trước khi tuyên bố xong |
| Đổi 96 chuỗi trong tầng luật làm hỏng hành vi trên macOS | người dùng macOS mất lệnh đúng | placeholder phải bung ra `python3` khi hệ không phải Windows, và có test khoá cả hai hệ |
| Cài 4 công cụ ngoài để chạy test thật | `codex` cần đăng nhập, `graphify` tải nặng | xin phép user từng lệnh cài, không tự chạy |
| Dựng lại 3 bundle portable sinh diff rất lớn | khó soi lại khi có lỗi | dựng lại thành một bước riêng, sau khi M1 và M2 đã xanh |
| `errors="replace"` che mất lỗi encoding thật | ký tự hỏng đi vào log mà không ai biết | chỉ áp cho luồng in ra, không áp cho luồng đọc file |
| Sửa `skill_inventory` theo layout `synced/` làm hỏng layout cũ | máy chưa cập nhật Claude Code mất bảng B0 | quét cả hai layout, có test cho từng layout |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Module ép UTF-8 | gọi hai lần không đổi thêm trạng thái, và không ném lỗi khi luồng đã là UTF-8 |
| Q2 | Entry point dưới code page cp1252 | không file nào trong 40 file ném `UnicodeEncodeError` |
| Q3 | Sáu hook trên Windows | mỗi hook thoát 0 và in đúng khối `[TDQ:*]` của phase hiện tại |
| Q4 | Tên lệnh trong `hooks.json` | sinh lại hai lần cho cùng một hệ không đổi nội dung file |
| Q5 | Shim trên Windows | sau khi cài, gõ nguyên văn một lệnh `python3` của tầng luật chạy được ở cả ba shell |
| Q6 | Lưới an toàn | máy Windows chưa cài shim thì header hook in dòng quy ước; máy khác không in gì thêm |
| Q7 | Harness test | test đọc thư mục nhà giả, không chạm `~/.claude` thật của máy |
| Q8 | Biên xuất | đường dẫn in ra và ghi vào sổ turn chỉ chứa dấu chéo xuôi |
| Q9 | Kho skill-index | không bản ghi nào mang đường dẫn tuyệt đối của một máy |
| Q10 | Kiểm kê năng lực | liệt kê được skill ở layout `synced/` và cả layout cũ |
| Q11 | Bộ test đầy đủ trên Windows | 0 fail, 0 error |
| Q12 | Mốc macOS và Linux | không ca nào chuyển từ xanh sang đỏ so với trước khi sửa |
| Q13 | Ba bundle portable | công cụ kiểm portable báo sạch cho cả ba |
| Q14 | Luật mới về `find_references` | có đủ ba mục When it applies, What to do, Self-check |
| Q15 | Lọc nhiễu lumen | kết quả tìm kiếm không còn đường dẫn thuộc ba bundle portable |
| Q16 | Phát hành | version tăng, CHANGELOG có mục mới, `CHANGELOG.md` dưới trần 500 dòng |
| Q17 | Lint tài liệu | mọi tài liệu của request thoát 0 |

DoD:

- Cả 17 hạng mục QC PASS.
- Mọi task trong plan tick `[x]`.
- Một lượt chạy test đầy đủ trên Windows: 0 fail, 0 error.
- Sáu hook quan sát được là sống khi cài plugin vào một project nháp.
- Report viết xong, không quá 50 dòng.

## 7. Câu hỏi còn mở

(Rỗng.)
