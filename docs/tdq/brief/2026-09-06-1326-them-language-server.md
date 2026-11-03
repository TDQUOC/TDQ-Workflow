# 2026-09-06-1326-them-language-server
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> hãy giúp tôi mở request install csharp, dockerfile, go, javascript, yaml và setup vào args của
> agent-lsp và thêm luôn vscode html language server và vscode css language server vào args

**Đọc lần đầu.** Cài 5 language server còn thiếu (csharp, dockerfile, go, javascript, yaml), rồi
viết cả 5 + html + css vào `args` của MCP `lsp` trong `~/.claude.json`. Kết quả mong đợi: args đi từ
4 mục (c, cpp, json, python) lên **11 mục**.

Phạm vi đoán: cài binary mức user + sửa đúng 1 key trong `~/.claude.json`. Không đụng repo code.

## Hiểu & kiến thức

### B1 — Hiện trạng (đo thật, 2026-09-06 13:26)

Tên binary agent-lsp mong đợi, lấy từ `agent-lsp doctor`:

| Ngôn ngữ | Binary | Có chưa | Đường cài | Tiền đề |
|---|---|---|---|---|
| dockerfile | `docker-langserver` | ✗ | ~~npm~~ → **`brew install docker-language-server`** (user chọn 4B) | bottle, không cần Go |
| javascript | `typescript-language-server` | ✗ | npm `typescript-language-server@6.0.0` | đã có node/npm |
| yaml | `yaml-language-server` | ✗ | npm `yaml-language-server@1.24.0` | đã có node/npm |
| go | `gopls` | ✗ | ~~`brew install gopls`~~ → **`brew install go` + `gopls`** | **ĐÃ SỬA ở B2 mục 1**: gopls cần lệnh `go` lúc chạy |
| csharp | `csharp-ls` | ✗ | `dotnet tool install -g csharp-ls` | **cần .NET SDK — máy CHƯA có** |
| html | `vscode-html-language-server` | **✓ đã có** | — | chỉ cần thêm vào args |
| css | `vscode-css-language-server` | **✓ đã có** | — | chỉ cần thêm vào args |

Máy hiện có: node v24.20.0 + npm 12.0.2 (nvm), brew 6.0.22. **Không có `go`, không có `dotnet`.**

### B2 — Ba phát hiện quyết định cách làm

1. **agent-lsp chấp nhận language id tuỳ ý.** Đã thử khô `agent-lsp doctor css:... html:...` →
   **cả hai `Status: ok`**. Nên html/css chỉ cần thêm vào args, không cần agent-lsp hỗ trợ sẵn
   (danh sách auto-detect nội bộ của nó không có html/css).
2. **go KHÔNG cần cài Go toolchain.** `brew install gopls` có formula sẵn → tránh kéo về nguyên bộ
   Go compiler chỉ để chạy 1 language server.
3. **csharp là món đắt nhất và đáng ngờ nhất.** `csharp-ls` là dotnet tool, bắt buộc có .NET SDK
   (`brew install --cask dotnet-sdk`, cỡ ~1 GB). Repo này **không có file C# nào**. Đây là điểm cần
   bạn quyết, tôi sẽ nêu rõ trong plan chứ không tự cắt.

### Phát hiện thêm — chưa yêu cầu, chỉ báo

`vscode-langservers-extracted@4.10.0` đã cài sẵn còn cung cấp **2 binary chưa dùng**:
`vscode-markdown-language-server` (8 capability, có `find_symbol` + `find_references`) và
`vscode-eslint-language-server`. Repo này rất nhiều `.md` → markdown server gần như **miễn phí**
(binary đã nằm sẵn trên máy, chỉ thêm 1 dòng args). Sẽ hỏi bạn có muốn thêm không.

### Bài học từ request LSP trước, phải áp lại

- npm global nằm dưới `~/.nvm/versions/node/v24.20.0/lib/node_modules` → **ghim theo phiên bản node**.
  Đổi node sau này là mất hết. Phải ghi rõ trong report.
- Sửa `~/.claude.json` phải vào key **gốc** `mcpServers`, không rơi vào `projects[<cwd>]`.
- Tool `mcp__lsp__*` chỉ nạp lại sau khi restart Claude Code.

## Hỏi đáp

Chờ bạn chọn lane. Hai điểm sẽ hỏi/nêu trong plan: (a) có thực sự cài .NET SDK ~1 GB cho csharp không,
(b) có thêm markdown/eslint vào args luôn không.

---

## Năng lực dùng được

