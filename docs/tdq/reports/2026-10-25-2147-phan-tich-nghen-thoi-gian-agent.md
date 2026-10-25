# BÁO CÁO PHÂN TÍCH ĐIỂM NGHẼN THỜI GIAN CHẠY CỦA AGENT & ĐỀ XUẤT TỐI ƯU
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## 1. Tóm tắt thực trạng & Dữ liệu lịch sử

Khảo sát được thực hiện theo yêu cầu của người dùng nhằm tìm ra nguyên nhân khiến agent tốn nhiều thời gian gần đây.
Dữ liệu được trích xuất từ 133 bản ghi trong `docs/tdq/timing.jsonl` và thực nghiệm đo trực tiếp trên testbed Desktop.

### Bảng thời gian các request tiêu biểu gần đây

| Request (Slug) | Tổng thời gian (giờ/phút) | Pha chiếm nhiều thời gian nhất | Thời gian pha đó |
|---|---|---|---|
| `2026-10-24-2348-hoan-thien-archify` | 11.45 giờ (41,225s) | `plan` | 11.07 giờ (39,848s) |
| `2026-10-25-1113-phan-tich-muoi-issue` | 3.82 giờ (13,742s) | `implement` | 1.87 giờ (6,743s) |
| `2026-10-25-1648-mastermap-va-readme-pro` | 3.25 giờ (11,703s) | `idle` / `report` | 1.19h / 42.2 phút |
| `2026-10-25-1510-xu-ly-issue-nen` | 1.54 giờ (5,532s) | `report` | 41.2 phút (2,470s) |
| `2026-10-25-2025-auto-update-plugin` | 1.35 giờ (4,871s) | `idle` / `implement` | 67.3m / 13.4 phút |

Nhận xét: Thời gian trung bình cho một request phức tạp hiện nay dao động từ 1.5 giờ đến gần 4 giờ.
Cá biệt có những request lớn kéo dài trên 10 giờ.

---

## 2. Số liệu đo lường thực nghiệm từ Testbed Desktop

Một testbed đo lường độc lập đã được tạo tại `C:\Users\admin\Desktop\tdq-latency-benchmark`.
Testbed so sánh chi phí giữa dự án mẫu tối giản và dự án TDQ-Workflow thực tế.

### Bảng đối chiếu số liệu đo đạc thực tế

| Hạng mục kiểm thử | Dự án mẫu (Desktop Example) | Dự án TDQ-Workflow thực tế | Tỉ lệ chênh lệch |
|---|---|---|---|
| Chạy unit test (`pytest`) | **0.34 giây** (5 tests) | **638.0 giây** (2,978 tests) | Chậm hơn **1,876 lần** |
| Khởi động Python process | 0.022 giây / lần | 0.022 giây / lần | Tương đương |
| Kiểm tra git status | 0.005 giây | 0.049 giây | TDQ chậm hơn ~10 lần |
| Hook `stop_gate.py` | Không có | 0.265 giây / lần dừng | Chi phí bổ sung |
| Hook `session_start.py` | Không có | 0.205 giây / lần bắt đầu | Chi phí bổ sung |
| Script `tdq_checkstatus.py` | Không có | 0.248 giây / lần gọi | Chi phí bổ sung |
| Handshake Archify Chrome Pipe | 0.0 giây (bỏ qua) | 1.5s - 5.0s (timeout đóng pipe) | Chi phí nghẽn Windows |
| Kích thước Context nạp thường trực | ~500 bytes | **115,250 bytes (~38,400 tokens)** | Nặng hơn **230 lần** |

---

## 3. Căn nguyên 4 điểm nghẽn chính gây trễ thời gian

### Điểm nghẽn 1: Bùng nổ phạm vi kiểm thử (Blast Radius Escalation)
- **Cơ chế:** Trong `scripts/tdq_test.py`, hằng số `NGUONG_TRON_BO = 0.6` (60%).
- Khi agent chỉnh sửa các tệp lõi (`scripts/tdq_setup.py`, `scripts/tdq_finish.py`, `hooks/scripts/...`), thuật toán quét phụ thuộc AST tính ra hơn 120/162 module bị ảnh hưởng.
- Tỉ lệ vượt 60% kích hoạt chạy toàn bộ test suite của dự án gồm 2,978 bài test.
- Thời gian chạy full suite lên tới **638 giây (~10.6 phút)**.
- Bash tool của agent có ngưỡng timeout mặc định là 120 giây (2 phút).
- Khi lệnh chạy vượt 120 giây, tiến trình bị ngắt hoặc buộc phải đẩy vào background.
- Agent bị kẹt trạng thái chờ, dẫn tới việc thực thi bị gián đoạn và kéo dài qua nhiều turn.

### Điểm nghẽn 2: Archify Native Inspection Timeout trên Windows
- **Cơ chế:** Khi hoàn tất spec/plan hoặc chạy `tdq_finish.py`, Archify kiểm tra tính toàn vẹn của sơ đồ HTML bằng headless browser.
- Lệnh gọi sử dụng cờ `--remote-debugging-pipe`.
- Trên môi trường Windows với tài khoản Quản trị (Process Elevation `IsUserAnAdmin=True`), cơ chế sandbox của Chrome tự động khởi động lại tiến trình.
- Việc khởi động lại làm đứt gãy kết nối anonymous pipe của hệ điều hành: `Chrome DevTools read pipe failed: stream ended`.
- Mỗi lần thử nghiệm thất bại làm tiêu tốn từ 1.5 đến 5 giây cho mỗi góc nhìn.
- Với Master Map có 4 góc nhìn, thời gian chờ tích lũy lên tới 20 giây cho mỗi lượt kiểm tra.

