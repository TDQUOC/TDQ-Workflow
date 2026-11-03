# Codex: hook TDQ chạy thật — 2026-10-07 (T6.3)

Bản sao `%TEMP%/tdq-sau-codex`; `.codex/hooks.json` ghi bằng chính `tdq_codex_mcp.khai_hook_codex` (như với một dự án của user): PreToolUse `Bash` (search_gate + search_observe), PreToolUse/PostToolUse `.*lsp.*` (search_observe), UserPromptSubmit. Dấu mốc sẵn sàng 3 tầng. Cùng câu hỏi với request 1843.

Hai điều kiện của `docs/tdq/research/2026-10-07-2041-hook-codex.md` được đáp ứng bằng cờ theo lần chạy (không sửa cấu hình user):
```
codex exec -C <bản sao> --dangerously-bypass-approvals-and-sandbox --dangerously-bypass-hook-trust --json "<câu hỏi>"
```

## Sổ tìm kiếm của bản sao (`docs/tdq/.tdq-search.jsonl`) — toàn bộ
```
{"ts": 1791384758.9808197, "khoa": "phien:01a116d9-915b-74d0-aa4f-7e2d4885d3df", "loai": "tim", "cho_phep": false, "tinh_cua_so": false, "doan_mo": true}
{"ts": 1791384786.743122, "khoa": "phien:01a116d9-915b-74d0-aa4f-7e2d4885d3df", "loai": "khai_niem", "cong_cu": "lsp:find_symbol"}
{"ts": 1791384802.2653847, "khoa": "phien:01a116d9-915b-74d0-aa4f-7e2d4885d3df", "loai": "tim", "cho_phep": true, "tinh_cua_so": true, "doan_mo": true}
{"ts": 1791384816.059618, "khoa": "phien:01a116d9-915b-74d0-aa4f-7e2d4885d3df", "loai": "tim", "cho_phep": true, "tinh_cua_so": true, "doan_mo": true}
```

## Diễn biến (trích)
```
ERROR `--dangerously-bypass-hook-trust` is enabled. Enabled hooks may run without review for this invocation.
ERROR `--dangerously-bypass-hook-trust` is enabled. Enabled hooks may run without review for this invocation.
ERROR Model metadata for `sonnet-4-6` not found. Defaulting to fallback metadata; this can degrade performance and cause issues.
AGENT_MESSAGE Tìm bằng `grep` trước, rồi đối chiếu hàm và dòng; không sửa file.
CMD "C:\\WINDOWS\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command "Get-Content -Raw 'C:\\Users\\admin\\.codex\\plugins\\cache\\tdq-local\\tdq- exit 0 --- | name: tdq-intake | description: Open a new TDQ request - record the ask, pick the lane, init state, analyse + interview until nothin
AGENT_MESSAGE Đang quét literal bằng `git grep`: file tạm, `Rename`, `CreateTemp`, ghi atomically.
AGENT_MESSAGE `git grep` bị hook chặn trước khi chạy. Dùng LSP tìm symbol liên quan, rồi grep lại theo tên đã xác định.
MCP lsp start_lsp {"root_dir": "C:\\Users\\admin\\AppData\\Local\\Temp\\tdq-sau-codex", "ready_timeout_seconds": 10} ok
MCP lsp find_symbol {"detail_level": "hover", "limit": 50, "query": "CreateTemp"} ok
CMD "C:\\WINDOWS\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command "git grep -n -I -E 'CreateTemp|TempFile|tempfile|NamedTemporaryFile|mkstemp| exit 0 .taskmaster/templates/example_prd.txt:35:- Properly pacing and scoping each feature so it is atomic but can also be built upon and improve
CMD "C:\\WINDOWS\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command "git grep -n -I -E 'NamedTemporaryFile|mkstemp|os\\.replace|os\\.rename|os\\ exit 0 .opencode/plugins/tdq-workflow.js:43:  const moc = new Date().toISOString().replace(/\.\d+Z$/, ''); | .opencode/plugins/tdq-workflow.js:61
AGENT_MESSAGE Đã thấy ứng viên trong `scripts/tdq_state.py`, `scripts/tdq_setup.py`, `scripts/plugin_tiers.py`. Đọc phạm vi hàm để chốt tên và dòng.
CMD "C:\\WINDOWS\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command '$files = @('"'scripts/tdq_state.py','scripts/tdq_setup.py','scripts/plugin_ exit 0 --- scripts/tdq_state.py | 394:            raw = f.read() | 395:    except OSError: | 396:        return None | 397:    try: | 398:       
CMD "C:\\WINDOWS\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command '$ranges = @(@('"'scripts/tdq_state.py',488,505), @('scripts/tdq_setup.py',4 exit 0 --- scripts/tdq_state.py | 488: | 489: | 490:def _atomic_write(path, text): | 491:    os.makedirs(os.path.dirname(path), exist_ok=True) | 
AGENT_MESSAGE - `scripts/tdq_state.py:490` — `_atomic_write`
- `scripts/tdq_setup.py:442` — `ghi_san_sang`
- `scripts/plugin_tiers.py:91` — `_write_settings`
- `scripts/claude_export.py:453` — `make_zip`

Không sửa file.

Có 1 lời gọi tool bị hook chặn. Nguyên văn lý do:

```text
Command blocked by PreToolUse hook: [TDQ:SEARCH] Code search before any concept query in this request.
Ask first: mcp__lsp__find_symbol / find_references (a symbol and its callers; if it answers "LSP client not initialized", call mcp__lsp__start_lsp with the project root first); or graphify query "<question>" (a concept in plain words, or the architecture).
Then exact names may be grepped for the next 10 searches; a name the user typed in the prompt is exempt.
```
TURN {"type": "turn.completed", "usage": {"input_tokens": 380371, "cached_input_tokens": 256256, "cache_write_input_tokens": 0, "output_tokens": 2714, "reasoning_output_tokens": 1215}}
```

## Đọc kết quả
- **Q5 ĐẠT dưới hai điều kiện**: 4 dòng sổ mang khoá phiên Codex `phien:01a116d9-…` (trước: 0). Cổng chặn `git grep` đầu tiên (`cho_phep: false`), lời gọi `find_symbol` được ghi `khai_niem` qua matcher `.*lsp.*`, hai lần grep sau được cho qua — đúng luật.
- Tên tool shell Codex chuyển cho hook là `Bash` (đo bằng hook dò ở T3.1) — khớp matcher.
- Lần chạy này dùng lời nhắc TRƯỚC lần sửa thứ hai của T6.2 (`start_lsp` đặt sau); lời nhắc mới chỉ đổi thứ tự câu, không đổi đường ghi sổ.
- Không có hai điều kiện (mặc định trên máy này) thì hook không chạy — xem lệch #1 (Q5).
