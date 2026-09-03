# TDQ STATE (generated — do not hand-edit)
Updated: 2026-09-03T01:40:02+07:00 · Project: /Users/truongdinhquoc/Documents/TDQWorkflow · schema 3

| Field | Value |
|---|---|
| Request | 2026-09-03-0053-sua-luat-va-kiem-lsp-that |
| Lane | full |
| Phase | implement |
| Spec | docs/tdq/spec/2026-09-03-0053-sua-luat-va-kiem-lsp-that.md — ✔ approved |
| Plan | docs/tdq/plan/2026-09-03-0053-sua-luat-va-kiem-lsp-that.md — ✔ approved |
| Quick approval | (not applicable) |
| Doc language | vi |
| Run mode | main |

## Where we are
plan_approved = true and implement_mode is settled. Forbidden: Stopping midway; batching the ticks at the end of the turn; leaving several tasks marked [~]. Enforced, not merely advised: the Stop hook blocks the end of the turn with [TDQ:UNFINISHED] while a task is still open, and the only legal way out is `tdq_state.py tam-hoan --ly-do "<why>"`, whose reason is shown to the user.

## What comes next
Do the whole plan in one turn, mark [~] when a task starts, red→green, flip to [x] as soon as it passes.
```
python3 scripts/tdq_state.py set phase=qc
```
Done when: Every task in the plan is ticked [x]

> Write state only through `python3 scripts/tdq_state.py …`. Unsure where you stand → run `tdq_state.py next`.
