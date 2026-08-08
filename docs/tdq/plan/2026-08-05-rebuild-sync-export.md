# Mini-plan — Rebuild bundle export để đồng bộ (quick)

Ngày: 2026-08-05 · Lane: quick · Request: ../requests/2026-08-05-rebuild-sync-export.md

## Phạm vi
- IN: chạy lại `claude_export.py build --dest ~/Documents/claude-code-export --zip`
  (ghi đè bundle cũ), rồi `check` + `unzip -t` xác nhận đồng bộ.
- OUT: sửa code, đổi `local-repos.json`, đổi cấu hình nguồn `~/.claude`.

## Task
- [x] **R1** Build lại — `python3 scripts/claude_export.py build --dest ~/Documents/claude-code-export --zip` — Test: exit 0, log "quét secret: sạch"
- [x] **R2** Check ngay sau build — `python3 scripts/claude_export.py check --dest ~/Documents/claude-code-export` — Test: exit 0, in `0 mục lệch`
- [x] **R3** Toàn vẹn zip — `unzip -t ~/Documents/claude-code-export.zip` — Test: "No errors detected"
- [x] **R4** Ghi mốc — append `claude-export/EXPORT_LOG.md` (EXPORT_DEST + tóm tắt) — Test: `tail` có dòng mới đúng ngày

## DoD
R1–R4 PASS → bundle đồng bộ lại với máy nguồn, 0 mục lệch.

Năng lực: không có (chỉ chạy lệnh có sẵn).
