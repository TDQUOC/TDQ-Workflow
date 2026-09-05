---
name: tdq-conventions
description: Shared TDQ workflow rules (one-turn protocol, state, approval, hook reminder codes, git, working log, research). Loaded by the other tdq-* skills; never invoked directly.
user-invocable: false
---

# TDQ Conventions

Rules shared by every phase. Other skills link here instead of copying them.

## 0. Language — three reader layers

One workflow, three kinds of reader, so three language rules. They never mix.

| Layer | What it covers | Language |
|---|---|---|
| Rules | `skills/**`, `agents/*.md`, comments and docstrings in `~/.gemini/config/plugins/tdq-workflow/hooks/` and `~/.gemini/config/plugins/tdq-workflow/scripts/` | **English**, always |
| Machine strings | anything a hook or a script PRINTS: log lines, errors, tables, argparse help | **English**, always |
| Documents & dialogue | brief/spec/plan/qc/report and every sentence spoken to the user | the language of field `doc_lang` |

- `doc_lang` is declared ONCE when the request opens — `tdq_state.py init <slug> <lane> --lang <code>` —
  and stays constant for the whole request. Read it with `tdq_state.py get doc_lang`.
- The code is a short BCP 47 machine code (`vi`, `en`, `ja`, `pt-br`), never a free-form name.
  Field missing or unreadable → fall back to the default `vi`.
- Never guess the language from the rule files: they are English by design, and their language says
  nothing about the reader. The user's own words and `doc_lang` are the only sources.
- A template quoted inside a rule file is a SHAPE, not wording to copy byte for byte: translate its text
  into `doc_lang` while keeping the structure (line order, labels `A`/`B`, the `➤` line, separators).

## 1. One-turn protocol (mandatory, in this order)

1. Turn start: the hook already printed `[TDQ:NEXT]` → use that text, **do not re-run**
   `tdq_state.py next`; run `next` only when the context has no such line.
2. Do only the work of the current phase — never start work belonging to a later phase.
3. A `[TDQ:<CODE>]` line injected by a hook → **do what it says FIRST**, before anything else,
   then print `✓ [TDQ:<CODE>] <what was done>`. Codes: [references/reminder-codes.md](references/reminder-codes.md).
4. A turn that changed the repo MUST end with the closing command
   `python3 "~/.gemini/config/plugins/tdq-workflow/scripts/tdq_finish.py" --files <files just edited> --log "<summary>" --phase <new phase>`
   — lint those files → append the working log → set phase → graphify. **Never Edit/Read the working log and append by
   hand**, not even when `stop_gate.py` blocks you: a block means "the command has not run", not "run something else to
   dodge it". This command is the **last action** of the turn. It runs BEFORE the closing chat block (summary,
   question, the `➤` approval line, over-budget report). After that block **no further tool call** may happen, so the
   block stays a real final response. A long turn (team mode, several merge rounds) may call `tdq_finish.py` MANY times — one call per real
   milestone, e.g. one merged batch; only the LAST call must be the final action. Never call it empty: every call
   carries `--files` and `--log` of the work just finished.
5. **The turn keeps running after the user-facing block was printed** — a hook blocked you, you noticed
   missed work, a tool failed. The LAST message must then reprint that block **WORD FOR WORD, 100%**:
   the summary, the question, EVERY option, the approval line. Put it RIGHT AFTER the
   `✓ [TDQ:<CODE>]` line. Reason: focus mode shows only the last message. Summarising it again or
   pointing backwards ("see the question above") loses the user the question and the options
   entirely. Shortening is banned; pointing backwards is banned.
6. **Every block addressed to the user** — pipeline question, interview, the spec / plan / mode / express
   gates, the commit question — follows [references/user-facing-block.md](references/user-facing-block.md).
   Its shape: an opening line addressing the user directly, full file paths, a separator rule, the bold
   answer block last, no emoji.

