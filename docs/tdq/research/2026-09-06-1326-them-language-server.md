# Research: chọn + cài language server (csharp, dockerfile, go, javascript, yaml)

- Ngày: 2026-09-06 13:26
- Bối cảnh máy (đã đo, không nghiên cứu lại): macOS darwin 25.5.0 Apple Silicon, brew 6.0.22,
  node v24.20.0 (nvm), npm 12.0.2. KHÔNG có `go`, KHÔNG có `dotnet`.
  Đang dùng `agent-lsp` v0.19.2 (MCP stdio, args `<lang>:<binary>,<flag>`).
  Đã có: clangd, pyright-langserver, vscode-json-language-server, vscode-langservers-extracted@4.10.0.
- Quy ước ghi chú: **[BẰNG CHỨNG]** = có nguồn/lệnh chạy thật; **[SUY ĐOÁN]** = suy luận của tôi.

---

## 1. C# — `csharp-ls` vs `Microsoft.CodeAnalysis.LanguageServer` (Roslyn LSP)

### Truy vấn
- tavily: "csharp-ls vs Microsoft.CodeAnalysis.LanguageServer Roslyn LSP 2026 maintained which to use"
- tavily: "\"roslyn-language-server\" dotnet tool install global standalone C# language server"
- WebFetch: https://github.com/razzmatazz/csharp-language-server
- WebFetch: https://www.nuget.org/packages/roslyn-language-server.osx-arm64
- Lệnh local: `curl api.github.com/repos/razzmatazz/csharp-language-server`, `brew info dotnet`, `brew info --cask dotnet-sdk`

### Nguồn
- https://github.com/razzmatazz/csharp-language-server
- https://www.nuget.org/packages/roslyn-language-server.osx-arm64 (và .linux-arm64, .win-x64)
- https://github.com/anthropics/claude-plugins-official/issues/463
- https://github.com/SofusA/csharp-language-server (dự án wrapper — đã tự tuyên bố DEPRECATED)
- https://github.com/seblyng/roslyn.nvim/issues/303
- https://www.jasonpenniman.com/roslyn-kiro

### Điều rút ra
1. **`csharp-ls` (razzmatazz) VẪN SỐNG KHỎE năm 2026** — **[BẰNG CHỨNG]**
   GitHub API: release mới nhất `0.27.0` publish `2026-08-24`, `pushed_at = 2026-09-06`,
   `archived = false`, 985 sao. Không có banner deprecate trong README.
2. **Yêu cầu .NET của `csharp-ls`: .NET 10 SDK trở lên** — **[BẰNG CHỨNG]** (README:
   "requires .NET 10 SDK or later to be installed on your machine"; vẫn mở được project nhắm
   .NET Core 3 / .NET Framework 4.8). Cài bằng `dotnet tool install --global csharp-ls`.
3. **Microsoft nay đã phát hành Roslyn LSP dạng standalone chính thức** — **[BẰNG CHỨNG]**
   Gói NuGet `roslyn-language-server` (+ biến thể theo RID: `osx-arm64`, `linux-arm64`, `win-x64`).
   Nó là "thin client" bọc và tự bundle `Microsoft.CodeAnalysis.LanguageServer`, chạy
   `roslyn-language-server --stdio --autoLoadProjects`.
   Cài: `dotnet tool install --global roslyn-language-server --prerelease`.
   Đây chính là server mà C# extension của VS Code + C# Dev Kit đang dùng.
4. **NHƯNG `roslyn-language-server` VẪN CÒN PRERELEASE** — **[BẰNG CHỨNG]** trang NuGet
   osx-arm64: bản mới nhất `5.12.0-1.26426.8`, publish `2026-08-27`, và "all available versions
   listed are prerelease builds only" → bắt buộc cờ `--prerelease`.
   Yêu cầu ghi trên NuGet: ".NET 10.0 or later runtime".
