# TDQ STATE (generated — do not hand-edit)
Updated: 2026-09-03T15:20:39+07:00 · Project: /Users/truongdinhquoc/Documents/TDQWorkflow · schema 3

| Field | Value |
|---|---|
| Request | 2026-09-03-1440-kiem-tuong-thich-3-host |
| Lane | full |
| Phase | idle |
| Spec | docs/tdq/spec/2026-09-03-1440-kiem-tuong-thich-3-host.md — ✔ approved |
| Plan | docs/tdq/plan/2026-09-03-1440-kiem-tuong-thich-3-host.md — ✔ approved |
| Quick approval | (not applicable) |
| Doc language | vi |
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
