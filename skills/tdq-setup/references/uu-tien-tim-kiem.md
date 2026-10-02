# The search-order rule — the single source
<!-- muc-luc-dong:
  1. The order, settled=16-36 ·
  2. The table — kind of question → which layer first, with the numbers=37-58 ·
  2b. The fourth layer: graphify, the map=59-92 ·
  2c. Runtime dependencies — what each layer needs, and what it falls back to=93-108 ·
  5. Where this rule is hooked in=109-120 ·
  6. The gate that holds this rule (since 2026-10-03)=121-135 ·
  3. Three details that live in a sibling file=136
-->

This file is the ORIGINAL. `tdq-intake` (two spots), `tdq-spec`, `tdq-plan` and `tdq-build` each
carry one line pointing back here; none of them restates the rule. Change the order → change it
here, and the five hook points keep matching because they only ever point.

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
2. **Opening rule:** this request has not asked lumen, LSP or `graphify query` yet → denied.
3. **Bounded unlock:** one concept-layer query unlocks the next `CUA_SO` searches
   (`scripts/search_rules.py`); after that a guess-list grep is denied again, a single exact name
   still passes.

The way out is always the same: run the query the denial names, then search again. Nothing is
denied while the concept layer is still being built.

## 3. Three details that live in a sibling file

These three are needed only when you hit the case, so they moved out of the decision path into
[uu-tien-tim-kiem-chi-tiet.md](uu-tien-tim-kiem-chi-tiet.md), each a section in that file's line
index:

- **Ollama's lifecycle** — wake on demand, release in the same turn. Read it before the first
  lumen query of a turn. The index itself is NOT kept fresh by searching: it is rebuilt in the
  `reindex` step of `scripts/tdq_finish.py`, every turn, through the CLI.
- **Outside plugin hooks pushing another order** — read it when rung 6 of the ladder reports one.
- **Never open documents before asking `find_references`** — measured: more warm-up, worse answer,
  monotonically. Read it before the first `find_references` of a turn.
