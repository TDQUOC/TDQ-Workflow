# QC — 2026-08-04-approval-gate-bug

Đối chiếu Definition of Done spec §6 (Q1–Q7).

| # | Hạng mục | Lệnh | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | `prompt_context.py` ghi dòng `signal` đúng schema, kể cả nhánh lệch mode | `python3 -m unittest test_prompt_context -v` (trong `tests/`) | `TestSignalWritten`: 2/2 pass — `test_signal_written_matched_and_unmatched` (case matched=True/False cho spec), `test_signal_mode_conflict` (dòng gần nhất có `matched=True, mode_conflict=True`) | PASS |
| Q2 | `bash_gate.py` nhắc khi tín hiệu lệch lúc `approve` (gồm case mode_conflict) | `python3 -m unittest test_bash_gate -v` (case a: `matched=False`) + kiểm tay case (b) | (a) `test_approve_reminds_when_signal_mismatch` pass — output có `[TDQ:APPROVE]`, `permissionDecision=allow`. (b) chạy tay `bash_gate.py` với ledger `signal matched=True mode_conflict=True target=plan` + lệnh `approve plan --mode main` → vẫn in `[TDQ:APPROVE] ... DỪNG, đừng chạy lệnh này`, `permissionDecision=allow` — đúng cam kết | PASS |
| Q3 | `bash_gate.py` im lặng khi khớp thật (`matched=True, mode_conflict=False`) lúc `approve` | `test_approve_silent_when_signal_matched` | pass — không phát sinh nhắc mới | PASS |
| Q4 | `bash_gate.py` nhắc khi lệch lúc `set phase=<plan|implement>` | `test_setphase_reminds_when_signal_mismatch` (2 case trong 1 test) | pass — cả case (a) `set phase=plan` ↔ target spec và (b) `set phase=implement` ↔ target plan đều nhắc | PASS |
| Q5 | Fail-open khi ledger không có dòng `signal` | `test_failopen_no_signal_row` | pass — `approve spec` không phát sinh nhắc mới khi ledger rỗng | PASS |
| Q6 | Không phá vỡ test suite hiện có | `python3 -m unittest discover -s tests -p "test_*.py"` | 448 passed, 0 fail (1 test cũ `test_compliance_protocol.py::test_prompt_clears_session_rows` được cập nhật assertion cho khớp hành vi mới có chủ đích — không phải regression, xem working log 20:23) | PASS |
| Q7 | doc_lint spec | `python3 scripts/doc_lint.py docs/tdq/spec/2026-08-04-approval-gate-bug.md` | exit 0 | PASS |

**Kết luận:** Q1–Q7 đều PASS. DoD đạt.

## Ghi chú bổ sung (ngoài Q1-Q7, kiểm tra chéo với plan §Definition of Done)

- Test regression T2.8 (`test_approve_not_swallowed_by_prior_edit_gate_remind`) —
  mô phỏng đúng bẫy dedupe do `edit_gate.py` đã chiếm mã `TDQ:APPROVE` trước —
  PASS, xác nhận `remind_force()` không bị `already_reminded()` nuốt.
- Test đối xứng cho nhánh `set phase=` (`test_setphase_silent_when_signal_matched`,
  T2.6) — PASS.
