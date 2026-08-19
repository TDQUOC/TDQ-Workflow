# Recording approval

The user approves in ordinary chat. The agent's job is to **recognise it correctly**
and **record it** — never to judge generously on the user's behalf.

## It is an approval only when BOTH parts are present

1. A word of consent: `duyệt` · `ok` · `oke` · `đồng ý` · `chốt` · `approve` · `làm đi` · `tiến hành`
2. The object currently awaiting approval: `spec` · `plan` · `quick` / `mini-plan`, or a
   pronoun pointing at it unmistakably: `cái này`, `cái đó`, `cái trên`.

Valid examples:

| Câu user | Ghi nhận |
|---|---|
| `duyệt spec` | `approve spec` |
| `ok plan, mode main` | `approve plan --mode main` |
| `chốt cái này` (đang chờ quick) | `approve quick` |
| `đồng ý, tiến hành plan mode subagent` | `approve plan --mode subagent` |

## NOT an approval (counter-examples)

| Câu user | Why not | What to do |
|---|---|---|
| `ok` | no object; may only mean "I heard you" | ASK again |
| `ok tôi hiểu rồi` | acknowledges understanding, not consent | ASK again |
| `spec ok chưa?` | a question (has `?`) | Answer, keep waiting |
| `plan này duyệt chưa` | asks about status, has `chưa` | Answer, keep waiting |
| `duyệt spec` while **plan** is pending | wrong object | Record spec only, NEVER infer plan |

Ambiguous → **ASK**. Never approve on the user's behalf.

## Command to run the moment you recognise it

```
python3 "./scripts/tdq_state.py" approve <spec|plan|quick> [--mode main|subagent] --by "<nguyên văn câu user>"
```

- `--by` is mandatory in practice: it is the only trace tying state back to the conversation.
- Approving twice is not an error (idempotent, exit 0).
- `approve plan` while the user has not named a mode → **ASK for the mode first**, never guess.
  Ask with the one-option-per-line shape of
  [interview.md](../../tdq-intake/references/interview.md):
  `- A (đề xuất): main — …` / `- B: subagent — …`.
- Every approval also adds one line to `docs/workinglog/<hôm nay>.md` (what was approved, when,
  and the user's exact words).
