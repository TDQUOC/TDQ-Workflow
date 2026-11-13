# Rescan 01 — Exhaustive Audit of Git Branches, Release/Export Pipeline, Unmerged Work & Porting Plan Gaps

> **Scanned Repository:** `C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow` (strictly READ-ONLY)
> **Compared Plan:** `c:\Users\admin\Documents\Projects\TDQ-Workflow-Antigravity\docs\AUDIT-AND-PORTING-PLAN.md`
> **Installed Antigravity Plugin:** `C:\Users\admin\.gemini\config\plugins\tdq-workflow` (`v0.74.0`, strictly READ-ONLY)
> **Audit Timestamp:** `2026-11-13`

---

## Executive Summary

1. **Release Architecture (`dev` → `main` via Git Plumbing, NOT `skills/tdq-release/`):**
   - `skills/tdq-release/` **does not exist and never existed** in Git history (`git log --all -- "*tdq-release*"` is empty). There is also **no `release` or `release/*` branch** locally or on `origin`, and **no GitHub Actions release workflow** (`.github/workflows/test.yml` only runs `unittest` + `context_surface.py`).
   - Instead, `main` (`6f03655c`, `v0.95.0`, **175 files**) is the clean runtime release branch synthesized from `dev` (**6,230 files**) via Git plumbing (`git ls-tree` → temporary `GIT_INDEX_FILE` → `git write-tree` → `git commit-tree` → `git update-ref refs/heads/main`) inside `scripts/build_portable.py --sinh-main --nguon dev --nhanh-dich main` (`sinh_nhanh_main`, lines `595–736`).
2. **Local `dev` (`v0.97.0`) vs Remote/`main` (`v0.95.0`) Split:**
   - `origin/main` and local `main` are at **`v0.95.0`** (`6f03655c`, tagged `v0.95.0` → `5c2bb858`, built from `dev@b3480d0c`).
   - Local `dev` (`b423ee06`, `v0.97.0`) is **48 commits ahead of `origin/dev` (`685552e7`)** and **49 commits ahead of `dev@b3480d0c` (`v0.95.0` base)**. Neither `v0.96.0` nor `v0.97.0` has been pushed to `origin` or published to `main`.
3. **Why Antigravity Stalled at `v0.74.0` + Critical `tdq_setup.py` Host Bug:**
   - Neither `build_portable.py --sinh-main`, nor `tdq_setup.py`, nor `hooks/scripts/session_start.py` ever invokes `--sinh-agy`. Antigravity was manually exported once on `2026-10-19` (`v0.74.0`) and never wired into release or session sync.
   - **Critical newly discovered bug:** `tdq_setup.doc_phien_ban_plugin(goc_plugin)` (`scripts/tdq_setup.py:1495-1507`) only checks `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` — it **ignores root `plugin.json`**, returning `None` on Antigravity! Furthermore, `thuc_hien_setup_bu()` (`tdq_setup.py:1534-1546`) unconditionally mutates `~/.claude/CLAUDE.md`, `~/.claude/plugins/cache`, and `.codex/hooks.json` with Claude/Codex syntax while doing nothing for Antigravity.
