# BRIEF — Áp dụng nâng cấp triết lý và kiến trúc Andrej Karpathy vào TDQ Workflow

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> "okay commit và merge sau đó mở request phân tích và apply nâng cấp tdq-workflow dựa trên bài học đã học của karrpathy"

### Đọc bước đầu

- **Mục tiêu**: Hiện thực hóa 5 đề xuất cải tiến kiến trúc cốt lõi từ Báo cáo Nghiên cứu `docs/tdq/reports/2026-10-16-1245-hoc-hoi-andrej-karpathy-skills.html` vào hệ thống TDQ Workflow, bao gồm:
  1. *Kỷ luật phẫu thuật cấp dòng (Line-level Surgical Traceability)*: Bổ sung kiểm tra và nhắc nhở tính phẫu thuật vào `hooks/scripts/edit_gate.py` và luật `skills/tdq-build/references/rules/chung.md` (cấm drive-by refactoring, cấm tự ý sửa comment, khoảng trắng, hoặc code không liên quan đến task).
  2. *Luật "YAGNI đứng trên SOLID"*: Cập nhật `skills/tdq-conventions/references/clean-code.md` và `skills/tdq-build/references/rules/chung.md` cấm tạo Interface, Abstract Class hay Strategy Pattern cho mã chỉ dùng 1 lần (Single-use). Viết hàm phẳng tinh gọn trước, chỉ refactor khi có ca sử dụng thứ hai.
  3. *Chủ động phản biện và tinh giản Intake (Surface Tradeoffs & Push Back)*: Bổ sung cơ chế phản biện kiến trúc tại `skills/tdq-intake/references/interview.md`, cho phép Agent phản biện giải pháp cồng kềnh và đưa ra 2-3 kịch bản kèm công sức.
  4. *Khai báo công thức Goal-Driven Loops cho Subagents*: Chuẩn hóa quy tắc thực thi hướng mục tiêu `[Goal] -> verify: [Check]` trong `agents/tdq-implementer.md`.
  5. *Quy tắc "Chỉ dọn rác của chính mình" (Clean Up Only Your Own Mess)*: Tinh chỉnh Intentionality rule trong `chung.md` cấm xóa dead code có sẵn từ trước làm vỡ namespace hay xung đột git; chỉ dọn dẹp các biến/import mồ côi do chính thay đổi của mình tạo ra.
- **Phạm vi dự kiến**:
  - `skills/tdq-build/references/rules/chung.md`
  - `skills/tdq-conventions/references/clean-code.md`
  - `skills/tdq-intake/references/interview.md`
  - `hooks/scripts/edit_gate.py`
  - `agents/tdq-implementer.md`
  - Bộ test tương ứng trong `tests/test_edit_gate.py`

## Hiểu & kiến thức

### Năng lực dùng được

Phân vân → DÙNG. Kiểm kê ngày 2026-10-16: 9 skill trên đĩa, cộng skill built-in trong context. Không xoá bảng này kể cả khi không có dòng DÙNG nào.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| Agent | built-in | DÙNG | Chạy kiểm định độc lập mức `ultra` qua `tdq-qc-tester` |
| token_budget.py & doc_index.py | project | DÙNG | Đồng bộ chỉ mục dòng và khóa ngân sách token sau khi cập nhật rules |
| tdq-intake | plugin:tdq-workflow | NỀN | mở request, phỏng vấn và chuyển phase |
| tdq-spec | plugin:tdq-workflow | NỀN | lập đặc tả kỹ thuật và kiểm tra hợp đồng |
| tdq-plan | plugin:tdq-workflow | NỀN | lập kế hoạch phân tách task TDD |
| tdq-build | plugin:tdq-workflow | NỀN | thực thi TDD, chạy QC và lập báo cáo |
| tdq-conventions | plugin:tdq-workflow | NỀN | quy tắc workflow, ngôn ngữ 3 tầng |
| tdq-status | plugin:tdq-workflow | NỀN | kiểm tra trạng thái tiến độ |
| tdq-lean | plugin:tdq-workflow | NỀN | kiểm tra tính tinh gọn của mã nguồn |
| tdq-setup | plugin:tdq-workflow | NỀN | kiểm tra LSP và môi trường |
| tdq-check-status | plugin:tdq-workflow | NỀN | phục hồi phiên khi có sự cố |
| Đã xét 15 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

