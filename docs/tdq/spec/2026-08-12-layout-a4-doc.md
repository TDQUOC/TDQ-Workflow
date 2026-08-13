# SPEC — Đổi tài liệu sản phẩm sang khổ A4 dọc (bề ngang 1240px)

Ngày: 2026-08-12 · Bản: 1.0 · Brief: ../brief/2026-08-12-layout-a4-doc.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi

- **Mục tiêu.** Dựng lại toàn bộ tài liệu sản phẩm trên canvas Excalidraw theo bề ngang
  khổ A4 dọc **1240px** (A4 @150dpi), cỡ chữ thân **16** / chú thích tối thiểu **14** /
  tiêu đề chương **30**, để khi zoom vừa bề ngang vào cửa sổ ~1400px thì tỉ lệ hiển thị
  ≥ 1,0 và chữ thân hiện ra ≥ 16px thay vì ~7px như hiện nay.

- **Trong phạm vi:**
  - 14 khung (Ch.0 mục lục + Ch.1–Ch.13), mỗi khung `x = 40`, `width = 1240`.
  - Vẽ lại 10 chương: Ch.0, 1, 3, 4, 6, 7, 8, 11, 12, 13 — 8 chương vì đang xếp 2–3 cột,
    Ch.4 và Ch.7 vì rộng do bản chất (state machine xếp ngang, sequence diagram 6 lane).
  - Dời 4 khối cũ **không vẽ lại**: Ch.2 (760px), Ch.5 (940px), Ch.9 (760px), Ch.10 (760px)
    — đo được là đã hẹp hơn 1240px nên chỉ cần căn lại vào khung mới.
  - Sửa hằng số khổ trong `scripts/canvas_draw.py` và `scripts/canvas_move_block.py`.
  - Thêm 2 phép kiểm mới vào `scripts/check_canvas_layout.py`: `--width` (mọi khung rộng
    đúng số cho trước) và `--fontsize` (không text nào nhỏ hơn ngưỡng), kèm unit test.
  - Export lại `.excalidraw` + `.png` vào `docs/diagrams/`.

- **NGOÀI phạm vi:**
  - Đổi **nội dung** chữ của bất kỳ chương nào. Đây là việc đổi khổ, không phải viết lại.
    Ngoại lệ duy nhất: xuống dòng lại (`\\n`) cho vừa bề ngang mới — cùng câu chữ.
  - Thêm hay bớt chương. Vẫn đúng 13 chương nội dung + mục lục.
  - Cắt trang / ép chiều cao thành bội số 1754px (user chọn 2A: chiều cao thả tự do).
  - Xuất PDF. Chỉ `.excalidraw` và `.png` như hiện tại.
  - Sửa 4 khối cũ ở mức nội dung — chúng chỉ được dời.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | **BỎ** | A4 là hằng số ISO 216; số liệu còn lại đo từ file export trong repo |
