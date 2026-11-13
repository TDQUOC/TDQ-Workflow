# Exhaustive Rescan 03: `skills/**`, `agents/**`, Hidden Adapter Directories, and Host Tool/Shell/Syntax Mapping (`TDQ-Workflow v0.97.0` -> Antigravity)

- **Source Repo Scanned (Read-Only):** `C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow` (`v0.97.0`, branch `main`)
- **Baseline Plan Compared Against:** [AUDIT-AND-PORTING-PLAN.md](file:///c:/Users/admin/Documents/Projects/TDQ-Workflow-Antigravity/docs/AUDIT-AND-PORTING-PLAN.md) (plus [02-pipeline-skills-agents-audit.md](file:///c:/Users/admin/Documents/Projects/TDQ-Workflow-Antigravity/docs/research/02-pipeline-skills-agents-audit.md) and [04-antigravity-adapter-audit.md](file:///c:/Users/admin/Documents/Projects/TDQ-Workflow-Antigravity/docs/research/04-antigravity-adapter-audit.md))
- **Scan Scope:** Every single file recursively inside `skills/` (**74 files**), `portable_src/` (**1 file**), `agents/` (**6 files**), `.agents/` (**1 file**), `.claude/` (**2 config files + 4 worktree dirs**), `.claude-plugin/` (**2 files**), `.codex/` (**2 files**), `.codex-plugin/` (**1 file**), `.opencode/` (**2 files**), `.remember/` (**259 files**), `.taskmaster/` (**4 files**), `claude-export/` (**5 files**), `docs/claude-md-mau.md` (**1 file**), and root configs (`.env.example`, `pyrightconfig.json`, `.gitignore`, `.gitattributes`, `.graphifyignore`, `README.md`), cross-checked against `scripts/build_portable.py`, `scripts/tdq_ten_lenh.py`, `scripts/tdq_codex_mcp.py`, `scripts/tdq_setup.py`, and `scripts/tdq_checkportable.py`.

---

## 1. Delta Analysis vs. Existing `docs/AUDIT-AND-PORTING-PLAN.md`

Comparing this file-by-file rescan against [AUDIT-AND-PORTING-PLAN.md](file:///c:/Users/admin/Documents/Projects/TDQ-Workflow-Antigravity/docs/AUDIT-AND-PORTING-PLAN.md) confirmed the core architectural gaps already documented AND uncovered **12 concrete new findings / precision corrections** that must be incorporated into the porting implementation:

| # | Area | What `AUDIT-AND-PORTING-PLAN.md` Said | New / Corrected Evidence from Full Rescan |
|---|---|---|---|
| **D1** | **What `build_portable.py --sinh-agy` rewrites today** | Noted path mangling & missing agents/skills/hooks/MCP. | **Verified exact rewrite surface (`scripts/build_portable.py:678-804`):** `--sinh-agy` rewrites **ONLY 2 regex patterns** in `skills/**/*.md`: (1) `${CLAUDE_PLUGIN_ROOT}` / `$CLAUDE_PLUGIN_ROOT` -> raw `goc_cai` (producing mixed backslash/slash paths `C:\Users\admin\.gemini\config\plugins\tdq-workflow/scripts/...`), and (2) bare `\b(scripts/\|hooks/)` -> `<goc_cai>/scripts/...` (which **corrupts prose and example filenames** like `scripts/alpha.py` in `team-mode.md:131`, `scripts/a.py` in `team-mode-tra-cuu.md:58`, `scripts/scan.py` in `rules/index.md:74`). It rewrites **0 tool names, 0 `mcp__*` identifiers, 0 model names, 0 `python3` invocations in skills, 0 slash commands, and 0 shell continuations/operators**. |
| **D2** | **`python3` on Windows (`CreateProcessW` trap)** | Stated "`python3` resolves to Microsoft Store stub on Windows (357 occurrences across skills/docs)". | **Two crucial corrections:** (1) Exact counts: **`128` occurrences across `39` skill files** (`125` in `skills/**` + `3` in `portable_src/skills/tdq-checkportable/SKILL.md`), `265` in `scripts/`, `48` in `hooks/`, `179` in `tests/`, `18` in `README.md`, `2` in `.codex/hooks.json` (plus `7,784` in `docs/`). (2) **Empirical Windows trap:** On this machine `C:\Users\admin\.gemini\antigravity\bin\python3.cmd` (`@py -3 %*`) makes `python3` work inside interactive PowerShell (`PATHEXT` includes `.CMD`), **HOWEVER** Python `subprocess.run(["python3", ...], shell=False)` calls Win32 `CreateProcessW`, which **ignores `.cmd` shims** and falls straight through to `C:\Users\admin\AppData\Local\Microsoft\WindowsApps\python3.exe` -> **`rc=9009: Python was not found`**! And on fresh Windows machines without `python3.cmd`, even PowerShell fails with exit `49`/`9009`. Note also `python ` (without `3`) in `runtime-speed.md:18` and `mcp-first-guide.md:47`. |
| **D3** | **Backslash `\` multi-line continuations in skill code blocks** | **Not documented** in `AUDIT-AND-PORTING-PLAN.md`. | **12 lines across 3 skill files** (`vision-test-loop.md:87-94`, `tdq-plan/SKILL.md:32`, `tdq-setup/SKILL.md:110-112`) end with POSIX `\` line continuations inside fenced blocks. In Windows PowerShell 5.1 (`run_command`), `\` is **NOT** a line continuation (PowerShell uses backtick `` ` ``) — PowerShell passes literal `"\"` to `argparse` and aborts! |
| **D4** | **Inline POSIX env assignment + `/tmp/...` + `\|\|`** | Partially noted (`&&`/`\|\|`), missed inline `VAR=val cmd` in conventions & plan template. | `skills/tdq-conventions/SKILL.md:102` (`put TDQ_PROJECT_DIR=/tmp/... on that very command (no \|\| fallback)`) and `skills/tdq-plan/references/plan-template.md:36` (`phải có TDQ_PROJECT_DIR=<thư mục tạm> ngay trên chính lệnh đó`) mandate **POSIX inline env prefixing (`VAR=val cmd`)**, which throws a `CommandNotFoundException` in Windows PowerShell (`$env:TDQ_PROJECT_DIR='...'; py -3 ...` is required, and `/tmp` does not exist on Windows). |
| **D5** | **Legacy `Task` tool name for subagents** | Documented `Agent` tool (`subagent-tuning.md`), missed `Task` tool in `tdq-build/SKILL.md`. | `skills/tdq-build/SKILL.md:86` explicitly instructs: *"Call `tdq-implementer` for EVERY task of the wave IN ONE response — several **Task** calls in one response"*. `Task` was Claude Code's pre-`Agent` subagent dispatch tool; on Antigravity it is `invoke_subagent`. |
| **D6** | **Exact `mcp__*` count & Chrome DevTools plugin collision** | Cited "`mcp__lsp__*` (18 occurrences)". | **Exact count across `skills/` + `agents/` + `docs/claude-md-mau.md` is `40` occurrences across `39` lines in `14` files:** **`19` `mcp__lsp__*`** (`17` in `skills/`, `1` in `agents/tdq-refactor-cleaner.md:20`, `1` in `docs/claude-md-mau.md:58`) + **`20` `mcp__chrome-devtools__*`** + **`1` `mcp__chrome_devtools__*`** (`chrome-devtools-mcp-guide.md:31`). On Antigravity, eager MCP tools use **single underscores** (`mcp_<serverName>_<toolName>`, e.g., `mcp_lsp_find_references`), AND Antigravity already ships an official `chrome-devtools-plugin` (`C:\Users\admin\.gemini\config\plugins\chrome-devtools-plugin`) whose skills refer to bare tool names (`navigate_page`, `take_snapshot`, etc.) or `browser` subagent! |
| **D7** | **Slash commands (`/tdq:*` vs `/tdq-*` vs `tdq-workflow:*` vs host commands)** | Mentioned `/tdq-intake`, `/mcp`, `/skills` in `README_AGY`. | Verified **0 occurrences of `/tdq:*`** (`slash_tdq_colon = 0`) anywhere in the repo (TDQ already migrated phase commands to 11 hyphenated skills linked via Markdown `[tdq-spec](../tdq-spec/SKILL.md)` — 63 occurrences). **HOWEVER:** (1) Claude's `tdq-workflow:tdq-intake` namespace prefix survives in **3 places** (`docs/claude-md-mau.md:70`, `scripts/tdq_setup.py:1110`, `hooks/scripts/prompt_context.py:271`); (2) non-existent Antigravity slash commands appear in skills: `/mcp` (`tdq-intake/SKILL.md:54`, `kiem-lsp-hieu-ung.md:60`), `/code-review` (`plugin-routing.md:24`), `/hooks` (`uu-tien-tim-kiem.md:148`). Only `/goal` (`tdq-build/SKILL.md:21`) exists natively on Antigravity! |
| **D8** | **`.claude/rules/` vs actual rule locations** | Mentioned generating `.agent/rules/tdq-workflow.md`. | Confirmed `.claude/rules/` **does NOT exist** in `TDQ-Workflow`. Instead, always-on rules live in `docs/claude-md-mau.md` (`<!-- TDQ:TOOLS -->` block, mirrored verbatim in `scripts/tdq_setup.py:1090-1140`), while language coding rules live on-demand inside `skills/tdq-build/references/rules/` (`10` `.md` files + `2` `cookbooks/*.md`), where `rules/index.md:46` and `rules/them-ngon-ngu.md:48,56` hardcode `~/.claude/skills/tdq-rules/`! |
| **D9** | **74th non-Markdown file in `skills/`: `handoff-schema.json`** | Cited "11 skills + 62 reference `.md` files". | `skills/` actually contains **74 files**: `11` `SKILL.md` + `62` `references/**/*.md` + **`1` JSON schema `skills/tdq-conventions/references/handoff-schema.json`** (50 lines, defining `TDQ_HANDOFF_PAYLOAD` referenced by `agents/tdq-build-resolver.md:30`). Any file copier or `doc_lint` rule filtering `*.md` only will skip `handoff-schema.json` unless non-`.md` assets are preserved! |
| **D10** | **Agent filenames & frontmatter specifics (`v0.97.0`)** | Noted 6 agents, `haiku`, `effort`, comma-string `tools:`. | Verified all 6 exact filenames (`tdq-build-resolver.md`, `tdq-implementer.md`, `tdq-qc-tester.md`, `tdq-refactor-cleaner.md`, `tdq-reviewer.md`, `tdq-security-reviewer.md` — note `tdq-implementer.md`, NOT `implementer.md`; **0** `color:` fields). **3 agents omit `tools:` completely** (`tdq-implementer`, `tdq-build-resolver`, `tdq-refactor-cleaner`), while **3 agents use a comma-separated string** (`tools: Bash, Read, Grep, Glob` or `tools: Read, Grep, Glob`) instead of Antigravity's `EnableWriteTools` / `EnableMCPTools` boolean schema or YAML list. |
| **D11** | **`.opencode/plugins/tdq-workflow.js` adapter lesson** | Only briefly mentioned `.opencode/`. | `.opencode/plugins/tdq-workflow.js` (204 lines) reveals how TDQ solved a host **without Claude hooks**: it dynamically scans `skills/` (`fs.readdirSync`) and injects a compact `<TDQ_WORKFLOW>` bootstrap block on the first turn (`ctx.session.hook('context', ...)`), explicitly documenting (`lines 16-24`) that hijacking `chat.SystemPrompt` broke model routing on OpenCode. For Antigravity, `.agent/rules/tdq-workflow.md` (`activation: always_on`) is the clean, native equivalent! |
| **D12** | **Hidden repo directories (`.remember/`, `.taskmaster/`, `.claude/worktrees/`, `claude-export/`)** | Not inventoried in detail. | `.remember/` (259 files — third-party `remember` memory plugin logs/state) and `.taskmaster/` (4 files — Task Master AI config + PRD templates) + `.env.example` (TaskMaster API key placeholders + `ARCHIFY_ROOT`) are **author-local dev artifacts**, NOT TDQ runtime code — **except** `skills/tdq-conventions/SKILL.md:160-161` and `docs/claude-md-mau.md:50-53` hardcode calling external skill `mem0-memory`, which is absent on Antigravity! Also `.claude/worktrees/agent-a37e138360abceb26/...` already exceeds Windows 260-char `MAX_PATH` (`WinError 3`)! |

---

## 2. Complete Recursive Inventory (`skills/`, `portable_src/`, `agents/`, Adapter & Root Configs)

### 2.1 `skills/` (74 Files Total: 11 `SKILL.md` + 62 `references/**/*.md` + 1 `.json`; 0 `templates/`, 0 `scripts/`, 0 `assets/` Subdirs) & `portable_src/` (1 File)

> **Structural note:** Templates in TDQ-Workflow (`spec-template.md`, `plan-template.md`, `report-template.md`, `knowledge-template.md`) live inside each skill's `references/` folder rather than a separate `templates/` subdirectory. Currently `build_portable.py --sinh-agy` (`SKILLS_AGY`, lines 666–676) copies **8** of the 11 `skills/` directories + `portable_src/skills/tdq-checkportable` = **9 skills**, **omitting `tdq-browser-research` (1 file) and `tdq-browser-test` (1 file)**.

| # | Relative File Path | Lines | Bytes | Copied by `--sinh-agy` Today? |
|---|---|---:|---:|---|
| 1 | `skills/tdq-browser-research/SKILL.md` | 51 | 2,864 | **NO (DROPPED)** |
| 2 | `skills/tdq-browser-test/SKILL.md` | 77 | 3,993 | **NO (DROPPED)** |
| 3 | `skills/tdq-build/SKILL.md` | 171 | 14,542 | Yes |
| 4 | `skills/tdq-build/references/archify-lifecycle.md` | 33 | 4,196 | Yes |
| 5 | `skills/tdq-build/references/codex-mode.md` | 173 | 8,950 | Yes |
| 6 | `skills/tdq-build/references/qc.md` | 195 | 12,037 | Yes |
| 7 | `skills/tdq-build/references/report-template.md` | 155 | 9,908 | Yes |
| 8 | `skills/tdq-build/references/runtime-speed.md` | 82 | 5,710 | Yes |
| 9 | `skills/tdq-build/references/skill-eval.md` | 99 | 5,637 | Yes |
| 10 | `skills/tdq-build/references/team-mode-tra-cuu.md` | 65 | 4,050 | Yes |
| 11 | `skills/tdq-build/references/team-mode.md` | 181 | 11,498 | Yes |
| 12 | `skills/tdq-build/references/vision-test-loop.md` | 152 | 12,869 | Yes |
| 13 | `skills/tdq-build/references/rules/chung.md` | 233 | 12,348 | Yes |
| 14 | `skills/tdq-build/references/rules/cpp.md` | 69 | 3,311 | Yes |
| 15 | `skills/tdq-build/references/rules/csharp.md` | 68 | 3,150 | Yes |
| 16 | `skills/tdq-build/references/rules/go.md` | 72 | 3,286 | Yes |
| 17 | `skills/tdq-build/references/rules/html.md` | 66 | 3,272 | Yes |
| 18 | `skills/tdq-build/references/rules/index.md` | 76 | 3,634 | Yes |
| 19 | `skills/tdq-build/references/rules/python.md` | 70 | 3,030 | Yes |
| 20 | `skills/tdq-build/references/rules/rust.md` | 66 | 3,089 | Yes |
| 21 | `skills/tdq-build/references/rules/them-ngon-ngu.md` | 66 | 3,311 | Yes |
| 22 | `skills/tdq-build/references/rules/typescript-js.md` | 68 | 3,402 | Yes |
| 23 | `skills/tdq-build/references/rules/cookbooks/python-cookbook.md` | 146 | 5,252 | Yes |
| 24 | `skills/tdq-build/references/rules/cookbooks/typescript-js-cookbook.md` | 144 | 4,762 | Yes |
| 25 | `skills/tdq-check-status/SKILL.md` | 71 | 4,633 | Yes |
| 26 | `skills/tdq-check-status/references/bang-lech.md` | 54 | 5,793 | Yes |
| 27 | `skills/tdq-check-status/references/report-template.md` | 72 | 3,621 | Yes |
| 28 | `skills/tdq-conventions/SKILL.md` | 209 | 15,976 | Yes |
| 29 | `skills/tdq-conventions/references/approval.md` | 76 | 4,608 | Yes |
| 30 | `skills/tdq-conventions/references/clean-code.md` | 121 | 7,016 | Yes |
| 31 | `skills/tdq-conventions/references/context-budget.md` | 131 | 7,980 | Yes |
| 32 | `skills/tdq-conventions/references/handoff-schema.json` | 50 | 1,369 | Yes (via `copytree`, skipped by `.md` rewriter) |
| 33 | `skills/tdq-conventions/references/knowledge-template.md` | 58 | 2,892 | Yes |
| 34 | `skills/tdq-conventions/references/measure-scenario.md` | 40 | 2,114 | Yes |
| 35 | `skills/tdq-conventions/references/phases.md` | 37 | 6,511 | Yes |
| 36 | `skills/tdq-conventions/references/plugin-routing.md` | 105 | 6,577 | Yes |
| 37 | `skills/tdq-conventions/references/reminder-codes.md` | 86 | 6,604 | Yes |
| 38 | `skills/tdq-conventions/references/soul.md` | 146 | 8,296 | Yes |
| 39 | `skills/tdq-conventions/references/subagent-tuning.md` | 69 | 4,086 | Yes |
| 40 | `skills/tdq-conventions/references/tavily.md` | 29 | 1,983 | Yes |
| 41 | `skills/tdq-conventions/references/ultracode.md` | 63 | 3,505 | Yes |
| 42 | `skills/tdq-conventions/references/user-facing-block-vi-du.md` | 76 | 3,045 | Yes |
| 43 | `skills/tdq-conventions/references/user-facing-block.md` | 132 | 8,739 | Yes |
| 44 | `skills/tdq-conventions/references/worklog-images.md` | 21 | 1,145 | Yes |
| 45 | `skills/tdq-intake/SKILL.md` | 148 | 11,680 | Yes |
| 46 | `skills/tdq-intake/references/analyze-full.md` | 131 | 9,877 | Yes |
| 47 | `skills/tdq-intake/references/archify-quick.md` | 18 | 2,124 | Yes |
| 48 | `skills/tdq-intake/references/interview.md` | 120 | 5,823 | Yes |
| 49 | `skills/tdq-intake/references/issue-triage.md` | 31 | 1,855 | Yes |
| 50 | `skills/tdq-intake/references/kiem-lsp-hieu-ung.md` | 64 | 4,368 | Yes |
| 51 | `skills/tdq-intake/references/lane-decision.md` | 77 | 3,902 | Yes |
| 52 | `skills/tdq-intake/references/nhanh-request.md` | 55 | 2,888 | Yes |
| 53 | `skills/tdq-intake/references/quick-lane-mini.md` | 47 | 1,726 | Yes |
| 54 | `skills/tdq-intake/references/quick-lane-qc.md` | 85 | 4,751 | Yes |
| 55 | `skills/tdq-intake/references/quick-lane.md` | 124 | 9,640 | Yes |
| 56 | `skills/tdq-intake/references/scope-round.md` | 139 | 7,417 | Yes |
| 57 | `skills/tdq-intake/references/skill-inventory.md` | 80 | 4,831 | Yes |
| 58 | `skills/tdq-lean/SKILL.md` | 75 | 3,865 | Yes |
| 59 | `skills/tdq-plan/SKILL.md` | 121 | 8,909 | Yes |
| 60 | `skills/tdq-plan/references/mode-gate.md` | 159 | 9,331 | Yes |
| 61 | `skills/tdq-plan/references/plan-template-co-che.md` | 99 | 6,576 | Yes |
| 62 | `skills/tdq-plan/references/plan-template-huong-dan.md` | 53 | 4,251 | Yes |
| 63 | `skills/tdq-plan/references/plan-template.md` | 113 | 6,888 | Yes |
| 64 | `skills/tdq-setup/SKILL.md` | 132 | 9,103 | Yes |
| 65 | `skills/tdq-setup/references/chrome-devtools-mcp-guide.md` | 49 | 1,893 | Yes |
| 66 | `skills/tdq-setup/references/languages.md` | 62 | 4,516 | Yes |
| 67 | `skills/tdq-setup/references/mcp-first-guide.md` | 61 | 4,393 | Yes |
| 68 | `skills/tdq-setup/references/uu-tien-tim-kiem-chi-tiet.md` | 81 | 4,783 | Yes |
| 69 | `skills/tdq-setup/references/uu-tien-tim-kiem.md` | 159 | 11,697 | Yes |
| 70 | `skills/tdq-spec/SKILL.md` | 97 | 5,928 | Yes |
| 71 | `skills/tdq-spec/references/archify-ba.md` | 48 | 4,928 | Yes |
| 72 | `skills/tdq-spec/references/spec-template-huong-dan.md` | 99 | 7,831 | Yes |
| 73 | `skills/tdq-spec/references/spec-template.md` | 156 | 7,308 | Yes |
| 74 | `skills/tdq-status/SKILL.md` | 55 | 3,308 | Yes |
| P1 | `portable_src/skills/tdq-checkportable/SKILL.md` | 64 | 3,388 | Yes (`skills/tdq-checkportable/SKILL.md`) |

### 2.2 `agents/` (6 Files Total — **ALL 6 DROPPED** by `--sinh-agy` Today)

| # | Relative File Path | Lines | Bytes | `model:` | `effort:` | `tools:` Frontmatter | `color:` | Copied by `--sinh-agy`? |
|---|---|---:|---:|---|---|---|---|---|
| 1 | `agents/tdq-build-resolver.md` | 44 | 1,753 | `inherit` | `high` | *(omitted)* | *(none)* | **NO (DROPPED)** |
| 2 | `agents/tdq-implementer.md` | 70 | 5,870 | **`haiku`** | `medium` | *(omitted)* | *(none)* | **NO (DROPPED)** |
| 3 | `agents/tdq-qc-tester.md` | 31 | 1,967 | `inherit` | `high` | `Bash, Read, Grep, Glob` | *(none)* | **NO (DROPPED)** |
| 4 | `agents/tdq-refactor-cleaner.md` | 41 | 1,696 | `inherit` | `high` | *(omitted)* | *(none)* | **NO (DROPPED)** |
| 5 | `agents/tdq-reviewer.md` | 36 | 2,503 | `inherit` | `high` | `Read, Grep, Glob` | *(none)* | **NO (DROPPED)** |
| 6 | `agents/tdq-security-reviewer.md` | 52 | 2,495 | `inherit` | `high` | `Read, Grep, Glob` | *(none)* | **NO (DROPPED)** |

### 2.3 Adapter Directories, Hidden State Directories, and Root Config Files

| Directory / File | Exact Files (Lines / Bytes) | Structure, Purpose & Porting Implications |
|---|---|---|
| **`.agents/`** | `.agents/plugins/marketplace.json` (`20L`, `375B`) | Codex / multi-agent local marketplace catalog (`name: "tdq-local"`, `source: "local"`, `path: "./"`, `category: "Productivity"`). Note: Antigravity uses `.agent/` (singular) at workspace root for `rules/`, `skills/`, `agents/`, `hooks.json`! |
| **`.claude/`** | `.claude/settings.json` (`9L`, `193B`); `.claude/settings.local.json` (`5L`, `52B`); `.claude/worktrees/` (4 stale worktrees: `agent-a37e138360abceb26`, `agent-a382d2d7ee2734e74`, `agent-a45a16c73f42c0ad5`, `agent-ae5d0573024c25afd`) | **No `.claude/rules/` exists!** `.claude/settings.json` only sets `env`: `TDQ_SEARCH_WINDOW_SEC=45`, `TDQ_SEARCH_GREP_QUOTA=2`, `TDQ_SEARCH_BASH_QUOTA=2` (because hooks live in `hooks/hooks.json` via plugin discovery). `.claude/worktrees/agent-a37e138360abceb26` exceeds Windows `260`-char `MAX_PATH` (`WinError 3`) — any recursive walker without directory pruning crashes on it! |
| **`.claude-plugin/`** | `.claude-plugin/plugin.json` (`32L`, `1,335B`); `.claude-plugin/marketplace.json` (`13L`, `314B`) | `plugin.json` declares `name: "tdq-workflow"`, `version: "0.97.0"`, and `userConfig` (`TAVILY_API_KEY`, `TAVILY_API_KEY_BACKUP` `sensitive: true`, `ENABLE_DEVTOOL_MCP`). **Antigravity's plugin loader requires `.claude-plugin/plugin.json` or `.gemini-plugin/plugin.json` — `--sinh-agy` currently generates NEITHER!** |
| **`.codex/`** | `.codex/config.toml` (`9L`, `221B`); `.codex/hooks.json` (`25L`, `867B`) | `config.toml` sets `[shell_environment_policy.set]` `TDQ_SEARCH_*` quotas. `.codex/hooks.json` wires `PreToolUse` on `apply_patch` and `Bash` to `python3 hooks/scripts/codex_edit_gate.py`. Note: `codex_edit_gate.py` parses Codex's `*** Begin Patch` format, whereas Antigravity `PreToolUse` hooks follow Claude's JSON stdin/stdout protocol (`tool_name`, `tool_input`, `hookSpecificOutput.permissionDecision`), only needing tool-name aliases (`run_command`, `edit_file`, `write_file`, `grep_search`, `find_by_name`). |
| **`.codex-plugin/`** | `.codex-plugin/plugin.json` (`32L`, `1,066B`) | Codex plugin manifest (`v0.97.0`, `"skills": "./skills/"`, `"hooks": {}`, `interface` metadata). Note `"hooks": {}` is empty in `.codex-plugin/plugin.json` because Codex project hooks load from `.codex/hooks.json` instead. |
| **`.opencode/`** | `.opencode/INSTALL.md` (`47L`, `1,945B`); `.opencode/plugins/tdq-workflow.js` (`204L`, `7,399B`) | JS plugin for OpenCode (`v0.1+`). Dynamically enumerates `../../skills/*/SKILL.md` (`readSkillFrontmatter`) so new skills (`tdq-browser-*`, `tdq-lean`, etc.) are never missed, and prepends `<TDQ_WORKFLOW>` bootstrap context onto the first user message per session because OpenCode lacks Claude `SessionStart`/`UserPromptSubmit` hooks and mutating `SystemPrompt` broke provider routing. |
| **`.remember/`** | `259` files (`archive.md`, `now.md`, `recent.md`, `today-*.md`, `logs/*.log`, `logs/autonomous/*.log`, `tmp/*`) | **External third-party plugin state** (`remember` autonomous session-memory plugin used by the repo author). Git-ignored/local state; **must NOT be copied** into any Antigravity bundle (`EXCLUDE_DIRS` should exclude `.remember`). |
| **`.taskmaster/`** | `config.json` (`43L`), `state.json` (`6L`), `templates/example_prd.txt` (`47L`), `templates/example_prd_rpg.txt` (`511L`) | **External third-party tool config** (`Task Master AI` / `claude-code` provider config). Author-local dev scaffolding, **NOT** used by any TDQ skill/script/hook; exclude from Antigravity bundle. |
| **`claude-export/`** | `EXPORT_LOG.md` (`22L`), `INSTRUCTIONS.md` (`84L`), `MANIFEST.template.json` (`10L`), `README.template.md` (`142L`), `local-repos.json` (`4L`) | Internal export/archive templates for moving Claude Code sessions/artifacts across repos. Not part of TDQ plugin runtime. |
| **`.env.example`** | `22L` (`801B`) | Contains placeholder keys (`ANTHROPIC_API_KEY`, `PERPLEXITY_API_KEY`, `OPENAI_API_KEY`, etc.) for TaskMaster + `ARCHIFY_ROOT=""` (the **only** TDQ-relevant env var in `.env.example`, used by `scripts/tdq_archify.py`). No real secrets present. |
| **`pyrightconfig.json`** | `10L` (`201B`) | Configures Pyright (`include: ["scripts", "hooks/scripts", "tests"]`, `extraPaths: ["scripts", "hooks/scripts"]`, `pythonVersion: "3.11"`). Explains why `agent-lsp` + `pyright-langserver` resolves cross-imports like `import utf8_io` inside `scripts/` and `hooks/scripts/`. |
| **`docs/claude-md-mau.md`** | `104L` (`8,799B`) | Canonical `CLAUDE.md` template containing the `<!-- TDQ:TOOLS -->` block (`lines 62–79`, duplicated in `scripts/tdq_setup.py:1090-1140`) that enforces TDQ intake routing, 3-layer triangulation, chat-only gates (banning `AskUserQuestion`, `EnterPlanMode`, `ExitPlanMode`), and `Unknown skill` fallback. **Must be ported into `.agent/rules/tdq-workflow.md` (`activation: always_on`) for Antigravity!** |

---

## 3. Deep Scan Findings by Category

### 3.A Claude Tool Names vs. Antigravity Tool Names (`skills/**`, `portable_src/**`, `agents/**`, `docs/claude-md-mau.md`)

**Does `build_portable.py --sinh-agy` rewrite ANY tool names today? NO (`0` rewrites).**

Every occurrence of Claude-specific tools across the 82 target files (`74` `skills/` + `1` `portable_src/` + `6` `agents/` + `1` `docs/claude-md-mau.md`):

| Claude Identifier Scanned | Occurrences / Lines / Files | Exact `file:line` Locations | Antigravity Equivalent & Impact |
|---|---:|---|---|
| `AskUserQuestion` | **3** occ / 3 lines / 3 files | `skills/tdq-conventions/references/user-facing-block.md:103`, `skills/tdq-intake/references/interview.md:50`, `docs/claude-md-mau.md:76` | **`ask_question`**. **CRITICAL:** TDQ *bans* popup question tools so users can answer multi-question gates in chat (`1a 2b 3c`). If the rule only bans `AskUserQuestion`, Antigravity's model will call its native `ask_question` UI popup! Must ban **both** `ask_question` and `AskUserQuestion`. |
| `TodoWrite` | **0** | *(none)* | N/A (TDQ uses `docs/tdq/plan/<slug>.md` checkboxes instead). |
| `TaskCreate` / `TaskUpdate` / `TaskList` | **0** | *(none)* | N/A (`manage_task` on Antigravity is for background shell/timer tasks). |
| `EnterPlanMode` / `ExitPlanMode` | **5** occ / 4 lines / 2 files | `skills/tdq-conventions/references/approval.md:48,50` (`EnterPlanMode`), `docs/claude-md-mau.md:70,75` (`EnterPlanMode`, `ExitPlanMode`) | Antigravity uses `/plan` slash mode & artifact `RequestFeedback: true` ("Proceed" button). Must translate to: *"Never switch to `/plan` mode or emit an executable plan artifact with `RequestFeedback: true`; present plans in `docs/tdq/plan/<slug>.md` + chat summary."* |
| `Agent` tool / `Task` tool / `subagent_type` | **4** occ / 4 lines / 2 files | `skills/tdq-build/SKILL.md:86` (`several Task calls`), `skills/tdq-conventions/references/subagent-tuning.md:10,11,31,68` (`the Agent tool`); `subagent_type`: **0** | **`invoke_subagent`** (`TypeName`, `Role`, `Prompt`, `Model`, `Workspace: "inherit"\|"branch"\|"share"`). Also **CRITICAL on Antigravity**: subagents MUST call `send_message(Recipient="<parent_id>", Message=...)` because plain text output is NOT relayed back to the parent! |
| `TeamCreate` / `SendMessage` | **0** | *(none in Claude spelling)* | Note: While Claude's `SendMessage` is absent, Antigravity **requires** `send_message` in every subagent (`agents/tdq-*.md`) AND alternatively offers native `swarm` (`workspace: "share"`). |
| `Skill(` | **0** (`Skill` noun: 3 lines) | `skills/tdq-conventions/SKILL.md:161` (`Skill mem0-memory`), `skills/tdq-build/references/qc.md:115`, `skill-eval.md:1` | Antigravity loads skills by reading their `SKILL.md` via `read_file` from `<skills>` list. **Warning:** `mem0-memory` (`tdq-conventions/SKILL.md:160-161`, `docs/claude-md-mau.md:50-53`) does NOT exist on Antigravity — must mark optional (`if installed`). |
| `WebSearch` / `WebFetch` | **3** occ / 2 lines / 2 files | `skills/tdq-conventions/references/tavily.md:5` (`WebSearch`, `WebFetch`), `skills/tdq-intake/references/analyze-full.md:72` (`WebFetch`) | **`search_web`** (built-in search) / `read_url_content` or `run_command` / `browser` subagent (for JS-rendered pages). |
| `NotebookEdit` / `MultiEdit` | **0** | *(none)* | N/A. |
| `mcp__lsp__*` | **19** occ / 19 lines / 11 files | `skills/tdq-build/SKILL.md:69,120`, `skills/tdq-build/references/rules/chung.md:81`, `skills/tdq-conventions/references/reminder-codes.md:25,46`, `skills/tdq-intake/references/analyze-full.md:41`, `skills/tdq-plan/SKILL.md:58`, `skills/tdq-setup/SKILL.md:56,118,120`, `skills/tdq-setup/references/uu-tien-tim-kiem-chi-tiet.md:36,44`, `skills/tdq-setup/references/uu-tien-tim-kiem.md:27,39,72`, `skills/tdq-spec/SKILL.md:33,34`, `agents/tdq-refactor-cleaner.md:20`, `docs/claude-md-mau.md:58` | **`mcp_lsp_*`** (single underscore! e.g. `mcp_lsp_find_references`, `mcp_lsp_go_to_definition`, `mcp_lsp_diagnostics`, `mcp_lsp_document_symbols`, `mcp_lsp_hover`) when `lsp` is registered in `C:\Users\admin\.gemini\antigravity\mcp_config.json` (or `call_mcp_tool` if lazy-loaded). |
| `mcp__chrome-devtools__*` & `mcp__chrome_devtools__*` | **21** occ / 20 lines / 3 files | `skills/tdq-browser-research/SKILL.md:30,32,35,41,45,47` (6), `skills/tdq-browser-test/SKILL.md:28,29,35,36,38,44,47,48,52,54,58,63` (12), `skills/tdq-setup/references/chrome-devtools-mcp-guide.md:31,48` (3) | Antigravity already installs `chrome-devtools-plugin` (`skills/chrome-devtools/SKILL.md` uses bare tool names `navigate_page`, `take_snapshot`, `evaluate_script`, `get_css_styles`, etc., exposed as `mcp_<serverName>_<toolName>`) PLUS Antigravity has native `browser` subagent (`invoke_subagent(TypeName="browser", Model="flash")`). |
| `mcp__tavily*` | **0** in `skills/`/`agents/` | *(Note: `mcp__tavily` is referenced in `scripts/tdq_setup.py:1100` & `README.md`, while `tavily.md:3` writes `tavily-primary` -> `tavily-backup`)* | If Tavily MCP is configured in `mcp_config.json`, tools are `mcp_tavily-primary_tavily_search` etc.; otherwise fallback is Antigravity `search_web`. |
| `Bash` (as tool name) | **9** occ / 9 lines / 7 files | `skills/tdq-build/references/rules/index.md:46` *(Bash shell language, not tool)*; **8 tool refs:** `reminder-codes.md:32,43`, `tdq-setup/SKILL.md:81`, `uu-tien-tim-kiem-chi-tiet.md:17`, `uu-tien-tim-kiem.md:131`, `tdq-status/SKILL.md:13,19`, `agents/tdq-qc-tester.md:4` | **`run_command`** (`CommandLine`, `WaitMsBeforeAsync`, PowerShell on Windows — each call runs in a fresh session!). Note `tdq-status/SKILL.md:13`: *"run both in a SINGLE Bash call joined with `&&`"* fails on PS 5.1 unless changed to `;` inside `run_command`! |
| `Edit` (as tool name) | **11** occ / 9 lines / 6 files | `team-mode.md:160`, `tdq-conventions/SKILL.md:46`, `context-budget.md:76,100`, `reminder-codes.md:59,77`, `subagent-tuning.md:60`, `plan-template-huong-dan.md:51`, `plan-template.md:56` | **`edit_file`** (`Path`, `Target`, `Replacement`). Important: `ANTI-4` (`team-mode.md:160`) and `plan-template.md:56` (`Dùng Edit. CẤM dùng Write`) should name `edit_file` / `write_file`. |
| `Write` (as tool name) | **6** occ / 5 lines / 5 files | `context-budget.md:78`, `reminder-codes.md:59`, `subagent-tuning.md:60`, `plan-template-huong-dan.md:51`, `plan-template.md:56` | **`write_file`** (`Path`, `Content`, `Overwrite`). |
| `Read` (as tool name) | **11** occ / 10 lines / 7 files | `tdq-conventions/SKILL.md:46`, `context-budget.md:46,58,67,98,116,117`, `reminder-codes.md:22`, `plan-template-co-che.md:25`, `agents/tdq-qc-tester.md:4`, `agents/tdq-reviewer.md:4`, `agents/tdq-security-reviewer.md:4` | **`read_file`** (`Path`, `StartLine`, `EndLine` — note `context-budget.md:67,117` specifically says `Read with offset + limit`, whereas Antigravity `read_file` uses **`StartLine` + `EndLine`**!). |
| `Glob` (as tool name) | **3** occ / 3 lines / 3 files | `agents/tdq-qc-tester.md:4`, `agents/tdq-reviewer.md:4`, `agents/tdq-security-reviewer.md:4` | **`find_by_name`** (or `list_dir`). |
| `Grep` (as tool name) | **12** occ / 12 lines / 11 files | `reminder-codes.md:32`, `tdq-intake/SKILL.md:62`, `analyze-full.md:40,43`, `quick-lane.md:33`, `tdq-setup/SKILL.md:81`, `uu-tien-tim-kiem-chi-tiet.md:17`, `uu-tien-tim-kiem.md:132`, `agents/tdq-qc-tester.md:4`, `agents/tdq-reviewer.md:4`, `agents/tdq-security-reviewer.md:4`, `docs/claude-md-mau.md:65` | **`grep_search`**. |
| Claude Built-in Subagent Types (`Explore`, `Plan`) | **4** occ / 3 lines / 2 files | `skills/tdq-conventions/references/subagent-tuning.md:25,60` (`Explore`, `Plan`), `skills/tdq-intake/references/analyze-full.md:67` (`Explore`) | **`research`** (`invoke_subagent(TypeName="research", ...)` — read-only codebase/file explorer on Antigravity) or `self`. |
| Claude Model Tiers (`haiku`, `sonnet`, `opus`) | **19** occ / 15 lines / 7 files | `agents/tdq-implementer.md:3,4` (`model: haiku`), `team-mode.md:143` (`haiku`, `sonnet`, `opus`), `tdq-conventions/SKILL.md:166` (`sonnet-low-...`), `soul.md:49,50,144`, `subagent-tuning.md:3,4,25,37,38,40`, `plan-template-huong-dan.md:47`, `docs/claude-md-mau.md:39` | **`invoke_subagent` `Model` enum accepts ONLY `inherit`, `flash_lite`, `flash`, `pro`**! Passing `haiku`, `sonnet`, or `opus` fails schema validation (`haiku` -> `flash`, `sonnet`/`opus` -> `inherit` or `pro`). |

---

### 3.B Slash Commands & Skill Invocation Syntax (`/tdq:*` vs `/tdq-*` vs `tdq-workflow:*` & `tdq_ten_lenh.py`)

1. **Zero `/tdq:*` colon commands exist in `v0.97.0` (`0` occurrences across `skills/`, `agents/`, `scripts/`, `hooks/`):**
   - Earlier versions of TDQ used `/tdq:plan`, `/tdq:execute`, `/tdq:test`, `/tdq:qc`, `/tdq:finish`, and `scripts/tdq_ten_lenh.py` was built to audit skill/command naming consistency. Let's verify what `scripts/tdq_ten_lenh.py` (`156 lines`) actually does in `v0.97.0`:
     - `tdq_ten_lenh.py` scans `skills/<name>/SKILL.md` frontmatter `name:` fields and verifies that every `skills/tdq-*` folder name matches its frontmatter `name: tdq-*` and has no stale `/tdq:` colon references.
     - Across `skills/**`, skill-to-skill transitions are written as Markdown file links (`[tdq-spec](../tdq-spec/SKILL.md)`, `[tdq-plan](../tdq-plan/SKILL.md)`, `[tdq-build](../tdq-build/SKILL.md)` — **63 occurrences** across 60 lines in 28 files). That relative-link design works **natively** on Antigravity because Antigravity agents read `SKILL.md` files via `read_file`!
2. **How `build_portable.py` handles Codex vs. Antigravity command syntax:**
   - **Codex (`--sinh-codex`):** Does **NOT** rewrite slash commands either — `.codex-plugin/plugin.json` points `"skills": "./skills/"` directly, and Codex invokes skills as `$tdq-intake` or `/skills`.
   - **Antigravity (`--sinh-agy`):** Copies 9 skill folders into `C:\Users\admin\.gemini\config\plugins\tdq-workflow\skills\tdq-*\SKILL.md` (with `README_AGY` telling users to type `/tdq-intake`, `/tdq-status`, etc.), **without** generating `.claude-plugin/plugin.json` or `.gemini-plugin/plugin.json`, and **dropping** `tdq-browser-research` and `tdq-browser-test`.
3. **What STILL breaks on Antigravity around slash commands & skill namespaces:**
   - **Residual `tdq-workflow:tdq-intake` Claude namespace (`3` locations):**
     1. `docs/claude-md-mau.md:70`: *"Mọi yêu cầu mới từ người dùng BẮT BUỘC phải mở bằng skill `tdq-workflow:tdq-intake` (hoặc `tdq-intake` nếu cài cục bộ)"*
     2. `scripts/tdq_setup.py:1110`: Injects the exact same `tdq-workflow:tdq-intake` instruction into `CLAUDE.md`.
     3. `hooks/scripts/prompt_context.py:271`: Prints `open tdq-workflow:tdq-intake (or tdq-intake)` into `[TDQ:INTAKE]` prompt context!
     - On Antigravity, skills in `<skills>` are registered by bare frontmatter name (`tdq-intake`), NOT `tdq-workflow:tdq-intake`.
   - **Host slash commands in skills/docs that DO NOT EXIST on Antigravity (`6` occurrences across 5 skill files + `README_AGY`):**
     - `/mcp` in `skills/tdq-intake/SKILL.md:54` (*"ask the user to reconnect `/mcp`"*), `skills/tdq-intake/references/kiem-lsp-hieu-ung.md:60` (*"a reconnect of MCP `lsp` (`/mcp`), or starting the session again"*), and `scripts/build_portable.py:289` (`README_AGY` telling Antigravity users to type `/mcp`!). Antigravity has **no `/mcp` slash command** (MCP servers are managed in the MCP Servers UI panel or `C:\Users\admin\.gemini\antigravity\mcp_config.json`).
     - `/skills` in `scripts/build_portable.py:288` (`README_AGY` telling Antigravity users to type `/skills` to check loaded skills!). Antigravity's `<slash_commands>` list is `/goal`, `/compact`, `/schedule`, `/browser`, `/plan`, `/grill-me`, `/teamwork`, `/learn`, `/boost` — there is **no `/skills`**!
     - `/code-review` in `skills/tdq-conventions/references/plugin-routing.md:24` (Claude Code built-in slash command).
     - `/hooks` in `skills/tdq-setup/references/uu-tien-tim-kiem.md:148` (Codex CLI slash command).
     - `/goal` in `skills/tdq-build/SKILL.md:21` — **compatible** (matches Antigravity's `/goal`!).

---

### 3.C Shell / OS Command Compatibility Inside Skill Prompts & Templates (Windows PowerShell 5.1)

Antigravity on Windows executes every `run_command` call in a **fresh, stateless Windows PowerShell 5.1 process** (`Operating System: windows. Shell: powershell. Each command runs in a new session`). Scanning all 82 files revealed **6 distinct shell compatibility hazards**:

1. **`python3 ` command prefix (`128` occurrences across `39` skill files + `2` bare `python ` in `runtime-speed.md:18` & `mcp-first-guide.md:47`):**
   - Every single TDQ CLI invocation in `skills/**` and `portable_src/**` is written `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/..."` (126 lines) or `python3 scripts/...` (2 lines: `tdq-browser-test/SKILL.md:64`, `chrome-devtools-mcp-guide.md:46`) or `python3 ~/.claude/scripts/...` (`plugin-routing.md:103`).
   - **Empirical Windows behavior:** While `tdq_checkportable.py` can drop a `python3.cmd` (`@py -3 %*`) shim for interactive PowerShell, (a) `--sinh-agy` never runs `tdq_checkportable.py` (so machines without `python3.cmd` hit `WindowsApps\python3.exe` Microsoft Store stub -> exit `49`/`9009`), and (b) **any Python subprocess call `subprocess.run(["python3", ...], shell=False)` bypasses `.cmd` shims in `CreateProcessW` and fails with `rc=9009` even on THIS machine!**
   - **Fix:** Rewrite `python3 ` in Antigravity-built skill files (and hook registrations) to `py -3 ` on Windows (or `python ` when verified), and ensure `scripts/` internal `subprocess.run` calls always use `sys.executable`!
2. **Backslash `\` line continuations inside fenced shell commands (`12` lines across `3` skill files):**
   - `skills/tdq-build/references/vision-test-loop.md:87-94` (8 trailing `\` lines in `tdq_vision_diff.py` invocation!)
   - `skills/tdq-plan/SKILL.md:32` (`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_bench.py" simulate --plan docs/tdq/plan/<slug>.md \`)
   - `skills/tdq-setup/SKILL.md:110-112` (3 trailing `\` lines in `claude mcp add ... \`)
   - **Impact:** Copying & running any of these multi-line commands in PowerShell 5.1 fails immediately because `\` is treated as a literal path/arg token, NOT a line continuation! Must join onto single lines (or use PowerShell backtick `` ` ``).
3. **`&&` and `||` command chaining (`5` occurrences across `5` skill files):**
   - **Actionable bug (`skills/tdq-status/SKILL.md:13`):** Explicitly instructs the agent: *"Read two things (read-only, touch no file) — **run both in a SINGLE Bash call joined with `&&`**"* (`tdq_state.py next --brief` + `tdq_state.py get`, plus `tdq_timing.py status` on line 19). In Windows PowerShell 5.1 (`$PSVersionTable.PSVersion = 5.1`), `&&` throws `ParserError: The token '&&' is not a valid statement separator in this version`!
   - Other 4 occurrences are prose/anti-pattern warnings (`runtime-speed.md:24` `cd frontend && npm test` example, `tdq-conventions/SKILL.md:190` warning against `&&`, `context-budget.md:32` warning against `&&`, `tdq-conventions/SKILL.md:102` `no || fallback`).
4. **Inline POSIX env assignment `VAR=val cmd` + `/tmp/...` (`2` occurrences across `2` skill files):**
   - `skills/tdq-conventions/SKILL.md:102`: *"Every test touching workflow state MUST isolate with `tmp_path`: put `TDQ_PROJECT_DIR=/tmp/...` on that very command (no `||` fallback)."*
   - `skills/tdq-plan/references/plan-template.md:36`: *"4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó."*
   - **Impact:** In PowerShell 5.1, `TDQ_PROJECT_DIR=C:\temp py -3 ...` is **invalid syntax** (`CommandNotFoundException`), and `/tmp/...` does not exist on Windows. Must document PowerShell syntax: `$env:TDQ_PROJECT_DIR = "$env:TEMP\tdq-test"; py -3 ...`!
5. **Heredocs (`cat << 'EOF'`) and `/dev/null` (`2>/dev/null`):**
   - **0 occurrences** in `skills/**` and `agents/**` (`shell_heredoc = 0`, `2>/dev/null = 0`) — clean!
6. **POSIX-only CLI tools & `~/` / `${CLAUDE_PLUGIN_ROOT}` / `~/.claude` paths:**
   - **POSIX CLI calls in skills (`6` actionable lines):**
     - `skills/tdq-setup/SKILL.md:94` & `README.md:112`: `curl -fsSL https://raw.githubusercontent.com/blackwell-systems/agent-lsp/main/install.sh | sh` and `tdq-setup/SKILL.md:100`: `brew install lua-language-server` (fails on Windows; needs `go install` / Windows release binary instructions).
     - `skills/tdq-build/references/team-mode.md:69,70,173`: `grep -A2 'T1.1' <plan>`, `grep '(mcp)' <plan>`, `grep -c '^- \[x\]' docs/tdq/plan/<slug>.md` (fails in PowerShell where `grep` is not built-in -> use Antigravity `grep_search` or `Select-String`).
     - `skills/tdq-conventions/references/context-budget.md:75,98,116` & `uu-tien-tim-kiem-chi-tiet.md:53`: `grep -n` / `grep -rl` -> replace with Antigravity `grep_search` tool!
   - **`${CLAUDE_PLUGIN_ROOT}` (`126` lines across `37` files) & bare `scripts/`/`hooks/` (`39` occurrences across `38` lines in `25` files):**
     - Currently `--sinh-agy` substitutes raw `goc_cai` with Windows backslashes (`C:\Users\admin\.gemini\config\plugins\tdq-workflow/scripts/...`) AND blindly rewrites bare `scripts/` in prose/examples (`team-mode.md:131` `scripts/alpha.py`, `clean-code.md:69-106`, `rules/index.md:74` `scripts/scan.py`). Must normalize `goc_cai` to forward slashes (`C:/Users/...`) and restrict bare `scripts/` rewriting to actual `tdq_*.py` / plugin script paths!
   - **Claude-specific home paths (`20` lines across `10` files):**
     - `~/.claude.json` & `~/.claude/settings.json` & `claude mcp add/remove` (`tdq-setup/SKILL.md:54,56,110,116,117,121`, `chrome-devtools-mcp-guide.md:11,27`, `context-budget.md:121`) -> on Antigravity, MCP config is `C:\Users\admin\.gemini\antigravity\mcp_config.json`.
     - `~/.claude/skills/tdq-rules/` (`rules/index.md:46`, `rules/them-ngon-ngu.md:48,56`) -> on Antigravity, user skills live in `C:\Users\admin\.gemini\antigravity\skills\` or `C:\Users\admin\.gemini\config\plugins\`.
     - `~/.claude/projects/<project>/` (`issue-triage.md:11`, `measure-scenario.md:25`) & `~/.claude/image-cache/` (`worklog-images.md:8`) -> on Antigravity, transcripts & media live in `<appDataDir>\brain\<conversation-id>\.system_generated\logs\transcript.jsonl`.
     - `~/.claude/plugin-tiers.json` & `~/.claude/scripts/plugin_tiers.py` (`plugin-routing.md:98,100,103,104`) -> Claude-author-specific local script; does not exist on Antigravity.
   - **Stateless working directory hazard in worktree subagents (`team-mode.md:130`, `agents/tdq-implementer.md:13`):**
     - Subagents receive `WORKTREE: /abs/path/.tdq-worktrees/<slug>/t1.1`. Because Antigravity `run_command` resets `cwd` to the parent workspace on **every** call, `tdq-implementer` MUST prefix every `run_command` with `Set-Location "<WORKTREE>"; ` and pass absolute `<WORKTREE>/...` paths to `read_file`/`edit_file`/`write_file` (or be invoked with `Workspace="share"`/`"branch"`).

---

### 3.D Agent Frontmatter, Model Names & Subagent Protocol (`agents/*.md` in `v0.97.0`)

Inspecting all 6 files in `agents/` (`v0.97.0`) line-by-line:

1. **Exact Frontmatter Inventory:**
   - `agents/tdq-implementer.md`: `name: tdq-implementer`, `model: haiku`, `effort: medium` *(no `tools:`, no `color:`)*
   - `agents/tdq-build-resolver.md`: `name: tdq-build-resolver`, `model: inherit`, `effort: high` *(no `tools:`, no `color:`)*
   - `agents/tdq-refactor-cleaner.md`: `name: tdq-refactor-cleaner`, `model: inherit`, `effort: high` *(no `tools:`, no `color:`; body line 20 calls `mcp__lsp__diagnostics`)*
   - `agents/tdq-qc-tester.md`: `name: tdq-qc-tester`, `tools: Bash, Read, Grep, Glob`, `model: inherit`, `effort: high`
   - `agents/tdq-reviewer.md`: `name: tdq-reviewer`, `tools: Read, Grep, Glob`, `model: inherit`, `effort: high`
   - `agents/tdq-security-reviewer.md`: `name: tdq-security-reviewer`, `tools: Read, Grep, Glob`, `model: inherit`, `effort: high`
2. **Four Incompatibilities Blocking `agents/*.md` on Antigravity:**
   - **Gap A — Not shipped at all:** `build_portable.py --sinh-agy` copies **0** files from `agents/`, so `invoke_subagent(TypeName="tdq-implementer", ...)` fails immediately unless the leader dynamically calls `define_subagent` first or `.agent/agents/*.md` / plugin `agents/*.md` is installed.
   - **Gap B — Invalid `model: haiku` & unsupported `effort:`:** `tdq-implementer.md:3-4` sets `model: haiku` and all 6 agents set `effort: medium|high`. Antigravity's subagent schema only accepts `Model` in `["inherit", "flash_lite", "flash", "pro"]` (`haiku` -> `flash`) and has no `effort` field.
   - **Gap C — Comma-string Claude `tools:` names:** `Bash, Read, Grep, Glob` uses Claude tool names in a comma-delimited string. In Antigravity (`define_subagent` / `.agent/agents/*.md`), write capability is controlled by `EnableWriteTools: false` (for `tdq-reviewer`, `tdq-security-reviewer`) vs `EnableWriteTools: true` (for `tdq-implementer`, `tdq-build-resolver`, `tdq-refactor-cleaner`, `tdq-qc-tester` since QC tester runs test commands via `run_command`), plus `EnableMCPTools: true` (needed by `tdq-refactor-cleaner` for LSP diagnostics and `tdq-qc-tester` for browser/LSP checks).
   - **Gap D — Missing `send_message` return requirement (SILENT FAILURE):** All 6 agent system prompts tell the subagent to print its report block (`TASK/STATUS/...` or `TDQ_HANDOFF_PAYLOAD` JSON) as plain text output. On Antigravity (`<subagent_reminder>`), **plain text output from a subagent is NEVER relayed to the parent agent** — every subagent prompt MUST instruct the subagent to send its final structured block back to the caller's ID via `send_message(Recipient="<caller_id>", Message="<report>")`!

---

## 4. Quantified Master Table of Unported Patterns Missed by `build_portable.py --sinh-agy`

The table below quantifies **every single unported host assumption** across `skills/**` (74 files), `portable_src/**` (1 file), `agents/**` (6 files), and `docs/claude-md-mau.md` (1 file) in `TDQ-Workflow v0.97.0`:

| ID | Category | Source Pattern | Exact Count (Occ / Lines / Files) | Key `file:line` Citations (Complete or Representative) | Current `--sinh-agy` Behavior | Required Antigravity Porting Action |
|---|---|---|---:|---|---|---|
| **M01** | Missing Skills | `tdq-browser-research`, `tdq-browser-test` omitted from `SKILLS_AGY` | **2 skills** (`128` lines / `2` files) | `scripts/build_portable.py:666-676`; `skills/tdq-browser-research/SKILL.md:1-51`, `skills/tdq-browser-test/SKILL.md:1-77` | **MISSED** (only 9 of 11+1 skills copied) | Add both skills to `SKILLS_AGY` (12/12 total skills) and adapt tool refs for Antigravity `browser` subagent + `chrome-devtools-plugin`. |
| **M02** | Missing Agents | Entire `agents/*.md` directory not copied or converted | **6 agents** (`274` lines / `6` files) | `agents/tdq-build-resolver.md`, `tdq-implementer.md`, `tdq-qc-tester.md`, `tdq-refactor-cleaner.md`, `tdq-reviewer.md`, `tdq-security-reviewer.md` | **MISSED** (`0` agents copied) | Ship all 6 converted agents in plugin `agents/` + workspace `.agent/agents/` (and document `define_subagent` fallback). |
| **M03** | Missing Plugin Manifest & Rules | No `.claude-plugin/plugin.json` / `.gemini-plugin/plugin.json` and no `.agent/rules/tdq-workflow.md` | **2 manifests + 1 rule file** (`104` lines in `docs/claude-md-mau.md`) | `docs/claude-md-mau.md:62-79`, `.claude-plugin/plugin.json:1-32`, `scripts/tdq_setup.py:1090-1140` | **MISSED** (writes loose folder with `README.md` only) | Emit `.claude-plugin/plugin.json` + `.mcp.json` + `hooks/hooks.json` in plugin root AND generate `.agent/rules/tdq-workflow.md` (`activation: always_on`) for target workspaces. |
| **M04** | Shell Python Binary | `python3 ` CLI prefix (plus `2` bare `python `) | **128 occ** / `128` lines / `39` files | `tdq-intake/SKILL.md:53,55,81,126`, `tdq-spec/SKILL.md:45,52,88,94`, `tdq-plan/SKILL.md:32,71,75,105,121`, `tdq-build/SKILL.md:25,84,126,136,156,170`, `phases.md:3-37` (25x), `team-mode.md:49-171` (13x), `tdq-checkportable/SKILL.md:15,24,40`, etc. | **MISSED** (`0` rewritten; fails without `.cmd` shim and ALWAYS fails under `CreateProcessW` `shell=False` with `rc=9009`) | Rewrite `python3 ` -> `py -3 ` on Windows Antigravity builds (or cross-platform launcher) and enforce `sys.executable` inside Python scripts. |
| **M05** | Path Variable Expansion | `${CLAUDE_PLUGIN_ROOT}` / `$CLAUDE_PLUGIN_ROOT` mixed-slash output | **126 occ** / `126` lines / `37` files | Same 36 skill files + `docs/claude-md-mau.md:74` (`tdq-setup/SKILL.md:30` has unprefixed `${CLAUDE_PLUGIN_ROOT}/scripts/tdq_lsp.py`) | **PARTIAL / BUGGY** (injects raw Windows backslashes `C:\Users\.../scripts/...`) | Normalize `goc_cai` with `.replace("\\", "/")` before substitution so paths are clean `C:/Users/.../scripts/...`. |
| **M06** | Bare Path Over-Rewrite | `\b(scripts/\|hooks/)` regex in `_sua_duong_dan_tuong_doi_agy` | **39 occ** / `38` lines / `25` files (`~9` are sample/prose paths!) | Sample paths corrupted today: `team-mode.md:131` (`scripts/alpha.py`), `team-mode-tra-cuu.md:58` (`scripts/a.py`), `rules/index.md:74` (`scripts/scan.py`), `clean-code.md:69,77,85,98,106` | **BUGGY** (corrupts non-plugin example paths in prose/templates) | Restrict rewrite regex to actual shipped plugin files (`scripts/(?:tdq_\w+\|doc_lint\|kiem_no_marker\|scan_block_symbols\|skill_inventory\|step_audit\|token_audit)\.py` and `hooks/scripts/\w+\.py`). |
| **M07** | Shell Line Continuations | Trailing POSIX `\` inside fenced shell commands | **12 occ** / `12` lines / `3` files | `skills/tdq-build/references/vision-test-loop.md:87-94` (8L), `skills/tdq-plan/SKILL.md:32` (1L), `skills/tdq-setup/SKILL.md:110-112` (3L) | **MISSED** (breaks PowerShell 5.1 `run_command` parsing) | Collapse multi-line CLI invocations to single lines (or PowerShell `` ` `` continuations). |
| **M08** | Shell `&&` / `\|\|` Chaining | `&&` / `\|\|` in skill instructions | **5 occ** / `5` lines / `5` files (**1 active bug**) | **Active bug:** `skills/tdq-status/SKILL.md:13` (*"run both in a SINGLE Bash call joined with `&&`"*); prose: `runtime-speed.md:24`, `tdq-conventions/SKILL.md:102,190`, `context-budget.md:32` | **MISSED** (`&&` throws `ParserError` in Windows PowerShell 5.1) | Rewrite `tdq-status/SKILL.md:13,19` to join with `;` in PowerShell `run_command` (or run two parallel `run_command` calls). |
| **M09** | Inline POSIX Env + `/tmp` | `TDQ_PROJECT_DIR=/tmp/... cmd` inline env syntax | **2 occ** / `2` lines / `2` files | `skills/tdq-conventions/SKILL.md:102`, `skills/tdq-plan/references/plan-template.md:36` | **MISSED** (`VAR=val cmd` & `/tmp` fail in PowerShell) | Rewrite to PowerShell syntax (`$env:TDQ_PROJECT_DIR = "$env:TEMP\..."; py -3 ...`) or cross-platform Python `env=` wrapper. |
| **M10** | MCP Double-Underscore Prefix (`lsp`) | `mcp__lsp__*` | **19 occ** / `19` lines / `11` files | `tdq-build/SKILL.md:69,120`, `rules/chung.md:81`, `reminder-codes.md:25,46`, `analyze-full.md:41`, `tdq-plan/SKILL.md:58`, `tdq-setup/SKILL.md:56,118,120`, `uu-tien-tim-kiem-chi-tiet.md:36,44`, `uu-tien-tim-kiem.md:27,39,72`, `tdq-spec/SKILL.md:33,34`, `agents/tdq-refactor-cleaner.md:20`, `docs/claude-md-mau.md:58` | **MISSED** | Rewrite `mcp__lsp__` -> `mcp_lsp_` (Antigravity single-underscore MCP naming when server `lsp` is in `mcp_config.json`). |
| **M11** | MCP Double-Underscore Prefix (`chrome-devtools`) | `mcp__chrome-devtools__*` & `mcp__chrome_devtools__*` | **21 occ** / `20` lines / `3` files | `tdq-browser-research/SKILL.md:30,32,35,41,45,47` (6), `tdq-browser-test/SKILL.md:28,29,35,36,38,44,47,48,52,54,58,63` (12), `chrome-devtools-mcp-guide.md:31,48` (3) | **MISSED** (2 of 3 files weren't even copied!) | Map to Antigravity's installed `chrome-devtools` plugin tool names (`navigate_page`, `take_snapshot`, `evaluate_script`, etc. / `mcp_<server>_<tool>`) + native `browser` subagent (`Model="flash"`). |
| **M12** | Popup Gate Ban Bypass (`AskUserQuestion`) | Banning `AskUserQuestion` without banning `ask_question` | **3 occ** / `3` lines / `3` files | `user-facing-block.md:103`, `interview.md:50`, `docs/claude-md-mau.md:76` | **MISSED** (Antigravity agent calls `ask_question` popup, breaking TDQ chat gates!) | Explicitly ban `ask_question` alongside `AskUserQuestion` in all 3 locations + `.agent/rules/tdq-workflow.md`. |
| **M13** | Plan Mode Ban (`EnterPlanMode` / `ExitPlanMode`) | `EnterPlanMode`, `ExitPlanMode` | **5 occ** / `4` lines / `2` files | `approval.md:48,50`, `docs/claude-md-mau.md:70,75` | **MISSED** | Map to banning `/plan` mode switching and artifact `RequestFeedback: true` ("Proceed" button) on Antigravity. |
| **M14** | Subagent Dispatch Tool & Handoff | `Task` call / `the Agent tool` + missing `send_message` in subagents | **4 tool refs** + **6 agent prompts** (`10` locs / `8` files) | `tdq-build/SKILL.md:86` (`Task calls`), `subagent-tuning.md:10,11,31,68` (`Agent tool`), `agents/tdq-*.md` (all 6 lack `send_message`) | **MISSED** (subagents finish silently without `send_message`; `Set-Location` missing for worktrees!) | Map `Task`/`Agent` -> `invoke_subagent`; append mandatory `send_message(Recipient=<caller_id>, ...)` + worktree `Set-Location` rules to all 6 `agents/tdq-*.md` and `team-mode.md:126-140`. |
| **M15** | Claude Model Names & Built-in Subagents | `haiku`, `sonnet`, `opus` + `Explore`, `Plan` | **23 occ** / `18` lines / `8` files | `agents/tdq-implementer.md:3,4` (`haiku`), `team-mode.md:143`, `tdq-conventions/SKILL.md:166`, `soul.md:49,50,144`, `subagent-tuning.md:3,4,25,37,38,40,60`, `analyze-full.md:67` (`Explore`), `plan-template-huong-dan.md:47`, `docs/claude-md-mau.md:39` | **MISSED** (`Model` enum on Antigravity rejects `haiku`/`sonnet`/`opus`!) | Map `haiku` -> `flash`, `sonnet`/`opus` -> `inherit` (or `pro`); map `Explore`/`Plan` -> `research` subagent. |
| **M16** | Core File/Search/Web Tool Names | `Bash` (8), `Edit` (11), `Write` (6), `Read` + `offset/limit` (11), `Glob` (3), `Grep` (12), `WebSearch`/`WebFetch` (3) | **54 occ** across `23` files | `context-budget.md:58-117` (`Read` `offset + limit`), `plan-template.md:56` (`Dùng Edit. CẤM dùng Write`), `tavily.md:5`, `analyze-full.md:72`, `agents/tdq-qc-tester.md:4`, `tdq-reviewer.md:4`, `tdq-security-reviewer.md:4`, etc. | **MISSED** | Map `Bash` -> `run_command`, `Edit` -> `edit_file`, `Write` -> `write_file`, `Read (offset+limit)` -> `read_file (StartLine+EndLine)`, `Glob` -> `find_by_name`, `Grep` -> `grep_search`, `WebSearch` -> `search_web`. |
| **M17** | Slash Commands & Namespace Prefix | `tdq-workflow:tdq-intake` (3 repo locs) + `/mcp`, `/skills`, `/code-review`, `/hooks` (6 skill locs + `README_AGY`) | **9 occ** across `7` files | `docs/claude-md-mau.md:70`, `scripts/tdq_setup.py:1110`, `hooks/scripts/prompt_context.py:271`; `/mcp` in `tdq-intake/SKILL.md:54`, `kiem-lsp-hieu-ung.md:60`, `build_portable.py:289`; `/skills` in `build_portable.py:288`; `/code-review` in `plugin-routing.md:24`; `/hooks` in `uu-tien-tim-kiem.md:148` | **MISSED** (and `README_AGY` actively instructs users to run non-existent `/skills` & `/mcp`!) | Replace `tdq-workflow:tdq-intake` -> `tdq-intake` (`/tdq-intake`); replace `/mcp` & `/skills` instructions with Antigravity's Plugins / MCP Servers UI & `mcp_config.json`. |
| **M18** | Claude Home / Config Paths & POSIX Installers | `~/.claude.json`, `~/.claude/settings.json`, `claude mcp add`, `~/.claude/skills/`, `~/.claude/projects/`, `curl ... \| sh`, `brew`, `grep -c/-n` | **28 occ** across `14` files | `tdq-setup/SKILL.md:54,56,94,100,110-121`, `chrome-devtools-mcp-guide.md:11,27`, `rules/index.md:46`, `rules/them-ngon-ngu.md:48,56`, `plugin-routing.md:98-104`, `issue-triage.md:11`, `measure-scenario.md:25`, `worklog-images.md:8`, `team-mode.md:69,70,173` | **MISSED** | Point MCP setup (`tdq_lsp.py` & `tdq-setup`) to `C:\Users\admin\.gemini\antigravity\mcp_config.json`; point transcripts to `<appDataDir>\brain\<id>\.system_generated\logs\transcript.jsonl`; provide Windows `go install`/binary steps for `agent-lsp`; replace shell `grep` with `grep_search` / `Select-String`. |
| **M19** | External Uninstalled Skill Mandate | Hardcoded `mem0-memory` requirement | **2 occ** / `2` files | `skills/tdq-conventions/SKILL.md:160-161`, `docs/claude-md-mau.md:50-53` | **MISSED** | Gate `mem0-memory` with *"when `mem0-memory` skill is installed; otherwise record in `docs/tdq/knowledge/`"* so agents do not stall searching for a missing skill. |
| **M20** | Non-Markdown Reference Schema | `handoff-schema.json` skipped if copier/rewriter assumes `*.md` only | **1 file** (`50` lines) | `skills/tdq-conventions/references/handoff-schema.json` (used by `agents/tdq-build-resolver.md:30`) | Copied by `shutil.copytree`, ignored by `.md` walkers | Keep `copytree` for non-`.md` assets (`*.json`) while restricting text rewrites to `.md` files, and update `R13` count awareness (`62` `.md` + `1` `.json` = `63` reference files, `74` total files in `skills/`). |
