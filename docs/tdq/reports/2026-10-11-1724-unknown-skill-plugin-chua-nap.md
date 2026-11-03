# REPORT — Setup tự phát hiện và bật plugin tdq-workflow chưa bật ở scope user (`2026-10-11-1724-unknown-skill-plugin-chua-nap` · lane full · mode main · 9 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Nguyên nhân:** plugin `tdq-workflow@tdq-local` đã cài ở scope user nhưng chưa từng được bật trong `~/.claude/settings.json`. Nó chỉ được bật trong `.claude/settings.json` của vài project, trong khi khối ghim ở `~/.claude/CLAUDE.md` áp cho mọi repo. Hệ quả: ở 9routerfork, cả `tdq-workflow:tdq-intake` lẫn `tdq-intake` đều báo `Unknown skill`, và hook không chạy.
**Đã làm:**
- `plugin_tiers.bat_khoa` ghi khóa `enabledPlugins` nguyên tử, có `.bak`.
- Bậc kiểm mới `tdq_setup.kiem_plugin_user`:
  - chưa có bản cài thì ghi nợ;
  - lệch phiên bản thì chỉ cảnh báo;
  - chưa bật thì tự bật.
- Khối ghim thêm dòng dự phòng: khi gặp `Unknown skill`, đọc thẳng `skills/tdq-intake/SKILL.md`.
- Đồng bộ lại toàn khối `docs/claude-md-mau.md`.
- Thêm mục "Plugin phải bật ở scope user" vào `docs/notes/user-level-install.md`.

**Máy này:** setup đã bật `tdq-workflow@tdq-local: true` ở cấp user (bản cũ lưu ở `settings.json.bak`). Chạy lại setup lần 2 không ghi gì thêm.
**Kiểm:**
- QC full PASS sau 1 vòng fix (QC1.1: biến `CLAUDE_PLUGIN_ROOT` lọt vào bundle Antigravity).
- Trọn suite 2549 test, còn 2 module đỏ (`test_codex_cli`, `test_tu_khoi_tao`). Cả 2 đã đỏ ở HEAD sạch, không phải hồi quy.
**Đầu ra:** `scripts/plugin_tiers.py`, `scripts/tdq_setup.py`, `docs/claude-md-mau.md`, `docs/notes/user-level-install.md`, 5 file test.
**Bạn cần tự làm:**
- Chạy `/plugin update tdq-workflow@tdq-local`: bản cài đang là 0.59.0, còn instruction là 0.66.0.
- Mở phiên mới để harness nạp plugin.

**Giới hạn:**
- Trần byte của khối ghim nâng 4300 → 6000.
- Nợ có sẵn: `test_codex_cli::test_ba_cho_goi_y_cung_mot_lenh` và nhóm `SessionStartKichHoat` (chập chờn).

**Lệch spec chờ duyệt:** Q3 (id=1). Dòng dự phòng dài 269 ký tự ở bản mẫu nhưng 315 ký tự ở máy này (ngưỡng ≤ 300), do đường dẫn cài dài. Đã giữ mệnh đề nhắc chạy setup.
**Git:** chưa commit

## Thời gian

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 0s | — | 1 |
| analyze | 6 min | — | 1 |
| spec | 2 min | — | 1 |
| plan | 1h 52min | — | 1 |
| implement | 7 min | — | 1 |
| qc | 28 min | — | 1 |
| report | 6s | — | 1 |
| **Total** | **2h 36min** | **—** | |
