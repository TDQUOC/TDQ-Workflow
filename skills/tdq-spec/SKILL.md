---
name: tdq-spec
description: Viết spec tiếng Việt cho request TDQ, đăng ký vào state, trình rồi DỪNG chờ duyệt; duyệt xong viết plan cùng turn. Dùng khi chế độ chuyên sâu xong analyze.
---

# TDQ Spec

Load [tdq-conventions](../tdq-conventions/SKILL.md). The spec text itself is written in
**tiếng Việt** (nhắc lại có chủ ý — bản gốc ở `skills/tdq-conventions/SKILL.md`).

## Các bước

1. **Write** `docs/tdq/spec/<slug>.md` out of `docs/tdq/brief/<slug>.md`.
   Full khuôn: [references/spec-template.md](references/spec-template.md).
   Sections that MUST be there: goal & scope (in/out) · **Lộ trình** (copied from the
   brief: which phase runs, which is dropped, which skill is used, why — approving the
   spec approves the route with it) · **Ranh giới module** (§2b — module table, file
   areas, dependencies; required in lane full, dropped in lane quick) · a measurable
   output · the approach + its reason · năng lực & công cụ (§3b — copy the verdict table
   from the brief, machine-checked by doc_lint R8) ·
   standing requirements (log service ON by default, no placeholder, a test per part) ·
   constraints & risks · QC scope + Definition of Done · open questions.
   Mục "câu hỏi còn mở" PHẢI rỗng — còn câu hỏi thì quay lại phase `analyze`.

2. **Self-review.** Re-read it for holes and contradictions, and fix them. Run the machine
   check (R8 inspects §3b):
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/doc_lint.py" docs/tdq/spec/<slug>.md`
   until it exits 0.
   A deeper review happens only when the user asks for it — that is the one case where
   agent `tdq-reviewer` gets called (tùy chọn).

3. **Register the file into state:**
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set spec_file=docs/tdq/spec/<slug>.md
   ```

4. **Present it, then STOP.** Write the spec block per
   [user-facing-block.md](../tdq-conventions/references/user-facing-block.md) — all 5
   components, in that order, the approval block at the end of the message:
   ```
   Tôi đã viết xong spec cho yêu cầu của bạn.

   **Mục tiêu:** <1–2 câu>.
   **Đầu ra chính:** <gạch đầu dòng ngắn>.
   **Định nghĩa hoàn thành:** <gạch đầu dòng ngắn>.
   **Rủi ro đáng chú ý:** <gạch đầu dòng ngắn>.

   Xem đầy đủ tại: `docs/tdq/spec/<slug>.md`

   ---

   **Bạn duyệt spec này chứ?**

   ➤ Duyệt: nhắn "duyệt spec" (duyệt xong tôi viết plan ngay) · Góp ý: nhắn trực tiếp
   ```
   The body is ≤ 50 lines and must be a REAL summary — swapping it for a bare status line
   like "đã ghi log, đang chờ duyệt" is banned; thin summary → write the missing part now.
   When the output of the spec IS a khuôn/template (e.g. an A/B question khuôn) and you
   have to quote that block as an example, label the quote right before it.
   Nhãn dạng "(khuôn mẫu — áp dụng cho các lần hỏi sau, không phải câu hỏi của turn này)".
   Mục đích: đọc lại transcript không nhầm là đang hỏi lại.
   Then **end the turn**. Do not write the plan, do not touch code. The user comments
   instead of approving → fix the spec, bump the version number, present again, wait again.

5. **The user approves → record it IMMEDIATELY:**
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" approve spec --by "<nguyên văn câu user>"
   ```
   Ambiguous wording → ASK. Full rule in
   [approval.md](../tdq-conventions/references/approval.md).

Xong khi: `spec_approved = true` and `spec_file` points at the file you presented.
Bước kế tiếp: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=plan`
then on to [tdq-plan](../tdq-plan/SKILL.md) **NGAY trong cùng turn** — the user is not
made to send one more message.
