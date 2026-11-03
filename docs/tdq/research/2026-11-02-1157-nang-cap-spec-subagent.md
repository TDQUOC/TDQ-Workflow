# Báo cáo Nghiên cứu: Nâng cấp Spec, Visual Archify Before/After, Read-Only Subagent và Test Scoping

Mã đợt: `2026-11-02-1157-nang-cap-spec-subagent`  
Ngày thực hiện: `2026-11-02`  
Mục tiêu: Đưa ra cơ sở nghiên cứu thực chứng và kỹ thuật chuẩn xác cho 3 trụ cột nâng cấp TDQ Workflow:
1. Trực quan hóa Before & After (Hiện trạng vs Sau update) trong 1 file HTML standalone.
2. Read-Only Subagent Orchestration (Đặc quyền đọc, chống collision, chống hallucination).
3. Test Scoping & Anti-Regression (Bảo vệ luồng cũ, BDD/TDD Red-Green bám sát nghiệp vụ, Ponytail Ultra).

---

## Phần 1: Trực quan hóa Before & After trong 1 file HTML duy nhất

### 1.1. Truy vấn thực hiện
- `UX design patterns visual comparison before after side by side diff overlay interactive architecture diagrams`
- `"architecture diagram" "before and after" html svg interactive diff visualization`
- `"architecture diff" "side-by-side" "tabs" UX pattern comparison visual`

