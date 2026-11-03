# BRIEF — Sinh Master Map thực tế và nâng cấp README chuyên nghiệp
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay vậy hãy phân tích và sinh lại Mastermap và handle lại readme để mang tính chất đọc cảm giác wow hơn, xịn và chuyên nghiệp hơn, đồng thời bổ sung hướng dẫn setup và install dependency

Mục tiêu:
1. Phân tích toàn diện kiến trúc thực tế của `TDQ-Workflow` (các tầng Skills, CLI Scripts, Hooks, Search 3-Tier, Archify Personal BA & Master Map, DevTools MCP, Team/Worktree Mode) và xuất bản bộ **Master Map** chính thức tại `docs/architecture/` (`index.html` + các trang biểu đồ góc nhìn chi tiết + `manifest.json` đồng bộ dấu vân tay mã nguồn).
2. Tái thiết kế và viết lại `README.md` ở gốc dự án mang phong cách ấn tượng ("wow"), chuyên nghiệp, trực quan, nêu bật giá trị cốt lõi (6 trụ cột bất biến, Tam Giác Khảo Sát 3 Chiều, Personal BA với Archify, UI/UX 5-Layer Audit), kèm hướng dẫn đầy đủ cách cài đặt dependencies (Python >= 3.10, Node.js >= 18, `agent-lsp`, Language Servers, `graphify`, `archify`, Chrome DevTools MCP) và lệnh tự động cấu hình `tdq_setup.py`.

Phạm vi dự kiến:
- Bộ mô hình kiến trúc Master Map của `TDQ-Workflow` và đầu ra HTML/manifest tại `docs/architecture/`.
- Tệp `README.md` tại gốc dự án (kiểm tra giới hạn dòng R6 ≤ 500 dòng của `doc_lint.py` và các bài kiểm liên quan tới `README.md`).

Điểm cần làm rõ (sẽ xác nhận ở bước phân tích):
- Ngôn ngữ trình bày của `README.md` (tiếng Việt chuyên nghiệp kết hợp thuật ngữ kỹ thuật chuẩn, hay song ngữ Việt–Anh).
- Các góc nhìn (views) chi tiết trong Master Map (`overview`, `lifecycle-pipeline`, `search-and-archify`, `hooks-and-gates`).

## Hiểu & kiến thức

### Năng lực dùng được

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | Mở và khảo sát request |
| tdq-spec | plugin:tdq-workflow | NỀN | Đặc tả cấu trúc Master Map và README.md |
| tdq-plan | plugin:tdq-workflow | NỀN | Lập kế hoạch từng bước thực thi |
| tdq-build | plugin:tdq-workflow | NỀN | Xây dựng, render Master Map và QC |
| tdq-conventions | plugin:tdq-workflow | NỀN | Quy tắc chung, state, approval |
| tdq-setup | plugin:tdq-workflow | DÙNG | Đối chiếu chính xác 8 bậc cài đặt và tự phục hồi dependency cho phần hướng dẫn trong README.md |
| tdq-browser-test | plugin:tdq-workflow | DÙNG | Kiểm chứng giao diện hiển thị của Master Map (`docs/architecture/index.html` và các trang con) trên Chrome DevTools MCP |
| frontend-design | built-in | DÙNG | Thiết kế giao diện portal `docs/architecture/index.html` của Master Map chuyên nghiệp, hiện đại |
| Đã xét 21 skill khác | plugin/built-in | KHÔNG | khác lĩnh vực |

### Triangulation Code Exploration (Khảo sát 3 chiều)

| Vùng file chạm | Phát hiện qua lớp nào | Tác động & quan hệ |
|---|---|---|
| `README.md` | Grep + `test_docs_consistency.py` | Phải giữ đủ 4 host (`Claude Code`, `Codex`, `OpenCode`, `Antigravity`) kèm đúng câu lệnh cài đặt, giữ đúng bộ đếm `` `skills/` (11) ``, `` `agents/` (6) ``, `` `hooks/` (13) ``, không chứa từ khóa bundle cũ (`portable_claude`, `antigravity_portable`...), và tổng số dòng ≤ 500 (luật R6 của `doc_lint.py`). |
| `scripts/tdq_archify.py` (`_generate_index_html`) | LSP + Read | Nâng cấp giao diện trang chủ Master Map (`index.html`) sang thiết kế Dashboard/Portal hiện đại, giữ nguyên các chuỗi dữ liệu kiểm thử (`Evidence Kind:`, `Revision:`, `Coverage:`, `Views Inventory`, `View Diagram`). |
| `docs/architecture/` & `docs/tdq/models/master.model.json` | Read + `sync_master` | Xây dựng mô hình kiến trúc thực tế của toàn bộ `TDQ-Workflow` với các góc nhìn chuyên sâu (`overview`, `pipeline-lifecycle`, `search-and-archify`, `hooks-and-gates`) và xuất bản qua `tdq_archify.py sync-master`. |
| `scripts/tdq_setup.py`, `scripts/tdq_lsp.py`, `scripts/tdq_devtool_mcp.py` | LSP + Graphify god-nodes | Nguồn đối chiếu chuẩn xác cho mục "Setup & Install Dependencies" trong `README.md` (Python >= 3.10, Node >= 18, `agent-lsp`, Language Servers, `graphify`, `archify`, Chrome CDP 9222). |

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| analyze | CÓ | Khảo sát toàn bộ ràng buộc kiểm thử trên `README.md` và cấu trúc `sync-master` |
| spec | CÓ | Đặc tả cấu trúc 4 góc nhìn Master Map và bố cục `README.md` chuyên nghiệp |
| plan | CÓ | Chia task dựng model Master Map, nâng cấp portal `index.html`, viết lại `README.md` và kiểm thử |
| implement | CÓ | Thực thi sinh Master Map thật, cập nhật `README.md` và kiểm tra trên trình duyệt |
| qc | CÓ | Kiểm chứng toàn diện theo mức QC người dùng chọn |
| report | CÓ | Báo cáo nghiệm thu và hỏi commit |

## Hỏi đáp

### 1. Bộ Master Map (`docs/architecture/`)
- Người dùng chọn **1a**: Portal Đa Góc Nhìn (4 Views: `overview`, `pipeline-lifecycle`, `search-and-archify`, `hooks-and-gates`) + nâng cấp giao diện trang chủ `docs/architecture/index.html` sang chuẩn Dashboard chuyên nghiệp.

### 2. Phong cách và nội dung `README.md`
- Người dùng chọn **2a**: Phong cách Flagship Open-Source (Tiếng Việt chuyên sâu + Thuật ngữ chuẩn), có hệ thống huy hiệu, tuyên ngôn giá trị, kiến trúc 6 trụ cột, liên kết thẳng tới Master Map, cẩm nang Setup & Install Dependencies đầy đủ từ A–Z (`tdq_setup.py`, Python, Node.js, `agent-lsp`, Language Servers, `graphify`, `archify`, Chrome DevTools MCP) và cài đặt đa host (`Claude Code`, `Codex`, `OpenCode`, `Antigravity`).

### 3. Mức QC (step 5c)
- Người dùng chọn **3a**: Mức `full` (DoD + trọn unit test toàn repo + hồi quy vùng chạm + ràng buộc kiến trúc + clean code). Đã ghi nhận `muc_qc=full` vào `state.json`.