Phân vân → DÙNG. Kiểm kê ngày 2026-09-06: 9 skill trên đĩa (8 khớp bộ lọc, 1 ẩn), cộng skill
built-in trong context. Không xoá bảng này kể cả khi không có dòng DÙNG nào.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-lsp-setup | plugin:tdq-workflow | **DÙNG** | đây chính là lĩnh vực của request: thang 7 bậc, bảng `LANG_SERVER`, cách agent-lsp nhận args |
| tdq-conventions | plugin:tdq-workflow | NỀN | luật chung của workflow |
| tdq-intake / tdq-spec / tdq-plan / tdq-build / tdq-status / tdq-check-status | plugin:tdq-workflow | NỀN | chính là pipeline đang chạy |
| Đã xét 1 skill khác trên đĩa + skill built-in trong context | plugin/built-in | KHÔNG | khác lĩnh vực |

## Hiểu & kiến thức

### B1b — Điều tra code tại chỗ (đo 2026-09-06 13:33)

**Phát hiện lớn nhất: repo này KHÔNG có file nào thuộc 5 ngôn ngữ được yêu cầu.**
Kiểm kê `git ls-files` theo đuôi:

| Đuôi | Số file | Đuôi | Số file |
|---|---|---|---|
| `.md` | 1000 | `.html` | **8** |
| `.py` | 221 | `.png` | 5 |
| `.json` | 144 | `.excalidraw` | 4 |
| `.jsonl` | 39 | `.toml` | 2 |
| `.log` | 33 | `.css` `.js` `.ts` `.go` `.cs` `.yaml` `Dockerfile` | **0** |

→ Việc này **không phục vụ repo hiện tại** mà là dựng sẵn năng lực cho máy. Điều đó hợp lý vì
`args` của MCP `lsp` nằm ở **user scope** `~/.claude.json` → áp cho MỌI project trên máy. Cần bạn
xác nhận đúng ý (câu Q1).

Kèm theo: 1000 file `.md` và 8 file `.html` là con số thật của repo → markdown server và html
server có ích ngay tại đây, khác hẳn 5 ngôn ngữ kia.

### B1c — Thang LSP sẽ KHÔNG đổi sau request này (đọc `scripts/tdq_lsp.py`)

| Cơ chế | Dòng | Hệ quả cho request này |
|---|---|---|
| `EXT_LANG` ngửi đuôi file của project | `:52-62` | dockerfile không có trong bảng; yaml/json **cố ý loại** khỏi phép ngửi |
| `NGUONG_FILE = 3` | `:154` | ngôn ngữ dưới 3 file bị coi là nhiễu, không đòi server |
| Bậc 3 chỉ đòi server cho ngôn ngữ ĐÃ NGỬI THẤY | `:262-279` | repo 0 file go/cs/js/yaml → bậc 3 vẫn chỉ báo "HTML, Python" |
| `LANG_CONFIG`: go/csharp thuộc nhóm **A** | `:107-131` | nhóm A chỉ CẢNH BÁO, không chặn → bậc 7 không tụt |

→ Cài 5 server này **không làm thang 6/7 tốt lên cũng không xấu đi** trên repo này. Lợi ích nằm ở
project khác. Đây là sự thật phải nói thẳng trong spec, không được bán nhầm giá trị.

### B1d — Xung đột với bảng tra của chính repo

`scripts/tdq_lsp.py:67-98` đã có sẵn dòng cài cho 4/5 ngôn ngữ, nhưng **lệch với đường tôi định đi**:

| Ngôn ngữ | Lệnh trong `tdq_lsp.py` | Đường tôi đề xuất | Vì sao lệch |
|---|---|---|---|
| go | `go install golang.org/x/tools/gopls@latest` | `brew install gopls` | máy không có Go toolchain; `go install` bất khả thi |
| csharp | `dotnet tool install -g csharp-ls` | *(chờ research)* | máy không có dotnet |
| javascript | `npm i -g typescript-language-server typescript` | y hệt | khớp |
| yaml | `npm i -g yaml-language-server` | y hệt | khớp |
| **dockerfile** | **không có trong bảng** | brew `docker-language-server` (user chọn 4B) | bảng thiếu hẳn ngôn ngữ này |

→ Sinh ra một hạng mục phạm vi phụ cần bạn quyết (câu Q4): có cập nhật `LANG_SERVER` trong
`tdq_lsp.py` cho khớp thực tế không, hay chỉ đụng `~/.claude.json` rồi để bảng tra lệch tiếp.

### B2 — Research đa hướng (subagent, 4 truy vấn)

Xem đầy đủ tại: `docs/tdq/research/2026-09-06-1326-them-language-server.md` (273 dòng).
Bốn kết luận làm thay đổi kế hoạch:

