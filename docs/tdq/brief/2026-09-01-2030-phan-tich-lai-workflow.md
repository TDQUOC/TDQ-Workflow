# BRIEF — phân tích lại toàn bộ workflow TDQ

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> commit và mở request nhanh phân tích lại toàn bộ workflow và cho tôi biết các pha hiện tại,
> và cách mà workflow xử lí một request cũng như cách kiểm tra

Đọc lần đầu:

- Mục tiêu: có một bản mô tả đúng-với-code của workflow TDQ sau khi gỡ pha sơ đồ — liệt kê pha
  hiện tại, đường đi của một request từ lúc user gõ prompt đến lúc đóng, và các lớp kiểm tra
  (hook, gate, test, lint, QC) đang chặn ở đâu.
- Phạm vi đoán: đọc `scripts/tdq_state.py`, các hook trong `hooks/`, cây `skills/tdq-*`,
  `scripts/doc_lint.py`, `tests/`. Sản phẩm là tài liệu, không đổi hành vi code.
- Chỗ chưa rõ: user muốn kết quả nằm trong chat hay thành file tài liệu trong repo.

## Hiểu & kiến thức

(lane nhanh — gộp vào mini-plan)

## Hỏi đáp

(lane nhanh — gộp vào mini-plan)
