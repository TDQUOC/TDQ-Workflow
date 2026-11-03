# QC — Đổi tên mode thực thi + phân tích lý do đề xuất

Ngày: 2026-08-14 · Plan: ../plan/2026-08-14-doi-ten-mode-implement.md · 10 hạng mục DoD.
Vòng 1 có 1 FAIL (Q4) → đã fix ở task QC1.1, chạy lại Q4 + Q9 + Q10.

| # | Hạng mục | Kết quả |
|---|---|---|
| Q1 | `mode_label` in 2 nhãn Việt hoá | PASS |
| Q2 | `--mode inline` → `implement_mode=main` | PASS |
| Q3 | `--mode "sub-agent implement"` → `subagent` | PASS |
| Q4 | `looks_like_approval` ở cổng mode | FAIL vòng 1 → PASS sau QC1.1 |
| Q5 | `tdq_state.py next` phase `mode` chứa 2 nhãn mới | PASS |
| Q6 | SKILL.md có khuôn nhãn mới + luật căn cứ | PASS |
| Q7 | plan-template.md và tdq-build/SKILL.md có nhãn mới | PASS |
| Q8 | log service bật mặc định, `TDQ_LOG=0` tắt được | PASS |
| Q9 | full suite | PASS |
| Q10 | doc_lint mọi file `.md` đã sửa | PASS |

## Bằng chứng

**Q1** — `mode_label('main')` / `mode_label('subagent')`:
```
làm trực tiếp (inline implement)
giao trợ lý (sub-agent implement)
```

**Q2/Q3** — state thử ở `TDQ_PROJECT_DIR` riêng (không đụng state thật):
`approve plan --mode inline` → `get implement_mode` = `main`;
`approve plan --mode "sub-agent implement"` → `subagent`.

**Q4** — vòng 1: `looks_like_approval("A", "mode")` = `False`, trong khi khuôn mới mời
user nhắn "A"/"B" → FAIL. Sau QC1.1 (thêm `LETTER` + `mode_from_answer`):
```
'main' True main          'A' True main
'subagent' True subagent  'B' True subagent
'inline implement' True main
'sub-agent' True subagent
'Ai làm cũng được' False None
```

**Q5** — `tdq_state.py next` ở phase `mode` in cả `inline implement` lẫn `sub-agent implement`.

**Q6** — `grep -c "inline implement" skills/tdq-plan/SKILL.md` = 2; `grep -c "căn cứ"` = 1.

**Q7** — `grep -l "inline implement"` liệt kê `skills/tdq-build/SKILL.md` và
`skills/tdq-plan/references/plan-template.md`.

**Q8** — mặc định: `[2026-08-14T01:02:48+07:00] ⚠️ qc log` (1 dòng có timestamp);
`TDQ_LOG=0` → 0 dòng.

**Q9** — `python3 -m pytest tests/ -q` → `552 passed, 235 subtests passed in 39.32s`
(≥ 536 theo DoD).

**Q10** — `doc_lint.py` trên 6 file `.md` đã sửa → exit 0.