| # | Kết luận | Bằng chứng | Hệ quả |
|---|---|---|---|
| 1 | **`gopls` BẮT BUỘC có lệnh `go` trên PATH lúc CHẠY** | go.dev/gopls: *"gopls executes the `go` command found using `$PATH`"*; golang/go#41701 panic `go command required, not found` | **Tôi đã nói SAI ở lượt trước.** `brew install gopls` chỉ khai `depends_on "go" => :build` + có bottle arm64 → cài xong được binary **hỏng khi chạy**. Muốn có `go` thì phải `brew install go` trước. |
| 2 | **Không có cách chạy C# LSP mà bỏ được .NET SDK** | cả `csharp-ls` lẫn Roslyn LS đều nạp project qua MSBuild; `dotnet tool install` bản thân là lệnh của SDK | csharp là món đắt nhất: `brew install dotnet` (10.0.400) rồi `dotnet tool install --global csharp-ls` |
| 3 | `csharp-ls` **vẫn sống** (0.27.0, push 2026-09-06); Roslyn LS chính chủ **còn prerelease** | npm/NuGet + GitHub `pushed_at` | chọn `csharp-ls` bây giờ, ghi nhận Roslyn LS là hướng nâng cấp khi GA |
| 4 | `yaml-language-server@1.24.0` cực tươi (2026-09-03); `dockerfile-language-server-nodejs@0.15.0` **đứng yên từ 2025-10-15** | npm `time.modified`, GitHub `pushed_at`, `archived=false` | yaml không do dự; dockerfile có đối thủ chính chủ `docker/docker-language-server` (phủ Dockerfile+Compose+Bake, `brew install docker-language-server` 0.20.1 bottled, **không cần Go**) |

Cảnh báo phụ ghi nhận, chưa hành động: TypeScript đã lên 7.0.2 và TS7 bỏ `tsserver.js` → cả
`typescript-language-server` lẫn `vtsls` sẽ hỏng trên project TS7 trong 6–12 tháng tới.
`vtsls` bị loại: npm đứng ở 0.3.0 từ 2025-12-24, README tự nhận "best-effort".

### B3 — Tên binary đã xác minh khớp 100% với cái agent-lsp mong đợi

| Gói npm | Version | Binary sinh ra |
|---|---|---|
| `dockerfile-language-server-nodejs` | 0.15.0 | `docker-langserver` |
| `typescript-language-server` | 6.0.0 | `typescript-language-server` |
| `yaml-language-server` | 1.24.0 | `yaml-language-server` |

Đã có sẵn trên PATH (`~/.nvm/versions/node/v24.20.0/bin/`), cài 0 đồng: `vscode-html-language-server`,
`vscode-css-language-server`, `vscode-markdown-language-server`, `vscode-eslint-language-server`,
`vscode-json-language-server`. Đĩa trống 400 Gi.

## Hỏi đáp

### Vòng 1 — 2026-09-06 13:45 (gộp vòng scope + vòng chi tiết)

Vòng scope CHẠY, lý do: dấu hiệu 2 — quét khung 9 mặt thấy ≥2 mặt request không nói gì đến
(chi phí toolchain/tương thích, và bảo trì bảng tra `tdq_lsp.py`).

| # | Câu hỏi | Phương án | Người dùng chọn |
|---|---|---|---|
| 1 | Mục đích: repo 0 file thuộc 5 ngôn ngữ — dựng sẵn cho máy? | A đủ cả / B chỉ thứ dùng được ngay / C chỉ món rẻ | **A** — dựng sẵn cho máy, cài đủ cả 5 |
| 2 | Go: có cài `brew install go` không? | A có / B bỏ go | **A** — cài `brew install go` rồi `gopls` |
| 3 | C#: có cài .NET 10 SDK không? | A có / B bỏ csharp | **A** — cài `brew install dotnet` rồi `csharp-ls` |
| 4 | Dockerfile: npm hay brew chính chủ? | A npm / B brew / C cả hai | **B** — brew `docker-language-server` (Docker chính chủ) |
| 5 | Thêm miễn phí typescript + markdown? | A typescript+markdown / B đúng danh sách / C thêm cả eslint | **C** — thêm cả `typescript`, `markdown`, `eslint` |
| 6 | Có sửa bảng `LANG_SERVER` trong `tdq_lsp.py` không? | A có / B không | **A** — sửa bảng `LANG_SERVER` cho khớp |
| 7 | Cây làm việc đang bẩn — xử lý nhánh thế nào? | A commit trước / B làm tiếp nhánh cũ / C tôi tự lo | **C** — user tự commit, KHÔNG mở nhánh mới |

## Kiến thức đã chốt

**Quyết định đã đóng** (2026-09-06 13:50, sau vòng 1):

1. Mục tiêu là **năng lực mức máy**, không phải repo này. Spec phải nói thẳng: thang LSP của repo
   TDQ-Workflow **không đổi** sau request này; giá trị nằm ở project khác.