5. **Hệ quả về hệ sinh thái**: wrapper cộng đồng `SofusA/csharp-language-server` đã tự đánh dấu
   **Deprecated** với lý do "Microsoft has released official support for running the language server
   outside of vscode, under the name `roslyn-language-server`" — **[BẰNG CHỨNG]**. Tức hướng đi dài
   hạn của cộng đồng là Roslyn LS chính chủ.
6. **Có chạy C# LSP mà KHÔNG cần full .NET SDK không? → THỰC TẾ LÀ KHÔNG.** — **[BẰNG CHỨNG] +
   [SUY ĐOÁN]**
   - Lệnh `dotnet tool install --global` là lệnh của **SDK**, không có trong runtime-only → muốn cài
     theo đường chuẩn thì phải có SDK. **[BẰNG CHỨNG: đây là thiết kế CLI của .NET]**
   - Cả hai server đều nạp project bằng **MSBuild** (csharp-ls đọc `.sln`/`.csproj`; Roslyn LS nhận
     notification `open` với `.sln`/`.slnx`/`.csproj`) → không có MSBuild thì không phân tích được
     project, chỉ còn parse file lẻ. **[SUY ĐOÁN mạnh, dựa trên mô tả kiến trúc trong nguồn]**
   - Đường vòng lý thuyết: tải thẳng gói NuGet `Microsoft.CodeAnalysis.LanguageServer.osx-arm64`
     rồi chạy DLL bằng runtime .NET 10. Kỹ thuật thì được, nhưng vẫn cần .NET 10 runtime + MSBuild
     để hữu ích, và mất cơ chế update. **[SUY ĐOÁN — không khuyến nghị]**
   - Kết luận thực dụng: **`brew install dotnet`** (formula `dotnet`, alias `dotnet@10`, stable
     `10.0.400`, có bottle) là cách gọn nhất; formula này là bản .NET đầy đủ có SDK.
     Cask `dotnet-sdk` cũng cho `10.0.400`. **[BẰNG CHỨNG: `brew info dotnet`, `brew info --cask dotnet-sdk`]**

### Khuyến nghị mục 1
- Cài `.NET 10` trước: `brew install dotnet`.
- **Chọn `csharp-ls`** cho lần cài này: bản ổn định (0.27.0), stable-release thật, không cần cờ
  `--prerelease`, hành xử "một server LSP thuần" đúng kiểu `agent-lsp` mong đợi (stdio, không cần
  extension host). Lệnh: `dotnet tool install --global csharp-ls` → binary `csharp-ls`.
- **[SUY ĐOÁN]** Ghi nhận Roslyn LS là hướng nâng cấp tương lai: khi `roslyn-language-server` ra bản
  GA (bỏ prerelease), nên đổi sang nó vì đó là server chính chủ, phủ tính năng rộng hơn (kể cả Razor).
  Lưu ý nó "không thiết kế để chạy standalone hoàn toàn" — vài hành vi cần client gửi notification
  `open` project, nên với `agent-lsp` có rủi ro không tự nạp solution.

---

## 2. Go — `gopls` có chạy được khi máy KHÔNG có Go toolchain không?

### Truy vấn
- tavily: "gopls requires go toolchain on PATH to work without Go installed"
- Lệnh local: `brew info gopls`, `brew deps --include-build gopls`, tải formula `gopls.rb`

### Nguồn
- https://go.dev/gopls (mục "Supported Go versions")
- https://github.com/golang/go/issues/41701 ("x/tools/gopls: fail gracefully without a Go installation")
- https://github.com/Homebrew/homebrew-core/blob/HEAD/Formula/g/gopls.rb
- https://go.dev/gopls/workspace

