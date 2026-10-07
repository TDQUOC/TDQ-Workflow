# Thang kiểm sau khi gỡ lumen — 2026-10-07 (T6.1)

Lệnh: `python3 scripts/tdq_lsp.py check` trên máy thật (plugin lumen VẪN cài lúc này — thang không còn hỏi tới nó), sau `graphify extract . --code-only`.

Trước (request 1843, giả lập lumen vắng): 8 bậc, smoke 4 tầng, `Tổng: CHƯA ĐẠT`, exit 4.

```
Bậc 1 · binary agent-lsp → ĐẠT (0.19.2)
Bậc 2 · MCP `lsp` → ĐẠT (2 server đã đăng ký)
Bậc 3 · language server theo project → ĐẠT (đủ cho 2 ngôn ngữ: HTML, Python, khởi động thử ok)
Bậc 4 · quyền tool `mcp__lsp__*` → ĐẠT (1 mục trong allow)
Bậc 5 · hook plugin ngoài xung đột → ĐẠT (không plugin nào chèn thứ tự tìm kiếm khác)
Bậc 6 · cấu hình gốc import theo ngôn ngữ → ĐẠT (2 ngôn ngữ đều có file mốc ở gốc dự án)
Bậc 7 · đồ thị graphify → ĐẠT (đồ thị mới hơn mọi file mã nguồn)

Smoke test ba tầng:
  grep      ĐẠT  · tìm ra định nghĩa trong _api.py
  LSP       ĐẠT  · trả lời được
  graphify  ĐẠT  · trả lời được

Tổng: ĐẠT · 7/7 bậc ĐẠT · smoke 3/3 tầng trả lời được
exit=0
```
