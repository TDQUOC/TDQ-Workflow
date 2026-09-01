# TDQ phase table (generated — do NOT hand-edit)

Regenerate: `python3 scripts/tdq_state.py phases-doc > <file>`.
Source: the `PHASE_TABLE` constant in `scripts/tdq_state.py`.
Whatever phase you stand in, do only that phase's job, then run exactly its command.

| phase | entered when | the single job | command onward | done when | forbidden |
|---|---|---|---|---|---|
| `no_state` | No TDQ request is open | Ask the user to pick a lane, then open a new request | `python3 scripts/tdq_state.py init <YYYY-MM-DD-HHMM-slug> <nhanh\|chuyen-sau> [--lang <code>]` | state.json has active_request and lane | Editing code before a request is open |
| `analyze` | A request is open, deep mode | Read the code, research, interview the user until nothing is vague | `python3 scripts/tdq_state.py set phase=spec` | No question is left that would change the outcome | Writing the spec while anything is still vague |
| `spec` | Analysis is finished | Write the spec (with its roadmap section), register spec_file, present the summary and STOP for the user's approval | `python3 scripts/tdq_state.py approve spec --by "<the user's sentence verbatim>"` | spec_approved = true | Inferring that the user approved; making the user send one more turn before the plan is written |
| `plan` | spec_approved = true | Write the plan with a PROPOSED mode, register plan_file, present it and STOP for approval | `python3 scripts/tdq_state.py approve plan --by "<verbatim>"` | plan_approved = true | Editing code before the plan is approved; withholding the approval record until the user names a mode |
| `mode` | plan_approved = true but implement_mode is not settled | Explain the 2 modes briefly, ask the user to choose, STOP for the answer | `python3 scripts/tdq_state.py approve plan --mode <main\|subagent> --by "<verbatim>"` | implement_mode is not null | Editing code before the mode is settled; choosing the mode for the user |
| `implement` | plan_approved = true and implement_mode is settled | Do the whole plan in one turn, mark [~] when a task starts, red→green, flip to [x] as soon as it passes | `python3 scripts/tdq_state.py set phase=qc` | Every task in the plan is ticked [x] | Stopping midway; batching the ticks at the end of the turn; leaving several tasks marked [~]. Enforced, not merely advised: the Stop hook blocks the end of the turn with [TDQ:UNFINISHED] while a task is still open, and the only legal way out is `tdq_state.py tam-hoan --ly-do "<why>"`, whose reason is shown to the user |
| `qc` | Implementation is finished | Run the spec's Definition of Done, record the results, fix what fails | `python3 scripts/tdq_state.py set phase=report` | Every QC item of the spec PASSes, with evidence | Ignoring a failing test; reporting PASS without running it |
| `report` | QC has PASSed | Write a short report (10-20 lines recommended, no hard limit) then ask the user about committing | `python3 scripts/tdq_state.py set phase=idle` | The report is written and the user has been asked about committing | Committing or pushing before the user asks for it |
| `idle` | Finished, or no request opened yet | Wait for a new request from the user | `python3 scripts/tdq_state.py init <YYYY-MM-DD-HHMM-slug> <nhanh\|chuyen-sau> [--lang <code>]` | A new request is open | Overwriting an unfinished request without asking the user |
| `quick` | lane = quick | Analyse → a mini spec/plan merged into one file → wait for approval → write the working log FIRST → implement → QC against the DoD (ON by default) → a fix round if it FAILs | `python3 scripts/tdq_state.py approve quick [--no-qc] --by "<the user's sentence verbatim>"` | quick_approved = true, the log is written, the plan's QC section exists (evidence or the skipped-at-user's-request line), no red test is left, phase is back to idle | Implementing before the working log is written; batching the ticks at the end of the turn or leaving several tasks marked [~]; closing the job with a red test or a known bug; running set phase=idle after the 3-round fix cap without telling the user |

The commands verbatim (copy-paste, no escaping):

```
no_state: python3 scripts/tdq_state.py init <YYYY-MM-DD-HHMM-slug> <nhanh|chuyen-sau> [--lang <code>]
analyze: python3 scripts/tdq_state.py set phase=spec
spec: python3 scripts/tdq_state.py approve spec --by "<the user's sentence verbatim>"
plan: python3 scripts/tdq_state.py approve plan --by "<verbatim>"
mode: python3 scripts/tdq_state.py approve plan --mode <main|subagent> --by "<verbatim>"
implement: python3 scripts/tdq_state.py set phase=qc
qc: python3 scripts/tdq_state.py set phase=report
report: python3 scripts/tdq_state.py set phase=idle
idle: python3 scripts/tdq_state.py init <YYYY-MM-DD-HHMM-slug> <nhanh|chuyen-sau> [--lang <code>]
quick: python3 scripts/tdq_state.py approve quick [--no-qc] --by "<the user's sentence verbatim>"
```

Detailed checklist of the running phase: `python3 scripts/tdq_state.py next`.

