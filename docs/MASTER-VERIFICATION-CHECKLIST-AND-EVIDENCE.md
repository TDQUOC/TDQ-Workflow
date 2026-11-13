# TDQ-Workflow v0.97.0 trên Google Antigravity — Master Verification Checklist & Bằng Chứng Thực Nghiệm (10 Phân Hệ)

> **Thời điểm tạo & kiểm chứng:** `2026-11-14T01:42:05+07:00` · **Baseline Upstream:** `C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow` (`dev @ b423ee06`) · **Compiled Plugin:** `plugins/tdq-workflow` (`OK`)

## Tóm Tắt Chỉ Số Đạt Chuẩn (Observed Live Evidence)

| Chỉ số kiểm định | Kết quả thực tế quan sát | Tham chiếu bằng chứng |
|---|---|---|
| **Plugin Build Compiler** | `scripts: 61` (`60 .py + 1 sample`), `hooks: 19` (`21 .py` tổng gồm AGY adapters), `skills_files: 75`, `agents: 6`, `ast_checked_py: 81`, `md_checked_budget: 22` | `py -3 -B tools/build_agy_plugin.py` (rc=`0`) |
| **Official Validator (`source`)** | `name: tdq-workflow`, `agents: 6`, `hooks: 6`, `mcpServers: 3`, `rules: 10`, `skills: 12`, `findings: []` (**0 error / 0 warning**) | `agy.EXE plugin validate plugins/tdq-workflow --strict --json` (rc=`0`) |
| **Official Validator (`staged install`)** | `install_dry_run_rc: 0`, `install_staged_rc: 0`, `staged_validate findings: []` (**0 error / 0 warning**) | `tools/install_agy_plugin.py --dry-run` & `--target <tmp>` |
| **Pytest Verification (`V1–V6`)** | **`14/14 PASSED`** (`0` failed, `16996.7 ms`) | `py -3 -m pytest tests/ -v --basetemp=.pytest_tmp` (rc=`0`) |
| **Linters & Token / Symbol Gates** | `doc_lint` skills (`74` files): `0 violations` · agents (`6`): `0` · rules (`10`): `0` · `token_budget --kiem`: rc=`0` · `scan_block_symbols --chi-khoi`: `0` ngoài whitelist (`stderr: `) · `i18n_check`: `0` dòng Việt trong 3 hook mới | `docs/verification_evidence.json` -> `linters` |
| **7 Companion Extensions & MCP** | `agent-lsp.exe` stdio JSON-RPC sống (`36.3 ms`, **65 tools**), `chrome-devtools` (`npx 11.19.0`), `tavily-primary` (`no_variables_trap: True`), Archify `ĐẠT`, Graphify OK, Vision Diff OK, Codex CLI `codex-cli 0.166.0` | `test_v5` & `tools/run_full_verification.py` |
| **Upstream & Global Config Safety** | `upstream_code_clean: True` (`dev @ b423ee06`), `~/.gemini/config/config.json` SHA-256 bất biến: `3525858d7521b7b54147410e29966dd58325604676e7befefb7df67f2b03a646` | `git status -- plugins/ .claude-plugin/ scripts/ hooks/ tools/` |

---

## Mục 1 — 7 Companion Extensions & MCP Servers (`V5` Live Probes)

| Checklist | Extension / Engine | Lệnh / Cơ chế kiểm chứng | Kết quả thực tế quan sát |
|---|---|---|---|
| - [x] | **1. Agent-LSP MCP (`lsp`)** | Live stdio NDJSON JSON-RPC `initialize` + `tools/list` trên `C:\Users\admin\.local\bin\agent-lsp.exe` (`binary_exists: True`) | `rc=0`, độ trễ `36.3 ms`, trả về **65** tools thực tế *(Lưu ý thực nghiệm: chuỗi `instructions` của `agent-lsp.exe` tự quảng cáo `66 code intelligence tools`, nhưng `tools/list` trả đúng `65` tool sorted)* |
| - [x] | **2. Chrome DevTools MCP (`chrome-devtools`)** | Kiểm tra `mcp_config.json` + `C:\Users\admin\AppData\Local\fnm_multishells\42416_1794595305260\npx.cmd --version` | `configured: True`, `npx` `11.19.0` (`rc=0`), args: `-y chrome-devtools-mcp@latest --userDataDir=C:/Users/admin/.gemini/chrome-devtools-profile` |
| - [x] | **3. Tavily MCP (`tavily-primary`)** | Kiểm tra `mcp_config.json` & không bẫy `"variables"` (tự tắt plugin) | `configured: True`, `no_variables_trap: True`, args: `-y tavily-mcp@latest` |
| - [x] | **4. Archify Visual BA** | `C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe -X utf8 scripts/tdq_setup.py --kiem-archify` | `rc=0` · `archify · ĐẠT (Node.js v24.21.0 (>= 18) · Archify tại C:\Users\admin\Documents\archify\archify\bin\archify.mjs)` |
| - [x] | **5. Graphify AST** | `scripts/tdq_graphify.py --help` + `graphify --help` | `tdq_graphify rc=0`, `graphify_cli rc=0` |
| - [x] | **6. Vision Diff** | `C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe -X utf8 scripts/tdq_vision_diff.py --help` | `rc=0` (`--source`, `--figma-url`, `--dist`, `--embed-base64`) |
| - [x] | **7. Codex CLI** | `C:\Users\admin\AppData\Local\fnm_multishells\42416_1794595305260\codex.CMD --version` | `rc=0` · `codex-cli 0.166.0` |

<details><summary>Danh sách đầy đủ 65 tool trả về từ live MCP tools/list (agent-lsp.exe)</summary>