| Interview | **CÓ — đã xong** | 4 câu, user trả lời `1A 2A 3A 4A` lúc 13:04 |
| Spec + plan (2 gate duyệt) | **CÓ** | Vẽ lại 10 chương; chốt sai khổ là làm lại toàn bộ |
| Chia subagent | **BỎ** | Mọi task ghi vào CÙNG một canvas sống; song song sẽ giẫm chân nhau đúng như sự cố dời khối ở request trước |
| QC độc lập (agent) | **BỎ** | Bằng chứng QC là output máy của `check_canvas_layout.py` + 14 ảnh cắt theo khung — đọc trực tiếp được |
| Report | **CÓ** | Khung bất biến |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | 14 khung đều rộng đúng 1240px tại `x = 40` | canvas sống + file export | `check_canvas_layout.py --width 1240` exit 0 |
| 2 | 10 chương vẽ lại theo 1 cột | Ch.0, 1, 3, 4, 6, 7, 8, 11, 12, 13 | `--contain --overlap --order` exit 0 |
| 3 | 4 khối cũ dời nguyên vẹn | Ch.2, 5, 9, 10 | `--count-by-region` cho 55 / 63 / 19 / 15 phần tử |
| 4 | Không text nào `fontSize` < 14 | mọi phần tử text | `check_canvas_layout.py --fontsize 14` exit 0 |
| 5 | Cờ `--width` + `--fontsize` có unit test | `scripts/check_canvas_layout.py`, `tests/test_check_canvas_layout.py` | `pytest tests/test_check_canvas_layout.py -q` xanh, có ca đúng + ca sai cho mỗi cờ |
| 6 | Mục lục 14 dòng khớp tiêu đề thật | Ch.0 | `--toc` exit 0 |
| 7 | File scene export lại | `docs/diagrams/tdq-workflow-product-doc.excalidraw` | `json.load` được, mọi phép kiểm trên file đều exit 0 |
| 8 | Ảnh PNG export lại | `docs/diagrams/tdq-workflow-product-doc.png` | bề ngang ảnh ≤ 1400px, > 100 KB |
| 9 | Không chương nào tràn chữ | 14 ảnh cắt theo khung | xem đủ 14/14, không chương nào cắt chữ |

## 3. Cách tiếp cận & lý do

- **Chọn:** đổi hằng số `W = 2640 → 1240` trong `canvas_draw.py` (và `CHAPTER_W` trong
  `canvas_move_block.py`), nâng mặc định cỡ chữ trong `Chapter.text/card`, rồi **vẽ lại**
  10 chương bằng chính bộ dựng đó — mỗi chương một khối script khai báo, thẻ xếp 1 cột.
  Bốn khối cũ đã hẹp thì dời bằng `canvas_layout_apply.py`.

- **Vì:** hàm `fit()` trong `canvas_draw.py` đã cảnh báo mọi dòng vượt 70% bề rộng ô — đổi
  `W` xuống 1240 là nó tự bắt hết chỗ tràn khi vẽ lại, không phải soi mắt. Bộ kiểm hình học
  đã có sẵn và đã có test, chỉ cần thêm 2 cờ. Đây là con đường đã chạy được ở request trước,
  chi phí thấp nhất.

- **Đã loại — thu nhỏ toàn cảnh (scale 0,47):** giữ nguyên hình, nhân mọi toạ độ và cỡ chữ
  với 1240/2640. Loại vì tỉ lệ chữ/bề ngang không đổi → chữ vẫn nhỏ y như cũ. Đây đúng là
  cái bệnh đang có.

- **Đã loại — cho Ch.4 và Ch.7 làm "trang ngang" ngoại lệ:** user chọn 3A, và một tài liệu
  hai khổ thì mỗi lần cuộn qua phải zoom lại.

- **Đã loại — cắt trang đúng A4 (1240×1754):** user chọn 2A. Excalidraw không có khái niệm
  trang; ép bội số chiều cao sẽ chèn khoảng trắng lớn giữa các chương ngắn.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `excalidraw-skill` | user | DÙNG | Đầu ra 1–3, 6–9: luật cỡ chữ tiếng Việt `k≈0,75`, luật chữ ≤ 70% bề rộng ô, luật chụp-kiểm sau mỗi batch |
| `mem0-memory` | user | DÙNG | Sau khi chốt: lưu 1 fact về khổ 1240px để lần sau vẽ đúng ngay |
| `tdq-intake` / `tdq-spec` / `tdq-plan` / `tdq-build` / `tdq-conventions` | project | NỀN | Skill khung đang chạy request này |
| Đã xét 268 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- **Log service: BỎ** — việc này không tạo runtime. `check_canvas_layout.py` là công cụ
  kiểm chạy một lần, in kết quả ra stdout rồi thoát; không có tiến trình chạy nền để log.
- Không placeholder, không TODO stub. Mọi số liệu trên canvas phải truy được về file thật
  trong repo, y như luật đã áp ở request trước.
