# Yêu cầu: Nâng cấp toàn diện TDQ Workflow từ Master Blueprint
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

"okay vậy mở request để phân tích kĩ và update tdq-workflow để nâng cấp toàn diện tdq-workflow để hoạt độg hiệu quả và tốt hơn"

### Đọc hiểu lần đầu & Định vị Request
- **Mục tiêu**: Chuyển từ nghiên cứu sang triển khai mã nguồn thực tế nâng cấp toàn diện TDQ Workflow dựa trên tài liệu Master Blueprint (`docs/tdq/de-xuat-nang-cap-toan-dien-tu-everything-claude-code.md`).
- **Phạm vi dự kiến**:
  1. **Tầng 1 (Luật & Subagents)**: Chuẩn hóa `TDQ_HANDOFF_PAYLOAD`, tích hợp quy tắc Clean Code Invariants (Immutability, Fn ≤ 50 dòng, TDD), cập nhật luật đối kháng `Adversarial Skeptic` cho reviewer, bổ sung các subagent tinh hoa (`tdq-security-reviewer`, `tdq-build-resolver`, `tdq-refactor-cleaner`).
  2. **Tầng 2 (Gác cổng Hooks)**: Triển khai Stop-Batching Hook (`.claude/tmp/edited_files.txt`), Strategic Compaction Gate (Weighted Tool Counter), `doc_file_gate.py` (chặn tệp rác ngoài vùng), Denial Deduplication.
  3. **Tầng 3 (Công cụ CLI)**: Nâng cấp `tdq_team.py` với TCAS AST Import Dependency Graph và NTFS Junction Sharing trên Windows 11; công cụ thu hoạch tri thức tự học có kiểm duyệt `tdq_harvest.py`.
- **Điểm chưa rõ**:
  - Thứ tự và phạm vi gói triển khai trong đợt này (Ưu tiên gói cốt lõi P0 + P1 hay toàn diện P0–P3).
  - Mức kiểm thử nghiệm thu QC (`full` hay `ultra`).

## Hiểu & kiến thức

### Năng lực dùng được

Phân vân → DÙNG. Kiểm kê ngày 2026-10-18: 25 skill trên đĩa, cộng skill built-in trong context. Không xoá bảng này kể cả khi không có dòng DÙNG nào.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-conventions | plugin:tdq-workflow | NỀN | quy tắc quy trình, state, one-turn protocol |
| tdq-intake | plugin:tdq-workflow | NỀN | mở request, phỏng vấn và phân tích |
| tdq-spec | plugin:tdq-workflow | NỀN | viết đặc tả kỹ thuật chi tiết cho đợt nâng cấp mã nguồn |
| tdq-plan | plugin:tdq-workflow | NỀN | lập kế hoạch từng task thực thi có test kiểm chứng |
| tdq-build | plugin:tdq-workflow | NỀN | điều phối thực thi và chạy kiểm thử tự động |
| tdq-lean | plugin:tdq-workflow | DÙNG | rà soát gạt bỏ over-engineering trong mã nguồn nâng cấp |
| tdq-setup | plugin:tdq-workflow | NỀN | kiểm soát bộ tìm kiếm 3 tầng LSP/graphify/grep |
| tdq-status | plugin:tdq-workflow | NỀN | báo cáo trạng thái |
| security-review | built-in | DÙNG | đối chiếu quy chuẩn an ninh khi tạo tdq-security-reviewer |
| code-review | built-in | DÙNG | đối chiếu luật review đối kháng |
| Đã xét 20 skill khác | plugin/built-in | KHÔNG | khác lĩnh vực |

### Lộ trình Pipeline

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| analyze (hiện tại) | CÓ | Phỏng vấn làm rõ phạm vi ưu tiên và mức QC |
| spec | CÓ | Viết bản đặc tả kỹ thuật chi tiết các mô-đun nâng cấp |
| plan | CÓ | Lập kế hoạch từng task thực thi kèm bài test tương ứng |
| implement | CÓ | Triển khai mã nguồn vào hooks, scripts, agents, skills |
| qc | CÓ | Chạy lại toàn bộ test suite và xác nhận hiệu năng thực tế |
| report | CÓ | Báo cáo nghiệm thu và chuẩn bị phát hành |

## Hỏi đáp

### Vòng 1: Xác nhận Phạm vi Nâng cấp & Mức QC (2026-10-18 00:13)
- **Câu hỏi 1**: Bạn muốn phạm vi triển khai trong đợt này như thế nào?
  - Lựa chọn: B (Triển khai toàn bộ cả 4 giai đoạn P0 + P1 + P2 + P3 trong một đợt nâng cấp toàn diện).
- **Câu hỏi 2**: Bạn muốn kiểm định chất lượng (QC) ở mức nào?
  - Lựa chọn: B (ultra — kiểm định tối đa với bài đo benchmark thời gian phản hồi thực tế trên Windows 11 và kiểm thử đối kháng gắt gao).
- **Câu hỏi 3**: Bạn muốn bổ sung thêm gì không?
  - Lựa chọn & Ý kiến người dùng: "phân tích kĩ và nâng cấp kĩ toanf bộ mọi thứ chắt lọc từ everything claude code để giúp cho tdq-workflow hoạt động xịn và ổn định hơn".
- **Kết luận**:
  - Triển khai trọn vẹn cả 4 tầng kỹ thuật theo đúng Master Blueprint.
  - Thiết lập mức QC: `ultra` (chạy 100% test suite, đo benchmark tốc độ trên Windows 11, kiểm tra bảo toàn trạng thái và không hồi quy).

