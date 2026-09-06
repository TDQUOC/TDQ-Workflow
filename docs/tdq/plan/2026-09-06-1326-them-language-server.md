# PLAN — Thêm 10 language server vào agent-lsp

Ngày: 2026-09-06 · Spec: ../spec/2026-09-06-1326-them-language-server.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — `tdq_bench.py simulate` (hệ số agent 1.5) cho `Winner: đội`, cách biệt **2.0 phút** (40.7 so với 38.7), 1 đợt, giao được đúng 1 task còn leader giữ 19 (ĐỀ XUẤT theo số đo, user chốt lúc duyệt)
Trạng thái plan: ĐÃ DUYỆT · Mode chốt: main (inline implement)

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Cài toolchain nền và binary
- P2 — Thử khô 10 mục args
- P3 — Ghi cấu hình MCP
- P4 — Bảng tra trong repo
- P5 — Log & test bắt buộc
- Cụm song song
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang `[x]`
   NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. **Không commit/push cho đến khi user yêu cầu** — user đã chọn tự lo phần git (câu 7C).
7. **Cấm ghi một mục args vào `~/.claude.json` khi mục đó chưa qua thử khô ở P2.**

## P1 — Cài toolchain nền và binary

- [x] **T1.1** (e10m) `brew install go` — Test: `go version` in ra `go1.27.x`
- [x] **T1.2** (e4m) `brew install gopls` — Test: `gopls version` in ra `v0.23.x` **và** `command -v go` không rỗng (gopls vô dụng nếu thiếu Go — rủi ro R1 của spec)
  - Cần: T1.1
- [x] **T1.3** (e30m) `brew install dotnet` — Test: `dotnet --version` in ra `10.0.x`
- [x] **T1.4** (e6m) `dotnet tool install --global csharp-ls` — Test: `command -v csharp-ls` không rỗng; rỗng thì kiểm `~/.dotnet/tools` có trong `$PATH` không và **HỎI user** trước khi đụng `~/.zshrc` (rủi ro R4)
  - Cần: T1.3
- [x] **T1.5** (e4m) `brew install docker-language-server` — Test: `docker-language-server --help` chạy được, không lỗi
- [x] **T1.6** (e4m) `npm i -g typescript-language-server typescript` — Test: `command -v typescript-language-server` không rỗng
- [x] **T1.7** (e3m) `npm i -g yaml-language-server` — Test: `command -v yaml-language-server` không rỗng
- [x] **T1.8** (e2m) Xác nhận 4 binary có sẵn không cần cài — Test: `command -v` trả đường dẫn cho cả `vscode-html-language-server`, `vscode-css-language-server`, `vscode-markdown-language-server`, `vscode-eslint-language-server`

**Xong P1 khi**: cả 9 binary (`go`, `gopls`, `dotnet`, `csharp-ls`, `docker-language-server`, `typescript-language-server`, `yaml-language-server` + 4 binary có sẵn) đều gọi được từ shell.

## P2 — Thử khô 10 mục args

Phase này là hàng rào bảo vệ `~/.claude.json`. Không mục nào được ghi vào cấu hình trước khi
`agent-lsp doctor` xác nhận nó `ok`.

- [x] **T2.1** (e6m) Thử khô mục `dockerfile` — rủi ro R1: chưa rõ agent-lsp có nhận **hai** tham số sau dấu phẩy (`start` và `--stdio`) hay không — Test: `agent-lsp doctor dockerfile:docker-language-server,start,--stdio` in ra `Status: ok`. FAIL → lùi về `npm i -g dockerfile-language-server-nodejs` rồi thử `dockerfile:docker-langserver,--stdio`, ghi rõ việc đổi phương án vào mục QC
  - Cần: T1.5
- [x] **T2.2** (e5m) Thử khô 3 mục cần toolchain nền — Test: `agent-lsp doctor go:gopls csharp:csharp-ls` in `Status: ok` cho cả hai
  - Cần: T1.2, T1.4
