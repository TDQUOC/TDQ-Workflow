# Brief: Hiện thực cấu trúc Task Block chi tiết kèm 4 chốt an toàn và cơ chế gọi Model Tier thấp ở Implement

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

- **Lời người dùng:** "mở request deep để thực hiện cơ chế mới đó cho plan và các chốt an toàn bổ sung trong tdq-workflow, đồng thời cơ chế tự động ở implement sẽ gọi model tier thấp implement task để nhanh và tiieets kiệm hơn"
- **Mục tiêu:**
  1. Hiện thực hóa cấu trúc **The Self-Contained Executable Task Block** chuẩn mực cho Plan (gồm 8 trường kỹ thuật + 4 chốt an toàn cơ học cho model 30B/Haiku) vào `skills/tdq-plan/references/plan-template.md` và `plan-template-huong-dan.md`.
  2. Bổ sung **Rule linter R15** vào `scripts/doc_lint.py` để tự động kiểm tra và cưỡng chế tính đầy đủ của Task Block đối với các task can thiệp mã nguồn.
  3. Cấu hình cơ chế tự động điều phối subagent: ở phase `implement` (subagent mode), cấu hình `agents/tdq-implementer.md` sử dụng `model: haiku` (hoặc model tier thấp), và cập nhật `skills/tdq-build/references/team-mode.md` để tự động chuyển giao trọn vẹn khối Task Block (đầy đủ chữ ký hàm, pseudo-code, vị trí neo, công cụ phẫu thuật, ca góc hiểm) cho subagent thi công chuẩn xác 100%.
- **Phạm vi:**
  - `skills/tdq-plan/references/plan-template.md`, `skills/tdq-plan/references/plan-template-huong-dan.md`
  - `scripts/doc_lint.py` (Rule R15)
  - `tests/test_doc_lint_r15.py` (Unit tests cho Rule R15)
  - `agents/tdq-implementer.md` (Cấu hình `model: haiku`)
  - `skills/tdq-build/references/team-mode.md` (Cập nhật prompt dispatching nạp trọn vẹn Task Block)

## Hiểu & kiến thức

### Năng lực dùng được

| Skill / Công cụ | Nguồn | Quyết định | Lý do |
|---|---|---|---|
| `tdq-spec` | plugin:tdq-workflow | NỀN | Soạn spec đặc tả kỹ thuật chi tiết |
| `tdq-plan` | plugin:tdq-workflow | NỀN | Lập kế hoạch phân tách task theo TDD |
| `tdq-build` | plugin:tdq-workflow | NỀN | Chạy build và QC ultra |
| `Archify CLI` (`tdq_archify.py`) | project | DÙNG | Render sơ đồ trực quan Hiện trạng vs Đề xuất |
| `doc_lint.py` | scripts/ | DÙNG | Hiện thực rule R15 |
| Đã xét 25 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

### 1. Kiến trúc Self-Contained Task Block kèm 4 Chốt An Toàn

Một task can thiệp code trong Plan được chuẩn hóa gồm:
- Header chuẩn: `- [ ] **Tx.y** (eNm) <Tên task hành động> — Test: <lệnh kiểm>`
- 8 trường con thụt lề:
  1. `Chạm:` `<danh sách file>`
  2. `Cần:` `<phụ thuộc nếu có>`
  3. `Mục tiêu:` `<1 câu vai trò kỹ thuật>`
  4. `Vị trí neo:` `<hàm/dòng neo cụ thể trong file>` (Chốt an toàn 1)
  5. `Công cụ:` `<chỉ định rõ Edit vs Write>` (Chốt an toàn 2)
  6. `Ràng buộc:` `<stdlib, không cài thêm lib, giới hạn dòng>` (Chốt an toàn 3)
  7. `Đặc tả kỹ thuật:` `<chữ ký hàm, type hints, input/output>`
  8. `Logic cốt lõi:` `<pseudo-code 1-2-3>`
  9. `Ca góc hiểm & TDD:` `<xử lý lỗi biên, assertion mong đợi>` (Chốt an toàn 4)

### 2. Rule Linter R15 trong `scripts/doc_lint.py`

- Quét các task trong `docs/tdq/plan/<slug>.md`.
- Nếu task có `Chạm:` chứa file mã nguồn (đuôi `.py`, `.ts`, `.js`, `.go`, `.rs`, `.c`, `.cpp`):
  - Bắt buộc phải có ít nhất 1 dòng đặc tả logic (chứa từ khóa `Đặc tả`, `Logic`, `Giải thuật`, `Pseudo-code`, hoặc `Mục tiêu`).
  - Nếu thiếu: Báo lỗi `[R15] Task Tx.y modifies source code but lacks technical specification / pseudo-code block`.
- Nếu task chỉ chạm file tài liệu/cấu hình: Cho phép Compact 1 dòng.

### 3. Tự động điều phối Model Tier thấp ở Implement

- Cập nhật `agents/tdq-implementer.md`: Đặt `model: haiku` (thay vì `inherit`), giảm effort xuống `medium` khi task đã có Micro-Spec chi tiết.
- Cập nhật `skills/tdq-build/references/team-mode.md`: Khi nạp task vào prompt delegation, sao chép trọn vẹn khối Task Block để model nhỏ có đầy đủ chỉ dẫn thi công tự thân.

### Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| `spec` | CÓ | Thiết kế chi tiết đặc tả R15, Task Block template và subagent model config |
| `plan` | CÓ | Lập kế hoạch chi tiết cho các task hiện thực TDD |
| `implement` | CÓ | Cập nhật template, linter R15, test suite và agent definition |
| `qc` (ultra) | CÓ | Chạy test suite linter, smoke test team mode và kiểm định độc lập |
| `report` | CÓ | Xuất báo cáo nghiệm thu 4 phần kèm sơ đồ Archify HTML Trước/Sau |

## Hỏi đáp

### Vòng phỏng vấn chi tiết & Chốt mức QC

- **Lựa chọn 1 (1a):** Cố định `model: haiku` trong `agents/tdq-implementer.md`, effort `medium` khi đã có Micro-Spec tự thân; tối ưu chi phí (rẻ hơn 15–20 lần) và tăng tốc thực thi.
- **Lựa chọn 2 (2a):** Rule R15 trong `scripts/doc_lint.py` chặn cứng (`exit 1`) — bắt buộc mọi task can thiệp mã nguồn phải có phần đặc tả logic/pseudo-code, không cho nộp plan sơ sài.
- **Lựa chọn 3 (3c):** Mức QC `ultra` — kiểm thử toàn diện DoD, unit test linter, smoke test team delegation và kiểm định độc lập bởi agent `tdq-qc-tester`.

