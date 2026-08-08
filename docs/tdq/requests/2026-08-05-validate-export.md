# Request — 2026-08-05-validate-export

## Nguyên văn user
"hãy validate bản export lại giúp tôi"

## Cách hiểu ban đầu
- Mục tiêu: chạy lại việc kiểm tra (validate) bundle export vừa build tại
  `~/Documents/claude-code-export` (+ `.zip`) từ request trước
  (`2026-08-05-full-claude-export`) — không phải build lại từ đầu.
- Phạm vi đoán: chạy lại `claude_export.py check`, `unzip -t`, có thể thêm 1 lượt QC
  độc lập (agent `tdq-qc-tester`) xác nhận cấu trúc bundle + không rò rỉ secret,
  giống các bước T6.3–T6.5 đã làm ở request trước nhưng chạy LẠI để xác nhận bundle
  vẫn đúng ngay bây giờ (không có gì thay đổi/lệch từ lúc build tới giờ).
- Chỗ chưa rõ: có cần build lại bundle mới không, hay chỉ validate bundle hiện có;
  phạm vi validate rộng tới đâu (chỉ check nhanh hay full QC lại từ đầu).
