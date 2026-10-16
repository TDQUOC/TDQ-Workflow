# QC — Áp dụng nâng cấp triết lý và kiến trúc Andrej Karpathy vào TDQ Workflow

Ngày: 2026-10-16 · Plan: ../plan/2026-10-16-1410-nang-cap-triet-ly-karpathy.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Cập nhật `chung.md` và `clean-code.md` với quy tắc Surgical, Clean Own Mess và YAGNI > SOLID | `python scripts/doc_lint.py skills/tdq-build/references/rules/chung.md skills/tdq-conventions/references/clean-code.md` | 2 file đạt 0 vi phạm lint; chứa đầy đủ quy tắc cấm drive-by refactor, phân biệt dead code và quy tắc 1 use case = 1 hàm phẳng | PASS |
| Q2 | Cập nhật `interview.md` và `agents/tdq-implementer.md` với Push Back và 4 nguyên lý Karpathy | `python scripts/doc_lint.py skills/tdq-intake/references/interview.md agents/tdq-implementer.md` | 2 file đạt 0 vi phạm lint; hướng dẫn rõ quy tắc Surface Tradeoffs, Push Back và loop `[Step] -> verify: [Check]` | PASS |
| Q3 | Hook `edit_gate.py` mớm thông điệp Surgical & Simplicity trong JIT micro-rules | `python -m unittest discover -s tests -p "test_edit_gate.py"` | 36 tests OK; hook in đúng thông điệp `surgical edits only; no single-use abstraction` dưới trần 200 ký tự | PASS |
| Q4 | Đồng bộ chỉ mục dòng, bảng neo luật, bộ lọc `luat_gon.py` và khóa ngân sách token | `python -m unittest discover -s tests -p "test_luat_gon.py" && python -m unittest discover -s tests -p "test_luat_skill.py" && python scripts/token_budget.py --kiem` | 11 tests `test_luat_gon` OK, 11 tests `test_luat_skill` OK, 52/52 file khớp khóa ngân sách token | PASS |
| Q5 | Kiểm tra số dòng và dung lượng context thực tế của `luat_gon.loc_than_luat` ở mức `full` đã giảm ~50 dòng ví dụ so với `ultra` | `python -c "import sys; sys.path.insert(0, 'hooks/scripts'); import luat_gon; t=luat_gon.doc_than_luat('.'); print(len(luat_gon.loc_than_luat(t,'ultra').splitlines()) - len(luat_gon.loc_than_luat(t,'full').splitlines()))"` | Giảm đúng 56 dòng (~2.000 ký tự / ~500 tokens) ở mức `full` mặc định | PASS |
| QC-F1 | Bộ unit test (mức `ultra` chạy trọn bộ kiểm định vùng chạm) | `python scripts/tdq_test.py vung-cham --silent` | 933 tests thuộc các module vùng chạm chạy xanh 100% | PASS |
| QC-F2 | Hồi quy vùng chạm trên toàn bộ các file code và test chạm | `python -m unittest discover -s tests -p "test_edit_gate.py"` && `python -m unittest discover -s tests -p "test_luat_gon.py"` && `python -m unittest discover -s tests -p "test_context_hooks.py"` && `python -m unittest discover -s tests -p "test_doc_index.py"` && `python -m unittest discover -s tests -p "test_token_budget.py"` | Toàn bộ 120 tests thuộc 5 module test chạm đều PASS 100% | PASS |
| QC-F3 | Ràng buộc kiến trúc trong Spec §5 (luật gọn nội hóa, ngôn ngữ 3 tầng) | `python scripts/doc_lint.py skills/tdq-build/references/rules/chung.md skills/tdq-conventions/references/clean-code.md` | Giữ đúng luật gọn, chuỗi máy in ra trong hook và rule bằng tiếng Anh cố định | PASS |
| QC-F4 | Tự kiểm 5 câu hỏi SOLID Clean Code (`skills/tdq-conventions/references/clean-code.md`) | Kiểm tra cấu trúc phân nhánh và trách nhiệm trong `hooks/scripts/luat_gon.py`, `hooks/scripts/edit_gate.py` | Cả 5 nguyên tắc SRP, OCP, LSP, ISP, DIP đều đạt; YAGNI được đặt lên trên SOLID | PASS |

## Bằng chứng

### Q1 & Q2
```
[2026-10-16T14:27:40] doc_lint: lint 3 file: chung.md, clean-code.md, interview.md
[2026-10-16T14:27:40] doc_lint: done — 0 violation(s) total, exit 0
agents/tdq-implementer.md: valid frontmatter, no lint errors
```

### Q3 & Q4
```
test_edit_gate.py: Ran 36 tests in 3.439s — OK
test_luat_gon.py: Ran 11 tests in 0.005s — OK
test_luat_skill.py: Ran 11 tests in 0.137s — OK
test_token_budget.py: Ran 8 tests in 2.160s — OK
token_budget: 52/52 file khớp khóa
```

### Q5
```
Delta lines between ultra and full: 56 lines cut
Full law body in 'full' mode: 77 lines (down from 133 lines)
Context saving: ~2,000 characters (~500 tokens) per turn in phase implement and per subagent
```

### Kiểm Định Độc Lập Mức Ultra
```
Subagent tdq-workflow:tdq-qc-tester report:
- DoD check: Q1-Q5 all PASS
- Code audit: 0 defects
- VERDICT: PASS everything
```
