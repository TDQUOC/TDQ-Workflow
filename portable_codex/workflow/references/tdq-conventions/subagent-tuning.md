# Choosing model & effort for a sub-agent

Goal: on every agent call, pick the "just enough" tier — do not burn Opus on wrapping a script,
do not force Haiku into work that needs deep reasoning.

## Two knobs, two different scopes

| Knob | Set where | Changeable at call time? |
|---|---|---|
| `model` | agent frontmatter (default) **and** the Agent tool's `model` parameter at call time | **Yes** — the call parameter overrides frontmatter |
| `effort` | **only** agent frontmatter (`low\|medium\|high\|xhigh\|max`) | **No** — the Agent tool has no `effort` parameter yet |

So: `effort` is a FIXED property of the role; `model` is the knob you turn per task.

## Defaults per role (already written into frontmatter)

| Agent | model | effort | Why |
|---|---|---|---|
| `tdq-implementer` | inherit | high | writes real code, red→green, a mistake breaks the plan |
| `tdq-qc-tester` | inherit | high | must be suspicious and dig at the edges, not just rerun a command |
| `tdq-reviewer` | inherit | high | finding gaps/contradictions in a spec-plan is pure reasoning |
| `general-purpose` (research) | sonnet | medium | runs Tavily broadly, synthesises shallowly; no frontier needed |

`inherit` = follow the model the user has on in the main session. Use `inherit` for agents doing
quality work; use a concrete model for mechanical agents so their cost does not depend on which
model the user happens to have enabled.

## Rule for overriding `model` at call time (Agent tool parameter)

Turn it per task, in order — stop at the first matching row:

| If the task is | Pass `model` |
|---|---|
| Purely mechanical: run one command, read one file, return it verbatim | `haiku` |
| Search/read broadly then summarise, deciding nothing | `sonnet` |
| Writing code, fixing logic, design, review, QC | leave empty (keep the agent's default) |
| The hardest task of the plan, or one that already failed once on a lower model | `opus` |

Record the reason for an override in the working log whenever you deviate from the default —
one line is enough.

## Warning about `effort`

Frontmatter `effort` **overrides** the session's effort level (the env var still beats both).
Setting `effort: low` on an agent that does quality work means that agent thinks shallowly EVEN
WHEN the user has the session on `high`. Only set `low` on purely mechanical agents.

Making effort genuinely vary per task would require splitting each agent into several variants —
considered and REJECTED (spec 2026-08-04-workflow-linh-hoat §3): twice the files, easy to drift.

## Sources

- https://code.claude.com/docs/en/sub-agents — frontmatter field table (`model`,
  `effort`; plugin subagents only ignore `permissionMode`/`mcpServers`/`hooks`). Checked 2026-08-04.
- https://code.claude.com/docs/en/model-config — effort precedence: env var >
  frontmatter (when the agent is active) > session level > model default. Checked 2026-08-04.
- https://github.com/anthropics/claude-code/issues/43083 — the Agent tool has no `effort`
  parameter yet (open feature request). Checked 2026-08-04.