```text
activate_skill, add_workspace_folder, apply_edit, blast_radius, callers, close_document, commit_session, create_simulation_session, deactivate_skill, destroy_session, detect_changes, detect_lsp_servers, did_change_watched_files, discard_session, evaluate_session, execute_command, explore, explore_symbol, export_cache, find_callers, find_references, find_symbol, format_document, format_range, get_completions, get_cross_repo_references, get_diagnostics, get_document_highlights, get_inlay_hints, get_semantic_tokens, get_server_capabilities, get_signature_help, get_skill_phase, get_symbol_documentation, get_symbol_source, get_tests_for_file, go_to_declaration, go_to_definition, go_to_implementation, go_to_symbol, go_to_type_definition, import_cache, insert_after_symbol, insert_before_symbol, inspect_symbol, list_symbols, list_workspace_folders, open_document, prepare_rename, preview_edit, remove_workspace_folder, rename_symbol, replace_symbol_body, restart_lsp_server, run_build, run_tests, safe_apply_edit, safe_delete_symbol, safe_edit, set_log_level, simulate_chain, simulate_edit, start_lsp, suggest_fixes, type_hierarchy
```
</details>

---

## Mục 2 — Host Addons, Manifests, Build Compiler & Safe Installer (`V1`, `V2`)

- [x] `plugins/tdq-workflow/plugin.json`: Schema Antigravity hợp lệ (`name: tdq-workflow`, `displayName: TDQ Workflow`, `version: 0.97.0`, `logo: assets/logo.svg`, `suggestedPrompts: 3`).
- [x] `plugins/tdq-workflow/assets/logo.svg`: SVG icon vector hợp lệ.
- [x] `plugins/tdq-workflow/hooks.json`: Top-level Antigravity group schema (6 nhóm, không chứa khóa `description` sai chuẩn, không dùng `${PLUGIN_ROOT}` trong chuỗi `command`).
- [x] `plugins/tdq-workflow/mcp_config.json`: Khai báo đúng **3** MCP servers (`lsp`, `chrome-devtools`, `tavily-primary`), **không** có block `variables` hay chuỗi giả `"${TAVILY_API_KEY}"`.
- [x] `plugins/tdq-workflow/manifest.json` & `plugins/tdq-workflow/README.md`: Đồng bộ danh sách script/skill/agent và `upstream_commit: b423ee06`.
- [x] `.agents/plugins.json`: Khai báo `{"entries": [{"path": "./plugins"}]}` kích hoạt discovery cục bộ trong workspace mà không đụng cấu hình toàn cục.
- [x] `agy.EXE plugin validate plugins/tdq-workflow --strict --json`: Exit `0`, `findings: []` (`agents: 6`, `hooks: 6`, `mcpServers: 3`, `rules: 10`, `skills: 12`).
- [x] `tools/install_agy_plugin.py`: `--dry-run` (rc=`0`), staged `--target` (rc=`0`) -> `agy.EXE plugin validate` trên thư mục staged trả về `findings: []` (`staged_validate_json` sạch 100%).
- [x] Kiểm tra biên dịch Python & ngân sách Markdown (`V2`): `81` tệp `.py` parse AST sạch (không lỗi `\U` unicodeescape), `22` tệp `.md` (`rules/*.md` + `SKILL.md`) đều `< 24,000 bytes`.

---

## Mục 3 — Soul, Clean Code Invariants, Thang 7 Nấc `TDQ:GON`, `R1–R15` & Hệ Luật 2 Tầng (`rules/` — 10 Files)