7. **Never end a turn while the plan still has tasks** — stopping with a `[ ]` task left is abandoning the job,
   however good the progress report looks. Exactly **three exceptions** may stop a turn:
   1. Something only the user decides: spec/plan scope change, destructive or hard-to-reverse work, an input only
      the user holds.
   2. A technical block with no option you may pick yourself (lost access, no network, broken tool).
   3. The QC fix loop hit its ceiling of 3 rounds — rule in `tdq-build/references/qc.md`.
   Running out of step budget is NOT an exception: report it and carry on. Neither is "let's leave the rest for the
   next turn to keep this one tidy".

**The `Next step:` line of every skill names the phase that comes next** — the phase key itself,
or, when the phase does not change, that fact plus the skill to load. A bare command is not
enough. This is the FALLBACK layer: the hook `[TDQ:NEXT]` stays the main road wherever the host
runs hooks, and this line carries the load where it does not. Gemini CLI, GitHub Copilot CLI and
Aider have no lifecycle hooks, so on those hosts the skill text is all the agent ever sees.
Phase keys and what each phase owes: [references/phases.md](references/phases.md).

Done when: the new phase is recorded in state and the working log holds this turn's entry.
Next step: phase does not change here — follow the "transition command" column of
[references/phases.md](references/phases.md) for the phase you are actually in, then load the
skill that owns it.

## 2. Phase table

Full table (entry condition / single job / transition command / done when / forbidden):
[references/phases.md](references/phases.md) — a file **generated** from the `PHASE_TABLE`
constant in `~/.gemini/config/plugins/tdq-workflow/scripts/tdq_state.py`. Never copy its commands elsewhere, never hand-edit it.

## 3. State

- Read and write state **only** through the CLI:
  `python3 "~/.gemini/config/plugins/tdq-workflow/scripts/tdq_state.py" <next|get|set|approve|init|reset>`.
  Hand-editing `docs/tdq/state.json` or `docs/tdq/STATE.md` is forbidden (generated mirror, read-only).
- `next` answers "what do I do now". `get <key>` reads one field.
- `init <slug> <quick|full>` = **open a new request**; it wipes every old field (lane, phase, spec/plan file, every
  approval mark, implement_mode) and keeps the old slug in `previous_request`. Run it for EVERY new request once the
  user picks a lane; an unfinished request → name the slug and phase about to be lost, then **ask the user first**.
- `reset` only when the user closes a request for good. To experiment with the workflow, aim at a throwaway project:
  put `TDQ_PROJECT_DIR=/tmp/...` on that very command (no `||` fallback).
- Any state trouble is a warning only (exit 0). Exit 2 means the command syntax was wrong.

## 4. Recording approval

The user approves in ordinary chat — no required syntax, no gate that blocks the user.
Signals, counter-examples, and the command to run: [references/approval.md](references/approval.md).

Three rules that must never break, whatever else changes:
- Ambiguous wording → **ASK**; never infer that approval was given.
- Approving the spec is not approving the plan. Record only what the user named.
- Execution mode is always the USER's choice (main | subagent). Proposing is fine, deciding for them is not.

## 5. Document tree

```
docs/tdq/
  state.json + STATE.md   # state written through the CLI; STATE.md is a generated mirror, read-only
  brief/<slug>.md     research/<slug>.md   spec/<slug>.md
  plan/<slug>.md      qc/<slug>.md         reports/<slug>.md
docs/workinglog/YYYY-MM-DD.md
```
Slug: `YYYY-MM-DD-HHMM-<kebab, ≤5 words, unaccented ASCII>` (local time, so sorting names sorts by
time), the same in every folder. Old date-only slugs still READ fine; writing a new one without hour
and minute makes `init` refuse. `brief/` merges request, knowledge and Q&A into one file with exactly
three sections — verbatim request · understanding & knowledge · Q&A. The heading wording is the one
`doc_lint.py` checks for that language; keep the three sections, in that order, whatever the language.

## 6. Working log

- Any turn that changed the repo → `tdq_finish.py --log` appends to the END of `docs/workinglog/<today>.md`: time,
  files changed, why, tests run. How the hook detects it: [reminder-codes.md](references/reminder-codes.md).
