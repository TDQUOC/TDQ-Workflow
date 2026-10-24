# Đặc Tả Kiến Trúc Tích Hợp Archify Vào TDQ-Workflow

Tài liệu này xác lập thiết kế kiến trúc chuẩn hóa cho việc tích hợp bộ công cụ Archify (`v3.2.0`) vào hệ thống TDQ-Workflow (`v0.81.0`).
Mục tiêu là cung cấp năng lực trực quan hóa kiến trúc dự án và hỗ trợ nghiệp vụ tương tác (Personal Business Analyst) cho lập trình viên trước khi viết mã.

---

## 1. Tổng Quan & Triết Lý Thiết Kế Mô Hình 2 Tầng

### 1.1 Bối cảnh & Mục tiêu
TDQ-Workflow hướng tới việc tối ưu hóa chu trình phát triển phần mềm có sự tham gia của AI.
Tuy nhiên, giai đoạn thiết kế ban đầu thường thiếu phương tiện trực quan hóa luồng nghiệp vụ tương tác.
Các lập trình viên, đặc biệt là fresher và junior, gặp khó khăn khi hình dung toàn cảnh tác động từ các khối văn bản thuần túy.
Việc tích hợp Archify mang lại khả năng mô phỏng luồng tương tác ngay từ bước lập đặc tả (`spec`).
Hệ thống giúp phân định ranh giới module, điều kiện rẽ nhánh và các trường hợp ngoại lệ trước khi triển khai mã nguồn.

### 1.2 Triết lý "Personal Business Analyst"
Hệ sinh thái TDQ-Workflow đóng vai trò như một chuyên viên phân tích nghiệp vụ cá nhân cho từng lập trình viên.
Mỗi tính năng trước khi bước vào giai đoạn viết code đều được trực quan hóa thành sơ đồ tương tác đa chiều.
Lập trình viên có thể kiểm tra trực tiếp luồng đi của dữ liệu, điểm chặn lỗi và cách các tầng giao tiếp với nhau.

### 1.3 Mô hình kiến trúc 2 tầng (Two-Tier Visualization Model)
Hệ thống tổ chức trực quan hóa thành 2 tầng phân tách rõ rệt về phạm vi nhận thức:

1. **Tầng 1 — Master Architecture Console (`docs/architecture/index.html`):**
   - Đại diện cho bức tranh toàn cảnh vĩ mô của toàn bộ kho mã nguồn.
   - Thể hiện đầy đủ các phân hệ, ranh giới bảo vệ (boundary) và các luồng gọi chéo module.
   - Được cập nhật định kỳ khi nghiệm thu tính năng mới hoặc sau mỗi lần quét mã nguồn toàn diện.

2. **Tầng 2 — Task Scope BA Flow (`docs/tdq/spec/<slug>-preview.html`):**
   - Đại diện cho góc nhìn vi mô phục vụ riêng cho một yêu cầu hoặc một tính năng cụ thể.
   - Tập trung trực diện vào các thành phần chịu tác động theo phân làn: UI -> Core -> Storage -> External.
   - Hỗ trợ đối chiếu trạng thái Hiện trạng (Trước) và Thiết kế mới (Sau) khi thực hiện refactor.

### 1.4 Các nguyên tắc thiết kế bất biến
- **Không xâm lấn (Non-invasive):** Không can thiệp hay sửa đổi trực tiếp vào kho mã nguồn gốc của Archify.
- **Tiêu chuẩn Python thuần (Stdlib Only):** Module adapter chỉ sử dụng thư viện chuẩn của Python, không thêm dependency bên ngoài.
- **Ngoại tuyến hoàn toàn (Zero-Network):** Tài liệu xuất bản đóng gói trọn vẹn tài nguyên, hoạt động không cần kết nối internet.
- **Nguyên tắc tinh gọn (Lean Principle):** Không áp đặt sinh sơ đồ cho các tác vụ siêu nhỏ, bảo toàn tốc độ của pipeline nhánh nhanh.

