# Research: agent-lsp đa server, tự nhận ngôn ngữ, tsserver "No Project", crash 0xc0000409, monorepo

Ngày: 2026-10-07. Phiên bản đang dùng: agent-lsp 0.19.2 (`C:\Users\admin\.local\bin\agent-lsp.exe`).
Nguồn chính: mã nguồn agent-lsp (clone `--depth 1` HEAD 0.21.0 + tag `v0.19.2`, tại `C:\tmp\alsp-src\agent-lsp`),
issue GitHub của agent-lsp, mã `typescript-language-server` 6.0.1 và `typescript` 5.9.3 cài trong fnm,
log `~/.cache/agent-lsp/spawn-logs/*.log`, và probe LSP thô tự viết (`C:\tmp\alsp-probe\*.py`).

`git diff v0.19.2 HEAD` trên `internal/lsp/manager.go`, `cmd/agent-lsp/{tools_workspace,server,tools_analysis}.go`
không có thay đổi; chỉ `internal/config/{autodetect,parse}.go` thêm vài dòng (MQL). Mọi kết luận định tuyến dưới đây đúng cho 0.19.2.

## Cấu hình hiện tại (`claude mcp get lsp`)

```
Scope: User config
Command: C:\Users\admin\.local\bin\agent-lsp.exe
Args: typescript:...\fnm\aliases\default\typescript-language-server.cmd,--stdio
      python:...\pyright-langserver.cmd,--stdio
      json:...\vscode-json-language-server.cmd,--stdio
      html:...\vscode-html-language-server.cmd,--stdio
```
=> chế độ multi-server (Mode 2), thứ tự entry: typescript (entry[0] = "default"), python, json, html.
`agent-lsp --help` liệt kê: multi-server args, `--config`, `--merge-config`, `--http`, không args = auto-detect;
lệnh `init`, `doctor`, `update`, `uninstall`. `agent-lsp doctor --help` không có help (parser coi `--help` là entry sai định dạng).

---

## Q1. Nhiều server cùng lúc? Định tuyến? start_lsp thay hay thêm?

**Truy vấn**: đọc `internal/lsp/manager.go`, `cmd/agent-lsp/server.go`, `cmd/agent-lsp/tools_workspace.go`, `tools_analysis.go`, `internal/config/parse.go`; issue #55.

**Phát hiện (nguồn: mã)**:
- Có. `ServerManager` giữ một `managedEntry` cho mỗi server (client + tập phần mở rộng + languageID). Các server chạy song song.
- Cấu hình: CLI `lang:binary,arg1,arg2 ...` (tách ở dấu `:` đầu tiên nên `typescript:C:\...` vẫn đúng); `--config file.json` dạng
  `{"servers":[{"extensions":["go"],"command":["gopls"],"language_id":"go"}]}`; `--merge-config` = auto-detect + overlay.
  Phần mở rộng lấy từ `extensionMap` (`parse.go`): typescript→ts,tsx; javascript→js,jsx,mjs,cjs; python→py,pyw; ngôn ngữ
  không có trong bảng (json, html) → phần mở rộng = chính languageID (`json`, `html`; **không** gồm `htm`).
- **Hai kiểu định tuyến**:
  1. Công cụ có `file_path` (open_document, list_symbols, find_references, go_to_definition, ...) → `clientForFile`:
     `resolver.ClientForFile(path)` theo phần mở rộng; nếu client đó chưa khởi tạo thì **rơi về client "hiện hành" `cs`**.
  2. Công cụ không có file (`find_symbol` = workspace/symbol, `get_server_capabilities`, add_workspace_folder, restart...) →
     **luôn dùng `cs.get()`** (client hiện hành), không định tuyến theo ngôn ngữ (`tools_analysis.go:209`).
- `start_lsp` **có** `language_id` → `StartForLanguage`: chỉ (khởi động lại) đúng entry đó, các entry khác **giữ nguyên**,
  rồi `cs.set(client)` — tức **thêm/khởi động lại một server và đổi server "hiện hành"**. Python/TypeScript/JavaScript
  đi qua **daemon broker** (`daemonLanguages` trong `daemon.go`): tiến trình `agent-lsp daemon-broker` tách rời, sống tiếp
  sau khi phiên kết thúc (log thấy pyright "exited cleanly after 30m"), và được dùng lại theo (root, language).
