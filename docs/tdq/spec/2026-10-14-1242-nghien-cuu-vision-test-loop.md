# SPEC — Nghiên cứu mở rộng mindset test và vòng lặp so sánh vision UI/UX Figma cho TDQ Workflow

Ngày: 2026-10-14 · Bản: 1.0 · Brief: ../brief/2026-10-14-1242-nghien-cuu-vision-test-loop.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

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

- **Mục tiêu**:
  Xây dựng bản Đề xuất Giải pháp Kiến trúc (Architectural Proposal Spec) hoàn chỉnh và khả thi nhằm giải quyết triệt để 2 vấn đề lớn trong quy trình phát triển của AI với TDQ Workflow:
  1. **Mở rộng Mindset kiểm thử của AI**: Xóa bỏ tư duy kiểm thử máy móc, hình thức, hời hợt; thiết lập khung chuẩn kiểm thử theo kịch bản người dùng thực tế (User-Scenario-Driven Testing) với dữ liệu phong phú, ca biên sắc bén và loại bỏ các test anti-patterns (over-mocking, assert tautology).
  2. **Kiến trúc Vòng lặp Kiểm thử Thị giác (Vision Test Loop)**: Xây dựng cơ chế khép kín cho các task liên quan đến UI/UX, Figma, Web frontend:
     - Tự động thu thập nguồn thiết kế chuẩn (`image source`) và ảnh chụp render thực tế (`image dist`).
     - Cơ chế so sánh Hybrid: Thuật toán Pixel Diff tính toán ma trận sai khác, tự động khoanh vùng Bounding Box highlight vùng lệch trực quan kết hợp Multimodal Vision AI (Claude Vision) phân tích ngữ nghĩa UI (font, spacing, padding, color, layout).
     - Vòng lặp tự động sửa lỗi (Self-Correction Loop) với trần an toàn nghiêm ngặt (tối đa 3 vòng lặp, cơ chế dừng sớm khi không hội tụ, dừng báo người dùng khi quá tải).
     - File báo cáo thị giác trực quan song song cả 2 định dạng: **Markdown Report (`.md`)** cho AI/hệ thống và **Interactive HTML Report (`.html`)** tương tác cao cho con người kiểm chứng trực tiếp trên trình duyệt.
     - Vòng hậu kiểm độc lập (Reviewer Sub-agent) kiểm tra chéo trước khi đóng task.
     - Cơ chế Human-in-the-loop: Chủ động yêu cầu người dùng hỗ trợ khi thiếu tài nguyên ngoài tầm với.

- **Trong phạm vi**:
  1. Đặc tả khung chuyển đổi Mindset kiểm thử: Bộ quy chuẩn 3 tầng kịch bản kiểm thử (Happy path thực tế, Boundary/Edge cases, Visual/UX verification) và danh mục Test Anti-Patterns cấm kỵ.
  2. Đặc tả kiến trúc kỹ thuật Vision Test Loop: Luồng dữ liệu (Data flow), các thành phần module (Source capture, Dist capture, Hybrid Diff Engine, Bounding Box Highlight Generator, Feedback Loop Controller).
  3. Đặc tả công cụ và công nghệ tích hợp: MCP Browser (`cloudcli-browser` / Playwright), thư viện xử lý ảnh (Pillow / OpenCV), và Multimodal Vision Evaluation prompt chuẩn.
  4. Đặc tả cấu trúc Visual Report và quy trình Reviewer Sub-agent độc lập.
  5. Đặc tả cơ chế Human-in-the-loop và xử lý ngoại lệ (vượt trần 3 vòng lặp, thiếu asset, server lỗi).
  6. Đề xuất kế hoạch tích hợp từng bước vào TDQ Workflow (kế hoạch phase sau, quy ước contract trong spec/plan/qc).

- **NGOÀI phạm vi**:
  - Viết mã nguồn triển khai thực tế (code implementation) trong turn này (theo chỉ đạo chính xác của người dùng: "hãy mở request nghiên cứu và phân tích và cho lại tôi đề xuất chưa implement ở turn này").
  - Chỉnh sửa trực tiếp mã nguồn CLI lõi (`scripts/tdq_state.py`) hay các hook hiện hành trong turn này.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| `analyze` | CÓ | Đã hoàn thành: khảo sát năng lực, nghiên cứu đa góc độ, phỏng vấn chốt kiến thức |
