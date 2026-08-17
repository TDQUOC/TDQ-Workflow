# Graph Report - TDQWorkflow  (2026-08-17)

## Corpus Check
- 35 files · ~54,910 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 736 nodes · 1433 edges · 26 communities (25 shown, 1 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 72 edges (avg confidence: 0.67)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2b45dc1c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- canvas_a4_rebuild.py
- _common.py
- tdq_team.py
- token_audit.py
- tdq_checkstatus.py
- claude_export.py
- tdq_bench.py
- build_portable.py
- doc_lint.py
- tdq_checkportable.py
- Changelog
- tdq_finish.py
- check_canvas_layout.py
- tdq_timing.py
- context_surface.py
- skill_inventory.py
- tdq_state.py
- cli
- plugin_tiers.py
- effective_lane
- turn_snapshot
- Exception
- tdq-workflow — Plugin Claude Code
- quet
- main
- _parse_approve_args

## God Nodes (most connected - your core abstractions)
1. `Changelog` - 26 edges
2. `cli()` - 21 edges
3. `main()` - 20 edges
4. `log()` - 17 edges
5. `cmd_build()` - 17 edges
6. `_cli_approve()` - 14 edges
7. `_warn()` - 13 edges
8. `load()` - 13 edges
9. `LoiThieuSo` - 13 edges
10. `gom_bang_chung()` - 12 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `effective_lane()`  [INFERRED]
  hooks/scripts/edit_gate.py → scripts/tdq_state.py
- `main()` --calls--> `effective_phase()`  [INFERRED]
  hooks/scripts/edit_gate.py → scripts/tdq_state.py
- `main()` --calls--> `load()`  [INFERRED]
  hooks/scripts/edit_gate.py → scripts/tdq_state.py
- `main()` --calls--> `plan_tick_state()`  [INFERRED]
  hooks/scripts/edit_gate.py → scripts/tdq_state.py
- `main()` --calls--> `today_log_rel()`  [INFERRED]
  hooks/scripts/edit_gate.py → scripts/tdq_state.py

## Import Cycles
- None detected.

## Communities (26 total, 1 thin omitted)

### Community 0 - "canvas_a4_rebuild.py"
Cohesion: 0.06
Nodes (47): build_ch4(), build_ch7(), build_all(), build_generic(), build_moved(), build_toc(), Builder, chapter_elements() (+39 more)

### Community 1 - "_common.py"
Cohesion: 0.07
Nodes (52): _check_signal_mismatch(), _clean(), _latest_signal(), main(), Dòng kind="signal" GẦN NHẤT khớp target (duyệt ngược sổ turn)., already_reminded(), approve_hint(), block() (+44 more)

### Community 2 - "tdq_team.py"
Cohesion: 0.09
Nodes (50): Exception, _bao_dam_tich_hop(), _boi_canh(), build_parser(), canh_bao_lach_luat(), chia_dot(), _co_nhanh(), _do_xung_dot() (+42 more)

### Community 3 - "token_audit.py"
Cohesion: 0.07
Nodes (48): _blocks(), _has_usage(), _log(), _log_enabled(), main(), median(), merge(), _now() (+40 more)

### Community 4 - "tdq_checkstatus.py"
Cohesion: 0.08
Nodes (45): bao_cao_markdown(), _ca(), cham_ca_lech(), _cham_d2(), _cham_d3(), _cham_d5(), _cham_d6(), _cham_d7() (+37 more)

### Community 5 - "claude_export.py"
Cohesion: 0.09
Nodes (44): cli_versions(), clone_repo(), cmd_build(), cmd_check(), collect_config_files(), copy_config(), copy_launch_agents(), copy_repo_memory() (+36 more)

### Community 6 - "tdq_bench.py"
Cohesion: 0.09
Nodes (43): _agent_stub(), build_parser(), dem_cap_chong(), _do_mot_luot(), _do_tick(), _doc_mau_that(), _dung_repo_tam(), _git() (+35 more)

### Community 7 - "build_portable.py"
Cohesion: 0.10
Nodes (38): _bo_qua_file(), _bo_qua_thu_muc(), copy_loc(), dem_bien_trong_cay(), doc_frontmatter(), _doc_text(), doi_bien_plugin_root(), _ghi_json() (+30 more)

### Community 8 - "doc_lint.py"
Cohesion: 0.08
Nodes (33): collect(), Doc, lint_file(), main(), pair(), _plan_contracts(), _r9_in_scope(), Bước trong mục 'Các bước' phải đánh số 1, 2, 3… không nhảy, không lặp. (+25 more)

### Community 9 - "tdq_checkportable.py"
Cohesion: 0.12
Nodes (31): bat_trusted(), bien_moi_truong_mcp(), chay_setup(), da_trusted(), _doc(), doc_manifest(), duong_config_codex(), ghi_de_co_backup() (+23 more)

### Community 10 - "Changelog"
Cohesion: 0.07
Nodes (26): 0.11.10 — 2026-08-13, 0.11.11 — 2026-08-13, 0.11.12 — 2026-08-13, 0.11.13 — 2026-08-13, 0.11.4 trở về 0.7.0, 0.11.5 — 2026-08-13, 0.11.6 — 2026-08-13, 0.11.7 — 2026-08-13 (+18 more)

### Community 11 - "tdq_finish.py"
Cohesion: 0.15
Nodes (22): _changed_files(), _log(), _log_enabled(), main(), _now(), parse_args(), _project_dir(), Về `idle` = hết request → chốt sổ thời gian vào docs/tdq/timing.jsonl.      Chạy (+14 more)

### Community 12 - "check_canvas_layout.py"
Cohesion: 0.16
Nodes (21): bbox(), boxes_overlap(), center(), check_chapters(), check_contain(), check_fontsize(), check_order(), check_overlap() (+13 more)

### Community 13 - "tdq_timing.py"
Cohesion: 0.14
Nodes (22): bang_markdown(), cua_so_phase(), da_dong_so(), dinh_dang(), dong_ho_ngan(), dong_so(), _giay_model(), _log() (+14 more)

### Community 14 - "context_surface.py"
Cohesion: 0.18
Nodes (19): _log(), _log_enabled(), main(), measure_hooks(), _num(), _payload(), print_table(), Quét toàn bộ bề mặt tài liệu, trả về danh sách dòng bảng. (+11 more)

### Community 15 - "skill_inventory.py"
Cohesion: 0.15
Nodes (19): _clean(), _condense(), _enabled_plugins(), _filter(), _frontmatter(), inventory(), _load_json(), main() (+11 more)

### Community 16 - "tdq_state.py"
Cohesion: 0.09
Nodes (27): _atomic_write(), _echo_state(), lane_label(), parse_slug(), _parse_value(), plugin_root_cmd(), _pop_json_flag(), prompt_context_last() (+19 more)

### Community 17 - "cli"
Cohesion: 0.24
Nodes (17): cli(), _cli_approve(), default_state(), _dong_so_request_cu(), ghi_moc_phase(), _info(), load(), log_enabled() (+9 more)

### Community 18 - "plugin_tiers.py"
Cohesion: 0.34
Nodes (16): _claude_dir(), cmd_enable(), cmd_reset(), cmd_status(), _key_for(), _load_json(), _log(), _log_on() (+8 more)

### Community 19 - "effective_lane"
Cohesion: 0.24
Nodes (13): effective_lane(), effective_mode(), effective_phase(), next_headline(), phase_key(), phase_row(), Khoá tra PHASE_TABLE cho state hiện tại., Dòng PHASE_TABLE để HIỂN THỊ cho state hiện tại.      Khác `phase_key`: hàm này (+5 more)

### Community 20 - "turn_snapshot"
Cohesion: 0.14
Nodes (18): _file_changed_since_approval(), _git(), plan_tick_state(), True khi file spec/plan đã đổi nội dung so với lúc duyệt. Dùng để phân biệt, stdout (bytes) của lệnh git, hoặc None khi không chạy được., Gốc repo (porcelain in path theo gốc, không theo cwd). None nếu không phải repo., Dấu nhận dạng file untracked → (dấu, số byte đã đọc).      Ưu tiên NỘI DUNG: mti, Vân tay trạng thái làm việc của repo, hoặc None khi không lấy được.      Gồm cả (+10 more)

### Community 22 - "tdq-workflow — Plugin Claude Code"
Cohesion: 0.22
Nodes (8): Cài đặt (chỉ trong repo/project), Cách hook điều khiển agent, Cấu trúc, Duyệt bằng chat thường, Dùng hằng ngày, Pipeline, Quy ước cứng, tdq-workflow — Plugin Claude Code

### Community 23 - "quet"
Cohesion: 0.36
Nodes (7): khoi_mau(), la_ky_hieu(), main(), quet(), True khi ch là dấu câu/ký hiệu ngoài ASCII — thứ whitelist phải quản., Nội dung các khối ``` trong file — đây mới là phần THẬT SỰ in ra cho user., {ký tự: (tổng số lần, {file: số lần})} cho mọi ký hiệu ngoài ASCII.

### Community 24 - "main"
Cohesion: 0.28
Nodes (8): main(), within(), find_shadow_states(), Project root cho state: TDQ_PROJECT_DIR > git root > thư mục đã có state > cwd., State/mirror lạc chỗ: state.json ngoài root, hoặc STATE.md mồ côi (S6)., resolve_project_dir(), state_md_path(), state_path()

### Community 25 - "_parse_approve_args"
Cohesion: 0.33
Nodes (6): _fail(), normalize_lane(), _parse_approve_args(), -> (target, mode, by, no_qc). Chỉ lỗi khi cú pháp thật sự sai., Chỉ dùng cho SAI CÚ PHÁP LỆNH — exit 2 (spec §2.9.4)., Bí danh -> định danh máy ("quick"/"full"). Không nhận ra -> None (người gọi

## Knowledge Gaps
- **32 isolated node(s):** `0.24.0 — 2026-08-17`, `0.23.0 — 2026-08-17`, `0.22.0 — 2026-08-16`, `0.21.0 — 2026-08-16`, `0.20.0 — 2026-08-15` (+27 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `turn_log_append()` connect `_common.py` to `tdq_state.py`, `cli`?**
  _High betweenness centrality (0.007) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `main()` (e.g. with `effective_lane()` and `effective_mode()`) actually correct?**
  _`main()` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `0.24.0 — 2026-08-17`, `0.23.0 — 2026-08-17`, `0.22.0 — 2026-08-16` to the rest of the system?**
  _32 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `canvas_a4_rebuild.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06293706293706294 - nodes in this community are weakly interconnected._
- **Should `_common.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07456140350877193 - nodes in this community are weakly interconnected._
- **Should `tdq_team.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08944793850454227 - nodes in this community are weakly interconnected._
- **Should `token_audit.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07183673469387755 - nodes in this community are weakly interconnected._