- [x] **Hiến pháp Soul (`skills/tdq-conventions/references/soul.md`):** Giữ nguyên thứ bậc bất khả xâm phạm **chất lượng > runtime > context cost**, 5 Bất biến Clean Code (kèm #4 *Giả thuyết + 5 Whys* & #5 *Triage Before Touch*), và thang 7 nấc `TDQ:GON` (*YAGNI trước SOLID*, Log Service bật mặc định với `TDQ_LOG=0` để tắt).
- [x] **Bảng 6 ký hiệu phi-ASCII hợp lệ (`scan_block_symbols.py --chi-khoi`):** `Total: 6 distinct symbol(s) across 9 file(s) · 0 character(s) OUTSIDE the whitelist need a decision.` (`stderr` rỗng; `➤ · — → – …`).
- [x] **Bộ Linter Tài Liệu & Ngân Sách Token:** `doc_lint.py skills` (`141.2 ms`, `0 violations` trên `74` files), `doc_lint.py agents` (`0 violations` trên `6` files), `doc_lint.py rules` (`0 violations` trên `10` files), `token_budget.py --kiem` (rc=`0`).

### Danh Sách 10 Tệp Luật 2 Tầng (`plugins/tdq-workflow/rules/*.md` — Đều `< 24,000 B`)

| Checklist | Tệp Rule | Kích thước (bytes) | Trigger Antigravity | Vai trò |
|---|---|---|---|---|
| - [x] | `AGENTS.md` | `3,231` B | `always_on` | Tầng 1 — Soul, Pipeline, Tool Map & PS 5.1 (nạp nền) |
| - [x] | `domain-git-safety.md` | `548` B | `model_decision` | Tầng 2 — Luật ngữ cảnh tự nạp theo quyết định model |
| - [x] | `domain-mcp-first.md` | `632` B | `model_decision` | Tầng 2 — Luật ngữ cảnh tự nạp theo quyết định model |
| - [x] | `lang-csharp.md` | `193` B | `glob` | Tầng 2 — Luật ngôn ngữ/kỹ thuật chỉ nạp theo glob file |
| - [x] | `lang-go.md` | `238` B | `glob` | Tầng 2 — Luật ngôn ngữ/kỹ thuật chỉ nạp theo glob file |
| - [x] | `lang-python.md` | `409` B | `glob` | Tầng 2 — Luật ngôn ngữ/kỹ thuật chỉ nạp theo glob file |
| - [x] | `lang-rust.md` | `237` B | `glob` | Tầng 2 — Luật ngôn ngữ/kỹ thuật chỉ nạp theo glob file |
| - [x] | `lang-shell-powershell.md` | `273` B | `glob` | Tầng 2 — Luật ngôn ngữ/kỹ thuật chỉ nạp theo glob file |
| - [x] | `lang-sql-migration.md` | `191` B | `glob` | Tầng 2 — Luật ngôn ngữ/kỹ thuật chỉ nạp theo glob file |
| - [x] | `lang-typescript.md` | `294` B | `glob` | Tầng 2 — Luật ngôn ngữ/kỹ thuật chỉ nạp theo glob file |

### Kiểm Chứng 15 Luật Linter `R1–R15` (`doc_lint.py` + `token_budget.py`)

| Checklist | Mã | Mô tả luật | Bằng chứng thực thi |
|---|---|---|---|
| - [x] | **R1** | Bước đánh số trong section steps phải liên tục `1, 2, 3…`, không nhảy cóc, không lặp. | `doc_lint.py skills` (`74` files -> `0 violations`, rc=`0`) |
| - [x] | **R2** | Mọi lệnh copy-paste phải nằm trong fenced code block, inline code hoặc ô bảng. | `doc_lint.py skills` (`0 violations`) |
| - [x] | **R3** | Mỗi `SKILL.md` phải ghi rõ điều kiện hoàn tất (exit condition) và bước tiếp theo. | `doc_lint.py skills` (`0 violations`) |
| - [x] | **R4** | Không dùng từ ngữ mơ hồ trong bước/luật nếu 3 dòng kế tiếp không chốt bằng bảng hoặc `→`. | `doc_lint.py skills` (`0 violations`) |
| - [x] | **R5** | Giới hạn độ dài câu (<= 40 từ) để model nhỏ đọc đúng trọng tâm. | `doc_lint.py skills` (`0 violations`) |
| - [x] | **R6** | Giới hạn số dòng riêng cho từng `SKILL.md` (`SKILL_LINE_LIMITS`); mọi file `<= 500` dòng. | `doc_lint.py skills` (`0 violations`) |
| - [x] | **R7** | Skill sinh tệp đầu ra cho người dùng phải đính kèm output template chuẩn. | `doc_lint.py skills` (`0 violations`) |
| - [x] | **R8** | Tệp dưới `spec/` phải có bảng `§3b` liệt kê năng lực. | `doc_lint.py` + `test_v6_full_10_step_e2e_pipeline` |
| - [x] | **R9** | `soul.md` + `references/rules/*` bắt buộc đủ 3 mục `##` chuẩn (`When it applies` / `What to do` / `Self-check`). | `doc_lint.py skills` (`0 violations`) |
| - [x] | **R10** | Spec lane full bắt buộc có `## 2b. Ranh giới module` để plan cắt task theo module. | `doc_lint.py --pair` (`test_v6_full_10_step_e2e_pipeline`) |
| - [x] | **R11** | Spec chỉ nêu điều kiện ĐẠT (pass condition); lệnh kiểm thử cụ thể thuộc về Plan. | `doc_lint.py --pair` (`0 violations`) |
| - [x] | **R12** | Kiểm soát nhất quán ngôn ngữ trên đoạn văn dài, báo đúng dòng đầu tiên vi phạm. | `doc_lint.py skills` (`0 violations`) |
| - [x] | **R13** | Khóa SHA-256 & trần `<= 3.500` tokens cho các tệp luật qua `docs/tdq/token-budget.json`. | `token_budget.py --kiem` (`rc=0`, `0` drift) |
| - [x] | **R14** | Ngưỡng số trong Spec `§6` phải kèm baseline đo trước và fallback. | `doc_lint.py --pair` (`0 violations`) |
| - [x] | **R15** | Mọi Task Block sửa mã nguồn trong Plan (theo mốc ngày) phải có đặc tả kỹ thuật / `Logic:` hoặc pseudo-code. | `doc_lint.py --pair` + `test_new06_to_new14` |

---

## Mục 4 — Toàn Bộ 12 Skills (75 Files: 74 `.md` + `handoff-schema.json`) & 20 Nhóm Biên Dịch `M01–M20`

| Checklist | Skill | Tổng số file | Kích thước `SKILL.md` (bytes < 24,000) | Trạng thái `doc_lint` |
|---|---|---|---|---|
| - [x] | `tdq-browser-research` | `1` | `2,872` B | `0 violations` |
| - [x] | `tdq-browser-test` | `1` | `4,041` B | `0 violations` |
| - [x] | `tdq-build` | `22` | `14,351` B | `0 violations` |
| - [x] | `tdq-check-status` | `3` | `4,555` B | `0 violations` |
| - [x] | `tdq-checkportable` | `1` | `3,303` B | `0 violations` |
| - [x] | `tdq-conventions` | `17` | `15,753` B | `0 violations` |
| - [x] | `tdq-intake` | `13` | `11,504` B | `0 violations` |
| - [x] | `tdq-lean` | `1` | `3,783` B | `0 violations` |
| - [x] | `tdq-plan` | `5` | `8,764` B | `0 violations` |
| - [x] | `tdq-setup` | `6` | `8,990` B | `0 violations` |
| - [x] | `tdq-spec` | `4` | `5,825` B | `0 violations` |
| - [x] | `tdq-status` | `1` | `3,232` B | `0 violations` |

### Bảng Đối Chiếu Biên Dịch `M01–M20` (Claude -> Antigravity 2.0 + Windows PS 5.1)

| Checklist | Mã | Điểm lệch nguồn gốc (`dev @ b423ee06`) | Xử lý đã kiểm chứng | Trạng thái |
|---|---|---|---|---|
| - [x] | **M01** | 2 browser skills (`tdq-browser-research`, `tdq-browser-test`) bị bỏ sót ở adapter cũ | Khôi phục đủ **12 skills** (`75` files) trong `plugins/tdq-workflow/skills/` | **PASS** |
| - [x] | **M02** | 6 subagents không được copy/biên dịch | Xuất đủ **6 agents** (`tdq-*.md`) chuẩn YAML `model` + `tools` list AGY 2.0 | **PASS** |
| - [x] | **M03** | Thiếu `plugin.json` chuẩn + `rules/` (`0 bytes`) | Sinh `plugin.json`, `assets/logo.svg`, `manifest.json`, **10 files `rules/*.md`** | **PASS** |
| - [x] | **M04** | 128 lệnh `python3 ` (lỗi `rc=9009` trên Windows) | Biên dịch sang `py -3 -X utf8` trong bản xuất AGY | **PASS** |
| - [x] | **M05** | `${CLAUDE_PLUGIN_ROOT}` nội suy đường dẫn Windows `\U` vào `.py` | Cấm nội suy vào `.py` (dùng `Path(__file__).resolve()`); POSIX slash trong `.md` | **PASS** |
| - [x] | **M06** | Regex `\b(scripts/|hooks/)` thay nhầm ví dụ prose | Thu hẹp regex chỉ khớp đúng tên script thật của plugin | **PASS** |
| - [x] | **M07** | 12 dòng nối `\` POSIX gãy trên PowerShell 5.1 | Gộp thành single-line commands tương thích PS 5.1 | **PASS** |
| - [x] | **M08** | `&&` / `||` gãy trên PowerShell 5.1 | Chuyển sang dấu `;` / kiểm tra `$LASTEXITCODE` | **PASS** |
| - [x] | **M09** | `TDQ_PROJECT_DIR=/tmp/...` inline POSIX env | Đổi sang mẫu PowerShell `$env:TDQ_PROJECT_DIR=...; py -3 ...` | **PASS** |
| - [x] | **M10** | `mcp__lsp__*` (double underscore) sai prefix AGY | Đổi sang `mcp_tdq-workflow_lsp_*` + hỗ trợ `call_mcp_tool` | **PASS** |
| - [x] | **M11** | `mcp__chrome-devtools__*` sai tên server AGY | Đổi sang `chrome-devtools` trong `mcp_config.json` & skills | **PASS** |
| - [x] | **M12** | Chỉ cấm `AskUserQuestion` mà quên `ask_question` | Cấm cả `ask_question` / `ask_user_question` trong `ask_gate.py` & `AGENTS.md` | **PASS** |
| - [x] | **M13** | Chỉ cấm `EnterPlanMode`, dễ nhầm `/plan` của AGY | Cấm rõ `enter_plan_mode` & phân biệt `/plan` vs `/tdq-plan` (`[TDQ:NO-PLAN-MODE]`) | **PASS** |
| - [x] | **M14** | `Task` / `Agent` tool & subagent không tự trả lời cha | Ánh xạ `invoke_subagent`, bổ sung bắt buộc `send_message` vào 6 agents | **PASS** |
| - [x] | **M15** | Model aliases Claude `haiku`/`sonnet`/`opus` gây ERROR đỏ | Ánh xạ sang `flash` / `inherit` / `pro` hợp lệ theo Go validator | **PASS** |
| - [x] | **M16** | Tools Claude (`Bash`, `Read`, `Edit`, `Write`, `Grep`, `Glob`) không tồn tại | Ánh xạ chuẩn sang AGY 2.0 (`run_command`, `read_file`, `edit_file`, `write_file`, `send_message`) | **PASS** |
| - [x] | **M17** | Slash commands lạ (`/mcp`, `/skills`, `/code-review`, `/hooks`) | Loại bỏ tham chiếu slash command không tồn tại trên AGY | **PASS** |
| - [x] | **M18** | Đường dẫn `~/.claude/*` & lệnh POSIX `claude mcp add` | Chuyển sang `~/.gemini/config/plugins/tdq-workflow/` & `install_agy_plugin.py` | **PASS** |
| - [x] | **M19** | `mem0-memory` bắt buộc cứng dù máy không cài | Chuyển `mem0-memory` thành tùy chọn an toàn khi vắng mặt | **PASS** |
| - [x] | **M20** | `handoff-schema.json` bị bỏ qua nếu chỉ copy `*.md` | Copy & bảo toàn nguyên vẹn `skills/tdq-build/references/handoff-schema.json` (`75` skill files) | **PASS** |

---

## Mục 5 — Toàn Bộ 6 Subagents (`plugins/tdq-workflow/agents/tdq-*.md`)

| Checklist | Tệp Subagent | Kích thước | `model` Tier AGY | `tools` Array (`[]string`) | Quy ước vận hành AGY tiêm sẵn |
|---|---|---|---|---|---|
| - [x] | `tdq-build-resolver.md` | `1,763` B | `flash` | `[read_file, edit_file, write_file, run_command, send_message]` | `[TDQ:GON]`, `Set-Location "<WORKTREE>"`, bắt buộc `send_message` trả kết quả |
| - [x] | `tdq-implementer.md` | `5,779` B | `flash` | `[read_file, edit_file, write_file, run_command, send_message]` | `[TDQ:GON]`, `Set-Location "<WORKTREE>"`, bắt buộc `send_message` trả kết quả |
| - [x] | `tdq-qc-tester.md` | `2,062` B | `inherit` | `[read_file, run_command, send_message]` | `[TDQ:GON]`, `Set-Location "<WORKTREE>"`, bắt buộc `send_message` trả kết quả |
| - [x] | `tdq-refactor-cleaner.md` | `1,722` B | `inherit` | `[read_file, edit_file, write_file, run_command, send_message]` | `[TDQ:GON]`, `Set-Location "<WORKTREE>"`, bắt buộc `send_message` trả kết quả |
| - [x] | `tdq-reviewer.md` | `2,599` B | `inherit` | `[read_file, run_command, send_message]` | `[TDQ:GON]`, `Set-Location "<WORKTREE>"`, bắt buộc `send_message` trả kết quả |
| - [x] | `tdq-security-reviewer.md` | `2,571` B | `pro` | `[read_file, run_command, send_message]` | `[TDQ:GON]`, `Set-Location "<WORKTREE>"`, bắt buộc `send_message` trả kết quả |

---

## Mục 6 — 6 Lifecycle Hook Events, 21 Hook Scripts & 24 Mã `[TDQ:*]`

- [x] **6 Hook Events hoạt động trong `hooks.json`:** `SessionStart`, `PreInvocation`, `PreToolUse`, `PostToolUse`, `PostInvocation`, `Stop`
- [x] **21 Tệp Python trong `hooks/scripts/`:** `_common.py`, `agy_pretooluse_gate.py`, `agy_stop_gate.py`, `ask_gate.py`, `bash_gate.py`, `codex_edit_gate.py`, `doc_file_gate.py`, `edit_gate.py`, `lsp_gate.py`, `luat_gon.py`, `post_invocation.py`, `prompt_context.py`, `read_gate.py`, `search_gate.py`, `search_observe.py`, `session_start.py`, `stop_batch_checker.py`, `stop_gate.py`, `strategic_compact_gate.py`, `subagent_dispatch_gate.py`, `subagent_start.py`
- [x] **`i18n_check.py` trên 3 hook mới thêm (`_common.py`, `post_invocation.py`, `subagent_dispatch_gate.py`):** `0 Vietnamese line(s) in 3 file(s)` (rc=`0`).
- [x] **Đăng ký đủ 24/24 mã `[TDQ:*]` (`test_all_24_tdq_codes_registered` PASSED):**
  `EDIT`, `TEST`, `TICK`, `DIRTY`, `LOG`, `READ`, `SEARCH`, `NO-PLAN-MODE`, `LSP`, `LSP-WAIT`, `COMPACT`, `GON`, `UNFINISHED`, `PAUSE`, `LECH`, `SETUP`, `SUBAGENT`, `VUNG`, `GATE`, `ANCHOR`, `ZERO-POPUP`, `READONLY`, `SCOPE`, `FEEDBACK`

---

## Mục 7 — Toàn Bộ 14 Edge Cases (`EC-01..EC-14`) & Stress Test NTFS (`V3`)

| Checklist | Mã | Độ nặng | Kịch bản lỗi hiểm hóc | Giải pháp vá | Bằng chứng kiểm thử live |
|---|---|---|---|---|---|
| - [x] | **EC-01** | `P0` | Sửa Brain Artifact (`<appDataDir>/brain/`) làm `edit_gate`/`stop_gate` khóa cứng | Loại trừ `artifactDirectoryPath` & đường dẫn ngoài `cwd` trong `edit_gate.py` / `_common.py` | `test_ec01_to_ec14_live_cmd_hooks` PASSED |
| - [x] | **EC-02** | `P0` | Thiếu `docs/workinglog/YYYY-MM-DD.md` khiến `remind('TDQ:LOG')` `exit(0)` làm chết rào chắn sau | Chuyển `remind()` sang in-memory queue & flush SAU mọi cổng `block()` | `test_ec01_to_ec14_live_cmd_hooks` PASSED |
| - [x] | **EC-03** | `P0` | Subagent chạm `stop_gate.py` bị nhốt vòng lặp vô hạn bởi state của Leader | Nhận diện subagent tất định + đăng ký `sessions.json`; `stop_gate` trả `allow` cho subagent | `test_ec01_to_ec14_live_cmd_hooks` PASSED |
| - [x] | **EC-04** | `P0` | Đánh dấu `[>]` trong `plan.md` làm đổi `plan_sha` khiến `canh_bao_lach_luat` khóa chết worker | Dùng `kiem_tra_stale()` thay `plan_sha` thô trong `tdq_team.py` + `edit_gate.py` | `test_v6_full_10_step_e2e_pipeline` PASSED |
| - [x] | **EC-05** | `P0` | Subagent (`Workspace='inherit'`) sửa nhầm `<main_repo>/src/*` ngoài `.tdq-worktrees/` | Chặn cứng subagent sửa code ngoài `.tdq-worktrees/` khi team worktree đang mở | `test_ec01_to_ec14_live_cmd_hooks` PASSED |
| - [x] | **EC-06** | `P0` | Antigravity không gửi `agent_id` ở stdin khiến subagent lọt rào trước phase `implement` | Suy ra `is_subagent` & `agent_type` theo `conversationId` + khóa phase cho non-implementer | `test_ec01_to_ec14_live_cmd_hooks` PASSED |
| - [x] | **EC-07** | `P0` | 56/65 tool LSP đi qua `call_mcp_tool` bị `lsp_gate.py` & `search_observe.py` bỏ lọt | Unwrap `call_mcp_tool` (`ServerName` + `ToolName` + `Arguments`) thành `mcp_<srv>_<tool>` | `test_ec01_to_ec14_live_cmd_hooks` PASSED |
| - [x] | **EC-08** | `P0` | Cờ approve cũ không xóa khi về `idle`/`report` cho phép tự ý sửa code khi user feedback bug | Thêm cổng `[TDQ:FEEDBACK]` ở `edit_gate.py` & `bash_gate.py` khi `phase in ('idle','report')` | `test_ec01_to_ec14_live_cmd_hooks` PASSED |
| - [x] | **EC-09** | `P1` | `read_file` dùng `StartLine`/`EndLine` inclusive + phân trang `ByteOffset > 0` gây `[TDQ:DOC]` giả | Tính `limit = EndLine - eff_start + 1`; miễn trừ đọc lặp khi `ByteOffset > 0` | `test_ec01_to_ec14_live_cmd_hooks` PASSED |
| - [x] | **EC-10** | `P1` | 8 tiến trình ghi chung `.tdq-turn.jsonl` trên NTFS mất 29.1% dòng | Lockfile + `msvcrt.locking(LK_NBLCK)` retry loop + per-`convId` `.tdq-runtime/` shards | `test_ntfs_8process_320_writes_zero_loss`: **320/320 (0% loss)** |
| - [x] | **EC-11** | `P1` | `session_start.py` gọi `tdq_setup.py` + `claude` gây stall 12.7s & `WinError 206` | Bỏ nhánh đồng bộ Claude/Codex trong `session_start.py` dưới Antigravity | `test_ec01_to_ec14_live_cmd_hooks` PASSED |
| - [x] | **EC-12** | `P1` | `PreInvocation` bắn ở mọi model-step (15 lần/lượt) xóa nhầm turn ledger giữa lượt | Fast-path cho step `2..N` khi `last_user_input_sha` không đổi; giữ nguyên turn ledger | `test_ec01_to_ec14_live_cmd_hooks` PASSED |
| - [x] | **EC-13** | `P1` | Windows `cp1252` crash ở `codex_edit_gate.py`, `luat_gon.py` khi gặp tiếng Việt | Inject `utf8_io` chuẩn + sửa `sys.stdin.buffer.read().decode('utf-8-sig')` | `test_v2_python_ast` + `test_ec01_to_ec14` PASSED |
| - [x] | **EC-14** | `P2` | `transcript.jsonl` của Antigravity double-encode JSON trong `tool_calls[].args` | Unpack `json.loads()` nhiều lớp an toàn trong `tdq_transcript.py` & `_common.py` | `test_real_antigravity_transcript_parsing` PASSED |

---

## Mục 8 — Toàn Bộ 61 Files Trong `scripts/` (60 `.py` + 1 Sample), 7 Excluded & 28 CLI Fixes (`NEW-01..NEW-28`)

- [x] **60 `.py` CLI Runtime Scripts đã xuất & qua `ast.parse`:** `archify_artifacts.py`, `archify_delivery.py`, `archify_model.py`, `claude_export.py`, `context_surface.py`, `doc_dup.py`, `doc_index.py`, `doc_lint.py`, `i18n_check.py`, `kiem_no_marker.py`, `lsp_module.py`, `luat_phan_loai.py`, `plugin_tiers.py`, `scan_block_symbols.py`, `search_replay.py`, `search_rules.py`, `setup_status.py`, `setup_status_render.py`, `skill_inventory.py`, `skill_router.py`, `skill_tokens.py`, `step_audit.py`, `tdq_archify.py`, `tdq_bench.py`, `tdq_checkportable.py`, `tdq_checkstatus.py`, `tdq_codex.py`, `tdq_codex_mcp.py`, `tdq_devtool_mcp.py`, `tdq_eval.py`, `tdq_eval_contract.py`, `tdq_eval_hosts.py`, `tdq_finish.py`, `tdq_graphify.py`, `tdq_harvest.py`, `tdq_knowledge.py`, `tdq_lsp.py`, `tdq_no.py`, `tdq_readiness.py`, `tdq_runtime_bench.py`, `tdq_setup.py`, `tdq_skill_eval.py`, `tdq_state.py`, `tdq_team.py`, `tdq_ten_lenh.py`, `tdq_test.py`, `tdq_test_manifest.py`, `tdq_test_process.py`, `tdq_test_receipt.py`, `tdq_test_report.py`, `tdq_test_result.py`, `tdq_timing.py`, `tdq_transcript.py`, `tdq_transcript_cache.py`, `tdq_vision_diff.py`, `tdq_vungfile.py`, `tdq_worktree_registry.py`, `token_audit.py`, `token_budget.py`, `utf8_io.py`
- [x] **1 Tệp dữ liệu mẫu đi kèm:** `samples/transcript-step-audit.jsonl`
- [x] **7 Scripts dev/canvas nội bộ đã loại khỏi plugin đóng gói (giữ nguyên `tdq_knowledge.py`):** `build_portable.py`, `canvas_a4_ch4_ch7.py`, `canvas_a4_rebuild.py`, `canvas_draw.py`, `canvas_layout_apply.py`, `canvas_move_block.py`, `check_canvas_layout.py`

### Danh Sách 28 Bản Vá CLI Windows & Antigravity (`NEW-01..NEW-28`)

| Checklist | Mã | Độ nặng | Mô-đun mục tiêu | Nội dung vá & ca kiểm thử pytest |
|---|---|---|---|---|
| - [x] | **NEW-01** | `P0` | `tdq_finish.py` | Sửa `.strip()` cắt ký tự đầu đường dẫn `git status` + thêm `-c core.quotepath=false -z` (tiếng Việt) + kiểm tra `agents/` & `rules/` — `test_new01_tdq_finish_vietnamese_z_paths_and_watched_rules` PASSED |
| - [x] | **NEW-02** | `P0` | `lsp_module.py` | Thêm `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8` vào WMI PS + guard không `taskkill` khi path chứa `\ufffd` / `?` — `test_new02_03_04_lsp_module_and_search_rules` PASSED |
| - [x] | **NEW-03** | `P0` | `search_rules.py` | Named regex bắt `mcp_<server>_lsp_<tool>` + nhận diện `run_command`/`Get-ChildItem` + `utf8_io` — `test_new02_03_04_lsp_module_and_search_rules` PASSED |
| - [x] | **NEW-04** | `P0` | `search_rules.py` | Sửa `_tach_script` không báo `malformed` oan cho đường dẫn Windows `"C:\dir\"` & escape `` `n `` PowerShell — `test_new02_03_04_lsp_module_and_search_rules` PASSED |
| - [x] | **NEW-05** | `P0` | `tdq_state.py` + readers | Dùng `utf-8-sig` chống BOM xóa state, thêm `qc_file` vào `default_state()`, retry atomic replace + `PRUNE_DIRS` — `test_new05_tdq_state_hotfix_prune_and_atomic_retry` PASSED |
| - [x] | **NEW-06** | `P0` | `tdq_setup.py` | `doc_phien_ban_plugin()` đọc root `plugin.json` (`0.97.0`) thay vì trả `None` — `test_new06_to_new14...` PASSED |
| - [x] | **NEW-07** | `P0` | `tdq_codex_mcp.py` | Ngăn `khai_hook_codex()` ghi đè `.codex/hooks.json` hỏng từ plugin AGY — `test_new06_to_new14...` PASSED |
| - [x] | **NEW-08** | `P0` | `tdq_harvest.py` + `tdq_knowledge.py` | Đồng bộ `docs/tdq/logs`, `trang_thai:`, tham số `--project` cho cả 4 subparser & quét đệ quy `candidates/`/`approved/` — `test_new06_to_new14...` PASSED |
| - [x] | **NEW-09** | `P1` | `tdq_state.py` & `tdq_codex.py` | Tìm `tdq_codex.py` theo `GOC_PLUGIN` thay vì trong repo đích — `test_new06_to_new14...` PASSED |
| - [x] | **NEW-10** | `P1` | `tdq_team.py` | `canh_bao_lach_luat` dùng `kiem_tra_stale()` thay vì so `plan_sha` thô — `test_new06_to_new14...` PASSED |
| - [x] | **NEW-11** | `P1` | `tdq_team.py` | Thêm `-c core.longpaths=true`, dọn nhánh mồ côi khi lỗi worktree, chuẩn hóa `\` & thêm `rules/`/`.gemini/` — `test_new06_to_new14...` PASSED |
| - [x] | **NEW-12** | `P1` | `skill_tokens.py` | Gỡ bỏ `os.execv()` gây lỗi MSVCRT trên Windows + clean ImportError — `test_new06_to_new14...` + `test_new15_to_new28...` PASSED |
| - [x] | **NEW-13** | `P1` | `skill_inventory.py` | Bổ sung `_agy_plugin_skill_dirs` quét `~/.gemini/config/plugins/` & `<project>/plugins/` — `test_new15_to_new28...` PASSED |
| - [x] | **NEW-14** | `P1` | `tdq_lsp.py` & `tdq_devtool_mcp.py` | Đọc đúng cấu hình `mcp_config.json` của plugin & Antigravity (`~/.gemini/antigravity/mcp_config.json`) — `test_new06_to_new14...` PASSED |
| - [x] | **NEW-15** | `P1` | `tdq_eval.py` | Chuẩn hóa `/` trong `_ghi_ma_nguon` để không nhầm `docs\tdq\plan\*.md` là sửa code — `test_new15_to_new28...` PASSED |
| - [x] | **NEW-16** | `P1` | `tdq-checkportable` | Gỡ bỏ cờ `--trust` đã xóa (`rc=2`) & chuẩn hóa đường dẫn script plugin — `doc_lint.py skills` (`0 violations`) |
| - [x] | **NEW-17** | `P1` | `doc_lint.py` (`rule_r15`) | Bổ sung hỗ trợ từ khóa tiếng Anh (`Touch:`/`Files:`, `Logic:`/`Pseudocode:`) & mốc ngày — `test_new06_to_new14...` PASSED |
| - [x] | **NEW-18** | `P1` | `tdq_setup.py` | Hỗ trợ `py -3`, Windows backslash & gỡ `shlex.split` POSIX khỏi `_RE_LENH_WORKFLOW` — `test_new06_to_new14...` PASSED |
| - [x] | **NEW-19** | `P1` | `tdq_test.py` & `tdq_test_*.py` | Đệ quy `tat_ca_module()`, retry `winerror == 5` trong `tdq_test_process.py`, thêm `.tdq-worktrees/` vào receipt — `test_new15_to_new28...` PASSED |
| - [x] | **NEW-20** | `P2` | `tdq_runtime_bench.py` | Ép `encoding='utf-8-sig'` / `'utf-8'` khi đọc file JSON/text — `test_new15_to_new28...` PASSED |
| - [x] | **NEW-21** | `P2` | `tdq_eval_hosts.py` / `tdq_ten_lenh.py` | Nhận diện host `antigravity` & dọn đường dẫn kiểm thử — `test_new15_to_new28...` PASSED |
| - [x] | **NEW-22** | `P2` | `tdq_codex.py` | Bọc `_cli_run()` với `CREATE_NO_WINDOW` & `OwnedProcessJob` cleanup — `test_v2_python_ast` PASSED |
| - [x] | **NEW-23** | `P2` | `tdq_graphify.py` & `archify_artifacts.py` | Thêm `.gemini`, `.agents`, `.tdq-worktrees` vào `OUTPUT_DIRS` / `EXCLUDED_DIR_NAMES` — `test_new15_to_new28...` PASSED |
| - [x] | **NEW-24** | `P2` | `tdq_checkstatus.py` & `scan_block_symbols.py` | Chấp nhận `py -3 scripts/tdq_state.py` & lọc `SCOPE` chỉ qua các file tồn tại — `scan_block_symbols.py --chi-khoi` (`rc=0`, empty stderr) |
| - [x] | **NEW-25** | `P2` | `tdq_worktree_registry.py` & `tdq_bench.py` | Gỡ lệnh POSIX-only trong recovery & bổ sung `utf8_io` — `test_new15_to_new28...` PASSED |
| - [x] | **NEW-26** | `P2` | `tdq_eval_contract.py` & `evals/` compatibility | Thêm host `antigravity` hợp lệ trong contract schema — `test_new15_to_new28...` PASSED |
| - [x] | **NEW-27** | `P3` | `tdq_transcript.py` & `tdq_timing.py` | Đọc `<appDataDir>/brain/<id>/.system_generated/logs/transcript.jsonl` + unpack double-JSON `args` — `test_real_antigravity_transcript_parsing` PASSED |
| - [x] | **NEW-28** | `P3` | 18+ standalone CLI scripts | Inject `import utf8_io` hàng loạt chống crash `cp1252` trên console Windows — `test_v2_python_ast` (`81` `.py` AST OK) |

---

## Mục 9 — Chuỗi Kiểm Chứng E2E 10 Bước Toàn Vòng Đời (`V6`: `test_v6_full_10_step_e2e_pipeline`)

| Checklist | Bước E2E | Hành động thực thi trên Git repo cô lập | Kết quả kiểm chứng |
|---|---|---|---|
| - [x] | **Bước 1** | `tdq_state.py init` + `set lane=full slug=calc-demo phase=spec` (commit baseline `calc.py` + `test_calc.py`) | Exit `0`, khởi tạo `docs/tdq/STATE.md` & `state.json` |
| - [x] | **Bước 2** | Sinh Spec có `## 2b. Ranh giới module` & bảng `§3b` -> `tdq_state.py approve spec --by "approve spec"` | Exit `0`, ghi nhận phê duyệt Spec |
| - [x] | **Bước 3** | Sinh Plan có Task `T1.1` (`Chạm:`, `Logic:`) -> `doc_lint.py --pair` -> `approve plan --mode subagent` -> `set phase=implement` | `doc_lint --pair` exit `0`, commit sạch trước khi mở worktree |
| - [x] | **Bước 4** | `tdq_team.py assign` -> `audit` -> `wave` -> `open T1.1` | Tạo thành công worktree `.tdq-worktrees/calc-demo/t1.1` & nhánh `tdq/calc-demo/t1.1` |
| - [x] | **Bước 5** | Chạy `pytest -B` trong worktree (**RED** fail `subtract` -> sửa `return a + b` -> **GREEN** pass -> `git commit`) | Xác nhận `RED != 0` trước sửa và `GREEN == 0` sau sửa |
| - [x] | **Bước 6** | Gọi hook `edit_gate.py` ghi ngoài vùng (`secret_extra.py`) -> bị chặn `deny` `[TDQ:VUNG]`; tiếp theo `tdq_team.py check/merge/clean` | Merge về `main`, dọn sạch `.tdq-worktrees/calc-demo`, code `src/calc.py` đạt `return a + b` |
| - [x] | **Bước 7** | Tick `[x]` Task `T1.1` & `DoD-1` trong Plan -> `set phase=qc` -> chạy QC `pytest tests/test_calc.py` | Exit `0`, QC xanh 100% |
| - [x] | **Bước 8** | Chuyển `phase=report` -> xuất Báo cáo 4 mục -> chạy `tdq_harvest.py scan --project` & `tdq_knowledge.py check` | Exit `0`, kiểm tra đầy đủ schema knowledge/harvest |
| - [x] | **Bước 9** | Chạy `tdq_finish.py --files src/calc.py --log "Completed calc-demo"` | Exit `0`, ghi worklog ngày & chạy chốt hậu kiểm |
| - [x] | **Bước 10** | `tdq_state.py set phase=idle` -> `tdq_state.py get` xác nhận `phase == "idle"` & `.tdq/worktrees` trống sạch | Exit `0`, đóng vòng đời an toàn tuyệt đối |

---

## Mục 10 — Bằng Chứng An Toàn Upstream Read-Only & Bất Biến Cấu Hình Toàn Cục

- [x] **Kho gốc Read-Only (`C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow`):** `HEAD` giữ nguyên `b423ee06`; **`upstream_code_clean: True`** (`git status --short -- plugins/ .claude-plugin/ scripts/ hooks/ tools/` rỗng hoàn toàn). *(Ghi chú minh bạch: `upstream_clean` trả `false` do kho gốc vốn có sẵn 6 tệp `docs/` WIP từ `2026-11-11` trước khi kiểm toán, hoàn toàn không có thay đổi nào do workspace này gây ra.)*
- [x] **Cấu hình Antigravity toàn cục (`~/.gemini/config/config.json`):** `exists: True`, SHA-256 trước và sau kiểm chứng giữ nguyên bất biến `3525858d7521b7b54147410e29966dd58325604676e7befefb7df67f2b03a646`.
- [x] **Discovery cục bộ an toàn (`.agents/plugins.json`):** `{"entries": [{"path": "./plugins"}]}`

---

### Phụ Lục — Toàn Bộ 14 Test Cases Đã Chạy (`pytest tests/ -v --basetemp=.pytest_tmp`)

1. - [x] `tests/test_agy_plugin_validate.py::test_v1_agy_plugin_validate_strict_json` — **PASSED**
2. - [x] `tests/test_agy_plugin_validate.py::test_v1_install_dry_run_and_staged_validate` — **PASSED**
3. - [x] `tests/test_agy_plugin_validate.py::test_v2_python_ast_and_md_budgets_and_no_traps` — **PASSED**
4. - [x] `tests/test_cli_fixes_new01_28.py::test_new01_tdq_finish_vietnamese_z_paths_and_watched_rules` — **PASSED**
5. - [x] `tests/test_cli_fixes_new01_28.py::test_new02_03_04_lsp_module_and_search_rules` — **PASSED**
6. - [x] `tests/test_cli_fixes_new01_28.py::test_new05_tdq_state_hotfix_prune_and_atomic_retry` — **PASSED**
7. - [x] `tests/test_cli_fixes_new01_28.py::test_new06_to_new14_setup_lsp_codex_harvest_knowledge_devtool_team_doclint` — **PASSED**
8. - [x] `tests/test_cli_fixes_new01_28.py::test_new15_to_new28_transcript_eval_hosts_test_isolation_tokens` — **PASSED**
9. - [x] `tests/test_e2e_workflow.py::test_v5_live_mcp_agent_lsp_stdio_and_7_companion_extensions` — **PASSED**
10. - [x] `tests/test_e2e_workflow.py::test_v6_full_10_step_e2e_pipeline` — **PASSED**
11. - [x] `tests/test_hooks_dual_protocol.py::test_all_24_tdq_codes_registered` — **PASSED**
12. - [x] `tests/test_hooks_dual_protocol.py::test_ec01_to_ec14_live_cmd_hooks` — **PASSED**
13. - [x] `tests/test_ntfs_concurrency.py::test_ntfs_8process_320_writes_zero_loss` — **PASSED**
14. - [x] `tests/test_ntfs_concurrency.py::test_real_antigravity_transcript_parsing` — **PASSED**
