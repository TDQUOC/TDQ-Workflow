# Brief — mind-map HTML trình bày dạng sơ đồ
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> commit đi và bắt đầu mở request xử lí tôi muôn mind-map html khi xem sẽ trình bày theo dạng
> diagarm để dễ quan sát và nắm

Kèm 1 ảnh tham chiếu: flowchart kiểu "Lamp doesn't work" — hộp bo góc màu, hộp quyết định hình
thoi, mũi tên nối dọc, nhánh Yes/No rẽ ngang sang hộp kết quả.

### Cách hiểu đầu tiên

- **Mục tiêu:** trang `docs/tdq/mind-map/<feature>.html` khi mở lên phải hiện thành **sơ đồ
  luồng có hộp và mũi tên**, thay vì danh sách bước `<ol>` như hiện tại — để nhìn phát nắm ngay
  luồng chạy và chỗ rẽ nhánh lỗi.
- **Phạm vi đoán:** `scripts/mindmap_render.py` (918 dòng) — cụ thể là `_render_business_layer`
  đang sinh `<ol class="steps">`. Lớp chi tiết (`render_svg`, `_layout`) ĐÃ vẽ SVG dạng cây rồi,
  nên hạ tầng vẽ SVG có sẵn để tái dùng. Có thể chạm cả trang tổng `index.html`
  (`_render_dependency_svg` — đã là sơ đồ, nhưng cần soi lại cho đồng bộ phong cách).
- **Dữ liệu đầu vào không đổi:** vẫn là file `.md` một-bước-một-dòng (`B<n> · mô tả (file::hàm)`,
  `B<n>!` là nhánh lỗi). Sơ đồ phải suy ra được hình dạng từ đúng cú pháp đó, không bắt người
  dùng viết thêm.

### Chỗ chưa rõ (chờ interview)

1. Bước thường vẽ hộp chữ nhật, còn bước có nhánh lỗi `B<n>!` vẽ hình thoi quyết định — đúng
   như ảnh — hay giữ tất cả là hộp và chỉ tô màu khác?
2. Vẽ bằng SVG tự sinh (như `render_svg` sẵn có, không phụ thuộc gì thêm) hay bằng Mermaid?
3. Sơ đồ thay hẳn danh sách bước, hay đặt sơ đồ lên trên và giữ danh sách bên dưới?
4. Lớp chi tiết (call tree) có đổi theo luôn không, hay chỉ đổi lớp nghiệp vụ?
5. Trang tổng `index.html` có nằm trong phạm vi lần này không?

## Hiểu & kiến thức

### Năng lực dùng được

| Skill/công cụ | Nguồn | Phán quyết | Vì sao |
|---|---|---|---|
| `tdq-conventions` | plugin:tdq-workflow | DÙNG | luật gốc mọi phase |
| `tdq-spec` / `tdq-plan` / `tdq-diagram` / `tdq-build` | plugin:tdq-workflow | DÙNG | lane full đi đủ cửa |
| `tdq-lsp-setup` | plugin:tdq-workflow | DÙNG | luật tìm ký hiệu LSP+lumen trước grep |
| `tdq-check-status` / `tdq-status` | plugin:tdq-workflow | BỎ | phiên đang chạy liên tục, không cần khôi phục |
| `tdq-intake` | plugin:tdq-workflow | ĐANG DÙNG | phase hiện tại |
| built-in `artifact-diagramming` | context | DÙNG (tham chiếu) | `render_svg` hiện tại đã theo cơ chế của nó (viewBox có kích thước, `currentColor`, `<marker>`, `role="img"`) — bản vẽ mới phải giữ đúng cơ chế đó |
| Excalidraw / Figma MCP | plugin | BỎ | sinh ảnh rời, trong khi trang cần SVG sinh tự động lúc build, không có bước tay |

### Đọc code — hiện trạng

- `scripts/mindmap_render.py` (918 dòng) là nơi duy nhất sinh HTML. Trang feature có **2 lớp**,
  đổi qua lại bằng 1 nút:
  - **lớp nghiệp vụ** `_render_business_layer` (dòng 432) → `<ol class="steps">`, mỗi bước 1 `<li>`
    viền trái, bước lỗi đổi màu viền. Đây là chỗ phải đổi.
  - **lớp chi tiết** `_render_detail_layer` (dòng 459) → mỗi bước 1 figure SVG cây lời gọi, vẽ bằng
    `render_svg` (337) + `_layout` (314) + `_leaf_count` (331). SVG dạng hộp + mũi tên có `<marker>`,
    dùng `currentColor` nên tự hợp 2 theme.
