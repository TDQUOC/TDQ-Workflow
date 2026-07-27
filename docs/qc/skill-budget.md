# QC — Budget skills (Validate C) — 2026-07-27

Tiêu chí (spec mục 3.1): description ≤ 2 dòng, body ≤ 500 dòng. Đo bằng `wc -l` + parse frontmatter.

| Skill | Body (dòng) | Description | Kết quả |
|---|---|---|---|
| tdq-analyze | 29 | 154 chars, 1 dòng | PASS |
| tdq-approve | 25 | 123 chars, 1 dòng | PASS |
| tdq-conventions | 54 | 142 chars, 1 dòng | PASS |
| tdq-implement | 36 | 153 chars, 1 dòng | PASS |
| tdq-plan | 30 | 154 chars, 1 dòng | PASS |
| tdq-qc | 21 | 133 chars, 1 dòng | PASS |
| tdq-report | 24 | 129 chars, 1 dòng | PASS |
| tdq-spec | 30 | 142 chars, 1 dòng | PASS |
| tdq-start | 34 | 152 chars, 1 dòng | PASS |
| tdq-status | 22 | 149 chars, 1 dòng | PASS |

Kết luận: 10/10 skill PASS budget. Phần dài (Tavily) đã tách vào `skills/tdq-conventions/references/tavily.md` (chỉ load khi cần). `claude plugin validate . --strict` PASS sau C1, C2, C3, C4.