4. **Unmerged Worktrees, Branches, Stashes & Dirty Working Tree:**
   - Every named `feature/*`, `bugfix/*`, `tdq/*`, and `local-sync` branch is **100% merged into `dev`** (`git merge-base --is-ancestor` verified).
   - Both active Git worktrees (`worktree-agent-a37e138360abceb26` @ `b493bfc0` and `worktree-agent-a45a16c73f42c0ad5` @ `60c8123f`) were verified byte-for-byte identical in patch content to commits already merged into `dev` (`436c30f9` and `fd11ac4c`). All 6 stashes (`2026-10-25`) are obsolete Archify backups.
   - **Active unimplemented request in `dev` dirty tree:** `docs/tdq/brief/2026-11-11-1435-chan-tu-sua-khi-feedback.md` (+ `STATE.md` / `state.json`) exposes a live loophole in `hooks/scripts/edit_gate.py` where AI edits source code unrestricted when `phase == "idle"`, `phase == "report"`, or `active_request == ""` after user bug feedback (proposing `[TDQ:FEEDBACK]` + Clean Code Invariant #5 *"Triage Before Touch"*).
5. **12 Concrete Gaps Uncovered Against `docs/AUDIT-AND-PORTING-PLAN.md`:**
   - Detailed in **Section 3** (`GAP-1` through `GAP-12`), including 3 `P0` runtime blockers (`5` hook scripts bypassing `_common.py` stdout/exit protocol, `v0.96.0` `read_gate.py` range-overlap math breaking on Antigravity `StartLine`/`EndLine`, and `tdq_setup.py` `doc_phien_ban_plugin()`/`thuc_hien_setup_bu()` host bugs).

---

## Section 1 — Remote & Local Release Branch Audit, `claude-export`, `.github/`, `build/`, and Host Sync

### 1.1 Remote (`origin`) Heads & Tags (`git ls-remote --heads --tags origin`)

- **Remote URL:** `https://github.com/TDQUOC/TDQ-Workflow.git` (`origin/HEAD -> origin/main`)
- **`release` / `release/*` branches:** **None** on remote or local.

| Remote Branch (`refs/heads/*`) | Commit SHA | Relationship to Local `dev` (`b423ee06`) | Status / Notes |
|---|---|---|---|
| `main` | `6f03655caaa02252ecb8a9332303b2f1e1771b8a` | Plumbing release commit from `dev@b3480d0` | **Active release branch (`v0.95.0`)**, matches local `main` (`6f03655c`, `2026-11-08`) |
| `dev` | `685552e7f771183fb4dc0909a031c6803ec98c4c` | Ancestor of local `dev` (behind by **48 commits**) | Last pushed commit: `docs(release): record verified 0.95.0 publication evidence` |
| `bugfix/giam-timeout-agent-lsp` | `3e0ef5f8f9ca280a5e9bb17121b9302a8981b393` | Ancestor of `dev` (merged) | Matches local `bugfix/giam-timeout-agent-lsp` |
| `feature/che-do-tdq-direct` | `3c51a0826f28044e657727c9d42c7df754d5870c` | Ancestor of `dev` (merged) | Historical remote branch |
| `feature/nang-cap-toan-dien-tdq-workflow` | `d37ae797e06da8bc0219c6b4df11aa304cc62e88` | Ancestor of `dev` (merged) | Historical remote branch |
| `tdq-doi-ten-mode-implement` | `9b98199b91b86d6ec8602af65a7b9f8875a31667` | Ancestor of `dev` (merged) | Historical remote branch |
| `tdq-ext-2026-07-30-sample-socketio-chat` | `873ee672a028e50469b7f5a67355d4776c89e4b4` | Ancestor of `dev` (merged) | Historical remote branch |
| `tdq-graphify-chi-source` | `8853879ca996b59df069103f4448e9182f9d34f9` | Ancestor of `dev` (merged) | Historical remote branch |
| `tdq-plan-uoc-tinh-phut` | `6581418e8b0d1f7f50bb614e258ed0b6f26165cc` | Ancestor of `dev` (merged) | Historical remote branch |

- **19 Git Tags (identical on `origin` and local):**
  `v0.40.0`, `v0.41.0`, `v0.73.0`, `v0.73.1`, `v0.81.0`, `v0.82.0`, `v0.83.0`, `v0.84.1`, `v0.84.2`, `v0.85.0`, `v0.85.1`, `v0.86.0`, `v0.87.0`, `v0.88.0`, `v0.89.0`, `v0.90.0`, `v0.91.0`, `v0.92.0`, and annotated tag **`v0.95.0`** (`5c2bb858` → `6f03655c` on `main`).
  *(Note: `v0.93.0` and `v0.94.0` have `release: v0.93.0` / `release: v0.94.0` commits on `main` (`67f6f99f`, `46601630`) without Git tags; `v0.96.0` and `v0.97.0` exist only on local `dev` without `main` commits or tags.)*

### 1.2 Exact Release Branch Architecture (`dev` → `main`)

- **Why `skills/tdq-release/` was not found:** The repo contains **11 skills** under `skills/` (`tdq-analyze`, `tdq-archify`, `tdq-build`, `tdq-conventions`, `tdq-debug`, `tdq-graphify`, `tdq-intake`, `tdq-plan`, `tdq-qc`, `tdq-report`, `tdq-research`) plus `portable_src/skills/tdq-checkportable`. There has never been a `tdq-release` skill.
- **Documented Release Contract:** Defined in `skills/tdq-intake/references/nhanh-request.md:43-50` and design report `docs/tdq/reports/2026-10-14-1713-tach-nhanh-dev-main-release.md`:
  1. All development, specs, plans, tests, and state tracking live on **`dev`** (`6,230` tracked files at `b423ee06`).
  2. **`main`** (`175` tracked files at `6f03655c`) is a **generated runtime-only branch** built via `scripts/build_portable.py --sinh-main --nguon dev --nhanh-dich main` (`sinh_nhanh_main`, `scripts/build_portable.py:595-736`):
     - Reads `git ls-tree -r -z dev` without checking out `main` or touching the working tree.
     - Filters paths through `la_duong_dan_release(rel_posix)` (`build_portable.py:598-615`):
       - **`RELEASE_EXCLUDE_DIRS` (16 dirs, lines `62-67`):** `.git`, `docs`, `tests`, `evals`, `graphify-out`, `.taskmaster`, `tools_kiem`, `.github`, `portable`, `portable_claude`, `portable_codex`, `__pycache__`, `.pytest_cache`, `.venv`, `node_modules`, `.remember`, `ClaudeExport`.
       - **`RELEASE_EXCLUDE_FILES` (lines `68-71`):** `.DS_Store`, `CHANGELOG-archive.md`, `pyrightconfig.json`, `state.json`, `.tdq-turn.jsonl`.
       - **`RELEASE_EXCLUDE_SCRIPTS` (**13** scripts, lines `72-77`, plus `scripts/samples/*` at line `606`):** `canvas_a4_ch4_ch7.py`, `canvas_a4_rebuild.py`, `canvas_draw.py`, `canvas_layout_apply.py`, `canvas_move_block.py`, `check_canvas_layout.py`, `doc_dup.py`, `doc_index.py`, `i18n_check.py`, `luat_phan_loai.py`, `skill_router.py`, `tdq_eval.py`, **`tdq_knowledge.py`**.
     - Writes filtered entries into a temporary `GIT_INDEX_FILE` via `git update-index -z --index-info`, creates tree via `git write-tree`, commits onto previous `main` parent (NOT a merge commit from `dev`!) with message `release: v<version> (from dev@<short_sha>)`, and updates `refs/heads/main`.
  3. **End-to-End Version Bump & Publication Sequence** (verified from commits `9bde4e13`, `6f03655c`, `685552e7` `docs/tdq/artifacts/2026-11-08-1207-va-lo-hong-edit-gate-3-tang/release-0.95.0.json`, and `112e9945`):
     - Bump `"version"` in `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` *(note: `README.md` badge is forgotten at `0.89.0`!)*.
     - Prepend release notes in `CHANGELOG.md` and rotate older entries into `docs/CHANGELOG-archive-2.md` to obey `doc_lint.py` R6 (`< 500` lines).
     - Update `docs/tdq/.tdq-phat-hanh.json` (`{"phien_ban": "X.Y.Z", "cap_nhat": "..."}`).
     - Run `python3 scripts/build_portable.py --sinh-main --nguon dev --nhanh-dich main`.
     - When user explicitly says `"release và push"`: push `dev` & `main`, tag `vX.Y.Z` on `main`, archive `main` into `TDQ-Workflow-X.Y.Z.zip` (`175` entries) + `SHA256SUMS.txt`, publish GitHub Release via `gh release create`, and record `release-X.Y.Z.json` evidence on `dev`.

### 1.3 Inspection of `docs/tdq/.tdq-phat-hanh.json`, `.github/`, and `build/`

| Path | Tracked? | Current State & Exact Purpose |
|---|---|---|
| `docs/tdq/.tdq-phat-hanh.json` | Yes (`dev` only; excluded from `main` via `docs`) | Contains `{"phien_ban": "0.97.0", "cap_nhat": "2026-11-11T14:58:11"}` (dirty timestamp bump from `13:00:00`). Defined as `MOC_PHAT_HANH` in `hooks/scripts/search_rules.py` and read/written by `tdq_setup.doc_phat_hanh()` / `ghi_phat_hanh()` (`scripts/tdq_setup.py:1509-1531`). Serves as the **per-workspace setup stamp**: when `plugin_version != .tdq-phat-hanh.json["phien_ban"]`, `session_start.py` runs `tu_dong_cap_nhat_khi_doi_phien_ban(cwd)` (`thuc_hien_setup_bu`). |
| `.github/workflows/test.yml` | Yes (`dev` only; excluded from `main`) | **Only file inside `.github/`.** 44 lines: triggers on `push` (`main`, `dev`) and `pull_request`, runs `python -m unittest discover -s tests -p "test_*.py"` on `[ubuntu-latest, macos-latest, windows-latest] × ["3.11", "3.13"]` and `python scripts/context_surface.py`. **Zero release/packaging automation exists in CI.** |
| `build/` | Untracked (in `.gitignore`? No — empty dir, Git ignores empty dirs) | **Completely empty directory** (`0` files, `0` subdirs, timestamp `2026-11-01 21:48:23`, leftover scratch dir from `v0.85.0` packaging). |

### 1.4 `claude-export/` + `scripts/claude_export.py` vs Repo Root vs `main`

- **Contents of `claude-export/` (5 files):** `INSTRUCTIONS.md`, `EXPORT_LOG.md`, `MANIFEST.template.json`, `README.template.md`, `local-repos.json`.
- **Purpose:** `scripts/claude_export.py` (`622` lines) is **NOT** the plugin release publisher — it is a **personal Claude Code workstation migration tool** (`build --dest <dir> [--zip]` / `check --dest <dir>`) that snapshots `~/.claude` (`CLAUDE.md`, `settings.json`, `plugins/known_marketplaces.json`, `plugins/installed_plugins.json`), MCP servers from `~/.claude.json` (scrubbing secrets to `<SET_ME>`), and local Git repos listed in `claude-export/local-repos.json`. Last logged run in `EXPORT_LOG.md`: `v0.8.0` (`2026-08-05`, macOS).
- **3 Subtle Couplings & Asymmetries Discovered:**
  1. **Runtime import coupling:** `scripts/build_portable.py:36` imports `from claude_export import plugin_version, sha256_of`! And `plugin_version(repo)` (`scripts/claude_export.py:213-218`) **only reads `.claude-plugin/plugin.json`**.
  2. **Asymmetry between `main` and `--sinh-agy`:** `RELEASE_EXCLUDE_DIRS` (`build_portable.py:62-67`) excludes `ClaudeExport` (PascalCase) rather than `claude-export` (kebab-case), so **all 5 files of `claude-export/` ARE shipped on `main` (`175` files)**! Conversely, `EXCLUDE_DIRS` (`build_portable.py:44-49`, used by `--sinh-agy`) excludes `claude-export` (`--sinh-agy` skips it), **but `--sinh-agy` (`sinh_agy_tai_cho`, lines `551-592`) does NOT exclude `RELEASE_EXCLUDE_SCRIPTS` or `scripts/samples/*`**!
  3. **Hardcoded macOS paths:** `claude-export/local-repos.json` hardcodes `/Users/truongdinhquoc/Documents/TDQWorkflow` and `/Users/truongdinhquoc/Documents/mem0R&D`, causing `python scripts/claude_export.py build` to fail on Windows unless `--local-repos` is overridden. It also only probes `agy --version` in `CLI_TOOLS` (`claude_export.py:55`) and never exports `~/.gemini/config`.

### 1.5 Host Sync Matrix & Why Antigravity Stalled at `v0.74.0`

| Host Target | Install Location | Version Found | How Sync / Update Works Today |
|---|---|---|---|
| **Claude Code** | `~/.claude/plugins/cache/tdq-local/tdq-workflow/0.95.0` (`installed_plugins.json` user scope; stale project scope `0.92.0` on `claudecodeui`) | **`v0.95.0`** (`6f03655c`, matches `origin/main`) | **Fully automated in `session_start.py` + `tdq_setup.py`:** (1) `tu_dong_cap_nhat_plugin_user()` checks local marketplace vs installed version and runs `claude plugin update` + `dong_bo_mcp_plugin_cache()`; (2) `kich_hoat_kiem_tra_remote_nen()` spawns detached `tdq_setup.py --update-plugin` every `7200s` (`claude plugin marketplace update tdq-local` pulling `origin/main`); (3) `tu_dong_cap_nhat_khi_doi_phien_ban()` pins `<!-- TDQ:TOOLS -->` into `~/.claude/CLAUDE.md`. |
| **Codex CLI** | Repo `.codex-plugin/plugin.json` + `.agents/plugins/marketplace.json` (`"url": "./"`) + `~/.codex/config.toml` | **`v0.97.0`** (in-repo) | `tdq_setup.py` (`dong_bo_mcp_codex`, `dong_bo_hooks_codex`) syncs `[mcp_servers.lsp]` & `[mcp_servers.chrome-devtools]` into `~/.codex/config.toml` and `.codex/hooks.json` into workspace. |
| **OpenCode** | `.opencode/plugins/tdq-workflow.js` | **`v0.97.0`** (in-repo) | Reads `../../skills` dynamically from repo root via symlink/path. |
| **Antigravity** | `C:\Users\admin\.gemini\config\plugins\tdq-workflow` (enabled in `~/.gemini/config/config.json`: `{"plugins": {"tdq-workflow": true}}`) | **`v0.74.0`** (`2026-10-19`, **23 versions behind**) | **0% automated + broken in `tdq_setup.py`:**<br>1. `build_portable.py --sinh-agy` is completely manual and never called by `--sinh-main`, `tdq_setup.py`, or `session_start.py`.<br>2. `tdq_setup.doc_phien_ban_plugin()` (`tdq_setup.py:1495-1507`) only checks `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` — returning `None` on `~/.gemini/config/plugins/tdq-workflow` (which only has root `plugin.json`).<br>3. If `thuc_hien_setup_bu()` (`tdq_setup.py:1534-1546`) runs, it unconditionally writes Claude tool rules (`mcp__lsp__*`, `tdq-workflow:tdq-intake`) to `~/.claude/CLAUDE.md` and `.codex/hooks.json` to the project while doing nothing for Antigravity! |

---

## Section 2 — Diff `main` (`v0.95.0`) vs `dev` (`v0.97.0`), Dirty Files, Worktrees & Branches

### 2.1 Runtime & Skill Delta Between `main` (`v0.95.0` / `dev@b3480d0c`) and `dev` (`v0.97.0` / `b423ee06`)

Between `b3480d0c` (the exact `dev` commit from which `main@6f03655c` `v0.95.0` was built) and `dev` HEAD `b423ee06` (`48` commits after `685552e7`), **15 runtime/skill files** changed (alongside `CHANGELOG.md`, `docs/*`, and `tests/{test_adapter_host.py, test_archify_gate.py, test_doc_lint.py, test_hooks.py}`):

| Version & Commit(s) | Modified Runtime / Skill Files | Exact Technical Change & Impact on Antigravity Porting |
|---|---|---|
| **`v0.96.0`**<br>`423d34e3`, `5a5f015d` | `scripts/tdq_state.py` (`+151` lines), `skills/tdq-archify/references/{archify-ba.md, archify-quick.md}`, `skills/tdq-report/references/report-template.md` | **Archify State Gate & Report Manifest Gate:**<br>- Added `archify_bo_qua: ""` to `default_state()` and `ARCHIFY_MOC = "2026-11-09-0143"` (only requests with slug `>= ARCHIFY_MOC` are enforced).<br>- `_archify_gate()` blocks `tdq_state.py approve spec` and `approve quick` unless the spec/brief `.manifest.json` exists and `archify_check.py check` reports `"current"` (or `--bo-qua-archify "<reason>"` is passed).<br>- `_chan_report_thieu()` blocks `tdq_state.py set phase=idle` unless `docs/tdq/reports/<active_request>.md` contains all 4 required sections (Vietnamese OR English regexes) AND for slugs `>= ARCHIFY_MOC` has a `"current"` `.manifest.json`! |
| **`v0.96.0`**<br>`59953861`, `377fab37` | `hooks/scripts/read_gate.py` (`+68` lines), `skills/tdq-conventions/references/soul.md` (`+6` lines), `skills/tdq-intake/references/quick-lane.md` (`+5/-4`) | **70% Line-Range Overlap Anti-Loop & Clean Code Invariant #4:**<br>- `read_gate.py` added `_tinh_overlap_ratio(v1, v2)` (`intersection / min(len1, len2)`), `_dem_lap_doan(entries, fp, vung)` (threshold `>= 0.7`), and `_tao_thong_diep()`. Triggers `[TDQ:DOC]` warning when `lap_count >= 2` overlapping slices (`>= 70%`) even before total file reads hit 3!<br>- `soul.md` added **Invariant #4 (Reflective Thought & Hypothesis)**: form hypothesis before reading, read 100–300 lines whole instead of 30–50 line sliding windows, apply 5 Whys RCA. |
| **`v0.97.0`**<br>`01f48fe0`, `f1cce1c6`, `f523a55f`, `112e9945`, `b423ee06` | `scripts/doc_lint.py` (`+49` lines), `agents/tdq-implementer.md`, `skills/tdq-plan/references/{plan-template.md, plan-template-huong-dan.md}`, `skills/tdq-build/references/team-mode.md`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` | **Self-Contained Task Block, `doc_lint` R15, Mechanical Locks & Dynamic Model Tier Routing:**<br>- `doc_lint.py` added **`rule_r15`**: blocks any plan task with `Chạm:` touching code extensions (`.py/.ts/.tsx/.js/.jsx/.go/.rs/.c/.cpp/.cs/.rb/.php/.java`) if the task block lacks technical logic keywords (`"đặc tả"`, `"logic"`, `"giải thuật"`, `"thuật toán"`, `"pseudo-code"`).<br>- `plan-template.md` & `plan-template-huong-dan.md` standardized the **Self-Contained Task Block** (`Chạm`, `Cần`, `Mục tiêu`, `Vị trí neo`, `Công cụ`, `Ràng buộc`, `Đặc tả kỹ thuật`, `Logic cốt lõi`, `Ca góc hiểm & TDD`), Adaptive Granularity, and **4 Mechanical Safety Locks** (*Lock #2 hardcodes Claude tools: `Dùng Edit. CẤM dùng Write trên file có sẵn`!*).<br>- `agents/tdq-implementer.md` changed from `model: inherit` / `effort: high` to **`model: haiku` / `effort: medium`**.<br>- `team-mode.md` updated `TASK:` prompt to embed the full Task Block and added **Dynamic Model Tier Routing** (`haiku` default → leader overrides `model: sonnet` or `opus` for complex tasks). |

### 2.2 Dirty & Untracked Files in `dev` Working Tree

`git status -u` on `C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow` shows **5 modified tracked files** and **1 untracked file** (plus gitignored `docs/tdq/state.json` on disk):

1. **`docs/tdq/brief/2026-11-11-1435-chan-tu-sua-khi-feedback.md` (Untracked — CRITICAL UNFINISHED BUGFIX):**
   - Documents a real live failure observed right after `v0.97.0`: when the user gives bug feedback or reports a defect after a report/idle state, the AI immediately jumps into reading and editing source files without running root-cause analysis or waiting for user approval.
   - **Root Cause Verified in `hooks/scripts/edit_gate.py:115-117 & 137-155`:**
     - If `state is None` (`state.json` missing) or `active_request == ""`, `edit_gate.py` returns `allow`!
     - Even when `active_request` IS set, if `phase == "idle"` or `phase == "report"` after an earlier completed request (where `spec_approved`/`plan_approved` or `quick_approved` are already `True`), `cong_dang_cho(state)` returns `None`, so `edit_gate.py` returns `allow`!
   - **Planned 3-Layer Fix in Brief:**
     1. `edit_gate.py`: Hard-block source code edits whenever `phase != "implement"` (and not in an active `qc` fix round) with error tag **`[TDQ:FEEDBACK]`**, forcing intake/triage first.
     2. `prompt_context.py`: Detect feedback/bug signals when `phase == "idle"` / `"report"` and inject a Triage reminder.
     3. `soul.md` + `skills/tdq-intake/references/issue-triage.md`: Add **Clean Code Invariant #5 (*"Triage Before Touch"*)** (Classify → Root Cause → Impact Assessment → Options → Wait for User Choice).
2. **`docs/tdq/STATE.md` (Modified) & `docs/tdq/state.json` (Gitignored on disk):**
   - Opened request `2026-11-11-1435-chan-tu-sua-khi-feedback` (`lane: "quick"`, `phase: "idle"`, `quick_approved: false`, `lsp_bo_qua` set). Zero code changes made yet.
3. **`docs/tdq/.tdq-phat-hanh.json` (Modified):** Timestamp bumped `13:00:00` → `2026-11-11T14:58:11` (`phien_ban: "0.97.0"`).
4. **`docs/architecture/status.json` (Modified):** `checked_at` bumped to `2026-11-11T07:58:36Z` (currently `stale: true` on `spec-template.md` and `test_context_hooks.py`).
5. **`docs/tdq/timing.jsonl` & `docs/workinglog/2026-11-11.md` (Modified):** Appended session timing entry and `14:58` workinglog note for `2026-11-11-1435`.

### 2.3 Unmerged Local Branches, Active Worktrees & Stashes

| Ref / Worktree / Stash | Commit SHA | Merged into `dev`? | Verification Evidence |
|---|---|---|---|
| `bugfix/giam-timeout-agent-lsp` | `3e0ef5f8` | **YES** (ancestor) | `git merge-base --is-ancestor 3e0ef5f8 dev` → `0` |
| `bugfix/do-dung-bao-toan-loi` | `6ca709ea` | **YES** (ancestor) | `git merge-base --is-ancestor 6ca709ea dev` → `0` |
| `bugfix/kiem-chung-tang-toc` | `4cefc130` | **YES** (ancestor) | `git merge-base --is-ancestor 4cefc130 dev` → `0` |
| `feature/va-lo-hong-edit-gate-3-tang` | `d6116f2c` | **YES** (ancestor) | `git merge-base --is-ancestor d6116f2c dev` → `0` |
| `local-sync` | `fd11ac4c` | **YES** (ancestor) | `git merge-base --is-ancestor fd11ac4c dev` → `0` |
| All `chore/*`, `feature/*`, `tdq/*` (12 branches) | Various | **YES** (all ancestors) | `git branch --no-merged dev` lists ONLY `main` and the 2 worktree branches below |
| Worktree 1: `.claude/worktrees/agent-a37e138360abceb26` (`worktree-agent-a37e138360abceb26`) | `b493bfc0` | **YES (patch-identical to `436c30f9` on `dev`)** | `git show --format= b493bfc0 == git show --format= 436c30f9` (`True`, `4,054 == 4,054` chars: `fix(intake): bo hanh vi tu suy dien ranh gioi...`). Only untracked file inside is `runtime-71ef6fde.json` QA evidence. |
| Worktree 2: `.claude/worktrees/agent-a45a16c73f42c0ad5` (`worktree-agent-a45a16c73f42c0ad5`) | `60c8123f` | **YES (patch-identical to `fd11ac4c` on `dev`)** | `git show --format= 60c8123f == git show --format= fd11ac4c` (`True`, `3,322 == 3,322` chars: `chore: dong bo thay doi cuc bo...`). Clean working tree. |
| Leftover dirs: `.claude/worktrees/agent-a382d2d7ee2734e74` & `agent-ae5d0573024c25afd` | N/A (not registered worktrees) | N/A | Only contain `.pytest_cache` |
| `stash@{0}` .. `stash@{5}` (6 stashes) | `2026-10-25 15:43:58–15:44:01` | **Obsolete** | Named `archify-worktree-backup-t2.1..t3.3` from `2026-10-24-2348-hoan-thien-archify` (`v0.80–v0.84`), completely superseded in `dev`. |

---

## Section 3 — Exhaustive Gap Comparison vs `docs/AUDIT-AND-PORTING-PLAN.md`

Every item below was cross-checked line-by-line against `c:\Users\admin\Documents\Projects\TDQ-Workflow-Antigravity\docs\AUDIT-AND-PORTING-PLAN.md` (`279` lines):

### GAP-1 · `[P0 — Hook Adapter Blocker]` 5 Hook Scripts Bypass `_common.py` Output & Exit Protocol Directly
- **What `AUDIT-AND-PORTING-PLAN.md` assumes (Nhóm 3, lines `234–244`):** Assumes placing the Dual-Protocol stdout formatter in `hooks/scripts/_common.py` (`block()`, `remind()`, `allow()`) will adapt all hooks to Antigravity's single-JSON-object `stdout` contract.
- **Verified Reality in `hooks/scripts/*.py`:**
  1. `read_gate.py:187, 194, 217, 221-229` prints `{"hookSpecificOutput": ...}` directly via `_common.json.dumps(...)` and calls `sys.exit(0)` with empty `""` stdout on allow!
  2. `stop_gate.py:240, 250, 298, 321, 361` constructs and prints `{"decision": "block", "stop_hook_active": false}` and `{"hookSpecificOutput": {"hookEventName": "Stop", ...}}` directly, and returns `""` on allow (`lines 264, 266, 268, 357`)!
  3. `session_start.py:386` and `prompt_context.py:222, 246, 398, 426, 433` call `print(...)` with raw multi-line text directly (and `session_start.py:329` reads `payload.get("cwd") or os.getcwd()` directly instead of `payload_cwd(payload)`!).
  4. `search_observe.py:149, 169, 210, 217`, `search_gate.py:172, 180, 190`, `lsp_gate.py:138, 143, 158`, and `ask_gate.py:47, 52` call `sys.exit(0)` with empty `""` stdout instead of routing through `_common.allow(payload)`!
- **Required Plan Update (Nhóm 3):** Refactor all direct `print(...)` and bare `sys.exit(0)` calls across those hooks to route through host-aware helpers in `_common.py` (`emit_allow()`, `emit_context()`, `emit_stop_block()`, `payload_cwd()`).

### GAP-2 · `[P0 — Hook Logic Bug]` `v0.96.0` `read_gate.py` 70% Overlap Math Breaks on Antigravity `read_file` Parameters
- **What `AUDIT-AND-PORTING-PLAN.md` says (Nhóm 3, line `239`):** Says map `read_file.{Path,StartLine,EndLine} → Read.{file_path,offset,limit}` without accounting for `v0.96.0`'s new 70% range-overlap check (`read_gate.py:39-105, 161-200`).
- **Verified Reality:**
  - Antigravity `read_file` uses 1-based inclusive `StartLine` and `EndLine` (omitting `StartLine` starts at line `1`; omitting `EndLine` reads up to `800` lines).
  - In `read_gate.py:44-50`, `_vung(offset, limit)` computes `(offset, offset + limit)` when `offset > 0 and limit > 0`, else `(0, 0)`. In `_tinh_overlap_ratio` (`line 58`), `chieu_dai <= 0` returns `0.0`!
  - Therefore, if an agent calls `read_file(Path="foo.py", StartLine=100)` (omitting `EndLine`) and the adapter maps `limit=0`, `_vung(100, 0)` becomes `(0, 0)` (treated as whole-file read instead of slice!), OR if `EndLine=150` without `StartLine` maps `offset=0, limit=150`, `_vung(0, 150)` ALSO becomes `(0, 0)`!
- **Required Plan Update (Nhóm 3):** Specify exact normalization for `read_file`:
  - Both `StartLine` and `EndLine` omitted → `offset=0, limit=0` (whole-file / initial 800-line read).
  - Either `StartLine` or `EndLine` present → `s = int(StartLine or 1)`, `limit = (int(EndLine) - s + 1) if EndLine is not None else 800`, `offset = s`.

### GAP-3 · `[P0 — Setup / Host Contamination Bug]` `tdq_setup.doc_phien_ban_plugin()` Returns `None` on Antigravity & `thuc_hien_setup_bu()` Mutates Claude/Codex Files
- **What `AUDIT-AND-PORTING-PLAN.md` misses (Nhóm 1 & Nhóm 5):** Does not audit `scripts/tdq_setup.py`'s runtime version/sync path called from `hooks/scripts/session_start.py:332-343`.
- **Verified Reality (`scripts/tdq_setup.py`):**
  1. `doc_phien_ban_plugin(goc_plugin)` (`lines 1495-1507`) checks ONLY `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`. On Antigravity (`~/.gemini/config/plugins/tdq-workflow`, which has root `plugin.json`), it returns `None`! Likewise `claude_export.plugin_version()` (`claude_export.py:213-218`) only reads `.claude-plugin/plugin.json`.
  2. In `session_start.py:333-342`, every session calls `tu_dong_cap_nhat_plugin_user()`, `kich_hoat_kiem_tra_remote_nen()`, and `tu_dong_cap_nhat_khi_doi_phien_ban(cwd)` → `thuc_hien_setup_bu()` (`tdq_setup.py:1534-1546`), which unconditionally:
     - Injects Claude's `<!-- TDQ:TOOLS -->` (`mcp__lsp__*`, `tdq-workflow:tdq-intake`) into `~/.claude/CLAUDE.md`;
     - Spawns `claude plugin marketplace update` in the background;
     - Writes `.codex/hooks.json` into the workspace;
     - Never checks or updates Antigravity's `~/.gemini/config/plugins/tdq-workflow` or `mcp_config.json`!
- **Required Plan Update (Nhóm 1 & Nhóm 5):**
  1. Add `"plugin.json"` fallback to `tdq_setup.doc_phien_ban_plugin()` (and `claude_export.plugin_version()`).
  2. Make `session_start.py` and `tdq_setup.py` host-aware (`host == "antigravity"`): skip Claude/Codex mutations when running inside Antigravity, and verify Antigravity MCP/plugin health instead.

### GAP-4 · `[P1 — Lifecycle Drift]` No Release / Update Sync Mechanism Keeps `~/.gemini/config/plugins/tdq-workflow` Current
- **What `AUDIT-AND-PORTING-PLAN.md` misses:** Fixes `--sinh-agy` in Nhóm 1, **but has no mechanism to prevent Antigravity from drifting behind again** (which is why `~/.gemini/config/plugins/tdq-workflow` froze at `v0.74.0` for 23 releases).
- **Required Plan Update (Nhóm 1 / Nhóm 6):** Either (a) deploy directly as a standalone repo/plugin in `TDQ-Workflow-Antigravity` with an install/sync script (`scripts/install_agy_plugin.py` or `build_portable.py --install-agy`) that copies/verifies into `~/.gemini/config/plugins/tdq-workflow`, AND/OR (b) wire `--sinh-agy` into the release script / `tdq_setup.py` host update path so version bumps automatically refresh `~/.gemini/config/plugins/tdq-workflow`.

### GAP-5 · `[P1 — `v0.97.0` Subagent Schema Mismatch]` `model: haiku` & Dynamic Model Tier Routing vs Antigravity `Model` Enum
- **What `AUDIT-AND-PORTING-PLAN.md` misses (Nhóm 4, lines `246–262`):** Written before noticing `v0.97.0` (`01f48fe0`, `f523a55f`) changed `agents/tdq-implementer.md` to `model: haiku` / `effort: medium` and added **Dynamic Model Tier Routing** (`haiku` / `sonnet` / `opus`) to `skills/tdq-build/references/team-mode.md`!
- **Verified Reality on Antigravity:**
  - `invoke_subagent`'s `Model` enum ONLY accepts: `"inherit" | "flash_lite" | "flash" | "pro"` (passing `"haiku"`, `"sonnet"`, or `"opus"` causes an immediate tool schema error!).
  - Furthermore, Antigravity's `invoke_subagent` instruction states: *"Default to 'inherit' unless the user explicitly requests a different model"* (except `browser`, which defaults to `"flash"`).
- **Required Plan Update (Nhóm 2 & Nhóm 4):**
  - Strip unsupported `model: haiku` / `effort: medium` from Antigravity `agents/*.md` frontmatter (or verify exact supported keys in `agy-customizations`).
  - Translate `team-mode.md`'s *Dynamic Model Tier Routing* section for Antigravity: default `Model: "inherit"` (or map small mechanical tasks → `"flash"` / complex architectural tasks → `"pro"` only when permitted by Antigravity subagent rules, never `"haiku"`/`"sonnet"`/`"opus"`).

### GAP-6 · `[P1 — `v0.97.0` Prompt Translation]` `plan-template.md` & `plan-template-huong-dan.md` Hardcode Claude `Edit`/`Write` Tool Names in Mechanical Lock #2
- **What `AUDIT-AND-PORTING-PLAN.md` misses (Nhóm 2, lines `226–233`):** Lists `AGENTS.md`, `SKILL.md`, and `agents/*.md` for tool-name translation, missing `v0.97.0`'s newly added `Công cụ:` field in `skills/tdq-plan/references/plan-template.md:56` and `plan-template-huong-dan.md:51`:
  - `Công cụ: <Dùng Edit. CẤM dùng Write trên file có sẵn...>`
- **Required Plan Update (Nhóm 2):** Translate `plan-template.md` and `plan-template-huong-dan.md` to Antigravity's native file tools (`Dùng edit_file. CẤM dùng write_file (Overwrite=true) trên file có sẵn...`) so implementer subagents following Mechanical Safety Lock #2 do not hallucinate `Edit`/`Write` tool calls.

### GAP-7 · `[P1 — Security / Workflow Gate Loophole]` Unfinished `dev` Request `2026-11-11-1435-chan-tu-sua-khi-feedback` (`[TDQ:FEEDBACK]`)
- **What `AUDIT-AND-PORTING-PLAN.md` misses:** Unaware of the untracked brief `docs/tdq/brief/2026-11-11-1435-chan-tu-sua-khi-feedback.md` in `dev`'s working tree.
- **Verified Reality:** `edit_gate.py:115-117, 137-155` currently allows source code edits whenever `state is None`, `active_request == ""`, or `phase in ("idle", "report")` (because `cong_dang_cho(state)` is `None` once prior gates were approved).
- **Required Plan Update (Nhóm 3 & Nhóm 2):** Document and decide whether to include the `[TDQ:FEEDBACK]` phase guard in `edit_gate.py` + Clean Code Invariant #5 (*"Triage Before Touch"*) in `soul.md` during porting so Antigravity does not inherit this known bug.

### GAP-8 · `[P1 — Subagent Security Boundary]` `edit_gate.py` & `bash_gate.py` Rely on `payload.get("agent_id")` (Absent on Antigravity) + Missing `SubagentStart`
- **What `AUDIT-AND-PORTING-PLAN.md` misses (Nhóm 3 & Nhóm 4):** Maps `conversationId`, `workspacePaths`, `lastUserInput`, and `toolCall`, **but overlooks `payload.get("agent_id")`** (`edit_gate.py:103, 125` and `bash_gate.py:136`) and `hooks/scripts/subagent_start.py`!
- **Verified Reality:**
  - `edit_gate.py` (`TDQ:STATE` blocking subagents from editing `state.json`/`STATE.md`) and `bash_gate.py` (`TDQ:STATE` / `TDQ:TEAM` blocking subagents from running `tdq_state.py` or `git commit/merge/push`) ONLY trigger when `bool(payload.get("agent_id"))` is `True`!
  - Antigravity has **no `SubagentStart` hook** and **no `agent_id` field** in its `PreToolUse` payload — instead, subagent invocations pass through `PreToolUse` on `invoke_subagent` (in the parent conversation) and subsequent subagent tool calls carry the subagent's own `conversationId`!
- **Required Plan Update (Nhóm 3 & Nhóm 4):**
  1. Intercept `PreToolUse` on `invoke_subagent` (or record spawned subagent state / parent `conversationId` in `.tdq-parent-conv` during `SessionStart`) so `edit_gate.py` and `bash_gate.py` can detect `conversationId != leader_conversationId` as `is_subagent = True`!
  2. Fold `subagent_start.py`'s `[TDQ:GON]` brevity rules directly into `agents/tdq-*.md` system prompts (since `SubagentStart` does not exist on Antigravity).

### GAP-9 · `[P2 — Packaging Bug]` `RELEASE_EXCLUDE_SCRIPTS` Has **13** Scripts (Including `tdq_knowledge.py`!), Breaking `tdq_harvest.py` if Applied Blindly
- **What `AUDIT-AND-PORTING-PLAN.md` says (lines `158` & `275`):**
  - Line `158` (Nhóm 1): *"Áp dụng đúng bộ lọc `RELEASE_EXCLUDE_SCRIPTS` (loại bỏ 12 script dev/canvas nội bộ) cho nhánh build Antigravity."*
  - Line `275` (Nhóm 6): *"Fix mismatch schema `status:` vs `trang_thai:` giữa `tdq_harvest.py` và `tdq_knowledge.py`."*
- **Verified Reality (`scripts/build_portable.py:72-77`):**
  - `RELEASE_EXCLUDE_SCRIPTS` actually contains **13 scripts** (plus `scripts/samples/*`), and **`tdq_knowledge.py` is inside `RELEASE_EXCLUDE_SCRIPTS`**, whereas `tdq_harvest.py` is NOT excluded (so `main` ships `tdq_harvest.py` without `tdq_knowledge.py`)!
- **Required Plan Update (Nhóm 1 & Nhóm 6):** Do NOT copy `RELEASE_EXCLUDE_SCRIPTS` blindly if `tdq_knowledge.py` is meant to be usable alongside `tdq_harvest.py` in Antigravity — either keep `tdq_knowledge.py` in the Antigravity bundle (exclude only the 12 internal canvas/eval/lint-dev scripts + `scripts/samples/*`) or exclude both together.

### GAP-10 · `[P2 — Source Baseline Clarity]` `main` / `origin` (`v0.95.0`) vs Local `dev` (`v0.97.0`) 48-Commit Gap
- **What `AUDIT-AND-PORTING-PLAN.md` misses (Section 1.1):** States source repo is `v0.97.0` without noting that `main` and `origin/main` (and the user's active Claude Code installation!) are still at **`v0.95.0` (`6f03655c`)** — 48 commits behind local `dev` (`b423ee06`).
- **Required Plan Update:** Explicitly pin the Antigravity port baseline to **`dev@b423ee06` (`v0.97.0`)** (NOT `main@6f03655c`), because `v0.96.0` (`_archify_gate`, `_chan_report_thieu`, `read_gate` 70% overlap, `soul.md` #4) and `v0.97.0` (`doc_lint` R15, Self-Contained Task Blocks, Mechanical Safety Locks) live exclusively on local `dev`.

### GAP-11 · `[P2 — Export Tooling Debt]` `claude-export/` Hardcodes macOS Paths & Ships Unfiltered on `main`
- **What `AUDIT-AND-PORTING-PLAN.md` misses:**
  1. `build_portable.py:36` depends on `from claude_export import plugin_version, sha256_of` at runtime.
  2. `claude-export/local-repos.json` hardcodes `/Users/truongdinhquoc/...` (fails on Windows without `--local-repos`).
  3. `RELEASE_EXCLUDE_DIRS` has typo `ClaudeExport` instead of `claude-export`.
- **Required Plan Update (Nhóm 1):** Decouple `plugin_version` / `sha256_of` from `claude_export.py` (or keep `claude-export/` excluded in Antigravity plugin builds while ensuring `build_portable.py` handles root `plugin.json`).

### GAP-12 · `[P2 — Broken Bundled Skill]` `portable_src/skills/tdq-checkportable/SKILL.md` Calls Removed `--trust` Flag & Claude Paths
- **What `AUDIT-AND-PORTING-PLAN.md` misses (Nhóm 1, line `220`):** Plans to bundle `12 skills` (`11` core + `tdq-checkportable`), omitting from the implementation checklist (though previously spotted in `04-antigravity-adapter-audit.md:70`) that `portable_src/skills/tdq-checkportable/SKILL.md` instructs running `python3 scripts/tdq_checkportable.py setup --trust` (which crashes with exit code `2` since `--trust` was removed in `v0.50.0`) and checks `.claude/settings.json` instead of `~/.gemini/config/plugins/tdq-workflow/hooks/hooks.json` & `mcp_config.json`!
- **Required Plan Update (Nhóm 1 / Nhóm 2):** Rewrite `tdq-checkportable/SKILL.md` (and `tdq_checkportable.py` if bundled) for Antigravity's layout (`plugin.json`, `hooks/hooks.json`, `rules/AGENTS.md`, `mcp_config.json`). Also update stale `README.md` version badge (`0.89.0` → `0.97.0`).

---

## Summary Checklist Mapping Gaps to `AUDIT-AND-PORTING-PLAN.md` Work Groups

| Porting Plan Group | Newly Discovered Gaps to Fold In |
|---|---|
| **Nhóm 1 (Build & Packaging)** | `GAP-4` (auto-sync/install into `~/.gemini/config/plugins/tdq-workflow`), `GAP-9` (`RELEASE_EXCLUDE_SCRIPTS` has **13** scripts incl. `tdq_knowledge.py` + `scripts/samples/*`), `GAP-10` (pin baseline to `dev@b423ee06` `v0.97.0`, not `main@6f03655c`), `GAP-11` (`claude_export.plugin_version` dependency), `GAP-12` (fix `tdq-checkportable/SKILL.md` `--trust` crash + `README.md` `0.89.0` badge). |
| **Nhóm 2 (Rules & Tool Mapping)** | `GAP-5` (translate `team-mode.md` Dynamic Model Tier Routing `haiku/sonnet/opus` → Antigravity `Model` rules), `GAP-6` (translate `v0.97.0` `plan-template.md` & `plan-template-huong-dan.md` Mechanical Lock #2 `Edit`/`Write` → `edit_file`/`write_file`), `GAP-7` (`soul.md` Invariant #5 *"Triage Before Touch"* awareness). |
| **Nhóm 3 (Dual-Protocol Hooks)** | `GAP-1` (refactor direct `print()` / `sys.exit(0)` in `read_gate.py`, `stop_gate.py`, `session_start.py`, `prompt_context.py`, `search_observe.py`, `search_gate.py`, `lsp_gate.py`, `ask_gate.py`), `GAP-2` (`v0.96.0` `read_gate.py` `StartLine`/`EndLine` 70% range-overlap normalization), `GAP-7` (`[TDQ:FEEDBACK]` idle/report edit loophole in `edit_gate.py`), `GAP-8` (subagent identity detection without `payload["agent_id"]`). |
| **Nhóm 4 (Subagent Architecture)** | `GAP-5` (strip/adapt `v0.97.0` `model: haiku` / `effort: medium` in `agents/tdq-implementer.md`), `GAP-8` (fold `subagent_start.py` `[TDQ:GON]` into `agents/tdq-*.md` since Antigravity lacks `SubagentStart`). |
| **Nhóm 5 (LSP & Setup Sync)** | `GAP-3` (`tdq_setup.doc_phien_ban_plugin()` returns `None` on root `plugin.json`; gate `thuc_hien_setup_bu()`, `tu_dong_cap_nhat_plugin_user()`, and `kich_hoat_kiem_tra_remote_nen()` by host so Antigravity sessions do not mutate `~/.claude` / `.codex`). |
| **Nhóm 6 (Source Bugfixes)** | `GAP-9` (ensure `tdq_knowledge.py` isn't excluded while fixing `tdq_harvest.py` ↔ `tdq_knowledge.py` `status:`/`trang_thai:` mismatch). |
