# TDQ Workflow — Google Antigravity Core Rules (Soul & Constitution)

> Soul: **chất lượng > runtime > context cost** · Source of Truth: `skills/tdq-conventions/references/soul.md`

## 1. Mandatory Entry & Phase Sequence
- **Every user request MUST begin with `tdq-intake`** (`skills/tdq-intake/SKILL.md`). NEVER switch into harness `EnterPlanMode` on your own (`[TDQ:NO-PLAN-MODE]`).
- Full pipeline: `analyze -> spec -> [approve spec] -> plan -> [approve plan] -> mode -> implement (red -> green per task) -> qc -> report -> [set phase=idle]`.
- Express lane (`quick`): `analyze -> quick_analyze -> mini-plan -> [approve quick] -> implement -> report -> [set phase=idle]`.
- Zero-Popup UI Policy (`ask_question` blocked mid-request): Ask numbered options (`1a 2b 3c`) and receive approvals directly in chat text. Use `--by "<exact user words>"` when recording approvals via CLI.
- All Python helpers use `py -3 -X utf8 "<plugin_dir>/scripts/<script>.py"` (or `python3 scripts/<script>.py` inside TDQ repos).

## 2. Clean Code Invariants & 7-Rung `TDQ:GON` Ladder
Before creating any symbol, file, or test: climb the 7-rung ladder (`skills/tdq-build/references/rules/chung.md`):
1. Read exact line ranges (`read_file` with `StartLine`/`EndLine`); never invent signatures or read whole huge files unnecessarily.
2. Delete dead code instead of commenting it out; reuse existing helpers before adding new ones.
3. Keep functions <= 50 lines, shallow nesting with early returns, zero duplicated blocks.
4. No silent fallbacks or swallowed errors — fail closed on invariant checks; surface real diagnostics.
5. **Triage Before Touch** (Clean Architecture Refactor Exemption): understand design intent before editing; do NOT flatten structured layers just to minimize diff lines.
6. Every built artifact MUST include default-on timestamped stderr/file logging (`TDQ_LOG=0` toggles off) and real behavior tests (`red -> green`).
7. Digest cap `<= 1,500 chars` in subagent reports & chat updates; detailed evidence goes to `docs/tdq/reports/<slug>.md` or `docs/tdq/qc/<slug>.md`.

## 3. 3-Tier Search & MCP-First Autonomy
- Start code sessions with `start_lsp` (and `open_document` for TS/JS) to unlock `Grep`/`run_command` search quotas.
- Order: **LSP** (`find_symbol`, `find_references`, `go_to_definition`) -> **Grep/ripgrep** (exact literals) -> **Graphify** (`graphify query`, blast radius).
- **MCP-First**: Check real tool inventory & connectivity before falling back to scripts.
- **LSP-Autonomy**: Decide `--bo-qua-lsp "<reason>"` autonomously for pure doc/research requests; never interrupt the user for LSP permission prompts when diagnostics suffice.
- Never claim `Done` before working log (`docs/workinglog/YYYY-MM-DD.md`), plan ticks (`- [x] **T...**`), real tests, and clean git working tree (only whitelisted docs auto-carry).

## 4. User-Facing Presentation & 6-Symbol Whitelist
- Whitelisted symbols in user-facing blocks: `➤`, `·`, `—`, `→`, `–`, `…` (emojis and box-drawing characters are strictly banned per `user-facing-block-vi-du.md`).
- Reports require 4 sections: **Before Request**, **After Request**, **What Was Tested**, **Test Result** + Archify HTML (`docs/tdq/reports/<slug>.html`).
