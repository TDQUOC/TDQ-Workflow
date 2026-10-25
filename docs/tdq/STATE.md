# TDQ STATE (generated — do not hand-edit)
Updated: 2026-10-25T20:42:58+07:00 · Project: C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow · schema 3

| Field | Value |
|---|---|
| Request | 2026-10-25-2025-auto-update-plugin |
| Lane | quick |
| Phase | idle |
| Spec | (none) |
| Plan | docs/tdq/plan/2026-10-25-2025-auto-update-plugin.md — ⏳ awaiting approval |
| Quick approval | ✔ approved |
| Doc language | vi |
| Lean level | full |
| QC level | full |
| Run mode | (not settled) |

## Where we are
Finished, or no request opened yet. Forbidden: Overwriting an unfinished request without asking the user.

## What comes next
Wait for a new request from the user.
```
python3 scripts/tdq_state.py init <YYYY-MM-DD-HHMM-slug> <nhanh|chuyen-sau> [--lang <code>]
```
Done when: A new request is open

> Write state only through `python3 scripts/tdq_state.py …`. Unsure where you stand → run `tdq_state.py next`.