| `spec` | CÓ | Đang chạy: lập bản đề xuất kiến trúc toàn diện và khả thi |
| `plan` | BỎ | Turn nghiên cứu & đề xuất kiến trúc, chưa implement code |
| `implement` | BỎ | Theo chỉ đạo của người dùng: chưa triển khai code ở turn này |
| `qc` | CÓ | Kiểm định tài liệu đề xuất, đo đạc tính khả thi toolchain, doc_lint, mức QC ultra có sub-agent QC độc lập soi phản biện |
| `report` | CÓ | Tổng kết báo cáo kết quả nghiên cứu và chuyển giao kế hoạch hành động tiếp theo |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| Đ1 | Tài liệu Khung Quy chuẩn Mindset Kiểm thử Thực tế cho AI | §3.1 trong spec này | Định nghĩa đầy đủ nguyên tắc User-Scenario-Driven Testing, cấu trúc 3 tầng kịch bản và danh mục 6 Test Anti-Patterns bị cấm |
| Đ2 | Tài liệu Đặc tả Kiến trúc Chi tiết Vision Test Loop | §3.2 trong spec này | Mô tả trọn vẹn luồng dữ liệu 6 bước: Source Capture → Dist Capture → Hybrid Diff & Bounding Box → Vision Semantic Analysis → Auto-fix Loop (cap 3) → Báo người dùng nếu quá tải |
| Đ3 | Đặc tả Định dạng Kép Visual Report (MD & Interactive HTML) và Quy trình Sub-agent | §3.3 trong spec này | Cấu trúc file markdown `docs/tdq/visual-reports/<slug>.md` và bản đặc tả HTML Report tương tác (Slider so sánh, Bounding Box Inspector) kèm quy trình Reviewer sub-agent hậu kiểm độc lập |
| Đ4 | Đặc tả Cơ chế Human-in-the-loop và Kế hoạch Tích hợp Workflow | §3.4 trong spec này | Kịch bản dừng hỏi người dùng khi thiếu tài nguyên (ảnh/font/Figma token) và roadmap phân kỳ triển khai vào các phase của TDQ Workflow |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| Khung Mindset Kiểm thử | §3.1 của spec | Không phụ thuộc | Đ1 |
| Kiến trúc Vision Test Loop | §3.2 của spec | Khung Mindset | Đ2 |
| Visual Report & Sub-agent | §3.3 của spec | Kiến trúc Vision Test Loop | Đ3 |
| Human-in-the-loop & Roadmap | §3.4 của spec | Kiến trúc Vision Test Loop | Đ4 |

## 3. Cách tiếp cận & lý do

### 3.1. Khung Quy chuẩn Mindset Kiểm thử Thực tế cho AI (Đ1)

Nhằm xóa bỏ tình trạng AI viết test máy móc, hời hợt, hình thức, khung quy chuẩn mới quy định:

1. **Nguyên tắc "User-Scenario-Driven Testing" (Kiểm thử Định hướng Kịch bản Người dùng)**:
   - Mọi test case phải đứng ở góc nhìn của người dùng cuối (Black-box / Behavioral perspective) thay vì đứng ở góc nhìn dòng code (White-box implementation details).
   - Cấu trúc kịch bản bắt buộc: `Given [Ngữ cảnh thực tế & Dữ liệu phong phú] - When [Chuỗi hành động của người dùng] - Then [Kỳ vọng hiển thị và trạng thái hệ thống]`.
   - Dữ liệu thử nghiệm (Fixture / Mock data) phải thực tế: Tên có dấu tiếng Việt, địa chỉ thật, chuỗi ký tự dài, số tiền thực tế, định dạng ngày tháng chuẩn; tuyệt đối cấm dùng dữ liệu ngây thơ như `"a"`, `"test"`, `123`.

2. **Cấu trúc 3 Tầng Kịch bản Bắt buộc cho Mọi Tính năng**:
   - **Tầng 1: Realistic Happy Path**: Luồng chính nhưng với dữ liệu phong phú và đa dạng trường hợp sử dụng phổ biến.
   - **Tầng 2: Boundary & Edge Scenarios**: Input rỗng, input cực đại, ký tự đặc biệt, định dạng sai, mạng chậm/timeout, click liên tiếp (race condition), responsive co giãn màn hình.
   - **Tầng 3: Visual & UX Verification (Đối với task có giao diện)**: Bắt buộc giao diện phải được render thực tế và xác nhận bằng thị giác (Rendered & Visually Validated), cấm dừng lại ở việc kiểm tra thẻ HTML có tồn tại trong mã nguồn.