### Điều rút ra — ĐÂY LÀ CÂU DỨT KHOÁT
1. **gopls BẮT BUỘC cần lệnh `go` trên `$PATH` lúc chạy.** — **[BẰNG CHỨNG, nguồn chính chủ]**
   go.dev/gopls: *"While running, gopls executes the `go` command found using `$PATH` to obtain
   information about your workspace."* Trang này còn phân biệt rõ 3 phiên bản Go liên quan, trong đó
   có "the `go` toolchain on the `PATH` when gopls is running".
2. **Không có `go` thì gopls hỏng, không phải degrade nhẹ.** — **[BẰNG CHỨNG]**
   golang/go#41701 ghi nhận panic thật:
   `panic: err: go command required, not found: exec: "go": executable file not found in %PATH%`.
   Tên issue "fail gracefully without a Go installation" tự nó xác nhận: không có Go = không dùng được.
3. **gopls chỉ hỗ trợ build system là lệnh `go`** (Bazel không được hỗ trợ chính thức, phải cấu hình
   `go/packages` driver) → càng khẳng định phụ thuộc toolchain. **[BẰNG CHỨNG: gopls README]**
4. **`brew install gopls` KHÔNG kéo theo Go.** — **[BẰNG CHỨNG, quan trọng]**
   Formula `gopls.rb` khai báo `depends_on "go" => :build` — tức Go chỉ là **build dependency**.
   Vì Homebrew có sẵn bottle cho `arm64_tahoe`/`arm64_sequoia` (hash trong formula), máy này sẽ
   **cài bottle, KHÔNG build từ nguồn, KHÔNG cài Go**. `brew deps gopls` (runtime) trả về rỗng;
   chỉ `brew deps --include-build gopls` mới in `go`.
   → Nếu chỉ chạy `brew install gopls`, ta sẽ có binary gopls **hỏng khi chạy** vì thiếu `go`.
5. Phiên bản: `brew info gopls` → stable **0.23.0**, bottled. **[BẰNG CHỨNG]**
6. gopls theo Go Release Policy: chỉ hỗ trợ 2 bản Go major mới nhất. **[BẰNG CHỨNG: go.dev/gopls]**

### Khuyến nghị mục 2
- **Bắt buộc cài Go toolchain trước**: `brew install go`, rồi mới `brew install gopls`
  (hoặc `go install golang.org/x/tools/gopls@latest` sau khi có Go — cách này gopls luôn khớp toolchain).
- Nếu người dùng **không muốn cài Go toolchain** → **không thêm `go` vào agent-lsp**. Không có phương án
  thay thế: không tồn tại Go LSP nào không cần toolchain (gopls là server chính thức và duy nhất
  đáng dùng). **[SUY ĐOÁN dựa trên hệ sinh thái, nhưng rủi ro thấp]**
- Cỡ chi phí: `brew install go` là bottle, vài trăm MB đĩa. **[SUY ĐOÁN]**

---

## 3. JavaScript/TypeScript — `typescript-language-server` vs `vtsls`

### Truy vấn
- tavily: "vtsls vs typescript-language-server 2026 which is better maintained feature coverage"
- Lệnh local: `npm view typescript-language-server version time.modified engines`,
  `npm view @vtsls/language-server version time.modified versions`, GitHub API cả hai repo.

### Nguồn
- https://github.com/yioneko/vtsls
- https://zed.dev/docs/languages/typescript
- https://github.com/helix-editor/helix/issues/13032
- https://github.com/typescript-language-server/typescript-language-server/issues/650
- YouTube "TypeScript 7 + Vue in Neovim: Navigating the Transition (2026)"

### Điều rút ra
1. **Số liệu bảo trì đo thật (2026-09-06)** — **[BẰNG CHỨNG]**
   | | npm version | npm time.modified | repo pushed_at | archived |
   |---|---|---|---|---|
   | `typescript-language-server` | **6.0.0** | 2026-08-20 | 2026-09-06 | false |
   | `@vtsls/language-server` | **0.3.0** | **2025-12-24** | 2026-09-06 | false |
   → Cả hai repo đều còn hoạt động, nhưng **vtsls đã 8+ tháng không ra bản npm mới**, còn
   typescript-language-server vừa lên major 6.0.0 tháng trước.
