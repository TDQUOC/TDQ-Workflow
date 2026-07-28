# Graph Report - TDQWorkflow  (2026-07-28)

## Corpus Check
- 51 files · ~22,664 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 236 nodes · 477 edges · 16 communities (12 shown, 4 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5da97cb0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- run_hook
- write_state
- _common.py
- TestEditGate
- TestState
- Working log — 2026-07-27
- TestBashGate
- TDQ Conventions
- tdq_state.py
- Hướng dẫn tự cài tdq-workflow ở user-level (thủ công)
- stop_gate.py
- tdq-workflow — Plugin Claude Code
- TestPromptContext
- Working log — 2026-07-28
- .stop
- TDQ Approve (user-only)

## God Nodes (most connected - your core abstractions)
1. `write_state()` - 43 edges
2. `write_file()` - 28 edges
3. `run_hook()` - 19 edges
4. `read_state()` - 19 edges
5. `TestApproveGate` - 19 edges
6. `approve()` - 18 edges
7. `load_fixture()` - 17 edges
8. `Working log — 2026-07-27` - 14 edges
9. `TestEditGate` - 14 edges
10. `TestBashGate` - 13 edges

## Surprising Connections (you probably didn't know these)
- `approve()` --calls--> `run_hook()`  [EXTRACTED]
  tests/test_approve_gate.py → tests/helper.py
- `approve()` --calls--> `load_fixture()`  [EXTRACTED]
  tests/test_approve_gate.py → tests/helper.py
- `main()` --calls--> `read_payload()`  [EXTRACTED]
  hooks/scripts/bash_gate.py → hooks/scripts/_common.py
- `main()` --calls--> `read_payload()`  [EXTRACTED]
  hooks/scripts/edit_gate.py → hooks/scripts/_common.py
- `main()` --calls--> `read_payload()`  [EXTRACTED]
  hooks/scripts/session_start.py → hooks/scripts/_common.py

## Import Cycles
- None detected.

## Communities (16 total, 4 thin omitted)

### Community 0 - "run_hook"
Cohesion: 0.12
Nodes (14): load_fixture(), Shared test utilities: run hook scripts as subprocesses with stdin JSON., Minimal Claude Code transcript: one assistant message with text content., run_hook(), write_transcript(), B3 — bash_gate.py: git naming bans, AI commit-msg bans, state.json write bans., B4 — session_start.py + prompt_context.py: context injection per state., TestSessionStart (+6 more)

### Community 1 - "write_state"
Cohesion: 0.17
Nodes (7): read_state(), write_file(), write_state(), approve(), B1 — approve_gate.py: validate by state + registered detail file., TestApproveGate, TestStopGate

### Community 2 - "_common.py"
Cohesion: 0.19
Nodes (14): block(), main(), _clean(), main(), approve_hint(), deny(), payload_cwd(), Shared helpers for TDQ hook scripts (stdlib only). (+6 more)

### Community 3 - "TestEditGate"
Cohesion: 0.22
Nodes (5): decision(), Parse PreToolUse hook stdout -> (permissionDecision, reason)., now_iso(), B2 — edit_gate.py: block edits pre-approval, protect state.json, quick log-first, TestEditGate

### Community 4 - "TestState"
Cohesion: 0.21
Nodes (3): run_state_cli(), A3 — tdq_state.py: default schema, CLI, protected keys, atomic write., TestState

### Community 5 - "Working log — 2026-07-27"
Cohesion: 0.13
Nodes (14): ~16:30 — Lập spec cho TDQWorkflow plugin, ~16:50 — Đổi đường dẫn working log theo yêu cầu người dùng, ~17:10 — Bổ sung quy tắc khai thác Tavily vào spec, ~17:25 — Check lazy load, bổ sung mục 3.1 vào spec, ~17:35 — Approve gate luôn hướng dẫn user lệnh duyệt, ~17:50 — Approve validate bằng state + detail file; vá lỗ hổng state.json, ~18:05 — Lane quick có cửa duyệt nhẹ + ghi summary plan vào working log trước implement, ~18:20 — User duyệt spec v0.1.6; lập plan (+6 more)

### Community 7 - "TDQ Conventions"
Cohesion: 0.09
Nodes (19): Doc tree (in the user's project), Git, Language, Quality bars, Research, State, TDQ Conventions, Working log (mandatory) (+11 more)

### Community 8 - "tdq_state.py"
Cohesion: 0.30
Nodes (10): cli(), default_state(), _fail(), load(), now_iso(), _parse_value(), Return the state dict, or None if missing/corrupt., Atomic write (temp file + rename). Returns the saved state. (+2 more)

### Community 9 - "Hướng dẫn tự cài tdq-workflow ở user-level (thủ công)"
Cohesion: 0.29
Nodes (6): 1. Cài qua local marketplace, 2. Đồng bộ rule working log ở `~/.claude/CLAUDE.md`, 3. Thêm instruction TDQ cho MỌI task vào `~/.claude/CLAUDE.md`, 4. Gỡ, Hướng dẫn tự cài tdq-workflow ở user-level (thủ công), Lưu ý an toàn

### Community 10 - "stop_gate.py"
Cohesion: 0.43
Nodes (6): check_invite(), invite_problem(), last_assistant_text(), main(), Text of the most recent assistant message in the transcript (or '')., Vietnamese reason why this approve invitation cannot be honoured, or None.

### Community 11 - "tdq-workflow — Plugin Claude Code"
Cohesion: 0.29
Nodes (6): Cài đặt (chỉ trong repo/project), Cấu trúc, Dùng hằng ngày, Pipeline, Quy ước cứng, tdq-workflow — Plugin Claude Code

### Community 13 - "Working log — 2026-07-28"
Cohesion: 0.20
Nodes (9): ~00:30 — Detect bug approve_gate không ghi state (báo từ project insightfaceserverv2), ~00:35 — Implement fix approve_gate matcher (user đã gõ lệnh duyệt quick; hook duyệt fail im lặng do chính bug này — live repro), ~00:45 — Setup test live sau restart (user yêu cầu verify fix), ~00:45 — Verify live PASS + dọn test, ~09:04 — Request `fix-implement-mode-gate` (lane quick, ĐÃ DUYỆT), ~09:20 — Mở request `2026-07-28-fix-invite-without-request` (lane quick, CHỜ DUYỆT), ~09:25 — Đóng turn: graphify + dọn, Plan ĐÃ DUYỆT 09:17 (Mode thực thi: main — 6 task tuần tự, cùng 2 file hook) (+1 more)

## Knowledge Gaps
- **46 isolated node(s):** `~00:30 — Detect bug approve_gate không ghi state (báo từ project insightfaceserverv2)`, `~00:35 — Implement fix approve_gate matcher (user đã gõ lệnh duyệt quick; hook duyệt fail im lặng do chính bug này — live repro)`, `~00:45 — Setup test live sau restart (user yêu cầu verify fix)`, `~00:45 — Verify live PASS + dọn test`, `~09:04 — Request `fix-implement-mode-gate` (lane quick, ĐÃ DUYỆT)` (+41 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `write_state()` connect `write_state` to `run_hook`, `TestEditGate`, `TestState`, `TestPromptContext`, `.stop`?**
  _High betweenness centrality (0.123) - this node is a cross-community bridge._
- **Why does `run_hook()` connect `run_hook` to `write_state`, `TestEditGate`, `TestBashGate`, `TestPromptContext`, `.stop`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Why does `write_file()` connect `write_state` to `run_hook`, `TestEditGate`, `TestPromptContext`, `.stop`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **What connects `~00:30 — Detect bug approve_gate không ghi state (báo từ project insightfaceserverv2)`, `~00:35 — Implement fix approve_gate matcher (user đã gõ lệnh duyệt quick; hook duyệt fail im lặng do chính bug này — live repro)`, `~00:45 — Setup test live sau restart (user yêu cầu verify fix)` to the rest of the system?**
  _46 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `run_hook` be split into smaller, more focused modules?**
  _Cohesion score 0.12096774193548387 - nodes in this community are weakly interconnected._
- **Should `Working log — 2026-07-27` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._
- **Should `TDQ Conventions` be split into smaller, more focused modules?**
  _Cohesion score 0.09090909090909091 - nodes in this community are weakly interconnected._