# Express pipeline — detail
<!-- muc-luc-dong:
  Table of contents=25-34 · How deep the analysis goes — B0, B1, B2=35-52 ·
  The ten execution steps=53-121 · Mini spec/plan template (≤ 40 lines)=122-148 ·
  The block that presents the mini-plan to the user=149-171 · Ba phần tách sang file em=172
-->

Express differs from the deep pipeline by **merging the documents and merging the
gates**, not by dropping thought. Analysis, research and the interview are all KEPT; drop one
only on the thresholds in `## How deep the analysis goes` below — and say why.

| Step | Deep | Express |
|---|---|---|
| Analysis + reading the code | yes | yes — B1 always; B0/B2 on the thresholds below |
| Scope round | conditional, on the trigger signs | identical — the same set of signs |
| Interview | loops until nothing is vague | when a question can still change the outcome |
| Documents | brief + spec + plan | **1 file** `docs/tdq/plan/<slug>.md` |
| Approval gates | 2 (spec, plan) + 1 question on the run mode | **1** (the express approval) |
| QC | file `qc/<slug>.md`, depth per `muc_qc` | one check per DoD line, in the plan's `## QC` section, depth per `muc_qc` |
| Fix round on FAIL | 3-round cap, written into `qc/` | 3-round cap, written into the plan |
The scope round in express shares the rule in [scope-round.md](scope-round.md): one trigger
sign met → ask about areas + context first; none met → write one SKIP reason line into the
mini-plan under `## Phạm vi` and move on. <!-- i18n-allow: canonical name in the default language -->

## Table of contents

- How deep the analysis goes — B0, B1, B2
- The ten execution steps
- Mini spec/plan template (≤ 40 lines)
- The block that presents the mini-plan to the user
- The tick rule — `[ ]` · `[~]` · `[x]`
- QC in the express pipeline
- The fix round

## How deep the analysis goes — B0, B1, B2

Step 1 below is a real analysis phase (`phase = analyze`, table row `quick_analyze`), with
NO approval gate of its own — express keeps exactly one gate. How deep it goes is fixed:

| Step | Express rule |
|---|---|
| B1 read the code | **ALWAYS.** The target is a code symbol → call `mcp__lsp__*` first (`start_lsp` if it answers "not initialized"); a vague concept → `graphify query` plus grep over synonyms, merged; grep last. A question about **links** or the overall map ("who calls X", "what breaks if X changes") → `graphify query\|path\|explain\|affected`; the graph holds only `scripts/` and `hooks/` |
| B0 capability inventory | ONLY when the request touches ground with no precedent — no earlier report under `docs/tdq/report/` touched the same directory |
| B2 research | ONLY when an unknown outside the repo exists (a library, an API, a version, third-party behaviour) — hand it to a sub-agent, digest ≤ 1,500 characters |

**Skipping B0 or B2 costs one line**: the reason goes under the mini-plan's `## Phạm vi` <!-- i18n-allow: canonical section name in the default language -->
section, shape `Bỏ B0: <lý do>`. A step dropped in silence is a QC defect; B1 is never skipped. <!-- i18n-allow: sample line in the default language -->

Why not "always all three": over 43 closed requests, phase `analyze` costs a median 372 s
and a whole express request 533 s — running all three unconditionally makes express ~70 %
slower. Numbers: `docs/tdq/report/2026-09-01-2122-lane-nhanh-kiem-ke-nang-luc.md`.

## The ten execution steps

This is the whole of Part C of [SKILL.md](../SKILL.md) — moved here so the skill body does
not load this branch on every call. Entering the express pipeline you **MUST** read all ten
steps below before doing step 1; working from memory is banned.

1. **Analyse** — run `... set phase=analyze` first, so the phase is visible in the table.
   Do B1 always, B0 and B2 on the thresholds in `## How deep the analysis goes` above. A
   question that can still CHANGE the outcome → interview per
   [interview.md](interview.md), with the **scope round** ahead of the detail round exactly
   as in the deep pipeline ([scope-round.md](scope-round.md)).
2. **Write what the analysis settled into `docs/tdq/brief/<slug>.md`** — the file Part A
   already created — under `## Hiểu & kiến thức`, then register it with <!-- i18n-allow: canonical section name in the default language -->
   `... set brief_file=docs/tdq/brief/<slug>.md`. Do NOT stop for approval here: this phase
   has no gate. Then `... set phase=implement` and go straight on to step 3.
