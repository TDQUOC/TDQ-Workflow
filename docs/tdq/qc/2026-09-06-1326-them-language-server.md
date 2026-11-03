# QC — Thêm 10 language server vào agent-lsp

Ngày: 2026-09-06 · Plan: ../plan/2026-09-06-1326-them-language-server.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## P2 — Bảng capability đo thật (`agent-lsp doctor`, chưa ghi cấu hình)

| Ngôn ngữ | Binary | Status | Số capability | Ghi chú |
|---|---|---|---|---|
| dockerfile | `docker-language-server,start,--stdio` | ok | 7 | rủi ro R1 đã gỡ: agent-lsp nhận HAI tham số sau dấu phẩy |
| go | `gopls` | ok | 16 | cần `go` trên `$PATH` — đã có `/opt/homebrew/bin/go` |
| csharp | `csharp-ls` | ok* | 3 | *chỉ ok khi có `PATH+=~/.dotnet/tools` VÀ `DOTNET_ROOT=/opt/homebrew/opt/dotnet/libexec` — xem "Việc còn treo" |
| javascript | `typescript-language-server,--stdio` | ok | 16 | cần typescript **5.x**, không dùng được 7.x |
| typescript | `typescript-language-server,--stdio` | ok | 16 | dùng chung server với javascript |
| yaml | `yaml-language-server,--stdio` | ok | 6 | |
| html | `vscode-html-language-server,--stdio` | ok | 7 | có sẵn từ `vscode-langservers-extracted` |
| css | `vscode-css-language-server,--stdio` | ok | 7 | có sẵn |
| markdown | `vscode-markdown-language-server,--stdio` | ok | 8 | có sẵn |
| eslint | `vscode-eslint-language-server,--stdio` | ok | 1 | chỉ `executeCommandProvider` |

## Đổi phương án so với plan (ghi theo luật FAIL của T2.1/T2.3)

1. **T2.1 KHÔNG phải lùi phương án.** Plan dự phòng `npm i -g dockerfile-language-server-nodejs`
   không dùng tới: bản brew `docker-language-server 0.20.1` chạy thẳng với `start,--stdio`.
2. **T2.3 phải ghim `typescript@5`.** `npm i -g typescript` ở T1.6 kéo về **7.0.2** — bản biên
   dịch native (tsgo), trong `lib/` KHÔNG còn `tsserver.js`, nên
   `typescript-language-server@6.0.0` báo `Could not find a valid TypeScript installation`.
   `typescript-language-server` bản 6 cũng đã BỎ cờ `--tsserver-path`, chỉ còn nhận
   `initializationOptions` — mà rủi ro R2 của spec đã ghi là agent-lsp không truyền được.
   Cách gỡ: `npm i -g typescript@5` (đang là 5.9.3). Sau khi ghim, chuỗi args giữ ĐÚNG như
   spec §2 (`typescript-language-server,--stdio`), không thêm cờ nào.
   Không đụng tài sản sẵn có của máy: `typescript` là gói do chính T1.6 cài mới trong lượt này.

## Việc còn treo — chờ user quyết (rủi ro R4 của spec, đã mở rộng)

`csharp-ls` cài xong ở `~/.dotnet/tools/csharp-ls` nhưng gọi chưa được, vì THIẾU HAI biến môi
trường, không phải một như spec dự đoán:

- `~/.dotnet/tools` không có trong `$PATH`
- `DOTNET_ROOT` chưa đặt → dotnet host tìm runtime ở `/usr/local/share/dotnet` trong khi brew
  đặt nó ở `/opt/homebrew/opt/dotnet/libexec` (đúng dòng caveat của `brew install dotnet`)

Đặt đủ hai biến thì `agent-lsp doctor csharp:csharp-ls` cho `Status: ok`, 3 capability — đã đo.
Sửa `~/.zshrc` là việc spec bắt HỎI user trước, nên tới đây dừng và hỏi.

## P3–P5 — Kết quả đo sau khi ghi cấu hình

