# Research — cấu hình gốc dự án của language server, theo ngôn ngữ

Request: `2026-09-03-0053-sua-luat-va-kiem-lsp-that` · phase analyze
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Câu hỏi: bậc kiểm mới phải tìm file nào cho mỗi ngôn ngữ, để biết language server có gốc dự án
đúng hay không.

## Truy vấn 1 — cách các client LSP xác định gốc dự án

Nguồn: <https://www.opencode.asia/source-code/lsp> (phân tích module LSP của opencode, 30+
server) · <https://go.dev/gopls/workspace> (tài liệu chính thức gopls) ·
<https://rust-analyzer.github.io/book/configuration.html> (tài liệu chính thức rust-analyzer).

Mọi client LSP đều dùng cùng một cơ chế: **đi ngược cây thư mục từ file đang mở, tìm "root
marker"** — một file mốc đặc trưng cho ngôn ngữ. opencode liệt kê nguyên văn:

- frontend (TS, Deno, Vue, Astro, Svelte): `package.json`, `tsconfig.json`, `deno.json`
- systems (Go, Rust, C/C++, Swift): `go.mod` / `Cargo.toml` / `compile_commands.json` /
  `Package.swift`
- scripting (Python, Java, Kotlin, Ruby): `pyproject.toml`, `setup.py` / `pom.xml` /
  `build.gradle`
- functional (Lua, Zig, Gleam, OCaml, Haskell): `.luarc.json` / `build.zig` / `gleam.toml` /
  `dune` / `hie.yaml`

gopls nói rõ vì sao điều này bắt buộc: *"gopls needs a defined scope in which language features
like references, rename, and implementation should operate"* — không có scope thì đúng những
tính năng workflow này dựa vào (references, rename) không hoạt động đúng.

rust-analyzer xác nhận gốc workspace là **thư mục chứa `Cargo.toml`**.

## Truy vấn 2 — Lua, Java, Ruby, PHP

Nguồn: <https://luals.github.io/wiki/configuration> · <https://zed.dev/docs/languages/lua> ·
<https://github.com/LuaLS/lua-language-server/wiki/Libraries>.

`.luarc.json` đặt ở **gốc workspace** khai `workspace.library` — chính là khái niệm "gốc import"
của Lua. Tài liệu chính thức của LuaLS ghi root marker là `.luarc.json`, `.luarc.jsonc`,
`.luacheckrc`, `.stylua.toml`, `.git`. Một thảo luận trên helix ghi lại đúng triệu chứng của
repo này: đặt `.luarc.json` sai chỗ → server chỉ thấy file đang mở trong buffer.

## Điều rút ra — hai nhóm ngôn ngữ, và chỉ một nhóm nguy hiểm

**Nhóm A — file mốc là manifest build, gần như luôn có sẵn.** Go (`go.mod`), Rust
(`Cargo.toml`), Java (`pom.xml`/`build.gradle`), C# (`*.csproj`/`*.sln`), Elixir (`mix.exs`),
Gleam (`gleam.toml`), Dart (`pubspec.yaml`), Zig (`build.zig`), Swift (`Package.swift`), PHP
(`composer.json`), Ruby (`Gemfile`), Scala (`build.sbt`). Không có file này thì dự án **không
build được**, nên lập trình viên phát hiện ngay. Bậc kiểm ở đây gần như luôn ĐẠT.

**Nhóm B — cấu hình là TUỲ CHỌN, thiếu thì hỏng âm thầm.** Python
(`pyrightconfig.json`/`pyproject.toml`/`setup.py`), TypeScript/JavaScript
(`tsconfig.json`/`jsconfig.json`/`package.json`), Lua (`.luarc.json`), C/C++
(`compile_commands.json`/`compile_flags.txt`). Bốn nhóm này **chạy được mà không cần cấu hình**,
nên không ai phát hiện ra là chỉ mục liên file đang chết.

Đây chính xác là chỗ repo TDQWorkflow sập: Python, không có `pyrightconfig.json`, chạy tốt, test
xanh, thang báo 6/6 ĐẠT — mà độ phủ truy vấn quan hệ chỉ 7 %. Xem báo cáo
`2026-09-03-0017-them-pyrightconfig-do-lai`.

**Kết luận cho thiết kế**: bậc kiểm mới có giá trị cao nhất ở nhóm B và gần như vô ích ở nhóm A.
Nhưng kiểm cả hai nhóm rẻ như nhau (chỉ là `os.path.exists`), nên khác biệt không nằm ở việc
kiểm hay không mà ở **mức nghiêm trọng**: nhóm A thiếu → dự án hỏng sẵn rồi, chỉ cần cảnh báo;
nhóm B thiếu → đúng cái bẫy đã cắn repo này.

**Điều research KHÔNG trả lời được**: không nguồn nào nói cách kiểm chỉ mục "có hoạt động thật
không" mà không gọi vào chính language server. Xác nhận ràng buộc đã nêu ở brief — script Python
không gọi được MCP, nên phần kiểm bằng hiệu ứng phải là luật cho agent, không thể là bậc script.