2. Cài đủ 5 ngôn ngữ user yêu cầu + 4 món thêm (`typescript`, `markdown`, `eslint`, cộng
   `html`/`css` vốn đã nằm trong yêu cầu gốc). Args đi từ **4 → 13 mục**.
3. Đường cài đã chốt:
   - `brew install go` (1.27.1) → `brew install gopls` (0.23.0)
   - `brew install dotnet` (10.0.400) → `dotnet tool install --global csharp-ls` (0.27.0)
   - `brew install docker-language-server` (0.20.1) — **không** dùng npm `dockerfile-language-server-nodejs`
   - `npm i -g typescript-language-server typescript` (6.0.0) — phục vụ cả `javascript` lẫn `typescript`
   - `npm i -g yaml-language-server` (1.24.0)
   - `html`, `css`, `markdown`, `eslint`, `json`: binary đã có sẵn, **không cài gì**
4. Sửa `scripts/tdq_lsp.py` bảng `LANG_SERVER`: dòng `go` đổi sang đường brew, thêm dòng
   `dockerfile`. Đây là **file repo duy nhất** request này chạm tới.
5. **Không mở nhánh request** (user chọn 7C, tự lo commit). `nhanh_request` để trống, làm trên
   `chore/cai-uv-pyenv-graphify`. Không tự commit bất cứ thứ gì.

**Phương án bị loại và lý do:**

| Bị loại | Vì sao |
|---|---|
| `brew install gopls` đơn lẻ | binary hỏng khi chạy — thiếu lệnh `go` (B2 mục 1) |
| Roslyn LS chính chủ cho C# | còn prerelease, bắt buộc cờ `--prerelease`, có rủi ro không tự nạp solution khi chạy standalone |
| npm `dockerfile-language-server-nodejs` | đứng yên từ 2025-10-15; bản brew chính chủ phủ rộng hơn (Compose + Bake) |
| `@vtsls/language-server` | npm đứng ở 0.3.0 từ 2025-12-24, README tự nhận "best-effort" |
| Cài lumen/agent-lsp plugin | ngoài phạm vi; plugin agent-lsp có hook `PreToolUse` sẽ làm tụt bậc 6 |

**Rủi ro kỹ thuật đã biết, phải kiểm ở bước implement:**

| # | Rủi ro | Cách kiểm | Phương án lùi |
|---|---|---|---|
| R1 | `docker-language-server` cần **2 tham số** `start --stdio`, mà args agent-lsp là `<lang>:<binary>,<flag>` — chưa rõ nó có nhận nhiều tham số sau dấu phẩy không | `agent-lsp doctor dockerfile:docker-language-server,start,--stdio` | quay về npm `docker-langserver,--stdio` (phương án 4A) |
| R2 | agent-lsp nhiều khả năng **không truyền được `initializationOptions`** → yaml server chỉ chạy mặc định + SchemaStore; docker server không tắt được telemetry | đọc `--help`/`doctor`, ghi nhận capability thật | chấp nhận mặc định, ghi rõ giới hạn trong report |
| R3 | npm global ghim theo phiên bản node (`~/.nvm/versions/node/v24.20.0`) — nâng node là mất sạch | ghi cảnh báo trong report | không có |
| R4 | `dotnet tool install --global` cần `~/.dotnet/tools` nằm trong `$PATH` | `command -v csharp-ls` sau khi cài | thêm dòng export vào `~/.zshrc` (hỏi user trước) |
| R5 | Tool `mcp__lsp__*` chỉ nạp lại sau khi **restart Claude Code** | nhắc user restart ở report | không có |

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Research bổ sung | **BỎ** | 4 hướng đã trả lời dứt khoát cả 4 câu; phần còn lại là đo tại máy, không phải tra web |
| Spec | **CÓ** | khung bất biến |
| Plan | **CÓ** | khung bất biến; mỗi ngôn ngữ là 1 task có phép kiểm riêng bằng `agent-lsp doctor` |
| Chia subagent | **BỎ** | các bước cài phụ thuộc tuần tự (go trước gopls, dotnet trước csharp-ls) và đều là lệnh mạng; song song không rút ngắn mà làm khó truy vết lỗi |
| QC bằng agent độc lập | **CÓ** | tiêu chí DoD là "13 mục args đều `Status: ok`" — kiểm được khách quan bằng lệnh, đúng việc của agent QC |
| Deep review spec/plan | **BỎ** | phạm vi hẹp, chỉ 1 file repo bị chạm; rủi ro đã liệt kê R1–R5 |
| Implement | **CÓ** | khung bất biến |
| Report | **CÓ** | khung bất biến |
