---
name: tdq-intake
description: Mở request TDQ mới - ghi yêu cầu, chọn lane, init state, phân tích + interview đến hết mơ hồ. Dùng cho MỌI prompt mới, kể cả câu hỏi/check/việc nhỏ.
---

# TDQ Intake — mở request & phân tích

Load [tdq-conventions](../tdq-conventions/SKILL.md) first. Mọi output cho user: **tiếng Việt**.
This skill owns two phases: `no_state` → `analyze`.

## Tầng nhỏ — answer or fix on the spot, no request opened

Enter tier `nhỏ` only when **all 4** conditions hold:

1. Product behaviour does not change, or exactly one obvious spot changes (typo,
   constant, display string, version number).
2. No source file is added and none is deleted.
3. Nothing touches hooks, state, or an approval gate.
4. It finishes inside one turn, with nothing the user has to decide.

At this tier: answer or fix straight away. No request, no `init` state, no plan, no QC.
If the repo changed, still run `tdq_finish.py --log` like every other turn.

**Escape rule (mandatory).** Break any condition midway → STOP, name the condition that
broke, then open a normal request from Part A. Never keep going at tier `nhỏ`.

## Phần A — Mở request (phase `no_state`)

Definition of a "new request": ANY user prompt while NO request is open — open means
`active_request` exists AND `phase != idle`. When phase ≠ idle the user's message belongs
to the running request (approval, feedback, interview answer); never nest a new request.

The request is a BUG REPORT rather than a feature ("chạy sai", "bị treo", "kết quả không
như mong đợi") → follow [references/issue-triage.md](references/issue-triage.md) first,
then come back to step 1 below.

1. **Record the request.** Create `docs/tdq/brief/<slug>.md` with slug
   `YYYY-MM-DD-HHMM-<kebab ≤5 từ, không dấu>`. The brief is the ONLY file of the intake +
   analyze phases, with exactly 3 sections: `## Nguyên văn` (the user's words verbatim
   plus your first reading: goal, guessed scope, unclear spots), `## Hiểu & kiến thức`,
   `## Hỏi đáp`. Write only the first section here; Part B fills the other two. Line 2 of
   the brief — right under the title — copies this line verbatim (spec/plan/qc/report
   carry it too):

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

2. **Propose a lane, then ASK.** In chat: 2–3 lines summarising what the user wants.
   Judging size/need (`Cỡ:/Cần:`) is an INTERNAL step — it picks which option you
   recommend, and that line is NEVER printed to chat. Then ask "Bạn muốn chạy pipeline
   nào?" with one option per line per [references/interview.md](references/interview.md),
   the recommendation always at A:
   `- A (đề xuất): chế độ nhanh (express) — <lý do>` on the next line `- B: chế độ chuyên sâu (deep) — <lý do>`,
   following the full khuôn (including the block explaining what the 2 pipelines mean) in
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

Xong khi: `state.json` has `active_request` and the `lane` the user chose.
Bước kế tiếp: Phần B (chế độ chuyên sâu (deep)) hoặc Phần C (chế độ nhanh (express)).

## Phần B — Phân tích (phase `analyze`, chỉ chế độ chuyên sâu (deep))

Load this only for chế độ chuyên sâu (deep) — chế độ nhanh does not need it. Play the
expert of that exact field; the goal is to leave this phase with ZERO guesswork. Do all 6
steps (capability inventory, read the code, research, interview, settle the knowledge,
gate check) per [references/analyze-full.md](references/analyze-full.md). The verdict
table khuôn for the capability-inventory step (B0):
[references/skill-inventory.md](references/skill-inventory.md).
The interview runs general → specific: the **scope round** first (which areas + context in
numbers, per [references/scope-round.md](references/scope-round.md)), and only then the
detail questions inside the areas the user picked. The scope round is conditional; skip it
and one line of reasoning goes into the brief.

Xong khi: `brief/<slug>.md` has all 3 sections (including `### Lộ trình`) and all 3 gate
questions can be answered.
Bước kế tiếp: `python3 "${CLAUDE_PROJECT_DIR}/.claude/tdq/scripts/tdq_state.py" set phase=spec`
then on to [tdq-spec](../tdq-spec/SKILL.md) — same turn if the interview is finished; if
questions remain, present them and stop.

## Phần C — Chế độ nhanh (express)

Chế độ nhanh is a shortened path, NOT a path with thinking steps cut out. The nine
execution steps — from analysis to asking about the commit — live in
[references/quick-lane.md](references/quick-lane.md) under `## Chín bước thi hành`.
**You MUST open that file and read all nine steps before doing step 1; working from memory
is banned.** That same file also holds the mini-plan khuôn, the tick rule, the QC rule and
the fix round.

Xong khi: `quick_approved = true`, the log is written, section `## QC` exists, no red test.
Bước kế tiếp: hỏi user về commit; hết request thì `... set phase=idle`.
