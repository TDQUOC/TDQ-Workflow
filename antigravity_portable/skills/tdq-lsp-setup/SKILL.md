---
name: tdq-lsp-setup
description: Check and set up agent-lsp so the workflow searches code by meaning, not by text. Six rungs - binary, lsp MCP server, language servers, tool permissions, lumen health, conflicting plugin hooks. Use when opening a request, when an LSP tool fails, or on a new machine.
---

# TDQ LSP Setup — agent-lsp as the workflow's search layer

Load [tdq-conventions](../tdq-conventions/SKILL.md).
Upstream: <https://github.com/blackwell-systems/agent-lsp> · local clone on this machine:
`~/Documents/Add_on_for_claude/agent-lsp`. 30 languages, 65 MCP tools, one Go binary.

**Why it exists.** grep matches characters; agent-lsp answers the questions the language server
itself answers — where is this defined, who calls it, what type is it. That is the difference
between finding a name and finding the thing. The search-order rule lives in
[references/uu-tien-tim-kiem.md](references/uu-tien-tim-kiem.md) and is binding on every phase.

## The one hard rule of this skill

**Never install anything, never edit another plugin's files, without the user saying yes first.**
`~/.gemini/antigravity-cli/tdq/scripts/tdq_lsp.py` only ever DIAGNOSES and prints the exact command. A human approves, then the
command runs. This holds even when a rung is trivially fixable and even when the build is blocked.
Starting or stopping a process already installed on the machine is not installing — that is why
`danh-thuc` and `nha` are allowed to run unattended.

## The ladder — `python3 ~/.gemini/antigravity-cli/tdq/scripts/tdq_lsp.py kiem`

Six rungs, printed one line each, a missing rung printing the command that fixes it.

| Rung | What it checks | When it is missing |
|---|---|---|
| 1 | the `agent-lsp` binary is on PATH | print the install command, ask, then run it |
| 2 | the `lsp` MCP server is registered in `~/.claude.json` | `agent-lsp init` |
| 3 | a language server exists for every language THIS project uses | the per-language command, see [references/languages.md](references/languages.md) |
| 4 | `mcp__lsp__*` sits in the allow list of `~/.claude/settings.json` | add the entry, otherwise every call prompts |
| 5 | lumen's health — ollama installed, model pulled, daemon reachable | warning only; lumen is the fallback, not the main layer |
| 6 | an outside plugin hook pushing a different search order | report the path, ASK the user, never edit it yourself |

Rungs 1–4 are actionable, so a gap there makes the exit code 3. Rungs 5–6 only warn and never
change the exit code: search still works through agent-lsp and grep without either of them.

Rung 3 sniffs the languages from the files actually in the project, ignoring `.git`,
`node_modules`, `.venv`, `portable_*` and friends. A language under 3 files is treated as noise.
YAML and JSON are config formats in nearly every repo, so they never trigger a request.

## Rung 6 — a conflicting plugin hook

Some plugins register a `PreToolUse` hook on `Grep`/`Bash` that tells the agent to search their
way first. That competes with the order this workflow settled on. The rung names the plugin and
the file. What happens next is the USER's call:

1. Report: which plugin, which file, which matcher.
2. Ask for permission to remove just that `PreToolUse` block, keeping `SessionStart`.
3. Only then edit it, after backing the file up next to it.

A plugin update reinstalls the hook, and the cache path carries the version number, so expect to
see this rung come back. That is the point of checking it every time rather than fixing it once.

## Ollama, on demand only

`python3 ~/.gemini/antigravity-cli/tdq/scripts/tdq_lsp.py danh-thuc` wakes the daemon; `python3 ~/.gemini/antigravity-cli/tdq/scripts/tdq_lsp.py nha`
releases the embedding model right after the search. Never leave a model resident — that is the
machine cost the user objected to. Full lifecycle:
[references/uu-tien-tim-kiem.md](references/uu-tien-tim-kiem.md).

`nha` kills the daemon only when this script started it, tracked by a marker file. A daemon the
user started stays up. On macOS the Ollama desktop app supervises the server and restarts it.
On such a machine the daemon is effectively always up, so only the model release matters.

## Runbook — setting a machine up, and re-configuring it later

These are the exact steps run on 2026-08-23, in order, each with its backup and its undo. Read
this instead of digging an old plan out when the machine changes or a language gets added. Every
step changes the machine or a file outside the repo, so **each one needs the user's yes first** —
that rule has no exception, not even for a blocked build.

**Step 1 — the binary.** `curl -fsSL https://raw.githubusercontent.com/blackwell-systems/agent-lsp/main/install.sh | sh`
· check `agent-lsp --version` · undo `agent-lsp uninstall`.

**Step 2 — the language servers**, before the MCP server, because auto-detect only sees what is
already installed. The four this workflow keeps: `npm i -g pyright` ·
`npm i -g typescript-language-server typescript@5` · `dotnet tool install -g csharp-ls` ·
`brew install lua-language-server`. Put `~/.dotnet/tools` on PATH for `csharp-ls`. Check with
`agent-lsp doctor`: it starts every server and prints `Status: ok` or the real error. Any other
language: the table in [references/languages.md](references/languages.md).

**Step 3 — register the MCP server.** Do NOT run `agent-lsp init` unattended. With no terminal to
answer its prompts it takes the defaults silently and writes `.mcp.json` plus a `CLAUDE.md` into
the current directory. Register it explicitly instead, which also names the server `lsp` and
covers languages auto-detect skips, Lua among them:

```
claude mcp add --scope user lsp -- agent-lsp \
  python:pyright-langserver,--stdio typescript:typescript-language-server,--stdio \
  javascript:typescript-language-server,--stdio csharp:csharp-ls \
  lua:lua-language-server c:clangd cpp:clangd
```

The syntax is `language:binary[,arg…]`. Back `~/.claude.json` up first; undo with
`claude mcp remove --scope user lsp`. A newly registered server loads only on the NEXT session, so
an `mcp__lsp__*` call in the session that registered it will not find the tool yet.

**Step 4 — tool permissions.** Add `"mcp__lsp__*"` to `permissions.allow` of
`~/.claude/settings.json`, backing that file up beside itself first. Without it every LSP call
raises a prompt, and a search layer that asks permission per call stops being used.

**Step 5 — the conflicting plugin hook**, per the section above. Back the plugin's `hooks.json` up
next to itself with the version in the name, drop only `PreToolUse`, keep `SessionStart`. The hook
returns with the next plugin update, and hooks load at session start, so the nudging line keeps
appearing until the session restarts.

**Acceptance:** `python3 ~/.gemini/antigravity-cli/tdq/scripts/tdq_lsp.py kiem` prints six rungs ĐẠT and exits 0.

Done when: `kiem` prints six rungs with no actionable gap, and one `mcp__lsp__*` call returns the
right file and line for a real function in the repo.
Next step: go back to the phase that called this skill and search with LSP first, per
[references/uu-tien-tim-kiem.md](references/uu-tien-tim-kiem.md).