---

## 2. Sơ Đồ Kiến Trúc Tổng Thể & Luồng Dữ Liệu

### 2.1 Sơ đồ tuần tự tương tác (Sequence Architecture)

```text
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  NGƯỜI DÙNG  │     │   TDQ SPEC   │     │ TDQ ADAPTER  │     │ARCHIFY ENGINE│     │VIEWER RUNTIME│
│  (Developer) │     │  (Intake)    │     │(Python CLI)  │     │  (Node.js)   │     │  (HTML/JS)   │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │                    │                    │
       │ 1. Gửi yêu cầu     │                    │                    │                    │
       │───────────────────>│                    │                    │                    │
       │                    │ 2. Thiết kế luồng  │                    │                    │
       │                    │    & tạo JSON-IR   │                    │                    │
       │                    │───────────────────>│                    │                    │
       │                    │                    │ 3. Pre-flight      │                    │
       │                    │                    │    & finalize      │                    │
       │                    │                    │───────────────────>│                    │
       │                    │                    │                    │ 4. A* routing,     │
       │                    │                    │                    │    nhúng font/CSS  │
       │                    │                    │                    │    & xuất HTML     │
       │                    │                    │ 5. Báo hoàn tất    │<───────────────────│
       │                    │                    │<───────────────────│                    │
       │                    │ 6. Đường dẫn HTML  │                    │                    │
       │                    │<───────────────────│                    │                    │
       │ 7. Khối duyệt spec kèm preview HTML     │                    │                    │
       │<───────────────────│                    │                    │                    │
       │                    │                    │                    │                    │
       │ 8. Mở xem trực quan (CLI open)          │                    │                    │
       │────────────────────────────────────────>│                    │                    │
       │                    │                    │ 9. Kích hoạt mở    │                    │
       │                    │                    │────────────────────────────────────────>│
       │ 10. Thao tác tương tác, soi reachability, duyệt spec         │                    │
       │──────────────────────────────────────────────────────────────────────────────────>│
```

### 2.2 Luồng xử lý dữ liệu qua các bước
1. **Khởi tạo dữ liệu:** Agent tiếp nhận yêu cầu, phân tích logic nghiệp vụ và sinh candidate JSON-IR chuẩn.
2. **Kiểm tra môi trường:** Adapter xác thực Node.js và vị trí gói Archify engine trước khi gọi biên dịch.
3. **Biên dịch bố cục:** Engine Archify tính toán tọa độ theo giải thuật A* trực giao, cân bằng khoảng cách và né vật cản.
4. **Đóng gói nguyên tử:** Engine xuất file HTML độc lập chứa đầy đủ font JetBrains Mono Base64 và CSS/JS runtime.
5. **Duyệt và phản hồi:** Khối duyệt spec hiển thị đường dẫn HTML; người dùng kiểm tra trực quan và xác nhận duyệt.

---

## 3. Phân Hệ Adapter Python CLI (`scripts/tdq_archify.py`)

Module `scripts/tdq_archify.py` đóng vai trò cầu nối điều phối giữa TDQ-Workflow và engine Archify.

### 3.1 Hợp đồng giao tiếp (Contracts & API)
Adapter cung cấp các hàm chức năng xử lý nghiệp vụ với chuẩn đầu vào và đầu ra nghiêm ngặt:

- `find_archify_root() -> Optional[Path]`:
  Dò tìm đường dẫn thư mục gốc của Archify theo thứ tự ưu tiên: biến môi trường `ARCHIFY_ROOT`, thư mục lân cận `../archify`, và cache plugin.
- `preflight_check() -> Tuple[bool, str]`:
  Kiểm tra sự hiện diện của Node.js (phiên bản 18 trở lên) và file thực thi `bin/archify.mjs`.
- `build_finalize_command(...) -> List[str]`:
  Xây dựng danh sách tham số dòng lệnh để gọi tiến trình con Node.js thực thi lệnh `finalize`.
