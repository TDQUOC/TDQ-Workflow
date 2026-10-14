# SPEC — Tích hợp khung mindset kiểm thử thực tế và vòng lặp Vision Test Loop vào TDQ Workflow

Ngày: 2026-10-14 · Bản: 1.1 · Brief: ../brief/2026-10-14-1303-tich-hop-vision-test-loop.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: ĐÃ DUYỆT

## Mục lục

- 1. Mục tiêu & phạm vi
- 1b. Lộ trình
- 2. Đầu ra cụ thể
- 2b. Ranh giới module
- 3. Cách tiếp cận & lý do
- 3b. Năng lực & công cụ
- 4. Yêu cầu bắt buộc
- 5. Ràng buộc & rủi ro
- 6. QC & Definition of Done
- 7. Câu hỏi còn mở

## 1. Mục tiêu & phạm vi

- **Mục tiêu**: Hiện thực hóa bản đặc tả kiến trúc `2026-10-14-1242-nghien-cuu-vision-test-loop` vào mã nguồn CLI (`scripts/tdq_vision_diff.py`) và hệ thống tài liệu quy chuẩn (`skills/`) của TDQ Workflow, bao gồm việc **xây dựng một file Skill Rule Reference chi tiết (`skills/tdq-build/references/vision-test-loop.md`)** theo định dạng từng bước cơ học (step-by-step runbook, bảng quyết định rõ ràng, ví dụ RIGHT/WRONG, lệnh copy-pasteable) để **ngay cả các model tier thấp** cũng dễ dàng tuân theo 100%, chấm dứt lối kiểm thử máy móc hình thức và bắt buộc thực thi **Vision Test Loop** đối với mọi task liên quan đến thị giác có tài liệu tham chiếu (mockup, wireframe, screenshot mẫu, prototype HTML/web, hoặc Figma) nhằm hạn chế tối đa việc người dùng phải feedback nhiều lần và sửa đi sửa lại qua nhiều round.
- **Trong phạm vi**:
  1. Xây dựng công cụ dòng lệnh `scripts/tdq_vision_diff.py` sử dụng `Pillow` (`PIL`):
     - Hỗ trợ nhận ảnh chuẩn từ đường dẫn cục bộ (`--source` từ mockup, prototype screenshot, wireframe...) VÀ tùy chọn `--figma-url` tự động tải ảnh qua Figma REST API (dùng `urllib.request` với biến môi trường `FIGMA_TOKEN`; trả mã lỗi `3` rõ ràng để kích hoạt `pause --loai dau-vao-user` khi thiếu token/quyền truy cập).
     - Chuẩn hóa kích thước 2 ảnh (`source`, `dist`) bằng **Canvas Padding / Letterboxing** (tuyệt đối không co giãn làm méo tỷ lệ chữ và bố cục).
     - Hỗ trợ **Masking / Ignore Regions** (`--ignore-boxes` dạng `x,y,w,h;...`) để che vùng động (đồng hồ, quảng cáo, video) trước khi tính độ lệch.
     - Tính toán sai lệch màu sắc pixel với ngưỡng dung sai khử răng cưa (`--color-tolerance`), gom cụm vùng lệch thành các **Bounding Box màu đỏ đánh số thứ tự `[1]`, `[2]`...** vẽ trực tiếp lên ảnh `diff_highlight.png`.
     - Xuất file `metrics.json` chứa `mismatch_rate`, `threshold`, `passed`, kích thước canvas và danh sách tọa độ từng Bounding Box.
     - Tự động sinh bộ đôi báo cáo **Markdown Report (`<slug>.md`)** và **Interactive HTML Report (`<slug>.html`)** từ template tĩnh dựng sẵn trong script (gồm Before/After Split Slider, Overlay Onion-Skin & Blink 2Hz, Interactive Bounding Box Explorer click-to-zoom, và Multi-round Timeline). Mặc định nhúng đường dẫn ảnh tương đối, đồng thời hỗ trợ cờ `--embed-base64` để xuất 1 file HTML độc lập.
  2. Xây dựng file **Skill Rule Reference chi tiết cho cả model tier thấp** tại `skills/tdq-build/references/vision-test-loop.md` (liên kết tầng 1 trực tiếp từ `skills/tdq-build/SKILL.md` và `skills/tdq-spec/SKILL.md`):
     - Bảng quyết định kích hoạt (Trigger Decision Table) rõ ràng, không mơ hồ cho mọi loại nguồn thị giác (mockup, wireframe, screenshot mẫu, prototype HTML/web, Figma).
     - Hướng dẫn **User-Scenario-Driven Testing** 3 tầng (`Given - When - Then`) và bảng **6 Test Anti-Patterns cấm kỵ (`ANTI-1`..`ANTI-6`)** kèm ví dụ code **WRONG vs RIGHT** trực quan.
     - Quy trình **6 bước Vision Test Loop** viết dưới dạng lệnh copy-pasteable tuần tự (1 → 6), quy tắc quy chiếu từng hộp Bounding Box `[1]`, `[2]` sang thuộc tính CSS/HTML, trần 3 vòng auto-fix + dừng sớm, quy trình gọi Reviewer Sub-agent độc lập (trần 1 lượt feedback), kịch bản Human-in-the-loop và Checklist tự kiểm (`Self-check`) trước khi báo PASS.
  3. Cập nhật móc nối ngắn gọn trong `skills/tdq-build/SKILL.md`, `skills/tdq-spec/SKILL.md`, `skills/tdq-build/references/qc.md`, `skills/tdq-build/references/rules/chung.md` và `skills/tdq-build/references/rules/html.md` để mọi model khi vào `spec`, `implement` hoặc `qc` đều được dẫn thẳng tới `vision-test-loop.md`.
  4. Xây dựng bộ unit test đầy đủ cho `scripts/tdq_vision_diff.py`, đồng bộ chỉ mục dòng (`doc_index.py`) và khóa ngân sách token (`token_budget.py`).
