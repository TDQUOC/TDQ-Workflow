---
name: tdq-start
description: Start the TDQ workflow for a new request - intake, lane recommendation (quick/full), state init. Use when the user gives a new task/feature/bug request.
---

# TDQ Start — Intake & Lane

Read [tdq-conventions](../tdq-conventions/SKILL.md) first. Act as a meticulous, experienced expert in the request's domain. All user-facing output in Vietnamese.

## Steps

1. **Capture the request.** Create `docs/tdq/requests/<slug>.md` (slug `YYYY-MM-DD-<kebab-title>`): original request verbatim + your first-read understanding (goal, scope guess, unknowns).

2. **Recommend a lane, then ask.** Summarize both options with a recommendation tailored to THIS request, then ask the user to choose:
   - **quick** — small/clear change (< ~1h, few files, low risk): analyze → mini plan in chat → approve → implement.
   - **full** — feature/complex/risky: analyze & interview → spec (duyệt) → plan (duyệt) → implement → QC → report.
   Format (VI): 2–3 dòng tóm tắt việc, 1 dòng đề xuất lane kèm lý do, rồi hỏi "Bạn muốn chạy lane nào: quick hay full?". Wait for the answer.

3. **Init state** with the chosen lane — MANDATORY, and before any plan/spec is presented:
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" init <slug> <quick|full>`
   Never print the approve line while state has no open request in the matching lane: the user would type the command and the gate would refuse it. The Stop hook blocks the turn if you do. Same rule when work resumes after a `reset` — reopen the request first.

4. **Route:**
   - **full** → set phase analyze (`... set phase=analyze`) and continue with [tdq-analyze](../tdq-analyze/SKILL.md).
   - **quick** → follow the quick flow below in the SAME conversation.

## Quick lane flow (mandatory gate)

1. Analyze briefly (read the code involved; interview only if something is genuinely unclear — never guess).
2. Present in chat a plan of **≤ 10 lines (VI)**: what will be done, files touched, quick validate/test steps.
3. Tell the user exactly: `➤ Để duyệt: gõ /tdq-workflow:tdq-approve quick · Góp ý: nhắn trực tiếp` — then STOP and wait. Edits outside `docs/` are blocked until approved.
4. After approval, the hook confirms. Then, in this order:
   1. Append the approved plan summary to `docs/workinglog/<today>.md` NOW (create the file if missing). Implementation stays blocked until this append happens.
   2. Implement end-to-end in one turn, run the quick validate/test, report the result briefly (VI).
5. Finish: append the outcome entry to the working log; ask the user whether to commit.
