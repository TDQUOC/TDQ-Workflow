# Graph Report - TDQWorkflow  (2026-07-27)

## Corpus Check
- 49 files · ~18,755 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 161 nodes · 380 edges · 10 communities (7 shown, 3 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c26942a4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- run_hook
- read_payload
- write_state
- read_state
- TestState
- TestBashGate
- tdq_state.py
- TestPromptContext
- write_file
- Working log — 2026-07-27

## God Nodes (most connected - your core abstractions)
1. `write_state()` - 35 edges
2. `write_file()` - 23 edges
3. `run_hook()` - 17 edges
4. `load_fixture()` - 15 edges
5. `read_state()` - 15 edges
6. `approve()` - 14 edges
7. `TestApproveGate` - 14 edges
8. `TestEditGate` - 14 edges
9. `read_payload()` - 13 edges
10. `TestBashGate` - 13 edges

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

## Communities (10 total, 3 thin omitted)

### Community 0 - "run_hook"
Cohesion: 0.13
Nodes (13): load_fixture(), Shared test utilities: run hook scripts as subprocesses with stdin JSON., run_hook(), B1 — approve_gate.py: validate by state + registered detail file., B3 — bash_gate.py: git naming bans, AI commit-msg bans, state.json write bans., B4 — session_start.py + prompt_context.py: context injection per state., TestSessionStart, ChainBase (+5 more)

### Community 1 - "read_payload"
Cohesion: 0.21
Nodes (16): block(), main(), _clean(), main(), approve_hint(), deny(), payload_cwd(), Shared helpers for TDQ hook scripts (stdlib only). (+8 more)

### Community 2 - "write_state"
Cohesion: 0.25
Nodes (6): decision(), Parse PreToolUse hook stdout -> (permissionDecision, reason)., write_state(), now_iso(), B2 — edit_gate.py: block edits pre-approval, protect state.json, quick log-first, TestEditGate

### Community 3 - "read_state"
Cohesion: 0.25
Nodes (3): read_state(), approve(), TestApproveGate

### Community 4 - "TestState"
Cohesion: 0.21
Nodes (3): run_state_cli(), A3 — tdq_state.py: default schema, CLI, protected keys, atomic write., TestState

### Community 6 - "tdq_state.py"
Cohesion: 0.30
Nodes (10): cli(), default_state(), _fail(), load(), now_iso(), _parse_value(), Return the state dict, or None if missing/corrupt., Atomic write (temp file + rename). Returns the saved state. (+2 more)

### Community 9 - "Working log — 2026-07-27"
Cohesion: 0.15
Nodes (12): ~16:30 — Lập spec cho TDQWorkflow plugin, ~16:50 — Đổi đường dẫn working log theo yêu cầu người dùng, ~17:10 — Bổ sung quy tắc khai thác Tavily vào spec, ~17:25 — Check lazy load, bổ sung mục 3.1 vào spec, ~17:35 — Approve gate luôn hướng dẫn user lệnh duyệt, ~17:50 — Approve validate bằng state + detail file; vá lỗ hổng state.json, ~18:05 — Lane quick có cửa duyệt nhẹ + ghi summary plan vào working log trước implement, ~18:20 — User duyệt spec v0.1.6; lập plan (+4 more)

## Knowledge Gaps
- **11 isolated node(s):** `~16:30 — Lập spec cho TDQWorkflow plugin`, `~16:50 — Đổi đường dẫn working log theo yêu cầu người dùng`, `~17:10 — Bổ sung quy tắc khai thác Tavily vào spec`, `~17:25 — Check lazy load, bổ sung mục 3.1 vào spec`, `~17:35 — Approve gate luôn hướng dẫn user lệnh duyệt` (+6 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `write_state()` connect `write_state` to `run_hook`, `read_state`, `TestState`, `TestPromptContext`, `write_file`?**
  _High betweenness centrality (0.178) - this node is a cross-community bridge._
- **Why does `run_hook()` connect `run_hook` to `write_state`, `read_state`, `TestBashGate`, `TestPromptContext`, `write_file`?**
  _High betweenness centrality (0.084) - this node is a cross-community bridge._
- **Why does `TestBashGate` connect `TestBashGate` to `run_hook`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **What connects `~16:30 — Lập spec cho TDQWorkflow plugin`, `~16:50 — Đổi đường dẫn working log theo yêu cầu người dùng`, `~17:10 — Bổ sung quy tắc khai thác Tavily vào spec` to the rest of the system?**
  _11 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `run_hook` be split into smaller, more focused modules?**
  _Cohesion score 0.12873563218390804 - nodes in this community are weakly interconnected._