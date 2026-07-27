---
name: tdq-approve
description: User-only approval command for TDQ gates (spec, plan, quick). Claude must never invoke this - the user types it to approve.
disable-model-invocation: true
argument-hint: "[spec|plan|quick]"
---

# TDQ Approve (user-only)

This command exists for the USER to approve a gate by typing it themselves:

- `/tdq-workflow:tdq-approve spec` — duyệt spec (lane full)
- `/tdq-workflow:tdq-approve plan` — duyệt plan (lane full, sau khi spec đã duyệt)
- `/tdq-workflow:tdq-approve quick` — duyệt mini-plan (lane quick)

The `approve_gate` hook validates everything (active request, lane, order, registered detail file exists & non-empty) and writes the protected state fields (`*_approved`, `*_sha256`, `*_approved_at`). If validation fails, the hook blocks the command with a Vietnamese reason and state stays unchanged.

## Instructions for Claude when this command appears

You only ever see this AFTER the user typed it and the hook accepted it. The hook's context message states what was approved and what to do next — follow it exactly:
- spec approved → proceed to tdq-plan (next turn).
- plan approved → mark plan ĐÃ DUYỆT, then tdq-implement end-to-end in one turn, ticking each task immediately.
- quick approved → FIRST append the approved plan summary to `docs/workinglog/<today>.md`, THEN implement (edits stay blocked until the log is written).

Never attempt to trigger this command, simulate its output, or edit `docs/tdq/state.json` to reproduce its effect. If a gate is pending, the only valid move is to show the user the exact command line and wait.
