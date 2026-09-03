---
name: tdq-intake
description: Open a new TDQ request - record the ask, pick the lane, init state, analyse + interview until nothing is vague. Use for EVERY new prompt, including questions, checks and small jobs.
---

# TDQ Intake — open the request & analyse

Load [tdq-conventions](../tdq-conventions/SKILL.md) first. Every output for the user is written
in the user's language (`doc_lang`, default Vietnamese).
This skill owns two phases: `no_state` → `analyze`.

## Tier `nhỏ` — answer or fix on the spot, no request opened <!-- i18n-allow: canonical name in the default language -->

Enter tier `nhỏ` only when **all 4** conditions hold: <!-- i18n-allow: canonical name in the default language -->

1. Product behaviour does not change, or exactly one obvious spot changes (typo,
   constant, display string, version number).
2. No source file is added and none is deleted.
3. Nothing touches hooks, state, or an approval gate.
4. It finishes inside one turn, with nothing the user has to decide.

At this tier: answer or fix straight away. No request, no `init` state, no plan, no QC.
If the repo changed, still run `tdq_finish.py --log` like every other turn.

**Escape rule (mandatory).** Break any condition midway → STOP, name the condition that
broke, then open a normal request from Part A. Never keep going at tier `nhỏ`. <!-- i18n-allow: canonical name in the default language -->

## Part A — Open the request (phase `no_state`)

Definition of a "new request": ANY user prompt while NO request is open — open means
`active_request` exists AND `phase != idle`. When phase ≠ idle the user's message belongs
to the running request (approval, feedback, interview answer); never nest a new request.

The request is a BUG REPORT rather than a feature ("it runs wrong", "it hangs", "the result
is not what I expected") → follow [references/issue-triage.md](references/issue-triage.md)
first, then come back to step 1 below.

1. **Record the request.** Create `docs/tdq/brief/<slug>.md` with slug
   `YYYY-MM-DD-HHMM-<kebab, ≤5 words, no accents>`. The brief is the ONLY file of the intake +
   analyze phases, with exactly 3 sections: `## Nguyên văn` (the user's words verbatim <!-- i18n-allow: canonical name in the default language -->
   plus your first reading: goal, guessed scope, unclear spots), `## Hiểu & kiến thức`, <!-- i18n-allow: canonical name in the default language -->
   `## Hỏi đáp`. Write only the first section here; Part B fills the other two. Line 2 — right <!-- i18n-allow: canonical name in the default language -->
   under the title — copies this verbatim (spec/plan/qc/report carry it too):

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md <!-- i18n-allow: canonical Soul line copied verbatim -->

1b. **Check the search layer.** Run `python3 scripts/tdq_lsp.py kiem` — seven rungs, agent-lsp
   through import-root config. A rung is missing → print the exact command it gave you, **ASK the
   user for permission, and only run it once they say yes.** Never install unasked, never edit
   another plugin's file. Rungs 5–6 only warn. Details:
   [tdq-lsp-setup](../tdq-lsp-setup/SKILL.md). Then prove the index actually answers: the effect
   check in [references/kiem-lsp-hieu-ung.md](references/kiem-lsp-hieu-ung.md), once, here —
   skipping it when the ladder passed is a QC defect, because every rung checks only that
   something EXISTS. The search order that follows is binding on every phase: <!-- i18n-allow: canonical rule sentence in the default language -->
   Đối tượng tìm là ký hiệu code (hàm, class, biến, kiểu) → chọn lớp theo LOẠI truy vấn: quan
   hệ và đổi tên dùng `mcp__lsp__*`; tên chính xác đã biết dùng grep; khái niệm mơ hồ dùng
   lumen; chưa chắc thuộc loại nào thì gọi song song rồi gộp. Bảng đầy đủ kèm số đo:
   `skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md`.

2. **Propose a lane, then ASK.** In chat: 2–3 lines summarising what the user wants.
   Judging size/need (`Cỡ:/Cần:`) is an INTERNAL step — it picks which option you <!-- i18n-allow: canonical name in the default language -->
   recommend, and that line is NEVER printed to chat. Then ask which pipeline the user
   wants, with one option per line per [references/interview.md](references/interview.md),
   the recommendation always at A. The question line is NUMBERED `1.` per rule 8 of
   [user-facing-block.md](../tdq-conventions/references/user-facing-block.md).
   Shape: `1. Bạn muốn chạy pipeline nào?` then `- A (đề xuất): chế độ nhanh (express) — <lý do>` on the next line `- B: chế độ chuyên sâu (deep) — <lý do>`. <!-- i18n-allow: option sample in the default language -->
   Full template, including the block explaining the 2 pipelines:
   [references/lane-decision.md](references/lane-decision.md).
   **STOP and wait for the user's answer.** Never pick the lane yourself.

3. **Init state** as soon as the user settles the lane:
   ```
   python3 "${CLAUDE_PROJECT_DIR}/.claude/tdq/scripts/tdq_state.py" init <slug> <quick|full>
   ```
   This command **wipes** the old state. If another request is still unfinished → name the
   slug and phase about to be lost, **ask the user first**, then run it.

4. **Branch:**
   - `full` → `... set phase=analyze`, continue with Part B inside this same turn.
   - `quick` → do Part C, skipping Part B.

Done when: `state.json` has `active_request` and the `lane` the user chose.
Next step: phase `analyze` (deep, Part B) or `quick_analyze` (express, Part C) — the lane decides.

## Part B — Analysis (phase `analyze`, deep pipeline only)

Load this only for the deep pipeline — express does not need it. Play the
expert of that exact field; the goal is to leave this phase with ZERO guesswork. Do all 6
steps (capability inventory, read the code, research, interview, settle the knowledge,
gate check) per [references/analyze-full.md](references/analyze-full.md). The verdict
table template for the capability-inventory step (B0):
[references/skill-inventory.md](references/skill-inventory.md).
The interview runs general → specific: the **scope round** first (which areas + context in
numbers, per [references/scope-round.md](references/scope-round.md)), and only then the
detail questions inside the areas the user picked. The scope round is conditional; skip it
and one line of reasoning goes into the brief.

Done when: `brief/<slug>.md` has all 3 sections (including `### Lộ trình`) and all 3 gate <!-- i18n-allow: canonical name in the default language -->
questions can be answered.
The `### Lộ trình` you write here runs `spec` → `plan` with nothing in between: approving the <!-- i18n-allow: canonical name in the default language -->
spec approves the route. Name the feature flows the request is built from, one line per flow.

Next step: phase `spec` — `python3 "${CLAUDE_PROJECT_DIR}/.claude/tdq/scripts/tdq_state.py" set phase=spec`
then on to [tdq-spec](../tdq-spec/SKILL.md) — same turn if the interview is finished; if
questions remain, present them and stop.

## Part C — Express pipeline

Express is a shortened path, NOT a path with thinking steps cut out. The ten
execution steps — from analysis to asking about the commit — live in
[references/quick-lane.md](references/quick-lane.md) under `## The ten execution steps`.
**You MUST open that file and read all ten steps before doing step 1; working from memory
is banned.** That same file also holds how deep the analysis goes (B1 always, B0 and B2 on
thresholds), the mini-plan template, the tick rule, the QC rule and the fix round.

Step 1 sets `phase=analyze`, showing the express analysis as its own row (`quick_analyze`) in the
phase table. That phase has **NO approval gate** — express keeps one gate, the approval at step 6.

Done when: `quick_approved = true`, the log is written, section `## QC` exists, no red test.
Next step: phase `idle` — ask about the commit, the request is over → `... set phase=idle`.
