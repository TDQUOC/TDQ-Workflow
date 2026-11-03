# Dọn máy user khỏi lumen — 2026-10-07 (P7)

Làm SAU khi `tdq_test.py tron-bo` xanh (127 module, 0 đỏ, 22:02). User đã chọn 2A, 2B, 2C.

## Bản sao trước khi sửa
- `~/.claude/settings.json.truoc-tdq-20261007220249.bak` (có)
- `~/.codex/config.toml.truoc-tdq-20261007220249.bak` (có)
- `~/.claude/CLAUDE.md.truoc-tdq-20261007220249.bak` (có)

## Đã làm
| Việc | Lệnh | Kết quả |
|---|---|---|
| Gỡ plugin Claude Code | `claude plugin uninstall lumen@claude-plugins-official` | `✔ Successfully uninstalled plugin: lumen (scope: user)` (mục `enabledPlugins` tự biến mất) |
| Bỏ MCP lumen của Codex | `codex mcp remove lumen` | `Removed global MCP server 'lumen'.` |
| Bỏ env | sửa JSON `~/.claude/settings.json` | bỏ `OLLAMA_HOST`, `LUMEN_EMBED_MODEL` (khối `env` rỗng nên bỏ luôn) |
| Dừng MCP lumen của phiên đang chạy | `taskkill /PID 22876 /F` | khoá file cache được nhả |
| Xoá dữ liệu | `rm -rf` cache plugin (85 MB), `~/.local/share/lumen` (418 MB), `~/.config/lumen` | cả 3 không còn |
| Xoá model | `ollama rm qwen3-embedding:0.6b` | `deleted 'qwen3-embedding:0.6b'` (639 MB); ollama và các model khác giữ nguyên |
| Khối luật CLAUDE.md toàn cục | `tdq_setup.ghim_huong_dan_tool(~/.claude/CLAUDE.md)` (không chạy `main`) | khối giữa `<!-- TDQ:TOOLS -->` thành bản 3 tầng; diff ngoài khối = rỗng |

## Kiểm sau
```
$ grep -i lumen ~/.claude/settings.json ~/.codex/config.toml   → (rỗng)
~/.claude/settings.json:0
~/.codex/config.toml:0
ls: cannot access '~/.local/share/lumen': No such file or directory
ls: cannot access '~/.config/lumen': No such file or directory
ls: cannot access '~/.claude/plugins/cache/claude-plugins-official/lumen': No such file or directory
qwen3-embedding trong ollama list: 0
```

Ghi chú: `codex mcp remove` ghi lại `config.toml` bằng chuỗi trích đơn TOML (`'C:\...'`) cho các mục khác — giá trị tương đương, đó là cách định dạng của chính Codex CLI.
