# EXPORT_LOG — Lịch sử chạy `claude-export/INSTRUCTIONS.md`

Mỗi lần chạy INSTRUCTIONS.md để sinh bundle, ghi thêm dòng vào CUỐI file này theo
định dạng:

```
YYYY-MM-DD HH:MM — <tóm tắt>
```

Bước 7 của INSTRUCTIONS.md ghi 2 dòng mỗi lần chạy: một dòng xác nhận `EXPORT_DEST`
(ghi trước khi `mkdir` tạo bundle), một dòng tóm tắt kết quả (số file copy, số plugin
liệt kê, cảnh báo nếu có). Đặt `TDQ_EXPORT_NO_LOG=1` trước khi chạy để tắt ghi log cho
một lần chạy cụ thể (ngoại lệ có chủ đích, không phải mặc định).
2026-08-04 14:13 — EXPORT_DEST=/Users/truongdinhquoc/Documents/claude-code-export
2026-08-04 14:16 — trial run: copied 18 config file(s) + tdqworkflow-repo/, listed 49 plugin(s) (scope user), tdq-local path rewritten, no warning