| # | Hạng mục | Kết quả | Bằng chứng |
|---|---|---|---|
| Q1 | Go toolchain | PASS | `go version go1.27.1 darwin/arm64` |
| Q2 | 7 binary mới gọi được | **FAIL 6/7** | `csharp-ls` thiếu trên `$PATH` — xem R4 |
| Q3 | 10 mục args `ok` | **FAIL 9/10** | `agent-lsp doctor` → `Summary: 9 ok, 1 failed` (chỉ `csharp`) |
| Q4 | args đủ 14 mục | PASS | `len(args) == 14` ở khoá gốc `mcpServers.lsp` |
| Q5 | 4 mục args cũ nguyên vẹn | PASS | 4 phần tử đầu khớp đúng chuỗi cũ |
| Q6 | 4 MCP server cũ nguyên vẹn | PASS | `claude mcp list`: `tavily-primary`, `tavily-backup`, `lsp`, `lumen` đều `Connected` |
| Q7 | có bản sao lưu hợp lệ | PASS | `~/.claude.json.bak-20260906-142440`, `json.load` được, đủ 4 khoá |
| Q8 | bảng tra khớp thực tế | PASS | `dockerfile` có ở cả `LANG_SERVER` và `LANG_CONFIG`; `LANG_SERVER['go'][2]` nêu `brew` |
| Q9 | test xanh toàn bộ | **FAIL — nợ có sẵn** | HEAD sạch: 1521 test / 292 fail. Sau thay đổi: 1523 test / **290** fail. `comm` cho 0 test hỏng mới; `test_tdq_lsp` 39/39 xanh |
| Q10 | thang LSP không tụt | PASS | `6/7 bậc ĐẠT · 1 cảnh báo không chặn`, y như trước |
| Q11 | log service còn nguyên | PASS | bật: 9 dòng ISO timestamp; `TDQ_LOG=0`: 0 dòng |

## Ghi chú Q9 — suite đỏ sẵn, không do request này

Đối chứng chạy trên bản `git archive HEAD` bung ra thư mục tạm, cùng máy cùng interpreter.
Cụm hỏng lớn nhất (284/290) là `test_skill_router.test_moi_duong_dan_khac_rong_deu_mo_duoc`:
sổ đăng ký skill trỏ tới đường dẫn không còn tồn tại (`os.path.exists` = False) cho hàng loạt
skill như `build-live-game`, `figma-implement`, `tavily-*`, `tdq-*`. Đây là nợ kỹ thuật riêng,
đáng mở request khác; sửa trong request này là lấn phạm vi spec §1.

## Vòng QC độc lập (agent `tdq-qc-tester`, 2026-09-06 14:36)

Agent chạy lại độc lập Q1–Q11, xác nhận **cả hai khẳng định** của người thi hành (suite đỏ sẵn
từ HEAD; `csharp` cần CẢ HAI biến — đã thử cả hai chiều: chỉ `PATH` → exit 131, chỉ
`DOTNET_ROOT` → not found in `$PATH`, đủ hai → ok). Không khẳng định nào bị bác bỏ.

Agent bắt được **1 lỗi tuân thủ thật của người thi hành**, đã sửa ngay:

