# Graph Report - TDQWorkflow  (2026-08-16)

## Corpus Check
- 31 files · ~40,414 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 561 nodes · 1083 edges · 24 communities
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 58 edges (avg confidence: 0.7)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e88a9c37`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- canvas_a4_rebuild.py
- token_audit.py
- tdq_checkstatus.py
- claude_export.py
- _common.py
- doc_lint.py
- tdq_finish.py
- tdq_state.py
- Changelog
- check_canvas_layout.py
- cli
- tdq_timing.py
- context_surface.py
- skill_inventory.py
- turn_snapshot
- plugin_tiers.py
- effective_lane
- main
- Chapter
- tdq-workflow — Plugin Claude Code
- quet
- _parse_approve_args
- _cli_approve
- _warn

## God Nodes (most connected - your core abstractions)
1. `Changelog` - 24 edges
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
- `turn_rows()` --calls--> `turn_log_read()`  [INFERRED]
  hooks/scripts/_common.py → scripts/tdq_state.py
- `main()` --calls--> `effective_lane()`  [INFERRED]
  hooks/scripts/edit_gate.py → scripts/tdq_state.py
- `main()` --calls--> `effective_phase()`  [INFERRED]
  hooks/scripts/edit_gate.py → scripts/tdq_state.py
- `main()` --calls--> `load()`  [INFERRED]
  hooks/scripts/edit_gate.py → scripts/tdq_state.py

## Import Cycles
- None detected.

## Communities (24 total, 0 thin omitted)

### Community 0 - "canvas_a4_rebuild.py"
Cohesion: 0.08
Nodes (43): build_ch4(), build_ch7(), build_all(), build_generic(), build_moved(), build_toc(), Builder, chapter_elements() (+35 more)

### Community 1 - "token_audit.py"
Cohesion: 0.07
Nodes (48): _blocks(), _has_usage(), _log(), _log_enabled(), main(), median(), merge(), _now() (+40 more)

### Community 2 - "tdq_checkstatus.py"
Cohesion: 0.08
Nodes (45): bao_cao_markdown(), _ca(), cham_ca_lech(), _cham_d2(), _cham_d3(), _cham_d5(), _cham_d6(), _cham_d7() (+37 more)

### Community 3 - "claude_export.py"
Cohesion: 0.09
Nodes (44): cli_versions(), clone_repo(), cmd_build(), cmd_check(), collect_config_files(), copy_config(), copy_launch_agents(), copy_repo_memory() (+36 more)

### Community 4 - "_common.py"
Cohesion: 0.11
Nodes (39): _check_signal_mismatch(), _clean(), _latest_signal(), main(), Dòng kind="signal" GẦN NHẤT khớp target (duyệt ngược sổ turn)., already_reminded(), block(), echo_line() (+31 more)

### Community 5 - "doc_lint.py"
Cohesion: 0.08
Nodes (33): collect(), Doc, lint_file(), main(), pair(), _plan_contracts(), _r9_in_scope(), Bước trong mục 'Các bước' phải đánh số 1, 2, 3… không nhảy, không lặp. (+25 more)

### Community 6 - "tdq_finish.py"
Cohesion: 0.15
Nodes (22): _changed_files(), _log(), _log_enabled(), main(), _now(), parse_args(), _project_dir(), Về `idle` = hết request → chốt sổ thời gian vào docs/tdq/timing.jsonl.      Chạy (+14 more)

### Community 7 - "tdq_state.py"
Cohesion: 0.16
Nodes (16): _atomic_write(), lane_label(), plugin_root_cmd(), prompt_context_last(), prompt_context_path(), prompt_context_save(), Xoá dòng của session này (đầu turn). Dòng session khác giữ nguyên., Digest nội dung [TDQ:...] đã in ở turn trước cho session này, None nếu chưa có. (+8 more)

### Community 8 - "Changelog"
Cohesion: 0.08
Nodes (24): 0.11.10 — 2026-08-13, 0.11.11 — 2026-08-13, 0.11.12 — 2026-08-13, 0.11.13 — 2026-08-13, 0.11.4 trở về 0.7.0, 0.11.5 — 2026-08-13, 0.11.6 — 2026-08-13, 0.11.7 — 2026-08-13 (+16 more)

### Community 9 - "check_canvas_layout.py"
Cohesion: 0.16
Nodes (21): bbox(), boxes_overlap(), center(), check_chapters(), check_contain(), check_fontsize(), check_order(), check_overlap() (+13 more)

### Community 10 - "cli"
Cohesion: 0.11
Nodes (24): cli(), _echo_state(), find_shadow_states(), ghi_moc_phase(), _info(), now_iso(), parse_slug(), _parse_value() (+16 more)

### Community 11 - "tdq_timing.py"
Cohesion: 0.14
Nodes (22): bang_markdown(), cua_so_phase(), da_dong_so(), dinh_dang(), dong_ho_ngan(), dong_so(), _giay_model(), _log() (+14 more)

### Community 12 - "context_surface.py"
Cohesion: 0.18
Nodes (19): _log(), _log_enabled(), main(), measure_hooks(), _num(), _payload(), print_table(), Quét toàn bộ bề mặt tài liệu, trả về danh sách dòng bảng. (+11 more)

### Community 13 - "skill_inventory.py"
Cohesion: 0.15
Nodes (19): _clean(), _condense(), _enabled_plugins(), _filter(), _frontmatter(), inventory(), _load_json(), main() (+11 more)

### Community 14 - "turn_snapshot"
Cohesion: 0.21
Nodes (12): _git(), stdout (bytes) của lệnh git, hoặc None khi không chạy được., Gốc repo (porcelain in path theo gốc, không theo cwd). None nếu không phải repo., Dấu nhận dạng file untracked → (dấu, số byte đã đọc).      Ưu tiên NỘI DUNG: mti, Vân tay trạng thái làm việc của repo, hoặc None khi không lấy được.      Gồm cả, Path đang khác so với HEAD (bỏ cờ trạng thái, rename lấy vế đích).      Cùng vùn, Trạng thái đầu turn: log hôm nay + vân tay repo + danh sách path đang bẩn     +, repo_root() (+4 more)

### Community 15 - "plugin_tiers.py"
Cohesion: 0.34
Nodes (16): _claude_dir(), cmd_enable(), cmd_reset(), cmd_status(), _key_for(), _load_json(), _log(), _log_on() (+8 more)

### Community 16 - "effective_lane"
Cohesion: 0.33
Nodes (10): effective_lane(), effective_phase(), next_headline(), phase_key(), Khoá tra PHASE_TABLE cho state hiện tại., Dòng 1 của `next` — cũng là toàn bộ output của `next --brief`., Khối 5 phần (spec §2.2), ≤20 dòng.      brief=True   → đúng 1 dòng tiêu đề (dùng, Mirror markdown ≤30 dòng cho agent/user đọc thẳng (spec §2.3.1). (+2 more)

### Community 17 - "main"
Cohesion: 0.18
Nodes (16): approve_hint(), plan_mode(), Mode đã chốt trong plan_file (dòng 'Mode thực thi:'), None nếu chưa ghi., _compact(), _emit(), looks_like_approval(), main(), mode_from_answer() (+8 more)

### Community 18 - "Chapter"
Cohesion: 0.23
Nodes (4): Chapter, Trả danh sách (x, w) cho `count` thẻ dàn đều hết bề ngang chương., Bố cục MỘT cột: trả danh sách y cho các khối cao `heights` xếp dọc., Gom element của một chương rồi ghi một lượt.

### Community 19 - "tdq-workflow — Plugin Claude Code"
Cohesion: 0.22
Nodes (8): Cài đặt (chỉ trong repo/project), Cách hook điều khiển agent, Cấu trúc, Duyệt bằng chat thường, Dùng hằng ngày, Pipeline, Quy ước cứng, tdq-workflow — Plugin Claude Code

### Community 20 - "quet"
Cohesion: 0.36
Nodes (7): khoi_mau(), la_ky_hieu(), main(), quet(), True khi ch là dấu câu/ký hiệu ngoài ASCII — thứ whitelist phải quản., Nội dung các khối ``` trong file — đây mới là phần THẬT SỰ in ra cho user., {ký tự: (tổng số lần, {file: số lần})} cho mọi ký hiệu ngoài ASCII.