3. **Danh mục 6 Test Anti-Patterns Bị Cấm Tuyệt đối**:
   - `ANTI-1: Tautology Assertions`: Cấm các câu lệnh assert hiển nhiên đúng như `assert True`, `assert response is not None`, `assert len(result) >= 0` mà không kiểm tra giá trị thực sự bên trong.
   - `ANTI-2: Over-mocking (Mock mù quáng)`: Cấm mock luôn cả đối tượng hoặc tầng cần kiểm chứng hành vi (ví dụ: test UI mà mock toàn bộ DOM browser, test API mà mock luôn controller).
   - `ANTI-3: Circular Logic Testing`: Viết test dựa vào chính code vừa tạo ra thay vì dựa vào tài liệu nghiệp vụ/kỳ vọng người dùng.
   - `ANTI-4: Happy-path-only Syndrome`: Chỉ viết 1 ca test duy nhất cho trường hợp lý tưởng nhất, bỏ qua toàn bộ ca lỗi và ca biên.
   - `ANTI-5: Invisible Visual Tests`: Coi việc HTML có class CSS là "giao diện đã đúng" mà không kiểm tra độ hiển thị thị giác thực tế trên canvas/browser.
   - `ANTI-6: Silent Catches`: Bọc try-catch nuốt lỗi trong test khiến test luôn "xanh" dù code bên dưới ném exception.

---

### 3.2. Kiến trúc Kỹ thuật Vòng lặp Kiểm thử Thị giác — Vision Test Loop (Đ2)

Kiến trúc giải pháp được thiết kế theo mô hình **Hybrid Visual Diffing & Self-Correction Loop**:

```
[Design Source] ───┐
 (Figma/Mockup)    │
                   ├──> [Hybrid Diff Engine] ──> [Visual Report] ──> [Sub-agent Review]
[Rendered Dist] ───┘    (Pixel Diff + Boxes)    (Ảnh + Metrics)        (Hậu kiểm)
 (MCP Browser)                     │
                                   ▼
                      [Multimodal Vision AI]
                      (Claude Semantic Eval)
                                   │
                           ┌───────┴───────┐
                           ▼               ▼
                      [PASS: ≤1%]     [FAIL: >1%]
                           │               │
                        Kết thúc      [Fix Action List]
                                           │
                                           ▼ (Lặp ≤ 3 vòng)
                                    [Agent Sửa Code]
                                           │
                                           ▼
                                 [Re-render & Re-test]
                                           │
                                  (Quá 3 vòng -> Báo user)
```

#### Chi tiết 6 bước trong chu trình:

1. **Bước 1: Thu thập Nguồn Thiết kế (`Image Source`)**:
   - *Cách 1 (Local Asset - Khuyến nghị)*: Đọc file ảnh thiết kế gốc (PNG, JPG, SVG) được lưu tại thư mục dự án (ví dụ `docs/assets/designs/<screen>.png` hoặc `assets/mockups/`).
   - *Cách 2 (MCP/System Capture)*: Capture trực tiếp từ ứng dụng mẫu, trang tham chiếu đang chạy hoặc màn hình máy tính thông qua công cụ chụp màn hình.
   - *Cách 3 (Figma REST API)*: Nếu có URL Figma và `FIGMA_ACCESS_TOKEN`, gọi endpoint `https://api.figma.com/v1/images/:file_key?ids=:node_id&format=png&scale=2` để tải về ảnh render chuẩn của component/frame.
   - *Fallback*: Nếu không thể tự lấy ảnh nguồn (thiếu token, link riêng tư, chưa có asset), kích hoạt ngay cơ chế Human-in-the-loop để yêu cầu người dùng cung cấp.