2. **Độ phủ tính năng: vtsls nhỉnh hơn về nguyên tắc.** — **[BẰNG CHỨNG]**
   vtsls README: "LSP wrapper around TypeScript extension bundled with VSCode. All features and
   performance are nearly the same" — nó fill VSCode API và patch tối thiểu lên chính extension
   TS của VS Code, nên bám sát upstream. Zed **dùng vtsls làm mặc định** cho TS/TSX/JS và xếp
   typescript-language-server là "Alternate Language Server".
   Helix issue #13032: "completion is a lot faster and more reliable" so với tsls.
3. **Điểm yếu của vtsls** — **[BẰNG CHỨNG]** README tự cảnh báo: "no absolute guarantee for its
   robustness … best-effort product but possibly not as reliable as other functionally identical
   alternatives". Zed docs cảnh báo vtsls **có thể hết RAM trên project rất lớn** (Zed phải nâng
   `maxTsServerMemory` mặc định lên 8 GiB). Không hỗ trợ TS plugin từ VSCode extension, không chạy trong browser.
4. **Điểm yếu của typescript-language-server** — **[BẰNG CHỨNG]** issue #650 ghi nhận chậm hơn trải
   nghiệm tsserver trong VS Code, và cộng đồng neovim từng đánh giá nó "một trong những server chậm nhất".
5. **Bối cảnh lớn hơn: TypeScript 7 (tsgo) đang đổi luật chơi** — **[BẰNG CHỨNG một phần]**
   `npm view typescript version` = **7.0.2** (modified 2026-09-05); `@typescript/native-preview`
   = `7.0.0-dev.20260707.2`. Nguồn video 2026 mô tả: TS7 viết lại bằng Go, **bỏ hẳn `tsserver.js`**,
   và chính `tsc` nói LSP trực tiếp (`tsc --lsp`), nvim-lspconfig có entry `ts_go`.
   Hệ quả: cả `typescript-language-server` lẫn `vtsls` đều là wrapper quanh `tsserver` (TS6-), nên
   **trong project chỉ cài TypeScript 7 thì chúng có thể lỗi**. **[BẰNG CHỨNG mức transcript, chưa
   xác minh trên docs chính chủ Microsoft → coi là cảnh báo, không phải kết luận]**
6. Ràng buộc node: `typescript-language-server@6` yêu cầu `node >= 22.22.2`; vtsls yêu cầu `node >= 18`.
   Máy có node v24.20.0 → **cả hai đều chạy được**. **[BẰNG CHỨNG: `npm view … engines`]**

### Khuyến nghị mục 3
- **Chọn `typescript-language-server@6.0.0`** cho lần cài này. Lý do: nhịp release đang đều
  (major mới 2026-08-20 vs vtsls đứng yên từ 2025-12), là lựa chọn "an toàn/bảo thủ", và với
  `agent-lsp` thì thứ ta cần là hover/definition/references — chỗ chênh lệch giữa hai server chủ yếu
  nằm ở completion/refactor nâng cao (thứ agent ít dùng). **[SUY ĐOÁN có cơ sở]**
- `npm i -g typescript-language-server typescript` → binary `typescript-language-server --stdio`.
  Nhớ cài kèm `typescript` global vì server cần tsserver.
- **[SUY ĐOÁN]** Nếu sau này thấy chậm/thiếu tính năng trên repo TS lớn → đổi sang
  `npm i -g @vtsls/language-server` (binary `vtsls --stdio`), cấu hình `maxTsServerMemory` nếu OOM.
- **[CẢNH BÁO]** Theo dõi TS7: khi project chuyển sang TS7, khả năng phải đổi sang `tsgo`/`tsc --lsp`.

---

## 4. Dockerfile + YAML

