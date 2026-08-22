# SPEC — Thêm lệnh xoá cache cho mô-đun tiện ích

Ngày: 2026-08-19 · Bản: 1.0 · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi
Thêm hàm `xoa_cache(thu_muc)` vào `src/tien_ich.py` để dọn file tạm, có test riêng.

## 2. Đầu ra cụ thể
| # | Đầu ra | Đường dẫn | Đo "xong" bằng |
|---|---|---|---|
| 1 | Hàm `xoa_cache` | `src/tien_ich.py` | xoá đúng file `.tmp`, giữ file khác |
| 2 | Test cho hàm mới | thư mục test | có ca xoá đúng và ca thư mục rỗng |

## 6. QC & Definition of Done
| # | Hạng mục | Điều kiện PASS |
|---|---|---|
| Q1 | Hàm chạy đúng | xoá hết `.tmp`, không đụng file khác |
| Q2 | Có test riêng | test của mô-đun xanh |
