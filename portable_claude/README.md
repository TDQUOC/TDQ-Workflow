# TDQ Workflow — bản portable cho Claude Code

## Cài ở máy mới — làm theo đúng thứ tự này

1. **Chép** trọn nội dung thư mục này vào gốc project của bạn, giữ nguyên `.claude/` và
   `.mcp.json`.
2. **Kiểm** trước khi mở Claude Code:
   ```
   python3 .claude/tdq/scripts/tdq_checkportable.py check
   ```
   Đọc theo tiền tố: `SẠCH` xong · `THIẾU` chưa có · `LỆCH` khác manifest · `LƯU Ý` việc
   chỉ bạn làm được.
3. **Vá** nếu có `THIẾU`/`LỆCH`: `python3 .claude/tdq/scripts/tdq_checkportable.py setup` (xem mục
   cảnh báo bên dưới — nó chỉ dựng lại được hai file).
4. **Đặt biến môi trường** cho MCP nếu `check` báo thiếu. Script cố ý KHÔNG làm hộ và
   không bao giờ in giá trị khoá — chỉ báo tên biến.
5. **Mở Claude Code** trong project đó. Lần mở đầu nó hỏi có tin thư mục này không →
   **bấm đồng ý**. Không đồng ý thì hook và cấu hình project không có hiệu lực.
6. **Khởi động lại phiên** để skill và agent trong thư mục mới được quét.
7. **Duyệt MCP server** — mỗi server trong `.mcp.json` cần bạn duyệt một lần.

Xong bảy bước thì nhắn `chạy skill tdq-checkportable` để máy tự kiểm lại lần cuối.

## Ba việc máy KHÔNG tự làm được

1. **Tin cậy thư mục** — bước 5 ở trên. Chỉ bạn bấm được, không có cờ dòng lệnh nào trong
   bộ này thay thế.
2. **Duyệt MCP server** — bước 7.
3. **Khởi động lại** — bước 6. Bỏ qua thì skill mới nằm im, không báo lỗi gì.

## Cảnh báo về tự vá

`setup` dựng lại được đúng hai file cấu hình mà bundle có đủ dữ liệu để tái tạo:
`.claude/settings.json` (từ `hooks.json` đi kèm) và `.mcp.json`. Ghi đè thì luôn sao lưu
thành `<file>.tdq-bak-<timestamp>`, và khối `env` bạn tự thêm được giữ lại.

File khác thiếu hoặc lệch thì `setup` **không** bịa nội dung — nó báo `CÒN …` và exit khác 0;
nguồn đúng duy nhất là bản gốc, chép lại từ đó. Chỉ muốn kiểm, không sửa: dùng `check`.

## Khoá bí mật

`.mcp.json` chỉ ghi TÊN biến môi trường, không bao giờ chứa giá trị khoá. Tự đặt biến ở máy
mình trước khi dùng MCP.
