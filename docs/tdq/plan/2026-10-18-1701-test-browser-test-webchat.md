# Mini-Plan — Kiểm Thử UI/UX 5 Lớp Thực Tế Ứng Dụng WebChat Socket.io

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Mục tiêu
Dùng kỹ năng mới `tdq-browser-test` thông qua Chrome DevTools MCP thực hiện kiểm thử UI/UX 5 lớp chuyên sâu (phân vùng chi tiết từng element, từng layout viewport, state interactions và silent faults) trên ứng dụng WebChat Socket.io tại `C:\Users\admin\Desktop\ResreachSocketIOWebsocketOverHTTP\index.html`.

## Danh sách công việc (5 Lớp Test)
- [x] **T1** (e5m) **Lớp 1: Khảo sát Tree DOM a11y & Cấu trúc Layout**: Lấy snapshot toàn diện, lập danh sách UID các container (Header, Status indicator, Messages list, Input form, Action buttons) đảm bảo không có container nào rỗng hoặc lỗi a11y.
- [x] **T2** (e5m) **Lớp 2: Kiểm thử Responsive Viewport & Screenshot**:
  - Chụp ảnh màn hình Desktop (1440x900) lưu `docs/workinglog/images/webchat-desktop.png`.
  - Resize và chụp ảnh màn hình Mobile (375x812) lưu `docs/workinglog/images/webchat-mobile.png`.
  - Kiểm tra tràn ngang (horizontal scroll), vỡ flex/grid layout.
- [x] **T3** (e5m) **Lớp 3: Tương tác Phần tử Thực tế (Element Interactions)**:
  - Hover trên các nút tương tác (Connect, Send, Clear).
  - Điền form input chat và test kích hoạt gửi tin nhắn.
  - Kiểm tra trạng thái transition (active, focus, disabled).
- [x] **T4** (e5m) **Lớp 4: Silent Fault Detection (Bắt sạch lỗi ngầm)**:
  - Quét toàn bộ console logs tìm cảnh báo, unhandled exception đỏ (`list_console_messages`).
  - Quét toàn bộ network requests tìm lỗi 4xx/5xx hoặc failed requests (`list_network_requests`).
- [x] **T5** (e5m) **Lớp 5: Thẩm định CSS Cascade & Tương phản WCAG AA**:
  - Kiểm tra quy tắc cascade layer, CSS variables theme token (`get_css_styles`).
  - Đánh giá độ tương phản màu chữ và nền trên UI.
- [x] **T6** (e5m) **Tổng hợp & Báo cáo QC**: Xuất bản báo cáo kiểm thử chi tiết và bàn giao kết quả.

## Definition of Done
- 5/5 lớp kiểm thử được thực hiện đầy đủ bằng tool Chrome DevTools MCP thực tế trên trang `index.html`.
- Chụp và lưu trữ 2 ảnh chụp Desktop và Mobile vào `docs/workinglog/images/`.
- Không bỏ sót bất kỳ lỗi giao diện, console hay network nào.
