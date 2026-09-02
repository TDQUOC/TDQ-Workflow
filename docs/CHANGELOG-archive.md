# Changelog — bản lưu trữ

Các bản 0.17.0 trở về trước, tách khỏi `CHANGELOG.md`
để file chính nằm dưới trần R6 500 dòng. Mới nhất trên cùng.

## 0.17.0 — 2026-08-14

Trang trí khối chat cuối trả lời user: dùng markdown mà cả ba mặt (terminal, app,
extension) đều dựng được, tách nhãn khỏi nội dung, và chốt bằng test thay vì bằng trí nhớ.
Màu và cỡ chữ không làm được — ba mặt không dùng chung bộ dựng, mẫu số chung là markdown
terminal dựng được. Nguyên tắc xuyên suốt: **chỉ thêm dấu đánh dấu, không đổi một từ nào**
của nội dung đang chạy.

- `skills/tdq-conventions/references/user-facing-block.md`: viết lại. Thêm bảng 5 thành
  phần kèm cấu trúc trình bày dùng cho từng thành phần, mục `## Bảy luật trang trí`, bảng
  6 ký hiệu ngoài ASCII được phép, và ví dụ đối chiếu `### Trước` / `### Sau`.
- Luật cấm emoji giữ nguyên; chỗ nới đúng một điểm là ký hiệu Unicode, giới hạn trong sáu
  ký tự `➤ · — → – …`. Cả sáu đều có bằng chứng đang in ra cho user trong kho. Ký tự `▸`
  bị loại vì grep toàn kho ra 0 kết quả. Ký tự kẻ khung bị cấm vì đòi canh cột.
- Trang trí khối mẫu trong 8 file skill và 3 file bản portable: nhãn trường in đậm với dấu
  hai chấm nằm TRONG cặp sao, đường dẫn và tên lệnh bọc nháy ngược. Năm chỗ mã sinh chuỗi
  giữ nguyên từng byte để hook và test cũ không lệch.
- `skills/tdq-status/SKILL.md`: bỏ `✔` và `⏳` ở dòng báo trạng thái duyệt, thay bằng chữ
  in đậm. Đây là chỗ duy nhất trong kho còn dạy Claude in emoji ra cho user.
- `scripts/scan_block_symbols.py` (mới): quét ký tự Unicode loại `P*`/`S*` ngoài ASCII
  trong 12 file phạm vi, có chế độ `--chi-khoi` chỉ quét nội dung khối in cho user.
- `tests/test_user_facing_block.py`: 4 → 10 test (58 subtest). Thêm phép kiểm whitelist ký
  hiệu, phép kiểm khối mẫu theo luật 1/3/7, phép kiểm chuỗi do mã sinh, phép kiểm bản
  portable khớp khuôn gốc, và bảng `SO_KHOI` chặn trường hợp phép kiểm chạy rỗng mà vẫn
  xanh. Toàn bộ suite: 569 → 574 test.
