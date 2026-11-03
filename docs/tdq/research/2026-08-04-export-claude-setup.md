# Research: 2026-08-04-export-claude-setup

## Truy vấn 1 — Settings hierarchy (global/project/local)
- Nguồn chính thức: https://code.claude.com/docs/en/settings
- Nguồn phụ: agentfactory.panaversity.org, shanraisshan/claude-code-best-practice (GitHub),
  claudefa.st/blog/guide/settings-reference
- Rút ra: thứ tự ưu tiên (cao→thấp): Managed (`managed-settings.json`, IT-deploy) > CLI flags
  > `.claude/settings.local.json` (project, cá nhân, gitignore) > `.claude/settings.json`
  (project, chia sẻ team) > `~/.claude/settings.local.json` (user, cá nhân) >
  `~/.claude/settings.json` (user, mặc định toàn máy). Máy này chỉ có `~/.claude/settings.json`
  (global) và `.claude/settings.json` của riêng project TDQWorkflow — không có
  `settings.local.json` ở đâu, không có `managed-settings.json`. → Export chỉ cần copy đúng
  2 tầng này, không cần xử lý local/managed.

## Truy vấn 2 — Cài lại plugin/marketplace trên máy mới
- Nguồn: https://code.claude.com/docs/en/plugin-marketplaces (chính thức),
  garyj.dev/post/claude-cli-the-missing-manual, GitHub issue anthropics/claude-code#21370
- Rút ra: có CLI non-interactive `claude plugin marketplace add <source>` và
  `claude plugin install <plugin>@<marketplace>` — dùng được trong script, không bắt buộc
  vào UI tương tác. **Chưa có lệnh bulk-install-all** (feature request #21370 còn mở tại
  thời điểm research) → script export phải liệt kê **từng plugin** rồi loop cài lần lượt,
  không thể "cài nguyên marketplace một phát". `/reload-plugins` cần chạy sau khi cài để
  plugin có hiệu lực trong session đang mở.

## Truy vấn 3 — MCP config, secret trong `.mcp.json` / `~/.claude.json`
- Nguồn: codingnomads.com, claudecertificationguide.com, shanraisshan best-practice (GitHub),
  backslash.security blog
