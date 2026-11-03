# Brief — Nghiên cứu mở rộng mindset test và vòng lặp so sánh vision UI/UX Figma cho TDQ Workflow

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> "okay bây giờ tôi muốn mở request handle một vấn đề, có case AI dùng tdq workflow xử lí task nhưng test rất máy móc, đôi lúc chưa đúng tôi cần mở rộng mindset test của AI để giả lập đúng expect output và giả lập đúng case sử dụng, nhất là những task liên quan đến UI/UX figma, những task đó rất dễ check sai, nên tôi muốn bạn phân tihcs giúp tôi liệu có thể ở những task liên quan đến vision bắt buộc agent code phải capture image source và image dist để compare chi tiết thậm chí khoanh vùng và highligh vùng UIUX và check kĩ nếu chwua đạt thì làm lại loop cho đến khi pass thì có được không? hãy mở request nghiên cứu và phân tích và cho lại tôi đề xuất chưa implement ở turn này"

### First reading

- **Mục tiêu chính**:
  1. Phân tích nguyên nhân và cách mở rộng mindset kiểm thử của AI agent trong TDQ Workflow: tránh test máy móc hình thức, hướng tới việc giả lập đúng trường hợp sử dụng thực tế (realistic user scenarios) và kiểm tra đúng output kỳ vọng (expected output).
  2. Nghiên cứu tính khả thi và đề xuất kiến trúc cho các task liên quan đến Vision / UI/UX / Figma:
     - Cơ chế bắt buộc agent chụp ảnh màn hình nguồn (image source: thiết kế Figma, mockup, ảnh mẫu) và ảnh đích (image dist: kết quả render thực tế trên trình duyệt/ứng dụng).
     - So sánh đối chiếu chi tiết (visual comparison / multimodal diffing), phát hiện sai lệch trực quan, khoanh vùng và highlight các điểm lệch UI/UX.
     - Vòng lặp phản hồi (test-fix-verify loop): nếu chưa đạt thì tự động lặp lại cho đến khi pass hoặc đạt ngưỡng nghiệm thu.
  3. Bổ sung các yêu cầu nâng cao từ người dùng:
     - Sinh file **Visual Report** chi tiết kèm hình ảnh trực quan (source, dist, diff highlight, bảng sai lệch).
     - Vòng kiểm tra hậu kỳ (Post-implementation Review) độc lập: Sau khi hoàn thành, một Reviewer (sub-agent) kiểm tra lại file report và hình ảnh; nếu phát hiện lỗi thì feedback lại để agent tiếp tục sửa.
     - Cơ chế **Human-in-the-loop**: Khi thiếu tài nguyên (ảnh, icon, font, Figma link) ngoài tầm với, agent được phép báo người dùng hỗ trợ cung cấp thay vì tự đoán mò hoặc giả lập sai lệch.
  4. Lập báo cáo phân tích toàn diện và đưa ra đề xuất giải pháp kiến trúc (proposal) mà **chưa tiến hành implement code trong turn này**.

- **Phạm vi dự kiến (Guessed scope)**:
  - Nghiên cứu cơ chế tích hợp công cụ Vision / Browser (MCP browser, Playwright/Puppeteer screenshot, canvas capture, image diffing algorithms / LLM vision multimodal feedback).
  - Tích hợp vào các giai đoạn của TDQ Workflow:
    + Phase `plan` / `spec`: Xác định task thuộc loại `vision`/`ui-ux`, khai báo nguồn source/dist và visual DoD.
    + Phase `implement` / `qc`: Cơ chế chụp source vs dist, công cụ diff/highlight, vòng lặp auto-fix tối đa 3 vòng và báo cáo người dùng nếu quá tải.
    + Vòng review độc lập: Sub-agent rà soát visual report trước khi đóng task.
  - Phân tích chi phí (tokens, runtime, rate limits) và rủi ro vòng lặp vô hạn (infinite loop).

## Hiểu & kiến thức

### Năng lực dùng được

Phân vân → DÙNG. Kiểm kê ngày 2026-10-14: 24 skill trên đĩa, cộng skill built-in trong context. Không xoá bảng này kể cả khi không có dòng DÙNG nào.

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
| Đã xét 15 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

### 1. Phân tích hiện trạng: Vì sao AI kiểm thử máy móc?

