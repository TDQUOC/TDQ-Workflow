# EXPORT_LOG — Lịch sử sinh bundle export

Mỗi lần chạy `scripts/claude_export.py build` trên máy thật, thêm 2 gạch đầu dòng vào
CUỐI mục "Mốc": một dòng ghi `EXPORT_DEST`, một dòng tóm tắt kết quả. Script KHÔNG tự
ghi file này — cách ghi ở mục "Ghi log" của `INSTRUCTIONS.md`.

## Mốc

- 2026-08-04 14:13 — EXPORT_DEST=/Users/truongdinhquoc/Documents/claude-code-export
- 2026-08-04 14:16 — trial run bộ 7 bước tay: copy 18 file cấu hình + `tdqworkflow-repo/`, liệt kê 49 plugin (scope user), đã rewrite path `tdq-local`, không có cảnh báo
- 2026-08-05 04:17 — EXPORT_DEST=/Users/truongdinhquoc/Documents/claude-code-export
- 2026-08-05 04:17 — build 0.7.0 bằng `scripts/claude_export.py`: 1624 file / 15 MB · zip 6,4 MB · commit 61244c6 · 49 plugin + 2 marketplace + 2 MCP server · quét secret sạch · `check` ngay sau build ra 0 mục lệch · bản cũ giữ ở `claude-code-export.bak-20260805` và `claude-code-export.zip.bak-20260805`
- 2026-08-05 04:28 — EXPORT_DEST=/Users/truongdinhquoc/Documents/claude-code-export
- 2026-08-05 04:28 — sinh lại sau khi vá 2 lỗi QC báo: 1642 file / 15 MB · zip 6,8 MB · commit c4d57c2 · 49 plugin + 2 marketplace + 2 MCP server · quét secret sạch · `check` ra 0 mục lệch
- 2026-08-05 10:26 — EXPORT_DEST=/Users/truongdinhquoc/Documents/claude-code-export
- 2026-08-05 10:26 — sinh lại sau khi vá `_cli_approve`: 1696 file / 17 MB · zip 8,2 MB · 49 plugin + 2 marketplace + 2 MCP server · quét secret sạch · `check` ra 0 mục lệch
- 2026-08-05 10:27 — build lượt 2 sau khi commit mốc trên: 1709 file / 17 MB · zip 8,5 MB · commit `a5385093` · `check` ra 0 mục lệch · `unzip -t` No errors
- Lưu ý đọc số: bundle mang theo `.git` nên mỗi commit mới thêm vài object, số file tăng dần qua các lượt build. Dòng mốc này được commit SAU lần build cuối, vậy `check` sẽ báo lệch đúng 1 commit cho tới lần `build` kế tiếp.
- 2026-08-05 18:54 — EXPORT_DEST=/Users/truongdinhquoc/Documents/claude-code-export
- 2026-08-05 18:54 — build full multi-repo (0.8.0): 2121 file · zip 10,9 MB · 2 repo (`tdqworkflow-repo`@453e3702, `mem0-repo`@bb3ad38a) · 21 file cấu hình · 49 plugin + 2 marketplace + 3 MCP server · 1 LaunchAgent plist (`com.mem0.gateway.plist`) · quét secret sạch · `check` ra 0 mục lệch · `unzip -t` No errors · QC agent xác nhận không rò rỉ TAVILY key
- 2026-08-05 19:33 — EXPORT_DEST=/Users/truongdinhquoc/Documents/claude-code-export
- 2026-08-05 19:33 — rebuild đồng bộ lại sau khi validate lúc 19:22 phát hiện 2 mục lệch (`config/installed_plugins.json`, `config/known_marketplaces.json` — do `~/.claude/plugins/*.json` bị auto-sync ghi lại lúc 18:58): 2121 file · zip 10,9 MB · 2 repo (không đổi commit so với lần trước) · quét secret sạch · `check` ra 0 mục lệch · `unzip -t` No errors