2. **Bước 2: Chụp ảnh Render Thực tế (`Image Dist`)**:
   - Sử dụng công cụ MCP Browser (`mcp__cloudcli-browser` hoặc Playwright headless script).
   - Thiết lập Viewport chuẩn khớp với kích thước của Image Source (mặc định Desktop: `1440x900`, Mobile: `375x812`, hoặc kích thước chính xác của frame thiết kế).
   - Điều hướng (navigate) đến trang web cục bộ (ví dụ `http://localhost:3000` hoặc file static `index.html`).
   - Đợi trang render hoàn chỉnh (`browser_wait_for` selector hoặc network idle) để tránh chụp khi animation hoặc font chưa tải xong.
   - Gọi lệnh `browser_take_screenshot` lưu vào `docs/tdq/visual-reports/images/<slug>-dist-v1.png`.

3. **Bước 3: Thuật toán So sánh Hybrid & Khoanh vùng Bounding Box (Hybrid Diff Engine)**:
   - *Tại sao phải Hybrid?* Thuật toán Pixel Diff tính toán toán học chính xác từng pixel và tọa độ (x, y, w, h), nhưng không hiểu ngữ nghĩa thiết kế. Ngược lại, Multimodal Vision AI hiểu sâu ngữ nghĩa (biết đó là nút bấm, biết font bị lệch) nhưng khó ước lượng chính xác pixel tọa độ nếu không có chỉ dẫn thị giác.
   - *Xử lý tầng 1 (Computer Vision qua Pillow/OpenCV)*:
     - Chuẩn hóa kích thước 2 ảnh về cùng độ phân giải bằng kỹ thuật đệm viền (canvas padding / letterboxing), tuyệt đối CẤM co giãn ảnh (rescaling/stretch) làm méo tỷ lệ giao diện và sai lệch bố cục.
     - Cơ chế Mặt nạ che vùng động (Masking / Ignore Regions): Cho phép khai báo danh sách `ignore_selectors` hoặc tọa độ `ignore_boxes` (ví dụ: ngày giờ động, avatar ngẫu nhiên, banner quảng cáo xoay vòng) để loại trừ trước khi tính toán chênh lệch pixel.
     - Tính ma trận chênh lệch màu sắc từng pixel (Color delta).
     - Áp dụng bộ lọc ngưỡng dung sai (Threshold tolerance) để bỏ qua sai lệch vi mô do khử răng cưa (subpixel antialiasing) giữa các hệ điều hành.
     - Gom cụm các pixel chênh lệch liền kề thành các cụm (Connected Component Contours).
     - Vẽ Bounding Box hình chữ nhật màu đỏ nổi bật xung quanh từng cụm lỗi, đánh số nhãn trực quan: `[1]`, `[2]`, `[3]`,...
     - Xuất ra ảnh `diff_highlight.png` và file JSON metrics: tổng số pixel lệch, tỷ lệ phần trăm lệch (`mismatch_rate`), danh sách tọa độ các hộp Bounding Box.

4. **Bước 4: Phân tích Ngữ nghĩa Thị giác qua Multimodal AI (Claude Vision)**:
   - Nạp cả 3 ảnh: `source.png` (nguồn chuẩn), `dist.png` (render thực tế) và `diff_highlight.png` (khoanh vùng lỗi) vào ngữ cảnh của Claude thông qua multimodal capability.
   - Chạy prompt phân tích chuyên biệt (Visual Evaluation Prompt), yêu cầu AI đối chiếu từng Bounding Box đánh số:
     - `Box [1] (Header area)`: Lệch font chữ (kỳ vọng `Inter Bold 24px`, thực tế `Roboto Regular 20px`), lệch màu chữ (`#111827` vs `#374151`).
     - `Box [2] (Button CTA)`: Lệch padding (thiếu `padding: 12px 24px`, hiện tại đang `8px 16px`), thiếu `border-radius: 8px`.
     - `Box [3] (Card grid)`: Lệch khoảng cách `gap` giữa các cột (kỳ vọng `gap: 24px`, thực tế `gap: 16px`).
   - Phân loại mức độ nghiêm trọng:
     - *CRITICAL*: Vỡ layout, tràn text ra ngoài khung, đè z-index, mất thành phần.
     - *MAJOR*: Sai font, sai màu sắc chủ đạo, lệch padding/margin > 8px.
     - *MINOR*: Lệch khoảng cách 1-2px, sai đổ bóng nhẹ.