- **Căn bệnh "Testing Implementation Details" thay vì "User Behavior"**:
  - AI thường nhìn vào code vừa viết rồi sinh ra test tương ứng (circular logic), dẫn tới việc chỉ test những gì code đang làm chứ không test những gì người dùng thực sự kỳ vọng.
  - Ví dụ: Một chức năng tạo hóa đơn, AI viết test kiểm tra hàm `calculate_tax()` được gọi với tham số X, nhưng không bao giờ test kịch bản người dùng đặt hàng với giỏ hàng rỗng, áp mã giảm giá vượt quá giá trị đơn hàng, hay xem giao diện hóa đơn render ra sao.
- **Lạm dụng Mock quá đà (Over-mocking & False Confidence)**:
  - Để test "xanh" nhanh nhất, AI thường mock mọi thứ: mock database, mock network, mock browser DOM. Khi chạy test thì 100% pass nhưng khi deploy thật thì vỡ vì mock khác xa môi trường runtime.
  - Assertions hời hợt: Sử dụng các assert kiểu hình thức như `assert response is not None`, `assert result == True`, `assert status_code == 200` mà không kiểm tra nội dung dữ liệu trả về, không kiểm tra tác dụng phụ (side effects), không kiểm tra trạng thái màn hình.
- **Điểm mù thị giác (Visual Blindness) trong các task UI/UX & Figma**:
  - Với task UI/UX, AI hiện chỉ inspect DOM hoặc regex tìm kiếm class/id CSS trong file code.
  - Tuy nhiên, một thẻ `<div>` có class `btn-primary` không đảm bảo nút bấm hiển thị đúng: nó có thể bị nút khác đè lên (z-index), bị tràn chữ (text overflow), sai font-family do chưa load font, sai padding/margin gây vỡ flexbox, hoặc màu nền tương phản quá thấp khiến người dùng không đọc được.

### 2. Đề xuất mở rộng Mindset Kiểm thử cho AI trong TDQ Workflow

- **Nguyên tắc "User-Scenario-Driven Testing" (Kiểm thử định hướng kịch bản người dùng)**:
  - Mọi kịch bản test trong spec/plan phải mô tả dưới dạng kịch bản người dùng thực tế: `Given [Ngữ cảnh người dùng] - When [Hành động thực tế] - Then [Kỳ vọng hiển thị/kết quả]`.
  - Bắt buộc kiểm tra 3 tầng kịch bản:
    1. *Happy path thực tế*: Dữ liệu phong phú, tên có dấu tiếng Việt, ký tự đặc biệt, số tiền thực tế thay vì dummy data ngắn ngủi.
    2. *Boundary & Edge cases*: Dữ liệu rỗng, dữ liệu cực đại, màn hình co nhỏ (responsive), mạng chập chờn.
    3. *Visual & UX Verification*: Giao diện phải được render và nhìn thấy được (Rendered & Visually inspected).
- **Bộ lọc Anti-patterns kiểm thử (Test Anti-pattern Checklist)**:
  - Cấm hoàn toàn các assert vô nghĩa (`assert True`, `assert x is not None`).
  - Cấm mock các thành phần cần kiểm chứng tính tích hợp thực tế.

### 3. Phân tích tính khả thi & Kiến trúc Vòng lặp Kiểm thử Thị giác (Vision Test Loop)

Kiến trúc giải pháp được thiết kế theo mô hình **Hybrid Visual Diffing, Self-Correction Feedback Loop & Independent Review**:

1. **Thu thập nguồn thiết kế (Image Source)**:
   - File mockup gốc (PNG, JPG, SVG) được lưu trong `docs/assets/designs/` hoặc thư mục dự án.
   - Capture trực tiếp từ máy cục bộ, trang mẫu tham chiếu, hoặc qua MCP Browser.
   - Hoặc gọi qua Figma API (với Personal Access Token) để render node thiết kế thành ảnh chuẩn.
   - **Human-in-the-loop**: Khi thiếu tài nguyên (icon, font, asset ảnh chuẩn, token Figma), agent chủ động dừng lại và yêu cầu người dùng hỗ trợ cung cấp thay vì tự đoán mò.
2. **Chụp ảnh render thực tế (Image Dist)**:
   - Kích hoạt môi trường dev cục bộ (local server hoặc file HTML static).
   - Sử dụng công cụ MCP Browser (`cloudcli-browser` hoặc Playwright script) để tự động navigate đến trang web, thiết lập viewport chuẩn (Desktop: 1440x900, Mobile: 375x812), đợi render hoàn tất (`browser_wait_for`) và gọi `browser_take_screenshot` lưu thành `dist.png`.
