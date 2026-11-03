# QUESTIONS — 2026-08-02-tdq-default-cleanup

## Vòng 1 (chờ trả lời)
1. Câu hỏi thuần giải đáp/đọc (không đổi repo, không tạo artifact — ví dụ "check config giúp tôi", "giải thích đoạn code này") có bắt buộc qua intake không?
   - (a) Cũng qua intake — tuyệt đối mọi prompt.
   - (b) Được trả lời thẳng; chỉ cần đụng repo/tạo output là phải intake. (đề xuất)
2. §5 superpower: bỏ trọn, hay giữ ý "external agent phải report kết quả thành file"?
   - Đề xuất: bỏ trọn — ý report-file đã nằm trong tdq-build external + external_task.py.
3. Có thêm tầng hook (UserPromptSubmit của plugin nhắc "phải qua tdq-intake" khi chưa có request mở) không?
   - Đề xuất: có — đây là tầng deterministic duy nhất, instruction thuần có thể bị model bỏ qua.

## Trả lời (vòng 1 — 2026-08-02 11:35)
1. **Tuyệt đối mọi prompt** — kể cả câu hỏi thuần giải đáp cũng qua intake.
2. **Bỏ trọn §5** — các ý giá trị đã có trong plugin.
3. **Có hook enforce** — UserPromptSubmit nhắc bắt buộc intake khi chưa có request mở.

## Vòng 2 — không còn câu hỏi đổi kết quả
- Làm rõ tự chốt (suy ra từ thiết kế, không đổi kết quả): "mọi prompt" áp cho YÊU CẦU MỚI khi không có request đang mở; message trong luồng request đang chạy (duyệt spec/plan, góp ý, trả lời interview) không mở intake mới.
