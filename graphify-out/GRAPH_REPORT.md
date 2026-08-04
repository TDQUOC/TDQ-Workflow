# Graph Report - TDQWorkflow  (2026-08-04)

## Corpus Check
- 297 files · ~228,363 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2551 nodes · 3610 edges · 236 communities (194 shown, 42 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 10 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `465cf14c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- tdq_state.py
- write_state
- doc_lint.py
- external_task.py
- _common.py
- .write
- write_file
- search_task.py
- 2. Thay đổi theo file
- TestState
- SPEC — Yêu cầu mới ⇒ state được đồng bộ lại theo lane user chọn
- InventoryBase
- TestPromptContext
- _read
- Working log — 2026-07-28
- .run_cli
- StubBase
- Spec: TDQWorkflow Plugin cho Claude Code
- TestBashGate
- test_external_task.py
- Working log — 2026-07-31
- Working log — 2026-07-30
- .set_response
- ProtocolTest
- TestEditGate
- StubBase
- Changelog
- good_report
- ModelsBase
- ._go
- TokenBudgetTest
- StateFileTest
- plugin_tiers.py
- helper.py
- .run_cli
- _run
- .run_cli
- SPEC — Vá điểm mù của verify-by-effect (sổ turn chỉ thấy Edit/Write)
- Working log — 2026-08-02
- skill_inventory.py
- PhaseTableTest
- PLAN — Kiểm kê & tận dụng skill phụ trợ (0.3.3)
- Working log — 2026-07-27
- Working log 2026-07-29
- Deep search hybrid — Phase 1 (scout ∥ agy tổng quát) → Phase 2 (agy đào sâu)
- load_fixture
- test_search_task.py
- PLAN — TDQ 0.3.0 (instruction-hardening-7b)
- PLAN — Search agent "deep search" dùng agy CLI, tích hợp TDQ workflow
- AGENTS.md
- external_models.py
- Bảng phase TDQ (tự sinh — KHÔNG sửa tay)
- run_state_cli
- PLAN — Hybrid deep search 0.6.0 (scout ∥ agy tổng quát → agy đào sâu)
- Đợt 1 (21:13) — khả thi tổng quát
- SkillResolveTest
- SplitTest
- PLAN — Audit tổng thể TDQ workflow 0.6.0 — HOÀN THÀNH
- PLAN — TDQ workflow là default tuyệt đối + bỏ §5 superpower
- QC — 2026-07-31-audit-full-workflow
- SPEC — TDQ 0.3.0: tuân thủ kiểm được, state đọc được, workflow đủ rõ cho mọi model
- 2. Đầu ra cụ thể
- SPEC — TDQ workflow là default tuyệt đối + bỏ mục superpower (mục 5 cũ)
- Working Log — 2026-08-04
- 04-build.md
- Knowledge — 2026-08-03-check-external-assign-flow
- PLAN — Vá điểm mù verify-by-effect (0.3.1)
- PLAN — Đổi thiết kế mode external: giao cả plan 1 lần + phase + verify 3 tầng
- SPEC — Kiểm kê & tận dụng skill phụ trợ (tdq-workflow 0.3.3)
- SPEC — Mode implement "external": giao task cho Codex/Antigravity qua worktree
- SPEC — Tối ưu bộ plugin user-level: tier hoá, lazy-load, viết lại §10 (v1.0)
- SPEC — Search agent "deep search" dùng agy CLI, tích hợp TDQ workflow
- SPEC — Audit tổng thể TDQ workflow 0.6.0 (conflict, edge case, robustness model thấp)
- SPEC — Hybrid deep search: Claude scout ∥ agy tổng quát → agy đào sâu
- SPEC — Đổi thiết kế mode external: giao cả plan 1 lần + fix loop
- SPEC — Bộ công cụ export cấu hình Claude Code sang máy khác
- TDQ Workflow — bản portable (agent nào cũng chạy được)
- Bảng phase TDQ (tự sinh — KHÔNG sửa tay)
- workflow/references/approval.md
- TDQ Conventions
- test_portable_sync.py
- INSTRUCTIONS — Dựng bundle export cấu hình Claude Code
- doc
- Plan — TDQWorkflow Plugin v0.1
- KNOWLEDGE — external-agent-mode
- PLAN — Bộ công cụ export cấu hình Claude Code sang máy khác
- REPORT — Instruction hardening cho model yếu (tdq-workflow 0.3.0)
- REPORT — Audit toàn diện tdq-workflow 0.6.0
- REPORT — Đổi thiết kế mode external: giao cả plan / theo phase
- REPORT — Bộ công cụ export cấu hình Claude Code sang máy khác
- Working log 2026-08-03
- Kiểm kê năng lực (bước B0)
- tdq-workflow — Plugin Claude Code
- tdq-intake/SKILL.md
- Kiểm kê năng lực (bước B0)
- DocsConsistencyTest
- {{BUNDLE_NAME}} — Claude Code setup export
- Hướng dẫn tự cài tdq-workflow ở user-level (thủ công)
- KNOWLEDGE — Search agent dùng agy cho advanced search (2026-07-31)
- Knowledge — 2026-07-31-hybrid-deep-search
- KNOWLEDGE — 2026-08-02-tdq-default-cleanup
- PLAN — Vá chặn oan do vân tay repo (0.3.2)
- PLAN — Mode implement "external" (Codex/Antigravity qua worktree) — HOÀN THÀNH (mode main, 2026-07-30 23:10; Q9 PENDING chờ user cài plugin codex)
- PLAN — Tối ưu bộ plugin user-level: tier hoá + lazy-load (HOÀN THÀNH — QC PASS 9/9, 14:58)
- Bằng chứng
- QC — Vá điểm mù verify-by-effect (0.3.1)
- REPORT — Kiểm kê & tận dụng skill phụ trợ (tdq-workflow 0.3.3)
- REPORT — Vá điểm mù verify-by-effect (tdq-workflow 0.3.1)
- Research: 2026-08-04-export-claude-setup
- Brief deep search — LLM local tham số thấp làm engine code-agent (2026-07-31)
- ._run_with
- SearchScoutAgentTest
- TurnStartRowTest
- TurnLedgerTest
- Report — TDQWorkflow Plugin v0.1.0 — 2026-07-27
- Knowledge — 2026-07-31-audit-full-workflow
- Knowledge: 2026-08-04-export-claude-setup
- Bằng chứng
- QC — Tối ưu plugin user-level: tier hoá + lazy-load
- REPORT — Vá chặn oan do vân tay repo (tdq-workflow 0.3.2)
- REPORT — Tối ưu bộ plugin user-level: tier hoá + lazy-load
- Request: Claude tự quyết implement mode, không hỏi user
- Request: state phải luôn nằm ở project root (chống "state bóng")
- RESEARCH — Search agent dùng agy (2026-07-31)
- Brief deep search — LLM local tham số thấp làm engine code-agent (2026-07-31)
- BRIEF — Vector database chạy local cho RAG (2026)
- add
- add
- CheckPacketSkillsTest
- FixRoundsTest
- KNOWLEDGE — instruction-hardening-7b (chốt trước khi viết spec)
- KNOWLEDGE — Tối ưu plugin user-level + lazy-load
- QC — Kiểm kê & tận dụng skill phụ trợ (0.3.3)
- QC — Mode implement "external" (Codex/Antigravity qua worktree)
- QC — TDQ workflow là default tuyệt đối + bỏ mục superpower
- REPORT — Mode implement "external" (Codex/Antigravity qua worktree)
- Report — Hybrid deep search 2 phase (tdq-workflow 0.6.0)
- REQUEST — Hook = remind, bỏ skill tdq-approve, instruction/skills đủ chi tiết cho model yếu (7B)
- REQUEST — Kiểm kê & tận dụng skill phụ trợ
- requests/2026-07-31-hybrid-deep-search.md
- RESEARCH — Instruction/skills đủ chắc để model yếu đi đúng workflow
- RESEARCH — Tối ưu plugin user-level + lazy-load
- Research — 2026-07-31-hybrid-deep-search
- Brief: phiên bản Python 3 mới nhất
- Brief: phiên bản Python 3 mới nhất
- Brief: phiên bản npm mới nhất của 2 package
- Brief: phiên bản Python 3 mới nhất
- BRIEF — Vector database chạy local cho RAG (2026)
- 04 — Build: Implement → QC → Report
- 06 — Deep search hybrid qua search_task.py (agy + search thường)
- Khuôn gói cho engine ngoài (mode external)
- TDQ Build — Implement → QC → Report
- Vòng interview
- BuildCommandTest
- DeepSearchDocTest
- EnvTest
- SearchRunnerAgentTest
- QUESTIONS — Interview request instruction-hardening-7b
- QUESTIONS — external-agent-mode
- QUESTIONS — 2026-08-02-tdq-default-cleanup
- Questions: 2026-08-04-export-claude-setup
- reports/2026-07-31-agy-search-agent.md
- REPORT — TDQ workflow là default tuyệt đối + bỏ mục superpower
- REQUEST — Fix chặn oan `[TDQ:LOG]` khi log ghi qua shell
- REQUEST — Fix agy không tạo file (--add-dir) + Claude tự bắt kết quả agent
- REQUEST — Tối ưu bộ plugin user-level theo ranking + lazy-load
- REQUEST — Search agent dùng agy cho advanced search, tích hợp TDQ workflow
- Research — 2026-07-31-audit-full-workflow
- RESEARCH — 2026-08-02-tdq-default-cleanup
- 2.3 Thiết kế state file
- QC — kiểm chất lượng
- Chọn lane: quick hay full
- SPEC — 2026-08-04-approval-gate-bug
- QC — Smoke e2e (E1) — 2026-07-27
- questions/2026-07-31-agy-search-agent.md
- Questions — 2026-07-31-audit-full-workflow
- Questions — 2026-07-31-hybrid-deep-search
- Questions — 2026-08-03-check-external-assign-flow
- REQUEST — Mode giao việc cho agent ngoài (codex/antigravity) trong TDQ workflow
- REQUEST — Sample Socket.IO chat để test mode external (codex + agy)
- REQUEST — Tự chọn theo đề xuất khi gặp chặn kỹ thuật giữa build
- REQUEST — Check bump version + đồng bộ plugin repo ↔ user-level
- REQUEST — Dòng duyệt plan gợi ý sai mode đã chốt
- Brief — Công nghệ speech-to-text word-level realtime (2026)
- Brief — Công nghệ speech-to-text word-level realtime (2026)
- TDQ STATE (tự sinh — không sửa tay)
- 01 — Intake: mở request & phân tích
- Khuôn plan
- external_report_schema.json
- Ghi nhận duyệt
- Mã nhắc của hook
- TDQ Intake — mở request & phân tích
- Khuôn plan
- QC — 2026-07-31-agy-search-agent
- QC — 2026-07-31-hybrid-deep-search (0.6.0)
- QC — export-claude-setup (2026-08-04)
- QUESTIONS — Tối ưu plugin user-level + lazy-load
- requests/2026-07-31-audit-full-workflow.md
- requests/2026-08-02-tdq-default-cleanup.md
- requests/2026-08-03-check-external-assign-flow.md
- requests/2026-08-04-export-claude-setup.md
- Report — 2026-07-31-failpath-demo (fallback tavily)
- tdq-build/references/report-template.md
- TDQ Plan
- tdq-spec/references/spec-template.md
- EXPORT_LOG.md
- skill-budget.md
- token-budget.md
- v0.1/README.md
- E2E-AGY.task.md
- E2E-CODEX.task.md
- S1.task.md
- S2.task.md
- qc/2026-08-03-check-external-assign-flow.md
- 2026-07-31-local-llm-engine/report.md
- 2026-07-31-npm-versions/report.md
- 2026-07-31-stt-wordlevel-claude/report.md
- 2026-07-31-stt-wordlevel/report.md
- 2026-07-31-trigger-test/report.md
- 2026-07-31-vectordb-local-rag/report.md
- portable/README.md
- Knowledge — 2026-08-04-approval-gate-bug
- PLAN — Sửa lỗi approval-gate (nhắc nhở khi duyệt sai)
- REPORT — Sửa lỗi approval-gate (nhắc nhở khi duyệt sai)
- Research — 2026-08-04-approval-gate-bug
- REQUEST — 2026-08-04-approval-gate-bug
- QC — 2026-08-04-approval-gate-bug
- Questions — 2026-08-04-approval-gate-bug

## God Nodes (most connected - your core abstractions)
1. `write_state()` - 32 edges
2. `good_report()` - 30 edges
3. `TestState` - 26 edges
4. `TestBashGate` - 24 edges
5. `Working log — 2026-07-31` - 24 edges
6. `Working log — 2026-07-30` - 23 edges
7. `Working log — 2026-07-28` - 22 edges
8. `run_state_cli()` - 22 edges
9. `write_file()` - 22 edges
10. `StubBase` - 22 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `today_log_rel()`  [INFERRED]
  hooks/scripts/edit_gate.py → scripts/tdq_state.py
- `main()` --calls--> `plan_mode()`  [EXTRACTED]
  hooks/scripts/prompt_context.py → hooks/scripts/_common.py
- `main()` --calls--> `read_payload()`  [EXTRACTED]
  hooks/scripts/bash_gate.py → hooks/scripts/_common.py
- `main()` --calls--> `read_payload()`  [EXTRACTED]
  hooks/scripts/edit_gate.py → hooks/scripts/_common.py
- `main()` --calls--> `read_payload()`  [EXTRACTED]
  hooks/scripts/prompt_context.py → hooks/scripts/_common.py

## Import Cycles
- None detected.

## Communities (236 total, 42 thin omitted)

### Community 0 - "tdq_state.py"
Cohesion: 0.06
Nodes (64): _atomic_write(), cli(), _cli_approve(), default_state(), effective_lane(), effective_mode(), effective_phase(), _fail() (+56 more)

### Community 1 - "write_state"
Cohesion: 0.10
Nodes (22): write_state(), stop_gate.py (0.3.0) — đối chiếu lời nhắc với hiệu ứng thật trong sổ turn.  Điểm, P3 (0.3.1) — hiệu ứng THẬT trên đĩa, không chỉ tin sổ turn.      Sổ turn chỉ ghi, Giả lập prompt_context: chụp trạng thái đĩa lúc mở turn., Bug gốc: log append bằng shell → không có `log_written` → chặn oan., Log hôm nay chưa tồn tại đầu turn, được tạo bằng shell trong turn., Có ảnh chụp nhưng log KHÔNG đổi → vẫn phải chặn., Không phải git repo → repo_sha None, nhưng chiều log vẫn vá được. (+14 more)

### Community 2 - "doc_lint.py"
Cohesion: 0.06
Nodes (36): collect(), Doc, lint_file(), main(), pair(), _plan_contracts(), Bước trong mục 'Các bước' phải đánh số 1, 2, 3… không nhảy, không lặp., Lệnh phải copy-paste được: trong khối ```, trong inline-code, hoặc ô bảng. (+28 more)

### Community 3 - "external_task.py"
Cohesion: 0.08
Nodes (49): build_command(), check_packet_skills(), count_packet_tasks(), _extract_json(), fix_rounds(), _fix_rounds_path(), _load_fix_rounds(), _log() (+41 more)

### Community 4 - "_common.py"
Cohesion: 0.10
Nodes (41): _check_signal_mismatch(), _clean(), _latest_signal(), main(), Dòng kind="signal" GẦN NHẤT khớp target (duyệt ngược sổ turn)., already_reminded(), approve_hint(), echo_line() (+33 more)

### Community 5 - ".write"
Cohesion: 0.10
Nodes (13): DocLintTest, LintBase, MissingPathTest, PairTest, R8Test, P5 — mỗi rule của scripts/doc_lint.py có 1 fixture bẩn + 1 fixture sạch.  Lint l, R8 chỉ soi file nằm trong thư mục tên `spec/`., Spec viết trước 0.3.3: 1 dòng allow ở bất kỳ đâu miễn cả rule cho file đó. (+5 more)

### Community 6 - "write_file"
Cohesion: 0.07
Nodes (18): write_file(), BookkeepingExclusionTest, git(), P1 — ảnh chụp trạng thái đầu turn (spec 0.3.1 §4 S3).  Hai helper này là nền của, Sổ sách đã commit rồi sửa tiếp → phải lọt qua cả pathspec của `diff HEAD`., 0.3.2 — dấu của file untracked phải theo NỘI DUNG, không theo mtime., `touch`/ghi đè y hệt byte (formatter, build tool) không phải là thay đổi., Quá trần đọc thì vẫn phải có dấu (size), không được bỏ trắng. (+10 more)

### Community 7 - "search_task.py"
Cohesion: 0.08
Nodes (42): _AgentLogger, build_command(), build_search_prompt(), build_url_prompt(), call_agy(), call_with_retry(), cmd_merge(), cmd_run() (+34 more)

### Community 8 - "2. Thay đổi theo file"
Cohesion: 0.05
Nodes (38): Definition of Done, Nguyên tắc thực thi, Phase 1 — CLI ghi nhận duyệt, Phase 2 — Hook chỉ còn nhắc, Phase 3 — Skills & tài liệu, Phase 4 — Nghiệm thu & đóng gói, PLAN — TDQ 0.2.0: hard gate → nhắc nhở, duyệt bằng chat tự nhiên, 1. Unit / e2e (+30 more)

### Community 9 - "TestState"
Cohesion: 0.05
Nodes (6): A3 — tdq_state.py: default schema, CLI, protected keys, atomic write., A6: duyệt quick phải đẩy phase=implement để idle sau đó thành terminal., A18: ts kiểu số/None/thiếu không được crash hook., State phải luôn về MỘT file ở project root — chạy CLI từ thư mục con     không đ, TestProjectRootResolution, TestState

### Community 10 - "SPEC — Yêu cầu mới ⇒ state được đồng bộ lại theo lane user chọn"
Cohesion: 0.05
Nodes (33): Definition of Done, Nguyên tắc thực thi, Phase 1 — Core state (nền cho mọi thứ còn lại), Phase 2 — Lưới an toàn không trượt vì transcript trễ, Phase 3 — Nhắc & chỉ dẫn, Phase 4 — Đóng gói & nghiệm thu, PLAN — Yêu cầu mới ⇒ state được đồng bộ lại theo lane user chọn (0.1.7), Edge case đã kiểm (+25 more)

### Community 11 - "InventoryBase"
Cohesion: 0.11
Nodes (18): CliTest, InventoryBase, LogServiceTest, PluginTest, ProjectDirResolveTest, P1 (0.3.3) — scripts/skill_inventory.py: kiểm kê skill trên đĩa.  Script là nửa, 2 dòng nhắc built-in phải in NGUYÊN VĂN, kể cả khi bảng rỗng., Tầng project đè tầng user: user bật + project tắt → không liệt kê. (+10 more)

### Community 12 - "TestPromptContext"
Cohesion: 0.10
Nodes (7): now_iso(), session_start.py + prompt_context.py (0.3.0) — bơm context theo state., Trần 600 ký tự không được cắt mất dòng luật hay dòng lệnh., A22 — cắt MAX_CHARS không được đứt giữa inline-code (nửa lệnh = lệnh sai)., TestPromptContext, TestSessionStart, TestTruncation

### Community 13 - "_read"
Cohesion: 0.09
Nodes (14): AgentsMdTemplateTest, ExternalTaskTemplateSkillTest, PortableExternalSyncTest, QuickLaneExternalSkillTest, Contract test cho skill docs — request skill-vao-goi-external (P4).  Đối tượng:, T4.4 — tdq-plan SKILL.md + plan-template.md: luật bắt buộc nhãn `(mcp)`     theo, T4.5 — quick external: gói task đơn cũng chép skill (skill-dump);     task quick, T5.1 — portable 03-plan/04-build phải mang cùng luật mới (mcp, split-plan     lu (+6 more)

### Community 14 - "Working log — 2026-07-28"
Cohesion: 0.06
Nodes (30): ~00:30 — Detect bug approve_gate không ghi state (báo từ project insightfaceserverv2), ~00:35 — Implement fix approve_gate matcher (user đã gõ lệnh duyệt quick; hook duyệt fail im lặng do chính bug này — live repro), ~00:45 — Setup test live sau restart (user yêu cầu verify fix), ~00:45 — Verify live PASS + dọn test, ~09:04 — Request `fix-implement-mode-gate` (lane quick, ĐÃ DUYỆT), ~09:20 — Mở request `2026-07-28-fix-invite-without-request` (lane quick, CHỜ DUYỆT), ~09:25 — Đóng turn: graphify + dọn, ~09:30 — Commit (user duyệt "okay commit") (+22 more)

### Community 15 - ".run_cli"
Cohesion: 0.13
Nodes (8): BrokenInputTest, EnableTest, IdempotentTest, LogTest, Test cho scripts/plugin_tiers.py — HOME giả trong tmpdir., ResetTest, StatusTest, TierBase

### Community 16 - "StubBase"
Cohesion: 0.13
Nodes (11): CallTimeoutTest, PreflightTest, Dựng stub binary agy trong PATH + run-dir tạm. Không mạng, không binary thật., Response cho call agy -p thứ n. agy bọc structured_output trong JSON vỏ., T3.2 — validate agy CLI + CẢ hai model slug qua external_models.py., T3.4 — retry ≤2 kèm lỗi cũ, retry dùng slug escalation., T3.6 — call quá TDQ_SEARCH_TIMEOUT bị kill, tính 1 lần fail → retry., T3.7 — run-dir đúng run-id, brief.md copy vào, log per-agent ISO, LOG=0 tắt. (+3 more)

### Community 17 - "Spec: TDQWorkflow Plugin cho Claude Code"
Cohesion: 0.07
Nodes (27): 10. QC / test / validate cho chính plugin (checklist rule 9), 11. Deliverables (Expect_Output), 12. Giới hạn & rủi ro (minh bạch), 1. Ý tưởng & mục tiêu, 2.1 Trong scope (MVP), 2.2 Ngoài scope (MVP), 2. Scope, 3.1 Lazy load & ngân sách token (bắt buộc) (+19 more)

### Community 19 - "test_external_task.py"
Cohesion: 0.08
Nodes (11): ParseDungLinesTest, PlanTimeoutTest, Test external_task.py — lõi mode external (stub binary, không mạng)., T1.2/Q7 — timeout theo số task trong gói: 540×n, trần 3600, env thắng., Khuôn gói task (skills/tdq-build/references/external-task.md) đủ mục và     ví d, T1.3 (skill-vao-goi-external) — nội dung sau `## SKILL` đầu tiên     không được, 2 agent runner: tồn tại, frontmatter hợp lệ, nêu đúng chữ ký lệnh lõi., T1.1 (skill-vao-goi-external) — cú pháp chuẩn dòng `Dùng:` + nhãn (mcp). (+3 more)

### Community 20 - "Working log — 2026-07-31"
Cohesion: 0.08
Nodes (24): 14:14–14:22 — Research (không đổi repo, ghi gộp ở entry sau), 14:23–14:30 — TDQ intake + analyze: request 2026-07-31-agy-search-agent (lane full), 14:34–14:45 — Phase spec: 2026-07-31-agy-search-agent (bản 1.1, CHỜ DUYỆT), 14:47–14:55 — Phase plan: 2026-07-31-agy-search-agent (CHỜ DUYỆT), 15:00–15:25 — Build + QC 2026-07-31-agy-search-agent (mode main), 15:22–15:35 — QC vòng 2: fix trigger search-runner qua Agent tool, 15:36–15:40 — Trigger test PASS + đóng QC vòng 2 + commit 0.5.0, 15:39 — Benchmark deep search: Run A (agy) khởi động (+16 more)

### Community 21 - "Working log — 2026-07-30"
Cohesion: 0.08
Nodes (23): ~00:05–08:38 — Tổng kiểm workflow + audit 43 plugin (chỉ đọc/phân tích), 11:07 — Mở request mới: tối ưu plugin user-level + lazy-load (tdq-intake Phần A), 12:05 — Analyze request plugin-lazy-load (lane full), 12:3x — Đóng interview vòng 1, chốt knowledge, phase=spec, 14:16 — Viết spec plugin-lazy-load v1.0 (phase spec), 14:24 — Spec được duyệt, 14:25 — Viết plan plugin-lazy-load (phase plan), 14:46–15:00 — Implement end-to-end request plugin-lazy-load (mode main) + QC + report (+15 more)

### Community 22 - ".set_response"
Cohesion: 0.19
Nodes (4): -> [khối args của từng lần gọi] (prompt nhiều dòng nằm trọn trong khối)., T1.3/Q2/Q9 — subcommand run-plan: 2 attempt, report plan-round-<n>.json., RunPlanTest, RunTest

### Community 23 - "ProtocolTest"
Cohesion: 0.22
Nodes (3): ProtocolTest, P2 — giao thức tuân thủ: nhắc có mã, quan sát hiệu ứng, đối chiếu ở Stop.  Nguyê, rows()

### Community 24 - "TestEditGate"
Cohesion: 0.20
Nodes (4): now_iso(), edit_gate.py (0.3.0) — quan sát vào sổ turn + nhắc; không bao giờ chặn., TestEditGate, today_log_rel()

### Community 25 - "StubBase"
Cohesion: 0.16
Nodes (7): FailTest, HardenTest, LogTest, Dựng stub binary codex/agy trong PATH + worktree/cwd tạm., A4/A12/A13/A24 — artifact debug + feedback + stagger timeout + atomic write., RetryTest, StubBase

### Community 26 - "Changelog"
Cohesion: 0.14
Nodes (19): 0.1.0 — 2026-07-27, 0.1.4 — 2026-07-28, 0.1.6 — 2026-07-28, 0.2.0 — 2026-07-28, 0.3.0 — 2026-07-29, 0.3.1 — 2026-07-29, 0.3.2 — 2026-07-29, 0.3.3 — 2026-07-29 (+11 more)

### Community 27 - "good_report"
Cohesion: 0.16
Nodes (5): good_plan_report(), good_report(), PlanSchemaTest, T1.1 — discriminator kind: task|plan; vắng kind = task (hồi quy)., SchemaTest

### Community 28 - "ModelsBase"
Cohesion: 0.20
Nodes (4): AgyListTest, CodexProbeTest, ModelsBase, Test external_models.py — list model available thật (stub binary, không mạng).

### Community 29 - "._go"
Cohesion: 0.17
Nodes (6): LogServiceUnifiedTest, T5.2/Q1/Q8 — E2E mock tầng script, vai orchestrator: chia 7 task     thành 2 gói, T3.2 (skill-vao-goi-external) — run-plan --plan-file: cảnh báo, vẫn chạy., T5.2 (skill-vao-goi-external) — 3 đường log cùng cơ chế: không slug →     stderr, RunPlanFileWarningTest, TwoPhaseE2ETest

### Community 30 - "TokenBudgetTest"
Cohesion: 0.18
Nodes (7): decision(), Parse PreToolUse hook stdout -> (permissionDecision, additionalContext).      0., budget(), P5 — ngân sách token của spec §2.7, đo thật chứ không phải khuyến nghị.  Mỗi ký, Sinh state cho mọi phase — trần phải đúng ở phase dài nhất, không chỉ phase dễ., description của mọi skill luôn nằm trong context — tổng phải gọn., TokenBudgetTest

### Community 32 - "plugin_tiers.py"
Cohesion: 0.34
Nodes (16): _claude_dir(), cmd_enable(), cmd_reset(), cmd_status(), _key_for(), _load_json(), _log(), _log_on() (+8 more)

### Community 33 - "helper.py"
Cohesion: 0.16
Nodes (8): Shared test utilities: run hook scripts as subprocesses with stdin JSON., Chạy CLI với process cwd = cwd và KHÔNG set TDQ_PROJECT_DIR (giống user     gõ l, run_hook(), run_state_cli_in(), P2/T2.12 — hook không bao giờ làm hỏng tool call (spec §4.7).  Mọi hook × mọi tr, ResilienceTest, P1 — xử lý state file: S1–S8 của spec 0.3.0 (mỗi yêu cầu 1 test)., P2 — sổ turn docs/tdq/.tdq-turn.jsonl (T2.1, T2.2).

### Community 34 - ".run_cli"
Cohesion: 0.21
Nodes (5): ParsePlanTest, T2.1/Q8 — chia gói ≤6 task, tôn trọng ranh giới phase., T1.2 (skill-vao-goi-external) — task (mcp) tách gói riêng, khóa skills., SplitPlanMcpTest, SplitPlanTest

### Community 35 - "_run"
Cohesion: 0.21
Nodes (6): prompt_context.py — nhắc [TDQ:INTAKE] khi KHÔNG có request mở (spec 2026-08-02)., T1.1-T1.4 (2026-08-04-approval-gate-bug): looks_like_approval() phải lưu     lại, _run(), TestIntakeReminder, TestSignalWritten, write_file_plan_mode()

### Community 36 - ".run_cli"
Cohesion: 0.19
Nodes (5): HardenTest, MergeTest, Chạy search_task.main IN-PROCESS: PATH → stub, HTTP → mock., A4/A7/A14/A15/A16 — persist raw, cảnh báo separator, schema guard,     merge đếm, T4.1 + T4.2 — dedup URL, rank tất định 5 khóa; merged.json + report ≤50 dòng

### Community 37 - "SPEC — Vá điểm mù của verify-by-effect (sổ turn chỉ thấy Edit/Write)"
Cohesion: 0.12
Nodes (15): 1. Bối cảnh & triệu chứng, 2. Nguyên nhân gốc, 3. Các phương án đã cân nhắc, 4. Thiết kế, 5. Ngoài phạm vi, 6. Phạm vi test (mỗi task 1 test, red → green), 7. Definition of Done, 8. Rủi ro & giảm thiểu (+7 more)

### Community 38 - "Working log — 2026-08-02"
Cohesion: 0.12
Nodes (15): 11:31 — Mở request tdq-default-cleanup, 11:36 — Analyze xong tdq-default-cleanup (lane full), 11:47 — Spec v1.1 tdq-default-cleanup, 11:52 — Plan tdq-default-cleanup trình duyệt, 12:01 — Build + QC + report tdq-default-cleanup (HOÀN THÀNH), 13:05 — Mở request fix-approve-hint-mode, 13:22 — Quick approved: fix-approve-hint-mode (mini-plan), 13:30 — Fix-approve-hint-mode HOÀN THÀNH (quick) (+7 more)

### Community 39 - "skill_inventory.py"
Cohesion: 0.19
Nodes (15): _clean(), _enabled_plugins(), _frontmatter(), inventory(), _load_json(), main(), _plugin_skill_dirs(), [(name, desc≤60, nguồn)] — trùng tên thì nguồn quét trước thắng. (+7 more)

### Community 40 - "PhaseTableTest"
Cohesion: 0.12
Nodes (7): PhaseTableTest, P1/P3 — PHASE_TABLE là nguồn sự thật duy nhất; doc phải khớp hằng trong code., A6: lane quick phải có terminal — quick_approved + phase=idle là đã xong., Bug A1: escape sai trong re.sub → literal `\\1` thay vì lệnh thật., A26: dòng duyệt quick khớp intake (biến thể external); A6: có bước đóng., A40: bản chạy trong ngữ cảnh plugin phải in path plugin-root., Mỗi phase phải xuất hiện trong doc kèm đúng lệnh chuyển tiếp.          A40: bản

### Community 41 - "PLAN — Kiểm kê & tận dụng skill phụ trợ (0.3.3)"
Cohesion: 0.13
Nodes (14): Definition of Done, Năng lực → task, P1 — `scripts/skill_inventory.py` + test, P2 — Bước B0 trong `tdq-intake`, P3 — Khuôn spec §3b + hợp đồng 6 trường ở plan, P4 — `doc_lint.py`: R8 + `--pair`, P5 — `tdq-build` thi hành hợp đồng, P6 — `PHASE_TABLE` + `phases.md` (+6 more)

### Community 42 - "Working log — 2026-07-27"
Cohesion: 0.13
Nodes (14): ~16:30 — Lập spec cho TDQWorkflow plugin, ~16:50 — Đổi đường dẫn working log theo yêu cầu người dùng, ~17:10 — Bổ sung quy tắc khai thác Tavily vào spec, ~17:25 — Check lazy load, bổ sung mục 3.1 vào spec, ~17:35 — Approve gate luôn hướng dẫn user lệnh duyệt, ~17:50 — Approve validate bằng state + detail file; vá lỗ hổng state.json, ~18:05 — Lane quick có cửa duyệt nhẹ + ghi summary plan vào working log trước implement, ~18:20 — User duyệt spec v0.1.6; lập plan (+6 more)

### Community 43 - "Working log 2026-07-29"
Cohesion: 0.13
Nodes (14): ~00:05 — User duyệt spec 0.3.0 → viết plan, ~01:00–01:40 — Implement plan 0.3.0 end-to-end (P3 → P8), ~02:10 — Phân tích + viết spec fix điểm mù verify-by-effect, ~02:30 — User duyệt spec → viết plan, ~02:45–03:30 — Implement plan 0.3.1 end-to-end (mode main), ~04:00 — Audit toàn bộ tdq-workflow 0.3.1 (theo yêu cầu user), ~04:15 — User duyệt fix 0.3.2 → plan, ~04:20–05:00 — Implement 0.3.2 end-to-end (mode main) (+6 more)

### Community 44 - "Deep search hybrid — Phase 1 (scout ∥ agy tổng quát) → Phase 2 (agy đào sâu)"
Cohesion: 0.13
Nodes (13): Cap + config env, Deep search hybrid — Phase 1 (scout ∥ agy tổng quát) → Phase 2 (agy đào sâu), Degrade Phase 1 — 3 nhánh, Luật brief — FULL data, Luật trigger, Luật verify + fallback, Phase 1 — 2 slot cố định, chạy song song, Phase 2 — agy đào sâu theo route đã chốt (+5 more)

### Community 45 - "load_fixture"
Cohesion: 0.29
Nodes (7): load_fixture(), read_state(), ChainBase, E1 — chuỗi end-to-end cả hai lane theo mô hình 0.3.0.  User duyệt bằng chat → Cl, TestFullLaneChain, TestQuickLaneChain, today()

### Community 46 - "test_search_task.py"
Cohesion: 0.24
Nodes (7): good_finding(), good_report(), Test search_task.py — deep search điều phối multi-call agy (stub binary, không m, T1.1 — schema all-required, URL bắt buộc có path., T3.3 — 1 call search + ≤N call đọc URL; parse structured_output; gộp finding., RunRouteTest, SchemaTest

### Community 47 - "PLAN — TDQ 0.3.0 (instruction-hardening-7b)"
Cohesion: 0.14
Nodes (13): Definition of Done, P1 — CLI `scripts/tdq_state.py`: state file, mirror, PHASE_TABLE, next, get, P2 — Hook: sổ turn, mã nhắc, đối chiếu bằng hiệu ứng, P3 — Skills 9 → 5 (+ conventions), P4 — Bản portable, P5 — Lint + test ngân sách token, P6 — Dọn dẹp, P7 — Đóng gói 0.3.0 (+5 more)

### Community 48 - "PLAN — Search agent "deep search" dùng agy CLI, tích hợp TDQ workflow"
Cohesion: 0.14
Nodes (13): Definition of Done, Năng lực → task, P1 — Schema + khung script + env, P2 — Subcommand `split` (cap bằng code), P3 — Subcommand `run` (1 agent chạy các route được giao), P4 — Subcommand `merge` (rank tất định bằng code), P5 — Agent vỏ mỏng + khuôn orchestrator, P6 — Tích hợp tầng search + config (+5 more)

### Community 49 - "AGENTS.md"
Cohesion: 0.18
Nodes (7): 02 — Spec, Các bước, 03 — Plan, Chốt engine + model (chỉ mode external), Các bước, Khuôn spec, Kiểm trước khi trình

### Community 50 - "external_models.py"
Cohesion: 0.33
Nodes (13): _cache_path(), _candidates(), list_agy(), list_codex(), _log(), main(), _now(), _probe_codex() (+5 more)

### Community 51 - "Bảng phase TDQ (tự sinh — KHÔNG sửa tay)"
Cohesion: 0.14
Nodes (12): analyze, Bảng phase TDQ (tự sinh — KHÔNG sửa tay), idle, implement, no_state, plan, qc, quick (+4 more)

### Community 52 - "run_state_cli"
Cohesion: 0.24
Nodes (4): run_state_cli(), NextTest, P1 — lệnh `next`, `next --brief`, `get <key>` (spec §2.2)., QC1.1 — tiêu đề phải nói đúng phase mà thân bài đang dùng.          Lane quick g

### Community 53 - "PLAN — Hybrid deep search 0.6.0 (scout ∥ agy tổng quát → agy đào sâu)"
Cohesion: 0.17
Nodes (11): Definition of Done, Năng lực → task, P1 — search_task.py: default model + start-agent (đầu ra #1, #2), P2 — Agent scout + doc quy ước (đầu ra #3, #4), P3 — Docs khớp + version 0.6.0 (đầu ra #5, #6), P4 — Log & test bắt buộc, P5 — E2E hybrid + QC (đầu ra #7; Q3, Q4, Q6, Q8-dương), P6 — Đóng turn (+3 more)

### Community 54 - "Đợt 1 (21:13) — khả thi tổng quát"
Cohesion: 0.17
Nodes (11): Q1: "use OpenAI Codex CLI as subagent inside Claude Code delegate tasks", Q2: "codex exec non-interactive headless", Q3: "Google Antigravity CLI headless", Q4: "codex mcp-server Claude Code", Q5: cách cài codex-plugin-cc, Q6: model slug Codex hiện hành, Q7: thiết kế prompt cho model cấp thấp/context ngắn, RESEARCH — external-agent-mode (+3 more)

### Community 55 - "SkillResolveTest"
Cohesion: 0.30
Nodes (4): T2.1 (skill-vao-goi-external) — resolver 3 tầng: repo → ~/.claude/skills     → p, T2.2 (skill-vao-goi-external) — dump nguyên văn + references, skill ma., SkillDumpTest, SkillResolveTest

### Community 57 - "PLAN — Audit tổng thể TDQ workflow 0.6.0 — HOÀN THÀNH"
Cohesion: 0.18
Nodes (10): Definition of Done, Năng lực → task, P1 — Fix issue đã biết + khung sổ findings, P2 — Hai việc chạy dài: deep search + S1 (khởi động NGAY đầu build, chạy nền), P3 — Review tĩnh chéo (chạy song song lúc chờ P2), P4 — Sample S2 + fix issue S/M, P5 — Log & test bắt buộc, P6 — QC, report, đóng sổ (+2 more)

### Community 58 - "PLAN — TDQ workflow là default tuyệt đối + bỏ §5 superpower"
Cohesion: 0.18
Nodes (10): Definition of Done, Năng lực → task, P0 — Nền (đã xong ở analyze), P1 — Hook [TDQ:INTAKE] (red → green), P2 — CLAUDE.md user-level, P3 — Skill tdq-intake, P4 — QC & đóng, PLAN — TDQ workflow là default tuyệt đối + bỏ §5 superpower (+2 more)

### Community 59 - "QC — 2026-07-31-audit-full-workflow"
Cohesion: 0.18
Nodes (10): Bảng QC Q1–Q10 (T6.1), Bảng token deep search (T2.2), Findings, Findings S1 — quick external model thấp (T2.5), Findings S2 — full mini + 3 nhánh sự cố (T4.1–T4.4), QC — 2026-07-31-audit-full-workflow, Review tĩnh lớp 1 (T3.1–T3.3), T3.1 — skills + references + portable + CLAUDE.md §10 (candidates từ reviewer phụ, đã tự xác minh 10/10 điểm S/M bằng grep/sed dòng trích dẫn) (+2 more)

### Community 60 - "SPEC — TDQ 0.3.0: tuân thủ kiểm được, state đọc được, workflow đủ rõ cho mọi model"
Cohesion: 0.18
Nodes (11): 1.1 Mục tiêu, 1.2 In-scope, 1.3 Out-of-scope, 1. Mục tiêu & phạm vi, 3. Kiến trúc & lý do chọn, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. Phạm vi QC / test / validate (điều kiện pass đo được) (+3 more)

### Community 61 - "2. Đầu ra cụ thể"
Cohesion: 0.18
Nodes (11): 2.10 Dọn dẹp gộp vào, 2.11 Cập nhật `~/.claude/CLAUDE.md` §10, 2.1 Giao thức tuân thủ: nhắc có mã → quan sát hiệu ứng → đối chiếu cuối turn, 2.2 CLI: `next` và `get <key>`, 2.4 Skills 9 → 5 (+ conventions), 2.5 Bản portable (chạy ngoài Claude Code), 2.6 Lint chất lượng doc, 2.7 Ngân sách token (có test đo, không phải khuyến nghị) (+3 more)

### Community 62 - "SPEC — TDQ workflow là default tuyệt đối + bỏ mục superpower (mục 5 cũ)"
Cohesion: 0.18
Nodes (10): 1. Mục tiêu & phạm vi, 1b. Mapping số mục CLAUDE.md (cũ → mới, sau khi xóa §5), 2. Đầu ra cụ thể, 3. Cách tiếp cận & lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. QC & Definition of Done (+2 more)

### Community 63 - "Working Log — 2026-08-04"
Cohesion: 0.10
Nodes (20): 12:17 — Mở request export Claude Code setup, 12:27 — Phase analyze hoàn tất (lane full), 12:30 — Bổ sung quyết định: bộ công cụ export lưu trong repo, 12:45 — Viết spec + review + sửa theo 5 góp ý tdq-reviewer, 13:05 — Viết plan (mode main) + fix bug doc_lint.py chặn pair-check, 13:15 — Sửa plan theo 7 góp ý tdq-reviewer + đăng ký state, 14:03 — Duyệt plan (mode main), chuyển phase implement, 14:24 — Chặn kỹ thuật T4.2: rsync T2.5 lọt data loại trừ vào bundle (+12 more)

### Community 64 - "04-build.md"
Cohesion: 0.18
Nodes (7): Khuôn gói task cho engine ngoài (mode external), Chạy cái gì, Ghi kết quả, Khi FAIL, QC — kiểm chất lượng, Khuôn report, Kiểm trước khi trình

### Community 65 - "Knowledge — 2026-08-03-check-external-assign-flow"
Cohesion: 0.20
Nodes (9): Bổ sung (user, 12:39): trigger qua subagent, Kiểm cổng, Knowledge — 2026-08-03-check-external-assign-flow, Kết luận, Nguồn, Năng lực dùng được, Phát hiện (nguồn: skills/tdq-build/SKILL.md dòng 53–87, 98–101), Phạm vi đụng tới (ước lượng) (+1 more)

### Community 66 - "PLAN — Vá điểm mù verify-by-effect (0.3.1)"
Cohesion: 0.20
Nodes (9): Definition of Done, P1 — Helper trong `scripts/tdq_state.py`, P2 — Ghi ảnh chụp đầu turn (`hooks/scripts/prompt_context.py`), P3 — Đối chiếu cuối turn (`hooks/scripts/stop_gate.py`), P4 — Doc & đóng gói 0.3.1, P5 — QC & report, PLAN — Vá điểm mù verify-by-effect (0.3.1), Task phát sinh từ QC (+1 more)

### Community 67 - "PLAN — Đổi thiết kế mode external: giao cả plan 1 lần + phase + verify 3 tầng"
Cohesion: 0.20
Nodes (9): Definition of Done, Năng lực → task, P1 — Script: schema + run-plan (spec §2 #1, #2), P2 — Luật chia phase + fix-rounds (spec §2 #8, một phần #3), P3 — Skill & khuôn gói (spec §2 #3, #4, #5), P4 — Agents + đồng bộ doc (spec §2 #6, #9), P5 — Log & test bắt buộc + QC, PLAN — Đổi thiết kế mode external: giao cả plan 1 lần + phase + verify 3 tầng (+1 more)

### Community 68 - "SPEC — Kiểm kê & tận dụng skill phụ trợ (tdq-workflow 0.3.3)"
Cohesion: 0.20
Nodes (9): 1. Mục tiêu & phạm vi, 2. Đầu ra cụ thể, 3. Cách tiếp cận & lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. QC & Definition of Done, 7. Câu hỏi còn mở (+1 more)

### Community 69 - "SPEC — Mode implement "external": giao task cho Codex/Antigravity qua worktree"
Cohesion: 0.20
Nodes (9): 1. Mục tiêu & phạm vi, 2. Đầu ra cụ thể, 3. Cách tiếp cận & lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. QC & Definition of Done, 7. Câu hỏi còn mở (+1 more)

### Community 70 - "SPEC — Tối ưu bộ plugin user-level: tier hoá, lazy-load, viết lại §10 (v1.0)"
Cohesion: 0.20
Nodes (9): 1. Mục tiêu & phạm vi, 2. Đầu ra đo đếm được, 3. Cách tiếp cận + lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. Phạm vi QC & Definition of Done, 7. Câu hỏi còn mở (+1 more)

### Community 71 - "SPEC — Search agent "deep search" dùng agy CLI, tích hợp TDQ workflow"
Cohesion: 0.20
Nodes (9): 1. Mục tiêu & phạm vi, 2. Đầu ra cụ thể, 3. Cách tiếp cận & lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. QC & Definition of Done, 7. Câu hỏi còn mở (+1 more)

### Community 72 - "SPEC — Audit tổng thể TDQ workflow 0.6.0 (conflict, edge case, robustness model thấp)"
Cohesion: 0.20
Nodes (9): 1. Mục tiêu & phạm vi, 2. Đầu ra cụ thể, 3. Cách tiếp cận & lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. QC & Definition of Done, 7. Câu hỏi còn mở (+1 more)

### Community 73 - "SPEC — Hybrid deep search: Claude scout ∥ agy tổng quát → agy đào sâu"
Cohesion: 0.20
Nodes (9): 1. Mục tiêu & phạm vi, 2. Đầu ra cụ thể, 3. Cách tiếp cận & lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. QC & Definition of Done, 7. Câu hỏi còn mở (+1 more)

### Community 74 - "SPEC — Đổi thiết kế mode external: giao cả plan 1 lần + fix loop"
Cohesion: 0.20
Nodes (9): 1. Mục tiêu & phạm vi, 2. Đầu ra cụ thể, 3. Cách tiếp cận & lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. QC & Definition of Done, 7. Câu hỏi còn mở (+1 more)

### Community 75 - "SPEC — Bộ công cụ export cấu hình Claude Code sang máy khác"
Cohesion: 0.20
Nodes (9): 1. Mục tiêu & phạm vi, 2. Đầu ra cụ thể, 3. Cách tiếp cận & lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. QC & Definition of Done, 7. Câu hỏi còn mở (+1 more)

### Community 76 - "TDQ Workflow — bản portable (agent nào cũng chạy được)"
Cohesion: 0.20
Nodes (10): Chất lượng, Cây tài liệu, Ghi nhận duyệt, Giao thức một turn (bắt buộc, đúng thứ tự), Git, Pipeline, Research, State (+2 more)

### Community 77 - "Bảng phase TDQ (tự sinh — KHÔNG sửa tay)"
Cohesion: 0.20
Nodes (10): analyze, Bảng phase TDQ (tự sinh — KHÔNG sửa tay), idle, implement, no_state, plan, qc, quick (+2 more)

### Community 78 - "workflow/references/approval.md"
Cohesion: 0.20
Nodes (8): Ghi nhận duyệt, KHÔNG phải câu duyệt (phản ví dụ), Là câu duyệt khi có ĐỦ hai phần, Lệnh phải chạy NGAY khi nhận ra, Bảng 5 mã (danh sách đóng), Hook nhìn thấy thay đổi bằng cách nào, Mã nhắc của hook, Điểm chặn duy nhất

### Community 79 - "TDQ Conventions"
Cohesion: 0.20
Nodes (10): 1. Giao thức một turn (bắt buộc, làm đúng thứ tự), 2. Bảng phase, 3. State, 4. Ghi nhận duyệt, 5. Cây tài liệu, 6. Working log, 7. Git, 8. Research (+2 more)

### Community 80 - "test_portable_sync.py"
Cohesion: 0.31
Nodes (5): PortableSyncTest, P4 — bản portable (chạy ngoài Claude Code) phải tồn tại và KHÔNG lệch với skills, Danh sách bước đã chuẩn hoá: bỏ link, bỏ đậm, bỏ đường dẫn riêng của plugin., read(), steps()

### Community 81 - "INSTRUCTIONS — Dựng bundle export cấu hình Claude Code"
Cohesion: 0.22
Nodes (8): Bước 1 — Thu thập trạng thái thật máy nguồn, Bước 2 — Lọc secret/runtime, Bước 3 — Copy file cấu hình local + repo TDQWorkflow, Bước 4 — Rewrite path marketplace `tdq-local` theo vị trí đích (BẮT BUỘC), Bước 5 — Điền manifest, Bước 6 — Điền README, Bước 7 — Ghi log, INSTRUCTIONS — Dựng bundle export cấu hình Claude Code

### Community 82 - "doc"
Cohesion: 0.22
Nodes (9): doc, Expect_Output, git & worktree, Graphify, Phong cách trình bày, quy tắc chung, Research & độ tin cậy thông tin, workflow (+1 more)

### Community 83 - "Plan — TDQWorkflow Plugin v0.1"
Cohesion: 0.22
Nodes (8): Definition of Done (theo spec mục 10), Nguyên tắc thực thi, Phase A — Nền móng, Phase B — Hooks + unit test (red/green từng script), Phase C — Skills (10), Phase D — Agents, Phase E — QC tổng + tài liệu, Plan — TDQWorkflow Plugin v0.1

### Community 84 - "KNOWLEDGE — external-agent-mode"
Cohesion: 0.22
Nodes (8): Kiểm cổng, KNOWLEDGE — external-agent-mode, Nguồn, Năng lực dùng được (B0 — bảng phán quyết), Phương án đã loại, Quyết định đã chốt (8, từ questions cùng slug), Sự thật đã xác minh trên máy, Đính chính 23:45 (sau chẩn đoán sâu, có bằng chứng)

### Community 85 - "PLAN — Bộ công cụ export cấu hình Claude Code sang máy khác"
Cohesion: 0.22
Nodes (8): Definition of Done, Năng lực → task, P1 — Viết bộ công cụ export tĩnh (`claude-export/`), P2 — Thu thập dữ liệu thật & copy vào bundle đích, P3 — Điền manifest/README thật & ghi log, P4 — QC tổng & log/test bắt buộc, PLAN — Bộ công cụ export cấu hình Claude Code sang máy khác, Quy tắc thi hành (áp cho mọi task)

### Community 86 - "REPORT — Instruction hardening cho model yếu (tdq-workflow 0.3.0)"
Cohesion: 0.22
Nodes (8): Cách chạy / cách kiểm, Giới hạn còn lại, Kết quả QC, Quyết định đáng chú ý, REPORT — Instruction hardening cho model yếu (tdq-workflow 0.3.0), Ánh xạ tên skill cũ → mới, Đã làm gì, Đầu ra

### Community 87 - "REPORT — Audit toàn diện tdq-workflow 0.6.0"
Cohesion: 0.22
Nodes (8): Cách chạy / cách kiểm, Giới hạn còn lại, Kết quả QC, Quyết định đáng chú ý, REPORT — Audit toàn diện tdq-workflow 0.6.0, Đã làm gì, Đầu ra, Đề xuất tiếp theo

### Community 88 - "REPORT — Đổi thiết kế mode external: giao cả plan / theo phase"
Cohesion: 0.22
Nodes (8): Cách chạy / cách kiểm, Giới hạn còn lại, Kết quả QC, Quyết định đáng chú ý, REPORT — Đổi thiết kế mode external: giao cả plan / theo phase, Đã làm gì, Đầu ra, Đề xuất tiếp theo

### Community 89 - "REPORT — Bộ công cụ export cấu hình Claude Code sang máy khác"
Cohesion: 0.22
Nodes (8): Cách chạy / cách kiểm, Giới hạn còn lại, Kết quả QC, Quyết định đáng chú ý, REPORT — Bộ công cụ export cấu hình Claude Code sang máy khác, Đã làm gì, Đầu ra, Đề xuất tiếp theo

### Community 90 - "Working log 2026-08-03"
Cohesion: 0.22
Nodes (8): 12:30 — Mở request check-external-assign-flow, 12:35 — Analyze check-external-assign-flow (lane full), 12:38 — Chốt analyze check-external-assign-flow, 12:45 — Spec 1.1 check-external-assign-flow, 12:50 — Spec 1.2 check-external-assign-flow (góp ý user), 12:58 — Plan check-external-assign-flow, 13:40 — Hoàn tất build + QC + report request check-external-assign-flow, Working log 2026-08-03

### Community 91 - "Kiểm kê năng lực (bước B0)"
Cohesion: 0.22
Nodes (9): 4 lý do loại (đóng — cấm tự chế lý do khác), Agent ngoài (không có skill system), Bảng quá dài, Các bước, Khuôn bảng (copy nguyên khối rồi điền), Kiểm kê năng lực (bước B0), Lane quick, Luật điền ô "Phán quyết" (+1 more)

### Community 92 - "tdq-workflow — Plugin Claude Code"
Cohesion: 0.22
Nodes (8): Cài đặt (chỉ trong repo/project), Cách hook điều khiển agent, Cấu trúc, Duyệt bằng chat thường, Dùng hằng ngày, Pipeline, Quy ước cứng, tdq-workflow — Plugin Claude Code

### Community 94 - "Kiểm kê năng lực (bước B0)"
Cohesion: 0.22
Nodes (8): 4 lý do loại (đóng — cấm tự chế lý do khác), Bảng quá dài, Các bước, Khuôn bảng (copy nguyên khối rồi điền), Kiểm kê năng lực (bước B0), Lane quick, Luật điền ô "Phán quyết", Số phận từng phán quyết ở các phase sau

### Community 95 - "DocsConsistencyTest"
Cohesion: 0.25
Nodes (3): DocsConsistencyTest, P6 — doc không được mô tả hành vi mà 0.3.0 đã bỏ.  Doc nói "hook chặn" trong khi, relevant_files()

### Community 96 - "{{BUNDLE_NAME}} — Claude Code setup export"
Cohesion: 0.25
Nodes (7): 1. Giới thiệu bundle, 2. CLI dependency cần cài, 3. Cài Claude Code CLI, 4. Add marketplace + cài từng plugin, 5. Copy file cấu hình + rewrite path `tdq-local` + điền lại API key, 6. Verify, {{BUNDLE_NAME}} — Claude Code setup export

### Community 97 - "Hướng dẫn tự cài tdq-workflow ở user-level (thủ công)"
Cohesion: 0.25
Nodes (7): 1. Cài qua local marketplace, 2. Đồng bộ rule working log ở `~/.claude/CLAUDE.md`, 3. Thêm instruction TDQ cho MỌI task vào `~/.claude/CLAUDE.md`, 4. Dùng ngoài Claude Code, 5. Gỡ, Hướng dẫn tự cài tdq-workflow ở user-level (thủ công), Lưu ý an toàn

### Community 98 - "KNOWLEDGE — Search agent dùng agy cho advanced search (2026-07-31)"
Cohesion: 0.25
Nodes (7): Kiểm cổng, KNOWLEDGE — Search agent dùng agy cho advanced search (2026-07-31), Nguồn, Năng lực dùng được, Phương án đã loại + lý do, Quyết định đã chốt (interview 14:27 + probe), Ràng buộc

### Community 99 - "Knowledge — 2026-07-31-hybrid-deep-search"
Cohesion: 0.25
Nodes (7): Hiện trạng code (đọc 2026-07-31), Knowledge — 2026-07-31-hybrid-deep-search, Nguồn, Năng lực dùng được, Phương án đã loại, Quyết định đã chốt (từ request + interview), Ràng buộc

### Community 100 - "KNOWLEDGE — 2026-08-02-tdq-default-cleanup"
Cohesion: 0.25
Nodes (7): Cách tiếp cận, KNOWLEDGE — 2026-08-02-tdq-default-cleanup, Nguồn, Năng lực dùng được, Phương án đã loại, Quyết định đã chốt (user trả lời vòng 1), Ràng buộc

### Community 101 - "PLAN — Vá chặn oan do vân tay repo (0.3.2)"
Cohesion: 0.25
Nodes (7): Ngoài phạm vi (đã nêu lý do trong chat), P1 — `scripts/tdq_state.py`: vân tay chỉ tính file "thật", P2 — `hooks/scripts/stop_gate.py`, P3 — Log service (D), P4 — Doc & đóng gói 0.3.2, P5 — QC & report, PLAN — Vá chặn oan do vân tay repo (0.3.2)

### Community 102 - "PLAN — Mode implement "external" (Codex/Antigravity qua worktree) — HOÀN THÀNH (mode main, 2026-07-30 23:10; Q9 PENDING chờ user cài plugin codex)"
Cohesion: 0.25
Nodes (7): Definition of Done, Năng lực → task, P1 — Lõi script + unit test (repo, red → green từng task), P2 — State machine + hooks + doc tự sinh, P3 — Khuôn task + agents + skills + CLAUDE.md, P4 — Cài plugin + chạy thật + QC + đóng, PLAN — Mode implement "external" (Codex/Antigravity qua worktree) — HOÀN THÀNH (mode main, 2026-07-30 23:10; Q9 PENDING chờ user cài plugin codex)

### Community 103 - "PLAN — Tối ưu bộ plugin user-level: tier hoá + lazy-load (HOÀN THÀNH — QC PASS 9/9, 14:58)"
Cohesion: 0.25
Nodes (7): Definition of Done, Năng lực → task, P1 — Script `plugin_tiers.py` + test (trong repo, red → green từng task), P2 — Cài user-level, P3 — `~/.claude/CLAUDE.md`, P4 — QC & đóng, PLAN — Tối ưu bộ plugin user-level: tier hoá + lazy-load (HOÀN THÀNH — QC PASS 9/9, 14:58)

### Community 104 - "Bằng chứng"
Cohesion: 0.25
Nodes (7): Bằng chứng, Không sửa (có chủ ý), Kết luận, Q7 — ba kịch bản audit, dựng lại nguyên trạng (bản cài 0.3.2), Q8 — hồi quy 0.3.1, Q9 — git treo quá 2 s, QC — Vá chặn oan do vân tay repo (0.3.2)

### Community 105 - "QC — Vá điểm mù verify-by-effect (0.3.1)"
Cohesion: 0.25
Nodes (7): Bằng chứng, Ghi chú lệch so với spec, Kết luận, Lỗi phát hiện trong QC và đã sửa, Q1, Q10 — smoke trên bản cài user-level 0.3.1 (`TDQ_PROJECT_DIR` đặt riêng từng lệnh), QC — Vá điểm mù verify-by-effect (0.3.1)

### Community 106 - "REPORT — Kiểm kê & tận dụng skill phụ trợ (tdq-workflow 0.3.3)"
Cohesion: 0.25
Nodes (7): Còn chờ user, Kết quả QC, Lệch so với spec (chi tiết + lý do ở file QC), REPORT — Kiểm kê & tận dụng skill phụ trợ (tdq-workflow 0.3.3), Vấn đề, Đã làm gì, Đầu ra

### Community 107 - "REPORT — Vá điểm mù verify-by-effect (tdq-workflow 0.3.1)"
Cohesion: 0.25
Nodes (7): Giới hạn còn lại, Kết quả QC, Quyết định đáng chú ý, REPORT — Vá điểm mù verify-by-effect (tdq-workflow 0.3.1), Vấn đề, Đã làm gì, Đầu ra

### Community 108 - "Research: 2026-08-04-export-claude-setup"
Cohesion: 0.25
Nodes (7): Research: 2026-08-04-export-claude-setup, Truy vấn 1 — Settings hierarchy (global/project/local), Truy vấn 2 — Cài lại plugin/marketplace trên máy mới, Truy vấn 3 — MCP config, secret trong `.mcp.json` / `~/.claude.json`, Truy vấn 4 — Backup/restore `~/.claude` giữa các máy (cộng đồng), Truy vấn 5 — Claude Code trên Windows: bắt buộc WSL2 hay hỗ trợ native?, Truy vấn 6 — Cài Codex CLI đa nền (macOS/Linux/Windows)

### Community 109 - "Brief deep search — LLM local tham số thấp làm engine code-agent (2026-07-31)"
Cohesion: 0.25
Nodes (7): Brief deep search — LLM local tham số thấp làm engine code-agent (2026-07-31), Câu hỏi, Dữ kiện đã có, Hướng từ phase 1, Luật, Ngữ cảnh, Tiêu chí rank

### Community 114 - "Report — TDQWorkflow Plugin v0.1.0 — 2026-07-27"
Cohesion: 0.29
Nodes (6): Cách chạy / test, Kết quả, QC (docs/qc/), Quyết định đáng chú ý & giới hạn, Report — TDQWorkflow Plugin v0.1.0 — 2026-07-27, Đề xuất tiếp theo

### Community 115 - "Knowledge — 2026-07-31-audit-full-workflow"
Cohesion: 0.29
Nodes (6): Cách tiếp cận đã chọn, Knowledge — 2026-07-31-audit-full-workflow, Nguồn, Năng lực dùng được, Quyết định đã chốt (interview vòng 1 — questions/ cùng slug), Ràng buộc

### Community 116 - "Knowledge: 2026-08-04-export-claude-setup"
Cohesion: 0.29
Nodes (6): Khảo sát máy nguồn (đọc code/cấu hình thực tế), Kiểm cổng (3 câu hỏi bắt buộc trước khi sang spec), Knowledge: 2026-08-04-export-claude-setup, Loại trừ khỏi export (đã có căn cứ từ research + khảo sát), Năng lực dùng được, Quyết định đã chốt (từ vòng interview)

### Community 117 - "Bằng chứng"
Cohesion: 0.29
Nodes (6): Bằng chứng, Kết luận, Q1, Q12 — ghi chú lệch nhẹ so với spec, Q9 — smoke trên bản cài user-level (mọi lệnh đặt TDQ_PROJECT_DIR riêng), QC — Instruction hardening cho model yếu (0.3.0)

### Community 118 - "QC — Tối ưu plugin user-level: tier hoá + lazy-load"
Cohesion: 0.29
Nodes (6): Bằng chứng T2.6 — 3 case an toàn chạy tay trên máy thật, Bằng chứng T3.3 — audit CLAUDE.md (skill claude-md-improver), Ghi chú lệch (có chủ ý), Kết luận, QC — Tối ưu plugin user-level: tier hoá + lazy-load, Đối chiếu DoD spec §6 (vòng 1)

### Community 119 - "REPORT — Vá chặn oan do vân tay repo (tdq-workflow 0.3.2)"
Cohesion: 0.29
Nodes (6): Còn lại, Kết quả QC, REPORT — Vá chặn oan do vân tay repo (tdq-workflow 0.3.2), Vấn đề, Đã làm gì, Đầu ra

### Community 120 - "REPORT — Tối ưu bộ plugin user-level: tier hoá + lazy-load"
Cohesion: 0.29
Nodes (6): Còn chờ user, Hợp đồng skill đã thi hành, Kết quả QC — PASS 9/9 vòng 1, REPORT — Tối ưu bộ plugin user-level: tier hoá + lazy-load, Vấn đề, Đã làm gì

### Community 121 - "Request: Claude tự quyết implement mode, không hỏi user"
Cohesion: 0.29
Nodes (6): Bằng chứng thu được, Hướng fix đề xuất, Nguyên nhân (không phải bug code, là lỗ hổng thiết kế 0.1.3), Nguyên văn, Request: Claude tự quyết implement mode, không hỏi user, Unknowns cần user chốt

### Community 122 - "Request: state phải luôn nằm ở project root (chống "state bóng")"
Cohesion: 0.29
Nodes (6): Bằng chứng, Mong muốn, Nguyên nhân, Nguyên văn, Request: state phải luôn nằm ở project root (chống "state bóng"), Ràng buộc

### Community 123 - "RESEARCH — Search agent dùng agy (2026-07-31)"
Cohesion: 0.29
Nodes (6): Kết luận khả thi, RESEARCH — Search agent dùng agy (2026-07-31), Truy vấn 1: Gemini CLI headless còn dùng được không (bối cảnh chọn agy), Truy vấn 2: agy headless có tool search không (probe thật trên máy, 2026-07-31 14:20), Truy vấn 3: agy --json-schema headless (docs chính thức), Truy vấn 4: chống bịa citation với model yếu

### Community 124 - "Brief deep search — LLM local tham số thấp làm engine code-agent (2026-07-31)"
Cohesion: 0.29
Nodes (6): Brief deep search — LLM local tham số thấp làm engine code-agent (2026-07-31), Câu hỏi, Dữ kiện đã có, Luật, Ngữ cảnh, Tiêu chí rank

### Community 125 - "BRIEF — Vector database chạy local cho RAG (2026)"
Cohesion: 0.29
Nodes (6): BRIEF — Vector database chạy local cho RAG (2026), Câu hỏi, Dữ kiện đã có, Hướng từ phase 1, Ngữ cảnh, Tiêu chí rank

### Community 126 - "add"
Cohesion: 0.43
Nodes (3): add(), Sample E2E cho mode external — task E2E-AGY (fallback do orchestrator tự làm)., AddTest

### Community 127 - "add"
Cohesion: 0.43
Nodes (3): add(), Sample module for E2E Codex tests., TestE2ECodex

### Community 130 - "KNOWLEDGE — instruction-hardening-7b (chốt trước khi viết spec)"
Cohesion: 0.33
Nodes (6): 1. Vấn đề cốt lõi, 2. Quyết định đã chốt, 3. Tiêu chí "model yếu đọc cũng làm đúng" (lint sẽ chấm), 4. Đánh đổi đã biết, 5. Chưa quyết (không chặn spec), KNOWLEDGE — instruction-hardening-7b (chốt trước khi viết spec)

### Community 131 - "KNOWLEDGE — Tối ưu plugin user-level + lazy-load"
Cohesion: 0.33
Nodes (5): Kiểm cổng, KNOWLEDGE — Tối ưu plugin user-level + lazy-load, Năng lực dùng được, Quyết định đã chốt (interview vòng 1 — xem ../questions/ cùng slug), Sự thật đã chốt (từ research + đo máy)

### Community 132 - "QC — Kiểm kê & tận dụng skill phụ trợ (0.3.3)"
Cohesion: 0.33
Nodes (5): Bằng chứng Q9 — rà bảo mật `scripts/skill_inventory.py`, Ghi chú lệch so với spec (có chủ ý), Kết luận, Lỗi phát hiện trong QC và đã sửa, QC — Kiểm kê & tận dụng skill phụ trợ (0.3.3)

### Community 133 - "QC — Mode implement "external" (Codex/Antigravity qua worktree)"
Cohesion: 0.33
Nodes (5): Bảng DoD Q1–Q9 (T4.5, vòng 1), Bằng chứng T3.7 — audit CLAUDE.md (skill claude-md-improver), Ghi chú sai lệch có chủ đích (vòng 1), QC — Mode implement "external" (Codex/Antigravity qua worktree), Đính chính sau QC (23:45, request fix-agy-adddir-sync-agent)

### Community 134 - "QC — TDQ workflow là default tuyệt đối + bỏ mục superpower"
Cohesion: 0.33
Nodes (5): Backup CLAUDE.md (T2.1), Bảng QC Q1–Q6, QC — TDQ workflow là default tuyệt đối + bỏ mục superpower, QC vòng 1 — 5 fail phát hiện ở T4.1, đã fix (QC1.1–QC1.3), Đối chiếu §5 superpower (cũ) → chỗ thay thế trong plugin

### Community 135 - "REPORT — Mode implement "external" (Codex/Antigravity qua worktree)"
Cohesion: 0.33
Nodes (5): Kết quả, QC (chi tiết trong file QC), REPORT — Mode implement "external" (Codex/Antigravity qua worktree), Việc user cần làm, Đề xuất tiếp

### Community 136 - "Report — Hybrid deep search 2 phase (tdq-workflow 0.6.0)"
Cohesion: 0.33
Nodes (5): Bằng chứng chính, Hạn chế / việc còn lại, Kết quả, Report — Hybrid deep search 2 phase (tdq-workflow 0.6.0), Token Claude E2E (usage từng agent)

### Community 137 - "REQUEST — Hook = remind, bỏ skill tdq-approve, instruction/skills đủ chi tiết cho model yếu (7B)"
Cohesion: 0.33
Nodes (6): Câu hỏi chờ user, Hiểu ban đầu (first read), Nguyên văn yêu cầu, REQUEST — Hook = remind, bỏ skill tdq-approve, instruction/skills đủ chi tiết cho model yếu (7B), Ràng buộc đã biết, Việc liên quan đang mở (từ đợt rà soát 2026-07-28)

### Community 138 - "REQUEST — Kiểm kê & tận dụng skill phụ trợ"
Cohesion: 0.33
Nodes (5): Chỗ chưa rõ, Cách hiểu đầu tiên, Nguyên văn yêu cầu, REQUEST — Kiểm kê & tận dụng skill phụ trợ, Đã xác minh trước khi viết spec (turn phân tích)

### Community 139 - "requests/2026-07-31-hybrid-deep-search.md"
Cohesion: 0.33
Nodes (5): Bổ sung (user, 15:59 +07), Chốt thêm (user, 16:01 +07), Chỗ chưa rõ (sẽ interview nếu lane full), Cách hiểu đầu tiên, Nguyên văn yêu cầu (user, 15:53 +07)

### Community 140 - "RESEARCH — Instruction/skills đủ chắc để model yếu đi đúng workflow"
Cohesion: 0.33
Nodes (6): Kết luận dùng cho spec, R1 — PreToolUse có nhận `additionalContext` không? (câu hỏi sống-còn của thiết kế 0.2.0), R2 — Instruction dạng văn xuôi KHÔNG phải cơ chế bảo đảm, R3 — Viết prompt/instruction cho model yếu (7B), R4 — Chuẩn viết skill của Claude Code (giới hạn thực tế khi "viết chi tiết hơn"), RESEARCH — Instruction/skills đủ chắc để model yếu đi đúng workflow

### Community 141 - "RESEARCH — Tối ưu plugin user-level + lazy-load"
Cohesion: 0.33
Nodes (5): RESEARCH — Tối ưu plugin user-level + lazy-load, Số liệu đo tại máy (2026-07-30), Truy vấn 1 — cơ chế enabledPlugins & scope, Truy vấn 2 — chi phí context của plugin/skill, Truy vấn 3 — lệnh quản lý plugin

### Community 142 - "Research — 2026-07-31-hybrid-deep-search"
Cohesion: 0.33
Nodes (5): Dữ liệu benchmark nội bộ (docs/tdq/research/search/, 2026-07-31), Ground truth model, Research — 2026-07-31-hybrid-deep-search, Truy vấn 1 — pattern orchestration đa agent cho search, Truy vấn 2 — hệ research đa agent của Anthropic (căn cứ chính)

### Community 143 - "Brief: phiên bản Python 3 mới nhất"
Cohesion: 0.33
Nodes (5): Brief: phiên bản Python 3 mới nhất, Câu hỏi, Dữ kiện đã có, Ngữ cảnh, Tiêu chí rank

### Community 144 - "Brief: phiên bản Python 3 mới nhất"
Cohesion: 0.33
Nodes (5): Brief: phiên bản Python 3 mới nhất, Câu hỏi, Dữ kiện đã có, Ngữ cảnh, Tiêu chí rank

### Community 145 - "Brief: phiên bản npm mới nhất của 2 package"
Cohesion: 0.33
Nodes (5): Brief: phiên bản npm mới nhất của 2 package, Câu hỏi, Dữ kiện đã có, Ngữ cảnh, Tiêu chí rank

### Community 146 - "Brief: phiên bản Python 3 mới nhất"
Cohesion: 0.33
Nodes (5): Brief: phiên bản Python 3 mới nhất, Câu hỏi, Dữ kiện đã có, Ngữ cảnh, Tiêu chí rank

### Community 147 - "BRIEF — Vector database chạy local cho RAG (2026)"
Cohesion: 0.33
Nodes (5): BRIEF — Vector database chạy local cho RAG (2026), Câu hỏi, Dữ kiện đã có, Ngữ cảnh, Tiêu chí rank

### Community 148 - "04 — Build: Implement → QC → Report"
Cohesion: 0.33
Nodes (6): 04 — Build: Implement → QC → Report, Luật cứng (áp cho cả ba phase), Nhánh external (Phần A, mode external), Phần A — Implement (phase `implement`), Phần B — QC (phase `qc`), Phần C — Report (phase `report`)

### Community 149 - "06 — Deep search hybrid qua search_task.py (agy + search thường)"
Cohesion: 0.33
Nodes (5): 06 — Deep search hybrid qua search_task.py (agy + search thường), Degrade + env + fallback, Luật trigger, Phase 1 — 2 slot cố định song song (ngoại lệ của luật split), Tổng hợp + Phase 2 — code quyết, không tự chia

### Community 150 - "Khuôn gói cho engine ngoài (mode external)"
Cohesion: 0.33
Nodes (5): Ghi chú cho orchestrator (không đưa vào gói), Khuôn 1 — GÓI TASK ĐƠN (quick lane, lệnh `run`), Khuôn 2 — GÓI PLAN / PHASE (lane full, lệnh `run-plan`), Khuôn 3 — GÓI FIX (vòng mini-plan fix, lệnh `run-plan --round <n+1>`), Khuôn gói cho engine ngoài (mode external)

### Community 151 - "TDQ Build — Implement → QC → Report"
Cohesion: 0.33
Nodes (6): Luật cứng (áp cho cả ba phase), Nhánh external (Phần A, mode external), Phần A — Implement (phase `implement`), Phần B — QC (phase `qc`), Phần C — Report (phase `report`), TDQ Build — Implement → QC → Report

### Community 152 - "Vòng interview"
Cohesion: 0.33
Nodes (5): Ghi lại, Hỏi cái gì, Hỏi thế nào, Khi nào dừng, Vòng interview

### Community 153 - "BuildCommandTest"
Cohesion: 0.20
Nodes (4): BuildCommandTest, DefaultModelTest, T1.1 (0.6.0) — default flash-medium, escalation flash-high, docs đồng bộ., T3.1 — lệnh agy đúng flags; prompt khuôn grounded đủ 3 luật.     Effort nằm tron

### Community 158 - "QUESTIONS — Interview request instruction-hardening-7b"
Cohesion: 0.40
Nodes (5): Giả định tôi tự chốt (nói rõ để bạn bác nếu sai), QUESTIONS — Interview request instruction-hardening-7b, Vòng 0 — intake, Vòng 1, Vòng 2

### Community 159 - "QUESTIONS — external-agent-mode"
Cohesion: 0.40
Nodes (4): Kết vòng interview, QUESTIONS — external-agent-mode, Vòng 1 (21:55) — 4 câu đổi kết quả, Vòng 2 (21:58) — 4 câu chốt nốt

### Community 160 - "QUESTIONS — 2026-08-02-tdq-default-cleanup"
Cohesion: 0.40
Nodes (4): QUESTIONS — 2026-08-02-tdq-default-cleanup, Trả lời (vòng 1 — 2026-08-02 11:35), Vòng 1 (chờ trả lời), Vòng 2 — không còn câu hỏi đổi kết quả

### Community 161 - "Questions: 2026-08-04-export-claude-setup"
Cohesion: 0.40
Nodes (4): Chốt (không còn câu hỏi nào làm đổi kết quả), Questions: 2026-08-04-export-claude-setup, Vòng 1 — 2026-08-04, Vòng 2 — 2026-08-04

### Community 162 - "reports/2026-07-31-agy-search-agent.md"
Cohesion: 0.40
Nodes (4): Cách dùng nhanh, Giới hạn / PENDING, Kết quả QC (chi tiết: docs/tdq/qc/2026-07-31-agy-search-agent.md), Đã làm

### Community 163 - "REPORT — TDQ workflow là default tuyệt đối + bỏ mục superpower"
Cohesion: 0.40
Nodes (4): Lưu ý, QC, REPORT — TDQ workflow là default tuyệt đối + bỏ mục superpower, Đã làm

### Community 164 - "REQUEST — Fix chặn oan `[TDQ:LOG]` khi log ghi qua shell"
Cohesion: 0.40
Nodes (4): Liên quan, Nguyên văn triệu chứng, REQUEST — Fix chặn oan `[TDQ:LOG]` khi log ghi qua shell, Vì sao là lane full

### Community 165 - "REQUEST — Fix agy không tạo file (--add-dir) + Claude tự bắt kết quả agent"
Cohesion: 0.40
Nodes (4): Chẩn đoán (có bằng chứng), Nguyên văn yêu cầu, Phạm vi dự kiến, REQUEST — Fix agy không tạo file (--add-dir) + Claude tự bắt kết quả agent

### Community 166 - "REQUEST — Tối ưu bộ plugin user-level theo ranking + lazy-load"
Cohesion: 0.40
Nodes (4): Chỗ chưa rõ (cần phân tích/hỏi), Cách hiểu đầu tiên, Nguyên văn yêu cầu, REQUEST — Tối ưu bộ plugin user-level theo ranking + lazy-load

### Community 167 - "REQUEST — Search agent dùng agy cho advanced search, tích hợp TDQ workflow"
Cohesion: 0.40
Nodes (4): Cách hiểu đầu tiên, Nguyên văn yêu cầu, REQUEST — Search agent dùng agy cho advanced search, tích hợp TDQ workflow, Rủi ro đã biết (từ probe)

### Community 168 - "Research — 2026-07-31-audit-full-workflow"
Cohesion: 0.40
Nodes (4): Khảo sát nội bộ (đọc code turn analyze), Research — 2026-07-31-audit-full-workflow, Truy vấn 1 (tavily-primary, advanced): prompt engineering small local LLM instruction following limitations agentic workflow reliability, Truy vấn 2 (tavily-primary, advanced): multi-agent LLM pipeline failure modes state machine orchestration edge cases 2025

### Community 169 - "RESEARCH — 2026-08-02-tdq-default-cleanup"
Cohesion: 0.40
Nodes (4): Kết luận thiết kế, RESEARCH — 2026-08-02-tdq-default-cleanup, Truy vấn 1: enforce workflow mỗi prompt — hook vs CLAUDE.md, Truy vấn 2: viết description skill để luôn trigger

### Community 170 - "2.3 Thiết kế state file"
Cohesion: 0.40
Nodes (5): 2.3.1 Hai file, một nguồn sự thật, 2.3.2 Quy tắc đọc/ghi cho agent (nhúng vào `tdq-conventions` + `AGENTS.md`), 2.3.3 Yêu cầu kỹ thuật xử lý file, 2.3.4 Bảng quyết định phase (`PHASE_TABLE` — hằng trong code, doc trích lại), 2.3 Thiết kế state file

### Community 171 - "QC — kiểm chất lượng"
Cohesion: 0.40
Nodes (4): Chạy cái gì, Ghi kết quả, Khi FAIL, QC — kiểm chất lượng

### Community 172 - "Chọn lane: quick hay full"
Cohesion: 0.40
Nodes (4): Bảng quyết, Chọn lane: quick hay full, Khuôn câu hỏi (copy được), Luồng mỗi lane

### Community 173 - "SPEC — 2026-08-04-approval-gate-bug"
Cohesion: 0.18
Nodes (10): 1. Mục tiêu & phạm vi, 2. Đầu ra cụ thể, 3. Cách tiếp cận & lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. QC & Definition of Done, 7. Câu hỏi còn mở (+2 more)

### Community 174 - "QC — Smoke e2e (E1) — 2026-07-27"
Cohesion: 0.50
Nodes (3): 1. Chain test 2 lane (hook thật, chạy subprocess), 2. Headless CLI thật (`claude -p --plugin-dir .`), QC — Smoke e2e (E1) — 2026-07-27

### Community 175 - "questions/2026-07-31-agy-search-agent.md"
Cohesion: 0.50
Nodes (3): Bổ sung từ user (14:34, không cần hỏi lại — yêu cầu rõ), Các điểm Claude chốt (không đổi kết quả, có lý do — user không cần quyết), Vòng 1 (14:27, đã chốt)

### Community 176 - "Questions — 2026-07-31-audit-full-workflow"
Cohesion: 0.50
Nodes (3): Không còn câu hỏi mở, Questions — 2026-07-31-audit-full-workflow, Vòng 1 (2026-07-31 17:3x, AskUserQuestion)

### Community 177 - "Questions — 2026-07-31-hybrid-deep-search"
Cohesion: 0.50
Nodes (3): Các câu đã chốt trước đó qua chat (15:53–16:01), Questions — 2026-07-31-hybrid-deep-search, Vòng 1 (2026-07-31 16:07 +07, AskUserQuestion)

### Community 178 - "Questions — 2026-08-03-check-external-assign-flow"
Cohesion: 0.50
Nodes (3): Questions — 2026-08-03-check-external-assign-flow, Vòng 1, Vòng 2 (chốt thiết kế)

### Community 179 - "REQUEST — Mode giao việc cho agent ngoài (codex/antigravity) trong TDQ workflow"
Cohesion: 0.50
Nodes (3): Cách hiểu đầu tiên, Nguyên văn yêu cầu, REQUEST — Mode giao việc cho agent ngoài (codex/antigravity) trong TDQ workflow

### Community 180 - "REQUEST — Sample Socket.IO chat để test mode external (codex + agy)"
Cohesion: 0.50
Nodes (3): Cách hiểu đầu tiên, Nguyên văn yêu cầu, REQUEST — Sample Socket.IO chat để test mode external (codex + agy)

### Community 181 - "REQUEST — Tự chọn theo đề xuất khi gặp chặn kỹ thuật giữa build"
Cohesion: 0.50
Nodes (3): Cách hiểu đầu tiên, Nguyên văn yêu cầu, REQUEST — Tự chọn theo đề xuất khi gặp chặn kỹ thuật giữa build

### Community 182 - "REQUEST — Check bump version + đồng bộ plugin repo ↔ user-level"
Cohesion: 0.50
Nodes (3): Cách hiểu đầu tiên, Nguyên văn yêu cầu, REQUEST — Check bump version + đồng bộ plugin repo ↔ user-level

### Community 183 - "REQUEST — Dòng duyệt plan gợi ý sai mode đã chốt"
Cohesion: 0.50
Nodes (3): Cách hiểu đầu tiên, Nguyên văn yêu cầu, REQUEST — Dòng duyệt plan gợi ý sai mode đã chốt

### Community 184 - "Brief — Công nghệ speech-to-text word-level realtime (2026)"
Cohesion: 0.50
Nodes (3): Brief — Công nghệ speech-to-text word-level realtime (2026), Câu hỏi, Yêu cầu bằng chứng

### Community 185 - "Brief — Công nghệ speech-to-text word-level realtime (2026)"
Cohesion: 0.50
Nodes (3): Brief — Công nghệ speech-to-text word-level realtime (2026), Câu hỏi, Yêu cầu bằng chứng

### Community 186 - "TDQ STATE (tự sinh — không sửa tay)"
Cohesion: 0.50
Nodes (3): TDQ STATE (tự sinh — không sửa tay), Việc tiếp theo, Đang ở đâu

### Community 187 - "01 — Intake: mở request & phân tích"
Cohesion: 0.50
Nodes (4): 01 — Intake: mở request & phân tích, Phần A — Mở request (phase `no_state`), Phần B — Phân tích (phase `analyze`, chỉ lane full), Phần C — Lane quick

### Community 188 - "Khuôn plan"
Cohesion: 0.50
Nodes (3): Dòng `Mode thực thi`, Khuôn plan, Kiểm trước khi trình

### Community 189 - "external_report_schema.json"
Cohesion: 0.50
Nodes (3): oneOf, $schema, title

### Community 190 - "Ghi nhận duyệt"
Cohesion: 0.50
Nodes (4): Ghi nhận duyệt, KHÔNG phải câu duyệt (phản ví dụ), Là câu duyệt khi có ĐỦ hai phần, Lệnh phải chạy NGAY khi nhận ra

### Community 191 - "Mã nhắc của hook"
Cohesion: 0.50
Nodes (4): Bảng 5 mã (danh sách đóng), Hook nhìn thấy thay đổi bằng cách nào, Mã nhắc của hook, Điểm chặn duy nhất

### Community 192 - "TDQ Intake — mở request & phân tích"
Cohesion: 0.50
Nodes (4): Phần A — Mở request (phase `no_state`), Phần B — Phân tích (phase `analyze`, chỉ lane full), Phần C — Lane quick, TDQ Intake — mở request & phân tích

### Community 193 - "Khuôn plan"
Cohesion: 0.50
Nodes (3): Dòng `Mode thực thi`, Khuôn plan, Kiểm trước khi trình

### Community 204 - "TDQ Plan"
Cohesion: 0.67
Nodes (3): Chốt engine + model (chỉ mode external), Các bước, TDQ Plan

### Community 229 - "Knowledge — 2026-08-04-approval-gate-bug"
Cohesion: 0.22
Nodes (8): Kiểm cổng, Knowledge — 2026-08-04-approval-gate-bug, Lịch sử liên quan (git log), Năng lực dùng được, Quyết định đã chốt (qua vòng interview), Research (tóm tắt, đầy đủ ở `docs/tdq/research/2026-08-04-approval-gate-bug.md`), Rủi ro còn lại (ghi nhận, không phải chỗ chưa rõ), Đọc code (tóm tắt)

### Community 230 - "PLAN — Sửa lỗi approval-gate (nhắc nhở khi duyệt sai)"
Cohesion: 0.22
Nodes (8): Definition of Done, Ghi chú review (áp dụng 5 góp ý `tdq-reviewer` vòng 1), Năng lực → task, P1 — Lưu tín hiệu duyệt vào turn ledger (`prompt_context.py`), P2 — Đối chiếu tín hiệu trong `bash_gate.py` (cả `approve` và `set phase=`), P3 — Test bắt buộc tổng hợp, PLAN — Sửa lỗi approval-gate (nhắc nhở khi duyệt sai), Quy tắc thi hành (áp cho mọi task)

### Community 231 - "REPORT — Sửa lỗi approval-gate (nhắc nhở khi duyệt sai)"
Cohesion: 0.22
Nodes (8): Cách chạy / cách kiểm, Giới hạn còn lại, Kết quả QC, Quyết định đáng chú ý, REPORT — Sửa lỗi approval-gate (nhắc nhở khi duyệt sai), Đã làm gì, Đầu ra, Đề xuất tiếp theo

### Community 232 - "Research — 2026-08-04-approval-gate-bug"
Cohesion: 0.29
Nodes (6): Kết luận rút ra cho hướng kỹ thuật, Research — 2026-08-04-approval-gate-bug, Truy vấn 1: Claude Code PreToolUse hook permissionDecision deny — chặn cứng theo pattern nào, Truy vấn 2: LLM agent bỏ qua instruction chèn trong context / tool output — failure mode, Truy vấn 3: Human-in-the-loop approval gate — chặn cứng vs nhắc mềm, Đối chiếu với lịch sử chính plugin (đọc code, không phải research ngoài nhưng liên quan)

### Community 233 - "REQUEST — 2026-08-04-approval-gate-bug"
Cohesion: 0.40
Nodes (4): Cách hiểu đầu tiên, Ghi chú vận hành, Nguyên văn yêu cầu, REQUEST — 2026-08-04-approval-gate-bug

## Knowledge Gaps
- **988 isolated node(s):** `Đang ở đâu`, `Việc tiếp theo`, `Năng lực dùng được`, `Đọc code (tóm tắt)`, `Lịch sử liên quan (git log)` (+983 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **42 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `today_log_rel()` connect `tdq_state.py` to `_common.py`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **Why does `main()` connect `_common.py` to `tdq_state.py`?**
  _High betweenness centrality (0.011) - this node is a cross-community bridge._
- **What connects `Đang ở đâu`, `Việc tiếp theo`, `Năng lực dùng được` to the rest of the system?**
  _988 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `tdq_state.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0648018648018648 - nodes in this community are weakly interconnected._
- **Should `write_state` be split into smaller, more focused modules?**
  _Cohesion score 0.09722222222222222 - nodes in this community are weakly interconnected._
- **Should `doc_lint.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0593990216631726 - nodes in this community are weakly interconnected._
- **Should `external_task.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08163265306122448 - nodes in this community are weakly interconnected._