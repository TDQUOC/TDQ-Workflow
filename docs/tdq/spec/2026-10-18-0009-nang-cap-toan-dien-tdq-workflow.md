# SPEC — Nâng cấp toàn diện TDQ Workflow từ Master Blueprint

Ngày: 2026-10-18 · Bản: 1.0 · Brief: ../brief/2026-10-18-0009-nang-cap-toan-dien-tdq-workflow.md · Lane: full
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
- Mục tiêu: Hiện thực hóa toàn bộ đề xuất trong Master Blueprint (`docs/tdq/de-xuat-nang-cap-toan-dien-tu-everything-claude-code.md`) vào mã nguồn TDQ Workflow, bao gồm cơ chế Stop-Batching Hook giảm độ trễ Windows 11 xuống < 200ms, Strategic Compaction Gate tiết kiệm 35–50% context, chuẩn hóa JSON Handoff < 200 tokens, đội ngũ 6 subagent tinh hoa, giải thuật TCAS AST chống va chạm logic và công cụ tự học có kiểm duyệt `tdq_harvest.py`.
- Trong phạm vi:
  - Triển khai Stop-Batching Hook (`hooks/scripts/stop_batch_checker.py`) và bộ đệm `.claude/tmp/edited_files.txt`.
  - Triển khai Strategic Compaction Gate (`hooks/scripts/strategic_compact_gate.py`) với Weighted Tool Counter tại các Natural Gate Boundaries.
  - Triển khai Denial Deduplication trong cơ chế gác cổng hook.
  - Triển khai `hooks/scripts/doc_file_gate.py` chặn tệp Markdown rác ngoài không gian quy định.
  - Nâng cấp `scripts/tdq_team.py` với giải thuật TCAS AST Import Dependency Graph và chia sẻ thư viện NTFS Junction (`mklink /J`) trên Windows 11.
  - Xây dựng công cụ thu hoạch tri thức tự học có kiểm duyệt `scripts/tdq_harvest.py` và vùng cách ly `docs/tdq/knowledge/candidates/`.
  - Chuẩn hóa JSON Schema cho giao thức bàn giao `TDQ_HANDOFF_PAYLOAD` (< 200 tokens).
  - Bổ sung các subagent tinh hoa: `agents/tdq-security-reviewer.md`, `agents/tdq-build-resolver.md`, `agents/tdq-refactor-cleaner.md`.
  - Nâng cấp `agents/tdq-reviewer.md` với luật đối kháng `Adversarial Skeptic` (Fail-Closed $\ge 0.80$).
  - Bổ sung quy tắc Clean Code Invariants (Immutability, Hàm $\le 50$ dòng, TDD) vào `skills/tdq-conventions/references/soul.md`.
  - Viết bộ bài kiểm thử tự động toàn diện trong `tests/` bao phủ 100% các tính năng mới.
- NGOÀI phạm vi:
  - Không sao chép các thành phần bloatware của ECC (daemon Rust `ecc2/`, TUI Ratatui, SQLite WAL actor).
  - Không nhập 71 subagent phân mảnh của ECC.
  - Không nạp luật tự động không qua kiểm duyệt của con người.

## 1b. Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | Mã nguồn ECC và TDQ Workflow đã có sẵn cục bộ trên máy |
| Interview | CÓ | Đã thực hiện Vòng 1 chốt phạm vi toàn diện P0–P3 và mức QC ultra |
| QC độc lập (agent) | CÓ | Chạy kiểm thử tự động mức ultra với bài đo benchmark độ trễ thực tế trên Windows 11 |

