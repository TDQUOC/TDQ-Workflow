# Brief — 2026-08-12-layout-a4-doc

## Nguyên văn

> hiện tại nó đang không ổn lắm, tôi muốn design để có width như một tờ a4 dọc có thể
> đọc rõ, hiện tại chữ nếu theo view thì quá nhỏ

Kèm ảnh chụp màn hình canvas ở mức zoom vừa bề ngang: Ch.0 mục lục và Ch.1 hiện đủ,
nhưng chữ thân trong các thẻ nhỏ tới mức không đọc nổi.

### Cách hiểu đầu tiên

**Mục tiêu.** Đổi khổ tài liệu từ khung ngang 2640px hiện tại sang **bề ngang khổ A4
dọc**, để khi zoom vừa bề ngang trên màn hình thì chữ thân đọc rõ.

**Chẩn đoán vì sao chữ nhỏ.** Không phải `fontSize` sai — mà là **tỉ lệ**. Khung rộng
2640px, chữ thân `fontSize` 13–15. Khi người đọc zoom để vừa bề ngang 2640px vào một
cửa sổ ~1400px, mọi thứ co còn ~53%, chữ 13px hiển thị như ~7px. Thu bề ngang khung
xuống cỡ A4 dọc thì cùng `fontSize` đó sẽ hiển thị to gấp ~2 lần ở cùng thao tác zoom.

**Phạm vi đoán (chờ user xác nhận).**
- Đổi hằng số `W` trong `scripts/canvas_draw.py` từ 2640 xuống bề ngang A4, và
  `CHAPTER_X`/`CHAPTER_W` trong `canvas_move_block.py` theo.
- Vẽ lại 9 chương đã vẽ mới (Ch.0, 1, 3, 4, 6, 8, 11, 12, 13) theo 1 cột thay vì 2–3 cột.
- 5 khối cũ (Ch.2, 5, 7, 9, 10) phải xử lý riêng: chúng rộng 760–2640px, khối Ch.7
  (sequence diagram, 6 lane ngang) và Ch.4 (8 node state machine xếp ngang) **không thể**
  bóp vào bề ngang A4 mà vẫn đọc được.
- Toạ độ y của cả 14 khung phải tính lại từ đầu — khung hẹp thì cao hơn.

**Chỗ chưa rõ — phải hỏi.**
1. Bề ngang A4 quy ra bao nhiêu px trên canvas (A4 dọc 210mm: 794px @96dpi, 1240px @150dpi,
   1654px @200dpi)? Chọn số nào quyết định luôn cỡ chữ tương đối.
2. Mỗi chương = đúng một trang A4 (cao cố định 297mm, chương dài phải cắt trang) hay chỉ
   lấy **bề ngang** A4, còn chiều cao thả tự do theo nội dung?
3. Ba khối bản chất nằm ngang (Ch.4 state machine 8 node, Ch.7 sequence diagram 6 lane,
   Ch.2 lưới 2 cột) xử lý sao khi bề ngang co lại?
4. Có tăng `fontSize` không, hay giữ nguyên và chỉ dựa vào việc thu bề ngang?

## Hiểu & kiến thức

### Năng lực dùng được (B0)

| Năng lực | Phán quyết | Vì sao |
|---|---|---|
| `excalidraw-skill` (user) | **DÙNG** | Toàn bộ việc là dựng lại hình trên canvas 127.0.0.1:17739; skill giữ luật cỡ chữ (`k≈0.75` cho tiếng Việt, chữ ≤ 70% bề rộng ô) và luật chụp-kiểm |
| `mem0-memory` (user) | **DÙNG** | Chốt xong lưu 1 fact về khổ trang đã chọn, để lần sau vẽ đúng ngay |
| `scripts/canvas_draw.py` (nội bộ) | **DÙNG** | Đã đóng gói khuôn chương + hàm `fit()` cảnh báo tràn; chỉ cần đổi hằng số `W` và bố cục cột |
| `scripts/check_canvas_layout.py` (nội bộ) | **DÙNG** | 6 phép kiểm hình học đã có test; là bằng chứng QC cho khổ mới |
| `scripts/canvas_move_block.py` (nội bộ) | **DÙNG** | Luật xoá-tạo-lại (`update_element` silent-fail) vẫn áp dụng |
| `graphify` (user) | KHÔNG | Việc này không hỏi về kiến trúc code |
| Nhóm skill Unity / Adobe / Figma | KHÔNG | Sai lĩnh vực |

### Số liệu đo trên bản export hiện tại

Đo bằng bounding box thật, không ước lượng (`docs/diagrams/tdq-workflow-product-doc.excalidraw`):

| Ch | Bề rộng nội dung | Cỡ chữ đang dùng | Nhận xét |
|---|---|---|---|
| 0, 1, 3, 6, 8, 11, 12, 13 | 2540–2550 | 13–15 thân, 28 tiêu đề | Rộng vì TÔI xếp 2–3 cột; dồn 1 cột là hết rộng |
| 2 | **760** | 14–17 | Đã hẹp sẵn, gần vừa khổ A4 |
| 5 | **940** | 14–20 | Đã hẹp sẵn |
| 9 | **760** | 14–18 | Đã hẹp sẵn |
| 10 | **760** | 14–20 | Đã hẹp sẵn |
| 4 | 2550 | **11–13** | 8 node state machine xếp NGANG + bảng schema 3 cột — rộng do bản chất |
| 7 | **2640** | 12–13 | Sequence diagram 6 lane dọc × 19 message — rộng do bản chất |

