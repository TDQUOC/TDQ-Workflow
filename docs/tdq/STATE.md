# TDQ STATE (generated — do not hand-edit)
Updated: 2026-11-03T19:53:37+07:00 · Project: C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow · schema 3

| Field | Value |
|---|---|
| Request | 2026-11-03-1420-phoi-hop-cong-cu |
| Lane | full |
| Phase | report |
| Spec | docs/tdq/spec/2026-11-03-1420-phoi-hop-cong-cu.md — ✔ approved |
| Plan | docs/tdq/plan/2026-11-03-1420-phoi-hop-cong-cu.md — ✔ approved |
| Quick approval | (not applicable) |
| Doc language | vi |
| Lean level | ultra |
| QC level | ultra |
| Run mode | subagent |

## Where we are
QC has PASSed. Forbidden: Committing or pushing before the user asks for it.

## What comes next
Write a short report (10-20 lines recommended, no hard limit) then ask the user about committing.
```
python3 scripts/tdq_state.py set phase=idle
```
Done when: The report is written and the user has been asked about committing

> Write state only through `python3 scripts/tdq_state.py …`. Unsure where you stand → run `tdq_state.py next`.
