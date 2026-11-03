# Chuẩn bị Lumen cho nhánh CÓ — 2026-10-07

- Ollama: đánh thức bằng `tdq_lsp.py wake` lúc 19:56:41 (pid 11900, cổng 11434). Trước đó ollama TẮT — chính trạng thái máy khi request mở.
- Cấu hình đo: backend ollama · host `http://localhost:11434` · model `qwen3-embedding:0.6b` (env `OLLAMA_HOST`, `LUMEN_EMBED_MODEL` trong `~/.claude/settings.json`) · lumen 0.0.42 `lumen-windows-amd64.exe` trong cache plugin.
- `health_check` (MCP): `Status: OK — service and configured model are ready`.

| Repo | Lệnh | Kết quả | Thời gian |
|---|---|---|---|
| TDQ-Workflow | `lumen index` | 7 file thay đổi, 102 chunk | 7 s (5,2 s index) |
| claudecodeui | `lumen index` | 2 file thay đổi, 35 chunk | 1 s (0,44 s index) |

Cả hai đã có index sẵn từ trước nên đây là index tăng dần, không phải dựng từ đầu.

`index_status` sau index — index tươi lúc 2026-10-07T12:56:5xZ (UTC):
- claudecodeui: 1025/1025 file, 10016 chunk, `Stale: no`.
- TDQ-Workflow: 1271/1271 file, 16889 chunk, `Stale: no`.

## Chống rò đáp án
Index TDQ-Workflow phủ cả `docs/`, nên hai file câu hỏi kèm đáp án (`cau-hoi-*.md`) cũng nằm trong index → nhánh CÓ có thể "tìm" ra chính file đáp án. Xử lý: chuyển tạm 2 file ra `%TEMP%/tdq-bench-lumen/`, index lại (`2 removed`, còn 1269 file), đo xong chuyển về. Đã soát: không file nào khác trong `docs/` chứa đáp án của bộ câu hỏi hiện tại (3 file cũ nhắc `sha256_noi_dung` là lịch sử của chính tính năng đó — nhánh nào đọc thấy cũng được, công bằng cho cả hai).
