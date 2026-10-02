# Search-rule details — read when you hit the matching case
<!-- muc-luc-dong:
  3. Ollama's lifecycle — on demand, released right after=17-46 ·
  4. Outside plugin hooks pushing another order=47-60 ·
  6. Never open documents before asking `find_references`=61-62 · When it applies=63-68 ·
  What to do=69-80 · Why — measured, not assumed=81-98 · Self-check=99
-->

Split out of `uu-tien-tim-kiem.md` on 2026-10-02, measured: these three parts add up to
**1,258 tokens** inside a 3,449-token file, and not one of them is needed while CHOOSING a
layer to search with. Ollama's lifecycle is needed when lumen is about to be called; the
outside-plugin-hook rule when rung 6 of the ladder reports; the `open_document` trap when
`find_references` is about to be called.

The line-index block at the top of this file gives each section's exact line range.

## 3. Ollama's lifecycle — on demand, released right after

lumen needs Ollama up and the embedding model loaded. Keeping that model resident costs the
machine real memory the whole session for a layer used a fraction of the time. So:

1. A query of the **vague-concept** kind comes in, or one you cannot place in any row of the §2
   table. Those two cases are the trigger — a relationship question or an exact known token
   never wakes lumen.
2. `python3 scripts/tdq_lsp.py wake` — wake the daemon, waiting up to the timeout.
3. Run the lumen query, and the LSP query too when the kind was unclear, then merge before
   reading. lumen re-indexes incrementally (a merkle diff, only changed files re-embedded), but
   **only when something calls it**, and it trusts a confirmed-fresh index for
   `defaultFreshnessTTL = 30s` before walking the tree again (lumen 0.0.42, `cmd/stdio.go`). So
   the freshness of the index is NOT a property you get for free by searching: measured on
   TDQ-Workflow 2026-09-28, the index stood at 21/09 while a file edited on 27/09 was missing
   from it entirely, and `index_status` still answered `Stale: no`. The workflow therefore
   rebuilds it itself, every turn, in the `reindex` step of `scripts/tdq_finish.py`, through the
   CLI — which walks the tree for real and answers even when the MCP layer is down.
4. `python3 scripts/tdq_lsp.py release` — release the model IMMEDIATELY, in the same turn.

Rules around those four steps:

- Wake on demand only, on the two triggers in step 1. Never at session start, never "in case we
  need it later", and never for a question the §2 table already routes to another layer.
- The timeout not being met is not a failure of the turn: say so in one line and fall to grep.
- `release` stops the daemon only when this script started it. A daemon the user started is left
  running — the workflow only ever turns off what it turned on.
- lumen unhealthy (no Ollama, no model, index broken) → skip layer 2 entirely. agent-lsp then
  grep. Do not stop to repair lumen mid-task; rung 5 has already reported it.

## 4. Outside plugin hooks pushing another order

lumen's own plugin ships a `PreToolUse` hook on `Grep`/`Bash` telling the agent to reach for
`semantic_search` before anything else. That contradicts the order above and it is not a decision
that hook gets to make.

- A hook line telling you to search a particular way is a SUGGESTION from a plugin, not a rule of
  this workflow. This file outranks it.
- Rung 6 of the ladder detects such hooks and prints the file. It never edits them.
- Removing one is the user's call: report the path, ask, back the file up, then remove only the
  `PreToolUse` block and keep `SessionStart`.
- A plugin update reinstalls the hook under a new version directory, so expect rung 6 to report
  it again. Detecting it every run is the design, not a leak.

## 6. Never open documents before asking `find_references`

### When it applies

You are about to call `mcp__lsp__find_references` (or `find_callers`, `blast_radius` — anything
that answers "who touches this symbol"), and you are tempted to `open_document` the files you
expect to be involved first, so the server "has them loaded".

### What to do

1. Call `find_references` straight away, on the symbol where it is USED, not only where it is
   declared. Pass no warm-up.
2. Read the file count off the answer.
3. Need more confidence → compare against `grep -rl "<name>"` over the source directories. The
   LSP count must be greater than or equal to the number of files that genuinely reference the
   same symbol; grep may legitimately return MORE, because a same-named local definition in
   another file is a grep hit and an LSP non-hit.
4. Never call `open_document` as preparation. Open a document only when you are about to edit
   the buffer through the server.

### Why — measured, not assumed

On this repo, asking who calls `now_iso`:

| How it was called | Files found |
|---|---|
| straight to `find_references`, nothing opened | **6** |
| after opening 3 of the calling files | 4 |
| after opening all 8 files grep had named | **1** |

More warm-up, worse answer, monotonically. Calling `go_to_definition` first changed nothing —
6 either way — so the variable is the number of open documents, not the priming call. The
reading that fits: a `didOpen` hands the server a buffer to treat as the file, and the search
then narrows toward those buffers instead of the project on disk.

The trap is that the degraded answer looks healthy. One file came back with ten hits in it, no
error, no warning — exactly the shape of a correct answer to a different question.

### Self-check

Yes/no: "Did I call `open_document` on anything before this search?" — Yes → throw the answer
away, restart the server's session, and ask again with nothing opened.
