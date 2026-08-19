---
name: tdq-build
description: Thực thi trọn plan TDQ đã duyệt trong một turn, chạy QC bám DoD, viết report rồi hỏi về commit. Dùng khi plan chế độ chuyên sâu vừa duyệt.
---

# TDQ Build — Implement → QC → Report

Load [tdq-conventions](../tdq-conventions/SKILL.md). Requires `plan_approved = true`.
This skill owns three phases: `implement` → `qc` → `report`.

## Hard rules (all three phases)

- **Enter build IN THE SAME TURN the user approves the plan, then run end-to-end in ONE
  turn.** Do not make the user send another message, do not stop halfway to ask "shall I
  continue". Stop only on a genuine scope change, a missing/ambiguous `implement_mode`, or a
  blocker only the user can clear.
- **Technical blocker → take the proposed option, do not ask.** When an option exists, TAKE
  IT, write one decision line plus the reason into the working log, and carry on. You may
  COMMIT ON YOUR OWN to clear a blocker (message describing the change, NO push, and list that
  commit in the report). Stop and ask only for: a spec/plan scope change, destructive or
  hard-to-undo work beyond a commit (DB schema change, deleting data, changing a public API
  contract), or missing input only the user holds.
- **Tick immediately.** Starting a task marks it `- [~]`; a passing test turns it into
  `- [x]` BEFORE the next task starts. Never batch ticks at the end of a turn. Three states:
  `[ ]` not started · `[~]` in progress · `[x]` done. The `[~]` mark is the only thing that
  tells an outsider (status line, user, another agent) where you stand when they look at the
  plan file mid-run.
- **The `(eNm)` estimate is metadata only.** A task may carry the minutes Claude estimated for
  itself right after the task code (`- [ ] **T1.1** (e12m) việc — Test: ...`). The plan's ETA =
  the sum of `eNm` over unfinished tasks. Keep it as-is when ticking, do not re-score midway,
  and it does NOT change the tick rule above — an `(e60m)` task ticks exactly like an `(e5m)`
  one. A task with no estimate is valid too.
- **Red → green.** Every task: run/write the check first (it must fail), then code, then rerun
  until it passes.
- **Language rules.** About to write/change a source file → open
  [references/rules/index.md](references/rules/index.md), look up the file extension, load
  `chung.md` plus exactly ONE language file. Never load the whole set for one language.
- **No placeholders.** Missing information at this stage means the analysis fell short — say
  so, do not stub.
- **If a subagent is running, wait it out**, or set a trigger to resume automatically. Never
  end the turn while one is still running.

## Part A — Implement (phase `implement`)

1. Read `implement_mode` from state and follow it exactly:
   - `main` (nhãn user thấy: "làm trực tiếp (inline implement)"): do EVERYTHING in this
     conversation yourself, but in the plan's cluster order, and still record the reason for
     each task you keep. The leader doctrine applies in every mode:
     [references/team-mode.md](references/team-mode.md).
   - `subagent` (nhãn user thấy: "giao trợ lý (sub-agent implement)"): you are the LEADER of a
     team. **Step 0 — before typing the first line of code: assign the WHOLE plan**
     (`python3 scripts/tdq_team.py phan-cong`, then `kiem-ke`). Then loop wave by wave.
     `cum` takes the next wave; `mo <task>` opens a branch + worktree per task.
     Call `tdq-implementer` for EVERY task of the wave IN ONE response — several Task calls in
     one response means they run concurrently. Mark the tasks you just handed out `[>]`.
     On receiving a report, run `kiem` then `hop`, tick `[x]` IMMEDIATELY, `don`, then back to
     `cum`. The default is DELEGATE. You may keep a task only when it matches exactly one group
     in the closed reason set (lookup table in `team-mode.md`); inventing a group outside that
     set makes `kiem-ke` exit non-zero. While a wave is running, the leader works the `tu_lam`
     tasks of that same wave.
     Full rules (decision table, delegation prompt template, ĐÚNG/SAI examples, self-check):
     [references/team-mode.md](references/team-mode.md) — **BẮT BUỘC mở đọc trước khi
     phân công; cấm làm theo trí nhớ.**
   The mode is what the USER said at approval. Missing mode, or you think another mode fits
   better → **DỪNG và HỎI**.

2. Loop per task (mode `subagent`: one round = exactly one `tdq-implementer` call):
   1. Report one line: which task is starting, and mark it `- [~]` in the plan.
      Mode `subagent`: a task handed to a sub-agent carries `- [>]` (several at once are
      allowed); `- [~]` is only for a task the LEADER does personally, and still only one.
   2. Task has a `Dùng:` block → LOAD that skill now (per the `Nạp` field), do exactly what
      `Để` says, and do not spill into what `Không dùng cho` lists. No block → skip this step.
   3. Red: run the task's check → confirm it fails (or write the failing test first).
   4. Code: the smallest change that satisfies the task, following the existing style.
      **Search before creating:** about to create a NEW file/class/function/constant → one
      round of `graphify query "<tên>"` or grep the name plus 2 synonyms; creating anyway after
      finding something close → record it in the plan task as
      `Tạo mới thay vì dùng <đường dẫn> vì <lý do>`. Creating without searching is a defect even
      when the tests are green.
   5. Green: rerun until it passes, running only **the module's tests** — the full suite is
      saved for exactly one run at QC. Paste the real output; never declare done unrun.
   6. Turn `- [~]` into `- [x]` for that task in the plan IMMEDIATELY — in mode `subagent` the
      main agent ticks as soon as the sub-agent's report arrives AND `hop` has completed,
      without waiting for the other tasks.
      (deliberate repetition — the original is in `## Hard rules` in this same file.)

3. All tasks done: run the full suite EXACTLY ONCE, then close the turn's books with ONE
   command
   `python3 "${CLAUDE_PROJECT_DIR}/.claude/tdq/scripts/tdq_finish.py" --files <file .md vừa sửa> --log "<task xong, file đổi, kết quả test>" --phase qc`
   — lint the right file, append the working log, set the phase, graphify: 4 jobs in 1 call.

Xong khi: mọi task trong plan đã tick `[x]` và test suite xanh.
Bước kế tiếp: lệnh `tdq_finish.py … --phase qc` ở mục 3 (đã set phase luôn).

## Part B — QC (phase `qc`)

The three execution steps — from counting DoD items to the fix loop on a FAIL — live in
[references/qc.md](references/qc.md) under `## Ba bước thi hành`. **BẮT BUỘC mở file đó và
đọc hết ba bước trước khi chạy hạng mục đầu tiên; cấm làm theo trí nhớ.** That same file also
carries the qc file template and the 3-fix-round cap.

Xong khi: mọi hạng mục QC PASS và có bằng chứng trong file qc.
Bước kế tiếp: `python3 "${CLAUDE_PROJECT_DIR}/.claude/tdq/scripts/tdq_state.py" set phase=report`.

## Part C — Report (phase `report`)

The four execution steps — from writing the report to asking the user about a commit — live in
[references/report-template.md](references/report-template.md) under `## Bốn bước thi hành`.
**BẮT BUỘC mở file đó và đọc hết bốn bước trước khi viết report; cấm làm theo trí nhớ.**
That same file also carries the report template and the verbatim commit question block.

Xong khi: report đã ghi và user đã được hỏi về commit.
Bước kế tiếp: `python3 "${CLAUDE_PROJECT_DIR}/.claude/tdq/scripts/tdq_state.py" set phase=idle`
(hoặc `reset` nếu user muốn xoá hẳn để sang request mới).
