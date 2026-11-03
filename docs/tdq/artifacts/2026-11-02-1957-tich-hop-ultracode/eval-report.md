# Eval — Ultracode routing V1

## Baseline
- TDQ main/batch Agent path, no `_ultracode` contract.
- Same repository, host family and permission assumptions.
- No contract tests for suffix routing, finite completion accounting, host fallback or TDQ-owned Workflow implement.

## Candidate evidence
- `tests/test_ultracode_routing.py` + `tests/test_ultracode_contract.py`: **12 passed**.
- Gate/unit region (`test_edit_gate.py`, `test_bash_gate.py` included earlier): **77 passed, 6 subtests**.
- Analyze used two finite Workflow runs: 15 agents, all completed; found state/Git/worktree/plugin constraints not captured by the first solo hypothesis.
- Candidate pre-implement eval-plan gate: PASS (`valid_plan`); host adapter reports interactive cell `UNSUPPORTED`, so runtime quality is certified separately by T4.1 and host probes, never fabricated here.

## Decision
| Route | Quality result | Decision |
|---|---|---|
| Lane suffix + finite analyze routing | Adds verified trigger/state invariants with no observed false-positive | KEEP |
| Spec/plan review | Contract-only; no extra gate, evidence-preserving | KEEP |
| Workflow implement | TDQ-owned worktree only; native isolation forbidden | KEEP conditionally |
| Agent SDK runtime | SDK absent on this machine | UNSUPPORTED, fallback |
| Token ceiling | User explicitly rejected; finite route termination verified | DROP ceiling |

Token/latency/tool counts are reported but not quality thresholds. Final KEEP remains conditional on QC runtime/full-suite evidence.
