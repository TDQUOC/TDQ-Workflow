# Mini-plan — Validate lại bundle export (quick)

Ngày: 2026-08-05 · Lane: quick · Request: ../requests/2026-08-05-validate-export.md

## Phạm vi
- IN: chạy lại toàn bộ lệnh validate trên bundle HIỆN CÓ tại
  `~/Documents/claude-code-export` (+ `.zip`) — không sửa `claude_export.py`, không
  build lại bundle mới.
- OUT: build lại bundle, sửa code, đổi manifest.

## Task
- [x] **V1** `check` drift — `python3 scripts/claude_export.py check --dest ~/Documents/claude-code-export` — Test: exit 0, in `0 mục lệch` — **FAIL thực tế**: exit 1, 2 mục lệch (`config/installed_plugins.json`, `config/known_marketplaces.json`). Nguyên nhân: `~/.claude/plugins/*.json` bị ghi lại lúc 18:58 (mtime), 4 phút SAU lúc build bundle (18:54). Diff chỉ đổi field `lastUpdated` (mốc sync marketplace), không đổi danh sách plugin/marketplace thật. Ngoài phạm vi quick (không rebuild) — báo cho user quyết định.
- [x] **V2** Toàn vẹn zip — `unzip -t ~/Documents/claude-code-export.zip` — Test: kết thúc bằng "No errors detected" — PASS
- [x] **V3** Cấu trúc bundle còn đủ — `test -d` cho `tdqworkflow-repo/.git`, `mem0-repo/.git`, `config/skills-graphify/`, `config/skills-mem0-memory/`, `config/launch-agents/com.mem0.gateway.plist` — Test: cả 5 tồn tại — PASS
- [x] **V4** Secret scan lại — grep giá trị TAVILY key thật (đọc từ `~/.claude/settings.json`, không in ra chat) trong toàn bộ bundle — Test: 0 match — PASS (0 match cả PRIMARY/BACKUP)

## DoD
V1–V4 đều PASS → bundle vẫn hợp lệ, không lệch, không rò rỉ secret. Bất kỳ mục FAIL
→ báo rõ trong chat, không tự sửa nếu vượt phạm vi (đổi code/build lại).

Năng lực: không có (chỉ chạy lệnh có sẵn, không cần skill ngoài).