### Community 21 - "_parse_approve_args"
Cohesion: 0.33
Nodes (6): _fail(), normalize_lane(), _parse_approve_args(), -> (target, mode, by, no_qc). Chỉ lỗi khi cú pháp thật sự sai., Chỉ dùng cho SAI CÚ PHÁP LỆNH — exit 2 (spec §2.9.4)., Bí danh -> định danh máy ("quick"/"full"). Không nhận ra -> None (người gọi

### Community 22 - "_cli_approve"
Cohesion: 0.27
Nodes (10): _cli_approve(), default_state(), _file_changed_since_approval(), load(), plan_tick_state(), True khi file spec/plan đã đổi nội dung so với lúc duyệt. Dùng để phân biệt, Ghi nhận việc user đã duyệt. Không phải gate: cảnh báo khi lệch nhưng     VẪN gh, Đọc state. Trả None khi chưa có file.      File hỏng (S2): đổi tên thành state.j (+2 more)

### Community 23 - "_warn"
Cohesion: 0.33
Nodes (6): _dong_so_request_cu(), effective_mode(), log_enabled(), Cảnh báo ra stderr kèm timestamp (spec §4.1). Tắt bằng TDQ_LOG=0.      Không bao, Đóng sổ thời gian của request đang mở vào docs/tdq/timing.jsonl.      Import MUỘ, _warn()

## Knowledge Gaps
- **30 isolated node(s):** `0.22.0 — 2026-08-16`, `0.21.0 — 2026-08-16`, `0.20.0 — 2026-08-15`, `0.19.0 — 2026-08-15`, `0.18.0 — 2026-08-14` (+25 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `turn_log_append()` connect `_common.py` to `main`, `cli`, `tdq_state.py`?**
  _High betweenness centrality (0.007) - this node is a cross-community bridge._
- **Why does `main()` connect `main` to `_common.py`, `tdq_state.py`, `turn_snapshot`, `effective_lane`, `_cli_approve`, `_warn`?**
  _High betweenness centrality (0.004) - this node is a cross-community bridge._
- **Why does `payload_cwd()` connect `_common.py` to `main`, `cli`?**
  _High betweenness centrality (0.004) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `main()` (e.g. with `effective_lane()` and `effective_mode()`) actually correct?**
  _`main()` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `0.22.0 — 2026-08-16`, `0.21.0 — 2026-08-16`, `0.20.0 — 2026-08-15` to the rest of the system?**
  _30 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `canvas_a4_rebuild.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08176100628930817 - nodes in this community are weakly interconnected._
- **Should `token_audit.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07183673469387755 - nodes in this community are weakly interconnected._