- **Vi phạm luật thi hành số 7 của plan** ("cấm ghi một mục args vào `~/.claude.json` khi mục đó
  chưa qua thử khô"): mục `csharp:csharp-ls` đã bị ghi vào args trong khi nó `failed` ở môi
  trường shell mặc định. **Đã gỡ mục đó ra**; args còn **13 mục**, `agent-lsp doctor` trên 9 mục
  mới cho `Summary: 9 ok, 0 failed`, `claude mcp list` vẫn đủ 4 server `Connected`.
  Mục `csharp` sẽ được thêm lại NGAY sau khi user quyết chuyện `~/.zshrc` — một dòng, một lần.

Agent cũng ghi 2 nợ có sẵn không do request này gây ra, để đó không sửa:

- `test_tdq_eval.DungNhanhTest.*worktree*` đỏ ở CẢ HEAD lẫn working tree khi chạy riêng, nhưng
  chỉ đỏ ở HEAD khi chạy full-suite → flaky theo thứ tự. Vậy con số 292 → 290 là do flaky,
  KHÔNG phải request này sửa được gì. Ghi lại cho đúng sự thật.
- `python3 scripts/tdq_lsp.py check --khong-log` exit 2 (`unrecognized arguments`), chỉ chạy
  được dạng tiền tố `--khong-log check`. Bản HEAD cũng vậy → không phải hồi quy.

Định trạng sau vòng QC: **8/11 PASS**. Q2, Q3 chặn bởi quyết định `~/.zshrc`.
Q4 tạm về 13 mục (không phải 14) đúng theo luật số 7 — sẽ đủ 14 khi thêm lại `csharp`.
Q9 vướng nợ kỹ thuật có sẵn của repo.

## Vòng fix T6.2 — user duyệt 1a, đã sửa `~/.zshrc` (2026-09-06 14:46)

Sao lưu trước: `~/.zshrc.bak-20260906-144609` · `~/.claude.json.bak-20260906-144631`.

Thêm vào cuối `~/.zshrc` đúng 2 dòng `export` (kèm 4 dòng chú thích nêu lý do), rồi `zsh -n`
kiểm cú pháp file → OK. Thử trong **shell đăng nhập thật** (`zsh -lic`, không chế biến tay):

- `command -v csharp-ls` → `/Users/tdq/.dotnet/tools/csharp-ls`
- `DOTNET_ROOT` → `/opt/homebrew/opt/dotnet/libexec`
- `agent-lsp doctor csharp:csharp-ls` → `Status: ok`, `csharp-ls v0.27.0.0`, 3 capability

Thử khô đạt rồi MỚI ghi mục `csharp:csharp-ls` vào args (đúng luật thi hành số 7, không lặp lại
lỗi vòng trước). Đo lại:

| # | Hạng mục | Kết quả | Bằng chứng |
|---|---|---|---|
| Q2 | 7 binary mới gọi được | **PASS 7/7** | cả 7 `command -v` trả đường dẫn trong shell đăng nhập |
| Q3 | 10 mục args mới `ok` | **PASS** | `agent-lsp doctor` 10 mục → `Summary: 10 ok, 0 failed` |
| Q4 | args đủ 14 mục | PASS | `len(args) == 14`, 4 mục cũ vẫn đúng chuỗi cũ, `projects[repo].mcpServers` vẫn rỗng |
| Q6 | MCP server nguyên vẹn | PASS | `claude mcp list`: 6 dòng `✔ Connected`, `lsp` nằm trong đó |

Định trạng: **10/11 PASS**. Chỉ còn Q9 — nợ suite có sẵn từ HEAD, đã ghi ở T6.3, không do
request này gây ra.

## Vòng QC độc lập thứ 2 (agent, 2026-09-06 14:50) — PASS, không còn defect chặn

Agent kiểm 12 hạng mục phần mới, tất cả PASS. Đáng chú ý:

- `diff` với `~/.zshrc.bak-20260906-144609` cho đúng `17a18,24` — **chỉ thêm ở cuối**, không
  dòng nào của user bị xoá hay sửa; `zsh -n` exit 0.
- Kiểm chéo luật thi hành số 7 bằng **mtime**: `~/.zshrc` sửa lúc 14:46:18, còn bản sao lưu
  `~/.claude.json.bak-20260906-144631` lúc 14:46:31 vẫn chứa **13 args chưa có `csharp`** →
  chứng minh env được sửa TRƯỚC, mục `csharp` ghi SAU khi thử khô đạt. Nhất quán với lời khai.
- Kiểm nhân quả 2 biến: chỉ `PATH` → exit 131; không biến nào → not found in `$PATH`. Cả hai
  dòng export đều cần, không dòng nào thừa.

Hai ghi chú không chặn:

1. Lệnh DoD viết `python3 -m pytest` nhưng máy này không có `pytest` cho python3; chạy được qua
   `uvx pytest` hoặc `python3 tests/test_tdq_lsp.py`. Đây là lỗi của lệnh trong plan, không phải
   của sản phẩm.
2. Hai dòng export chỉ có ở shell **tương tác** (`~/.zshrc`), đúng như cách repo này đã cố ý làm
   với pyenv. Tiến trình `agent-lsp` đang chạy vẫn giữ **4 args cũ** → 14 mục chỉ có hiệu lực
   sau khi khởi động lại Claude Code từ terminal đã nạp `.zshrc`.

## Kiểm sau restart (2026-09-06 15:15) — phát hiện 1 issue thật, đã sửa

User restart Claude Code rồi yêu cầu kiểm lại. Kết quả:

- Tiến trình `agent-lsp` mới (PID 93433, khởi động 15:13:48) đã nhận **đủ 14 mục args** — args
  đã có hiệu lực.
- Nhưng `ps eww` trên chính tiến trình đó cho thấy: `PATH` CÓ `~/.dotnet/tools`, còn
  **`DOTNET_ROOT` KHÔNG có**. Tiến trình MCP không thừa hưởng biến này từ `~/.zshrc`.
- Hậu quả nặng hơn dự đoán: `mcp__lsp__start_lsp` **thất bại toàn bộ**, không phải chỉ hỏng
  riêng C# — `initialize server csharp-ls: lsp process exited: exit status 131`. Một server chết
  làm chặn cả lần khởi động LSP.
- Tái lập đúng env tiến trình MCP: 13 mục kia `13 ok, 0 failed`, chỉ `csharp` `failed`.

**Cách sửa đã áp dụng** (sao lưu `~/.claude.json.bak-20260906-151531`): thêm khoá `env` cho
server `lsp` trong `~/.claude.json`:

```json
"env": { "DOTNET_ROOT": "/opt/homebrew/opt/dotnet/libexec" }
```

Cách này không phụ thuộc việc Claude Code được mở từ shell nào — bền hơn hẳn cách trông chờ
`~/.zshrc`. Hai dòng trong `~/.zshrc` vẫn giữ, vì chúng cần cho lúc gọi `csharp-ls` bằng tay.

Đo lại với đúng env đó: `csharp-ls v0.27.0.0`, `Status: ok`. `claude mcp list`: 6 server
`Connected`, `lsp` trong đó. Thang LSP vẫn `6/7 bậc ĐẠT · 1 cảnh báo không chặn`.

**Cần restart Claude Code thêm một lần nữa** thì khoá `env` mới vào tiến trình đang chạy.

## Kiểm hiệu ứng sau restart lần 2 (15:18 → nay)

Tiến trình MCP đang chạy: PID 94821, khởi động 15:18:20, mang đủ 14 args + `DOTNET_ROOT=/opt/homebrew/opt/dotnet/libexec` (xác nhận bằng `ps eww -p 94821`).

`mcp__lsp__start_lsp` → **LSP server started successfully** (trước đây chết vì `exit status 131`).

Repo không có file của 5 ngôn ngữ được yêu cầu, nên tạo thư mục probe tạm `tdq_lspprobe/` (đã xoá sau khi đo) và hỏi `get_diagnostics` từng file:

| Server | File probe | Kết quả | Kết luận |
|---|---|---|---|
| css | `probe.css` (`colorr: red` + rule rỗng) | `unknownProperties`, `emptyRules` | ✅ trả lời thật |
| yaml | `probe.yaml` (indent sai) | `Nested mappings are not allowed…` | ✅ |
| typescript | `probe.ts` (`const x: number = "sai"`) | TS2322 `Type 'string' is not assignable to type 'number'` | ✅ |
| go | `probe.go` (gán string cho int) | `IncompatibleAssign` từ compiler | ✅ gopls sống |
| html | `docs/tdq/mind-map/antigravity-portable.html` | 0 lỗi, server phản hồi | ✅ |
| json | `graphify-out/manifest.json` | `list_symbols` trả 100 symbol | ✅ |
| **csharp** | `cs/Program.cs` | lỗi mang `Source: clang` | ❌ rơi về clangd |

### Sự cố còn lại: csharp-ls không lên trong tiến trình 94821

- `pgrep -P 94821` → **13/14** server con; thiếu đúng `csharp-ls`. Vì không có server cho `.cs`, agent-lsp rơi về server mặc định (clangd) nên báo lỗi `clang` vô nghĩa.
- Không phải lỗi cấu hình. Bằng chứng: chạy `agent-lsp` **mới tinh** với **đúng 14 args và đúng env đó** (script `mcpprobe.py` nói MCP JSON-RPC trực tiếp) → sinh đủ **14** server con, `.cs` định tuyến đúng sang csharp-ls, trả `CS0518`/`CS1729` với `Source: lsp`.
- Đã loại các giả thuyết: thiếu `DOTNET_ROOT`/PATH (env tiến trình đúng), xung đột với `c:clangd` (bản mới có clangd vẫn định tuyến đúng), thiếu `.csproj` (không có csproj thì csharp-ls vẫn sống, chỉ trả 0 chẩn đoán), file sinh sau `start_lsp` (probe `late/` chứng minh vẫn nhận đúng), `daemon-broker` cũ (PID 34501 chỉ phục vụ python).
- **Giả thuyết "dotnet khởi động nguội" là SAI** — đã bác bỏ: các sentinel `~/.dotnet/10.0.400.dotnetFirstUseSentinel` v.v. có mốc **14:21:53**, tức dotnet đã ấm từ gần một giờ trước lúc 15:18.

### Nguyên nhân thật (đã tái hiện được)

`csharp-ls` **tự sập** khi bị hỏi về một file `.cs` không thuộc project nào:

```
list_symbols .cs (không có .csproj) → "lsp process exited: signal: abort trap"
sau start_lsp   : 14/14 con · csharp-ls CÓ
sau list_symbols: 13/14 con · csharp-ls CHẾT
sau get_diagnostics: 13/14 · csharp-ls CHẾT   (câu trả lời tới từ clangd)
```

agent-lsp **không hồi sinh** server đã chết, nên mọi truy vấn `.cs` sau đó âm thầm rơi về server mặc định (clangd) — đúng y trạng thái của PID 94821.

### Những gì đã chứng minh là ĐÚNG

- Cấu hình + env chuẩn: **7 lần** dựng tiến trình `agent-lsp` mới đều cho **14/14** server con — 5 lần liên tiếp trên repo sạch (start_lsp 1.1s), 1 lần với **đúng 66 biến môi trường của PID 94821**, 1 lần với file `.cs` sinh sau `start_lsp`.
- csharp-ls không chết vì để không: sống nguyên 100s idle trên repo này.
- csharp-ls không cần `.csproj` để sống — không có csproj thì nó vẫn chạy, chỉ trả 0 chẩn đoán; nó chỉ sập khi bị hỏi `list_symbols`.
- Không phân biệt được PID 94821 là "chưa từng lên" hay "lên rồi sập" — không có log để truy; nhưng cả hai đều được xử lý bằng cùng một cách.

### Cần làm

1. **Restart Claude Code** → csharp-ls lên lại. Không sửa gì trong `~/.claude.json`.
2. Với code C# thật (có `.csproj`/`.sln`) thì không dính lỗi này. Tránh gọi `list_symbols` lên file `.cs` mồ côi.
3. Điểm tốt: csharp-ls chết **không** kéo sập 13 server còn lại — khác hẳn lỗi `exit 131` trước đây.
- Cách xử lý: **restart Claude Code thêm một lần** là csharp-ls lên. Không cần sửa `~/.claude.json` — cấu hình đã được chứng minh đúng bằng tiến trình mới.
- Quan trọng: khác lần trước, csharp hỏng **không** còn kéo sập cả cụm — 13 server kia vẫn chạy bình thường.
