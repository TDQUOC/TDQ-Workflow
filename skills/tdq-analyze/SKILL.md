---
name: tdq-analyze
description: Analyze & complete a TDQ request - codebase reading, multi-route web research, interview loop until zero ambiguity. Runs after tdq-start in the full lane.
---

# TDQ Analyze — Analysis & Complete

Read [tdq-conventions](../tdq-conventions/SKILL.md). Roleplay the matching expert (e.g. senior backend engineer, DevOps, data engineer) for the request's domain. Output VI.

## Goal
Leave this phase with ZERO guessing left: every requirement, constraint, and edge either confirmed by the user, verified in the codebase, or sourced from research. Placeholders and assumptions presented as facts are forbidden.

## Steps

1. **Read the codebase.** Locate everything the request touches (entry points, data flow, configs, tests). Note versions/frameworks in use.

2. **Research (multi-route).** Follow the Tavily rules in [tavily.md](../tdq-conventions/references/tavily.md): 2–4 differently-angled queries via `tavily-primary`, extract top hits, distill. Save to `docs/tdq/research/<slug>.md` as query → source → point. Skip only if the task is purely internal refactoring with no external unknowns.

3. **Interview loop.** List every open question that changes the outcome (scope, UX, data, errors, performance, compatibility). Ask the user in VI — for each question give 2–4 concrete options with a one-line summary each and mark your recommendation. Use AskUserQuestion when available, otherwise numbered chat questions. Record Q&A in `docs/tdq/questions/<slug>.md`. REPEAT until no outcome-changing question remains — multiple rounds are expected; never fill gaps with guesses.

4. **Distill knowledge.** Write `docs/tdq/knowledge/<slug>.md`: confirmed decisions, constraints, chosen approach + why, rejected alternatives + why, sources.

5. **Gate check** before moving on (spec checklist):
   - Final scope clear: what will be built, what is new, concrete outputs?
   - Models/downloads/installs needed identified?
   - QC/test/validate scope defined?
   Missing → back to step 3.

6. **Advance:** `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=spec`, then continue with [tdq-spec](../tdq-spec/SKILL.md) in a NEW turn (spec is never written in the same turn as the plan).
