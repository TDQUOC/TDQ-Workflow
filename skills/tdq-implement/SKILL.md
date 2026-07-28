---
name: tdq-implement
description: Execute an approved TDQ plan end-to-end in one turn - tick each task immediately when its test passes, never stop midway. Full lane, after plan approval.
---

# TDQ Implement

Read [tdq-conventions](../tdq-conventions/SKILL.md). Requires `plan_approved` (hooks enforce). User-facing updates in VI.

## Hard rules
- **End-to-end in ONE turn.** Never stop mid-plan to ask "shall I continue". Stop only for a genuine scope change, a missing/ambiguous `implement_mode` (see below), or a blocker only the user can resolve.
- **Tick immediately.** The moment a task's test/validate passes, edit the plan file and mark that task `- [x]` BEFORE starting the next task. Never batch ticks for later — "several tasks done, none ticked" is a rule violation.
- **Red → green.** For each task: run/write its check first (expect fail), implement, re-run until pass.
- **No placeholders.** Missing info at this stage means analysis failed — surface it, don't stub it.
- **Waiting on a subagent?** Wait for it or set up an automatic continuation trigger — do not end the turn while it runs.

## Mode (state `implement_mode` — decided by the USER, never by you)
There is NO default mode. Read `implement_mode` from state and follow it:
- `main`: implement in this conversation, task by task in plan order.
- `subagent`: spawn `tdq-implementer` agents, each in its own git worktree (branch names must not start with `claude|antigravity|gemini|codex`). Merge worktrees back and verify the merge; remove stale worktrees.

The mode comes from the `Mode thực thi:` line of the plan the user approved — the approve gate parses it there and writes it into state. Setting `implement_mode` yourself changes nothing: the gate overwrites it from the approved plan. If it is null, or you want a different mode than the approved one, STOP and ask the user; a mode change means revising the plan line and getting the plan approved again.

## Per-task loop
1. Announce (1 dòng VI) which task is starting.
2. Red: run the task's test/validate → confirm it fails (or write the failing test).
3. Implement the smallest complete change that satisfies the task. Follow existing code style.
4. Green: re-run until pass. Paste the actual result — never claim untested success.
5. Tick `- [x]` for that task in `docs/tdq/plan/<slug>.md` NOW.

## Built-product requirements (from spec)
- Logging service ON by default: timestamps, level, enough context to debug production issues; document how to adjust verbosity.
- Unit tests per component, runnable by one command recorded in the plan.

## On completion
1. Run the full test suite / DoD checks from the plan.
2. Append the working log entry (END of `docs/workinglog/<today>.md`): tasks done, files, test results. Run graphify update if installed.
3. `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=qc`, then continue with [tdq-qc](../tdq-qc/SKILL.md).
