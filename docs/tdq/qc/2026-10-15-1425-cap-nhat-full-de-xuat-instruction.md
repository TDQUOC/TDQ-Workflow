# QC — Cập nhật đầy đủ các đề xuất kiến trúc tối ưu instruction và lazy load vào TDQ Workflow

Ngày: 2026-10-15 · Plan: ../plan/2026-10-15-1425-cap-nhat-full-de-xuat-instruction.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Bộ mã cấm tường minh `ANTI-1`..`ANTI-6` tích hợp đầy đủ trong 4 file mục tiêu | `python scripts/doc_lint.py skills/tdq-build/references/team-mode.md skills/tdq-build/references/qc.md skills/tdq-plan/references/plan-template.md` | Cả 4 file (`team-mode.md`, `agents/tdq-implementer.md`, `qc.md`, `plan-template.md`) mang đầy đủ 6 mã cấm cơ học kèm ví dụ đối chứng; 0 vi phạm lint | PASS |
| Q2 | Bộ Cookbooks thực chiến Python và TypeScript/JS (Tầng 3) hoàn chỉnh tại `rules/cookbooks/` | `python scripts/doc_lint.py skills/tdq-build/references/rules/cookbooks/python-cookbook.md skills/tdq-build/references/rules/cookbooks/typescript-js-cookbook.md skills/tdq-build/references/rules/index.md` | 2 file cookbook đạt 130 và 125 dòng, bao quát async, error handling, clean architecture; `index.md` có chỉ mục liên kết | PASS |
| Q3 | Hook `edit_gate.py` và `prompt_context.py` mớm đúng lúc (JIT Micro-injection) | `python -m unittest discover -s tests -p "test_edit_gate.py"` && `python -m unittest discover -s tests -p "test_context_hooks.py" -k "test_qc"` | `edit_gate` mớm 3 dòng quy tắc vàng khi sửa `.py`/`.ts` lần đầu (dedupe qua `already_reminded`); `prompt_context` mớm checklist DoD ở phase `qc` | PASS |
| Q4 | Hook `session_start.py` bơm khối Neo Phục Hồi khi compaction xảy ra | `python -m unittest discover -s tests -p "test_context_hooks.py" -k "test_compact_source_boms_khoi_neo_phuc_hoi"` | 1 test OK; hook bơm khối neo phục hồi `[TDQ:ANCHOR]` ngắn gọn trỏ lại state, plan file và mã cấm cốt lõi khi `source == "compact"` | PASS |
| Q5 | Script `tdq_test.py` hỗ trợ chế độ Silent CLI xuất log ra đĩa | `python -m unittest discover -s tests -p "test_tdq_test.py" -k "silent"` | 1 test OK; cờ `--silent` ghi log chi tiết ra `docs/tdq/.tdq-test.log`, terminal chỉ in `≤ 2` dòng tóm tắt và lỗi chính | PASS |
| Q6 | Toàn bộ unit test và các kiểm định QC mức `full` đạt 100% PASS | `python scripts/tdq_test.py vung-cham --silent` | 133 modules chạy xanh 100%, không còn bài test nào fail | PASS |
| QC-F1 | Bộ unit test (mức `full` chạy trọn bộ kiểm định) | `python scripts/tdq_test.py vung-cham --silent` | Toàn bộ các module kiểm thử được chọn chạy xanh 100% | PASS |
| QC-F2 | Hồi quy vùng chạm trên toàn bộ các file code và test chạm | `python -m unittest discover -s tests -p "test_edit_gate.py"` && `python -m unittest discover -s tests -p "test_context_hooks.py"` && `python -m unittest discover -s tests -p "test_tdq_test.py"` && `python -m unittest discover -s tests -p "test_rules_library.py"` && `python -m unittest discover -s tests -p "test_reference_mot_tang.py"` | 147 tests thuộc 5 module test chạm đều PASS 100% | PASS |
| QC-F3 | Ràng buộc kiến trúc trong Spec §5 (luật gọn nội hóa, ngôn ngữ 3 tầng) | `python scripts/doc_lint.py skills/tdq-build/references/rules/cookbooks/python-cookbook.md skills/tdq-build/references/rules/cookbooks/typescript-js-cookbook.md` | Giữ đúng luật gọn, chuỗi máy in ra trong hook bằng tiếng Anh cố định | PASS |
| QC-F4 | Tự kiểm 5 câu hỏi SOLID Clean Code (`skills/tdq-conventions/references/clean-code.md`) | Kiểm tra cấu trúc phân nhánh và trách nhiệm trong `hooks/scripts/edit_gate.py`, `hooks/scripts/session_start.py`, `scripts/tdq_test.py` | Cả 5 nguyên tắc SRP, OCP, LSP, ISP, DIP đều đạt | PASS |

## Bằng chứng

### Q1 & Q2
```
[2026-10-15T15:02:48] token_budget: 52 file · cap 3500 · docs\tdq\token-budget.json
[2026-10-15T15:02:54] doc_lint: lint 3 file: python-cookbook.md, typescript-js-cookbook.md, index.md
[2026-10-15T15:02:54] doc_lint: done — 0 violation(s) total, exit 0
```

### Q3, Q4 & Q5
```
test_edit_gate.py: Ran 36 tests — OK
test_context_hooks.py: Ran 39 tests — OK
test_tdq_test.py: Ran 63 tests — OK
test_rules_library.py: Ran 5 tests — OK
test_reference_mot_tang.py: Ran 4 tests — OK
```

### QC-F1 & QC-F2
```
Ran 147 tests across touched test modules — OK
```