Kết luận quan trọng: **4/5 khối cũ (Ch.2, 5, 9, 10) vốn đã hẹp 760–940px** — chúng không
phải vấn đề, chỉ cần dời lại. Chỗ thật sự phải thiết kế lại là 8 chương tôi xếp nhiều cột,
cộng **hai** khối rộng do bản chất là Ch.4 và Ch.7. Ch.2 tuy là lưới 2 cột nhưng chỉ rộng
760px nên vẫn vừa.

### Vì sao chữ nhỏ — tính bằng số

Không phải `fontSize` sai. Khi zoom vừa bề ngang khung 2640px vào cửa sổ ~1400px, tỉ lệ
hiển thị là 1400/2640 ≈ **0,53**; chữ thân 13px hiện ra như ~7px. Nếu khung rộng 1240px thì
tỉ lệ là 1400/1240 ≈ **1,13** — chữ 16px hiện ra như ~18px, đọc thoải mái. Vậy đòn bẩy chính
là **bề rộng khung**, cỡ chữ chỉ là điều chỉnh phụ.

### Khổ A4 dọc quy ra pixel (ISO 216: 210 × 297 mm)

| DPI | Bề ngang × cao | Ký tự/dòng ở cỡ chữ 16 (k=0,75) | Tổng chiều cao tài liệu ước tính |
|---|---|---|---|
| 96 | 794 × 1123 | ~66 — chuẩn sách | ~46.000px (rất dài) |
| **150** | **1240 × 1754** | ~103 | ~30.000px |
| 200 | 1654 × 2339 | ~138 — dài quá một dòng đọc | ~23.000px |

Hiện tại tổng cao 15.420px ở bề ngang 2640.

### Không cần research ngoài

Kích thước A4 là hằng số tiêu chuẩn ISO 216, không phải ẩn số cần tra; mọi dữ kiện còn lại
đo trực tiếp từ file export trong repo. Bỏ bước research theo đúng luật "việc thuần nội bộ".

### Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | **BỎ** | A4 là hằng số ISO 216; mọi số liệu còn lại đo từ file export trong repo |
| Interview | **CÓ — xong** | 4 câu, user trả lời `1A 2A 3A 4A` lúc 13:04 |
| Spec + plan (2 gate duyệt) | **CÓ** | Vẽ lại 11 chương, chốt sai khổ là làm lại toàn bộ |
| Chia subagent | **BỎ** | Mọi task ghi vào CÙNG một canvas sống; chạy song song sẽ giẫm chân nhau đúng như sự cố dời khối ở request trước |
| QC độc lập (agent) | **BỎ** | Bằng chứng QC là output máy của `check_canvas_layout.py` + ảnh cắt theo khung — đọc được trực tiếp, không cần agent thứ hai diễn giải |
| Report | **CÓ** | Khung bất biến |

## Hỏi đáp

### Vòng 1 — 13:02, user trả lời `1A 2A 3A 4A` lúc 13:04

**Câu 1 — Bề ngang A4 lấy bao nhiêu px?** → **A: 1240px (A4 @150dpi)**.
~103 ký tự/dòng ở cỡ chữ 16. Loại 794px (tài liệu cao ~46.000px, cuộn quá nhiều) và
1654px (~138 ký tự/dòng, dài quá một dòng đọc).

**Câu 2 — Chiều cao?** → **A: chỉ lấy bề ngang A4, chiều cao mỗi chương thả tự do.**
Không cắt trang, không ép bội số 1754px. Tài liệu là canvas cuộn dọc, không phải bản in.

**Câu 3 — Hai khối rộng do bản chất?** → **A: vẽ lại theo chiều dọc.**
Ch.4 state machine 8 node xếp dọc + bảng schema 21 field một cột; Ch.7 sequence diagram
giữ 6 lane nhưng bóp còn ~193px/lane trong bề ngang 1240. Không có chương ngoại lệ.

**Câu 4 — Cỡ chữ?** → **A: chuẩn hoá lên** — thân 16, chú thích tối thiểu 14
(hiện có chỗ 11–12), tiêu đề chương 30.

Không còn câu hỏi nào làm đổi kết quả.

### Kiểm cổng

- **Phạm vi cuối rõ chưa?** Rồi: 14 khung bề ngang 1240px; vẽ lại 11 chương (0, 1, 3, 4,
  6, 7, 8, 11, 12, 13 + mục lục), dời 4 khối cũ đã hẹp sẵn (2, 5, 9, 10); export lại 2 file.
- **Cần model / download / cài đặt gì không?** Không. Pillow đã cài vào `.venv` ở request
  trước để cắt ảnh; không thêm gói nào.
- **Phạm vi QC/test đã có chưa?** Rồi: 6 phép kiểm của `check_canvas_layout.py` (đã có 11
  unit test) + phép kiểm mới "mọi khung rộng đúng 1240" + "không text nào `fontSize` < 14"
  + xem 14 ảnh cắt theo khung.
