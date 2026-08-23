# Graph Report - TDQWorkflow  (2026-08-23)

## Corpus Check
- 60 files · ~82,006 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1171 nodes · 2203 edges · 56 communities (51 shown, 5 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 108 edges (avg confidence: 0.63)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9bbdfa3d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- canvas_a4_rebuild.py
- doc_lint.py
- tdq_lsp.py
- tdq_checkstatus.py
- claude_export.py
- tdq_bench.py
- skill_inventory.py
- _common.py
- skill_tokens.py
- tdq_checkportable.py
- Changelog — bản lưu trữ
- build_portable.py
- tdq_worktree_registry.py
- lenh_soat
- tdq_state.py
- token_audit.py
- tdq_timing.py
- tdq_finish.py
- doc_dup.py
- check_canvas_layout.py
- _bash
- cli
- step_audit.py
- tdq_eval.py
- context_surface.py
- LoiThieuSo
- log
- tdq_team.py
- plugin_tiers.py
- _log
- main
- turn_snapshot
- main
- main
- luat_phan_loai.py
- effective_lane
- _boi_canh
- chia_dot
- i18n_check.py
- lenh_bao_cao
- _fail
- chay_va_cham
- tdq-workflow — Plugin Claude Code
- _chuyen_tick
- quet
- dod_tick_state
- Lưới hồi quy: đo độ tuân thủ luật TDQ
- Task
- bao-loi/seed/src/tien_ich.py
- _chung/seed/src/tien_ich.py
- chay_bo
- _duong_dan_ghi_bash
- sha256_noi_dung
- iter_events
- seed/README.md
- Exception

## God Nodes (most connected - your core abstractions)
1. `cli()` - 24 edges
2. `lenh_soat()` - 20 edges
3. `Changelog — bản lưu trữ` - 17 edges
4. `_git()` - 17 edges
5. `log()` - 17 edges
6. `cmd_build()` - 17 edges
7. `Changelog` - 16 edges
8. `main()` - 16 edges
9. `_log()` - 16 edges
10. `main()` - 16 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `effective_lane()`  [INFERRED]
  hooks/scripts/prompt_context.py → scripts/tdq_state.py
- `main()` --calls--> `effective_mode()`  [INFERRED]
  hooks/scripts/prompt_context.py → scripts/tdq_state.py
- `main()` --calls--> `effective_phase()`  [INFERRED]
  hooks/scripts/prompt_context.py → scripts/tdq_state.py
- `main()` --calls--> `load()`  [INFERRED]
  hooks/scripts/prompt_context.py → scripts/tdq_state.py
- `main()` --calls--> `phase_key()`  [INFERRED]
  hooks/scripts/prompt_context.py → scripts/tdq_state.py

## Import Cycles
- None detected.

## Communities (56 total, 5 thin omitted)

### Community 0 - "canvas_a4_rebuild.py"
Cohesion: 0.06
Nodes (47): build_ch4(), build_ch7(), build_all(), build_generic(), build_moved(), build_toc(), Builder, chapter_elements() (+39 more)

### Community 1 - "doc_lint.py"
Cohesion: 0.06
Nodes (49): collect(), Doc, _doc_lang(), _lane_cua_spec(), lint_file(), _log(), main(), pair() (+41 more)

### Community 2 - "tdq_lsp.py"
Cohesion: 0.08
Nodes (46): Bac, bac1_binary(), bac2_mcp(), bac3_language_server(), bac4_quyen_tool(), bac5_lumen(), bac6_hook_xung_dot(), chay_kiem() (+38 more)

### Community 3 - "tdq_checkstatus.py"
Cohesion: 0.08
Nodes (45): bao_cao_markdown(), _ca(), cham_ca_lech(), _cham_d2(), _cham_d3(), _cham_d5(), _cham_d6(), _cham_d7() (+37 more)

### Community 4 - "claude_export.py"
Cohesion: 0.09
Nodes (44): cli_versions(), clone_repo(), cmd_build(), cmd_check(), collect_config_files(), copy_config(), copy_launch_agents(), copy_repo_memory() (+36 more)

### Community 5 - "tdq_bench.py"
Cohesion: 0.09
Nodes (43): _agent_stub(), build_parser(), dem_cap_chong(), _do_mot_luot(), _do_tick(), _doc_mau_that(), _dung_repo_tam(), _git() (+35 more)

### Community 6 - "skill_inventory.py"
Cohesion: 0.08
Nodes (35): _clean(), _condense(), _enabled_plugins(), _filter(), _frontmatter(), inventory(), _load_json(), main() (+27 more)

### Community 7 - "_common.py"
Cohesion: 0.12
Nodes (34): _check_signal_mismatch(), _clean(), _latest_signal(), main(), The LATEST kind="signal" row matching target (walking the turn ledger backwards), already_reminded(), approve_hint(), block() (+26 more)

### Community 8 - "skill_tokens.py"
Cohesion: 0.09
Nodes (36): ban_do_skill_md(), _chu(), dem_qua_venv(), do_mo_ta(), do_theo_phase(), _in_bang(), khoa_tra(), lenh_mo_ta() (+28 more)

### Community 9 - "tdq_checkportable.py"
Cohesion: 0.10
Nodes (35): bat_trusted(), bien_moi_truong_mcp(), chay_setup(), da_trusted(), _doc(), doc_manifest(), duong_config_codex(), ghi_de_co_backup() (+27 more)

### Community 10 - "Changelog — bản lưu trữ"
Cohesion: 0.06
Nodes (33): 0.16.0 — 2026-08-14, 0.17.0 — 2026-08-14, 0.18.0 — 2026-08-14, 0.19.0 — 2026-08-15, 0.20.0 — 2026-08-15, 0.21.0 — 2026-08-16, 0.22.0 — 2026-08-16, 0.23.0 — 2026-08-17 (+25 more)

### Community 11 - "build_portable.py"
Cohesion: 0.11
Nodes (34): _bo_qua_file(), _bo_qua_thu_muc(), copy_loc(), dem_bien_trong_cay(), doc_frontmatter(), _doc_text(), doi_bien_plugin_root(), _ghi_json() (+26 more)

### Community 12 - "tdq_worktree_registry.py"
Cohesion: 0.12
Nodes (30): doc(), _doc_de_ghi(), dong_dong(), dong_mo(), duong_md(), duong_so(), _ghi(), ghi_md() (+22 more)

### Community 13 - "lenh_soat"
Cohesion: 0.11
Nodes (30): _da_merge(), _doc_mb(), _file_ban(), _file_bo_qua_dang_ke(), _git(), _go_thu_muc(), _in_goi_y(), _khoa_khong() (+22 more)

### Community 14 - "tdq_state.py"
Cohesion: 0.09
Nodes (27): _atomic_write(), _echo_state(), lane_label(), parse_slug(), _parse_value(), plugin_root_cmd(), _pop_json_flag(), prompt_context_last() (+19 more)

### Community 15 - "token_audit.py"
Cohesion: 0.12
Nodes (25): classify(), _content_text(), dem_anh(), dem_nhieu(), dem_token(), _khoa(), _kich_thuoc_jpeg(), _kich_thuoc_png() (+17 more)

### Community 16 - "tdq_timing.py"
Cohesion: 0.14
Nodes (24): _has_usage(), _parse_time(), bang_markdown(), cua_so_phase(), da_dong_so(), dinh_dang(), dong_ho_ngan(), dong_so() (+16 more)

### Community 17 - "tdq_finish.py"
Cohesion: 0.15
Nodes (22): _changed_files(), _log(), _log_enabled(), main(), _now(), parse_args(), _project_dir(), Back to `idle` = the request is over → close the timing books into docs/tdq/timi (+14 more)

### Community 18 - "doc_dup.py"
Cohesion: 0.12
Nodes (23): _bam_shingle(), _cap_tho(), cli(), dem_token_loat(), doc_dong(), _gop_lien_ke(), in_bang(), log() (+15 more)

### Community 19 - "check_canvas_layout.py"
Cohesion: 0.16
Nodes (21): bbox(), boxes_overlap(), center(), check_chapters(), check_contain(), check_fontsize(), check_order(), check_overlap() (+13 more)

### Community 20 - "_bash"
Cohesion: 0.10
Nodes (23): _bash(), _ca(), kiem_L002(), kiem_L035(), kiem_L121(), kiem_L136(), kiem_L149(), kiem_L218() (+15 more)

### Community 21 - "cli"
Cohesion: 0.17
Nodes (23): cli(), _cli_approve(), default_state(), _dong_so_request_cu(), find_shadow_states(), ghi_moc_phase(), _info(), load() (+15 more)

### Community 22 - "step_audit.py"
Cohesion: 0.15
Nodes (20): _blocks(), _log(), _log_enabled(), main(), median(), merge(), _now(), percentile() (+12 more)

### Community 23 - "tdq_eval.py"
Cohesion: 0.13
Nodes (19): build_parser(), _chay_test(), _ghi_ma_nguon(), kiem_L001(), kiem_L005(), kiem_L010(), kiem_L012(), kiem_L209() (+11 more)

### Community 24 - "context_surface.py"
Cohesion: 0.18
Nodes (19): _log(), _log_enabled(), main(), measure_hooks(), _num(), _payload(), print_table(), Scan the whole documentation surface, returning the list of table rows. (+11 more)

### Community 25 - "LoiThieuSo"
Cohesion: 0.16
Nodes (19): cham_lai_tat_ca(), cham_mot_ma(), cham_phien(), doc_bo_ca(), doc_transcript(), lay_token(), lenh_cham(), lenh_chay() (+11 more)

### Community 26 - "log"
Cohesion: 0.13
Nodes (19): chay_phien(), dong_log(), dung_lenh(), dung_moi_truong(), dung_sandbox(), _git(), kiem_dich(), lenh_dung_nhanh() (+11 more)

### Community 27 - "tdq_team.py"
Cohesion: 0.15
Nodes (17): b_level(), build_parser(), _do_xung_dot(), _file_xung_dot(), _kich_thuoc(), lenh_kiem_ke(), _log_enabled(), _loi() (+9 more)

### Community 28 - "plugin_tiers.py"
Cohesion: 0.34
Nodes (16): _claude_dir(), cmd_enable(), cmd_reset(), cmd_status(), _key_for(), _load_json(), _log(), _log_on() (+8 more)

### Community 29 - "_log"
Cohesion: 0.22
Nodes (17): _bao_dam_tich_hop(), _co_nhanh(), _duong_worktree(), _la_repo(), lenh_hop(), lenh_kiem(), lenh_mo(), _log() (+9 more)

### Community 30 - "main"
Cohesion: 0.19
Nodes (15): _dod_hint(), _log_changed(), main(), The file name to quote in the block message — a file new in this turn wins., [TDQ:DOD] — a REMINDER, never a block: the books are being closed while checkbox, The start-of-turn snapshot — take the NEWEST row.      Normally there is one row, Did today's log change since the start of the turn (however it was written)?, _repo_changed() (+7 more)

### Community 31 - "turn_snapshot"
Cohesion: 0.18
Nodes (15): _git(), plan_tick_state(), stdout (bytes) of a git command, or None when it cannot run., Repo root (porcelain prints paths from the root, not from cwd). None if not a re, Fingerprint of an untracked file → (mark, bytes read).      CONTENT first: a cha, Fingerprint of the repo working state, or None when it cannot be taken.      Cov, Paths differing from HEAD (status flags dropped, renames keep the target)., Checkbox state of the current plan. Never raises. (+7 more)

### Community 32 - "main"
Cohesion: 0.15
Nodes (15): _all_items(), carry_cost(), cost_equivalent(), _fmt(), main(), phan_ra(), _phan_vi(), The carry-cost table grouped by bucket, descending. `paths` empty → empty table. (+7 more)

### Community 33 - "main"
Cohesion: 0.22
Nodes (13): _compact(), _emit(), looks_like_approval(), main(), mode_from_answer(), _nhac_worktree(), An answer at the mode gate -> the machine identifier, or None if unreadable., One line, only while the ledger holds an open row — silent the rest of the time. (+5 more)

### Community 34 - "luat_phan_loai.py"
Cohesion: 0.19
Nodes (13): bang_nhap(), doc_bang(), doc_ranh_gioi(), goi_y_nhan(), liet_ke_ma(), _log(), main(), The suggested label for one anchor, with its reason.      The order runs from th (+5 more)

### Community 35 - "effective_lane"
Cohesion: 0.20
Nodes (14): cong_dang_cho(), effective_lane(), effective_mode(), next_headline(), phase_key(), phase_row(), The PHASE_TABLE lookup key for the current state., The PHASE_TABLE row to DISPLAY for the current state.      Unlike `phase_key`, t (+6 more)

### Community 36 - "_boi_canh"
Cohesion: 0.20
Nodes (14): _boi_canh(), canh_bao_lach_luat(), doc_plan(), duong_ban_do(), lenh_cum(), lenh_phan_cong(), _ly_do_hoan(), The user picked team mode but the leader types code of a task it promised away → (+6 more)

### Community 37 - "chia_dot"
Cohesion: 0.14
Nodes (14): chia_dot(), _chia_dot_theo_phase(), _chia_dot_theo_phu_thuoc(), doc_phu_thuoc(), _dot_som_nhat(), _khoa_phase(), _la_file_luat(), quyet_dinh_task() (+6 more)

### Community 38 - "i18n_check.py"
Cohesion: 0.24
Nodes (11): allowed_fence_lines(), collect(), _log(), main(), python_line_kinds(), Return one finding dict per Vietnamese line of a single file., Log service: one ISO-timestamp line on stderr. Off with TDQ_LOG=0.      On stder, Expand files and directories into a sorted list of files to scan. (+3 more)

### Community 39 - "lenh_bao_cao"
Cohesion: 0.17
Nodes (12): bao_cao_so(), doc_ban_ghi(), don_vi_kiem(), _in_bang(), kiem_dinh_dau(), lenh_bao_cao(), Build the whole audit file out of the table. No hand-typed number gets in., Read every scored session record. No record at all → return an empty list. (+4 more)

### Community 40 - "_fail"
Cohesion: 0.17
Nodes (12): _chan_worktree_con_mo(), _fail(), normalize_doc_lang(), normalize_lane(), _parse_approve_args(), _pop_lang_flag(), Return the normalised language code, or None when it is not a valid code.      A, -> (target, mode, by, no_qc). Fails only on genuinely wrong syntax. (+4 more)

### Community 41 - "chay_va_cham"
Cohesion: 0.18
Nodes (11): chay_va_cham(), dau_nhiem(), dau_nhiem_phien(), _ghi_ban_ghi(), _noi_dung(), phan_tich(), The content of a tool_result may be a string or a list of text blocks., Normalise a stream-json transcript into what the scorer reads.      Returns: the (+3 more)

### Community 42 - "tdq-workflow — Plugin Claude Code"
Cohesion: 0.22
Nodes (8): Cài đặt (chỉ trong repo/project), Cách hook điều khiển agent, Cấu trúc, Duyệt bằng chat thường, Dùng hằng ngày, Pipeline, Quy ước cứng, tdq-workflow — Plugin Claude Code

### Community 43 - "_chuyen_tick"
Cohesion: 0.22
Nodes (9): _chuyen_tick(), kiem_L003(), kiem_L013(), kiem_L145(), The sequence (call index, task code, new mark) pulled from every write to the pl, Tick `[~]` first, `[x]` after, and never bulk-tick several tasks at once., Flip `[~]` to `[x]` AT ONCE: at no moment do two tasks carry `[~]`., Every task has its own test: between its `[~]` and `[x]` there must be a test ru (+1 more)

### Community 44 - "quet"
Cohesion: 0.36
Nodes (7): khoi_mau(), la_ky_hieu(), main(), quet(), True when ch is non-ASCII punctuation/symbol — what the whitelist has to govern., The content of the ``` blocks in a file — this is what is REALLY printed to the, {character: (total count, {file: count})} for every non-ASCII symbol.

### Community 45 - "dod_tick_state"
Cohesion: 0.25
Nodes (8): _dod_section(), dod_tick_state(), _plan_path(), Absolute path of the plan of the active request, or None when there is none., Every line under a DoD heading, up to the next `## ` heading.      Three details, Checkbox state of the plan's Definition of Done section. Never raises., How many task boxes of the current plan are not `[x]` yet. Never raises.      A, task_open_count()

### Community 46 - "Lưới hồi quy: đo độ tuân thủ luật TDQ"
Cohesion: 0.40
Nodes (4): Bộ ca, Chạy lại — một lệnh, Lưới hồi quy: đo độ tuân thủ luật TDQ, Đọc kết quả

### Community 50 - "chay_bo"
Cohesion: 0.50
Nodes (4): chay_bo(), Work still to run, interleaved between branches on every run.      Interleaved s, Run the whole round. Returns (total cost, whether it stopped early on the cap)., viec_con_lai()

### Community 51 - "_duong_dan_ghi_bash"
Cohesion: 0.50
Nodes (4): _duong_dan_ghi_bash(), _duong_dan_sed(), The file `sed -i` overwrites. Split with shlex because a sed expression often us, The paths one Bash command WRITES to. Reading a file does not count, only writin

### Community 52 - "sha256_noi_dung"
Cohesion: 0.50
Nodes (4): _file_changed_since_approval(), True when the spec/plan file changed since it was approved. It tells     'a redu, Hash the CONTENT part of a spec/plan: from the first `##` heading onward.      W, sha256_noi_dung()

### Community 53 - "iter_events"
Cohesion: 0.50
Nodes (4): hanh_vi_read(), iter_events(), Yield the jsonl records one by one. A broken/empty line is skipped without spoil, Measure `Read` behaviour: how many calls, how many carry `offset`/`limit`, how m

## Knowledge Gaps
- **42 isolated node(s):** `0.31.0 — 2026-08-23`, `0.29.0 — 2026-08-22`, `0.28.0 — 2026-08-22`, `0.27.0 — 2026-08-22`, `0.26.0 — 2026-08-18` (+37 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Task` connect `Task` to `tdq_team.py`, `_boi_canh`?**
  _High betweenness centrality (0.006) - this node is a cross-community bridge._
- **Why does `prompt_context_last()` connect `tdq_state.py` to `main`, `cli`?**
  _High betweenness centrality (0.006) - this node is a cross-community bridge._
- **Why does `mode_label()` connect `_common.py` to `tdq_state.py`?**
  _High betweenness centrality (0.006) - this node is a cross-community bridge._
- **What connects `0.31.0 — 2026-08-23`, `0.29.0 — 2026-08-22`, `0.28.0 — 2026-08-22` to the rest of the system?**
  _42 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `canvas_a4_rebuild.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06293706293706294 - nodes in this community are weakly interconnected._
- **Should `doc_lint.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05878084179970972 - nodes in this community are weakly interconnected._
- **Should `tdq_lsp.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08078231292517007 - nodes in this community are weakly interconnected._