- Trang tổng `render_total_page` (786) đã có `_render_dependency_svg` (677) — lưới phụ thuộc giữa
  các feature, cũng hộp + mũi tên. Phong cách hộp/mũi tên trong repo vì thế đã có 2 bản mẫu.
- Cấu trúc dữ liệu: `parse_diagram` (119) trả `steps` là danh sách phẳng `Step(num, is_error, desc,
  file, func, location_raw)`. **`B<n>!` không được gắn cha con** với `B<n>` — nó chỉ là một phần tử
  nữa trong cùng danh sách, phân biệt bằng cờ `is_error` và trùng `num`. Muốn vẽ nhánh rẽ ngang như
  ảnh flowchart thì phải gom `B<n>` với `B<n>!` cùng số lại thành một cặp ở tầng dựng sơ đồ.
- CSS `STYLE` (479) đã có sẵn bộ biến màu 3 trạng thái theme (`:root`, `prefers-color-scheme`,
  `[data-theme]`) và `--err` cho nhánh lỗi → sơ đồ mới dùng lại bộ biến này, không thêm palette.
- Không có phụ thuộc ngoài: trang là file HTML tĩnh mở bằng `file://`, CSS/JS đều nội tuyến.
  Nạp Mermaid từ CDN sẽ phá tính chất này (mở offline là hỏng), nên hướng SVG tự sinh là mặc định.
- Test hiện có: `tests/test_mindmap_render.py` khoá hành vi lớp nghiệp vụ + lớp chi tiết.

### Research

Vòng research: BỎ — việc thuần nội bộ, không có ẩn số ngoài: bộ vẽ SVG, cú pháp `.md`, CSS và
test đều nằm trong repo; cơ chế vẽ SVG chuẩn đã có bản mẫu ngay trong cùng file.

### Phạm vi đã chốt

- Mặt CHỌN: dễ đọc/trực quan · chạy offline không phụ thuộc ngoài · dễ mở rộng về sau
- Mặt LOẠI: hiệu năng render · bảo mật · đa nền tảng ngoài trình duyệt (in ấn/PDF, màn hình cảm ứng)
- Bối cảnh: xem bằng trình duyệt trên máy VÀ preview trong VS Code · file HTML tĩnh mở `file://` ·
  sơ đồ hiện có 5 file feature, mỗi file 6–10 bước · một người giữ (chính chủ repo)
- Mức đầu tư suy ra: vừa — vì công cụ nội bộ một người giữ, nhưng user chọn 3 mặt chất lượng và
  kéo cả trang tổng vào phạm vi → DoD phải có test biên (bước lỗi, mô tả dài, sơ đồ 1 bước)

### Chốt kiến thức

**Quyết định đã chốt**

1. **Vẽ bằng SVG tự sinh trong Python**, KHÔNG Mermaid, KHÔNG thư viện ngoài. Lý do: trang mở
   bằng `file://` và preview trong VS Code — cả hai đều không đảm bảo tải được script từ CDN;
   repo cũng đã có 2 bản mẫu SVG hộp+mũi tên trong chính file này để tái dùng cơ chế.
2. **Ai là hình thoi:** bước `B<n>` **có** nhánh lỗi đi kèm trở thành **hình thoi quyết định**;
   dòng `B<n>!` là **hộp kết quả rẽ ngang sang phải** của hình thoi đó (đúng vai "Plug in lamp"
   trong ảnh). Bước không có nhánh lỗi giữ hộp chữ nhật. Đây là cách đọc duy nhất khớp với ảnh
   tham chiếu, vì hình thoi trong flowchart luôn là chỗ RẼ, không phải chỗ kết quả.
3. **Hộp tự cao theo chữ:** ngắt dòng mô tả theo số ký tự suy từ `BOX_W` và `font-size`, mỗi dòng
   một `<tspan>`; chiều cao hộp = số dòng × chiều cao dòng + đệm. Không cắt chữ, bỏ hẳn kiểu
   `label[:26]` ở lớp nghiệp vụ.
4. **Bố cục trang feature:** sơ đồ ở trên, `<ol class="steps">` hiện tại giữ nguyên ngay bên dưới.
   Sơ đồ để nắm luồng, danh sách để đọc mô tả đầy đủ và `file::hàm`.
5. **Nhãn cạnh:** cạnh đi xuống từ hình thoi ghi `ok`, cạnh rẽ ngang ghi `lỗi`. Cạnh giữa 2 bước
   thường không có nhãn (đỡ rối).
