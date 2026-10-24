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
   Full template: [references/spec-template.md](references/spec-template.md); the self-check is in the tier-1 sibling
[references/spec-template-huong-dan.md](references/spec-template-huong-dan.md).
   Sections that MUST be there: goal & scope (in/out) · **Lộ trình** (copied from the <!-- i18n-allow: canonical spec section names -->
   brief: which phase runs, dropped, skill used, why) · **Ranh giới module** (§2b — lane full) ·
   a measurable output · **Luồng & Sơ đồ kiến trúc** (§2c — Mermaid diagram, Trước vs Sau; sinh kèm file HTML tương tác `docs/tdq/spec/<slug>-preview.html` qua `scripts/tdq_archify.py` khi có Archify) ·
   approach + reason · **Năng lực & công cụ** (§3b — verdict table checked by R8) ·
   **Giải thuật cốt lõi** (§3c — step-by-step logic, O(T), O(S), edge cases) ·
   **Mental Model cho Fresher** (§3d — analogy + glossary) · standing requirements ·
   constraints & risks · QC scope + Definition of Done · open questions (MUST be empty).

   **§2b is built from LSP semantics, not from directory names.** A module boundary comes from
   who really imports and calls whom — `mcp__lsp__find_references` on the module's entry symbols,
   `mcp__lsp__go_to_definition` on what it pulls in. Guessing the boundary from folder names is a
   defect. <!-- i18n-allow: canonical rule sentence in the default language -->
   The 3-layer search order is a MANDATORY rule (BẮT BUỘC) in every phase. Read sections 1
   and 2 of `skills/tdq-setup/references/uu-tien-tim-kiem.md` — the line-index block at the
   top of that file gives the exact line range, so the whole file never has to be read.

2. **Self-review.** Re-read it for holes and contradictions. Run Fresher Accessibility
   Check in `references/spec-template-huong-dan.md` to ensure a fresher grasps the logic.
   Run the machine check (R8 inspects §3b, R14 inspects thresholds):
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/doc_lint.py" docs/tdq/spec/<slug>.md`
   until it exits 0. Measure BEFORE presenting.
   A deeper review happens only when the user asks for it — that is the one case where
   agent `tdq-reviewer` gets called (optional).

3. **Register the file into state:**
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set spec_file=docs/tdq/spec/<slug>.md
   ```

4. **Present it, then STOP.** Write the spec block per
   [user-facing-block.md](../tdq-conventions/references/user-facing-block.md) — all
   components, in that order, the approval block at the end of the message:
   <!-- i18n-allow: chat block written in the user's document language -->
   ```
   Tôi đã viết xong spec cho yêu cầu của bạn.

   **Mục tiêu:** <1–2 câu>.
   **Đầu ra chính:** <gạch đầu dòng ngắn>.
   **Luồng & Giải thuật:** <1–2 câu tóm tắt sơ đồ luồng và giải thuật chính>.
   **Bản xem trước kiến trúc tương tác:** `docs/tdq/spec/<slug>-preview.html` (kèm lệnh CLI mở nhanh: `python3 scripts/tdq_archify.py open`).
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
   Then **end the turn** (chat approval only, no popup). Do not write plan. The user comments
   instead of approving → fix the spec, bump the version number, present again, wait again.

5. **The user approves → record it IMMEDIATELY:**
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" approve spec --by "<the user's exact words>"
   ```
   Ambiguous wording → ASK. Full rule in
   [approval.md](../tdq-conventions/references/approval.md).

Done when: `spec_approved = true` and `spec_file` points at the file you presented.
Next step: phase `plan` — `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=plan`
then on to [tdq-plan](../tdq-plan/SKILL.md) **in that very same turn** — the user is not
made to send one more message. An approved spec goes straight to the plan; nothing stands
between the two gates.