- **NGOÀI phạm vi**:
  - Không cài đặt thêm thư viện bên thứ ba nặng nề (OpenCV, PyTorch) vì `Pillow` và `urllib.request` có sẵn đã đáp ứng trọn vẹn.
  - Không sửa đổi cơ chế hook chặn của Claude Code (`hooks/scripts/`), giữ đúng triết lý cổng kiểm tra nằm ở tầng CLI và quy trình QC.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| `analyze` | CÓ | Đã hoàn thành khảo sát ngân sách token, vị trí tích hợp trong `scripts/` và `skills/`, hoàn tất phỏng vấn |
| `spec` | CÓ | Lập bản đặc tả kỹ thuật chi tiết các module chạm, giao diện CLI `tdq_vision_diff.py`, file rule reference chi tiết cho model tier thấp và DoD có đo trước (R14) |
| `plan` | CÓ | Chia nhỏ các task TDD (đỏ → xanh) cho CLI `tdq_vision_diff.py` và xây dựng/cập nhật các file luật trong `skills/` |
| `implement` | CÓ | Viết unit test và code `scripts/tdq_vision_diff.py`, tạo `vision-test-loop.md` và cập nhật `skills/`, chạy `doc_index.py` và `token_budget.py` |
| `qc` | CÓ | Chạy bộ kiểm thử mức `ultra` (DoD, trọn suite unit test, hồi quy vùng chạm, smoke test, runtime test và Reviewer Sub-agent độc lập) |
| `report` | CÓ | Tổng kết kết quả, hỏi người dùng về commit và gộp nhánh |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Công cụ CLI đối chiếu thị giác & sinh báo cáo kép `.md` + `.html` | `scripts/tdq_vision_diff.py` | Hỗ trợ `--source` / `--figma-url`, `--dist`, `--out-dir`, `--threshold`, `--color-tolerance`, `--ignore-boxes`, `--embed-base64`, `--round`; thực hiện Canvas Padding, Masking, vẽ Bounding Box đỏ đánh số `[1]`, `[2]`, xuất `diff_highlight.png`, `metrics.json`, `<slug>.md` và `<slug>.html` |
| 2 | Bộ kiểm thử đơn vị (Unit Tests) cho công cụ đối chiếu thị giác | Thư mục `tests/` (module kiểm thử của `tdq_vision_diff`) | Kiểm chứng đầy đủ các hàm: Canvas Padding không méo tỷ lệ, Masking vùng động, phát hiện & gom cụm Bounding Box, xuất `metrics.json`, render `.md` & `.html` (cả đường dẫn tương đối và `--embed-base64`), xử lý `--figma-url` khi thiếu/có `FIGMA_TOKEN`, và tắt log bằng `TDQ_LOG=0` |
| 3 | File Skill Rule Reference chi tiết cho cả model tier thấp | `skills/tdq-build/references/vision-test-loop.md` | Có chỉ mục dòng (`muc-luc-dong`), bảng quyết định kích hoạt (mockup/wireframe/screenshot/prototype/Figma), kịch bản 3 tầng (`Given - When - Then`), bảng 6 Anti-Patterns kèm ví dụ WRONG/RIGHT, 6 bước Vision Test Loop copy-pasteable, Reviewer Sub-agent (trần 1 lượt feedback), Human-in-the-loop và Checklist tự kiểm; đạt chuẩn `doc_lint.py` (R1–R7, R13 ≤ 3500 tokens) và `i18n_check.py` |
| 4 | Liên kết điều phối tầng 1 & Quy chuẩn QC trong hệ thống `skills/` | `skills/tdq-build/SKILL.md`, `skills/tdq-spec/SKILL.md`, `skills/tdq-build/references/qc.md`, `skills/tdq-build/references/rules/chung.md`, `skills/tdq-build/references/rules/html.md`, `docs/tdq/token-budget.json` | Trỏ tầng 1 trực tiếp tới `references/vision-test-loop.md`; giữ mọi file trong `rules/` dưới trần dòng (150 dòng cho `html.md`, 252 dòng cho `chung.md`) và toàn bộ `references/` dưới trần 3500 tokens |