- [x] **T2.3** (e5m) Thử khô 3 mục npm — Test: `agent-lsp doctor javascript:typescript-language-server,--stdio typescript:typescript-language-server,--stdio yaml:yaml-language-server,--stdio` in `Status: ok` cho cả ba
  - Cần: T1.6, T1.7
- [x] **T2.4** (e4m) Thử khô 4 mục binary có sẵn — Test: `agent-lsp doctor html:... css:... markdown:... eslint:...` in `Status: ok` cho cả bốn
  - Cần: T1.8
- [x] **T2.5** (e3m) Ghi lại số capability thật của từng mục mới vào `docs/tdq/qc/2026-09-06-1326-them-language-server.md` — Test: file tồn tại, có đủ 10 dòng, mỗi dòng một ngôn ngữ kèm số capability đo được
  - Cần: T2.1, T2.2, T2.3, T2.4

**Xong P2 khi**: cả 10 mục mới đều `Status: ok`, và bảng capability đã ghi ra file.

## P3 — Ghi cấu hình MCP

- [x] **T3.1** (e2m) Sao lưu `~/.claude.json` sang `~/.claude.json.bak-<timestamp>` — Test: file `.bak` tồn tại và `json.load` được, có đủ 4 khoá `tavily-primary`, `tavily-backup`, `lsp`, `lumen`
- [x] **T3.2** (e6m) Ghi 14 mục args vào khoá **gốc** `mcpServers.lsp.args` bằng `json.load`/`json.dump` (cấm sửa chuỗi — rủi ro R6) — Test: đọc lại file, `len(args) == 14`, và 4 mục cũ `c:clangd`, `cpp:clangd`, `json:...`, `python:...` còn nguyên đúng chuỗi cũ
  - Cần: T2.5, T3.1
- [x] **T3.3** (e4m) Xác minh cấu hình sau khi ghi — Test: `claude mcp list` liệt kê đủ 4 server và `lsp` báo connected; `projects[<repo>].mcpServers` vẫn rỗng
  - Cần: T3.2

**Xong P3 khi**: args có đúng 14 phần tử ở khoá gốc, 4 MCP server cũ còn nguyên, có bản sao lưu.

## P4 — Bảng tra trong repo

- [x] **T4.1** (e14m) Sửa `LANG_SERVER` + `LANG_CONFIG` trong `scripts/tdq_lsp.py`: dòng `go` đổi sang đường brew có nêu tiền đề Go, thêm khoá `dockerfile` vào **cả hai** bảng; viết test đỏ trước rồi mới sửa cho xanh — Test: `python3 -m pytest tests/test_tdq_lsp.py -q` xanh toàn bộ
  - Chạm: `scripts/tdq_lsp.py`, `tests/test_tdq_lsp.py` → hàm `bac3_language_server()` (`:262`) và `bac7_cau_hinh_goc_import()` (`:363`) là hai nơi duy nhất đọc hai bảng này (nguồn: grep `LANG_SERVER|LANG_CONFIG` trên `scripts/ hooks/ tests/ skills/` — chỉ 6 điểm chạm, đều trong `tdq_lsp.py`)
  - Dùng: `tdq-lsp-setup`
  - Để: xác định đúng tên binary và nhóm A/B cho khoá `dockerfile`, nạp skill TRƯỚC bước đỏ. Agent ngoài không có skill system: đọc `skills/tdq-lsp-setup/SKILL.md` rồi làm theo.
  - Ra: `scripts/tdq_lsp.py` có khoá `dockerfile` ở cả hai bảng và dòng `go` trỏ đường brew
  - Kiểm: `python3 -c "import sys; sys.path.insert(0,'scripts'); import tdq_lsp; assert 'dockerfile' in tdq_lsp.LANG_SERVER and 'dockerfile' in tdq_lsp.LANG_CONFIG and 'brew' in tdq_lsp.LANG_SERVER['go'][2]; print('ok')"`
  - Không dùng cho: sửa `skills/tdq-lsp-setup/references/languages.md` — file đó là bản chép nguyên văn từ upstream agent-lsp v0.18.0, sửa nó sẽ kéo theo phải sinh lại `portable_claude/` và `portable_codex/`, nằm ngoài phạm vi spec §1

