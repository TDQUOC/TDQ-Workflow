# SPEC — Điều tra và khắc phục lỗi LSP search gate và tdq_team clean

Ngày: 2026-10-15 · Bản: 1.0 · Brief: ../brief/2026-10-15-0958-dieu-tra-loi-lsp-search-team-clean.md · Lane: full
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

- **Mục tiêu**: Khắc phục triệt để 3 rào cản lớn mà agent thường xuyên gặp phải khi thực thi công việc trong các dự án dùng TDQ Workflow:
  1. Loại bỏ lỗi CLI `exit 2 unrecognized arguments: <task>` khi agent gọi `tdq_team.py clean <task>`, đồng bộ quy trình dọn dẹp worktree trong tài liệu hướng dẫn mode subagent.
  2. Nâng cấp hook `search_gate.py` và module `search_rules.py` để tự động phát hiện ngôn ngữ dự án theo `cwd`, thay thế chuỗi ví dụ gán cứng `e.g. python` bằng `language_id` thực tế, và gợi ý công cụ `mcp__lsp__list_symbols` khi agent tìm kiếm trong phạm vi một file cụ thể.
  3. Bổ sung chỉ dẫn cơ học rõ ràng cho việc khởi tạo và sử dụng `mcp__lsp__*` trong khối ghim `KHOI_HUONG_DAN` (`CLAUDE.md`) và tài liệu tìm kiếm 3 tầng, giúp agent hiểu rõ điều kiện tiên quyết gọi `start_lsp` đầu phiên, bước `open_document` đối với TypeScript/JS để tránh bẫy tsserver "No Project", và các công cụ tra cứu symbol thay vì dùng Grep đoán mò.
- **Trong phạm vi**:
  1. *Module CLI `tdq_team.py`*:
     - Cập nhật hàm `build_parser()` để lệnh con `clean` nhận tham số tùy chọn `task` (`nargs="?", default=None`).
     - Cập nhật hàm `lenh_don()`: nếu có truyền `task`, kiểm tra worktree của task tương ứng; nếu worktree còn tồn tại thì dọn dẹp an toàn; nếu worktree đã được tự động dọn bởi `merge` trước đó thì in thông báo `Worktree for <task> already cleaned.` và trả về `0` (thành công) thay vì báo lỗi cú pháp exit 2; nếu không truyền `task` thì dọn dẹp toàn bộ worktree của slug hiện tại như cũ.
     - Cập nhật dòng 91 trong `skills/tdq-build/SKILL.md` và `skills/tdq-build/references/team-mode.md` làm rõ rằng `merge` đã tự động dọn dẹp worktree của task, và cuối wave thì chạy `sweep --clean`.
  2. *Module Hook & Luật tìm kiếm `search_rules.py` & `search_gate.py`*:
     - Bổ sung hàm phát hiện ngôn ngữ dự án `do_ngon_ngu_du_an(cwd)` (đọc từ `.tdq-lsp-module.json` hoặc nhận diện file mốc `package.json`/`tsconfig.json` -> `typescript`, `pyproject.toml`/`requirements.txt` -> `python`, `go.mod` -> `go`, `Cargo.toml` -> `rust`).
     - Tinh chỉnh hàm `loi_nhac()` trong `scripts/search_rules.py`: truyền ngôn ngữ dự án vào để tạo câu nhắc chính xác với `language_id` thực tế (ví dụ: `language_id = "typescript"` cho dự án TS), loại bỏ chuỗi gán cứng `e.g. python`.
     - Trong `quyet_dinh()` / `search_gate.py`: nếu lệnh Grep có chỉ định đường dẫn file cụ thể trong `path`, bổ sung gợi ý sử dụng `mcp__lsp__list_symbols(file_path="...")` để xem danh sách hàm/class thay vì grep regex.
  3. *Instruction `KHOI_HUONG_DAN` & Tài liệu*:
     - Cập nhật `KHOI_HUONG_DAN` trong `scripts/tdq_setup.py` và ghim lại vào `~/.claude/CLAUDE.md`: hướng dẫn quy trình 3 bước (gọi `start_lsp` đầu phiên kèm `language_id`, với TS/JS mở 1 file bằng `open_document`, dùng `list_symbols` xem cấu trúc file, `find_symbol` tìm symbol workspace, `find_references` tìm nơi gọi) và nhắc rõ việc gọi LSP sẽ mở khóa 10 lượt grep tiếp theo.
     - Cập nhật `skills/tdq-setup/references/uu-tien-tim-kiem.md` đồng bộ hướng dẫn.
  4. *Bộ unit test*:
     - Bổ sung test cho lệnh `tdq_team.py clean <task>` (cả trường hợp còn worktree và trường hợp đã được merge dọn sạch) và `tdq_team.py clean` không tham số.
     - Bổ sung test cho câu thông báo tự động theo ngôn ngữ của `search_rules.py` và gợi ý `list_symbols` khi grep trong file cụ thể.
