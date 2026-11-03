# MINI-PLAN — Phân tích điểm nghẽn thời gian chạy của Agent & Đo lường thực nghiệm
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Phạm vi
Bỏ B0: Đã có tiền lệ khảo sát đo lường trong `docs/tdq/bench/` và `docs/tdq/audit/`.
Bỏ B2: Khảo sát thực nghiệm trực tiếp trên môi trường nội bộ máy phát triển.
Trong: Tạo testbed đo lường trên Desktop, profile thời gian các tầng (hook, test runner, tdq_finish, archify), lập báo cáo phân tích và đề xuất tối ưu.
Ngoài: Chưa can thiệp sửa đổi mã nguồn sản phẩm chính của TDQ-Workflow trong request này.

## Nhiệm vụ
- [x] Task 1: Khởi tạo benchmark testbed tại `C:\Users\admin\Desktop\tdq-latency-benchmark` gồm project mẫu và script đo lường tự động.
  Chạm: `C:\Users\admin\Desktop\tdq-latency-benchmark`
- [x] Task 2: Đo lường runtime thực tế của từng tầng (hook overhead, test radius 60%, tdq_finish, archify finalize, context injection).
  Chạm: `docs/tdq/reports/2026-10-25-2147-phan-tich-nghen-thoi-gian-agent.md`
- [x] Task 3: Tổng hợp báo cáo phân tích căn nguyên điểm nghẽn, bảng dữ liệu đối chiếu và lộ trình đề xuất giải pháp tối ưu.
  Chạm: `docs/tdq/reports/2026-10-25-2147-phan-tich-nghen-thoi-gian-agent.md`

## Định nghĩa hoàn thành (DoD)
1. Thư mục benchmark tại Desktop được khởi tạo và chạy thành công các phép đo tự động.
2. Báo cáo `docs/tdq/reports/2026-10-25-2147-phan-tich-nghen-thoi-gian-agent.md` có đầy đủ bảng số liệu đo lường thời gian thực tế (giây/lần chạy) của từng tầng.
3. Báo cáo phân tích rõ căn nguyên 4 điểm nghẽn chính kèm giải pháp xử lý cụ thể.
4. Working tree sạch sẽ sau khi hoàn tất.

## QC
- DoD 1: PASS — Thư mục `C:\Users\admin\Desktop\tdq-latency-benchmark` chạy hoàn tất 2 script đo lường tự động.
- DoD 2: PASS — Báo cáo có bảng dữ liệu thực tế lịch sử (133 requests) và bảng đối chiếu testbed.
- DoD 3: PASS — Phân tích chi tiết 4 điểm nghẽn chính (Blast radius, Chrome pipe, Context bloat, Deep procedural overhead) và 4 nhóm giải pháp.
- DoD 4: PASS — Các tệp thuộc phạm vi tài liệu và báo cáo theo đúng kế hoạch.
