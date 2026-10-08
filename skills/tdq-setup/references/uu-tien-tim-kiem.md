# The search-order rule — the single source
<!-- muc-luc-dong:
  1. The order, settled=16-59 ·
  2. The table — kind of question → which layer first, with the numbers=60-88 ·
  2b. graphify, the map=89-122 ·
  2c. Runtime dependencies — what each layer needs, and what it falls back to=123-139 ·
  5. Where this rule is hooked in=140-151 ·
  6. The gate that holds this rule (since 2026-10-03)=152-172 ·
  3. Two details that live in a sibling file=173
-->

This file is the ORIGINAL. `tdq-intake` (two spots), `tdq-spec`, `tdq-plan` and `tdq-build` each
carry one line pointing back here; none of them restates the rule. Change the order → change it
here, and the five hook points keep matching because they only ever point.

## 1. The order, settled

**There is no single winning layer. Three exist, and you pick the first one from the KIND of
question you are asking.** Relationship questions go to agent-lsp. An exact known name goes to
grep. A vague concept, a blast-radius or an architecture question goes to graphify — for a vague
concept, together with a grep over several synonyms. **Only when the kind is unclear do you call
several at once and merge.**

The canonical sentence, quoted verbatim at every hook point:

> Đối tượng tìm là ký hiệu code (hàm, class, biến, kiểu) → chọn lớp theo LOẠI truy vấn: quan
> hệ và đổi tên dùng `mcp__lsp__*`; tên chính xác đã biết dùng grep; khái niệm mơ hồ dùng
> `graphify query` song song grep nhiều từ đồng nghĩa; vỡ lan và bản đồ kiến trúc dùng graphify;
> chưa chắc loại nào thì gọi song song rồi gộp. Bảng đầy đủ kèm số đo:
> `skills/tdq-setup/references/uu-tien-tim-kiem.md`.

This is a soft rule for the CHOICE of layer: picking the wrong first layer for the kind of
question is a QC defect, not a turn the machine refuses. Two exemptions, both narrow:

- The target is text, not a symbol — a message string, a config key, a comment, a filename.
- The ladder's rungs 1–4 are not satisfied, so there is no LSP to try. Say so in one line, then
  fall through to graphify and grep.

An LSP that answers "LSP client not initialized" is not dead: call `mcp__lsp__start_lsp`, then ask
again. Measured 2026-10-07: reading that answer as "LSP is dead" cost a session one extra denied
search.

