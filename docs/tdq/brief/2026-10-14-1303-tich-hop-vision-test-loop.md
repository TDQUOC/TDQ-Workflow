# Brief — Tích hợp khung mindset kiểm thử thực tế và vòng lặp Vision Test Loop vào TDQ Workflow

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> "okay vậy hãy mở request update vào tdq workflow đi"
> (Tiếp nối trực tiếp từ bản đặc tả kiến trúc đã duyệt `docs/tdq/spec/2026-10-14-1242-nghien-cuu-vision-test-loop.md`).
> Bổ sung từ người dùng: "1a 2a 3c 4 ko áp cứng là phải figma mà mở rộng ra là những cái liên quan đến vision mà có smokup hoặc figma hoặc prototype thì cần tuân theo mà check kĩ để hạn chế người dùng phải feed back nhiều lần và sửa nhiều round"

### First reading

- **Mục tiêu chính**:
  Triển khai thực tế bản đặc tả kiến trúc đã được nghiệm thu (`docs/tdq/spec/2026-10-14-1242-nghien-cuu-vision-test-loop.md`) vào mã nguồn CLI và hệ thống quy chuẩn của TDQ Workflow:
  1. **Tầng CLI (`scripts/tdq_vision_diff.py`)**:
     - Xây dựng công cụ xử lý & đối chiếu thị giác tự động bằng `Pillow` (`PIL`):
       + Hỗ trợ linh hoạt nhiều nguồn tham chiếu (`--source` nhận file ảnh cục bộ từ mockup, wireframe, prototype screenshot, hoặc `--figma-url` tự động tải qua Figma REST API khi có `FIGMA_TOKEN`).
       + Chuẩn hóa kích thước 2 ảnh (`source`, `dist`) bằng **Canvas Padding / Letterboxing** (tuyệt đối không co giãn làm méo tỷ lệ).
       + Hỗ trợ **Masking / Ignore Regions** (`--ignore-boxes`) để che các vùng động (đồng hồ, quảng cáo, video) trước khi tính độ lệch.
       + Tính toán ma trận sai khác pixel với ngưỡng dung sai khử răng cưa (`--color-tolerance`), gom cụm các vùng sai lệch liên thông (Connected Components / Grid Clustering) và vẽ **Bounding Box màu đỏ đánh số thứ tự `[1]`, `[2]`...** lên ảnh `diff_highlight.png`.
       + Xuất dữ liệu đo lường có cấu trúc `metrics.json` (`mismatch_rate`, `passed`, danh sách tọa độ `[x, y, w, h]` và tỷ lệ lệch từng vùng).
       + Tự động sinh bộ đôi báo cáo **Markdown Report (`<slug>.md`)** và **Interactive HTML Report (`<slug>.html`)** từ template tĩnh dựng sẵn trong script (tích hợp Before/After Split Slider, Overlay Onion-Skin & Blink 2Hz, Interactive Bounding Box Explorer click-to-zoom, và Multi-round Timeline). Mặc định dùng đường dẫn tương đối tới ảnh và hỗ trợ cờ `--embed-base64` để xuất 1 file HTML độc lập.
       + Tích hợp dịch vụ log chuẩn TDQ (`[<ISO-timestamp>] tdq_vision_diff: ...` ra `stderr`, tắt bằng `TDQ_LOG=0`).
  2. **Tầng Luật & Quy chuẩn (`skills/`)**:
     - Tích hợp **User-Scenario-Driven Testing** (kịch bản `Given - When - Then` 3 tầng) và **6 Test Anti-Patterns cấm kỵ (`ANTI-1`..`ANTI-6`)** vào `skills/tdq-build/references/rules/chung.md` và `skills/tdq-spec/references/spec-template.md`.
     - Mở rộng phạm vi kích hoạt **Vision Test Loop 6 bước** cho **mọi task liên quan đến thị giác (vision) có tài liệu tham chiếu (mockup, wireframe, screenshot mẫu, HTML/web prototype, hoặc Figma)** vào `skills/tdq-build/references/rules/html.md` và gắn cổng kiểm tra vào `skills/tdq-build/references/qc.md` nhằm kiểm tra kỹ lưỡng ngay từ đầu, hạn chế tối đa việc người dùng phải feedback nhiều lần và sửa nhiều round.
  3. **Tầng Kiểm thử & Hợp đồng Tài liệu (`tests/`, `token-budget.json`)**:
     - Viết trọn bộ unit test (`tests/test_tdq_vision_diff.py`) kiểm chứng từng hàm và kịch bản thực tế của `scripts/tdq_vision_diff.py`.
     - Cập nhật chỉ mục dòng (`doc_index.py`), khóa ngân sách token (`token_budget.py`), đảm bảo `doc_lint.py` và `i18n_check.py` đạt 0 vi phạm.

