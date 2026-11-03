# Brief — Thử Nghiệm Thực Tế Kỹ Năng tdq-browser-test Trên Ứng Dụng WebChat Socket.io

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

Người dùng yêu cầu:
> "2" (chọn option 2: Chạy thử nghiệm thực tế kỹ năng tdq-browser-test trên ứng dụng WebChat Socket.io ngoài máy).

- **Mục tiêu**: Chạy quy trình kiểm thử UI/UX 5 lớp phân vùng thực tế bằng kỹ năng mới `tdq-browser-test` thông qua Chrome DevTools MCP (đang kết nối CDP port 9222) trên ứng dụng WebChat Socket.io (`C:\Users\admin\Desktop\ResreachSocketIOWebsocketOverHTTP\index.html`).
- **Phạm vi dự kiến**:
  1. Mở file HTML hoặc khởi tạo server local phục vụ file `index.html`.
  2. Dùng công cụ `mcp__chrome-devtools__*` thực hiện lần lượt 5 lớp kiểm định:
     - Lớp 1: Tree DOM a11y structure (duyệt UID các element chính: chat container, input, send button, status).
     - Lớp 2: Responsive Desktop (1440x900) & Mobile (375x812), chụp ảnh màn hình lưu `docs/workinglog/images/`.
     - Lớp 3: Tương tác trực tiếp: nhập tin nhắn, click nút gửi/Enter, hover trạng thái button.
     - Lớp 4: Quét sạch console errors & network requests hỏng.
     - Lớp 5: Đánh giá CSS layout & style cascade.
  3. Lập báo cáo kiểm định UI/UX chi tiết không bỏ sót lỗi.
- **Điểm chưa rõ**: Đã xác định đúng thư mục mục tiêu `C:\Users\admin\Desktop\ResreachSocketIOWebsocketOverHTTP\index.html`.
