# TDQ Workflow — portable bundle for Antigravity CLI (agy)

agy's exact global config path is NOT settled across sources as of 2026-08 — this bundle does
not guess one. It installs its own core (skills, hook scripts) at ONE fixed path under your
home folder, and ships 3 config files whose content you copy into EVERY known candidate
location. Self-check with agy's own commands tells you which one actually took.

## Install on a new machine — follow this exact order

1. **Copy the core.** Copy `skills/`, `hooks/`, `scripts/` from this bundle so the whole tree
   sits at exactly:
   ```
   ~/.gemini/antigravity-cli/tdq/
   ```
   (create the folders if they do not exist yet). Every generated config file's command/path
   below points at this exact location — moving the core elsewhere breaks all 3 config files.

2. **Copy the skill files** into EVERY candidate skill root agy might scan on your version:
   - `~/.gemini/antigravity-cli/skills/`
   - `~/.gemini/antigravity/skills/`
   - `~/.gemini/skills/`
   (copy the whole content of `skills/` into each — harmless if a path does not exist on your
   install, just skip it).

3. **Copy `config/hooks.json`** into EVERY candidate hook-config location:
   - `~/.gemini/config/hooks.json`
   - `~/.gemini/antigravity-cli/hooks.json`

4. **Copy `config/settings.json`** (the Fine-Grained Permissions Engine, a SECOND and coarser
   defensive layer — the hooks above are the real hard `deny`) into:
   - `~/.gemini/antigravity-cli/settings.json`

5. **Copy `config/mcp_config.json`** into BOTH known locations:
   - `~/.gemini/config/mcp_config.json`
   - `~/.gemini/antigravity-cli/mcp_config.json`

6. **Set the environment variables** the MCP servers need. This bundle never writes a key
   value, only the variable NAMES — set `TAVILY_API_KEY` (and the backup server's variable)
   yourself before using MCP.

7. **Restart agy**, then self-check with agy's own commands:
   - `/skills` — do the `tdq-conventions, tdq-lsp-setup, tdq-intake, tdq-spec, tdq-plan, tdq-build, tdq-checkportable, tdq-status, tdq-check-status` skills show up? Not there at one path → try another
     candidate from step 2 that you have not copied to yet.
   - `/mcp` — do `tavily-primary`/`tavily-backup` show up as configured servers?
   - `/permissions` — does the permissions list include the `deny` entries from
     `config/settings.json`?

8. **Smoke-test the hard deny manually.** Ask agy to run a command matching one of the 2
   banned cases (e.g. `git checkout -b antigravity-test`, or writing straight to
   `docs/tdq/state.json` through the shell) and confirm it is actually refused. If it is NOT
   refused, the hook did not load — check step 3/2 again, or try another candidate path.

## What this bundle cannot do for you

1. **Know which candidate path your agy version reads** — no source available as of 2026-08
   confirms one canonical global path per config type; step 7's self-check is the only way to
   find out on YOUR machine.
2. **Restart** — step 7. Skip it and the copied files just sit there, unloaded.
3. **Set the MCP environment variables** — step 6.

## Secret keys

`config/mcp_config.json` only records the NAMES of environment variables, never a key value.

## Known limitation

This bundle has not been exercised against a real agy install — see the risk table in the
originating spec. The layered design (hard-deny hook + coarser permissions-engine `deny`) is
meant to degrade safely if one layer does not load on your version: report back which
candidate paths actually worked so this bundle can drop the ones that never do.
