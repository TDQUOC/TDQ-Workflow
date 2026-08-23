---
name: tdq-spec
description: Write the spec for a TDQ request in the user's document language, register it into state, present it then STOP and wait for approval; once approved, write the plan in the same turn. Use when the deep pipeline has finished analyze.
---

# TDQ Spec

Load [tdq-conventions](../tdq-conventions/SKILL.md). The spec text itself is written in the
user's document language `doc_lang` (deliberate repetition — the original is
`skills/tdq-conventions/SKILL.md`).

## Steps

1. **Write** `docs/tdq/spec/<slug>.md` out of `docs/tdq/brief/<slug>.md`.
   Full template: [references/spec-template.md](references/spec-template.md).
   Sections that MUST be there: goal & scope (in/out) · **Lộ trình** (copied from the <!-- i18n-allow: canonical spec section names -->
   brief: which phase runs, which is dropped, which skill is used, why — approving the
   spec approves the route with it) · **Ranh giới module** (§2b — module table, file <!-- i18n-allow: canonical spec section names -->
   areas, dependencies; required in lane full, dropped in lane quick) · a measurable
   output · the approach + its reason · **Năng lực & công cụ** (§3b — copy the verdict table <!-- i18n-allow: canonical spec section names -->
   from the brief, machine-checked by doc_lint R8) ·
   standing requirements (log service ON by default, no placeholder, a test per part) ·
   constraints & risks · QC scope + Definition of Done · open questions.
   The "open questions" section MUST be empty — a question left → back to phase `analyze`.

   **§2b is built from LSP semantics, not from directory names.** A module boundary comes from
   who really imports and calls whom — `mcp__lsp__find_references` on the module's entry symbols,
   `mcp__lsp__go_to_definition` on what it pulls in. Guessing the boundary from folder names is a
   defect. <!-- i18n-allow: canonical rule sentence in the default language -->
   Đối tượng tìm là ký hiệu code (hàm, class, biến, kiểu) → BẮT BUỘC thử `mcp__lsp__*` trước;
   LSP trả rỗng mới tới lumen; grep là lớp cuối. Luật gốc:
   `skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md`.

2. **Self-review.** Re-read it for holes and contradictions, and fix them. Run the machine
   check (R8 inspects §3b):
   `python3 "${CLAUDE_PROJECT_DIR}/.claude/tdq/scripts/doc_lint.py" docs/tdq/spec/<slug>.md`
   until it exits 0.
   A deeper review happens only when the user asks for it — that is the one case where
   agent `tdq-reviewer` gets called (optional).

3. **Register the file into state:**
   ```
   python3 "${CLAUDE_PROJECT_DIR}/.claude/tdq/scripts/tdq_state.py" set spec_file=docs/tdq/spec/<slug>.md
   ```

4. **Present it, then STOP.** Write the spec block per
   [user-facing-block.md](../tdq-conventions/references/user-facing-block.md) — all 5
   components, in that order, the approval block at the end of the message:
   <!-- i18n-allow: chat block written in the user's document language -->
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
   The body is ≤ 50 lines and must be a REAL summary; a bare status line like "written to the
   log, waiting for approval" is banned. A thin summary → write the missing part now.
   When the output of the spec IS a template (e.g. an A/B question template) and you have to
   quote that block as an example, label the quote right before it, in the user's document
   language: "(template — for later questions, not this turn's question)". The point: someone
   re-reading the transcript must not mistake it for a question being asked again.
   Then **end the turn**. Do not write the plan, do not touch code. The user comments
   instead of approving → fix the spec, bump the version number, present again, wait again.

5. **The user approves → record it IMMEDIATELY:**
   ```
   python3 "${CLAUDE_PROJECT_DIR}/.claude/tdq/scripts/tdq_state.py" approve spec --by "<the user's exact words>"
   ```
   Ambiguous wording → ASK. Full rule in
   [approval.md](../tdq-conventions/references/approval.md).

Done when: `spec_approved = true` and `spec_file` points at the file you presented.
Next step: `python3 "${CLAUDE_PROJECT_DIR}/.claude/tdq/scripts/tdq_state.py" set phase=plan`
then on to [tdq-plan](../tdq-plan/SKILL.md) **in that very same turn** — the user is not
made to send one more message.
