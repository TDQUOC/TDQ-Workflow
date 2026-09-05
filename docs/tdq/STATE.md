# TDQ STATE (generated — do not hand-edit)
Updated: 2026-09-05T13:00:18+07:00 · Project: /Users/truongdinhquoc/Documents/TDQWorkflow · schema 3

| Field | Value |
|---|---|
| Request | 2026-09-05-1241-khong-co-tavily-web-search |
| Lane | quick |
| Phase | report |
| Spec | (none) |
| Plan | docs/tdq/plan/2026-09-05-1241-khong-co-tavily-web-search.md — ⏳ awaiting approval |
| Quick approval | ✔ approved |
| Doc language | vi |
| Run mode | (not settled) |

## Where we are
lane = quick. Forbidden: Implementing before the working log is written; batching the ticks at the end of the turn or leaving several tasks marked [~]; closing the job with a red test or a known bug; running set phase=idle after the 3-round fix cap without telling the user.

## What comes next
Analyse → a mini spec/plan merged into one file → wait for approval → write the working log FIRST → implement → QC against the DoD (ON by default) → a fix round if it FAILs.
```
python3 scripts/tdq_state.py approve quick [--no-qc] --by "<the user's sentence verbatim>"
```
Done when: quick_approved = true, the log is written, the plan's QC section exists (evidence or the skipped-at-user's-request line), no red test is left, phase is back to idle

> Write state only through `python3 scripts/tdq_state.py …`. Unsure where you stand → run `tdq_state.py next`.
