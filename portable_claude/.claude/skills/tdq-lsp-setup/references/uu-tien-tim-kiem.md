# The search-order rule — the single source

This file is the ORIGINAL. `tdq-intake`, `tdq-spec`, `tdq-plan` and `tdq-build` each carry one
line pointing back here; none of them restates the rule. Change the order → change it here, and
the four hook points keep matching because they only ever point.

## 1. The order, settled

**agent-lsp runs FIRST. lumen runs only when agent-lsp came back empty. grep is the last layer.**

The canonical sentence, quoted verbatim at every hook point:

> Đối tượng tìm là ký hiệu code (hàm, class, biến, kiểu) → BẮT BUỘC thử `mcp__lsp__*` trước;
> LSP trả rỗng mới tới lumen; grep là lớp cuối. Luật gốc:
> `skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md`.

This is a soft rule, not a blocking hook. Reaching for grep on a code symbol without trying LSP
first is a QC defect, not a turn the machine refuses. Two exemptions, both narrow:

- The target is text, not a symbol — a message string, a config key, a comment, a filename.
- The ladder's rungs 1–4 are not satisfied, so there is no LSP to try. Say so in one line, then
  fall through to grep.

## 2. Why that order, and what lumen still adds

| Question | agent-lsp | lumen |
|---|---|---|
| where is this symbol defined | exact, from the compiler's own index | approximate, by embedding distance |
| who calls this function | exact — `find_references`, call hierarchy | cannot answer |
| what type is this expression | exact — hover, type hierarchy | cannot answer |
| rename safely across the repo | exact — the server computes the edits | cannot answer |
| errors in this file right now | exact — `get_diagnostics` | cannot answer |
| "the part that handles retry logic" | weak — needs a name to match on | strong — this is what it is for |
| a language with no server installed | nothing | still works, it only needs text |
| cost when idle | a binary on disk | an Ollama model resident in RAM |

Reading of the table: agent-lsp replaces lumen for every question with a right answer, and lumen
keeps exactly one job — a conceptual query with no symbol name to hang it on. That job is real,
which is why lumen stays; it is narrow, which is why it stays second.

## 3. Ollama's lifecycle — on demand, released right after

lumen needs Ollama up and the embedding model loaded. Keeping that model resident costs the
machine real memory the whole session for a layer used a fraction of the time. So:

1. LSP query comes back **empty** — the one and only trigger.
2. `python3 scripts/tdq_lsp.py danh-thuc` — wake the daemon, waiting up to the timeout.
3. Run the lumen query.
4. `python3 scripts/tdq_lsp.py nha` — release the model IMMEDIATELY, in the same turn.

Rules around those four steps:

- Wake on demand only. Never at session start, never "in case we need it later".
- The timeout not being met is not a failure of the turn: say so in one line and fall to grep.
- `nha` stops the daemon only when this script started it. A daemon the user started is left
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

Each of those four files carries the quoted sentence from section 1 and a link back here. They
must not drift: `tests/test_tdq_lsp_skill.py` compares them against this file and fails when one
of them is edited alone.
