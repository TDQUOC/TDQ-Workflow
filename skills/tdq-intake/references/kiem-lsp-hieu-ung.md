# The effect check — proving every LSP module actually answers
<!-- muc-luc-dong:
  Why the ladder alone is not enough=11-25 · What a module is=26-33 ·
  The four steps, per module=34-51 · When a module fails=52
-->

Run at intake step 1b whenever rung 8 of `python3 scripts/tdq_lsp.py check` does not pass. Since
0.59.0 this is no longer a soft step: `tdq_state.py init` refuses to open a request while any LSP
module of the project is unproven, stale or failed.

## Why the ladder alone is not enough

Rungs 1–7 check that something EXISTS: a binary, a registered server, a permission entry, a
config file — and `agent-lsp doctor`, which starts every server. None of them sends the question the
agent will send. On 2026-10-07 `doctor` reported healthy in all three failures measured that day:

- `start_lsp` without `language_id` on a Python repo → agent-lsp started every server, made
  TypeScript current, tsserver crashed `0xc0000409` or answered "No Project";
- a TypeScript monorepo with two `tsconfig.json` → "No Project" until a file was opened;
- `start_lsp html` after `start_lsp python` → `find_symbol` answered empty for Python names.

And earlier (2026-09-03): a missing import-root marker left `find_callers` reaching 1 of 15 files
while six rungs read ĐẠT. Rung 6 catches that cause; this check catches the symptom, whatever the
cause.

## What a module is

One (language, root) pair: the root is the deepest directory holding that language's marker
(`tsconfig.json` > `jsconfig.json` > `package.json`; `pyrightconfig.json` > `pyproject.toml` >
`setup.py`; `go.mod`; `Cargo.toml`…). A one-language repo is one module; claudecodeui is
`typescript:.` + `typescript:server`. `python3 scripts/tdq_lsp.py module` prints the list with the
status of each. Markup (HTML, CSS) has no import graph and is never checked.

## The four steps, per module

1. `python3 scripts/tdq_lsp.py kich-ban` — for every module still blocking, the script picks a
   symbol defined once in that module and used from at least one other file, and prints three MCP
   calls: `start_lsp` (that module's root + `language_id`), `open_document`, `find_references`.
2. Send those three calls EXACTLY as printed — same root, same `language_id`, same line/column.
   Changing them proves a different path from the one the agent will use. `find_references`
   answering "workspace is still being indexed" is not a failure: a fresh daemon indexes for a
   while (a large TypeScript repo took over 20 s on 2026-10-08) — do other work, then resend it.
3. Read `symbols=N` on the `find_references` answer. `find_references` through agent-lsp prints
   namespaces, not file paths, so the script judges the COUNT: it passes when N is greater than the
   occurrences of the name in its own file, i.e. at least one reference came from another file.
4. `python3 scripts/tdq_lsp.py ghi-kiem <module> <N>` — the script records the verdict. Do not
   judge it yourself.

A result stays valid 24 hours, and until the module's marker file or its MCP `lsp` entry changes;
after that the module is stale and the steps run again for that module only.

## When a module fails

1. Read the cause, in this order: `start_lsp` returned an error (server crash → rung 3 and the
   commit-memory warning of `tdq_setup.py`; a crash `0xc0000409` with little free commit is
   `VirtualAlloc failed`, fixed by a larger pagefile, not by reinstalling) · N = 0 or only the
   own-file count (wrong root, missing marker → rung 6) · `No Project` (TypeScript: the file was
   not opened first).
2. Fix what is yours to fix — `python3 scripts/tdq_setup.py` again, a reconnect of MCP `lsp`
   (`/mcp`) after a server was declared — then rerun `kich-ban` for that module.
3. Still failing → tell the user the module, the count and the cause in one block. Only the user
   may open the request anyway, with `init ... --bo-qua-lsp "<reason>"`; the reason lands in state
   (`lsp_bo_qua`) and the report reads it out.