6. **Bước đầu và các bước kết thúc** (bước cuối luồng chính + mỗi hộp nhánh lỗi) vẽ dạng viên
   thuốc (bo góc lớn) như ảnh, để mắt bắt được đâu là điểm vào và điểm ra.
7. **Trang tổng:** *Lưới phụ thuộc* dùng chung bộ hộp/mũi tên/màu mới; *Cây nhánh* đổi từ danh
   sách lồng nhau thành sơ đồ cây SVG (nhánh tổng → nhánh con → feature), mỗi ô feature là một
   link; danh sách link cũ lùi xuống dưới sơ đồ, không xoá.
8. **Kiến trúc 3 tầng thuần** (mặt "dễ mở rộng" user chọn): dựng mô hình node/edge từ `steps` →
   tính bố cục (toạ độ, kích thước) → sinh chuỗi SVG. Ba hàm rời nhau, tầng dựng mô hình và tầng
   bố cục không sinh một ký tự HTML nào, nên thêm hình dạng mới về sau chỉ chạm tầng sinh SVG.
9. **Lớp chi tiết (`render_svg`) giữ nguyên logic**, chỉ dùng chung helper hình dạng/màu nếu việc
   đó không đổi kết quả hiện tại của nó.

**Phương án đã loại**

- Mermaid nạp từ CDN — phá tính chất offline (mặt B user chọn).
- Nhúng sẵn thư viện Mermaid vào file — file HTML phình vài trăm KB cho mỗi sơ đồ, và vẫn là
  phụ thuộc ngoài phải nâng cấp bằng tay.
- Đổi cú pháp file `.md` để khai nhánh rõ hơn — user không phải viết thêm gì là ràng buộc đã có
  từ đầu; 5 file sơ đồ đang tồn tại phải render được y nguyên.

**Nguồn:** đọc trực tiếp `scripts/mindmap_render.py`, `tests/test_mindmap_render.py`,
`skills/tdq-diagram/SKILL.md`, `docs/kien-truc.md`; ảnh flowchart user gửi.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| analyze | CÓ | đang chạy — 2 vòng hỏi, đã đóng |
| research thêm | BỎ | việc thuần nội bộ, không ẩn số ngoài |
| spec | CÓ | khung bất biến |
| diagram | CÓ | bắt buộc ở lane full — 2 luồng feature: dựng trang feature, dựng trang tổng |
| plan | CÓ | khung bất biến |
| chọn mode chạy | CÓ | đo bằng `tdq_bench.py mo-phong` trên chính plan |
| implement | CÓ | khung bất biến |
| qc | CÓ | tự QC theo `tdq-build`; mức đầu tư vừa → có test biên |
| QC độc lập bằng agent | BỎ | DoD kiểm được hết bằng lệnh test tự động, không cần mắt thứ hai |
| review sâu `tdq-reviewer` | BỎ | phạm vi gọn trong 1 file code + 1 file test |
| report | CÓ | khung bất biến |

## Hỏi đáp

### Vòng 1 — scope + hình dạng (2026-08-27 20:04)

| # | Hỏi | Đáp |
|---|---|---|
| 1 | Bao quanh mặt nào? | A+B+C — dễ đọc, offline không phụ thuộc, dễ mở rộng. Bỏ "chỉ cần chạy được" |
| 2 | Xem ở đâu? | A+B — trình duyệt trên máy VÀ preview trong VS Code |
| 3 | Bước lỗi vẽ hình gì? | A — `B<n>!` là **hình thoi quyết định**, rẽ ngang, đúng ảnh flowchart |
| 4 | Sơ đồ đặt đâu? | A — sơ đồ ở TRÊN, danh sách bước giữ nguyên bên dưới |
| 5 | Lớp chi tiết có đổi? | A — không đổi, chỉ chỉnh cho đồng bộ màu/kiểu nếu lệch |
| 6 | Trang tổng `index.html`? | B — CÓ, làm luôn cho đồng bộ |

### Vòng 2 — mức đồng bộ & chữ dài (2026-08-27 20:32)

| # | Hỏi | Đáp |
|---|---|---|
| 7 | Trang tổng đồng bộ tới mức nào? | B — đồng bộ phong cách VÀ vẽ *Cây nhánh* thành sơ đồ cây hộp + mũi tên; danh sách link lùi xuống dưới |
| 8 | Mô tả bước dài xử lý sao? | B — hộp TỰ CAO theo chữ, không cắt chữ nào; sơ đồ dài hơn cũng chấp nhận |

Không còn câu hỏi nào đổi được kết quả → đóng vòng hỏi.
