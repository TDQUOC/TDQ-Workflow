# Brief: Nghiên cứu phương án tích hợp Archify vào TDQ-Workflow

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

### Lời người dùng
> "okay bây giờ mở request phân tích nghiên cứu hướng bổ sung cái này vào tdq-workflow, vì tôi đang đánh giá thấy tdq-workflow đang thiếu ở mặt flow spec và kiến trúc doc hỗ trợ tối đa cho dev hiểu và nắm kiến trúc (kiểu personal Business analysis của mỗi task á) nên tôi muốn tra cứu và đề xuất phương án đưa archify vào tdq-workflow ở cả 2 pipeline để tdq-workflow có thể có flow BA trực quan, ngắn gọn dễ hiểu cho dev hơn trước khi viết code, và cũng để phân tích và dựng full lại kiến trúc của một project/ code base. Tôi hoàn toàn hỗ trợ mọi thứ, kể cả config endpoint cho archify nếu như achify ko thể tự dùng chung endpoint AI với claude code/codex, để tận dụng hết mức sức mạnh của archify để TDQ-workflow được hoàn thiện hơn và hỗ trợ dev hiểu và nắm cấu trúc hơn trước khi code"

### Đọc hiểu lần đầu

- **Mục tiêu cốt lõi:**
  1. Đưa Archify vào làm cánh tay đắc lực cho TDQ-Workflow ở cả 2 pipeline (`quick` và `full`), biến TDQ-Workflow thành công cụ hỗ trợ trực quan hóa kiến trúc và nghiệp vụ (vai trò như một "Personal Business Analyst" cho từng task).
  2. Cung cấp flow BA trực quan, ngắn gọn, dễ hiểu (bằng HTML tương tác) cho lập trình viên (đặc biệt là fresher/junior dev) nắm bắt luồng dữ liệu, ranh giới module, điều kiện rẽ nhánh trước khi viết mã.
  3. Hỗ trợ tái hiện và dựng toàn diện (full architecture/codebase map) cho một dự án hiện có.
  4. Xác định phương án cấu hình endpoint/AI model nếu Archify cần runtime LLM riêng biệt hoặc dùng chung với harness (Claude Code / Codex).

## Hiểu & kiến thức

### Năng lực dùng được (B0 Skill Inventory)

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `tdq-spec` | plugin:tdq-workflow | DÙNG | Tích hợp sinh sơ đồ luồng BA tương tác tại §2b & §2c |
| `tdq-intake` | plugin:tdq-workflow | DÙNG | Tích hợp sinh mini-workflow cho express pipeline |
| `tdq-plan` | plugin:tdq-workflow | DÙNG | Tham chiếu node/boundary kiến trúc khi lập WBS task |
| `tdq-setup` | plugin:tdq-workflow | DÙNG | Cài đặt và kiểm thử pre-flight cho Node.js & Archify CLI |
| `archify` | local/external (`C:\Users\admin\Documents\archify`) | DÙNG | Engine biên dịch hình học A*, 11 renderers và viewer HTML |
| `claude-api` | built-in | DÙNG | Thiết kế kiến trúc cấu hình AI endpoint độc lập/dùng chung |
| `dataviz` | built-in | KHÔNG | Archify đã có sẵn Pele 1.3.0 và hệ thống render nội bộ |
| `frontend-design` | built-in | KHÔNG | Viewer của Archify đã có CSS Midnight Console chuẩn |

### Bằng chứng mã nguồn & Khảo sát 3 chiều

| Vùng file chạm dự kiến | Phát hiện qua lớp nào | Tác động & Quan hệ |
|---|---|---|
| `skills/tdq-spec/SKILL.md` & `references/spec-template.md` | Grep / Đọc code | Nâng cấp §2c: sinh song song `spec/<slug>-preview.html` |
| `skills/tdq-intake/references/quick-lane.md` | Grep / Đọc code | Bổ sung tùy chọn BA preview nhẹ cho lane quick |
| `scripts/tdq_graphify.py` & `graphify-out/` | Grep / Đọc code | Đề xuất module Adapter chuyển `graph.json` $\rightarrow$ Archify |
| `scripts/tdq_archify.py` (Mới) | Thiết kế mới | CLI wrapper điều phối gọi `archify.mjs finalize` an toàn |
| `scripts/tdq_setup.py` & `skills/tdq-setup/` | Grep / Đọc code | Thêm bậc kiểm tra môi trường Node.js và gói Archify |
| `docs/tdq/` & `docs/architecture/` | Khảo sát | Vị trí lưu trữ các artifact kiến trúc (Master Map + Task Scopes) |

