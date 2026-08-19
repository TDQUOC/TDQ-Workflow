---
name: tdq-status
description: Báo trạng thái TDQ hiện tại (request, lane, phase, mode thực thi, ai đã duyệt gì) và bước kế tiếp chính xác. Dùng khi user hỏi workflow đang ở đâu.
---

# TDQ Status

Read the state and report in **tiếng Việt** (nhắc lại có chủ ý — bản gốc ở
`skills/tdq-conventions/SKILL.md`), ≤ 10 lines. Read-only: write nothing into state.

## Các bước

1. Run both commands (merged into ONE Bash call with `&&`):
   ```
   python3 "./scripts/tdq_state.py" next --brief
   python3 "./scripts/tdq_state.py" get
   ```
   A request is open → also run
   `python3 "./scripts/tdq_timing.py" status` (same Bash call) for the
   clock line: how long the current phase has run and how long the whole request took.
   That command only reads, it writes no state.
   Always use `next --brief` (121 characters) — drop `--brief` (1.350 characters) only when
   you truly need the full checklist of the phase, because that output is carried again on
   every later API call.
   No `active_request` yet → report "Chưa có request TDQ nào đang chạy." plus the step for
   opening a new request, then stop.

2. Report these items, one line each:
   - Request + lane + current phase.
   - `implement_mode`: the mode the user settled on (nothing yet → write "chưa chốt").
   - Spec: **đã duyệt** (with `spec_approved_at` and `spec_approved_by`) / **chờ duyệt** /
     — chưa có. Same for the plan (`plan_approved_by`) or quick (`quick_approved_by`),
     depending on the lane.
   - Spec approved → compare the current sha256 of `spec_file` against `spec_sha256`; a
     mismatch warns "spec đã đổi sau khi duyệt, cần duyệt lại".
   - Phase `implement`/`qc` → count `- [x]` over the total tasks in the plan file → progress.
   - The clock: print the `⏱ …` line returned by `tdq_timing.py status` verbatim (how long
     the current phase cost in wall/model time, and how long the request cost).

3. Close with the next step, taking the "Việc tiếp theo" and "Lệnh" lines verbatim from the
   `next` output. Waiting on an approval → also print:
   `➤ Duyệt: nhắn "duyệt <spec|plan|quick>" · Góp ý: nhắn trực tiếp`.
   The whole answer to the user follows the shared khuôn in
   [user-facing-block.md](../tdq-conventions/references/user-facing-block.md) — bold field
   labels, the `➤` line last.

Lost context (new session, another machine, another agent just did a phase for you) or a
state that drifted from disk → stop here and switch to
[tdq-check-status](../tdq-check-status/SKILL.md) to recover.

Xong khi: the user finishes reading and knows where things stand and what comes next.
Bước kế tiếp: the skill matching the current phase — see
[phases.md](../tdq-conventions/references/phases.md).
