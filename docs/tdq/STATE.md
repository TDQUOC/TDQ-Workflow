# TDQ STATE (generated — do not hand-edit)
Updated: 2026-11-03T00:05:25+07:00 · Project: C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow · schema 3

| Field | Value |
|---|---|
| Request | (none) |
| Lane | (not chosen) |
| Phase | idle |
| Spec | (none) |
| Plan | (none) |
| Quick approval | (not applicable) |
| Doc language | vi |
| Lean level | ultra |
| QC level | full |
| Run mode | (not settled) |

## Where we are
No TDQ request is open. Forbidden: Editing code before a request is open.

## What comes next
Ask the user to pick a lane, then open a new request.
```
python3 scripts/tdq_state.py init <YYYY-MM-DD-HHMM-slug> <nhanh|chuyen-sau> [--lang <code>]
```
Done when: state.json has active_request and lane

> Write state only through `python3 scripts/tdq_state.py …`. Unsure where you stand → run `tdq_state.py next`.
