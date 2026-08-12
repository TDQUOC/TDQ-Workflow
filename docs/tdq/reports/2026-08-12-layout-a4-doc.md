# REPORT — Tài liệu sản phẩm Excalidraw đổi sang khổ A4 dọc

Ngày: 2026-08-12 · Lane full · Mode main · Spec/Plan: `docs/tdq/{spec,plan}/2026-08-12-layout-a4-doc.md`

## Đã làm
- Chốt khổ **1240px** (A4 dọc @150dpi), bố cục MỘT cột, chữ thân 16 / tối thiểu 14 / tiêu đề 30.
- Thêm 2 phép kiểm máy `--width` và `--fontsize` vào `scripts/check_canvas_layout.py` (+6 test).
- `canvas_draw.py`: `W = 1240`, nâng cỡ chữ mặc định, thêm hàm `stack()` cho bố cục 1 cột (+14 test).
- `scripts/canvas_a4_rebuild.py` (mới): dựng TOÀN BỘ scene ra file nháp → kiểm bằng máy → mới xoá
  canvas và tạo lại một lượt. Câu chữ giữ nguyên, chỉ ngắt dòng lại (`unwrap` + `rewrap`).
- `scripts/canvas_a4_ch4_ch7.py` (mới): dựng tay Ch.4 (8 state xếp dọc + schema 21 field 1 cột) và
  Ch.7 (sequence 6 lane ~193px, nhãn đặt trên mũi tên).
- 4 khối vốn đã hẹp (Ch.2/5/9/10) chỉ dời và căn giữa, không vẽ lại.
- Export lại `.excalidraw` (393 phần tử) và `.png` (1260×19448).

## Kết quả QC
12/12 hạng mục PASS — chi tiết `docs/tdq/qc/2026-08-12-layout-a4-doc.md`. Full-suite 477 test xanh.

## Điểm cần biết
- Ch.6 mất 6 mũi tên nối khi chuyển 1 cột; thứ tự vẫn rõ nhờ đầu thẻ đánh số 1…7.
- Con số Q8 trong plan (55/63/19/15) là số cũ; số máy đúng là 54/62/18/14 trên cả backup lẫn bản
  mới, tập id trùng khít → không mất phần tử.
- Tổng chiều cao tài liệu 19.549px; backup an toàn ở `docs/diagrams/_backup-a4-2026-08-12.excalidraw`.

## Commit
Chưa commit gì. Request trước (`2026-08-12-hoan-thien-doc-excalidraw`) cũng còn chờ bạn quyết.
