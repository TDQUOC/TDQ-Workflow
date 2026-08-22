---
name: tdq-check-status
description: Recover an unfinished TDQ request: read the disk directly, report, and continue after a single nod from the user. Use when an old session died, when switching machines, or when another agent just ran a phase for you.
---

# TDQ Check Status — detect the unfinished request, then continue

Load [tdq-conventions](../tdq-conventions/SKILL.md). This skill belongs to NO phase: it can be
called from any phase, including when `state.json` is wrong or missing.

Difference from [tdq-status](../tdq-status/SKILL.md): `tdq-status` quickly reports what the
state DECLARES. This skill compares the state against the DISK and then recovers — heavier,
so use it only when context was lost.

## Hard rules — never lose data

- **The disk is the evidence, `state.json` is only the claim.** They disagree → trust the disk.
- **Absolutely banned:** `tdq_state.py` with subcommand `init` or `reset`, and equally banned is
  deleting or overwriting an existing brief/spec/plan/qc/report. Those two subcommands wipe
  the open request.
- Only patch commands from exactly two families may run: `tdq_state.py set …` and
  `tdq_state.py approve …`.
- **One nod gate only.** Present the report → wait for the user's nod → run every patch
  command → move on. Never ask a second time, never run before the nod.
- Verdict `CẦN USER QUYẾT` → STOP, present the question; guessing what the user wants is banned. <!-- i18n-allow: verdict/section string printed verbatim -->
- **A corrupt `state.json` is NOT the same as no state.** Corrupt while the disk still holds a
  spec/plan is case D1 at level `chan`: show it to the user and ask to rebuild the state. <!-- i18n-allow: verdict/section string printed verbatim -->
  Treating it as "no request yet" loses the whole request.

## Steps

1. Run the detector (read-only, writes nothing):
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_checkstatus.py" report
   ```
   Need machine-readable data → add `--json`. The script finds the project root itself;
   force it with `--project`.

2. Read the output. It already follows the 6-section template of
   [references/report-template.md](references/report-template.md) — reprint it verbatim for
   the user, do not re-summarise it in your own words, add no judgement beyond the table.

3. Look every drift code up in [references/bang-lech.md](references/bang-lech.md) to learn
   its meaning and its limits. That table is the only source; inventing extra diagnoses is
   banned.

4. Branch on the exact `## Kết luận` line: <!-- i18n-allow: verdict/section string printed verbatim -->
   - `TIẾP TỤC ĐƯỢC` → report one line, then carry on with the work under `## Việc kế tiếp`. <!-- i18n-allow: verdict/section string printed verbatim -->
   - `VÁ RỒI TIẾP TỤC` → print the `## Lệnh vá đề xuất` block and ask the user exactly one <!-- i18n-allow: verdict/section string printed verbatim -->
     question: whether to run these patch commands and continue. **STOP and wait for the user.**
   - `CẦN USER QUYẾT` → print the `chan`-level cases, lay out the choices per the option <!-- i18n-allow: verdict/section string printed verbatim -->
     template of conventions, **STOP and wait for the user**. Run no patch command at all.

5. The user nods at step 4 → run each command of the patch block verbatim, in order.
   A command outside the two families `set`/`approve` must NOT be run; report it instead —
   that is a bug in the detector, not something to fix by hand.

6. Re-run step 1 once to confirm the verdict has risen to `TIẾP TỤC ĐƯỢC`. <!-- i18n-allow: verdict/section string printed verbatim -->

7. Hand over at the phase you actually stand in, per
   [phases.md](../tdq-conventions/references/phases.md):
   - `analyze` / `spec` → [tdq-spec](../tdq-spec/SKILL.md); a phase with an approval gate
     means re-presenting that exact gate, then STOPPING for the user's approval.
   - `plan` → [tdq-plan](../tdq-plan/SKILL.md), stopping at the plan approval gate too.
   - `implement` / `qc` / `report` → [tdq-build](../tdq-build/SKILL.md), carry on right away.
     At `implement`, resume the exact task the report shows as `[~]`.

Done when: the user has read the report, every needed patch command has run, and the skill of
the correct phase is loaded to continue.
Next step: the skill at step 7 matching the current phase.