**Calling LSP per module (0.59.0, BINDING).** A project is a list of LSP modules — one
(language, root) pair each, printed by `python3 scripts/tdq_lsp.py module`; a one-language repo is
one row, a monorepo with two `tsconfig.json` is two. agent-lsp runs every configured server side by
side and routes a FILE tool (`find_references`, `find_callers`, `list_symbols`…) by the file's
extension, but `find_symbol` only ever asks the server of the LAST `start_lsp` (upstream issue #55).
So:

1. Before working inside a module: `start_lsp` with `root_dir` = that module's root AND
   `language_id` = its language. Never omit `language_id` — agent-lsp then starts every server and
   makes TypeScript current (crash `0xc0000409` / "No Project" on a Python repo, 2026-10-07). The
   hook `lsp_gate.py` (`TDQ:LSP`) denies such a call and lists the valid ones.
2. TypeScript/JavaScript: `open_document` one file of the module before asking anything —
   tsserver answers "No Project" until a file is open.
3. Prefer the file tools; they cannot hit the wrong server. `find_symbol` comes back empty after a
   `start_lsp` for another language — that is the routing, not a missing symbol.
4. Moving to another module = `start_lsp` again with that module's root and language.

## 2. The table — kind of question → which layer first, with the numbers

Every number names the repo it was measured on. The LSP and grep rows come from
`docs/tdq/report/2026-09-03-0017-them-pyrightconfig-do-lai.md` (TDQ-Workflow); the vague-concept
row from `docs/tdq/bench/2026-10-07-1843-chat-luong-lumen/tong-hop.md` (TDQ-Workflow and
claudecodeui, 12 concept questions each).

| Kind of question | Example | First layer | The measurement behind it |
|---|---|---|---|
| relationship — who calls this, blast radius, safe rename | "who calls `tdq_state.load`" | **agent-lsp** | file coverage **15/15**, zero false positives; grep hits the same 15 but drags in 6 more files it should not — precision 67 % |
| exact name you already know the token of | "where is `bac5_hook_xung_dot` defined" | **grep** | grep answers in ~0.1 s against LSP's 3–6 s, and both reach 6/6 locations; LSP wins nothing here but time lost |
| vague concept, no name to hang it on | "the spot that writes a temp file then swaps it in" | **`graphify query` + grep over synonyms, merged** | LSP ranks the real target **13/62** — it is a NAME index. Without a semantic layer, agents on grep/LSP/graphify hit **11/12** (TDQ-Workflow) and **10/12** (claudecodeui) fully and missed **0**, against 12/12 and 11/12 with lumen, at **0.88×** and **1.06×** the tokens |
| type, diagnostics, implementations | "what type does this return" | **agent-lsp** | the only layer that answers these at all |
| the kind is unclear | anything you cannot place in a row above | **call in parallel, merge** | cheaper to pay two queries than to pick wrong and re-search |

Two things the table does NOT say. It does not say grep is a fallback — for an exact known token
grep is the *right* first layer, not a concession. And it does not say LSP is optional: the 15/15
vs 67 % gap only appeared once the repo had a real `pyrightconfig.json`. An LSP with no import-root
config silently answers relationship questions with **7 %** coverage while every rung still reports
ĐẠT, which is why rung 6 exists.

Standing exception: a language with no server installed → graphify and grep only.

lumen (semantic search) was a fourth layer until 0.58.0. It was removed because the measurement
above showed no significant loss without it, while it cost an ollama daemon, a per-turn reindex
and a layer that went silently stale. Its concept questions were written by agents searching with
grep, so they favour grep — the measurement refutes "worse without lumen", it does not prove lumen
useless anywhere.

## 2b. graphify, the map

graphify answers a question no other layer can: **who is affected if I change this, two hops out.**
It reads a graph built from the source, so it costs nothing to traverse and it never guesses from
names. It is not a type checker and it holds no diagnostics — nodes carry a label, a source file
and a location, nothing more.

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
to disambiguate. Rung 7 of the ladder checks exactly this, and the `graphify` step of
`tdq_finish.py` rebuilds it whenever a code file changed.

## 2c. Runtime dependencies — what each layer needs, and what it falls back to

A layer never announces its own death. It answers less, or answers about the past, and the shape
of that answer looks exactly like a correct one. So the fallback is written down in advance:

| Layer | Runtime dependency | Dead → falls back to |
|---|---|---|
| grep | nothing | — it IS the floor |
| agent-lsp | a language server + an import-root marker (`pyrightconfig.json` and friends) | graphify, then grep, losing types and diagnostics |
| graphify | a `graph.json` newer than the code | agent-lsp over several round trips, more expensive; grep over synonyms for a concept |

Rungs 1–8 of `scripts/tdq_lsp.py check` measure every one of those dependencies. Rung 7 measures
graphify **by effect** — a real freshness probe — because a rung that only checks existence is
blind to the way a graph actually fails. Rung 8 measures agent-lsp the same way, per module,
through the MCP path itself (`tdq_lsp.py kich-ban` → the agent sends the calls → `ghi-kiem`):
`agent-lsp doctor` reported healthy in all three failures measured on 2026-10-07.

## 5. Where this rule is hooked in

| Phase | File | What LSP does there |
|---|---|---|
| intake / analyze | `skills/tdq-intake/SKILL.md`, `references/analyze-full.md` | diagnose the environment; read code by symbol, not by grep |
| spec | `skills/tdq-spec/SKILL.md` | build §2b module boundaries from real references, not from directory names |
| plan | `skills/tdq-plan/SKILL.md` | build the `Chạm:` line from "who calls this", not from a guess |
| implement | `skills/tdq-build/SKILL.md` | `## Hard rules`, and "Search before creating" at step 2.4 |

Each of those five files carries a short pointer to section 1, never a copy of the rule:
`tests/test_tdq_setup_skill.py` fails when one of them copies the sentence back or loses the link.

## 6. The gate that holds this rule (since 2026-10-03)

The rule is not only text. `hooks/scripts/search_gate.py` sits on `PreToolUse` for `Bash` and
`Grep` — on Claude Code and on Codex — and DENIES (code `TDQ:SEARCH`) by three rules, in order:

1. **Exempt:** a file-list filter (`git ls-files | grep …`), and a name the user typed verbatim
   in the latest prompt.
2. **Opening rule:** this request has not asked LSP or `graphify query` yet → denied.
3. **Bounded unlock:** one concept-layer query unlocks the next `CUA_SO` searches
   (`scripts/search_rules.py`); after that a guess-list grep is denied again, a single exact name
   still passes.

The denial names only the layers the readiness stamp marks live, each with the call to run
(0.58.0). An LSP call is recorded the moment it is made (`PreToolUse`), so a call that fails
because the server was not started still counts as asking. The way out is always the same: run
the query the denial names, then search again. Nothing is denied while no concept layer can
answer yet.

Under Codex the gate only runs when Codex may start processes and the project hooks are trusted
under `/hooks` — `docs/tdq/research/2026-10-07-2041-hook-codex.md`.

## 3. Two details that live in a sibling file

These two are needed only when you hit the case, so they live outside the decision path in
[uu-tien-tim-kiem-chi-tiet.md](uu-tien-tim-kiem-chi-tiet.md), each a section in that file's line
index:

- **Outside plugin hooks pushing another order** — read it when rung 5 of the ladder reports one.
- **Never open documents before asking `find_references`** — measured: more warm-up, worse answer,
  monotonically. Read it before the first `find_references` of a turn.
