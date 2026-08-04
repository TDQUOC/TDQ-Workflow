# QC — Tối ưu time/token cho TDQ workflow

Ngày: 2026-08-04 · Spec §6 · Plan: ../plan/2026-08-04-toi-uu-token-workflow.md
Kết quả: **10/10 PASS**

| # | Lệnh kiểm | Kỳ vọng | Output thật | Kết |
|---|---|---|---|---|
| Q1 | `grep -c '^## Nhóm' <đề xuất>` | `5` | `5` | PASS |
| Q2 | đếm dòng bảng task trong 5 nhóm | ≥12, không ô trống | A=6 B=3 C=2 D=4 E=4 → **19**, ô trống 0 | PASS |
| Q3 | đếm dòng bảng nguyên nhân | ≥10, mỗi dòng có số | **12** dòng (N1–N12), 0 dòng thiếu số | PASS |
| Q4 | `grep -c 'P0\|P1\|P2' <đề xuất>` | ≥12 | `21` | PASS |
| Q5 | `python3 scripts/token_audit.py --sessions 1` | exit 0, in bảng carry-cost | exit `0`, có dòng `carry-cost` | PASS |
| Q6 | `cd tests && python3 -m unittest test_token_audit` | OK | `Ran 10 tests … OK` | PASS |
| Q7 | tắt log bằng `TDQ_AUDIT_LOG=0` | stderr rỗng | `stderr lines: 0` | PASS |
| Q8 | `python3 scripts/doc_lint.py --pair <spec> <plan>` | exit 0 | exit `0` | PASS |
| Q9 | `wc -l <report>` | ≤50 | `      50` | PASS |
| Q10 | `git status --porcelain` | chỉ docs/tdq, docs/workinglog, script + test mới | 9 file mới đúng phạm vi; 5 file `M` là dư từ request trước (STATE.md, working log, 3 file graphify-out) | PASS |

## Ghi chú kỹ thuật

**Q7 — dạng lệnh trong spec bị zsh hiểu nhầm.** Spec ghi
`TDQ_AUDIT_LOG=0 python3 scripts/token_audit.py 2>&1 >/dev/null | wc -l`.
Trên zsh, tính năng MULTIOS nhân đôi stdout vào pipe nên lệnh này trả `22` dù log
đã tắt đúng. Dạng đúng để kiểm: `2>"$tmp/err.txt" >/dev/null` rồi đếm dòng file err.
Đã kiểm bằng dạng này → **0 dòng**. Test `test_tat_log_bang_bien_moi_truong` trong
`tests/test_token_audit.py` khẳng định cùng điều đó qua `subprocess` (không qua shell).

**T4.2 — full suite chạy đúng MỘT lần:** `Ran 472 tests in 41.481s … OK`
(462 test cũ + 10 test mới, không hỏng test nào).

**Q10 — 5 file `M`:** `docs/tdq/STATE.md` do `tdq_state.py` ghi, `docs/workinglog/2026-08-04.md`
do luật working log, 3 file `graphify-out/*` do hook post-commit của request trước. Không
file nào nằm ngoài phạm vi spec §1 (không sửa CLAUDE.md, skill, hook, script workflow).
