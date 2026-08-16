# Graph Report - TDQWorkflow  (2026-08-16)

## Corpus Check
- 32 files · ~40,732 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 573 nodes · 1103 edges · 23 communities
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 58 edges (avg confidence: 0.7)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1d18bc6f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- _common.py
- canvas_a4_rebuild.py
- token_audit.py
- tdq_checkstatus.py
- claude_export.py
- doc_lint.py
- tdq_finish.py
- Changelog
- check_canvas_layout.py
- tdq_timing.py
- context_surface.py
- skill_inventory.py
- tdq_state.py
- cli
- plugin_tiers.py
- code_rule_scan.py
- _cli_approve
- Chapter
- prompt_context.py
- main
- tdq-workflow — Plugin Claude Code
- quet
- _parse_approve_args

## God Nodes (most connected - your core abstractions)
1. `Changelog` - 23 edges
2. `cli()` - 21 edges
3. `main()` - 20 edges
4. `log()` - 17 edges
5. `cmd_build()` - 17 edges
6. `main()` - 16 edges
7. `_cli_approve()` - 14 edges
8. `payload_cwd()` - 13 edges
9. `_warn()` - 13 edges
10. `load()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `payload_cwd()` --calls--> `resolve_project_dir()`  [INFERRED]
  hooks/scripts/_common.py → scripts/tdq_state.py
- `observe()` --calls--> `turn_log_append()`  [INFERRED]
  hooks/scripts/_common.py → scripts/tdq_state.py
- `turn_rows()` --calls--> `turn_log_read()`  [INFERRED]
  hooks/scripts/_common.py → scripts/tdq_state.py
- `remind()` --calls--> `turn_log_append()`  [INFERRED]
  hooks/scripts/_common.py → scripts/tdq_state.py
- `block()` --calls--> `turn_log_append()`  [INFERRED]
  hooks/scripts/_common.py → scripts/tdq_state.py

## Import Cycles
- None detected.

## Communities (23 total, 0 thin omitted)

### Community 0 - "_common.py"
Cohesion: 0.12
Nodes (37): _check_signal_mismatch(), _clean(), _latest_signal(), main(), Dòng kind="signal" GẦN NHẤT khớp target (duyệt ngược sổ turn)., already_reminded(), block(), echo_line() (+29 more)

### Community 1 - "canvas_a4_rebuild.py"
Cohesion: 0.08
Nodes (43): build_ch4(), build_ch7(), build_all(), build_generic(), build_moved(), build_toc(), Builder, chapter_elements() (+35 more)

### Community 2 - "token_audit.py"
Cohesion: 0.07
Nodes (48): _blocks(), _has_usage(), _log(), _log_enabled(), main(), median(), merge(), _now() (+40 more)

### Community 3 - "tdq_checkstatus.py"
Cohesion: 0.08
Nodes (45): bao_cao_markdown(), _ca(), cham_ca_lech(), _cham_d2(), _cham_d3(), _cham_d5(), _cham_d6(), _cham_d7() (+37 more)

### Community 4 - "claude_export.py"
Cohesion: 0.09
Nodes (44): cli_versions(), clone_repo(), cmd_build(), cmd_check(), collect_config_files(), copy_config(), copy_launch_agents(), copy_repo_memory() (+36 more)

### Community 5 - "doc_lint.py"
Cohesion: 0.08
Nodes (33): collect(), Doc, lint_file(), main(), pair(), _plan_contracts(), _r9_in_scope(), Bước trong mục 'Các bước' phải đánh số 1, 2, 3… không nhảy, không lặp. (+25 more)

### Community 6 - "tdq_finish.py"
Cohesion: 0.15
Nodes (22): _changed_files(), _log(), _log_enabled(), main(), _now(), parse_args(), _project_dir(), Về `idle` = hết request → chốt sổ thời gian vào docs/tdq/timing.jsonl.      Chạy (+14 more)

### Community 7 - "Changelog"
Cohesion: 0.08
Nodes (23): 0.11.10 — 2026-08-13, 0.11.11 — 2026-08-13, 0.11.12 — 2026-08-13, 0.11.13 — 2026-08-13, 0.11.4 trở về 0.7.0, 0.11.5 — 2026-08-13, 0.11.6 — 2026-08-13, 0.11.7 — 2026-08-13 (+15 more)

### Community 8 - "check_canvas_layout.py"
Cohesion: 0.16
Nodes (21): bbox(), boxes_overlap(), center(), check_chapters(), check_contain(), check_fontsize(), check_order(), check_overlap() (+13 more)

### Community 9 - "tdq_timing.py"
Cohesion: 0.14
Nodes (22): bang_markdown(), cua_so_phase(), da_dong_so(), dinh_dang(), dong_ho_ngan(), dong_so(), _giay_model(), _log() (+14 more)

### Community 10 - "context_surface.py"
Cohesion: 0.18
Nodes (19): _log(), _log_enabled(), main(), measure_hooks(), _num(), _payload(), print_table(), Quét toàn bộ bề mặt tài liệu, trả về danh sách dòng bảng. (+11 more)

### Community 11 - "skill_inventory.py"
Cohesion: 0.15
Nodes (19): _clean(), _condense(), _enabled_plugins(), _filter(), _frontmatter(), inventory(), _load_json(), main() (+11 more)

### Community 12 - "tdq_state.py"
Cohesion: 0.09
Nodes (28): _atomic_write(), _echo_state(), lane_label(), parse_slug(), plugin_root_cmd(), _pop_json_flag(), prompt_context_last(), prompt_context_path() (+20 more)

### Community 13 - "cli"
Cohesion: 0.16
Nodes (22): cli(), default_state(), _dong_so_request_cu(), find_shadow_states(), ghi_moc_phase(), _info(), load(), log_enabled() (+14 more)

### Community 14 - "plugin_tiers.py"
Cohesion: 0.34
Nodes (16): _claude_dir(), cmd_enable(), cmd_reset(), cmd_status(), _key_for(), _load_json(), _log(), _log_on() (+8 more)

### Community 15 - "code_rule_scan.py"
Cohesion: 0.27
Nodes (12): chay_linter(), doc_bang_linter(), _git(), gom_file(), in_bang(), log(), main(), quet() (+4 more)

### Community 16 - "_cli_approve"
Cohesion: 0.14
Nodes (19): _cli_approve(), _file_changed_since_approval(), _git(), plan_tick_state(), True khi file spec/plan đã đổi nội dung so với lúc duyệt. Dùng để phân biệt, Ghi nhận việc user đã duyệt. Không phải gate: cảnh báo khi lệch nhưng     VẪN gh, stdout (bytes) của lệnh git, hoặc None khi không chạy được., Gốc repo (porcelain in path theo gốc, không theo cwd). None nếu không phải repo. (+11 more)

### Community 17 - "Chapter"
Cohesion: 0.23
Nodes (4): Chapter, Trả danh sách (x, w) cho `count` thẻ dàn đều hết bề ngang chương., Bố cục MỘT cột: trả danh sách y cho các khối cao `heights` xếp dọc., Gom element của một chương rồi ghi một lượt.

### Community 18 - "prompt_context.py"
Cohesion: 0.20
Nodes (11): approve_hint(), plan_mode(), Mode đã chốt trong plan_file (dòng 'Mode thực thi:'), None nếu chưa ghi., _compact(), _emit(), looks_like_approval(), Turn trước đã in y hệt nội dung này — thay bằng dòng ngắn cùng mã., critical=True: cảnh báo/hành động riêng cho turn này (duyệt mơ hồ, mode     lệch (+3 more)

### Community 19 - "main"
Cohesion: 0.32
Nodes (12): main(), effective_lane(), effective_mode(), effective_phase(), next_headline(), phase_key(), Khoá tra PHASE_TABLE cho state hiện tại., Dòng 1 của `next` — cũng là toàn bộ output của `next --brief`. (+4 more)

### Community 20 - "tdq-workflow — Plugin Claude Code"
Cohesion: 0.22
Nodes (8): Cài đặt (chỉ trong repo/project), Cách hook điều khiển agent, Cấu trúc, Duyệt bằng chat thường, Dùng hằng ngày, Pipeline, Quy ước cứng, tdq-workflow — Plugin Claude Code

### Community 21 - "quet"
Cohesion: 0.36
Nodes (7): khoi_mau(), la_ky_hieu(), main(), quet(), True khi ch là dấu câu/ký hiệu ngoài ASCII — thứ whitelist phải quản., Nội dung các khối ``` trong file — đây mới là phần THẬT SỰ in ra cho user., {ký tự: (tổng số lần, {file: số lần})} cho mọi ký hiệu ngoài ASCII.

