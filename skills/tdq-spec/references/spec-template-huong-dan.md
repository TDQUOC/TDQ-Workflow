# Checking a spec before presenting it

Split out of `spec-template.md` on 2026-10-02 (954 tokens). The three sections below are SELF-CHECK
work, done once at the end of phase `spec`. None of it is copied into the spec, so none of it has
to sit in context while the spec is written.

## §6 holds the CONDITION, never the check command

The spec is sealed with a sha256 when the user approves it, while **a concrete check
command is only correct AFTER the code exists** — test file name, selection flag, function
name. Write those into the spec and a wrong name found at QC time forces a re-approval,
even though the intent did not change by a single word. Measured in 2 of 7 cases in
`docs/tdq/reports/2026-08-18-2050-spec-doi-sau-khi-duyet.md`.

So: **the spec carries the PASS CONDITION, the plan carries the CHECK COMMAND.** The plan
is not sealed, so renaming a test file there is everyday work and touches no approval gate.

| Written in the spec (RIGHT) | Written in the spec (WRONG — move it to the plan) |
|---|---|
| editing a bookkeeping line leaves the sha alone, editing a numbered section changes it | `pytest tests/test_state.py -q -k sha` green |
| a new spec carrying a check command is blocked by the linter, an old spec still passes | `pytest tests/test_doc_lint.py -q -k r11` green |

Rule **R11** of `doc_lint.py` guards exactly this, and applies only to specs from
2026-08-19 onward.

## Check before presenting

- Every output in §2 has at least one QC item in §6.
- §6 holds no `tests/...` path and no `-k` flag — the check command lives in the plan.
- §1b is present: every workflow step/phase says `CÓ` or `BỎ`, with the reason. <!-- i18n-allow: canonical spec section names -->
- §2b is present in lane full: one row per module, no two modules declaring one path.
- §3b is present: one row per skill marked `DÙNG` or `NỀN`, everything else merged into the <!-- i18n-allow: canonical spec section names -->
  summary row `Đã xét <N> skill khác` — machine-checked by `doc_lint.py` rule R8. <!-- i18n-allow: canonical spec section names -->
- A PASS condition in §6 is measurable by a command, not by feel.
- §7 is empty.
- No sentence uses a vague word ("phù hợp", "tối ưu", "nếu cần") without a concrete <!-- i18n-allow: the banned words are matched literally by doc_lint -->
  threshold beside it.

## The scope checklist — every box answered before presenting

| Question | The answer must live in |
|---|---|
| What does this work PRODUCE? | §1 mục tiêu + §2 bảng đầu ra <!-- i18n-allow: canonical spec section names --> |
| Are the areas dropped at the scope round written down? | §1 mục NGOÀI phạm vi <!-- i18n-allow: canonical spec section names --> |
| What is NEW compared with what exists today? | §3 cách tiếp cận <!-- i18n-allow: canonical spec section names --> |
| Which file/command/screen exactly is the output? | §2 cột đường dẫn/vị trí <!-- i18n-allow: canonical spec section names --> |
| Is a model needed (name, where it runs, cost)? | §1 phạm vi + §5 ràng buộc <!-- i18n-allow: canonical spec section names --> |
| Is any download/install needed? | §5 ràng buộc — ghi rõ tên gói và bản <!-- i18n-allow: canonical spec section names --> |
| How is QC/test/validate done? | §6 bảng QC + DoD <!-- i18n-allow: canonical spec section names --> |

One box still unanswered → the spec is not ready to present, go back to phase analyze.