5. **Bước 5: Vòng lặp Tự sửa lỗi (Self-Correction Loop) & Ngưỡng Nghiệm thu**:
   - **Tiêu chuẩn PASS**: Tỷ lệ `mismatch_rate <= 1.0%` VÀ không còn lỗi CRITICAL/MAJOR.
   - **Nếu FAIL**:
     - Tự động sinh danh sách việc cần sửa (Actionable Fix List) gắn liền với file code (file CSS, file component JSX/HTML).
     - Agent tiến hành chỉnh sửa mã nguồn để fix các điểm lệch.
     - Tự động re-render, chụp lại ảnh `dist-v2.png`, chạy lại diff và đánh giá vòng tiếp theo.

6. **Bước 6: Cơ chế An toàn Vòng lặp (Safety Budget & Human Fallback)**:
   - **Trần số vòng lặp (`loop_cap = 3`)**: Tối đa 3 vòng lặp auto-fix (nhất quán với quy tắc trần 3 vòng QC của TDQ Workflow).
   - **Cơ chế Dừng sớm (Early Stopping / Divergence Guard)**: Nếu sau 1 vòng sửa mà `mismatch_rate` tăng lên (code sửa làm giao diện vỡ thêm) hoặc không giảm → dừng ngay, không chạy tiếp để tránh dao động (oscillation).
   - **Dừng báo Người dùng khi Quá trần**: Nếu hết 3 vòng lặp mà vẫn chưa đạt tiêu chuẩn PASS, agent **BẮT BUỘC DỪNG LẠI**, xuất file Visual Report đầy đủ hình ảnh và thông báo cho người dùng với chẩn đoán rõ ràng: "Đã qua 3 vòng auto-fix nhưng tỷ lệ lệch vẫn còn X% tại các vị trí [1], [2]. Cần người dùng hỗ trợ duyệt chấp nhận sai lệch hoặc can thiệp thủ công".

---

### 3.3. Đặc tả Định dạng Kép Visual Report (Markdown & Interactive HTML) và Quy trình Sub-agent (Đ3)

Để phục vụ tối ưu cho cả hai đối tượng: **AI agent (đọc văn bản/JSON/ảnh)** và **Người dùng (kiểm tra trực quan bằng mắt)**, hệ thống xuất song song 2 định dạng báo cáo cho mỗi phiên so sánh:

#### 1. Báo cáo Markdown (`docs/tdq/visual-reports/<slug>.md`) — Tối ưu cho AI & Git:
- **Metadata**: Thời gian, tên màn hình, viewport (ví dụ `1440x900`), số vòng lặp đã chạy (`round_count`), kết quả cuối cùng (`PASS`/`FAIL`).
- **Hình ảnh Đối chiếu Trực quan (Bảng ảnh 3 cột)**:
  - Cột 1: Ảnh Nguồn (`Image Source`): Thiết kế chuẩn từ Figma/Mockup.
  - Cột 2: Ảnh Đích (`Image Dist`): Render thực tế phiên bản mới nhất.
  - Cột 3: Ảnh Khoanh vùng Lỗi (`Diff Highlight`): Ảnh trực quan có các khung Bounding Box đỏ `[1]`, `[2]`.
- **Bảng Chỉ số Định lượng (Metrics Table)**:
  - Tỷ lệ sai khác pixel (`mismatch_rate %`).
  - Số lượng vùng sai khác (Count of bounding boxes).
  - Trạng thái từng vòng lặp: Vòng 1 (4.2%) → Vòng 2 (1.8%) → Vòng 3 (0.6% - PASS).
- **Bảng Chi tiết Điểm lệch & Đánh giá Ngữ nghĩa (Actionable Items Table)**:
  - Bảng phân tích từng hộp `[1]`, `[2]` với cột: Vị trí, Sai lệch thiết kế, Mã code liên quan, Trạng thái (Fixed / Accepted / Pending).