- `start_lsp` **không** `language_id` → `StartAll`: khởi động **tất cả** entry (chế độ trực tiếp, không daemon), `cs` = entry[0].
  Nếu một server khởi tạo lỗi → rollback (shutdown hết những cái vừa bật) và trả lỗi. `StartAll` gán `e.client` mới
  **không shutdown client cũ** → gọi lại nhiều lần có thể rò tiến trình.
- Giải thích quan sát (1): `start_lsp python` rồi `start_lsp html` → pyright vẫn chạy và công cụ theo file `.py` vẫn tới pyright,
  nhưng `find_symbol` đi tới `cs` = html server → 0 kết quả. Đây đúng là **issue #55 (OPEN)** "Multi-server ... routes server-less
  calls (get_server_capabilities, find_symbol) to the default server", tác giả issue đề xuất fan-out hoặc định tuyến theo tài liệu
  dùng gần nhất — chưa sửa ở 0.21.0. CHANGELOG cũng ghi `restart_lsp_server` chỉ restart server mặc định.
- Ngoài lề: `autoInitClient` so `strings.HasPrefix(filePath, rootDir+"/")` — trên Windows đường dẫn `\` không khớp, có thể
  kích `StartAll` ngoài ý muốn khi client theo file chưa khởi tạo (chưa kiểm thực tế).

**Rút ra**: Hỗ trợ đa server, nhưng chỉ công cụ theo file mới định tuyến theo phần mở rộng. Muốn `find_symbol`
đúng ngôn ngữ thì **`start_lsp language_id=<ngôn ngữ cần hỏi>` phải là lệnh gọi cuối cùng** trước `find_symbol`
(hoặc tránh `find_symbol`, dùng `list_symbols`/`find_references` theo file). Độ tin cậy: **cao** (đọc mã + issue #55 + tái hiện).

## Q2. Tự nhận ngôn ngữ khi bỏ `language_id`?

**Nguồn**: `tools_workspace.go:191`, `manager.go` (`StartAll`, `defaultClientLocked`), `internal/config/autodetect.go`, `docs/reference/tools.md:48`.

- **Không có** nhận dạng ngôn ngữ theo nội dung repo trong `start_lsp`. Tài liệu: "Without this, all configured servers are started.
  Use `get_server_capabilities` to diagnose which server is active." Server "hiện hành" = **entry đầu tiên trong danh sách cấu hình**.
- Với cấu hình của user, entry[0] = typescript → giải thích quan sát (2): repo Python + `start_lsp` không language_id
  → bật cả 4 server, `cs` = typescript-language-server (repo không có tsconfig → "No Project"; nếu TS crash → StartAll rollback toàn bộ).
- Chế độ auto-detect (không args): quét PATH cho bảng `knownServers`, thứ tự **alphabet theo languageID**
  (c, cpp, csharp, dockerfile, go, java, javascript, json, kotlin, mql, php, python, ruby, rust, typescript, yaml) → entry[0] là cái
  đầu tiên tìm thấy theo alphabet (issue #55: clangd thành default). Không có "ranking" theo repo.
- Có công cụ riêng `detect_lsp_servers(workspace_dir)` quét ngôn ngữ nguồn + binary, nhưng `start_lsp` không dùng nó.
- `language_id` trên các công cụ theo file chỉ là languageId cho didOpen ("auto-detected from file extension"), không chọn server.

**Rút ra**: luôn truyền `language_id`; nếu muốn mặc định hợp lý thì sắp thứ tự args MCP sao cho ngôn ngữ hay dùng nhất đứng đầu.
Độ tin cậy: **cao**.

## Q3. tsserver "No Project" với workspace/symbol, cách làm cho chạy

**Nguồn**: `typescript-language-server/lib/cli.mjs` 6.0.1 dòng 26127 (`workspaceSymbol`) và 21263 (`lastFileOrDummy`);
`typescript/lib/typescript.js` 5.9.3 `getFullNavigateToItems` (dòng 196308); probe thô `C:\tmp\alsp-probe\ws*.py`.

- tsls gửi `navto` với `file: this.tsClient.lastFileOrDummy()` = `documents.files[0] || workspaceFolders[0].fsPath`.
  Khi chưa mở tài liệu nào, `file` là **thư mục workspace** → tsserver `getProjects` không tìm được project cho "file" đó →
  `ThrowNoProject` → "No Project." Không phải do thiếu tsconfig ở root; là do **chưa có tài liệu mở**.
- Có file mở → tsserver tìm các project chứa file đó và chạy navto trên toàn project (không chỉ file).
- Probe thô (node chạy trực tiếp cli.mjs, repo claudecodeui, query `RUNNING_VERSION`, const ở `server/index.ts`):
  | root | file mở | kết quả |
  |---|---|---|
  | repo root | không | ERROR No Project |
  | server/ | không | ERROR No Project |
  | server/ | server/index.ts | 1 symbol |
  | repo root | server/index.ts | 1 symbol |
  | server/ | src/App.tsx rồi server/index.ts (và ngược lại) | 1 symbol |
  | server/ | chỉ server/shared/utils.ts | 1 symbol |
  => Ở mức tsls, **mở 1 file thuộc project là đủ**, kể cả root ở gốc monorepo; không cần `projectWideIntellisense` hay initOptions.
- **Qua agent-lsp thì khác**: `start_lsp typescript root=server/` (daemon) + `open_document server/index.ts` + `find_symbol RUNNING_VERSION`
  → 0; lặp lại với `start_lsp` không language_id (chế độ trực tiếp) → vẫn 0; nhưng `find_symbol findApplicationRoot`
  (hàm export trong `server/shared/utils.ts`) → 1 kết quả live (`detail_level=hover`, URI `file:///c%3A/...`).
  `GetWorkspaceSymbols` trong agent-lsp không lọc kết quả. Nguyên nhân chưa xác định — nghi `documents.files[0]` của tsls
  trong agent-lsp không phải file vừa mở (agent-lsp/broker có thể đã mở file khác trước, ví dụ qua `WithDocument`), làm navto
  quét project khác. Issue liên quan: #42 (workspace/symbol phụ thuộc tài liệu đã mở; cache `refs.db` có thể che kết quả live),
  #54 (sau restart, workspace symbols rỗng tới khi mở lại tài liệu).
