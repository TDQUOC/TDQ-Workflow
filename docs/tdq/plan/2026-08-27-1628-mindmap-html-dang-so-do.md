# PLAN — mind-map HTML trình bày dạng sơ đồ luồng

Ngày: 2026-08-27 · Spec: ../spec/2026-08-27-1628-mindmap-html-dang-so-do.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — mọi task đều sửa cùng một file `scripts/mindmap_render.py`, không cắt được đợt song song nào; đo bằng `tdq_bench.py mo-phong` (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH (2026-08-27, mode `main` — user chọn "inline")

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Tầng dựng mô hình luồng
- P2 — Tầng bố cục
- P3 — Tầng sinh SVG lớp nghiệp vụ
- P4 — Trang tổng
- P5 — Log & test bắt buộc
- Cụm song song
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test của bộ render, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. Ngôn ngữ: docstring và chú thích trong `scripts/` viết tiếng Anh; mọi hằng chuỗi user thấy
   khai kèm cụm `i18n-allow` — theo dòng đã chốt 2026-08-22 của `docs/kien-truc.md`.

## P1 — Tầng dựng mô hình luồng

- [x] **T1.1** (e14m) Viết `build_flow_model(steps)`: từ danh sách `Step` phẳng dựng ra danh sách node và danh sách cạnh — gom `B<n>` với `B<n>!` cùng số thành một cặp, node cha mang vai `quyet-dinh`, node `B<n>!` mang vai `nhanh-loi`, bước đầu mang vai `vao`, bước cuối luồng chính và mỗi node nhánh lỗi mang vai `ra`; cạnh xuống nhãn `ok` chỉ khi rời một node quyết định, cạnh rẽ ngang nhãn `lỗi`. Trả dữ liệu thuần, không sinh một ký tự HTML/SVG nào — Test: `python3 -m pytest tests/test_mindmap_render.py -q -k flow_model`
  - Chạm: `scripts/mindmap_render.py`, `tests/test_mindmap_render.py` → nơi gọi (LSP `find_references` + lumen chạy song song): `_render_business_layer` chỉ được gọi ở `mindmap_render.render_feature_page`; `parse_diagram` được gọi ở `render_feature_page` và `collect_total_data`; ngoài module chỉ có `scripts/tdq_mindmap.py::cmd_xem` import vào, không hook nào dùng. Bản sao portable (`portable_codex/`, `portable_claude/`, `antigravity_portable/`) do `scripts/build_portable.py` sinh lại, không sửa tay.
  - Dùng: `tdq-lsp-setup`
  - Để: tìm mọi nơi gọi `_render_business_layer` và `parse_diagram` bằng LSP + lumen song song trước khi sửa, nạp skill TRƯỚC bước đỏ. Agent ngoài không có skill system: đọc `skills/tdq-lsp-setup/SKILL.md` rồi làm theo.
  - Ra: danh sách nơi gọi ghi vào dòng `Chạm:` của chính task này
  - Kiểm: `python3 scripts/tdq_lsp.py kiem` exit 0
  - Không dùng cho: cài thêm plugin hay sửa file của plugin khác
- [x] **T1.2** (e8m) Ca biên của tầng mô hình: sơ đồ 1 bước (không cạnh nào), sơ đồ mọi bước đều có nhánh lỗi, nhiều nhánh lỗi cùng một số `B<n>` — cả 3 ca ra mô hình hợp lệ, không ngoại lệ — Test: `python3 -m pytest tests/test_mindmap_render.py -q -k flow_model_bien`
  - Chạm: `scripts/mindmap_render.py`, `tests/test_mindmap_render.py` → `build_flow_model`
  - Cần: T1.1

**Xong P1 khi**: `build_flow_model` trả mô hình đúng cho cả 5 file sơ đồ thật và 3 ca biên, và kết quả của nó không chứa chuỗi `<`.

## P2 — Tầng bố cục

- [x] **T2.1** (e10m) Viết `wrap_label(text, max_chars)`: ngắt mô tả thành danh sách dòng theo ranh giới từ, số ký tự mỗi dòng suy từ `BOX_W` và `font-size`, không cắt cụt chữ nào, từ dài hơn một dòng vẫn được giữ nguyên trên dòng riêng — Test: `python3 -m pytest tests/test_mindmap_render.py -q -k wrap_label`
  - Chạm: `scripts/mindmap_render.py`, `tests/test_mindmap_render.py` → file mới về mặt hàm, chưa node nào phụ thuộc
- [x] **T2.2** (e16m) Viết `layout_flow(model)`: mỗi node có `x`, `y`, `w`, `h`, `lines`; chiều cao suy từ số dòng của `wrap_label`; luồng chính xếp một cột dọc, node nhánh lỗi đặt sang cột phải ngang hàng node quyết định của nó; trả thêm bề rộng và chiều cao tổng cho `viewBox` — Test: `python3 -m pytest tests/test_mindmap_render.py -q -k layout_flow`
  - Chạm: `scripts/mindmap_render.py`, `tests/test_mindmap_render.py` → `build_flow_model`
  - Cần: T1.1, T2.1
- [x] **T2.3** (e8m) Khoá điều kiện không chồng lấn: với cả 5 file sơ đồ thật và 3 ca biên, không cặp node nào có hình chữ nhật bao giao nhau, và mô tả dài cho ra node cao hơn mô tả ngắn — Test: `python3 -m pytest tests/test_mindmap_render.py -q -k layout_khong_chong_lan`
  - Chạm: `scripts/mindmap_render.py`, `tests/test_mindmap_render.py` → `layout_flow`
  - Cần: T2.2

**Xong P2 khi**: mọi node của mọi sơ đồ thật có toạ độ và kích thước, không cặp nào chồng lấn.

## P3 — Tầng sinh SVG lớp nghiệp vụ

- [x] **T3.1** (e12m) Viết bộ helper hình dạng dùng chung: `_svg_hop` (chữ nhật bo góc), `_svg_hinh_thoi` (polygon), `_svg_vien_thuoc` (bo góc lớn), `_svg_nhan_nhieu_dong` (mỗi dòng một `<tspan>`), `_svg_mui_ten` (`<marker>` + `<line>` + nhãn). Chỉ dùng `currentColor` và biến `--*`, không mã màu cứng — Test: `python3 -m pytest tests/test_mindmap_render.py -q -k svg_helper`
  - Chạm: `scripts/mindmap_render.py`, `tests/test_mindmap_render.py` → `render_svg`, `_render_dependency_svg`
- [x] **T3.2** (e14m) Viết `render_flow_svg(model, layout)`: ráp helper thành một `<figure>` có `viewBox` đúng kích thước, `role="img"` + `aria-label`, `<figcaption>` nêu đúng một điều khẳng định; bước thường ra `<rect`, bước có nhánh lỗi ra `<polygon`, điểm vào và điểm ra ra viên thuốc; mọi ký tự của mô tả đều có mặt — Test: `python3 -m pytest tests/test_mindmap_render.py -q -k render_flow_svg`
  - Chạm: `scripts/mindmap_render.py`, `tests/test_mindmap_render.py` → `_render_business_layer`
  - Cần: T2.2, T3.1
  - Dùng: `artifact-diagramming`
  - Để: giữ đúng cơ chế SVG chuẩn cho hình mới — `viewBox` có kích thước, `currentColor`, `<marker>` mũi tên, `role="img"` + `aria-label`, một hình một điều khẳng định; nạp skill TRƯỚC bước đỏ. Agent ngoài không có skill system: đọc mô tả skill trong context rồi làm theo.
  - Ra: `render_flow_svg` trong `scripts/mindmap_render.py` sinh `<figure>` đủ 5 yếu tố trên
  - Kiểm: `python3 -m pytest tests/test_mindmap_render.py -q -k render_flow_svg` xanh
  - Không dùng cho: đổi lớp chi tiết (`render_svg`) hay bảng màu chung của trang
- [x] **T3.3** (e10m) Ghép vào `_render_business_layer`: sơ đồ đứng TRƯỚC `<ol class="steps">` trong cùng `<section id="lop-nghiep-vu">`, danh sách bước và khối phụ thuộc giữ nguyên từng chữ; thêm khối cuộn ngang `overflow-x: auto` + `max-width: 100%` vào `STYLE` — Test: `python3 -m pytest tests/test_mindmap_render.py -q -k business_layer`
  - Chạm: `scripts/mindmap_render.py`, `tests/test_mindmap_render.py` → `render_feature_page`
  - Cần: T3.2
- [x] **T3.4** (e6m) Khoá hồi quy lớp chi tiết: `render_svg` và các test lớp chi tiết đang có vẫn xanh, không sửa một kỳ vọng nào của chúng — Test: `python3 -m pytest tests/test_mindmap_render.py tests/test_mindmap_nhan_doc.py -q`
  - Chạm: `scripts/mindmap_render.py` → `render_svg`
  - Cần: T3.1

**Xong P3 khi**: trang feature có đủ sơ đồ + danh sách, đúng thứ tự, và test lớp chi tiết cũ không đổi một dòng kỳ vọng.

## P4 — Trang tổng

- [x] **T4.1** (e10m) Viết `build_branch_model(features)`: dựng cây nhánh tổng → nhánh con → feature thành node/cạnh, feature chưa có file đánh cờ `thieu-file`. Trả dữ liệu thuần — Test: `python3 -m pytest tests/test_mindmap_render.py -q -k branch_model`
  - Chạm: `scripts/mindmap_render.py`, `tests/test_mindmap_render.py` → `_render_branch_tree`
- [x] **T4.2** (e14m) Vẽ cây nhánh thành SVG bằng helper của T3.1: mỗi ô feature bọc trong `<a href>` tới trang riêng, ô `thieu-file` vẽ nét đứt và mờ, không gắn link; danh sách link cũ giữ nguyên và đặt XUỐNG DƯỚI sơ đồ — Test: `python3 -m pytest tests/test_mindmap_render.py -q -k cay_nhanh_svg`
  - Chạm: `scripts/mindmap_render.py`, `tests/test_mindmap_render.py` → `render_total_page`
  - Cần: T3.1, T4.1
- [x] **T4.3** (e8m) Chuyển `_render_dependency_svg` sang dùng chung helper của T3.1 và bỏ cắt cụt `label[:34]`, kết quả vẫn đủ mọi ô và mọi cạnh; danh sách cạnh phụ thuộc giữ nguyên — Test: `python3 -m pytest tests/test_mindmap_render.py -q -k luoi_phu_thuoc`
  - Chạm: `scripts/mindmap_render.py`, `tests/test_mindmap_render.py` → `render_total_page`
  - Cần: T3.1

**Xong P4 khi**: `index.html` có sơ đồ cây nhánh, lưới phụ thuộc theo phong cách mới, và danh sách link cũ vẫn còn trong trang.

## P5 — Log & test bắt buộc

- [x] **T5.1** (e6m) Log service: mỗi lần dựng sơ đồ in một dòng stderr có timestamp nêu số node và số cạnh đã vẽ, tắt bằng `TDQ_LOG=0` — Test: `python3 -m pytest tests/test_mindmap_render.py -q -k log_service`
  - Chạm: `scripts/mindmap_render.py`, `tests/test_mindmap_render.py` → `render_feature_page`, `render_total_page`
  - Cần: T3.3, T4.2
- [x] **T5.2** (e10m) Render lại cả 5 file sơ đồ thật trong `docs/tdq/mind-map/` và trang tổng: exit 0, mọi bước và mọi cạnh phụ thuộc còn trong trang, không thẻ nào trỏ ra ngoài (`<script src`, `<link href`) — Test: `python3 -m pytest tests/test_mindmap_render.py -q -k so_do_that`
  - Chạm: `tests/test_mindmap_render.py` → không sửa file nguồn nào
  - Cần: T5.1
- [x] **T5.3** (e6m) Kiểm ngôn ngữ đúng tầng và không placeholder: mọi hằng `TEXT_*` mới có cụm `i18n-allow`, docstring viết tiếng Anh, không còn `TODO`/`FIXME` — Test: `python3 scripts/i18n_check.py && grep -rn "TODO\|FIXME" scripts/mindmap_render.py`
  - Chạm: `scripts/mindmap_render.py` → `STYLE`, các hằng `TEXT_*`
  - Cần: T5.1

## Cụm song song

**Một cụm duy nhất.** Toàn bộ 12 task đều chạm `scripts/mindmap_render.py`; hai task chạy song
song ở hai worktree sẽ sửa cùng file và chỉ vỡ lúc merge, git không cảnh báo trước. Đường cắt
theo file duy nhất có thể tách được là `tests/test_mindmap_render.py`, nhưng test phải viết TRƯỚC
code trong cùng task (luật đỏ→xanh), nên tách ra không tạo thêm chỗ chạy song song nào.
Trần tốc độ của mode đội ở plan này = 1 → không có lợi thế.

## Khối hợp đồng skill khung

Ba skill khung của lane full không gắn vào một task lẻ nào vì chúng điều khiển cả phase; hợp
đồng của chúng ghi ở đây cho đủ, đúng luật R8.

- Dùng: `tdq-build`
- Để: chạy phase implement → qc → report end-to-end trong một lượt, giữ luật đỏ→xanh và tick ngay
- Ra: `docs/tdq/qc/2026-08-27-1628-mindmap-html-dang-so-do.md` và `docs/tdq/reports/2026-08-27-1628-mindmap-html-dang-so-do.md`
- Kiểm: mọi ô tick của mục Definition of Done ở dưới đều `[x]` và có bằng chứng trong file qc
- Không dùng cho: sửa spec đã duyệt, hay tự commit khi không có chặn kỹ thuật

- Dùng: `tdq-diagram`
- Để: vẽ và lấy duyệt 2 sơ đồ feature trước khi viết plan này (đã chạy xong ở phase diagram)
- Ra: `docs/tdq/mind-map/mind-map-trang-feature.md`, `docs/tdq/mind-map/mind-map-trang-tong.md`
- Kiểm: `python3 scripts/tdq_mindmap.py kiem docs/tdq/mind-map/mind-map-trang-feature.md` exit 0 và `python3 scripts/tdq_mindmap.py lien-he` exit 0
- Không dùng cho: sửa sơ đồ đã duyệt mà không hỏi lại user

- Dùng: `tdq-plan`
- Để: viết chính file plan này từ spec đã duyệt, đo mode thực thi bằng `tdq_bench.py`
- Ra: `docs/tdq/plan/2026-08-27-1628-mindmap-html-dang-so-do.md`
- Kiểm: `python3 scripts/doc_lint.py --pair docs/tdq/spec/2026-08-27-1628-mindmap-html-dang-so-do.md docs/tdq/plan/2026-08-27-1628-mindmap-html-dang-so-do.md` exit 0
- Không dùng cho: đổi phạm vi ngoài spec §1

## Definition of Done

Trỏ về §6 của spec (12 hạng mục Q1–Q12):

- [x] Q1 Tầng mô hình trả dữ liệu thuần, cặp `B<n>`/`B<n>!` ra 1 node quyết định + 1 node nhánh lỗi + 1 cạnh nhãn `lỗi` — `python3 -m pytest tests/test_mindmap_render.py -q -k flow_model`
- [x] Q2 Hộp cao theo chữ, không mất chữ, không chồng lấn — `python3 -m pytest tests/test_mindmap_render.py -q -k "wrap_label or layout"`
- [x] Q3 Đúng hình dạng theo vai và nhãn cạnh `ok`/`lỗi` — `python3 -m pytest tests/test_mindmap_render.py -q -k render_flow_svg`
- [x] Q4 Trang feature đủ 2 khối, sơ đồ đứng trước danh sách — `python3 -m pytest tests/test_mindmap_render.py -q -k business_layer`
- [x] Q5 Lớp chi tiết không đổi hành vi — `python3 -m pytest tests/test_mindmap_render.py tests/test_mindmap_nhan_doc.py -q`
- [x] Q6 Trang tổng: cây nhánh có SVG mỗi feature một link, lưới phụ thuộc phong cách mới, danh sách link cũ còn — `python3 -m pytest tests/test_mindmap_render.py -q -k "cay_nhanh_svg or luoi_phu_thuoc"`
- [x] Q7 Không phụ thuộc ngoài, không thẻ trỏ ra ngoài — `python3 -m pytest tests/test_mindmap_render.py -q -k so_do_that`
- [x] Q8 Không mã màu cứng trong sơ đồ mới — `python3 -m pytest tests/test_mindmap_render.py -q -k svg_helper`
- [x] Q9 Cả 5 file sơ đồ thật render lại được, không mất bước — `python3 -m pytest tests/test_mindmap_render.py -q -k so_do_that`
- [x] Q10 Ca biên (1 bước, mọi bước có nhánh lỗi, mô tả 20 từ) không vỡ — `python3 -m pytest tests/test_mindmap_render.py -q -k "flow_model_bien or layout_khong_chong_lan"`
- [x] Q11 Log service có timestamp, `TDQ_LOG=0` thì im — `python3 -m pytest tests/test_mindmap_render.py -q -k log_service`
- [x] Q12 Ngôn ngữ đúng tầng, không placeholder — `python3 scripts/i18n_check.py`
- [x] Bộ test toàn repo không có lỗi MỚI so với trước request — `python3 -m pytest tests/ -q`