- **NGOÀI phạm vi**:
  - Không thay đổi thuật toán nhận diện regex đoán mò `doan_mo` hay cơ chế đếm cửa sổ mở khóa 10 lượt grep của `search_gate.py`.
  - Không thay đổi hành vi của các lệnh con khác trong `tdq_team.py` (`open`, `check`, `merge`, `sweep`, `audit`).

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | Bài toán hoàn toàn nằm trong mã nguồn Python (`tdq_team.py`, `search_gate.py`, `search_rules.py`) và tài liệu instruction của TDQ-Workflow |
| Interview | CÓ | Đã hoàn thành 1 vòng phỏng vấn chốt đủ 4 câu hỏi (`1a 2a 3a 4b`) |
| QC độc lập (agent) | BỎ | Áp dụng mức QC `lite` đã chọn |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Lệnh `tdq_team.py clean [task]` hỗ trợ tham số task tùy chọn và idempotent | `scripts/tdq_team.py` | Lệnh `clean <task>` dọn worktree của task nếu còn, trả về `0` và in thông báo thân thiện nếu đã dọn trước đó; lệnh `clean` không tham số dọn toàn bộ slug như cũ |
| 2 | Hook `search_gate.py` và `search_rules.py` tự động phát hiện ngôn ngữ dự án và gợi ý `list_symbols` | `scripts/search_rules.py`, `hooks/scripts/search_gate.py` | Câu nhắc chặn không còn gán cứng `e.g. python`, in đúng `language_id` theo project hiện tại, và gợi ý `list_symbols` khi grep trong file cụ thể |
| 3 | Hướng dẫn LSP rõ ràng trong `KHOI_HUONG_DAN`, `CLAUDE.md` và tài liệu tìm kiếm | `scripts/tdq_setup.py`, `skills/tdq-setup/references/uu-tien-tim-kiem.md`, `skills/tdq-build/SKILL.md` | `KHOI_HUONG_DAN` ghi rõ 3 bước gọi LSP và mở khóa grep, `SKILL.md` chuẩn hóa quy trình dọn dẹp sau merge |

## 2b. Ranh giới module

Xác định bằng ngữ nghĩa phụ thuộc qua LSP (`scripts/tdq_team.py` và `scripts/search_rules.py` là 2 module độc lập không import lẫn nhau; instruction và hook nằm ở tầng riêng):

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| `team-clean` | `scripts/tdq_team.py` | Không | 1 |
| `search-rules-lang` | `scripts/search_rules.py`, `hooks/scripts/search_gate.py` | Không | 2 |
| `search-instruction` | `scripts/tdq_setup.py`, `skills/tdq-setup/references/uu-tien-tim-kiem.md`, `skills/tdq-build/SKILL.md` | Không | 3 |

## 3. Cách tiếp cận & lý do

