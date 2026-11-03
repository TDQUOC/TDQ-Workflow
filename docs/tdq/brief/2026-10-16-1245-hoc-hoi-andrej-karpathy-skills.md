# BRIEF — Phân tích học hỏi từ andrej-karpathy-skills để cải tiến TDQ Workflow

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> "hi tôi có clone C:\Users\admin\Documents\andrej-karpathy-skills hãy mở request fan out subagent phân tích kĩ tdq-workflow hiện tại và project đó để cho tôi biết có thể học hỏi gì ở project đó để khiến quy trình làm việc của tdq-workflow tốt hơn và hiệu quả hơn. Output đợt này expect html report chi tiết và chứng cứ nếu có chưa implement thay đổi ở turn này"

### Đọc bước đầu

- **Mục tiêu**:
  1. Phân tích, khảo sát toàn diện cấu trúc, tư tưởng thiết kế, bộ guidelines, rule và kỹ thuật của repo `C:\Users\admin\Documents\andrej-karpathy-skills`.
  2. So sánh đối chiếu với pipeline, triết lý vận hành (Soul, TDD, 3-layer search, hook gates, team mode, subagents) và instruction của TDQ Workflow hiện tại.
  3. Fan-out các subagent độc lập để phân tích đa chiều (triết lý coding của Karpathy, cách tổ chức skill/rule, phương pháp prompt/guidelines, tác động đến hiệu suất và độ tin cậy của Agent).
  4. Rút ra các bài học đắt giá, điểm mạnh có thể học hỏi hoặc tích hợp để nâng cấp quy trình làm việc của TDQ Workflow tốt hơn, tự nhiên hơn và hiệu quả hơn.
  5. Xuất bản tài liệu báo cáo chuyên sâu dạng HTML Report chi tiết tại `docs/tdq/reports/2026-10-16-1245-hoc-hoi-andrej-karpathy-skills.html`, trực quan, có bằng chứng thực tế, bảng so sánh đối sánh, và lộ trình đề xuất cải tiến khả thi (chưa can thiệp sửa code hệ thống ở lượt này).
- **Phạm vi dự kiến**:
  - Khảo sát mã nguồn và tài liệu của `C:\Users\admin\Documents\andrej-karpathy-skills` (`README.md`, `CLAUDE.md`, `CURSOR.md`, `EXAMPLES.md`, `skills/karpathy-guidelines/SKILL.md`, `.cursor/rules/karpathy-guidelines.mdc`).
  - Khảo sát các thành phần tương ứng của TDQ Workflow: `skills/tdq-build/references/rules/`, `skills/tdq-conventions/references/clean-code.md`, `skills/tdq-conventions/references/soul.md`, cơ chế kiểm soát chất lượng TDD, cách thức tương tác người dùng.
  - Xây dựng file HTML Report hoàn chỉnh, tự chứa (standalone), thiết kế UX hiện đại, có biểu đồ/bảng so sánh và chứng cứ trích dẫn cụ thể.
- **Điểm chưa rõ**:
  - Người dùng đã chốt rõ: Output là báo cáo HTML chi tiết có chứng cứ, và CHƯA implement thay đổi mã nguồn ở turn này.

## Hiểu & kiến thức

### Năng lực dùng được

Phân vân → DÙNG. Kiểm kê ngày 2026-10-16: 9 skill trên đĩa, cộng skill built-in trong context. Không xoá bảng này kể cả khi không có dòng DÙNG nào.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| Agent | built-in | DÙNG | Fan-out 2 subagent chạy ngầm phân tích đa chiều về triết lý và kiến trúc UX |
| tdq-intake | plugin:tdq-workflow | NỀN | mở request, phỏng vấn và chuyển phase |
| tdq-spec | plugin:tdq-workflow | NỀN | lập đặc tả kỹ thuật cho báo cáo HTML Report |
| tdq-plan | plugin:tdq-workflow | NỀN | lập kế hoạch phân tách task thiết kế HTML Report |
| tdq-build | plugin:tdq-workflow | NỀN | thực thi dựng file HTML Report và kiểm định QC |
| tdq-conventions | plugin:tdq-workflow | NỀN | quy tắc workflow, ngôn ngữ 3 tầng |
| tdq-status | plugin:tdq-workflow | NỀN | kiểm tra trạng thái tiến độ |
| tdq-lean | plugin:tdq-workflow | NỀN | kiểm tra tính tinh gọn của tài liệu |
| tdq-setup | plugin:tdq-workflow | NỀN | kiểm tra LSP và môi trường |
| tdq-check-status | plugin:tdq-workflow | NỀN | phục hồi phiên khi có sự cố |
| Đã xét 15 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

