# Step cost & context cost

Two different costs, sitting on two different tiers of [soul.md](soul.md). Filing a rule in the
wrong tier is how a rule gets legitimately ignored, so each part stays in its own part.

Measure with two commands:

```
python3 "./scripts/step_audit.py" --sessions 2
python3 "./scripts/token_audit.py" --sessions 2 --top 8
```

## Table of contents

- [Step cost (tier 2 — runtime)](#Step cost (tier 2 — runtime))
- [Context cost (tier 3)](#Context cost (tier 3))

## Step cost (tier 2 — runtime)

One tool call = one round-trip. Measured on real sessions: median **3.3 s** per step, p90
12.3 s. Total time scales DIRECTLY with the number of steps, so this is the runtime tier, not
context cost.

- **Batch tool calls.** Knowing 2–5 independent tool calls up front (Bash, Read, Grep) → issue
  them ALL IN ONE TURN; several independent Bash commands get joined with `&&`. Split them when
  you need to isolate a failure.
- **Batch Bash commands.** Several independent shell commands in one piece of work → one
  command joined by `&&`, or `;` when you want them all to run even if one fails. Never split
  into several turns just to see each command's output separately.
- **Conditional re-reading (SOFT rule).** When the information is still complete and intact in
  context, do not re-read the file. But you MUST re-read on any of the five cases below. This
  rule must never be turned into a blocking check.
- **Waiting on long work.** A long-running command (build, big test suite, server) → run it in
  the background and wait on a condition. No `sleep` polling loop: each round is a whole step
  that adds no information.

### Five cases where re-reading is MANDATORY

1. Context has been compacted — what remains is a summary, not the file's content.
2. Last time you read only part of it (`offset`/`limit`), not the whole file.
3. The file may have changed since: you just edited it, a command regenerated it, a sub-agent
   or the user touched it.
4. You are about to edit that very file — before an Edit you must hold the latest content.
5. You are not sure you remember, or you need a detail you skipped last time.

**When in doubt, re-read: quality stands above runtime.** One redundant read costs 3.3 seconds;
reasoning over stale content costs a whole wrong fix cycle. This rule does not carry across to a
sub-agent — an agent has its own context and must read for itself.

### Re-reading by RULE or by FORGETTING

Measured over 5 real sessions (`token_audit.py --sessions 5`): `Read` was called 451 times,
**64.1% of them re-reads of a file already read in the same session**, median 1,786 tokens each.
That number is NOT evidence of waste: the five cases above make re-reading mandatory, and most
re-reads land squarely in them. It only means the distinction is worth drawing clearly.

A re-read counts as "by FORGETTING" when **all five** statements below hold — i.e. it falls into
none of the five mandatory cases:

- Context has not been compacted since the previous read.
- Last time you read the WHOLE file, no `offset`/`limit`.
- Nobody has touched the file since: you have not edited it, no command regenerated it, no
  sub-agent or user went near it.
- You are not about to Edit that file.
- You still remember the passage clearly and need no detail you skipped last time.

The three fastest signs, all three being re-reads out of habit:

- Re-reading a whole file just to confirm ONE line → `grep -n` answers exactly that question.
- Re-reading right after `Edit` reported success → `Edit` would have failed on a mismatch, so
  the re-read adds nothing.
- Re-reading a file you just `Write`-verbatim in the same session.

The two error directions are not symmetric: skipping a NEEDED read means reasoning over stale
content and losing a whole fix cycle; one redundant read costs 3.3 seconds and one carry. So
whenever the five conditions are not certainly all true — **when in doubt, re-read**.

### Never batch these

Splitting the four cases below is RIGHT and batching them is WRONG, even where batching is
technically possible.

| Case | Why batching it is banned here |
|---|---|
| The red step → green step of TDD | batched, there is no evidence the test really went red; red-green becomes theatre |
| Isolating a failure | batch 5 commands and you cannot tell which failed, so you rerun them one by one — more steps, not fewer |
| Destructive or hard-to-undo commands | delete, overwrite, `git reset` — you must see the previous command's result before running the next |
| A command that needs the previous command's result | batched, the later command runs on an assumption and returns a wrong result nobody notices |

RIGHT example: one turn issuing `Read a.py`, `Read b.py`, `grep -n "foo" c.py` — three unrelated
pieces of work; you reason only after all three land.
WRONG example: one turn running `pytest` (expecting red), then `Edit`, then `pytest` again — the red
step loses its evidence, and the first run is meaningless because the file was not yet changed.

## Context cost (tier 3)

Every tool call = 1 API call = the model re-reads the ENTIRE context: one output costs
`its token count × the number of API calls after it` — **carry-cost**. Measure with
`token_audit.py` (counting with a real tokenizer; the chars/4 estimate is badly off exactly in
the priciest group). Images are counted by 28×28 px patches, not by base64 length.

- **Lint the exact file.** Run `doc_lint.py` on EXACTLY the file you just changed, never pass a
  whole directory (`docs/tdq`): linting a directory prints ~8,000 characters of unrelated errors
  from old files.
- **Quiet CLI.** `tdq_state.py init|set|reset` prints one line by default; add `--json` only
  when you genuinely need to inspect the state. Use `next --brief` instead of `next` unless you
  need the full checklist.
- **Read just enough.** Files over 200 lines: locate with `grep -n`, then Read with
  `offset`/`limit`. No `cat` (use Read), no `grep -A5 -B5` when `-c`/`-l` already answers.
- **Give heavy work to a subagent.** Web research and reading ≥4 files go to a separate agent —
  an agent has its own context window and returns only a digest to the main conversation.
- **Output cap for external tools (MCP).** An MCP tool is third-party code: TDQ cannot change
  what it returns, only cap it. Set `MAX_MCP_OUTPUT_TOKENS` in `~/.claude/settings.json`
  (Claude Code's default is 50,000, with a warning from 10,000). Measured over 5 real sessions:
  every existing MCP group stays under 8,800 tokens per call and the whole MCP cluster is only
  **1.9%** of total carry-cost. This cap does NOT cut current cost. It stops the rare giant case
  in the future — one call is enough to inflate a whole session.
  Over the cap the output is truncated with a marker: on seeing the marker → call again with
  narrower parameters (filter, paginate, select fields); never treat the readable part as enough
  and conclude from it.
- **Soul decides.** Every rule above only cuts cost when the output does not change. Work that
  demands reading WHOLE files or running every check gets done in full: quality stands above
  context cost, per [soul.md](soul.md).
