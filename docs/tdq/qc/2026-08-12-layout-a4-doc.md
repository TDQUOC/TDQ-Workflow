# QC — Đổi tài liệu sản phẩm sang khổ A4 dọc (1240px)

Ngày: 2026-08-12 · Plan: ../plan/2026-08-12-layout-a4-doc.md · Lane full · Mode main
Kiểm trên file export `docs/diagrams/tdq-workflow-product-doc.excalidraw` (393 phần tử).

| # | Hạng mục | Lệnh | Kết quả |
|---|---|---|---|
| Q1 | Đủ 13 chương, số liên tục | `check_canvas_layout.py <export> --chapters --expect 13` | PASS — 13 chương |
| Q2 | Mọi khung rộng 1240px | `--width 1240` | PASS — 14/14 khung |
| Q3 | Không khung nào chồng lấn | `--overlap` | PASS — 91 cặp |
| Q4 | Mọi phần tử nằm trọn trong khung | `--contain` | PASS — 379 phần tử |
| Q5 | Thứ tự dọc khớp số chương | `--order` | PASS |
| Q6 | Mục lục khớp tiêu đề thật | `--toc` | PASS — 14/14 dòng |
| Q7 | Không text nào cỡ < 14 | `--fontsize 14` | PASS |
| Q8 | 4 khối dời đủ phần tử | `--count-by-region` | PASS — xem ghi chú dưới |
| Q9 | Không chương nào tràn chữ | cắt PNG theo bbox từng khung, xem 14 ảnh | PASS — 14/14 |
| Q10 | Hai cờ mới có test | `pytest tests/test_check_canvas_layout.py -q` | PASS — 17 test |
| Q11 | Hai file export tồn tại | `ls -la docs/diagrams/` | PASS — .excalidraw 372 KB, .png 3,6 MB (1260×19448) |
| Q12 | Full-suite không đỏ | `.venv/bin/python -m pytest -q` | PASS — 477 test + 140 subtest |

## Ghi chú Q8 — con số 55/63/19/15 trong plan là số CŨ

`--count-by-region` cho Ch.2 = 54, Ch.5 = 62, Ch.9 = 18, Ch.10 = 14. Chạy đúng lệnh đó
trên bản backup `_backup-a4-2026-08-12.excalidraw` cũng ra 54/62/18/14 — chênh đúng 1 vì
phép đếm theo vùng KHÔNG tính chính khung `ch<N>-frame`. Đối chiếu tập id giữa backup và
bản mới: trùng khít, không mất phần tử nào. Kết luận: không có lỗi, số trong plan chép
nhầm từ QC request trước.

## Sai lệch có chủ ý (không phải lỗi)

- Ch.6: 6 mũi tên nối bị bỏ khi chuyển sang 1 cột (28 → 23 phần tử). Thứ tự vẫn rõ vì
  đầu thẻ đã đánh số "1 · Intake" … "7 · Report".
- Ch.4: 88 → 37 phần tử; Ch.0: 16 → 15 — do dựng lại theo cấu trúc dọc.
- Ch.1, 3, 8, 11, 12, 13: giữ nguyên số phần tử.
- Ch.8: dòng cây thư mục được bóp khoảng đệm giữa hai cột (`squeeze_tree_line`) thay vì
  ngắt theo từ — có test riêng trong `tests/test_canvas_draw.py`.
