# RESEARCH — Bump version + export đầy đủ hơn

Lớp search: `tavily-primary` (MCP), 3 truy vấn khác góc nhìn. Không dùng backup/WebSearch.

## Truy vấn 1 — Migrate cấu hình Claude Code sang máy mới, copy file nào

Nguồn: `code.claude.com/docs/en/mcp-quickstart` · `inventivehq.com/knowledge-base/claude/where-configuration-files-are-stored`
· `nickang.com/how-to-sync-claude-code-global-files-across-machines` · `steeman.be/posts/syncing-claude-code-across-multiple-machines`

Điều rút ra:

- Nên copy: `settings.json`, `settings.local.json`, `CLAUDE.md`, `commands/`, `skills/`,
  cấu hình `plugins/`, và `~/.claude.json` cho MCP.
- KHÔNG copy: `.credentials.json` (đăng nhập lại), `statsig/`, `projects/` (session),
  history/debug/shell-snapshots/telemetry — đúng hướng danh sách loại trừ hiện có.
- macOS giữ credential trong Keychain, không nằm trong file → máy đích bắt buộc `claude login`.
- `claude doctor` là lệnh verify sau khi dựng lại. Bundle hiện chưa dùng lệnh này.

## Truy vấn 2 — MCP server ở đâu, khôi phục thế nào bằng CLI

Nguồn: `code.claude.com/docs/en/mcp-quickstart` (bảng scope) · `github.com/anthropics/claude-code/issues/15797`
· `builder.io/blog/claude-code-mcp-servers` · `mcpbundles.com/blog/claude-code-mcp-tools`

Điều rút ra:

- MCP scope `user` nằm ở **`~/.claude.json`, key top-level `mcpServers`** — đúng vị trí
  máy nguồn đang dùng (`tavily-primary`, `tavily-backup`).
- Khôi phục bằng script: `claude mcp add-json <name> '<json>' --scope user`. Có cả
  `claude mcp list` / `claude mcp get <name>` để verify.
- Issue 15797: `~/.claude.json` chứa oauth/history/machineID — **cấm** copy đè nguyên file
  sang máy đích. Chỉ trích `mcpServers` rồi add lại bằng CLI.
- `${VAR}` trong config MCP là cú pháp hợp lệ để giữ key ngoài file — máy nguồn đang dùng
  đúng dạng này (`Bearer ${TAVILY_API_KEY_PRIMARY}`), nên khối `mcpServers` copy được
  mà KHÔNG lộ key.

## Truy vấn 3 — Marketplace local + cài plugin bằng CLI

Nguồn: `code.claude.com/docs/en/plugin-marketplaces` · `codingnomads.com/claude-code-discover-install-plugins-marketplace`
· `github.com/anthropics/claude-code/issues/11278`

Điều rút ra:

- `claude plugin marketplace add <local dir>` hợp lệ và không tương tác — dùng được trong script.
- Marketplace + install là **hai bước riêng**, không có lệnh bulk-install — khớp README hiện tại.
- Issue 11278: bug phân giải path khi source trỏ vào `marketplace.json` thay vì thư mục
  → bundle nên trỏ `tdq-local` vào **thư mục repo**, đúng như Bước 4 đang làm.
- Có thể ghim marketplace theo commit SHA cho cài lặp lại được — hiện bundle không ghim gì.

## Truy vấn 4 — Xác minh lại cú pháp trước khi ghi vào README template

Truy vấn: `claude mcp add-json --scope user restore MCP servers new machine claude doctor`
Nguồn: `github.com/anthropics/claude-code/issues/16728` · `hackernoon.com/navigating-claude-code-mcp-servers-worth-adding`
· kiểm tại chỗ trên máy nguồn với CLI `2.1.221`.

Điều rút ra:

- `claude mcp add-json [options] <name> <json>` còn đúng, cờ scope là `-s, --scope <scope>`
  nhận `local | user | project`, mặc định `local` → README phải ghi rõ `--scope user`.
- `claude doctor` còn đúng, mô tả: kiểm tra sức khoẻ bản cài, đọc settings không cần trust prompt.
- Cảnh báo từ issue 16728: có báo cáo rằng từ `v2.0.8`, `--scope user` ghi sang
  `~/.claude/.claude.json` theo từng project thay vì khoá `mcpServers` ở gốc `~/.claude.json`.
- Kiểm thực tế trên máy này: `~/.claude/.claude.json` KHÔNG tồn tại, `projects[$HOME]`
  không có `mcpServers`, 0 project nào có khối riêng, còn khoá gốc `mcpServers` của
  `~/.claude.json` có đúng 2 server đang Connected. Vậy nguồn mà `claude_export.py` đọc
  là đúng cho bản CLI này. Máy đích dùng bản CLI khác thì `claude mcp list` ở bước verify
  là chỗ phát hiện lệch.

## Kết luận dùng cho spec

1. Khối `mcpServers` copy được an toàn (chỉ chứa `${VAR}`) — lấp được lỗ hổng lớn nhất
   của bundle hiện tại: máy đích không có MCP server nào.
2. Không copy đè `~/.claude.json`; phải dùng `claude mcp add-json ... --scope user`.
3. `claude doctor` bổ sung vào bước verify.
4. Loại trừ nên bám `.gitignore` thay vì liệt kê tay — rsync không tự đọc `.gitignore`.
