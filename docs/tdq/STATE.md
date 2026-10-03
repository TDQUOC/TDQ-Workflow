# TDQ STATE (generated — do not hand-edit)
Updated: 2026-10-03T10:43:38+07:00 · Project: C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow · schema 3

| Field | Value |
|---|---|
| Request | 2026-10-03-0732-do-truoc-lam-mot-turn |
| Lane | full |
| Phase | idle |
| Spec | docs/tdq/spec/2026-10-03-0732-do-truoc-lam-mot-turn.md — ✔ approved |
| Plan | docs/tdq/plan/2026-10-03-0732-do-truoc-lam-mot-turn.md — ✔ approved |
| Quick approval | (not applicable) |
| Doc language | vi |
| Lean level | full |
| QC level | full |
| Run mode | subagent |

## Where we are
Finished, or no request opened yet. Forbidden: Overwriting an unfinished request without asking the user.

## What comes next
Wait for a new request from the user.
```
python3 scripts/tdq_state.py init <YYYY-MM-DD-HHMM-slug> <nhanh|chuyen-sau> [--lang <code>]
```
Done when: A new request is open

> Write state only through `python3 scripts/tdq_state.py …`. Unsure where you stand → run `tdq_state.py next`.
