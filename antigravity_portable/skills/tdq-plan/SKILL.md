---
name: tdq-plan
description: Turn an approved spec into a checkbox plan, one test per task: STOP and wait for the user to approve the plan, then ask how to run it and build in the same turn. Use when a deep-pipeline spec has been approved.
---

# TDQ Plan

Load [tdq-conventions](../tdq-conventions/SKILL.md). The plan text is written in the user's
document language `doc_lang` (deliberate repetition — the original is
`skills/tdq-conventions/SKILL.md`). Requires `spec_approved = true` — the approved spec is the
outline the tasks are written against, and a task tracing back to nothing in it is out of
scope. Spec approved → plan NOW.

## Steps

1. **Pick the mode to PROPOSE.** Weigh both options, write the fitting one into the plan at
   step 2 with its reason; the user settles it at gate `mode` (step 6):
   - `main` — display label "làm trực tiếp (inline implement)": work through it sequentially <!-- i18n-allow: user-facing mode label -->
     right inside this conversation (small plan, tightly dependent tasks, shared files).
   - `subagent` — display label "giao trợ lý (sub-agent implement)": assistants run in parallel, <!-- i18n-allow: user-facing mode label -->
     you lead and cut the plan into waves, one worktree per agent, doing the unsplittable part
     yourself. Rule: `tdq-build/references/team-mode.md`.
   The proposal is **never eyeballed**: once the plan is written (step 2), MEASURE on that very plan:
   ```
   python3 "~/.gemini/antigravity-cli/tdq/scripts/tdq_bench.py" mo-phong --plan docs/tdq/plan/<slug>.md \
     --thuc-do docs/tdq/bench/2026-08-17-2001-smoke-test-main-vs-doi-thuc-do.json --he-so-agent 1.5
   ```
   The `Winner:` line of that command IS the proposal; copy the minute gap into the reason.
   `--he-so-agent 1.5` assumes a sub-agent 1.5× slower than the leader, so a team winning at that conservative factor wins for real.
   Command errors (the plan has no `Chạm:` line) → fix the plan and measure again, guessing is banned. <!-- i18n-allow: canonical name kept verbatim -->

2. **Write** `docs/tdq/plan/<slug>.md` out of the APPROVED spec — the full template lives in
   [references/plan-template.md](references/plan-template.md).
   Must be there: the status header + source spec · **a line of its own**
   `Mode thực thi: <main|subagent> — <reason>` · the phases with checkbox tasks · a task of its own for <!-- i18n-allow: canonical name kept verbatim -->
   the log service and for unit tests · a Definition of Done pointing back at §6 of the spec, **every
   DoD line checkable by one command** (QC counts its items off that exact number of lines).
   One task = one piece of work + one measurable check, carrying the minute estimate `(eNm)`:
   ```
   - [ ] **T1.1** (e6m) <the concrete work> — Test: <command or pass criterion>
   ```
   **Every task that creates or edits a source file needs a `Chạm:` line right under it**, listing <!-- i18n-allow: canonical name kept verbatim -->
   the paths in backticks: it is the blast-radius map and what `tdq_team.py phan-cong` reads to cut
   waves. Template: the 2 sections `Chạm:`/`Cụm song song` of plan-template. <!-- i18n-allow: canonical name kept verbatim -->
   **Build `Chạm:` from "who calls this", never by eye:** `mcp__lsp__find_references` on every <!-- i18n-allow: canonical name kept verbatim -->
   symbol the task changes, so a caller outside the obvious folder still lands on the line. <!-- i18n-allow: canonical rule sentence in the default language -->
   Đối tượng tìm là ký hiệu code (hàm, class, biến, kiểu) → chọn lớp theo LOẠI truy vấn: quan
   hệ và đổi tên dùng `mcp__lsp__*`; tên chính xác đã biết dùng grep; khái niệm mơ hồ dùng
   lumen; chưa chắc thuộc loại nào thì gọi song song rồi gộp. Bảng đầy đủ kèm số đo:
   `skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md`.
   **Score `eNm` as you write the task**, never later and never padded: minutes the agent SPENDS
   EXECUTING it (approval waits do not count). Plan ETA = the sum over unfinished tasks; the full
   scoring rule is the last section of plan-template.
   **The `(mcp)` label rule:** a task with a `Dùng:` block whose skill needs an MCP tool at runtime → <!-- i18n-allow: canonical name kept verbatim -->
   that `Dùng:` line ends with ` (mcp)` OUTSIDE the backticks: that task must be done by Claude. <!-- i18n-allow: canonical name kept verbatim -->

