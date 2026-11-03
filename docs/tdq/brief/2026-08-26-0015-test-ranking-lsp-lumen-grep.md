# Test ranking khả năng find: LSP vs lumen vs grep

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> tôi muốn mở request quick check lại khả năng find của lsp và lumen và grep hãy test thử và cho tôi biết kết quả ranking

Ý người dùng: kiểm chứng thực nghiệm (không chỉ đọc tài liệu) khả năng tìm kiếm code của 3 lớp
đang cấu hình trong workflow — `mcp__lsp__*`, lumen (`mcp__plugin_lumen_lumen__semantic_search`),
và `grep`/`Grep` — trên chính repo TDQWorkflow. Kết quả cần là bảng ranking (ai tìm đúng, ai
nhanh hơn, ai bao phủ hơn) cho vài loại truy vấn khác nhau (tìm theo tên symbol chính xác, tìm
theo mô tả khái niệm mơ hồ, tìm ai gọi một hàm).

Phạm vi đoán: chạy một bộ câu hỏi mẫu qua cả 3 công cụ trên vài symbol/khái niệm thật trong repo,
so sánh kết quả, không sửa code, không đổi cấu hình.

## Hiểu & kiến thức

- Đây là việc kiểm tra/đo lường (read-only), không đổi hành vi sản phẩm — phù hợp lane quick.
- 3 lớp tìm kiếm sẵn có:
  - `mcp__lsp__*` (agent-lsp) — chính xác theo compiler/server index, cho: định nghĩa, ai gọi,
    kiểu dữ liệu, refactor an toàn.
  - `mcp__plugin_lumen_lumen__semantic_search` (lumen) — theo embedding, mạnh khi không có tên
    symbol rõ ràng ("phần xử lý retry logic").
  - `Grep`/`Bash grep` — text match thuần, lớp cuối.
- Repo chủ yếu Python (scripts/, tests/) + Markdown skills — ngôn ngữ có LSP hỗ trợ theo bậc 3
  (kiem đã ĐẠT: HTML, Python).
- Kế hoạch test: chọn 3-4 truy vấn đại diện, chạy qua cả 3 lớp, chấm điểm theo: đúng, đủ, tốc độ
  cảm nhận, độ hữu ích của output. Không cần sửa file nào.

## Hỏi đáp

(không có câu hỏi cần hỏi lại — phạm vi đã đủ rõ để chạy quick lane)