### Tổng hợp phân tích chuyên sâu từ 2 Sub-agent

#### 1. Khảo sát dự án Andrej Karpathy Skills
- **Cơ chế đóng gói**: Single file `CLAUDE.md` (66 dòng), `.cursor/rules/karpathy-guidelines.mdc`, Claude Code Plugin marketplace (`.claude-plugin/plugin.json`), và `EXAMPLES.md` (523 dòng đối chứng thực tế).
- **Token Carry Cost**: Cực kỳ thấp (~500 - 600 tokens), tỷ suất đòn bẩy ngữ cảnh rất cao.
- **4 Nguyên lý cốt lõi đánh trúng tâm lý học LLM**:
  1. *Think Before Coding*: Tuyên bố giả định rõ ràng, nêu các cách hiểu khác nhau kèm ước lượng công sức, chủ động phản biện (push back), dừng lại hỏi khi bối rối.
  2. *Simplicity First*: Không trừu tượng hóa cho code dùng 1 lần (Single-use), không tính năng đầu cơ viễn vông, viết 200 dòng rút về 50 dòng, Senior Engineer Test.
  3. *Surgical Changes*: Chỉ chạm vào chỗ bắt buộc (Touch only what you must), không refactor dạo (drive-by refactoring), không đổi style lân cận, chỉ dọn rác do mình tạo ra, Line-level traceability test.
  4. *Goal-Driven Execution*: Biến mệnh lệnh thành mục tiêu kiểm chứng được (Verifiable Goals), tái hiện test đỏ trước khi fix bug, trao quyền cho LLM tự lặp (looping) đến khi đạt kết quả.

#### 2. Đối chiếu với TDQ Workflow
- **Điểm TDQ vượt trội**:
  - Cưỡng chế tất định bằng phần mềm (Deterministic Enforcement qua Hook Python: `edit_gate`, `search_gate`, `stop_gate`, `session_start`).
  - Định lượng hóa ranh giới khách quan (Cyclomatic ≤ 10, Cognitive ≤ 15, trần ký tự output, thang 7 bậc).
  - Phòng thủ chống gian lận AI (`ANTI-1` chống test đỏ ảo, `ANTI-2` chống assertion rỗng, `ANTI-6` giới hạn vùng file).
  - Bộ tìm kiếm 3 tầng chuẩn mực (LSP -> graphify -> grep).
- **Điểm TDQ còn cồng kềnh & ma sát nhận thức (Cognitive Friction)**:
  - Gánh nặng thuế giao thức (Protocol Tax) và carry-cost (~90k tokens tài liệu).
  - Menu phỏng vấn ISO cứng nhắc, chưa chủ động phản biện kiến trúc (Push Back) tự nhiên như Karpathy.
  - Xung đột ngầm giữa SOLID và Simplicity (dễ bị bẫy đẻ thêm Interface/Abstract Class cho use case đơn lẻ).
  - Thiếu kỷ luật phẫu thuật ở cấp độ dòng code (Line-level Surgical Discipline): trong file được chạm, agent vẫn có thể tiện tay format lại code xung quanh.

#### 3. Mô hình đề xuất: "Tâm thức Karpathy trong Bộ giáp TDQ" (Hybrid Architecture)
- Kết hợp hoàn hảo: Lớp vỏ ngoài là Bộ giáp kỷ luật thép của TDQ (Hooks, State, TDD, Git Sandbox) bảo vệ an toàn tuyệt đối; Lớp nhân bên trong là Tâm thức tinh gọn của Karpathy (Think, Simplicity, Surgical, Goal-driven) định hình tư duy thanh thoát cho Agent.

