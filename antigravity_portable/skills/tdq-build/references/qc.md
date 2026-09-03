# QC — quality control

QC means running things for real and pasting the evidence. There is no "probably fine".

## Table of contents

- The three execution steps
- What to run
- Recording the result
- Evidence
- Verdict
- When it FAILs

## The three execution steps

This is the whole of Part B of [SKILL.md](../SKILL.md) — moved here so the skill body does not
carry this branch on every call. On entering phase `qc` you **must** read all three steps below
before running the first item; working from memory is banned.

<!-- doc-lint: allow R1 -->
4. **The number of QC items = the number of Definition of Done lines**, plus the four fixed
   items QC-F1→F4. One command-run check per DoD line; beyond the fixed items, add nothing
   that is not in the DoD.
   Details: section `## What to run` in this file. Large or high-risk work → also call the
   `tdq-qc-tester` agent for an independent pass.

5. Write `docs/tdq/qc/<slug>.md`: each DoD item → PASS/FAIL with **evidence** (the command plus
   its real output). Assert nothing you have not run. (File template in section
   `## Recording the result` of this file.)

6. FAIL → go back to the plan, **no re-approval needed**: add fix tasks to the plan under
   `## QC vòng N — fix` in exactly the shape `- [ ] **QCn.1** <the work> — Test: <check>`, and work <!-- i18n-allow: canonical section name of the plan -->
   them under Part A's rules (red→green, tick immediately). Then rerun the failed item plus any
   item the fix could have broken, plus the full suite. Cap of 3 rounds; over the cap, STOP and
   tell the user. Pull the user in mid-way only when the fix demands a scope change. (Full
   version in section `## When it FAILs` of this file.)

Done when: every QC item PASSes and its evidence sits in the qc file.
Next step: `python3 "~/.gemini/config/plugins/tdq-workflow/scripts/tdq_state.py" set phase=report`.

## What to run

**The number of QC items = the number of Definition of Done lines in the plan, plus four fixed
items.** Each DoD line gets exactly one check runnable as a command, with the real output
pasted. Drop no DoD line. A DoD line that cannot be checked by command is a defect in the plan:
fix that line to be measurable before doing QC. The four fixed items always run, independent of
the DoD:

- QC-F1 — the whole test suite via exactly the command written in the plan, pasting the real
  pass/fail numbers. Long suite → `<test command> > /tmp/qc-run.log 2>&1; tail -n 40 /tmp/qc-run.log`,
  pasting verbatim only where a FAIL needs evidence.
- QC-F2 — touched-area regression: for every `Chạm:` line in the plan, run the tests of the <!-- i18n-allow: canonical field name of the plan -->
  module holding the affected node. A node with no test → write `KHÔNG CÓ TEST: <node>` into the <!-- i18n-allow: canonical marker written into the qc file -->
  QC file; that is technical debt to raise in the report and must not count as PASS.
- QC-F3 — architectural constraints: every line of the "Ràng buộc kiến trúc phải giữ" block in <!-- i18n-allow: canonical section name of the spec -->
  spec §5 is one check that the change did not break that line.
- QC-F4 — clean code: if this turn changed a source file, answer the 5 questions in the
  `## Self-check` section of `skills/tdq-conventions/references/clean-code.md` and record each
  yes/no answer in the qc file. Any "no" → fix the code and record what was fixed, never fix the
  answer. No source file touched → write `KHÔNG ÁP DỤNG — không sửa file code`. <!-- i18n-allow: canonical marker written into the qc file -->

Beyond the items above, add no item that is not in the DoD.

The things below are **checked only when the DoD reaches them**; do not run them for
completeness:

- Edges & error paths: empty input, wrong type, missing file, permission denied, network down.
- Log service: on by default, timestamped, switchable off/down through config.
- No placeholders: `TODO`, `FIXME`, leftover mock data presented as real.
- Skill contract: for EVERY `Dùng:` block in the plan, run the command in its `Kiểm` field; the <!-- i18n-allow: canonical field names of the plan -->
  artifact in its `Ra` field must exist. No artifact → change that spec §3b line to `KHÔNG` plus <!-- i18n-allow: canonical verdict value -->
  a closing reason, then rerun
  `python3 "~/.gemini/config/plugins/tdq-workflow/scripts/doc_lint.py" --pair <spec> <plan>` until it exits 0.
  Editing §3b edits the spec's CONTENT, so the sha still shifts and the hook still demands
  re-approval — by design: changing a capability verdict changes intent, so the user must be
  asked. Present exactly the one-line diff and ask for re-approval (`approve spec`) inside the
  QC turn itself. Conversely, editing the bookkeeping lines at the top of the file (Ngày, Bản, <!-- i18n-allow: canonical header field names -->
  Trạng thái) has NOT shifted <!-- i18n-allow: canonical header field names --> the sha since 2026-08-19. And §6 no longer holds check commands
  whose names could go stale. Both sources of "re-approval for a harmless reason" are cut at the
  root.

## Recording the result

`docs/tdq/qc/<slug>.md`:

<!-- i18n-allow: qc file template written in the default document language -->
```markdown
# QC — <tên việc>
Ngày: YYYY-MM-DD · Plan: ../plan/<slug>.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | | | | |

## Bằng chứng
### Q1
```
<output thật, cắt gọn phần dài> <!-- i18n-allow: qc template line in the default document language -->
```

## Kết luận <!-- i18n-allow: qc template line in the default document language -->
<PASS toàn bộ | FAIL: liệt kê hạng mục fail và task fix đã thêm vào plan> <!-- i18n-allow: qc template line in the default document language -->
```

## When it FAILs

1. Add fix tasks to the **approved plan**, under `## QC vòng N — fix`: <!-- i18n-allow: canonical section name of the plan -->
   `- [ ] **QCn.1** <the work> — Test: <check>`. No user re-approval needed.
2. Work them under the implement rules: red → green, tick `[x]` immediately.
3. Rerun the failed item, plus any item the fix could have broken, plus the test suite. Do not
   rerun unrelated items.
4. Repeat until every item PASSes. **Cap of 3 rounds** — over the cap, STOP and tell the user.

Ask the user only when the fix demands a scope change against the approved spec.
