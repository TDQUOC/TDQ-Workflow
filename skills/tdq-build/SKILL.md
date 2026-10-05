---
name: tdq-build
description: Run an approved TDQ plan end to end in one turn, QC it against the DoD, write the report, then ask about the commit. Use right after a deep-pipeline plan is approved.
---

# TDQ Build — Implement → QC → Report
<!-- muc-luc-dong:
  Hard rules (all three phases)=15-76 · Part A — Implement (phase `implement`)=77-144 ·
  Part B — QC (phase `qc`)=145-161 · Part C — Report (phase `report`)=162
-->

Load [tdq-conventions](../tdq-conventions/SKILL.md). Requires `plan_approved = true`.
This skill owns three phases: `implement` → `qc` → `report`.

## Hard rules (all three phases)

- **Enter build IN THE SAME TURN the user approves the plan, then run end-to-end in ONE
  turn.** Do not make the user send another message, do not stop halfway to ask "shall I
  continue". The ONLY stops are the four `pause --loai` kinds below, plus a missing/ambiguous
  `implement_mode`.
- **The end of the turn is gated, not merely asked for.** While the phase is `implement` and
  the plan still has an open task, the Stop hook refuses to close the turn with
  `[TDQ:UNFINISHED]` and pushes you to keep going. A real force-majeure stop → run
  `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" pause --loai <kind> --ly-do "<why>"`,
  TELL THE USER that reason in chat, and only then end the turn; `resume` clears it when the
  run resumes. The kinds are a CLOSED list, `pause` refuses others: `mat-truy-cap` (lost
  access, broken tool, no workaround) · `pha-huy` (destructive or hard-to-undo beyond a commit:
  data deletion, DB schema, public API, push/publish) · `dau-vao-user` (secret, account, payment,
  adding/dropping a spec §2 output) · `tran-qc` (QC fix loop hit its 3-round cap).
- **An unreachable spec threshold is NOT a stop.** Apply that §6 row's fallback column (none →
  the option you would recommend), record it with the state command `lech add` (its flags:
  `--q --nguong --do --chon --ly-do`), finish the plan; the report asks for approval of each.
  Asking mid-run (a question popup too) is the failure this removes; `[TDQ:ASK]` reminds you.
- **Technical blocker → take the proposed option, do not ask.** When an option exists, TAKE
  IT, write one decision line plus the reason into the working log, and carry on. You may
  COMMIT ON YOUR OWN to clear a blocker (message describing the change, NO push, and list that
  commit in the report).
- **Tick immediately.** Starting a task marks it `- [~]`; a passing test turns it into
  `- [x]` BEFORE the next task starts. Never batch ticks at the end of a turn. Three states:
  `[ ]` not started · `[~]` in progress · `[x]` done. The `[~]` mark is the only thing that
  tells an outsider (status line, user, another agent) where you stand when they look at the
  plan file mid-run.
- **The `(eNm)` estimate is metadata only.** A task may carry the minutes Claude estimated for
  itself right after the task code (`- [ ] **T1.1** (e12m) <the work> — Test: ...`). The plan's ETA =
  the sum of `eNm` over unfinished tasks. Keep it as-is when ticking, do not re-score midway,
  and it does NOT change the tick rule above — an `(e60m)` task ticks exactly like an `(e5m)`
  one. A task with no estimate is valid too.
- **Red → green.** Every task: run/write the check first (it must fail), then code, then rerun
  until it passes.
- **Build less than asked: climb the ladder.** Stop at the first rung that holds. Rung 1: does
  this thing need to exist at all — a file, a class, a function, a constant, a config key, a
  dependency, an abstraction layer? A need you inferred rather than read is speculative, so
  skip it and say so in one line. Rung 2: is it already in this codebase? The ladder only ever
  chooses among options that ALREADY pass the complexity floor (cyclomatic ≤ 10, cognitive
  ≤ 15), and no comment or declared "known ceiling" buys an exception to it. The full 7 rungs,
  the intensity table per `muc_gat` and the RIGHT/WRONG examples live in
  [references/rules/chung.md](references/rules/chung.md) between `<!-- luat-gon:bat-dau -->`
  and `<!-- luat-gon:ket-thuc -->`.
