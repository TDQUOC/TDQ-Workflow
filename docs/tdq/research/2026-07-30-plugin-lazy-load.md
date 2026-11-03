# RESEARCH — Tối ưu plugin user-level + lazy-load

Ngày: 2026-07-30 · Tool: tavily-primary (3 truy vấn, không cần failover)

## Truy vấn 1 — cơ chế enabledPlugins & scope

Nguồn: code.claude.com/docs/en/settings · code.claude.com/docs/en/plugins-reference ·
thejavaguy.org/posts/025 · github.com/anthropics/claude-code issue #27247

- `enabledPlugins`: map `plugin@marketplace: true/false`. Vắng key → theo `defaultEnabled`.
- Thứ tự thắng: managed > local (`.claude/settings.local.json`) > project > user.
  Plugin bật ở project KHÔNG tắt được bằng user settings — phải dùng local. Ở máy này
  mọi plugin đều scope user (trừ superpowers@project khác) → sửa user settings là đủ.
- CLI: `claude plugin enable|disable <tên>@<marketplace> --scope user`; áp dụng không cần
  restart bằng `/reload-plugins` (user gõ).
- Bug #27247: `enabledPlugins` trong settings.local.json bị bỏ qua nếu settings.json
  thiếu key đó. Không ảnh hưởng (user settings.json đã có 49 entry).
- KHÔNG có cơ chế tắt riêng 1 agent/skill trong plugin — chỉ tắt được cả plugin.

## Truy vấn 2 — chi phí context của plugin/skill

Nguồn: github issue #42650 · dev.to (giảm 44% overhead) · reddit r/ClaudeCode ·
naqeebali-shamsi.medium.com (issue #29971)

- Catalog skill (tên + description) bị nhét vào MỌI message: ~50 token/skill;
  50–100 skill ≈ 4–5k token/message → compact sớm hơn hẳn.
- Issue #42650 xác nhận: chưa có deferred discovery cho skill catalog; "disabling
  plugins removes both the catalog AND the ability to invoke — they're coupled"
  → **lazy-load thật = tắt mặc định + bật khi cần**, không có đường khác.
- Kinh nghiệm cộng đồng: cắt 63% component → nhanh và chính xác hơn; "mọi hook chạy
  trên mọi tool call"; chỉ giữ always-on tối thiểu.

## Truy vấn 3 — lệnh quản lý plugin

Nguồn: code.claude.com/docs/en/discover-plugins · codingnomads.com · HN 45530150

- Trong phiên: `/plugin disable|enable <tên>@<marketplace>` rồi `/reload-plugins`.
- Ngoài phiên: `claude plugin enable|disable ... --scope user`.
- `/plugin list --enabled|--disabled` để soát.

## Số liệu đo tại máy (2026-07-30)

- 50 entry cài đặt, 49 bật ở `~/.claude/settings.json` (superpowers scope project khác).
- ~225 SKILL.md trên đĩa từ plugin đang bật (skill_inventory.py; vài description chứa
  `|` làm vỡ parse dạng bảng — ghi nhận riêng). Top nặng: data-engineering 34,
  huggingface 25, hyperframes 19, datarobot 13, figma 12, qt 12, cloudflare 11.
- 16 MCP server + 11 LSP server từ plugin; 7 plugin có hook (tdq, remember, lumen,
  hookify, learning-output-style, unreal, superpowers-ngoài-project).
- 5 key cần tắt tồn tại đúng dạng `<tên>@claude-plugins-official`.