- `atomic_delivery(temp_file: Path, target_file: Path) -> None`:
  Thực hiện ghi file tạm an toàn và sử dụng `os.replace` để hoán đổi nguyên tử, chống ghi đè lỗi.
- `open_viewer(file_path: Path) -> bool`:
  Kích hoạt trình duyệt web mặc định của hệ điều hành để mở file HTML tương tác.

### 3.2 Các lệnh điều phối (CLI Subcommands)
Adapter hỗ trợ các lệnh thông qua giao diện dòng lệnh tiêu chuẩn:

| Lệnh | Cú pháp | Mục đích |
|---|---|---|
| `check` | `python3 scripts/tdq_archify.py check` | Kiểm tra tính sẵn sàng của Node.js và đường dẫn Archify |
| `render` | `python3 scripts/tdq_archify.py render <type> <json> <out.html>` | Biên dịch sơ đồ sang file HTML tương tác hoàn chỉnh |
| `open` | `python3 scripts/tdq_archify.py open <file.html>` | Mở file HTML tương tác trên trình duyệt mặc định |
| `sync-master` | `python3 scripts/tdq_archify.py sync-master` | Cập nhật các thay đổi vào Master Architecture Console |

### 3.3 Cơ chế phòng thủ và thoái lui mềm (Graceful Fallback)
Khi môi trường thiếu Node.js hoặc không tìm thấy Archify, adapter kích hoạt chế độ thoái lui:
- Trả về mã lỗi có cấu trúc kèm thông báo hướng dẫn rõ ràng.
- Giữ nguyên khối mã Mermaid dạng văn bản tĩnh trong tài liệu markdown để không làm gián đoạn chu trình TDQ.

---

## 4. Phân Hệ Cầu Nối Graphify-to-Archify

Phân hệ này giải quyết triệt để điểm nghẽn phụ thuộc mạng bên ngoài của Graphify hiện tại.

### 4.1 Điểm nghẽn hiện tại của tầng hiển thị Graphify
Hiện tại, `scripts/tdq_graphify.py` xuất file `CALLFLOW.html` sử dụng thư viện Mermaid tải qua CDN internet.
Cách làm này bộc lộ ba hạn chế lớn:
1. Không hoạt động được trong môi trường cô lập mạng (air-gapped).
2. Đồ thị tĩnh không cho phép lập trình viên tương tác để lọc bớt các thành phần gây nhiễu.
3. Nhãn chữ và dây nối dễ bị chồng chéo khi đồ thị vượt quá 20 nút.

### 4.2 Cơ chế chuyển đổi dữ liệu (`graphify_to_archify`)
Adapter bổ sung hàm chuyển đổi từ `graphify-out/graph.json` sang định dạng JSON-IR của Archify:
- Đọc danh sách `nodes` và `edges` từ dữ liệu AST của Graphify.
- Trích xuất thông tin `source_file` và `source_location` để ánh xạ vào trường `sources: [{ path, startLine, endLine }]`.
- Gom nhóm các hàm và lớp vào các khối `boundaries` dựa trên phân cụm cộng đồng Louvain hoặc cấu trúc thư mục.
- Chuyển đổi các liên kết phụ thuộc thành quan hệ định tuyến trực giao rõ ràng.

### 4.3 Năng lực tương tác vượt trội sau chuyển đổi
- **Khảo sát vỡ lan tương tác (Interactive Blast Radius):** Nhấp vào một module để xem toàn bộ chuỗi tác động trước và sau.
- **Dò tìm đường gọi (Route-probe):** Cho phép chọn hai hàm bất kỳ để tìm đường dẫn gọi ngắn nhất qua các tầng.
- **Truy vết mã nguồn tại chỗ:** Nhấp vào nút sơ đồ để xem vị trí dòng mã thực tế trong kho lưu trữ Git.

---

## 5. Phân Hệ Tích Hợp Quy Chuẩn BA Vào Spec & Quick Lane

