# SPEC — Cập nhật đầy đủ các đề xuất kiến trúc tối ưu instruction và lazy load vào TDQ Workflow

Ngày: 2026-10-15 · Bản: 1.0 · Brief: ../brief/2026-10-15-1425-cap-nhat-full-de-xuat-instruction.md · Lane: full
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

- **Mục tiêu**: Hiện thực hóa toàn bộ 4 trụ cột kiến trúc từ Báo cáo Đề xuất `docs/kien-truc-instruction-lazy-load.md` vào mã nguồn và hệ thống tài liệu của TDQ Workflow, đồng thời trang bị cơ chế Neo Phục Hồi chống mất mát ngữ cảnh sau Compaction dài để các mô hình tier thấp hoạt động bền bỉ, chuẩn xác mà không làm cháy token.
- **Trong phạm vi**:
  1. *Bộ mã cấm cơ học tường minh (`ANTI-1` đến `ANTI-6`)*:
     - Tích hợp chuẩn hóa vào `skills/tdq-build/references/team-mode.md`, `agents/tdq-implementer.md`, `skills/tdq-build/references/qc.md`, `skills/tdq-plan/references/plan-template.md`.
  2. *Kim tự tháp 3 tầng & Thư viện Cookbooks thực chiến*:
     - Soạn thảo 2 Cookbooks thực chiến chất lượng cao: `skills/tdq-build/references/rules/cookbooks/python-cookbook.md` và `typescript-js-cookbook.md`.
     - Cập nhật `skills/tdq-build/references/rules/index.md` bổ sung đường dẫn nạp Cookbooks tầng 3 khi gặp lỗi bế tắc.
  3. *Hook-driven JIT Micro-injection & Chống mất ngữ cảnh sau Compaction*:
     - Nâng cấp `hooks/scripts/edit_gate.py`: Mớm 3 dòng quy tắc vàng khi sửa file `.py` hoặc `.ts` lần đầu trong phiên.
     - Nâng cấp `hooks/scripts/session_start.py`: Bổ sung xử lý khi `source == "compact"` để reset cờ đã nhắc và bơm Khối Neo Phục Hồi (Compact Recovery Anchor) ngắn gọn trỏ lại state, plan file và mã cấm cốt lõi.
     - Nâng cấp `hooks/scripts/prompt_context.py`: Tự động mớm khung kiểm định DoD khi bước vào phase `qc`.
  4. *Silent CLI & Externalized Logs*:
     - Nâng cấp `scripts/tdq_test.py`: Hỗ trợ cờ `--silent` ghi log chi tiết ra file đĩa, terminal chỉ in `≤ 2` dòng tóm tắt và lỗi chính.
  5. *Hệ thống kiểm thử tự động hóa*:
     - Bổ sung unit test toàn diện cho các cơ chế mới, bảo đảm đạt 100% PASS và tuân thủ ngân sách token.
