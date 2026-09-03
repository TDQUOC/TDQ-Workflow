# The search-order rule — the single source

This file is the ORIGINAL. `tdq-intake` (two spots), `tdq-spec`, `tdq-plan` and `tdq-build` each
carry one line pointing back here; none of them restates the rule. Change the order → change it
here, and the five hook points keep matching because they only ever point.

## 1. The order, settled

**There is no single winning layer. Pick the first layer from the KIND of question you are
asking — relationship questions go to agent-lsp, an exact known name goes to grep, a vague
concept goes to lumen. Only when the kind is unclear do you call all of them at once and merge.**

The canonical sentence, quoted verbatim at every hook point:

> Đối tượng tìm là ký hiệu code (hàm, class, biến, kiểu) → chọn lớp theo LOẠI truy vấn: quan
> hệ và đổi tên dùng `mcp__lsp__*`; tên chính xác đã biết dùng grep; khái niệm mơ hồ dùng
> lumen; chưa chắc thuộc loại nào thì gọi song song rồi gộp. Bảng đầy đủ kèm số đo:
> `skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md`.

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

## 3. Ollama's lifecycle — on demand, released right after

lumen needs Ollama up and the embedding model loaded. Keeping that model resident costs the
machine real memory the whole session for a layer used a fraction of the time. So:

1. A query of the **vague-concept** kind comes in, or one you cannot place in any row of the §2
   table. Those two cases are the trigger — a relationship question or an exact known token
   never wakes lumen.
2. `python3 ~/.gemini/config/plugins/tdq-workflow/scripts/tdq_lsp.py danh-thuc` — wake the daemon, waiting up to the timeout.
3. Run the lumen query, and the LSP query too when the kind was unclear, then merge before
   reading. lumen's `semantic_search` auto-reindexes the project incrementally (Merkle root-hash
   diff, only changed files re-embedded) whenever its index is stale — no separate reindex step
   or script is needed to keep data fresh.
4. `python3 ~/.gemini/config/plugins/tdq-workflow/scripts/tdq_lsp.py nha` — release the model IMMEDIATELY, in the same turn.

Rules around those four steps:

- Wake on demand only, on the two triggers in step 1. Never at session start, never "in case we
  need it later", and never for a question the §2 table already routes to another layer.
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

Each of those five files carries the quoted sentence from section 1 and a link back here. They
must not drift: `tests/test_tdq_lsp_skill.py` compares them against this file and fails when one
of them is edited alone.
