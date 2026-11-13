# Exhaustive Line-by-Line Rescan Report: `scripts/`, `portable_src/`, `tools_kiem/`, and `evals/`

- **Target Repository Audited (Read-Only):** `C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow` (`v0.97.0`)
- **Baseline Compared Against:**
  - `c:\Users\admin\Documents\Projects\TDQ-Workflow-Antigravity\docs\AUDIT-AND-PORTING-PLAN.md`
  - `c:\Users\admin\Documents\Projects\TDQ-Workflow-Antigravity\docs\research\04-antigravity-adapter-audit.md`
  - `c:\Users\admin\Documents\Projects\TDQ-Workflow-Antigravity\docs\research\05-cli-e2e-and-extensions-audit.md`
- **Empirical Verification Harness:** `C:\Users\admin\.gemini\antigravity\brain\2a408580-dde6-4a41-aeda-5a1f871c0366\scratch\rescan_b\verify_bugs.py` -> `verify_output.txt` (`rc=0`, strictly read-only on source repo)

---

## 0. Executive Summary & 100% Coverage Proof

### Exact File Inventory Audited Line-by-Line
| Directory | Total Files | `.py` Files | Coverage | Notes |
|---|---:|---:|---|---|
| `scripts/` | **68** | **67** | **100% (68/68)** | Note: `scripts/` actually contains **67** `.py` files (plus `scripts/samples/transcript-step-audit.jsonl`), 9 more than the initial ~58 estimate. Every single file was read line-by-line. |
| `portable_src/` | **1** | **0** | **100% (1/1)** | `portable_src/skills/tdq-checkportable/SKILL.md` |
| `tools_kiem/` | **1** | **1** | **100% (1/1)** | `tools_kiem/dem_da_nen_tang.py` |
| `evals/` | **474** | **8** | **100% of `.py`, configs, README, corpus & seeds** | All 8 `.py` scripts, `tuan-thu/README.md`, all 12 `ca.json` + seed specs/plans, `tdq-upgrade-offline.json`, `skill-quality/corpus.json`, `photoboth360_precision_gold.json`. |

### Headline Result: 28 Newly Discovered Bugs / Missed Gaps Beyond `AUDIT-AND-PORTING-PLAN.md`

While `AUDIT-AND-PORTING-PLAN.md` captured the primary `build_portable.py` bundle issues (`G1–G25`), this exhaustive line-by-line rescan + live Windows empirical suite uncovered **28 previously undocumented bugs and porting blockers** across `scripts/`, `portable_src/`, `tools_kiem/`, and `evals/` — including **8 P0 Critical** and **11 P1 High** defects that silently corrupt data, kill live LSP daemons, skip linting, false-deny PowerShell commands, or break Antigravity setup/hooks/evals.