### Phân tích chi tiết các điểm tác động

1. **Tại `skills/tdq-build/references/rules/chung.md`**:
   - Tinh chỉnh câu hỏi số 3 của *The Intentionality rule*: Làm rõ chỉ xóa dead code do chính thay đổi trong request tạo ra; dead code có sẵn từ trước chỉ nêu ra trong báo cáo, không tự ý xóa gây xung đột git.
   - Bổ sung quy tắc *Surgical Changes (Line-level Traceability)*: Mọi dòng thêm/sửa trong git diff phải truy vết trực tiếp về yêu cầu người dùng; cấm drive-by refactoring, cấm sửa comment/quote style lân cận.
2. **Tại `skills/tdq-conventions/references/clean-code.md`**:
   - Bổ sung nguyên tắc *Simplicity & YAGNI before SOLID*: Cấm tạo Interface, Abstract Class hoặc Strategy Pattern cho code chỉ dùng 1 lần (single-use code). Viết 1 hàm phẳng duy nhất; chỉ áp dụng OCP/DIP khi có ít nhất 2 trường hợp sử dụng thực tế.
3. **Tại `skills/tdq-intake/references/interview.md`**:
   - Bổ sung quy tắc *Think Before Coding — Surface Tradeoffs & Push Back*: Trước khi hỏi câu hỏi chi tiết, nếu phát hiện giải pháp người dùng yêu cầu quá phức tạp so với bài toán, Agent bắt buộc phải chủ động phản biện (push back) và đề xuất phương án đơn giản hơn kèm ước lượng công sức.
4. **Tại `agents/tdq-implementer.md`**:
   - Tích hợp 4 nguyên lý Karpathy vào chỉ dẫn thực thi của Subagent: (1) Surgical line-level diff; (2) No single-use abstraction; (3) Clean up only your own orphans; (4) Goal-driven loop `[Step] -> verify: [Check]`.
5. **Tại `hooks/scripts/edit_gate.py` và `tests/test_edit_gate.py`**:
   - Tích hợp quy tắc nhắc nhở tính phẫu thuật (`Surgical changes: touch only what you must, no drive-by refactor`) vào chuỗi nhắc nhở JIT micro-rules khi sửa file mã nguồn lần đầu trong phiên.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Research web | BỎ | Đã hoàn thành nghiên cứu chuyên sâu ở request trước (`2026-10-16-1245-hoc-hoi-andrej-karpathy-skills`) |
| Interview | CÓ | Đã hoàn thành vòng 1 chốt các lựa chọn `1a 2a 3c` |
| QC độc lập | CÓ | Áp dụng mức QC `ultra` theo yêu cầu của người dùng |

## Hỏi đáp

### Vòng 1 (2026-10-16 14:12)

1. **Phạm vi áp dụng các bài học Karpathy trong đợt này**:
   - A (đề xuất): Triển khai trọn gói cả 5 cải tiến vào tài liệu và mã nguồn (`chung.md`, `clean-code.md`, `interview.md`, `agents/tdq-implementer.md`, và `edit_gate.py`).
   - B: Chỉ cập nhật phần tài liệu hướng dẫn (`skills/` và `agents/`), chưa sửa `edit_gate.py`.
   - **Người dùng chọn:** `1a`
2. **Cơ chế tích hợp Surgical Rule vào `edit_gate.py`**:
   - A (đề xuất): Gộp nguyên lý Surgical & No Single-Use Abstraction vào thông điệp JIT micro-rules (nhắc nhẹ 1 lần đầu phiên khi sửa code, không chặn lệnh, không tạo ma sát nhận thức).
   - B: Tạo một cơ chế đếm số dòng sửa đổi để chặn cứng (deny) nếu sửa nhiều dòng.
   - **Người dùng chọn:** `2a`
3. **Mức QC (chất lượng kiểm định cho request này)**:
   - A: `full`
   - B (đề xuất): `lite` — DoD + unit test vùng chạm (`tdq_test.py vung-cham`).
   - C: `ultra`
   - **Người dùng chọn:** `3c` (`ultra`)