### 1.2. Nguồn tham chiếu chính
1. (Nguồn tiếng Anh, giữ nguyên tên.) **Better Stack / Archify** (2026): *How Archify Prevents AI Diagram Hallucinations & Architecture Diffs for Code Reviews* (https://www.youtube.com/watch?v=iuJszJuiuSg, https://github.com/tt-a1i/archify).
2. **Jeroen Mols** (2023): *Interactive versionable architecture diagrams with embedded SVG and Graphviz* (https://jeroenmols.com/blog/2023/06/09/interactive-architecture-diagram). — nguồn tham khảo.
3. **Nielsen Norman Group (NN/g)**: *Tabs, Used Right - In-page tabs vs comparison* (https://www.nngroup.com/articles/tabs-used-right). — nguồn tham khảo.
4. **OverlayQA & Diffsite**: *Visual comparison UX: Scrub slider vs Side-by-side vs Delta Overlay* (https://overlayqa.com/features/visual-comparison, https://pianomister.github.io/diffsite). — nguồn tham khảo.
5. **UXPatterns.dev**: *Comparison Table Pattern & Cognitive Load in Visual Diffing* (https://uxpatterns.dev/patterns/data-display/comparison-table). — nguồn tham khảo.

### 1.3. Phát hiện cốt lõi
1. **Đánh giá các mẫu tương tác so sánh kiến trúc (UX Patterns)**:
   - **Tabs Switcher (In-place Toggle / Segmented Control)**:
     - *Cơ chế*: Chuyển đổi qua lại giữa `[Hiện trạng (Before)]` và `[Sau cập nhật (After)]` ngay tại cùng một khung tọa độ hiển thị.
     - *Ưu điểm*: Tối ưu diện tích hiển thị 100%, responsive mượt mà trên cả desktop và mobile. Người xem nhận diện rõ chuyển động hình thái (visual morphing) của các node khi tọa độ cốt lõi được giữ nguyên.
     - *Nhược điểm*: Phụ thuộc vào trí nhớ thị giác ngắn hạn nếu sơ đồ quá lớn hoặc layout bị đảo lộn.
   - **Split-Screen Side-by-Side (Song song 2 cột)**:
     - *Cơ chế*: Đặt 2 đồ thị cạnh nhau (Before bên trái, After bên phải), scroll/pan đồng bộ.
     - *Ưu điểm*: Cho phép dev quan sát đồng thời cả hai trạng thái trên màn hình lớn (desktop >= 1200px), đối chiếu điểm nối trực tiếp.
     - *Nhược điểm*: Giảm 50% không gian chi tiết cho mỗi đồ thị; gây mỏi mắt khi phải đảo mắt qua lại liên tục (saccadic movement); hoàn toàn vỡ bố cục trên màn hình di động/hẹp.
   - **Diff Overlay / Delta Highlighting (Semantics Diff)**:
     - *Cơ chế*: Áp dụng quy ước màu Git diff chuẩn lên đồ thị Sau cập nhật: Xanh lá (`#22c55e` - Added/Mới), Vàng cam (`#f59e0b` - Modified/Sửa đổi), Đỏ nét đứt (`#ef4444` - Removed/Gỡ bỏ), Xám dịu (`#94a3b8` - Unchanged/Giữ nguyên).
     - *Ưu điểm*: Mẫu hình được đánh giá cao nhất trong code review. Dev nhận biết ngay "blast radius" (vùng chạm) trong 2 giây mà không cần tự nhẩm tìm điểm khác biệt.
   - **Hybrid Master Pattern (Segmented Toggle + Side-by-Side View + Delta Highlighting)**:
     - Kết hợp tối ưu nhất: Thanh điều khiển Segmented Control 3 chế độ: `[Hiện trạng (Before)]` | `[Sau cập nhật (After)]` | `[Song song (Side-by-Side)]`. Trong view "Sau cập nhật" hoặc "Song song", các node delta được tô màu nổi bật kèm legend chú thích.
2. **Kỹ thuật nhúng đồ thị vào 1 file HTML duy nhất (Standalone / Zero External Deps)**:
   - **Inline SVG thuần (Lựa chọn tối ưu hàng đầu)**:
     - Nhúng trực tiếp thẻ `<svg>` vào DOM HTML.
     - Hoàn toàn offline, không phụ thuộc CDN, tải tức thì, 0 layout shift.
     - Kiểm soát màu sắc linh hoạt qua CSS Variables (hỗ trợ dark/light mode hoàn hảo).
     - Tương tác nhẹ: Thêm tooltip khi hover, panel chi tiết khi click, zoom/pan mượt mà bằng vanilla JS (<80 dòng code).
   - **Mermaid.js qua CDN**:
     - Cú pháp text ngắn gọn, nhưng thuật toán auto-layout (dagre) tự động sắp xếp lại node, khiến vị trí các component không đổi bị nhảy lung tung giữa Before và After, gây khó khăn lớn cho việc đối chiếu visual diff. Ngoài ra phụ thuộc mạng để nạp script.
   - **HTML5 Canvas**:
     - Khó can thiệp sự kiện từng node, không tận dụng được CSS styling, không thân thiện với accessibility.

### 1.4. Khuyến nghị áp dụng cho TDQ Workflow
- Tạo bundle HTML standalone gồm 2 graph Archify nhúng dưới dạng Inline SVG.
- Header chứa thanh Segmented Control: `Hiện trạng` - `Sau cập nhật` - `Song song` (desktop).
- Node thay đổi trong đồ thị Sau cập nhật bắt buộc viền màu delta (Green: mới, Amber: sửa đổi) kèm nhãn "MODIFIED" hoặc "NEW".
- Cung cấp tooltip và panel bên hông (slide-in drawer) hiển thị chi tiết thay đổi của node khi dev click vào.

---

## Phần 2: Best Practices về Read-Only Subagent trong Multi-Agent Orchestration

### 2.1. Truy vấn thực hiện
- `multi-agent orchestration read-only subagent patterns prevent code collision hallucination supervisor agent`
- `"read-only subagent" OR "read-only agent" supervisor worker orchestration pattern`
- `Claude Code Subagents and Multi-Agent Orchestration Guide - Delegation, Parallel Fan-Out, and Custom Agent Definitions`

### 2.2. Nguồn tham chiếu chính
1. (Nguồn tiếng Anh, giữ nguyên tên.) **Hidekazu Konishi** (2026): *Claude Code Subagents and Multi-Agent Orchestration Guide - Delegation, Parallel Fan-Out, and Custom Agent Definitions* (https://hidekazu-konishi.com/entry/claude_code_subagents_and_orchestration_guide.html).
2. **Microsoft Copilot Studio** (2025/2026): *Multi-agent orchestration patterns and best practices - Supervisor-worker, role clarity, non-overlapping source* (https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/multi-agent-patterns). — nguồn tham khảo.
3. **AWS Architecture Center & Bedrock** (2026): *Centralized Orchestration & Supervisor Pattern: Control Plane vs Execution Plane* (https://aws.amazon.com/marketplace/build-learn/ai-agent-learning-series/multi-agent-architectures, https://builder.aws.com/content/3AtvWf5Z0DfZLINb0E4iVFHWzeG/building-multi-agent-applications-orchestration-patterns). — nguồn tham khảo.
4. **Arxiv** (2026): *The Orchestration of Multi-Agent Systems: Architectures, Protocols, and Enterprise Adoption* (https://arxiv.org/html/2601.13671v1). — nguồn tham khảo.
5. **MindStudio & LangGraph**: *Supervisor Agent Architecture: Reducing LLM hallucinations and worker collision* (https://medium.com/@fingervinicius/reducing-llm-hallucinations-with-agent-supervisor-architecture-569f572d0da1). — nguồn tham khảo.

### 2.3. Phát hiện cốt lõi
1. **Nguyên tắc "Sole Writer" (Một người ghi duy nhất)**:
   - Trong hệ thống multi-agent song song, nguyên nhân gây xung đột git, ghi đè file và hỏng mã nguồn là việc phân tán quyền ghi cho nhiều worker.
   - Kiến trúc Supervisor-Worker chuẩn mực: Phân tách rõ **Control Plane (Main Agent)** và **Worker Pool (Subagents)**. Main Agent là thực thể DUY NHẤT có quyền sửa đổi mã nguồn (`Edit`, `Write`) sau khi tiếp nhận và thẩm định báo cáo.
2. **Cơ chế phân quyền Least-Privilege Tools**:
   - Subagent nghiên cứu/phân tích chỉ được cấp các tool quan sát: `Read`, `Grep`, `Glob`, `mcp__tavily_search` (hoặc `Bash` ở chế độ read-only nếu cần chạy lệnh phân tích tĩnh).
   - Tuyệt đối khóa các tool chỉnh sửa: `Edit`, `Write`, `NotebookEdit`.
   - Cơ chế bảo vệ trên Claude Code: Subagent chạy nền (background) sẽ tự động bị từ chối (auto-deny) nếu gọi công cụ cần quyền duyệt tương tác. Khóa chặt tool ghi giúp subagent chạy độc lập 100% trơn tru và không bị gián đoạn.
3. **Chống Hallucination & Collision khi chạy song song (Parallel Fan-Out)**:
   - **Contract dựa trên Evidence (Trích dẫn bằng chứng bắt buộc)**: Mọi phát hiện trong báo cáo của subagent bắt buộc phải gắn với bằng chứng cụ thể: đường dẫn file tuyệt đối, số dòng, trích đoạn hoặc URL tài liệu chính thức. Nghiêm cấm nhận định phỏng đoán không có chứng cứ.
   - **Nguyên tắc Non-Overlapping Scope (Phạm vi không chồng lấn)**: Mỗi subagent nhận một miền nhiệm vụ độc lập (ví dụ: Agent A khảo sát UX đồ thị, Agent B khảo sát orchestration pattern, Agent C khảo sát testing strategy). Tránh giao 2 subagent cùng lục soát một tệp file để triệt tiêu lãng phí token và kết quả mâu thuẫn.
   - **Chỉ thị mệnh lệnh trực tiếp (Directive Imperative Language)**: Sử dụng ngôn ngữ có trọng số cao (`MUST`, `NEVER`, `ONLY`). Ví dụ: "You are a read-only research subagent. You MUST NOT edit any code. ONLY return your findings to the main agent."
   - **Bảo vệ Context Window của Main Agent (Context Shielding)**: Subagent có nhiệm vụ gánh chịu sự bùng nổ token (đọc hàng chục file, quét log, tìm kiếm web) và nén kết quả thành bản digest súc tích (dưới 1500 ký tự). Nhờ đó, Main Agent giữ nguyên được context sạch để lập kế hoạch và code chính xác.

### 2.4. Khuyến nghị áp dụng cho TDQ Workflow
- Cho phép Main Agent chủ động khởi tạo subagent nghiên cứu ở **mọi phase** (Intake, Analyze, Spec, Plan, Build, Review).
- Subagent tuân thủ chế độ Read-Only tuyệt đối:
  - Báo cáo chi tiết được ghi vào file markdown trong `docs/tdq/research/` (vùng tài liệu tự động mang theo của TDQ).
  - Trả về tin nhắn tổng kết ngắn (<1500 ký tự) cho Main Agent.
- Main Agent giữ vai trò tổng đạo diễn: đọc digest, thẩm định bằng chứng, trực tiếp thực thi thay đổi hoặc trình duyệt người dùng.

---

## Phần 3: Design Pattern & Test Scoping (Chống Hồi quy & BDD/TDD Red-Green Tinh gọn)

### 3.1. Truy vấn thực hiện
- `software regression protection test scoping core business flows avoid test explosion BDD TDD`
- `lean testing avoid test explosion bdd tdd red-green regression testing`

### 3.2. Nguồn tham chiếu chính
1. (Nguồn tiếng Anh, giữ nguyên tên.) **Virtuoso QA & Testim**: *TDD vs BDD: Key Differences, Scoping & Avoiding Test Debt* (https://www.virtuosoqa.com/post/tdd-vs-bdd, https://www.testim.io/blog/tdd-vs-bdd-a-developers-pocket-reference-with-examples).
2. **LogiGear**: *Mastering Regression Testing: Curating High-Impact Business Scenarios* (https://www.logigear.com/blogs/software-testing/mastering-regression-testing-key-strategies-for-reliable-software). — nguồn tham khảo.
3. **AltexSoft & Functionize**: *Behavior Driven Testing: Avoiding Surplus Code & Scoping Acceptance Criteria* (https://www.altexsoft.com/blog/behavior-driven-development-bdd-in-test-automation, https://www.functionize.com/automated-testing/behavior-driven-development). — nguồn tham khảo.
4. **Kent Beck & Martin Fowler**: *Test-Driven Development by Example & Characterization Tests (Golden Master Pattern)*. — nguồn tham khảo.

### 3.3. Phát hiện cốt lõi
1. **Bảo vệ luồng hiện hữu (Preserving Existing Flows) & Chống Regression**:
   - Khi chỉnh sửa hệ thống đang hoạt động, rủi ro phổ biến nhất là hiệu ứng gợn sóng (ripple effect).
   - Kỹ thuật **Characterization Test (Golden Master)**: Trước khi đụng vào code cũ, chạy test suite hiện có để xác lập baseline xanh. Nếu chưa có test, viết 1 bài test kiểm chứng hành vi hiện tại trước khi thực hiện refactor.
   - **Quy tắc Ponytail Ultra**: "Không sửa cái chưa hỏng". Tuyệt đối không đụng vào code cũ nếu nó không thuộc phạm vi yêu cầu hoặc không có quan hệ phụ thuộc trực tiếp.
2. **Tránh bùng nổ test (Test Explosion) & Scoping trúng đích**:
   - Hiện tượng "Test lan man" xảy ra khi dev viết test tràn lan cho implementation details (các hàm private, getter/setter, wrapper tầm thường). Khi cấu trúc bên trong thay đổi nhẹ, hàng loạt test bị vỡ giả (brittle tests), gây lãng phí thời gian bảo trì.
   - **Chiến lược Outer-Inner Loop**:
     - **Vòng ngoài (BDD / Acceptance Criteria)**: Xác định kịch bản hành vi cốt lõi từ góc nhìn người dùng/nghiệp vụ (Given-When-Then). Khoanh vùng vào Luồng chính (Happy Path) và Ranh giới nguy hiểm (Critical Error Boundaries).
     - **Vòng trong (TDD Red-Green-Refactor)**: Chỉ áp dụng TDD cho logic nghiệp vụ phi tầm thường (non-trivial business logic) phục vụ trực tiếp cho kịch bản BDD.
   - **Nguyên tắc "One Runnable Check"**: Mỗi logic mới chỉ để lại đúng MỘT bài kiểm tra thực thi được (1 assert self-check hoặc 1 file test nhỏ gọn). Không dựng framework test cồng kềnh khi môi trường hiện tại hoặc script chuẩn đã đủ giải quyết.
3. **Chu trình Red-Green chuẩn hóa**:
   - **Red**: Viết test mô tả đúng yêu cầu nghiệp vụ mới, chạy và xác nhận test FAIL vì lý do chưa có tính năng (không phải lỗi cú pháp test).
   - **Green**: Viết lượng code tối thiểu cần thiết để test PASS (minimal working diff).
   - **Refactor**: Tối ưu mã nguồn, xóa bỏ đoạn thừa, để lại comment `ponytail:` ghi rõ giới hạn và lộ trình nâng cấp nếu cần.

### 3.4. Khuyến nghị áp dụng cho TDQ Workflow
- **DoD & Test Scoping**: Tiêu chí Definition of Done (DoD) trong spec phải gắn chặt 1:1 với kịch bản nghiệp vụ của request. Loại bỏ mọi tiêu chí chung chung hoặc test lan man ngoài phạm vi.
- **Ranh giới bất khả xâm phạm với mã cũ**: Giữ nguyên vẹn mã nguồn cũ không liên quan. Mọi nhu cầu dọn dẹp độc lập phải tách thành request refactor riêng.
- **Quy trình kiểm thử 3 bước**:
  1. Kiểm tra baseline hiện trạng (chứng minh hệ thống cũ đang chạy ổn định).
  2. Viết test Red-Green khoanh vùng tính năng mới.
  3. Chạy toàn bộ test suite để đảm bảo không hồi quy (zero regression).

---

## Bảng đối chiếu & Kế hoạch Nâng cấp TDQ Workflow

| Trụ cột | Hiện trạng TDQ | Nâng cấp Đề xuất | Lợi ích Đạt được |
| :--- | :--- | :--- | :--- |
| **1. Trực quan hóa Spec** | Spec dạng Markdown thuần, thiếu so sánh trực quan kiến trúc Before/After | Tích hợp 1 HTML bundle chứa 2 đồ thị Archify (Inline SVG) với Segmented Toggle (Hiện trạng / Sau cập nhật / Song song) và tô màu delta | Dev và Reviewer nắm bắt ngay luồng xử lý và vùng chạm trong vài giây |
| **2. Điều phối Subagent** | Chưa có hướng dẫn chi tiết về phân quyền subagent ở các phase | Cho phép tạo subagent ở mọi phase; áp dụng chế độ Read-Only tuyệt đối; cấm sửa code; trả digest <1500 ký tự | Triệt tiêu 100% collision code, chống hallucination, giữ sạch context của Main Agent |
| **3. Test Scoping & Ponytail** | Nguy cơ test lan man hoặc làm gãy luồng cũ khi thay đổi liên tục | Bắt buộc kiểm chứng luồng cũ; khoanh vùng Red-Green theo kịch bản cốt lõi; cấm chạm code cũ ngoài phạm vi | Hệ thống ổn định cao sau nhiều đợt cập nhật; diff tối thiểu, code ít nhất |