### Điểm nghẽn 3: Phình to Context và trượt Prompt Cache (Context Bloat & Cache Miss)
- **Cơ chế:** Mỗi phiên làm việc nạp vào bộ nhớ ngữ cảnh một lượng dữ liệu rất lớn:
  - Tệp `.remember/today-*.md`: hơn 11,600 bytes (~3,800 tokens).
  - Tệp `docs/workinglog/*.md`: hơn 13,700 bytes (~4,500 tokens).
  - Tệp `CLAUDE.md` và luật TDQ: hơn 6,000 bytes (~2,000 tokens).
  - Lịch sử chat và công cụ: hàng chục nghìn tokens.
- Tổng dung lượng ngữ cảnh thường trực vượt 38,000 tokens ngay khi vừa khởi tạo.
- Khi ngữ cảnh quá lớn, độ trễ sinh từ (Inference Latency) của LLM tăng từ 3 giây lên 30-50 giây cho mỗi lượt phản hồi.
- Nếu một request có 30 lượt hội thoại, thời gian thuần túy chờ LLM phản hồi đã mất từ 15 đến 25 phút.
- Khi thời gian nghỉ giữa các lượt vượt 300 giây, TTL của prompt cache bị hết hạn, khiến mô hình phải đọc lại toàn bộ dữ liệu từ đầu.

### Điểm nghẽn 4: Thủ tục phân mảnh quá nhiều bước trong Deep Mode
- **Cơ chế:** Quy trình Deep Pipeline hiện tại yêu cầu tuân thủ nghiêm ngặt từng bước nhỏ:
  - Đổi tick mini-plan sang `[~]`.
  - Viết mã nguồn và chạy test đỏ/xanh.
  - Đổi tick sang `[x]`.
  - Cập nhật nhật ký công việc `workinglog`.
  - Chạy `tdq_finish.py` với nhiều bộ kiểm tra lint, git status, và archify status.
- Một request có 11 nhiệm vụ sẽ nhân chi phí thủ tục lên gấp 11 lần (hơn 50 lượt gọi công cụ).
- Bất kỳ lỗi nhỏ nào về độ dài câu markdown (Luật R5 vượt 40 từ) hoặc lệch hash tệp đều chặn đứng quy trình và bắt buộc agent phải sửa lại.

---

## 4. Bảng phân tích SWOT các giải pháp khắc phục

| Tiêu chí | Giải pháp A: Tối ưu Test Runner & Blast Radius | Giải pháp B: Khắc phục Archify Pipe trên Windows | Giải pháp C: Nén Context & Tối ưu Cache |
|---|---|---|---|
| **Hiệu quả giảm thời gian** | **Giảm 10 - 30 phút mỗi request** | Giảm 20 - 60 giây mỗi lần finish | Giảm 5 - 15 phút thời gian chờ model |
| **Độ phức tạp kỹ thuật** | Trung bình (sửa ngưỡng và cơ chế batching) | Thấp (chuyển sang DevTools port hoặc static hash) | Thấp (cắt ngắn buffer `.remember` và log) |
| **Rủi ro hồi quy** | Thấp (vẫn giữ full suite ở khâu QC cuối) | Rất thấp (không phụ thuộc pipe trên Windows) | Không có |

---

## 5. Lộ trình đề xuất giải pháp cụ thể

### Nhóm 1: Tối ưu Test Runner (Ưu tiên cao nhất)
1. **Nâng ngưỡng chuyển đổi hoặc phân tầng Test:**
   - Thay vì chạy ngay toàn bộ 2,978 tests khi chạm file lõi trong pha `implement`, chỉ chạy smoke tests và các test trực tiếp (dưới 50 tests, runtime < 10 giây).
   - Chỉ bắt buộc chạy 100% full test suite ở phase `qc` cuối cùng (hoặc chỉ ở mức QC `ultra`).
2. **Kích hoạt chạy song song với `pytest -n auto`:**
   - Cài đặt `pytest-xdist` để tận dụng đa nhân CPU trên Windows.
   - Thời gian chạy full suite sẽ giảm từ 10.6 phút xuống còn dưới 2.5 phút.

### Nhóm 2: Tối ưu Archify Viewer trên Windows (Ưu tiên cao)
1. **Chuyển đổi cơ chế kiểm tra Browser trên Windows:**
   - Khi phát hiện môi trường Windows elevated, Archify tự động dùng kiểm tra hash tĩnh và xác thực DOM offline.
   - Hoặc kết nối qua Chrome DevTools MCP sẵn có (Port 9222) thay vì spawn process với `--remote-debugging-pipe`.

### Nhóm 3: Thu gọn Context và duy trì Prompt Cache (Ưu tiên trung bình)
1. **Tự động xoay vòng và cắt tỉa `.remember/today-*.md`:**
   - Giới hạn kích thước tệp nạp vào context dưới 4KB (thay vì 11.6KB).
   - Chỉ nạp các mục tóm tắt 3 giờ gần nhất, phần còn lại lưu trữ trong thư mục lưu trữ.
2. **Tối ưu hóa thời gian chờ (Keep-alive):**
   - Giữ các lượt tương tác của agent trong vòng 270 giây để bảo toàn prompt cache.

### Nhóm 4: Nới lỏng kiểm tra thủ tục trong pha phát triển nhanh
1. **Cho phép gộp thao tác kết thúc:**
   - Cho phép cập nhật nhật ký và chạy `tdq_finish.py` một lần ở cuối pha thay vì chạy sau từng nhiệm vụ nhỏ.