- **Make it run first, refactor after.** Step 1 is code that runs; tidying the project up comes
  after the feature is done and behaving. Write the simplest, most direct code you can —
  minimal, with no namespace, no class and no function the feature does not need, so the path
  of one feature never reads like a spider's web.
- **Language rules.** About to write/change a source file → open
  [references/rules/index.md](references/rules/index.md), look up the file extension, load
  `chung.md` plus exactly ONE language file. Never load the whole set for one language.
- **LSP + lumen together, before grep, on every search of a code symbol.** <!-- i18n-allow: canonical rule sentence in the default language -->
  The 4-layer search order is a MANDATORY rule (BẮT BUỘC) in every phase. Read sections 1
  and 2 of `skills/tdq-setup/references/uu-tien-tim-kiem.md` — the line-index block at the
  top of that file gives the exact line range, so the whole file never has to be read.
  It is a soft rule: reaching for grep on a symbol without trying LSP first is a QC defect, not a
  blocked edit. The `mcp__lsp__*` tools are missing → say so in one line, then fall through.
- **No placeholders.** Missing information at this stage means the analysis fell short — say
  so, do not stub.
- **If a subagent is running, wait it out**, or set a trigger to resume automatically. Never
  end the turn while one is still running.

## Part A — Implement (phase `implement`)

1. Read `implement_mode` from state and follow it exactly:
   - `main` (label the user sees: "làm trực tiếp (inline implement)"): do EVERYTHING in this <!-- i18n-allow: user-facing mode label -->
     conversation yourself, but in the plan's cluster order, and still record the reason for
     each task you keep. The leader doctrine applies in every mode:
     [references/team-mode.md](references/team-mode.md); the worktree ledger is in the tier-1 sibling
     [references/team-mode-tra-cuu.md](references/team-mode-tra-cuu.md).
   - `subagent` (label the user sees: "giao trợ lý (sub-agent implement)"): you are the LEADER of a <!-- i18n-allow: user-facing mode label -->
     team. **Step 0 — before typing the first line of code: assign the WHOLE plan**
     (`python3 scripts/tdq_team.py assign`, then `audit`). Then loop wave by wave.
     `wave` takes the next wave; `open <task>` opens a branch + worktree per task.
     Call `tdq-implementer` for EVERY task of the wave IN ONE response — several Task calls in
     one response means they run concurrently. Mark the tasks you just handed out `[>]`.
     On receiving a report, run `check` then `merge`, tick `[x]` IMMEDIATELY, `clean`, then back to
     `wave`. The default is DELEGATE. You may keep a task only when it matches exactly one group
     in the closed reason set (lookup table in `team-mode.md`); inventing a group outside that
     set makes `audit` exit non-zero. While a wave is running, the leader works the `tu_lam`
     tasks of that same wave.
     Full rules (decision table, delegation prompt template, RIGHT/WRONG examples, self-check):
     [references/team-mode.md](references/team-mode.md) — read the sections you are about to
     act on, through the line index at the top of that file; working from memory is banned.
   - `codex` (label the user sees: "giao Codex (codex implement)"): you stay the LEADER and <!-- i18n-allow: user-facing mode label -->
     Codex
     is a hired hand. Four beats per task, none skipped: you write the failing test, you RUN
     it and see red, Codex makes it green inside the declared file zone, then you run the test
     again and audit the zone. The commands are `scripts/tdq_codex.py` (one run per task) and
     `scripts/tdq_vungfile.py` (mark, audit, rollback). Codex never writes the test that
     measures it, and green alone is not done — a task that touched a file outside its zone
     is a FAIL. Never describe this mode as "the fast mode": measured, it lands level with
     `main`, and what it changes is who writes the code.
     Full rules (prompt template, result shape, digest threshold, self-check):
     [references/codex-mode.md](references/codex-mode.md) — read the sections you are about to
     act on, through the line index at the top of that file; working from memory is banned.
   The mode is what the USER said at approval. Missing mode, or you think another mode fits
   better → **STOP and ASK**.