- **Chọn**:
  1. *Lệnh `clean [task]` linh hoạt*: Cho phép `clean` nhận tham số `task` tùy chọn (`nargs="?"`). Nếu agent truyền `clean T1.1`: kiểm tra worktree của `T1.1`; nếu còn thì dọn; nếu đã được dọn trước đó bởi `merge` thì in `Worktree for T1.1 already cleaned.` và trả về `0`. Giúp agent không bao giờ bị gãy turn vì lỗi cú pháp CLI.
  2. *Phát hiện ngôn ngữ động cho câu nhắc tìm kiếm*: Tận dụng danh sách file mốc dự án đã có trong `tdq_lsp.py` / `lsp_module.py` (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`) để xác định ngôn ngữ chính của project hiện tại và đưa vào `loi_nhac()`.
  3. *Hướng dẫn LSP 3 bước cơ học trong `KHOI_HUONG_DAN`*: Đưa quy trình rõ ràng vào instruction ghim ở đầu ngữ cảnh của Claude Code để model nắm được cách khởi tạo `start_lsp` ngay từ đầu phiên, bước `open_document` đối với TypeScript/JS để tránh bẫy "No Project", và dùng đúng công cụ tra cứu thay vì grep đoán mò.
- **Vì**:
  - Giải quyết đúng nguyên nhân gốc rễ ở cả 2 đầu: vừa làm cho công cụ thân thiện, có khả năng dung thứ lỗi (`fault-tolerant`), vừa cung cấp instruction đầy đủ, chính xác theo ngữ cảnh ngôn ngữ của project đang làm việc.
- **Đã loại**:
  - *Chỉ sửa câu chữ trong tài liệu mà không sửa parser của `tdq_team.py clean`*: Loại vì LLM đôi khi vẫn có thể suy luận gọi `clean <task>`, việc để CLI văng lỗi exit 2 làm hỏng trải nghiệm tự động hóa của mode subagent.
  - *Bỏ chặn grep đoán mò*: Loại vì luật chặn grep đoán mò là hàng rào bắt buộc đã được người dùng chốt từ 2026-10-03 để buộc model phải tư duy qua tầng khái niệm trước khi quét code.

## 3b. Năng lực & công cụ

Chép từ brief mục `### Năng lực dùng được`. Phân vân → DÙNG.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | tiếp nhận, phân tích yêu cầu và phỏng vấn chốt phạm vi |
| tdq-spec | plugin:tdq-workflow | NỀN | viết đặc tả kỹ thuật và kiểm tra R8, R11, R14 |
| tdq-plan | plugin:tdq-workflow | NỀN | lập kế hoạch triển khai theo từng task TDD |
| tdq-build | plugin:tdq-workflow | NỀN | thực thi TDD đỏ -> xanh, chạy QC mức `lite` và lập báo cáo |
| tdq-conventions | plugin:tdq-workflow | NỀN | quy tắc workflow, ngôn ngữ 3 tầng và hợp đồng tài liệu |
| tdq-status | plugin:tdq-workflow | NỀN | kiểm tra trạng thái |
| tdq-lean | plugin:tdq-workflow | NỀN | áp dụng bậc thang build-less-than-asked (`TDQ:GON`) |
| tdq-setup | plugin:tdq-workflow | NỀN | kiểm tra môi trường công cụ và LSP |
| tdq-check-status | plugin:tdq-workflow | NỀN | phục hồi phiên khi cần |
| Đã xét 12 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- **Log service bật mặc định**: Ghi log tiến độ kèm timestamp ISO ra `stderr`, tắt hoàn toàn qua `TDQ_LOG=0`.
- **Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật**.
- **Mỗi thành phần có unit test riêng, chạy được bằng một lệnh**.
- **Code viết ra bám 5 nguyên tắc SOLID** theo `skills/tdq-conventions/references/clean-code.md`, và bám rule ngôn ngữ trong `skills/tdq-build/references/rules/` (cyclomatic ≤ 10, cognitive ≤ 15).

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md` — chỉ những dòng việc này chạm tới):
- `skills/` chỉ được **nhắc tên lệnh** của `scripts/`, cấm chép nội dung script vào skill — việc này chạm ở `skills/tdq-build/SKILL.md` và `skills/tdq-setup/references/uu-tien-tim-kiem.md`.
- 2026-08-22: ngôn ngữ chia 3 tầng — luật trong `skills/`, `agents/`, chú thích/docstring của `hooks/` + `scripts/` và chuỗi máy in ra đều viết TIẾNG ANH cố định (không bảng tra i18n); tài liệu sinh cho user và lời thoại viết theo `doc_lang` — việc này chạm ở `scripts/tdq_team.py`, `scripts/search_rules.py`, `hooks/scripts/search_gate.py` và `skills/tdq-setup/references/uu-tien-tim-kiem.md`.
- 2026-10-03: **thêm một điểm chặn** — `hooks/scripts/search_gate.py` trả `deny` (mã `TDQ:SEARCH`) cho một lần tìm code đi tắt tầng khái niệm — việc này chạm ở `hooks/scripts/search_gate.py` và `scripts/search_rules.py`.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Cải tiến câu nhắc của `search_gate.py` làm lệch các test case hiện có của bộ test `test_search_rules.py` và `test_search_gate.py` | Làm đỏ các bài test kiểm tra chuỗi thông báo chặn | Cập nhật hàm sinh câu nhắc có tham số ngôn ngữ với giá trị mặc định tương thích ngược và cập nhật đồng bộ các bài test |
| Lệnh `clean <task>` xóa nhầm worktree khi task chưa hoàn thành | Mất mã nguồn đang làm việc dở dang của task | Sử dụng hàm kiểm tra điều kiện an toàn `_ly_do_chan` có sẵn trong `tdq_team.py` trước khi thực hiện xóa |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS | Đo trước | Dự phòng nếu trượt |
|---|---|---|---|---|
| Q1 | Lệnh `tdq_team.py clean` hỗ trợ tham số task tùy chọn và xử lý an toàn khi đã dọn | Gọi `tdq_team.py clean <task>` trên task đã merge/dọn trả về exit code `0` và in thông báo `already cleaned`; gọi trên task có worktree sạch thì dọn dẹp thành công; gọi không tham số thì dọn toàn bộ slug | Đo trước: `clean T1.1` trả về exit code `2` (lỗi `unrecognized arguments: T1.1`), sau khi sửa trả về exit code `0` (biên 2 mã lỗi) | Nếu worktree chưa merge thì từ chối xóa và trả về exit code `1` có thông báo lý do rõ ràng |
| Q2 | Hook `search_gate.py` và `search_rules.py` tự động phát hiện ngôn ngữ dự án và gợi ý `list_symbols` | Câu thông báo chặn `[TDQ:SEARCH]` in đúng `language_id` thực tế của dự án (`typescript`, `python`, `go`, `rust`), không còn in chuỗi cứng `e.g. python`; gợi ý `mcp__lsp__list_symbols` khi lệnh grep có đường dẫn file cụ thể | Đo trước: 100% câu nhắc hiện tại đều in cứng `e.g. python`, sau khi sửa 0% xuất hiện `e.g. python` khi project là TypeScript/Go/Rust (biên 100%) | Nếu không xác định được ngôn ngữ của project thì in câu nhắc tổng quát không gán cứng tên ngôn ngữ nào |
| Q3 | Khối ghim `KHOI_HUONG_DAN`, `CLAUDE.md` và tài liệu hướng dẫn 3 bước gọi LSP | `KHOI_HUONG_DAN` ghi rõ 3 bước gọi LSP (`start_lsp` đầu phiên, `open_document` cho TS/JS, và tra cứu chính xác), giữ độ dài ≤ 25 dòng; `SKILL.md` và `uu-tien-tim-kiem.md` được cập nhật đồng bộ | Đo trước: `KHOI_HUONG_DAN` hiện có 20 dòng, sau khi bổ sung dự kiến ~24 dòng (biên 1 dòng dưới trần 25 dòng) | Tối ưu hóa câu chữ ngắn gọn để đảm bảo không vượt trần 25 dòng |
| Q4 | Hợp đồng tài liệu, chuẩn ngôn ngữ 3 tầng và khóa ngân sách token | Các file tài liệu và mã nguồn thay đổi đạt 0 vi phạm với `doc_lint.py`, `i18n_check.py` và khóa ngân sách `token_budget.py` (mọi file reference ≤ 3500 tokens) | `nhanh-request.md` và `uu-tien-tim-kiem.md` đều dưới 1500 tokens (biên > 2,000 tokens so với trần 3,500 tokens) | Chạy `doc_index.py` và `token_budget.py` cập nhật khóa ngay khi sửa |

**DoD**:
1. `scripts/tdq_team.py` hỗ trợ `clean [task]` an toàn, đạt chuẩn SOLID & độ phức tạp hàm (cyclomatic ≤ 10, cognitive ≤ 15).
2. `scripts/search_rules.py` và `hooks/scripts/search_gate.py` tự động nhận diện ngôn ngữ dự án và tạo câu nhắc chính xác kèm gợi ý `list_symbols` cho file cụ thể.
3. `KHOI_HUONG_DAN` và tài liệu workflow được cập nhật hoàn chỉnh, đạt `doc_lint.py`, `i18n_check.py`, `token_budget.py --kiem` và vượt qua toàn bộ các bước kiểm tra QC mức `lite`.

## 7. Câu hỏi còn mở

(Rỗng — toàn bộ câu hỏi đã được chốt.)
