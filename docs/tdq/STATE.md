# TDQ STATE (generated — do not hand-edit)
Updated: 2026-10-03T11:41:51+07:00 · Project: C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow · schema 3

| Field | Value |
|---|---|
| Request | 2026-10-03-1101-nghien-cuu-nen-context |
| Lane | full |
| Phase | implement |
| Spec | docs/tdq/spec/2026-10-03-1101-nghien-cuu-nen-context.md — ✔ approved |
| Plan | docs/tdq/plan/2026-10-03-1101-nghien-cuu-nen-context.md — ✔ approved |
| Quick approval | (not applicable) |
| Doc language | vi |
| Lean level | full |
| QC level | full |
| Run mode | subagent |

## Where we are
plan_approved = true and implement_mode = subagent. Forbidden: Doing a task the map marked as dispatched yourself on main; merging before `check` passes; leaving several tasks marked [~].

## What comes next
Assign the WHOLE plan first (step 0), then release wave by wave to sub-agents, merging one wave before releasing the next — the leader only does what cannot be split.
```
python3 scripts/tdq_state.py set phase=qc
```
Done when: Every task in the plan is ticked [x] and no leftover worktree remains

> Write state only through `python3 scripts/tdq_state.py …`. Unsure where you stand → run `tdq_state.py next`.