- Không tìm thấy tài liệu chính thức nào về `projectWideIntellisense` liên quan tới navto; tsls không có tuỳ chọn khởi tạo nào đổi
  tham số `file` của navto.

**Rút ra**: "No Project" = hạn chế đã biết của tsls (navto bắt buộc có file ngữ cảnh). Khắc phục: luôn `open_document` một file `.ts`
thuộc đúng project trước `find_symbol`. Nhưng `find_symbol` qua agent-lsp với TS vẫn **không đáng tin** (âm tính giả với const
top-level); dùng `list_symbols`/`find_references`/`go_to_definition` theo file, đối chiếu grep.
Độ tin cậy: **cao** cho cơ chế No Project; **trung bình-thấp** cho nguyên nhân 0 kết quả sau khi mở file.

## Q4. Crash 0xc0000409 khi chạy typescript-language-server qua `.cmd`

**Nguồn**: `~/.cache/agent-lsp/spawn-logs/typescript.log`; `Win32_OperatingSystem`; `procattr_windows.go`; CHANGELOG 0.12.0; probe `probe.py`.

- Log lúc crash (2026-10-07 21:52, root claudecodeui):
  ```
  [error] LSP server ...typescript-language-server.cmd (PID 6380) exited with error after 3s. Last stderr:
  [low_level_alloc.cc : 554] RAW: Check new_pages != nullptr failed: VirtualAlloc failed
  [info] daemon: Initialize FAILED: ... exit status 0xc0000409
  ```
  => node (abseil LowLevelAlloc trong V8/node) gọi `VirtualAlloc` thất bại → abort qua `__fastfail` → mã STATUS_STACK_BUFFER_OVERRUN
  (0xc0000409 là mã chung của fail-fast, không thật sự là tràn stack).
- Bộ nhớ hệ thống lúc kiểm: RAM 32.7 GB (trống 20.3 GB) nhưng **commit còn trống 3.7 GB / 48.7 GB** (pagefile cố định 16 GB).
  Tổng private bytes tiến trình chỉ ~12.7 GB → phần lớn commit thuộc nơi khác (VM `vmmemCmZygote`, driver...). Tức là
  **cạn commit limit**, không phải lỗi shim.
- Shim `typescript-language-server.cmd` là cmd-shim chuẩn của npm (gọi `node.exe ...\lib\cli.mjs %*`), `aliases\default` là junction
  tới `node-versions\v24.21.0\installation` — không phải shim động của fnm. Probe: chạy qua `.cmd` và chạy `node cli.mjs` trực tiếp
  đều initialize thành công ở thời điểm kiểm.
- agent-lsp đã xử lý vấn đề console cho `.cmd` (0.12.0: `CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW`, cố ý không `DETACHED_PROCESS`
  vì cmd.exe cần console). 0.19.2 có cùng cờ.