## Hiểu & kiến thức

### Năng lực dùng được

Phân vân → DÙNG. Kiểm kê ngày 2026-10-14: 24 skill trên đĩa, cộng skill built-in trong context. Không xoá bảng này kể cả khi không có dòng DÙNG nào.

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

### Khảo sát mã nguồn & Kiến trúc hiện trạng

1. **Ràng buộc kiến trúc (`docs/kien-truc.md`)**:
   - File code thực thi mới bắt buộc đặt tại `scripts/` (`scripts/tdq_vision_diff.py`).
   - Toàn bộ docstring, comment và thông báo in ra từ `scripts/` phải viết bằng tiếng Anh để vượt qua `scripts/i18n_check.py` (chỉ các chuỗi template tiếng Việt có chủ đích mới gắn `# i18n-allow`).
   - Toàn bộ văn bản quy tắc trong `skills/` phải viết bằng tiếng Anh (trừ các cụm từ khóa hoặc khối mẫu giao tiếp người dùng có `<!-- i18n-allow: ... -->`).
2. **Phân tích Ngân sách Token (`docs/tdq/token-budget.json`, trần `TRAN_TOKEN = 3500`)**:
   - `skills/tdq-build/references/qc.md`: Hiện có `3329` tokens (còn dư `171` tokens). Do đó, ở `qc.md` chỉ đặt quy tắc điều phối ngắn gọn (~70-90 tokens) và trỏ sang file luật chi tiết.
   - `skills/tdq-build/references/rules/chung.md`: Hiện có `2973` tokens (còn dư `527` tokens). Đây là file được nạp bắt buộc ở mọi ngôn ngữ khi implement — rất phù hợp để đặt mục `## User-scenario-driven testing and banned anti-patterns` (~280 tokens).
   - `skills/tdq-build/references/rules/html.md`: Hiện có `599` tokens (còn dư `2901` tokens). Đây là file luật của nhóm giao diện HTML/CSS/UI — vị trí lý tưởng để đặt trọn vẹn quy trình 6 bước **Vision Test Loop** (áp dụng cho mọi task vision có mockup, prototype, screenshot tham chiếu hoặc Figma), hướng dẫn CLI `scripts/tdq_vision_diff.py`, Reviewer Sub-agent (trần 1 lượt feedback) và Human-in-the-loop (~1000 tokens), vừa tuân thủ luật Build-less-than-asked (Bậc 2: tận dụng file sẵn có thay vì đẻ file mới) vừa không làm tăng giới hạn dòng của `skills/tdq-build/SKILL.md` (`174/174` dòng).
   - `skills/tdq-spec/references/spec-template.md`: Hiện có `2009` tokens (còn dư `1491` tokens). Bổ sung hướng dẫn thiết lập DoD 3 tầng kịch bản người dùng và ngưỡng `mismatch_rate` cho task UI/UX.
3. **Thư viện xử lý ảnh sẵn có**:
   - Python 3 với `Pillow 12.3.0` (`PIL.Image`, `PIL.ImageChops`, `PIL.ImageDraw`, `PIL.ImageStat`) đã cài đặt sẵn trên máy, chạy độc lập không cần cài thêm dependency mới (khớp Bậc 5 của luật Build-less-than-asked).

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| `analyze` | CÓ | Đã hoàn thành khảo sát ngân sách token, vị trí tích hợp trong `scripts/` và `skills/`, hoàn tất phỏng vấn |
| `spec` | CÓ | Lập bản đặc tả kỹ thuật chi tiết các module chạm, giao diện CLI `tdq_vision_diff.py` và DoD có đo trước (R14) |
| `plan` | CÓ | Chia nhỏ các task TDD (đỏ → xanh) cho CLI `tdq_vision_diff.py` và cập nhật các file luật trong `skills/` |
| `implement` | CÓ | Viết unit test và code `scripts/tdq_vision_diff.py`, cập nhật `skills/`, chạy `doc_index.py` và `token_budget.py` |
| `qc` | CÓ | Chạy bộ kiểm thử mức `ultra` (DoD, trọn suite unit test, hồi quy vùng chạm, smoke test, runtime test và Reviewer Sub-agent độc lập) |
| `report` | CÓ | Tổng kết kết quả, hỏi người dùng về commit và gộp nhánh |