3. **Optimise.** Cut redundancy, check the dependency order, cross-check the 2 mapping rules: every
   output in spec §2 → ≥ 1 task; every `DÙNG` row in spec §3b → ≥ 1 contract block with all 5 fields <!-- i18n-allow: canonical name kept verbatim -->
   (`Dùng/Để/Ra/Kiểm/Không dùng cho`). Machine check: `python3 "~/.gemini/antigravity-cli/tdq/scripts/doc_lint.py" --pair <spec> <plan>` must exit 0; a deeper review only when the user asks (`tdq-reviewer`). <!-- i18n-allow: canonical name kept verbatim -->

4. **Register the file into state:**
   ```
   python3 "~/.gemini/antigravity-cli/tdq/scripts/tdq_state.py" set plan_file=docs/tdq/plan/<slug>.md
   ```
   Do **NOT** set `implement_mode` here — that field is written only when approval is recorded.

5. **Present it, then STOP.** Write the plan block per
   [user-facing-block.md](../tdq-conventions/references/user-facing-block.md) — all 5
   components, the approval block at the end of the message, and **no** mode question here:
   <!-- i18n-allow: chat block written in the user's document language -->
   ```
   Tôi đã viết xong plan để thực hiện yêu cầu của bạn.

   **Cách làm:** <1–2 câu>.
   **Khối lượng:** <số phase>, <số task>, ước tính <tổng phút>.
   **Kiểm thế nào:** <số dòng DoD>, mỗi dòng một lệnh kiểm.

   Xem đầy đủ tại: `docs/tdq/plan/<slug>.md`

   ---

   **Bạn duyệt plan này chứ?**

   ➤ Duyệt: nhắn "duyệt plan" (duyệt xong tôi hỏi bạn một câu về cách chạy) · Góp ý: nhắn trực tiếp
   ```
   The body is ≤ 10 lines and a REAL summary; a bare status line ("written to the log, waiting for
   approval") is banned. Quoting a template as an example → label it right before the excerpt, in the
   user's language: "(template — not this turn's question)". Then **end the turn**; comments → fix,
   present again, wait.

6. **The user approves → record it IMMEDIATELY, then ask about the run mode in the SAME turn:**
   ```
   python3 "~/.gemini/antigravity-cli/tdq/scripts/tdq_state.py" approve plan --by "<the user's exact words>"
   ```
   Does the approval sentence already name a mode (`main`/`inline`, `subagent`/`sub-agent`)? Then add
   `--mode <that value>`, **skip** the gate below and build right away — re-asking is banned.
   No mode named → state stops at phase `mode`; print the question block then STOP. That block
   lives verbatim in [references/mode-gate.md](references/mode-gate.md): two options "làm trực <!-- i18n-allow: user-facing mode labels -->
   tiếp (inline implement)" / "giao trợ lý (sub-agent implement)", one per line, proposal at A. <!-- i18n-allow: user-facing mode labels -->
   Right under the two options there MUST be a **"Vì sao đề xuất"** paragraph, 1–3 lines long. <!-- i18n-allow: canonical name of the block -->
   Generalities are banned. Give all 4 grounds read off the plan: task count, dependency chain, how
   many files several tasks touch at once, whether an `(mcp)` label is present. Close with one
   sentence on why not the other option (examples in mode-gate.md). The two names are **display
   labels**; state records `main`/`subagent` (`MODE_LABELS`/`MODE_ALIASES` in `~/.gemini/antigravity-cli/tdq/scripts/tdq_state.py`).
   The user answers → re-run the command with `--mode <main|subagent>` and build RIGHT AWAY, same
   turn. The settled mode is the USER's, even when it differs from your proposal.

Done when: `plan_approved = true` and `implement_mode` is not empty.
Next step: flip the plan header to `ĐÃ DUYỆT`, run <!-- i18n-allow: canonical name kept verbatim -->
`python3 "~/.gemini/antigravity-cli/tdq/scripts/tdq_state.py" set phase=implement`; then on to [tdq-build](../tdq-build/SKILL.md) **in that very same turn**.
