# The interview round

Goal: no question is left whose different answers would lead to a different product.

## Table of contents

- Two tiers of questions — general first, detail second
- What to ask
- How to ask
- Recording it
- When to stop

## Two tiers of questions — general first, detail second

- **Tier 1 — the scope round**: which areas the request spans, what the real context is. Runs
  conditionally; the full rule is in [scope-round.md](scope-round.md). Skip it and the
  reason must be written down.
- **Tier 2 — the detail round**: the 7 items below, but **ask only inside the areas the user
  chose at tier 1**. An area the user ruled out is not asked about, and not slipped into
  the spec either.

Run tier 1 before tier 2. If the scope round was SKIPPED by its own criteria, tier 2 asks
exactly as it did before.

## What to ask

Ask only what **changes the outcome**. For each item below: if you can answer it yourself,
skip it; if you cannot, ask.

- Scope: what is in, what is definitively out.
- Output: which file/screen/API exactly; how "done" is measured.
- Data: source, volume, format, sensitive data.
- Errors & edges: how it behaves when it breaks, who sees the error.
- Performance & scale: the acceptable threshold.
- Compatibility: versions, OS, existing dependencies.
- Operations: where it runs, who maintains it, logging/monitoring.

Do not ask: what reading the code answers, what section `## Nguyên văn` of the brief <!-- i18n-allow: canonical section name -->
already holds, what is only a presentation preference.

## How to ask

Every question carries **2–4 concrete options**. **Always ask with a list in chat** — no
AskUserQuestion, so the user reads every option at once and can answer freely.

The whole round is one block spoken to the user: wrap it per
[user-facing-block.md](../../tdq-conventions/references/user-facing-block.md) — an opening
line addressing the user directly, a `---` divider, then the bold answer block at the end of the
message. The options inside are pasted in exactly this shape:

<!-- i18n-allow: option template written in the default language -->
```
<số>. <Câu hỏi>
- A (đề xuất): <phương án> — <hệ quả 1 dòng>
- B: <phương án> — <hệ quả 1 dòng>
- C: <phương án> — <hệ quả 1 dòng>
```

Rules of this shape:

- Each option is exactly **1 line of its own**, starting with `- ` then the UPPERCASE label
  `A`/`B`/`C`/`D`.
- **Merging is banned** — never put several options onto one line or into a paragraph like `(a) … · (b) …`.
- The option you recommend is always **A** and carries the label `(đề xuất)`; the others <!-- i18n-allow: the label is written in the default language -->
  carry no label. <!-- i18n-allow: the label is written in the default language -->
- After the label comes `:` then the content. The consequence is joined with ` — `, on that
  same line.
- Several questions in one round → number them `1.`, `2.` and give each its own option list.
- The pipeline question, the execution-mode question (main/subagent) and the commit
  question all follow this shape too.

**The closing question of a round is conditional** — write it only when that round has at
least one question (even if there is exactly 1). A round with no question at all does not
get an empty interview round built just to ask it: go straight to the next step.

<!-- i18n-allow: closing-question template in the default language -->
```
<số>. Bạn muốn bổ sung thêm gì không?
- A (đề xuất): Không, đủ rồi — làm tiếp đi.
- B: Có — tôi nói thêm.
```

**The answer-guidance line** — right under the last option list of each round, add exactly
1 short block (the principle + 1 neutral example) so a newcomer knows what to type and what
it gets them:

<!-- i18n-allow: guidance line written in the default language -->
```
_Trả lời bằng chữ cái (vd: "A"), hoặc gõ thẳng câu tự nhiên khớp ý bạn chọn (vd: "chọn
phương án A") — cả hai đều được hiểu như nhau._
```

Only 1 such block, never repeated per question when a round holds several — put it at the
end, after the last option. The example inside stays neutral (never welded to one specific
question such as lane/mode) because this file serves every A/B/C-style question.

A closed option set never covers everything the user has in mind; that question is where
they add the rest.

## Recording it

Every question–answer goes into the brief under `## Hỏi đáp` <!-- i18n-allow: canonical section name -->: the question, the options,
what the user chose (verbatim), and the timestamp.

## When to stop

Stop when you re-read the question list and every remaining question **cannot** change the
product. One question left that can → run another round. Moving on to the spec while
anything still has to be guessed is banned.
