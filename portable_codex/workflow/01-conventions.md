---
name: tdq-conventions
description: Shared TDQ workflow rules (one-turn protocol, state, approval, hook reminder codes, git, working log, research). Loaded by the other tdq-* skills; never invoked directly.
user-invocable: false
---

# TDQ Conventions

Rules shared by every phase. Other skills link here instead of copying them.
Mọi output cho user viết **tiếng Việt**.

## 1. One-turn protocol (mandatory, in this order)

1. Turn start: the hook already printed `[TDQ:NEXT]` → use that text, **do not re-run**
   `tdq_state.py next`; run `next` only when the context has no such line.
2. Do only the work of the current phase — never start work belonging to a later phase.
3. A `[TDQ:<MÃ>]` line injected by a hook → **do what it says FIRST**, before anything else,
   then print `✓ [TDQ:<MÃ>] <đã làm gì>`. Codes: [references/reminder-codes.md](references/reminder-codes.md).
4. A turn that changed the repo MUST end with the closing command
   `python3 "./scripts/tdq_finish.py" --files <file vừa sửa> --log "<tóm tắt>" --phase <phase mới>`
   — lint those files → append the working log → set phase → graphify. **Never Edit/Read the working log and append by
   hand**, not even when `stop_gate.py` blocks you: a block means "the command has not run", not "run something else to
   dodge it". This command is the **last action** of the turn; it runs BEFORE the closing chat block (summary, question,
   `➤ Duyệt:`, over-budget report), and after that block **no further tool call** may happen, so it stays a real final
   response. A long turn (team mode, several merge rounds) may call `tdq_finish.py` MANY times — one call per real
   milestone, e.g. one merged batch; only the LAST call must be the final action. Never call it empty: every call
   carries `--files` and `--log` of the work just finished.
5. **Turn còn chạy tiếp sau khi đã in khối user-facing** (bị hook chặn, tự phát hiện sót
   việc, lỗi tool) → message cuối phải in **LẠI NGUYÊN VĂN 100%** khối đó. Gồm tóm tắt,
   câu hỏi, ĐỦ option, dòng `➤ Duyệt:`. Đặt NGAY SAU dòng `✓ [TDQ:<MÃ>]`. Lý do: focus mode
   chỉ hiện message cuối. Tóm tắt lại hay trỏ ngược ("xem câu hỏi ở trên") đều làm user
   mất sạch câu hỏi và option. Cấm rút gọn, cấm trỏ ngược.
6. **Every block addressed to the user** (pipeline question, interview, the spec / plan / mode / express gates, the
   commit question) follows [references/user-facing-block.md](references/user-facing-block.md): câu dẫn xưng "bạn",
   full file paths, a separator rule, the bold answer block last, no emoji.

7. **Never end a turn while the plan still has tasks** — stopping with a `[ ]` task left is abandoning the job,
   however good the progress report looks. Exactly **three exceptions** may stop a turn:
   1. Something only the user decides: spec/plan scope change, destructive or hard-to-reverse work, an input only
      the user holds.
   2. A technical block with no option you may pick yourself (lost access, no network, broken tool).
   3. The QC fix loop hit its ceiling of 3 rounds — rule in `tdq-build/references/qc.md`.
   Running out of step budget is NOT an exception: report it and carry on. Neither is "let's leave the rest for the
   next turn to keep this one tidy".

Xong khi: phase mới đã ghi vào state và working log đã có entry của turn này.
Bước kế tiếp: theo cột "lệnh chuyển tiếp" trong [references/phases.md](references/phases.md).

## 2. Phase table

Full table (entry condition / single job / transition command / done when / forbidden):
[references/phases.md](references/phases.md) — a file **generated** from the `PHASE_TABLE`
constant in `scripts/tdq_state.py`. Never copy its commands elsewhere, never hand-edit it.

## 3. State

- Read and write state **only** through the CLI:
  `python3 "./scripts/tdq_state.py" <next|get|set|approve|init|reset>`.
  Hand-editing `docs/tdq/state.json` or `docs/tdq/STATE.md` is forbidden (generated mirror, read-only).
- `next` answers "what do I do now". `get <key>` reads one field.
- `init <slug> <quick|full>` = **open a new request**; it wipes every old field (lane, phase, spec/plan file, every
  approval mark, implement_mode) and keeps the old slug in `previous_request`. Run it for EVERY new request once the
  user picks a lane; an unfinished request → name the slug and phase about to be lost, then **ask the user first**.
- `reset` only when the user closes a request for good. To experiment with the workflow, aim at a throwaway project:
  put `TDQ_PROJECT_DIR=/tmp/...` on that very command (no `||` fallback).