### Truy vấn
- tavily: "yaml-language-server redhat schema store configuration dockerfile-language-server-nodejs alternative 2026"
- Lệnh local: `npm view dockerfile-language-server-nodejs / yaml-language-server version time.modified`,
  GitHub API cho `rcjsuen/dockerfile-language-server`, `docker/docker-language-server`,
  `redhat-developer/yaml-language-server`, `brew info docker-language-server`
- WebFetch: https://github.com/rcjsuen/dockerfile-language-server

### Nguồn
- https://github.com/rcjsuen/dockerfile-language-server (repo đã đổi tên từ `…-nodejs`, API trả 301)
- https://github.com/docker/docker-language-server
- https://github.com/redhat-developer/yaml-language-server (+ README trên GitHub)
- https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml
- https://zed.dev/docs/languages/yaml
- https://archlinux.org/packages/extra/any/yaml-language-server

### Điều rút ra — Dockerfile
1. **`dockerfile-language-server-nodejs` (rcjsuen) vẫn là chuẩn de-facto, nhưng đã chậm nhịp.**
   — **[BẰNG CHỨNG]** npm version **0.15.0**, `time.modified = 2025-10-15`; repo `pushed_at = 2025-10-15`,
   `archived = false`. Tức ~11 tháng không có commit mới tính tới 2026-09-06.
   README **không** có ghi chú deprecate và **không** trỏ sang dự án khác.
   Binary tên **`docker-langserver`** (không phải `dockerfile-language-server`), chạy `--stdio`.
2. **Đối thủ: `docker/docker-language-server` (chính chủ Docker).** — **[BẰNG CHỨNG]**
   Viết bằng Go, phủ **Dockerfile + Compose + Bake** (rộng hơn hẳn). `pushed_at = 2026-06-22`,
   nhưng release ổn định mới nhất vẫn là **v0.20.1 (2025-10-14)** — tức cũng không ra bản mới gần đây.
   **Cài được bằng brew có bottle**: `brew info docker-language-server` → stable **0.20.1 (bottled)**
   → **KHÔNG cần Go toolchain** để cài (khác hẳn gopls, vì đây là bottle binary và không có
   runtime dependency toolchain). **[BẰNG CHỨNG: brew info]**
3. **[SUY ĐOÁN]** Việc cả hai repo cùng dừng quanh 2025-10 và rcjsuen (tác giả gốc) cũng là người
   trong hệ Docker gợi ý nỗ lực đang dồn về phía Docker; nhưng chưa có tuyên bố chính thức nào
   nói dockerfile-language-server-nodejs bị bỏ.

### Điều rút ra — YAML
4. **`yaml-language-server` (redhat-developer) chắc chắn vẫn là lựa chọn chuẩn, và rất tươi.**
   — **[BẰNG CHỨNG]** npm version **1.24.0**, `time.modified = 2026-09-03` (3 ngày trước);
   repo `pushed_at = 2026-09-03`, `archived = false`. Arch Linux đóng gói 1.24.0 ngày 2026-08-31.
   Zed dùng chính nó làm Language Server cho YAML. Không có đối thủ nào đáng kể. Binary:
   **`yaml-language-server --stdio`**.
5. **YAML server CẦN cấu hình schema mới thực sự hữu ích** — **[BẰNG CHỨNG]**
   - Mặc định `yaml.schemaStore.enable = true` → tự map schema từ JSON Schema Store theo pattern
     tên file thông dụng (đủ tốt cho `docker-compose.yml`, GitHub Actions, k8s…).
   - Thứ tự ưu tiên resolve schema (README): 1) modeline `# yaml-language-server: $schema=...`
     2) property `$schema` inline 3) custom schema provider 4) `yaml.disableSchemaDetection`
     5) `yaml.schemas` 6) `json/schemaAssociations` 7) SchemaStore.
   - Setting quan trọng: `yaml.schemas` (map schema→glob), `yaml.customTags` (bắt buộc cho
     CloudFormation `!Ref`/`!GetAtt`… nếu không sẽ báo lỗi giả), `yaml.yamlVersion` (mặc định 1.2,
     đặt 1.1 cho file cũ), `yaml.format.enable`, `yaml.maxItemsComputed` (mặc định 5000).
   - Hỗ trợ JSON Schema draft-04, draft-07, 2019-09, 2020-12.
