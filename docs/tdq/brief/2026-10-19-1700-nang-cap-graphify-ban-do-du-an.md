# BRIEF — Nâng Cấp Graphify Xây Bản Đồ Toàn Tập Và Đánh Giá Thay Thế LSP

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

"okay tôi muốn bổ sung nâng cấp graphiffy để có thể làm map toàn tập từ graphify để xây bản đồ hoàn thiện của project và để cho agent code tra cứu thì có thể giúp thay lsp được không, và có giúp sreach tính năng hoặc funtion hoặc future đầy đủ hơn không, biết là có thể gắn openAI compatible, hãy check xem có khả thi không và hiệu quả thế nào, nếu cần tôi có thể cấp endpoint và model để bạn test"

### Đọc hiểu lần đầu
- **Mục tiêu**:
  1. Khảo sát và đánh giá tính khả thi của việc sử dụng Graphify (kết hợp OpenAI-compatible LLM backend) để xây dựng bản đồ hoàn thiện (full map / comprehensive knowledge graph) của project phục vụ agent tra cứu.
  2. Trả lời câu hỏi cốt lõi: Graphify có thể thay thế LSP (Language Server Protocol) được không? Ưu và nhược điểm ra sao?
  3. Đánh giá khả năng tìm kiếm tính năng (features), hàm (functions), hoặc dự định/tương lai (futures/concepts) có đầy đủ và vượt trội hơn so với tìm kiếm truyền thống không.
  4. Chuẩn bị cơ chế kết nối OpenAI-compatible endpoint & model để thực nghiệm đo đạc hiệu quả thực tế nếu người dùng cấp thông tin.
- **Phạm vi dự kiến**:
  - Phân tích kiến trúc 3 tầng hiện tại (`LSP` ↔ `Graphify` ↔ `Grep`) và số đo thực nghiệm đối chiếu.
  - Kiểm tra các cờ trích xuất nâng cao của Graphify: semantic extraction, community clustering, `--mode deep`, OpenAI-compatible provider.
  - Thiết kế cấu hình thử nghiệm và phương pháp đánh giá (benchmark) độ chính xác, chi phí token, thời gian trích xuất.

## Hiểu & kiến thức

### 1. Phân tích ranh giới: Graphify vs LSP
- **LSP (Compiler Level)**: Bắt buộc cho việc phân tích cú pháp tĩnh, type checking, rename symbol an toàn, tra cứu định nghĩa chính xác theo ngữ cảnh biên dịch (file, dòng, cột). Graphify KHÔNG thể thay thế hoàn toàn LSP vì đồ thị không thể kiểm tra kiểu dữ liệu hoặc bắt lỗi compile trước khi chạy.
- **Graphify (Knowledge Graph Level)**: Vượt trội ở góc nhìn vĩ mô toàn dự án, tìm vết lan truyền thay đổi đa tầng (`affected`), gom cụm tính năng (`community`), và liên kết tài liệu quy ước (`docs/`, `skills/`) với mã nguồn (`rationale_for`).
- **Kết luận**: Hai công cụ cộng sinh tạo thành 2 tầng tìm kiếm bù trừ cho nhau, không triệt tiêu nhau.

### 2. Khả năng tìm kiếm Feature / Function bằng OpenAI-compatible
- Graphify hỗ trợ cờ trích xuất ngữ nghĩa đầy đủ: `graphify extract <dir> --backend openai` với biến môi trường `OPENAI_BASE_URL` và `OPENAI_MODEL`.
- Khả năng tìm kiếm qua `graphify query "<câu hỏi>"` dùng BFS traversal kết hợp tóm tắt cụm giúp tìm đúng các thực thể liên quan đến ý đồ tính năng mà grep từ khóa không thể tìm được.

### 3. Cơ chế Full Extract & Keep Update
- Cấu hình trích xuất đầy đủ cả code lẫn tài liệu (`skills/`, `docs/`) thay vì chỉ `--code-only`.
- Duy trì tính cập nhật liên tục qua `tdq_finish.py` (incremental AST) và tích hợp tùy chọn `graphify update` / `graphify watch`.

## Hỏi đáp

- Người dùng đã chọn 1a: Express pipeline (quick lane).
- Phản hồi làm rõ: Request này chỉ cần nghiên cứu (research), smoke test và phân tích để trả về báo cáo toàn diện kèm đề xuất hướng đi; CHƯA thay đổi behavior hiện tại của TDQ-Workflow ở request này.