- A read-only or analysis turn writes nothing. A turn that only edits the working log adds no further entry.
- **Images the user attached.** A turn with attached images that must also write a working log → copy them into
  `docs/workinglog/assets/`, then put the links inside the `--log` string, BEFORE calling `tdq_finish.py`. Paths,
  numbering, full rule: [references/worklog-images.md](references/worklog-images.md).

## 7. Git

- Branch, commit and worktree names **never** start with `claude`, `antigravity`, `gemini`, `codex`.
- Commit messages **never** contain "generated with <AI>", any translation of that phrase, or an AI Co-Authored-By trailer.
- **Never** commit or push before the user asks. Sole exception: a TDQ build hits a technical
  block only a commit clears → commit it with a proper message, do **NOT** push, list it in the report.
- No git in the project yet → you may init git or a worktree; check the worktree merges back.
- **A request branch is named `<loại>/<mô tả>`** — forward slash only, because
  `git check-ref-format --branch` rejects the backslash form; `<mô tả>` is kebab-case,
  no accents. Five types: `feature/login-gui`, `bugfix/state-mat-nhanh-goc`,
  `hotfix/hook-treo-turn`, `chore/bump-phien-ban`, `docs/kien-truc-module`. Lane `full`
  and `quick` open one, tier `nhỏ` none; it merges back `--no-ff` then is deleted. Rule:
  [../tdq-intake/references/nhanh-request.md](../tdq-intake/references/nhanh-request.md).

## 8. Research

- Web search goes through `tavily-primary` first, always. Failover and advanced patterns:
  [references/tavily.md](references/tavily.md).
- Every claim needs a source or a stated basis. Never invent one. Routing work to plugins and the protocol for
  already-enabled ones: [references/plugin-routing.md](references/plugin-routing.md).
- Never put an API key in an answer, a log, a shell command or a prompt.
- Work that matters (architecture, the user's preferences, a recurring bug) → search mem0 with
  `project` = the repo name BEFORE concluding; store one short fact once settled. Skill `mem0-memory`.

## 9. Sub-agents

- The `description` of every Agent call reads `<model>-<effort>-<task-kebab>` (e.g.
  `sonnet-low-research-doc`) — the name alone tells which model and effort are running.
- Default model/effort per role plus the override rule: [references/subagent-tuning.md](references/subagent-tuning.md).

## 10. One-batch rule (tier 2 — runtime) and context cost

One tool call is one round trip ≈ 3.3 s. Total time scales with the NUMBER OF STEPS; context size only nudges it.
That is why this rule belongs to the **runtime** tier, not to context cost.

- **When it applies:** you are about to issue two or more tool calls and none of them needs another's result.
- **What to do:** issue them all in ONE batch; join independent Bash commands with `&&`; do not re-read a file whose
  content is still in context.
- **Self-check:** "Does the later call need the earlier call's result?" — No → batch. Yes → split.

Cases where batching is banned, the (soft) re-read rule with RULE-vs-FORGOT, the MCP output ceiling, reading just
enough, handing heavy work to a subagent: [references/context-budget.md](references/context-budget.md); the
before/after carry-cost measurement scenario: [references/measure-scenario.md](references/measure-scenario.md).

## 11. Quality

- Soul — the rule above every rule: quality > runtime > context cost. Writing or changing a rule, rules that contradict each other, or a plan to cut steps → open [references/soul.md](references/soul.md).
- Clean code is standing behaviour, not a gate you ask about. Every time you write or change code, shape the project,
  scripts, functions and classes as cleanly as the five SOLID principles allow. Two-reader table, RIGHT/WRONG examples,
  five-question checklist: [references/clean-code.md](references/clean-code.md).
- No placeholders, no TODO stubs, no mock data presented as real. Missing information → ask the user, do not guess.
- Anything built ships a log service on by default (timestamps, enough detail to debug, switchable off through config).
- Every task in a plan has its own test; a passing task is ticked `[x]` IMMEDIATELY, never batched at the end of the turn.
