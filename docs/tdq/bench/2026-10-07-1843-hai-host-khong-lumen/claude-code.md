# Claude Code khi plugin lumen tắt — 2026-10-07

Bản sao: `git clone --local` ở `%TEMP%/tdq-thu-host`, thêm `docs/tdq/.tdq-san-sang.json` ghi grep/LSP/graphify sẵn sàng, lumen KHÔNG (đúng trạng thái sau khi gỡ plugin).

Lệnh (không sửa `~/.claude/settings.json`):
```
claude -p "<câu hỏi tìm chỗ ghi file nguyên tử, bảo grep trước>" \
  --settings '{"enabledPlugins":{"lumen@claude-plugins-official":false,"tdq-workflow@tdq-local":true}}' \
  --permission-mode bypassPermissions --output-format stream-json --verbose
```

Ghi chú các lần chạy:
- Lần 1: chỉ tắt lumen → plugin TDQ KHÔNG được nạp (TDQ bật theo dự án, bản sao ở thư mục khác) → không có hook, không có giá trị đo. Bỏ.
- Lần 2: thêm `tdq-workflow@tdq-local: true` nhưng có `timeout 600` → tiến trình dừng giữa chừng (exit 127) sau 2 lượt chặn. Bỏ, chạy lại.
- Lần 3 (dưới đây): chạy hết, `FINAL success`, 12 lượt, 0,26 USD.

