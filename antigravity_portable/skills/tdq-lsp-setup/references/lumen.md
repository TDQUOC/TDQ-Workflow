# lumen — upstream, and how to install it on each host

Upstream: <https://github.com/ory/lumen> (Ory Corp, Apache-2.0). It is a Go binary that indexes a
repo with AST parsing, embeds through Ollama or LM Studio, and exposes vector search over MCP.
Everything runs locally: no cloud call, no npm at runtime.

This workflow does NOT ship lumen. The version this repo has been measured against is **0.0.42**.
Verify the copy on a machine with `go.mod` (`module github.com/ory/lumen`) and
`.claude-plugin/plugin.json` (`"repository": "https://github.com/ory/lumen"`), not by name alone.

## Install, per host

Ask the user before any of these — installing a plugin or a marketplace is their call.

| Host | Commands |
|---|---|
| Claude Code (upstream) | `/plugin marketplace add ory/claude-plugins` then `/plugin install lumen@ory` |
| Claude Code (this machine) | installed as `lumen@claude-plugins-official`, Anthropic's mirror of the same repo |
| Codex CLI ≥ 0.147.0 | `codex plugin marketplace add ory/claude-plugins` then `codex plugin add lumen@ory` |
| OpenCode | add `"@ory/lumen-opencode"` to the `plugin` array of `opencode.json` |
| Cursor | the bundle `.cursor-plugin/` inside the repo, through Cursor's plugin workflow |
| Anything else | run the MCP server directly, see below |

The marketplace already exists → upgrade before installing: `codex plugin marketplace upgrade ory`
(the Claude Code equivalent is `claude plugin marketplace update ory`).

## Any other host — the MCP server on its own

lumen is a plain stdio MCP server, so any client that speaks MCP can use it without a plugin
system. Build or fetch the binary, then point the client at `lumen stdio`:

```
git clone https://github.com/ory/lumen && cd lumen && go build -o bin/lumen .
```

`~/.gemini/antigravity-cli/tdq/scripts/run` in the repo does the same job for a packaged copy. It resolves the plugin root from
whichever root variable the host exports — Claude Code, Cursor or Codex each set their own. Then
it looks for `bin/lumen` and `bin/lumen-<os>-<arch>`, downloading the release binary on first run
when neither is present. That fallback chain is why one bundle works under three hosts.

Registering it with Claude Code by hand, without the plugin:

```
claude mcp add --scope user lumen -- <path to>/lumen stdio
```

## What it still needs, whatever the host

Ollama installed, the daemon reachable, and the embedding model pulled:
`ollama pull ordis/jina-embeddings-v2-base-code`. Rung 5 of `tdq_lsp.py kiem` checks exactly those
three things — **not** whether the plugin or the MCP server itself is present. A machine can pass
rung 5 with no lumen tool registered at all, so check the tool list too.

## The hook it brings with it

The plugin registers a `PreToolUse` hook on `Grep`/`Bash` nudging the agent to reach for lumen
first. That competes with the search order this workflow settled on, which is what rung 6 detects.
Removing it is the user's decision, and a plugin update puts it back — see the rung 6 section of
[SKILL.md](../SKILL.md).
