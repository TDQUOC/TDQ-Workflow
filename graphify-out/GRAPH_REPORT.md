# Graph Report - TDQWorkflow  (2026-08-15)

## Corpus Check
- 30 files · ~36,587 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 504 nodes · 976 edges · 16 communities
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 57 edges (avg confidence: 0.7)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `28fbbf20`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- tdq_state.py
- _common.py
- canvas_a4_rebuild.py
- token_audit.py
- claude_export.py
- doc_lint.py
- Changelog
- check_canvas_layout.py
- tdq_finish.py
- context_surface.py
- skill_inventory.py
- plugin_tiers.py
- code_rule_scan.py
- Chapter
- tdq-workflow — Plugin Claude Code
- quet

## God Nodes (most connected - your core abstractions)
1. `Changelog` - 29 edges
2. `main()` - 20 edges
3. `cli()` - 17 edges
4. `log()` - 17 edges
5. `cmd_build()` - 17 edges
6. `main()` - 16 edges
7. `_cli_approve()` - 14 edges
8. `payload_cwd()` - 13 edges
9. `_warn()` - 12 edges
10. `load()` - 12 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `default_state()`  [INFERRED]
  hooks/scripts/session_start.py → scripts/tdq_state.py
- `main()` --calls--> `state_path()`  [INFERRED]
  hooks/scripts/edit_gate.py → scripts/tdq_state.py
- `main()` --calls--> `state_md_path()`  [INFERRED]
  hooks/scripts/edit_gate.py → scripts/tdq_state.py
- `main()` --calls--> `_info()`  [INFERRED]
  hooks/scripts/stop_gate.py → scripts/tdq_state.py
- `payload_cwd()` --calls--> `resolve_project_dir()`  [INFERRED]
  hooks/scripts/_common.py → scripts/tdq_state.py

## Import Cycles
- None detected.

## Communities (16 total, 0 thin omitted)

### Community 0 - "tdq_state.py"
Cohesion: 0.05
Nodes (79): _atomic_write(), cli(), _cli_approve(), default_state(), _echo_state(), effective_lane(), effective_mode(), effective_phase() (+71 more)

### Community 1 - "_common.py"
Cohesion: 0.08
Nodes (54): _check_signal_mismatch(), _clean(), _latest_signal(), main(), Dòng kind="signal" GẦN NHẤT khớp target (duyệt ngược sổ turn)., already_reminded(), approve_hint(), block() (+46 more)

### Community 2 - "canvas_a4_rebuild.py"
Cohesion: 0.08
Nodes (43): build_ch4(), build_ch7(), build_all(), build_generic(), build_moved(), build_toc(), Builder, chapter_elements() (+35 more)

### Community 3 - "token_audit.py"
Cohesion: 0.07
Nodes (48): _blocks(), _has_usage(), _log(), _log_enabled(), main(), median(), merge(), _now() (+40 more)

### Community 4 - "claude_export.py"
Cohesion: 0.09
Nodes (44): cli_versions(), clone_repo(), cmd_build(), cmd_check(), collect_config_files(), copy_config(), copy_launch_agents(), copy_repo_memory() (+36 more)

### Community 5 - "doc_lint.py"
Cohesion: 0.08
Nodes (33): collect(), Doc, lint_file(), main(), pair(), _plan_contracts(), _r9_in_scope(), Bước trong mục 'Các bước' phải đánh số 1, 2, 3… không nhảy, không lặp. (+25 more)

### Community 6 - "Changelog"
Cohesion: 0.06
Nodes (31): 0.10.0 — 2026-08-09, 0.11.0 — 2026-08-09, 0.11.10 — 2026-08-13, 0.11.11 — 2026-08-13, 0.11.12 — 2026-08-13, 0.11.13 — 2026-08-13, 0.11.1 — 2026-08-09, 0.11.2 — 2026-08-09 (+23 more)

### Community 7 - "check_canvas_layout.py"
Cohesion: 0.16
Nodes (21): bbox(), boxes_overlap(), center(), check_chapters(), check_contain(), check_fontsize(), check_order(), check_overlap() (+13 more)

### Community 8 - "tdq_finish.py"
Cohesion: 0.16
Nodes (20): _changed_files(), _log(), _log_enabled(), main(), _now(), parse_args(), _project_dir(), Một dòng ≤ 200 ký tự cho trường hợp mọi bước pass. (+12 more)

### Community 9 - "context_surface.py"
Cohesion: 0.18
Nodes (19): _log(), _log_enabled(), main(), measure_hooks(), _num(), _payload(), print_table(), Quét toàn bộ bề mặt tài liệu, trả về danh sách dòng bảng. (+11 more)

### Community 10 - "skill_inventory.py"
Cohesion: 0.15
Nodes (19): _clean(), _condense(), _enabled_plugins(), _filter(), _frontmatter(), inventory(), _load_json(), main() (+11 more)

### Community 11 - "plugin_tiers.py"
Cohesion: 0.34
Nodes (16): _claude_dir(), cmd_enable(), cmd_reset(), cmd_status(), _key_for(), _load_json(), _log(), _log_on() (+8 more)

### Community 12 - "code_rule_scan.py"
Cohesion: 0.27
Nodes (12): chay_linter(), doc_bang_linter(), _git(), gom_file(), in_bang(), log(), main(), quet() (+4 more)

### Community 13 - "Chapter"
Cohesion: 0.23
Nodes (4): Chapter, Trả danh sách (x, w) cho `count` thẻ dàn đều hết bề ngang chương., Bố cục MỘT cột: trả danh sách y cho các khối cao `heights` xếp dọc., Gom element của một chương rồi ghi một lượt.

### Community 14 - "tdq-workflow — Plugin Claude Code"
Cohesion: 0.22
Nodes (8): Cài đặt (chỉ trong repo/project), Cách hook điều khiển agent, Cấu trúc, Duyệt bằng chat thường, Dùng hằng ngày, Pipeline, Quy ước cứng, tdq-workflow — Plugin Claude Code

### Community 15 - "quet"
Cohesion: 0.36
Nodes (7): khoi_mau(), la_ky_hieu(), main(), quet(), True khi ch là dấu câu/ký hiệu ngoài ASCII — thứ whitelist phải quản., Nội dung các khối ``` trong file — đây mới là phần THẬT SỰ in ra cho user., {ký tự: (tổng số lần, {file: số lần})} cho mọi ký hiệu ngoài ASCII.

## Knowledge Gaps
- **35 isolated node(s):** `0.19.0 — 2026-08-15`, `0.18.0 — 2026-08-14`, `0.17.0 — 2026-08-14`, `0.16.0 — 2026-08-14`, `0.15.1 — 2026-08-14` (+30 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `_common.py` to `tdq_state.py`?**
  _High betweenness centrality (0.005) - this node is a cross-community bridge._
- **Why does `turn_log_append()` connect `_common.py` to `tdq_state.py`?**
  _High betweenness centrality (0.005) - this node is a cross-community bridge._
- **Why does `Chapter` connect `Chapter` to `canvas_a4_rebuild.py`?**
  _High betweenness centrality (0.004) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `main()` (e.g. with `effective_lane()` and `effective_mode()`) actually correct?**
  _`main()` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `0.19.0 — 2026-08-15`, `0.18.0 — 2026-08-14`, `0.17.0 — 2026-08-14` to the rest of the system?**
  _35 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `tdq_state.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05185185185185185 - nodes in this community are weakly interconnected._
- **Should `_common.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07740112994350283 - nodes in this community are weakly interconnected._