# BRIEF — Benchmark Và Audit Toàn Diện Graphify Full Extraction Trên Dự Án Photoboth360

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

"commit và thử graphify full cho C:\Users\admin\Documents\Photoboth360 và thử chạy test và validate/ audit xem performance và độ chính xác giúp tôi, tôi cần chạy ít nhất 50 bài test và thống kê kết quả chi tiết và đọ hiệu quả, mỗi bài test phải có đầy đủ log"

### Đọc hiểu lần đầu
- **Mục tiêu**:
  1. Thực hiện trích xuất toàn diện (`graphify extract` full AST + Semantic với endpoint/model hiện tại) cho dự án thực tế `C:\Users\admin\Documents\Photoboth360`.
  2. Xây dựng và thực thi bộ kiểm thử ít nhất 50 test cases để kiểm tra, xác thực (validate) và kiểm toán (audit) toàn diện:
     - Hiệu năng (Performance): Thời gian trích xuất, tốc độ truy vấn, token tiêu thụ.
     - Độ chính xác (Accuracy): Kiểm tra độ chính xác của các node (functions, classes, routes, models), các cạnh quan hệ (`calls`, `imports`, `references`, `rationale_for`), và độ bao phủ so với mã nguồn thực tế.
     - Khả năng tìm kiếm ý niệm (`graphify query`): Độ chuẩn xác khi truy vấn tính năng, controller, socket, camera/hardware.
  3. Ghi log chi tiết cho từng bài test (50 logs riêng biệt) và tổng hợp bảng số liệu thống kê hiệu quả.
- **Phạm vi dự kiến**:
  - Dự án mục tiêu: `C:\Users\admin\Documents\Photoboth360` (gồm `nodeserver` và `photobooth-360-hardware`).
  - Viết harness script thực thi 50 test cases tự động, xuất log chi tiết ra tệp kết quả.
  - Đo lường và lập báo cáo audit toàn diện.

## Hiểu & kiến thức

### 1. Đặc điểm dự án mục tiêu Photoboth360
- Đường dẫn: `C:\Users\admin\Documents\Photoboth360`
- Cấu trúc:
  - `nodeserver/`: Backend Node.js / Express (controller, models, routes, socket, utils, views, app.js, config.js, Test.js, README.MD).
  - `photobooth-360-hardware/`: Thành phần client / hardware.
- Loại tệp: JavaScript (`.js`), JSON, Markdown (`.md`).

### 2. Thiết kế bộ kiểm thử 50 bài test (Benchmark Suite)
Bộ test chia thành 5 nhóm đa chiều (mỗi nhóm 10 test case = 50 tests):
1. **Nhóm 1 (T01 - T10): Kiểm tra sự hiện diện & độ đầy đủ của Nodes (Entity Coverage)**
   - Xác minh các file và hàm quan trọng của `nodeserver` đều xuất hiện trong `graph.json` (ví dụ `app.js`, `config.js`, các controller, models, socket handler).
2. **Nhóm 2 (T11 - T20): Kiểm tra độ chính xác của các cạnh phụ thuộc (Imports & Requires)**
   - Xác minh các quan hệ `imports` / `requires` giữa các file trong `nodeserver` (ví dụ: `app.js` require `routes`, `controller` require `models`).
3. **Nhóm 3 (T21 - T30): Kiểm tra độ chính xác của các quan hệ gọi hàm (Call Flow & Methods)**
   - Xác minh các cạnh `calls` hoặc `method` giữa các hàm và module thực tế trong code.
4. **Nhóm 4 (T31 - T40): Kiểm tra khả năng truy vấn ý niệm & tính năng (`graphify query`)**
   - Chạy 10 câu truy vấn ngữ nghĩa thực tế (socket connection, database config, image upload, camera control, route dispatching...) và đối chiếu kết quả trả về.
5. **Nhóm 5 (T41 - T50): Kiểm tra bản đồ tác động & vĩ mô (`affected`, `god-nodes`, `communities`)**
   - Đánh giá khả năng phân tích vết lan truyền (`affected`) khi thay đổi module cốt lõi, xác định đúng các hub trung tâm (`god-nodes`), và kiểm tra nhãn cụm tính năng.

### 3. Phương thức ghi log và đo lường
- Mỗi bài test ghi lại: Tên test, mục tiêu, input, raw output, kết quả (PASS/FAIL), thời gian thực thi (latency).
- Xuất log chi tiết ra tệp `evals/photoboth360_audit_logs.jsonl` hoặc thư mục log riêng.

## Hỏi đáp

- Người dùng đã chọn 1a: Express pipeline (quick lane).
- Yêu cầu trọng tâm: Extract full Graphify cho `Photoboth360`, chạy ít nhất 50 bài test kiểm toán hiệu năng + độ chính xác kèm log đầy đủ cho từng test.
