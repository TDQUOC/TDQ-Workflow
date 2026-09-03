# Before/after carry-cost measurement scenario

Use it to compare how many tokens the TDQ workflow burns before and after a standardisation
round (e.g. the P1-P4 skill split of `2026-08-05-toi-uu-p0-p1-workflow`). Measure with
`~/.gemini/config/plugins/tdq-workflow/scripts/token_audit.py` on a real transcript — never estimate by eye.

## Fixed script (run identically for the before and the after session)

Use a separate throwaway project, not the main repo, so the logs stay unmixed:

1. Open a sample quick request: send `"fix one comment line in test.py"` (a tiny task,
   no real research or interview, so the scenario stays repeatable).
2. Answer the lane question: pick the express lane.
3. Approve the mini-plan: send `"approve quick"`.
4. Let Claude implement one fake task (change exactly one comment line), then validate.
5. Answer "no, that is all" to the closing interview question, if it appears.
6. End the session right after the result report — ask nothing else.

Note the session id (or its start and end time) of each run so the right transcript can be
sliced out for measurement.

## Measuring with `token_audit.py`

```bash
python3 ~/.gemini/config/plugins/tdq-workflow/scripts/token_audit.py --transcript-dir ~/.claude/projects/<project-slug> --sessions 1 --top 5
```

- `--transcript-dir` points at the folder holding the throwaway project's `*.jsonl` (the path
  includes the project path that Claude Code turned into a dashed slug).
- `--sessions 1` measures only the session that just ran the scenario, never a neighbour.
- `--top 5` also prints the five priciest tool outputs — useful to see where the cost sits.

Run that command for the **before** session (standardisation not applied) and the **after**
session (applied), then compare the two outputs: total equiv-input tokens, cache/baseline
ratio, bookkeeping ratio — which column dropped, and by how many percent.

## Recording the result

Paste both output tables (before/after) verbatim into the report or the QC file, together with
the percentage drop in total equiv-input tokens — that is carry-cost evidence, not an estimate.