3. **So sánh đối chiếu chi tiết (Compare & Highlight)**:
   - **Tầng 1 (Thuật toán Pixel & Bounding Box)**: Chạy script so sánh ảnh (dùng Pillow/OpenCV). Script tính ma trận sai khác, áp dụng ngưỡng dung sai màu sắc (color tolerance), nhóm các cụm pixel lệch thành các Bounding Box hình chữ nhật màu đỏ/cam, đánh số thứ tự `[1]`, `[2]`, `[3]`, và tính tỷ lệ lệch tổng thể (`mismatch_rate`).
   - **Tầng 2 (Multimodal AI Vision Semantic Analysis)**: Đưa cả 3 ảnh (`source.png`, `dist.png`, `diff_highlight.png`) vào mô hình Vision (Claude Multimodal). AI sẽ phân tích ngữ nghĩa UI tại từng Bounding Box:
     + Box 1: Font chữ lệch (kỳ vọng Inter SemiBold 16px, thực tế Roboto Regular 14px).
     + Box 2: Spacing lệch (padding top thiếu 12px, khoảng cách giữa các card quá hẹp).
     + Box 3: Màu sắc lệch (mã hex `#2563EB` thay vì `#1D4ED8`).
4. **Vòng lặp phản hồi tự động (Test-Fix-Verify Feedback Loop)**:
   - Nếu `mismatch_rate <= threshold` (ví dụ < 1.0% do khử răng cưa) và AI Vision xác nhận "NO_CRITICAL_DEFECT" → **PASS**.
   - Nếu chưa đạt:
     + Trích xuất danh sách các điểm lệch hành động được (Actionable Fix List).
     + Agent tiến hành sửa CSS/HTML tương ứng.
     + Tự động render, chụp ảnh lại và lặp lại bước so sánh.
5. **Cơ chế an toàn & Giới hạn vòng lặp (Safety & Loop Budget)**:
   - *Trần số vòng lặp (`loop_cap`)*: Tối đa 3 vòng lặp (tương đồng với quy tắc trần 3 vòng QC của TDQ Workflow).
   - *Quy tắc dừng báo người dùng*: Nếu hết 3 vòng vẫn chưa đạt (hoặc qua 1 vòng mà sai lệch tăng lên) → BẮT BUỘC dừng lại, xuất báo cáo kèm hình ảnh và báo cho người dùng hỗ trợ xử lý.
6. **Báo cáo trực quan & Vòng kiểm tra hậu kỳ (Visual Report & Sub-agent Review)**:
   - Tự động sinh file **Visual Report** (`docs/tdq/visual-reports/<slug>.md`) kèm hình ảnh đối chiếu (Source, Dist, Diff Highlight) và bảng chỉ số sai lệch.
   - Kích hoạt một reviewer độc lập (sub-agent) đọc lại file report và hình ảnh để thực hiện "second-pair-of-eyes review". Nếu phát hiện lỗi sót, reviewer gửi feedback để agent tiếp tục tinh chỉnh trước khi nghiệm thu.

### Lộ trình

Bảng lộ trình các bước còn lại (áp dụng cho request Nghiên cứu & Đề xuất kiến trúc, không sinh mã triển khai):

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| `analyze` | CÓ | Đang tiến hành: khảo sát, nghiên cứu, hoàn thành phỏng vấn và chốt kiến thức |
| `spec` | CÓ | Lập bản Đề xuất Giải pháp Kiến trúc hoàn chỉnh (Architectural Spec Proposal) chi tiết các cơ chế, hợp đồng kỹ thuật và lộ trình tích hợp |
| `plan` | BỎ | Turn này là nghiên cứu và đề xuất kiến trúc thuần túy, chưa viết mã triển khai thực tế |
| `implement` | BỎ | Theo đúng chỉ đạo của người dùng: "hãy mở request nghiên cứu và phân tích và cho lại tôi đề xuất chưa implement ở turn này" |
| `qc` | CÓ | Kiểm định tài liệu đề xuất: rà soát tính khả thi của toolchain, kiểm tra hợp đồng văn bản (`doc_lint`), mức QC `ultra` có agent QC độc lập soi phản biện bản đề xuất |
| `report` | CÓ | Lập báo cáo kết quả nghiên cứu toàn diện và đề xuất các bước hành động tiếp theo cho người dùng |

## Hỏi đáp

### Vòng 1 — Định hình Phạm vi & Phương án Kiến trúc

