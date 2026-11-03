# BRIEF — Phân tích điểm nghẽn thời gian chạy của Agent & Đo lường thực nghiệm
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

"Okay bây giờ tôi muốn mở request bạn check giúp tôi, gần đây một request tốn rất nhiều time cho agent chạy bạn có quyền tạo một vài example project ở desktop chạy thử và phân tích thử sau đó report cho tôi nđiểm nghẽn là ở đâu và đề xuất cho tôi hiểu trước"

### Đọc hiểu ban đầu
- **Mục tiêu:** Kiểm tra, phân tích và thực nghiệm đo lường nguyên nhân khiến các request gần đây tốn quá nhiều thời gian (runtime latency / time overhead) cho agent thực thi trong TDQ-Workflow. Tạo project ví dụ mẫu tại Desktop để chạy thử, profile và xuất báo cáo chỉ rõ điểm nghẽn (bottlenecks) kèm đề xuất giải pháp tối ưu.
- **Phạm vi dự kiến:**
  - Khảo sát các mốc thời gian thực tế ghi nhận trong `docs/tdq/timing.jsonl` và nhật ký thực thi gần đây.
  - Phân tích các tầng có nguy cơ gây trễ:
    1. Vùng kiểm thử lan tỏa (`tdq_test.py vung-cham` khi radius vượt 60% kích hoạt chạy 162 modules toàn bộ suite > 120s - 600s).
    2. Các chốt chặn Gate/Hook thực thi lặp lại: `stop_gate.py`, `search_gate.py`, `tdq_finish.py` (Archify finalize, Graphify, LSP check, token lock).
    3. Trực quan hóa kiến trúc Archify / Chrome DevTools Pipe handshake trên Windows.
    4. Chi phí context injection và kích thước prompt khổng lồ (`today-2026-10-25.md` > 11KB, full git diff dump).
  - Tạo dummy/benchmark test projects trên Desktop để đo lường runtime thực tế của từng pha và từng công cụ độc lập.
  - Lập báo cáo phân tích toàn cảnh điểm nghẽn và đề xuất các giải pháp khắc phục triệt để.
- **Điểm chưa rõ:** Chưa có (yêu cầu phân tích khảo sát và đề xuất rõ ràng).

## Hiểu & kiến thức

### 1. Dữ liệu thực tế từ timing log (`docs/tdq/timing.jsonl`)
- Ghi nhận các request gần đây tiêu tốn thời gian cực lớn:
  - `2026-10-24-2348-hoan-thien-archify`: phase `plan` tốn 39,848s (11.07h).
  - `2026-10-25-1113-phan-tich-muoi-issue`: phase `implement` tốn 6,743s (1.87h), tổng request 13,742s (3.81h).
  - `2026-10-25-1648-mastermap-va-readme-pro`: tổng request 11,703s (3.25h).
  - `2026-10-25-2025-auto-update-plugin`: phase `implement` tốn 807s, tổng 4,871s.

### 2. Các điểm nghẽn tiềm năng đã sơ bộ nhận diện
1. **Bùng nổ phạm vi kiểm thử (Blast Radius > 60% trigger full suite):**
   - Khi chỉnh sửa file lõi (`scripts/tdq_setup.py`, `hooks/scripts/session_start.py`), thuật toán `tdq_test.py vung-cham` tính toán phụ thuộc ra 124/162 modules (>60%), tự động kích hoạt chạy 100% test suite.
   - Toàn bộ suite mất ~600 giây (10 phút). Vì timeout của tool Bash mặc định là 120s, lệnh bị đẩy vào background và agent phải chờ đợi hoặc bị block nhiều turn.
2. **Chi phí lặp lại của Hook & Gate (Stop Gate / PreToolUse Gate / Finish):**
   - Mỗi lệnh tool và mỗi lần agent dừng đều kích hoạt chuỗi kiểm tra: `stop_gate.py` -> `tdq_finish.py` (chạy qua lint regex, worklog check, token lock, status archify, graphify).
3. **Trực quan hóa Archify & Chrome DevTools Pipe Timeout:**
   - Khi xuất bản kiến trúc, lệnh `finalize` native diagram gọi Chrome inspection qua pipes. Trên môi trường Windows với process elevation, Chrome relaunch làm pipe stream closed, timeout 1.5s - 5s mỗi view khiến quy trình chậm lại.
4. **Context Injection Bloat (Prompt Token Explosion):**
   - SessionStart hook tiêm vào context các file `.remember/today-*.md` (hơn 11KB text), các khối nhắc nhở luật, danh sách symbol LSP... khiến mô hình xử lý lâu hơn và prompt cache dễ bị trượt.

## Hỏi đáp

- Người dùng đã phê duyệt chạy chế độ nhanh (express) và trao toàn quyền tạo project benchmark mẫu trên Desktop để đo lường thực nghiệm.

