# Graph Report - TDQWorkflow  (2026-08-22)

## Corpus Check
- 56 files · ~72,444 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1018 nodes · 1926 edges · 45 communities (41 shown, 4 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 96 edges (avg confidence: 0.62)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c2f490e2`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- tdq_team.py
- token_audit.py
- canvas_a4_rebuild.py
- doc_lint.py
- tdq_checkstatus.py
- claude_export.py
- tdq_bench.py
- skill_tokens.py
- build_portable.py
- step_audit.py
- _common.py
- Changelog
- main
- tdq_state.py
- cli
- tdq_finish.py
- check_canvas_layout.py
- _bash
- LoiThieuSo
- tdq_timing.py
- skill_router.py
- lenh_bao_cao
- context_surface.py
- skill_inventory.py
- log
- effective_lane
- plugin_tiers.py
- main
- luat_phan_loai.py
- tdq_eval.py
- tdq-workflow — Plugin Claude Code
- _chuyen_tick
- quet
- _parse_approve_args
- bao-loi/seed/src/tien_ich.py
- _chung/seed/src/tien_ich.py
- chay_bo
- chay_va_cham
- _duong_dan_ghi_bash
- main
- Exception
- i18n_check.py
- Lưới hồi quy: đo độ tuân thủ luật TDQ
- iter_events
- seed/README.md

## God Nodes (most connected - your core abstractions)
1. `Changelog` - 29 edges
2. `cli()` - 23 edges
3. `main()` - 19 edges
4. `log()` - 17 edges
5. `cmd_build()` - 17 edges
6. `main()` - 16 edges
7. `_cli_approve()` - 14 edges
8. `_log()` - 14 edges
9. `payload_cwd()` - 13 edges
10. `main()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `payload_cwd()` --calls--> `resolve_project_dir()`  [INFERRED]
  hooks/scripts/_common.py → scripts/tdq_state.py
- `turn_rows()` --calls--> `turn_log_read()`  [INFERRED]
  hooks/scripts/_common.py → scripts/tdq_state.py
- `main()` --calls--> `cong_dang_cho()`  [INFERRED]
  hooks/scripts/edit_gate.py → scripts/tdq_state.py
- `main()` --calls--> `effective_phase()`  [INFERRED]
  hooks/scripts/edit_gate.py → scripts/tdq_state.py
- `main()` --calls--> `plan_tick_state()`  [INFERRED]
  hooks/scripts/edit_gate.py → scripts/tdq_state.py

## Import Cycles
- None detected.

## Communities (45 total, 4 thin omitted)

### Community 0 - "tdq_team.py"
Cohesion: 0.06
Nodes (66): b_level(), _bao_dam_tich_hop(), _boi_canh(), build_parser(), canh_bao_lach_luat(), chia_dot(), _chia_dot_theo_phase(), _chia_dot_theo_phu_thuoc() (+58 more)

### Community 1 - "token_audit.py"
Cohesion: 0.12
Nodes (25): classify(), _content_text(), dem_anh(), dem_nhieu(), dem_token(), _khoa(), _kich_thuoc_jpeg(), _kich_thuoc_png() (+17 more)

### Community 2 - "canvas_a4_rebuild.py"
Cohesion: 0.06
Nodes (47): build_ch4(), build_ch7(), build_all(), build_generic(), build_moved(), build_toc(), Builder, chapter_elements() (+39 more)

### Community 3 - "doc_lint.py"
Cohesion: 0.06
Nodes (49): collect(), Doc, _doc_lang(), _lane_cua_spec(), lint_file(), _log(), main(), pair() (+41 more)

### Community 4 - "tdq_checkstatus.py"
Cohesion: 0.08
Nodes (45): bao_cao_markdown(), _ca(), cham_ca_lech(), _cham_d2(), _cham_d3(), _cham_d5(), _cham_d6(), _cham_d7() (+37 more)

### Community 5 - "claude_export.py"
Cohesion: 0.09
Nodes (44): cli_versions(), clone_repo(), cmd_build(), cmd_check(), collect_config_files(), copy_config(), copy_launch_agents(), copy_repo_memory() (+36 more)

### Community 6 - "tdq_bench.py"
Cohesion: 0.09
Nodes (43): _agent_stub(), build_parser(), dem_cap_chong(), _do_mot_luot(), _do_tick(), _doc_mau_that(), _dung_repo_tam(), _git() (+35 more)

### Community 7 - "skill_tokens.py"
Cohesion: 0.09
Nodes (36): ban_do_skill_md(), _chu(), dem_qua_venv(), do_mo_ta(), do_theo_phase(), _in_bang(), khoa_tra(), lenh_mo_ta() (+28 more)

### Community 8 - "build_portable.py"
Cohesion: 0.05
Nodes (69): _bo_qua_file(), _bo_qua_thu_muc(), copy_loc(), dem_bien_trong_cay(), doc_frontmatter(), _doc_text(), doi_bien_plugin_root(), _ghi_json() (+61 more)

### Community 9 - "step_audit.py"
Cohesion: 0.15
Nodes (20): _blocks(), _log(), _log_enabled(), main(), median(), merge(), _now(), percentile() (+12 more)

### Community 10 - "_common.py"
Cohesion: 0.16
Nodes (29): _check_signal_mismatch(), _clean(), _latest_signal(), main(), The LATEST kind="signal" row matching target (walking the turn ledger backwards), already_reminded(), block(), echo_line() (+21 more)

### Community 11 - "Changelog"
Cohesion: 0.07
Nodes (29): 0.11.10 — 2026-08-13, 0.11.11 — 2026-08-13, 0.11.12 — 2026-08-13, 0.11.13 — 2026-08-13, 0.11.4 trở về 0.7.0, 0.11.5 — 2026-08-13, 0.11.6 — 2026-08-13, 0.11.7 — 2026-08-13 (+21 more)

### Community 12 - "main"
Cohesion: 0.12
Nodes (25): _log_changed(), main(), The start-of-turn snapshot — take the NEWEST row.      Normally there is one row, Did today's log change since the start of the turn (however it was written)?, The file name to quote in the block message — a file new in this turn wins., _repo_changed(), _sha(), _shell_changed_path() (+17 more)

### Community 13 - "tdq_state.py"
Cohesion: 0.09
Nodes (27): _atomic_write(), _echo_state(), lane_label(), parse_slug(), _parse_value(), plugin_root_cmd(), _pop_json_flag(), prompt_context_last() (+19 more)

### Community 14 - "cli"
Cohesion: 0.14
Nodes (27): cli(), _cli_approve(), default_state(), _dong_so_request_cu(), _file_changed_since_approval(), find_shadow_states(), ghi_moc_phase(), _info() (+19 more)

### Community 15 - "tdq_finish.py"
Cohesion: 0.15
Nodes (22): _changed_files(), _log(), _log_enabled(), main(), _now(), parse_args(), _project_dir(), Back to `idle` = the request is over → close the timing books into docs/tdq/timi (+14 more)

### Community 16 - "check_canvas_layout.py"
Cohesion: 0.16
Nodes (21): bbox(), boxes_overlap(), center(), check_chapters(), check_contain(), check_fontsize(), check_order(), check_overlap() (+13 more)

### Community 17 - "_bash"
Cohesion: 0.10
Nodes (23): _bash(), _ca(), kiem_L002(), kiem_L035(), kiem_L121(), kiem_L136(), kiem_L149(), kiem_L218() (+15 more)

### Community 18 - "LoiThieuSo"
Cohesion: 0.16
Nodes (19): cham_lai_tat_ca(), cham_mot_ma(), cham_phien(), doc_bo_ca(), doc_transcript(), lay_token(), lenh_cham(), lenh_chay() (+11 more)

### Community 19 - "tdq_timing.py"
Cohesion: 0.14
Nodes (24): _has_usage(), _parse_time(), bang_markdown(), cua_so_phase(), da_dong_so(), dinh_dang(), dong_ho_ngan(), dong_so() (+16 more)

### Community 20 - "skill_router.py"
Cohesion: 0.17
Nodes (16): bo_dau(), doc_kho(), dung_kho(), ghi_kho(), KhoBM25, lenh_dung_kho(), lenh_tra(), _log() (+8 more)

### Community 21 - "lenh_bao_cao"
Cohesion: 0.17
Nodes (12): bao_cao_so(), doc_ban_ghi(), don_vi_kiem(), _in_bang(), kiem_dinh_dau(), lenh_bao_cao(), Build the whole audit file out of the table. No hand-typed number gets in., Read every scored session record. No record at all → return an empty list. (+4 more)

### Community 22 - "context_surface.py"
Cohesion: 0.18
Nodes (19): _log(), _log_enabled(), main(), measure_hooks(), _num(), _payload(), print_table(), Scan the whole documentation surface, returning the list of table rows. (+11 more)

### Community 23 - "skill_inventory.py"
Cohesion: 0.15
Nodes (19): _clean(), _condense(), _enabled_plugins(), _filter(), _frontmatter(), inventory(), _load_json(), main() (+11 more)

### Community 24 - "log"
Cohesion: 0.13
Nodes (19): chay_phien(), dong_log(), dung_lenh(), dung_moi_truong(), dung_sandbox(), _git(), kiem_dich(), lenh_dung_nhanh() (+11 more)

### Community 25 - "effective_lane"
Cohesion: 0.20
Nodes (15): cong_dang_cho(), effective_lane(), effective_mode(), effective_phase(), next_headline(), phase_key(), phase_row(), The PHASE_TABLE row to DISPLAY for the current state.      Unlike `phase_key`, t (+7 more)

### Community 26 - "plugin_tiers.py"
Cohesion: 0.34
Nodes (16): _claude_dir(), cmd_enable(), cmd_reset(), cmd_status(), _key_for(), _load_json(), _log(), _log_on() (+8 more)

### Community 27 - "main"
Cohesion: 0.18
Nodes (16): approve_hint(), plan_mode(), The mode settled in plan_file (its 'Mode thực thi:' line), None when not written, _compact(), _emit(), looks_like_approval(), main(), mode_from_answer() (+8 more)

### Community 28 - "luat_phan_loai.py"
Cohesion: 0.19
Nodes (13): bang_nhap(), doc_bang(), doc_ranh_gioi(), goi_y_nhan(), liet_ke_ma(), _log(), main(), The suggested label for one anchor, with its reason.      The order runs from th (+5 more)

### Community 29 - "tdq_eval.py"
Cohesion: 0.13
Nodes (19): build_parser(), _chay_test(), _ghi_ma_nguon(), kiem_L001(), kiem_L005(), kiem_L010(), kiem_L012(), kiem_L209() (+11 more)

### Community 30 - "tdq-workflow — Plugin Claude Code"
Cohesion: 0.22
Nodes (8): Cài đặt (chỉ trong repo/project), Cách hook điều khiển agent, Cấu trúc, Duyệt bằng chat thường, Dùng hằng ngày, Pipeline, Quy ước cứng, tdq-workflow — Plugin Claude Code

### Community 31 - "_chuyen_tick"
Cohesion: 0.22
Nodes (9): _chuyen_tick(), kiem_L003(), kiem_L013(), kiem_L145(), The sequence (call index, task code, new mark) pulled from every write to the pl, Tick `[~]` first, `[x]` after, and never bulk-tick several tasks at once., Flip `[~]` to `[x]` AT ONCE: at no moment do two tasks carry `[~]`., Every task has its own test: between its `[~]` and `[x]` there must be a test ru (+1 more)

### Community 32 - "quet"
Cohesion: 0.36
Nodes (7): khoi_mau(), la_ky_hieu(), main(), quet(), True when ch is non-ASCII punctuation/symbol — what the whitelist has to govern., The content of the ``` blocks in a file — this is what is REALLY printed to the, {character: (total count, {file: count})} for every non-ASCII symbol.

### Community 33 - "_parse_approve_args"
Cohesion: 0.20
Nodes (10): _fail(), normalize_doc_lang(), normalize_lane(), _parse_approve_args(), _pop_lang_flag(), -> (target, mode, by, no_qc). Fails only on genuinely wrong syntax., Return the normalised language code, or None when it is not a valid code.      A, Strip the `--lang <code>` pair out of the argv of `init`.      Its position is f (+2 more)

### Community 36 - "chay_bo"
Cohesion: 0.50
Nodes (4): chay_bo(), Work still to run, interleaved between branches on every run.      Interleaved s, Run the whole round. Returns (total cost, whether it stopped early on the cap)., viec_con_lai()

### Community 37 - "chay_va_cham"
Cohesion: 0.18
Nodes (11): chay_va_cham(), dau_nhiem(), dau_nhiem_phien(), _ghi_ban_ghi(), _noi_dung(), phan_tich(), The content of a tool_result may be a string or a list of text blocks., Normalise a stream-json transcript into what the scorer reads.      Returns: the (+3 more)

### Community 38 - "_duong_dan_ghi_bash"
Cohesion: 0.50
Nodes (4): _duong_dan_ghi_bash(), _duong_dan_sed(), The file `sed -i` overwrites. Split with shlex because a sed expression often us, The paths one Bash command WRITES to. Reading a file does not count, only writin

### Community 39 - "main"
Cohesion: 0.15
Nodes (15): _all_items(), carry_cost(), cost_equivalent(), _fmt(), main(), phan_ra(), _phan_vi(), The carry-cost table grouped by bucket, descending. `paths` empty → empty table. (+7 more)

### Community 41 - "i18n_check.py"
Cohesion: 0.24
Nodes (11): allowed_fence_lines(), collect(), _log(), main(), python_line_kinds(), Return one finding dict per Vietnamese line of a single file., Log service: one ISO-timestamp line on stderr. Off with TDQ_LOG=0.      On stder, Expand files and directories into a sorted list of files to scan. (+3 more)

### Community 42 - "Lưới hồi quy: đo độ tuân thủ luật TDQ"
Cohesion: 0.40
Nodes (4): Bộ ca, Chạy lại — một lệnh, Lưới hồi quy: đo độ tuân thủ luật TDQ, Đọc kết quả

### Community 43 - "iter_events"
Cohesion: 0.50
Nodes (4): hanh_vi_read(), iter_events(), Yield the jsonl records one by one. A broken/empty line is skipped without spoil, Measure `Read` behaviour: how many calls, how many carry `offset`/`limit`, how m

## Knowledge Gaps
- **39 isolated node(s):** `0.27.0 — 2026-08-22`, `0.26.0 — 2026-08-18`, `0.25.0 — 2026-08-18`, `0.24.0 — 2026-08-17`, `0.23.0 — 2026-08-17` (+34 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `turn_log_append()` connect `_common.py` to `main`, `tdq_state.py`, `cli`?**
  _High betweenness centrality (0.007) - this node is a cross-community bridge._
- **Why does `phase_key()` connect `effective_lane` to `main`, `tdq_state.py`?**
  _High betweenness centrality (0.006) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `main()` (e.g. with `effective_lane()` and `effective_mode()`) actually correct?**
  _`main()` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `0.27.0 — 2026-08-22`, `0.26.0 — 2026-08-18`, `0.25.0 — 2026-08-18` to the rest of the system?**
  _39 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `tdq_team.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06459627329192547 - nodes in this community are weakly interconnected._
- **Should `token_audit.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12 - nodes in this community are weakly interconnected._
- **Should `canvas_a4_rebuild.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06293706293706294 - nodes in this community are weakly interconnected._