## Diễn biến lần 3 (trích từ stream-json)
```
INIT tool lumen: [] | tong tool 170
INIT mcp: [('cloudcli-browser', 'connected'), ('lsp', 'connected'), ('claude.ai Claude Docs', 'connected'), ('claude.ai Figma', 'connected'), ('claude.ai Google Drive', 'connected')]
INIT plugins: ['pyright-lsp', 'tdq-workflow', 'cc-plugin-agents-md', 'cc-plugin-telemetry', 'cc-plugin-plugin-authoring']
TOOL_USE Skill {"skill": "tdq-workflow:tdq-intake"}
RESULT  Launching skill: tdq-workflow:tdq-intake
TEXT Câu hỏi chỉ đọc, không đổi repo → thuộc tier `nhỏ`, trả lời luôn. Tìm bằng grep trước:
TOOL_USE Grep {"pattern": "os\\.replace|\\.replace\\(tmp|NamedTemporaryFile|mkstemp|Move-Item|rename\\(|\\.tmp\\b", "output_mode": "content"}
RESULT ERR PreToolUse:Grep hook error: [TDQ:SEARCH] Code search before any concept query in this request. | Ask first: lumen semantic_search with a natural-language query (what/how/where) — mcp__plugin_lumen_lumen__semantic_search in Claude Code, mcp__lumen__semantic_search in Codex; mcp__lsp__find_symbol / find_references (a symbol and its callers); or graphif
TOOL_USE ToolSearch {"query": "lumen", "max_results": 10}
RESULT  No matching deferred tools found
TEXT Không có tool lumen. Thử tầng LSP theo yêu cầu của hook:
TOOL_USE ToolSearch {"query": "select:mcp__lsp__find_symbol", "max_results": 1}
RESULT  [{"type": "tool_reference", "tool_name": "mcp__lsp__find_symbol"}]
TOOL_USE mcp__lsp__find_symbol {"query": "atomic"}
RESULT ERR LSP client not initialized; call start_lsp first
TEXT Tầng LSP chết (chưa khởi động), lumen không có → theo luật thì rơi xuống grep. Thử lại:
TOOL_USE Grep {"pattern": "os\\.replace|NamedTemporaryFile|mkstemp|\\.tmp\\b", "output_mode": "content"}
RESULT ERR PreToolUse:Grep hook error: [TDQ:SEARCH] Code search before any concept query in this request. | Ask first: lumen semantic_search with a natural-language query (what/how/where) — mcp__plugin_lumen_lumen__semantic_search in Claude Code, mcp__lumen__semantic_search in Codex; mcp__lsp__find_symbol / find_references (a symbol and its callers); or graphif
TOOL_USE Bash {"command": "graphify query \"ghi file nguyen tu: ghi file tam roi replace vao file dich\" 2>&1 | head -40", "description": "Query graphify for atomic file write code"}
RESULT  Graph: graphify-out/graph.json (1791 nodes) | Traversal: BFS depth=2 | Start: ['Ghi các món chưa xử lý được vào `docs/tdq/no-phu-thuoc.md`, không nhân bản dòng…', 'Ghim bản ngắn của luật 4 tầng vào instruction user-level, trong một khối có dấu…', 'Sinh layout agy THẲNG vào `dich` trên chính máy sẽ chạy nó. Đây là thứ thay cho…', 'kiem_dich()', 'Fil
TEXT Graphify trả lời được. Giờ grep tên chính xác:
TOOL_USE Grep {"pattern": "os\\.replace\\(|\\.replace\\(\\w*(path|dich|file|p)\\w*\\)|mkstemp|NamedTemporaryFile", "output_mode": "content", "glob": "*.py"}
RESULT  scripts\claude_export.py:465:        os.replace(tmp, final) | scripts\plugin_tiers.py:98:        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path) or ".", | scripts\plugin_tiers.py:103:        os.replace(tmp, path) | scripts\tdq_setup.py:456:        os.replace(tam, duong) | scripts\tdq_state.py:406:                os.replace(path, broken) | scripts\tdq_st
TOOL_USE Grep {"pattern": "\\.(replace|rename)\\((tam|tmp|dich|duong|path|final)\\b|tmp\\.replace|tam\\.replace|\\.tmp[\"']", "output_mode": "content", "glob": "*.py"}
RESULT  scripts\claude_export.py:456:    tmp = final + ".tmp" | scripts\claude_export.py:465:        os.replace(tmp, final) | scripts\plugin_tiers.py:99:                                   prefix=".settings-", suffix=".tmp") | scripts\plugin_tiers.py:103:        os.replace(tmp, path) | tests\test_claude_export.py:503:        self.assertFalse(os.path.exists(target +
TEXT Xem tên hàm bao quanh từng chỗ:
TOOL_USE Bash {"command": "sed -n '445,470p' scripts/claude_export.py; echo ----; sed -n '90,108p' scripts/plugin_tiers.py; echo ----; sed -n '440,460p' scripts/tdq_setup.py; echo ----; sed -n '
RESULT      for key, value in values.items(): |         text = text.replace("{{" + key + "}}", value) |     with open(os.path.join(dest, "README.md"), "w", encoding="utf-8") as f: |         f.write(text) |     log(f"ghi README.md ({len(manifest['plugins'])} plugin, " |         f"{len(manifest['marketplaces'])} marketplace)") |  |  | def make_zip(dest): |     """Compress to 
TEXT Có 4 chỗ ghi file kiểu này: ghi hết ra file tạm nằm cùng thư mục với file đích, rồi dùng `os.replace` thay vào file đích.

| # | Hàm | Dòng tạo file tạm | Dòng thay vào file đích | Ghi chú |
|---|---|---|---|---|
| 1 | `_atomic_write(path, text)` | `scripts/tdq_state.py:492` (`tempfile.mkstemp(dir=os.path.dirname(path), prefix=".tdq-", suffix=".tmp")`) | `scripts/tdq_state.py:496` | Ghi `state.json`. Khối `finally` xoá file tạm nếu còn sót |
| 2 | `_write_settings(data, path)` | `scripts/plugin_tiers.py:98` (`mkstemp`, prefix `.settings-`) | `scripts/plugin_tiers.py:103` | Trước khi ghi, sao bản cũ ra `.bak` |
| 3 | `ghi_san_sang(project, data)` | `scripts/tdq_setup.py:450` (`f"{duong}.{os.getpid()}.tmp"`) | `scripts/tdq_setup.py:456` | Ghi file mốc sẵn sàng (stamp) để hook đọc. Tên file tạm có PID |
| 4 | `make_zip(dest)` | `scripts/claude_export.py:456` (`final + ".tmp"`) | `scripts/claude_export.py:465` | Nén ra `.zip.tmp`. Lỗi giữa chừng thì `except BaseException` xoá file tạm, file zip cũ còn nguyên |

Hai chỗ trông giống nhưng không thuộc loại này:
- `scripts/tdq_state.py:406` cũng gọi `os.replace(path, broken)`, nhưng chỉ để dời file state hỏng sang chỗ khác, không phải ghi file mới.
- `_ghi()` ở `scripts/tdq_worktree_registry.py:188` ghi thẳng vào file đích bằng `open(duong, "w")`, nên vẫn có thể để lại file ghi dở.

**(1) MCP tool có chữ "lumen":** không có tool nào. `ToolSearch("lumen")` trả về "No matching deferred tools found", và danh sách tool đang có cũng không có tool nào chứa chữ lumen. Chữ này chỉ xuất hiện trong thông báo của hook, ở hai tên `mcp__plugin_lumen_lumen__semantic_search` và `mcp__lumen__semantic_search`, nhưng hai tool đó không có trong phiên này.

**(2) Lời gọi bị hook chặn:** có, 2 lần gọi `Grep`, cả hai bị hook PreToolUse chặn với cùng lý do. Nguyên văn:

```
PreToolUse:Grep hook error: [TDQ:SEARCH] Code search before any concept query in this request.
Ask first: lumen semantic_search with a natural-language query (what/how/where) 
FINAL success cost 0.25754 turns 12
```

## Đọc kết quả
- **Khởi động**: bình thường. `INIT tool lumen: []`, MCP `lsp` connected, plugin `tdq-workflow` nạp. Hook SessionStart in `[TDQ:NEXT]` như thường.
- **Search gate**: CHẶN grep 2 lần (`[TDQ:SEARCH] Code search before any concept query`) — đúng luật. Thông báo chặn mở đầu bằng `Ask first: lumen semantic_search …` → agent tốn 1 lượt `ToolSearch("lumen")` vô ích.
- **LSP**: `mcp__lsp__find_symbol` trả `LSP client not initialized; call start_lsp first` → agent kết luận "tầng LSP chết" và grep lại, bị chặn lần 2 (lời gọi LSP lỗi không được tính là đã hỏi tầng khái niệm).
- **graphify**: `graphify query` qua Bash trả lời → mở khoá; grep sau đó chạy.
- **Kết quả**: đúng đích `scripts/tdq_state.py` `_atomic_write` (cùng 3 chỗ tương tự). Hoàn thành được, nhưng mất ~4 lượt thừa (2 lượt bị chặn, 1 ToolSearch lumen, 1 LSP chưa khởi động).
