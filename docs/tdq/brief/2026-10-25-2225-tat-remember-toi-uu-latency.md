# BRIEF — Tắt Plugin Remember & Xử Lý Tối Ưu Latency Theo Đề Xuất
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

"tắt plugin remember và xử lý theo đề xuất"
"Tôi đã disable remember plugin r nên bạn ko cần lo về remember plugin nữa"

### Đọc hiểu ban đầu
- **Mục tiêu:**
  1. Người dùng đã tự tay disable plugin `remember` thành công (ngữ cảnh SessionStart đã giảm ngay lập tức hơn 11.6KB / 3,800 tokens thường trực).
  2. Tập trung triển khai 2 giải pháp tối ưu kỹ thuật cốt lõi theo đề xuất đã thống nhất:
     - **Tối ưu hóa Test Runner (`scripts/tdq_test.py`):**
       + Phân tầng kiểm thử: Trong pha `implement`, khi vùng chạm lan tỏa chạm ngưỡng 60% (`NGUONG_TRON_BO`), không tự động ép chạy 100% full test suite (2,978 tests / 638s) mà ưu tiên chạy targeted tests + smoke test suite nhanh (<10s).
       + Chỉ chạy 100% full test suite ở pha `qc` cuối cùng hoặc khi chỉ định cờ `--tron-bo` / mức QC `ultra`.
       + Hỗ trợ chạy đa nhân với `pytest -n auto` (khi có `pytest-xdist`) để rút ngắn thời gian full suite trên Windows từ ~10.6 phút xuống dưới 2.5 phút.
     - **Khắc phục điểm nghẽn Archify Chrome DevTools Pipe Timeout trên Windows:**
       + Bổ sung cơ chế fallback an toàn: Khi phát hiện môi trường Windows với process elevation (`IsUserAnAdmin=True`), không cố spawn browser với `--remote-debugging-pipe` để tránh timeout 1.5s-5s mỗi view; tự động chuyển sang xác thực static hash + DOM offline hoặc kết nối qua Chrome DevTools MCP sẵn có (Port 9222).
- **Phạm vi dự kiến:**
  - Chạm: `scripts/tdq_test.py`, `scripts/tdq_archify.py`, `scripts/tdq_finish.py`.
- **Điểm chưa rõ:** Không có.

## Hiểu & kiến thức

### 1. Phân tầng Test Runner (`scripts/tdq_test.py`)
- Hiện tại, hàm `ban_kinh` tự động trả về toàn bộ module (`tat_ca_module`) khi `len(chosen) >= NGUONG_TRON_BO * len(everything)` (60%).
- Điều này khiến việc sửa một file trung tâm trong phase `implement` kích hoạt chạy 2,978 tests (~10.6 phút), gây nghẽn nghiêm trọng.
- Giải pháp: Thêm cờ `--ep-tron-bo` (mặc định False ở phase `implement`). Khi ở phase `implement`, lệnh `vung-cham` chỉ chạy danh sách các module bị ảnh hưởng thực tế (`chosen`), thay vì ép chạy toàn bộ 100% test suite.
- Chỉ kích hoạt chạy 100% full suite ở phase `qc` hoặc khi người dùng truyền cờ `--ep-tron-bo`.
- Bổ sung tùy chọn chạy test song song qua `pytest -n auto` khi có `pytest-xdist`.

### 2. Fallback Archify Browser Check trên Windows (`scripts/archify_delivery.py`)
- Hiện tại hàm `_verify_finalize_gates` yêu cầu cổng `browser-check` phải là `"pass"` đối với mọi native diagram.
- Trên Windows Elevated (`IsUserAnAdmin=True`), cơ chế sandbox của Chrome relaunch tiến trình làm đứt pipe DevTools.
- Lỗi này gây ra timeout 1.5s - 5s mỗi view và chặn tiến trình finalize.
- Giải pháp: Thêm hàm kiểm tra `is_windows_elevated()`.
- Khi tiến trình chạy trên Windows có Elevation và các cổng `validate`, `deliver`, `check` đều đạt `pass`, cho phép cổng `browser-check` ở trạng thái `"not-run"` hoặc bỏ qua kiểm tra pipe trực tiếp.

## Hỏi đáp

- Người dùng đã chọn chế độ nhanh (express) và đã tự tay disable plugin `remember`.
- Không còn điểm vướng mắc hay giả định chưa rõ.

