# Graph Report - TDQWorkflow  (2026-07-28)

## Corpus Check
- 52 files · ~25,196 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 260 nodes · 423 edges · 16 communities (13 shown, 3 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8e9bc667`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- write_state
- TestApproveGate
- TestStopGateInvite
- TDQ Conventions
- _common.py
- Working log — 2026-07-27
- TestBashGate
- ChainBase
- tdq_state.py
- TestState
- Working log — 2026-07-28
- Hướng dẫn tự cài tdq-workflow ở user-level (thủ công)
- stop_gate.py
- tdq-workflow — Plugin Claude Code
- TDQ Approve (user-only)
- Request: Claude tự quyết implement mode, không hỏi user

## God Nodes (most connected - your core abstractions)
1. `TestApproveGate` - 24 edges
2. `approve()` - 20 edges
3. `write_state()` - 18 edges
4. `TestStopGateInvite` - 16 edges
5. `Working log — 2026-07-27` - 14 edges
6. `TestEditGate` - 14 edges
7. `TestBashGate` - 13 edges
8. `Working log — 2026-07-28` - 11 edges
9. `TestState` - 10 edges
10. `decision()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `read_payload()`  [EXTRACTED]
  hooks/scripts/bash_gate.py → hooks/scripts/_common.py
- `main()` --calls--> `read_payload()`  [EXTRACTED]
  hooks/scripts/edit_gate.py → hooks/scripts/_common.py
- `main()` --calls--> `read_payload()`  [EXTRACTED]
  hooks/scripts/session_start.py → hooks/scripts/_common.py
- `main()` --calls--> `payload_cwd()`  [EXTRACTED]
  hooks/scripts/edit_gate.py → hooks/scripts/_common.py
- `main()` --calls--> `payload_cwd()`  [EXTRACTED]
  hooks/scripts/session_start.py → hooks/scripts/_common.py

## Import Cycles
- None detected.

## Communities (16 total, 3 thin omitted)

### Community 0 - "write_state"
Cohesion: 0.10
Nodes (17): decision(), load_fixture(), Shared test utilities: run hook scripts as subprocesses with stdin JSON., Parse PreToolUse hook stdout -> (permissionDecision, reason)., Minimal Claude Code transcript: one assistant message with text content., run_hook(), write_file(), write_state() (+9 more)

### Community 1 - "TestApproveGate"
Cohesion: 0.15
Nodes (3): approve(), B1 — approve_gate.py: validate by state + registered detail file., TestApproveGate

### Community 2 - "TestStopGateInvite"
Cohesion: 0.13
Nodes (4): B5 — stop_gate.py: block end-of-turn when repo changed but working log stale., Dòng mời duyệt chỉ được phép tới tay user khi state đỡ được nó., TestStopGate, TestStopGateInvite

### Community 3 - "TDQ Conventions"
Cohesion: 0.09
Nodes (19): Doc tree (in the user's project), Git, Language, Quality bars, Research, State, TDQ Conventions, Working log (mandatory) (+11 more)

### Community 4 - "_common.py"
Cohesion: 0.19
Nodes (14): block(), main(), _clean(), main(), approve_hint(), deny(), payload_cwd(), Shared helpers for TDQ hook scripts (stdlib only). (+6 more)

### Community 5 - "Working log — 2026-07-27"
Cohesion: 0.13
Nodes (14): ~16:30 — Lập spec cho TDQWorkflow plugin, ~16:50 — Đổi đường dẫn working log theo yêu cầu người dùng, ~17:10 — Bổ sung quy tắc khai thác Tavily vào spec, ~17:25 — Check lazy load, bổ sung mục 3.1 vào spec, ~17:35 — Approve gate luôn hướng dẫn user lệnh duyệt, ~17:50 — Approve validate bằng state + detail file; vá lỗ hổng state.json, ~18:05 — Lane quick có cửa duyệt nhẹ + ghi summary plan vào working log trước implement, ~18:20 — User duyệt spec v0.1.6; lập plan (+6 more)

### Community 7 - "ChainBase"
Cohesion: 0.27
Nodes (5): ChainBase, E1 — simulated end-to-end hook chains for both lanes (full + quick)., TestFullLaneChain, TestQuickLaneChain, today()

### Community 8 - "tdq_state.py"
Cohesion: 0.30
Nodes (10): cli(), default_state(), _fail(), load(), now_iso(), _parse_value(), Return the state dict, or None if missing/corrupt., Atomic write (temp file + rename). Returns the saved state. (+2 more)

### Community 10 - "Working log — 2026-07-28"
Cohesion: 0.12
Nodes (16): ~00:30 — Detect bug approve_gate không ghi state (báo từ project insightfaceserverv2), ~00:35 — Implement fix approve_gate matcher (user đã gõ lệnh duyệt quick; hook duyệt fail im lặng do chính bug này — live repro), ~00:45 — Setup test live sau restart (user yêu cầu verify fix), ~00:45 — Verify live PASS + dọn test, ~09:04 — Request `fix-implement-mode-gate` (lane quick, ĐÃ DUYỆT), ~09:20 — Mở request `2026-07-28-fix-invite-without-request` (lane quick, CHỜ DUYỆT), ~09:25 — Đóng turn: graphify + dọn, ~09:30 — Commit (user duyệt "okay commit") (+8 more)

### Community 11 - "Hướng dẫn tự cài tdq-workflow ở user-level (thủ công)"
Cohesion: 0.29
Nodes (6): 1. Cài qua local marketplace, 2. Đồng bộ rule working log ở `~/.claude/CLAUDE.md`, 3. Thêm instruction TDQ cho MỌI task vào `~/.claude/CLAUDE.md`, 4. Gỡ, Hướng dẫn tự cài tdq-workflow ở user-level (thủ công), Lưu ý an toàn

### Community 12 - "stop_gate.py"
Cohesion: 0.43
Nodes (6): check_invite(), invite_problem(), last_assistant_text(), main(), Text of the most recent assistant message in the transcript (or '')., Vietnamese reason why this approve invitation cannot be honoured, or None.

### Community 13 - "tdq-workflow — Plugin Claude Code"
Cohesion: 0.29
Nodes (6): Cài đặt (chỉ trong repo/project), Cấu trúc, Dùng hằng ngày, Pipeline, Quy ước cứng, tdq-workflow — Plugin Claude Code

### Community 15 - "Request: Claude tự quyết implement mode, không hỏi user"
Cohesion: 0.29
Nodes (6): Bằng chứng thu được, Hướng fix đề xuất, Nguyên nhân (không phải bug code, là lỗ hổng thiết kế 0.1.3), Nguyên văn, Request: Claude tự quyết implement mode, không hỏi user, Unknowns cần user chốt

## Knowledge Gaps
- **56 isolated node(s):** `Pipeline`, `Cài đặt (chỉ trong repo/project)`, `Dùng hằng ngày`, `Cấu trúc`, `Quy ước cứng` (+51 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What connects `Pipeline`, `Cài đặt (chỉ trong repo/project)`, `Dùng hằng ngày` to the rest of the system?**
  _56 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `write_state` be split into smaller, more focused modules?**
  _Cohesion score 0.09863945578231292 - nodes in this community are weakly interconnected._
- **Should `TestStopGateInvite` be split into smaller, more focused modules?**
  _Cohesion score 0.1282051282051282 - nodes in this community are weakly interconnected._
- **Should `TDQ Conventions` be split into smaller, more focused modules?**
  _Cohesion score 0.09090909090909091 - nodes in this community are weakly interconnected._
- **Should `Working log — 2026-07-27` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._
- **Should `Working log — 2026-07-28` be split into smaller, more focused modules?**
  _Cohesion score 0.11764705882352941 - nodes in this community are weakly interconnected._