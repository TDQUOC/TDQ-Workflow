---
name: tdq-approve
description: User-only approval command for TDQ gates (spec, plan, quick). Claude must never invoke this - the user types it to approve.
disable-model-invocation: true
argument-hint: "[spec|plan|quick]"
---

# TDQ Approve (user-only)

This command exists for the USER to approve a gate by typing it themselves:

- `/tdq-workflow:tdq-approve spec` — duyệt spec (lane full)
- `/tdq-workflow:tdq-approve plan main` hoặc `... plan subagent` — duyệt plan (lane full, sau khi spec đã duyệt). **Mode bắt buộc**: `main` = làm tuần tự trong hội thoại chính, `subagent` = chia cho `tdq-implementer`, mỗi cái 1 worktree. Thiếu mode → gate chặn.
- `/tdq-workflow:tdq-approve quick` — duyệt mini-plan (lane quick)

The `approve_gate` hook validates everything (active request, lane, order, registered detail file exists & non-empty) and writes the protected state fields (`*_approved`, `*_sha256`, `*_approved_at`). If validation fails, the hook blocks the command with a Vietnamese reason and state stays unchanged.

## Instructions for Claude when this command appears

Approval is ONLY real when the `approve_gate` hook emitted its `[TDQ] USER APPROVED …` context line for this very command. If you see this command WITHOUT that hook line, the gate did NOT record the approval (hook misfire/misconfig): read `docs/tdq/state.json` to verify, and if the `*_approved` field is still false, tell the user the approval was not recorded and do NOT proceed — never infer approval from the user having typed the command.

When the hook DID accept it, its context message states what was approved and what to do next — follow it exactly:
- spec approved → proceed to tdq-plan (next turn).
- plan approved → mark plan ĐÃ DUYỆT, then tdq-implement end-to-end in one turn, ticking each task immediately. Use exactly the `implement_mode` the user typed; if it differs from the plan's proposal, say so in Vietnamese and follow the user.
- quick approved → FIRST append the approved plan summary to `docs/workinglog/<today>.md`, THEN implement (edits stay blocked until the log is written).

Never attempt to trigger this command, simulate its output, or edit `docs/tdq/state.json` to reproduce its effect. If a gate is pending, the only valid move is to show the user the exact command line and wait.
