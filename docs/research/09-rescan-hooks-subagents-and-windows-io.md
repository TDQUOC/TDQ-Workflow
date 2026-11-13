# Deep Security & Lifecycle Edge-Case Rescan: `TDQ-Workflow/hooks/` on Antigravity Runtime & Windows I/O

- **Date:** 2026-11-13
- **Auditor Role:** Hooks, Subagent Gates & Windows I/O Auditor (`d99d4c32-902b-42b8-9b97-f26f1d5c8a62`)
- **Scope Audited (100% Line-by-Line + Empirical Test Harnesses):**
  - All **20 files** under `C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow\hooks\` (`hooks/hooks.json` + **19 `.py` files** in `hooks/scripts/`, totaling 3,483 LOC; note `subagent_context.py` referenced in early notes is actually `hooks/scripts/subagent_start.py`).
  - Supporting gate/team/search/IO engines: `scripts/utf8_io.py`, `scripts/search_rules.py`, `scripts/tdq_team.py`, `scripts/tdq_state.py`.
  - Brief & git history: `docs/tdq/brief/2026-11-11-1435-chan-tu-sua-khi-feedback.md`, commits `59953861` (`read_gate.py` range-overlap) & `d6116f2c` (`stop_gate.py` message trim).
  - Current porting docs: `docs/AUDIT-AND-PORTING-PLAN.md`, `docs/research/03-hooks-and-gates-simulation.md`, `docs/research/04-antigravity-adapter-audit.md`.
  - Official Antigravity runtime specs & live transcripts: `agy-customizations/docs/hooks.md`, `migrate-agent-settings/SKILL.md`, `google-antigravity-sdk/references/built_in_tools.md`, `~/.gemini/config/hooks/auto-compact.ps1`, and **16 live `brain/*/.system_generated/logs/transcript.jsonl` files (~835 real Antigravity tool calls)**.
- **Empirical Test Harnesses & Raw Evidence:**
  - `scratch/rescan_d/inspect_transcript_and_tools.py` & `scratch/rescan_d/inspect_deep_schemas.py`
  - `scratch/rescan_d/run_edgecase_tests.py` → `scratch/rescan_d/edgecase_test_results.json`
  - `scratch/rescan_d/run_targeted_followup.py` → `scratch/rescan_d/edgecase_followup_results.json`

---

## 1. Executive Summary & Newly Uncovered P0/P1 Blocker Matrix

While `docs/AUDIT-AND-PORTING-PLAN.md` correctly identified the basic Claude-to-Antigravity stdin/stdout JSON envelope differences (`permissionDecision: "deny"` → `{"decision": "block"}`, `Stop` `"block"` → `"continue"`, `additionalContext` drop on `"allow"`), **line-by-line code tracing combined with live subprocess execution uncovered 14 critical edge cases — including 8 P0 showstoppers** that would either **hard-deadlock Antigravity sessions** or **silently bypass TDQ's core safety fences**.

| ID | Severity | Origin | Summary of Vulnerability / Edge Case | Empirical Verification Result |
| :--- | :---: | :--- | :--- | :--- |
| **EC-01** | **P0** | Antigravity + `edit_gate.py:87,96` + `stop_gate.py:278` | **Brain Artifact / Scratch Edit Hard-Block:** Writing/editing any Antigravity artifact (`<appDataDir>\brain\<id>\*.md`) on the same `C:` drive records `../../...` in `.tdq-turn.jsonl`, causing `stop_gate.py` to **hard-block** the turn demanding `tdq_finish.py` & `docs/workinglog/`! | **PROVEN** (`edgecase_test_results.json:181`: `{"decision": "block", "reason": "[TDQ:LOG] Repo changed (../../fake_brain_artifact.md)..."}`) |
| **EC-02** | **P0** | Upstream Live Bug (`edit_gate.py:158` + `_common.py:206-215`) | **Missing Workinglog Short-Circuit Kills All Downstream Fences:** Whenever today's `docs/workinglog/YYYY-MM-DD.md` does not exist on disk yet, `remind("TDQ:LOG")` calls `sys.exit(0)` on **both** Edit #1 (`allow`) and Edits #2..N (`already_reminded` → silent `sys.exit(0)`), turning `TDQ:TEAM`, `ngoai_vung_khai`, and `TDQ:TICK` (lines 170–289) into **100% dead code**! | **PROVEN** (`edgecase_followup_results.json:14-16`: unlimited unmapped, unticked `src/foo.py` edits allowed!) |
| **EC-03** | **P0** | Antigravity Subagent `Stop` + `stop_gate.py` | **Subagent `Stop` Hook Loop Trap:** Unlike Claude Code (`SubagentStop` vs `Stop`), Antigravity fires `Stop` at the end of **every subagent's** turn. Worker subagents get trapped by `[TDQ:LOG]` (demanding they edit main's workinglog!) and read-only `research`/`reviewer` subagents get trapped for 3 turns (`MAX_STREAK=3`) by `[TDQ:UNFINISHED]`! | **PROVEN** (`edgecase_test_results.json:200-201`: both worker and read-only subagents blocked on `Stop`!) |
| **EC-04** | **P0** | Upstream Live Bug (`tdq_team.py:1615` + `edit_gate.py:170`) | **Worker Deadlock After Leader Marks `[>]` in `plan.md`:** `IMPLEMENT_SUBAGENT_ROW` requires running `assign` → `open` → marking `[>]` in `plan.md`. Marking `[>]` changes `sha_file(plan)`. While `_boi_canh` (`line 592`) uses `kiem_tra_stale` (`plan_assignment_sha`), `canh_bao_lach_luat` (`line 1615`) still checks raw `plan_sha != sha_file(plan)` AND `edit_gate.py:170` sets `trong_project=True` for `.tdq-worktrees/`, **blocking every worker edit inside `.tdq-worktrees/` with `[TDQ:TEAM]`!** | **PROVEN** (`edgecase_followup_results.json:21`: worker edit inside `.tdq-worktrees/.../t1.1/src/foo.py` denied with `[TDQ:TEAM] Team mode with no assignment map`!) |
| **EC-05** | **P0** | Antigravity `Workspace="inherit"` + `tdq_team.py:1628` | **Accidental Main-Repo Edit Slips Past All 3 Fences:** Once `tdq_team.py open T1.1` creates branch `tdq/<slug>/t1.1`, `_co_nhanh` is `True` (`canh_bao_lach_luat` → `None`), `ngoai_vung_khai` ignores paths outside `.tdq-worktrees/` (`→ None`), and `[>]` satisfies `tick["has_doing"]` (`TDQ:TICK` → skipped). Both leader and `Workspace="inherit"` workers can overwrite `<main_repo>/src/foo.py` unblocked! | **PROVEN** (`edgecase_followup_results.json:24`: editing main `src/foo.py` returned `"permissionDecision": "allow"`!) |
| **EC-06** | **P0** | Antigravity Hook `stdin` + `edit_gate.py:103,125` + `bash_gate.py:136` | **Missing `agent_id` Bypasses Pre-Implement Subagent Fences:** Antigravity hook `stdin` has `conversationId` and `workspacePaths`, **never `agent_id`**. Pre-implement subagents (`analyze`/`spec`/`plan`) bypass `TDQ:TEAM` and `TDQ:STATE`, allowing direct edits to `src/*` and `docs/tdq/state.json`. | **PROVEN** (`edgecase_test_results.json:186-188`: `allow` without `agent_id` vs `deny` with `agent_id`!) |
| **EC-07** | **P0** | Porting Plan §5 Nhóm 4 + AGY 2.0 Tool Vocabulary | **Broken `tools:` Grants on Read-Only Subagents & `call_mcp_tool` Blind Spot:** In Antigravity 2.0, `grep_search`, `find_by_name`, and `list_dir` **do not exist** (`0` calls across 835 transcript tool calls; `migrate-agent-settings/SKILL.md:158` maps `Read/Glob/Grep → read_file`). Giving `tdq-reviewer`/`tdq-security-reviewer` `[read_file, grep_search, find_by_name, list_dir, send_message]` leaves them unable to list directories or grep! Furthermore, non-eager MCP tools (~56 of 65 `agent-lsp` tools) execute via **`call_mcp_tool`**, bypassing `mcp_.*lsp_.*` hook matchers! | **PROVEN** (835 tool calls across 16 live transcripts + `<mcp_servers>` runtime schema) |
| **EC-08** | **P0** | Upstream Gap (`edit_gate.py:115,137` + `tdq_state.py:2942`) | **`[TDQ:FEEDBACK]` Post-Request Approval Carryover Loophole (`2026-11-11-1435`):** `tdq_state.py set phase=idle` (`line 2942`) **never clears** `active_request`, `spec_approved`, `plan_approved`, or `quick_approved`. In `phase="report"` or `"idle"`, `cong_dang_cho(state)` is `None` and `TDQ:TICK` only checks `implement`/`qc`, so **100% of source code edits are allowed without triage or approval** when the user gives post-request bug feedback! | **PROVEN** (`edgecase_test_results.json:204-205`: `allow` in `report`, silent `""` allow in `idle`!) |
| **EC-09** | **P1** | Porting Plan §3.2 (`line 239`) + `read_gate.py:111-125` | **`read_file` `StartLine`/`EndLine` vs `offset`/`limit` Math & `ByteOffset` Trap:** Mapping inclusive `EndLine` directly to line-count `limit` inflates `[200, 350]` (151 lines) into `[200, 550]` (350 lines), breaking `_tinh_overlap_ratio`. Additionally, `read_file` paginates files >46,080 bytes via `ByteOffset=46080`, triggering false `[TDQ:DOC]` duplicate-read warnings on page 2! | **PROVEN** (`edgecase_test_results.json:128-129, 149`) |
| **EC-10** | **P1** | Windows NTFS Concurrency (`tdq_state.py:1875`, `read_gate.py:94`) | **29.1% Data Loss on Shared `.tdq-turn.jsonl` & Truncation Races:** Unlocked read-modify-`os.replace` in `turn_log_clear` + `except OSError: pass` on Windows NTFS sharing violations (`WinError 5`/`32`) dropped **93 of 320 rows (29.1%)** across 8 parallel processes! `read_gate.py` (`TRAN_DONG=400`) and `search_observe.py` (`TRAN_DONG=600`) truncate in-place via `open(..., "w")`. | **PROVEN** (`edgecase_followup_results.json:28-31`: `227/320` rows survived, `93` lost!) |
| **EC-11** | **P1** | `session_start.py:118-245` on Windows | **12.7s Startup Stall, `WinError 206` & Workspace `.codex` Pollution:** Running `session_start.py` invokes `claude.EXE plugin update`, hits dozens of `[WinError 206] Filename too long` copying `.claude/worktrees/` to cache, takes **12,684 ms**, and writes `.codex/hooks.json` into the target workspace! | **PROVEN** (`edgecase_test_results.json:92-93`: `12684.08 ms` + `.codex/hooks.json` created!) |
| **EC-12** | **P1** | Antigravity `PreInvocation` Frequency + `tdq_state.py:1940` | **`PreInvocation` Fires Per-Model-Step (Not Per-User-Turn):** `repo_status_digest` spawns 2 `git` subprocesses taking **167.3 ms** avg on `TDQ-Workflow`. Unconditional execution on a 15-step tool turn adds **2.5+ seconds** of pure hook latency and resets turn snapshots mid-turn! | **PROVEN** (`edgecase_test_results.json:235-244`: `167.28 ms` avg × 15 = `2509.2 ms`) |
| **EC-13** | **P1** | Windows `cmd /c` `cp1252` (`codex_edit_gate.py:41,188`, `luat_gon.py:47`, `auto-compact.ps1:9`) | **Windows `cp1252` + `surrogateescape` Mojibake & Hook Crashes:** Under `cmd /c` with `PYTHONIOENCODING` unset, Python defaults to `cp1252` (`surrogateescape` on stdio, `backslashreplace` on stderr). `codex_edit_gate.py` omits `sys.stdin` from `reconfigure()`, corrupting Vietnamese UTF-8 paths (`'Đ'` `c4 90` → `'Ä\udc90'`) and causing false `[TDQ:VUNG]` denials; `luat_gon.py` lacks `utf8_io`; any new hook without `utf8_io` crashes with `UnicodeEncodeError` on `'đ'` (`U+0111`). | **PROVEN** (`edgecase_followup_results.json:2,11`: `cp1252 surrogateescape`, `khng \u0111\u1ecdc...`) |
| **EC-14** | **P2** | `transcript.jsonl` Serialization & `search_rules.py` PowerShell | **Double-Encoded String Args in `transcript.jsonl` & PowerShell File-Listing Blind Spot:** Every value in `transcript.jsonl` `tool_calls[*].args` is a JSON-encoded string (`"300"`, `"\"C:\\\\...\""`). Also, `search_rules.py` classifies `Get-ChildItem -Path src -Filter *.py -Recurse` as `khong_phai_tim` (`not_search`), missing native PowerShell file discovery on Windows. | **PROVEN** (`inspect_deep_schemas.py` & `edgecase_test_results.json:168-175`) |

---

## 2. Complete Audit of All 20 Files in `TDQ-Workflow/hooks/`

Inventory of `C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow\hooks\`: **1 JSON manifest** (`hooks/hooks.json`) + **19 Python files** in `hooks/scripts/` (17 executable hooks/CLIs + 2 shared helper modules `_common.py` and `luat_gon.py`).

| # | File | Lines | Current Event / Role | Encoding Safety (`cp1252`) | Antigravity Porting Verdict & Edge Cases Found |
| :-: | :--- | :---: | :--- | :--- | :--- |
| 1 | `hooks/hooks.json` | 136 | Claude Code hook manifest (`SessionStart`, `SubagentStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop`) | UTF-8 JSON | **REWRITE** for Antigravity (`PreInvocation`, `PreToolUse`, `PostToolUse`, `Stop`). Must remove `${CLAUDE_PLUGIN_ROOT}`, switch to `python` on Windows (`python3` Microsoft Store alias risk), and add `call_mcp_tool` + `invoke_subagent\|swarm` matchers. |
| 2 | `hooks/scripts/_common.py` | 311 | Core hook I/O, `read_stdin`, `remind`, `block`, `observe`, `within` | Safe (`imports utf8_io` at line 25) | **UPGRADE (Core Adapter):** (1) `remind()` calls `sys.exit(0)` even on `already_reminded` (`line 207`), killing downstream blocks in `edit_gate.py`! (2) Must output Antigravity `{"decision": "allow"\|"block", "reason": ...}` + spool `additionalContext` to `.tdq-pending-reminders-<convId>.jsonl` when `decision=="allow"`. (3) Must normalize Antigravity camelCase fields, `StartLine`/`EndLine`/`ByteOffset`, `call_mcp_tool`, and synthesize `agent_id` for subagents! |
| 3 | `hooks/scripts/luat_gon.py` | 76 | Pure reader/filter for `<!-- luat-gon -->` block in `chung.md` | **UNSAFE standalone** (no `utf8_io`; prints raw Vietnamese to `stderr` at lines 47, 52 → mojibake `khng \u0111\u1ecdc` under `cp1252`) | **PATCH:** Import `utf8_io` (or route warnings through `_common.log`). |
| 4 | `hooks/scripts/session_start.py` | 390 | `SessionStart`: plugin cache auto-update, `.codex` MCP sync, background search warm-up (`tdq_warmup.py`), `[TDQ:NEXT]` + `[TDQ:GON]` banner | Safe (`imports _common`) | **STRIP & MERGE INTO `PreInvocation` (Turn 1 Only):** Lines 118–245 (`_dong_bo_plugin_moi`, `_chay_setup_bu`, `tdq_codex_mcp`) took **12.68s**, threw `WinError 206` (MAX_PATH) & `WinError 5` copying `.claude/worktrees/`, and polluted target repo with `.codex/hooks.json`! Keep **only** `_khoi_dong_nen(cwd)` (`CREATE_NO_WINDOW \| DETACHED_PROCESS`), orphan worktree check, and initial `[TDQ:NEXT]`/`[TDQ:GON]` banner, gated once per leader `conversationId`. |
| 5 | `hooks/scripts/subagent_start.py` | 55 | `SubagentStart`: injects `[TDQ:GON]` lean law into subagent context *(referred to as `subagent_context.py` in early notes)* | Safe (`imports _common`) | **RE-ARCHITECT:** Antigravity has **no `SubagentStart` event**, and `PreInvocation` `additionalContext` should only inject `[TDQ:GON]` (never leader `[TDQ:NEXT]`/`[TDQ:APPROVE]`) when `is_subagent(cwd, conversationId)` is `True` on `invocation_num == 1`, plus embed `[TDQ:GON]` in `agents/tdq-implementer.md` & `tdq-qc-tester.md`. |
| 6 | `hooks/scripts/prompt_context.py` | 437 | `UserPromptSubmit`: clears turn ledger, takes `turn_snapshot`, injects `[TDQ:INTAKE]`/`[TDQ:APPROVE]`/`[TDQ:UNFINISHED]`/`[TDQ:NEXT]`, flushes deferred reminders | Safe (`imports _common`) | **UPGRADE FOR `PreInvocation`:** Antigravity fires `PreInvocation` on **every model step** (15x/turn) AND inside **subagents**! Must: (1) Detect subagent vs leader (`subagent` → inject only `[TDQ:GON]` + pending subagent reminders; never overwrite leader snapshot or inject `approve` commands). (2) Detect new user turn (`lastUserInput` changed / step 1) vs mid-turn tool step (mid-turn → ONLY flush `.tdq-pending-reminders-<convId>.jsonl`, skip `turn_log_clear` & 167ms `turn_snapshot`!). |
| 7 | `hooks/scripts/edit_gate.py` | 291 | `PreToolUse` (`Edit\|Write\|MultiEdit\|NotebookEdit`): enforces `TDQ:STATE`, pre-implement subagent `TDQ:TEAM`, `TDQ:APPROVE`, `TDQ:LOG`, `canh_bao_lach_luat`, `ngoai_vung_khai`, `TDQ:TICK`, cookbook reminders | Safe (`imports _common`) | **CRITICAL PATCHES NEEDED (5 P0s):** (1) Exclude `<appDataDir>/brain/` (`artifactDirectoryPath`) before `observe("edit")` & `TDQ:LOG` (`EC-01`). (2) Move `remind("TDQ:LOG")` & cookbook `remind()` **AFTER** all `block()` checks so missing workinglog never short-circuits `TDQ:TEAM`/`TDQ:TICK` (`EC-02`). (3) Fix `canh_bao_lach_luat` (`plan_sha` → `kiem_tra_stale`) and skip `canh_bao_lach_luat` when `in_worktree_doi` is `True` (`EC-04`). (4) Block main-repo edits on `giao` tasks even when `_co_nhanh` is `True` (`EC-05`). (5) Add `[TDQ:FEEDBACK]` block when `phase in ("idle", "report")` or `active_request is None` (`EC-08`). |
| 8 | `hooks/scripts/read_gate.py` | 233 | `PreToolUse` (`Read`): warns `[TDQ:DOC]` on whole-file re-reads (`>=4KB`, unchanged `mtime`) or `>=70%` line-range overlap (`commit 59953861`) | Safe (`imports _common`) | **PATCH:** (1) Convert Antigravity `StartLine`/`EndLine` (1-based inclusive) to `(dau, cuoi)` properly instead of `dau + EndLine` (`EC-09`). (2) Track `ByteOffset` so multi-chunk reads (`ByteOffset=46080`) of >46KB files do not false-trigger `[TDQ:DOC]`. (3) Spool `[TDQ:DOC]` reminder to `.tdq-pending-reminders-<convId>.jsonl` since Antigravity drops `additionalContext` on `PreToolUse` `"allow"`. (4) Replace unlocked `.tdq-read.jsonl` in-place `open("w")` truncation with per-session file or atomic locked write (`EC-10`). |
| 9 | `hooks/scripts/bash_gate.py` | 208 | `PreToolUse` (`Bash`): blocks `git commit --no-verify`, direct `state.json` shell writes, pre-implement subagent shell mutations, team-mode bypasses | Safe (`imports _common`) | **PATCH:** (1) Synthesize `agent_id` from `.tdq-sessions.json` so pre-implement subagents cannot mutate code via PowerShell `Set-Content`/`Out-File`/`python -c` (`EC-06`). (2) Add `[TDQ:FEEDBACK]` shell-mutation check in `idle`/`report` (`EC-08`). (3) Add PowerShell write cmdlets (`Set-Content`, `Add-Content`, `Out-File`, `New-Item`, `Copy-Item`, `Move-Item`, `Remove-Item`) to `_shell_writes_outside_docs` (`lines 60-85`, which currently only checks `>`, `sed -i`, `tee`, `cp`, `mv`, `rm`!). |
| 10 | `hooks/scripts/search_gate.py` | 201 | `PreToolUse` (`Grep\|Glob\|Bash`): blocks raw code search until symbol/graph/semantic search layers (`agent-lsp` / `graphify` / `txtai`) are queried first | Safe (`imports _common`) | **PATCH:** Match `run_command` (+ IDE `grep_search\|find_by_name\|list_dir` if running on IDE surface). Enhance `search_rules.py` for PowerShell `Get-ChildItem -Filter ... -Recurse` (`EC-14`). |
| 11 | `hooks/scripts/lsp_gate.py` | 163 | `PreToolUse` (`mcp__.*lsp__start_lsp`): blocks `start_lsp` without `language_id` (prevents 0xc0000409 crash) or mismatched `root_dir` | Safe (`imports _common`) | **PATCH (P0 `call_mcp_tool` Gap):** Must match **both** eager `mcp_.*lsp_start_lsp` AND lazy `call_mcp_tool` where `toolInput.ServerName` ends with `lsp` and `toolInput.ToolName == "start_lsp"` (`EC-07`)! |
| 12 | `hooks/scripts/search_observe.py` | 222 | `PostToolUse` (`Grep\|Glob\|Bash\|Read\|mcp__.*(lsp\|graphify\|txtai).*`): logs search layer usage to `.tdq-search.jsonl` to unlock `search_gate.py` | Safe (`imports _common`) | **CRITICAL PATCH:** Must match **both** `mcp_.*(lsp\|graphify\|txtai).*` AND **`call_mcp_tool`**! Otherwise, calling lazy LSP tools (`inspect_symbol`, `explore`, `find_references`) via `call_mcp_tool` **never gets recorded in `.tdq-search.jsonl`**, causing `search_gate.py` to permanently block subsequent searches (`EC-07`)! |
| 13 | `hooks/scripts/ask_gate.py` | 63 | `PreToolUse` (`AskUserQuestion`): reminds `[TDQ:LANG]` if `doc_lang == "vi"` | Safe (`imports _common`) | **ADAPT:** Match `ask_question`. Because Antigravity `PreToolUse` `"allow"` drops `additionalContext`, spool `[TDQ:LANG]` or rely on `rules/tdq-core.md`. Never omit `"decision": "allow"` on Antigravity (unlike Claude `decide=False`). |
| 14 | `hooks/scripts/stop_gate.py` | 367 | `Stop`: enforces `[TDQ:UNFINISHED]`, `[TDQ:PAUSE]`, `[TDQ:LOG]`, `[TDQ:TICK]` with `MAX_STREAK=3` circuit breaker | Safe (`imports _common`) | **CRITICAL PATCHES:** (1) Output `{"decision": "continue", "reason": ...}` instead of `"block"` (on Antigravity `Stop`, `"continue"` forces continuation!). (2) **Immediately return `{}` for subagents** (`is_subagent == True`) so workers and read-only subagents are never trapped in `[TDQ:LOG]`/`[TDQ:UNFINISHED]` loops (`EC-03`)! (3) Key `stop_streak` per `conversationId`. (4) Ignore paths outside `cwd` (e.g., `brain/` artifacts, `EC-01`). |
| 15 | `hooks/scripts/codex_edit_gate.py` | 223 | PreToolUse bridge for Codex `apply_patch` (`TDQ_CODEX_TASK` / `TDQ_CODEX_VUNG`) | **BUGGY `sys.stdin`** (reconfigures `stdout`/`stderr` at line 41, **forgets `sys.stdin`** at line 188 → Vietnamese UTF-8 paths become lone-surrogate mojibake `Ä\udc90` under `cp1252`!) | **PATCH `sys.stdin.reconfigure(encoding="utf-8", errors="replace")`:** Only needed if `implement_mode="codex"` is kept as an external CLI option; not wired in Antigravity `hooks.json`. |
| 16 | `hooks/scripts/agy_pretooluse_gate.py` | 157 | Legacy standalone Antigravity `PreToolUse` prototype (`.git/hooks` + `state.json` write guard) | Safe (`imports utf8_io`) | **SUPERSEDE / RETIRE:** Superseded by unified `_common.py` + full `edit_gate.py` / `bash_gate.py`. Retain its `.git/hooks` write guard inside `bash_gate.py` & `edit_gate.py`! (Note: currently NOT wired in `hooks/hooks.json`.) |
| 17 | `hooks/scripts/agy_stop_gate.py` | 211 | Legacy standalone Antigravity `Stop` prototype (correctly uses `"decision": "continue"`) | Safe (`imports utf8_io`) | **SUPERSEDE / MERGE INTO `stop_gate.py`:** Has 2 latent bugs of its own: (1) `.agy-stop-snapshot.json` & `.agy-stop-streak.json` are global per-repo (not per-`conversationId`), colliding on subagents; (2) no `PreInvocation` writer ever refreshes `.agy-stop-snapshot.json` at turn start! Merge its `"decision": "continue"` protocol directly into `stop_gate.py`. |
| 18 | `hooks/scripts/doc_file_gate.py` | 80 | Standalone CLI validator (`sys.argv[1]`) blocking rogue `.md` files outside `docs/tdq/` & `docs/workinglog/` | Safe (`imports utf8_io`) | **KEEP AS HELPER / INTEGRATE:** Not wired in `hooks.json`; if integrated into `edit_gate.py`, MUST exempt `<appDataDir>/brain/` (Antigravity artifacts) and `.gemini/` customization `.md` files! |
| 19 | `hooks/scripts/stop_batch_checker.py` | 78 | Standalone CLI (`sys.argv[1]`) counting `[x]` tasks for `[TDQ-BATCH-CHECKPOINT]` | Safe (`imports utf8_io`) | **LEGACY / NOT WIRED:** Superseded by `tdq_state.plan_tick_state`; safe to keep in `scripts/` for CLI compatibility. |
| 20 | `hooks/scripts/strategic_compact_gate.py` | 106 | Standalone CLI (`sys.argv[1:3]`) suggesting `/compact` at phase transitions | Safe (`imports utf8_io`) | **ADAPT OPTIONAL:** Notice Antigravity natively supports the `/compact` slash command (confirmed in `<slash_commands>`)! Can optionally surface `/compact` hint on `spec → plan` and `plan → implement` transitions. |

**Bonus Finding on User's Existing Global Hook (`C:\Users\admin\.gemini\config\hooks\auto-compact.ps1`):**
- Currently registered in `~/.gemini/config/hooks.json` on `PreToolUse` (`*`).
- Line 9 (`$rawInput = $input | Out-String`) lacks `[Console]::InputEncoding = [System.Text.Encoding]::UTF8`, and Line 13 (`catch { Write-Output '{}' }`) emits `{}` instead of `{"decision": "allow"}` on error. Our plugin `hooks.json` runs alongside global hooks (`hooks.md:92-99`: most restrictive decision wins), so TDQ's Python hooks must never fail into malformed output.

---

## 3. Live Antigravity Tool Call Schemas vs `AUDIT-AND-PORTING-PLAN.md` §3.2

### 3.1 Complete Empirical Tool Inventory (Extracted from 16 Live `brain/*/transcript.jsonl` Logs — 835 Tool Calls + Live Runtime Declarations)

| Category | Exact Antigravity Tool Name | Calls in Live Logs | Exact Parameter Keys (Case-Sensitive!) | Proposed in Plan §3.2? | Audit Status & Required Fix |
| :--- | :--- | :---: | :--- | :---: | :--- |
| **File Read** | `read_file` | 308 | `Path` (req), `StartLine` (int), `EndLine` (int), `ByteOffset` (int) | Partial | **FIX P1 (`EC-09`):** Plan mapped `EndLine → limit` directly (wrong math!) and omitted `ByteOffset` (causes false `[TDQ:DOC]` on >46KB files). |
| **File Edit** | `edit_file` | 29 | `Path` (req), `Target` (req), `Replacement` (req), `ArtifactMetadata` (obj: `Summary`, `UserFacing`, `RequestFeedback`) | Partial | **FIX P0 (`EC-01`):** Plan missed `ArtifactMetadata` and `<appDataDir>/brain/` path exclusion, causing `stop_gate.py` to hard-block artifact edits! |
| **File Write** | `write_file` | 48 | `Path` (req), `Content` (req), `Overwrite` (bool), `Append` (bool), `ArtifactMetadata` (obj) | Partial | **FIX P0 (`EC-01`):** Same `<appDataDir>/brain/` exclusion required. |
| **Shell Exec** | `run_command` | 377 | `CommandLine` (req), `WaitMsBeforeAsync` (req, int), `toolSummary` (req), `IsDaemon` (bool) | Yes | **FIX P1:** `bash_gate.py` must also detect PowerShell write cmdlets (`Set-Content`, `Out-File`, `Add-Content`, `New-Item`). |
| **Task Mgmt** | `manage_task` | 0 (decl) | `Action` (`list`\|`kill`\|`status`\|`send_input`), `TaskId`, `Input` | **NO** | **ADD:** `Action=="send_input"` can send shell commands to an interactive background PowerShell task; inspect `Input` in `bash_gate.py`! |
| **User Prompt** | `ask_question` | 0 (decl) | `questions` (array of `{question, options, is_multi_select}`) | Yes | Safe (`questions[i].question` matches `ask_gate.py`). |
| **Subagents** | `invoke_subagent` | 15 | `TypeName` (req), `Role` (req), `Prompt` (req), `Model`, `Workspace` (`inherit`\|`branch`\|`share`) | **NO** | **ADD P0 HOOK:** Hook `PreToolUse` on `invoke_subagent\|swarm` to record subagent dispatch metadata + block `Workspace="share"\|"branch"` collisions with `.tdq-worktrees/`! |
| **Subagents** | `define_subagent`, `manage_subagents`, `send_message` | 15 | `{Name, Description, SystemPrompt, EnableWriteTools...}`, `{Action, ConversationIds}`, `{Recipient, Message}` | **NO** | Allow; `define_subagent` with `EnableWriteTools=True` before `implement` should warn/block if trying to bypass read-only agents. |
| **Swarm** | `swarm` (+ worker board tools `post_message`, `read_board`, `swarm_wait`) | 0 (decl) | `{action: "status"\|"models"\|"add"\|"model"\|"kill"\|"title", name, brief, workspace, fork, model, n, tasks, title}` | **NO** | **ADD:** Hook `swarm` (`action=="add"`) alongside `invoke_subagent`. |
| **Eager MCP** | `mcp_<server>_<tool>` / `mcp_<plugin>_<server>_<tool>` | 8 | Tool-specific args (`query`, `chunk_id`, `language_id`, `root_dir`, etc.) | Partial | Note single underscore `mcp_` (vs Claude double `mcp__`) and optional `<plugin>_` prefix! Regex must be `^mcp_.*`. |
| **Lazy MCP** | **`call_mcp_tool`** | 0 (sys) | Server name + tool name + arguments object (used for ALL non-eager MCP tools!) | **MISSED (P0!)** | **CRITICAL FIX (`EC-07`):** Only ~9 of 65 `agent-lsp` tools are marked `eager: true`. All other 56 LSP tools go through `call_mcp_tool`! Must unwrap `call_mcp_tool` in `_common.py` for both `lsp_gate.py` (`PreToolUse`) and `search_observe.py` (`PostToolUse`)! |
| **IDE / SDK Surface Variants** | `view_file`, `list_directory` / `list_dir`, `search_directory` / `grep_search`, `find_file` / `find_by_name`, `create_file`, `replace_file_content`, `multi_replace_file_content` | **0 in AGY 2.0** | `AbsolutePath` / `TargetFile` / `DirectoryPath` / `SearchPath` / `Query` | Partial | **CRITICAL (`EC-07`):** Absent in Antigravity 2.0 desktop/CLI (`0/835` calls; confirmed by `migrate-agent-settings/SKILL.md:157-161`), but present in Antigravity SDK (`built_in_tools.md:24-33`: `view_file`, `list_directory`, `search_directory`, `find_file`, `create_file`) and older IDE surfaces (`hooks.md:115`: `view_file`). Keep in **hook matchers** for cross-surface safety, **NEVER rely on them in `agents/*.md` `tools:` lists without `run_command`!** |

---

### 3.2 Deep Dive: `read_gate.py` Range-Overlap (`commit 59953861`) & `edit_gate.py` `Target` Check

1. **Does `read_gate.py` or `edit_gate.py` check `Target` (`old_string`) line overlap on `edit_file`?**
   - **Verified line-by-line:** **NO.**
   - `hooks/scripts/read_gate.py` (`lines 1-233`) runs strictly on `PreToolUse(Read)`.
   - `hooks/scripts/edit_gate.py` (`lines 78-291`) extracts **only** `tool_input.get("file_path") or tool_input.get("notebook_path")` (`line 80`). It **never** reads `old_string` / `Target` or `new_string` / `Replacement`.

2. **How `read_gate.py` checks `offset`/`limit` (`lines 111-168`) — and why Plan §3.2 (`line 239`) breaks it:**
   - In `read_gate.py:111-125`:
     ```python
     def _vung(tool_input):
         try:
             dau = int(tool_input.get("offset") or 0)
             gioi_han = int(tool_input.get("limit") or 0)
         except (TypeError, ValueError):
             return 0, 0
         ...
         cuoi = dau + gioi_han if gioi_han else 0
         return dau, cuoi
     ```
   - Claude Code's `Read` passes `offset` (start line) and `limit` (**number of lines to read**).
   - Antigravity's `read_file` passes `StartLine` (1-based start line), `EndLine` (**1-based inclusive end line**, NOT a count!), and `ByteOffset` (byte offset into that line range when content exceeds `46,080` bytes).
   - **Empirical Bug 1 (`2A_naive_endline_as_limit`, `edgecase_test_results.json:124-144`):** When `StartLine=200, EndLine=350` (151 lines) is mapped naively to `offset=200, limit=350`, `_vung` records `dau=200, cuoi=550`! When the agent next reads **completely disjoint lines `351..530`**, `read_gate.py` computes 100% overlap with `[200, 550]`!
   - **Empirical Bug 2 (`2B_byteoffset_page2_false_positive`, `edgecase_test_results.json:147-150`):** When a file is >46,080 bytes (like `edgecase_test_results.json` at 74,455 bytes, which we ourselves just paginated with `ByteOffset=46080` during this audit!), Antigravity's `read_file` output explicitly instructs the agent:
     > *"To read the rest of this line range, call this tool again with the same StartLine and EndLine and ByteOffset=46080."*
     Without `ByteOffset` awareness, calling `read_file(Path=..., ByteOffset=46080)` immediately fires a false `[TDQ:DOC] ... is already in context from an earlier read, unchanged. Do not re-read.`!
   - **Exact Fix in `_common.py` Adapter:**
     - If `int(args.get("ByteOffset") or 0) > 0`: mark `tool_input["_byte_continuation"] = True` and **exempt from `read_gate.py` overlap warning**!
     - Convert `StartLine`/`EndLine` to `(offset, limit)` accurately:
       ```python
       start_line = int(float(args["StartLine"])) if args.get("StartLine") is not None else 0
       end_line = int(float(args["EndLine"])) if args.get("EndLine") is not None else 0
       if end_line > 0:
           eff_start = start_line if start_line > 0 else 1
           offset = eff_start
           limit = max(1, end_line - eff_start + 1)
       elif start_line > 0:
           offset = start_line
           limit = 800  # Antigravity read_file per-read cap is 800 lines
       else:
           offset, limit = 0, 0
       ```

3. **P0 Showstopper (`EC-01`): Editing Antigravity Brain Artifacts (`<appDataDir>/brain/<id>/*.md`) Hard-Blocks `stop_gate.py`!**
   - **Exact Code Trace:**
     - In `edit_gate.py:85-96`:
       ```python
       abs_target = os.path.abspath(target if os.path.isabs(target) else os.path.join(cwd, target))
       try:
           rel_target = os.path.relpath(abs_target, cwd)
       except ValueError:
           rel_target = abs_target
       ...
       observe(cwd, payload, "edit", path=rel_target)
       ```
     - On Windows, when both workspace (`C:\Users\admin\Documents\Projects\MyApp`) and `<appDataDir>` (`C:\Users\admin\.gemini\antigravity\brain\<id>\plan.md`) live on drive `C:`, `os.path.relpath` **succeeds** and returns `..\..\..\..\.gemini\antigravity\brain\<id>\plan.md`!
     - `edit_gate.py:96` writes `{"kind": "edit", "path": "..\\..\\..\\..\\.gemini\\..."}` into `.tdq-turn.jsonl` **BEFORE** line 170 checks `trong_project = within(abs_target, os.path.realpath(cwd))`!
     - At turn end, `stop_gate.py:278-306` reads `edited = [r["path"] for r in rows if event == "edit"]`, sees `edited` is non-empty and not under `docs/workinglog/`, and **blocks the agent from stopping** (`[TDQ:LOG] Repo changed (../../fake_brain_artifact.md), docs/workinglog/2026-11-13.md not appended`) — and during `implement`/`qc`, also fires `[TDQ:TICK]` (`line 314`)!
   - **Fix:** In `edit_gate.py` (right after resolving `abs_target`), if `artifactDirectoryPath` (or `~/.gemini/antigravity/brain/`) contains `abs_target` — OR more generally if `not within(abs_target, os.path.realpath(cwd))` — **do NOT record `"edit"` in `.tdq-turn.jsonl` and do NOT fire `remind("TDQ:LOG")`!**

---

## 4. CRITICAL CHECK: Subagent + Worktree Gate Interaction on Antigravity

### 4.1 How Antigravity Executes Subagents vs What Hooks Receive on `stdin`

1. **Do plugin hooks fire for subagents?**
   - **YES.** Hooks configured in `~/.gemini/config/hooks.json` or an enabled plugin's `hooks/hooks.json` execute around the agent loop and tool calls of **every** agent conversation, including subagents launched via `invoke_subagent` (`self`, `research`, custom `agents/tdq-*.md`) and `swarm` workers.
2. **What fields arrive in Hook `stdin` for a subagent?**
   - Verified against `agy-customizations/docs/hooks.md:155-165` and our own live subagent context:
     - `conversationId`: **Unique UUID per subagent** (e.g., parent is `2a408580-dde6-4a41-aeda-5a1f871c0366`; this subagent is `d99d4c32-902b-42b8-9b97-f26f1d5c8a62`).
     - `transcriptPath`: `...\brain\<subagent-conversationId>\.system_generated\logs\transcript.jsonl`.
     - `workspacePaths`:
       - When **`Workspace="inherit"`** (default, and required when using `tdq_team.py`'s `.tdq-worktrees/<slug>/<task>/`): `workspacePaths[0]` is the **MAIN REPOSITORY ROOT**, **NOT** `.tdq-worktrees/<slug>/<task>/`!
       - When **`Workspace="share"`** or **`"branch"`**: Antigravity creates its own separate git worktree/clone outside `.tdq-worktrees/`. **CRITICAL HAZARD:** Because `docs/tdq/state.json` and `docs/tdq/team/<slug>.json` are uncommitted during an active request, an Antigravity `"share"`/`"branch"` workspace **will NOT even have the live `state.json` or assignment map**, breaking all TDQ state/team hooks AND bypassing `tdq_team.py check/merge`! **Therefore, TDQ team mode MUST enforce `Workspace="inherit"` via `PreToolUse(invoke_subagent|swarm)` when `implement_mode == "subagent"`!**
     - **`agent_id` / `parentConversationId` / `agent_type`:** **DO NOT EXIST in Antigravity hook `stdin`!**

---

### 4.2 The 5 Severe Gate Failures Uncovered (All Empirically Verified)

#### Collision 1 (`EC-06`, P0): Missing `agent_id` Bypasses Pre-Implement Subagent Guards
- `edit_gate.py:103` (`state.json` write block) and `edit_gate.py:125` + `bash_gate.py:136` (pre-implement code edit block `[TDQ:TEAM]`) check `if payload.get("agent_id"):`.
- Because Antigravity never sends `agent_id`, a subagent invoked during `analyze`, `spec`, or `plan` has `payload.get("agent_id") == None`:
  - Editing `src/foo.py` → **ALLOWED** (`edgecase_test_results.json:186`).
  - Editing `docs/tdq/state.json` → **ALLOWED** with a mere reminder (`edgecase_test_results.json:188`).

#### Collision 2 (`EC-02`, P0 Upstream Bug): Missing `docs/workinglog/YYYY-MM-DD.md` Disables ALL Downstream Fences (`TDQ:TEAM`, `ngoai_vung_khai`, `TDQ:TICK`)!
- Look at `edit_gate.py:158-163` and `_common.py:206-215`:
  ```python
  # edit_gate.py:158
  if not os.path.isfile(os.path.join(cwd, log_rel)):
      remind(cwd, payload, "TDQ:LOG", [...])
  ```
  ```python
  # _common.py:206
  def remind(cwd, payload, code, lines, ...):
      if already_reminded(cwd, payload, code, rows=rows):
          sys.exit(0)   # <-- EXITS 0 SILENTLY ON EDIT #2..#N!
      ...
      sys.exit(0)       # <-- EXITS 0 WITH "allow" ON EDIT #1!
  ```
- **Consequence:** Until today's `docs/workinglog/YYYY-MM-DD.md` actually exists on disk, **every single call to `edit_gate.py` exits at line 159**, never reaching `canh_bao_lach_luat` (`line 182`), `ngoai_vung_khai` (`line 218`), or `TDQ:TICK` (`line 242`)! Proven in `edgecase_followup_results.json:14-16`.

#### Collision 3 (`EC-04`, P0 Upstream Bug): Marking `[>]` in `plan.md` Deadlocks Every Worker Inside `.tdq-worktrees/`!
- `tdq_state.py:1397-1402` (`IMPLEMENT_SUBAGENT_ROW`) instructs the leader:
  1. `tdq_team.py assign` (writes `docs/tdq/team/<slug>.json` with `"plan_sha": sha_file(plan)` and `"plan_assignment_sha": proj_sha`).
  2. `tdq_team.py audit` → `tdq_team.py wave` → `tdq_team.py open T1.1`.
  3. **Mark `[>]` on `T1.1` in `docs/tdq/plan/<slug>.md`** before spawning the subagent.
- Marking `[>]` changes the bytes of `plan/<slug>.md`, so `sha_file(plan)` changes!
- When the worker subagent (`Workspace="inherit"`, `cwd = <main_repo>`) calls `edit_file` on `<main_repo>/.tdq-worktrees/<slug>/t1.1/src/foo.py`:
  1. `edit_gate.py:170`: `trong_project = within(abs_target, os.path.realpath(cwd))` evaluates to **`True`** because `.tdq-worktrees/` is a subdirectory of `<main_repo>`!
  2. `edit_gate.py:182` calls `canh_bao_lach_luat(cwd, rel_target)`.
  3. `tdq_team.py:1615` checks `if ban_do.get("plan_sha") != sha_file(plan): return {"kieu": "chua-phan-cong", ...}` (someone updated `_boi_canh` at line 592 to use `kiem_tra_stale`, **but forgot line 1615**! And in `legacy-conservative` plans without explicit `- Cần:`, even `kiem_tra_stale` checks `plan_sha` at line 340!).
  4. `edit_gate.py:192` **HARD-BLOCKS THE WORKER** with:
     `[TDQ:TEAM] Team mode with no assignment map — you may not edit code on main first.` (`edgecase_followup_results.json:21`!)

#### Collision 4 (`EC-05`, P0): Accidental Main-Repo Edit Slips Past All 3 Fences!
- Suppose `plan_sha` matches (or is fixed) and `tdq_team.py open T1.1` has created branch `tdq/<slug>/t1.1` and `.tdq-worktrees/<slug>/t1.1/`, with `T1.1` marked `[>]` in `plan.md`.
- Because `Workspace="inherit"` gives the worker `cwd = <main_repo>`, suppose the worker (or the leader!) calls `edit_file(Path="<main_repo>/src/foo.py")` instead of `<main_repo>/.tdq-worktrees/<slug>/t1.1/src/foo.py`:
  1. **`canh_bao_lach_luat` (`tdq_team.py:1628`):** Checks `if _la_repo(cwd) and _co_nhanh(cwd, nhanh): return None`! Because branch `tdq/<slug>/t1.1` exists, it assumes the edit is fine and returns **`None`**!
  2. **`ngoai_vung_khai` (`tdq_team.py:1656`):** Checks if `abs_target` is inside `.tdq-worktrees/`. Because `<main_repo>/src/foo.py` is **not** inside `.tdq-worktrees/`, it returns **`None`**!
  3. **`TDQ:TICK` (`edit_gate.py:249-289`):** `in_worktree_doi` is `False`, `tick["has_doing"]` is **`True`** (because `tdq_state.py:821` defines `has_doing = dang > 0 or bool(da_giao)`!), `doing_count > 1` is `False` (`0 > 1`), and `doing_count == 1` is `False` (`0 == 1`) — so **every single `TDQ:TICK` branch is skipped**!
- **Result:** Editing `<main_repo>/src/foo.py` directly on `main` is **100% ALLOWED** (`edgecase_followup_results.json:24`), dirtying the main tree so `tdq_team.py merge T1.1` (`line 1302`) subsequently **refuses to merge**!

#### Collision 5 (`EC-03`, P0): `Stop` & `PreInvocation` Firing Inside Subagents
- When a `tdq-implementer` subagent finishes editing `.tdq-worktrees/<slug>/t1.1/src/foo.py` and stops its turn, `stop_gate.py` sees the edit in `.tdq-turn.jsonl` under `subagent_uuid` with no `docs/workinglog/` edit, and **blocks the subagent from stopping** (`[TDQ:LOG]`, `edgecase_test_results.json:200`)!
- When a read-only `research` or `tdq-reviewer` subagent stops during `implement` while tasks are `[ ]`, `stop_gate.py` sees `unfinished_reason` (`2 open task(s)`) and **blocks the read-only subagent from stopping for 3 full retry turns** (`[TDQ:UNFINISHED]`, `edgecase_test_results.json:201`)!

---

### 4.3 Deterministic Subagent Identity & Worktree Fence Architecture (`.tdq-sessions.json`)

Even though Antigravity hook `stdin` omits `agent_id`, **we can identify subagents with 100% determinism using two complementary signals**:

1. **Signal 1 — Transcript Step-0 Provenance (`transcriptPath` in Hook `stdin`):**
   - Verified across all 16 live `brain/*/transcript.jsonl` files:
     - In a **top-level human conversation** (`leader`), the first non-empty message step has `"source": "USER_EXPLICIT"` / `"type": "USER_INPUT"`.
     - In **every subagent conversation** (`invoke_subagent` or `swarm` worker), the conversation begins with `<subagent_reminder>` / `<SYSTEM_MESSAGE>` (`sender=<parent-uuid>`, no `USER_EXPLICIT` human step)!
2. **Signal 2 — `PreToolUse` Dispatch Registry (`docs/tdq/.tdq-runtime/sessions.json`):**
   - Hook `PreToolUse` on `invoke_subagent|swarm`:
     - Records the caller `conversationId` as a confirmed `leader` (or parent).
     - Parses `Prompt` / `brief` for `.tdq-worktrees/<slug>/<task>` or task code `T\d+\.\d+`, storing a pending dispatch `{parent_conv_id, type_name, role, task_id, worktree_root, ts}`.
     - Enforces: during `implement` (`implement_mode == "subagent"`), if `TypeName == "tdq-implementer"` and `Workspace in ("share", "branch")`, **block** with instruction to use `Workspace="inherit"` + `.tdq-worktrees/<slug>/<task>/`!
   - On a subagent's first `PreInvocation` / `PreToolUse`:
     - `_common.py` checks `transcriptPath` step 0 (cached per `conversationId` in `docs/tdq/.tdq-runtime/session-<convId>.json` so `transcript.jsonl` is read **at most once** per session, <1 ms!).
     - If subagent: sets `payload["agent_id"] = conversationId`, `payload["agent_type"] = role_or_type`, and binds `assigned_worktree` if matched!

**With `is_subagent` + `in_worktree_doi` known, the 4 Worktree Rules become airtight:**
1. **`in_worktree_doi` (`within(abs_target, join(cwd, ".tdq-worktrees"))`):**
   - **Skip `canh_bao_lach_luat`** completely (that fence is ONLY for edits outside `.tdq-worktrees/`, closing `EC-04`!).
   - **Enforce `ngoai_vung_khai(cwd, abs_target)`** (already works and proved in `edgecase_followup_results.json:23`!).
   - **Block leader from editing inside `.tdq-worktrees/`** (`if not is_subagent: block("TDQ:TEAM", "Leader may not edit inside .tdq-worktrees/...")`).
2. **Outside `.tdq-worktrees/` (`trong_project and not in_worktree_doi`) during `implement_mode == "subagent"`:**
   - **If `is_subagent`:** **ALWAYS BLOCK** (`src/*` on main repo is NEVER writable by a subagent in team mode — workers must write strictly inside `.tdq-worktrees/<slug>/<task>/` or `docs/tdq/research/`! Closes `EC-05`!).
   - **If `leader`:** In `canh_bao_lach_luat`, **remove** the `if _co_nhanh(cwd, nhanh): return None` loophole (`tdq_team.py:1628`)! Even after `tdq_team.py open T1.1` opens branch `tdq/<slug>/t1.1`, nobody may edit `src/foo.py` on the main checkout while `T1.1` is `giao`! And replace `ban_do.get("plan_sha") != sha_file(plan)` (`line 1615`) with a task-structure SHA that **always excludes checkbox state `[ ]/[~]/[>]/[x]`**!
3. **`Stop` Hook (`stop_gate.py`):**
   - If `is_subagent`: **exit 0 with `{}` immediately** (closes `EC-03`!).

---

## 5. Windows Encoding, NTFS Concurrency & `PreInvocation` Latency

### 5.1 Windows `cp1252` Encoding Findings (`Suite 1` + `Follow-up 1A/1B`)
- **Measured default under `cmd /c python` with `PYTHONIOENCODING` unset (`edgecase_followup_results.json:2`):**
  - `sys.stdin`: `encoding='cp1252'`, `errors='surrogateescape'`
  - `sys.stdout`: `encoding='cp1252'`, `errors='surrogateescape'`
  - `sys.stderr`: `encoding='cp1252'`, `errors='backslashreplace'`
- **3 Concrete Failures Proven:**
  1. **`codex_edit_gate.py:41-45, 188`:** Reconfigures `stdout` and `stderr` to UTF-8, **omitting `sys.stdin`**. When UTF-8 Vietnamese bytes (e.g., `'Đ'` = `0xc4 0x90`, `'ờ'` = `0xe1 0xbb 0x9d` — where `0x90` and `0x9d` are undefined in `cp1252`) enter `sys.stdin.read()`, Python decodes `0x90` via `surrogateescape` into lone surrogate `'\udc90'` (`'Ä\udc90'`). Any Vietnamese path in `TDQ_CODEX_VUNG` fails `pham_vung` comparison with mojibake!
  2. **`luat_gon.py:47, 52`:** Does not import `utf8_io`; printing Vietnamese warnings to `sys.stderr` produces corrupted output: `luat_gon: khng \u0111\u1ecdc \u0111\u01b0\u1ee3c thn lu\u1eadt` (`edgecase_followup_results.json:11`).
  3. **Any new Python hook without `utf8_io`:** `surrogateescape` on `cp1252` `stdout` only escapes `U+DC80..U+DCFF` — calling `print(json.dumps({"reason": "Chưa duyệt"}, ensure_ascii=False))` (`'ư'` = `U+01B0`, `'ệ'` = `U+1EC7`) **immediately crashes with uncaught `UnicodeEncodeError: 'charmap' codec can't encode character '\u01b0'`**!
- **Mandatory Rule for Port:** Every executable hook in `hooks/scripts/*.py` MUST import `utf8_io` (which reconfigures **all three** streams `sys.stdin`, `sys.stdout`, `sys.stderr` to `encoding="utf-8", errors="replace"`) on line 1 before reading stdin or importing anything else, AND `hooks.json` commands on Windows should invoke `python -X utf8 "<path>"`!

### 5.2 Parallel Tool Calls & Multi-Subagent NTFS Concurrency Races (`Suite 4`)
- **Empirical Stress Test (`edgecase_followup_results.json:27-33`):**
  - 8 parallel worker processes × 40 `turn_log_append` calls + periodic `turn_log_clear` on `.tdq-turn.jsonl` = **320 expected rows**.
  - **Actual surviving rows: `227` — `93` rows (`29.1%`) permanently lost!**
- **Root Causes:**
  1. `turn_log_clear` (`tdq_state.py:1875-1899`) reads the entire `.tdq-turn.jsonl`, filters out one session, and calls `_atomic_write` (`os.replace(tmp, path)`). Any `turn_log_append` written by another parallel tool call or subagent between `open("r")` and `os.replace()` is **wiped out**, AND on Windows NTFS `os.replace` raises `PermissionError: [WinError 5] Access is denied` / `[WinError 32]` whenever another process holds an open handle (silently swallowed by `except OSError: pass`)!
  2. `read_gate.py:_ghi_so` (`lines 94-109`) and `search_observe.py:ghi_so` (`lines 117-136`) truncate `.tdq-read.jsonl` (`TRAN_DONG=400`) and `.tdq-search.jsonl` (`TRAN_DONG=600`) **in-place with `open(duong, "w")`**, wiping parallel reads/searches that occurred during hook execution!
  3. `stop_gate.py` (`stop_streak.json`) and `agy_stop_gate.py` (`.agy-stop-snapshot.json`) use a **single repo-wide filename** instead of keying by `conversationId`.
- **Clean Architectural Fix (Zero Contention across Subagents + `msvcrt` Lock for Same-Session Parallel Tools):**
  1. **Shard per `conversationId`** under `docs/tdq/.tdq-runtime/`:
     - `turn-<convId>.jsonl` (eliminates 100% of cross-subagent `turn_log_clear` races — clearing a turn is now a single atomic file truncate/unlink for that `convId`!).
     - `read-<convId>.jsonl` (eliminates cross-subagent read-ledger races!).
     - `snap-<convId>.json` & `streak-<convId>.json` (eliminates `Stop` snapshot/streak clobbering!).
     - `pending-reminders-<convId>.jsonl` (spools `PreToolUse` `"allow"` reminders to next `PreInvocation`!).
  2. **Add a tiny cross-platform file lock (`with file_lock(lock_path):` using `msvcrt.locking` on `win32` / `fcntl.flock` on POSIX with 5ms backoff × 40 retries)** around same-session parallel tool appends (`read_file` × 5 in one model turn) and shared `.tdq-search.jsonl` / `sessions.json` writes!

### 5.3 `PreInvocation` Latency Benchmark (`Suite 4C`)
- Measured `tdq_state.repo_status_digest(TDQ_ROOT)` across 5 runs on Windows: **`167.28 ms` average** (`samples: 212.5, 155.7, 153.1, 156.2, 158.9 ms`), plus ~68 ms Python startup.
- Because Antigravity fires `PreInvocation` before **every model generation call** inside a turn (e.g., 15 tool calls = 15 `PreInvocation` firings), running `turn_snapshot` unconditionally on every `PreInvocation` adds **~2,509 ms + Python spawn overhead (~3.5s total)** per turn — AND worse, resetting `turn_snapshot` mid-turn would make `stop_gate.py` blind to edits made in steps 1..14!
- **Fix:** Store `{"last_user_input_sha": sha256(lastUserInput), "turn_active": True}` in `docs/tdq/.tdq-runtime/snap-<convId>.json` (cleared to `turn_active = False` when `stop_gate.py` allows stopping!).
  - On `PreInvocation` step 1 (`turn_active == False` or `last_user_input_sha` changed): run `turn_log_clear`, take `turn_snapshot`, emit `[TDQ:NEXT]`/`[TDQ:APPROVE]` (~220 ms once per user turn).
  - On `PreInvocation` steps 2..N (`turn_active == True` and same `last_user_input_sha`): **fast-path (<5 ms inside Python)** — ONLY drain and return `pending-reminders-<convId>.jsonl` (`[TDQ:DOC]`, `[TDQ:LOG]`, `[TDQ:RULE:*]`)!

---

## 6. `[TDQ:FEEDBACK]` Gate Requirement (`2026-11-11-1435-chan-tu-sua-khi-feedback.md`)

### 6.1 Root Cause Proven in Current `TDQ-Workflow` Codebase
Reading `docs/tdq/brief/2026-11-11-1435-chan-tu-sua-khi-feedback.md` alongside `soul.md` ("Phân loại feedback/bug — 3 mức") and `edit_gate.py:115-245` + `tdq_state.py:2942` exposed **why the agent repeatedly self-edited code on user bug feedback without permission**:

1. **Gap A (`no_state` / fresh workspace):** `edit_gate.py:115`: `if state is None or not state.get("active_request"): sys.exit(0)` — allows unlimited source edits when no TDQ request has ever been initialized!
2. **Gap B (Post-request `report` / `idle` approval carryover — THE BIG LOOPHOLE):**
   - When a request finishes, `tdq_state.py set phase=report` and `tdq_state.py set phase=idle` (`line 2942`) **keep `active_request`, `spec_approved: True`, `plan_approved: True` (or `quick_approved: True`) in `state.json`**!
   - When the user replies *"nút lưu bị lỗi rồi / có bug X"*, `edit_gate.py` runs:
     - `cong_dang_cho(state)` (`line 137`) returns **`None`** because `spec_approved`/`plan_approved`/`quick_approved` from the **already-finished** request are still `True`!
     - `effective_phase(state)` is `"report"` or `"idle"`, which is `not in ("implement", "qc")`, so `TDQ:TICK` (`line 242`) **also skips**!
     - Empirically proven in `edgecase_test_results.json:204-205`: `edit_gate.py` returned `"allow"` in `report` and silent `""` in `idle`!

### 6.2 Mechanical `[TDQ:FEEDBACK]` Gate Design for the Antigravity Port
Add a deterministic phase fence in **both `edit_gate.py` and `bash_gate.py`** whenever a project file outside `docs/` is targeted while `state` has an `active_request` AND `effective_phase(state) in ("idle", "report")` (unless an explicit Tier-`nhỏ` hotfix token was just recorded):

1. **Default Block (`[TDQ:FEEDBACK]`):**
   - In `edit_gate.py` (right after `TDQ:APPROVE` at line 156) and `bash_gate.py` (when `_shell_writes_outside_docs(cmd)` is `True`):
     - If `effective_phase(state) in ("idle", "report")` and not `has_valid_small_fix_token(cwd, session_id)`:
       - **BLOCK (`decision: "block"`)** with `[TDQ:FEEDBACK]`:
         > `"[TDQ:FEEDBACK] Phase is '{phase}' (previous request already finished implement/qc) — do NOT edit source code directly on feedback.\nClassify per 3-tier bug triage FIRST:\n• Tier Vừa/Lớn (>2 files, >15 LOC, logic/DB/API, or failed once) → present root cause + options via ask_question (or open new request / set phase=spec|analyze) and WAIT for user approval.\n• Tier Nhỏ (1-2 files, <=15 LOC, obvious typo/UI/config, no behavior change) → declare triage: python scripts/tdq_state.py hotfix --tier nho --files <f1,f2> --reason \"<1 line>\" (caps at 2 files in this turn)."`
2. **Bounded Tier-`nhỏ` Token (`tdq_state.py hotfix --tier nho --files <f1>[,<f2>] --reason ...`):**
   - Preserves `soul.md`'s 3-tier contract (*Tier `nhỏ`: <=2 files, <=15 LOC can fix + test immediately without nagging the user*), while making it **machine-auditable and strictly bounded**:
     - Rejects >2 files or rule/schema files;
     - `edit_gate.py` verifies `rel_target` is in the declared `hotfix_files` list (max 2 files) and `Replacement` delta is <=25 lines;
     - Automatically expires at turn end (`stop_gate.py` still enforces `[TDQ:LOG]` workinglog entry!).

---

## 7. Concrete Upgrades Required for `docs/AUDIT-AND-PORTING-PLAN.md`

To make the Antigravity port 100% bulletproof before implementation begins, update `docs/AUDIT-AND-PORTING-PLAN.md` with these 7 exact specifications:

1. **Update §3.2 Tool & Matcher Table (`hooks/hooks.json`):**
   - Invoke Python via `python -X utf8` (not bare `python3`, avoiding the Windows Store stub and guaranteeing UTF-8 stdio even before `utf8_io` loads).
   - **`PreToolUse` Matchers:**
     - `edit_gate.py`: `edit_file|write_file|create_file|replace_file_content|multi_replace_file_content`
     - `read_gate.py`: `read_file|view_file`
     - `bash_gate.py`: `run_command|manage_task`
     - `search_gate.py`: `run_command|grep_search|find_by_name|list_dir|search_directory|find_file|list_directory`
     - `lsp_gate.py`: `mcp_.*lsp_start_lsp|call_mcp_tool`
     - `ask_gate.py`: `ask_question`
     - `subagent_dispatch_gate.py` (new 40-line hook or inside `_common.py`): `invoke_subagent|swarm|define_subagent`
   - **`PostToolUse` Matchers:**
     - `search_observe.py`: `run_command|read_file|view_file|grep_search|find_by_name|list_dir|search_directory|find_file|list_directory|mcp_.*(lsp|graphify|txtai).*|call_mcp_tool`
   - **`PreInvocation` (`*`):** `prompt_context.py` (with leader/subagent split + step-1 vs step-2..N fast-path + one-time `session_start` warm-up without Claude/Codex cache sync).
   - **`Stop` (`*`):** `stop_gate.py` (outputs `{"decision": "continue", "reason": ...}`, immediate `{}` no-op for subagents!).

2. **Update §3.2 `_common.py` Adapter Specification:**
   - Unwrap `call_mcp_tool` (`ServerName` + `ToolName` + `Arguments` → synthetic `mcp_<ServerName>_<ToolName>` + `tool_input = Arguments`).
   - Fix `read_file` line math (`offset = StartLine or 1`, `limit = EndLine - offset + 1`, `ByteOffset > 0` → bypass duplicate-read warning).
   - Exclude `artifactDirectoryPath` and `<appDataDir>/brain/` paths from `observe("edit")`, `TDQ:LOG`, and `stop_gate.py`.
   - Fix `_common.py:remind()`: **do NOT `sys.exit(0)` inside `edit_gate.py` before `block()` checks** — queue reminders in memory during hook execution and only spool/flush after all `block()` fences pass!
   - Populate `payload["agent_id"]` for subagents via step-0 `transcriptPath` check + `docs/tdq/.tdq-runtime/sessions.json`.

3. **Update §5 Nhóm 4 (`agents/*.md` Frontmatter):**
   - Per `migrate-agent-settings/SKILL.md:154-161`, always set `subagent: true`, `mainAgent: false`, omit `model:`/`color:`, and **include `run_command` on `tdq-reviewer` and `tdq-security-reviewer`** (`tools: [read_file, run_command, send_message]`), because `grep_search`/`find_by_name`/`list_dir` do not exist in Antigravity 2.0! (Read-only safety for those two roles is mechanically enforced by `edit_gate.py` + `bash_gate.py` via `.tdq-runtime/sessions.json` blocking any mutating shell command from `agent_type in ("tdq-reviewer", "tdq-security-reviewer")`!)

4. **Update §5 Nhóm 2 (`scripts/tdq_team.py`, `scripts/tdq_transcript.py`, `scripts/search_rules.py`):**
   - `tdq_team.py:1615`: Replace `ban_do.get("plan_sha") != sha_file(plan)` with checkbox-insensitive task projection SHA, and remove `_co_nhanh` main-edit bypass at `line 1628`. Also accept English `- Deps:` alongside `- Cần:` at `line 54`.
   - `tdq_transcript.py`: `json.loads()` stringified values inside `transcript.jsonl` `tool_calls[*].args`.
   - `search_rules.py` & `bash_gate.py`: Add PowerShell `Get-ChildItem -Filter ... -Recurse` (`LOC_FILE`) and PowerShell file-write cmdlets (`Set-Content`, `Add-Content`, `Out-File`, `New-Item`, `Remove-Item`, `Move-Item`, `Copy-Item`).

5. **Shard Runtime Ledgers per `conversationId` + Windows `msvcrt.locking` (`EC-10`):**
   - Store session ledgers under `docs/tdq/.tdq-runtime/<kind>-<convId>.jsonl` and wrap shared JSONL/JSON writes with `msvcrt.locking` on Windows.

6. **Implement `[TDQ:FEEDBACK]` Mechanical Gate (`EC-08`):**
   - Block unapproved edits in `phase in ("idle", "report")` unless bounded `tdq_state.py hotfix --tier nho` token (<=2 files, <=25 lines) is active, and clear stale approval flags when closing to `idle` (or mark `request_closed: True`).