| ID | Sev | File : Line | Summary of Newly Discovered Bug (Missed or Incomplete in Prior Plan) | Empirical Proof |
|---|---|---|---|---|
| **NEW-01** | **P0** | `scripts/tdq_finish.py:73, 86-93, 179` | **`_run()` `.strip()` slices off 1st character of 1st unstaged filename** (`" M docs/..."` -> `"ocs/..."`), silently skipping `doc_lint.py` and `token_budget.py`! Also lacks `-z` / `-c core.quotepath=false` (breaks Vietnamese filenames) and `step_khoa_token` (`L179`) misses `agents/`, `rules/`, `GEMINI.md`. | **PROVEN (E2)** |
| **NEW-02** | **P0** | `scripts/lsp_module.py:503-521, 560, 580` | **PowerShell `IBM437` stdout pipe mangles non-ASCII `--root-dir` -> `don_broker()` `taskkill /F` kills LIVE `agent-lsp` brokers!** `tdq_lsp._run` uses `CREATE_NO_WINDOW`, causing PS 5.1 `[Console]::OutputEncoding` to default to `IBM437` (`DựÁn` -> `D?An`), failing `os.path.isdir()`. | **PROVEN (E4)** |
| **NEW-03** | **P0** | `scripts/search_rules.py:868, 887, 31, 682` | **Double LSP bug + Antigravity tool blindness:** Prior plan noted `L868` regex, but **missed `L887`** (`cuoi = re.split(r"__|\.", ten)[-1]`), which STILL fails to extract `find_references` from `mcp_tdq-workflow_lsp_find_references`! Also `phan_loai` (`L31, 682`) completely ignores Antigravity's `run_command` (`CommandLine`), `grep_search`, and `find_by_name`. | **PROVEN (E5a,b)** |
| **NEW-04** | **P0** | `scripts/search_rules.py:261-285, 342, 756-826` | **Windows PowerShell valid commands HARD-DENIED in ALL phases:** `_tach_script` treats `\` inside `"..."` as POSIX escape and `` ` `` as POSIX command substitution -> `la_malformed=True` -> `status="unknown"` -> `quyet_dinh()` **hard-blocks** `Get-ChildItem "C:\Users\admin\"` and ``Write-Host "a`nb"`` even in `analyze`! | **PROVEN (E5c)** |
| **NEW-05** | **P0** | `scripts/tdq_state.py:409-427` (+ `tdq_checkstatus.py:281`, `tdq_test.py:492`, `doc_lint.py:155,607,684`) | **UTF-8 BOM on `state.json` destroys active workflow state!** PowerShell 5.1 `Set-Content -Encoding UTF8` writes BOM (`\xef\xbb\xbf`); `tdq_state.load()` uses `encoding="utf-8"`, catches `JSONDecodeError`, **renames `state.json` to `state.json.corrupt-<ts>`**, and resets workflow to `None`! | **PROVEN (E6a)** |
| **NEW-06** | **P0** | `scripts/tdq_setup.py:1495-1507, 1510-1585` | **`doc_phien_ban_plugin()` ignores Antigravity root `plugin.json`:** Checks ONLY `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`. Returns `None` inside an installed Antigravity plugin, breaking version-stamp checks and raising `OSError("Setup version stamp was not written")` at `L1584`. | **PROVEN (E3)** |
| **NEW-07** | **P0** | `scripts/tdq_codex_mcp.py:154, 237-309` | **Called from AGY bundle, `khai_hook_codex()` writes broken hooks into `<project>/.codex/hooks.json`:** Points to `<agy-bundle>/hooks/scripts/*.py` (which does not exist in AGY bundle!) with `python3`, breaking Codex CLI in that project! | **PROVEN (E7f)** |
| **NEW-08** | **P0** | `scripts/tdq_harvest.py:20-21, 76, 98-104, 175` vs `scripts/tdq_knowledge.py:22, 126-146, 180` | **Triple broken contract between `tdq_harvest.py` and `tdq_knowledge.py`:** (1) `tdq_harvest` scans `docs/workinglog/*.md` instead of `docs/tdq/logs/*.md`; (2) writes `status: candidate`/`approved` while `tdq_knowledge` requires `trang_thai: candidate`/`reviewed` + `nguoi_duyet`/`ngay_duyet`/`evidence`; (3) `tdq_knowledge check <dir>` is non-recursive, missing `candidates/` and `approved/`. | **PROVEN (E7a)** |
| **NEW-09** | **P1** | `scripts/tdq_state.py:1584-1587` & `scripts/tdq_codex.py:654-690` | **`codex` execution mode is broken in external user repos:** `tdq_state._probe_codex(root)` checks `os.path.join(root, "scripts", "tdq_codex.py")` in user `cwd` instead of `GOC_PLUGIN`! Likewise `tdq_codex.kiem_hook_ban(cwd)` checks `cwd/hooks/scripts/codex_edit_gate.py`. | **PROVEN (E6b)** |
| **NEW-10** | **P1** | `scripts/tdq_team.py:1615` (vs `L327-336`) | **`canh_bao_lach_luat()` ignores projection v1 (`kiem_tra_stale`) and compares raw `plan_sha`:** Ticking `- [>]` on any task changes `sha_file(plan)` while `kiem_tra_stale()` is `False`, causing `canh_bao_lach_luat` to emit false `"chua-phan-cong"` warnings on **every** file edit! | **PROVEN (E6c)** |
| **NEW-11** | **P1** | `scripts/tdq_team.py:49, 71-72, 178, 1188` | **Windows backslash & Antigravity blind spots in `tdq_team.py`:** `_PATH` (`L49`) and `"/" in duong` (`L178`) drop backticked `src\foo.py`; `TIEN_TO_FILE_LUAT` (`L71`) omits `rules/`, `.gemini/`, `.agents/`, `GEMINI.md`, `plugin.json`, `mcp_config.json`; `chay_test_task` (`L1188`) only rewrites `python3` at token 0 (`cd app && python3 -m pytest` fails!). | **PROVEN (E6d)** |
| **NEW-12** | **P1** | `scripts/skill_tokens.py:49-50, 138, 237` | **`nhay_sang_venv()` (`L138`) calls `os.execv()` on Windows + Unix `.venv-tokens/bin/pip` hint:** On Windows MSVCRT, `os.execv` spawns an asynchronous background child without argument quoting and exits the parent immediately, breaking exit codes, stdout pipes, and paths with spaces! | Static + Win32 spec |
| **NEW-13** | **P1** | `scripts/skill_inventory.py:161-203, 236-243` | **100% blind to Antigravity skills:** Scans ONLY `.claude/skills`, `~/.claude/skills`, and `~/.claude/plugins/installed_plugins.json`. Completely misses `.agents/skills/`, `.gemini/antigravity/skills/`, and `~/.gemini/config/plugins/*/skills/`. | Static verified |
| **NEW-14** | **P1** | `scripts/tdq_timing.py:368` & `scripts/tdq_transcript.py:58-62, 108-110, 249-266, 528` | **100% blind to Antigravity transcripts:** `--host` only accepts `("auto", "claude", "codex")`. Cannot locate or parse Antigravity's `<appDataDir>\brain\<conv-id>\.system_generated\logs\transcript.jsonl` (`USER_INPUT` / `PLANNER_RESPONSE` / `tool_calls`). `tdq_timing.py` always fails with `"timing unavailable"` on AGY. | Static verified |
| **NEW-15** | **P1** | `scripts/tdq_eval.py:184-196, 351-354, 475, 555, 581, 745, 1125-1275, 1481` & `tdq_eval_hosts.py:20` & `tdq_eval_contract.py:113-126` | **Eval suite broken for Antigravity & Windows:** `SUPPORTED_HOSTS` lacks `antigravity`; `tdq_eval.py` misses `run_command`/`CommandLine` and `write_file`/`edit_file`/`read_file` capital `Path`/`Content`; Windows backslash paths in `_ghi_ma_nguon` (`L555`) falsely classify `docs\tdq\plan\*.md` as **source code writes**; `lenh_chay` (`L1481`) hard-fails on Windows via macOS Keychain `lay_token()`. | **PROVEN (E7c)** |
| **NEW-16** | **P1** | `portable_src/skills/tdq-checkportable/SKILL.md:21-50` & `scripts/tdq_checkportable.py:296` | **Skill instructs running `tdq_checkportable.py setup --trust` -> crashes with `rc=2 unrecognized arguments: --trust`!** Also `SKILL.md` tells agent to inspect `.claude/settings.json` & `.mcp.json` (absent in AGY), and `tdq_checkportable.py:296` prints dead flag `setup --codex`. | **PROVEN (E7b)** |
| **NEW-17** | **P1** | `scripts/doc_lint.py:526-568` (`rule_r15`) | **v0.97.0 `R15` breaks backward compatibility + misses English `doc_lang=en`:** Unlike `R11`/`R14`, `rule_r15` has **no slug date cutoff** — **6/6** existing `evals/tuan-thu/*/seed/docs/tdq/plan/*.md` fail `R15`! Also checks only Vietnamese `chạm:`/`cham:` (ignoring English `touch:`/`files:`), misses `.h/.hpp/.kt/.swift/.mjs/.cjs/.mts` and `Pseudocode:`, and is trivially bypassed if prose contains `"logic"`. | **PROVEN (E7d)** |
| **NEW-18** | **P1** | `scripts/tdq_setup.py:119, 252, 804, 995-996, 1025, 1809, 1848` | **`tdq_setup.py` Windows & AGY failures:** `shlex.split` (`L119, 1809`) corrupts unquoted Windows paths, UNC `\\server\...` paths, and trailing-`\` paths; `_RE_LENH_WORKFLOW` (`L252`) fails on Windows `\` paths & `py -3`; `kiem_dryrun_hook` (`L1025`) tests absent `hooks/scripts/prompt_context.py`; `ghim_huong_dan_tool` (`L1848`) writes `~/.claude/CLAUDE.md` only and has dead unreachable code at `L996`. | **PROVEN (E3)** |
| **NEW-19** | **P1** | `scripts/tdq_test.py:97, 130-136, 887` & `tdq_test_process.py:245` & `tdq_test_receipt.py:29-33` | **`tdq_test.py` `tat_ca_module()` (`L130`) uses flat `os.listdir(tests_dir)` while `_result_inventory()` (`L887`) uses `os.walk`:** `ban_kinh` misses nested `tests/sub/test_*.py`! `TOP_DIRS` (`L97`) omits `rules/`; `tdq_test_process.py:245` temp cleanup retries `winerror==32` only, missing `winerror==5` (`Access Denied` on `.git/objects/pack` read-only files). | Static verified |
| **NEW-20** | **P2** | `scripts/tdq_runtime_bench.py:260, 382, 455, 466, 467` | **Missing `encoding="utf-8"` on `Path.read_text()` (`L260, 382, 455`) and child `open(..., 'w')` (`L466`):** Crashes with `UnicodeDecodeError` (`cp1252`) if test files contain Vietnamese/UTF-8 text! Missed by `tools_kiem/dem_da_nen_tang.py` because its AST checker only inspects bare `open()`. | Static verified |
| **NEW-21** | **P2** | `tools_kiem/dem_da_nen_tang.py:27-31, 108, 158` | **Broken multi-platform gate script:** Checks deleted `portable_codex/.codex/hooks.json` and `antigravity_portable/hooks.json`; misses `Path.open`/`read_text`/`write_text`; lacks `utf8_io` (`ensure_ascii=False` crashes if stdout is `cp1252` with non-ASCII output). | **PROVEN (E1)** |
| **NEW-22** | **P2** | `scripts/tdq_codex.py:887-898` | **`_cli_run()` bypasses `OwnedProcessJob` and lacks `CREATE_NO_WINDOW`:** On timeout (`subprocess.TimeoutExpired`), `codex.cmd` (`cmd.exe /c node ...`) leaves orphaned `node.exe` / Codex child processes running on Windows! | Static verified |
| **NEW-23** | **P2** | `scripts/tdq_graphify.py:38-43` & `archify_artifacts.py:32-41` & `tdq_state.py:312-313` | **Incomplete directory exclusion sets cause false `stale` / false `stray state` warnings:** `tdq_graphify.OUTPUT_DIRS` omits `docs/tdq`, `.tdq-worktrees`, `dist`, `build` (every `state.json` update marks full Graphify `stale`!); `archify_artifacts.EXCLUDED_DIR_NAMES` omits `.gemini`, `.agents`, `.worktrees`; `tdq_state.PRUNE_DIRS` omits `.tdq-worktrees`, `.worktrees`, `.gemini`, `.agents`. | Static verified |
| **NEW-24** | **P2** | `scripts/context_surface.py:120, 132, 170-259` & `scan_block_symbols.py:42-44` | **Stale portable paths & non-recursive globs:** `context_surface.py` globs `references/*.md` non-recursively (missing `references/rules/*.md`) and deleted `portable/**/*.md`; `scan_block_symbols.py` allowlists deleted `portable/workflow/*` files. | Static verified |
| **NEW-25** | **P2** | `scripts/tdq_worktree_registry.py:41-119, 327` & `tdq_bench.py:120, 178-241` | **POSIX-only commands in recovery/bench templates:** `tdq_worktree_registry.py` outputs `mv`, `ls -la`, `&&`, unquoted paths; `tdq_bench.py:120` uses `Test: \`true\`` (POSIX `/bin/true`, fails on Windows) and `mkdir -p` / `python3`. | Static verified |
| **NEW-26** | **P2** | `evals/audit_*.py`, `evals/tuan-thu/README.md`, `evals/skill-quality/corpus.json` | **7 CLI/test scripts in `evals/` + `tools_kiem/` lack `utf8_io`:** `audit_photoboth360_50_tests.py` uses `subprocess.run(..., text=True)` without `encoding="utf-8"` and hardcodes `C:\Users\admin\Documents\Photoboth360`; `audit_photoboth360_precision.py:314` `open("x")` crashes on re-run; `corpus.json:141` cites non-existent `hooks/tdq_hook.py`. | **PROVEN (E1)** |
| **NEW-27** | **P3** | `scripts/tdq_vungfile.py`, `tdq_archify.py`, `archify_artifacts.py`, `archify_delivery.py`, `tdq_bench.py`, `tdq_runtime_bench.py` | **Missing `subprocess.CREATE_NO_WINDOW` on Windows `git`/`node`/child subprocess calls:** Causes transient console window flashes when invoked from GUI/IDE background tasks on Windows. Also `tdq_vungfile.py` lacks `-c core.quotepath=false`. | Static verified |
| **NEW-28** | **P3** | `scripts/tdq_vision_diff.py:42, 52` & `canvas_*.py` | **`tdq_vision_diff.py` hardcodes `python3` in `FIGMA_PAUSE_HINT` (`L52`)** and imports external `PIL` (`Pillow`) at module top-level (`L42`, though Pillow IS installed on current machine). `canvas_a4_rebuild.py:211,365` uses unclosed `open()` handles; `canvas_a4_ch4_ch7.py:84,92` hardcodes `python3` and `Claude Agent`. | **PROVEN (E7e)** |

---

## 1. Deep-Dive & Live Empirical Proofs for Top Newly Discovered Bugs

All empirical proofs below were executed safely inside `scratch/rescan_b/verify_bugs.py` (`PYTHONDONTWRITEBYTECODE=1`) against `TDQ-Workflow` without modifying a single byte of the source repo.

### 1.1 [NEW-01 / P0] `tdq_finish.py` First-Character Filename Slicing & Unicode Quotepath Bug
- **Location:** `scripts/tdq_finish.py:73` (`_run`) and `scripts/tdq_finish.py:86-93` (`_changed_files`), plus `L179` (`step_khoa_token`).
- **Root Cause:**
  1. `_run()` returns `(p.stdout + p.stderr).strip()`.
  2. When the first file in `git status --porcelain` has an unstaged worktree modification (the normal case at the end of a turn: `" M docs/tdq/spec/2026-11-13-demo.md\n"`), `.strip()` strips the leading space (`"M docs/tdq/spec/2026-11-13-demo.md"`).
  3. `_changed_files()` then slices `path = line[3:].strip()` (`L87`), chopping off the `'d'` in `docs/` -> `"ocs/tdq/spec/2026-11-13-demo.md"`!
  4. `step_lint()` (`L107`) checks `os.path.exists(f)` -> `False` -> **silently skips linting the modified Markdown file (`status='skip', detail='no .md file'`)**! Similarly, if `skills/...` is first (`"kills/..."`), `step_khoa_token()` skips regenerating `token-budget.json`.
  5. Additionally, `git status --porcelain` is run without `-z` or `-c core.quotepath=false`, so any Vietnamese filename (`báo_cáo.md`) is octal-quoted (`"docs/tdq/spec/b\\303\\241o_c\\303\\241o.md"`), `line[3:].strip().strip('"')` leaves literal `\303\241`, and `os.path.exists()` returns `False`!
  6. Finally, `step_khoa_token()` (`L179`) only checks `f"{os.sep}skills{os.sep}" in f`, ignoring edits to `agents/*.md`, `rules/*.md`, `CLAUDE.md`, or `GEMINI.md`.
- **Live Empirical Output (`verify_output.txt` §E2):**
  ```text
  Raw git status --porcelain: ' M docs/tdq/spec/2026-11-13-demo.md\n'
  tdq_finish._changed_files(): ['...\\finish_repo\\ocs/tdq/spec/2026-11-13-demo.md']
  Does returned path exist?    [False]
  tdq_finish.step_lint():      name='lint', status='skip', detail='no .md file'
  With Vietnamese untracked file: ['...\\ocs/tdq/spec/2026-11-13-demo.md', '...\\docs/tdq/spec/b\\303\\241o_c\\303\\241o.md']
  Exists check on Vietnamese path: [False, False]
  ```
- **Porting Fix:** Use `git -c core.quotepath=false status --porcelain -z` (or `.rstrip("\r\n")` instead of `.strip()` in `_run` when parsing porcelain output — compare `tdq_archify.py:73-103` `_get_git_dirty_files` which already parses `-z` properly!), and expand `step_khoa_token` to check `skills`, `agents`, `rules`, `CLAUDE.md`, `GEMINI.md`.

---

### 1.2 [NEW-02 / P0] `lsp_module.py` PowerShell `IBM437` Encoding Corrupts Paths & Kills Live `agent-lsp` Brokers
- **Location:** `scripts/lsp_module.py:500-521` (`_doc_tien_trinh_mac_dinh`), `L550-568` (`broker_mo_coi`), `L571-585` (`_tat_mac_dinh`, `don_broker`).
- **Root Cause:**
  - On Windows (`os.name == "nt"`), `_doc_tien_trinh_mac_dinh()` runs `powershell -NoProfile -Command "$ps = Get-CimInstance Win32_Process ... | ConvertTo-Json -Compress"` via `tdq_lsp._run()` (`CREATE_NO_WINDOW`).
  - Without a console or explicit `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8`, Windows PowerShell 5.1 writes stdout using `IBM437`!
  - Any project path containing Vietnamese or non-ASCII characters (`DựÁn_TiếngViệt`) has its `CommandLine` mangled to `D?An_Ti?ngVi?t` in JSON stdout.
  - `broker_mo_coi()` (`L560`) checks `if not os.path.isdir(b["goc"]): mo_coi.append(b)` — **ignoring `cha_song: True`!** Because `D?An_Ti?ngVi?t` is not a directory on disk, `don_broker()` (`tdq_lsp.py don-rac` / `tdq_setup.py`) executes `taskkill /PID <pid> /F` on a **LIVE** `agent-lsp daemon-broker`!
- **Live Empirical Output (`verify_output.txt` §E4):**
  ```text
  Real directory on disk:       '...\\tmp_empirical\\DựÁn_TiếngViệt' (isdir=True)
  [Console]::OutputEncoding.WebName : IBM437
  liet_ke_broker() entry:       [{'pid': 99999, ..., 'cha_song': True, 'goc': '...\\D?An_Ti?ngVi?t', 'lang': ''}]
  broker_mo_coi() result:       [{'pid': 99999, ..., 'cha_song': True, 'goc': '...\\D?An_Ti?ngVi?t', 'lang': ''}]
  ```
- **Porting Fix:**
  1. Prefix the PowerShell command in `lsp_module.py:504` with `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; `.
  2. Guard `broker_mo_coi()` (`L560`): never classify a path containing `'?'` or `\ufffd` (encoding replacement chars) as a missing-directory orphan, or require `not b.get("cha_song", True)` when path chars are uncertain.

---

### 1.3 [NEW-03 & NEW-04 / P0] `search_rules.py` Double LSP Split Bug, Antigravity Tool Blindness & PowerShell False-Deny
- **Location:** `scripts/search_rules.py:31` (`CONG_CU_SHELL`), `L261-285` (`_tach_script`), `L342` (`_tach_tu`), `L682` (`phan_loai`), `L756-826` (`quyet_dinh`), `L868 & 887` (`la_goi_khai_niem`).
- **Root Causes:**
  1. **Double LSP Bug (`L868` + `L887`):** `AUDIT-AND-PORTING-PLAN.md` (`G8`) noted `LSP = re.compile(r"^mcp__[^_]*lsp[^_]*__|^lsp[._]", re.I)` at `L868`, **but missed `L887`:**
     ```python
     cuoi = re.split(r"__|\.", ten)[-1]
     return "lsp" if LSP_HOI.match(cuoi) else None
     ```
     Antigravity names MCP tools `mcp_<serverName>_<toolName>` (single underscore!), e.g. `mcp_tdq-workflow_lsp_find_references` or `mcp_lsp_find_references`. Even if `L868` is updated, `re.split(r"__|\.", ten)[-1]` returns the **entire** string `'mcp_tdq-workflow_lsp_find_references'`, which fails `LSP_HOI.match(cuoi)` (`^(workspace_symbol|find_references|...)$`) and STILL returns `None`!
  2. **Antigravity Tool Names Bypassed (`L31, 682`):** `CONG_CU_SHELL` only contains `{"bash", "exec_command", "shell", "shell_command", "container.exec"}` — missing Antigravity's `run_command` (which passes `{"CommandLine": ...}`, whereas `_script_cua` only checks `"command"`/`"cmd"`). And `L682` checks `if cong_cu == "Grep":` — missing Antigravity's `grep_search` (`Query`, `SearchPath`) and `find_by_name`.
  3. **PowerShell False-Deny in ALL Phases (`L261-285, 342, 756, 821`):** `_tach_script` uses POSIX double-quote backslash escaping (`\` escapes `"` in `"C:\Users\admin\"`, leaving the quote unclosed -> `ngan_sach.la_malformed = True`) and treats PowerShell's escape character `` ` `` (e.g. ``Write-Host "line1`nline2"``) as POSIX backtick command substitution (`la_malformed = True`). Then `quyet_dinh()` (`L821`) unconditionally denies `status == "unknown"` — blocking non-search PowerShell commands (`Get-ChildItem`, `python`, `Write-Host`) across **every** phase!
- **Live Empirical Output (`verify_output.txt` §E5):**
  ```text
  la_goi_khai_niem('mcp_tdq-workflow_lsp_find_references') -> None
  L887 re.split(r'__|\.', 'mcp_tdq-workflow_lsp_find_references')[-1] -> 'mcp_tdq-workflow_lsp_find_references' (LSP_HOI match=False)
  Bash('grep -rn foo src/')        -> allowed=False
  run_command('grep -rn foo src/') -> allowed=True  <-- BYPASSED!
  Bash('Get-ChildItem "C:\\Users\\admin\\"') -> allowed=False, status='unknown', reason='malformed' | [TDQ:SEARCH] Command could not be parsed safely (malformed).
  Bash('Write-Host "line1`nline2"') -> allowed=False, status='unknown', reason='malformed' | [TDQ:SEARCH] Command could not be parsed safely (malformed).
  Bash('python "C:\\Users\\admin\\scripts\\"') -> allowed=False, status='unknown', reason='malformed' | [TDQ:SEARCH] Command could not be parsed safely (malformed).
  ```
- **Porting Fix:**
  - In `la_goi_khai_niem` (`L868-888`), match `^mcp_[A-Za-z0-9_-]*lsp[A-Za-z0-9_-]*_(?P<op>workspace_symbol|find_references|goto_definition|...)` directly via named regex group (do not rely on `__` splitting!). Also update Graphify/CodeSight regexes (`L866-869`) for single-underscore `mcp_<server>_<tool>`.
  - Add `"run_command"` to `CONG_CU_SHELL`, extract `CommandLine` in `_script_cua()`, and handle `grep_search` (`Query`/`SearchPath`).
  - Add Windows/PowerShell lexing mode (when `os.name == "nt"` or PowerShell syntax detected): do not treat `\"` at end of `C:\path\"` as escaped quote unless preceded by non-path context, and inside PowerShell `"..."` treat `` `n ``, `` `r ``, `` `t ``, `` `" ``, `` `$ `` as character escapes rather than POSIX command substitution `( `...` )` unless `` ` `` appears as paired command substitution or `$()`!

---

### 1.4 [NEW-05 / P0] UTF-8 BOM Destroys `state.json` (`tdq_state.py:409-427`)
- **Location:** `scripts/tdq_state.py:409` (`load`), plus `L594, 796, 874, 929, 1061, 2328`; `scripts/tdq_checkstatus.py:281`; `scripts/tdq_test.py:492`; `scripts/doc_lint.py:155, 607, 684`; `scripts/tdq_skill_eval.py:46`; `scripts/tdq_archify.py:612, 718, 773`.
- **Root Cause:** On Windows PowerShell 5.1 (the default shell in Antigravity on Windows!), `Set-Content -Encoding UTF8` and `Out-File -Encoding UTF8` prepend a 3-byte UTF-8 BOM (`\xef\xbb\xbf`). Python's `json.loads()` rejects BOM with `JSONDecodeError: Unexpected UTF-8 BOM` unless opened with `encoding="utf-8-sig"`. Worse, `tdq_state.load(heal=True)` treats `ValueError` (parent of `JSONDecodeError`) as file corruption, **renaming the user's valid `state.json` to `state.json.corrupt-<timestamp>`** and returning `None`!
- **Live Empirical Output (`verify_output.txt` §E6a):**
  ```text
  [2026-11-13T17:29:58+07:00] ⚠️ state.json is corrupt → kept at state.json.corrupt-20261113-172958; state rebuilt from defaults.
  After UTF-8 BOM state.json -> tdq_state.load() returned: None
  Files in docs/tdq/ after load(): ['state.json.corrupt-20261113-172958']
  ```
- **Porting Fix:** Standardize all JSON/Markdown/config readers across `scripts/` onto `encoding="utf-8-sig"` (while keeping writers on `encoding="utf-8"` so TDQ never emits BOMs).

---

### 1.5 [NEW-06, NEW-07, NEW-18 / P0-P1] `tdq_setup.py` & `tdq_codex_mcp.py` Antigravity + Windows Bugs
- **Locations:**
  - `scripts/tdq_setup.py:119` (`_chay_lenh`), `L252` (`_RE_LENH_WORKFLOW`), `L704-742` (`kiem_plugin_user`), `L804, 811, 917, 927, 945`, `L995-996`, `L1025-1030` (`kiem_dryrun_hook`), `L1495-1507` (`doc_phien_ban_plugin`), `L1580-1585`, `L1809` (`chay_lenh`), `L1848` (`ghim_huong_dan_tool`).
  - `scripts/tdq_codex_mcp.py:86` (`_nguon_lsp`), `L154` (`GOC_HOOK`), `L237-309` (`khai_hook_codex`).
- **Live Empirical Output (`verify_output.txt` §E3 & §E7f):**
  ```text
  shlex.split(unquoted Win):   ['C:Usersadmin.localbinclaude.exe', 'plugin', 'update', 'tdq@tdq-workflow', '--scope', 'user']
  shlex.split(quoted UNC):     ['\\fileserver\\tools\\claude.exe', 'plugin', 'update', 'tdq@tdq-workflow']
  shlex.split(trailing slash): ValueError(ValueError('No closing quotation'))
  tdq_setup.doc_phien_ban_plugin(agy_bundle with root plugin.json): None
  _RE_LENH_WORKFLOW.search('python C:\\Users\\admin\\.gemini\\config\\plugins\\tdq-workflow\\scripts\\tdq_state.py next') -> False
  _RE_LENH_WORKFLOW.search('py -3 scripts/tdq_state.py next') -> False
  tdq_codex_mcp.khai_hook_codex() from AGY bundle ->
    generated command: python3 "C:\...\agy_bundle\hooks\scripts/search_gate.py"
    does hook script exist in AGY bundle? False
  ```
- **Specific Bugs & Fixes:**
  1. `doc_phien_ban_plugin(goc_plugin)` (`tdq_setup.py:1495`): Add `goc_plugin / "plugin.json"` (Antigravity's root manifest) alongside `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`.
  2. `_chay_lenh` (`L119`) & `chay_lenh` (`L1809`): Accept `list[str]` directly (stop formatting `f'"{claude}" ...'` into a string only to re-parse with POSIX `shlex.split`!).
  3. `_RE_LENH_WORKFLOW` (`L252`): Support `[/\\]` path separators and `py(?:\s+-3)?` launcher so Windows commands in skills/docs are validated properly.
  4. `ghim_huong_dan_tool` (`L1848`): On Antigravity host (or `--host antigravity`), target `~/.gemini/GEMINI.md` (or skip writing `~/.claude/CLAUDE.md` when Claude is absent), and delete dead unreachable line `L996`.
  5. `tdq_codex_mcp.khai_hook_codex()` (`L237-309`): Check `(GOC_HOOK / ten_script).is_file()` before writing `.codex/hooks.json`, and use `tdq_ten_lenh.python_cho_hook()` instead of hardcoded `python3` (`L248`)! Also let `_nguon_lsp()` (`L86`) fall back to Antigravity's `~/.gemini/antigravity/mcp_config.json` and `~/.gemini/config/plugins/tdq-workflow/.mcp.json` when `~/.claude.json` is absent.

---

### 1.6 [NEW-08 / P0] `tdq_harvest.py` vs `tdq_knowledge.py` Broken Schema & Directory Contract
- **Locations:** `scripts/tdq_harvest.py:20-21, 76, 98-104, 175-178` vs `scripts/tdq_knowledge.py:22, 126-146, 180`.
- **Live Empirical Output (`verify_output.txt` §E7a):**
  ```text
  tdq_harvest.cmd_scan() on docs/tdq/logs/*.md found candidates: 0  <-- SCANS WRONG DIR docs/workinglog!
  tdq_harvest candidate validated by tdq_knowledge: valid=False, reason="Invalid or missing trang_thai: None (must be one of ('candidate', 'reviewed', 'rejected', 'superseded'))"
  tdq_harvest approved  validated by tdq_knowledge: valid=False, reason="Invalid or missing trang_thai: None (must be one of ('candidate', 'reviewed', 'rejected', 'superseded'))"
  ```
- **Porting Fix:**
  1. Scan both `docs/tdq/logs/*.md` (canonical TDQ logs dir) and `docs/workinglog/*.md` (legacy) in `tdq_harvest.cmd_scan()` (`L76`).
  2. Emit `trang_thai: candidate`, `auto_policy: false`, `nguon: {evidence: <rel_source>}` in `tdq_harvest.py:98-104`, and on `approve` (`L175`) require `--reviewer` (or `$USERNAME`) to write `trang_thai: reviewed`, `nguoi_duyet`, `ngay_duyet`, `evidence`.
  3. Make `tdq_knowledge.py:180` scan `**/*.md` recursively under a target directory.

---

### 1.7 [NEW-09, NEW-10, NEW-11 / P1] `tdq_state._probe_codex` & `tdq_team.py` Bugs
- **Live Empirical Output (`verify_output.txt` §E6b,c,d):**
  ```text
  tdq_state._probe_codex(external_user_repo): (False, 'chưa có tầng CLI Codex (scripts/tdq_codex.py)')
  kiem_tra_stale after ticking [>]:         (False, '')
  canh_bao_lach_luat(unrelated file) BEFORE ticking [>]: None
  canh_bao_lach_luat(unrelated file) AFTER  ticking [>]: {'kieu': 'chua-phan-cong', 'ma': None, 'nhanh': None}
  tdq_team._PATH.findall('`src\app\main.py` and `src/app/ok.py`'): ['src/app/ok.py']
  ```
- **Porting Fixes:**
  1. `tdq_state.py:1585`: Check `os.path.join(GOC_PLUGIN, "scripts", "tdq_codex.py")` (fallback `os.path.join(root, "scripts", "tdq_codex.py")`) instead of only `root`! Same in `tdq_codex.py:668` (`kiem_hook_ban`): resolve `hooks/scripts/codex_edit_gate.py` against `GOC_PLUGIN`.
  2. `tdq_team.py:1615`: Replace `if ban_do.get("plan_sha") != sha_file(plan):` with `if kiem_tra_stale(plan, ban_do)[0]:`!
  3. `tdq_team.py:49 & 178`: Allow `\` in `_PATH = re.compile(r"\`([A-Za-z0-9_./\\-]+\.[A-Za-z0-9]+)\`")`, check `("/" in duong or "\\" in duong)`, and normalize `.replace("\\", "/")`.
  4. `tdq_team.py:71-72`: Add `"rules/"`, `".gemini/"`, `".agents/"`, `"GEMINI.md"`, `"plugin.json"`, `"mcp_config.json"`, `"hooks.json"` to `TIEN_TO_FILE_LUAT`.
  5. `tdq_team.py:1188` (`chay_test_task`): Rewrite `python3` after `&&` / `;` as well (not just at string start), and wrap in `OwnedProcessJob` on Windows so timed-out subagent test trees don't leak grandchild processes!

---

## 2. Support Directories Line-by-Line Audit (`portable_src/`, `tools_kiem/`, `evals/`)

### 2.1 `portable_src/` (1/1 file read)
- **File:** `portable_src/skills/tdq-checkportable/SKILL.md` (59 lines)
  1. **`L50` (`setup --trust` CRASH — P1, Proven in E7b):** Instructs agent: *"Nếu user muốn tự động ghi trust luôn: chạy kèm cờ `setup --trust`"*. Running `python scripts/tdq_checkportable.py setup --trust` **crashes with exit code 2 (`error: unrecognized arguments: --trust`)**!
  2. **`L21-30, 34-46` (Claude-only files in portable skill):** Tells agent to inspect `<project>/.claude/settings.json` and `<project>/.mcp.json`, neither of which exists in an Antigravity portable/plugin bundle (`~/.gemini/config/plugins/tdq-workflow/` + `~/.gemini/antigravity/mcp_config.json`).
  3. **`L15` (`python3`):** Uses `python3 scripts/tdq_checkportable.py` without Windows fallback (`python` / `<plugin_root>/scripts/tdq_checkportable.py`).

### 2.2 `tools_kiem/` (1/1 file read)
- **File:** `tools_kiem/dem_da_nen_tang.py` (163 lines)
  1. **`L27-31` (Stale/deleted targets — P2):** Hardcodes `portable_codex/.codex/hooks.json` and `antigravity_portable/hooks.json` — both directories were deleted/renamed (`dist/tdq-antigravity` now uses root `plugin.json` + `rules/` and has NO `hooks.json`).
  2. **`L108` (`kiem_encoding_open` blind spot — P2):** AST visitor only checks `isinstance(node.func, ast.Name) and node.func.id == "open"` — **completely misses** `Path.open()`, `io.open()`, `Path.read_text()`, and `Path.write_text()` without `encoding=` (which allowed `tdq_runtime_bench.py:260,382,455` to slip through!).
  3. **`L1-19, 158` (Missing `utf8_io` — P2):** Does not import `utf8_io`, while `L158` prints `json.dumps(..., ensure_ascii=False)` (will `UnicodeEncodeError` on `cp1252` whenever any matched path/detail contains Vietnamese characters).

### 2.3 `evals/` (8/8 `.py` files + `README.md` + all 12 `tuan-thu` cases + `corpus.json` + `tdq-upgrade-offline.json` read)
| File | Lines | Findings & Windows / Antigravity Issues |
|---|---:|---|
| `evals/audit_photoboth360_50_tests.py` | 150 | **P2:** Missing `utf8_io` (prints Vietnamese labels at `L131-147`); `L22-29` `subprocess.run(..., text=True)` **without `encoding="utf-8"`** (uses `cp1252`, corrupting UTF-8 JSON output from `tdq_lsp.py` / `search_rules.py`!) and lacks `CREATE_NO_WINDOW`; `L13` hardcodes `C:\Users\admin\Documents\Photoboth360`. |
| `evals/audit_photoboth360_precision.py` | 351 | **P2:** Missing `utf8_io`; `L314` uses `LOG.open("x", encoding="utf-8")` (**crashes with `FileExistsError`** if re-run without manually deleting the log file!); hardcodes `C:\Users\admin\Documents\Photoboth360`. |
| `evals/test_photoboth360_precision.py` | 53 | **P3:** Missing `utf8_io` (imports `audit_photoboth360_precision`). |
| `evals/audit_graphify_full_wiki_ab.py` | 183 | **P2:** Missing `utf8_io`; `L45-52` assumes `ANTHROPIC_AUTH_TOKEN` / `ANTHROPIC_API_KEY` / `ANTHROPIC_MODEL` env vars (no Gemini/Antigravity provider option); `L59, 151` `subprocess.run` lacks `CREATE_NO_WINDOW`. |
| `evals/test_graphify_full_wiki_ab.py` | 73 | **P3:** Missing `utf8_io`. |
| `evals/tuan-thu/README.md` | 64 | **P2:** `L11, 14` hardcode macOS `/private/tmp/tdq-eval-nhanh` and `python3 scripts/tdq_eval.py`; describes only Claude/Codex live execution. |
| `evals/tuan-thu/*/ca.json` & `seed/**` (12 cases) | — | **P1 (Proven in E7d):** **6 of 6** seed plans (`build-tick-tung-task`, `commit-khong-push`, `duyet-bang-chu-cai`, `duyet-plan-kem-mode`, `mode-subagent-tach-nhanh`, `sua-plan-giua-chung`) now **FAIL `doc_lint.py` R15** because `R15` added in `v0.97.0` forgot a slug-date cutoff! Also `evals/tuan-thu/_chung/seed/tests/test_tien_ich.py` lacks `utf8_io`. |
| `evals/skill-quality/corpus.json` | 180 | **P2:** `L141` references non-existent `hooks/tdq_hook.py`; `L22, 62, 102` prompt patterns assume `python3` and `.claude` conventions. |
| `evals/tdq-upgrade-offline.json` | 95 | **Clean JSON fixture**, though commands/paths reflect Claude layout (`hooks/scripts/`, `.claude-plugin/`). |

---

## 3. Complete 67-File `scripts/*.py` Line-by-Line Audit Matrix

Every single `.py` file in `scripts/` (67/67) + `scripts/samples/transcript-step-audit.jsonl` (1/1) is documented below across the 6 subsystems.

### Subsystem A: Host, Setup, Command Naming & Packaging (11 files)
| Script | Lines | `utf8_io` | Host / Windows / Antigravity Findings (`file:line`) |
|---|---:|---|---|
| `utf8_io.py` | 31 | Self | **CLEAN.** Safely reconfigures `sys.stdout`/`sys.stderr` to `utf-8` (`errors="replace"`). Note: does NOT reconfigure `sys.stdin` — hook scripts reading JSON from `sys.stdin` must read `sys.stdin.buffer.read().decode("utf-8-sig")` on Windows. |
| `tdq_ten_lenh.py` | 150 | Lib (no CLI) | **G3/G18 confirmed + 2 nuances:** `L19-46` (`HO_TRO`) maps only `claude` (`:` separator) and `codex` (`$` prefix) — **missing `antigravity`/`agy`** (`/tdq-...` slash skills & `@tdq-...` mentions). `python_cho_hook()` (`L80-115`) handles Windows `py -3`/`python` well, and `chay_subprocess()` (`L118-149`) sets `CREATE_NO_WINDOW`. |
| `plugin_tiers.py` | 156 | Direct (`L19`) | **Mostly clean, Claude-centric metadata:** `TIER_CONTRACTS` (`L23-98`) defines `tdq-core` / `tdq` / `tdq-devtools` with Claude `hooks/hooks.json` & `.claude-plugin/marketplace.json` assumptions; add Antigravity bundle tier mapping if `tdq-antigravity` is validated via `plugin_tiers.py`. |
| `setup_status.py` | 482 | Direct (`L26`) | **P1 AGY blindness:** `L41` hardcodes `~/.claude.json`; `L313-316` runs `claude mcp list`; `L422` checks `~/.claude/plugins`. Completely blind to `~/.gemini/antigravity/mcp_config.json` and `~/.gemini/config/plugins/tdq-workflow/`. |
| `setup_status_render.py` | 158 | Lib (imported by `setup_status`) | **P3 stale copy:** `L117` renders heading `"Thang 7 bậc"` while `tdq_setup.py` was upgraded to 8 rungs (`8 bậc`). |
| `tdq_checkstatus.py` | 645 | Direct (`L27`) | **P1/P2 bugs:** `L281` reads `state.json` with `encoding="utf-8"` (UTF-8 BOM flags valid state as `"hong"`!); `L46-50, 169` hardcode `python3 scripts/...`; `L565-566` suggests `cd ... && git status` (`&&` fails in PowerShell 5.1!). |
| `tdq_readiness.py` | 212 | Lib (imported by `tdq_checkstatus`) | **P2 AGY hints:** `L88, 114, 146` remediation commands hardcode `python3 scripts/tdq_setup.py` and Claude plugin assumptions. |
| `tdq_setup.py` | 2069 | Direct (`L31`) | **P0/P1 (Proven in E3):** (1) `doc_phien_ban_plugin` (`L1495-1507`) ignores root `plugin.json` -> returns `None` on AGY, crashing `tu_dong_cap_nhat_khi_doi_phien_ban` (`L1584`); (2) `_chay_lenh` (`L119`) & `chay_lenh` (`L1809`) use POSIX `shlex.split` on Windows command strings (`L804,811,917,927,945`); (3) `_RE_LENH_WORKFLOW` (`L252`) rejects Windows `\` paths and `py -3`; (4) `kiem_dryrun_hook` (`L1025`) tests absent `hooks/scripts/prompt_context.py`; (5) `ghim_huong_dan_tool` (`L72, 995-996, 1848, 1965`) writes `~/.claude/CLAUDE.md` only and has dead code after `return` at `L996`; (6) `kiem_plugin_user` (`L704`) & `no_skill_khong_ton_tai` (`L1413`) check Claude scopes only. |
| `tdq_checkportable.py` | 356 | Direct (`L25`) | **P1 (Proven in E7b):** `portable_src/.../SKILL.md:50` tells agent to pass `setup --trust`, which `argparse` rejects (`rc=2`); `L296` prints dead hint `setup --codex` (also not an argument!); checks `.claude/settings.json` & `.mcp.json` instead of AGY plugin/MCP config. |
| `build_portable.py` | 652 | Direct (`L26`) | **CoreGaps G1-G17 confirmed + `L480-560`:** Antigravity target (`build_antigravity`) omits `scripts/` or leaves `python3 scripts/...` / `CLAUDE_PLUGIN_ROOT` / `AskUserQuestion` / `Agent(...)` / `mcp__lsp__*` unrewritten; does not rewrite `GEMINI.md` / `rules/` with dynamic `<plugin_root>` paths; does not generate `.mcp.json` with Windows-safe `cmd /c npx` or Python launcher. |
| `claude_export.py` | 288 | Direct (`L22`) | **Claude-export specific, P3 Windows note:** Exports Claude plugin tiers (`dist/claude-tiers`); uses `encoding="utf-8"` (`L44`) — switch JSON loads to `"utf-8-sig"` for safety. |

### Subsystem B: MCP & External Tools (6 files)
| Script | Lines | `utf8_io` | Host / Windows / Antigravity Findings (`file:line`) |
|---|---:|---|---|
| `tdq_codex_mcp.py` | 346 | Direct (`L24`) | **P0 (Proven in E7f):** `khai_hook_codex` (`L237-309`) writes `<agy-bundle>/hooks/scripts/*.py` (non-existent in AGY!) + `python3` (`L248`) into `<project>/.codex/hooks.json`! `_nguon_lsp` (`L86`) reads ONLY `~/.claude.json` (misses `~/.gemini/antigravity/mcp_config.json`). |
| `tdq_codex.py` | 1042 | Direct (`L31`) | **P1/P2:** `kiem_hook_ban` (`L654-690`) checks `cwd/hooks/scripts/codex_edit_gate.py` instead of `GOC_PLUGIN` (always fails in external repos!); `_cli_run` (`L887`) uses raw `subprocess.run` without `OwnedProcessJob` or `CREATE_NO_WINDOW` (orphans `node.exe` children on timeout!); `L275,283,291,312,853` hardcode `python3 scripts/tdq_codex.py`. |
| `tdq_devtool_mcp.py` | 312 | Direct (`L21`) | **P1 AGY & Windows:** `L54, 139-165, 190-238` read/write ONLY `~/.claude.json` & `~/.claude/settings.json`; writes bare `"command": "npx"` (on Windows some MCP hosts require `npx.cmd` or `cmd /c npx`); completely blind to Antigravity's already-installed `chrome-devtools-plugin` and `~/.gemini/antigravity/mcp_config.json`! |
| `tdq_lsp.py` | 698 | Direct (`L25`) | **P1 AGY & Windows:** Rungs 2 & 4 (`L289-375, 420-583`) inspect ONLY `~/.claude.json`, `~/.claude/settings.json`, `~/.claude/plugins/` -> **always exit 3 on Antigravity-only machines**! `L506` prints `cd {project} && ...` (unquoted + `&&`); `L104-129` suggests macOS `brew install` on Windows. |
| `lsp_module.py` | 618 | Transitive (`tdq_lsp`, `L17`) | **P0 (Proven in E4):** `_doc_tien_trinh_mac_dinh` (`L503-521`) runs PowerShell without UTF-8 `OutputEncoding` -> `IBM437` mangles Vietnamese `--root-dir` -> `broker_mo_coi` (`L560`) + `don_broker` (`L580`) **`taskkill /F` live `agent-lsp` brokers!** Also `doc_mcp_args` (`L224-226`) reads only `~/.claude.json`, and `L416-422` prints `mcp__lsp__*`. |
| `tdq_graphify.py` | 158 | Lib (`tdq_finish` imports it; add `utf8_io` if CLI-invoked) | **P2:** `OUTPUT_DIRS` (`L38-43`) only excludes `{".git", "graphify-out", "__pycache__", ".pytest_cache", "node_modules", ".venv", "venv"}` — **missing `docs/tdq`, `.tdq-worktrees`, `.gemini`, `.agents`, `dist`, `build`**! Every `tdq_state.py` write marks full Graphify manifest `stale`! |

### Subsystem C: Rules, Skills & Token / Context Tooling (10 files)
| Script | Lines | `utf8_io` | Host / Windows / Antigravity Findings (`file:line`) |
|---|---:|---|---|
| `luat_phan_loai.py` | 195 | Direct (`L18`) | **CLEAN.** Pure rule-classification logic; UTF-8 safe. |
| `search_rules.py` | 1128 | Direct (`L22` when `__main__`? Wait: check!) | **P0 (Proven in E1 & E5):** (1) **Does NOT import `utf8_io`!** (`E1` AST check caught `scripts/search_rules.py` has no `import utf8_io` — if CLI `main()` prints Vietnamese `loi_nhac` on `cp1252`, it crashes!); (2) **Double LSP bug** at `L868` AND `L887` (`re.split(r"__|\.", ten)[-1]`); (3) **Antigravity tool bypass** (`run_command`/`CommandLine`, `grep_search`, `find_by_name` ignored at `L31, 682`); (4) **PowerShell false-deny** (`L261-285, 342, 756, 821` blocks `C:\path\"` and `` `n `` in all phases!); (5) `L147-179` hardcodes `mcp__lsp__*` in `loi_nhac`. |
| `search_replay.py` | 218 | Direct (`L19`) | **P2:** Replays Claude/Codex transcripts against `search_rules.py`; lacks Antigravity `transcript.jsonl` event shape (`PLANNER_RESPONSE` -> `tool_calls`). |
| `skill_inventory.py` | 284 | Direct (`L23`) | **P1 AGY blindness:** `L161-203, 236-243` scan ONLY `.claude/skills`, `~/.claude/skills`, and `~/.claude/plugins/installed_plugins.json` — outputs `(no skill on disk)` for all Antigravity skills in `.agents/skills/`, `~/.gemini/antigravity/skills/`, and `~/.gemini/config/plugins/*/skills/`. |
| `skill_router.py` | 246 | Direct (`L20`) | **Mostly clean:** Routes prompts to TDQ skills; command rendering should pass `host="antigravity"` once `tdq_ten_lenh.py` supports `/tdq-...`. |
| `skill_tokens.py` | 274 | Direct (`L24`) | **P1 Windows bug:** `nhay_sang_venv()` (`L138`) calls `os.execv(vpy, [vpy, *sys.argv])` — broken on Windows MSVCRT (spawns background child without quoting spaces and exits parent immediately, breaking pipes & exit code)! Replace with `sys.exit(subprocess.call([vpy, *sys.argv]))`. Also `CAI_DAT` (`L49-50`) hardcodes `.venv-tokens/bin/pip` and `&&` (on Windows venv pip is `.venv-tokens\Scripts\pip.exe`), though `venv_python()` (`L128`) already checks `Scripts/python.exe`! |
| `context_surface.py` | 312 | Direct (`L22`) | **P2:** `L120` globs `references/*.md` non-recursively (misses `references/rules/*.md`); `L132` globs deleted `portable/**/*.md`; `L170-259` `--hooks` hardcodes Claude `hooks/scripts/*.py`. |
| `token_budget.py` | 268 | Direct (`L21`) | **P2:** Checks `CLAUDE.md`, `skills/`, `agents/` — add `GEMINI.md` and `rules/*.md` when measuring Antigravity always-on / rule token surface! |
| `token_audit.py` | 295 | Direct (`L20`) | **P2:** Parses Claude JSONL `usage` fields; blind to Antigravity `transcript.jsonl`. |
| `step_audit.py` | 318 | Direct (`L21`) | **P2:** Audits Claude/Codex transcript steps (sample at `scripts/samples/transcript-step-audit.jsonl`); blind to Antigravity `transcript.jsonl` `PLANNER_RESPONSE` `tool_calls`. |

### Subsystem D: Linting, Docs, i18n & Debt Markers (7 files)
| Script | Lines | `utf8_io` | Host / Windows / Antigravity Findings (`file:line`) |
|---|---:|---|---|
| `doc_lint.py` | 742 | Direct (`L26`) | **P1 (Proven in E7d):** (1) `L155, 607, 684` use `encoding="utf-8"` instead of `"utf-8-sig"` (BOM breaks frontmatter/config parsing); (2) `rule_r15` (`L526-568`) lacks slug date cutoff (**breaks 6/6 existing eval seed plans!**), checks only Vietnamese `chạm:`/`cham:` (misses `doc_lang=en`), misses `Pseudocode:` & `.h/.hpp/.kt/.swift/.mjs/.cjs/.mts`, and is trivially bypassed if `"logic"` appears anywhere in task prose. |
| `doc_dup.py` | 198 | Direct (`L18`) | **Mostly clean:** Uses `encoding="utf-8"` (`L54` -> prefer `"utf-8-sig"`). |
| `doc_index.py` | 234 | Direct (`L19`) | **Mostly clean:** Generates `docs/tdq/INDEX.md`; uses POSIX `/` normalization cleanly; switch `encoding="utf-8"` reads to `"utf-8-sig"`. |
| `i18n_check.py` | 215 | Direct (`L19`) | **Clean on Windows.** Scans repo files for Vietnamese diacritics unless `# i18n-allow`; update excluded/target dirs if `rules/` or `GEMINI.md` are added. |
| `kiem_no_marker.py` | 184 | Direct (`L18`) | **Clean on Windows.** Validates `TDQ-DEBT` markers; switch `encoding="utf-8"` reads to `"utf-8-sig"`. |
| `tdq_no.py` | 276 | Transitive (`tdq_state`, `L19`) | **Mostly clean:** Debt ledger CLI; hints at `L214, 248` print `python3 scripts/tdq_no.py`. |
| `scan_block_symbols.py` | 112 | Direct (`L17`) | **P2 stale allowlist:** `L42-44` still lists 3 deleted `portable/workflow/...` paths; update allowlist for `dist/tdq-antigravity` if run against built artifacts. |

### Subsystem E: Execution, State, Team, Worktrees, Tests, Finish, Harvest, Timing, Bench & Eval (22 files)
| Script | Lines | `utf8_io` | Host / Windows / Antigravity Findings (`file:line`) |
|---|---:|---|---|
| `tdq_state.py` | 2975 | Direct (`L36`) | **P0/P1 (Proven in E6a,b):** (1) `load()` (`L409`) + `L594,796,874,929,1061,2328` use `encoding="utf-8"` — **UTF-8 BOM renames `state.json` to `.corrupt-*` and wipes state!** (2) `_probe_codex` (`L1584-1587`) checks `root/scripts/tdq_codex.py` instead of `GOC_PLUGIN/scripts/tdq_codex.py` (**Codex mode unselectable in external repos!**); (3) `PRUNE_DIRS` (`L312-313`) omits `.tdq-worktrees`, `.worktrees`, `.gemini`, `.agents` (causes false stray-state warnings); (4) `L1330, 1439, 1446, 2675, 2739` hardcode `python3`, `${CLAUDE_PLUGIN_ROOT}`, `mcp__lsp__*`, and `"by": "claude"`. |
| `tdq_team.py` | 1782 | Direct (`L31`) | **P1 (Proven in E6c,d):** (1) `canh_bao_lach_luat` (`L1615`) checks `ban_do.get("plan_sha") != sha_file(plan)` instead of `kiem_tra_stale(plan, ban_do)[0]`, firing false `"chua-phan-cong"` on every file edit once `[>]` is ticked! (2) `_PATH` (`L49`) & `L178` drop Windows `\` paths; (3) `TIEN_TO_FILE_LUAT` (`L71-72`) misses `rules/`, `.gemini/`, `.agents/`, `GEMINI.md`, `plugin.json`, `mcp_config.json`; (4) `chay_test_task` (`L1188`) uses `shell=True`, only rewrites `python3` at token 0, and lacks `OwnedProcessJob`. Note: NTFS junction creation (`_tao_ntfs_junction_sharing`, `L925`) & `follow_symlinks=False` (`_kich_thuoc`, `L1012`) ARE well-implemented for Windows! |
| `tdq_worktree_registry.py` | 362 | Lib (`tdq_team` imports it; add `utf8_io` for CLI `L340`) | **P2:** **Missing direct `utf8_io` import** when run as `__main__` (`E1` check: imports only stdlib!); `L41-119, 327` output POSIX-only `mv`, `ls -la`, `&&`, unquoted `{duong_dan}`, and literal `<slug>`. |
| `tdq_vungfile.py` | 228 | Direct (`L20`) | **P3:** `subprocess.run(["git", ...])` (`L47-53`) lacks `CREATE_NO_WINDOW` and `-c core.quotepath=false` (non-ASCII changed files get octal-quoted by git!). |
| `tdq_test.py` | 1048 | Direct (`L29`) | **P1:** (1) `tat_ca_module` (`L130-136`) uses flat `os.listdir(tests_dir)` while `_result_inventory` (`L887-893`) uses recursive `os.walk(tests_dir)` — `ban_kinh` misses nested `tests/sub/test_*.py`! (2) `_doc_state` (`L492`) uses `encoding="utf-8"` (fails on BOM); (3) `TOP_DIRS` (`L97`) omits `"rules"`. |
| `tdq_test_manifest.py` | 142 | Lib (used by `tdq_test`) | **Mostly clean:** Uses `encoding="utf-8"` (`L68` -> `"utf-8-sig"`). |
| `tdq_test_process.py` | 268 | Lib (used by `tdq_test`) | **Well-designed Win32 Job Object (`OwnedProcessJob` with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`), 1 P2 bug at `L245`:** `_cleanup_with_retry` only retries `getattr(exc, "winerror", None) == 32` (`ERROR_SHARING_VIOLATION`), **missing `winerror == 5` (`ERROR_ACCESS_DENIED`)** which Windows raises on read-only `.git/objects/pack/*` files or transient Defender/indexer handle releases! |
| `tdq_test_receipt.py` | 214 | Lib (used by `tdq_test`) | **P2:** `EXCLUDED_DIRS` / `GENERATED_PREFIXES` (`L29-33`) omit `.gemini`, `.agents`, `.worktrees`. |
| `tdq_test_report.py` | 176 | Lib (used by `tdq_test`) | **CLEAN.** Pure formatting/reporting. |
| `tdq_test_result.py` | 164 | Lib (used by `tdq_test`) | **CLEAN.** Structured result builder. |
| `tdq_finish.py` | 296 | Direct (`L23`) | **P0 (Proven in E2):** `_run()` (`L73`) `.strip()` + `line[3:]` (`L87`) slices off 1st char of 1st unstaged file (`docs/...` -> `ocs/...`), skipping `step_lint` and `step_khoa_token`! Lacks `-z` / `-c core.quotepath=false` (breaks Vietnamese filenames); `step_khoa_token` (`L179`) checks only `\skills\`. |
| `tdq_harvest.py` | 258 | Direct (`L18`) | **P0 (Proven in E7a):** Scans `docs/workinglog` (`L76`) instead of `docs/tdq/logs`; writes `status: candidate` / `status: approved` (`L102, 175`) into `docs/tdq/knowledge/approved/`, 100% incompatible with `tdq_knowledge.py`! |
| `tdq_knowledge.py` | 196 | Transitive (`tdq_state`, `L20`) | **P0/P2 (Proven in E7a):** Incompatible with `tdq_harvest.py` frontmatter; `main()` (`L180`) uses non-recursive `glob.glob(os.path.join(target, "*.md"))`, skipping `candidates/` and `approved/` subdirectories! |
| `tdq_timing.py` | 412 | Transitive (`tdq_state`, `L26`) | **P1:** `--host` (`L368`) supports ONLY `("auto", "claude", "codex")`. Blind to Antigravity `transcript.jsonl`; always outputs `"no transcript source found; timing unavailable"` on AGY. |
| `tdq_bench.py` | 748 | Direct (`L26`) | **P2:** `L120` sample plan uses `Test: \`true\`` (POSIX-only, fails on Windows); `L178-241, 532-714` hardcode `mkdir -p` and `python3 scripts/tdq_bench.py`; `L316, 329, 365` `subprocess.run` lack `CREATE_NO_WINDOW`. |
| `tdq_runtime_bench.py` | 542 | Direct (`L25`) | **P2:** `L260, 382, 455` call `Path.read_text()` **without `encoding="utf-8"`** (`cp1252` crash on UTF-8 test files!); `L466` inline child `open(..., 'w')` lacks `encoding='utf-8'`; `L467` `Popen` lacks `CREATE_NO_WINDOW`. |
| `tdq_eval.py` | 1922 | Direct (`L35`) | **P1 (Proven in E7c):** Misses AGY tools `run_command` (`CommandLine`), `write_file`/`edit_file`/`read_file` (`Path`, `Content`, `Replacement`) (`L184-196, 351-354, 536-539`); `_duong_dan_sed` (`L475`) uses POSIX `shlex.split` on Windows paths; `L555, 581, 745, 752` forward-slash checks (`"docs/tdq/plan/" in d`) **misclassify Windows `docs\tdq\plan\*.md` writes as source-code edits!** `L1125-1275, 1481` block live runs on Windows via macOS Keychain `lay_token()`; `L1183, 1331, 1474` check `.claude-plugin` / `/.claude/plugins/` only. |
| `tdq_eval_contract.py` | 210 | Lib (used by `tdq_eval`) | **P1:** `_path_kind` (`L113-126`) omits `rules/`, `.gemini/`, `plugin.json`, `mcp_config.json`, `hooks.json`, `GEMINI.md` from `"behavioral"`, misclassifying Antigravity rule/manifest edits as `"review-required"` or `"docs_only"`. |
| `tdq_eval_hosts.py` | 524 | Lib (used by `tdq_eval`) | **P1:** `SUPPORTED_HOSTS = ("claude", "codex")` (`L20`) — no `"antigravity"` / `"agy"` adapter or transcript collector. |
| `tdq_skill_eval.py` | 318 | Direct (`L22`) | **P2:** `_load_json` (`L46`) uses `encoding="utf-8"` instead of `"utf-8-sig"`; live runner delegates to Claude/Codex CLI only. |
| `tdq_transcript.py` | 568 | Lib (imported by `tdq_timing`, add `utf8_io` if CLI `L525`!) | **P1:** **Has `__main__` CLI (`L525`) WITHOUT importing `utf8_io`!** (`E1` check: `tdq_transcript.py` only imports stdlib + `tdq_transcript_cache` — running `python scripts/tdq_transcript.py` directly on Windows `cp1252` with Vietnamese prompts crashes!). And supports only `claude` (`~/.claude/projects`) and `codex` (`~/.codex/sessions`), completely missing Antigravity `<appDataDir>\brain\<id>\.system_generated\logs\transcript.jsonl`! |
| `tdq_transcript_cache.py` | 148 | Lib (used by `tdq_transcript`) | **CLEAN.** SQLite/JSON cache helper; uses `encoding="utf-8"`. |

### Subsystem F: Visual, Canvas & Archify (11 files)
| Script | Lines | `utf8_io` | Host / Windows / Antigravity Findings (`file:line`) |
|---|---:|---|---|
| `archify_artifacts.py` | 562 | Lib (used by `tdq_archify`) | **P2:** `EXCLUDED_DIR_NAMES` (`L32-41`) excludes `.claude` and `.tdq-worktrees`, **missing `.gemini`, `.agents`, `.worktrees`, `.venv-tokens`**; `L512` `subprocess.run` lacks `CREATE_NO_WINDOW`. |
| `archify_delivery.py` | 396 | Lib (used by `tdq_archify`) | **Mostly clean on Windows:** Handles `is_windows_elevated()` (`L63`) and `os.startfile` (`L311`) properly; `L169, 317, 353` `subprocess.run` lack `CREATE_NO_WINDOW`. |
| `archify_model.py` | 348 | Lib (used by `tdq_archify`) | **CLEAN.** Pure stdlib JSON-IR validation & Graphify bridge; `utf-8` explicit. |
| `tdq_archify.py` | 1322 | Direct (`L22`) | **Mostly clean, P3 Windows items:** `_get_git_dirty_files` (`L75`) properly uses `git status --porcelain -z`! Add `CREATE_NO_WINDOW` on `git` calls (`L75, 130`) and `"utf-8-sig"` on JSON reads (`L612, 718, 773`). |
| `tdq_vision_diff.py` | 725 | Direct (`L40`) | **P3 (Proven in E7e):** `FIGMA_PAUSE_HINT` (`L52`) hardcodes `python3 scripts/tdq_state.py`; `L42` top-level `from PIL import Image...` requires external `Pillow` (installed on current machine, `rc=0`, but if run in bare stdlib Python even `--help` raises `ModuleNotFoundError` — consider lazy import or clear exit-2 message); `L335` `"utf-8"` -> `"utf-8-sig"`. |
| `canvas_a4_ch4_ch7.py` | 176 | Transitive (`canvas_a4_rebuild`, `L13`) | **P3 diagram text:** `L84` hardcodes `python3 scripts/tdq_state.py next`; `L92` hardcodes `🤖 Claude\nAgent`. |
| `canvas_a4_rebuild.py` | 383 | Direct (`L27`) | **P3:** `L211` `open(path, encoding="utf-8")` and `L365` `open(args.out, "w", encoding="utf-8")` are unclosed file handles (no `with` context manager); use `"utf-8-sig"` on `L211`. |
| `canvas_draw.py` | 125 | Transitive (`canvas_move_block`, `L18`) | **CLEAN.** Pure helper library. |
| `canvas_layout_apply.py` | 61 | Direct (`L16`) | **CLEAN.** Local Excalidraw batch mover (`127.0.0.1:17739`). |
| `canvas_move_block.py` | 210 | Direct (`L23`) | **CLEAN.** Local Excalidraw HTTP helper (`127.0.0.1:17739`). |
| `check_canvas_layout.py` | 339 | Direct (`L21`) | **Mostly clean:** `L38` `open(source, encoding="utf-8")` -> `"utf-8-sig"`. |

---

## 4. Cross-Cutting Sweeps Summary

### 4.1 CLI Entrypoints (`if __name__ == "__main__":`) Missing `utf8_io` (Proven by AST Scan `E1`)
Every script below has a `__main__` entrypoint **WITHOUT** importing `utf8_io` directly or transitively — guaranteed to `UnicodeEncodeError` on Vietnamese output when invoked under Windows `cp1252` pipes:
1. `scripts/search_rules.py` *(has `main()` at `L1095`, no `import utf8_io`!)*
2. `scripts/tdq_transcript.py` *(has `main()` at `L525`, no `import utf8_io`!)*
3. `scripts/tdq_worktree_registry.py` *(has `main()` at `L340`, no `import utf8_io`!)*
4. `tools_kiem/dem_da_nen_tang.py`
5. `evals/audit_graphify_full_wiki_ab.py`
6. `evals/audit_photoboth360_50_tests.py`
7. `evals/audit_photoboth360_precision.py`
8. `evals/test_graphify_full_wiki_ab.py`
9. `evals/test_photoboth360_precision.py`

*(Note: `E1` initially listed `search_rules.py`, `tdq_transcript.py`, `tdq_worktree_registry.py` under "Library modules" only because `search_rules` was accidentally in the hardcoded `utf8_bearers` set — inspect confirmed **none** of those 3 import `utf8_io`, and all 3 have `__main__` CLI entrypoints!)*

### 4.2 Every `~/.claude`, `.claude`, `CLAUDE_*`, `CODEX_*`, `.gemini`, `antigravity`, `agy` Reference in `scripts/`
| Script | Exact Host-Specific Paths / Env Vars Used | Antigravity Equivalent Needed |
|---|---|---|
| `build_portable.py` | `.claude-plugin`, `.codex-plugin`, `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `dist/tdq-antigravity` | Full AGY bundle compiler (`scripts/` copy + path rewrite + `rules/` + `.mcp.json` + `plugin.json`) |
| `tdq_setup.py` | `~/.claude/CLAUDE.md`, `~/.claude.json`, `~/.claude/plugins/`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `claude` CLI | Root `plugin.json`, `~/.gemini/GEMINI.md`, `~/.gemini/antigravity/mcp_config.json`, `~/.gemini/config/plugins/tdq-workflow` |
| `setup_status.py` | `~/.claude.json`, `~/.claude/plugins`, `claude mcp list` | `~/.gemini/antigravity/mcp_config.json`, `~/.gemini/config/plugins/` |
| `tdq_checkportable.py` | `.claude/settings.json`, `.mcp.json`, `.codex/hooks.json` | AGY plugin dir (`~/.gemini/config/plugins/tdq-workflow/plugin.json`) & `mcp_config.json` |
| `tdq_codex_mcp.py` | `~/.claude.json` (`_nguon_lsp`), `GOC_HOOK = hooks/scripts` | Fallback to `~/.gemini/antigravity/mcp_config.json` + guard missing `hooks/scripts` in AGY bundle |
| `tdq_devtool_mcp.py` | `~/.claude.json`, `~/.claude/settings.json` | Detect AGY `chrome-devtools-plugin` (`~/.gemini/config/plugins/chrome-devtools-plugin`) & `~/.gemini/antigravity/mcp_config.json` |
| `tdq_lsp.py` & `lsp_module.py` | `~/.claude.json`, `~/.claude/settings.json`, `~/.claude/plugins/`, `mcp__lsp__*` | Read `~/.gemini/antigravity/mcp_config.json` + AGY plugin `.mcp.json`; emit `mcp_tdq-workflow_lsp_*` / `mcp_lsp_*` |
| `search_rules.py` | `Bash`, `Grep`, `mcp__[^_]*lsp[^_]*__` | Add `run_command` (`CommandLine`), `grep_search` (`Query`), `find_by_name`, `mcp_<server>_lsp_<op>` |
| `skill_inventory.py` | `.claude/skills`, `~/.claude/skills`, `~/.claude/plugins/installed_plugins.json` | Add `.agents/skills`, `~/.gemini/antigravity/skills`, `~/.gemini/config/plugins/*/skills` |
| `tdq_state.py` | `${CLAUDE_PLUGIN_ROOT}`, `mcp__lsp__*`, `"by": "claude"`, `.claude/` in `PRUNE_DIRS` | Dynamic `<plugin_root>`, host-aware MCP names & `"by": host`, add `.gemini`, `.agents`, `.tdq-worktrees` to `PRUNE_DIRS` |
| `tdq_team.py` | `.claude/`, `CLAUDE.md`, `AGENTS.md` in `TIEN_TO_FILE_LUAT` | Add `rules/`, `.gemini/`, `.agents/`, `GEMINI.md`, `plugin.json`, `mcp_config.json` |
| `tdq_transcript.py` & `tdq_timing.py` | `~/.claude/projects`, `~/.codex/sessions`, `--host auto\|claude\|codex` | Add `antigravity` host reading `<appDataDir>\brain\<conv-id>\.system_generated\logs\transcript.jsonl` |
| `tdq_eval.py`, `tdq_eval_hosts.py`, `tdq_eval_contract.py` | `claude`, `codex`, `.claude-plugin/plugin.json`, `/.claude/plugins/`, macOS `security` Keychain | Add `antigravity` host, root `plugin.json`, `.gemini/config/plugins/`, AGY tool names (`run_command`, `write_file`, `edit_file`, `read_file`) & `rules/` in `_path_kind` |
| `archify_artifacts.py` & `tdq_test_receipt.py` | `.claude` in `EXCLUDED_DIR_NAMES` / `EXCLUDED_DIRS` | Add `.gemini`, `.agents`, `.worktrees`, `.venv-tokens` |

---

## 5. Actionable Additions Required in `AUDIT-AND-PORTING-PLAN.md`

To achieve **zero missed bugs** during implementation, add the following work items to `AUDIT-AND-PORTING-PLAN.md`:

1. **Phase 1 ( Core Runtime & Windows Fixes — MUST-FIX BEFORE DOGFOODING ):**
   - **`tdq_finish.py` (`NEW-01`):** Fix `_run()` `.strip()` chopping `" M "` porcelain status (`docs/...` -> `ocs/...`), switch to `git -c core.quotepath=false status --porcelain -z`, and include `agents/`, `rules/`, `GEMINI.md` in `step_khoa_token()`.
   - **`lsp_module.py` (`NEW-02`):** Prepend `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8;` to the Windows PowerShell WMI query (`L504`) and harden `broker_mo_coi()` (`L560`) so live brokers in Vietnamese/non-ASCII directories are NEVER killed!
   - **`search_rules.py` (`NEW-03`, `NEW-04`, `E1`):** Import `utf8_io`; fix **both** `L868` AND `L887` (`re.split`) for single-underscore `mcp_<server>_lsp_<tool>`; add Antigravity `run_command`/`CommandLine` and `grep_search`/`Query`; fix Windows trailing-backslash `"C:\path\"` and PowerShell backtick `` `n `` false-malformed hard-denies!
   - **UTF-8-BOM Hardening (`NEW-05`):** Change `encoding="utf-8"` -> `encoding="utf-8-sig"` on all JSON/Markdown/config readers in `tdq_state.py`, `tdq_checkstatus.py`, `tdq_test.py`, `doc_lint.py`, `tdq_skill_eval.py`, `tdq_archify.py` so PowerShell 5.1 BOM writes never trigger `state.json.corrupt-*` data loss.
   - **`tdq_state.py` & `tdq_team.py` (`NEW-09`, `NEW-10`, `NEW-11`):** Fix `_probe_codex()` (`L1585`) & `tdq_codex.kiem_hook_ban()` (`L668`) to resolve against `GOC_PLUGIN`; fix `canh_bao_lach_luat()` (`L1615`) to use `kiem_tra_stale(plan, ban_do)[0]` instead of raw `plan_sha`; allow `\` in `tdq_team._PATH` (`L49`); expand `TIEN_TO_FILE_LUAT`, `PRUNE_DIRS`, `OUTPUT_DIRS`, `EXCLUDED_DIR_NAMES`.

2. **Phase 2 ( Setup, MCP, Skills & Portable Tooling ):**
   - **`tdq_setup.py` & `setup_status.py` (`NEW-06`, `NEW-18`):** Recognize root `plugin.json` in `doc_phien_ban_plugin()`; eliminate POSIX `shlex.split` on Windows paths; update `_RE_LENH_WORKFLOW` for `\` and `py -3`; make `setup_status.py`, `tdq_lsp.py`, `lsp_module.py`, `tdq_devtool_mcp.py` read `~/.gemini/antigravity/mcp_config.json` & `~/.gemini/config/plugins/`.
   - **`tdq_codex_mcp.py` (`NEW-07`):** Guard `khai_hook_codex()` when `hooks/scripts/` is absent in AGY bundle and use `python_cho_hook()` instead of `python3`.
   - **`tdq_checkportable.py` + `SKILL.md` (`NEW-16`):** Either implement `--trust` (and `--antigravity`) in `tdq_checkportable.py` or remove the crashing `--trust` / `--codex` instructions.
   - **`skill_inventory.py` & `skill_tokens.py` (`NEW-12`, `NEW-13`):** Add AGY skill directories to `skill_inventory.py`; replace broken Windows `os.execv` in `skill_tokens.py:138` with `subprocess.call` and show `.venv-tokens\Scripts\pip` on Windows.

3. **Phase 3 ( Knowledge, Linting, Transcripts, Timing & Evals ):**
   - **`tdq_harvest.py` + `tdq_knowledge.py` (`NEW-08`):** Unify log scan dir (`docs/tdq/logs`), frontmatter schema (`trang_thai`), and recursive directory check.
   - **`doc_lint.py` (`NEW-17`):** Add slug date cutoff to `rule_r15` (fixing 6/6 broken eval seed plans), add English `doc_lang=en` markers (`touch:`/`files:`), and tighten prose bypass.
   - **`tdq_transcript.py` + `tdq_timing.py` (`NEW-14`, `E1`):** Add `utf8_io` + `--host antigravity` parser for `<appDataDir>\brain\<conv-id>\.system_generated\logs\transcript.jsonl`.
   - **`tdq_eval*.py` + `tools_kiem/dem_da_nen_tang.py` + `tdq_test*.py` + `tdq_runtime_bench.py` (`NEW-15`, `NEW-19`..`NEW-28`):** Add `antigravity` host & tool names/arg keys (`CommandLine`, `Path`, `Content`), normalize `\` before `THU_MUC_TAI_LIEU` checks in `_ghi_ma_nguon`, add `winerror == 5` retry in `tdq_test_process.py:245`, recurse `tat_ca_module()` in `tdq_test.py:130`, and add `encoding="utf-8"` to `tdq_runtime_bench.py` & `evals/audit_*.py`.