## Hỏi đáp

### Vòng 1 — Chốt chi tiết tính năng CLI & Mức QC (2026-10-14 13:15)

1. Trong công cụ `scripts/tdq_vision_diff.py`, ngoài việc nhận 2 file ảnh cục bộ (`--source` và `--dist`), bạn có muốn tích hợp luôn tùy chọn `--figma-url` để tự động tải ảnh thiết kế chuẩn qua Figma REST API (khi có `FIGMA_TOKEN`) không?
- A (đề xuất): Có, tích hợp cả hai — hỗ trợ truyền file ảnh cục bộ VÀ hỗ trợ `--figma-url` (dùng `urllib.request` chuẩn của Python gọi Figma API khi có `FIGMA_TOKEN`; nếu thiếu token hoặc lỗi quyền truy cập thì báo mã dừng để người dùng cấp).
- B: Không cần trong script — `tdq_vision_diff.py` chỉ nhận đường dẫn 2 file ảnh đã có trên đĩa (`--source` và `--dist`), việc tải ảnh thực hiện bên ngoài.
*Đã chọn: 1a.*

2. Đối với file báo cáo tương tác `docs/tdq/visual-reports/<slug>.html`, bạn muốn cơ chế nhúng hình ảnh (`source`, `dist`, `diff_highlight`) hoạt động như thế nào?
- A (đề xuất): Mặc định nhúng đường dẫn tương đối tới các file ảnh trong thư mục báo cáo (giữ file HTML nhẹ, load nhanh), đồng thời hỗ trợ cờ `--embed-base64` để đóng gói tất cả ảnh vào 1 file HTML độc lập (self-contained) khi cần chia sẻ rời.
- B: Luôn nhúng thẳng Base64 toàn bộ hình ảnh vào trong 1 file `.html` duy nhất ở mọi lần chạy.
- C: Chỉ dùng đường dẫn tương đối tới file ảnh trên đĩa, không cần tùy chọn Base64.
*Đã chọn: 2a.*

3. Request này bạn muốn QC tới mức nào?
- A (đề xuất): `full` — DoD + trọn unit test + hồi quy vùng chạm + ràng buộc kiến trúc + clean code. Không chạy runtime test.
- B: `lite` — DoD + unit test của riêng vùng chạm. Nhanh nhất, đổi lại không ai chạy trọn suite.
- C: `ultra` — như `full`, thêm smoke test, runtime test và một agent QC độc lập soi lại.
*Đã chọn: 3c (`ultra`).*

4. Bạn muốn bổ sung thêm gì không?
- A (đề xuất): Không, đủ rồi — làm tiếp đi.
- B: Có — tôi nói thêm.
*Nguyên văn câu trả lời của người dùng:* `"1a 2a 3c 4 ko áp cứng là phải figma mà mở rộng ra là những cái liên quan đến vision mà có smokup hoặc figma hoặc prototype thì cần tuân theo mà check kĩ để hạn chế người dùng phải feed back nhiều lần và sửa nhiều round"`
*Chốt bổ sung:* Không áp cứng là chỉ Figma; mọi task liên quan đến thị giác (vision) có tài liệu tham chiếu (mockup, wireframe, screenshot mẫu, prototype HTML/web, hoặc Figma) đều bắt buộc kích hoạt quy trình **Vision Test Loop** để tự đối chiếu `source` vs `dist`, khoanh vùng highlight, tự sửa và hậu kiểm kỹ lưỡng nhằm giảm thiểu số lần người dùng phải feedback và sửa qua nhiều round.
