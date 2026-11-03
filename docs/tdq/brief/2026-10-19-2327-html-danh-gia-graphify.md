# BRIEF — HTML đánh giá Graphify dễ hiểu
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> Hãy tạo cho tôi một html phân tích nhanh gọn dễ hiểu về độ chính xác, performance của graphify và câu 2 là nó có ther thay được lsp hoặc lumen không và khi extract full thì có giúp ai dễ tìm hơn không và có tiết kiệm token và tool call không

Đọc hiểu lần đầu:
- Tạo một báo cáo HTML tiếng Việt độc lập, mở trực tiếp trên trình duyệt, trình bày ngắn gọn.
- Trả lời: độ chính xác và hiệu năng; thay LSP/Lumen được không; full extraction giúp AI định vị mã ra sao; khả năng giảm token và tool call.
- Tái sử dụng số liệu audit Photoboth360 hiện có, không gọi thêm API hoặc thay behavior TDQ Workflow.
- Phải phân biệt tỷ lệ PASS của smoke tests với precision/recall thực tế; không khẳng định đã đo tiết kiệm token/tool calls khi chưa có benchmark đối chứng.

## Hiểu & kiến thức

- Kết quả lần chạy trước: 50/50 PASS; 21,585 nodes; 52,741 links. Các phép kiểm dùng substring và một số điều kiện rộng, không chứng minh độ chính xác tuyệt đối.
- Có lần đổi T14 từ socket.io sang path sau khi không tìm thấy cạnh socket.io; báo cáo phải giữ đây là giới hạn chưa giải quyết, không che bằng tỷ lệ PASS mới.
- Truy vấn CLI khoảng 2.7 giây/lần gồm khởi động tiến trình; tra node/edge trong Python RAM không thể so trực tiếp với CLI hoặc suy ra thời gian full extraction.
- Chưa có đo A/B về token, tool calls, chi phí xây/cập nhật index hay đối chứng Lumen trên cùng tác vụ.
- Repo còn thay đổi chưa commit từ audit trước và cấu hình LSP; không tự commit, dọn hoặc ghi đè các thay đổi đó.

## Hỏi đáp

- Người dùng chọn “A”: express, loại docs.
- Chưa init request hoặc chuyển nhánh: còn các tệp audit chưa commit thuộc `evals/` và kiểm tra LSP module `python:.` chỉ trả 2 tham chiếu trong file định nghĩa, không thấy tham chiếu từ test.
- Đã hoàn nguyên nội dung `pyrightconfig.json` từ bản sao lưu do lần start_lsp có scope ở lượt trước đã thu hẹp include; `git diff --stat -- pyrightconfig.json` không còn chênh lệch nội dung. Không xóa bản sao lưu.
- Người dùng trả lời “Đồng ý” cho cả hai điều kiện: giữ nguyên thay đổi audit và bỏ qua kiểm chứng LSP riêng cho HTML tĩnh. Đã init quick bằng CLI với lý do bỏ qua và mở nhánh `docs/html-danh-gia-graphify` từ `chore/audit-graphify-full-photoboth360`.
- B1: đã đọc trực tiếp harness dòng 156–217 và báo cáo tổng hợp; query chỉ đòi một keyword, affected cũng chỉ đòi một từ, explain chỉ kiểm chiều dài; log không lưu toàn bộ stdout/stderr. Không coi 50/50 là precision/recall hoặc chứng minh blast radius đầy đủ.
- Nguồn so sánh Lumen/LSP: quy tắc tìm kiếm hiện hành, mục 1–2b trong `skills/tdq-setup/references/uu-tien-tim-kiem.md`. Các phép đo repo khác chỉ là bối cảnh, không chuyển thành kết quả Photoboth360.
- Đầu ra dự kiến: `docs/tdq/reports/graphify-danh-gia-nhanh.html`, offline, responsive, không thư viện ngoài; bốn phần kết luận và bảng số liệu có nguồn. Dùng skill dataviz khi trình bày số liệu, không gọi API.