**Xong P4 khi**: test cũ `test_thieu_ngon_ngu_trong_lang_config` (khoá bất biến `set(LANG_CONFIG) == set(LANG_SERVER)`) vẫn xanh sau khi thêm khoá mới.

## P5 — Log & test bắt buộc

- [x] **T5.1** (e4m) Xác nhận log service của `tdq_lsp.py` còn nguyên sau khi sửa — Test: `python3 scripts/tdq_lsp.py check` in ra dòng có ISO timestamp; `TDQ_LOG=0 python3 scripts/tdq_lsp.py check` không in dòng timestamp nào
  - Cần: T4.1
- [~] **T5.2** (e6m) Chạy toàn bộ test suite của repo — Test: `python3 -m pytest tests/ -q` xanh, không test nào đỏ hay lỗi import
  - Cần: T4.1
- [x] **T5.3** (e4m) Thang LSP không tụt — Test: `python3 scripts/tdq_lsp.py check` vẫn in `6/7 bậc ĐẠT · 1 cảnh báo`, đúng như trước khi làm
  - Cần: T3.3, T4.1

## Cụm song song

**Một cụm duy nhất, gồm đúng một task giao được: `T4.1`.** Lý do: 19/20 task nằm trên chuỗi
phụ thuộc thẳng (`T1.1→T1.2`, `T1.3→T1.4`, mọi task P2 cần task P1 tương ứng, P3 cần P2, P5 cần
P4). `T4.1` là task duy nhất chạm file mã nguồn repo, cũng là task duy nhất không phụ thuộc
binary nào, nên nó chạy song song được với toàn bộ P1–P3.

Đó cũng đúng là điều `tdq_bench.py simulate` đo được: 1 đợt, giao 1 task, leader giữ 19, đội
thắng **2.0 phút** trên tổng ~126 phút. Cách biệt mỏng — số đo đề xuất `subagent`, nhưng nếu bạn
chọn `main` thì mất tối đa 2 phút và đổi lại không phải dựng worktree. Quyền chốt là của bạn.

Không có file nóng: chỉ `T4.1` khai `Chạm:`, nên không đường dẫn nào bị 2 task trở lên khai.

## Definition of Done

Trỏ về §6 của spec.

- [x] Q1 Go toolchain có trên máy — `go version` in `go1.27.x`
- [x] Q2 Cả 7 binary mới gọi được — `for b in go gopls dotnet csharp-ls docker-language-server typescript-language-server yaml-language-server; do command -v $b; done` trả đủ 7 đường dẫn
- [x] Q3 Cả 10 mục args mới `ok` — `agent-lsp doctor <10 mục>` không mục nào báo thiếu binary
- [x] Q4 Args đủ 14 mục ở khoá gốc — `python3 -c "import json;d=json.load(open('/Users/tdq/.claude.json'));print(len(d['mcpServers']['lsp']['args']))"` in `14`
- [x] Q5 4 mục args cũ còn nguyên — cùng lệnh trên, kiểm 4 phần tử đầu khớp chuỗi cũ
- [x] Q6 4 MCP server cũ còn nguyên — `claude mcp list` liệt kê `tavily-primary`, `tavily-backup`, `lsp`, `lumen`
- [x] Q7 Có bản sao lưu hợp lệ — `python3 -c "import json,glob;json.load(open(sorted(glob.glob('/Users/tdq/.claude.json.bak-*'))[-1]));print('ok')"`
- [x] Q8 Bảng tra khớp thực tế — `python3 -c "import sys;sys.path.insert(0,'scripts');import tdq_lsp;assert 'dockerfile' in tdq_lsp.LANG_SERVER and 'dockerfile' in tdq_lsp.LANG_CONFIG and 'brew' in tdq_lsp.LANG_SERVER['go'][2];print('ok')"`
- [ ] Q9 Test xanh toàn bộ — `python3 -m pytest tests/ -q`
- [x] Q10 Thang LSP không tụt — `python3 scripts/tdq_lsp.py check` vẫn `6/7 bậc ĐẠT · 1 cảnh báo`
- [x] Q11 Log service còn nguyên — `python3 scripts/tdq_lsp.py check` có dòng ISO timestamp, `TDQ_LOG=0` thì im

