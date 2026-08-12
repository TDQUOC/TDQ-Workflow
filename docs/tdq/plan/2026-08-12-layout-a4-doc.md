# PLAN — Đổi tài liệu sản phẩm sang khổ A4 dọc (bề ngang 1240px)

Ngày: 2026-08-12 · Spec: ../spec/2026-08-12-layout-a4-doc.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — mọi task ghi vào CÙNG một canvas sống `127.0.0.1:17739`; chạy song song trong worktree riêng không cô lập được canvas và sẽ giẫm chân nhau đúng như sự cố dời khối ở request trước (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: ĐÃ DUYỆT

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Mọi thao tác sửa phần tử trên canvas: DELETE + `POST /api/elements/batch`, KHÔNG dùng
   `update_element` (silent-fail đã xác nhận 2 lần).
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — Chốt chặn an toàn & bộ kiểm mới

- [x] **T1.1** (n1) Backup scene hiện tại ra `docs/diagrams/_backup-a4-2026-08-12.excalidraw` — Test: `python3 -c "import json;print(len(json.load(open('docs/diagrams/_backup-a4-2026-08-12.excalidraw'))['elements']))"` in ra ≥ 450
- [x] **T1.2** (n3) Thêm cờ `--width <px>` vào `check_canvas_layout.py`: mọi `ch<N>-frame` phải có `width` bằng đúng số cho trước (sai số `TOL`) — Test: `pytest tests/test_check_canvas_layout.py -q -k width` — 1 ca đúng + 1 ca sai, xanh
- [x] **T1.3** (n3) Thêm cờ `--fontsize <min>` vào `check_canvas_layout.py`: không phần tử `type=="text"` nào có `fontSize` nhỏ hơn ngưỡng, báo id + cỡ khi FAIL — Test: `pytest tests/test_check_canvas_layout.py -q -k fontsize` — 1 ca đúng + 1 ca sai, xanh
- [x] **T1.4** (n1) Đưa `--width`/`--fontsize` vào nhánh `--all` và cập nhật `--help` — Test: `python3 scripts/check_canvas_layout.py --help` liệt kê cả hai cờ

**Xong P1 khi**: `pytest tests/test_check_canvas_layout.py -q` xanh với ≥ 15 test, file backup tồn tại.

## P2 — Đổi khổ trong bộ dựng

- [x] **T2.1** (n2) `canvas_draw.py`: `W = 2640 → 1240`; `CHAPTER_W` trong `canvas_move_block.py` theo cùng — Test: `grep -n "^W = 1240" scripts/canvas_draw.py` và `grep -n "CHAPTER_W = 1240" scripts/canvas_move_block.py` đều khớp
- [x] **T2.2** (n3) `canvas_draw.py`: nâng mặc định cỡ chữ — `text(size=16)`, `card(head_size=20, body_size=16)`, tiêu đề chương 30; `row()` mặc định `margin=40, gap=24` cho khổ hẹp — Test: dựng một chương thử ở canvas rỗng, `--fontsize 14` exit 0
- [x] **T2.3** (n3) Thêm hàm `stack(top, heights, gap=24)` vào `Chapter` trả về danh sách `y` cho bố cục 1 cột, thay cho gọi `row()` nhiều cột — Test: unit test thuần hàm trong `tests/test_canvas_draw.py`, kiểm y liên tiếp cách nhau đúng `h+gap`

**Xong P2 khi**: `fit()` không cảnh báo khi dựng chương thử, test suite xanh.

## P3 — Vẽ lại 10 chương theo 1 cột

Mỗi task: xoá sạch `ch<N>-*` cũ rồi dựng lại trong khung rộng 1240, kiểm ngay bằng
`--contain --fontsize 14` trên chương đó trước khi sang chương sau.

- [x] **T3.1** (n5) Vẽ lại Ch.1 Tổng quan — Test: `check_canvas_layout.py <live> --contain --fontsize 14` exit 0, không cảnh báo `fit()`
  - Dùng: `excalidraw-skill` (mcp)
  - Để: áp luật bề rộng chữ tiếng Việt `k≈0,75`, luật chữ ≤ 70% bề rộng ô và luật
    chụp-kiểm sau mỗi batch cho toàn bộ P3–P4; nạp skill TRƯỚC task này. Agent ngoài
    không có skill system: đọc `~/.claude/skills/excalidraw-skill/SKILL.md` rồi làm theo.
  - Ra: các phần tử `ch1-*` trên canvas sống, thấy được trong `docs/diagrams/tdq-workflow-product-doc.excalidraw` sau P5
  - Kiểm: `python3 scripts/check_canvas_layout.py http://127.0.0.1:17739/api/elements --contain --fontsize 14` exit 0
  - Không dùng cho: sửa `check_canvas_layout.py` ở P1 — đó là code Python thuần, không đụng canvas
- [x] **T3.2** (n5) Vẽ lại Ch.3 Getting Started — Test: như trên
- [x] **T3.3** (n8) Vẽ lại Ch.4: 8 node state machine xếp DỌC + bảng schema 21 field một cột — Test: như trên, và `--fontsize 14` exit 0 (hiện chương này có chữ 11px)
- [x] **T3.4** (n5) Vẽ lại Ch.6 Ví dụ thực tế — Test: như trên
- [x] **T3.5** (n8) Vẽ lại Ch.7 sequence diagram: giữ 6 lane, mỗi lane ~193px, nhãn message đặt PHÍA TRÊN mũi tên và canh trái theo điểm đầu, KHÔNG dùng bound label — Test: như trên, thêm `--contain` chạy lại sau 30s để chắc không có nhãn trôi
- [x] **T3.6** (n5) Vẽ lại Ch.8 Kiến trúc & thư mục (số script lấy bằng `ls -1 scripts/*.py | wc -l` tại thời điểm vẽ) — Test: như trên, số trên canvas khớp output lệnh đếm
- [x] **T3.7** (n5) Vẽ lại Ch.11 Giới hạn — Test: như trên
- [x] **T3.8** (n5) Vẽ lại Ch.12 Troubleshooting — Test: như trên
- [x] **T3.9** (n5) Vẽ lại Ch.13 Roadmap — Test: như trên

**Xong P3 khi**: 9 chương trên đều `--contain --fontsize 14` exit 0.

## P4 — Dời 4 khối cũ vào khung mới

- [x] **T4.1** (n3) Tính bảng `MOVES` mới trong `canvas_layout_apply.py`: y đích của cả 14 khung theo chiều cao thật sau P3, khung Ch.2/5/9/10 rộng 1240, nội dung khối căn giữa theo trục ngang — Test: chạy chế độ khô (in bảng, chưa ghi) không báo lệch số phần tử và không có phần tử bị hai vùng cùng chọn
- [x] **T4.2** (n5) Ghi một lượt: xoá hết phần tử cũ TRƯỚC, rồi batch-create toàn bộ — Test: `check_canvas_layout.py <live> --count-by-region` cho Ch.2 = 55, Ch.5 = 63, Ch.9 = 19, Ch.10 = 15
- [x] **T4.3** (n3) Vẽ lại Ch.0 mục lục đủ 14 dòng `toc-0`…`toc-13` khớp tiêu đề thật — Test: `--toc` exit 0

**Xong P4 khi**: `--chapters --overlap --contain --order --toc --width 1240 --fontsize 14` trên canvas sống đều exit 0.

## P5 — Export & kiểm hình

- [x] **T5.1** (n2) Export `docs/diagrams/tdq-workflow-product-doc.excalidraw` — Test: `json.load` được, chạy lại toàn bộ cờ kiểm trên FILE cũng exit 0
- [x] **T5.2** (n2) Export `docs/diagrams/tdq-workflow-product-doc.png` — Test: `ls -la` cho file > 100 KB, bề ngang ảnh ≤ 1400px
- [x] **T5.3** (n3) Cắt PNG theo bbox từng `ch<N>-frame` bằng Pillow rồi XEM đủ 14 ảnh — Test: 14/14 ảnh không chương nào cắt chữ
- [x] **T5.4** (n1) Lưu 1 fact về khổ 1240px đã chốt để lần sau vẽ đúng ngay — Test: `list_memories` (project = TDQWorkflow) trả về fact vừa lưu
  - Dùng: `mem0-memory` (mcp)
  - Để: ghi đúng một fact ngắn "tài liệu Excalidraw của repo dùng khổ A4 dọc 1240px,
    chữ thân 16 / tối thiểu 14 / tiêu đề 30"; nạp skill TRƯỚC khi gọi tool.
  - Ra: một memory trong mem0 project `TDQWorkflow`
  - Kiểm: `search_memories` với từ khoá "1240" trả về đúng fact đó
  - Không dùng cho: lưu nội dung chương hay số đo từng chương — chỉ lưu quy ước khổ

## Px — Log & test bắt buộc

Log: BỎ — việc này không tạo runtime; `check_canvas_layout.py` là công cụ kiểm chạy một
lần, in kết quả ra stdout rồi thoát, không có tiến trình nền để log.

- [x] **Tx.1** (n2) Unit test cho hai cờ mới và cho `stack()`, chạy bằng một lệnh — Test: `.venv/bin/python -m pytest tests/test_check_canvas_layout.py tests/test_canvas_draw.py -q` xanh
- [x] **Tx.2** (n1) Full-suite không có test pass → fail — Test: `.venv/bin/python -m pytest -q` không test nào đỏ

## Definition of Done

Trỏ về §6 của spec, 12 hạng mục:

1. Q1 đủ 13 chương — `check_canvas_layout.py <export> --chapters --expect 13`
2. Q2 mọi khung rộng 1240 — `... --width 1240`
3. Q3 không khung nào chồng lấn — `... --overlap`
4. Q4 mọi phần tử trong khung của nó — `... --contain`
5. Q5 thứ tự y đúng số chương — `... --order`
6. Q6 mục lục khớp tiêu đề — `... --toc`
7. Q7 không text nào `fontSize` < 14 — `... --fontsize 14`
8. Q8 4 khối cũ đủ phần tử — `... --count-by-region` (55 / 63 / 19 / 15)
9. Q9 không chương nào tràn chữ — xem 14 ảnh cắt theo khung
10. Q10 hai cờ mới có test — `pytest tests/test_check_canvas_layout.py -q`
11. Q11 hai file export tồn tại — `ls -la docs/diagrams/`
12. Q12 full-suite không đỏ — `.venv/bin/python -m pytest -q`
