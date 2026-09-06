# SPEC — Thêm 10 language server vào agent-lsp

Ngày: 2026-09-06 · Bản: 1.0 · Brief: ../brief/2026-09-06-1326-them-language-server.md · Lane: full
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

- **Mục tiêu:** đưa `args` của MCP `lsp` trong `~/.claude.json` từ **4 mục lên 14 mục**, và cài
  đủ binary để cả 14 mục đều trả `Status: ok` khi chạy `agent-lsp doctor`. Đây là năng lực mức
  **máy** (user scope), áp cho mọi project.

- **Trong phạm vi:**
  - 5 ngôn ngữ user yêu cầu: `csharp`, `dockerfile`, `go`, `javascript`, `yaml`
  - 2 ngôn ngữ user yêu cầu thêm, binary đã có sẵn: `html`, `css`
  - 3 mục thêm miễn phí user chọn ở câu 5C: `typescript`, `markdown`, `eslint`
  - Cài toolchain nền bắt buộc: Go 1.27.1 và .NET SDK 10.0.400
  - Sửa bảng tra `LANG_SERVER` + `LANG_CONFIG` trong `scripts/tdq_lsp.py` cho khớp thực tế
  - Unit test khoá hai thay đổi bảng tra đó

- **NGOÀI phạm vi:**
  - **Không** cải thiện thang LSP của chính repo TDQ-Workflow. Repo có 0 file `.cs/.go/.js/.ts/.yaml`
    và không có `Dockerfile`; bậc 3 chỉ đòi server cho ngôn ngữ nó ngửi thấy ≥3 file
    (`scripts/tdq_lsp.py:262`), nên thang vẫn đứng ở 6/7 như trước. Giá trị nằm ở project khác.
  - **Không** cài plugin `agent-lsp` (hook `PreToolUse` của nó làm tụt bậc 6) và không cài plugin lumen.
  - **Không** sửa cảnh báo bậc 5 (`MODEL_LUMEN` hardcode) — việc riêng, không thuộc request này.
  - **Không** mở nhánh git, **không** commit, **không** push. User chọn 7C: tự lo phần git.
  - **Không** truyền `initializationOptions`/`yaml.schemas` tuỳ biến cho yaml server — xem R2 ở §5.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | 4 hướng ở brief §B2 đã trả lời dứt khoát cả 4 câu; phần còn lại là đo tại máy |
| Interview | ĐÃ XONG | vòng 1 đã chốt 7 câu, không còn câu nào đổi được kết quả |
| Spec | CÓ | khung bất biến |
| Plan | CÓ | khung bất biến; mỗi ngôn ngữ là 1 task có phép kiểm riêng |
| Chia subagent | BỎ | các bước cài phụ thuộc tuần tự (go trước gopls, dotnet trước csharp-ls), đều là lệnh mạng; song song không rút ngắn mà làm khó truy vết lỗi |
| QC độc lập (agent) | CÓ | DoD đo được khách quan bằng lệnh `agent-lsp doctor` — đúng việc của agent QC |
| Deep review spec/plan | BỎ | phạm vi hẹp, chỉ 1 file repo bị chạm, rủi ro đã liệt kê đủ ở §5 |
| Implement | CÓ | khung bất biến |
| Report | CÓ | khung bất biến |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Go toolchain + `gopls` | `/opt/homebrew/bin/go`, `/opt/homebrew/bin/gopls` | cả hai có trên `$PATH` và in được số phiên bản |
| 2 | .NET SDK + `csharp-ls` | `/opt/homebrew/bin/dotnet`, `~/.dotnet/tools/csharp-ls` | `csharp-ls` có trên `$PATH` |
| 3 | `docker-language-server` | `/opt/homebrew/bin/docker-language-server` | có trên `$PATH`, chạy được chế độ stdio |
| 4 | `typescript-language-server` + `typescript` | `~/.nvm/versions/node/v24.20.0/bin/` | có trên `$PATH` |
| 5 | `yaml-language-server` | `~/.nvm/versions/node/v24.20.0/bin/` | có trên `$PATH` |
| 6 | `args` MCP `lsp` đủ **14 mục** | `~/.claude.json` khoá gốc `mcpServers.lsp.args` | mảng có đúng 14 phần tử, khoá nằm ở gốc chứ không rơi vào `projects[...]` |
| 7 | Bảng tra khớp thực tế | `scripts/tdq_lsp.py` `LANG_SERVER`, `LANG_CONFIG` | dòng `go` trỏ đường brew; có dòng `dockerfile` |
| 8 | Unit test khoá đầu ra 7 | bộ test của `tdq_lsp` trong repo | test mới chạy xanh bằng một lệnh |
| 9 | Bản sao lưu trước khi sửa | `~/.claude.json.bak-<timestamp>` | file tồn tại, là JSON hợp lệ, có đủ 4 MCP server cũ |

