# TDQ STATE (generated — do not hand-edit)
Updated: 2026-11-08T13:21:41+07:00 · Project: C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow · schema 3

| Field | Value |
|---|---|
| Request | 2026-11-08-1207-va-lo-hong-edit-gate-3-tang |
| Lane | full |
| Phase | idle |
| Spec | docs/tdq/spec/2026-11-08-1207-va-lo-hong-edit-gate-3-tang.md — ✔ approved |
| Plan | docs/tdq/plan/2026-11-08-1207-va-lo-hong-edit-gate-3-tang.md — ✔ approved |
| Quick approval | (not applicable) |
| Doc language | vi |
| Lean level | ultra |
| QC level | full |
| Run mode | main |

## Where we are
Finished, or no request opened yet. Forbidden: Overwriting an unfinished request without asking the user.

## What comes next
Wait for a new request from the user.
```
python3 scripts/tdq_state.py init <YYYY-MM-DD-HHMM-slug> <nhanh|chuyen-sau> [--lang <code>]
```
Done when: A new request is open

> Write state only through `python3 scripts/tdq_state.py …`. Unsure where you stand → run `tdq_state.py next`.