2. Loop per task (mode `subagent`: one round = exactly one `tdq-implementer` call):
   1. Report one line: which task is starting, and mark it `- [~]` in the plan.
      Mode `subagent`: a task handed to a sub-agent carries `- [>]` (several at once are
      allowed); `- [~]` is only for a task the LEADER does personally, and still only one.
   2. Task has a `Dùng:` block → LOAD that skill now (per the `Nạp` field), do exactly what <!-- i18n-allow: canonical contract field names -->
      `Để` says, and do not spill into what `Không dùng cho` lists. No block → skip this step. <!-- i18n-allow: canonical contract field names -->
   3. Red: run the task's check → confirm it fails (or write the failing test first).
   4. Code: the smallest change that satisfies the task, following the existing style.
      **Search before creating:** about to create a NEW file/class/function/constant → first
      `mcp__lsp__find_symbol` on the name plus 2 synonyms. The compiler's index answers
      "does this exist already" exactly. LSP comes back empty → then one round of
      `graphify query "<name>"` or grep the name plus 2 synonyms; creating anyway after
      finding something close → record it in the plan task as
      `Tạo mới thay vì dùng <đường dẫn> vì <lý do>`. Creating without searching is a defect even <!-- i18n-allow: canonical note written into the plan -->
      when the tests are green.
   5. Green: rerun until it passes with `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_test.py" vung-cham`
      — the touched zone PLUS its blast radius (falls back to the full suite by itself when the
      radius is wide). Paste the real output; never declare done unrun.
   6. Turn `- [~]` into `- [x]` for that task in the plan IMMEDIATELY — in mode `subagent` the
      main agent ticks as soon as the sub-agent's report arrives AND `merge` has completed,
      without waiting for the other tasks.
      (deliberate repetition — the original is in `## Hard rules` in this same file.)

3. All tasks done: do NOT run the full suite here — QC-F1 (`tdq_test.py tron-bo`) is that run.
   Close the turn's books with ONE command
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_finish.py" --files <edited .md files> --log "<tasks done, files changed, test result>" --phase qc`
   — lint the right file, append the working log, set the phase, graphify: 4 jobs in 1 call.

Done when: every task in the plan is ticked `[x]` and the test suite is green.
Next step: phase `qc` — the `tdq_finish.py … --phase qc` command of item 3 sets it, then Part B.

## Part B — QC (phase `qc`)

**How much QC runs comes from `muc_qc`**, the level the user settled before the spec — the
table of levels is in [references/qc.md](references/qc.md). Smoke and runtime checks (level
`ultra`) run under a **120-second cap each**; hitting the cap is a FAIL, and raising the cap
needs the user's yes, never your own call.

The three execution steps — from counting DoD items to the fix loop on a FAIL — live in
[references/qc.md](references/qc.md) under `## The three execution steps` — read THAT section
before running the first item, through the line index at the top of the file; working from memory
is banned. The same file also carries the qc file template and the 3-fix-round cap, each its own
section in that index, so nothing here needs the whole file in context at once.

Done when: every QC item PASSes and its evidence sits in the qc file.
Next step: phase `report` — `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=report`,
then Part C below.

## Part C — Report (phase `report`)

The execution steps — from writing the report through asking about the commit to merging the
request branch back — live in
[references/report-template.md](references/report-template.md) under `## The execution steps`.
Read THAT section before writing the report, through the line index at the top of the file.
Working from memory is banned. The report template and the verbatim commit question block are
separate sections in the same index, fetched when you reach them.

Done when: the report is written, the user has been asked about the commit, and the request
branch has been merged back into `nhanh_goc`.
Next step: phase `idle` — `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=idle`
(or `reset` when the user wants the slate wiped for a new request). The request ends there.