1. Request này bạn muốn tập trung đề xuất sâu những khía cạnh nào?
- A (đề xuất): Cả 2 khía cạnh: (1) Mở rộng Mindset kiểm thử thực tế cho AI toàn workflow + (2) Kiến trúc chi tiết Visual Test Loop (Figma/Source vs Dist + Bounding Box Highlight + Auto Fix Loop).
- B: Chỉ tập trung sâu vào cơ chế Visual Test Loop cho UI/UX/Figma (chụp ảnh, diffing, khoanh vùng highlight và feedback loop).
- C: Chỉ tập trung vào bộ quy tắc mở rộng Mindset kiểm thử của AI (tiêu chuẩn kịch bản thực tế, chống test máy móc, chống mock hời hợt).
*Đã chọn: A (Cả 2 khía cạnh: Mindset kiểm thử thực tế + Kiến trúc chi tiết Visual Test Loop).*

2. Đối với các task UI/UX, nguồn thiết kế chuẩn (`image source`) bạn dự kiến cung cấp chủ yếu theo hình thức nào?
- A (đề xuất): Kết hợp linh hoạt: Ưu tiên file ảnh mockup có sẵn trong repo (hoặc thư mục chỉ định), kèm tùy chọn fetch qua Figma API nếu có Figma URL và API Token.
- B: Thuần túy qua file ảnh cục bộ (người dùng export ảnh từ Figma hoặc chụp mockup bỏ vào thư mục dự án).
- C: Tích hợp trực tiếp Figma API (bắt buộc cấu hình Figma Personal Access Token để tự động lấy ảnh frame thiết kế).
*Đã chọn: A kết hợp linh hoạt (file ảnh có sẵn, capture từ máy/MCP, hoặc Figma API; nếu ngoài tầm với thì báo người dùng hỗ trợ).*

3. Về cơ chế so sánh và khoanh vùng highlight lệch UI/UX, bạn muốn tiếp cận theo hướng nào?
- A (đề xuất): Hybrid (Kết hợp): Thuật toán Pixel Diff tạo ảnh highlight đỏ các vùng lệch + Multimodal Vision (Claude đọc ảnh) để diễn giải chính xác lỗi (sai font, lệch padding, sai mã màu).
- B: Thuần túy Multimodal Vision AI: Đưa thẳng 2 ảnh Source và Dist cho Claude Vision tự so sánh và tự chỉ ra tọa độ/điểm lệch không cần script phụ trợ.
- C: Thuần túy Pixel Diff: Dùng script đo % pixel khác biệt và vẽ khung chữ nhật, đạt dưới ngưỡng % là pass.
*Đã chọn: A (Hybrid: Pixel Diff Bounding Box Highlight + Multimodal Vision).*

4. Về cơ chế vòng lặp phản hồi (Feedback loop), bạn muốn cấu hình giới hạn an toàn ra sao?
- A (đề xuất): Trần tối đa 3 vòng lặp (chuẩn theo trần QC của TDQ Workflow) + cơ chế dừng sớm nếu qua 1 vòng mà tỷ lệ sai lệch không giảm.
- B: Cho phép người dùng tùy chỉnh số vòng lặp tối đa (từ 1 đến 5 vòng) kèm trần token/thời gian.
- C: Chỉ chụp và so sánh 1 lần duy nhất để báo cáo cho người dùng duyệt, không tự động sửa lại theo vòng lặp.
*Đã chọn: A (Trần 3 vòng lặp auto-fix, nhưng nếu sau 3 vòng vẫn chưa ổn thì bắt buộc dừng lại báo người dùng hỗ trợ).*

5. Request này bạn muốn QC tới mức nào?
- A (đề xuất): `full` — DoD + kiểm tra tính khả thi của toolchain + kiểm định tài liệu đề xuất + doc_lint + clean code.
- B: `lite` — DoD + kiểm tra tài liệu đề xuất. Nhanh nhất.
- C: `ultra` — như `full`, thêm một agent QC độc lập soi phản biện bản đề xuất kiến trúc.
*Đã chọn: C (`ultra` — có agent QC độc lập soi phản biện bản đề xuất kiến trúc).*

6. Bạn muốn bổ sung thêm gì không?
- A (đề xuất): Không, đủ rồi — làm tiếp đi.
- B: Có — tôi nói thêm.
*Đã chọn: B (Bổ sung: Phải có file Visual Report kèm hình ảnh trực quan; sau khi hoàn thành có vòng review độc lập của Reviewer/Sub-agent đọc lại report/ảnh và feedback sửa tiếp nếu còn lỗi; khi thiếu resource ngoài tầm với phải báo người dùng hỗ trợ).*
