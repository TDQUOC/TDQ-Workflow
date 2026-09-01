# Graph Report - TDQWorkflow  (2026-08-27)

## Corpus Check
- 101 files · ~168,938 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2620 nodes · 4867 edges · 125 communities (116 shown, 9 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 196 edges (avg confidence: 0.62)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4f12b3bd`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- files
- antigravity_portable/scripts/canvas_a4_rebuild.py
- scripts/canvas_a4_rebuild.py
- scripts/skill_tokens.py
- antigravity_portable/scripts/doc_lint.py
- scripts/doc_lint.py
- antigravity_portable/scripts/tdq_mindmap.py
- antigravity_portable/scripts/tdq_lsp.py
- scripts/tdq_lsp.py
- antigravity_portable/scripts/tdq_checkstatus.py
- cli
- scripts/tdq_checkstatus.py
- antigravity_portable/scripts/claude_export.py
- antigravity_portable/scripts/tdq_bench.py
- scripts/claude_export.py
- scripts/tdq_bench.py
- scripts/tdq_mindmap.py
- main
- scripts/skill_inventory.py
- scripts/mindmap_render.py
- Changelog
- antigravity_portable/scripts/mindmap_render.py
- antigravity_portable/scripts/skill_tokens.py
- antigravity_portable/scripts/tdq_state.py
- scripts/tdq_checkportable.py
- cli
- _common.py
- antigravity_portable/scripts/tdq_worktree_registry.py
- scripts/tdq_state.py
- scripts/tdq_worktree_registry.py
- main
- lenh_soat
- lenh_soat
- antigravity_portable/scripts/tdq_checkportable.py
- antigravity_portable/scripts/token_audit.py
- main
- build_portable.py
- scripts/token_audit.py
- antigravity_portable/scripts/tdq_timing.py
- antigravity_portable/scripts/tdq_finish.py
- scripts/tdq_timing.py
- scripts/tdq_finish.py
- antigravity_portable/scripts/doc_dup.py
- render_total_page
- antigravity_portable/scripts/check_canvas_layout.py
- scripts/check_canvas_layout.py
- _bash
- antigravity_portable/scripts/skill_router.py
- antigravity_portable/scripts/step_audit.py
- scripts/step_audit.py
- tdq_eval.py
- antigravity_portable/scripts/context_surface.py
- _num
- antigravity_portable/scripts/skill_inventory.py
- scripts/context_surface.py
- _num
- main
- LoiThieuSo
- log
- antigravity_portable/scripts/tdq_team.py
- scripts/tdq_team.py
- main
- antigravity_portable/scripts/plugin_tiers.py
- _log
- scripts/plugin_tiers.py
- _log
- check_diagram
- build_call_tree
- main
- main
- antigravity_portable/scripts/luat_phan_loai.py
- _ghi_json
- render_state_md
- _boi_canh
- chia_dot
- scripts/luat_phan_loai.py
- cross_check_diagram
- _boi_canh
- chia_dot
- check_diagram
- antigravity_portable/scripts/i18n_check.py
- diagram_entries
- scripts/i18n_check.py
- main
- lenh_bao_cao
- chay_va_cham
- antigravity_portable/hooks/scripts/agy_pretooluse_gate.py
- hooks/scripts/agy_pretooluse_gate.py
- manifest.json
- tdq-workflow — Plugin Claude Code
- _chuyen_tick
- quet
- dod_tick_state
- render_total_page
- quet
- DiagramInvalid
- TDQ Workflow — portable bundle for Antigravity CLI (agy)
- _parse_approve_args
- state_path
- Task
- Lưới hồi quy: đo độ tuân thủ luật TDQ
- Task
- bien_moi_truong_mcp
- _sinh_settings
- cross_check_diagram
- _file_changed_since_approval
- iter_events
- bao-loi/seed/src/tien_ich.py
- _chung/seed/src/tien_ich.py
- chay_bo
- _duong_dan_ghi_bash
- sha256_noi_dung
- _parse_approve_args
- iter_events
- mode_label
- seed/README.md
- doc_frontmatter
- tach_duong_dan_patch
- Exception
- _report
- render_feature_page
- lint_file
- rule_r12
- Doc
- rule_r7

## God Nodes (most connected - your core abstractions)
1. `files` - 86 edges
2. `cli()` - 27 edges
3. `cli()` - 27 edges
4. `Changelog` - 20 edges
5. `lenh_soat()` - 20 edges
6. `lenh_soat()` - 20 edges
7. `load()` - 20 edges
8. `load()` - 18 edges
9. `log()` - 17 edges
10. `cmd_build()` - 17 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `plugin_version()`  [INFERRED]
  scripts/build_portable.py → antigravity_portable/scripts/claude_export.py
- `_continue()` --calls--> `now_iso()`  [INFERRED]
  hooks/scripts/agy_stop_gate.py → antigravity_portable/scripts/tdq_state.py
- `_current_snapshot()` --calls--> `repo_status_paths()`  [INFERRED]
  hooks/scripts/agy_stop_gate.py → antigravity_portable/scripts/tdq_state.py
- `main()` --calls--> `repo_status_paths()`  [INFERRED]
  hooks/scripts/agy_stop_gate.py → antigravity_portable/scripts/tdq_state.py
- `main()` --calls--> `effective_phase()`  [INFERRED]
  hooks/scripts/agy_stop_gate.py → antigravity_portable/scripts/tdq_state.py

## Import Cycles
- None detected.

## Communities (125 total, 9 thin omitted)

### Community 0 - "files"
Cohesion: 0.02
Nodes (86): files, config/hooks.json, config/mcp_config.json, config/settings.json, hooks/scripts/agy_pretooluse_gate.py, hooks/scripts/agy_stop_gate.py, README.md, scripts/canvas_a4_ch4_ch7.py (+78 more)

### Community 1 - "antigravity_portable/scripts/canvas_a4_rebuild.py"
Cohesion: 0.06
Nodes (47): build_ch4(), build_ch7(), build_all(), build_generic(), build_moved(), build_toc(), Builder, chapter_elements() (+39 more)

### Community 2 - "scripts/canvas_a4_rebuild.py"
Cohesion: 0.06
Nodes (47): build_ch4(), build_ch7(), build_all(), build_generic(), build_moved(), build_toc(), Builder, chapter_elements() (+39 more)

### Community 3 - "scripts/skill_tokens.py"
Cohesion: 0.05
Nodes (59): _bam_shingle(), _cap_tho(), cli(), dem_token_loat(), doc_dong(), _gop_lien_ke(), in_bang(), log() (+51 more)

### Community 4 - "antigravity_portable/scripts/doc_lint.py"
Cohesion: 0.15
Nodes (17): collect(), _log(), main(), pair(), _plan_contracts(), _r9_in_scope(), A SKILL.md must state when it is done and where to go next., An over-long sentence makes a small model read the wrong emphasis. (+9 more)

### Community 5 - "scripts/doc_lint.py"
Cohesion: 0.06
Nodes (49): collect(), Doc, _doc_lang(), _lane_cua_spec(), lint_file(), _log(), main(), pair() (+41 more)

### Community 6 - "antigravity_portable/scripts/tdq_mindmap.py"
Cohesion: 0.08
Nodes (43): default_output_path(), `<root>/docs/tdq/mind-map/<slug>.html` from `<anything>/<slug>.md`., build_link_graph(), build_parser(), cmd_doi_chieu(), cmd_kiem(), cmd_lien_he(), cmd_sinh() (+35 more)

### Community 7 - "antigravity_portable/scripts/tdq_lsp.py"
Cohesion: 0.08
Nodes (46): Bac, bac1_binary(), bac2_mcp(), bac3_language_server(), bac4_quyen_tool(), bac5_lumen(), bac6_hook_xung_dot(), chay_kiem() (+38 more)

### Community 8 - "scripts/tdq_lsp.py"
Cohesion: 0.08
Nodes (46): Bac, bac1_binary(), bac2_mcp(), bac3_language_server(), bac4_quyen_tool(), bac5_lumen(), bac6_hook_xung_dot(), chay_kiem() (+38 more)

### Community 9 - "antigravity_portable/scripts/tdq_checkstatus.py"
Cohesion: 0.07
Nodes (46): bao_cao_markdown(), _ca(), cham_ca_lech(), _cham_d2(), _cham_d3(), _cham_d5(), _cham_d6(), _cham_d7() (+38 more)

### Community 10 - "cli"
Cohesion: 0.08
Nodes (47): _chan_so_do_chua_duyet(), _chan_worktree_con_mo(), cli(), _cli_approve(), _cli_approve_diagram(), _cli_diagram(), _cli_implement_pause(), default_state() (+39 more)

### Community 11 - "scripts/tdq_checkstatus.py"
Cohesion: 0.08
Nodes (45): bao_cao_markdown(), _ca(), cham_ca_lech(), _cham_d2(), _cham_d3(), _cham_d5(), _cham_d6(), _cham_d7() (+37 more)

### Community 12 - "antigravity_portable/scripts/claude_export.py"
Cohesion: 0.09
Nodes (44): cli_versions(), clone_repo(), cmd_build(), cmd_check(), collect_config_files(), copy_config(), copy_launch_agents(), copy_repo_memory() (+36 more)

### Community 13 - "antigravity_portable/scripts/tdq_bench.py"
Cohesion: 0.09
Nodes (43): _agent_stub(), build_parser(), dem_cap_chong(), _do_mot_luot(), _do_tick(), _doc_mau_that(), _dung_repo_tam(), _git() (+35 more)

### Community 14 - "scripts/claude_export.py"
Cohesion: 0.09
Nodes (44): cli_versions(), clone_repo(), cmd_build(), cmd_check(), collect_config_files(), copy_config(), copy_launch_agents(), copy_repo_memory() (+36 more)

### Community 15 - "scripts/tdq_bench.py"
Cohesion: 0.09
Nodes (43): _agent_stub(), build_parser(), dem_cap_chong(), _do_mot_luot(), _do_tick(), _doc_mau_that(), _dung_repo_tam(), _git() (+35 more)

### Community 16 - "scripts/tdq_mindmap.py"
Cohesion: 0.09
Nodes (41): build_link_graph(), build_parser(), cmd_doi_chieu(), cmd_kiem(), cmd_lien_he(), cmd_sinh(), cmd_xem(), default_title() (+33 more)

### Community 17 - "main"
Cohesion: 0.08
Nodes (40): _chan_chua_xong(), _dod_hint(), _log_changed(), main(), The file name to quote in the block message — a file new in this turn wins., [TDQ:DOD] — a REMINDER, never a block: the books are being closed while checkbox, Reason to refuse the end of a turn while the plan still has open tasks, or None., Blocks in a row against the SAME plan content; resets as soon as a checkbox move (+32 more)

### Community 18 - "scripts/skill_inventory.py"
Cohesion: 0.08
Nodes (35): _clean(), _condense(), _enabled_plugins(), _filter(), _frontmatter(), inventory(), _load_json(), main() (+27 more)

### Community 19 - "scripts/mindmap_render.py"
Cohesion: 0.08
Nodes (38): build_flow_model(), count_calls(), _feature_levels(), _flow_box(), GraphIndex, _grid_label(), _layout(), layout_branch_tree() (+30 more)

### Community 20 - "Changelog"
Cohesion: 0.05
Nodes (37): 0.16.0 — 2026-08-14, 0.17.0 — 2026-08-14, 0.18.0 — 2026-08-14, 0.19.0 — 2026-08-15, 0.20.0 — 2026-08-15, 0.21.0 — 2026-08-16, 0.22.0 — 2026-08-16, 0.23.0 — 2026-08-17 (+29 more)

### Community 21 - "antigravity_portable/scripts/mindmap_render.py"
Cohesion: 0.10
Nodes (28): build_call_tree(), CallNode, count_calls(), docstring_first_line(), GraphIndex, _layout(), _leaf_count(), _module_ast() (+20 more)

### Community 22 - "antigravity_portable/scripts/skill_tokens.py"
Cohesion: 0.09
Nodes (36): ban_do_skill_md(), _chu(), dem_qua_venv(), do_mo_ta(), do_theo_phase(), _in_bang(), khoa_tra(), lenh_mo_ta() (+28 more)

### Community 23 - "antigravity_portable/scripts/tdq_state.py"
Cohesion: 0.07
Nodes (35): _atomic_write(), find_shadow_states(), lane_label(), mode_label(), parse_slug(), _parse_value(), plugin_root_cmd(), prompt_context_last() (+27 more)

### Community 24 - "scripts/tdq_checkportable.py"
Cohesion: 0.10
Nodes (35): bat_trusted(), bien_moi_truong_mcp(), chay_setup(), da_trusted(), _doc(), doc_manifest(), duong_config_codex(), ghi_de_co_backup() (+27 more)

### Community 25 - "cli"
Cohesion: 0.12
Nodes (35): _chan_worktree_con_mo(), cli(), _cli_approve(), _cli_approve_diagram(), _cli_diagram(), _cli_implement_pause(), default_state(), _dong_so_request_cu() (+27 more)

### Community 26 - "_common.py"
Cohesion: 0.14
Nodes (31): _check_signal_mismatch(), _clean(), _latest_signal(), main(), The LATEST kind="signal" row matching target (walking the turn ledger backwards), already_reminded(), block(), echo_line() (+23 more)

### Community 27 - "antigravity_portable/scripts/tdq_worktree_registry.py"
Cohesion: 0.12
Nodes (30): doc(), _doc_de_ghi(), dong_dong(), dong_mo(), duong_md(), duong_so(), _ghi(), ghi_md() (+22 more)

### Community 28 - "scripts/tdq_state.py"
Cohesion: 0.09
Nodes (29): cong_dang_cho(), _dod_section(), effective_lane(), effective_mode(), lane_label(), next_headline(), parse_slug(), _parse_value() (+21 more)

### Community 29 - "scripts/tdq_worktree_registry.py"
Cohesion: 0.12
Nodes (30): doc(), _doc_de_ghi(), dong_dong(), dong_mo(), duong_md(), duong_so(), _ghi(), ghi_md() (+22 more)

### Community 30 - "main"
Cohesion: 0.11
Nodes (29): _git(), plan_tick_state(), stdout (bytes) of a git command, or None when it cannot run., Repo root (porcelain prints paths from the root, not from cwd). None if not a re, Fingerprint of an untracked file → (mark, bytes read).      CONTENT first: a cha, Fingerprint of the repo working state, or None when it cannot be taken.      Cov, Checkbox state of the current plan. Never raises., Turn-start state: today's log + the repo fingerprint + the list of dirty     pat (+21 more)

### Community 31 - "lenh_soat"
Cohesion: 0.11
Nodes (30): _da_merge(), _doc_mb(), _file_ban(), _file_bo_qua_dang_ke(), _git(), _go_thu_muc(), _in_goi_y(), _khoa_khong() (+22 more)

### Community 32 - "lenh_soat"
Cohesion: 0.11
Nodes (30): _da_merge(), _doc_mb(), _file_ban(), _file_bo_qua_dang_ke(), _git(), _go_thu_muc(), _in_goi_y(), _khoa_khong() (+22 more)

### Community 33 - "antigravity_portable/scripts/tdq_checkportable.py"
Cohesion: 0.14
Nodes (27): bat_trusted(), chay_setup(), da_trusted(), _doc(), doc_manifest(), duong_config_codex(), ghi_de_co_backup(), _ghi_json_co_backup() (+19 more)

### Community 34 - "antigravity_portable/scripts/token_audit.py"
Cohesion: 0.12
Nodes (25): classify(), _content_text(), dem_anh(), dem_nhieu(), dem_token(), _khoa(), _kich_thuoc_jpeg(), _kich_thuoc_png() (+17 more)

### Community 35 - "main"
Cohesion: 0.11
Nodes (25): _compact(), _emit(), looks_like_approval(), main(), mode_from_answer(), _nhac_worktree(), An answer at the mode gate -> the machine identifier, or None if unreadable., One line, only while the ledger holds an open row — silent the rest of the time. (+17 more)

### Community 36 - "build_portable.py"
Cohesion: 0.17
Nodes (25): _bo_qua_file(), _bo_qua_thu_muc(), copy_loc(), dem_bien_trong_cay(), _doc_text(), doi_bien_plugin_root(), ghi_manifest(), log() (+17 more)

### Community 37 - "scripts/token_audit.py"
Cohesion: 0.12
Nodes (25): classify(), _content_text(), dem_anh(), dem_nhieu(), dem_token(), _khoa(), _kich_thuoc_jpeg(), _kich_thuoc_png() (+17 more)

### Community 38 - "antigravity_portable/scripts/tdq_timing.py"
Cohesion: 0.14
Nodes (24): _has_usage(), _parse_time(), bang_markdown(), cua_so_phase(), da_dong_so(), dinh_dang(), dong_ho_ngan(), dong_so() (+16 more)

### Community 39 - "antigravity_portable/scripts/tdq_finish.py"
Cohesion: 0.15
Nodes (22): _changed_files(), _log(), _log_enabled(), main(), _now(), parse_args(), _project_dir(), Back to `idle` = the request is over → close the timing books into docs/tdq/timi (+14 more)

### Community 40 - "scripts/tdq_timing.py"
Cohesion: 0.14
Nodes (24): _has_usage(), _parse_time(), bang_markdown(), cua_so_phase(), da_dong_so(), dinh_dang(), dong_ho_ngan(), dong_so() (+16 more)

### Community 41 - "scripts/tdq_finish.py"
Cohesion: 0.15
Nodes (22): _changed_files(), _log(), _log_enabled(), main(), _now(), parse_args(), _project_dir(), Back to `idle` = the request is over → close the timing books into docs/tdq/timi (+14 more)

### Community 42 - "antigravity_portable/scripts/doc_dup.py"
Cohesion: 0.12
Nodes (23): _bam_shingle(), _cap_tho(), cli(), dem_token_loat(), doc_dong(), _gop_lien_ke(), in_bang(), log() (+15 more)

### Community 43 - "render_total_page"
Cohesion: 0.09
Nodes (24): build_branch_model(), _feature_levels(), _flow_box(), _grid_label(), layout_branch_tree(), layout_flow(), _layout_grid(), _max_chars() (+16 more)

### Community 44 - "antigravity_portable/scripts/check_canvas_layout.py"
Cohesion: 0.16
Nodes (21): bbox(), boxes_overlap(), center(), check_chapters(), check_contain(), check_fontsize(), check_order(), check_overlap() (+13 more)

### Community 45 - "scripts/check_canvas_layout.py"
Cohesion: 0.16
Nodes (21): bbox(), boxes_overlap(), center(), check_chapters(), check_contain(), check_fontsize(), check_order(), check_overlap() (+13 more)

### Community 46 - "_bash"
Cohesion: 0.10
Nodes (23): _bash(), _ca(), kiem_L002(), kiem_L035(), kiem_L121(), kiem_L136(), kiem_L149(), kiem_L218() (+15 more)

### Community 47 - "antigravity_portable/scripts/skill_router.py"
Cohesion: 0.17
Nodes (16): bo_dau(), doc_kho(), dung_kho(), ghi_kho(), KhoBM25, lenh_dung_kho(), lenh_tra(), _log() (+8 more)

### Community 48 - "antigravity_portable/scripts/step_audit.py"
Cohesion: 0.15
Nodes (20): _blocks(), _log(), _log_enabled(), main(), median(), merge(), _now(), percentile() (+12 more)

### Community 49 - "scripts/step_audit.py"
Cohesion: 0.15
Nodes (20): _blocks(), _log(), _log_enabled(), main(), median(), merge(), _now(), percentile() (+12 more)

### Community 50 - "tdq_eval.py"
Cohesion: 0.13
Nodes (19): build_parser(), _chay_test(), _ghi_ma_nguon(), kiem_L001(), kiem_L005(), kiem_L010(), kiem_L012(), kiem_L209() (+11 more)

### Community 51 - "antigravity_portable/scripts/context_surface.py"
Cohesion: 0.18
Nodes (19): _log(), _log_enabled(), main(), measure_hooks(), _num(), _payload(), print_table(), Scan the whole documentation surface, returning the list of table rows. (+11 more)

### Community 52 - "_num"
Cohesion: 0.17
Nodes (20): _num(), Boxes for every feature (dashed + dim when it has no file yet) and one     arrow, The branch tree as one figure: top branch → sub branch → feature.      A feature, Format a coordinate: integers stay integers, so the markup stays readable., A rounded rectangle — the shape of an ordinary step., A diamond filling the same box — the shape of a step that branches., A pill (corner radius = half the height) — the entry and exit points., A centred multi-line label: one `<tspan>` per line, vertically centred.      The (+12 more)

### Community 53 - "antigravity_portable/scripts/skill_inventory.py"
Cohesion: 0.15
Nodes (19): _clean(), _condense(), _enabled_plugins(), _filter(), _frontmatter(), inventory(), _load_json(), main() (+11 more)

### Community 54 - "scripts/context_surface.py"
Cohesion: 0.18
Nodes (19): _log(), _log_enabled(), main(), measure_hooks(), _num(), _payload(), print_table(), Scan the whole documentation surface, returning the list of table rows. (+11 more)

### Community 55 - "_num"
Cohesion: 0.17
Nodes (20): _num(), Boxes for every feature (dashed + dim when it has no file yet) and one     arrow, The branch tree as one figure: top branch → sub branch → feature.      A feature, Format a coordinate: integers stay integers, so the markup stays readable., A rounded rectangle — the shape of an ordinary step., A diamond filling the same box — the shape of a step that branches., A pill (corner radius = half the height) — the entry and exit points., A centred multi-line label: one `<tspan>` per line, vertically centred.      The (+12 more)

### Community 56 - "main"
Cohesion: 0.19
Nodes (18): _continue(), _current_snapshot(), _cwd_of(), _log_changed(), main(), The path to quote — a path new since the baseline wins over one already known., Ported verbatim (pure) from `hooks/scripts/stop_gate.py::unfinished_reason`., Force the loop onward, and say on stderr which of the 3 cases matched (TDQ_LOG=0 (+10 more)

### Community 57 - "LoiThieuSo"
Cohesion: 0.16
Nodes (19): cham_lai_tat_ca(), cham_mot_ma(), cham_phien(), doc_bo_ca(), doc_transcript(), lay_token(), lenh_cham(), lenh_chay() (+11 more)

### Community 58 - "log"
Cohesion: 0.13
Nodes (19): chay_phien(), dong_log(), dung_lenh(), dung_moi_truong(), dung_sandbox(), _git(), kiem_dich(), lenh_dung_nhanh() (+11 more)

### Community 59 - "antigravity_portable/scripts/tdq_team.py"
Cohesion: 0.15
Nodes (17): b_level(), build_parser(), _do_xung_dot(), _file_xung_dot(), _kich_thuoc(), lenh_kiem_ke(), _log_enabled(), _loi() (+9 more)

### Community 60 - "scripts/tdq_team.py"
Cohesion: 0.15
Nodes (17): b_level(), build_parser(), _do_xung_dot(), _file_xung_dot(), _kich_thuoc(), lenh_kiem_ke(), _log_enabled(), _loi() (+9 more)

### Community 61 - "main"
Cohesion: 0.13
Nodes (14): build_parser(), collect_total_data(), default_total_output_path(), load_graph(), main(), parse_diagram(), One parsed step: its number, whether it is an error branch, and location., Structured read of an ALREADY-VALID diagram: title, branch, depends, steps. (+6 more)

### Community 62 - "antigravity_portable/scripts/plugin_tiers.py"
Cohesion: 0.34
Nodes (16): _claude_dir(), cmd_enable(), cmd_reset(), cmd_status(), _key_for(), _load_json(), _log(), _log_on() (+8 more)

### Community 63 - "_log"
Cohesion: 0.22
Nodes (17): _bao_dam_tich_hop(), _co_nhanh(), _duong_worktree(), _la_repo(), lenh_hop(), lenh_kiem(), lenh_mo(), _log() (+9 more)

### Community 64 - "scripts/plugin_tiers.py"
Cohesion: 0.34
Nodes (16): _claude_dir(), cmd_enable(), cmd_reset(), cmd_status(), _key_for(), _load_json(), _log(), _log_on() (+8 more)

### Community 65 - "_log"
Cohesion: 0.22
Nodes (17): _bao_dam_tich_hop(), _co_nhanh(), _duong_worktree(), _la_repo(), lenh_hop(), lenh_kiem(), lenh_mo(), _log() (+9 more)

### Community 66 - "check_diagram"
Cohesion: 0.19
Nodes (12): _check_branch(), _check_depends(), check_diagram(), _check_steps(), _check_title(), One broken rule, at one 1-based line. `str()` renders the report line., The first content line must be the title; anything else loses the feature name., Exactly one branch line: none leaves the feature unplaced, two place it twice. (+4 more)

### Community 67 - "build_call_tree"
Cohesion: 0.12
Nodes (14): build_call_tree(), docstring_first_line(), _module_ast(), _node_display_label(), _node_match_core(), _parse_line(), The label shown to the reader — the node's own label, unchanged (e.g. `foo()`)., The bare callable name used to MATCH a node against a step's `func`.      Stripp (+6 more)

### Community 68 - "main"
Cohesion: 0.15
Nodes (15): _all_items(), carry_cost(), cost_equivalent(), _fmt(), main(), phan_ra(), _phan_vi(), The carry-cost table grouped by bucket, descending. `paths` empty → empty table. (+7 more)

### Community 69 - "main"
Cohesion: 0.15
Nodes (15): _all_items(), carry_cost(), cost_equivalent(), _fmt(), main(), phan_ra(), _phan_vi(), The carry-cost table grouped by bucket, descending. `paths` empty → empty table. (+7 more)

### Community 70 - "antigravity_portable/scripts/luat_phan_loai.py"
Cohesion: 0.19
Nodes (13): bang_nhap(), doc_bang(), doc_ranh_gioi(), goi_y_nhan(), liet_ke_ma(), _log(), main(), The suggested label for one anchor, with its reason.      The order runs from th (+5 more)

### Community 71 - "_ghi_json"
Cohesion: 0.15
Nodes (14): The content of `.mcp.json`: servers + env variable NAMES only, never a key value, sinh_mcp(), _ghi_json(), Write JSON byte-for-byte the way `tdq_checkportable._ghi_json_co_backup` writes, `.codex/config.toml` — declare MCP servers in the Codex `[mcp_servers.<name>]` s, `.codex/hooks.json` — the same wire shape as `hooks/hooks.json`, other matchers, `config/hooks.json` — commands point at the ONE fixed canonical core path (`GOC_, `config/settings.json` — permissions engine layer 2, coarser than the hook on pu (+6 more)

### Community 72 - "render_state_md"
Cohesion: 0.20
Nodes (14): cong_dang_cho(), effective_lane(), effective_mode(), next_headline(), phase_key(), phase_row(), The PHASE_TABLE lookup key for the current state., The PHASE_TABLE row to DISPLAY for the current state.      Unlike `phase_key`, t (+6 more)

### Community 73 - "_boi_canh"
Cohesion: 0.20
Nodes (14): _boi_canh(), canh_bao_lach_luat(), doc_plan(), duong_ban_do(), lenh_cum(), lenh_phan_cong(), _ly_do_hoan(), The user picked team mode but the leader types code of a task it promised away → (+6 more)

### Community 74 - "chia_dot"
Cohesion: 0.14
Nodes (14): chia_dot(), _chia_dot_theo_phase(), _chia_dot_theo_phu_thuoc(), doc_phu_thuoc(), _dot_som_nhat(), _khoa_phase(), _la_file_luat(), quyet_dinh_task() (+6 more)

### Community 75 - "scripts/luat_phan_loai.py"
Cohesion: 0.19
Nodes (13): bang_nhap(), doc_bang(), doc_ranh_gioi(), goi_y_nhan(), liet_ke_ma(), _log(), main(), The suggested label for one anchor, with its reason.      The order runs from th (+5 more)

### Community 76 - "cross_check_diagram"
Cohesion: 0.14
Nodes (14): code_node_pairs(), comment_mask(), cross_check_diagram(), diagram_step_locations(), extract_depends(), filter_code_nodes(), node_function_name(), True for every line that sits inside (or opens) an HTML comment block. (+6 more)

### Community 77 - "_boi_canh"
Cohesion: 0.20
Nodes (14): _boi_canh(), canh_bao_lach_luat(), doc_plan(), duong_ban_do(), lenh_cum(), lenh_phan_cong(), _ly_do_hoan(), The user picked team mode but the leader types code of a task it promised away → (+6 more)

### Community 78 - "chia_dot"
Cohesion: 0.14
Nodes (14): chia_dot(), _chia_dot_theo_phase(), _chia_dot_theo_phu_thuoc(), doc_phu_thuoc(), _dot_som_nhat(), _khoa_phase(), _la_file_luat(), quyet_dinh_task() (+6 more)

### Community 79 - "check_diagram"
Cohesion: 0.19
Nodes (12): _check_branch(), _check_depends(), check_diagram(), _check_steps(), _check_title(), One broken rule, at one 1-based line. `str()` renders the report line., The first content line must be the title; anything else loses the feature name., Exactly one branch line: none leaves the feature unplaced, two place it twice. (+4 more)

### Community 80 - "antigravity_portable/scripts/i18n_check.py"
Cohesion: 0.24
Nodes (11): allowed_fence_lines(), collect(), _log(), main(), python_line_kinds(), Return one finding dict per Vietnamese line of a single file., Log service: one ISO-timestamp line on stderr. Off with TDQ_LOG=0.      On stder, Expand files and directories into a sorted list of files to scan. (+3 more)

### Community 81 - "diagram_entries"
Cohesion: 0.20
Nodes (12): _chan_so_do_chua_duyet(), diagram_entries(), _diagram_id(), diagram_pending(), _diagram_register(), _heal_diagrams(), Put `path` into the diagram list and return its element. Never duplicates., Gate `plan`: the diagram list must be non-empty and fully approved.      Phase ` (+4 more)

### Community 82 - "scripts/i18n_check.py"
Cohesion: 0.24
Nodes (11): allowed_fence_lines(), collect(), _log(), main(), python_line_kinds(), Return one finding dict per Vietnamese line of a single file., Log service: one ISO-timestamp line on stderr. Off with TDQ_LOG=0.      On stder, Expand files and directories into a sorted list of files to scan. (+3 more)

### Community 83 - "main"
Cohesion: 0.17
Nodes (12): build_parser(), collect_total_data(), default_output_path(), default_total_output_path(), load_graph(), main(), `<root>/docs/tdq/mind-map/index.html` — the aggregate page's fixed name., `<root>/docs/tdq/mind-map/<slug>.html` from `<anything>/<slug>.md`. (+4 more)

### Community 84 - "lenh_bao_cao"
Cohesion: 0.17
Nodes (12): bao_cao_so(), doc_ban_ghi(), don_vi_kiem(), _in_bang(), kiem_dinh_dau(), lenh_bao_cao(), Build the whole audit file out of the table. No hand-typed number gets in., Read every scored session record. No record at all → return an empty list. (+4 more)

### Community 85 - "chay_va_cham"
Cohesion: 0.18
Nodes (11): chay_va_cham(), dau_nhiem(), dau_nhiem_phien(), _ghi_ban_ghi(), _noi_dung(), phan_tich(), The content of a tool_result may be a string or a list of text blocks., Normalise a stream-json transcript into what the scorer reads.      Returns: the (+3 more)

### Community 86 - "antigravity_portable/hooks/scripts/agy_pretooluse_gate.py"
Cohesion: 0.33
Nodes (9): _branch_names(), _clean(), _deny(), _first_command(), _log(), main(), The shell command text off the payload, or "" when no known shape carries one., One timestamped stderr line naming the matched case. Off with TDQ_LOG=0.      De (+1 more)

### Community 87 - "hooks/scripts/agy_pretooluse_gate.py"
Cohesion: 0.33
Nodes (9): _branch_names(), _clean(), _deny(), _first_command(), _log(), main(), The shell command text off the payload, or "" when no known shape carries one., One timestamped stderr line naming the matched case. Off with TDQ_LOG=0.      De (+1 more)

### Community 88 - "manifest.json"
Cohesion: 0.22
Nodes (8): external_commands, mcp_servers, python_min, version, git, graphify, tavily-backup, tavily-primary

### Community 89 - "tdq-workflow — Plugin Claude Code"
Cohesion: 0.22
Nodes (8): Cài đặt (chỉ trong repo/project), Cách hook điều khiển agent, Cấu trúc, Duyệt bằng chat thường, Dùng hằng ngày, Pipeline, Quy ước cứng, tdq-workflow — Plugin Claude Code

### Community 90 - "_chuyen_tick"
Cohesion: 0.22
Nodes (9): _chuyen_tick(), kiem_L003(), kiem_L013(), kiem_L145(), The sequence (call index, task code, new mark) pulled from every write to the pl, Tick `[~]` first, `[x]` after, and never bulk-tick several tasks at once., Flip `[~]` to `[x]` AT ONCE: at no moment do two tasks carry `[~]`., Every task has its own test: between its `[~]` and `[x]` there must be a test ru (+1 more)

### Community 91 - "quet"
Cohesion: 0.36
Nodes (7): khoi_mau(), la_ky_hieu(), main(), quet(), True when ch is non-ASCII punctuation/symbol — what the whitelist has to govern., The content of the ``` blocks in a file — this is what is REALLY printed to the, {character: (total count, {file: count})} for every non-ASCII symbol.

### Community 92 - "dod_tick_state"
Cohesion: 0.25
Nodes (8): _dod_section(), dod_tick_state(), _plan_path(), Absolute path of the plan of the active request, or None when there is none., Every line under a DoD heading, up to the next `## ` heading.      Three details, Checkbox state of the plan's Definition of Done section. Never raises., How many task boxes of the current plan are not `[x]` yet. Never raises.      A, task_open_count()

### Community 93 - "render_total_page"
Cohesion: 0.25
Nodes (8): build_branch_model(), The same edges as the SVG, spelled out as text — every reason legible     withou, Top branch -> sub branch -> feature, general down to the business page —     nes, Turn the `{slug: info}` map of collect_total_data into a 3-tier tree.      Retur, Build the self-contained aggregate HTML page: branch tree + dependency grid., _render_branch_tree(), _render_edge_list(), render_total_page()

### Community 94 - "quet"
Cohesion: 0.36
Nodes (7): khoi_mau(), la_ky_hieu(), main(), quet(), True when ch is non-ASCII punctuation/symbol — what the whitelist has to govern., The content of the ``` blocks in a file — this is what is REALLY printed to the, {character: (total count, {file: count})} for every non-ASCII symbol.

### Community 95 - "DiagramInvalid"
Cohesion: 0.29
Nodes (5): CallNode, DiagramInvalid, ValueError, One function in a step's call tree: itself, plus its own callees (line, CallNode, The diagram fails check_diagram; carries the violations for the caller to print.

### Community 96 - "TDQ Workflow — portable bundle for Antigravity CLI (agy)"
Cohesion: 0.33
Nodes (5): Install on a new machine — follow this exact order, Known limitation, Secret keys, TDQ Workflow — portable bundle for Antigravity CLI (agy), What this bundle cannot do for you

### Community 97 - "_parse_approve_args"
Cohesion: 0.33
Nodes (6): normalize_lane(), normalize_mode(), _parse_approve_args(), -> (target, mode, by, no_qc, diagram). Fails only on genuinely wrong syntax., Alias -> machine identifier ("quick"/"full"). Unrecognised -> None (the     call, Alias -> machine identifier ("main"/"subagent"). The ONLY entry point for a

### Community 98 - "state_path"
Cohesion: 0.33
Nodes (6): find_shadow_states(), State project root: TDQ_PROJECT_DIR > git root > a dir holding state > cwd., Misplaced state/mirror: state.json outside root, or an orphan STATE.md (S6)., resolve_project_dir(), state_md_path(), state_path()

### Community 100 - "Lưới hồi quy: đo độ tuân thủ luật TDQ"
Cohesion: 0.40
Nodes (4): Bộ ca, Chạy lại — một lệnh, Lưới hồi quy: đo độ tuân thủ luật TDQ, Đọc kết quả

### Community 102 - "bien_moi_truong_mcp"
Cohesion: 0.50
Nodes (4): bien_moi_truong_mcp(), Turn an env dict into lines safe to print: only the KEY name + set/unset, no val, State of the key variables the manifest MCP needs — variable NAMES, no values., to_ten_khoa()

### Community 103 - "_sinh_settings"
Cohesion: 0.50
Nodes (4): `hooks.json` (shipped with the bundle) → the `.claude/settings.json` of the targ, sinh_settings(), `hooks/hooks.json` + the repo `env` block → `.claude/settings.json` of the targe, _sinh_settings()

### Community 104 - "cross_check_diagram"
Cohesion: 0.14
Nodes (14): code_node_pairs(), comment_mask(), cross_check_diagram(), diagram_step_locations(), extract_depends(), filter_code_nodes(), node_function_name(), True for every line that sits inside (or opens) an HTML comment block. (+6 more)

### Community 105 - "_file_changed_since_approval"
Cohesion: 0.50
Nodes (4): _file_changed_since_approval(), True when the spec/plan file changed since it was approved. It tells     'a redu, Hash the CONTENT part of a spec/plan: from the first `##` heading onward.      W, sha256_noi_dung()

### Community 106 - "iter_events"
Cohesion: 0.50
Nodes (4): hanh_vi_read(), iter_events(), Yield the jsonl records one by one. A broken/empty line is skipped without spoil, Measure `Read` behaviour: how many calls, how many carry `offset`/`limit`, how m

### Community 109 - "chay_bo"
Cohesion: 0.50
Nodes (4): chay_bo(), Work still to run, interleaved between branches on every run.      Interleaved s, Run the whole round. Returns (total cost, whether it stopped early on the cap)., viec_con_lai()

### Community 110 - "_duong_dan_ghi_bash"
Cohesion: 0.50
Nodes (4): _duong_dan_ghi_bash(), _duong_dan_sed(), The file `sed -i` overwrites. Split with shlex because a sed expression often us, The paths one Bash command WRITES to. Reading a file does not count, only writin

### Community 111 - "sha256_noi_dung"
Cohesion: 0.50
Nodes (4): _file_changed_since_approval(), True when the spec/plan file changed since it was approved. It tells     'a redu, Hash the CONTENT part of a spec/plan: from the first `##` heading onward.      W, sha256_noi_dung()

### Community 112 - "_parse_approve_args"
Cohesion: 0.50
Nodes (4): normalize_lane(), _parse_approve_args(), -> (target, mode, by, no_qc, diagram). Fails only on genuinely wrong syntax., Alias -> machine identifier ("quick"/"full"). Unrecognised -> None (the     call

### Community 113 - "iter_events"
Cohesion: 0.50
Nodes (4): hanh_vi_read(), iter_events(), Yield the jsonl records one by one. A broken/empty line is skipped without spoil, Measure `Read` behaviour: how many calls, how many carry `offset`/`limit`, how m

### Community 114 - "mode_label"
Cohesion: 0.67
Nodes (3): approve_hint(), mode_label(), The label PRINTED to a reader, same rule as lane_label: an unknown mode comes

### Community 119 - "_report"
Cohesion: 0.18
Nodes (12): Yield (normalised title, first line index, last line index) for every heading., Steps in the 'steps' section must run 1, 2, 3… with no jump and no repeat., A command must be copy-pasteable: inside a ``` block, inline code, or a table ce, A vague word in a step/rule section — unless the next 3 lines pin it down with a, [(line index, cells)] of the §3b table; None when the spec has no 3b section., A file under `spec/` must carry a valid §3b table (the capability inventory)., _report(), rule_r1() (+4 more)

### Community 120 - "render_feature_page"
Cohesion: 0.18
Nodes (9): build_flow_model(), DiagramInvalid, ValueError, Turn the FLAT step list of parse_diagram into `{"nodes", "edges"}`.      parse_d, Build the full two-layer HTML page for one feature. Pure: no file I/O.      Rais, The diagram fails check_diagram; carries the violations for the caller to print., _render_business_layer(), render_feature_page() (+1 more)

### Community 121 - "lint_file"
Cohesion: 0.22
Nodes (9): _lane_cua_spec(), lint_file(), Returns 'full' | 'quick' | None. None means the spec declares no lane., A lane-full spec needs `## 2b. Ranh giới module` — the plan cuts tasks along it., True when the spec file name starts with a date earlier than the rule landing da, A spec states the PASS CONDITION only; the concrete check command belongs to the, rule_r10(), rule_r11() (+1 more)

### Community 122 - "rule_r12"
Cohesion: 0.33
Nodes (6): _doc_lang(), _r12_van_xuoi(), None = does not qualify as prose (breaks the run). True/False = carries Vietname, The `doc_lang` of the request owning this file, or the default when there is no, A long prose paragraph in the wrong language → reported once, on its first line., rule_r12()

### Community 123 - "Doc"
Cohesion: 0.40
Nodes (3): Doc, One markdown file, pre-split: lines, fenced regions, headings., Does the line right above carry `<!-- doc-lint: allow Rn -->` for this very rule

## Knowledge Gaps
- **141 isolated node(s):** `0.35.0 — 2026-08-27`, `0.34.0 — 2026-08-26`, `0.33.0 — 2026-08-24`, `0.32.0 — 2026-08-23`, `0.31.0 — 2026-08-23` (+136 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `load()` connect `cli` to `state_path`, `main`, `antigravity_portable/scripts/tdq_checkstatus.py`, `main`, `scripts/tdq_state.py`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Why does `load()` connect `cli` to `antigravity_portable/scripts/tdq_checkstatus.py`, `diagram_entries`, `antigravity_portable/scripts/tdq_state.py`, `dod_tick_state`, `main`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **What connects `0.35.0 — 2026-08-27`, `0.34.0 — 2026-08-26`, `0.33.0 — 2026-08-24` to the rest of the system?**
  _141 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `files` be split into smaller, more focused modules?**
  _Cohesion score 0.023255813953488372 - nodes in this community are weakly interconnected._
- **Should `antigravity_portable/scripts/canvas_a4_rebuild.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06013986013986014 - nodes in this community are weakly interconnected._
- **Should `scripts/canvas_a4_rebuild.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06293706293706294 - nodes in this community are weakly interconnected._
- **Should `scripts/skill_tokens.py` be split into smaller, more focused modules?**
  _Cohesion score 0.053005464480874315 - nodes in this community are weakly interconnected._