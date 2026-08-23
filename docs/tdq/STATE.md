# TDQ STATE (generated — do not hand-edit)
Updated: 2026-08-23T10:36:45+07:00 · Project: /Users/truongdinhquoc/Documents/TDQWorkflow · schema 3

| Field | Value |
|---|---|
| Request | 2026-08-23-0052-skill-tdq-lsp-setup |
| Lane | full |
| Phase | report |
| Spec | docs/tdq/spec/2026-08-23-0052-skill-tdq-lsp-setup.md — ✔ approved |
| Plan | docs/tdq/plan/2026-08-23-0052-skill-tdq-lsp-setup.md — ✔ approved |
| Quick approval | (not applicable) |
| Doc language | vi |
| Run mode | main |

## Where we are
QC has PASSed. Forbidden: Committing or pushing before the user asks for it.

## What comes next
Write a short report (10-20 lines recommended, no hard limit) then ask the user about committing.
```
python3 scripts/tdq_state.py set phase=idle
```
Done when: The report is written and the user has been asked about committing

> Write state only through `python3 scripts/tdq_state.py …`. Unsure where you stand → run `tdq_state.py next`.
