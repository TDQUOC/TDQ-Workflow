# Research: clone-setting-to-codex — cấu trúc/khả năng cấu hình thật của Codex CLI (2026)

Nguồn: Tavily search + extract, kiểm tra alive bằng curl (2026-08-05). Slug: `2026-08-05-clone-setting-codex`.

## Truy vấn đã chạy
1. `OpenAI Codex CLI config.toml schema mcp_servers approval_policy sandbox_mode profiles` (domain: github.com, developers.openai.com)
2. `Codex CLI AGENTS.md instructions file discovery global project priority`
3. `Codex CLI skills SKILL.md "codex skills" official documentation`
4. `Codex CLI plugin marketplace manifest "codex plugin add" hooks lifecycle events official`
5. `developers.openai.com codex config mcp_servers command args env official reference`
6. `developers.openai.com codex hooks SessionStart PreToolUse configuration reference stable`
7. tavily-extract: `developers.openai.com/plugins/build/plugins`, `learn.chatgpt.com/docs/config-file/config-reference`, `developers.openai.com/codex/enterprise/managed-configuration`

## Câu 1 — config.toml schema chính thức, vị trí, project-level config
**CÓ nguồn chính thức** (learn.chatgpt.com/docs/config-file/config-reference — trang "Configuration Reference" của OpenAI/ChatGPT Learn, đúng domain docs chính thức Codex).
- File chính: `~/.codex/config.toml` (CODEX_HOME mặc định `~/.codex`, khớp dữ kiện `codex doctor` đã có).
- Có project-level: `.codex/config.toml` trong repo — được nhiều nguồn xác nhận (inventivehq.com, github issue #26207 nói tới `$CODEX_HOME/.config.toml` layer riêng cho profile). Khối hợp lệ ghi nhận qua evidence: `mcp_servers`, `approval_policy`, `sandbox_mode`, `[features]`, `profiles`, `hooks` (bảng lồng, xem câu 5), `plugins.<name>.*`.
- Evidence quote (learn.chatgpt.com): "Key hooks | Type / Values table | Details Lifecycle hooks configured inline in config.toml. Uses the same event schema as hooks.json; see the Hooks guide for examples and supported events." — xác nhận `[hooks]` là khối config.toml chính thức.
- Evidence quote (GitHub issue #17012, openai/codex): nêu rõ published schema hiện chấp nhận `approval_policy`, `sandbox_mode`, `experimental_compact_prompt_file`, `features.child_agents_md`, `mcp_servers.*`, `notice.*`, `plugins.*` — nhưng một số field cũ (`ask_for_approval`, `sandbox`, `experimental_use_rmcp_client`, top-level `[env]`) đang gây lỗi validate (bug đang mở, danh pháp cũ→mới: `ask_for_approval`→`approval_policy`, `sandbox`→`sandbox_mode`).
- Ghi chú: có xu hướng mới "permission profiles" (`allowed_permission_profiles`, `default_permissions`) thay cho `sandbox_mode` cũ ở Codex ≥0.138.0 (nguồn: developers.openai.com/codex/enterprise/managed-configuration, chính thức) — cảnh báo khi build skill clone cần theo field mới, không hardcode field cũ.

## Câu 2 — file instruction tương đương CLAUDE.md
**CÓ, xác nhận nhiều nguồn (không chỉ 1 official nhưng đồng nhất; learn.chatgpt.com config-reference cũng nhắc `AGENTS.md`, `project_doc_fallback_filenames`, `project_doc_max_bytes` — các key config chính thức liên quan)**.
- Tên file: `AGENTS.md` (không phải CLAUDE.md).
- Discovery: 
  1. Global scope: `~/.codex/AGENTS.override.md` nếu có, else `~/.codex/AGENTS.md` — chỉ 1 file cấp global.
  2. Project scope: đi từ git root xuống cwd hiện tại, mỗi thư mục tìm `AGENTS.override.md` rồi `AGENTS.md` rồi fallback filenames (config `project_doc_fallback_filenames`).
  3. File gần cwd hơn có precedence cao hơn (nối chuỗi, phần sau override phần trước khi mâu thuẫn).
  4. Giới hạn kích thước: mặc định 32 KiB tổng (`project_doc_max_bytes`), dừng khi đạt cap.
- Evidence quote (learn.chatgpt.com config-reference, chính thức): "project_doc_fallback_filenames | array | Additional filenames to try when AGENTS.md is missing. | project_doc_max_bytes | number | Maximum bytes read from AGENTS.md" — xác nhận đây là config key thật trong config.toml, không phải suy đoán của blog.
- Claude Code không tự đọc AGENTS.md nhưng có thể import qua `@AGENTS.md` hoặc `/init` (theo nguồn thứ 3, không phải trọng tâm câu hỏi này).

## Câu 3 — khái niệm "skill" tương đương Claude Code Skills
**CÓ — Codex CLI có Agent Skills chính thức, cấu trúc gần như giống Claude Code Skills.**
- Cấu trúc thư mục: `<skill-name>/SKILL.md` (bắt buộc, frontmatter YAML `name` + `description`) + tùy chọn `scripts/`, `references/`, `assets/`.
- Vị trí discover: repo-scoped `.agents/skills/` (quét từ cwd lên tới repo root), cộng "user, admin, and system locations" (nguồn axiomstudio.ai, dẫn lại tài liệu Codex chính thức nhưng bản thân trang là third-party — không tự extract được trang gốc OpenAI trong phiên này).
- Progressive disclosure: chỉ đọc frontmatter lúc khởi động (~50-100 token/skill), tải full SKILL.md khi match description — khớp cơ chế Claude Code Skills.
- Không tìm thấy trang chính thức developers.openai.com riêng cho "Codex Skills" trong kết quả search (các nguồn là blog/third-party: blog.fsck.com, itecsonline.com, axiomstudio.ai, composio-community trên GitHub). Độ tin cậy: khá cao vì nhiều nguồn độc lập mô tả khớp nhau, nhưng **not_found cho "trang chính thức OpenAI mô tả đầy đủ Skills"** — cần phase 2 tìm thêm nếu cần trích dẫn chính thức 100%.
- Skill có thể phân phối qua plugin (`skills/` dir trong plugin) — xem câu 4.

## Câu 4 — "plugin" (`codex plugin add/list/marketplace`)
**CÓ nguồn chính thức**: developers.openai.com/plugins/build/plugins ("Package your plugin" — trang chính thức OpenAI).
- Manifest bắt buộc: `.codex-plugin/plugin.json` (duy nhất field bắt buộc).
- Cấu trúc thư mục plugin:
  - `.codex-plugin/plugin.json` — manifest (required)
  - `skills/<skill-name>/SKILL.md` — optional, bundled skills
  - `hooks/hooks.json` — optional, lifecycle hooks (default path; nếu dùng path này không cần khai `hooks` trong manifest)
  - `.app.json` — optional, mapping MCP server đã đăng ký (registered app connections)
  - `.mcp.json` — optional, cấu hình MCP server bundled kèm plugin (dạng direct map hoặc wrapped `{"mcp_servers": {...}}`)
  - `assets/` — icon, logo, screenshot
- Evidence quote (developers.openai.com/plugins/build/plugins): "Every plugin has a manifest at `.codex-plugin/plugin.json`. It can also include a `skills/` directory, a `hooks/` directory for lifecycle hooks, an `.app.json` file that maps registered MCP server connections, an `.mcp.json` file that configures bundled MCP servers..."
- Evidence quote: "Installing or enabling a plugin doesn't automatically trust its hooks. Plugin-bundled hooks are non-managed hooks, so Codex skips them until the user reviews and trusts the current hook definition." — plugin CÓ THỂ chứa hook, nhưng hook không tự chạy, cần user review/trust (qua `/hooks`).
- Plugin hook nhận biến môi trường `PLUGIN_ROOT`, `PLUGIN_DATA`, và (để tương thích) `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA` — điểm thú vị: Codex tự đặt biến tương thích với format Claude Code plugin.
- "Marketplace snapshot": trang docs.codex-marketplace.com (bên thứ 3, không phải OpenAI) mô tả marketplace lưu metadata, cache plugin tại `~/.codex/plugins/cache/`, bật plugin ghi vào `~/.codex/config.toml`. Đây khớp với `codex doctor`/`--help` đã biết nhưng nguồn không phải chính thức OpenAI — cần dè dặt, chỉ dùng để tham khảo cấu trúc chung.
- Manifest field mẫu (từ codex-marketplace.com/docs, không chính thức nhưng khớp cấu trúc plugin.json chính thức): `name`, `version`, `description`, `author`, `skills`, `mcpServers`, `apps`, `hooks`, `interface.*`.

## Câu 5 — hooks chính thức, GA hay experimental
**CÓ — hooks là tính năng chính thức, đã chuyển sang STABLE (không còn alpha) theo nhiều nguồn, xác nhận qua config-reference chính thức có khối `hooks`/`managed_hooks`.**
- Evidence quote (learn.chatgpt.com/docs/config-file/config-reference, chính thức OpenAI docs): liệt kê các event hợp lệ: "Matcher groups for hook events such as PreToolUse, PermissionRequest, PostToolUse, PreCompact, PostCompact, SessionStart, SessionEnd, SubagentStart, SubagentStop, UserPromptSubmit, or Stop." — đây là **danh sách event hooks chính thức** (nhiều hơn dữ kiện ban đầu SessionStart/PreToolUse/SubagentStart/Stop — thực tế có ít nhất 10 event).
- Cũng có `managed_hooks` (bảng riêng, admin-enforced) dùng cùng schema event.
- Format: hook có thể khai inline trong `config.toml` (khối `[hooks]`) HOẶC file `hooks.json` riêng (project: `.codex/hooks.json`, global: `~/.codex/hooks.json`) — cùng schema JSON: `{"hooks": {"<Event>": [{"matcher": "...", "hooks": [{"type": "command", "command": "...", "statusMessage": "...", "timeout": N}]}]}}`.
- Lịch sử phiên bản (theo nguồn thứ 3 blakecrosley.com, không chính thức nhưng nhất quán với nhiều issue GitHub): hooks bắt đầu experimental ở v0.99.0/v0.100.0 (AfterAgent, AfterToolUse), mở rộng SessionStart/Stop ở v0.114-0.116 (experimental), PreToolUse/PostToolUse ~v0.117.0, UserPromptSubmit ~PR #14626 (tháng 3/2026), và "stable" từ v0.124.0 (23/4/2026) — thời điểm hooks chuyển từ file riêng bắt buộc sang có thể khai inline trong config.toml.
- Lưu ý README của project khác (`SimplifyWorkflow/PluginOutput`) nói "Codex intentionally does not run untrusted project or plugin hooks automatically" — KHỚP với evidence chính thức ở câu 4 (plugin-bundled hooks là non-managed, cần user trust qua `/hooks`). Đây là hành vi có thật của Codex, không phải quy ước tự chế — quy ước tự chế của project đó chỉ là cách tổ chức file (`.codex/hooks.json`, `.codex/rules/*.rules` — phần `.rules` KHÔNG tìm thấy tài liệu chính thức Codex core, có thể là convention riêng của tool `rulesync` bên thứ 3, xem câu 6 note).
- Có bug đang mở liên quan hooks (GitHub #21639 hooks ngừng chạy sau update Desktop; #19385 PreToolUse chưa hỗ trợ `additionalContext`) — cho thấy tính năng vẫn đang biến động dù gọi là "stable".

## Câu 6 — MCP server config format thật, so với Claude Code
**CÓ nguồn chính thức + xác nhận chéo (GitHub commit chính thức openai/codex sửa docs MCP).**
- Khối bắt buộc: `[mcp_servers.<name>]` (đúng — KHÔNG phải `mcpServers` camelCase như Claude Code). Bên trong:
  - stdio: `command` (string, bắt buộc), `args` (array, optional), `env` (table, optional) hoặc `env_vars` (array tên biến forward từ shell, không remap được), `cwd`, `startup_timeout_sec` (mặc định 10s), `tool_timeout_sec` (mặc định 60s), `enabled` (bool).
  - HTTP: `url`, `bearer_token_env_var`, hỗ trợ OAuth (`codex mcp login`).
- Evidence quote (github.com/openai/codex commit 2e95e56, chính thức repo): "IMPORTANT: the top-level key is `mcp_servers` rather than `mcpServers`." (bản cũ) → bản mới: "The top-level table name must be `mcp_servers` ... The sub-table name (`server-name`...) can be anything you would like."
- Khác biệt lớn nhất với Claude Code: Claude Code dùng JSON (`settings.json`/`.mcp.json`, key `mcpServers` camelCase); Codex dùng TOML (`config.toml`, key `mcp_servers` snake_case, bảng con `[mcp_servers.<name>]`). Cấu trúc field tương đương (`command`/`args`/`env`) nhưng cú pháp và tên khối khác hẳn — không thể copy nguyên si, cần chuyển đổi JSON→TOML.
- Enterprise/managed layer (developers.openai.com/codex/enterprise/managed-configuration, chính thức): có thể allowlist MCP server theo `identity` (match `command`/`url` bằng exact/prefix/regex) trong `requirements.toml` — nằm ngoài phạm vi cấu hình user thường, chỉ áp dụng khi admin-managed.

## Tổng kết nguồn chính thức vs không chính thức
| Câu hỏi | Có nguồn chính thức OpenAI? |
|---|---|
| 1. config.toml schema | Có (learn.chatgpt.com/docs config-reference + github.com/openai/codex issue) |
| 2. AGENTS.md discovery | Có phần (config-reference xác nhận key liên quan; discovery order chi tiết từ nguồn thứ 3 nhất quán) |
| 3. Skills tương đương | Không tìm thấy trang chính thức riêng trong phiên search này (chỉ third-party, dù nhất quán) — not_found một phần |
| 4. Plugin structure/manifest | Có (developers.openai.com/plugins/build/plugins — chính thức) |
| 5. Hooks chính thức/stable | Có (config-reference liệt kê event chính thức; lịch sử version từ nguồn thứ 3) |
| 6. MCP server format | Có (commit chính thức openai/codex + config-reference) |