- Any state trouble is a warning only (exit 0). Exit 2 means the command syntax was wrong.

## 4. Recording approval

The user approves in ordinary chat — no required syntax, no gate that blocks the user.
Signals, counter-examples, and the command to run: [references/approval.md](references/approval.md).

Three rules that must never break, whatever else changes:
- Ambiguous wording → **ASK**; never infer that approval was given.
- Approving the spec is not approving the plan. Record only what the user named.
- Execution mode is always the USER's choice (main | subagent). Proposing is fine, deciding for them is not.

## 5. Document tree

```
docs/tdq/
  state.json + STATE.md   # state ghi qua CLI; STATE.md là mirror tự sinh, chỉ đọc
  brief/<slug>.md     research/<slug>.md   spec/<slug>.md
  plan/<slug>.md      qc/<slug>.md         reports/<slug>.md
docs/workinglog/YYYY-MM-DD.md
```
Slug: `YYYY-MM-DD-HHMM-<kebab ≤5 từ, không dấu>` (local time, so sorting names sorts by time),
the same in every folder. Old date-only slugs still READ fine; writing a new one without hour
and minute makes `init` refuse. `brief/` merges request, knowledge and Q&A into one file with
exactly three sections: `## Nguyên văn`, `## Hiểu & kiến thức`, `## Hỏi đáp`.

## 6. Working log

- Any turn that changed the repo → `tdq_finish.py --log` appends to the END of `docs/workinglog/<hôm nay>.md`: time,
  files changed, why, tests run. How the hook detects it: [reminder-codes.md](references/reminder-codes.md).
- A read-only or analysis turn writes nothing. A turn that only edits the working log adds no further entry.
- **Images the user attached.** A turn with attached images that must also write a working log → copy them into
  `docs/workinglog/assets/`, then put the links inside the `--log` string, BEFORE calling `tdq_finish.py`. Paths,
  numbering, full rule: [references/worklog-images.md](references/worklog-images.md).

## 7. Git

- Branch, commit and worktree names **never** start with `claude`, `antigravity`, `gemini`, `codex`.
- Commit messages **never** contain "generated with <AI>", "được tạo cùng/với/bởi <AI>", or an AI Co-Authored-By trailer.
- **Never** commit or push before the user asks.

## 8. Research

- Web search goes through `tavily-primary` first, always. Failover and advanced patterns:
  [references/tavily.md](references/tavily.md).
- Every claim needs a source or a stated basis. Never invent one. Routing work to plugins and the protocol for
  already-enabled ones: [references/plugin-routing.md](references/plugin-routing.md).
- Never put an API key in an answer, a log, a shell command or a prompt.

## 9. Sub-agents

- The `description` of every Agent call reads `<model>-<effort>-<việc-kebab>` (e.g.
  `sonnet-low-research-doc`) — the name alone tells which model and effort are running.
- Default model/effort per role plus the override rule: [references/subagent-tuning.md](references/subagent-tuning.md).

## 10. One-batch rule (tier 2 — runtime) and context cost

One tool call is one round trip ≈ 3.3 s. Total time scales with the NUMBER OF STEPS; context size only nudges it.
That is why this rule belongs to the **runtime** tier, not to context cost.

- **When it applies:** you are about to issue two or more tool calls and none of them needs another's result.
- **What to do:** issue them all in ONE batch; join independent Bash commands with `&&`; do not re-read a file whose
  content is still in context.
- **Self-check:** "Does the later call need the earlier call's result?" — No → batch. Yes → split.

Cases where batching is banned, the (soft) re-read rule with RULE-vs-FORGOT, the MCP output ceiling, reading just
enough, handing heavy work to a subagent: [references/context-budget.md](references/context-budget.md); the
before/after carry-cost measurement scenario: [references/measure-scenario.md](references/measure-scenario.md).

## 11. Quality

- Soul — the rule above every rule: chất lượng > runtime > context cost. Writing or changing a rule, rules that contradict each other, or a plan to cut steps → open [references/soul.md](references/soul.md).
- Clean code is standing behaviour, not a gate you ask about. Every time you write or change code, shape the project,
  scripts, functions and classes as cleanly as the five SOLID principles allow. Two-reader table, RIGHT/WRONG examples,
  five-question checklist: [references/clean-code.md](references/clean-code.md).
- No placeholders, no TODO stubs, no mock data presented as real. Missing information → ask the user, do not guess.
- Anything built ships a log service on by default (timestamps, enough detail to debug, switchable off through config).
- Every task in a plan has its own test; a passing task is ticked `[x]` IMMEDIATELY, never batched at the end of the turn.
