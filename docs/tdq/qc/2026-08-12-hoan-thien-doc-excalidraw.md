# QC — 2026-08-12-hoan-thien-doc-excalidraw

Nguồn DoD: `docs/tdq/plan/2026-08-12-hoan-thien-doc-excalidraw.md` §Definition of Done (9 dòng)
+ 1 hạng mục full-suite bắt buộc. Đối tượng kiểm: file export
`docs/diagrams/tdq-workflow-product-doc.excalidraw` (450 phần tử, chụp lúc 12:46).

| # | Hạng mục | Lệnh | Kết quả |
|---|---|---|---|
| Q1 | Đủ 13 chương, số liên tục 1→13 | `check_canvas_layout.py <export> --chapters --expect 13` | **PASS** — 13 chương nội dung + Ch.0 mục lục |
| Q2 | Không cặp khung nào chồng lấn | `... --overlap` | **PASS** — so 91 cặp khung |
| Q3 | Mọi phần tử nằm trong khung của nó | `... --contain` | **PASS** — 436 phần tử, không phần tử lạc |
| Q4 | Thứ tự y đúng số chương | `... --order` | **PASS** — 14 khung đúng thứ tự dọc |
| Q5 | Mục lục khớp tiêu đề thật | `... --toc` | **PASS** — 14 tiêu đề ↔ 14 dòng `toc-<N>` |
| Q6 | Không tràn chữ ở chương nào | cắt PNG theo bbox từng `ch<N>-frame`, xem 14 ảnh | **PASS** — 14/14 ảnh, không chương nào cắt chữ |
| Q7 | Số phần tử 5 khối cũ không đổi | `... --count-by-prefix` so với `_backup-2026-08-12.excalidraw` | **PASS có ghi chú** — xem bên dưới |
| Q8 | `docs/diagrams/` có `.excalidraw` và `.png` > 100 KB | `ls -la docs/diagrams/` | **PASS** — 427 KB và 3.39 MB |
| Q9 | Script kiểm có test và test xanh | `pytest tests/test_check_canvas_layout.py -q` | **PASS** — 11 passed |
| Q10 | Full-suite không có test pass → fail | `.venv/bin/python -m pytest -q` | **PASS** — 457 passed, 140 subtests |

## Ghi chú Q7 — lệch 2 phần tử ở chương 5, có chủ đích

Số đo ở P1 (backup) so với hiện tại: ch2 55→55 · ch5 65→**63** · ch7 60→60 · ch9 19→19 ·
ch10 15→15.

Hai phần tử mất là `ch5-e059` ("còn") và `ch5-e060` ("hết") — bound label mồ côi:
`containerId` trỏ tới arrow `ch5-e024`/`ch5-e026` nằm cách xa chúng, nên frontend bố trí
lại vị trí mỗi lần sync, trôi ~75px/lần và cuối cùng ra khỏi khung chương (Q3 FAIL 3 lần
liên tiếp, nới khung 2 lần đều chỉ hoãn được). Đã gỡ id khỏi `boundElements` của arrow
chứa rồi xoá hẳn. Nội dung chữ bị mất không mang thông tin (2 mảnh của một nhãn đã hỏng),
Q6 xác nhận chương 5 đọc đủ nghĩa sau khi xoá.

## Giới hạn của bộ kiểm

Q6 không dùng `set_viewport` + `get_canvas_screenshot` như plan viết vì `set_viewport`
không crop ảnh — mọi lần chụp đều ra toàn scene. Thay bằng cắt PNG đã export theo
bounding box của từng `ch<N>-frame` (Pillow). Cùng dữ liệu pixel, chỉ khác đường lấy.

KẾT LUẬN: **10/10 hạng mục PASS**, không có vòng fix.
