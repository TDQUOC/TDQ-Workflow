# PLAN — Thêm lệnh xoá cache cho mô-đun tiện ích

Ngày: 2026-08-19 · Spec: ../spec/2026-08-19-0900-them-lenh-xoa-cache.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — plan nhỏ, ba task cùng sửa một file (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: CHỜ DUYỆT

## Quy tắc thi hành (áp cho mọi task)
1. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi `[x]` NGAY.
2. Không commit/push cho đến khi user yêu cầu.

## P1 — Hàm xoá cache
- [ ] **T1.1** (e6m) Test đỏ cho `xoa_cache`: xoá hết `.tmp`, giữ file khác — Test: `python3 -m pytest tests/test_tien_ich.py -q` đỏ đúng ca mới
  - Chạm: `tests/test_tien_ich.py`
- [ ] **T1.2** (e8m) Viết `xoa_cache(thu_muc)` trong mô-đun tiện ích — Test: ca của T1.1 xanh
  - Chạm: `src/tien_ich.py`
  - Cần: T1.1
- [ ] **T1.3** (e5m) Ca thư mục rỗng và thư mục không tồn tại — Test: `python3 -m pytest tests/test_tien_ich.py -q` xanh
  - Chạm: `tests/test_tien_ich.py`
  - Cần: T1.2

## Cụm song song
Một cụm: cả ba task đụng chung mô-đun tiện ích và test của nó.

## Definition of Done
- Q1 hàm chạy đúng — `python3 -m pytest tests/test_tien_ich.py -q` xanh.
- Q2 có test riêng — test của mô-đun có đủ ba ca.
