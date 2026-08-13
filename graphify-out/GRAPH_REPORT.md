# Graph Report - TDQWorkflow  (2026-08-14)

## Corpus Check
- 27 files · ~31,878 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 455 nodes · 890 edges · 14 communities
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 51 edges (avg confidence: 0.69)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b79ab790`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- canvas_a4_rebuild.py
- claude_export.py
- _common.py
- doc_lint.py
- token_audit.py
- tdq_state.py
- check_canvas_layout.py
- tdq_finish.py
- context_surface.py
- skill_inventory.py
- plugin_tiers.py
- Changelog
- tdq-workflow — Plugin Claude Code
- Chapter

## God Nodes (most connected - your core abstractions)
1. `Changelog` - 26 edges
2. `main()` - 17 edges
3. `log()` - 17 edges
4. `cmd_build()` - 17 edges
5. `cli()` - 17 edges
6. `main()` - 15 edges
7. `_cli_approve()` - 14 edges
8. `payload_cwd()` - 13 edges
9. `main()` - 12 edges
10. `Builder` - 12 edges

## Surprising Connections (you probably didn't know these)
- `payload_cwd()` --calls--> `resolve_project_dir()`  [INFERRED]
  hooks/scripts/_common.py → scripts/tdq_state.py
- `turn_rows()` --calls--> `turn_log_read()`  [INFERRED]
  hooks/scripts/_common.py → scripts/tdq_state.py
- `main()` --calls--> `effective_lane()`  [INFERRED]
  hooks/scripts/edit_gate.py → scripts/tdq_state.py
- `main()` --calls--> `effective_phase()`  [INFERRED]
  hooks/scripts/edit_gate.py → scripts/tdq_state.py
- `main()` --calls--> `plan_tick_state()`  [INFERRED]
  hooks/scripts/edit_gate.py → scripts/tdq_state.py

## Import Cycles
- None detected.

## Communities (14 total, 0 thin omitted)

### Community 0 - "canvas_a4_rebuild.py"
Cohesion: 0.08
Nodes (43): build_ch4(), build_ch7(), build_all(), build_generic(), build_moved(), build_toc(), Builder, chapter_elements() (+35 more)

### Community 1 - "claude_export.py"
Cohesion: 0.09
Nodes (44): cli_versions(), clone_repo(), cmd_build(), cmd_check(), collect_config_files(), copy_config(), copy_launch_agents(), copy_repo_memory() (+36 more)

### Community 2 - "_common.py"
Cohesion: 0.09
Nodes (49): _check_signal_mismatch(), _clean(), _latest_signal(), main(), Dòng kind="signal" GẦN NHẤT khớp target (duyệt ngược sổ turn)., already_reminded(), approve_hint(), block() (+41 more)

### Community 3 - "doc_lint.py"
Cohesion: 0.09
Nodes (30): collect(), Doc, lint_file(), main(), pair(), _plan_contracts(), Bước trong mục 'Các bước' phải đánh số 1, 2, 3… không nhảy, không lặp., Lệnh phải copy-paste được: trong khối ```, trong inline-code, hoặc ô bảng. (+22 more)

### Community 4 - "token_audit.py"
Cohesion: 0.11
Nodes (30): _all_items(), carry_cost(), classify(), _content_text(), cost_equivalent(), default_transcript_dir(), find_sessions(), _fmt() (+22 more)

### Community 5 - "tdq_state.py"
Cohesion: 0.05
Nodes (78): _atomic_write(), cli(), _cli_approve(), default_state(), _echo_state(), effective_lane(), effective_mode(), effective_phase() (+70 more)

### Community 6 - "check_canvas_layout.py"
Cohesion: 0.16
Nodes (21): bbox(), boxes_overlap(), center(), check_chapters(), check_contain(), check_fontsize(), check_order(), check_overlap() (+13 more)

### Community 7 - "tdq_finish.py"
Cohesion: 0.16
Nodes (20): _changed_files(), _log(), _log_enabled(), main(), _now(), parse_args(), _project_dir(), Một dòng ≤ 200 ký tự cho trường hợp mọi bước pass. (+12 more)

### Community 8 - "context_surface.py"
Cohesion: 0.18
Nodes (19): _log(), _log_enabled(), main(), measure_hooks(), _num(), _payload(), print_table(), Quét toàn bộ bề mặt tài liệu, trả về danh sách dòng bảng. (+11 more)

### Community 9 - "skill_inventory.py"
Cohesion: 0.16
Nodes (17): _clean(), _condense(), _enabled_plugins(), _frontmatter(), inventory(), _load_json(), main(), _plugin_skill_dirs() (+9 more)

### Community 10 - "plugin_tiers.py"
Cohesion: 0.34
Nodes (16): _claude_dir(), cmd_enable(), cmd_reset(), cmd_status(), _key_for(), _load_json(), _log(), _log_on() (+8 more)

### Community 11 - "Changelog"
Cohesion: 0.06
Nodes (33): 0.10.0 — 2026-08-09, 0.11.0 — 2026-08-09, 0.11.10 — 2026-08-13, 0.11.11 — 2026-08-13, 0.11.12 — 2026-08-13, 0.11.13 — 2026-08-13, 0.11.1 — 2026-08-09, 0.11.2 — 2026-08-09 (+25 more)

### Community 12 - "tdq-workflow — Plugin Claude Code"
Cohesion: 0.22
Nodes (8): Cài đặt (chỉ trong repo/project), Cách hook điều khiển agent, Cấu trúc, Duyệt bằng chat thường, Dùng hằng ngày, Pipeline, Quy ước cứng, tdq-workflow — Plugin Claude Code

### Community 13 - "Chapter"
Cohesion: 0.23
Nodes (4): Chapter, Trả danh sách (x, w) cho `count` thẻ dàn đều hết bề ngang chương., Bố cục MỘT cột: trả danh sách y cho các khối cao `heights` xếp dọc., Gom element của một chương rồi ghi một lượt.

## Knowledge Gaps
- **34 isolated node(s):** `0.13.0 — 2026-08-14`, `0.12.0 — 2026-08-13`, `0.11.13 — 2026-08-13`, `0.11.12 — 2026-08-13`, `0.11.11 — 2026-08-13` (+29 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `turn_log_append()` connect `_common.py` to `tdq_state.py`?**
  _High betweenness centrality (0.006) - this node is a cross-community bridge._
- **Why does `Chapter` connect `Chapter` to `canvas_a4_rebuild.py`?**
  _High betweenness centrality (0.005) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `main()` (e.g. with `effective_lane()` and `effective_mode()`) actually correct?**
  _`main()` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `0.13.0 — 2026-08-14`, `0.12.0 — 2026-08-13`, `0.11.13 — 2026-08-13` to the rest of the system?**
  _34 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `canvas_a4_rebuild.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08176100628930817 - nodes in this community are weakly interconnected._
- **Should `claude_export.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09292929292929293 - nodes in this community are weakly interconnected._
- **Should `_common.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08888888888888889 - nodes in this community are weakly interconnected._