#### 2. Báo cáo Tương tác HTML (`docs/tdq/visual-reports/<slug>.html`) — Tối ưu cho Con người:
File HTML độc lập (standalone, self-contained với CSS/JS nhúng trực tiếp, ảnh base64 hoặc đường dẫn tương đối), được **sinh tự động bởi script `tdq_vision_diff.py` từ template dựng sẵn** (tuyệt đối CẤM LLM tự viết mã HTML tương tác để chống cháy token ngữ cảnh). File cho phép người dùng mở trực tiếp bằng trình duyệt với các tính năng trải nghiệm cao cấp:
- **Chế độ So sánh Kéo trượt (Before/After Image Comparison Slider)**:
  - Thanh trượt tương tác (Interactive Split Slider): Người dùng kéo thanh chia đôi màn hình qua lại giữa ảnh thiết kế gốc (Figma) và ảnh render thực tế để mắt thường nhận biết ngay lập tức sự dịch chuyển layout, lệch font hay lệch vị trí nút bấm.
- **Chế độ Lớp phủ Chồng mờ (Overlay Onion-Skin & Blink)**:
  - Slider điều chỉnh độ mờ (Opacity 0% - 100%) giữa 2 lớp ảnh đè lên nhau.
  - Nút bấm "Blink Difference": Tự động nhấp nháy luân phiên giữa 2 ảnh với tần số 2Hz để làm nổi bật các điểm chuyển động bất thường trong layout.
- **Trình Duyệt Lỗi Tương tác (Interactive Bounding Box Explorer)**:
  - Bên cạnh ảnh là danh sách các thẻ lỗi `[1]`, `[2]`, `[3]` được phân loại theo mức độ: Đỏ (Critical), Vàng (Major), Xanh lam (Minor).
  - Khi người dùng click vào một thẻ lỗi:
    + Ảnh bên cạnh tự động zoom và highlight khung chữ nhật đỏ tương ứng.
    + Hiển thị popup chi tiết phân tích của Claude Vision: Sai lệch cái gì (ví dụ: `Font size hiện tại 14px, thiết kế yêu cầu 16px`), gợi ý đoạn mã CSS cần sửa (Code Snippet Suggestion).
- **Lịch sử Vòng lặp (Multi-round Timeline Tabs)**:
  - Các tab điều hướng `Round 1`, `Round 2`, `Round 3` để người dùng theo dõi tiến trình AI đã tự động khắc phục lỗi qua từng vòng lặp ra sao (tỷ lệ lệch giảm dần từ 4.2% → 0.6%).

#### Quy trình Reviewer Sub-agent Hậu kiểm Độc lập (Second-Pair-of-Eyes):
- Sau khi agent implement hoàn thành các vòng auto-fix và tạo bộ đôi file Visual Report (`.md` và `.html`):
- Khởi chạy một Sub-agent chuyên biệt đóng vai trò **Design Reviewer** (có thể là `general-purpose` agent hoặc agent `tdq-reviewer` được cấu hình multimodal vision).
- Nhiệm vụ của Reviewer Sub-agent:
  1. Đọc file `Visual Report` (`.md`), kiểm tra số liệu metrics và trực tiếp xem các file ảnh đính kèm bằng công cụ `Read`.
  2. Rà soát độc lập: Đánh giá xem có lỗi trực quan nào mà thuật toán pixel diff bỏ sót không (ví dụ: hiệu ứng hover, font fallback, tương phản màu chữ với nền, cảm giác thẩm mỹ chung).
  3. Phán quyết:
     - `APPROVED`: Đồng ý nghiệm thu visual, ghi nhận vào file report và bàn giao sang phase tiếp theo.
     - `FEEDBACK`: Phát hiện lỗi thị giác nghiêm trọng còn sót lại → gửi báo cáo feedback chi tiết kèm mã code để agent tiếp tục chỉnh sửa trước khi đóng task.
  4. **Quy tắc an toàn Reviewer**: Reviewer chỉ được phép phản hồi feedback tối đa **đúng 1 lượt**. Nếu sau lượt sửa đó mà giao diện vẫn chưa đạt yêu cầu, agent BẮT BUỘC dừng lại và kích hoạt Human-in-the-loop để người dùng trực tiếp quyết định, tuyệt đối không tạo ra vòng lặp vô hạn giữa implementer và reviewer.

---

### 3.4. Cơ chế Human-in-the-loop & Kế hoạch Phân kỳ Tích hợp TDQ Workflow (Đ4)

