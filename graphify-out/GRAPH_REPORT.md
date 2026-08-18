# Graph Report - TDQWorkflow  (2026-08-18)

## Corpus Check
- 37 files · ~60,531 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 823 nodes · 1571 edges · 30 communities (28 shown, 2 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 78 edges (avg confidence: 0.66)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b3501cfa`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- build_portable.py
- tdq_team.py
- canvas_a4_rebuild.py
- token_audit.py
- doc_lint.py
- tdq_checkstatus.py
- claude_export.py
- tdq_bench.py
- skill_tokens.py
- _common.py
- Changelog
- main
- tdq_finish.py
- tdq_state.py
- check_canvas_layout.py
- tdq_timing.py
- skill_router.py
- cli
- context_surface.py
- skill_inventory.py
- plugin_tiers.py
- main
- effective_lane
- main
- tdq-workflow — Plugin Claude Code
- quet
- _parse_approve_args
- Exception
- Exception
- tdq_checkportable.py

## God Nodes (most connected - your core abstractions)
1. `Changelog` - 28 edges
2. `cli()` - 21 edges
3. `log()` - 17 edges
4. `cmd_build()` - 17 edges
5. `main()` - 15 edges
6. `_warn()` - 14 edges
7. `load()` - 14 edges
8. `_cli_approve()` - 14 edges
9. `_log()` - 14 edges
10. `LoiThieuSo` - 13 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `cong_dang_cho()`  [INFERRED]
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

## Communities (30 total, 2 thin omitted)

### Community 0 - "build_portable.py"
Cohesion: 0.10
Nodes (36): _bo_qua_file(), _bo_qua_thu_muc(), copy_loc(), dem_bien_trong_cay(), doc_frontmatter(), _doc_text(), doi_bien_plugin_root(), _ghi_json() (+28 more)

### Community 1 - "tdq_team.py"
Cohesion: 0.07
Nodes (65): b_level(), _bao_dam_tich_hop(), _boi_canh(), build_parser(), canh_bao_lach_luat(), chia_dot(), _chia_dot_theo_phase(), _chia_dot_theo_phu_thuoc() (+57 more)

### Community 2 - "canvas_a4_rebuild.py"
Cohesion: 0.06
Nodes (47): build_ch4(), build_ch7(), build_all(), build_generic(), build_moved(), build_toc(), Builder, chapter_elements() (+39 more)

### Community 3 - "token_audit.py"
Cohesion: 0.07
Nodes (48): _blocks(), _has_usage(), _log(), _log_enabled(), main(), median(), merge(), _now() (+40 more)

### Community 4 - "doc_lint.py"
Cohesion: 0.07
Nodes (43): collect(), Doc, _lane_cua_spec(), lint_file(), _log(), main(), pair(), _plan_contracts() (+35 more)

### Community 5 - "tdq_checkstatus.py"
Cohesion: 0.08
Nodes (45): bao_cao_markdown(), _ca(), cham_ca_lech(), _cham_d2(), _cham_d3(), _cham_d5(), _cham_d6(), _cham_d7() (+37 more)

### Community 6 - "claude_export.py"
Cohesion: 0.09
Nodes (44): cli_versions(), clone_repo(), cmd_build(), cmd_check(), collect_config_files(), copy_config(), copy_launch_agents(), copy_repo_memory() (+36 more)

### Community 7 - "tdq_bench.py"
Cohesion: 0.09
Nodes (42): _agent_stub(), build_parser(), dem_cap_chong(), _do_mot_luot(), _do_tick(), _doc_mau_that(), _dung_repo_tam(), _git() (+34 more)

### Community 8 - "skill_tokens.py"
Cohesion: 0.10
Nodes (34): Exception, ban_do_skill_md(), _chu(), do_mo_ta(), do_theo_phase(), _in_bang(), khoa_tra(), lenh_mo_ta() (+26 more)

### Community 9 - "_common.py"
Cohesion: 0.12
Nodes (32): _check_signal_mismatch(), _clean(), _latest_signal(), main(), Dòng kind="signal" GẦN NHẤT khớp target (duyệt ngược sổ turn)., already_reminded(), approve_hint(), block() (+24 more)

### Community 10 - "Changelog"
Cohesion: 0.07
Nodes (28): 0.11.10 — 2026-08-13, 0.11.11 — 2026-08-13, 0.11.12 — 2026-08-13, 0.11.13 — 2026-08-13, 0.11.4 trở về 0.7.0, 0.11.5 — 2026-08-13, 0.11.6 — 2026-08-13, 0.11.7 — 2026-08-13 (+20 more)

### Community 11 - "main"
Cohesion: 0.12
Nodes (25): _log_changed(), main(), Ảnh chụp đầu turn — lấy dòng MỚI NHẤT.      Bình thường mỗi turn chỉ có một dòng, Log hôm nay có đổi so với đầu turn không (bất kể ghi bằng cách nào)., Tên file để nêu trong lời chặn — ưu tiên file mới xuất hiện trong turn.      Chu, _repo_changed(), _sha(), _shell_changed_path() (+17 more)

### Community 12 - "tdq_finish.py"
Cohesion: 0.15
Nodes (22): _changed_files(), _log(), _log_enabled(), main(), _now(), parse_args(), _project_dir(), Về `idle` = hết request → chốt sổ thời gian vào docs/tdq/timing.jsonl.      Chạy (+14 more)

### Community 13 - "tdq_state.py"
Cohesion: 0.11
Nodes (23): _atomic_write(), lane_label(), parse_slug(), _parse_value(), plugin_root_cmd(), _pop_json_flag(), prompt_context_last(), prompt_context_path() (+15 more)

### Community 14 - "check_canvas_layout.py"
Cohesion: 0.16
Nodes (21): bbox(), boxes_overlap(), center(), check_chapters(), check_contain(), check_fontsize(), check_order(), check_overlap() (+13 more)

### Community 15 - "tdq_timing.py"
Cohesion: 0.14
Nodes (22): bang_markdown(), cua_so_phase(), da_dong_so(), dinh_dang(), dong_ho_ngan(), dong_so(), _giay_model(), _log() (+14 more)

### Community 16 - "skill_router.py"
Cohesion: 0.17
Nodes (16): bo_dau(), doc_kho(), dung_kho(), ghi_kho(), KhoBM25, lenh_dung_kho(), lenh_tra(), _log() (+8 more)

### Community 17 - "cli"
Cohesion: 0.18
Nodes (21): cli(), _cli_approve(), default_state(), _dong_so_request_cu(), _echo_state(), ghi_moc_phase(), _info(), load() (+13 more)

### Community 18 - "context_surface.py"
Cohesion: 0.18
Nodes (19): _log(), _log_enabled(), main(), measure_hooks(), _num(), _payload(), print_table(), Quét toàn bộ bề mặt tài liệu, trả về danh sách dòng bảng. (+11 more)

### Community 19 - "skill_inventory.py"
Cohesion: 0.15
Nodes (19): _clean(), _condense(), _enabled_plugins(), _filter(), _frontmatter(), inventory(), _load_json(), main() (+11 more)

### Community 20 - "plugin_tiers.py"
Cohesion: 0.34
Nodes (16): _claude_dir(), cmd_enable(), cmd_reset(), cmd_status(), _key_for(), _load_json(), _log(), _log_on() (+8 more)

### Community 21 - "main"
Cohesion: 0.17
Nodes (15): _compact(), _emit(), looks_like_approval(), main(), mode_from_answer(), Turn trước đã in y hệt nội dung này — thay bằng dòng ngắn cùng mã., critical=True: cảnh báo/hành động riêng cho turn này (duyệt mơ hồ, mode     lệch, Câu trả lời ở cổng mode -> định danh máy, hoặc None nếu không đọc ra được. (+7 more)

### Community 22 - "effective_lane"
Cohesion: 0.20
Nodes (15): cong_dang_cho(), effective_lane(), effective_mode(), effective_phase(), next_headline(), phase_key(), phase_row(), Mirror markdown ≤30 dòng cho agent/user đọc thẳng (spec §2.3.1). (+7 more)

### Community 23 - "main"
Cohesion: 0.28
Nodes (8): main(), within(), find_shadow_states(), Project root cho state: TDQ_PROJECT_DIR > git root > thư mục đã có state > cwd., State/mirror lạc chỗ: state.json ngoài root, hoặc STATE.md mồ côi (S6)., resolve_project_dir(), state_md_path(), state_path()

### Community 24 - "tdq-workflow — Plugin Claude Code"
Cohesion: 0.22
Nodes (8): Cài đặt (chỉ trong repo/project), Cách hook điều khiển agent, Cấu trúc, Duyệt bằng chat thường, Dùng hằng ngày, Pipeline, Quy ước cứng, tdq-workflow — Plugin Claude Code

### Community 25 - "quet"
Cohesion: 0.36
Nodes (7): khoi_mau(), la_ky_hieu(), main(), quet(), True khi ch là dấu câu/ký hiệu ngoài ASCII — thứ whitelist phải quản., Nội dung các khối ``` trong file — đây mới là phần THẬT SỰ in ra cho user., {ký tự: (tổng số lần, {file: số lần})} cho mọi ký hiệu ngoài ASCII.

### Community 26 - "_parse_approve_args"
Cohesion: 0.33
Nodes (6): _fail(), normalize_lane(), _parse_approve_args(), -> (target, mode, by, no_qc). Chỉ lỗi khi cú pháp thật sự sai., Chỉ dùng cho SAI CÚ PHÁP LỆNH — exit 2 (spec §2.9.4)., Bí danh -> định danh máy ("quick"/"full"). Không nhận ra -> None (người gọi

### Community 29 - "tdq_checkportable.py"
Cohesion: 0.11
Nodes (33): bat_trusted(), bien_moi_truong_mcp(), chay_setup(), da_trusted(), _doc(), doc_manifest(), duong_config_codex(), ghi_de_co_backup() (+25 more)

## Knowledge Gaps
- **34 isolated node(s):** `0.26.0 — 2026-08-18`, `0.25.0 — 2026-08-18`, `0.24.0 — 2026-08-17`, `0.23.0 — 2026-08-17`, `0.22.0 — 2026-08-16` (+29 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `turn_log_append()` connect `_common.py` to `cli`, `tdq_state.py`, `main`?**
  _High betweenness centrality (0.007) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `main()` (e.g. with `effective_lane()` and `effective_mode()`) actually correct?**
  _`main()` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `0.26.0 — 2026-08-18`, `0.25.0 — 2026-08-18`, `0.24.0 — 2026-08-17` to the rest of the system?**
  _34 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `build_portable.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1021021021021021 - nodes in this community are weakly interconnected._
- **Should `tdq_team.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06606990622335891 - nodes in this community are weakly interconnected._
- **Should `canvas_a4_rebuild.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06293706293706294 - nodes in this community are weakly interconnected._
- **Should `token_audit.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07183673469387755 - nodes in this community are weakly interconnected._