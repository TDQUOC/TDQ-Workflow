# Brief: Đánh giá khả thi & tích hợp tính năng enable-devtoolmcp vào TDQ Workflow
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> "okay tôi muốn là trong TDQ-Workflow config plugin có một input enable-devtoolmcp nếu tick nó lên thì khi session start sẽ check xem trên máy đó đã có setup chưa, nếu chưa thì sẽ dựa trên doc này setup, (coppy doc này vào tdq-workflow) luôn và khi nó đc enable và setup thành công thì trong tdq-workflow cũng có skill để tận dụng full power của devtool mcp trong việc test, resreach, craw data,...  hãy mở request check giúp tôi là có khả thi không ? nếu khả thi thì trả về tôi report chi tiết và hướng đề xuất tối ưu"

### Đọc hiểu lần đầu:
- **Mục tiêu**:
  1. Đánh giá tính khả thi (feasibility study) của việc thêm tùy chọn cấu hình `enable-devtoolmcp` (trong plugin config/manifest của TDQ Workflow).
  2. Cơ chế kích hoạt: Khi tick bật `enable-devtoolmcp`, tại sự kiện SessionStart (hoặc qua hook khởi động phiên), hệ thống tự động kiểm tra xem máy hiện tại đã cài đặt và cấu hình Chrome DevTools MCP chưa.
  3. Tự động hóa thiết lập (auto-setup): Nếu chưa setup, tự động dựa trên tài liệu hướng dẫn (`CHROME_DEVTOOLS_MCP_GUIDE.md`) để setup trọn gói (đăng ký MCP server `chrome-devtools`, cấu hình bypass quyền 2 tầng trong `settings.json`, tạo profile Chrome cách ly và script auto-launch).
  4. Lưu trữ tài liệu: Sao chép tài liệu `CHROME_DEVTOOLS_MCP_GUIDE.md` vào thư mục tài liệu/references của plugin TDQ-Workflow.
  5. Bổ sung skill chuyên biệt: Khi được kích hoạt thành công, TDQ Workflow cung cấp skill mới (ví dụ `tdq-browser` hoặc `tdq-devtool`) để khai thác toàn diện sức mạnh của Chrome DevTools MCP cho các tác vụ E2E web testing, visual smoke test, deep research, crawl dữ liệu, debug network/console.
  6. Xuất bản báo cáo chi tiết và đề xuất phương án kiến trúc tối ưu nhất.
- **Phạm vi dự kiến**:
  - Khảo sát khả năng mở rộng của plugin TDQ Workflow (`.claude-plugin/plugin.json`, hook `SessionStart`, script `tdq_setup.py`).
  - Đánh giá tính tương thích đa nền tảng (Windows, macOS, Linux).
  - Soạn thảo báo cáo phân tích khả thi và lộ trình triển khai chi tiết.
- **Điểm chưa rõ**: Cần người dùng xác nhận lựa chọn pipeline để thực hiện phân tích và kết xuất báo cáo.

## Hiểu & kiến thức
(Sẽ cập nhật ở phase analyze)

## Hỏi đáp
(Trao đổi lựa chọn pipeline)
