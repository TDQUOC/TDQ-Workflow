# Kiểm tra bản HTML tổng hợp đợt 1

Ngày 27/10/2026 · Bổ sung trình bày cho request đang ở phase report.

- Đầu ra: [HTML tổng hợp](../../reports/2026-10-27-1246-do-dung-bao-toan-loi.html), có tóm tắt trước/sau, QC, runtime, giới hạn, đề xuất và toàn bộ báo cáo gốc trong mục mở rộng.
- [Markdown nguồn](../../reports/2026-10-27-1246-do-dung-bao-toan-loi.md) giữ nguyên SHA-256 `4afc72e6049d0dda30c5b8dfd75a82c2b9e3acc5df0bdf5bec21a42639510c34`.
- [Kiểm nội dung](report-html-content-check.json): toàn văn nguồn được giữ nguyên sau chuyển HTML; 42 liên kết hợp lệ, ID duy nhất, không có tài nguyên ngoài. Cả sáu kiểm đều đạt.
- [Kiểm browser](report-html-browser-check.json): Chrome DevTools MCP, desktop 1440×900 và mobile giả lập 375×812. Đã đọc cây accessibility, kiểm số liệu KPI, mục lục, các vùng chính và phần mở rộng.
- Desktop: không tràn ngang; bảy liên kết mục lục có đích; ba mục giới hạn mở/đóng đúng. Mobile: chiều rộng document bằng viewport 375px; báo cáo mở rộng hiển thị, ba bảng dài cuộn trong vùng riêng.
- Bàn phím: focus-visible có outline solid 3px. Hover mục lục có underline 2px. Không có form/backend để kiểm submit hoặc khôi phục API.
- Console: không có error/warning. Network: chỉ tải tài liệu cục bộ thành công; CSS inline, không gọi font/CDN/API.
- Đã xem ảnh [desktop](report-html-desktop.jpg) và [mobile](../../../workinglog/images/2026-10-27-1246-do-dung-bao-toan-loi-report-mobile.jpg), cùng ảnh vùng QC mobile trong phiên. Chữ, thẻ KPI và thẻ lịch sử test không bị cắt hoặc đè nhau.
- MCP không ghi trực tiếp ảnh/JSON vào repo vì root cấu hình của service khác workspace. Đã nhận kết quả inline và lưu qua công cụ workspace. Resize cửa sổ native bị chặn ở 500px; bằng chứng mobile dùng viewport CDP đúng 375px, không nhận 500px là 375px.
- Không có mẫu hình ảnh tham chiếu, không tuyên bố pixel-diff. Đây là kiểm trình bày tài liệu; số liệu 3.290 test/12 skip lấy từ bằng chứng QC trước đó, không chạy lại suite hoặc tạo số đo runtime mới.
- [Biên nhận tạo HTML](report-html-build.json) giữ hash nguồn, hash HTML và thời điểm tạo. Có thể tái tạo bằng `build_report_html.py` với `markdown_it` đã có sẵn; không cài thêm dependency.
- Giữ nguyên trạng thái chờ bàn giao Git; không thay source runtime, cổng duyệt, worker hoặc plugin cache.
