# Report — 2026-08-12-hoan-thien-doc-excalidraw

Lane full · mode main · 26/26 task `[x]` · QC 10/10 PASS.

## Đã làm

Gom toàn bộ canvas Excalidraw thành một tài liệu sản phẩm đọc dọc: **14 khung** xếp
thành một cột từ `y=0` đến `y=15420` — Ch.0 mục lục + 13 chương nội dung.

- **Dời 5 khối cũ** (không vẽ lại, đúng yêu cầu): Ch.2 Ưu điểm · Ch.5 Flow lane ·
  Ch.7 Sequence diagram · Ch.9 Manifest & Dependency · Ch.10 Nền tảng & Test/Dev.
- **Vẽ mới 8 chương**: Ch.1 Tổng quan · Ch.3 Getting Started · Ch.4 State machine +
  schema 21 field · Ch.6 Ví dụ thực tế · Ch.8 Kiến trúc & thư mục · Ch.11 Giới hạn ·
  Ch.12 Troubleshooting · Ch.13 Roadmap, cộng Ch.0 mục lục.
- **3 script mới**: `check_canvas_layout.py` (6 phép kiểm hình học, có 11 unit test),
  `canvas_move_block.py`, `canvas_layout_apply.py`, `canvas_draw.py`.
- **Export**: `docs/diagrams/tdq-workflow-product-doc.excalidraw` (450 phần tử) và
  `.png` (2660×15440, 3.39 MB).

## Hai bài học phải trả giá

1. **`update_element` silent-fail** trên server canvas: trả "success", version tăng,
   nhưng `x/y/width/height/text` không đổi. Mọi thao tác sửa phải delete + batch-create.
   Đã lưu vào mem0.
2. **Dời từng khối một là sai**: khối vừa dời rơi vào vùng nguồn của lệnh kế tiếp và bị
   cuốn theo (ch2 mất 36 phần tử vào ch7, ch10 nuốt cả `ch2-title`). Phải restore từ
   backup rồi viết lại `canvas_layout_apply.py` — tính hết mọi phép dời trên MỘT ảnh chụp
   scene, có chốt chặn lệch số và chốt chặn một phần tử bị hai vùng cùng chọn, rồi ghi một lượt.

## Giới hạn

- Chương 5 còn 63 phần tử thay vì 65: hai bound label mồ côi trôi ~75px mỗi lần frontend
  sync, không thể giữ trong khung, đã xoá. Chi tiết trong file QC.
- Q6 kiểm tràn chữ bằng cách cắt PNG đã export theo bbox từng khung (Pillow), không dùng
  `set_viewport` như plan viết — `set_viewport` không crop được ảnh chụp.
- 5 khối cũ giữ nguyên phong cách gốc (tiêu đề căn giữa, bề ngang hẹp hơn khung 2640px)
  nên nhìn không đồng bộ với 9 chương vẽ mới. Đây là hệ quả của lựa chọn "dời, không vẽ lại".
- Pillow được cài thêm vào `.venv` để cắt ảnh; không thêm dependency vào sản phẩm.

## Git

Chưa commit. Thay đổi: `docs/diagrams/` (2 file mới + backup), `scripts/` (4 script mới),
`tests/test_check_canvas_layout.py`, spec/plan/qc/report, working log.