6. **[SUY ĐOÁN]** Với `agent-lsp` (args dạng `<lang>:<binary>,<flag>`), nhiều khả năng **không truyền
   được settings LSP dạng JSON** cho yaml server → sẽ chỉ chạy với mặc định + SchemaStore.
   Điều này vẫn hữu ích (validate cú pháp, outline, hover cho file phổ biến), nhưng **cần kiểm chứng
   xem agent-lsp có cơ chế truyền `initializationOptions`/`workspace/configuration` hay không** trước
   khi hứa hẹn tính năng schema tuỳ biến. → **Đây là điểm cần xác minh ở bước implement.**

### Khuyến nghị mục 4
- YAML: `npm i -g yaml-language-server@1.24.0` → `yaml-language-server --stdio`. Không do dự.
- Dockerfile: **`npm i -g dockerfile-language-server-nodejs@0.15.0`** → `docker-langserver --stdio`.
  Lý do chọn cái này thay vì docker/docker-language-server: cùng hệ npm/node (đồng nhất với các
  server khác đang cài), binary nhẹ, và yêu cầu của người dùng là "dockerfile" chứ không phải
  compose/bake. **[SUY ĐOÁN có cơ sở]**
- **[Phương án thay thế]** Nếu muốn phủ luôn Compose + Bake: `brew install docker-language-server`
  (0.20.1, bottled, không cần Go). Có thể cân nhắc thay thế hẳn.

---

## Tổng hợp lệnh cài đề xuất

```sh
# 1. C#  (bắt buộc .NET 10 trước)
brew install dotnet                       # dotnet 10.0.400, có SDK
dotnet tool install --global csharp-ls     # -> binary: csharp-ls

# 2. Go  (BẮT BUỘC có toolchain, gopls không chạy thiếu `go`)
brew install go
brew install gopls                        # gopls 0.23.0  -> binary: gopls

# 3. JavaScript/TypeScript
npm i -g typescript typescript-language-server   # -> typescript-language-server --stdio

# 4. Dockerfile + YAML
npm i -g dockerfile-language-server-nodejs       # -> docker-langserver --stdio
npm i -g yaml-language-server                    # -> yaml-language-server --stdio
```

Lưu ý khi ghép vào `agent-lsp` (args `<lang>:<binary>,<flag>`):
- `csharp:csharp-ls` — **[SUY ĐOÁN]** csharp-ls mặc định dùng stdio, có thể KHÔNG cần cờ `--stdio`;
  cần thử `csharp-ls --help` sau khi cài.
- `go:gopls` — gopls mặc định stdio khi chạy không tham số; cờ phổ biến là `serve`.
- `javascript:typescript-language-server,--stdio`
- `dockerfile:docker-langserver,--stdio` (chú ý tên binary khác tên gói!)
- `yaml:yaml-language-server,--stdio`

## Rủi ro / điểm cần xác minh khi implement
1. `csharp-ls` cần .NET 10 SDK → cài `dotnet` là bước nặng nhất (vài GB). Hỏi người dùng có chấp nhận không.
2. `gopls` vô dụng nếu không cài Go. **Đây là quyết định phải hỏi người dùng**, không tự làm.
3. Tên binary dockerfile là `docker-langserver`, dễ cấu hình sai.
4. `agent-lsp` có truyền được settings (yaml schemas, ts preferences) hay không — chưa xác minh.
5. TS7 đang phá vỡ mô hình tsserver → cấu hình javascript có thể phải làm lại trong 6-12 tháng tới.