### 5.1 Nâng cấp Phase `spec` (Pipeline `full`)
Quy chuẩn biên soạn đặc tả trong `skills/tdq-spec/` được nâng cấp đồng bộ:
- Tại mục **§2b (Ranh giới module)**: Xác định rõ ràng các ranh giới kiến trúc và trách nhiệm của từng vùng.
- Tại mục **§2c (Luồng hoạt động & Sơ đồ kiến trúc)**:
  - Sinh đồng thời khối mã minh họa logic và file HTML tương tác `docs/tdq/spec/<slug>-preview.html`.
  - Khối giao tiếp duyệt spec hiển thị đường link trực quan để người dùng kiểm tra trước khi bấm duyệt.
- Giới hạn token nghiêm ngặt: Bản mô tả JSON-IR chỉ chứa khung cấu trúc dưới 15 nút và dưới 700 tokens.

### 5.2 Tích hợp quy chuẩn Quick Lane BA
Trong `skills/tdq-intake/references/quick-lane.md`, quy chuẩn trực quan hóa được phân tầng theo độ phức tạp:
- **Tác vụ đơn lẻ (1 file mã nguồn):** Duy trì sơ đồ văn bản tinh gọn để tối ưu hóa thời gian thực thi.
- **Tác vụ chạm từ 2 module trở lên hoặc tái cấu trúc (Refactor):**
  - Tự động kích hoạt việc sinh mini-workflow dưới 10 nút.
  - Phân làn rõ ràng giữa trạng thái Trước và Sau để lập trình viên tự tin thao tác mà không gây vỡ mã nguồn.

---

## 6. Phân Hệ Cấu Hình Hybrid AI Endpoint

Hệ thống thiết lập cơ chế cấu hình AI lai, đáp ứng hài hòa giữa tính kinh tế và năng lực mở rộng.

### 6.1 Kiến trúc lai 2 chế độ (Hybrid AI Architecture)

1. **Chế độ 1 — Tận dụng phiên Agent hiện tại (Mặc định / Zero Cost):**
   - Bộ não Claude Code hoặc Codex trực tiếp tạo cấu trúc JSON-IR thông qua context đang làm việc.
   - Adapter chỉ tiếp nhận JSON và gọi engine Archify nội bộ để biên dịch, không phát sinh chi phí gọi API riêng.

2. **Chế độ 2 — Autonomous Codebase Scanning (Dành cho quét toàn dự án):**
   - Khi cần phân tích và dựng lại toàn bộ kiến trúc cho một kho mã nguồn lớn nhiều chục nghìn dòng.
   - Hệ thống kết nối với một Endpoint AI chuyên dụng được khai báo riêng, giải phóng tải cho phiên làm việc chính.

### 6.2 Cấu hình biến môi trường trong `.env.example`
Các tham số kết nối được quy chuẩn hóa trong file `.env.example`:

```bash
# ==============================================================================
# ARCHIFY AI ENDPOINT & ENGINE CONFIGURATION
# ==============================================================================
# Đường dẫn cài đặt Archify engine cục bộ (mặc định tự dò ../archify)
ARCHIFY_ROOT=

# Endpoint API dành riêng cho chế độ quét tự động toàn bộ codebase
ARCHIFY_AI_ENDPOINT=https://api.anthropic.com/v1

# Khóa xác thực API (chỉ lưu placeholder, không commit khóa thật)
ARCHIFY_API_KEY=your-api-key-here

# Tên mô hình AI đảm nhận việc phân tích kiến trúc
ARCHIFY_MODEL=claude-3-7-sonnet-20250219
```

### 6.3 An toàn và bảo mật thông tin
- Adapter đọc các tham số thông qua biến môi trường của hệ thống hoặc file cấu hình cục bộ không commit Git.
- Khóa bí mật luôn được ẩn khỏi các thông điệp ghi log và báo cáo kiểm thử.

---

## 7. Phân Hệ Standalone Interactive Viewer Runtime

Trọng tâm trải nghiệm người dùng nằm ở file artifact HTML xuất bản từ engine Archify.

