# Graph Report - TDQWorkflow  (2026-09-03)

## Corpus Check
- 98 files · ~148,282 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2255 nodes · 4105 edges · 99 communities (94 shown, 5 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 114 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f3d90baf`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- files
- build_portable.py
- antigravity_portable/scripts/canvas_a4_rebuild.py
- scripts/canvas_a4_rebuild.py
- _common.py
- antigravity_portable/scripts/doc_lint.py
- scripts/doc_lint.py
- antigravity_portable/scripts/tdq_lsp.py
- scripts/tdq_lsp.py
- antigravity_portable/scripts/tdq_checkstatus.py
- scripts/tdq_checkstatus.py
- antigravity_portable/scripts/claude_export.py
- antigravity_portable/scripts/tdq_bench.py
- scripts/claude_export.py
- scripts/tdq_bench.py
- antigravity_portable/scripts/skill_tokens.py
- scripts/skill_tokens.py
- antigravity_portable/scripts/tdq_checkportable.py
- antigravity_portable/scripts/tdq_worktree_registry.py
- scripts/tdq_worktree_registry.py
- antigravity_portable/scripts/tdq_state.py
- lenh_soat
- lenh_soat
- scripts/tdq_state.py
- main
- cli
- antigravity_portable/scripts/token_audit.py
- scripts/token_audit.py
- antigravity_portable/scripts/tdq_timing.py
- antigravity_portable/scripts/tdq_finish.py
- scripts/tdq_timing.py
- scripts/tdq_finish.py
- cli
- antigravity_portable/scripts/doc_dup.py
- scripts/doc_dup.py
- antigravity_portable/scripts/check_canvas_layout.py
- scripts/check_canvas_layout.py
- _bash
- Changelog
- antigravity_portable/scripts/skill_router.py
- antigravity_portable/scripts/step_audit.py
- scripts/skill_router.py
- scripts/step_audit.py
- tdq_eval.py
- antigravity_portable/scripts/context_surface.py
- antigravity_portable/scripts/skill_inventory.py
- scripts/context_surface.py
- scripts/skill_inventory.py
- Changelog — bản lưu trữ
- LoiThieuSo
- log
- antigravity_portable/scripts/tdq_team.py
- scripts/tdq_team.py
- render_state_md
- antigravity_portable/scripts/plugin_tiers.py
- _log
- scripts/plugin_tiers.py
- _log
- _fail
- hooks/scripts/agy_stop_gate.py
- _fail
- turn_snapshot
- main
- render_state_md
- main
- antigravity_portable/scripts/luat_phan_loai.py
- _boi_canh
- chia_dot
- scripts/luat_phan_loai.py
- _boi_canh
- chia_dot
- antigravity_portable/scripts/i18n_check.py
- scripts/i18n_check.py
- lenh_bao_cao
- chay_va_cham
- antigravity_portable/hooks/scripts/agy_pretooluse_gate.py
- hooks/scripts/agy_pretooluse_gate.py
- manifest.json
- tdq-workflow — Plugin Claude Code
- _chuyen_tick
- quet
- dod_tick_state
- quet
- dod_tick_state
- TDQ Workflow — portable bundle for Antigravity CLI (agy)
- find_shadow_states
- find_shadow_states
- Task
- Lưới hồi quy: đo độ tuân thủ luật TDQ
- Task
- _file_changed_since_approval
- iter_events
- bao-loi/seed/src/tien_ich.py
- _chung/seed/src/tien_ich.py
- chay_bo
- _duong_dan_ghi_bash
- _file_changed_since_approval
- iter_events
- seed/README.md

## God Nodes (most connected - your core abstractions)
1. `files` - 85 edges
2. `cli()` - 26 edges
3. `cli()` - 26 edges
4. `Changelog` - 21 edges
5. `lenh_soat()` - 20 edges
6. `lenh_soat()` - 20 edges
7. `Changelog — bản lưu trữ` - 18 edges
8. `log()` - 17 edges
9. `cmd_build()` - 17 edges
10. `_git()` - 17 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `effective_phase()`  [INFERRED]
  antigravity_portable/hooks/scripts/agy_stop_gate.py → antigravity_portable/scripts/tdq_state.py
- `_continue()` --calls--> `log_enabled()`  [INFERRED]
  antigravity_portable/hooks/scripts/agy_stop_gate.py → antigravity_portable/scripts/tdq_state.py
- `_continue()` --calls--> `now_iso()`  [INFERRED]
  antigravity_portable/hooks/scripts/agy_stop_gate.py → antigravity_portable/scripts/tdq_state.py
- `_sha()` --calls--> `sha256_file()`  [INFERRED]
  antigravity_portable/hooks/scripts/agy_stop_gate.py → antigravity_portable/scripts/tdq_state.py
- `_current_snapshot()` --calls--> `today_log_rel()`  [INFERRED]
  antigravity_portable/hooks/scripts/agy_stop_gate.py → antigravity_portable/scripts/tdq_state.py

## Import Cycles
- None detected.

## Communities (99 total, 5 thin omitted)

### Community 0 - "files"
Cohesion: 0.02
Nodes (85): files, config/hooks.json, config/mcp_config.json, config/settings.json, hooks/scripts/agy_pretooluse_gate.py, hooks/scripts/agy_stop_gate.py, README.md, scripts/canvas_a4_ch4_ch7.py (+77 more)

### Community 1 - "build_portable.py"
Cohesion: 0.05
Nodes (78): _bo_qua_file(), _bo_qua_thu_muc(), copy_loc(), dem_bien_trong_cay(), doc_frontmatter(), _doc_text(), doi_bien_plugin_root(), _ghi_json() (+70 more)

### Community 2 - "antigravity_portable/scripts/canvas_a4_rebuild.py"
Cohesion: 0.06
Nodes (47): build_ch4(), build_ch7(), build_all(), build_generic(), build_moved(), build_toc(), Builder, chapter_elements() (+39 more)

### Community 3 - "scripts/canvas_a4_rebuild.py"
Cohesion: 0.06
Nodes (47): build_ch4(), build_ch7(), build_all(), build_generic(), build_moved(), build_toc(), Builder, chapter_elements() (+39 more)

### Community 4 - "_common.py"
Cohesion: 0.07
Nodes (58): _check_signal_mismatch(), _clean(), _latest_signal(), main(), The LATEST kind="signal" row matching target (walking the turn ledger backwards), already_reminded(), approve_hint(), block() (+50 more)

### Community 5 - "antigravity_portable/scripts/doc_lint.py"
Cohesion: 0.06
Nodes (49): collect(), Doc, _doc_lang(), _lane_cua_spec(), lint_file(), _log(), main(), pair() (+41 more)

### Community 6 - "scripts/doc_lint.py"
Cohesion: 0.06
Nodes (49): collect(), Doc, _doc_lang(), _lane_cua_spec(), lint_file(), _log(), main(), pair() (+41 more)

### Community 7 - "antigravity_portable/scripts/tdq_lsp.py"
Cohesion: 0.08
Nodes (48): Bac, bac1_binary(), bac2_mcp(), bac3_language_server(), bac4_quyen_tool(), bac5_lumen(), bac6_hook_xung_dot(), bac7_cau_hinh_goc_import() (+40 more)

### Community 8 - "scripts/tdq_lsp.py"
Cohesion: 0.08
Nodes (48): Bac, bac1_binary(), bac2_mcp(), bac3_language_server(), bac4_quyen_tool(), bac5_lumen(), bac6_hook_xung_dot(), bac7_cau_hinh_goc_import() (+40 more)

### Community 9 - "antigravity_portable/scripts/tdq_checkstatus.py"
Cohesion: 0.08
Nodes (45): bao_cao_markdown(), _ca(), cham_ca_lech(), _cham_d2(), _cham_d3(), _cham_d5(), _cham_d6(), _cham_d7() (+37 more)

### Community 10 - "scripts/tdq_checkstatus.py"
Cohesion: 0.08
Nodes (45): bao_cao_markdown(), _ca(), cham_ca_lech(), _cham_d2(), _cham_d3(), _cham_d5(), _cham_d6(), _cham_d7() (+37 more)

### Community 11 - "antigravity_portable/scripts/claude_export.py"
Cohesion: 0.09
Nodes (44): cli_versions(), clone_repo(), cmd_build(), cmd_check(), collect_config_files(), copy_config(), copy_launch_agents(), copy_repo_memory() (+36 more)

### Community 12 - "antigravity_portable/scripts/tdq_bench.py"
Cohesion: 0.09
Nodes (43): _agent_stub(), build_parser(), dem_cap_chong(), _do_mot_luot(), _do_tick(), _doc_mau_that(), _dung_repo_tam(), _git() (+35 more)

### Community 13 - "scripts/claude_export.py"
Cohesion: 0.09
Nodes (44): cli_versions(), clone_repo(), cmd_build(), cmd_check(), collect_config_files(), copy_config(), copy_launch_agents(), copy_repo_memory() (+36 more)

### Community 14 - "scripts/tdq_bench.py"
Cohesion: 0.09
Nodes (43): _agent_stub(), build_parser(), dem_cap_chong(), _do_mot_luot(), _do_tick(), _doc_mau_that(), _dung_repo_tam(), _git() (+35 more)

### Community 15 - "antigravity_portable/scripts/skill_tokens.py"
Cohesion: 0.09
Nodes (36): ban_do_skill_md(), _chu(), dem_qua_venv(), do_mo_ta(), do_theo_phase(), _in_bang(), khoa_tra(), lenh_mo_ta() (+28 more)

### Community 16 - "scripts/skill_tokens.py"
Cohesion: 0.09
Nodes (36): ban_do_skill_md(), _chu(), dem_qua_venv(), do_mo_ta(), do_theo_phase(), _in_bang(), khoa_tra(), lenh_mo_ta() (+28 more)

### Community 17 - "antigravity_portable/scripts/tdq_checkportable.py"
Cohesion: 0.10
Nodes (35): bat_trusted(), bien_moi_truong_mcp(), chay_setup(), da_trusted(), _doc(), doc_manifest(), duong_config_codex(), ghi_de_co_backup() (+27 more)

### Community 18 - "antigravity_portable/scripts/tdq_worktree_registry.py"
Cohesion: 0.12
Nodes (30): doc(), _doc_de_ghi(), dong_dong(), dong_mo(), duong_md(), duong_so(), _ghi(), ghi_md() (+22 more)

### Community 19 - "scripts/tdq_worktree_registry.py"
Cohesion: 0.12
Nodes (30): doc(), _doc_de_ghi(), dong_dong(), dong_mo(), duong_md(), duong_so(), _ghi(), ghi_md() (+22 more)

### Community 20 - "antigravity_portable/scripts/tdq_state.py"
Cohesion: 0.09
Nodes (28): _atomic_write(), lane_label(), mode_label(), parse_slug(), plugin_root_cmd(), prompt_context_last(), prompt_context_path(), prompt_context_save() (+20 more)

### Community 21 - "lenh_soat"
Cohesion: 0.11
Nodes (30): _da_merge(), _doc_mb(), _file_ban(), _file_bo_qua_dang_ke(), _git(), _go_thu_muc(), _in_goi_y(), _khoa_khong() (+22 more)

### Community 22 - "lenh_soat"
Cohesion: 0.11
Nodes (30): _da_merge(), _doc_mb(), _file_ban(), _file_bo_qua_dang_ke(), _git(), _go_thu_muc(), _in_goi_y(), _khoa_khong() (+22 more)

### Community 23 - "scripts/tdq_state.py"
Cohesion: 0.08
Nodes (29): _atomic_write(), lane_label(), mode_label(), parse_slug(), _parse_value(), plugin_root_cmd(), prompt_context_last(), prompt_context_path() (+21 more)

### Community 24 - "main"
Cohesion: 0.13
Nodes (27): _current_snapshot(), _cwd_of(), _log_changed(), main(), The path to quote — a path new since the baseline wins over one already known., _read_json(), _repo_changed(), _sha() (+19 more)

### Community 25 - "cli"
Cohesion: 0.14
Nodes (28): _continue(), Force the loop onward, and say on stderr which of the 3 cases matched (TDQ_LOG=0, cli(), _cli_approve(), _cli_implement_pause(), default_state(), _dong_so_request_cu(), _echo_state() (+20 more)

### Community 26 - "antigravity_portable/scripts/token_audit.py"
Cohesion: 0.12
Nodes (25): classify(), _content_text(), dem_anh(), dem_nhieu(), dem_token(), _khoa(), _kich_thuoc_jpeg(), _kich_thuoc_png() (+17 more)

### Community 27 - "scripts/token_audit.py"
Cohesion: 0.12
Nodes (25): classify(), _content_text(), dem_anh(), dem_nhieu(), dem_token(), _khoa(), _kich_thuoc_jpeg(), _kich_thuoc_png() (+17 more)

### Community 28 - "antigravity_portable/scripts/tdq_timing.py"
Cohesion: 0.14
Nodes (24): _has_usage(), _parse_time(), bang_markdown(), cua_so_phase(), da_dong_so(), dinh_dang(), dong_ho_ngan(), dong_so() (+16 more)

### Community 29 - "antigravity_portable/scripts/tdq_finish.py"
Cohesion: 0.15
Nodes (22): _changed_files(), _log(), _log_enabled(), main(), _now(), parse_args(), _project_dir(), Back to `idle` = the request is over → close the timing books into docs/tdq/timi (+14 more)

### Community 30 - "scripts/tdq_timing.py"
Cohesion: 0.14
Nodes (24): _has_usage(), _parse_time(), bang_markdown(), cua_so_phase(), da_dong_so(), dinh_dang(), dong_ho_ngan(), dong_so() (+16 more)

### Community 31 - "scripts/tdq_finish.py"
Cohesion: 0.15
Nodes (22): _changed_files(), _log(), _log_enabled(), main(), _now(), parse_args(), _project_dir(), Back to `idle` = the request is over → close the timing books into docs/tdq/timi (+14 more)

### Community 32 - "cli"
Cohesion: 0.16
Nodes (25): cli(), _cli_approve(), _cli_implement_pause(), default_state(), _dong_so_request_cu(), _echo_state(), ghi_moc_phase(), _info() (+17 more)

### Community 33 - "antigravity_portable/scripts/doc_dup.py"
Cohesion: 0.12
Nodes (23): _bam_shingle(), _cap_tho(), cli(), dem_token_loat(), doc_dong(), _gop_lien_ke(), in_bang(), log() (+15 more)

### Community 34 - "scripts/doc_dup.py"
Cohesion: 0.12
Nodes (23): _bam_shingle(), _cap_tho(), cli(), dem_token_loat(), doc_dong(), _gop_lien_ke(), in_bang(), log() (+15 more)

### Community 35 - "antigravity_portable/scripts/check_canvas_layout.py"
Cohesion: 0.16
Nodes (21): bbox(), boxes_overlap(), center(), check_chapters(), check_contain(), check_fontsize(), check_order(), check_overlap() (+13 more)

### Community 36 - "scripts/check_canvas_layout.py"
Cohesion: 0.16
Nodes (21): bbox(), boxes_overlap(), center(), check_chapters(), check_contain(), check_fontsize(), check_order(), check_overlap() (+13 more)

### Community 37 - "_bash"
Cohesion: 0.10
Nodes (23): _bash(), _ca(), kiem_L002(), kiem_L035(), kiem_L121(), kiem_L136(), kiem_L149(), kiem_L218() (+15 more)

### Community 38 - "Changelog"
Cohesion: 0.09
Nodes (21): 0.19.0 — 2026-08-15, 0.20.0 — 2026-08-15, 0.21.0 — 2026-08-16, 0.22.0 — 2026-08-16, 0.23.0 — 2026-08-17, 0.24.0 — 2026-08-17, 0.25.0 — 2026-08-18, 0.26.0 — 2026-08-18 (+13 more)

### Community 39 - "antigravity_portable/scripts/skill_router.py"
Cohesion: 0.17
Nodes (16): bo_dau(), doc_kho(), dung_kho(), ghi_kho(), KhoBM25, lenh_dung_kho(), lenh_tra(), _log() (+8 more)

### Community 40 - "antigravity_portable/scripts/step_audit.py"
Cohesion: 0.15
Nodes (20): _blocks(), _log(), _log_enabled(), main(), median(), merge(), _now(), percentile() (+12 more)

### Community 41 - "scripts/skill_router.py"
Cohesion: 0.17
Nodes (16): bo_dau(), doc_kho(), dung_kho(), ghi_kho(), KhoBM25, lenh_dung_kho(), lenh_tra(), _log() (+8 more)

### Community 42 - "scripts/step_audit.py"
Cohesion: 0.15
Nodes (20): _blocks(), _log(), _log_enabled(), main(), median(), merge(), _now(), percentile() (+12 more)

### Community 43 - "tdq_eval.py"
Cohesion: 0.13
Nodes (19): build_parser(), _chay_test(), _ghi_ma_nguon(), kiem_L001(), kiem_L005(), kiem_L010(), kiem_L012(), kiem_L209() (+11 more)

### Community 44 - "antigravity_portable/scripts/context_surface.py"
Cohesion: 0.18
Nodes (19): _log(), _log_enabled(), main(), measure_hooks(), _num(), _payload(), print_table(), Scan the whole documentation surface, returning the list of table rows. (+11 more)

### Community 45 - "antigravity_portable/scripts/skill_inventory.py"
Cohesion: 0.15
Nodes (19): _clean(), _condense(), _enabled_plugins(), _filter(), _frontmatter(), inventory(), _load_json(), main() (+11 more)

### Community 46 - "scripts/context_surface.py"
Cohesion: 0.18
Nodes (19): _log(), _log_enabled(), main(), measure_hooks(), _num(), _payload(), print_table(), Scan the whole documentation surface, returning the list of table rows. (+11 more)

### Community 47 - "scripts/skill_inventory.py"
Cohesion: 0.15
Nodes (19): _clean(), _condense(), _enabled_plugins(), _filter(), _frontmatter(), inventory(), _load_json(), main() (+11 more)

### Community 48 - "Changelog — bản lưu trữ"
Cohesion: 0.11
Nodes (18): 0.11.10 — 2026-08-13, 0.11.11 — 2026-08-13, 0.11.12 — 2026-08-13, 0.11.13 — 2026-08-13, 0.11.4 trở về 0.7.0, 0.11.5 — 2026-08-13, 0.11.6 — 2026-08-13, 0.11.7 — 2026-08-13 (+10 more)

### Community 49 - "LoiThieuSo"
Cohesion: 0.16
Nodes (19): cham_lai_tat_ca(), cham_mot_ma(), cham_phien(), doc_bo_ca(), doc_transcript(), lay_token(), lenh_cham(), lenh_chay() (+11 more)

### Community 50 - "log"
Cohesion: 0.13
Nodes (19): chay_phien(), dong_log(), dung_lenh(), dung_moi_truong(), dung_sandbox(), _git(), kiem_dich(), lenh_dung_nhanh() (+11 more)

### Community 51 - "antigravity_portable/scripts/tdq_team.py"
Cohesion: 0.15
Nodes (17): b_level(), build_parser(), _do_xung_dot(), _file_xung_dot(), _kich_thuoc(), lenh_kiem_ke(), _log_enabled(), _loi() (+9 more)

### Community 52 - "scripts/tdq_team.py"
Cohesion: 0.15
Nodes (17): b_level(), build_parser(), _do_xung_dot(), _file_xung_dot(), _kich_thuoc(), lenh_kiem_ke(), _log_enabled(), _loi() (+9 more)

### Community 53 - "render_state_md"
Cohesion: 0.17
Nodes (17): Ported verbatim (pure) from `hooks/scripts/stop_gate.py::unfinished_reason`., unfinished_reason(), cong_dang_cho(), effective_lane(), effective_mode(), effective_phase(), next_headline(), phase_key() (+9 more)

### Community 54 - "antigravity_portable/scripts/plugin_tiers.py"
Cohesion: 0.34
Nodes (16): _claude_dir(), cmd_enable(), cmd_reset(), cmd_status(), _key_for(), _load_json(), _log(), _log_on() (+8 more)

### Community 55 - "_log"
Cohesion: 0.22
Nodes (17): _bao_dam_tich_hop(), _co_nhanh(), _duong_worktree(), _la_repo(), lenh_hop(), lenh_kiem(), lenh_mo(), _log() (+9 more)

### Community 56 - "scripts/plugin_tiers.py"
Cohesion: 0.34
Nodes (16): _claude_dir(), cmd_enable(), cmd_reset(), cmd_status(), _key_for(), _load_json(), _log(), _log_on() (+8 more)

### Community 57 - "_log"
Cohesion: 0.22
Nodes (17): _bao_dam_tich_hop(), _co_nhanh(), _duong_worktree(), _la_repo(), lenh_hop(), lenh_kiem(), lenh_mo(), _log() (+9 more)

### Community 58 - "_fail"
Cohesion: 0.12
Nodes (16): _chan_spec_chua_duyet(), _chan_worktree_con_mo(), _fail(), normalize_doc_lang(), normalize_lane(), normalize_mode(), _parse_approve_args(), _pop_lang_flag() (+8 more)

### Community 59 - "hooks/scripts/agy_stop_gate.py"
Cohesion: 0.23
Nodes (15): _continue(), _current_snapshot(), _cwd_of(), _log_changed(), main(), The path to quote — a path new since the baseline wins over one already known., Ported verbatim (pure) from `hooks/scripts/stop_gate.py::unfinished_reason`., Force the loop onward, and say on stderr which of the 3 cases matched (TDQ_LOG=0 (+7 more)

### Community 60 - "_fail"
Cohesion: 0.12
Nodes (16): _chan_spec_chua_duyet(), _chan_worktree_con_mo(), _fail(), normalize_doc_lang(), normalize_lane(), normalize_mode(), _parse_approve_args(), _pop_lang_flag() (+8 more)

### Community 61 - "turn_snapshot"
Cohesion: 0.17
Nodes (16): _git(), plan_tick_state(), stdout (bytes) of a git command, or None when it cannot run., Repo root (porcelain prints paths from the root, not from cwd). None if not a re, Fingerprint of an untracked file → (mark, bytes read).      CONTENT first: a cha, Fingerprint of the repo working state, or None when it cannot be taken.      Cov, Paths differing from HEAD (status flags dropped, renames keep the target)., Checkbox state of the current plan. Never raises. (+8 more)

### Community 62 - "main"
Cohesion: 0.15
Nodes (15): _all_items(), carry_cost(), cost_equivalent(), _fmt(), main(), phan_ra(), _phan_vi(), The carry-cost table grouped by bucket, descending. `paths` empty → empty table. (+7 more)

### Community 63 - "render_state_md"
Cohesion: 0.20
Nodes (15): cong_dang_cho(), effective_lane(), effective_mode(), effective_phase(), next_headline(), phase_key(), phase_row(), The PHASE_TABLE lookup key for the current state. (+7 more)

### Community 64 - "main"
Cohesion: 0.15
Nodes (15): _all_items(), carry_cost(), cost_equivalent(), _fmt(), main(), phan_ra(), _phan_vi(), The carry-cost table grouped by bucket, descending. `paths` empty → empty table. (+7 more)

### Community 65 - "antigravity_portable/scripts/luat_phan_loai.py"
Cohesion: 0.19
Nodes (13): bang_nhap(), doc_bang(), doc_ranh_gioi(), goi_y_nhan(), liet_ke_ma(), _log(), main(), The suggested label for one anchor, with its reason.      The order runs from th (+5 more)

### Community 66 - "_boi_canh"
Cohesion: 0.20
Nodes (14): _boi_canh(), canh_bao_lach_luat(), doc_plan(), duong_ban_do(), lenh_cum(), lenh_phan_cong(), _ly_do_hoan(), The user picked team mode but the leader types code of a task it promised away → (+6 more)

### Community 67 - "chia_dot"
Cohesion: 0.14
Nodes (14): chia_dot(), _chia_dot_theo_phase(), _chia_dot_theo_phu_thuoc(), doc_phu_thuoc(), _dot_som_nhat(), _khoa_phase(), _la_file_luat(), quyet_dinh_task() (+6 more)

### Community 68 - "scripts/luat_phan_loai.py"
Cohesion: 0.19
Nodes (13): bang_nhap(), doc_bang(), doc_ranh_gioi(), goi_y_nhan(), liet_ke_ma(), _log(), main(), The suggested label for one anchor, with its reason.      The order runs from th (+5 more)

### Community 69 - "_boi_canh"
Cohesion: 0.20
Nodes (14): _boi_canh(), canh_bao_lach_luat(), doc_plan(), duong_ban_do(), lenh_cum(), lenh_phan_cong(), _ly_do_hoan(), The user picked team mode but the leader types code of a task it promised away → (+6 more)

### Community 70 - "chia_dot"
Cohesion: 0.14
Nodes (14): chia_dot(), _chia_dot_theo_phase(), _chia_dot_theo_phu_thuoc(), doc_phu_thuoc(), _dot_som_nhat(), _khoa_phase(), _la_file_luat(), quyet_dinh_task() (+6 more)

### Community 71 - "antigravity_portable/scripts/i18n_check.py"
Cohesion: 0.24
Nodes (11): allowed_fence_lines(), collect(), _log(), main(), python_line_kinds(), Return one finding dict per Vietnamese line of a single file., Log service: one ISO-timestamp line on stderr. Off with TDQ_LOG=0.      On stder, Expand files and directories into a sorted list of files to scan. (+3 more)

### Community 72 - "scripts/i18n_check.py"
Cohesion: 0.24
Nodes (11): allowed_fence_lines(), collect(), _log(), main(), python_line_kinds(), Return one finding dict per Vietnamese line of a single file., Log service: one ISO-timestamp line on stderr. Off with TDQ_LOG=0.      On stder, Expand files and directories into a sorted list of files to scan. (+3 more)

### Community 73 - "lenh_bao_cao"
Cohesion: 0.17
Nodes (12): bao_cao_so(), doc_ban_ghi(), don_vi_kiem(), _in_bang(), kiem_dinh_dau(), lenh_bao_cao(), Build the whole audit file out of the table. No hand-typed number gets in., Read every scored session record. No record at all → return an empty list. (+4 more)

### Community 74 - "chay_va_cham"
Cohesion: 0.18
Nodes (11): chay_va_cham(), dau_nhiem(), dau_nhiem_phien(), _ghi_ban_ghi(), _noi_dung(), phan_tich(), The content of a tool_result may be a string or a list of text blocks., Normalise a stream-json transcript into what the scorer reads.      Returns: the (+3 more)

### Community 75 - "antigravity_portable/hooks/scripts/agy_pretooluse_gate.py"
Cohesion: 0.33
Nodes (9): _branch_names(), _clean(), _deny(), _first_command(), _log(), main(), The shell command text off the payload, or "" when no known shape carries one., One timestamped stderr line naming the matched case. Off with TDQ_LOG=0.      De (+1 more)

### Community 76 - "hooks/scripts/agy_pretooluse_gate.py"
Cohesion: 0.33
Nodes (9): _branch_names(), _clean(), _deny(), _first_command(), _log(), main(), The shell command text off the payload, or "" when no known shape carries one., One timestamped stderr line naming the matched case. Off with TDQ_LOG=0.      De (+1 more)

### Community 77 - "manifest.json"
Cohesion: 0.22
Nodes (8): external_commands, mcp_servers, python_min, version, git, graphify, tavily-backup, tavily-primary

### Community 78 - "tdq-workflow — Plugin Claude Code"
Cohesion: 0.22
Nodes (8): Cài đặt (chỉ trong repo/project), Cách hook điều khiển agent, Cấu trúc, Duyệt bằng chat thường, Dùng hằng ngày, Pipeline, Quy ước cứng, tdq-workflow — Plugin Claude Code

### Community 79 - "_chuyen_tick"
Cohesion: 0.22
Nodes (9): _chuyen_tick(), kiem_L003(), kiem_L013(), kiem_L145(), The sequence (call index, task code, new mark) pulled from every write to the pl, Tick `[~]` first, `[x]` after, and never bulk-tick several tasks at once., Flip `[~]` to `[x]` AT ONCE: at no moment do two tasks carry `[~]`., Every task has its own test: between its `[~]` and `[x]` there must be a test ru (+1 more)

### Community 80 - "quet"
Cohesion: 0.36
Nodes (7): khoi_mau(), la_ky_hieu(), main(), quet(), True when ch is non-ASCII punctuation/symbol — what the whitelist has to govern., The content of the ``` blocks in a file — this is what is REALLY printed to the, {character: (total count, {file: count})} for every non-ASCII symbol.

### Community 81 - "dod_tick_state"
Cohesion: 0.25
Nodes (8): _dod_section(), dod_tick_state(), _plan_path(), Absolute path of the plan of the active request, or None when there is none., Every line under a DoD heading, up to the next `## ` heading.      Three details, Checkbox state of the plan's Definition of Done section. Never raises., How many task boxes of the current plan are not `[x]` yet. Never raises.      A, task_open_count()

### Community 82 - "quet"
Cohesion: 0.36
Nodes (7): khoi_mau(), la_ky_hieu(), main(), quet(), True when ch is non-ASCII punctuation/symbol — what the whitelist has to govern., The content of the ``` blocks in a file — this is what is REALLY printed to the, {character: (total count, {file: count})} for every non-ASCII symbol.

### Community 83 - "dod_tick_state"
Cohesion: 0.25
Nodes (8): _dod_section(), dod_tick_state(), _plan_path(), Absolute path of the plan of the active request, or None when there is none., Every line under a DoD heading, up to the next `## ` heading.      Three details, Checkbox state of the plan's Definition of Done section. Never raises., How many task boxes of the current plan are not `[x]` yet. Never raises.      A, task_open_count()

### Community 84 - "TDQ Workflow — portable bundle for Antigravity CLI (agy)"
Cohesion: 0.33
Nodes (5): Install on a new machine — follow this exact order, Known limitation, Secret keys, TDQ Workflow — portable bundle for Antigravity CLI (agy), What this bundle cannot do for you

### Community 85 - "find_shadow_states"
Cohesion: 0.33
Nodes (6): find_shadow_states(), State project root: TDQ_PROJECT_DIR > git root > a dir holding state > cwd., Misplaced state/mirror: state.json outside root, or an orphan STATE.md (S6)., resolve_project_dir(), state_md_path(), state_path()

### Community 86 - "find_shadow_states"
Cohesion: 0.33
Nodes (6): find_shadow_states(), State project root: TDQ_PROJECT_DIR > git root > a dir holding state > cwd., Misplaced state/mirror: state.json outside root, or an orphan STATE.md (S6)., resolve_project_dir(), state_md_path(), state_path()

### Community 88 - "Lưới hồi quy: đo độ tuân thủ luật TDQ"
Cohesion: 0.40
Nodes (4): Bộ ca, Chạy lại — một lệnh, Lưới hồi quy: đo độ tuân thủ luật TDQ, Đọc kết quả

### Community 90 - "_file_changed_since_approval"
Cohesion: 0.50
Nodes (4): _file_changed_since_approval(), True when the spec/plan file changed since it was approved. It tells     'a redu, Hash the CONTENT part of a spec/plan: from the first `##` heading onward.      W, sha256_noi_dung()

### Community 91 - "iter_events"
Cohesion: 0.50
Nodes (4): hanh_vi_read(), iter_events(), Yield the jsonl records one by one. A broken/empty line is skipped without spoil, Measure `Read` behaviour: how many calls, how many carry `offset`/`limit`, how m

### Community 94 - "chay_bo"
Cohesion: 0.50
Nodes (4): chay_bo(), Work still to run, interleaved between branches on every run.      Interleaved s, Run the whole round. Returns (total cost, whether it stopped early on the cap)., viec_con_lai()

### Community 95 - "_duong_dan_ghi_bash"
Cohesion: 0.50
Nodes (4): _duong_dan_ghi_bash(), _duong_dan_sed(), The file `sed -i` overwrites. Split with shlex because a sed expression often us, The paths one Bash command WRITES to. Reading a file does not count, only writin

### Community 96 - "_file_changed_since_approval"
Cohesion: 0.50
Nodes (4): _file_changed_since_approval(), True when the spec/plan file changed since it was approved. It tells     'a redu, Hash the CONTENT part of a spec/plan: from the first `##` heading onward.      W, sha256_noi_dung()

### Community 97 - "iter_events"
Cohesion: 0.50
Nodes (4): hanh_vi_read(), iter_events(), Yield the jsonl records one by one. A broken/empty line is skipped without spoil, Measure `Read` behaviour: how many calls, how many carry `offset`/`limit`, how m

## Knowledge Gaps
- **142 isolated node(s):** `0.39.0 — 2026-09-03`, `0.38.0 — 2026-09-02`, `0.37.0 — 2026-09-01`, `0.36.0 — 2026-09-01`, `0.35.0 — 2026-08-27` (+137 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `files` connect `files` to `manifest.json`?**
  _High betweenness centrality (0.001) - this node is a cross-community bridge._
- **Why does `sha256_of()` connect `scripts/claude_export.py` to `build_portable.py`?**
  _High betweenness centrality (0.001) - this node is a cross-community bridge._
- **Why does `plugin_version()` connect `scripts/claude_export.py` to `build_portable.py`?**
  _High betweenness centrality (0.001) - this node is a cross-community bridge._
- **What connects `0.39.0 — 2026-09-03`, `0.38.0 — 2026-09-02`, `0.37.0 — 2026-09-01` to the rest of the system?**
  _142 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `files` be split into smaller, more focused modules?**
  _Cohesion score 0.023529411764705882 - nodes in this community are weakly interconnected._
- **Should `build_portable.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05031645569620253 - nodes in this community are weakly interconnected._
- **Should `antigravity_portable/scripts/canvas_a4_rebuild.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06013986013986014 - nodes in this community are weakly interconnected._