## 2b. Ranh giới module

Xác định bằng ngữ nghĩa phụ thuộc qua LSP (`scripts/` chỉ phụ thuộc `utf8_io` và thư viện chuẩn + `PIL`; `skills/` là văn bản quy tắc độc lập được khóa bởi `docs/tdq/token-budget.json`):

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| `vision-cli` | `scripts/tdq_vision_diff.py`, thư mục `tests/` (bộ test của `tdq_vision_diff`) | Không (chỉ dùng `utf8_io`, `PIL` và stdlib) | 1, 2 |
| `vision-rule-ref` | `skills/tdq-build/references/vision-test-loop.md` | `vision-cli` (nhắc lệnh CLI `tdq_vision_diff.py`) | 3 |
| `skill-wiring` | `skills/tdq-build/SKILL.md`, `skills/tdq-spec/SKILL.md`, `skills/tdq-build/references/qc.md`, `skills/tdq-build/references/rules/chung.md`, `skills/tdq-build/references/rules/html.md`, `docs/tdq/token-budget.json` | `vision-rule-ref` | 4 |

## 3. Cách tiếp cận & lý do

- **Chọn**:
  1. **Xây dựng `scripts/tdq_vision_diff.py` gọn nhẹ, mô-đun hóa theo SOLID**:
     - Tách riêng từng hàm đơn trách nhiệm (SRP) với độ phức tạp nhận thức thấp (cyclomatic ≤ 10, cognitive ≤ 15):
       + `fetch_figma_source(figma_url, out_path, token)`: Phân tích `file_key` và `node_id` từ URL Figma, gọi Figma REST API qua `urllib.request` để lấy URL ảnh PNG render chuẩn và tải về `out_path`. Nếu thiếu `FIGMA_TOKEN` hoặc lỗi HTTP/mạng, ghi log và trả mã thoát `3` (`NEED_USER_INPUT`) kèm hướng dẫn gọi `tdq_state.py pause --loai dau-vao-user`.
       + `normalize_canvas(src_img, dist_img)`: Tạo canvas kích thước `(max(w1, w2), max(h1, h2))` và dán 2 ảnh tại gốc `(0, 0)` (Canvas Padding / Letterboxing), trả về 2 ảnh cùng kích thước mà không làm co giãn bất kỳ pixel gốc nào.
       + `apply_ignore_mask(diff_mask, ignore_boxes)`: Xóa các vùng chữ nhật `(x, y, w, h)` nằm trong danh sách loại trừ khỏi mặt nạ sai lệch trước khi tính tỷ lệ lệch và gom cụm.
       + `find_bounding_boxes(diff_mask, grid_size, min_area)`: Chia lưới ô vuông (mặc định `16x16` px) và dùng thuật toán duyệt thành phần liên thông (BFS trên lưới ô có pixel lệch) để gom các ô liền kề thành danh sách các Bounding Box `[x, y, w, h]`, lọc nhiễu nhỏ hơn `min_area`.
       + `render_highlight_image(dist_img, diff_mask, boxes)`: Phủ lớp tint đỏ bán trong suốt lên pixel lệch, vẽ khung viền đỏ đậm `2px` và nhãn đánh số `[1]`, `[2]`... tại góc mỗi Bounding Box.
       + `write_reports(out_dir, slug, metrics, src_path, dist_path, diff_path, embed_base64)`: Tự động sinh báo cáo Markdown `<slug>.md` và báo cáo tương tác `<slug>.html` từ template tĩnh dựng sẵn trong script (hỗ trợ cả đường dẫn tương đối mặc định và nhúng Base64 khi truyền `--embed-base64`).
  2. **Tạo file Skill Rule Reference chuyên biệt `skills/tdq-build/references/vision-test-loop.md` cho cả model tier thấp**:
     - Thiết kế theo chuẩn `doc_lint.py` (câu ngắn ≤ 40 từ, đánh số bước liên tục `1.`..`6.`, không dùng từ mơ hồ, lệnh bọc trong代码块 copy-pasteable, có khối chỉ mục dòng `<!-- muc-luc-dong: ... -->` ở đầu file).
     - Đặt tại tầng 1 `skills/tdq-build/references/vision-test-loop.md` (được trỏ thẳng từ `skills/tdq-build/SKILL.md` và `skills/tdq-spec/SKILL.md`), vừa tuân thủ quy tắc 1-tầng của bộ test cấu trúc reference, vừa không chạm vào giới hạn 10 file cố định của thư mục con `references/rules/`.