3. **Write the mini spec/plan MERGED into 1 file** `docs/tdq/plan/<slug>.md`, ≤ 40 lines:
   scope in/out, one checkbox task per test, DoD with every line checkable by a command.
   **Every task that edits source must carry a `Chạm:` line** listing the paths in <!-- i18n-allow: canonical name in the default language -->
   backticks — short does not mean the file map is optional. The checkbox has 4 states:
   `[ ]` not started · `[~]` in progress · `[>]` handed to a sub-agent · `[x]` done. At
   implement time (step 8) mark `[~]` when the task starts and switch to `[x]` the moment
   the test is green.
4. **Present a ≤ 10-line summary** in chat: what will be done, which files it touches, and
   how it is validated. Add exactly 1 line `Ước tính sẽ dùng skill: <the skills that will be <!-- i18n-allow: canonical name in the default language -->
   USED, or "không có">` (in doubt → USE). <!-- i18n-allow: label written in the default language -->
5. **Ask the QC level inside the SAME block as the approval invite** — express keeps exactly
   ONE stop, so this question never gets a turn of its own. Three options, default `full`, and
   `off` is never offered (full rule: step 5c of [analyze-full.md](analyze-full.md)). Print
   this, then **STOP**:
<!-- i18n-allow: sample of the approval block, written in doc_lang -->
```
<số>. Request này bạn muốn QC tới mức nào?
- A (đề xuất): `full` — DoD + test của từng task. Không chạy runtime test.
- B: `lite` — chỉ DoD. Nhanh nhất, đổi lại không ai chạy test của từng task.
- C: `ultra` — như `full`, thêm smoke test, runtime test và một agent QC độc lập soi lại.

➤ Duyệt: nhắn "duyệt nhanh" kèm mức (vd "duyệt nhanh, QC full"); "duyệt quick" vẫn chạy — duyệt xong implement ngay · Góp ý: nhắn trực tiếp
```
6. The user approves → record the level FIRST, then the approval:
   `... set muc_qc=<lite|full|ultra>`, then
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" approve quick --by "<the user's sentence verbatim>"`.
   Approved without naming a level → `full`, and never re-ask.
7. Append the mini-plan summary to `docs/workinglog/<today>.md` **BEFORE** touching code.
8. Implement end-to-end in 1 turn. **Before typing the first line of code, count the tasks
   whose `Chạm:` sets are disjoint** (no task sharing a path with another): <!-- i18n-allow: canonical name in the default language -->
   - **3 or more** → hand them to sub-agent `tdq-implementer`, one agent per task, issued in
     the same response so they run in parallel; the cap is **4 branches**, the same cap
     `python3 scripts/tdq_team.py wave` applies in deep mode (task 5 prints `CHỜ SLOT`). Build <!-- i18n-allow: canonical name in the default language -->
     a worktree only for an agent that ACTUALLY writes files. Mark `[>]` when handing over,
     switch to `[x]` as the report lands.
   - **fewer than 3** → run inline; an agent for 1–2 tasks costs more briefing than it saves.
   Each task: mark `[~]` BEFORE editing code (hook `edit_gate` BLOCKS when the plan has no
   `[~]`; `tests/**` is exempt), red→green, switch to
   `[x]` the moment the test is green — batching ticks at the end of the turn is banned.
   Then run **QC at the level in `muc_qc`**: one check per DoD line, evidence written into the
   plan's `## QC` section. `muc_qc=off` → section `## QC` holds a single line saying it was
   skipped at the user's request, quoting the user verbatim.
   (The full tick rule is in `## The tick rule` and the full QC rule in `## QC in the express
   pipeline`, both in this file.)
9. **Fix round when QC FAILs or a bug shows up**: add tasks to the plan under
   `## QC vòng N — fix`, fix red→green, then re-run the failed items plus the items the fix <!-- i18n-allow: canonical name in the default language -->
   could have broken. There is a 3-round cap — over the cap, STOP, tell the user, propose
   moving to the deep pipeline, and leave the phase as it is. (Full version in
   `## The fix round` in this file.)
10. Append the result to the working log; ask the user about the commit.

Done when: `quick_approved = true`, the log is written, section `## QC` exists, no red test.
Next step: ask the user about the commit; the request is over → `... set phase=idle`.

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

➤ Duyệt: nhắn "duyệt nhanh" kèm mức QC (vd "duyệt nhanh, QC full"); "duyệt quick" vẫn chạy — duyệt xong tôi làm ngay · Góp ý: nhắn trực tiếp
```

## Ba phần tách sang file em

Luật tick, QC của lane này và vòng fix ở [quick-lane-qc.md](quick-lane-qc.md) — nạp khi tới bước
cần, không phải ở bước 1.