- Rút ra: `.mcp.json` (project root) dùng cho server team-shared, hỗ trợ cú pháp `${VAR}` để
  KHÔNG hard-code secret — đây là khuyến nghị chính thức. `~/.claude.json` (user scope) là
  personal, không nên đặt secret ở project scope. Máy này (mục khảo sát #10) đã tuân theo
  đúng khuyến nghị: 2 MCP server `tavily-primary`/`tavily-backup` trong `~/.claude.json` chỉ
  tham chiếu `${TAVILY_API_KEY_PRIMARY}` / `${TAVILY_API_KEY_BACKUP}` qua header, còn giá trị
  thật nằm ở `env` của `~/.claude/settings.json` (hard-code, không đưa vào project git). →
  Export không được copy nguyên giá trị 2 key này; phải để user tự điền lại trên máy mới
  (README hướng dẫn xin key tại tavily.com + set vào settings.json máy mới, hoặc set biến
  môi trường shell).
- Lệnh CLI thêm MCP server: `claude mcp add --transport <stdio|http> --scope <local|project|user> <name> -- <command>` (stdio) hoặc kèm URL (http). Dùng được để script hoá việc thêm lại 2 server tavily trên máy mới nếu muốn tự động (nhưng vẫn cần user tự nhập giá trị 2 API key vào biến môi trường trước).

## Truy vấn 4 — Backup/restore `~/.claude` giữa các máy (cộng đồng)
- Nguồn: jingles.dev (symlink ~/.claude ↔ git repo), GitHub jtklinger/claude-code-backup-guide,
  tommcfarlin.com (rclone), ai.rundatarun.io (rsync/scp giữa máy)
- Rút ra đồng thuận cộng đồng về **loại trừ khi backup/export** (không phải "sản phẩm cấu
  hình" mà là dữ liệu runtime/cá nhân/máy-cụ-thể):
  - Chat history (`history.jsonl`), session transcripts (`projects/*/*.jsonl`), `sessions/`,
    `debug/`, `logs/`, `cache/`, `shell-snapshots/`, `file-history/`, `telemetry/`,
    `image-cache/`, `paste-cache/`, `ide/`, `daemon*` — dữ liệu runtime, tái sinh tự động,
    có thể rất nặng.
  - `machineID`, `userID` trong `~/.claude.json`, và toàn bộ nhánh `projects` (thống kê
    phiên/đường dẫn cá nhân của máy nguồn) — không có ý nghĩa trên máy đích.
  - `oauthAccount` / token đăng nhập — không copy, máy mới tự đăng nhập lại
    (`claude login` hoặc onboarding lần đầu).
  - Plugin cache (`plugins/cache/`, `plugins/plugin-catalog-cache.json`) — cache tải lại
    được, không cần export; chỉ cần export **danh sách** (`installed_plugins.json`,
    `known_marketplaces.json`) để script cài lại.
  - Nên export: `settings.json` (đã lọc secret), `CLAUDE.md`, `plugin-tiers.json`,
    `keybindings.json` (nếu có), `statusline.sh`, `skills/` (user-level custom),
    `.remember/` (memory), `scripts/` (custom script global), danh sách plugin+marketplace
    đã cài, và toàn bộ project-level `.claude/` + repo liên quan (ở đây là chính
    `TDQWorkflow`, đã là git repo local).

## Truy vấn 5 — Claude Code trên Windows: bắt buộc WSL2 hay hỗ trợ native?
- Nguồn chính thức: https://code.claude.com/docs/en/setup ("Set up on Windows")
- Rút ra: Claude Code hỗ trợ **3 lựa chọn chính thức** trên Windows, KHÔNG bắt buộc WSL:
  - **Native Windows** — không cần gì thêm (Git for Windows optional), cài qua
    `winget install Anthropic.ClaudeCode` hoặc npm; KHÔNG hỗ trợ sandboxing.
  - **WSL 2** — cần bật WSL2; hỗ trợ đầy đủ sandboxing; khuyến nghị khi cần toolchain Linux.
  - **WSL 1** — fallback khi không dùng được WSL2, không hỗ trợ sandboxing.
  → README export nhánh Windows nên đưa **native Windows (winget/npm)** làm phương án
  chính (đơn giản nhất), WSL2 là phương án phụ khi cần sandbox — sửa lại giả định trước đó
  ("Windows phải qua WSL") cho đúng với tài liệu chính thức.

## Truy vấn 6 — Cài Codex CLI đa nền (macOS/Linux/Windows)
- Nguồn chính thức: https://learn.chatgpt.com/docs/codex/cli (OpenAI); đối chiếu thêm
  itecsonline.com (2 bài, macOS/Linux + Windows), tech-insider.org
- Rút ra: Codex CLI có **4 cách cài chính thức**, đều đa nền, không phụ thuộc app ChatGPT
  desktop (cách máy nguồn đang dùng chỉ là 1 lối tắt macOS-only, không phải cách cài
  chuẩn):
  1. Standalone installer (macOS/Linux): `curl -fsSL https://.../install.sh | sh` (không
     cần Node).
  2. npm (đa nền, kể cả Windows): `npm install -g @openai/codex`.
  3. Homebrew (macOS/Linux có brew): `brew install --cask codex`.
  4. Windows: PowerShell one-liner tương đương installer, hoặc npm, hoặc tải binary trực
     tiếp từ GitHub Releases; WSL2 vẫn dùng được nếu muốn nhưng không bắt buộc.
  → README export dùng cách **npm** làm phương án chung cho cả 3 OS (đơn giản, 1 lệnh, đã
  có Node.js là dependency bắt buộc khác trong bundle rồi), liệt kê thêm standalone
  installer làm phương án không cần Node cho macOS/Linux.
