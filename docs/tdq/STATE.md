# TDQ STATE (generated — do not hand-edit)
Updated: 2026-09-05T13:07:31+07:00 · Project: /Users/truongdinhquoc/Documents/TDQWorkflow · schema 3

| Field | Value |
|---|---|
| Request | 2026-09-05-1241-khong-co-tavily-web-search |
| Lane | quick |
| Phase | idle |
| Spec | (none) |
| Plan | docs/tdq/plan/2026-09-05-1241-khong-co-tavily-web-search.md — ⏳ awaiting approval |
| Quick approval | ✔ approved |
| Doc language | vi |
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
