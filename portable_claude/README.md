# TDQ Workflow — portable bundle for Claude Code

## Install on a new machine — follow this exact order

1. **Copy** the whole content of this folder into the root of your project, keeping
   `.claude/` and `.mcp.json` as they are.
2. **Check** before opening Claude Code:
   ```
   python3 .claude/tdq/scripts/tdq_checkportable.py check
   ```
   Read by prefix: `CLEAN` done · `MISSING` not there · `DRIFT` differs from the manifest ·
   `NOTE` something only you can do.
3. **Patch** if there is any `MISSING`/`DRIFT`: `python3 .claude/tdq/scripts/tdq_checkportable.py setup`
   (see the warning section below — it can only rebuild two files).
4. **Set the environment variables** for MCP if `check` reports them missing. The script
   deliberately does NOT do it for you and never prints a key value — it only names the
   variable.
5. **Open Claude Code** in that project. The first time it asks whether you trust this
   folder → **click yes**. Without that, the hooks and the project config have no effect.
6. **Restart the session** so the skills and agents in the new folder get scanned.
7. **Approve the MCP servers** — every server in `.mcp.json` needs one approval from you.

Once the seven steps are done, say `run the tdq-checkportable skill` so the machine runs a
final check for you.

## Three things the machine CANNOT do for you

1. **Trust the folder** — step 5 above. Only you can click it; no command-line flag in this
   bundle replaces it.
2. **Approve the MCP servers** — step 7.
3. **Restart** — step 6. Skip it and the new skills just sit there, with no error at all.

## Warning about self-patching

`setup` rebuilds exactly the two config files the bundle holds enough data to recreate:
`.claude/settings.json` (from the bundled `hooks.json`) and `.mcp.json`. Overwriting always
leaves a backup at `<file>.tdq-bak-<timestamp>`, and the `env` block you added yourself is
kept.

Any other file that is missing or has drifted is **not** invented by `setup` — it reports
`LEFT …` and exits non-zero; the only correct source is the original bundle, copy it from
there. Want a check without any change: use `check`.

## Secret keys

`.mcp.json` only records the NAMES of environment variables, never a key value. Set the
variables yourself on your own machine before using MCP.
