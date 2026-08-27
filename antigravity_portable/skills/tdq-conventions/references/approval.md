# Recording approval

The user approves in ordinary chat. The agent's job is to **recognise it correctly**
and **record it** — never to judge generously on the user's behalf.

## It is an approval only when BOTH parts are present

1. A word of consent in the user's own language — English: `approve` · `ok` · `go ahead` ·
   `confirmed`; Vietnamese: `duyệt` · `đồng ý` · `chốt` · `làm đi` · `tiến hành`. <!-- i18n-allow -->
2. The object currently awaiting approval: `spec` · `plan` · `quick` / `mini-plan`, or a
   pronoun pointing at it unmistakably (`this one`, `that one`, `the one above`; in Vietnamese
   `cái này`, `cái đó`, `cái trên`). <!-- i18n-allow -->

Valid examples:

| The user's sentence | Recorded as |
|---|---|
| `approve the spec` | `approve spec` |
| `duyệt spec` (vi) | `approve spec` | <!-- i18n-allow -->
| `ok plan, mode main` | `approve plan --mode main` |
| `go ahead with this one` (quick is pending) | `approve quick` |
| `chốt cái này` (vi, quick is pending) | `approve quick` | <!-- i18n-allow -->
| `agreed, run the plan in subagent mode` | `approve plan --mode subagent` |
| `đồng ý, tiến hành plan mode subagent` (vi) | `approve plan --mode subagent` | <!-- i18n-allow -->

## NOT an approval (counter-examples)

| The user's sentence | Why not | What to do |
|---|---|---|
| `ok` | no object; may only mean "I heard you" | ASK again |
| `ok, I get it` (vi `ok tôi hiểu rồi`) | acknowledges understanding, not consent | ASK again | <!-- i18n-allow -->
| `is the spec ok?` (vi `spec ok chưa?`) | a question (has `?`) | Answer, keep waiting | <!-- i18n-allow -->
| `has this plan been approved` (vi `plan này duyệt chưa`) | asks about status, not consent | Answer, keep waiting | <!-- i18n-allow -->
| `approve the spec` while **plan** is pending | wrong object | Record spec only, NEVER infer plan |

Ambiguous → **ASK**. Never approve on the user's behalf.

## Command to run the moment you recognise it

```
python3 "~/.gemini/antigravity-cli/tdq/scripts/tdq_state.py" approve <spec|plan|quick> [--mode main|subagent] --by "<the user's sentence verbatim>"
```

- `--by` is mandatory in practice: it is the only trace tying state back to the conversation.
- Approving twice is not an error (idempotent, exit 0).
- `approve plan` while the user has not named a mode → **ASK for the mode first**, never guess.
  Ask with the one-option-per-line shape of
  [interview.md](../../tdq-intake/references/interview.md):
  a numbered question line (`1. …`) followed by
  `- A (recommended): main — …` / `- B: subagent — …`, with the labels written in the user's
  language (Vietnamese: `- A (đề xuất): …`). <!-- i18n-allow --> The number is mandatory even
  for this single question — rule 8 of [user-facing-block.md](user-facing-block.md).
- Every approval also adds one line to `docs/workinglog/<today>.md` (what was approved, when,
  and the user's exact words).