Danh sách 14 mục args cuối cùng (4 mục đầu giữ nguyên, 10 mục sau là mới):

```
c:clangd
cpp:clangd
json:vscode-json-language-server,--stdio
python:pyright-langserver,--stdio
csharp:csharp-ls
dockerfile:docker-language-server,start,--stdio
go:gopls
javascript:typescript-language-server,--stdio
typescript:typescript-language-server,--stdio
yaml:yaml-language-server,--stdio
html:vscode-html-language-server,--stdio
css:vscode-css-language-server,--stdio
markdown:vscode-markdown-language-server,--stdio
eslint:vscode-eslint-language-server,--stdio
```

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| `M1-brew` | `/opt/homebrew/bin/go`, `/opt/homebrew/bin/gopls`, `/opt/homebrew/bin/dotnet`, `/opt/homebrew/bin/docker-language-server` | không | 1, 3, và nền cho 2 |
| `M2-dotnet-tool` | `~/.dotnet/tools/csharp-ls` | `M1-brew` (cần `dotnet` trước) | 2 |
| `M3-npm` | `~/.nvm/versions/node/v24.20.0/bin/typescript-language-server`, `.../yaml-language-server` | không | 4, 5 |
| `M4-cau-hinh-mcp` | `~/.claude.json`, `~/.claude.json.bak-*` | `M1`, `M2`, `M3` (binary phải có trước khi khai vào args) | 6, 9 |
| `M5-bang-tra-repo` | `scripts/tdq_lsp.py` và file test tương ứng của nó | không | 7, 8 |

`M5` độc lập hoàn toàn với `M1`–`M4`: nó chỉ sửa bảng tra tham chiếu trong repo, không phụ thuộc
binary nào có mặt hay chưa.

## 3. Cách tiếp cận & lý do

- **Chọn:** cài từng lớp theo thứ tự phụ thuộc (toolchain → server → args), mỗi server được nghiệm
  thu **riêng lẻ** bằng `agent-lsp doctor <lang>:<binary>[,<flag>]` **trước khi** ghi vào
  `~/.claude.json`. Chỉ khi cả 14 mục cùng `ok` mới ghi một lần vào file cấu hình.
- **Vì:** `agent-lsp doctor` nhận args ngay trên dòng lệnh nên thử khô được mà không đụng file thật.
  Cách này đã được chứng minh ở chính request này: `agent-lsp doctor css:... html:...` trả
  `Status: ok` cho cả hai trước khi bất cứ thứ gì được ghi. Ghi cấu hình hỏng thì mọi tool
  `mcp__lsp__*` chết cho tới lần restart sau, nên thử khô là bắt buộc.
