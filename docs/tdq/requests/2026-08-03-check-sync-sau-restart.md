# REQUEST — 2026-08-03-check-sync-sau-restart

Ngày: 2026-08-03 23:16 · Trạng thái: mở

## Nguyên văn
> tôi vừa restart claude hãy check xem user-level đã đc sync all newest change chưa?

## Cách hiểu đầu tiên
- Mục tiêu: sau khi restart Claude, xác nhận các cấu hình user-level (`~/.claude/`) đã phản ánh những thay đổi mới nhất của request `skill-vao-goi-external` vừa xong.
- Phạm vi đoán: đối chiếu `~/.claude/CLAUDE.md` mục 9 (mode external: skill-dump, AGENTS.md, nhãn `(mcp)`, `--plan-file`) với contract mới trong repo; kiểm plugin tdq-workflow bản đang nạp (skills/agents trong phiên) có khớp file repo không.
- Chỗ chưa rõ: "user-level" chỉ CLAUDE.md hay gồm cả plugin cache/skills đã cài ở `~/.claude/`.
- Việc thuần đọc-so sánh, không sửa code (trừ khi phát hiện lệch thì đề xuất sửa).