## 2. Đầu ra cụ thể
| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Bộ đệm và hook Stop-Batching | `hooks/scripts/stop_batch_checker.py` | Chạy py_compile không lỗi, kiểm tra gộp các tệp sửa cuối turn |
| 2 | Cổng nén ngữ cảnh chiến lược | `hooks/scripts/strategic_compact_gate.py` | Kiểm tra tải trọng công cụ có trọng số tại ranh giới gate tự nhiên |
| 3 | Cổng chặn tệp rác Markdown | `hooks/scripts/doc_file_gate.py` | Chặn đứng mọi tệp `.md` ghi ngoài `docs/tdq/` hoặc `docs/workinglog/` |
| 4 | Thuật toán TCAS AST & NTFS Junction | `scripts/tdq_team.py` | Phát hiện va chạm import AST giữa các task và tạo liên kết junction < 1s |
| 5 | Công cụ thu hoạch tri thức tự học | `scripts/tdq_harvest.py` | Quét lỗi QC FAIL, đưa vào candidates/ và yêu cầu approve CLI |
| 6 | Schema giao thức bàn giao tác tử | `skills/tdq-conventions/references/handoff-schema.json` | JSON Schema draft-07 hợp lệ, dung lượng < 200 tokens |
| 7 | Bộ 3 subagent tinh hoa mới | `agents/tdq-security-reviewer.md`, `agents/tdq-build-resolver.md`, `agents/tdq-refactor-cleaner.md` | Định dạng frontmatter chuẩn, tuân thủ Least Privilege và Worktree |
| 8 | Luật đối kháng cho Reviewer | `agents/tdq-reviewer.md` | Bổ sung quy tắc Adversarial Skeptic Fail-Closed $\ge 0.80$ |
| 9 | Quy tắc Clean Code Invariants | `skills/tdq-conventions/references/soul.md` | Bổ sung 3 quy tắc bất biến: Immutability, Hàm $\le 50$ dòng, TDD |
| 10 | Bộ kiểm thử tự động toàn diện | Thư mục kiểm thử tự động | 100% test suite vượt qua không có bài test đỏ |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| mod_hook_batch | `hooks/scripts/stop_batch_checker.py`, `hooks/scripts/doc_file_gate.py`, `hooks/scripts/strategic_compact_gate.py` | không | 1, 2, 3 |
| mod_team_tcas | `scripts/tdq_team.py` | không | 4 |
| mod_harvest | `scripts/tdq_harvest.py` | không | 5 |
| mod_agents_rules | `agents/tdq-security-reviewer.md`, `agents/tdq-build-resolver.md`, `agents/tdq-refactor-cleaner.md`, `agents/tdq-reviewer.md`, `skills/tdq-conventions/references/handoff-schema.json`, `skills/tdq-conventions/references/soul.md` | không | 6, 7, 8, 9 |

## 3. Cách tiếp cận & lý do
- Chọn: Triển khai theo kiến trúc 4 tầng chuẩn mực của TDQ Workflow (Luật -> Hooks -> CLI -> Data/UX). Dùng thư viện chuẩn Python (`ast`, `subprocess`, `pathlib`, `json`) để đảm bảo không phụ thuộc bên ngoài và vận hành tối ưu trên Windows 11.
- Vì: Giải quyết dứt điểm các hạn chế lớn nhất hiện nay của TDQ Workflow (độ trễ khi sửa nhiều file trên Windows 11, ngữ cảnh bị đầy bất thình lình, va chạm import ngầm giữa các task song song), đồng thời giữ trọn vẹn sự tinh gọn và kỷ luật gác cổng cứng của hệ thống.
- Đã loại:
  - Viết lại control plane bằng Rust như ECC (`ecc2`): Loại bỏ vì vi phạm nguyên tắc tối giản, gây phức tạp build pipeline và khó bảo trì.
  - Sử dụng 71 subagent phân mảnh: Loại bỏ vì gây loãng ngữ cảnh và chồng chéo chức năng.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-conventions | plugin:tdq-workflow | NỀN | quy tắc quy trình, state, one-turn protocol |
| tdq-intake | plugin:tdq-workflow | NỀN | mở request, phỏng vấn và phân tích |
| tdq-spec | plugin:tdq-workflow | NỀN | viết đặc tả kỹ thuật chi tiết cho đợt nâng cấp mã nguồn |
| tdq-plan | plugin:tdq-workflow | NỀN | lập kế hoạch từng task thực thi kèm bài test tương ứng |
| tdq-build | plugin:tdq-workflow | NỀN | điều phối thực thi và chạy kiểm thử tự động |
| tdq-lean | plugin:tdq-workflow | DÙNG | rà soát gạt bỏ over-engineering trong mã nguồn nâng cấp |
| tdq-setup | plugin:tdq-workflow | NỀN | kiểm soát bộ tìm kiếm 3 tầng LSP/graphify/grep |
| tdq-status | plugin:tdq-workflow | NỀN | báo cáo trạng thái |
| security-review | built-in | DÙNG | đối chiếu quy chuẩn an ninh khi tạo tdq-security-reviewer |
| code-review | built-in | DÙNG | đối chiếu luật review đối kháng |
| Đã xét 20 skill khác | plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc
- Log service bật mặc định: timestamp, đủ chi tiết debug, tắt/giảm được qua config. Mọi script CLI mới (`tdq_harvest.py`, `tdq_team.py`) đều có cờ `--verbose` và định dạng log chuẩn mực `[YYYY-MM-DDTHH:MM:SS]`.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh `pytest tests/`.
- Code viết ra bám 5 nguyên tắc SOLID theo `skills/tdq-conventions/references/clean-code.md`, và bám rule ngôn ngữ trong `skills/tdq-build/references/rules/`.