### 7.1 Đặc tính Zero-Network & Tự chứa (Self-contained)
File HTML xuất bản có dung lượng khoảng 1.2MB, bao gồm:
- Toàn bộ vector đồ họa SVG biểu diễn kiến trúc và sơ đồ luồng.
- Bộ font JetBrains Mono định dạng WOFF2 được mã hóa Base64 trực tiếp.
- Bộ phong cách hiển thị Midnight Console cao cấp và toàn bộ mã nguồn JavaScript xử lý tương tác.
- Hoạt động ổn định trên mọi trình duyệt hiện đại mà không cần nạp bất kỳ tài nguyên mạng nào.

### 7.2 Bộ tính năng tương tác hỗ trợ phát triển
1. **Semantic Passport:** Nhấp vào nút để xem thông số chi tiết, cổng giao tiếp và các ràng buộc kỹ thuật.
2. **Upstream / Downstream Reachability:** Làm sáng toàn bộ chuỗi tác động trước và sau của một thành phần được chọn.
3. **Route-probe (`#route=A~B`):** Tự động dò tìm và đánh dấu đường đi ngắn nhất giữa hai nút bất kỳ trên sơ đồ.
4. **Semantic Lens & Minimap:** Cho phép lọc nhanh theo vai trò thành phần và điều hướng qua bản đồ thu nhỏ.
5. **Motion Governor:** Mô phỏng dòng chảy dữ liệu thực tế bằng các hạt ánh sáng chuyển động dọc theo liên kết.

---

## 8. Lộ Trình Triển Khai & Ma Trận Kiểm Thử Nghiệm Thu

### 8.1 Lộ trình triển khai 4 giai đoạn
- **Giai đoạn 1 — Đặc tả kiến trúc & Môi trường:** Hoàn thiện tài liệu kiến trúc tích hợp và khai báo cấu hình mẫu.
- **Giai đoạn 2 — Xây dựng module điều phối CLI:** Triển khai `scripts/tdq_archify.py` và cầu nối `graphify_to_archify`.
- **Giai đoạn 3 — Đồng bộ quy chuẩn kỹ năng:** Cập nhật các tài liệu chỉ dẫn cho `tdq-spec`, `tdq-intake` và `tdq-setup`.
- **Giai đoạn 4 — Kiểm thử & Nghiệm thu:** Xây dựng bộ test suite tự động và tiến hành thẩm định độc lập mức `ultra`.

### 8.2 Ma trận kiểm thử nghiệm thu (DoD Q1 - Q7)

| Mã | Hạng mục kiểm tra | Tiêu chí đạt | Lệnh kiểm chứng |
|---|---|---|---|
| Q1 | Tài liệu kiến trúc tích hợp | Hoàn thiện đủ 8 phân hệ, đạt chuẩn linting markdown | `python3 scripts/doc_lint.py docs/kien-truc-tich-hop-archify.md` |
| Q2 | Module CLI Adapter | Chạy độc lập bằng Python stdlib, hỗ trợ đầy đủ lệnh | `python3 scripts/tdq_archify.py check` |
| Q3 | Đồng bộ Spec & Quick Lane | Hướng dẫn rõ ràng việc sinh HTML preview và khối duyệt | `git diff skills/tdq-spec/ skills/tdq-intake/` |
| Q4 | Khai báo biến môi trường | File `.env.example` có đầy đủ các biến Archify | `git diff .env.example` |
| Q5 | Kiểm tra môi trường setup | Script cài đặt hỗ trợ kiểm tra Node.js và Archify | `python3 scripts/tdq_setup.py` |
| Q6 | Bộ unit test adapter | Tối thiểu 5 bài kiểm thử tự động đạt kết quả thành công | `pytest tests/test_tdq_archify.py` |
| Q7 | Thẩm định độc lập Ultra | Hoàn tất rà soát chất lượng và xác nhận mọi tiêu chí | `python3 scripts/tdq_qc.py danh-gia` |
