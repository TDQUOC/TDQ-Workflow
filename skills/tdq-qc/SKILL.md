---
name: tdq-qc
description: Quality-check an implemented TDQ plan against its DoD; on failure append fix tasks to the plan (no re-approval) and loop until green.
---

# TDQ QC

Read [tdq-conventions](../tdq-conventions/SKILL.md). Output VI. Runs after tdq-implement, phase `qc`.

## Steps

1. **Run the full DoD** from the approved plan/spec: entire test suite, validates, lint/build if defined. Optionally spawn `tdq-qc-tester` for an independent pass (edge cases, error paths, log output present & timestamped).

2. **Record** `docs/tdq/qc/<slug>.md` (VI): từng hạng mục DoD → PASS/FAIL + bằng chứng (lệnh + output thật). No unverified claims.

3. **On FAIL — loop back to plan, no re-approval needed:**
   - Append fix tasks to the APPROVED plan under `## QC Round N — fix`, same format `- [ ] **QCn.** <việc> — Test/Validate: <check>`.
   - Implement them per [tdq-implement](../tdq-implement/SKILL.md) rules (red→green, tick immediately), in this same turn.
   - Re-run QC. Repeat until all PASS. Only involve the user if the fix requires a scope change.

4. **On all PASS:** update qc file kết luận PASS, `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=report`, continue with [tdq-report](../tdq-report/SKILL.md).
