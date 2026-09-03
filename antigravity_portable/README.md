# TDQ Workflow — plugin bundle for Antigravity CLI (agy)

This directory IS an agy plugin: `plugin.json` at the root, `skills/` beside it, plus
`hooks.json` and `mcp_config.json`. The layout was read off a live `agy 1.1.11` install on
2026-09-03. Installing is one copy plus two config keys.

## Install — this exact order

1. **Copy this whole directory** to the plugin root, keeping the directory name:
   ```
   ~/.gemini/config/plugins/tdq-workflow/
   ```

2. **Enable the plugin** in `~/.gemini/config/config.json` — add the key, keep everything else that file
   already holds:
   ```json
   { "plugins": { "tdq-workflow": { "enabled": true } } }
   ```

3. **Register the skill root** in `~/.gemini/config/skills.json`, appending to the existing `entries` array:
   ```json
   { "entries": [ { "path": "~/.gemini/config/plugins/tdq-workflow/skills" } ] }
   ```

4. **Set the environment variables** the MCP servers need. This bundle only ever records
   variable NAMES, never a key value — export `TAVILY_API_KEY` (and the backup server's
   variable) yourself before using MCP.

5. **Restart agy**, then self-check with agy's own commands:
   - `agy plugin list` — is `tdq-workflow` listed and enabled?
   - `/skills` — do the `tdq-conventions, tdq-lsp-setup, tdq-intake, tdq-spec, tdq-plan, tdq-build, tdq-checkportable, tdq-status, tdq-check-status` skills show up?
   - `/mcp` — are `tavily-primary`/`tavily-backup` listed as configured servers?

6. **Smoke-test the hard deny.** Ask agy to run one of the banned cases (e.g.
   `git checkout -b antigravity-test`, or writing straight to `docs/tdq/state.json` through the
   shell) and confirm it is refused. Not refused → the hook did not load; re-check steps 1–2.

## The hook `command` paths are absolute, and baked at build time

agy requires an ABSOLUTE `command`; a `~` inside quotes is not expanded and the hook dies with
exit 127. `hooks.json` therefore carries a real expanded path — the home folder of the machine
that BUILT the bundle. Copying a prebuilt bundle to another user's machine leaves those paths
pointing at the wrong home. Rebuild it locally instead — run the repo's `build_portable.py`
from a clone of TDQ-Workflow, then copy the freshly built directory over.
`python3 scripts/tdq_checkportable.py check --root <this directory>` prints a NOTE when the
baked home does not match the current one.

## What this bundle cannot do for you

1. **Restart agy** — step 5. Skip it and the files just sit there, unloaded.
2. **Set the MCP environment variables** — step 4.
3. **Guarantee the layout on a different agy version.** It was verified against `agy 1.1.11`
   only; step 5's self-check is how you find out on YOUR machine.

## Secret keys

`mcp_config.json` records only the NAMES of environment variables, never a key value.
