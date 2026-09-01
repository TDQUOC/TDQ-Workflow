# Express pipeline — detail

Express differs from the deep pipeline by **merging the documents and merging the
gates**, not by dropping thought. Analysis, a web search whenever there is an external
unknown, and an interview whenever a question can still change the outcome are all KEPT.
Drop them only when the work is purely internal or already fully clear — and say why.

| Step | Deep | Express |
|---|---|---|
| Analysis + reading the code | yes | yes |
| Web search | yes (2–4 queries) | yes when an external unknown exists |
| Scope round | conditional, on the trigger signs | identical — the same set of signs |
| Interview | loops until nothing is vague | when a question can still change the outcome |
| Documents | brief + spec + plan | **1 file** `docs/tdq/plan/<slug>.md` |
| Approval gates | 2 (spec, plan) + 1 question on the run mode | **1** (the express approval) |
| QC | file `qc/<slug>.md` | one check per DoD line, written into the plan's `## QC` section (ON by default) |
| Fix round on FAIL | 3-round cap, written into `qc/` | 3-round cap, written into the plan |
The scope round in express shares the rule in [scope-round.md](scope-round.md): one trigger
sign met → ask about areas + context first; none met → write one SKIP reason line into the
mini-plan under `## Phạm vi` and move on. <!-- i18n-allow: canonical name in the default language -->

## Table of contents

- The nine execution steps
- Reading the graph at step 1 (analysis)
- Mini spec/plan template (≤ 40 lines)
- The block that presents the mini-plan to the user
- The tick rule — `[ ]` · `[~]` · `[x]`
- QC in the express pipeline
- The fix round

## The nine execution steps

This is the whole of Part C of [SKILL.md](../SKILL.md) — moved here so the skill body does
not load this branch on every call. Entering the express pipeline you **MUST** read all nine
steps below before doing step 1; working from memory is banned.

1. **Analyse.** Read exactly the code involved. External unknown (library, API, version) →
   web search through `tavily-primary` BEFORE writing anything; purely internal → skip it
   and say why. A question that can still CHANGE the outcome → interview per
   [interview.md](interview.md), with the **scope round** ahead of the detail round exactly
   as in the deep pipeline ([scope-round.md](scope-round.md)).
2. **Write the mini spec/plan MERGED into 1 file** `docs/tdq/plan/<slug>.md`, ≤ 40 lines:
   scope in/out, one checkbox task per test, DoD with every line checkable by a command.
   **Every task that edits source must carry a `Chạm:` line** listing the paths in <!-- i18n-allow: canonical name in the default language -->
   backticks — short does not mean the file map is optional. The checkbox has 4 states:
   `[ ]` not started · `[~]` in progress · `[>]` handed to a sub-agent · `[x]` done. At
   implement time (step 7) mark `[~]` when the task starts and switch to `[x]` the moment
   the test is green.
3. **Present a ≤ 10-line summary** in chat: what will be done, which files it touches, and
   how it is validated. Add exactly 1 line `Ước tính sẽ dùng skill: <the skills that will be <!-- i18n-allow: canonical name in the default language -->
   USED, or "không có">` (in doubt → USE). <!-- i18n-allow: label written in the default language -->
4. Print exactly this line, then **STOP**:
<!-- i18n-allow: sample of the approval line, written in doc_lang -->
```
➤ Duyệt: nhắn "duyệt nhanh" (bỏ QC: "duyệt nhanh không QC"; "duyệt quick" vẫn chạy — duyệt xong implement ngay) · Góp ý: nhắn trực tiếp
```
5. The user approves → run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" approve quick [--no-qc] --by "<the user's sentence verbatim>"` (`--no-qc` ONLY when the user says so explicitly — silence about QC means QC stays ON).
6. Append the mini-plan summary to `docs/workinglog/<today>.md` **BEFORE** touching code.
7. Implement end-to-end in 1 turn. **Before typing the first line of code, count the tasks
   whose `Chạm:` sets are disjoint** (no task sharing a path with another): <!-- i18n-allow: canonical name in the default language -->
   - **3 or more** → hand them to sub-agent `tdq-implementer`, one agent per task, issued in
     the same response so they run in parallel; the cap is **4 branches** at a time — the
     same cap `python3 scripts/tdq_team.py cum` applies in the deep pipeline (task 5 prints
     `CHỜ SLOT`). Build a worktree only for an agent that ACTUALLY writes files; a read-only <!-- i18n-allow: canonical name in the default language -->
     agent gets none. Mark `[>]` when handing over, and switch to `[x]` as the report lands.
   - **fewer than 3** → run inline as before; standing up an agent for 1–2 disjoint tasks
     costs more briefing than it saves.
   Each task: mark `[~]` BEFORE editing code (hook `edit_gate` BLOCKS when the plan has no
   `[~]`; `tests/**` is exempt), red→green, switch to
   `[x]` the moment the test is green — batching ticks at the end of the turn is banned.
   Then run **QC** (ON by default): one check per DoD line, evidence written into the plan's
   `## QC` section. `quick_qc_skipped = true` → section `## QC` holds a single line saying
   it was skipped at the user's request, quoting the user verbatim.
   (The full tick rule is in `## The tick rule` and the full QC rule in `## QC in the express
   pipeline`, both in this file.)
8. **Fix round when QC FAILs or a bug shows up**: add tasks to the plan under
   `## QC vòng N — fix`, fix red→green, then re-run the failed items plus the items the fix <!-- i18n-allow: canonical name in the default language -->
   could have broken. There is a 3-round cap — over the cap, STOP, tell the user, propose
   moving to the deep pipeline, and leave the phase as it is. (Full version in
   `## The fix round` in this file.)
9. Append the result to the working log; ask the user about the commit.

