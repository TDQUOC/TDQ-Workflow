# Guidance for whoever WRITES the plan

Split out of `plan-template.md` on 2026-10-02. The three sections below are about writing and
self-checking, not about what gets copied into the plan — so they do not belong in context every
time a plan is written. The line-index block at the top of this file gives each section's exact
line range.

## The minute estimate `(eNm)` — six rules, and what it does NOT promise

`eNm` = the number of **minutes** Claude estimates it needs to EXECUTE that task itself (agent
runtime, not human waiting time). The unit is always minutes, an integer 1–999, never `1h` or
`0.5m`. The ETA of the whole plan = the sum of `eNm` over unfinished tasks.

- Score it as you write the task, never score it later.
- Estimate the time spent WORKING, not the time waiting for approval or interview answers.
- Unsure → score the number you actually believe, do not pad for safety.
- `eNm` is **optional**: missing on a task means that task is skipped in the ETA sum, and the
  plan still runs.
- `eNm` changes nothing about the tick rule `[ ] [~] [x]`: a `(e60m)` task ticks like a `(e5m)` one.
- `eNm` is NOT a promise of time to the user — it is the number the report compares to reality.

## The `Mode thực thi` line <!-- i18n-allow: canonical line name of the plan -->

- It MUST sit on **a line of its own**, never merged into another header line — tooling reads it.
- The value here is the **machine identifier**: `main`, `subagent` or `codex`. Which of them the
  machine can actually offer is what `tdq_state.py modes --json` answers; the labels the user
  reads at gate `mode` live in [mode-gate.md](mode-gate.md).
- This is only Claude's **proposal**. After the user approves the plan, phase `mode` asks; the
  mode written into state is the one the user SAID, never the proposal taken as settled. An
  approval sentence that already names a mode skips that gate and goes straight to implement.

## Check before presenting

- Every output in spec §2 maps to ≥ 1 task.
- Every task holds exactly one piece of work and one measurable check — no task shaped like
  "finish X".
- The first task of each phase opens a red → green path early.
- No task depends on a task placed after it.
