# Graph Report - TDQWorkflow  (2026-07-30)

## Corpus Check
- 161 files · ~109,011 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1574 nodes · 2363 edges · 114 communities (101 shown, 13 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 10 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `15d3dc6e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- run_hook
- tdq_state.py
- write_state
- good_report
- write_file
- 2. Thay đổi theo file
- PLAN — TDQ 0.3.0 (instruction-hardening-7b)
- _common.py
- .write
- SPEC — Yêu cầu mới ⇒ state được đồng bộ lại theo lane user chọn
- TestState
- helper.py
- InventoryBase
- doc_lint.py
- Working log — 2026-07-28
- .run_cli
- properties
- Spec: TDQWorkflow Plugin cho Claude Code
- 2. Đầu ra cụ thể
- TestPromptContext
- TestEditGate
- ModelsBase
- external_task.py
- plugin_tiers.py
- SkillShapeTest
- SPEC — Vá điểm mù của verify-by-effect (sổ turn chỉ thấy Edit/Write)
- skill_inventory.py
- TestBashGate
- Changelog
- PLAN — Kiểm kê & tận dụng skill phụ trợ (0.3.3)
- Working log — 2026-07-27
- Working log 2026-07-29
- Bảng phase TDQ (tự sinh — KHÔNG sửa tay)
- external_models.py
- Vòng interview
- Working log — 2026-07-30
- PLAN — Vá điểm mù verify-by-effect (0.3.1)
- SPEC — Kiểm kê & tận dụng skill phụ trợ (tdq-workflow 0.3.3)
- SPEC — Tối ưu bộ plugin user-level: tier hoá, lazy-load, viết lại §10 (v1.0)
- AGENTS.md
- TDQ Workflow — bản portable (agent nào cũng chạy được)
- Bảng phase TDQ (tự sinh — KHÔNG sửa tay)
- Ghi nhận duyệt
- tdq-conventions/SKILL.md
- TDQ Conventions
- doc
- Plan — TDQWorkflow Plugin v0.1
- REPORT — Instruction hardening cho model yếu (tdq-workflow 0.3.0)
- 04-build.md
- Kiểm kê năng lực (bước B0)
- tdq-workflow — Plugin Claude Code
- Đợt 1 (21:13) — khả thi tổng quát
- Hướng dẫn tự cài tdq-workflow ở user-level (thủ công)
- PLAN — Vá chặn oan do vân tay repo (0.3.2)
- PLAN — Tối ưu bộ plugin user-level: tier hoá + lazy-load (HOÀN THÀNH — QC PASS 9/9, 14:58)
- Bằng chứng
- QC — Vá điểm mù verify-by-effect (0.3.1)
- REPORT — Kiểm kê & tận dụng skill phụ trợ (tdq-workflow 0.3.3)
- REPORT — Vá điểm mù verify-by-effect (tdq-workflow 0.3.1)
- Kiểm kê năng lực (bước B0)
- SPEC — Mode implement "external": giao task cho Codex/Antigravity qua worktree
- TurnLedgerTest
- Report — TDQWorkflow Plugin v0.1.0 — 2026-07-27
- Bằng chứng
- QC — Tối ưu plugin user-level: tier hoá + lazy-load
- REPORT — Vá chặn oan do vân tay repo (tdq-workflow 0.3.2)
- REPORT — Tối ưu bộ plugin user-level: tier hoá + lazy-load
- Request: Claude tự quyết implement mode, không hỏi user
- Request: state phải luôn nằm ở project root (chống "state bóng")
- 03-plan.md
- add
- add
- KNOWLEDGE — Tối ưu plugin user-level + lazy-load
- QC — Kiểm kê & tận dụng skill phụ trợ (0.3.3)
- REQUEST — Kiểm kê & tận dụng skill phụ trợ
- RESEARCH — Tối ưu plugin user-level + lazy-load
- REQUEST — Fix chặn oan `[TDQ:LOG]` khi log ghi qua shell
- REQUEST — Tối ưu bộ plugin user-level theo ranking + lazy-load
- 04 — Build: Implement → QC → Report
- QC — kiểm chất lượng
- TDQ Build — Implement → QC → Report
- Chọn lane: quick hay full
- QC — Smoke e2e (E1) — 2026-07-27
- TDQ STATE (tự sinh — không sửa tay)
- 01-intake.md
- Ghi nhận duyệt
- Mã nhắc của hook
- Khuôn plan
- QUESTIONS — Tối ưu plugin user-level + lazy-load
- tdq-build/references/report-template.md
- tdq-spec/references/spec-template.md
- skill-budget.md
- token-budget.md
- v0.1/README.md
- portable/README.md
- KNOWLEDGE — external-agent-mode
- test_portable_sync.py
- PLAN — Mode implement "external" (Codex/Antigravity qua worktree) — HOÀN THÀNH (mode main, 2026-07-30 23:10; Q9 PENDING chờ user cài plugin codex)
- QC — Mode implement "external" (Codex/Antigravity qua worktree)
- REPORT — Mode implement "external" (Codex/Antigravity qua worktree)
- QUESTIONS — external-agent-mode
- REQUEST — Fix agy không tạo file (--add-dir) + Claude tự bắt kết quả agent
- REQUEST — Mode giao việc cho agent ngoài (codex/antigravity) trong TDQ workflow
- Mã nhắc của hook
- TDQ Intake — mở request & phân tích
- TDQ Plan
- REQUEST — Sample Socket.IO chat để test mode external (codex + agy)
- E2E-AGY.task.md
- E2E-CODEX.task.md
- S1.task.md
- S2.task.md

## God Nodes (most connected - your core abstractions)
1. `run_hook()` - 36 edges
2. `write_state()` - 34 edges
3. `TestState` - 24 edges
4. `Working log — 2026-07-30` - 23 edges
5. `Working log — 2026-07-28` - 22 edges
6. `run_state_cli()` - 22 edges
7. `write_file()` - 22 edges
8. `ProtocolTest` - 20 edges
9. `TestEditGate` - 19 edges
10. `load_fixture()` - 18 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `today_log_rel()`  [INFERRED]
  hooks/scripts/edit_gate.py → scripts/tdq_state.py
- `main()` --calls--> `read_payload()`  [EXTRACTED]
  hooks/scripts/bash_gate.py → hooks/scripts/_common.py
- `main()` --calls--> `read_payload()`  [EXTRACTED]
  hooks/scripts/edit_gate.py → hooks/scripts/_common.py
- `main()` --calls--> `read_payload()`  [EXTRACTED]
  hooks/scripts/prompt_context.py → hooks/scripts/_common.py
- `main()` --calls--> `read_payload()`  [EXTRACTED]
  hooks/scripts/session_start.py → hooks/scripts/_common.py

## Import Cycles
- None detected.

## Communities (114 total, 13 thin omitted)

### Community 0 - "run_hook"
Cohesion: 0.06
Nodes (24): decision(), load_fixture(), Parse PreToolUse hook stdout -> (permissionDecision, additionalContext).      0., read_state(), run_hook(), B3 — bash_gate.py: NHẮC (allow + additionalContext) về quy ước git và state.json, ProtocolTest, P2 — giao thức tuân thủ: nhắc có mã, quan sát hiệu ứng, đối chiếu ở Stop.  Nguyê (+16 more)

### Community 1 - "tdq_state.py"
Cohesion: 0.07
Nodes (62): _atomic_write(), cli(), _cli_approve(), default_state(), effective_lane(), effective_mode(), effective_phase(), _fail() (+54 more)

### Community 2 - "write_state"
Cohesion: 0.10
Nodes (22): write_state(), stop_gate.py (0.3.0) — đối chiếu lời nhắc với hiệu ứng thật trong sổ turn.  Điểm, P3 (0.3.1) — hiệu ứng THẬT trên đĩa, không chỉ tin sổ turn.      Sổ turn chỉ ghi, Giả lập prompt_context: chụp trạng thái đĩa lúc mở turn., Bug gốc: log append bằng shell → không có `log_written` → chặn oan., Log hôm nay chưa tồn tại đầu turn, được tạo bằng shell trong turn., Có ảnh chụp nhưng log KHÔNG đổi → vẫn phải chặn., Không phải git repo → repo_sha None, nhưng chiều log vẫn vá được. (+14 more)

### Community 3 - "good_report"
Cohesion: 0.09
Nodes (15): FailTest, good_report(), LogTest, ParsePlanTest, Test external_task.py — lõi mode external (stub binary, không mạng)., Dựng stub binary codex/agy trong PATH + worktree/cwd tạm., -> [khối args của từng lần gọi] (prompt nhiều dòng nằm trọn trong khối)., Khuôn gói task (skills/tdq-build/references/external-task.md) đủ mục và     ví d (+7 more)

### Community 4 - "write_file"
Cohesion: 0.07
Nodes (18): write_file(), BookkeepingExclusionTest, git(), P1 — ảnh chụp trạng thái đầu turn (spec 0.3.1 §4 S3).  Hai helper này là nền của, Sổ sách đã commit rồi sửa tiếp → phải lọt qua cả pathspec của `diff HEAD`., 0.3.2 — dấu của file untracked phải theo NỘI DUNG, không theo mtime., `touch`/ghi đè y hệt byte (formatter, build tool) không phải là thay đổi., Quá trần đọc thì vẫn phải có dấu (size), không được bỏ trắng. (+10 more)

### Community 5 - "2. Thay đổi theo file"
Cohesion: 0.05
Nodes (38): Definition of Done, Nguyên tắc thực thi, Phase 1 — CLI ghi nhận duyệt, Phase 2 — Hook chỉ còn nhắc, Phase 3 — Skills & tài liệu, Phase 4 — Nghiệm thu & đóng gói, PLAN — TDQ 0.2.0: hard gate → nhắc nhở, duyệt bằng chat tự nhiên, 1. Unit / e2e (+30 more)

### Community 6 - "PLAN — TDQ 0.3.0 (instruction-hardening-7b)"
Cohesion: 0.05
Nodes (36): 1. Vấn đề cốt lõi, 2. Quyết định đã chốt, 3. Tiêu chí "model yếu đọc cũng làm đúng" (lint sẽ chấm), 4. Đánh đổi đã biết, 5. Chưa quyết (không chặn spec), KNOWLEDGE — instruction-hardening-7b (chốt trước khi viết spec), Definition of Done, P1 — CLI `scripts/tdq_state.py`: state file, mirror, PHASE_TABLE, next, get (+28 more)

### Community 7 - "_common.py"
Cohesion: 0.12
Nodes (33): _clean(), main(), already_reminded(), approve_hint(), echo_line(), observe(), payload_cwd(), Helper dùng chung cho hook TDQ (chỉ stdlib).  Giao thức tuân thủ 0.3.0 (spec §2. (+25 more)

### Community 8 - ".write"
Cohesion: 0.12
Nodes (10): DocLintTest, LintBase, PairTest, R8Test, P5 — mỗi rule của scripts/doc_lint.py có 1 fixture bẩn + 1 fixture sạch.  Lint l, R8 chỉ soi file nằm trong thư mục tên `spec/`., Spec viết trước 0.3.3: 1 dòng allow ở bất kỳ đâu miễn cả rule cho file đó., --pair <spec> <plan>: mỗi DÙNG ở §3b phải có khối hợp đồng đủ 6 trường. (+2 more)

### Community 9 - "SPEC — Yêu cầu mới ⇒ state được đồng bộ lại theo lane user chọn"
Cohesion: 0.05
Nodes (33): Definition of Done, Nguyên tắc thực thi, Phase 1 — Core state (nền cho mọi thứ còn lại), Phase 2 — Lưới an toàn không trượt vì transcript trễ, Phase 3 — Nhắc & chỉ dẫn, Phase 4 — Đóng gói & nghiệm thu, PLAN — Yêu cầu mới ⇒ state được đồng bộ lại theo lane user chọn (0.1.7), Edge case đã kiểm (+25 more)

### Community 10 - "TestState"
Cohesion: 0.06
Nodes (4): A3 — tdq_state.py: default schema, CLI, protected keys, atomic write., State phải luôn về MỘT file ở project root — chạy CLI từ thư mục con     không đ, TestProjectRootResolution, TestState

### Community 11 - "helper.py"
Cohesion: 0.06
Nodes (16): Shared test utilities: run hook scripts as subprocesses with stdin JSON., Chạy CLI với process cwd = cwd và KHÔNG set TDQ_PROJECT_DIR (giống user     gõ l, run_state_cli(), run_state_cli_in(), DocsConsistencyTest, P6 — doc không được mô tả hành vi mà 0.3.0 đã bỏ.  Doc nói "hook chặn" trong khi, relevant_files(), NextTest (+8 more)

### Community 12 - "InventoryBase"
Cohesion: 0.12
Nodes (16): CliTest, InventoryBase, LogServiceTest, PluginTest, P1 (0.3.3) — scripts/skill_inventory.py: kiểm kê skill trên đĩa.  Script là nửa, Tầng project đè tầng user: user bật + project tắt → không liệt kê., settings.local.json bật được plugin mà tầng user không nhắc tới., Entry scope=project của PROJECT KHÁC không được lọt vào bảng. (+8 more)

### Community 13 - "doc_lint.py"
Cohesion: 0.09
Nodes (30): collect(), Doc, lint_file(), main(), pair(), _plan_contracts(), Lệnh phải copy-paste được: trong khối ```, trong inline-code, hoặc ô bảng., SKILL.md và file phase portable phải nói rõ khi nào xong và đi đâu tiếp. (+22 more)

### Community 14 - "Working log — 2026-07-28"
Cohesion: 0.06
Nodes (30): ~00:30 — Detect bug approve_gate không ghi state (báo từ project insightfaceserverv2), ~00:35 — Implement fix approve_gate matcher (user đã gõ lệnh duyệt quick; hook duyệt fail im lặng do chính bug này — live repro), ~00:45 — Setup test live sau restart (user yêu cầu verify fix), ~00:45 — Verify live PASS + dọn test, ~09:04 — Request `fix-implement-mode-gate` (lane quick, ĐÃ DUYỆT), ~09:20 — Mở request `2026-07-28-fix-invite-without-request` (lane quick, CHỜ DUYỆT), ~09:25 — Đóng turn: graphify + dọn, ~09:30 — Commit (user duyệt "okay commit") (+22 more)

### Community 15 - ".run_cli"
Cohesion: 0.13
Nodes (8): BrokenInputTest, EnableTest, IdempotentTest, LogTest, Test cho scripts/plugin_tiers.py — HOME giả trong tmpdir., ResetTest, StatusTest, TierBase

### Community 16 - "properties"
Cohesion: 0.07
Nodes (29): blocked, done, files_changed, notes, status, task_id, test_cmd, test_result (+21 more)

### Community 17 - "Spec: TDQWorkflow Plugin cho Claude Code"
Cohesion: 0.07
Nodes (27): 10. QC / test / validate cho chính plugin (checklist rule 9), 11. Deliverables (Expect_Output), 12. Giới hạn & rủi ro (minh bạch), 1. Ý tưởng & mục tiêu, 2.1 Trong scope (MVP), 2.2 Ngoài scope (MVP), 2. Scope, 3.1 Lazy load & ngân sách token (bắt buộc) (+19 more)

### Community 18 - "2. Đầu ra cụ thể"
Cohesion: 0.07
Nodes (27): 1.1 Mục tiêu, 1.2 In-scope, 1.3 Out-of-scope, 1. Mục tiêu & phạm vi, 2.10 Dọn dẹp gộp vào, 2.11 Cập nhật `~/.claude/CLAUDE.md` §10, 2.1 Giao thức tuân thủ: nhắc có mã → quan sát hiệu ứng → đối chiếu cuối turn, 2.2 CLI: `next` và `get <key>` (+19 more)

### Community 19 - "TestPromptContext"
Cohesion: 0.15
Nodes (5): now_iso(), session_start.py + prompt_context.py (0.3.0) — bơm context theo state., Trần 600 ký tự không được cắt mất dòng luật hay dòng lệnh., TestPromptContext, TestSessionStart

### Community 20 - "TestEditGate"
Cohesion: 0.20
Nodes (4): now_iso(), edit_gate.py (0.3.0) — quan sát vào sổ turn + nhắc; không bao giờ chặn., TestEditGate, today_log_rel()

### Community 21 - "ModelsBase"
Cohesion: 0.22
Nodes (4): AgyListTest, CodexProbeTest, ModelsBase, Test external_models.py — list model available thật (stub binary, không mạng).

### Community 22 - "external_task.py"
Cohesion: 0.22
Nodes (16): build_command(), _extract_json(), _log(), _log_enabled(), main(), _now(), parse_plan(), -> (argv, cwd). Flag đúng theo spec §3 — một chỗ duy nhất định nghĩa lệnh. (+8 more)

### Community 23 - "plugin_tiers.py"
Cohesion: 0.34
Nodes (16): _claude_dir(), cmd_enable(), cmd_reset(), cmd_status(), _key_for(), _load_json(), _log(), _log_on() (+8 more)

### Community 24 - "SkillShapeTest"
Cohesion: 0.22
Nodes (4): P3 — hình dạng bắt buộc của 6 skill sau khi gộp 9 → 5 (+conventions).  Mục tiêu:, SKILL.md của conventions phải trỏ tới doc phase tự sinh, không chép tay., read(), SkillShapeTest

### Community 25 - "SPEC — Vá điểm mù của verify-by-effect (sổ turn chỉ thấy Edit/Write)"
Cohesion: 0.12
Nodes (15): 1. Bối cảnh & triệu chứng, 2. Nguyên nhân gốc, 3. Các phương án đã cân nhắc, 4. Thiết kế, 5. Ngoài phạm vi, 6. Phạm vi test (mỗi task 1 test, red → green), 7. Definition of Done, 8. Rủi ro & giảm thiểu (+7 more)

### Community 26 - "skill_inventory.py"
Cohesion: 0.19
Nodes (15): _clean(), _enabled_plugins(), _frontmatter(), inventory(), _load_json(), main(), _plugin_skill_dirs(), [(name, desc≤60, nguồn)] — trùng tên thì nguồn quét trước thắng. (+7 more)

### Community 28 - "Changelog"
Cohesion: 0.17
Nodes (14): 0.1.0 — 2026-07-27, 0.1.4 — 2026-07-28, 0.1.6 — 2026-07-28, 0.2.0 — 2026-07-28, 0.3.0 — 2026-07-29, 0.3.1 — 2026-07-29, 0.3.2 — 2026-07-29, 0.3.3 — 2026-07-29 (+6 more)

### Community 29 - "PLAN — Kiểm kê & tận dụng skill phụ trợ (0.3.3)"
Cohesion: 0.13
Nodes (14): Definition of Done, Năng lực → task, P1 — `scripts/skill_inventory.py` + test, P2 — Bước B0 trong `tdq-intake`, P3 — Khuôn spec §3b + hợp đồng 6 trường ở plan, P4 — `doc_lint.py`: R8 + `--pair`, P5 — `tdq-build` thi hành hợp đồng, P6 — `PHASE_TABLE` + `phases.md` (+6 more)

### Community 30 - "Working log — 2026-07-27"
Cohesion: 0.13
Nodes (14): ~16:30 — Lập spec cho TDQWorkflow plugin, ~16:50 — Đổi đường dẫn working log theo yêu cầu người dùng, ~17:10 — Bổ sung quy tắc khai thác Tavily vào spec, ~17:25 — Check lazy load, bổ sung mục 3.1 vào spec, ~17:35 — Approve gate luôn hướng dẫn user lệnh duyệt, ~17:50 — Approve validate bằng state + detail file; vá lỗ hổng state.json, ~18:05 — Lane quick có cửa duyệt nhẹ + ghi summary plan vào working log trước implement, ~18:20 — User duyệt spec v0.1.6; lập plan (+6 more)

### Community 31 - "Working log 2026-07-29"
Cohesion: 0.13
Nodes (14): ~00:05 — User duyệt spec 0.3.0 → viết plan, ~01:00–01:40 — Implement plan 0.3.0 end-to-end (P3 → P8), ~02:10 — Phân tích + viết spec fix điểm mù verify-by-effect, ~02:30 — User duyệt spec → viết plan, ~02:45–03:30 — Implement plan 0.3.1 end-to-end (mode main), ~04:00 — Audit toàn bộ tdq-workflow 0.3.1 (theo yêu cầu user), ~04:15 — User duyệt fix 0.3.2 → plan, ~04:20–05:00 — Implement 0.3.2 end-to-end (mode main) (+6 more)

### Community 32 - "Bảng phase TDQ (tự sinh — KHÔNG sửa tay)"
Cohesion: 0.14
Nodes (12): analyze, Bảng phase TDQ (tự sinh — KHÔNG sửa tay), idle, implement, no_state, plan, qc, quick (+4 more)

### Community 33 - "external_models.py"
Cohesion: 0.41
Nodes (11): _cache_path(), _candidates(), list_agy(), list_codex(), _log(), main(), _now(), _probe_codex() (+3 more)

### Community 34 - "Vòng interview"
Cohesion: 0.33
Nodes (5): Ghi lại, Hỏi cái gì, Hỏi thế nào, Khi nào dừng, Vòng interview

### Community 35 - "Working log — 2026-07-30"
Cohesion: 0.08
Nodes (23): ~00:05–08:38 — Tổng kiểm workflow + audit 43 plugin (chỉ đọc/phân tích), 11:07 — Mở request mới: tối ưu plugin user-level + lazy-load (tdq-intake Phần A), 12:05 — Analyze request plugin-lazy-load (lane full), 12:3x — Đóng interview vòng 1, chốt knowledge, phase=spec, 14:16 — Viết spec plugin-lazy-load v1.0 (phase spec), 14:24 — Spec được duyệt, 14:25 — Viết plan plugin-lazy-load (phase plan), 14:46–15:00 — Implement end-to-end request plugin-lazy-load (mode main) + QC + report (+15 more)

### Community 36 - "PLAN — Vá điểm mù verify-by-effect (0.3.1)"
Cohesion: 0.20
Nodes (9): Definition of Done, P1 — Helper trong `scripts/tdq_state.py`, P2 — Ghi ảnh chụp đầu turn (`hooks/scripts/prompt_context.py`), P3 — Đối chiếu cuối turn (`hooks/scripts/stop_gate.py`), P4 — Doc & đóng gói 0.3.1, P5 — QC & report, PLAN — Vá điểm mù verify-by-effect (0.3.1), Task phát sinh từ QC (+1 more)

### Community 37 - "SPEC — Kiểm kê & tận dụng skill phụ trợ (tdq-workflow 0.3.3)"
Cohesion: 0.20
Nodes (9): 1. Mục tiêu & phạm vi, 2. Đầu ra cụ thể, 3. Cách tiếp cận & lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. QC & Definition of Done, 7. Câu hỏi còn mở (+1 more)

### Community 38 - "SPEC — Tối ưu bộ plugin user-level: tier hoá, lazy-load, viết lại §10 (v1.0)"
Cohesion: 0.20
Nodes (9): 1. Mục tiêu & phạm vi, 2. Đầu ra đo đếm được, 3. Cách tiếp cận + lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. Phạm vi QC & Definition of Done, 7. Câu hỏi còn mở (+1 more)

### Community 39 - "AGENTS.md"
Cohesion: 0.22
Nodes (4): 02 — Spec, Các bước, Khuôn spec, Kiểm trước khi trình

### Community 40 - "TDQ Workflow — bản portable (agent nào cũng chạy được)"
Cohesion: 0.20
Nodes (10): Chất lượng, Cây tài liệu, Ghi nhận duyệt, Giao thức một turn (bắt buộc, đúng thứ tự), Git, Pipeline, Research, State (+2 more)

### Community 41 - "Bảng phase TDQ (tự sinh — KHÔNG sửa tay)"
Cohesion: 0.20
Nodes (10): analyze, Bảng phase TDQ (tự sinh — KHÔNG sửa tay), idle, implement, no_state, plan, qc, quick (+2 more)

### Community 42 - "Ghi nhận duyệt"
Cohesion: 0.50
Nodes (4): Ghi nhận duyệt, KHÔNG phải câu duyệt (phản ví dụ), Là câu duyệt khi có ĐỦ hai phần, Lệnh phải chạy NGAY khi nhận ra

### Community 43 - "tdq-conventions/SKILL.md"
Cohesion: 0.31
Nodes (3): Khuôn gói task cho engine ngoài (mode external), Các bước, TDQ Spec

### Community 44 - "TDQ Conventions"
Cohesion: 0.20
Nodes (10): 1. Giao thức một turn (bắt buộc, làm đúng thứ tự), 2. Bảng phase, 3. State, 4. Ghi nhận duyệt, 5. Cây tài liệu, 6. Working log, 7. Git, 8. Research (+2 more)

### Community 45 - "doc"
Cohesion: 0.22
Nodes (9): doc, Expect_Output, git & worktree, Graphify, Phong cách trình bày, quy tắc chung, Research & độ tin cậy thông tin, workflow (+1 more)

### Community 46 - "Plan — TDQWorkflow Plugin v0.1"
Cohesion: 0.22
Nodes (8): Definition of Done (theo spec mục 10), Nguyên tắc thực thi, Phase A — Nền móng, Phase B — Hooks + unit test (red/green từng script), Phase C — Skills (10), Phase D — Agents, Phase E — QC tổng + tài liệu, Plan — TDQWorkflow Plugin v0.1

### Community 47 - "REPORT — Instruction hardening cho model yếu (tdq-workflow 0.3.0)"
Cohesion: 0.22
Nodes (8): Cách chạy / cách kiểm, Giới hạn còn lại, Kết quả QC, Quyết định đáng chú ý, REPORT — Instruction hardening cho model yếu (tdq-workflow 0.3.0), Ánh xạ tên skill cũ → mới, Đã làm gì, Đầu ra

### Community 48 - "04-build.md"
Cohesion: 0.22
Nodes (6): Chạy cái gì, Ghi kết quả, Khi FAIL, QC — kiểm chất lượng, Khuôn report, Kiểm trước khi trình

### Community 49 - "Kiểm kê năng lực (bước B0)"
Cohesion: 0.22
Nodes (9): 4 lý do loại (đóng — cấm tự chế lý do khác), Agent ngoài (không có skill system), Bảng quá dài, Các bước, Khuôn bảng (copy nguyên khối rồi điền), Kiểm kê năng lực (bước B0), Lane quick, Luật điền ô "Phán quyết" (+1 more)

### Community 50 - "tdq-workflow — Plugin Claude Code"
Cohesion: 0.22
Nodes (8): Cài đặt (chỉ trong repo/project), Cách hook điều khiển agent, Cấu trúc, Duyệt bằng chat thường, Dùng hằng ngày, Pipeline, Quy ước cứng, tdq-workflow — Plugin Claude Code

### Community 51 - "Đợt 1 (21:13) — khả thi tổng quát"
Cohesion: 0.17
Nodes (11): Q1: "use OpenAI Codex CLI as subagent inside Claude Code delegate tasks", Q2: "codex exec non-interactive headless", Q3: "Google Antigravity CLI headless", Q4: "codex mcp-server Claude Code", Q5: cách cài codex-plugin-cc, Q6: model slug Codex hiện hành, Q7: thiết kế prompt cho model cấp thấp/context ngắn, RESEARCH — external-agent-mode (+3 more)

### Community 52 - "Hướng dẫn tự cài tdq-workflow ở user-level (thủ công)"
Cohesion: 0.25
Nodes (7): 1. Cài qua local marketplace, 2. Đồng bộ rule working log ở `~/.claude/CLAUDE.md`, 3. Thêm instruction TDQ cho MỌI task vào `~/.claude/CLAUDE.md`, 4. Dùng ngoài Claude Code, 5. Gỡ, Hướng dẫn tự cài tdq-workflow ở user-level (thủ công), Lưu ý an toàn

### Community 53 - "PLAN — Vá chặn oan do vân tay repo (0.3.2)"
Cohesion: 0.25
Nodes (7): Ngoài phạm vi (đã nêu lý do trong chat), P1 — `scripts/tdq_state.py`: vân tay chỉ tính file "thật", P2 — `hooks/scripts/stop_gate.py`, P3 — Log service (D), P4 — Doc & đóng gói 0.3.2, P5 — QC & report, PLAN — Vá chặn oan do vân tay repo (0.3.2)

### Community 54 - "PLAN — Tối ưu bộ plugin user-level: tier hoá + lazy-load (HOÀN THÀNH — QC PASS 9/9, 14:58)"
Cohesion: 0.25
Nodes (7): Definition of Done, Năng lực → task, P1 — Script `plugin_tiers.py` + test (trong repo, red → green từng task), P2 — Cài user-level, P3 — `~/.claude/CLAUDE.md`, P4 — QC & đóng, PLAN — Tối ưu bộ plugin user-level: tier hoá + lazy-load (HOÀN THÀNH — QC PASS 9/9, 14:58)

### Community 55 - "Bằng chứng"
Cohesion: 0.25
Nodes (7): Bằng chứng, Không sửa (có chủ ý), Kết luận, Q7 — ba kịch bản audit, dựng lại nguyên trạng (bản cài 0.3.2), Q8 — hồi quy 0.3.1, Q9 — git treo quá 2 s, QC — Vá chặn oan do vân tay repo (0.3.2)

### Community 56 - "QC — Vá điểm mù verify-by-effect (0.3.1)"
Cohesion: 0.25
Nodes (7): Bằng chứng, Ghi chú lệch so với spec, Kết luận, Lỗi phát hiện trong QC và đã sửa, Q1, Q10 — smoke trên bản cài user-level 0.3.1 (`TDQ_PROJECT_DIR` đặt riêng từng lệnh), QC — Vá điểm mù verify-by-effect (0.3.1)

### Community 57 - "REPORT — Kiểm kê & tận dụng skill phụ trợ (tdq-workflow 0.3.3)"
Cohesion: 0.25
Nodes (7): Còn chờ user, Kết quả QC, Lệch so với spec (chi tiết + lý do ở file QC), REPORT — Kiểm kê & tận dụng skill phụ trợ (tdq-workflow 0.3.3), Vấn đề, Đã làm gì, Đầu ra

### Community 58 - "REPORT — Vá điểm mù verify-by-effect (tdq-workflow 0.3.1)"
Cohesion: 0.25
Nodes (7): Giới hạn còn lại, Kết quả QC, Quyết định đáng chú ý, REPORT — Vá điểm mù verify-by-effect (tdq-workflow 0.3.1), Vấn đề, Đã làm gì, Đầu ra

### Community 59 - "Kiểm kê năng lực (bước B0)"
Cohesion: 0.22
Nodes (8): 4 lý do loại (đóng — cấm tự chế lý do khác), Bảng quá dài, Các bước, Khuôn bảng (copy nguyên khối rồi điền), Kiểm kê năng lực (bước B0), Lane quick, Luật điền ô "Phán quyết", Số phận từng phán quyết ở các phase sau

### Community 60 - "SPEC — Mode implement "external": giao task cho Codex/Antigravity qua worktree"
Cohesion: 0.20
Nodes (9): 1. Mục tiêu & phạm vi, 2. Đầu ra cụ thể, 3. Cách tiếp cận & lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. QC & Definition of Done, 7. Câu hỏi còn mở (+1 more)

### Community 62 - "Report — TDQWorkflow Plugin v0.1.0 — 2026-07-27"
Cohesion: 0.29
Nodes (6): Cách chạy / test, Kết quả, QC (docs/qc/), Quyết định đáng chú ý & giới hạn, Report — TDQWorkflow Plugin v0.1.0 — 2026-07-27, Đề xuất tiếp theo

### Community 63 - "Bằng chứng"
Cohesion: 0.29
Nodes (6): Bằng chứng, Kết luận, Q1, Q12 — ghi chú lệch nhẹ so với spec, Q9 — smoke trên bản cài user-level (mọi lệnh đặt TDQ_PROJECT_DIR riêng), QC — Instruction hardening cho model yếu (0.3.0)

### Community 64 - "QC — Tối ưu plugin user-level: tier hoá + lazy-load"
Cohesion: 0.29
Nodes (6): Bằng chứng T2.6 — 3 case an toàn chạy tay trên máy thật, Bằng chứng T3.3 — audit CLAUDE.md (skill claude-md-improver), Ghi chú lệch (có chủ ý), Kết luận, QC — Tối ưu plugin user-level: tier hoá + lazy-load, Đối chiếu DoD spec §6 (vòng 1)

### Community 65 - "REPORT — Vá chặn oan do vân tay repo (tdq-workflow 0.3.2)"
Cohesion: 0.29
Nodes (6): Còn lại, Kết quả QC, REPORT — Vá chặn oan do vân tay repo (tdq-workflow 0.3.2), Vấn đề, Đã làm gì, Đầu ra

### Community 66 - "REPORT — Tối ưu bộ plugin user-level: tier hoá + lazy-load"
Cohesion: 0.29
Nodes (6): Còn chờ user, Hợp đồng skill đã thi hành, Kết quả QC — PASS 9/9 vòng 1, REPORT — Tối ưu bộ plugin user-level: tier hoá + lazy-load, Vấn đề, Đã làm gì

### Community 67 - "Request: Claude tự quyết implement mode, không hỏi user"
Cohesion: 0.29
Nodes (6): Bằng chứng thu được, Hướng fix đề xuất, Nguyên nhân (không phải bug code, là lỗ hổng thiết kế 0.1.3), Nguyên văn, Request: Claude tự quyết implement mode, không hỏi user, Unknowns cần user chốt

### Community 68 - "Request: state phải luôn nằm ở project root (chống "state bóng")"
Cohesion: 0.29
Nodes (6): Bằng chứng, Mong muốn, Nguyên nhân, Nguyên văn, Request: state phải luôn nằm ở project root (chống "state bóng"), Ràng buộc

### Community 69 - "03-plan.md"
Cohesion: 0.25
Nodes (6): 03 — Plan, Chốt engine + model (chỉ mode external), Các bước, Dòng `Mode thực thi`, Khuôn plan, Kiểm trước khi trình

### Community 70 - "add"
Cohesion: 0.43
Nodes (3): add(), Sample E2E cho mode external — task E2E-AGY (fallback do orchestrator tự làm)., AddTest

### Community 71 - "add"
Cohesion: 0.43
Nodes (3): add(), Sample module for E2E Codex tests., TestE2ECodex

### Community 72 - "KNOWLEDGE — Tối ưu plugin user-level + lazy-load"
Cohesion: 0.33
Nodes (5): Kiểm cổng, KNOWLEDGE — Tối ưu plugin user-level + lazy-load, Năng lực dùng được, Quyết định đã chốt (interview vòng 1 — xem ../questions/ cùng slug), Sự thật đã chốt (từ research + đo máy)

### Community 73 - "QC — Kiểm kê & tận dụng skill phụ trợ (0.3.3)"
Cohesion: 0.33
Nodes (5): Bằng chứng Q9 — rà bảo mật `scripts/skill_inventory.py`, Ghi chú lệch so với spec (có chủ ý), Kết luận, Lỗi phát hiện trong QC và đã sửa, QC — Kiểm kê & tận dụng skill phụ trợ (0.3.3)

### Community 74 - "REQUEST — Kiểm kê & tận dụng skill phụ trợ"
Cohesion: 0.33
Nodes (5): Chỗ chưa rõ, Cách hiểu đầu tiên, Nguyên văn yêu cầu, REQUEST — Kiểm kê & tận dụng skill phụ trợ, Đã xác minh trước khi viết spec (turn phân tích)

### Community 75 - "RESEARCH — Tối ưu plugin user-level + lazy-load"
Cohesion: 0.33
Nodes (5): RESEARCH — Tối ưu plugin user-level + lazy-load, Số liệu đo tại máy (2026-07-30), Truy vấn 1 — cơ chế enabledPlugins & scope, Truy vấn 2 — chi phí context của plugin/skill, Truy vấn 3 — lệnh quản lý plugin

### Community 76 - "REQUEST — Fix chặn oan `[TDQ:LOG]` khi log ghi qua shell"
Cohesion: 0.40
Nodes (4): Liên quan, Nguyên văn triệu chứng, REQUEST — Fix chặn oan `[TDQ:LOG]` khi log ghi qua shell, Vì sao là lane full

### Community 77 - "REQUEST — Tối ưu bộ plugin user-level theo ranking + lazy-load"
Cohesion: 0.40
Nodes (4): Chỗ chưa rõ (cần phân tích/hỏi), Cách hiểu đầu tiên, Nguyên văn yêu cầu, REQUEST — Tối ưu bộ plugin user-level theo ranking + lazy-load

### Community 78 - "04 — Build: Implement → QC → Report"
Cohesion: 0.33
Nodes (6): 04 — Build: Implement → QC → Report, Luật cứng (áp cho cả ba phase), Nhánh external (Phần A, mode external), Phần A — Implement (phase `implement`), Phần B — QC (phase `qc`), Phần C — Report (phase `report`)

### Community 79 - "QC — kiểm chất lượng"
Cohesion: 0.40
Nodes (4): Chạy cái gì, Ghi kết quả, Khi FAIL, QC — kiểm chất lượng

### Community 80 - "TDQ Build — Implement → QC → Report"
Cohesion: 0.33
Nodes (6): Luật cứng (áp cho cả ba phase), Nhánh external (Phần A, mode external), Phần A — Implement (phase `implement`), Phần B — QC (phase `qc`), Phần C — Report (phase `report`), TDQ Build — Implement → QC → Report

### Community 81 - "Chọn lane: quick hay full"
Cohesion: 0.40
Nodes (4): Bảng quyết, Chọn lane: quick hay full, Khuôn câu hỏi (copy được), Luồng mỗi lane

### Community 82 - "QC — Smoke e2e (E1) — 2026-07-27"
Cohesion: 0.50
Nodes (3): 1. Chain test 2 lane (hook thật, chạy subprocess), 2. Headless CLI thật (`claude -p --plugin-dir .`), QC — Smoke e2e (E1) — 2026-07-27

### Community 83 - "TDQ STATE (tự sinh — không sửa tay)"
Cohesion: 0.50
Nodes (3): TDQ STATE (tự sinh — không sửa tay), Việc tiếp theo, Đang ở đâu

### Community 84 - "01-intake.md"
Cohesion: 0.33
Nodes (4): 01 — Intake: mở request & phân tích, Phần A — Mở request (phase `no_state`), Phần B — Phân tích (phase `analyze`, chỉ lane full), Phần C — Lane quick

### Community 85 - "Ghi nhận duyệt"
Cohesion: 0.50
Nodes (4): Ghi nhận duyệt, KHÔNG phải câu duyệt (phản ví dụ), Là câu duyệt khi có ĐỦ hai phần, Lệnh phải chạy NGAY khi nhận ra

### Community 86 - "Mã nhắc của hook"
Cohesion: 0.50
Nodes (4): Bảng 5 mã (danh sách đóng), Hook nhìn thấy thay đổi bằng cách nào, Mã nhắc của hook, Điểm chặn duy nhất

### Community 87 - "Khuôn plan"
Cohesion: 0.50
Nodes (3): Dòng `Mode thực thi`, Khuôn plan, Kiểm trước khi trình

### Community 96 - "KNOWLEDGE — external-agent-mode"
Cohesion: 0.22
Nodes (8): Kiểm cổng, KNOWLEDGE — external-agent-mode, Nguồn, Năng lực dùng được (B0 — bảng phán quyết), Phương án đã loại, Quyết định đã chốt (8, từ questions cùng slug), Sự thật đã xác minh trên máy, Đính chính 23:45 (sau chẩn đoán sâu, có bằng chứng)

### Community 97 - "test_portable_sync.py"
Cohesion: 0.31
Nodes (5): PortableSyncTest, P4 — bản portable (chạy ngoài Claude Code) phải tồn tại và KHÔNG lệch với skills, Danh sách bước đã chuẩn hoá: bỏ link, bỏ đậm, bỏ đường dẫn riêng của plugin., read(), steps()

### Community 98 - "PLAN — Mode implement "external" (Codex/Antigravity qua worktree) — HOÀN THÀNH (mode main, 2026-07-30 23:10; Q9 PENDING chờ user cài plugin codex)"
Cohesion: 0.25
Nodes (7): Definition of Done, Năng lực → task, P1 — Lõi script + unit test (repo, red → green từng task), P2 — State machine + hooks + doc tự sinh, P3 — Khuôn task + agents + skills + CLAUDE.md, P4 — Cài plugin + chạy thật + QC + đóng, PLAN — Mode implement "external" (Codex/Antigravity qua worktree) — HOÀN THÀNH (mode main, 2026-07-30 23:10; Q9 PENDING chờ user cài plugin codex)

### Community 99 - "QC — Mode implement "external" (Codex/Antigravity qua worktree)"
Cohesion: 0.33
Nodes (5): Bảng DoD Q1–Q9 (T4.5, vòng 1), Bằng chứng T3.7 — audit CLAUDE.md (skill claude-md-improver), Ghi chú sai lệch có chủ đích (vòng 1), QC — Mode implement "external" (Codex/Antigravity qua worktree), Đính chính sau QC (23:45, request fix-agy-adddir-sync-agent)

### Community 100 - "REPORT — Mode implement "external" (Codex/Antigravity qua worktree)"
Cohesion: 0.33
Nodes (5): Kết quả, QC (chi tiết trong file QC), REPORT — Mode implement "external" (Codex/Antigravity qua worktree), Việc user cần làm, Đề xuất tiếp

### Community 101 - "QUESTIONS — external-agent-mode"
Cohesion: 0.40
Nodes (4): Kết vòng interview, QUESTIONS — external-agent-mode, Vòng 1 (21:55) — 4 câu đổi kết quả, Vòng 2 (21:58) — 4 câu chốt nốt

### Community 102 - "REQUEST — Fix agy không tạo file (--add-dir) + Claude tự bắt kết quả agent"
Cohesion: 0.40
Nodes (4): Chẩn đoán (có bằng chứng), Nguyên văn yêu cầu, Phạm vi dự kiến, REQUEST — Fix agy không tạo file (--add-dir) + Claude tự bắt kết quả agent

### Community 103 - "REQUEST — Mode giao việc cho agent ngoài (codex/antigravity) trong TDQ workflow"
Cohesion: 0.50
Nodes (3): Cách hiểu đầu tiên, Nguyên văn yêu cầu, REQUEST — Mode giao việc cho agent ngoài (codex/antigravity) trong TDQ workflow

### Community 104 - "Mã nhắc của hook"
Cohesion: 0.50
Nodes (4): Bảng 5 mã (danh sách đóng), Hook nhìn thấy thay đổi bằng cách nào, Mã nhắc của hook, Điểm chặn duy nhất

### Community 105 - "TDQ Intake — mở request & phân tích"
Cohesion: 0.50
Nodes (4): Phần A — Mở request (phase `no_state`), Phần B — Phân tích (phase `analyze`, chỉ lane full), Phần C — Lane quick, TDQ Intake — mở request & phân tích

### Community 106 - "TDQ Plan"
Cohesion: 0.67
Nodes (3): Chốt engine + model (chỉ mode external), Các bước, TDQ Plan

### Community 109 - "REQUEST — Sample Socket.IO chat để test mode external (codex + agy)"
Cohesion: 0.50
Nodes (3): Cách hiểu đầu tiên, Nguyên văn yêu cầu, REQUEST — Sample Socket.IO chat để test mode external (codex + agy)

## Knowledge Gaps
- **575 isolated node(s):** `~00:05–08:38 — Tổng kiểm workflow + audit 43 plugin (chỉ đọc/phân tích)`, `11:07 — Mở request mới: tối ưu plugin user-level + lazy-load (tdq-intake Phần A)`, `12:05 — Analyze request plugin-lazy-load (lane full)`, `12:3x — Đóng interview vòng 1, chốt knowledge, phase=spec`, `14:16 — Viết spec plugin-lazy-load v1.0 (phase spec)` (+570 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `write_state()` connect `write_state` to `run_hook`, `helper.py`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Why does `write_file()` connect `write_file` to `run_hook`, `helper.py`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Why does `run_state_cli()` connect `helper.py` to `run_hook`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **What connects `~00:05–08:38 — Tổng kiểm workflow + audit 43 plugin (chỉ đọc/phân tích)`, `11:07 — Mở request mới: tối ưu plugin user-level + lazy-load (tdq-intake Phần A)`, `12:05 — Analyze request plugin-lazy-load (lane full)` to the rest of the system?**
  _575 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `run_hook` be split into smaller, more focused modules?**
  _Cohesion score 0.06288448393711552 - nodes in this community are weakly interconnected._
- **Should `tdq_state.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0679563492063492 - nodes in this community are weakly interconnected._
- **Should `write_state` be split into smaller, more focused modules?**
  _Cohesion score 0.09722222222222222 - nodes in this community are weakly interconnected._