#### Cơ chế Human-in-the-loop (Tương tác có Kiểm soát):
Agent không được tự tiện bịa mock data hoặc giả định sai khi thiếu dữ liệu thị giác. Khi gặp các tình huống sau, agent dừng lại và kích hoạt câu hỏi tương tác trong chat:
1. **Thiếu tài nguyên thiết kế**: Không tìm thấy file mockup, không có link Figma, hoặc link Figma yêu cầu quyền truy cập bí mật → Thông báo người dùng cung cấp file ảnh hoặc API token.
2. **Thiếu font/icon bản quyền**: Thiết kế dùng font đặc thù không có sẵn trong hệ thống local → Hỏi người dùng muốn cài đặt font hay chọn font thay thế tương đương (fallback font).
3. **Quá trần 3 vòng lặp**: Đã chạy 3 vòng sửa nhưng chưa pass → Trình bày Visual Report và hỏi người dùng: "Duyệt chấp nhận mức lệch hiện tại hay muốn can thiệp chỉ dẫn sửa tiếp?".

#### Kế hoạch Phân kỳ Tích hợp vào TDQ Workflow (Roadmap cho các request sau):
- **Giai đoạn 1 (Tầng CLI & Script phụ trợ)**:
  - Viết script `scripts/tdq_vision_diff.py`: Nhận đầu vào 2 ảnh (source, dist), hỗ trợ canvas padding và masking vùng động, xuất ra `diff_highlight.png` với bounding boxes, file `metrics.json`, đồng thời tự động render file Interactive HTML Report từ template có sẵn.
  - Viết module tiện ích chụp ảnh qua browser: script wrapper gọi `mcp__cloudcli-browser` hoặc script Playwright headless.
- **Giai đoạn 2 (Tầng Luật & Contract trong Skills)**:
  - Cập nhật `skills/tdq-spec/`: Khi task được gắn nhãn `vision` hoặc `ui-ux`, bắt buộc spec §2 phải khai báo đường dẫn `Image Source` và viewport chuẩn.
  - Cập nhật `skills/tdq-plan/`: Bắt buộc task có bước chụp dist, chạy visual diff và link đến file Visual Report.
  - Cập nhật `skills/tdq-build/references/qc.md`: Bổ sung hạng mục cố định **QC-F5 (Visual Regression Check)** đối với các task UI/UX, áp dụng trần 3 vòng lặp auto-fix và cơ chế dừng báo người dùng.
- **Giai đoạn 3 (Tầng Agent & Multi-agent Automation)**:
  - Bổ sung cấu hình prompt cho Reviewer Sub-agent để tự động kích hoạt vòng hậu kiểm độc lập khi mức QC là `ultra`.

---

## 3b. Năng lực & công cụ

