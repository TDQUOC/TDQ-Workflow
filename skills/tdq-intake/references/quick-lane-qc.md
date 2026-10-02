# Express lane: the tick rule, QC, and the fix loop

Split out of `quick-lane.md` on 2026-10-02, measured: these three parts add up to **1,120 tokens**
inside a 4,356-token file, and not one of them is needed at STEP 1. The tick rule is needed when a
task starts; QC at step 6; the fix loop only when something is red. Loading all three as the
express lane opens is paying up front for three jobs that have not arrived.

The line-index block at the top of this file gives each section's exact line range.

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

Depth comes from `muc_qc` (default `full`; read it with `tdq_state.py get muc_qc`). Run it right
after implement finishes, **with as many items as the mini-plan has DoD lines**: one command-run
check per DoD line, with the real output pasted in. At `full` and above, add one fixed item: run
the exact `Test:` command of every task in the plan. At `lite` the DoD lines alone are the QC; at
`ultra` add the smoke and runtime items, each under the 120-second cap. The level table is owned
by [qc.md](../../tdq-build/references/qc.md) — do not restate it here, it would drift.

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

Opt-out ONLY when the user says so — a sentence such as "duyệt nhanh không QC" → record it <!-- i18n-allow: canonical name in the default language -->
with `set muc_qc=off`. Silence about QC means QC HAPPENS at `full`. Section `## QC` must still
exist, with exactly 1 line: <!-- i18n-allow: sample sentence in the default language -->

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