### Phạm vi đã chốt

- **Trong phạm vi (In-scope)**:
  1. Xây dựng Báo cáo HTML Report chuyên sâu, độc lập (Standalone Single-File HTML) tại `docs/tdq/reports/2026-10-16-1245-hoc-hoi-andrej-karpathy-skills.html`.
  2. Báo cáo tích hợp đầy đủ 6 Section lớn:
     - Header & KPI Summary Cards (Token cost, Cognitive load, Safety metrics).
     - Section 1: Executive Comparison Matrix & Radar Chart (Đối chiếu 6 trục năng lực).
     - Section 2: Token Economics & Carry-Cost Waterfall Chart (Thác nước chi phí ngữ cảnh).
     - Section 3: LLM Psychology: 4 Karpathy Pillars vs. TDQ Guards (Bảng đối sánh trực quan kèm code đối chứng WRONG/RIGHT từ `EXAMPLES.md`).
     - Section 4: Cognitive Friction Analysis & Real Workflow Bottlenecks (Bản đồ ma sát nhận thức trong pipeline TDQ).
     - Section 5: The Hybrid Architecture Proposal ("Tâm thức Karpathy trong Bộ giáp TDQ").
     - Section 6: Actionable Implementation Roadmap (5 đề xuất nâng cấp cụ thể cho TDQ v0.71+).
  3. Giao diện hiện đại, responsive, hỗ trợ Dark/Light mode toggle, biểu đồ inline SVG, không phụ thuộc internet/CDN.
  4. TUYỆT ĐỐI CHƯA can thiệp sửa đổi mã nguồn hoặc rule của TDQ Workflow ở request này (theo đúng yêu cầu của người dùng).
- **Ngoài phạm vi (Out-of-scope)**:
  - Chưa áp dụng các thay đổi mã nguồn vào `skills/` hay `hooks/` ở lượt này.
- **Mức QC đã chốt**: `ultra` (DoD + unit test/lint + kiểm tra độc lập và kiểm tra runtime render).

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Research web | BỎ | Hai subagent đã khảo sát toàn diện mã nguồn nội bộ của cả 2 dự án |
| Interview | CÓ | Đã hoàn thành vòng 1 chốt các lựa chọn 1a 2a 3c |
| QC độc lập | CÓ | Áp dụng mức QC `ultra` theo yêu cầu của người dùng |

## Hỏi đáp

### Vòng 1 (2026-10-16 12:50)

1. **Phạm vi phân tích và chiều sâu của HTML Report**:
   - A (đề xuất): Toàn diện cả 4 khía cạnh (Triết lý cốt lõi, Phân tích Token Economics & Agentic UX, Đối chiếu ma trận 1-1 có code WRONG/RIGHT, và Đề xuất 5 tính năng nâng cấp cụ thể cho TDQ).
   - B: Báo cáo tóm tắt tập trung chủ yếu vào so sánh triết lý và danh sách đề xuất ngắn gọn.
   - **Người dùng chọn:** `1a`
2. **Thiết kế & Tính năng giao diện HTML Report**:
   - A (đề xuất): Standalone Dashboard hiện đại (Dark/Light mode toggle, Navigation Tabs tương tác, biểu đồ Radar và Waterfall bằng SVG, bảng so sánh đối chứng trực quan, không phụ thuộc thư viện ngoài).
   - B: Báo cáo HTML trang phẳng đơn giản dạng văn bản đọc tuần tự.
   - **Người dùng chọn:** `2a`
3. **Mức QC (chất lượng kiểm định cho request này)**:
   - A: `full`
   - B (đề xuất): `lite` — DoD + kiểm tra cấu trúc render, link nội bộ và dung lượng file HTML.
   - C: `ultra`
   - **Người dùng chọn:** `3c` (`ultra`)