Chép từ brief mục `### Năng lực dùng được`. Phân vân → DÙNG.
Một dòng cho mỗi skill DÙNG hoặc NỀN, cộng đúng một dòng tổng cho phần còn lại.
Không xoá mục này kể cả khi không có dòng DÙNG nào.
Phán quyết chỉ nhận: DÙNG / KHÔNG (+ 1 trong 4 lý do đóng) / NỀN (skill khung đang chạy).

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | tiếp nhận và phân tích yêu cầu |
| tdq-spec | plugin:tdq-workflow | NỀN | lập bản đề xuất kiến trúc (spec proposal) |
| tdq-plan | plugin:tdq-workflow | NỀN | khung lập kế hoạch (bỏ qua ở turn nghiên cứu) |
| tdq-build | plugin:tdq-workflow | NỀN | khung triển khai và QC |
| tdq-conventions | plugin:tdq-workflow | NỀN | quy tắc workflow và định dạng văn bản |
| tdq-status | plugin:tdq-workflow | NỀN | báo cáo trạng thái |
| tdq-lean | plugin:tdq-workflow | NỀN | rà soát tránh over-engineering |
| tdq-setup | plugin:tdq-workflow | NỀN | kiểm tra môi trường tìm kiếm và công cụ |
| tdq-check-status | plugin:tdq-workflow | NỀN | phục hồi phiên |
| Đã xét 15 skill khác trên đĩa và 13 skill built-in | plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service: BỎ — Đây là tài liệu đề xuất giải pháp kiến trúc thuần túy, không tạo runtime daemon hay background service mới.
- Không placeholder, không TODO stub, không vẽ ra các giả định kỹ thuật không có khả năng thực thi.
- Khả thi về công cụ: Đã kiểm chứng môi trường thực tế sẵn có `Python` với thư viện `Pillow`, `Node v24`, và MCP Browser `cloudcli-browser` hoàn toàn hỗ trợ giải pháp.
- Tuân thủ cấu trúc tài liệu, tính nhất quán ngữ nghĩa và các quy tắc `doc_lint.py`.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md`):
- "File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/`" — Khi triển khai ở các phase sau, script `tdq_vision_diff.py` phải nằm trong `scripts/`.
- "Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md".
- "Ngôn ngữ chia 3 tầng: docstring/comment viết tiếng Anh cố định, mã in ra/prompt hướng dẫn tuân thủ i18n."

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Cháy token ngữ cảnh khi đưa quá nhiều ảnh độ phân giải cao vào LLM | Vượt hạn mức context window, tăng chi phí API | Nén ảnh (JPEG/WebP 80% chất lượng), resize về kích thước chuẩn vừa đủ (max width 1440px), chỉ crop các bounding box lỗi ở các vòng lặp sau |
| Thuật toán pixel diff quá nhạy cảm với font rendering giữa các OS | Báo lỗi giả (false positive) do khác biệt khử răng cưa | Đặt ngưỡng dung sai màu sắc (Color tolerance Delta E ≥ 10%) và ngưỡng bỏ qua cụm điểm ảnh < 4 pixel |
| Vòng lặp sửa code bị dao động (sửa chỗ này vỡ chỗ kia) | Tốn lượt lặp vô ích, không hội tụ | Cơ chế Early Stopping: So sánh `mismatch_rate` giữa các vòng, nếu không giảm thì lập tức dừng lại báo người dùng |
| Thiếu tài nguyên thiết kế (Figma link private, thiếu token, mất mạng) | Agent bị tắc hoặc bịa đặt dữ liệu sai | Cơ chế Human-in-the-loop: Dừng lại và trao đổi trực tiếp trong chat để người dùng hỗ trợ cung cấp ảnh |

## 6. QC & Definition of Done

Bảng đo trước cho các tiêu chí số (theo luật R14 `doc_lint`):

| Tiêu chí | Ngưỡng | Đo trước | Dự phòng nếu trượt |
|---|---|---|---|
| Số lượng giải pháp kiến trúc cốt lõi | ≥ 4 giải pháp (Đ1 đến Đ4) | 4 giải pháp chi tiết trong §3 | Bổ sung thêm giải pháp chi tiết |
| Trần số vòng lặp tối đa của Vision Loop | Đúng 3 vòng | 3 vòng (khớp trần QC của TDQ Workflow) | Điều chỉnh trần theo cấu hình |
| Lỗi vi phạm `doc_lint.py` | 0 lỗi vi phạm | Chạy script kiểm tra trực tiếp | Sửa format văn bản theo rule |

| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Mở rộng Mindset kiểm thử | §3.1 quy định rõ nguyên tắc User-Scenario-Driven Testing, 3 tầng kịch bản và 6 Anti-Patterns cấm kỵ |
| Q2 | Kiến trúc Vision Test Loop | §3.2 đặc tả chi tiết 6 bước: Source, Dist, Hybrid Diff, Multimodal AI, Auto-fix Loop (cap 3), Dừng báo người dùng |
| Q3 | Visual Report & Sub-agent Review | §3.3 định nghĩa cấu trúc bộ đôi báo cáo (Markdown cho AI và Interactive HTML với Slider/Onion-skin/Inspector cho người dùng) và quy trình Reviewer Sub-agent độc lập |
| Q4 | Human-in-the-loop & Feasibility | §3.4 quy định rõ kịch bản dừng hỏi người dùng khi thiếu asset; kiểm chứng toolchain (Pillow, Node, cloudcli-browser) sẵn sàng |
| Q5 | Hợp đồng tài liệu | `doc_lint.py` kiểm tra spec đạt 0 vi phạm |
| Q6 | Thẩm định QC mức ultra | Agent QC độc lập (`tdq-qc-tester` hoặc Reviewer) thẩm định, phản biện và xác nhận tính khả thi của bản đề xuất |

DoD:
- Q1–Q6 đạt 100%.
- Không có câu hỏi nào còn mở làm thay đổi kết quả.

## 7. Câu hỏi còn mở

(Trống — Mọi câu hỏi đã được giải quyết trọn vẹn trong phase analyze).
