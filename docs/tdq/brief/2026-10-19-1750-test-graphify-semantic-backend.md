# BRIEF — Thử Nghiệm Semantic Extraction Của Graphify Với Cấu Hình Claude Code Hiện Tại

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

"okay hyax dùng endpoint và apikey và model name như config hiện tại của claude code đê test giúp tôi"

### Đọc hiểu lần đầu
- **Mục tiêu**: Lấy thông số endpoint, token và model từ biến môi trường hiện tại của Claude Code (`ANTHROPIC_BASE_URL=http://36.50.55.22:20228/v1`, `ANTHROPIC_AUTH_TOKEN`, `model=custom-combo-no2`) để chạy thử nghiệm thực tế tính năng Semantic Extraction (`graphify extract` hoặc `graphify label`) của Graphify.
- **Phạm vi dự kiến**:
  - Thiết lập môi trường chạy thử nghiệm độc lập (không ghi đè trực tiếp đồ thị chính khi chưa hoàn tất kiểm tra).
  - Thử nghiệm trích xuất ngữ nghĩa trên một phạm vi mẫu (hoặc toàn bộ dự án).
  - Thu thập kết quả: số liên kết suy luận sinh ra (`INFERRED-edge`), nhãn cụm tính năng (`community labels`), thời gian phản hồi và độ ổn định của endpoint.
  - Báo cáo kết quả đo đạc thực tế cho người dùng.

## Hiểu & kiến thức

### 1. Cấu hình kết nối Backend
- Backend được chọn: `claude` (hỗ trợ custom Anthropic endpoint).
- Biến môi trường:
  - `ANTHROPIC_BASE_URL`: `http://36.50.55.22:20228/v1`
  - `ANTHROPIC_API_KEY`: Lấy từ `ANTHROPIC_AUTH_TOKEN` hiện tại của phiên làm việc.
  - `ANTHROPIC_MODEL`: `custom-combo-no2`

### 2. Phương án thử nghiệm an toàn
- Tạo một thư mục thử nghiệm cách ly (ví dụ `evals/graphify_test/` hoặc thư mục tạm) chứa một tập hợp đại diện các file code và docs (ví dụ: `hooks/scripts/_common.py`, `scripts/tdq_ten_lenh.py`, tài liệu conventions).
- Chạy trích xuất `graphify extract <dir> --backend claude --mode deep --out <dir>/out`.
- Đo đạc số nodes, số edges, nhãn community gán bởi LLM, thời gian thực thi và tính ổn định.

## Hỏi đáp

- Người dùng đã chọn 1a: Express pipeline (quick lane).
- Yêu cầu: Sử dụng trực tiếp cấu hình endpoint, auth token và model đang dùng của Claude Code để thực nghiệm tính năng trích xuất ngữ nghĩa của Graphify.
