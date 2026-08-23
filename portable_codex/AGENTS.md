# TDQ Workflow — guide for agents

Soul: chất lượng > runtime > context cost · luật gốc: `workflow/references/tdq-conventions/soul.md`

This bundle runs a pipeline with approval gates: intake → spec → plan → implement → QC →
report. Only the USER may approve, and every state change goes through `scripts/tdq_state.py`.

## Step 0 — check compatibility BEFORE anything else

```
python3 scripts/tdq_checkportable.py check
```

If it reports something missing, run `python3 scripts/tdq_checkportable.py setup`: it rebuilds
the two config files that can be recreated (`.claude/settings.json`, `.mcp.json`), always
leaves a backup at `<file>.tdq-bak-<timestamp>` before overwriting, and reports `LEFT …` for
whatever is only correct when copied from the original bundle.

The line `NOTE project is not trusted` is the most important line this command prints: while
untrusted, Codex ignores both `.codex/config.toml` and `.codex/hooks.json`, and the bundle
runs as if it were not there.

## Running on Codex CLI (>= 0.147.0) — use the native layer, no need to read `workflow/`

- `.agents/skills/` — Codex loads skills by `description` on its own, you do not pick files.
- `.codex/config.toml` — MCP servers; environment variable NAMES only, set them yourself.
- `.codex/hooks.json` + `hooks/` — machine-guarded approval gates (`SessionStart`,
  `UserPromptSubmit`, `PreToolUse` for `Bash` and `apply_patch`, `Stop`).

## Another harness — read `workflow/` in the exact numbered order

With no skill system, the number in the file name IS the routing mechanism:

- `workflow/01-conventions.md`
- `workflow/02-lsp-setup.md`
- `workflow/03-intake.md`
- `workflow/04-spec.md`
- `workflow/05-plan.md`
- `workflow/06-build.md`
- `workflow/07-checkportable.md`
- `workflow/08-status.md`
- `workflow/09-check-status.md`

Full phase table: `workflow/phases.md` (generated from the `PHASE_TABLE` constant, never
edited by hand).

## Four things the machine CANNOT do for you

1. Grant access to the project folder on the first run (`setup --trust` can do this for you).
2. Approve the hooks in the Codex UI — hooks have their own trust gate, `--trust` does NOT
   open it.
3. Approve every MCP server declared in `.codex/config.toml`.
4. Restart the session after a new instruction folder is added.
