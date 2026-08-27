# TDQ Workflow — portable bundle for Codex CLI

This bundle uses the REAL native mechanisms of Codex, not markdown read by hand:

| Layer | File in the bundle | What Codex does with it |
|---|---|---|
| Skill | `.agents/skills/<name>/SKILL.md` | scanned automatically, loaded on demand by `description` |
| MCP | `.codex/config.toml` | `[mcp_servers.<name>]`, environment variable NAMES only |
| Hook | `.codex/hooks.json` + `hooks/` | guards `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `Stop` |
| Fallback | `workflow/NN-*.md` | for any OTHER markdown-only harness to read in order |

Needs Codex CLI >= 0.147.0. An older build can still use `workflow/*.md`, but gets none
of the native layers.

## Install on a new machine — follow this exact order

The order matters: **trust FIRST, run AFTER**. While the project is untrusted, Codex skips
the WHOLE `.codex/` layer — MCP is not loaded, `hooks.json` is not read, and the bundle
looks empty without a single error.

1. **Copy** the whole content of this folder into the project root.
2. **Trust the project folder** — see the three ways just below.
3. **Check**:
   ```
   python3 scripts/tdq_checkportable.py check
   ```
   The output holds one line saying whether the project is trusted yet. Read by prefix:
   `CLEAN` done · `MISSING` not there · `DRIFT` differs from the manifest · `NOTE` something
   only you can do.
4. **Patch** if there is any `MISSING`/`DRIFT`: `python3 scripts/tdq_checkportable.py setup` —
   it rebuilds the two config files that can be recreated, always leaves a backup at
   `<file>.tdq-bak-<timestamp>` before overwriting, and reports `LEFT …` for whatever is only
   correct when copied from the original bundle.
5. **Set the environment variables** for MCP if `check` reports them missing. The script
   deliberately does NOT do this for you and never prints a key value — it only names the
   variable.
6. **Open Codex CLI** in the project, then **restart the session** once so the skills in
   `.agents/skills/` get scanned.
7. **Approve the hooks** in the Codex UI — a SEPARATE gate, see "Four things" below.
8. **Approve the MCP servers** — one approval per server.

## Trust — three ways, pick one

**Way 1 — let the script do it, no need to open Codex:**

```
cd <project root the bundle was copied into>
python3 scripts/tdq_checkportable.py setup --trust
```

**Way 2 — click inside Codex:** open Codex CLI right in the project folder; the first time it
enters an unknown folder it asks whether it may work here → pick the option that trusts the
folder.

**Way 3 — edit by hand** `~/.codex/config.toml` (or `$CODEX_HOME/config.toml`), adding:

```toml
[projects."/absolute/path/to/the/project"]
trust_level = "trusted"
```

The path must be ABSOLUTE with symlinks resolved, matching exactly the folder Codex runs in —
one character off and it does not take.

Way 1 is the ONLY path in this bundle that writes outside the bundle: it always leaves a
`<file>.tdq-bak-<timestamp>`, keeps the rest of the file untouched, and never writes over an
existing block. Without the `--trust` flag, `setup` does not touch that file at all.

To check that it took: run `check` again and read the trusted status line.

## Four things the machine CANNOT do for you

1. **Trust the folder** — `setup --trust` can do it for you (Way 1 above), or click yes in
   Codex.
2. **Approve the hooks** — hooks have their OWN trust gate: Codex shows "Review hooks" in the
   UI and you have to approve once. `--trust` does not open this gate, and editing
   `hooks.json` means approving again. Until approved, the hooks stay silent and never run.
3. **Approve the MCP servers** — every server in `.codex/config.toml` needs one approval from
   you.
4. **Restart** — new instructions are only loaded after the session restarts.

## Why step 3 runs the file directly instead of saying "run the tdq-checkportable skill"

The skill lives inside this very bundle, and Codex only scans `.agents/skills/` after the
project is trusted and the session has restarted. Calling the skill at the first step is a
circular dependency; running `python3 scripts/tdq_checkportable.py` straight from the
terminal is not. From the next time on, once everything is loaded, call the skill normally.

## Secret keys

No file in here holds a key value, only environment variable NAMES (`env_vars` in
`config.toml`). Set the variables yourself on your own machine before using MCP.
