---
name: tdq-plan
description: Turn an approved TDQ spec into a Vietnamese checkbox plan with per-task tests, register it, get review, wait for approval. Full lane, after spec approval.
---

# TDQ Plan

Read [tdq-conventions](../tdq-conventions/SKILL.md). Plan is VIETNAMESE. Requires `spec_approved` (the hooks enforce it). Never in the same turn as the spec.

## Steps

1. **Draft** `docs/tdq/plan/<slug>.md` from the APPROVED spec. Structure (VI):
   - Header: trạng thái (CHỜ DUYỆT), ngày, spec nguồn + version
   - Nguyên tắc thực thi (mode chạy, quy ước git, log)
   - Phases with checkbox tasks:
     `- [ ] **X1.** <việc cụ thể> — Test/Validate: <lệnh hoặc tiêu chí pass đo được>`
     Every task MUST have its own test/validate. Order tasks so an MVP path goes red → green early (write the failing check, then make it pass).
   - Task riêng cho logging service (bật mặc định) và unit tests
   - Definition of Done: trỏ về phạm vi QC của spec

2. **Optimize + review.** Trim over-engineering, check dependency order, verify every spec output maps to ≥1 task. Spawn `tdq-reviewer` on the plan; apply valid findings.

3. **Register:**
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set plan_file=docs/tdq/plan/<slug>.md`

4. **Present & wait.** Chat (VI): tóm tắt plan ≤ 10 dòng (số phase/task, mode thực thi, DoD), rồi in đúng dòng:
   `➤ Để duyệt: gõ /tdq-workflow:tdq-approve plan · Góp ý: nhắn trực tiếp`
   STOP the turn. Feedback → revise, re-present, wait again.

After approval: `... set phase=implement`, mark the plan header ĐÃ DUYỆT, then follow [tdq-implement](../tdq-implement/SKILL.md) — end-to-end in one turn.