- **NGOÀI phạm vi**:
  - Viết cookbooks cho 6 ngôn ngữ còn lại (Go, Rust, C#, C++, HTML, Bash) — sẽ triển khai ở các bản phát hành tiếp theo.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình chi tiết sau phỏng vấn`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | Phân tích nội bộ và RFC đã có sẵn đầy đủ |
| Interview | CÓ | Đã hoàn thành 1 vòng phỏng vấn chốt đủ 3 câu hỏi (`1a 2a 3a`) |
| QC độc lập (agent) | CÓ | Áp dụng mức QC `full` theo lựa chọn của người dùng |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Bộ mã cấm tường minh `ANTI-1`..`ANTI-6` kèm ví dụ đối chứng | `skills/tdq-build/references/team-mode.md`, `agents/tdq-implementer.md`, `skills/tdq-build/references/qc.md`, `skills/tdq-plan/references/plan-template.md` | Các file tài liệu mang đúng 6 mã cấm cơ học, đạt chuẩn lint |
| 2 | Bộ Cookbooks thực chiến Python và TypeScript/JS (Tầng 3) | `skills/tdq-build/references/rules/cookbooks/python-cookbook.md`, `typescript-js-cookbook.md`, `index.md` | 2 file cookbook chi tiết (> 100 dòng mỗi file) bao quát async, transaction, error handling, kiến trúc sạch; đạt tiêu chuẩn lint và ngân sách token |
| 3 | Cơ chế JIT Micro-injection và Neo Phục Hồi sau Compaction | `hooks/scripts/edit_gate.py`, `hooks/scripts/session_start.py`, `hooks/scripts/prompt_context.py` | `edit_gate` mớm 3 dòng quy tắc vàng khi sửa `.py`/`.ts` lần đầu; `session_start` bơm khối neo phục hồi khi `source == "compact"`; `prompt_context` mớm mẫu DoD ở phase `qc` |
| 4 | Chế độ Silent CLI xuất log thô ra đĩa | `scripts/tdq_test.py` | Lệnh `tdq_test.py --silent` ghi log chi tiết ra `docs/tdq/.tdq-test.log`, terminal chỉ in `≤ 2` dòng tóm tắt và lỗi chính |

## 2b. Ranh giới module

Xác định bằng ngữ nghĩa phụ thuộc qua LSP:

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| `anti-rules` | `skills/tdq-build/`, `agents/tdq-implementer.md`, `skills/tdq-plan/` | Không | 1 |
| `cookbooks` | `skills/tdq-build/references/rules/` | `anti-rules` | 2 |
| `jit-compact-hooks` | `hooks/scripts/edit_gate.py`, `session_start.py`, `prompt_context.py` | `cookbooks` | 3 |
| `silent-cli` | `scripts/tdq_test.py` | Không | 4 |

## 3. Cách tiếp cận & lý do

- **Chọn**:
  1. *Hiện thực hóa trọn vẹn 4 trụ cột kiến trúc*: Đưa các nguyên lý từ RFC vào vận hành thực tế (Mã cấm `ANTI`, Kim tự tháp 3 tầng, Hook JIT Injection, Silent CLI).
  2. *Bổ sung Cơ chế Neo Phục Hồi chống mất ngữ cảnh sau Compaction*: Giải quyết triệt để nỗi lo mất mát thông tin khi ngữ cảnh bị nén ở phiên dài.
- **Vì**:
  - Giúp mô hình nhỏ không bị "mù quy tắc", tuân thủ quy trình chuẩn xác mà không gây tốn kém token carry-cost.
- **Đã loại**:
  - *Viết trực tiếp toàn bộ nội dung cookbooks vào SKILL.md*: Loại vì sẽ làm phình to context tĩnh và đẩy nhanh chạm trần compaction.

## 3b. Năng lực & công cụ

Chép từ brief mục `### Năng lực dùng được`. Phân vân → DÙNG.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| Agent | built-in | DÙNG | Điều phối subagent khi chạy QC độc lập hoặc phân tích phức tạp |
| context_surface.py & skill_tokens.py | project | DÙNG | Đo lường dung lượng token sau khi thêm cookbooks |
| tdq-intake | plugin:tdq-workflow | NỀN | mở request, phỏng vấn và chuyển phase |
| tdq-spec | plugin:tdq-workflow | NỀN | lập đặc tả kỹ thuật và kiểm tra hợp đồng |
| tdq-plan | plugin:tdq-workflow | NỀN | lập kế hoạch phân tách task TDD |
| tdq-build | plugin:tdq-workflow | NỀN | thực thi TDD, chạy QC mức full và báo cáo |
| tdq-conventions | plugin:tdq-workflow | NỀN | quy tắc workflow, ngôn ngữ 3 tầng |
| tdq-status | plugin:tdq-workflow | NỀN | kiểm tra trạng thái tiến độ |
| tdq-lean | plugin:tdq-workflow | NỀN | bảo đảm không over-engineer |
| tdq-setup | plugin:tdq-workflow | NỀN | kiểm tra LSP và môi trường |
| tdq-check-status | plugin:tdq-workflow | NỀN | phục hồi phiên khi có sự cố |
| Đã xét 12 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- **Log service bật mặc định**: Ghi log tiến độ kèm timestamp ISO ra `stderr`, tắt qua `TDQ_LOG=0`.
- **Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật**.
- **Mỗi thành phần có unit test riêng, chạy được bằng một lệnh**.
- **Code viết ra bám 5 nguyên tắc SOLID** theo `skills/tdq-conventions/references/clean-code.md`, và bám rule ngôn ngữ trong `skills/tdq-build/references/rules/` (cyclomatic ≤ 10, cognitive ≤ 15).

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md` — chỉ những dòng việc này chạm tới):
- 2026-09-17: nội hoá luật "build less than asked" — thân luật ở `skills/tdq-build/references/rules/chung.md`, đọc–lọc bằng `hooks/scripts/luat_gon.py` theo `muc_gat`. Ba kênh bơm: `SessionStart` và `SubagentStart` mang thân luật, `UserPromptSubmit` chỉ một dòng con trỏ ở phase `implement` — việc này chạm ở `hooks/scripts/session_start.py`.
- 2026-08-22: ngôn ngữ chia 3 tầng — luật trong `skills/`, `agents/`, chú thích/docstring của `hooks/` + `scripts/` và chuỗi máy in ra đều viết TIẾNG ANH cố định — việc này chạm ở `hooks/scripts/edit_gate.py`, `session_start.py`, `scripts/tdq_test.py`.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Mớm JIT micro-rules trong `edit_gate.py` có thể làm chậm thao tác sửa file nếu đọc tệp chậm | Gây giật lag mỗi khi gọi lệnh `Edit` | Sử dụng bộ nhớ đệm cache hoặc chuỗi hằng số micro-rules ngắn gọn định sẵn trong code hook; không gọi I/O đọc tệp nặng |
| Thêm file Cookbooks mới có thể làm lệch chỉ mục token budget | Làm đỏ lệnh kiểm tra ngân sách token ở CI | Chạy script cập nhật khóa `token_budget.py` ngay sau khi tạo các file cookbook |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS | Đo trước | Dự phòng nếu trượt |
|---|---|---|---|---|
| Q1 | Bộ mã cấm tường minh `ANTI-1`..`ANTI-6` được tích hợp đầy đủ | 4 file mục tiêu mang đúng 6 mã cấm cơ học kèm mẫu đối chứng WRONG/RIGHT, đạt 0 vi phạm lint | Đo trước: chỉ `vision-test-loop.md` có mã cấm, sau khi thêm 4 file đều mang bộ mã cấm | Bổ sung thêm ví dụ đối chứng cụ thể |
| Q2 | Bộ Cookbooks thực chiến Python và TypeScript/JS (Tầng 3) hoàn chỉnh | 2 file cookbook tại `rules/cookbooks/` đạt ≥ 100 dòng mỗi file, bao quát async, error handling, clean architecture; `index.md` có chỉ mục trỏ tới | Đo trước: 0 file cookbook, sau khi làm có 2 file cookbook chuyên sâu | Tách nhỏ các kịch bản thực chiến |
| Q3 | Hook `edit_gate.py` và `prompt_context.py` mớm đúng lúc (JIT Micro-injection) | Khi sửa `.py` hoặc `.ts` lần đầu, `edit_gate` in 3 dòng quy tắc vàng; khi vào phase `qc`, `prompt_context` mớm checklist DoD | Đo trước: 0 lần mớm quy tắc vàng qua edit_gate; sau khi làm in đúng 3 dòng quy tắc vàng lần đầu | Sử dụng `already_reminded` của `_common.py` |
| Q4 | Hook `session_start.py` bơm khối Neo Phục Hồi khi compaction xảy ra | Khi gọi hook với `source == "compact"`, hook tự động reset cờ nhắc ngôn ngữ và bơm Khối Neo Phục Hồi (< 200 tokens) trỏ lại state và plan | Đo trước: 0 lần bơm khối neo phục hồi khi compact; sau khi làm kiểm chứng được khối neo phục hồi | Cập nhật hàm xử lý payload source |
| Q5 | Script `tdq_test.py` hỗ trợ chế độ Silent CLI xuất log ra đĩa | Khi truyền cờ `--silent`, log chi tiết được ghi ra file `docs/tdq/.tdq-test.log`, terminal chỉ in `≤ 2` dòng tóm tắt và lỗi chính | Đo trước: 0 cờ --silent hỗ trợ trong tdq_test.py; sau khi thêm cờ hoạt động chuẩn xác | Thiết lập đường dẫn file log mặc định |
| Q6 | Toàn bộ unit test và các kiểm định QC mức `full` đạt 100% PASS | Toàn bộ bài test trong suite chạy xanh 100%; đạt 0 vi phạm qua `doc_lint.py`, `i18n_check.py` và khóa `token_budget.py` | Đo trước: 100% test hiện tại đang pass; sau khi thêm tính năng mới giữ nguyên 100% test pass | Khắc phục ngay các bài test đỏ |

**DoD**:
1. Toàn bộ 4 đầu ra cụ thể (§2) được triển khai hoàn chỉnh, đúng chuẩn kiến trúc đề xuất.
2. Cơ chế Neo Phục Hồi chống mất ngữ cảnh sau Compaction được cài đặt và kiểm chứng qua unit test.
3. Toàn bộ kiểm thử vùng chạm và trọn bộ test suite đạt 100% PASS ở mức QC `full`.

## 7. Câu hỏi còn mở

(Rỗng — toàn bộ câu hỏi đã được chốt qua phỏng vấn vòng 1.)