### Các quyết định kỹ thuật đã chốt (Settled Decisions)
1. **Mô hình tổ chức 2 tầng (Master Architecture + Task BA Scopes):**
   - **Tầng 1 (Toàn dự án):** Duy trì 1 file HTML tổng thể duy nhất tại `docs/architecture/index.html` (hoặc `graphify-out/ARCHITECTURE.html`), cập nhật theo trạng thái thực của codebase khi merge/hoàn tất feature hoặc chạy quét định kỳ.
   - **Tầng 2 (Từng task/feature):** Mỗi task sinh 1 file scoped HTML tại `docs/tdq/spec/<slug>-preview.html` đóng vai trò "Personal BA" để dev tập trung 100% vào đúng luồng cần code (các nút nghiệp vụ, điều kiện rẽ nhánh, lỗi, đối chiếu Trước vs Sau).
2. **Phạm vi 2 pipeline:**
   - Pipeline `full`: Bắt buộc sinh `<slug>-preview.html` tại phase `spec` để người dùng và dev duyệt trực quan trước khi viết code.
   - Pipeline `quick`: Sinh sơ đồ workflow tinh gọn (<10 nút) khi task chạm $\ge 2$ module hoặc tác vụ refactor/kiến trúc; với việc siêu nhỏ giữ nguyên sơ đồ text để bảo toàn nguyên tắc Lean.
3. **Cơ chế Endpoint AI:** Kiến trúc lai (Hybrid). Mặc định dùng Agent session hiện tại (Claude Code / Codex) đóng vai trò bộ não xuất JSON-IR; đồng thời bổ sung module cấu hình Endpoint AI độc lập (`ARCHIFY_AI_ENDPOINT` / API key) để kích hoạt chế độ "Autonomous Codebase Scanning" khi cần quét và dựng full kiến trúc dự án lớn.
4. **Trải nghiệm hiển thị:** Standalone HTML nguyên tử offline 100%, nhúng font Base64 và CSS/JS runtime, hỗ trợ lệnh `tdq_archify.py open` để mở nhanh trình duyệt mặc định.
5. **Mức QC:** `ultra` — kiểm định toàn diện DoD, đối soát tương thích 2 codebase và có agent reviewer độc lập thẩm định.

### Lộ trình (Route)

| Bước/Phase | CÓ-BỎ | Vì sao |
|---|---|---|
| `analyze` | CÓ | Hoàn tất phân tích 3 chiều, B0 và 2 vòng phỏng vấn |
| `spec` | CÓ | Lập bản đặc tả thiết kế kiến trúc chi tiết (RFC Blueprint & Integration Contract) |
| `plan` | CÓ | Lập kế hoạch phân rã task kiểm thử và thực thi chi tiết |
| `implement` | CÓ | Triển khai các thành phần theo plan đã duyệt |
| `qc` | CÓ | Kiểm thử độc lập mức `ultra` (DoD + test + audit) |
| `report` | CÓ | Đóng gói báo cáo nghiệm thu và ghi nhật ký phát hành |

## Hỏi đáp

### Vòng 1 — Phạm vi & Kỹ thuật
- Câu 1: Phạm vi hỗ trợ BA trực quan ở 2 pipeline $\rightarrow$ **Chọn 1a (Kiến trúc linh hoạt theo tải)**.
- Câu 2: Cơ chế Endpoint AI cho Archify $\rightarrow$ **Chọn 2a (Kiến trúc lai Hybrid)**.
- Câu 3: Trải nghiệm xem và tương tác của Dev $\rightarrow$ **Chọn 3a (Standalone HTML nguyên tử offline + CLI open)**.
- Câu 4: Mức QC cho request $\rightarrow$ **Chọn 4c (ultra)**.
- Câu 5: Ý kiến bổ sung $\rightarrow$ **Người dùng đặt câu hỏi về mô hình 1 file HTML tổng hợp cho cả project hay mỗi feature mỗi file**.

### Vòng 2 — Mô hình tổ chức File Kiến trúc
- Câu 1: Mô hình tổ chức file kiến trúc $\rightarrow$ **Chọn 1a (Đồng thuận mô hình 2 tầng: Master Map toàn dự án + Task Scope BA Flow cho từng feature)**.
- Câu 2: Ý kiến bổ sung $\rightarrow$ **Chọn 2a (Không, đã rõ ràng và thống nhất phương án — chuyển sang viết spec)**.
