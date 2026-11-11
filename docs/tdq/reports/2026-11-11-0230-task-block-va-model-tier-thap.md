# REPORT — Hiện thực Task Block chi tiết và Tự động gọi Model Tier thấp ở Implement (`2026-11-11-0230-task-block-va-model-tier-thap` · lane full · mode subagent · 9 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Trước request (trạng thái/flow):** Task trong Plan chỉ có 1 dòng tóm tắt ngắn gọn (`- [ ] **Tx.y** (eNm) <tên task> — Test: <lệnh>`), bỏ rơi toàn bộ logic và chữ ký hàm từ Spec §3c khiến subagent thi công phải đoán mò interface; subagent `tdq-implementer` kế thừa model lớn của parent (`inherit` - Sonnet/Opus) gây tốn kém chi phí token và tốc độ chậm; linter `doc_lint.py` không kiểm tra độ sâu kỹ thuật của Plan.
**Sau request (trạng thái/flow):** Task can thiệp mã nguồn được mở rộng thành khối **Self-Contained Task Block** 8 trường (`Chạm:`, `Cần:`, `Mục tiêu:`, `Vị trí neo:`, `Công cụ:`, `Ràng buộc:`, `Đặc tả kỹ thuật:`, `Logic cốt lõi:`, `Ca góc hiểm & TDD:`) kèm 4 chốt an toàn cơ học cho model 30B/Haiku; linter `doc_lint.py` bổ sung **Rule R15** chặn cứng (exit 1) nếu task code thiếu logic; subagent `tdq-implementer` mặc định chạy `model: haiku` (`effort: medium`) rẻ hơn 15x, đồng thời hỗ trợ Dynamic Model Tier Routing cho phép Leader override `model: sonnet / opus` khi gặp task phức tạp. · **Đã làm:** P1 (Rule R15 doc_lint & unit test) · P2 (Plan template, hướng dẫn thích ứng & team-mode delegation) · P3 (Config subagent Haiku) · P4 (Log & kiểm thử hồi quy).
**Đã test gì:** Đã chạy unit test kiểm thử Rule R15 (`tests/test_doc_lint_r15.py`), toàn bộ test suite linter (`tests/test_doc_lint.py`), test suite điều phối team mode (`tests/test_team_mode.py`), kiểm tra khóa token budget (`token_budget.py --kiem`), xác minh toàn vẹn Archify HTML manifest và kiểm định độc lập qua agent `tdq-qc-tester`.
**Kết quả test:** 68/68 test linter PASS (gồm 3 test mới R15) · 153/153 test team mode PASS · token budget 62 file khóa sạch exit 0 · Archify manifest status current valid true · QC PASS 8/8 mục DoD, 0 defect.
**Đầu ra:** `scripts/doc_lint.py` (Rule R15) · `skills/tdq-plan/references/plan-template.md` · `skills/tdq-plan/references/plan-template-huong-dan.md` · `skills/tdq-build/references/team-mode.md` · `agents/tdq-implementer.md` · `tests/test_doc_lint_r15.py` · `docs/tdq/qc/2026-11-11-0230-task-block-va-model-tier-thap.md` · **Archify HTML:** `docs/tdq/reports/2026-11-11-0230-task-block-va-model-tier-thap.html` · Backup: không có
**Giới hạn:** Không có. Toàn bộ tính năng đã hoàn thiện và kiểm chứng tự động.
**Lệch spec chờ duyệt:** (không có)
**Git:** Nhánh `feat/task-block-va-model-tier-thap` đã commit các thay đổi kỹ thuật sạch, sẵn sàng merge về `dev`.

## Thời gian

Request `2026-11-11-0230-task-block-va-model-tier-thap` · lane full · opened at 2026-11-11T02:42:33+07:00

| Phase | Wall clock | API request | Tool wait | Background job | Observed union | Unattributed | Times entered |
|---|---|---|---|---|---|---|---|
| idle | 13s | 12s [partial] | 1s [partial] | — [unavailable] | 13s [partial] | 0s [partial] | 1 |
| analyze | 9 min | 1 min [partial] | 5s [partial] | — [unavailable] | 1 min [partial] | 8 min [partial] | 1 |
| spec | 3h 35min | 2 min [partial] | 28s [partial] | — [unavailable] | 3 min [partial] | 3h 32min [partial] | 1 |
| plan | 5h 59min | 4 min [partial] | 31s [partial] | — [unavailable] | 4 min [partial] | 5h 55min [partial] | 1 |
| implement | 26 min | 18 min [partial] | 9 min [partial] | — [unavailable] | 25 min [partial] | 8s [partial] | 1 |
| qc | 5 min | 3 min [partial] | 3 min [partial] | — [unavailable] | 5 min [partial] | 1s [partial] | 1 |
| Total | 10h 15min | 28 min [partial] | 14 min [partial] | — [unavailable] | 39 min [partial] | 9h 36min [partial] |  |

Model compute time is unavailable (`model_giay=null`). API includes network/provider latency; tool time is host wait. Observed metrics may overlap; unattributed time is not assumed user/model time.

## Thân PR (soạn sẵn)

**Tóm tắt:** Chuẩn hóa cấu trúc Self-Contained Task Block 8 trường kèm 4 chốt an toàn cơ học trong Plan, bổ sung Rule R15 trong `doc_lint.py` để cưỡng chế tính chi tiết, và cấu hình subagent `tdq-implementer` mặc định chạy model Haiku (tiết kiệm token 15x, hỗ trợ override Sonnet/Opus linh hoạt khi gặp task phức tạp).
**Trước/Sau:** `docs/tdq/spec/2026-11-11-0230-task-block-va-model-tier-thap-preview.html` và `docs/tdq/reports/2026-11-11-0230-task-block-va-model-tier-thap.html`.
**Đã kiểm:**
- `pytest tests/test_doc_lint.py tests/test_doc_lint_r15.py`: 68 passed in 4.40s
- `pytest tests/test_team_mode.py`: 153 passed, 1 skipped in 91.25s
- `python scripts/token_budget.py --kiem`: 62 file, cap 3500, clean exit 0
- `python scripts/tdq_archify.py verify`: valid: true, status: current
**Rủi ro hồi quy:** Không ảnh hưởng các plan tài liệu (Rule R15 chỉ kiểm tra task can thiệp mã nguồn có đuôi code). Các regex parser `_TASK` và `_PATH` của `tdq_team.py` được bảo toàn nguyên vẹn 100%.
<!-- tdq-archify-binding:start -->
<!-- manifest: 2026-11-11-0230-task-block-va-model-tier-thap.manifest.json -->
<!-- manifest_digest: 1662114d823d4b0fdaccd758113960d65f5882ea41a982268b2c1053f31c92c7 -->
<!-- tdq-archify-binding:end -->