## 5. Ràng buộc & rủi ro
Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md`):
- `hooks/` được gọi `scripts/`; `scripts/` **không** được import `hooks/` — việc này chạm ở `hooks/scripts/stop_batch_checker.py` và `hooks/scripts/strategic_compact_gate.py`
- `skills/` chỉ được **nhắc tên lệnh** của `scripts/`, cấm chép nội dung script vào skill — việc này chạm ở `skills/tdq-conventions/references/soul.md`
- Chỉ `scripts/tdq_state.py` được ghi `docs/tdq/state.json`; mọi nơi khác chỉ đọc qua CLI — việc này chạm ở `scripts/tdq_harvest.py`
- File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/` — việc này chạm ở toàn bộ các file Python mới tạo
- `tests/` gọi được vào mọi tầng; không tầng nào được import `tests/` — việc này chạm ở các bài test trong `tests/`

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Lệnh `mklink /J` trên Windows có thể thất bại nếu ổ đĩa khác nhau | Cấp phát worktree thất bại | Kiểm tra cùng ổ đĩa trước khi gọi `mklink`; nếu khác ổ thì fallback sang copy thông thường |
| Bộ đệm `.claude/tmp/edited_files.txt` bị xóa dở khi tiến trình crash | Mất danh sách file cần lint | Dùng cơ chế ghi append an toàn và chỉ xóa buffer khi hook Stop hoàn tất thành công |
| Thuật toán AST parse gặp lỗi cú pháp với tệp đang viết dở | Báo lỗi ngoại lệ trong `tdq_team.py` | Bọc trong khối `try/except SyntaxError` và bỏ qua các file chưa hoàn chỉnh cú pháp |

## 6. QC & Definition of Done
| # | Hạng mục kiểm | Điều kiện PASS | Đo trước | Dự phòng nếu trượt |
|---|---|---|---|---|
| Q1 | Đầy đủ bài kiểm thử tự động | 100% test suite `pytest tests/` vượt qua, 0 lỗi | Đo trước: 0 tests mới cho tính năng này · biên: 0 | Bổ sung test case và sửa lỗi logic cho đến khi 100% pass |
| Q2 | Độ trễ thao tác sửa file khi Stop-Batching | Ghi buffer tạm thời gian $\le 5$ ms/thao tác trên Windows 11 | Đo trước: 150–350ms khi spawn process trực tiếp · nguồn: thực nghiệm Windows 11 | Giữ buffer thuần văn bản append không gọi subprocess con |
| Q3 | Thời gian cấp phát Worktree qua NTFS Junction | Thời gian tạo junction hoàn tất $\le 2.0$ giây | Đo trước: 60–120s khi copy node_modules · nguồn: thực nghiệm Windows 11 | Fallback sang copy có hiển thị thanh tiến trình nếu mklink trượt |
| Q4 | Kích thước payload bàn giao tác tử | Payload `TDQ_HANDOFF_PAYLOAD` JSON $\le 250$ tokens | Đo trước: ~12.000 tokens văn bản tự do · nguồn: log phiên trước | Khống chế cứng độ dài mảng và trường chuỗi qua JSON Schema |
| Q5 | Kiểm định tài liệu chuẩn mực | `python scripts/doc_lint.py` chạy trên toàn bộ tài liệu đạt 0 lỗi | Đo trước: 0 lỗi trên tài liệu hiện tại · biên: 0 | Chỉnh sửa ngay các vi phạm quy tắc doc_lint |

DoD:
- Toàn bộ 10 đầu ra tại §2 đều được tạo lập hoặc cập nhật hoàn chỉnh, không có mã giả, không có TODO stub.
- 100% bài kiểm thử trong `tests/` vượt qua với exit code 0.
- `python scripts/doc_lint.py` chạy qua tất cả các file tài liệu trong `docs/tdq/` đạt 0 lỗi.
- Đã kiểm chứng thực tế hiệu quả của Stop-Batching Hook và NTFS Junction trên môi trường Windows 11.

## 7. Câu hỏi còn mở
(Trống — không còn câu hỏi nào chưa rõ.)
