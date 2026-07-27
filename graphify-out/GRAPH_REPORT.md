# Graph Report - TDQWorkflow  (2026-07-27)

## Corpus Check
- 49 files · ~19,613 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 177 nodes · 394 edges · 12 communities (9 shown, 3 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7fb76e52`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- run_hook
- read_payload
- TestEditGate
- write_state
- Hướng dẫn tự cài tdq-workflow ở user-level (thủ công)
- TestBashGate
- tdq_state.py
- TestPromptContext
- write_file
- Working log — 2026-07-27
- tdq-workflow — Plugin Claude Code
- TestState

## God Nodes (most connected - your core abstractions)
1. `write_state()` - 35 edges
2. `write_file()` - 23 edges
3. `run_hook()` - 17 edges
4. `load_fixture()` - 15 edges
5. `read_state()` - 15 edges
6. `Working log — 2026-07-27` - 14 edges
7. `approve()` - 14 edges
8. `TestApproveGate` - 14 edges
9. `TestEditGate` - 14 edges
10. `read_payload()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `approve()` --calls--> `run_hook()`  [EXTRACTED]
  tests/test_approve_gate.py → tests/helper.py
- `approve()` --calls--> `load_fixture()`  [EXTRACTED]
  tests/test_approve_gate.py → tests/helper.py
- `main()` --calls--> `read_payload()`  [EXTRACTED]
  hooks/scripts/approve_gate.py → hooks/scripts/_common.py
- `main()` --calls--> `read_payload()`  [EXTRACTED]
  hooks/scripts/bash_gate.py → hooks/scripts/_common.py
- `main()` --calls--> `read_payload()`  [EXTRACTED]
  hooks/scripts/edit_gate.py → hooks/scripts/_common.py

## Import Cycles
- None detected.

## Communities (12 total, 3 thin omitted)

### Community 0 - "run_hook"
Cohesion: 0.14
Nodes (12): load_fixture(), Shared test utilities: run hook scripts as subprocesses with stdin JSON., run_hook(), B3 — bash_gate.py: git naming bans, AI commit-msg bans, state.json write bans., B4 — session_start.py + prompt_context.py: context injection per state., TestSessionStart, ChainBase, E1 — simulated end-to-end hook chains for both lanes (full + quick). (+4 more)

### Community 1 - "read_payload"
Cohesion: 0.21
Nodes (16): block(), main(), _clean(), main(), approve_hint(), deny(), payload_cwd(), Shared helpers for TDQ hook scripts (stdlib only). (+8 more)

### Community 2 - "TestEditGate"
Cohesion: 0.22
Nodes (5): decision(), Parse PreToolUse hook stdout -> (permissionDecision, reason)., now_iso(), B2 — edit_gate.py: block edits pre-approval, protect state.json, quick log-first, TestEditGate

### Community 3 - "write_state"
Cohesion: 0.26
Nodes (5): read_state(), write_state(), approve(), B1 — approve_gate.py: validate by state + registered detail file., TestApproveGate

### Community 4 - "Hướng dẫn tự cài tdq-workflow ở user-level (thủ công)"
Cohesion: 0.29
Nodes (6): 1. Cài qua local marketplace, 2. Đồng bộ rule working log ở `~/.claude/CLAUDE.md`, 3. Thêm instruction TDQ cho MỌI task vào `~/.claude/CLAUDE.md`, 4. Gỡ, Hướng dẫn tự cài tdq-workflow ở user-level (thủ công), Lưu ý an toàn

### Community 6 - "tdq_state.py"
Cohesion: 0.30
Nodes (10): cli(), default_state(), _fail(), load(), now_iso(), _parse_value(), Return the state dict, or None if missing/corrupt., Atomic write (temp file + rename). Returns the saved state. (+2 more)

### Community 9 - "Working log — 2026-07-27"
Cohesion: 0.13
Nodes (14): ~16:30 — Lập spec cho TDQWorkflow plugin, ~16:50 — Đổi đường dẫn working log theo yêu cầu người dùng, ~17:10 — Bổ sung quy tắc khai thác Tavily vào spec, ~17:25 — Check lazy load, bổ sung mục 3.1 vào spec, ~17:35 — Approve gate luôn hướng dẫn user lệnh duyệt, ~17:50 — Approve validate bằng state + detail file; vá lỗ hổng state.json, ~18:05 — Lane quick có cửa duyệt nhẹ + ghi summary plan vào working log trước implement, ~18:20 — User duyệt spec v0.1.6; lập plan (+6 more)

### Community 10 - "tdq-workflow — Plugin Claude Code"
Cohesion: 0.29
Nodes (6): Cài đặt (chỉ trong repo/project), Cấu trúc, Dùng hằng ngày, Pipeline, Quy ước cứng, tdq-workflow — Plugin Claude Code

### Community 11 - "TestState"
Cohesion: 0.21
Nodes (3): run_state_cli(), A3 — tdq_state.py: default schema, CLI, protected keys, atomic write., TestState

## Knowledge Gaps
- **23 isolated node(s):** `~16:30 — Lập spec cho TDQWorkflow plugin`, `~16:50 — Đổi đường dẫn working log theo yêu cầu người dùng`, `~17:10 — Bổ sung quy tắc khai thác Tavily vào spec`, `~17:25 — Check lazy load, bổ sung mục 3.1 vào spec`, `~17:35 — Approve gate luôn hướng dẫn user lệnh duyệt` (+18 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `write_state()` connect `write_state` to `run_hook`, `TestEditGate`, `TestPromptContext`, `write_file`, `TestState`?**
  _High betweenness centrality (0.147) - this node is a cross-community bridge._
- **Why does `run_hook()` connect `run_hook` to `TestEditGate`, `write_state`, `TestBashGate`, `TestPromptContext`, `write_file`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Why does `TestBashGate` connect `TestBashGate` to `run_hook`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **What connects `~16:30 — Lập spec cho TDQWorkflow plugin`, `~16:50 — Đổi đường dẫn working log theo yêu cầu người dùng`, `~17:10 — Bổ sung quy tắc khai thác Tavily vào spec` to the rest of the system?**
  _23 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `run_hook` be split into smaller, more focused modules?**
  _Cohesion score 0.13756613756613756 - nodes in this community are weakly interconnected._
- **Should `Working log — 2026-07-27` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._