- Yếu tố làm tăng áp lực bộ nhớ: mỗi tsls bật **2 tsserver** (`--serverMode partialSemantic` + semantic); broker daemon sống
  ~30 phút sau phiên; `StartAll` không shutdown client cũ. Lúc kiểm có 2 broker TS (claudecodeui, claudecodeui/server) + 1 broker python
  vẫn sống, mỗi tsserver ~0.5 GB private.

**Rút ra**: nguyên nhân là `VirtualAlloc` thất bại do commit gần cạn; gọi node trực tiếp (`node.exe ...\cli.mjs --stdio`) chỉ bỏ một lớp
cmd.exe, **không** chữa gốc. Chữa: tăng pagefile (hoặc để system-managed), giảm commit của VM/ứng dụng khác, dọn broker cũ
(`agent-lsp daemon-broker` còn sống), tránh `start_lsp` không language_id lặp lại. Có thể vẫn trỏ thẳng node+cli.mjs cho gọn
(và tránh `title`/cmd.exe), nhưng đó là tối ưu phụ. Độ tin cậy: **trung bình-cao** (bằng chứng trực tiếp từ stderr + số đo commit;
không tìm được tài liệu chính thức nối 0xc0000409 với fnm/cmd-shim).

## Q5. Tính năng cho monorepo

**Nguồn**: `StartLspArgs` (`tools_workspace.go:30-36`), `internal/lsp/scope.go`, mô tả `add_workspace_folder`, `docs/architecture/roadmap.md:864`, README.

- `scope` (trên `start_lsp`): **chỉ có hiệu lực khi có `language_id`**. Sinh file cấu hình tạm ngay tại root: python → `pyrightconfig.json`
  (`include`), typescript → **ghi đè `tsconfig.json` ở root** (sao lưu bản cũ, khôi phục khi shutdown) bằng cấu hình tối giản
  `target ES2020, module commonjs, strict false, include=<scope>/**/*`. Với monorepo dùng `paths`, `NodeNext`, `allowJs`... cấu hình tạm này
  làm mất compilerOptions thật và có nguy cơ để lại file nếu tiến trình chết trước khi khôi phục. Issue #10 (đã đóng) từng có lỗi `include`
  hỏng. Roadmap tự nhận: "The `scope` parameter ... helps with monorepos but doesn't solve the fundamental problem".
- `add_workspace_folder` / `remove_workspace_folder` / `list_workspace_folders`: gửi didChangeWorkspaceFolders tới **client hiện hành `cs`**
  (một server); tài liệu nói gopls, rust-analyzer, typescript-language-server tự index thư mục mới. `get_cross_repo_references` dùng cơ chế này.
- Không có "root theo module": mỗi ngôn ngữ đúng **một client với một root**; định tuyến chỉ theo phần mở rộng, không theo đường dẫn.
  Đổi module = `start_lsp` lại với root khác (daemon được dùng lại theo cặp root+language).
- Thực tế với tsserver: root ở gốc monorepo vẫn được, miễn mở một file trong project con — tsserver tự tìm `tsconfig.json` gần nhất
  của file (probe Q3: root=repo, mở `server/index.ts` → tìm được). `find_references` theo file chạy đúng như grep (quan sát của user).

**Rút ra**: Với monorepo TS, đừng dùng `scope` (ghi đè tsconfig); đặt root = gốc repo hoặc module, mở một file của module cần hỏi rồi dùng
công cụ theo file. Độ tin cậy: **cao** (đọc mã), **trung bình** cho đánh giá rủi ro scope (không chạy thử).

---

## Ghi chú vận hành

- Trong lúc nghiên cứu đã gọi trên MCP `lsp` của phiên: `start_lsp typescript root=C:\Users\admin\Documents\claudecodeui\server`, rồi
  `start_lsp root=...\server` (không language_id → StartAll 4 server), `open_document server\index.ts`. Server hiện hành của phiên vì thế là
  typescript tại `claudecodeui\server`; cần `start_lsp` lại với root/language mong muốn.
- File tạm: `C:\tmp\alsp-src\agent-lsp` (clone), `C:\tmp\alsp-probe\{probe,ws,ws_lc,ws2,ws3}.py`.
- Trong Git Bash, `cd` kích hook fnm và thoát mã 1 (thông báo "We can't find the necessary environment variables") → lệnh sau `cd ... &&` bị bỏ;
  dùng đường dẫn tuyệt đối thay vì `cd`.
