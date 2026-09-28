# The search-order rule — the single source

This file is the ORIGINAL. `tdq-intake` (two spots), `tdq-spec`, `tdq-plan` and `tdq-build` each
carry one line pointing back here; none of them restates the rule. Change the order → change it
here, and the five hook points keep matching because they only ever point.

## Table of contents

- 1. The order, settled
- 2. The table — kind of question → which layer first, with the numbers
- 2b. The fourth layer: graphify, the map
- 2c. Runtime dependencies — what each layer needs, and what it falls back to
- 3. Ollama's lifecycle — on demand, released right after
- 4. Outside plugin hooks pushing another order
- 5. Where this rule is hooked in
- 6. Never open documents before asking `find_references`

## 1. The order, settled

**There is no single winning layer. Four exist, and you pick the first one from the KIND of
question you are asking.** Relationship questions go to agent-lsp. An exact known name goes to
grep. A vague concept goes to lumen. A blast-radius or architecture question goes to graphify.
**Only when the kind is unclear do you call several at once and merge.**

The canonical sentence, quoted verbatim at every hook point:

> Đối tượng tìm là ký hiệu code (hàm, class, biến, kiểu) → chọn lớp theo LOẠI truy vấn: quan
> hệ và đổi tên dùng `mcp__lsp__*`; tên chính xác đã biết dùng grep; khái niệm mơ hồ dùng
> lumen; vỡ lan và bản đồ kiến trúc dùng graphify; chưa chắc loại nào thì gọi song song rồi
> gộp. Bảng đầy đủ kèm số đo: `skills/tdq-setup/references/uu-tien-tim-kiem.md`.

This is a soft rule, not a blocking hook. Picking the wrong first layer for the kind of question
is a QC defect, not a turn the machine refuses. Two exemptions, both narrow:

- The target is text, not a symbol — a message string, a config key, a comment, a filename.
- The ladder's rungs 1–4 are not satisfied, so there is no LSP to try. Say so in one line, then
  fall through to grep.

## 2. The table — kind of question → which layer first, with the numbers

Every number below is measured, on this repo, in report
`docs/tdq/report/2026-09-03-0017-them-pyrightconfig-do-lai.md`. Nothing here is an estimate.

| Kind of question | Example | First layer | The measurement behind it |
|---|---|---|---|
| relationship — who calls this, blast radius, safe rename | "who calls `tdq_state.load`" | **agent-lsp** | file coverage **15/15**, zero false positives; grep hits the same 15 but drags in 6 more files it should not — precision 67 % |
| exact name you already know the token of | "where is `bac6_hook_xung_dot` defined" | **grep** | grep answers in ~0.1 s against LSP's 3–6 s, and both reach 6/6 locations; LSP wins nothing here but time lost |
| vague concept, no name to hang it on | "the spot that stamps the approval time" | **lumen** | LSP ranks the real target **13/62** — it is a NAME index, it does not understand concepts |
| type, diagnostics, implementations | "what type does this return" | **agent-lsp** | lumen cannot answer these at all |
| the kind is unclear | anything you cannot place in a row above | **call in parallel, merge** | cheaper to pay two queries than to pick wrong and re-search |

Two things the table does NOT say. It does not say grep is a fallback — for an exact known token
grep is the *right* first layer, not a concession. And it does not say LSP is optional: the 15/15
vs 67 % gap only appeared once the repo had a real `pyrightconfig.json`. An LSP with no import-root
config silently answers relationship questions with **7 %** coverage while every rung still reports
ĐẠT, which is why rung 7 exists.

Standing exceptions: a language with no server installed → lumen and grep only. lumen unhealthy →
agent-lsp then grep.

## 2b. The fourth layer: graphify, the map

graphify answers a question none of the other three can: **who is affected if I change this, two
hops out.** It reads a graph built from the source, so it costs nothing to traverse and it never
guesses from names. It is not a type checker and it holds no diagnostics — nodes carry a label,
a source file and a location, nothing more.

**Its value changes with the KIND of repo, so no number about it means anything without the repo
name beside it.** Measured 2026-09-28 on two repos with the same tool:

| Measure | TDQ-Workflow (docs/skills heavy) | claudecodeui (995 files, TS/React) |
|---|---|---|
| nodes / edges | 2415 / 5139 | 6258 / 16121 |
| **cross-file edges** | **12%** | **54%** |
| `calls` crossing files | 100 | **981** |
| `imports_from` | 8 | **3605** |
| **`rationale_for`** | **1035** | **2** |
| rebuild time | — | **16.5 s / 917 files** |

Two faces of one tool: a real code repo gives a **dependency map**, a documentation-heavy repo
gives **code ↔ reason** links. Neither repo gives both. On claudecodeui, `affected AppError`
returned **60 files with zero false positives** where `grep -rl` returned 66 — the 6 extra were
comments, a similarly named `AppErrorOptions`, and the definition site itself.

Cost, measured on claudecodeui: `affected --depth 1` is **12.6 KB against grep -rn's 42.9 KB**,
3.4× cheaper; `--depth 2` opens 134 → 207 nodes, a question grep cannot answer at any price;
`god-nodes` costs 251 bytes for 8 hubs.

**The one hard condition: the graph must be FRESH.** A stale graph does not fail loudly; it
answers about code that no longer exists. Measured on TDQ-Workflow: a graph 8 days old, 34% of
its nodes (845 of 2415) pointing into a deleted directory. `explain` then needed 3 extra queries
to disambiguate. Rung 8 of the ladder checks exactly this, and the `graphify` step of
`tdq_finish.py` rebuilds it whenever a code file changed.

## 2c. Runtime dependencies — what each layer needs, and what it falls back to

A layer never announces its own death. It answers less, or answers about the past, and the shape
of that answer looks exactly like a correct one. So the fallback is written down in advance:

| Layer | Runtime dependency | Dead → falls back to |
|---|---|---|
| grep | nothing | — it IS the floor |
| agent-lsp | a language server + an import-root marker (`pyrightconfig.json` and friends) | grep, losing types and diagnostics |
| graphify | a `graph.json` newer than the code | agent-lsp over several round trips, more expensive |
| lumen | ollama + the embedding model + an index holding the working tree's newest content | grep with more keywords, or reading `docs/` |

Rungs 1–8 of `scripts/tdq_lsp.py check` measure every one of those dependencies. Rungs 5 and 8
measure them **by effect**: a real round trip, and a real freshness probe. A rung that only
checks existence is blind to the way these two tools actually fail.

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

## 5. Where this rule is hooked in

| Phase | File | What LSP does there |
|---|---|---|
| intake / analyze | `skills/tdq-intake/SKILL.md`, `references/analyze-full.md` | diagnose the environment; read code by symbol, not by grep |
| spec | `skills/tdq-spec/SKILL.md` | build §2b module boundaries from real references, not from directory names |
| plan | `skills/tdq-plan/SKILL.md` | build the `Chạm:` line from "who calls this", not from a guess |
| implement | `skills/tdq-build/SKILL.md` | `## Hard rules`, and "Search before creating" at step 2.4 |

Each of those five files carries the quoted sentence from section 1 and a link back here. They
must not drift: `tests/test_tdq_setup_skill.py` compares them against this file and fails when one
of them is edited alone.

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