- **Đã loại:**
  - `brew install gopls` đơn lẻ — vì gopls gọi lệnh `go` lúc **chạy** (go.dev/gopls;
    golang/go#41701 panic `go command required, not found`), formula chỉ khai
    `depends_on "go" => :build` nên bottle không kéo Go về → binary hỏng.
  - Roslyn LS chính chủ cho C# — vì còn prerelease (5.12.0-1.26426.8), bắt buộc cờ `--prerelease`,
    và có rủi ro không tự nạp solution khi chạy standalone.
  - npm `dockerfile-language-server-nodejs@0.15.0` — vì đứng yên từ 2025-10-15; bản brew chính chủ
    `docker-language-server` 0.20.1 phủ rộng hơn (Dockerfile + Compose + Bake). Vẫn giữ làm
    phương án lùi cho R1.
  - `@vtsls/language-server` — vì npm đứng ở 0.3.0 từ 2025-12-24, README tự nhận "best-effort".

## 3b. Năng lực & công cụ

Chép từ brief mục `### Năng lực dùng được`. Phân vân → DÙNG.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-lsp-setup | plugin:tdq-workflow | DÙNG | đầu ra 6, 7: bảng `LANG_SERVER`, thang 7 bậc, cách agent-lsp nhận args |
| tdq-conventions | plugin:tdq-workflow | NỀN | luật chung của workflow |
| tdq-intake | plugin:tdq-workflow | NỀN | pipeline đang chạy |
| tdq-spec | plugin:tdq-workflow | NỀN | pipeline đang chạy |
| tdq-plan | plugin:tdq-workflow | NỀN | pipeline đang chạy |
| tdq-build | plugin:tdq-workflow | NỀN | pipeline đang chạy |
| tdq-status | plugin:tdq-workflow | NỀN | pipeline đang chạy |
| tdq-check-status | plugin:tdq-workflow | NỀN | pipeline đang chạy |
| Đã xét 1 skill khác trên đĩa và các skill built-in trong context | plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- **Log service bật mặc định:** `scripts/tdq_lsp.py` đã có sẵn (`_log()`, dòng ISO timestamp ra
  stderr, tắt bằng `--khong-log` hoặc `TDQ_LOG=0`). Thay đổi ở đầu ra 7 phải giữ nguyên cơ chế này;
  không thêm đường ghi log mới.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật. Cụ thể: **cấm** ghi
  một mục args mà chưa chứng minh nó `ok` bằng `agent-lsp doctor`.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh — áp cho đầu ra 7 (test ở đầu ra 8).
  Đầu ra 1–6 và 9 là trạng thái máy, không phải mã nguồn: nghiệm thu bằng lệnh đo ở §6 thay cho
  unit test.
- Code viết ra bám 5 nguyên tắc SOLID theo `skills/tdq-conventions/references/clean-code.md`, và
  bám rule ngôn ngữ trong `skills/tdq-build/references/rules/`.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md`):

- "Chỉ `scripts/tdq_state.py` được ghi `docs/tdq/state.json`; mọi nơi khác chỉ đọc qua CLI." —
  việc này chạm ở mọi lệnh ghi state của request.
- "File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/`" — việc này **không** tạo file code
  mới; chỉ sửa `scripts/tdq_lsp.py` và file test đã có của nó.
- "Tầng test gọi được vào mọi tầng; không tầng nào được import tầng test" — test mới ở đầu ra 8
  chỉ import `scripts/tdq_lsp.py`, đúng chiều cho phép.

Cài đặt/tải về cần thiết (tên gói và bản đã xác minh bằng `brew info` / `npm view` ngày 2026-09-06):

| Gói | Bản | Nguồn | Ghi chú |
|---|---|---|---|
| `go` | 1.27.1 | brew, bottled | bắt buộc cho gopls |
| `gopls` | 0.23.0 | brew, bottled | |
| `dotnet` | 10.0.400 | brew, bottled | SDK đầy đủ, vài GB |
| `csharp-ls` | 0.27.0 | `dotnet tool install --global` | |
| `docker-language-server` | 0.20.1 | brew, bottled | |
| `typescript-language-server` | 6.0.0 | npm global | kèm gói `typescript` |
| `yaml-language-server` | 1.24.0 | npm global | |

Đĩa trống trước khi cài: 400 Gi.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| R1 `docker-language-server` cần **hai** tham số `start --stdio`, chưa rõ agent-lsp có nhận nhiều tham số sau dấu phẩy không | mục `dockerfile` không chạy được | thử khô `agent-lsp doctor` trước khi ghi cấu hình; thất bại thì lùi về npm `docker-langserver,--stdio` |
| R2 agent-lsp nhiều khả năng không truyền được `initializationOptions` | yaml server chỉ chạy mặc định + SchemaStore; docker server không tắt được telemetry | chấp nhận mặc định, ghi rõ giới hạn trong report — không hứa tính năng schema tuỳ biến |
| R3 npm global ghim theo phiên bản node `v24.20.0` | nâng node là mất sạch server npm | ghi cảnh báo trong report |
| R4 `dotnet tool install --global` cần `~/.dotnet/tools` trong `$PATH` | `csharp-ls` cài xong vẫn không gọi được | kiểm bằng `command -v csharp-ls`; thiếu thì HỎI user trước khi sửa `~/.zshrc` |
| R5 tool `mcp__lsp__*` chỉ nạp lại sau khi restart Claude Code | user tưởng cấu hình hỏng | nhắc restart ở report |
| R6 ghi hỏng `~/.claude.json` làm chết cả 4 MCP đang chạy | mất tavily + lsp + lumen | sao lưu trước (đầu ra 9), ghi bằng `json.load`/`json.dump` chứ không sửa chuỗi, kiểm lại bằng `claude mcp list` |
| R7 `brew install dotnet` tải vài GB, có thể lâu hoặc đứt mạng | task treo giữa chừng | chạy riêng một task, kiểm lại bằng `dotnet --version`; đứt thì chạy lại lệnh, brew tự nối |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Go toolchain | lệnh `go` có trên `$PATH` và in ra số phiên bản 1.27.x |
| Q2 | Từng binary trong 5 gói mới | mỗi binary có trên `$PATH` đúng tên mà args khai |
| Q3 | Thử khô từng mục args mới | `agent-lsp doctor` trả `Status: ok` cho **cả 10 mục mới**, không mục nào cảnh báo thiếu binary |
| Q4 | Cấu hình sau khi ghi | `mcpServers.lsp.args` ở khoá **gốc** của `~/.claude.json` có đúng 14 phần tử; `projects[<repo>].mcpServers` vẫn rỗng |
| Q5 | 4 mục cũ không bị mất | `c`, `cpp`, `json`, `python` vẫn còn nguyên trong args, đúng chuỗi cũ |
| Q6 | 4 MCP server cũ không bị mất | `tavily-primary`, `tavily-backup`, `lsp`, `lumen` đều còn trong cấu hình |
| Q7 | Bản sao lưu | file `.bak-*` tồn tại và parse được thành JSON hợp lệ |
| Q8 | Bảng tra repo | `LANG_SERVER['go']` trỏ đường brew; tồn tại khoá `dockerfile` ở cả `LANG_SERVER` và `LANG_CONFIG` |
| Q9 | Test của bảng tra | test mới chạy xanh, và **toàn bộ** file test cũ của `tdq_lsp` vẫn xanh |
| Q10 | Thang LSP không tụt | vẫn 6/7 bậc ĐẠT, đúng 1 cảnh báo bậc 5 như trước khi làm |
| Q11 | Log service còn nguyên | chạy `tdq_lsp.py check` vẫn in dòng có ISO timestamp; đặt `TDQ_LOG=0` thì im |

**DoD:** Q1–Q11 đều PASS · 14 mục args đều `Status: ok` · không mục args nào được ghi mà chưa qua
thử khô · `~/.claude.json` có bản sao lưu · working log đã append · **không có commit nào được tạo**.

## 7. Câu hỏi còn mở

(Rỗng.)
