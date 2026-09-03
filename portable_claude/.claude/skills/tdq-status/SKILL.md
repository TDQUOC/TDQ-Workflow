---
name: tdq-status
description: Report the current TDQ state (request, lane, phase, execution mode, who approved what) and the exact next step. Use when the user asks where the workflow stands.
---

# TDQ Status

Read the state and report in the user's document language `doc_lang` (deliberate repetition —
the original is `skills/tdq-conventions/SKILL.md`), ≤ 10 lines. Read-only: write nothing into state.

## Steps

1. Run both commands (merged into ONE Bash call with `&&`):
   ```
   python3 "${CLAUDE_PROJECT_DIR}/.claude/tdq/scripts/tdq_state.py" next --brief
   python3 "${CLAUDE_PROJECT_DIR}/.claude/tdq/scripts/tdq_state.py" get
   ```
   A request is open → also run
   `python3 "${CLAUDE_PROJECT_DIR}/.claude/tdq/scripts/tdq_timing.py" status` (same Bash call) for the
   clock line: how long the current phase has run and how long the whole request took.
   That command only reads, it writes no state.
   Always use `next --brief` (121 characters) — drop `--brief` (1.350 characters) only when
   you truly need the full checklist of the phase, because that output is carried again on
   every later API call.
   No `active_request` yet → report that no TDQ request is running, plus the step for opening
   a new request, then stop.

2. Report these items, one line each:
   - Request + lane + current phase.
   - `implement_mode`: the mode the user settled on (nothing yet → say it is not settled).
   - Spec: **approved** (with `spec_approved_at` and `spec_approved_by`) / **waiting for
     approval** / not written yet. Same for the plan (`plan_approved_by`) or quick
     (`quick_approved_by`), depending on the lane.
   - Spec approved → compare the current sha256 of `spec_file` against `spec_sha256`; a
     mismatch warns that the spec changed after approval and must be approved again.
   - Phase `implement`/`qc` → count `- [x]` over the total tasks in the plan file → progress.
   - The clock: print the `⏱ …` line returned by `tdq_timing.py status` verbatim (how long
     the current phase cost in wall/model time, and how long the request cost).

3. Close with the next step, taking the "next job" and "command" lines verbatim from the
   `next` output. Waiting on an approval → also print: <!-- i18n-allow: the approval line is printed verbatim -->
   `➤ Duyệt: nhắn "duyệt <spec|plan|quick>" · Góp ý: nhắn trực tiếp`. <!-- i18n-allow: user-facing line printed verbatim -->
   The whole answer to the user follows the shared template in
   [user-facing-block.md](../tdq-conventions/references/user-facing-block.md) — bold field
   labels, the `➤` line last.

Lost context (new session, another machine, another agent just did a phase for you) or a
state that drifted from disk → stop here and switch to
[tdq-check-status](../tdq-check-status/SKILL.md) to recover.

Done when: the user finishes reading and knows where things stand and what comes next.
Next step: the phase does not change — reporting status moves nothing. Load the skill owning the
phase state is already in, per [phases.md](../tdq-conventions/references/phases.md).