- Hai cờ mới `--width` và `--fontsize` mỗi cờ có ít nhất một ca đúng và một ca sai trong
  `tests/test_check_canvas_layout.py`, chạy được bằng một lệnh.

## 5. Ràng buộc & rủi ro

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| `update_element` silent-fail trên server canvas | Sửa toạ độ tưởng xong mà không đổi | Luật cũ: chỉ DELETE + `POST /api/elements/batch`, verify bằng `get_element` |
| Dời nhiều khối tuần tự làm khối đã dời rơi vào vùng nguồn khối sau | Mất phần tử, đúng sự cố đã xảy ra | `canvas_layout_apply.py`: tính mọi phép dời trên MỘT ảnh chụp, có chốt chặn lệch số và chốt chặn hai vùng cùng chọn một phần tử |
| Bề ngang 1240 nhưng nội dung cũ viết cho 2540 | Chữ tràn ô hàng loạt | `fit()` cảnh báo ngay lúc dựng; thêm cờ máy `--contain` chặn ở QC |
| Ch.7 sequence diagram bóp còn ~193px/lane | Nhãn message đè lên lane kế bên | Nhãn đặt PHÍA TRÊN mũi tên, canh trái theo điểm đầu, không dùng bound label giữa mũi tên |
| Bound label mồ côi trôi ~75px mỗi lần frontend sync | Phần tử trôi ra ngoài khung, `--contain` FAIL | Không tạo bound label mới trên mũi tên; kiểm `--contain` sau mỗi chương |
| Tài liệu cao lên ~18.000–20.000px | PNG rất cao, xem nặng | Chấp nhận — đây là hệ quả trực tiếp của lựa chọn 1A/2A; ghi số đo thật vào report |
| Canvas mất trắng giữa chừng | Mất cả tài liệu | Backup `docs/diagrams/_backup-a4-2026-08-12.excalidraw` TRƯỚC khi động vào, khôi phục bằng `import --replace` |

Không cần model, không cần download, không cài thêm gói. Pillow đã có trong `.venv`.

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Đủ 13 chương, số liên tục | `check_canvas_layout.py <export> --chapters --expect 13` | exit 0 |
| Q2 | Mọi khung rộng đúng 1240px | `... --width 1240` | exit 0 |
| Q3 | Không cặp khung nào chồng lấn | `... --overlap` | exit 0 |
| Q4 | Mọi phần tử nằm trong khung của nó | `... --contain` | exit 0 |
| Q5 | Thứ tự y đúng số chương | `... --order` | exit 0 |
| Q6 | Mục lục khớp tiêu đề thật | `... --toc` | exit 0 |
| Q7 | Không text nào `fontSize` < 14 | `... --fontsize 14` | exit 0 |
| Q8 | 4 khối cũ không mất phần tử | `... --count-by-region` | Ch.2 = 55, Ch.5 = 63, Ch.9 = 19, Ch.10 = 15 |
| Q9 | Không chương nào tràn chữ | cắt PNG theo bbox từng `ch<N>-frame`, xem 14 ảnh | 14/14 không cắt chữ |
| Q10 | Hai cờ mới có test | `pytest tests/test_check_canvas_layout.py -q` | xanh, ≥ 4 ca mới (đúng/sai × 2 cờ) |
| Q11 | Hai file export tồn tại | `ls -la docs/diagrams/` | `.excalidraw` parse được, `.png` > 100 KB |
| Q12 | Full-suite không có test pass → fail | `.venv/bin/python -m pytest -q` | không test nào đỏ |

**DoD:** 12 hạng mục trên đều PASS · mọi task trong plan tick `[x]` · working log
`docs/workinglog/2026-08-12.md` có mục cho phase implement · report ≤ 50 dòng trong
`docs/tdq/reports/2026-08-12-layout-a4-doc.md`.

## 7. Câu hỏi còn mở

(Rỗng — 4 câu interview đã có đáp án `1A 2A 3A 4A`.)