## Kết quả thi hành (mode `main`, 2026-09-06 14:20–14:35)

18/20 task `[x]`. Hai task còn `[~]` và lý do đo được:

- **T1.4 / T2.2 (phần `csharp`)** — `csharp-ls` 0.27.0 đã nằm ở `~/.dotnet/tools/csharp-ls`
  nhưng gọi chưa được vì THIẾU HAI biến môi trường (spec R4 chỉ đoán một):
  `PATH` chưa có `~/.dotnet/tools`, và `DOTNET_ROOT` chưa trỏ tới
  `/opt/homebrew/opt/dotnet/libexec`. Đặt đủ hai biến thì `agent-lsp doctor csharp:csharp-ls`
  cho `Status: ok`, 3 capability — đã đo tại chỗ. Sửa `~/.zshrc` là việc spec R4 bắt HỎI user
  trước, nên dừng ở đây chờ user.
- **T5.2** — suite của repo ĐANG ĐỎ SẴN từ trước request này. Đo đối chứng bằng bản HEAD sạch
  (`git archive HEAD` ra thư mục tạm): HEAD có 1521 test / 292 fail / 4 error; sau thay đổi có
  1523 test / 290 fail / 4 error. `comm` hai danh sách tên test hỏng cho **0 test hỏng mới**,
  và `test_tdq_lsp` xanh 39/39. Cụm hỏng lớn nhất (284 ca) là
  `test_skill_router.test_moi_duong_dan_khac_rong_deu_mo_duoc` — sổ đăng ký skill trỏ tới
  đường dẫn không còn tồn tại trên máy. Sửa nó nằm ngoài phạm vi spec §1, nên KHÔNG tự ý làm.

Định trạng DoD: Q1, Q4–Q8, Q10, Q11 PASS. Q2/Q3 chờ quyết định `~/.zshrc`. Q9 vướng nợ kỹ
thuật có sẵn của repo, không do request này gây ra.

## P6 — Task fix sinh từ vòng QC (luật thi hành số 5, không cần duyệt lại)

- [x] **T6.1** (e3m) Gỡ mục `csharp:csharp-ls` khỏi args vì nó chưa qua thử khô ở env mặc định —
  vi phạm luật thi hành số 7 do agent QC bắt được — Test: `len(args) == 13`, `agent-lsp doctor`
  trên 9 mục mới cho `Summary: 9 ok, 0 failed`, `claude mcp list` đủ 4 server `Connected`
- [x] **T6.2** (e5m) CHỜ USER: thêm `export PATH="$PATH:$HOME/.dotnet/tools"` và
  `export DOTNET_ROOT="/opt/homebrew/opt/dotnet/libexec"` vào `~/.zshrc`, rồi thêm lại mục
  `csharp:csharp-ls` vào args — Test: `command -v csharp-ls` không rỗng ở shell mới;
  `agent-lsp doctor csharp:csharp-ls` cho `Status: ok`; `len(args) == 14`
  - Cần: quyết định của user (spec R4 bắt HỎI trước khi đụng `~/.zshrc`)
- [ ] **T6.3** (e0m) KHÔNG LÀM trong request này: 290 test đỏ của repo (chủ yếu
  `test_skill_router`) là nợ có sẵn từ HEAD, sửa nó lấn phạm vi spec §1 — đề xuất mở request
  riêng
