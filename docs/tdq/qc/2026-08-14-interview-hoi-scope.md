# QC — Vòng scope: interview đi từ tổng quát đến chi tiết

Ngày: 2026-08-14 · Spec §6 · Plan: ../plan/2026-08-14-interview-hoi-scope.md · Vòng 1

| # | Hạng mục | Lệnh | Kết quả | PASS? |
|---|---|---|---|---|
| Q1 | File luật đủ 5 mục | `grep -c "^## " scope-round.md` | `5` | PASS |
| Q2 | Bỏ vòng scope phải ghi lý do | `grep -c "Vòng scope: BỎ" scope-round.md` | `1` | PASS |
| Q3 | Hỏi bối cảnh bằng số, cấm hỏi trừu tượng | `grep -c "CCU"` = `1`; `grep -ci "CẤM hỏi"` = `1` | có cả hai | PASS |
| Q4 | interview.md trỏ file luật | `grep -c "scope-round.md" interview.md` | `1` | PASS |
| Q5 | analyze-full + quick-lane trỏ file luật | `grep -l "scope-round" …` | ra đủ 2 file | PASS |
| Q6 | SKILL.md nhắc vòng scope, không vượt trần | `grep -ci "vòng scope"` = `3`; `wc -l` = `109` ≤ 120 | đạt cả hai | PASS |
| Q7 | spec-template buộc chép mặt bị loại | `grep -c "mặt bị loại" spec-template.md` | `2` | PASS |
| Q8 | Checklist phase analyze nhắc vòng scope | `tdq_state.py next` ở phase `analyze` | in `- [ ] Vòng scope trước (mặt nào + bối cảnh bằng số) theo …scope-round.md, hoặc ghi 'Vòng scope: BỎ — lý do'` | PASS |
| Q9 | Log service còn nguyên | gọi `_warn("qc-probe")` | mặc định: `[2026-08-14T01:51:37+07:00] ⚠️ qc-probe` (1 dòng); `TDQ_LOG=0`: 0 dòng | PASS |
| Q10 | Full suite | `python3 -m pytest tests/ -q` | `563 passed, 244 subtests passed in 32.31s`, không có `failed` (≥ 552) | PASS |
| Q11 | doc_lint mọi file `.md` đã sửa | `python3 scripts/doc_lint.py <9 file>` | `exit=0` | PASS |

Kết luận: 11/11 PASS ngay vòng 1, không có vòng fix.
