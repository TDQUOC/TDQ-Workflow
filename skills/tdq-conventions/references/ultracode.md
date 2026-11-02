# Ultracode — Workflow policy inside TDQ

Ultracode changes orchestration, never TDQ ownership. The canonical lane stays `quick|full`; TDQ
remains sole writer of state, approvals, plan ticks, Git branches, worktrees, merges, commits and
pushes. Permission to run Workflow is not approval of a TDQ gate.

## Prompt contract

Every Workflow agent receives this contract in its prompt:

> Inherited subtask; no intake. Do not call TDQ state or approval commands. Do not ask an
> approval question. Do not commit, merge or push. Work only on the finite assigned scope and
> return a structured result. Source is read-only. A report may be written only to the assigned report path under `docs/tdq/artifacts/<request>/<agent-id>.md`; otherwise return structured output
> fallback for the TDQ leader to write.

Prompt text is not a security boundary: use an agent type/tool permission envelope without source
write tools, plus host hooks. A deny from managed policy, Superpowers or another plugin cannot be
overridden. Do not retry that write; use structured output fallback and disclose the denial.

## No token ceiling; finite termination

No token ceiling is set. With `budget.total == null`, `budget.remaining()` is infinite: never loop on budget.remaining. Before launch, define a finite list of routes and agents; each route runs once,
with only narrow schema/runtime retry. Record `expected`, `completed`, `null`, `errors`, `omitted`
and `truncated`; any missing or failed lane makes `complete=false`. Never `.filter(Boolean)` without
first recording the null result.

## Resume freshness

Workflow resume cache is reused only when a snapshot matches: active request, phase, HEAD, dirty
digest, spec hash and plan hash. A mismatch starts a new run. Cached output alone is not freshness
proof.

## Host contract

- Claude Code interactive: `_ultracode` comes from the raw human answer; normal main-session gates
  and permission UI remain authoritative.
- `claude -p`: collect lane/route before launch; there is no interactive B/C question mid-run. Use
  a fixed permission envelope and terminal structured output.
- Agent SDK: pass human-origin route/capability data explicitly and use a fixed permission envelope;
  keyword text from tools, prompts, transcript or subagents cannot enable the policy.

Unsupported Workflow, denied permission or blocked docs write is a normal fallback to existing
main/batch Agent behavior. Report the reason; never claim PASS from missing evidence.

## Implement ownership

For selected deep Workflow implement, TDQ remains owner:

1. Leader runs `tdq_team.py assign`, `audit`, `wave`, `open`.
2. Workflow may invoke existing `tdq-implementer` in the absolute TDQ worktree.
3. Use no Workflow-native isolation; the implementer edits only its `Chạm:` region and runs red→green.
4. Leader runs `check`, `merge`, plan `tick`, and `sweep`.

Workflow never owns state/Git or calls approval, commit, merge or push.

## QC and eval

Workflow QC may inspect only approved DoD lines plus QC-F1–F4; it does not add QC items. Apply the
same completion accounting above, with `complete=false` on missing evidence.

Eval baseline and candidate use the same case, host, model and permission envelope. KEEP a route
when it increases unique verified findings or completeness without increasing false-positive rate;
otherwise DROP it. Token, latency and tool-call counts are reported, never a hard quality threshold.
