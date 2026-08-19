---
name: tdq-plan
description: Biến spec thành plan checkbox, mỗi task một test: DỪNG chờ user duyệt plan, rồi hỏi cách chạy và build cùng turn. Dùng khi spec chế độ chuyên sâu đã duyệt.
---

# TDQ Plan

Load [tdq-conventions](../tdq-conventions/SKILL.md). The plan text is written in **tiếng Việt**
(nhắc lại có chủ ý — bản gốc ở `skills/tdq-conventions/SKILL.md`). Requires
`spec_approved = true`. The user approves the spec → write the plan RIGHT AWAY, same turn.

## Các bước

1. **Pick the mode to PROPOSE.** Weigh both options, write the fitting one into the plan at
   step 2 with its reason; the user settles it at gate `mode` (step 6):
   - `main` — nhãn hiển thị "làm trực tiếp (inline implement)": làm tuần tự ngay trong
     hội thoại này (small plan, tightly dependent tasks, shared files).
   - `subagent` — nhãn hiển thị "giao trợ lý (sub-agent implement)": nhiều trợ lý chạy
     song song, you lead and cut the plan into waves, one worktree per agent, doing the part that
     cannot be split yourself. Rule: `tdq-build/references/team-mode.md`.
   The proposal is **never eyeballed**: once the plan is written (step 2), MEASURE on that very plan:
   ```
   python3 "./scripts/tdq_bench.py" mo-phong --plan docs/tdq/plan/<slug>.md \
     --thuc-do docs/tdq/bench/2026-08-17-2001-smoke-test-main-vs-doi-thuc-do.json --he-so-agent 1.5
   ```
   The `Thắng:` line of that command IS the proposal; copy the minute gap into the reason.
   `--he-so-agent 1.5` is the conservative assumption — a sub-agent is 1.5× slower than the leader;
   a team that wins at this factor wins for real, not thanks to a pretty assumption.
   Command errors (the plan has no `Chạm:`) → fix the plan and measure again, guessing is banned.

2. **Write** `docs/tdq/plan/<slug>.md` out of the APPROVED spec — full khuôn in
   [references/plan-template.md](references/plan-template.md).
   Must be there: the status header + source spec · **một dòng riêng**
   `Mode thực thi: <main|subagent> — <lý do>` · the phases with checkbox tasks · a task of its own
   for the log service and for unit tests · a Definition of Done pointing back at §6 of the spec,
   **mỗi dòng DoD kiểm được bằng một lệnh** (QC counts its items off that exact number of lines).
   One task = one piece of work + one measurable check, carrying the minute estimate `(eNm)`:
   ```
   - [ ] **T1.1** (e6m) <việc cụ thể> — Test: <lệnh hoặc tiêu chí pass>
   ```
   **Every task that creates or edits a source file needs a `Chạm:` line right under it**, listing
   the paths in backticks: it is both the blast-radius map and what `tdq_team.py phan-cong` reads
   to cut parallel waves. Khuôn: the 2 sections `Chạm:`/`Cụm song song` of plan-template.
   **Score `eNm` as you write the task**, on every task, never scored later and never padded for
   safety. `eNm` is the number of minutes the agent SPENDS EXECUTING the task (waiting for approval
   does not count); the ETA of the whole plan = the sum of `eNm` over unfinished tasks. Full
   scoring rule: the last section of plan-template.
   **Luật nhãn `(mcp)`:** a task with a `Dùng:` block whose skill needs an MCP tool at runtime →
   that `Dùng:` line ends with ` (mcp)` OUTSIDE the backticks: that task must be done by Claude.

3. **Optimise.** Cut what is redundant, check the dependency order. Cross-check the 2 mapping
   rules: every output in spec §2 → ≥ 1 task; every `DÙNG` row in spec §3b → ≥ 1 contract block
   with all 5 fields (`Dùng/Để/Ra/Kiểm/Không dùng cho`) per the template. Self-check by machine:
   `python3 "./scripts/doc_lint.py" --pair <spec> <plan>` must exit 0.
   A deeper review happens only when the user asks — that is when agent `tdq-reviewer` (tùy chọn)
   gets called.

4. **Register the file into state:**
   ```
   python3 "./scripts/tdq_state.py" set plan_file=docs/tdq/plan/<slug>.md
   ```
   Do **NOT** set `implement_mode` here — that field is written only when approval is recorded.

5. **Present it, then STOP.** Write the plan block per
   [user-facing-block.md](../tdq-conventions/references/user-facing-block.md) — all 5
   components, the approval block at the end of the message, and **no** mode question here:
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
   The body is ≤ 10 lines and a REAL summary — swapping it for a bare status line such as "đã ghi
   log, đang chờ duyệt" is banned. Quoting a whole khuôn/template as an example → gắn nhãn ngay
   trước đoạn trích: "(khuôn mẫu — áp dụng cho các lần hỏi sau, không phải câu hỏi của
   turn này)". Then **end the turn**. Comments → fix, present again, wait.

6. **The user approves → record it IMMEDIATELY, then ask about the run mode in the SAME turn:**
   ```
   python3 "./scripts/tdq_state.py" approve plan --by "<nguyên văn>"
   ```
   The approval sentence already names a mode (`main`/`inline`, `subagent`/`sub-agent`) → add
   `--mode <that value>` to that very command, **skip** the gate below and build right away.
   Re-asking what the user just said is banned.
   Chưa nói mode → state dừng ở phase `mode`, in khối hỏi rồi DỪNG. Khuôn nguyên văn —
   two options "làm trực tiếp (inline implement)" and "giao trợ lý (sub-agent implement)",
   one option per line, the proposal always at A — lives in
   [references/mode-gate.md](references/mode-gate.md).
   Ngay dưới hai option phải có đoạn **"Vì sao đề xuất"** dài 1–3 dòng. Cấm nói chung
   chung: give all 4 grounds read off the plan itself (task count, dependency chain, how many
   files several tasks touch at once, whether an `(mcp)` label is present), closing with one
   sentence on why not the other option. Full rule with examples: same file mode-gate.md.
   The two names are **display labels**; state still records `main`/`subagent` (`MODE_LABELS`/`MODE_ALIASES` in `scripts/tdq_state.py`).
   The user answers → re-run the command above with `--mode <main|subagent>` and build LUÔN cùng
   turn. The settled mode is the one the USER said (it may differ from your proposal); choosing
   for the user is banned.

Xong khi: `plan_approved = true` and `implement_mode` is not empty.
Bước kế tiếp: flip the plan header to ĐÃ DUYỆT, run
`python3 "./scripts/tdq_state.py" set phase=implement`, then on to
[tdq-build](../tdq-build/SKILL.md) **NGAY trong cùng turn**.
