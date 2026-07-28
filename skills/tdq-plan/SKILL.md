---
name: tdq-plan
description: Turn an approved TDQ spec into a Vietnamese checkbox plan with per-task tests, register it, get review, wait for approval. Full lane, after spec approval.
---

# TDQ Plan

Read [tdq-conventions](../tdq-conventions/SKILL.md). Plan is VIETNAMESE. Requires `spec_approved` (the hooks enforce it). Never in the same turn as the spec.

## Steps

1. **Hỏi user chọn mode thực thi — BẮT BUỘC, trước khi viết plan.** Never pick it yourself. Use AskUserQuestion (or a plain VI question if unavailable) with exactly two options, your recommendation first and labelled `(Đề xuất)`, each with 1–2 lines of rationale:
   - `main` — làm tuần tự ngay trong hội thoại này (plan nhỏ, task phụ thuộc chặt, đụng chung file).
   - `subagent` — chia cho `tdq-implementer`, mỗi agent một git worktree (nhiều phase độc lập, chạy song song được).
   Wait for the answer; it goes into the plan as the proposal AND the user re-confirms it when approving.

2. **Draft** `docs/tdq/plan/<slug>.md` from the APPROVED spec. Structure (VI):
   - Header: trạng thái (CHỜ DUYỆT), ngày, spec nguồn + version
   - Nguyên tắc thực thi (quy ước git, log) + **một dòng RIÊNG, copy nguyên mẫu này**, không ghép chung dòng header:
     ```
     Mode thực thi: main — <lý do 1-2 câu>
     ```
     (`subagent` nếu user chọn vậy). Dòng này ghi lại lựa chọn user ở bước 1 và chỉ là **ĐỀ XUẤT**; thiếu nó thì gate chặn duyệt. Mode thật sự ghi vào state là mode user GÕ trong lệnh duyệt — Claude không được tự chốt ở bất kỳ đâu.
   - Phases with checkbox tasks:
     `- [ ] **X1.** <việc cụ thể> — Test/Validate: <lệnh hoặc tiêu chí pass đo được>`
     Every task MUST have its own test/validate. Order tasks so an MVP path goes red → green early (write the failing check, then make it pass).
   - Task riêng cho logging service (bật mặc định) và unit tests
   - Definition of Done: trỏ về phạm vi QC của spec

3. **Optimize + review.** Trim over-engineering, check dependency order, verify every spec output maps to ≥1 task. Spawn `tdq-reviewer` on the plan; apply valid findings.

4. **Register:**
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set plan_file=docs/tdq/plan/<slug>.md`
   You CANNOT set `implement_mode` — it is a protected state key. It is written only by the approve gate, from the mode the user typed in the approve command.

5. **Present & wait.** Chat (VI): tóm tắt plan ≤ 10 dòng (số phase/task, **mode user đã chọn ở bước 1 + lý do**, DoD), rồi in đúng dòng:
   `➤ Để duyệt: gõ /tdq-workflow:tdq-approve plan main|subagent · Góp ý: nhắn trực tiếp`
   Giữ nguyên `main|subagent` trong dòng đó — user gõ 1 trong 2 và chính chữ đó chốt mode (đổi ý so với bước 1 cũng được). Dòng mời thiếu mode sẽ bị Stop hook chặn.
   STOP the turn. Feedback → revise, re-present, wait again.

After approval: `... set phase=implement`, mark the plan header ĐÃ DUYỆT, then follow [tdq-implement](../tdq-implement/SKILL.md) — end-to-end in one turn.
