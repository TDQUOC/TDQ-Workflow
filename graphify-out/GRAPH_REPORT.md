# Graph Report - TDQWorkflow  (2026-08-24)

## Corpus Check
- 62 files · ~92,641 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1335 nodes · 2538 edges · 64 communities (59 shown, 5 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 120 edges (avg confidence: 0.63)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8f5f0f28`
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
- skill_tokens.py
- Changelog
- _common.py
- tdq_checkportable.py
- build_portable.py
- mindmap_render.py
- cli
- tdq_worktree_registry.py
- tdq_mindmap.py
- lenh_soat
- tdq_state.py
- token_audit.py
- tdq_timing.py
- tdq_finish.py
- main
- doc_dup.py
- main
- check_canvas_layout.py
- _bash
- cmd_xem
- step_audit.py
- tdq_eval.py
- context_surface.py
- LoiThieuSo
- log
- tdq_team.py
- plugin_tiers.py
- render_state_md
- _log
- plan_tick_state
- main
- luat_phan_loai.py
- _boi_canh
- chia_dot
- comment_mask
- check_diagram
- i18n_check.py
- render_total_page
- lenh_bao_cao
- _fail
- chay_va_cham
- cross_check_diagram
- tdq-workflow — Plugin Claude Code
- _chuyen_tick
- quet
- dod_tick_state
- Lưới hồi quy: đo độ tuân thủ luật TDQ
- DiagramInvalid
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
1. `cli()` - 27 edges
2. `lenh_soat()` - 20 edges
3. `load()` - 19 edges
4. `Changelog` - 18 edges
5. `_warn()` - 17 edges
6. `Changelog — bản lưu trữ` - 17 edges
7. `_git()` - 17 edges
8. `log()` - 17 edges
9. `cmd_build()` - 17 edges
10. `main()` - 16 edges

## Surprising Connections (you probably didn't know these)
- `_sha()` --calls--> `sha256_file()`  [INFERRED]
  hooks/scripts/stop_gate.py → scripts/tdq_state.py
- `_repo_changed()` --calls--> `repo_status_digest()`  [INFERRED]
  hooks/scripts/stop_gate.py → scripts/tdq_state.py
- `_repo_changed()` --calls--> `_warn()`  [INFERRED]
  hooks/scripts/stop_gate.py → scripts/tdq_state.py
- `_shell_changed_path()` --calls--> `repo_status_paths()`  [INFERRED]
  hooks/scripts/stop_gate.py → scripts/tdq_state.py
- `_dod_hint()` --calls--> `dod_tick_state()`  [INFERRED]
  hooks/scripts/stop_gate.py → scripts/tdq_state.py

## Import Cycles
- None detected.

## Communities (64 total, 5 thin omitted)

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

### Community 7 - "skill_tokens.py"
Cohesion: 0.09
Nodes (36): ban_do_skill_md(), _chu(), dem_qua_venv(), do_mo_ta(), do_theo_phase(), _in_bang(), khoa_tra(), lenh_mo_ta() (+28 more)

### Community 8 - "Changelog"
Cohesion: 0.05
Nodes (35): 0.16.0 — 2026-08-14, 0.17.0 — 2026-08-14, 0.18.0 — 2026-08-14, 0.19.0 — 2026-08-15, 0.20.0 — 2026-08-15, 0.21.0 — 2026-08-16, 0.22.0 — 2026-08-16, 0.23.0 — 2026-08-17 (+27 more)

### Community 9 - "_common.py"
Cohesion: 0.13
Nodes (32): _check_signal_mismatch(), _clean(), _latest_signal(), main(), The LATEST kind="signal" row matching target (walking the turn ledger backwards), already_reminded(), approve_hint(), block() (+24 more)

### Community 10 - "tdq_checkportable.py"
Cohesion: 0.10
Nodes (35): bat_trusted(), bien_moi_truong_mcp(), chay_setup(), da_trusted(), _doc(), doc_manifest(), duong_config_codex(), ghi_de_co_backup() (+27 more)

### Community 11 - "build_portable.py"
Cohesion: 0.11
Nodes (34): _bo_qua_file(), _bo_qua_thu_muc(), copy_loc(), dem_bien_trong_cay(), doc_frontmatter(), _doc_text(), doi_bien_plugin_root(), _ghi_json() (+26 more)

### Community 12 - "mindmap_render.py"
Cohesion: 0.10
Nodes (30): build_call_tree(), CallNode, count_calls(), docstring_first_line(), GraphIndex, _layout(), _leaf_count(), _module_ast() (+22 more)

### Community 13 - "cli"
Cohesion: 0.12
Nodes (33): cli(), _cli_approve(), _cli_approve_diagram(), _cli_diagram(), _cli_implement_pause(), default_state(), _dong_so_request_cu(), _echo_state() (+25 more)

### Community 14 - "tdq_worktree_registry.py"
Cohesion: 0.12
Nodes (30): doc(), _doc_de_ghi(), dong_dong(), dong_mo(), duong_md(), duong_so(), _ghi(), ghi_md() (+22 more)

### Community 15 - "tdq_mindmap.py"
Cohesion: 0.11
Nodes (29): build_link_graph(), build_parser(), cmd_doi_chieu(), cmd_kiem(), cmd_lien_he(), cmd_sinh(), default_title(), feature_path() (+21 more)

### Community 16 - "lenh_soat"
Cohesion: 0.11
Nodes (30): _da_merge(), _doc_mb(), _file_ban(), _file_bo_qua_dang_ke(), _git(), _go_thu_muc(), _in_goi_y(), _khoa_khong() (+22 more)

### Community 17 - "tdq_state.py"
Cohesion: 0.10
Nodes (25): _atomic_write(), lane_label(), parse_slug(), _parse_value(), plugin_root_cmd(), prompt_context_last(), prompt_context_path(), prompt_context_save() (+17 more)

### Community 18 - "token_audit.py"
Cohesion: 0.12
Nodes (25): classify(), _content_text(), dem_anh(), dem_nhieu(), dem_token(), _khoa(), _kich_thuoc_jpeg(), _kich_thuoc_png() (+17 more)

### Community 19 - "tdq_timing.py"
Cohesion: 0.14
Nodes (24): _has_usage(), _parse_time(), bang_markdown(), cua_so_phase(), da_dong_so(), dinh_dang(), dong_ho_ngan(), dong_so() (+16 more)

### Community 20 - "tdq_finish.py"
Cohesion: 0.15
Nodes (22): _changed_files(), _log(), _log_enabled(), main(), _now(), parse_args(), _project_dir(), Back to `idle` = the request is over → close the timing books into docs/tdq/timi (+14 more)

### Community 21 - "main"
Cohesion: 0.13
Nodes (23): _chan_chua_xong(), _dod_hint(), _log_changed(), main(), The file name to quote in the block message — a file new in this turn wins., [TDQ:DOD] — a REMINDER, never a block: the books are being closed while checkbox, Reason to refuse the end of a turn while the plan still has open tasks, or None., Blocks in a row against the SAME plan content; resets as soon as a checkbox move (+15 more)

### Community 22 - "doc_dup.py"
Cohesion: 0.12
Nodes (23): _bam_shingle(), _cap_tho(), cli(), dem_token_loat(), doc_dong(), _gop_lien_ke(), in_bang(), log() (+15 more)

### Community 23 - "main"
Cohesion: 0.13
Nodes (22): _compact(), _emit(), looks_like_approval(), main(), mode_from_answer(), _nhac_worktree(), An answer at the mode gate -> the machine identifier, or None if unreadable., One line, only while the ledger holds an open row — silent the rest of the time. (+14 more)

### Community 24 - "check_canvas_layout.py"
Cohesion: 0.16
Nodes (21): bbox(), boxes_overlap(), center(), check_chapters(), check_contain(), check_fontsize(), check_order(), check_overlap() (+13 more)

### Community 25 - "_bash"
Cohesion: 0.10
Nodes (23): _bash(), _ca(), kiem_L002(), kiem_L035(), kiem_L121(), kiem_L136(), kiem_L149(), kiem_L218() (+15 more)

### Community 26 - "cmd_xem"
Cohesion: 0.13
Nodes (22): build_parser(), collect_total_data(), default_output_path(), default_total_output_path(), load_graph(), main(), The parsed graph dict, or None when the file is missing/unreadable/corrupt., Build the full two-layer HTML page for one feature. Pure: no file I/O.      Rais (+14 more)

### Community 27 - "step_audit.py"
Cohesion: 0.15
Nodes (20): _blocks(), _log(), _log_enabled(), main(), median(), merge(), _now(), percentile() (+12 more)

### Community 28 - "tdq_eval.py"
Cohesion: 0.13
Nodes (19): build_parser(), _chay_test(), _ghi_ma_nguon(), kiem_L001(), kiem_L005(), kiem_L010(), kiem_L012(), kiem_L209() (+11 more)

### Community 29 - "context_surface.py"
Cohesion: 0.18
Nodes (19): _log(), _log_enabled(), main(), measure_hooks(), _num(), _payload(), print_table(), Scan the whole documentation surface, returning the list of table rows. (+11 more)

### Community 30 - "LoiThieuSo"
Cohesion: 0.16
Nodes (19): cham_lai_tat_ca(), cham_mot_ma(), cham_phien(), doc_bo_ca(), doc_transcript(), lay_token(), lenh_cham(), lenh_chay() (+11 more)

### Community 31 - "log"
Cohesion: 0.13
Nodes (19): chay_phien(), dong_log(), dung_lenh(), dung_moi_truong(), dung_sandbox(), _git(), kiem_dich(), lenh_dung_nhanh() (+11 more)

### Community 32 - "tdq_team.py"
Cohesion: 0.15
Nodes (17): b_level(), build_parser(), _do_xung_dot(), _file_xung_dot(), _kich_thuoc(), lenh_kiem_ke(), _log_enabled(), _loi() (+9 more)

### Community 33 - "plugin_tiers.py"
Cohesion: 0.34
Nodes (16): _claude_dir(), cmd_enable(), cmd_reset(), cmd_status(), _key_for(), _load_json(), _log(), _log_on() (+8 more)

### Community 34 - "render_state_md"
Cohesion: 0.15
Nodes (17): _chan_so_do_chua_duyet(), diagram_entries(), _diagram_id(), diagram_pending(), _diagram_register(), effective_mode(), _heal_diagrams(), phase_row() (+9 more)

### Community 35 - "_log"
Cohesion: 0.22
Nodes (17): _bao_dam_tich_hop(), _co_nhanh(), _duong_worktree(), _la_repo(), lenh_hop(), lenh_kiem(), lenh_mo(), _log() (+9 more)

### Community 36 - "plan_tick_state"
Cohesion: 0.18
Nodes (15): _git(), plan_tick_state(), stdout (bytes) of a git command, or None when it cannot run., Repo root (porcelain prints paths from the root, not from cwd). None if not a re, Fingerprint of an untracked file → (mark, bytes read).      CONTENT first: a cha, Fingerprint of the repo working state, or None when it cannot be taken.      Cov, Paths differing from HEAD (status flags dropped, renames keep the target)., Checkbox state of the current plan. Never raises. (+7 more)

### Community 37 - "main"
Cohesion: 0.15
Nodes (15): _all_items(), carry_cost(), cost_equivalent(), _fmt(), main(), phan_ra(), _phan_vi(), The carry-cost table grouped by bucket, descending. `paths` empty → empty table. (+7 more)

### Community 38 - "luat_phan_loai.py"
Cohesion: 0.19
Nodes (13): bang_nhap(), doc_bang(), doc_ranh_gioi(), goi_y_nhan(), liet_ke_ma(), _log(), main(), The suggested label for one anchor, with its reason.      The order runs from th (+5 more)

### Community 39 - "_boi_canh"
Cohesion: 0.20
Nodes (14): _boi_canh(), canh_bao_lach_luat(), doc_plan(), duong_ban_do(), lenh_cum(), lenh_phan_cong(), _ly_do_hoan(), The user picked team mode but the leader types code of a task it promised away → (+6 more)

### Community 40 - "chia_dot"
Cohesion: 0.14
Nodes (14): chia_dot(), _chia_dot_theo_phase(), _chia_dot_theo_phu_thuoc(), doc_phu_thuoc(), _dot_som_nhat(), _khoa_phase(), _la_file_luat(), quyet_dinh_task() (+6 more)

### Community 41 - "comment_mask"
Cohesion: 0.15
Nodes (12): parse_diagram(), One parsed step: its number, whether it is an error branch, and location., Structured read of an ALREADY-VALID diagram: title, branch, depends, steps., Step, comment_mask(), extract_depends(), mind_map_dir(), Absolute path of the diagram directory of a project. (+4 more)

### Community 42 - "check_diagram"
Cohesion: 0.19
Nodes (12): _check_branch(), _check_depends(), check_diagram(), _check_steps(), _check_title(), One broken rule, at one 1-based line. `str()` renders the report line., The first content line must be the title; anything else loses the feature name., Exactly one branch line: none leaves the feature unplaced, two place it twice. (+4 more)

### Community 43 - "i18n_check.py"
Cohesion: 0.24
Nodes (11): allowed_fence_lines(), collect(), _log(), main(), python_line_kinds(), Return one finding dict per Vietnamese line of a single file., Log service: one ISO-timestamp line on stderr. Off with TDQ_LOG=0.      On stder, Expand files and directories into a sorted list of files to scan. (+3 more)

### Community 44 - "render_total_page"
Cohesion: 0.17
Nodes (12): _feature_levels(), _layout_grid(), Longest-path depth of each slug: 0 with no depends, else 1 + its deepest dep., `(positions, columns)` — positions keyed by slug, columns keyed by level., Boxes for every feature (dashed + dim when it has no file yet) and one     label, The same edges as the SVG, spelled out as text — every reason legible     withou, Top branch -> sub branch -> feature, general down to the business page —     nes, Build the self-contained aggregate HTML page: branch tree + dependency grid. (+4 more)

### Community 45 - "lenh_bao_cao"
Cohesion: 0.17
Nodes (12): bao_cao_so(), doc_ban_ghi(), don_vi_kiem(), _in_bang(), kiem_dinh_dau(), lenh_bao_cao(), Build the whole audit file out of the table. No hand-typed number gets in., Read every scored session record. No record at all → return an empty list. (+4 more)

### Community 46 - "_fail"
Cohesion: 0.17
Nodes (12): _chan_worktree_con_mo(), _fail(), normalize_doc_lang(), normalize_lane(), _parse_approve_args(), _pop_lang_flag(), Return the normalised language code, or None when it is not a valid code.      A, -> (target, mode, by, no_qc, diagram). Fails only on genuinely wrong syntax. (+4 more)

### Community 47 - "chay_va_cham"
Cohesion: 0.18
Nodes (11): chay_va_cham(), dau_nhiem(), dau_nhiem_phien(), _ghi_ban_ghi(), _noi_dung(), phan_tich(), The content of a tool_result may be a string or a list of text blocks., Normalise a stream-json transcript into what the scorer reads.      Returns: the (+3 more)

### Community 48 - "cross_check_diagram"
Cohesion: 0.20
Nodes (10): code_node_pairs(), cross_check_diagram(), diagram_step_locations(), filter_code_nodes(), node_function_name(), Every node with `file_type == "code"` — nothing else tells a code node from, The bare function name a code node's label stands for.      A function-level nod, Pure: the `{(source_file, function)}` pairs a list of code nodes stands for. (+2 more)

### Community 49 - "tdq-workflow — Plugin Claude Code"
Cohesion: 0.22
Nodes (8): Cài đặt (chỉ trong repo/project), Cách hook điều khiển agent, Cấu trúc, Duyệt bằng chat thường, Dùng hằng ngày, Pipeline, Quy ước cứng, tdq-workflow — Plugin Claude Code

### Community 50 - "_chuyen_tick"
Cohesion: 0.22
Nodes (9): _chuyen_tick(), kiem_L003(), kiem_L013(), kiem_L145(), The sequence (call index, task code, new mark) pulled from every write to the pl, Tick `[~]` first, `[x]` after, and never bulk-tick several tasks at once., Flip `[~]` to `[x]` AT ONCE: at no moment do two tasks carry `[~]`., Every task has its own test: between its `[~]` and `[x]` there must be a test ru (+1 more)

### Community 51 - "quet"
Cohesion: 0.36
Nodes (7): khoi_mau(), la_ky_hieu(), main(), quet(), True when ch is non-ASCII punctuation/symbol — what the whitelist has to govern., The content of the ``` blocks in a file — this is what is REALLY printed to the, {character: (total count, {file: count})} for every non-ASCII symbol.

### Community 52 - "dod_tick_state"
Cohesion: 0.33
Nodes (6): _dod_section(), dod_tick_state(), _plan_path(), Absolute path of the plan of the active request, or None when there is none., Every line under a DoD heading, up to the next `## ` heading.      Three details, Checkbox state of the plan's Definition of Done section. Never raises.

### Community 53 - "Lưới hồi quy: đo độ tuân thủ luật TDQ"
Cohesion: 0.40
Nodes (4): Bộ ca, Chạy lại — một lệnh, Lưới hồi quy: đo độ tuân thủ luật TDQ, Đọc kết quả

### Community 54 - "DiagramInvalid"
Cohesion: 0.40
Nodes (3): DiagramInvalid, The diagram fails check_diagram; carries the violations for the caller to print., ValueError

### Community 58 - "chay_bo"
Cohesion: 0.50
Nodes (4): chay_bo(), Work still to run, interleaved between branches on every run.      Interleaved s, Run the whole round. Returns (total cost, whether it stopped early on the cap)., viec_con_lai()

### Community 59 - "_duong_dan_ghi_bash"
Cohesion: 0.50
Nodes (4): _duong_dan_ghi_bash(), _duong_dan_sed(), The file `sed -i` overwrites. Split with shlex because a sed expression often us, The paths one Bash command WRITES to. Reading a file does not count, only writin

### Community 60 - "sha256_noi_dung"
Cohesion: 0.50
Nodes (4): _file_changed_since_approval(), True when the spec/plan file changed since it was approved. It tells     'a redu, Hash the CONTENT part of a spec/plan: from the first `##` heading onward.      W, sha256_noi_dung()

### Community 61 - "iter_events"
Cohesion: 0.50
Nodes (4): hanh_vi_read(), iter_events(), Yield the jsonl records one by one. A broken/empty line is skipped without spoil, Measure `Read` behaviour: how many calls, how many carry `offset`/`limit`, how m

## Knowledge Gaps
- **44 isolated node(s):** `0.33.0 — 2026-08-24`, `0.32.0 — 2026-08-23`, `0.31.0 — 2026-08-23`, `0.29.0 — 2026-08-22`, `0.28.0 — 2026-08-22` (+39 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Task` connect `Task` to `tdq_team.py`, `_boi_canh`?**
  _High betweenness centrality (0.006) - this node is a cross-community bridge._
- **Why does `normalize_mode()` connect `main` to `tdq_state.py`, `_fail`?**
  _High betweenness centrality (0.005) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `load()` (e.g. with `main()` and `main()`) actually correct?**
  _`load()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `_warn()` (e.g. with `_repo_changed()` and `_streak_bump()`) actually correct?**
  _`_warn()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `0.33.0 — 2026-08-24`, `0.32.0 — 2026-08-23`, `0.31.0 — 2026-08-23` to the rest of the system?**
  _44 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `canvas_a4_rebuild.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06293706293706294 - nodes in this community are weakly interconnected._
- **Should `doc_lint.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05878084179970972 - nodes in this community are weakly interconnected._