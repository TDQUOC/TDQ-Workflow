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
