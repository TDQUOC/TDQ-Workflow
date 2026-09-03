# The effect check — proving the LSP index is actually alive

Run this once per request, at intake step 1b, right after the ladder comes back with no
actionable gap. It takes one LSP call and one grep.

## Why the ladder is not enough

All seven rungs of `python3 ~/.gemini/config/plugins/tdq-workflow/scripts/tdq_lsp.py check` check that something EXISTS: a binary, a
registered server, a permission entry, a config file. None of them asks the server a question and
looks at the answer. A language server whose import root is wrong starts fine, reports healthy,
and then answers every cross-file question from the scope of the single open file.

That is not hypothetical. This repo ran that way through three consecutive requests: six rungs
ĐẠT, tests green, and `find_callers` on `tdq_state.load` reaching **1 of the 15 files** that
really call it — 7 % coverage. Adding one `pyrightconfig.json` took it to 15/15. Measured in
`docs/tdq/report/2026-09-03-0017-them-pyrightconfig-do-lai.md`.

Rung 7 now catches the specific cause (a missing import-root marker). This check catches the
*symptom*, whatever the cause, which is why both exist.

## The three steps

1. **Pick** a function that really exists in the repo and is called from more than one file. Any
   one will do — pick it fresh each time. Never hard-code a file and line: the moment the code
   moves, a pinned check goes red for a reason that has nothing to do with the index.
2. **Compare** two answers for that one symbol:
   - `mcp__lsp__find_references` on its definition
   - `grep -rn "<the name>"` over the source directories
   Count **distinct files** on each side, not the number of hits.
3. **PASS** when the LSP file count is greater than or equal to the grep file count.

## The one trap in counting

`find_callers` prints **namespaces** (`TDQWorkflow/scripts.thu_thap`), not file paths. Counting
its lines as if they were files undercounts LSP badly — that mistake produced a false "3 files
missing" conclusion once already. Map each name back to its file before counting, or use
`find_references`, which does give locations.

## When it fails

Do not stop the request and do not start repairing the index mid-task:

1. Write one line in the brief: the index is not answering cross-file, with both counts.
2. Work through grep for the rest of this request — and say so in the brief, so the QC round
   knows why the search layer was not used.
3. Raise rung 7's printed suggestion with the user as a separate fix. The script never writes a
   config file itself; that stays the user's call.

Skipping this check when the ladder passed is a QC defect. The ladder is structurally blind to
this failure, so "seven rungs ĐẠT" is not an excuse for not running it.
