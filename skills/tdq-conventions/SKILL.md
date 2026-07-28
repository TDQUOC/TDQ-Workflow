---
name: tdq-conventions
description: Shared conventions for the TDQ workflow (doc tree, git naming, working log, research rules). Loaded by other tdq skills, not invoked directly.
user-invocable: false
---

# TDQ Conventions

Shared rules for every TDQ workflow phase. Other tdq-* skills reference this file.

## Language
- Internal reasoning and skill instructions: English.
- ALL user-facing output (chat, spec, plan, report, questions, log entries): Vietnamese.

## Doc tree (in the user's project)
```
docs/tdq/
  state.json          # workflow state — NEVER edit directly; use the CLI below
  requests/<slug>.md  # original request + intake summary
  questions/<slug>.md # interview Q&A
  research/<slug>.md  # web research notes with sources
  knowledge/<slug>.md # distilled decisions/constraints
  spec/<slug>.md      # spec (VI)
  plan/<slug>.md      # plan (VI, checkbox tasks)
  qc/<slug>.md        # QC results
  reports/<slug>.md   # final report (≤ 50 lines)
docs/workinglog/YYYY-MM-DD.md   # daily working log (append at END of file)
```
Slug format: `YYYY-MM-DD-<kebab-title>`. Reuse the same slug across all folders for one request.

## State
- Read/write state ONLY via: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" <get|init|set|reset> ...`
- Approval fields (`*_approved`, `*_sha256`, `*_approved_at`) and `implement_mode` are protected — only the user's `/tdq-workflow:tdq-approve` command can set them. The implement mode is ALWAYS the user's decision: ask before writing the plan, and it is fixed by the mode the user types in the approve command. Never try to bypass; hooks deny direct writes to state.json.
- An open request in the right lane must exist BEFORE you invite approval — an invitation the gate cannot honour wastes the user's move and is blocked by the Stop hook.
- `reset` only when the user closes/abandons a request, never while work continues. To test the workflow itself, run against a throwaway project via `TDQ_PROJECT_DIR=/tmp/... python3 .../tdq_state.py ...` instead of touching the real state.

## Git
- Branch/commit/worktree names must NOT start with: `claude`, `antigravity`, `gemini`, `codex` (any case).
- Commit messages must NOT contain "generated with <AI>", "được tạo cùng/với/bởi <AI>", or AI Co-Authored-By trailers.
- Never commit or push unless the user explicitly asks.

## Working log (mandatory)
- Any turn that changes the repo → append a short entry to `docs/workinglog/<today>.md` (create if missing).
- Entry: time/context, files changed, why, tests run (or why not). Append at the END of the file — anchor on the true last entry.
- If `graphify` is installed, also run its update command after logging.

## Research
- Web search: call `tavily-primary` tools first, always. On connection/auth/timeout/quota/tool error only, call the matching `tavily-backup` tool exactly once. Built-in WebSearch only after both fail AND the user approves. WebFetch is fine for known URLs.
- Power usage patterns: see [references/tavily.md](references/tavily.md).
- Every claim in specs/answers needs a source or a stated basis. Never invent facts.
- Never put API keys in replies, logs, shell commands, or prompts.

## Quality bars
- No placeholders, no TODO stubs, no mock data presented as real. If information is missing → interview the user instead of guessing.
- Products built by this workflow ship with a logging service ON by default (timestamps, enough detail to debug).
- Each plan task has its own test/validate step; tick `[x]` in the plan file IMMEDIATELY when a task's test passes — never batch ticks at end of turn.