Done when: `quick_approved = true`, the log is written, section `## QC` exists, no red test.
Next step: ask the user about the commit; the request is over → `... set phase=idle`.

## Reading the graph at step 1 (analysis)

A question about **links** or the **overall map** ("who calls X", "what does changing X
affect") → open the graph with `graphify query|path|explain|affected`. Finding a string or
reading a specific file → grep/read. The graph holds only `scripts/` and `hooks/`; tests and
docs are excluded by `.graphifyignore`.

## Mini spec/plan template (≤ 40 lines)

The template below is written in the default document language; when `doc_lang` is not `vi`,
translate the headings and labels into that language and keep the shape.

<!-- i18n-allow: document template written in the default language -->
```markdown
# QUICK — <tên việc>

**Ngày:** YYYY-MM-DD · Brief: ../brief/<slug>.md · Lane: quick
**Trạng thái:** CHỜ DUYỆT
**Ước tính sẽ dùng skill:** <skill sẽ DÙNG, hoặc "không có">

## Phạm vi
- Trong: <gạch đầu dòng>
- NGOÀI: <gạch đầu dòng>

## Task
- [ ] **T1** <việc cụ thể> — Test: <lệnh hoặc tiêu chí pass>
- [ ] **T2** <việc cụ thể> — Test: <lệnh>

## Definition of Done
- <điều kiện đo được, có lệnh kiểm>
```
Going past 40 lines means this work is no longer quick — say so to the user and propose
moving to the deep pipeline.

## The block that presents the mini-plan to the user

Per [user-facing-block.md](../../tdq-conventions/references/user-facing-block.md) — all 5
components, the approval block at the end of the message, no emoji:

<!-- i18n-allow: sample block written in the default language -->
```
Tôi đã lên kế hoạch gọn cho yêu cầu của bạn.

**Sẽ làm:** <gạch đầu dòng ngắn>.
**Đụng tới:** <file/khu vực>.
**Kiểm thế nào:** <lệnh hoặc tiêu chí>.
**Ước tính sẽ dùng skill:** <skill sẽ DÙNG, hoặc "không có">.

Xem đầy đủ tại: `docs/tdq/plan/<slug>.md`

---

**Bạn duyệt để tôi làm luôn chứ?**

➤ Duyệt: nhắn "duyệt nhanh" (bỏ QC: "duyệt nhanh không QC"; "duyệt quick" vẫn chạy — duyệt xong tôi làm ngay) · Góp ý: nhắn trực tiếp
```

## The tick rule — `[ ]` · `[~]` · `[x]`

(deliberate repeat — the source of this rule is `## Luật cứng` in `skills/tdq-build/SKILL.md`.) <!-- i18n-allow: section name of the source file -->

The checkbox has four states: `[ ]` not started · `[~]` in progress · `[>]` handed to a
sub-agent · `[x]` done. At implement time:

1. Mark `[~]` on the task you are about to do **BEFORE** editing the first line of code.
   Handed to a sub-agent → mark `[>]` instead of `[~]`, so the plan shows who holds it.
2. Write the test (red) → code → test green.
3. Switch `[~]`/`[>]` → `[x]` **IMMEDIATELY**, never after the next task.

Only one task carries `[~]` at a time; `[>]` may be several, at most the 4-branch cap.
**Batching ticks at the end of the turn is banned** — express does the whole
job in one turn, so batched ticks mean the plan reflected nothing while the work happened.

Fence: `hooks/scripts/edit_gate.py` **BLOCKS** (deny) every edit outside `docs/` and
`tests/` while the phase is `implement`/`qc` and no task in the plan carries `[~]`.
`tests/**` is exempt so a red test can still be written first. Blocked while the request is
in fact closed → run `python3 scripts/tdq_state.py set phase=idle`.

## QC in the express pipeline

ON by default. Run it right after implement finishes, **with as many items as the mini-plan
has DoD lines**: one command-run check per DoD line, with the real output pasted in.
Plus one fixed item: run the exact `Test:` command of every task in the plan.

Add no item beyond the DoD. Edges, error paths, logging and placeholders are checked only
when a DoD line calls for them. Express differs from the deep pipeline here: no
full-suite run over the repo, only each task's own test.

Evidence is appended to the plan file ITSELF, with no `qc/` file created:

<!-- i18n-allow: evidence template written in the default language -->
```markdown
## QC
- Q1 test từng task: PASS — `<lệnh>` → `<output thật>`
- Q2 DoD "<nguyên văn dòng DoD 1>": PASS — `<lệnh>` → `<output thật>`
- Q3 DoD "<nguyên văn dòng DoD 2>": PASS — `<lệnh>` → `<output thật>`
```

Opt-out ONLY when the user says so — a sentence such as "duyệt nhanh không QC" → run approve <!-- i18n-allow: canonical name in the default language -->
with `--no-qc`. Silence about QC means QC HAPPENS. Section `## QC` must still exist, with
exactly 1 line: <!-- i18n-allow: sample sentence in the default language -->

<!-- i18n-allow: opt-out template written in the default language -->
```markdown
## QC
**BỎ theo yêu cầu user:** "<nguyên văn câu user>"
```

## The fix round

- Runs when QC FAILs, or when a bug / red test shows up.
- Fix tasks go into the plan under the heading `## QC vòng N — fix`, in the shape <!-- i18n-allow: canonical name in the default language -->
  `- [ ] **QCn.1** <the job> — Test: <check>`. Do it red→green: `[~]` at the start, switch to
  `[x]` as soon as it is green. <!-- i18n-allow: canonical heading in the default language -->
- After the fix, re-run the items that FAILed plus the items the fix could have broken.
- **3-round cap.** Over the cap → STOP, tell the user, propose moving to the deep pipeline.
  Keep `phase=implement`, do NOT run `set phase=idle`.