### Community 23 - "_parse_approve_args"
Cohesion: 0.20
Nodes (10): mode_from_answer(), Câu trả lời ở cổng mode -> định danh máy, hoặc None nếu không đọc ra được., _fail(), normalize_lane(), normalize_mode(), _parse_approve_args(), -> (target, mode, by, no_qc). Chỉ lỗi khi cú pháp thật sự sai., Chỉ dùng cho SAI CÚ PHÁP LỆNH — exit 2 (spec §2.9.4). (+2 more)

## Knowledge Gaps
- **29 isolated node(s):** `0.21.0 — 2026-08-16`, `0.20.0 — 2026-08-15`, `0.19.0 — 2026-08-15`, `0.18.0 — 2026-08-14`, `0.17.0 — 2026-08-14` (+24 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `turn_log_append()` connect `tdq_state.py` to `_common.py`, `main`, `cli`?**
  _High betweenness centrality (0.007) - this node is a cross-community bridge._
- **Why does `main()` connect `main` to `_common.py`, `tdq_state.py`, `cli`, `_cli_approve`, `prompt_context.py`, `_parse_approve_args`?**
  _High betweenness centrality (0.004) - this node is a cross-community bridge._
- **Why does `payload_cwd()` connect `_common.py` to `prompt_context.py`, `main`, `cli`?**
  _High betweenness centrality (0.004) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `main()` (e.g. with `effective_lane()` and `effective_mode()`) actually correct?**
  _`main()` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `0.21.0 — 2026-08-16`, `0.20.0 — 2026-08-15`, `0.19.0 — 2026-08-15` to the rest of the system?**
  _29 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `_common.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1173054587688734 - nodes in this community are weakly interconnected._
- **Should `canvas_a4_rebuild.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08176100628930817 - nodes in this community are weakly interconnected._