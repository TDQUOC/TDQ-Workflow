# TDQ Workflow — Google Antigravity Native Plugin (`v0.97.0`)

Spec-driven engineering workflow compiled for Google Antigravity (`agy`).

- **Hooks:** `hooks.json` at plugin root (`SessionStart`, `PreInvocation`, `PreToolUse`, `PostToolUse`, `PostInvocation`, `Stop`).
- **Rules:** 2-tier `rules/AGENTS.md` + `rules/lang-*.md` (`glob`) + `rules/domain-*.md` (`model_decision`).
- **Skills (12):** tdq-browser-research, tdq-browser-test, tdq-build, tdq-check-status, tdq-checkportable, tdq-conventions, tdq-intake, tdq-lean, tdq-plan, tdq-setup, tdq-spec, tdq-status.
- **Subagents (6):** tdq-build-resolver.md, tdq-implementer.md, tdq-qc-tester.md, tdq-refactor-cleaner.md, tdq-reviewer.md, tdq-security-reviewer.md.
- **MCP:** `lsp` (`agent-lsp`), `chrome-devtools`, `tavily-primary`.
