# Điều chỉnh phạm vi — bỏ qua benchmark
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-10-31 · Request: `2026-10-27-1846-kiem-chung-tang-toc`.

Nguyên văn người dùng: **“có thể skip bench mà tổng hợp cho tôi ko?”**

## Phạm vi được bỏ qua

- T5.3 / D9: không chạy tiếp ba cặp Full A/B, không chứng nhận parity và ngưỡng median giảm ít nhất20% trên source cuối.
- T5.4 / D10: không chạy tiếp benchmark reuse/readiness/transcript, không chứng nhận lợi ích cold/warm hoặc log thật.
- Trạng thái hai mục: **SKIPPED_USER**, không phải PASS hiệu năng hoặc fallback đã đủ số đo. Bằng chứng thiếu/FAIL trước đó vẫn giữ nguyên.
- Không gửi dự thảo phối hợp sang chat khác; không cần thay đổi hay dừng công việc của chat khác để tổng hợp.

## Phần bàn giao còn thực hiện

Tổng hợp correctness, runtime, architecture/code review và các sửa lỗi; báo cáo QC cùng Markdown/HTML; kiểm report desktop/mobile và link bằng chứng. QC runtime/correctness được đánh giá độc lập với hai benchmark đã bỏ qua. Các gate report cũ bắt buộc benchmark đủ mẫu không được gọi là đã PASS; kiểm report theo phạm vi mới phải ghi riêng.

Giữ mặc định1worker, reuse/readiness/transcript off. Không công bố phần trăm tăng tốc từ các sample cũ khác source, bị ngắt hoặc không đạt parity. Không thay đổi spec đã duyệt hoặc bộ verifier để làm bằng chứng thiếu thành PASS. Checklist đóng hai mục theo quyết định người dùng phải mang nhãn SKIPPED_USER rõ ràng.
