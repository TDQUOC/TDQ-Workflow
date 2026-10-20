# Cẩm Nang: Nguyên Tắc MCP-First & Kịch Bản Pre-flight Connection Check

Tài liệu chuẩn hóa nguyên tắc ưu tiên sử dụng Model Context Protocol (MCP) và bộ kỹ năng của MCP trong toàn bộ quy trình TDQ Workflow (từ phân tích, lập spec, lên plan đến triển khai thực tế).

---

## 1. Nguyên Tắc MCP-First (Ưu Tiên MCP Hàng Đầu)

1. **Ưu tiên công cụ chuyên biệt thay vì thao tác mù mờ:**
   - Khi làm việc với các môi trường chuyên biệt như **Roblox Studio**, **Unity Engine**, **Google Chrome**, **PostgreSQL**, **Docker**...: Agent **BẮT BUỘC** phải rà soát các MCP server hiện có. Nếu có MCP hoặc skill tương ứng, phải ưu tiên sử dụng.
   - Nếu có MCP hỗ trợ: Phải lấy MCP làm công cụ thực thi và kiểm chứng chính, tuyệt đối không dùng các lệnh shell mù mờ hoặc đoán định trạng thái runtime.

2. **Tích hợp vào Spec & Plan:**
   - Trong giai đoạn soạn thảo Spec (§3b Năng lực & công cụ): Phải định danh rõ các MCP tools/skills sẽ được huy động.
   - Trong Plan: Phải đặt task kiểm tra kết nối MCP (Pre-flight check) ở đầu đợt thực thi trước khi gọi các lệnh thao tác sâu.

---

## 2. Kịch Bản Kiểm Tra Kết Nối Trước Khi Thực Thi (Pre-flight Check)

Trước khi gọi công cụ MCP hoặc giao việc cho sub-agent, Agent phải kiểm tra tính sẵn sàng của kết nối.

### Bảng Kiểm Tra Các Nền Tảng Phổ Biến

| Nền tảng MCP | Mục đích | Cách kiểm tra trước (Pre-flight Probe) | Trạng thái sẵn sàng |
|---|---|---|---|
| **Chrome DevTools MCP** | Điều khiển trình duyệt, E2E UI/UX, scraping | Kiểm tra cổng TCP `9222` (`Test-NetConnection -Port 9222` hoặc probe HTTP `http://127.0.0.1:9222/json/version`) | Cổng 9222 trả về HTTP 200 / JSON version |
| **Unity Engine MCP** | Đọc cấu trúc scene, GameObject, chạy test, điều khiển Editor | Kiểm tra cổng/socket nội bộ của Unity MCP Server (thường là WebSocket hoặc TCP endpoint cấu hình trong Editor) | Socket phản hồi bắt tay thành công |
| **Roblox Studio MCP** | Đọc DataModel, tạo Script/Part, kiểm thử Luau | Kiểm tra endpoint giao tiếp giữa plugin Roblox Studio và MCP server cục bộ | Server cục bộ phản hồi kết nối từ Studio plugin |
| **Database MCP (Postgres/MySQL)** | Tra cứu schema, kiểm tra dữ liệu | Kiểm tra kết nối chuỗi connection string qua ping / query SELECT 1 | Kết nối cơ sở dữ liệu mở thành công |

---

## 3. Quy Trình Xử Lý Khi Chưa Kết Nối Được

Khi MCP đã được cấu hình trong hệ thống nhưng **chưa thể kết nối tới runtime/ứng dụng**:
- **CẤM:** Tự ý fallback sang phán đoán mã nguồn mù mờ hoặc báo lỗi crash hệ thống.
- **BẮT BUỘC:** Tạm dừng và in thông báo rõ ràng, lịch sự hướng dẫn người dùng mở ứng dụng và kích hoạt kết nối theo kịch bản chuẩn.

### Mẫu Thông Báo Hướng Dẫn Người Dùng

#### 1. Dành cho Google Chrome (Chrome DevTools MCP):
```
[MCP:CHROME-DEVTOOLS] Chưa kết nối được với Google Chrome qua cổng Remote Debugging 9222.
Hướng dẫn mở:
1. Đảm bảo đã tắt các cửa sổ Chrome thông thường nếu dùng chung profile.
2. Khởi chạy Chrome với lệnh debug:
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%USERPROFILE%\ChromeDevProfile" --remote-allow-origins=*
3. Hoặc chạy script auto-launch: python3 scripts/tdq_devtool_mcp.py launch
```

#### 2. Dành cho Unity Engine:
```
[MCP:UNITY] Đã phát hiện cấu hình Unity MCP nhưng chưa kết nối được với Unity Editor.
Hướng dẫn kết nối:
1. Mở Unity Editor và mở project mục tiêu.
2. Vào Window -> MCP Server (hoặc menu cấu hình MCP của Unity plugin).
3. Bấm "Start Server" / xác nhận cổng kết nối đang ở trạng thái Listening.
4. Sau khi kết nối sẵn sàng, nhắn "tiếp tục" để tôi tiến hành kiểm thử và đồng bộ mã nguồn.
```

#### 3. Dành cho Roblox Studio:
```
[MCP:ROBLOX] Đã phát hiện cấu hình Roblox MCP nhưng chưa nhận được tín hiệu từ Roblox Studio.
Hướng dẫn kết nối:
1. Khởi động Roblox Studio và mở Place / Project cần lập trình.
2. Tại thanh Plugins, kích hoạt plugin "Roblox MCP Bridge" / "Local Server Bridge".
3. Xác nhận tính năng "Allow HTTP Requests" đã được bật trong Game Settings -> Security.
4. Nhắn "tiếp tục" để tôi tra cứu DataModel và triển khai script Luau chính xác.
```

---

## 4. Tóm Tắt Quy Tắc Cho Agent

1. **Nhận diện tác vụ:** Gặp Roblox/Unity/Web/DB -> Nghĩ ngay đến MCP.
2. **Pre-flight Check:** Kiểm tra cổng / socket / status trước khi bắt đầu.
3. **Chưa mở -> Hướng dẫn:** Nếu chưa mở, in hướng dẫn rõ ràng từng bước cho người dùng mở lên.
4. **Đã mở -> Triển khai:** Sử dụng đầy đủ bộ công cụ và kỹ năng mà MCP cung cấp để kiểm tra, thực thi và thẩm định kết quả.