- **Vì**:
  - Model tier thấp rất dễ bỏ sót hoặc suy diễn sai nếu quy tắc viết chung chung hoặc rải rác nhiều nơi. Một file reference chuyên biệt có bảng quyết định rõ ràng (Decision Table), ví dụ `WRONG vs RIGHT` và 6 bước lệnh copy-pasteable giúp model tier thấp thực thi chính xác từng bước như một máy trạng thái, đảm bảo chất lượng cuối cùng đồng nhất.
- **Đã loại**:
  - *Phương án tạo file thứ 11 bên trong thư mục con `skills/tdq-build/references/rules/`* — loại vì bộ test thư viện rule khóa cứng thư mục `rules/` chỉ chứa đúng 10 file ngôn ngữ và giới hạn mỗi file < 150 dòng; đặt tại `skills/tdq-build/references/vision-test-loop.md` cho phép viết đầy đủ runbook chi tiết (lên tới 500 dòng / 3500 tokens) mà hoàn toàn hợp chuẩn kiến trúc.

## 3b. Năng lực & công cụ

Chép từ brief mục `### Năng lực dùng được`. Phân vân → DÙNG.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | tiếp nhận và phân tích yêu cầu |
| tdq-spec | plugin:tdq-workflow | NỀN | viết đặc tả kỹ thuật cho request triển khai |
| tdq-plan | plugin:tdq-workflow | NỀN | lập kế hoạch triển khai chi tiết |
| tdq-build | plugin:tdq-workflow | NỀN | thực thi TDD đỏ -> xanh, chạy QC và lập báo cáo |
| tdq-conventions | plugin:tdq-workflow | NỀN | quy tắc workflow, ngôn ngữ 3 tầng và hợp đồng tài liệu |
| tdq-status | plugin:tdq-workflow | NỀN | kiểm tra trạng thái |
| tdq-lean | plugin:tdq-workflow | NỀN | kiểm soát độ gọn và bậc thang build-less-than-asked |
| tdq-setup | plugin:tdq-workflow | NỀN | kiểm tra môi trường công cụ và LSP |
| tdq-check-status | plugin:tdq-workflow | NỀN | phục hồi phiên khi cần |
| Đã xét 15 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- **Log service bật mặc định**: `scripts/tdq_vision_diff.py` xuất log có ISO timestamp (`[YYYY-MM-DDTHH:MM:SS] tdq_vision_diff: <message>`) ra `stderr`, đủ chi tiết để debug kích thước ảnh, số lượng Bounding Box, `mismatch_rate` và đường dẫn báo cáo; tắt được qua biến môi trường `TDQ_LOG=0`.
- **Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật**: Mọi thuật toán xử lý ảnh (Canvas Padding, Masking, Connected-Grid Bounding Box, Base64/Relative HTML rendering) đều chạy thật 100% trên ảnh `PIL.Image`.
- **Mỗi thành phần có unit test riêng, chạy được bằng một lệnh**: Tuân thủ quy trình TDD đỏ → xanh nghiêm ngặt.
- **Code viết ra bám 5 nguyên tắc SOLID** theo `skills/tdq-conventions/references/clean-code.md`, và bám rule ngôn ngữ trong `skills/tdq-build/references/rules/` (cyclomatic ≤ 10, cognitive ≤ 15).

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md` — chỉ những dòng việc này chạm tới):
- File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/` — việc này chạm ở `scripts/tdq_vision_diff.py`.
- `skills/` chỉ được **nhắc tên lệnh** của `scripts/`, cấm chép nội dung script vào skill — việc này chạm ở `skills/tdq-build/references/vision-test-loop.md`, `skills/tdq-build/references/rules/html.md` và `skills/tdq-build/references/qc.md`.
- 2026-08-22: ngôn ngữ chia 3 tầng — luật trong `skills/`, `agents/`, chú thích/docstring của `hooks/` + `scripts/` và chuỗi máy in ra đều viết TIẾNG ANH cố định (không bảng tra i18n); tài liệu sinh cho user và lời thoại viết theo `doc_lang` — việc này chạm ở `scripts/tdq_vision_diff.py` và các file trong `skills/`.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| File reference mới `skills/tdq-build/references/vision-test-loop.md` không được trỏ tầng 1 từ `SKILL.md` | Bộ test cấu trúc reference một tầng báo lỗi đỏ | Thêm liên kết trực tiếp `[references/vision-test-loop.md](references/vision-test-loop.md)` trong `skills/tdq-build/SKILL.md` và `skills/tdq-spec/SKILL.md` |
| Thêm quy tắc làm vượt trần `3500` tokens (R13) hoặc vượt trần dòng của `SKILL.md` / `rules/*.md` | `doc_lint.py`, `token_budget.py --kiem` hoặc bộ test thư viện rule báo lỗi đỏ | Đặt toàn bộ nội dung hướng dẫn chi tiết cho model tier thấp vào `skills/tdq-build/references/vision-test-loop.md` (ngân sách riêng 3500 tokens / 500 dòng), chỉ thêm con trỏ ngắn ở `SKILL.md`, `qc.md`, `chung.md`, `html.md` |
| Câu văn tiếng Anh trong `skills/` dài quá 40 từ vi phạm R5 của `doc_lint.py` | `doc_lint.py` báo lỗi `[R5] sentence of N words (> 40)` | Chia câu ngắn gọn ≤ 35 từ, dùng dấu `·` hoặc `;` hoặc bảng Markdown để model tier thấp đọc dễ nhất |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS | Đo trước | Dự phòng nếu trượt |
|---|---|---|---|---|
| Q1 | Công cụ CLI `scripts/tdq_vision_diff.py` xử lý chuẩn xác ảnh đối chiếu | Chạy `tdq_vision_diff.py` trên cặp ảnh test có vùng lệch và vùng ignore: thực hiện đúng Canvas Padding (không méo ảnh), loại trừ đúng `ignore_boxes`, phát hiện & vẽ Bounding Box đỏ đánh số `[1]`, `[2]` lên `diff_highlight.png`, xuất `metrics.json` chính xác | Pillow 12.3.0 đã cài sẵn, thời gian xử lý ảnh 1440x900 đo thử ~0.18 giây | Tối ưu bước gom cụm trên lưới ô `16x16` px để giữ tốc độ xử lý nhanh và ổn định |
| Q2 | Xuất bộ đôi báo cáo Markdown (`.md`) & Interactive HTML (`.html`) kèm hỗ trợ `--embed-base64` và `--figma-url` | Sinh đủ `<slug>.md` và `<slug>.html` (chứa Slider Before/After, Onion-skin & Blink, Bounding Box Explorer, Timeline); hỗ trợ cả đường dẫn tương đối và `--embed-base64`; xử lý `--figma-url` trả mã lỗi 3 chuẩn khi thiếu `FIGMA_TOKEN` | Template HTML tĩnh < 15 KB, 0 phụ thuộc mạng ngoài | Rút gọn CSS/JS nội tuyến trong hằng số template của `tdq_vision_diff.py` |
| Q3 | Bộ Unit Test của `tdq_vision_diff` và Log Service | Toàn bộ unit test mới cho `tdq_vision_diff` đều PASS; kiểm tra log xuất ISO timestamp ra `stderr` khi mặc định và im lặng hoàn toàn khi `TDQ_LOG=0` | Hiện có 0 lỗi trên bộ test nền của repo | Bổ sung test case phủ kín từng nhánh hàm và sửa ngay nếu có assertion trượt |
| Q4 | File Skill Rule Reference chi tiết `skills/tdq-build/references/vision-test-loop.md` & Liên kết trong `skills/` | File `vision-test-loop.md` có đủ bảng quyết định kích hoạt (mockup/wireframe/screenshot/prototype/Figma), kịch bản 3 tầng (`Given - When - Then`), 6 Anti-Patterns (kèm ví dụ WRONG/RIGHT), 6 bước lệnh copy-pasteable cho model tier thấp, Reviewer Sub-agent trần 1 lượt feedback, Human-in-the-loop và Checklist tự kiểm; được trỏ tầng 1 từ `SKILL.md` và liên kết tại `qc.md`, `chung.md`, `html.md` | Ngân sách file mới tối đa 3500 tokens và 500 dòng; dự kiến ~1600 tokens (~220 dòng) | Chạy `doc_index.py` và `token_budget.py` để khóa chỉ mục dòng và số đo token chuẩn xác |
| Q5 | Hợp đồng Tài liệu, Ngôn ngữ, Cấu trúc 1-tầng & Khóa Ngân sách Token | Chạy `doc_index.py --tat-ca`, `token_budget.py`, `doc_lint.py skills` và `i18n_check.py scripts/ skills/` đều kết thúc với `exit 0` (0 vi phạm, mọi file reference ≤ 3500 tokens) | Hiện tại `doc_lint.py skills` và `i18n_check.py` đều 0 vi phạm, trần 3500 tokens/file | Chia nhỏ câu > 40 từ hoặc thêm chú thích `i18n-allow` hợp lệ cho từ khóa tiếng Việt bắt buộc |
| Q6 | Thẩm định QC mức `ultra` (Smoke test, Runtime test & Independent QC Agent) | Chạy thực tế `tdq_vision_diff.py` tạo bộ báo cáo mẫu end-to-end, chạy trọn bộ suite kiểm thử của repo và kiểm tra bằng agent `tdq-qc-tester` độc lập xác nhận mọi tiêu chí đều PASS | Môi trường Python 3 + sub-agent `tdq-qc-tester` sẵn sàng 100% | Khắc phục ngay mọi điểm phản biện từ `tdq-qc-tester` trong vòng lặp QC (tối đa 3 vòng) |

**DoD**:
1. Công cụ `scripts/tdq_vision_diff.py` hoạt động hoàn chỉnh, đạt chuẩn SOLID & độ phức tạp hàm (cyclomatic ≤ 10, cognitive ≤ 15), có đầy đủ unit test xanh 100%.
2. File Skill Rule Reference chi tiết `skills/tdq-build/references/vision-test-loop.md` được viết rõ ràng, từng bước cơ học để cả model tier thấp cũng dễ dàng tuân theo, kèm liên kết đầy đủ từ `skills/tdq-build/SKILL.md`, `skills/tdq-spec/SKILL.md`, `qc.md`, `chung.md`, `html.md`.
3. Toàn bộ công cụ kiểm định hợp đồng của repo (`doc_index.py --kiem`, `token_budget.py --kiem`, `doc_lint.py`, `i18n_check.py`), bộ test cấu trúc skill và agent QC độc lập mức `ultra` đều PASS 100%.

## 7. Câu hỏi còn mở

(Rỗng — toàn bộ câu hỏi đã được chốt.)
