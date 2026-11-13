---
trigger: model_decision
description: When creating branches, worktrees, commits, merges, or running git cleanup operations in TDQ Workflow.
---

# Domain Rule: Git Isolation & Forbidden Prefixes

- NEVER start branch or worktree names with `claude`, `antigravity`, `gemini`, or `codex`.
- NEVER include `Co-Authored-By:` or AI attribution trailers in commit messages.
- On Windows, pass `-c core.longpaths=true` when creating deep worktrees under `.tdq-worktrees/`. Only auto-carry clean docs (`docs/**`, `*.md`, `logs/**`, `graphify-out/**`).
