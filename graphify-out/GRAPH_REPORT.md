# Graph Report - TDQWorkflow  (2026-08-11)

## Corpus Check
- 388 files · ~332,623 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3344 nodes · 4098 edges · 344 communities (286 shown, 58 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 10 edges (avg confidence: 0.53)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `023eeaf6`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- tdq_state.py
- .stop
- .write
- .run_inv
- Working log 2026-08-05
- doc_lint.py
- git
- claude_export.py
- 2. Thay đổi theo file
- SPEC — Yêu cầu mới ⇒ state được đồng bộ lại theo lane user chọn
- TestPromptContext
- test_token_audit.py
- Working log — 2026-07-28
- Working Log — 2026-08-04
- token_audit.py
- TestBashGate
- .run_cli
- Working log 2026-08-03
- Changelog
- Spec: TDQWorkflow Plugin cho Claude Code
- _project
- .build
- Working log — 2026-07-31
- Working log — 2026-07-30
- tdq_finish.py
- ProtocolTest
- TestEditGate
- TestState
- Working log 2026-08-09
- StateFileTest
- _common.py
- skill_inventory.py
- test_e2e_chain.py
- Spec — tối ưu token/time workflow (vòng 2)
- plugin_tiers.py
- _run
- test_quick_qc.py
- Kiến thức chốt — audit tối ưu token/time workflow (vòng 3)
- SPEC — Vá điểm mù của verify-by-effect (sổ turn chỉ thấy Edit/Write)
- Working log — 2026-08-02
- test_agent_frontmatter.py
- test_claude_export.py
- PhaseTableTest
- TokenBudgetTest
- PLAN — Kiểm kê & tận dụng skill phụ trợ (0.3.3)
- PLAN — Giảm over-engineer & over-test cho TDQ workflow
- Working log — 2026-07-27
- Working log 2026-07-29
- tdq-conventions/SKILL.md
- helper.py
- PLAN — TDQ 0.3.0 (instruction-hardening-7b)
- PLAN — Search agent "deep search" dùng agy CLI, tích hợp TDQ workflow
- PLAN — Triển khai 16 đề xuất P0+P1 tối ưu workflow TDQ & user-level Claude Code
- MultiRepoTest
- PLAN — Bump 0.7.0 + bộ export Claude Code chạy bằng một lệnh
- PLAN — Tối ưu token/time workflow (vòng 2)
- QC — giảm over-engineer workflow TDQ
- Working log 2026-08-08
- TestProjectRootResolution
- PLAN — Hybrid deep search 0.6.0 (scout ∥ agy tổng quát → agy đào sâu)
- PLAN — Full claude export (multi-repo local dependency)
- Đợt 1 (21:13) — khả thi tổng quát
- TDQ Conventions
- CheckTest
- test_claude_md_core.py
- NextTest
- Quy tắc làm việc cho Claude
- Hiểu & kiến thức
- ĐỀ XUẤT — Tối ưu time/token cho TDQ workflow
- Kiến thức chốt — tối ưu token/time workflow (vòng 2)
- PLAN — Audit tổng thể TDQ workflow 0.6.0 — HOÀN THÀNH
- PLAN — TDQ workflow là default tuyệt đối + bỏ §5 superpower
- PLAN — TDQ workflow linh hoạt & bớt ma sát
- PLAN — Skill clone-setting-to-codex
- PLAN — Siết QC và vòng fix cho lane quick
- QC — 2026-07-31-audit-full-workflow
- SPEC — TDQ 0.3.0: tuân thủ kiểm được, state đọc được, workflow đủ rõ cho mọi model
- 2. Đầu ra cụ thể
- SPEC — TDQ workflow là default tuyệt đối + bỏ mục superpower (mục 5 cũ)
- SPEC — Đưa skill vào gói external (hybrid 3 nhánh)
- SPEC — 2026-08-04-approval-gate-bug
- SPEC — Đề xuất tối ưu time/token cho TDQ workflow
- SPEC — Audit toàn bộ workflow TDQ, đề xuất tối ưu token/thời gian (vòng 3)
- SPEC — Bump 0.7.0 + bộ export Claude Code đầy đủ, chạy được bằng một lệnh
- SPEC — Skill clone-setting-to-codex
- SPEC — Full claude export (multi-repo local dependency)
- SPEC — Triển khai 16 đề xuất P0+P1 tối ưu workflow TDQ & user-level Claude Code
- SPEC — Siết QC và vòng fix cho lane quick
- SPEC — Giảm over-engineer & over-test cho TDQ workflow
- SPEC — Cắt token thừa trong TDQ workflow
- bash_gate.py
- stop_gate.py
- tdq-intake/SKILL.md
- ScanSecretsTest
- GateMergeTest
- Knowledge — 2026-08-03-check-external-assign-flow
- KNOWLEDGE — Bump version + export đầy đủ hơn
- Knowledge — 2026-08-05-clone-setting-codex
- KNOWLEDGE — Brainstorm + spec triển khai P0+P1 tối ưu workflow & user-level Claude Code
- PLAN — Vá điểm mù verify-by-effect (0.3.1)
- PLAN — Đổi thiết kế mode external: giao cả plan 1 lần + phase + verify 3 tầng
- PLAN — Đưa skill vào gói external (hybrid 3 nhánh)
- PLAN — Cắt token thừa trong TDQ workflow
- Mini-spec/plan — 2026-08-09-sua-mo-ta-skill-inventory (lane quick)
- Vòng 1 (2026-08-05 13:35)
- RESEARCH — Tối ưu token/time cho TDQ workflow
- Research: clone-setting-to-codex — cấu trúc/khả năng cấu hình thật của Codex CLI (2026)
- Research: Tối ưu token vòng 2 — biện pháp lâu dài cho agentic workflow
- SPEC — Kiểm kê & tận dụng skill phụ trợ (tdq-workflow 0.3.3)
- SPEC — Mode implement "external": giao task cho Codex/Antigravity qua worktree
- SPEC — Tối ưu bộ plugin user-level: tier hoá, lazy-load, viết lại §10 (v1.0)
- SPEC — Search agent "deep search" dùng agy CLI, tích hợp TDQ workflow
- SPEC — Audit tổng thể TDQ workflow 0.6.0 (conflict, edge case, robustness model thấp)
- SPEC — Hybrid deep search: Claude scout ∥ agy tổng quát → agy đào sâu
- SPEC — Đổi thiết kế mode external: giao cả plan 1 lần + fix loop
- SPEC — Bộ công cụ export cấu hình Claude Code sang máy khác
- SPEC — TDQ workflow linh hoạt & bớt ma sát
- {{BUNDLE_NAME}} — Claude Code setup export
- doc
- Plan — TDQWorkflow Plugin v0.1
- Nguyên văn
- KNOWLEDGE — external-agent-mode
- Knowledge — 2026-08-04-approval-gate-bug
- KNOWLEDGE — Tối ưu token/time cho TDQ workflow
- Knowledge — 2026-08-04-workflow-linh-hoat
- Knowledge — 2026-08-05-full-claude-export
- KNOWLEDGE — Siết QC và vòng fix cho lane quick
- Knowledge — 2026-08-08-giam-over-engineer-workflow
- PLAN — Sửa lỗi approval-gate (nhắc nhở khi duyệt sai)
- PLAN — Bộ công cụ export cấu hình Claude Code sang máy khác
- PLAN — Đề xuất tối ưu time/token cho TDQ workflow
- Mini-spec/plan — 2026-08-09-trigger-tieng-viet (lane quick)
- REPORT — Instruction hardening cho model yếu (tdq-workflow 0.3.0)
- REPORT — Audit toàn diện tdq-workflow 0.6.0
- REPORT — Đổi thiết kế mode external: giao cả plan / theo phase
- REPORT — Đưa skill vào gói external (hybrid 3 nhánh)
- REPORT — Sửa lỗi approval-gate (nhắc nhở khi duyệt sai)
- REPORT — Bộ công cụ export cấu hình Claude Code sang máy khác
- Working log 2026-08-07
- tdq-workflow — Plugin Claude Code
- tavily.md
- QuickQcApproveCliTest
- Hướng dẫn tự cài tdq-workflow ở user-level (thủ công)
- 2026-08-09-sua-mo-ta-skill-inventory
- KNOWLEDGE — Search agent dùng agy cho advanced search (2026-07-31)
- Knowledge — 2026-07-31-hybrid-deep-search
- KNOWLEDGE — 2026-08-02-tdq-default-cleanup
- PLAN — Vá chặn oan do vân tay repo (0.3.2)
- PLAN — Mode implement "external" (Codex/Antigravity qua worktree) — HOÀN THÀNH (mode main, 2026-07-30 23:10; Q9 PENDING chờ user cài plugin codex)
- PLAN — Tối ưu bộ plugin user-level: tier hoá + lazy-load (HOÀN THÀNH — QC PASS 9/9, 14:58)
- PLAN — Audit toàn bộ workflow TDQ, đề xuất tối ưu token/thời gian (vòng 3)
- Bằng chứng
- QC — Vá điểm mù verify-by-effect (0.3.1)
- Vòng 1 (2026-08-05 03:2x) — đã hỏi, chờ trả lời
- REPORT — Kiểm kê & tận dụng skill phụ trợ (tdq-workflow 0.3.3)
- REPORT — Vá điểm mù verify-by-effect (tdq-workflow 0.3.1)
- REPORT — Tối ưu time/token cho TDQ workflow
- REPORT — Giảm over-engineer & over-test cho TDQ workflow
- Research: 2026-08-04-export-claude-setup
- Brief deep search — LLM local tham số thấp làm engine code-agent (2026-07-31)
- TurnStartRowTest
- TurnLedgerTest
- INSTRUCTIONS — Dựng bundle export cấu hình Claude Code
- Report — TDQWorkflow Plugin v0.1.0 — 2026-07-27
- Knowledge — 2026-07-31-audit-full-workflow
- Knowledge — 2026-08-03-skill-vao-goi-external
- Knowledge: 2026-08-04-export-claude-setup
- Bằng chứng
- QC — Tối ưu plugin user-level: tier hoá + lazy-load
- REPORT — Vá chặn oan do vân tay repo (tdq-workflow 0.3.2)
- REPORT — Tối ưu bộ plugin user-level: tier hoá + lazy-load
- Request: Claude tự quyết implement mode, không hỏi user
- Request: state phải luôn nằm ở project root (chống "state bóng")
- RESEARCH — Search agent dùng agy (2026-07-31)
- Research — 2026-08-04-approval-gate-bug
- Research: Giảm chi phí token/thời gian dài hạn cho agentic coding workflow
- RESEARCH — Bump version + export đầy đủ hơn
- Brief deep search — LLM local tham số thấp làm engine code-agent (2026-07-31)
- BRIEF — Vector database chạy local cho RAG (2026)
- Chọn model & effort cho sub-agent
- Kiểm kê năng lực (bước B0)
- KNOWLEDGE — instruction-hardening-7b (chốt trước khi viết spec)
- KNOWLEDGE — Tối ưu plugin user-level + lazy-load
- MINI-PLAN — Thực thi 5 task P0 tối ưu token
- QC — Kiểm kê & tận dụng skill phụ trợ (0.3.3)
- QC — Mode implement "external" (Codex/Antigravity qua worktree)
- QC — TDQ workflow là default tuyệt đối + bỏ mục superpower
- QUESTIONS — Siết QC và vòng fix cho lane quick
- Vòng 1 — 2026-08-08 21:5x
- REPORT — Mode implement "external" (Codex/Antigravity qua worktree)
- Report — Hybrid deep search 2 phase (tdq-workflow 0.6.0)
- REPORT — Workflow linh hoạt: gộp gate, quick đủ bước, lộ trình động
- Report — Siết QC và vòng fix cho lane quick
- REQUEST — Hook = remind, bỏ skill tdq-approve, instruction/skills đủ chi tiết cho model yếu (7B)
- REQUEST — Kiểm kê & tận dụng skill phụ trợ
- requests/2026-07-31-hybrid-deep-search.md
- REQUEST — Bump version + làm lại bản export đầy đủ hơn
- Request: clone-setting-codex
- Request — tối ưu token/time workflow (vòng 2)
- REQUEST — Siết QC và vòng fix cho lane quick
- RESEARCH — Instruction/skills đủ chắc để model yếu đi đúng workflow
- RESEARCH — Tối ưu plugin user-level + lazy-load
- Research — 2026-07-31-hybrid-deep-search
- Research — 2026-08-03-skill-vao-goi-external
- Brief: phiên bản Python 3 mới nhất
- Brief: phiên bản Python 3 mới nhất
- Brief: phiên bản npm mới nhất của 2 package
- Brief: phiên bản Python 3 mới nhất
- BRIEF — Vector database chạy local cho RAG (2026)
- Brief — clone-setting-codex (phase 2 đào sâu)
- Brief — clone-setting-codex (phase 2 đào sâu)
- remind
- BuildManifestTest
- make_repo
- LogTest
- RepoIntegrityTest
- PLAN (quick) — 2026-08-05-bump-sync-user
- PLAN (quick) — 2026-08-05-dat-ten-subagent
- QUICK — Format câu hỏi interview: mỗi option 1 dòng
- Mini-plan — Rebuild bundle export để đồng bộ (quick)
- Mini-plan — Validate lại bundle export (quick)
- QC — 2026-08-05-toi-uu-p0-p1-workflow
- QC — Siết QC và vòng fix cho lane quick
- QUESTIONS — Interview request instruction-hardening-7b
- QUESTIONS — external-agent-mode
- QUESTIONS — 2026-08-02-tdq-default-cleanup
- Questions: 2026-08-04-export-claude-setup
- Hỏi–đáp: clone-setting-codex
- reports/2026-07-31-agy-search-agent.md
- REPORT — TDQ workflow là default tuyệt đối + bỏ mục superpower
- REPORT — Cắt token thừa trong TDQ workflow
- REQUEST — Fix chặn oan `[TDQ:LOG]` khi log ghi qua shell
- REQUEST — Fix agy không tạo file (--add-dir) + Claude tự bắt kết quả agent
- REQUEST — Tối ưu bộ plugin user-level theo ranking + lazy-load
- REQUEST — Search agent dùng agy cho advanced search, tích hợp TDQ workflow
- REQUEST — Thực thi 5 task P0 của đề xuất tối ưu token
- REQUEST — Tối ưu thời gian + token cho TDQ workflow
- Request: Làm TDQ workflow linh hoạt & bớt ma sát
- Request: audit toàn bộ workflow — tối ưu token/time
- REQUEST — Format câu hỏi interview: mỗi option 1 dòng
- REQUEST — Brainstorm + spec triển khai P0+P1 tối ưu workflow & user-level Claude Code
- Request: giảm over-engineer & over-test cho bộ workflow
- Research — 2026-07-31-audit-full-workflow
- RESEARCH — 2026-08-02-tdq-default-cleanup
- 2.3 Thiết kế state file
- QC — kiểm chất lượng
- TDQ Build — Implement → QC → Report
- Kịch bản đo carry-cost before/after
- phases.md
- Vòng interview
- Chọn cỡ request: nhỏ, quick hay full
- TDQ Intake — mở request & phân tích
- CollectConfigTest
- QuickQcPhaseTableTest
- QC — Smoke e2e (E1) — 2026-07-27
- QC — 2026-08-03-skill-vao-goi-external
- QC — workflow linh hoạt (gộp gate, lane quick đủ bước, lộ trình động)
- QC — Audit toàn bộ workflow TDQ, đề xuất tối ưu token/thời gian (vòng 3)
- QC — Bump 0.7.0 + bộ export Claude Code
- QC — Full claude export (multi-repo local dependency)
- questions/2026-07-31-agy-search-agent.md
- Questions — 2026-07-31-audit-full-workflow
- Questions — 2026-07-31-hybrid-deep-search
- Questions — 2026-08-03-check-external-assign-flow
- Hỏi–đáp — 2026-08-03-skill-vao-goi-external
- QUESTIONS — tối ưu token/time workflow
- Interview — 2026-08-04-workflow-linh-hoat
- Hỏi–đáp: 2026-08-05-audit-toi-uu-workflow
- Câu hỏi — 2026-08-05-full-claude-export
- Hỏi–đáp — tối ưu token vòng 2
- REQUEST — Mode giao việc cho agent ngoài (codex/antigravity) trong TDQ workflow
- REQUEST — Sample Socket.IO chat để test mode external (codex + agy)
- REQUEST — Tự chọn theo đề xuất khi gặp chặn kỹ thuật giữa build
- REQUEST — Check bump version + đồng bộ plugin repo ↔ user-level
- REQUEST — Dòng duyệt plan gợi ý sai mode đã chốt
- REQUEST — 2026-08-03-check-sync-sau-restart
- REQUEST — 2026-08-03-recheck-sync-restart-2
- requests/2026-08-04-approval-gate-bug.md
- REQUEST — 2026-08-05-bump-sync-user
- Request: full claude export
- Research — 2026-08-04-workflow-linh-hoat
- Brief — Công nghệ speech-to-text word-level realtime (2026)
- Brief — Công nghệ speech-to-text word-level realtime (2026)
- TDQ STATE (tự sinh — không sửa tay)
- Ghi nhận duyệt
- Định tuyến việc → plugin
- Mã nhắc của hook
- Khuôn plan
- Khuôn spec
- EXPORT_LOG — Lịch sử sinh bundle export
- QC — 2026-07-31-agy-search-agent
- QC — 2026-07-31-hybrid-deep-search (0.6.0)
- QC — 2026-08-04-approval-gate-bug
- QC — export-claude-setup (2026-08-04)
- QC — Tối ưu time/token cho TDQ workflow
- QC — Cắt token thừa trong TDQ workflow
- QUESTIONS — Tối ưu plugin user-level + lazy-load
- Questions — 2026-08-04-approval-gate-bug
- QUESTIONS — Format câu hỏi interview
- requests/2026-07-31-audit-full-workflow.md
- requests/2026-08-02-tdq-default-cleanup.md
- requests/2026-08-03-check-external-assign-flow.md
- requests/2026-08-04-export-claude-setup.md
- requests/2026-08-05-dat-ten-subagent.md
- requests/2026-08-05-rebuild-sync-export.md
- requests/2026-08-05-validate-export.md
- Report — 2026-07-31-failpath-demo (fallback tavily)
- edit_gate.py
- skill-budget.md
- token-budget.md
- v0.1/README.md
- E2E-AGY.task.md
- E2E-CODEX.task.md
- S1.task.md
- S2.task.md
- qc/2026-08-03-check-external-assign-flow.md
- reports/2026-08-05-audit-toi-uu-workflow.md
- reports/2026-08-05-bump-version-va-export.md
- reports/2026-08-05-full-claude-export.md
- reports/2026-08-05-toi-uu-p0-p1-workflow.md
- reports/2026-08-05-toi-uu-token-vong-2.md
- 2026-08-03-check-claude-md-sync.md
- 2026-08-03-check-external-lam-theo-skill.md
- 2026-08-03-check-skill-clone-worktree.md
- 2026-08-03-check-skill-vao-worktree-external.md
- 2026-07-31-local-llm-engine/report.md
- 2026-07-31-npm-versions/report.md
- 2026-07-31-stt-wordlevel-claude/report.md
- 2026-07-31-stt-wordlevel/report.md
- 2026-07-31-trigger-test/report.md
- 2026-07-31-vectordb-local-rag/report.md
- 2026-08-05-clone-setting-codex/report.md
- .test_reapprove_refreshes_sha256_after_file_changed
- .test_reapprove_unchanged_file_stays_idempotent
- .test_mode_external_bi_tu_choi
- .test_approve_quick_moves_phase_to_implement
- .test_row_age_ok_bad_ts_types
- .test_init_set_reset_in_mot_dong_khong_json
- .test_co_co_json_thi_in_lai_nguyen_state

## God Nodes (most connected - your core abstractions)
1. `Working log 2026-08-05` - 53 edges
2. `Working Log — 2026-08-04` - 30 edges
3. `write_state()` - 30 edges
4. `TestState` - 30 edges
5. `Working log 2026-08-03` - 29 edges
6. `TestBashGate` - 24 edges
7. `Working log — 2026-07-31` - 24 edges
8. `Working log — 2026-07-30` - 23 edges
9. `Working log — 2026-07-28` - 22 edges
10. `Working log 2026-08-09` - 21 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `today_log_rel()`  [INFERRED]
  hooks/scripts/edit_gate.py → scripts/tdq_state.py
- `main()` --calls--> `payload_cwd()`  [EXTRACTED]
  hooks/scripts/bash_gate.py → hooks/scripts/_common.py
- `main()` --calls--> `read_payload()`  [EXTRACTED]
  hooks/scripts/bash_gate.py → hooks/scripts/_common.py
- `main()` --calls--> `remind()`  [EXTRACTED]
  hooks/scripts/bash_gate.py → hooks/scripts/_common.py
- `main()` --calls--> `turn_rows()`  [EXTRACTED]
  hooks/scripts/bash_gate.py → hooks/scripts/_common.py

## Import Cycles
- None detected.

## Communities (344 total, 58 thin omitted)

### Community 0 - "tdq_state.py"
Cohesion: 0.05
Nodes (75): _atomic_write(), cli(), _cli_approve(), default_state(), _echo_state(), effective_lane(), effective_mode(), effective_phase() (+67 more)

### Community 1 - ".stop"
Cohesion: 0.10
Nodes (22): write_state(), stop_gate.py (0.3.0) — đối chiếu lời nhắc với hiệu ứng thật trong sổ turn.  Điểm, P3 (0.3.1) — hiệu ứng THẬT trên đĩa, không chỉ tin sổ turn.      Sổ turn chỉ ghi, Giả lập prompt_context: chụp trạng thái đĩa lúc mở turn., Bug gốc: log append bằng shell → không có `log_written` → chặn oan., Log hôm nay chưa tồn tại đầu turn, được tạo bằng shell trong turn., Có ảnh chụp nhưng log KHÔNG đổi → vẫn phải chặn., Không phải git repo → repo_sha None, nhưng chiều log vẫn vá được. (+14 more)

### Community 2 - ".write"
Cohesion: 0.07
Nodes (19): ContractFieldsTest, DocLintTest, LintBase, MissingPathTest, PairTest, R8Test, P5 — mỗi rule của scripts/doc_lint.py có 1 fixture bẩn + 1 fixture sạch.  Lint l, Cửa thoát chuẩn phải im được R5.          Bug cũ: rule_r5 gom dòng liền nhau thà (+11 more)

### Community 3 - ".run_inv"
Cohesion: 0.08
Nodes (27): CliTest, DescriptionTest, InventoryBase, LogServiceTest, PluginTest, ProjectDirResolveTest, P1 (0.3.3) — scripts/skill_inventory.py: kiểm kê skill trên đĩa.  Script là nửa, 2 dòng nhắc built-in phải in NGUYÊN VĂN, kể cả khi bảng rỗng. (+19 more)

### Community 4 - "Working log 2026-08-05"
Cohesion: 0.04
Nodes (53): 00:43 — Mở request tối ưu token vòng 2 (intake, chờ chốt lane), 00:52 — Phân tích vòng 2: đo lại chi phí, phát hiện token_audit đếm sai, 01:10 — Chốt interview vòng 2, viết knowledge + spec, 01:25 — User duyệt spec → viết plan (6 phase / 21 task), 02:04, 02:21, 02:27, 03:23 (+45 more)

### Community 5 - "doc_lint.py"
Cohesion: 0.06
Nodes (36): collect(), Doc, lint_file(), main(), pair(), _plan_contracts(), Bước trong mục 'Các bước' phải đánh số 1, 2, 3… không nhảy, không lặp., Lệnh phải copy-paste được: trong khối ```, trong inline-code, hoặc ô bảng. (+28 more)

### Community 6 - "git"
Cohesion: 0.05
Nodes (18): BookkeepingExclusionTest, git(), P1 — ảnh chụp trạng thái đầu turn (spec 0.3.1 §4 S3).  Hai helper này là nền của, Sổ sách đã commit rồi sửa tiếp → phải lọt qua cả pathspec của `diff HEAD`., 0.3.2 — dấu của file untracked phải theo NỘI DUNG, không theo mtime., `touch`/ghi đè y hệt byte (formatter, build tool) không phải là thay đổi., Quá trần đọc thì vẫn phải có dấu (size), không được bỏ trắng., Cap phải đếm FILE untracked; cắt theo dòng status thì 1 dòng `M` là đủ nuốt hết. (+10 more)

### Community 7 - "claude_export.py"
Cohesion: 0.09
Nodes (44): cli_versions(), clone_repo(), cmd_build(), cmd_check(), collect_config_files(), copy_config(), copy_launch_agents(), copy_repo_memory() (+36 more)

### Community 8 - "2. Thay đổi theo file"
Cohesion: 0.05
Nodes (38): Definition of Done, Nguyên tắc thực thi, Phase 1 — CLI ghi nhận duyệt, Phase 2 — Hook chỉ còn nhắc, Phase 3 — Skills & tài liệu, Phase 4 — Nghiệm thu & đóng gói, PLAN — TDQ 0.2.0: hard gate → nhắc nhở, duyệt bằng chat tự nhiên, 1. Unit / e2e (+30 more)

### Community 9 - "SPEC — Yêu cầu mới ⇒ state được đồng bộ lại theo lane user chọn"
Cohesion: 0.05
Nodes (33): Definition of Done, Nguyên tắc thực thi, Phase 1 — Core state (nền cho mọi thứ còn lại), Phase 2 — Lưới an toàn không trượt vì transcript trễ, Phase 3 — Nhắc & chỉ dẫn, Phase 4 — Đóng gói & nghiệm thu, PLAN — Yêu cầu mới ⇒ state được đồng bộ lại theo lane user chọn (0.1.7), Edge case đã kiểm (+25 more)

### Community 10 - "TestPromptContext"
Cohesion: 0.10
Nodes (9): now_iso(), session_start.py + prompt_context.py (0.3.0) — bơm context theo state., P1-6/P1-7 — không có gì đang chờ duyệt, nội dung NEXT y hệt turn trước         →, Đổi phase giữa 2 turn → KHÔNG được gọn hoá, phải in đủ nội dung mới., Trần 600 ký tự không được cắt mất dòng luật hay dòng lệnh., A22 — cắt MAX_CHARS không được đứt giữa inline-code (nửa lệnh = lệnh sai)., TestPromptContext, TestSessionStart (+1 more)

### Community 11 - "test_token_audit.py"
Cohesion: 0.10
Nodes (14): _assistant(), _assistant_line(), CarryCostTest, CliTest, CostEquivalentTest, IterEventsTest, MessageIdTest, Test cho scripts/token_audit.py — đo carry-cost của tool output trong transcript (+6 more)

### Community 12 - "Working log — 2026-07-28"
Cohesion: 0.06
Nodes (30): ~00:30 — Detect bug approve_gate không ghi state (báo từ project insightfaceserverv2), ~00:35 — Implement fix approve_gate matcher (user đã gõ lệnh duyệt quick; hook duyệt fail im lặng do chính bug này — live repro), ~00:45 — Setup test live sau restart (user yêu cầu verify fix), ~00:45 — Verify live PASS + dọn test, ~09:04 — Request `fix-implement-mode-gate` (lane quick, ĐÃ DUYỆT), ~09:20 — Mở request `2026-07-28-fix-invite-without-request` (lane quick, CHỜ DUYỆT), ~09:25 — Đóng turn: graphify + dọn, ~09:30 — Commit (user duyệt "okay commit") (+22 more)

### Community 13 - "Working Log — 2026-08-04"
Cohesion: 0.06
Nodes (30): 12:17 — Mở request export Claude Code setup, 12:27 — Phase analyze hoàn tất (lane full), 12:30 — Bổ sung quyết định: bộ công cụ export lưu trong repo, 12:45 — Viết spec + review + sửa theo 5 góp ý tdq-reviewer, 13:05 — Viết plan (mode main) + fix bug doc_lint.py chặn pair-check, 13:15 — Sửa plan theo 7 góp ý tdq-reviewer + đăng ký state, 14:03 — Duyệt plan (mode main), chuyển phase implement, 14:24 — Chặn kỹ thuật T4.2: rsync T2.5 lọt data loại trừ vào bundle (+22 more)

### Community 14 - "token_audit.py"
Cohesion: 0.11
Nodes (30): _all_items(), carry_cost(), classify(), _content_text(), cost_equivalent(), default_transcript_dir(), find_sessions(), _fmt() (+22 more)

### Community 15 - "TestBashGate"
Cohesion: 0.12
Nodes (4): B3 — bash_gate.py: NHẮC (allow + additionalContext) về quy ước git và state.json, P0-3 — 1 invoke `main()` chỉ đọc `.tdq-turn.jsonl` đúng 1 lần, dù cả     `_check, TestBashGate, TestBashGateSingleTurnRead

### Community 16 - ".run_cli"
Cohesion: 0.13
Nodes (8): BrokenInputTest, EnableTest, IdempotentTest, LogTest, Test cho scripts/plugin_tiers.py — HOME giả trong tmpdir., ResetTest, StatusTest, TierBase

### Community 17 - "Working log 2026-08-03"
Cohesion: 0.07
Nodes (29): 12:30 — Mở request check-external-assign-flow, 12:35 — Analyze check-external-assign-flow (lane full), 12:38 — Chốt analyze check-external-assign-flow, 12:45 — Spec 1.1 check-external-assign-flow, 12:50 — Spec 1.2 check-external-assign-flow (góp ý user), 12:58 — Plan check-external-assign-flow, 13:38 — Mở request check-claude-md-sync, 13:40 — Hoàn tất build + QC + report request check-external-assign-flow (+21 more)

### Community 18 - "Changelog"
Cohesion: 0.10
Nodes (27): 0.10.0 — 2026-08-09, 0.11.0 — 2026-08-09, 0.11.1 — 2026-08-09, 0.11.2 — 2026-08-09, 0.1.0 — 2026-07-27, 0.1.4 — 2026-07-28, 0.1.6 — 2026-07-28, 0.2.0 — 2026-07-28 (+19 more)

### Community 19 - "Spec: TDQWorkflow Plugin cho Claude Code"
Cohesion: 0.07
Nodes (27): 10. QC / test / validate cho chính plugin (checklist rule 9), 11. Deliverables (Expect_Output), 12. Giới hạn & rủi ro (minh bạch), 1. Ý tưởng & mục tiêu, 2.1 Trong scope (MVP), 2.2 Ngoài scope (MVP), 2. Scope, 3.1 Lazy load & ngân sách token (bắt buộc) (+19 more)

### Community 20 - "_project"
Cohesion: 0.15
Nodes (12): DryRunTest, LogServiceTest, OutputSizeTest, _project(), Test cho scripts/tdq_finish.py — gộp 4 việc bookkeeping cuối turn thành 1 lệnh., T3.3 — log service bật mặc định, tắt bằng TDQ_LOG=0., T3.4 — mọi bước pass thì stdout ≤ 200 ký tự; chi tiết chỉ khi --verbose., Dựng project giả có state TDQ + 1 file .md sạch để lint. (+4 more)

### Community 21 - ".build"
Cohesion: 0.13
Nodes (8): BuildConfigTest, BuildGuardTest, BuildLogTest, BuildRepoTest, BuildSecretScanTest, BuildZipTest, Fixture, Dựng máy nguồn giả + đích trong thư mục tạm cho mỗi ca.

### Community 22 - "Working log — 2026-07-31"
Cohesion: 0.08
Nodes (24): 14:14–14:22 — Research (không đổi repo, ghi gộp ở entry sau), 14:23–14:30 — TDQ intake + analyze: request 2026-07-31-agy-search-agent (lane full), 14:34–14:45 — Phase spec: 2026-07-31-agy-search-agent (bản 1.1, CHỜ DUYỆT), 14:47–14:55 — Phase plan: 2026-07-31-agy-search-agent (CHỜ DUYỆT), 15:00–15:25 — Build + QC 2026-07-31-agy-search-agent (mode main), 15:22–15:35 — QC vòng 2: fix trigger search-runner qua Agent tool, 15:36–15:40 — Trigger test PASS + đóng QC vòng 2 + commit 0.5.0, 15:39 — Benchmark deep search: Run A (agy) khởi động (+16 more)

### Community 23 - "Working log — 2026-07-30"
Cohesion: 0.08
Nodes (23): ~00:05–08:38 — Tổng kiểm workflow + audit 43 plugin (chỉ đọc/phân tích), 11:07 — Mở request mới: tối ưu plugin user-level + lazy-load (tdq-intake Phần A), 12:05 — Analyze request plugin-lazy-load (lane full), 12:3x — Đóng interview vòng 1, chốt knowledge, phase=spec, 14:16 — Viết spec plugin-lazy-load v1.0 (phase spec), 14:24 — Spec được duyệt, 14:25 — Viết plan plugin-lazy-load (phase plan), 14:46–15:00 — Implement end-to-end request plugin-lazy-load (mode main) + QC + report (+15 more)

### Community 24 - "tdq_finish.py"
Cohesion: 0.16
Nodes (20): _changed_files(), _log(), _log_enabled(), main(), _now(), parse_args(), _project_dir(), Một dòng ≤ 200 ký tự cho trường hợp mọi bước pass. (+12 more)

### Community 25 - "ProtocolTest"
Cohesion: 0.22
Nodes (3): ProtocolTest, P2 — giao thức tuân thủ: nhắc có mã, quan sát hiệu ứng, đối chiếu ở Stop.  Nguyê, rows()

### Community 26 - "TestEditGate"
Cohesion: 0.20
Nodes (4): now_iso(), edit_gate.py (0.3.0) — quan sát vào sổ turn + nhắc; không bao giờ chặn., TestEditGate, today_log_rel()

### Community 28 - "Working log 2026-08-09"
Cohesion: 0.09
Nodes (21): 00:15 — đóng request giảm over-engineer workflow, 00:25 — đồng bộ CLAUDE.md, bump 0.10.0, commit, 00:52, 00:56, 00:58, 01:13, 01:28 — Bump 0.11.0 và commit, 11:23 — Mở request sửa mô tả skill trong kiểm kê năng lực (+13 more)

### Community 29 - "StateFileTest"
Cohesion: 0.21
Nodes (4): run_state_cli(), P1 — xử lý state file: S1–S8 của spec 0.3.0 (mỗi yêu cầu 1 test)., _read(), StateFileTest

### Community 30 - "_common.py"
Cohesion: 0.21
Nodes (16): approve_hint(), payload_cwd(), plan_mode(), Helper dùng chung cho hook TDQ (chỉ stdlib).  Giao thức tuân thủ 0.3.0 (spec §2., Mode đã chốt trong plan_file (dòng 'Mode thực thi:'), None nếu chưa ghi., Project root cho state — cwd của payload có thể là thư mục con/worktree., read_payload(), session_id() (+8 more)

### Community 31 - "skill_inventory.py"
Cohesion: 0.16
Nodes (17): _clean(), _condense(), _enabled_plugins(), _frontmatter(), inventory(), _load_json(), main(), _plugin_skill_dirs() (+9 more)

### Community 32 - "test_e2e_chain.py"
Cohesion: 0.24
Nodes (10): decision(), load_fixture(), Parse PreToolUse hook stdout -> (permissionDecision, additionalContext).      0., read_state(), write_file(), ChainBase, E1 — chuỗi end-to-end cả hai lane theo mô hình 0.3.0.  User duyệt bằng chat → Cl, TestFullLaneChain (+2 more)

### Community 33 - "Spec — tối ưu token/time workflow (vòng 2)"
Cohesion: 0.12
Nodes (16): 1. Mục tiêu & phạm vi, 1b. Lộ trình, 2. Bảng phán quyết CLAUDE.md (user soát từng dòng), 3. Cách tiếp cận + lý do, 3b. Năng lực & công cụ, 4. Nhóm việc & đầu ra đo đếm được, 5. Yêu cầu bắt buộc, 6. Ràng buộc & rủi ro (+8 more)

### Community 34 - "plugin_tiers.py"
Cohesion: 0.34
Nodes (16): _claude_dir(), cmd_enable(), cmd_reset(), cmd_status(), _key_for(), _load_json(), _log(), _log_on() (+8 more)

### Community 35 - "_run"
Cohesion: 0.21
Nodes (6): prompt_context.py — nhắc [TDQ:INTAKE] khi KHÔNG có request mở (spec 2026-08-02)., T1.1-T1.4 (2026-08-04-approval-gate-bug): looks_like_approval() phải lưu     lại, _run(), TestIntakeReminder, TestSignalWritten, write_file_plan_mode()

### Community 36 - "test_quick_qc.py"
Cohesion: 0.16
Nodes (8): QuickQcApprovalHintTest, QuickQcDocTest, QuickQcPhasesDocTest, Lane quick: QC bám DoD (mặc định BẬT) + vòng fix trần 3 vòng.  Khoá cứng 4 nguồn, N4: phases.md là doc tự sinh — khớp render_phases_md() từng ký tự., Hook phải mách user đúng biến thể, và không lọc nó thành câu hỏi., N1: quick-lane.md phải định nghĩa QC, không chỉ nói 'chạy validate'., read()

### Community 37 - "Kiến thức chốt — audit tối ưu token/time workflow (vòng 3)"
Cohesion: 0.12
Nodes (15): 1. Số liệu đo hiện tại (sau các fix vòng 2), 2. Đối chiếu vòng 1 + vòng 2 (agent D), 3. Phát hiện mới (vòng 3) — token/thời gian, 4. Phát hiện mới (vòng 3) — issue logic/an toàn (user đã chốt: đưa vào report), 5. Nguyên tắc rút ra từ research ngoài (4 truy vấn tavily-primary, 12 finding), 6. Quyết định đã chốt (interview vòng 1 lúc mở request + vòng 2 lúc 11:18), 7. Phương án đã loại, 8. Nguồn (+7 more)

### Community 38 - "SPEC — Vá điểm mù của verify-by-effect (sổ turn chỉ thấy Edit/Write)"
Cohesion: 0.12
Nodes (15): 1. Bối cảnh & triệu chứng, 2. Nguyên nhân gốc, 3. Các phương án đã cân nhắc, 4. Thiết kế, 5. Ngoài phạm vi, 6. Phạm vi test (mỗi task 1 test, red → green), 7. Definition of Done, 8. Rủi ro & giảm thiểu (+7 more)

### Community 39 - "Working log — 2026-08-02"
Cohesion: 0.12
Nodes (15): 11:31 — Mở request tdq-default-cleanup, 11:36 — Analyze xong tdq-default-cleanup (lane full), 11:47 — Spec v1.1 tdq-default-cleanup, 11:52 — Plan tdq-default-cleanup trình duyệt, 12:01 — Build + QC + report tdq-default-cleanup (HOÀN THÀNH), 13:05 — Mở request fix-approve-hint-mode, 13:22 — Quick approved: fix-approve-hint-mode (mini-plan), 13:30 — Fix-approve-hint-mode HOÀN THÀNH (quick) (+7 more)

### Community 40 - "test_agent_frontmatter.py"
Cohesion: 0.21
Nodes (7): AgentDigestLimitTest, AgentFrontmatterTest, field(), frontmatter(), P2 — mọi agent phải khai rõ `model` và `effort` trong frontmatter.  Lý do: `effo, Agent làm việc chất lượng không được ép nghĩ nông (effort thấp)., Request toi-uu-token-vong-2 (T5.1/T5.2) — agent trả DIGEST, không trả     nguyên

### Community 41 - "test_claude_export.py"
Cohesion: 0.12
Nodes (7): ParseArgsTest, Test cho scripts/claude_export.py — bộ export cấu hình Claude Code sang máy khác, Mặc định tắt bước dò version CLI: 8 lệnh `--version` mỗi lần build là quá chậm., Template trong `claude-export/` là thứ script nạp thật, không phải văn bản trang, ReadMcpServersTest, run_cli(), TemplateTest

### Community 42 - "PhaseTableTest"
Cohesion: 0.12
Nodes (7): PhaseTableTest, P1/P3 — PHASE_TABLE là nguồn sự thật duy nhất; doc phải khớp hằng trong code., A6: lane quick phải có terminal — quick_approved + phase=idle là đã xong., Bug A1: escape sai trong re.sub → literal `\\1` thay vì lệnh thật., A26: dòng duyệt quick khớp intake (biến thể bỏ QC); A6: có bước đóng., A40: bản chạy trong ngữ cảnh plugin phải in path plugin-root., Mỗi phase phải xuất hiện trong doc kèm đúng lệnh chuyển tiếp.          A40: bản

### Community 43 - "TokenBudgetTest"
Cohesion: 0.21
Nodes (5): budget(), P5 — ngân sách token của spec §2.7, đo thật chứ không phải khuyến nghị.  Mỗi ký, Sinh state cho mọi phase — trần phải đúng ở phase dài nhất, không chỉ phase dễ., description của mọi skill luôn nằm trong context — tổng phải gọn., TokenBudgetTest

### Community 44 - "PLAN — Kiểm kê & tận dụng skill phụ trợ (0.3.3)"
Cohesion: 0.13
Nodes (14): Definition of Done, Năng lực → task, P1 — `scripts/skill_inventory.py` + test, P2 — Bước B0 trong `tdq-intake`, P3 — Khuôn spec §3b + hợp đồng 6 trường ở plan, P4 — `doc_lint.py`: R8 + `--pair`, P5 — `tdq-build` thi hành hợp đồng, P6 — `PHASE_TABLE` + `phases.md` (+6 more)

### Community 45 - "PLAN — Giảm over-engineer & over-test cho TDQ workflow"
Cohesion: 0.13
Nodes (14): Definition of Done, Năng lực → task, P1 — Sửa `doc_lint` (D7), P2 — Xoá nhánh external và deep search (D3), P3 — Xoá `portable/` (D4), P4 — Gộp output thành `brief/` (D5), P5 — Tầng `nhỏ` và QC bám DoD (D1, D2), P6 — Rút gọn skill nặng (D6) (+6 more)

### Community 46 - "Working log — 2026-07-27"
Cohesion: 0.13
Nodes (14): ~16:30 — Lập spec cho TDQWorkflow plugin, ~16:50 — Đổi đường dẫn working log theo yêu cầu người dùng, ~17:10 — Bổ sung quy tắc khai thác Tavily vào spec, ~17:25 — Check lazy load, bổ sung mục 3.1 vào spec, ~17:35 — Approve gate luôn hướng dẫn user lệnh duyệt, ~17:50 — Approve validate bằng state + detail file; vá lỗ hổng state.json, ~18:05 — Lane quick có cửa duyệt nhẹ + ghi summary plan vào working log trước implement, ~18:20 — User duyệt spec v0.1.6; lập plan (+6 more)

### Community 47 - "Working log 2026-07-29"
Cohesion: 0.13
Nodes (14): ~00:05 — User duyệt spec 0.3.0 → viết plan, ~01:00–01:40 — Implement plan 0.3.0 end-to-end (P3 → P8), ~02:10 — Phân tích + viết spec fix điểm mù verify-by-effect, ~02:30 — User duyệt spec → viết plan, ~02:45–03:30 — Implement plan 0.3.1 end-to-end (mode main), ~04:00 — Audit toàn bộ tdq-workflow 0.3.1 (theo yêu cầu user), ~04:15 — User duyệt fix 0.3.2 → plan, ~04:20–05:00 — Implement 0.3.2 end-to-end (mode main) (+6 more)

### Community 48 - "tdq-conventions/SKILL.md"
Cohesion: 0.17
Nodes (7): Khuôn report, Kiểm trước khi trình, Tiết kiệm context, Các bước, TDQ Plan, Các bước, TDQ Spec

### Community 49 - "helper.py"
Cohesion: 0.18
Nodes (7): Shared test utilities: run hook scripts as subprocesses with stdin JSON., Chạy CLI với process cwd = cwd và KHÔNG set TDQ_PROJECT_DIR (giống user     gõ l, run_hook(), run_state_cli_in(), P2/T2.12 — hook không bao giờ làm hỏng tool call (spec §4.7).  Mọi hook × mọi tr, ResilienceTest, P2 — sổ turn docs/tdq/.tdq-turn.jsonl (T2.1, T2.2).

### Community 50 - "PLAN — TDQ 0.3.0 (instruction-hardening-7b)"
Cohesion: 0.14
Nodes (13): Definition of Done, P1 — CLI `scripts/tdq_state.py`: state file, mirror, PHASE_TABLE, next, get, P2 — Hook: sổ turn, mã nhắc, đối chiếu bằng hiệu ứng, P3 — Skills 9 → 5 (+ conventions), P4 — Bản portable, P5 — Lint + test ngân sách token, P6 — Dọn dẹp, P7 — Đóng gói 0.3.0 (+5 more)

### Community 51 - "PLAN — Search agent "deep search" dùng agy CLI, tích hợp TDQ workflow"
Cohesion: 0.14
Nodes (13): Definition of Done, Năng lực → task, P1 — Schema + khung script + env, P2 — Subcommand `split` (cap bằng code), P3 — Subcommand `run` (1 agent chạy các route được giao), P4 — Subcommand `merge` (rank tất định bằng code), P5 — Agent vỏ mỏng + khuôn orchestrator, P6 — Tích hợp tầng search + config (+5 more)

### Community 52 - "PLAN — Triển khai 16 đề xuất P0+P1 tối ưu workflow TDQ & user-level Claude Code"
Cohesion: 0.14
Nodes (13): Definition of Done, Năng lực → task, P1 — Cụm script/hook lõi (`scripts/`, `hooks/scripts/`) — đầu ra #1, #2, #11, #12 spec §2, P2 — Cụm skill `tdq-build` (`skills/tdq-build/`) — đầu ra #5, #10, #14, #16 spec §2, P3 — Cụm skill `tdq-intake` (`skills/tdq-intake/`) — đầu ra #3, #6, #7 spec §2, P4 — Cụm skill `tdq-conventions` (`skills/tdq-conventions/`) — đầu ra #4, #9, #15 spec §2, P5 — Cụm test khoá đồng bộ (`tests/`) — đầu ra #8 spec §2, P6 — Đóng sổ (chạy SAU khi P1-P5 đã merge về nhánh chính) (+5 more)

### Community 53 - "MultiRepoTest"
Cohesion: 0.24
Nodes (5): _git(), LaunchAgentPlistTest, MultiRepoTest, P2: nhiều repo local dependency đọc từ `local-repos.json`., P3: copy plist LaunchAgent khớp tên repo local, chỉ để tham khảo.

### Community 54 - "PLAN — Bump 0.7.0 + bộ export Claude Code chạy bằng một lệnh"
Cohesion: 0.15
Nodes (12): Definition of Done, Năng lực → task, P1 — Bump 0.7.0, P2 — Khung `claude_export.py` + lớp thu thập nguồn, P3 — Lệnh `build`, P4 — Lệnh `check` (đo drift), P5 — Tài liệu bộ export, P6 — Sinh bundle thật + zip (+4 more)

### Community 55 - "PLAN — Tối ưu token/time workflow (vòng 2)"
Cohesion: 0.15
Nodes (12): Definition of Done, Giao việc theo phase (khi user chốt mode `subagent`), Mục QC (thêm task fix ở đây khi FAIL), Năng lực → task, P1 — Đo cho đúng trước đã (spec §4 nhóm E), P2 — Cắt context nền (spec §4 nhóm A), P3 — Một lệnh cuối turn (spec §4 nhóm B, task B1), P4 — Đưa luật vào skill và portable (spec §4 nhóm B, C, D, E) (+4 more)

### Community 56 - "QC — giảm over-engineer workflow TDQ"
Cohesion: 0.15
Nodes (12): Bằng chứng, Khiếm khuyết agent tìm ra — đã đối chiếu lại, đều đúng, Kết luận, Kết luận vòng 1, Q1 — phân loại lại 5 request cũ theo tầng mới, Q3 — chỗ còn chữ "external", Q8 — suite, Q9 — 5 hook với state giả (`TDQ_PROJECT_DIR` tạm, phase=implement, spec chưa duyệt) (+4 more)

### Community 57 - "Working log 2026-08-08"
Cohesion: 0.15
Nodes (12): 00:15 (2026-08-09), 15:36 — đóng sổ request 2026-08-07-siet-qc-lane-quick (commit 704ac3f), 21:53, 21:59, 22:13, 22:19, 22:40, 22:41 (+4 more)

### Community 58 - "TestProjectRootResolution"
Cohesion: 0.17
Nodes (3): A3 — tdq_state.py: default schema, CLI, protected keys, atomic write., State phải luôn về MỘT file ở project root — chạy CLI từ thư mục con     không đ, TestProjectRootResolution

### Community 59 - "PLAN — Hybrid deep search 0.6.0 (scout ∥ agy tổng quát → agy đào sâu)"
Cohesion: 0.17
Nodes (11): Definition of Done, Năng lực → task, P1 — search_task.py: default model + start-agent (đầu ra #1, #2), P2 — Agent scout + doc quy ước (đầu ra #3, #4), P3 — Docs khớp + version 0.6.0 (đầu ra #5, #6), P4 — Log & test bắt buộc, P5 — E2E hybrid + QC (đầu ra #7; Q3, Q4, Q6, Q8-dương), P6 — Đóng turn (+3 more)

### Community 60 - "PLAN — Full claude export (multi-repo local dependency)"
Cohesion: 0.17
Nodes (11): Definition of Done, Năng lực → task, P1 — Config danh sách repo local, P2 — Multi-repo clone trong `claude_export.py`, P3 — Tổng quát `skills/` + copy LaunchAgent plist, P4 — Manifest/README/check hỗ trợ N repo, P5 — Log & test bắt buộc, P6 — Build thật + QC trên máy nguồn (+3 more)

### Community 61 - "Đợt 1 (21:13) — khả thi tổng quát"
Cohesion: 0.17
Nodes (11): Q1: "use OpenAI Codex CLI as subagent inside Claude Code delegate tasks", Q2: "codex exec non-interactive headless", Q3: "Google Antigravity CLI headless", Q4: "codex mcp-server Claude Code", Q5: cách cài codex-plugin-cc, Q6: model slug Codex hiện hành, Q7: thiết kế prompt cho model cấp thấp/context ngắn, RESEARCH — external-agent-mode (+3 more)

### Community 62 - "TDQ Conventions"
Cohesion: 0.17
Nodes (12): 10. Tiết kiệm context (bắt buộc), 11. Chất lượng, 1. Giao thức một turn (bắt buộc, làm đúng thứ tự), 2. Bảng phase, 3. State, 4. Ghi nhận duyệt, 5. Cây tài liệu, 6. Working log (+4 more)

### Community 63 - "CheckTest"
Cohesion: 0.29
Nodes (3): CheckTest, Manifest hỏng là bundle không hợp lệ (2), không phải drift (1)., SHA cũ không có trong repo thì nói thẳng, không in `(+?)`.

### Community 64 - "test_claude_md_core.py"
Cohesion: 0.20
Nodes (7): CoreFileTest, InvariantRulesTest, MovedRulesTest, Chống bỏ sót khi rút gọn ~/.claude/CLAUDE.md (spec 2026-08-05 §2).  3 điều kiện,, (a) Luật đã chuyển phải nằm ở file đích, nếu không là mất luật., (b) Luật bất biến phải còn nguyên trong bản mẫu., _read()

### Community 65 - "NextTest"
Cohesion: 0.17
Nodes (3): NextTest, P1 — lệnh `next`, `next --brief`, `get <key>` (spec §2.2)., QC1.1 — tiêu đề phải nói đúng phase mà thân bài đang dùng.          Lane quick g

### Community 66 - "Quy tắc làm việc cho Claude"
Cohesion: 0.18
Nodes (10): 1. Quy trình chung, 2. Git & worktree, 3. Research & độ tin cậy, 4. Trình bày, 5. Log, 6. TDQ Workflow — mặc định tuyệt đối, 7. Chi tiết ở đâu — đọc khi cần, KHÔNG chép lại vào đây, 8. Plugin ngoài (+2 more)

### Community 67 - "Hiểu & kiến thức"
Cohesion: 0.18
Nodes (10): BRIEF — Cắt token thừa trong TDQ workflow, Hiểu & kiến thức, Hỏi đáp, Lộ trình, Nguyên văn, Năng lực dùng được, Ranh giới — KHÔNG đụng (đã xác định là có giá trị), Research web (+2 more)

### Community 68 - "ĐỀ XUẤT — Tối ưu time/token cho TDQ workflow"
Cohesion: 0.18
Nodes (10): Giả định & cách kiểm chứng lại, Mô hình chi phí, Nguyên nhân (mỗi dòng có số đo thật), Nhóm A — Cắt carry-cost của việc đọc và của CLI (L1), Nhóm B — Đẩy việc nặng sang subagent (L1), Nhóm C — Cắt context nền (L3), Nhóm D — Giảm số API call (L2), Nhóm E — Giảm output token & vệ sinh session (L2 + L3) (+2 more)

### Community 69 - "Kiến thức chốt — tối ưu token/time workflow (vòng 2)"
Cohesion: 0.18
Nodes (10): 1. Mô hình chi phí đã hiệu chỉnh, 2. Số liệu đo (2 session gần nhất, đã khử trùng lặp), 3. Nguyên nhân (đã đo, không suy đoán), 4. Quyết định đã chốt (interview 00:52 + 00:58), 5. Phương án đã loại, 6. Nguồn, Kiến thức chốt — tối ưu token/time workflow (vòng 2), Lộ trình (+2 more)

### Community 70 - "PLAN — Audit tổng thể TDQ workflow 0.6.0 — HOÀN THÀNH"
Cohesion: 0.18
Nodes (10): Definition of Done, Năng lực → task, P1 — Fix issue đã biết + khung sổ findings, P2 — Hai việc chạy dài: deep search + S1 (khởi động NGAY đầu build, chạy nền), P3 — Review tĩnh chéo (chạy song song lúc chờ P2), P4 — Sample S2 + fix issue S/M, P5 — Log & test bắt buộc, P6 — QC, report, đóng sổ (+2 more)

### Community 71 - "PLAN — TDQ workflow là default tuyệt đối + bỏ §5 superpower"
Cohesion: 0.18
Nodes (10): Definition of Done, Năng lực → task, P0 — Nền (đã xong ở analyze), P1 — Hook [TDQ:INTAKE] (red → green), P2 — CLAUDE.md user-level, P3 — Skill tdq-intake, P4 — QC & đóng, PLAN — TDQ workflow là default tuyệt đối + bỏ §5 superpower (+2 more)

### Community 72 - "PLAN — TDQ workflow linh hoạt & bớt ma sát"
Cohesion: 0.18
Nodes (10): Definition of Done, Năng lực → task, P1 — Nguồn sự thật: PHASE_TABLE + phases.md (đầu ra #2, #3, #6, #10), P2 — Heuristic model/effort cho sub-agent (đầu ra #8, #9), P3 — Skill: gộp gate, bỏ reviewer mặc định, lộ trình (đầu ra #1, #2, #3, #4, #7), P4 — Lane quick mới + luật hỏi mở (đầu ra #5, #6, #7), P5 — Đồng bộ portable, CLAUDE.md, rà chất lượng (đầu ra #11, #12), P6 — Log & test bắt buộc (+2 more)

### Community 73 - "PLAN — Skill clone-setting-to-codex"
Cohesion: 0.18
Nodes (10): Definition of Done, Năng lực → task, P1 — Scaffold skill, P2 — Script codex_clone.py: khung + convert 3 loại, P3 — Subcommand apply + build, P4 — Log & test bắt buộc, P5 — Chạy thật + review + QC, PLAN — Skill clone-setting-to-codex (+2 more)

### Community 74 - "PLAN — Siết QC và vòng fix cho lane quick"
Cohesion: 0.18
Nodes (10): Definition of Done, Năng lực → task, P1 — Test đỏ trước (khoá hành vi bằng máy), P2 — `scripts/tdq_state.py` (nguồn sự thật N3 + cờ opt-out), P3 — `skills/tdq-intake` (nguồn sự thật N1 + N2), P4 — Bản portable (nguồn sự thật N4), P5 — Log & test bắt buộc, P6 — QC (+2 more)

### Community 75 - "QC — 2026-07-31-audit-full-workflow"
Cohesion: 0.18
Nodes (10): Bảng QC Q1–Q10 (T6.1), Bảng token deep search (T2.2), Findings, Findings S1 — quick external model thấp (T2.5), Findings S2 — full mini + 3 nhánh sự cố (T4.1–T4.4), QC — 2026-07-31-audit-full-workflow, Review tĩnh lớp 1 (T3.1–T3.3), T3.1 — skills + references + portable + CLAUDE.md §10 (candidates từ reviewer phụ, đã tự xác minh 10/10 điểm S/M bằng grep/sed dòng trích dẫn) (+2 more)

### Community 76 - "SPEC — TDQ 0.3.0: tuân thủ kiểm được, state đọc được, workflow đủ rõ cho mọi model"
Cohesion: 0.18
Nodes (11): 1.1 Mục tiêu, 1.2 In-scope, 1.3 Out-of-scope, 1. Mục tiêu & phạm vi, 3. Kiến trúc & lý do chọn, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. Phạm vi QC / test / validate (điều kiện pass đo được) (+3 more)

### Community 77 - "2. Đầu ra cụ thể"
Cohesion: 0.18
Nodes (11): 2.10 Dọn dẹp gộp vào, 2.11 Cập nhật `~/.claude/CLAUDE.md` §10, 2.1 Giao thức tuân thủ: nhắc có mã → quan sát hiệu ứng → đối chiếu cuối turn, 2.2 CLI: `next` và `get <key>`, 2.4 Skills 9 → 5 (+ conventions), 2.5 Bản portable (chạy ngoài Claude Code), 2.6 Lint chất lượng doc, 2.7 Ngân sách token (có test đo, không phải khuyến nghị) (+3 more)

### Community 78 - "SPEC — TDQ workflow là default tuyệt đối + bỏ mục superpower (mục 5 cũ)"
Cohesion: 0.18
Nodes (10): 1. Mục tiêu & phạm vi, 1b. Mapping số mục CLAUDE.md (cũ → mới, sau khi xóa §5), 2. Đầu ra cụ thể, 3. Cách tiếp cận & lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. QC & Definition of Done (+2 more)

### Community 79 - "SPEC — Đưa skill vào gói external (hybrid 3 nhánh)"
Cohesion: 0.18
Nodes (10): 1. Mục tiêu & phạm vi, 2. Đầu ra cụ thể, 3. Cách tiếp cận & lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. QC & Definition of Done, 7. Câu hỏi còn mở (+2 more)

### Community 80 - "SPEC — 2026-08-04-approval-gate-bug"
Cohesion: 0.18
Nodes (10): 1. Mục tiêu & phạm vi, 2. Đầu ra cụ thể, 3. Cách tiếp cận & lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. QC & Definition of Done, 7. Câu hỏi còn mở (+2 more)

### Community 81 - "SPEC — Đề xuất tối ưu time/token cho TDQ workflow"
Cohesion: 0.18
Nodes (10): 1. Mục tiêu & phạm vi, 1b. Lộ trình, 2. Đầu ra cụ thể, 3. Cách tiếp cận & lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. QC & Definition of Done (+2 more)

### Community 82 - "SPEC — Audit toàn bộ workflow TDQ, đề xuất tối ưu token/thời gian (vòng 3)"
Cohesion: 0.18
Nodes (10): 1. Mục tiêu & phạm vi, 1b. Lộ trình, 2. Đầu ra cụ thể, 3. Cách tiếp cận & lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. QC & Definition of Done (+2 more)

### Community 83 - "SPEC — Bump 0.7.0 + bộ export Claude Code đầy đủ, chạy được bằng một lệnh"
Cohesion: 0.18
Nodes (10): 1. Mục tiêu & phạm vi, 1b. Lộ trình, 2. Đầu ra cụ thể, 3. Cách tiếp cận & lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. QC & Definition of Done (+2 more)

### Community 84 - "SPEC — Skill clone-setting-to-codex"
Cohesion: 0.18
Nodes (10): 1. Mục tiêu & phạm vi, 1b. Lộ trình, 2. Đầu ra cụ thể, 3. Cách tiếp cận & lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. QC & Definition of Done (+2 more)

### Community 85 - "SPEC — Full claude export (multi-repo local dependency)"
Cohesion: 0.18
Nodes (10): 1. Mục tiêu & phạm vi, 1b. Lộ trình, 2. Đầu ra cụ thể, 3. Cách tiếp cận & lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. QC & Definition of Done (+2 more)

### Community 86 - "SPEC — Triển khai 16 đề xuất P0+P1 tối ưu workflow TDQ & user-level Claude Code"
Cohesion: 0.18
Nodes (10): 1. Mục tiêu & phạm vi, 1b. Lộ trình, 2. Đầu ra cụ thể, 3. Cách tiếp cận & lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. QC & Definition of Done (+2 more)

### Community 87 - "SPEC — Siết QC và vòng fix cho lane quick"
Cohesion: 0.18
Nodes (10): 1. Mục tiêu & phạm vi, 1b. Lộ trình, 2. Đầu ra cụ thể, 3. Cách tiếp cận & lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. QC & Definition of Done (+2 more)

### Community 88 - "SPEC — Giảm over-engineer & over-test cho TDQ workflow"
Cohesion: 0.18
Nodes (10): 1. Mục tiêu & phạm vi, 1b. Lộ trình, 2. Đầu ra cụ thể, 3. Cách tiếp cận & lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. QC & Definition of Done (+2 more)

### Community 89 - "SPEC — Cắt token thừa trong TDQ workflow"
Cohesion: 0.18
Nodes (10): 1. Mục tiêu & phạm vi, 1b. Lộ trình, 2. Đầu ra cụ thể, 3. Cách tiếp cận & lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. QC & Definition of Done (+2 more)

### Community 90 - "bash_gate.py"
Cohesion: 0.31
Nodes (10): _check_signal_mismatch(), _clean(), _latest_signal(), main(), Dòng kind="signal" GẦN NHẤT khớp target (duyệt ngược sổ turn)., echo_line(), observe(), Như `remind()` nhưng KHÔNG dedupe theo mã — dùng khi một mã đã bị hook     khác (+2 more)

### Community 91 - "stop_gate.py"
Cohesion: 0.29
Nodes (10): turn_rows(), _log_changed(), main(), Ảnh chụp đầu turn — lấy dòng MỚI NHẤT.      Bình thường mỗi turn chỉ có một dòng, Log hôm nay có đổi so với đầu turn không (bất kể ghi bằng cách nào)., Tên file để nêu trong lời chặn — ưu tiên file mới xuất hiện trong turn.      Chu, _repo_changed(), _sha() (+2 more)

### Community 92 - "tdq-intake/SKILL.md"
Cohesion: 0.24
Nodes (5): Phần B — Phân tích (phase `analyze`, chỉ lane full), Khuôn mini-spec/plan (≤ 40 dòng), Lane quick — chi tiết, QC ở quick, Vòng fix

### Community 93 - "ScanSecretsTest"
Cohesion: 0.18
Nodes (3): P3: `CONFIG_DIRS` phải tự nhặt MỌI skill dưới `skills/`, không hard-code., ScanSecretsTest, SkillsGeneralizeTest

### Community 94 - "GateMergeTest"
Cohesion: 0.27
Nodes (4): GateMergeTest, P3 — luật gộp gate: duyệt spec → plan NGAY, duyệt plan+mode → build NGAY.  Bốn b, Bước quyết lộ trình phải có mặt ở intake (ghi) và spec (chép lại)., read()

### Community 95 - "Knowledge — 2026-08-03-check-external-assign-flow"
Cohesion: 0.20
Nodes (9): Bổ sung (user, 12:39): trigger qua subagent, Kiểm cổng, Knowledge — 2026-08-03-check-external-assign-flow, Kết luận, Nguồn, Năng lực dùng được, Phát hiện (nguồn: skills/tdq-build/SKILL.md dòng 53–87, 98–101), Phạm vi đụng tới (ước lượng) (+1 more)

### Community 96 - "KNOWLEDGE — Bump version + export đầy đủ hơn"
Cohesion: 0.20
Nodes (9): 8 lỗ hổng đã đo của bundle 2026-08-04, Cách tiếp cận đã chọn, KNOWLEDGE — Bump version + export đầy đủ hơn, Lộ trình, Nguồn, Năng lực dùng được, Phương án đã loại, Quyết định đã chốt (user trả lời vòng 1) (+1 more)

### Community 97 - "Knowledge — 2026-08-05-clone-setting-codex"
Cohesion: 0.20
Nodes (9): Kiểm cổng, Knowledge — 2026-08-05-clone-setting-codex, Lộ trình, Nguồn, Năng lực dùng được, Phương án đã loại, Quyết định đã chốt, Research (2 phase, 4 agent, 12 finding sau dedup — nguồn chính thức OpenAI trừ khi (+1 more)

### Community 98 - "KNOWLEDGE — Brainstorm + spec triển khai P0+P1 tối ưu workflow & user-level Claude Code"
Cohesion: 0.20
Nodes (9): KNOWLEDGE — Brainstorm + spec triển khai P0+P1 tối ưu workflow & user-level Claude Code, Lộ trình, Năng lực dùng được, P0 — vị trí + cách sửa đã xác định rõ, không còn mơ hồ, P1 — cần user quyết định hướng (ảnh hưởng effort/rủi ro thật, xem mục Câu hỏi), P1 — đã xác định rõ (không cần hỏi thêm), Quyết định (sau interview, `docs/tdq/questions/2026-08-05-toi-uu-p0-p1-workflow.md`), Rà soát code chi tiết (19 đề xuất, qua Explore agent) (+1 more)

### Community 99 - "PLAN — Vá điểm mù verify-by-effect (0.3.1)"
Cohesion: 0.20
Nodes (9): Definition of Done, P1 — Helper trong `scripts/tdq_state.py`, P2 — Ghi ảnh chụp đầu turn (`hooks/scripts/prompt_context.py`), P3 — Đối chiếu cuối turn (`hooks/scripts/stop_gate.py`), P4 — Doc & đóng gói 0.3.1, P5 — QC & report, PLAN — Vá điểm mù verify-by-effect (0.3.1), Task phát sinh từ QC (+1 more)

### Community 100 - "PLAN — Đổi thiết kế mode external: giao cả plan 1 lần + phase + verify 3 tầng"
Cohesion: 0.20
Nodes (9): Definition of Done, Năng lực → task, P1 — Script: schema + run-plan (spec §2 #1, #2), P2 — Luật chia phase + fix-rounds (spec §2 #8, một phần #3), P3 — Skill & khuôn gói (spec §2 #3, #4, #5), P4 — Agents + đồng bộ doc (spec §2 #6, #9), P5 — Log & test bắt buộc + QC, PLAN — Đổi thiết kế mode external: giao cả plan 1 lần + phase + verify 3 tầng (+1 more)

### Community 101 - "PLAN — Đưa skill vào gói external (hybrid 3 nhánh)"
Cohesion: 0.20
Nodes (9): Definition of Done, Năng lực → task, P1 — Parser dòng `Dùng:` + split-plan (spec §2 đầu ra 2), P2 — Lệnh `skill-dump` (spec §2 đầu ra 1), P3 — Warning máy-kiểm trong run-plan (spec §2 đầu ra 3), P4 — Khuôn + skill docs (spec §2 đầu ra 4–7), P5 — Sync, log & QC (spec §2 đầu ra 8–9, §4), PLAN — Đưa skill vào gói external (hybrid 3 nhánh) (+1 more)

### Community 102 - "PLAN — Cắt token thừa trong TDQ workflow"
Cohesion: 0.20
Nodes (9): Definition of Done, Năng lực → task, P1 — Cắt bản chép và step thừa (C1, C2, C3), thuần markdown, P2 — Hợp đồng skill còn 5 trường, P3 — Cắt lặp trong phases.md và interview (C4, C5), P4 — Một nguồn sự thật cho CLAUDE.md (C6), P5 — Đóng sổ, PLAN — Cắt token thừa trong TDQ workflow (+1 more)

### Community 103 - "Mini-spec/plan — 2026-08-09-sua-mo-ta-skill-inventory (lane quick)"
Cohesion: 0.20
Nodes (9): Definition of Done, Hiệu quả chốt (bản cũ → bản cuối), Mini-spec/plan — 2026-08-09-sua-mo-ta-skill-inventory (lane quick), Phạm vi, QC, QC vòng 2 — validate lại sau khi user restart Claude Code, QC vòng 3 — fix ca vắt ngưỡng, Task (+1 more)

### Community 104 - "Vòng 1 (2026-08-05 13:35)"
Cohesion: 0.20
Nodes (9): Q1 (P0-4) — hard-block hay soft-block task `(mcp)` khi mode external?, Q2 (P1-1) — rút gọn nạp cứng cho quick lane: cắt được `tdq-intake` rõ ràng,, Q3 (P1-2) — đồng bộ ngưỡng digest ≤1.500 ký tự lặp ở 8 file agent (không tự "nạp", Q4 (P1-3) — sửa `stop_gate.py` scope theo turn thay vì toàn working tree: rủi ro, Q5 (P1-4) — thêm ví dụ cụ thể (đổi schema DB, xoá data, đổi API contract công khai), Q6 (P1-12) — đo carry-cost before/after theo kịch bản chuẩn hoá cần 2 session sạch,, QUESTIONS — 2026-08-05-toi-uu-p0-p1-workflow, Thông báo (không phải câu hỏi, chỉ cần xác nhận đã đọc) (+1 more)

### Community 105 - "RESEARCH — Tối ưu token/time cho TDQ workflow"
Cohesion: 0.20
Nodes (9): Carry-cost: mỗi output của tool bị mang vác lại ở mọi call sau đó, Chi phí luôn-nạp, Chi phí THỜI GIAN, Phần 1 — Đo trên chính transcript của repo này (nguồn nội bộ, đáng tin nhất), Phần 1b — Số đo lặp lại được (`scripts/token_audit.py`), Phần 2 — Research bên ngoài (tavily-primary, 2 truy vấn, 2026-08-04), Phần 3 — Đối chiếu: nguyên nhân gốc trong TDQ workflow, Phần 4 — Xác minh 3 khẳng định bằng nguồn chính thức (+1 more)

### Community 106 - "Research: clone-setting-to-codex — cấu trúc/khả năng cấu hình thật của Codex CLI (2026)"
Cohesion: 0.20
Nodes (9): Câu 1 — config.toml schema chính thức, vị trí, project-level config, Câu 2 — file instruction tương đương CLAUDE.md, Câu 3 — khái niệm "skill" tương đương Claude Code Skills, Câu 4 — "plugin" (`codex plugin add/list/marketplace`), Câu 5 — hooks chính thức, GA hay experimental, Câu 6 — MCP server config format thật, so với Claude Code, Research: clone-setting-to-codex — cấu trúc/khả năng cấu hình thật của Codex CLI (2026), Truy vấn đã chạy (+1 more)

### Community 107 - "Research: Tối ưu token vòng 2 — biện pháp lâu dài cho agentic workflow"
Cohesion: 0.20
Nodes (9): 1. Context engineering chính thức của Anthropic, 2. Claude Code context editing / tool-result clearing / `/compact` vs `/clear`, 3. Prompt caching — cách tính phí cache_read, TTL, invalidation, 4. Giảm số API call / tool call — batching, code execution thay vì tool call, progressive disclosure, 5. Viết CLI/script cho agent tiêu thụ, 6. Kinh nghiệm thực chiến cộng đồng 2026 — giảm chi phí Claude Code trên codebase lớn, Research: Tối ưu token vòng 2 — biện pháp lâu dài cho agentic workflow, Điều áp dụng được cho TDQ (+1 more)

### Community 108 - "SPEC — Kiểm kê & tận dụng skill phụ trợ (tdq-workflow 0.3.3)"
Cohesion: 0.20
Nodes (9): 1. Mục tiêu & phạm vi, 2. Đầu ra cụ thể, 3. Cách tiếp cận & lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. QC & Definition of Done, 7. Câu hỏi còn mở (+1 more)

### Community 109 - "SPEC — Mode implement "external": giao task cho Codex/Antigravity qua worktree"
Cohesion: 0.20
Nodes (9): 1. Mục tiêu & phạm vi, 2. Đầu ra cụ thể, 3. Cách tiếp cận & lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. QC & Definition of Done, 7. Câu hỏi còn mở (+1 more)

### Community 110 - "SPEC — Tối ưu bộ plugin user-level: tier hoá, lazy-load, viết lại §10 (v1.0)"
Cohesion: 0.20
Nodes (9): 1. Mục tiêu & phạm vi, 2. Đầu ra đo đếm được, 3. Cách tiếp cận + lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. Phạm vi QC & Definition of Done, 7. Câu hỏi còn mở (+1 more)

### Community 111 - "SPEC — Search agent "deep search" dùng agy CLI, tích hợp TDQ workflow"
Cohesion: 0.20
Nodes (9): 1. Mục tiêu & phạm vi, 2. Đầu ra cụ thể, 3. Cách tiếp cận & lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. QC & Definition of Done, 7. Câu hỏi còn mở (+1 more)

### Community 112 - "SPEC — Audit tổng thể TDQ workflow 0.6.0 (conflict, edge case, robustness model thấp)"
Cohesion: 0.20
Nodes (9): 1. Mục tiêu & phạm vi, 2. Đầu ra cụ thể, 3. Cách tiếp cận & lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. QC & Definition of Done, 7. Câu hỏi còn mở (+1 more)

### Community 113 - "SPEC — Hybrid deep search: Claude scout ∥ agy tổng quát → agy đào sâu"
Cohesion: 0.20
Nodes (9): 1. Mục tiêu & phạm vi, 2. Đầu ra cụ thể, 3. Cách tiếp cận & lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. QC & Definition of Done, 7. Câu hỏi còn mở (+1 more)

### Community 114 - "SPEC — Đổi thiết kế mode external: giao cả plan 1 lần + fix loop"
Cohesion: 0.20
Nodes (9): 1. Mục tiêu & phạm vi, 2. Đầu ra cụ thể, 3. Cách tiếp cận & lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. QC & Definition of Done, 7. Câu hỏi còn mở (+1 more)

### Community 115 - "SPEC — Bộ công cụ export cấu hình Claude Code sang máy khác"
Cohesion: 0.20
Nodes (9): 1. Mục tiêu & phạm vi, 2. Đầu ra cụ thể, 3. Cách tiếp cận & lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. QC & Definition of Done, 7. Câu hỏi còn mở (+1 more)

### Community 116 - "SPEC — TDQ workflow linh hoạt & bớt ma sát"
Cohesion: 0.20
Nodes (9): 1. Mục tiêu & phạm vi, 2. Đầu ra cụ thể, 3. Cách tiếp cận & lý do, 3b. Năng lực & công cụ, 4. Yêu cầu bắt buộc, 5. Ràng buộc & rủi ro, 6. QC & Definition of Done, 7. Câu hỏi còn mở (+1 more)

### Community 117 - "{{BUNDLE_NAME}} — Claude Code setup export"
Cohesion: 0.22
Nodes (8): 1. Giới thiệu bundle, 2. CLI dependency cần cài, 3. Cài Claude Code CLI, 4. Add marketplace + cài từng plugin, 5. Copy file cấu hình + rewrite path `tdq-local` + điền lại API key, 6. Khôi phục MCP server, 7. Verify, {{BUNDLE_NAME}} — Claude Code setup export

### Community 118 - "doc"
Cohesion: 0.22
Nodes (9): doc, Expect_Output, git & worktree, Graphify, Phong cách trình bày, quy tắc chung, Research & độ tin cậy thông tin, workflow (+1 more)

### Community 119 - "Plan — TDQWorkflow Plugin v0.1"
Cohesion: 0.22
Nodes (8): Definition of Done (theo spec mục 10), Nguyên tắc thực thi, Phase A — Nền móng, Phase B — Hooks + unit test (red/green từng script), Phase C — Skills (10), Phase D — Agents, Phase E — QC tổng + tài liệu, Plan — TDQWorkflow Plugin v0.1

### Community 120 - "Nguyên văn"
Cohesion: 0.22
Nodes (8): 2026-08-09-trigger-tieng-viet, Chỗ chưa rõ, Hiểu & kiến thức, Hỏi đáp, Mục tiêu, Nguyên văn, Phạm vi đoán, Đo thật (274 skill trên máy, 2026-08-09)

### Community 121 - "KNOWLEDGE — external-agent-mode"
Cohesion: 0.22
Nodes (8): Kiểm cổng, KNOWLEDGE — external-agent-mode, Nguồn, Năng lực dùng được (B0 — bảng phán quyết), Phương án đã loại, Quyết định đã chốt (8, từ questions cùng slug), Sự thật đã xác minh trên máy, Đính chính 23:45 (sau chẩn đoán sâu, có bằng chứng)

### Community 122 - "Knowledge — 2026-08-04-approval-gate-bug"
Cohesion: 0.22
Nodes (8): Kiểm cổng, Knowledge — 2026-08-04-approval-gate-bug, Lịch sử liên quan (git log), Năng lực dùng được, Quyết định đã chốt (qua vòng interview), Research (tóm tắt, đầy đủ ở `docs/tdq/research/2026-08-04-approval-gate-bug.md`), Rủi ro còn lại (ghi nhận, không phải chỗ chưa rõ), Đọc code (tóm tắt)

### Community 123 - "KNOWLEDGE — Tối ưu token/time cho TDQ workflow"
Cohesion: 0.22
Nodes (8): Cách tiếp cận đã chọn, KNOWLEDGE — Tối ưu token/time cho TDQ workflow, Lộ trình, Mô hình chi phí (nền tảng mọi đề xuất), Nguyên nhân gốc đã xác định (kèm số đo), Nguồn, Năng lực dùng được, Quyết định đã chốt

### Community 124 - "Knowledge — 2026-08-04-workflow-linh-hoat"
Cohesion: 0.22
Nodes (8): Cách tiếp cận đã chọn, Knowledge — 2026-08-04-workflow-linh-hoat, Lộ trình (D6 — áp cho chính request này), Nguồn, Năng lực dùng được, Phương án đã loại, Quyết định đã chốt (từ interview vòng 1 + 2), Ràng buộc kỹ thuật

### Community 125 - "Knowledge — 2026-08-05-full-claude-export"
Cohesion: 0.22
Nodes (8): Kiểm cổng, Knowledge — 2026-08-05-full-claude-export, Lộ trình, Nguồn, Năng lực dùng được, Phương án đã loại, Quyết định đã chốt, Đã đọc

### Community 126 - "KNOWLEDGE — Siết QC và vòng fix cho lane quick"
Cohesion: 0.22
Nodes (8): Cách tiếp cận đã chọn, Kiểm cổng, KNOWLEDGE — Siết QC và vòng fix cho lane quick, Lộ trình, Năng lực dùng được, Phương án đã loại, Quyết định đã chốt (12/12 câu, không còn chỗ đoán), Ràng buộc kỹ thuật (đã xác minh bằng đọc code)

### Community 127 - "Knowledge — 2026-08-08-giam-over-engineer-workflow"
Cohesion: 0.22
Nodes (8): Kiểm cổng, Knowledge — 2026-08-08-giam-over-engineer-workflow, Lộ trình, Nguồn, Năng lực dùng được, Phương án đã loại, Quyết định đã chốt, Đã đọc

### Community 128 - "PLAN — Sửa lỗi approval-gate (nhắc nhở khi duyệt sai)"
Cohesion: 0.22
Nodes (8): Definition of Done, Ghi chú review (áp dụng 5 góp ý `tdq-reviewer` vòng 1), Năng lực → task, P1 — Lưu tín hiệu duyệt vào turn ledger (`prompt_context.py`), P2 — Đối chiếu tín hiệu trong `bash_gate.py` (cả `approve` và `set phase=`), P3 — Test bắt buộc tổng hợp, PLAN — Sửa lỗi approval-gate (nhắc nhở khi duyệt sai), Quy tắc thi hành (áp cho mọi task)

### Community 129 - "PLAN — Bộ công cụ export cấu hình Claude Code sang máy khác"
Cohesion: 0.22
Nodes (8): Definition of Done, Năng lực → task, P1 — Viết bộ công cụ export tĩnh (`claude-export/`), P2 — Thu thập dữ liệu thật & copy vào bundle đích, P3 — Điền manifest/README thật & ghi log, P4 — QC tổng & log/test bắt buộc, PLAN — Bộ công cụ export cấu hình Claude Code sang máy khác, Quy tắc thi hành (áp cho mọi task)

### Community 130 - "PLAN — Đề xuất tối ưu time/token cho TDQ workflow"
Cohesion: 0.22
Nodes (8): Definition of Done, Năng lực → task, P1 — Script đo `token_audit.py`, P2 — Chốt số liệu & nguồn, P3 — Viết file đề xuất, P4 — QC & Report, PLAN — Đề xuất tối ưu time/token cho TDQ workflow, Quy tắc thi hành (áp cho mọi task)

### Community 131 - "Mini-spec/plan — 2026-08-09-trigger-tieng-viet (lane quick)"
Cohesion: 0.22
Nodes (8): Chốt thiết kế (đo trên 274 skill), Definition of Done, Mini-spec/plan — 2026-08-09-trigger-tieng-viet (lane quick), Phát hiện: bảng kiểm kê đọc bản CACHE, không đọc repo, Phạm vi, QC, Task, Vòng fix trong lúc build (không phải QC FAIL sau khi xong)

### Community 132 - "REPORT — Instruction hardening cho model yếu (tdq-workflow 0.3.0)"
Cohesion: 0.22
Nodes (8): Cách chạy / cách kiểm, Giới hạn còn lại, Kết quả QC, Quyết định đáng chú ý, REPORT — Instruction hardening cho model yếu (tdq-workflow 0.3.0), Ánh xạ tên skill cũ → mới, Đã làm gì, Đầu ra

### Community 133 - "REPORT — Audit toàn diện tdq-workflow 0.6.0"
Cohesion: 0.22
Nodes (8): Cách chạy / cách kiểm, Giới hạn còn lại, Kết quả QC, Quyết định đáng chú ý, REPORT — Audit toàn diện tdq-workflow 0.6.0, Đã làm gì, Đầu ra, Đề xuất tiếp theo

### Community 134 - "REPORT — Đổi thiết kế mode external: giao cả plan / theo phase"
Cohesion: 0.22
Nodes (8): Cách chạy / cách kiểm, Giới hạn còn lại, Kết quả QC, Quyết định đáng chú ý, REPORT — Đổi thiết kế mode external: giao cả plan / theo phase, Đã làm gì, Đầu ra, Đề xuất tiếp theo

### Community 135 - "REPORT — Đưa skill vào gói external (hybrid 3 nhánh)"
Cohesion: 0.22
Nodes (8): Cách chạy / cách kiểm, Giới hạn còn lại, Kết quả QC, Quyết định đáng chú ý, REPORT — Đưa skill vào gói external (hybrid 3 nhánh), Đã làm gì, Đầu ra, Đề xuất tiếp theo

### Community 136 - "REPORT — Sửa lỗi approval-gate (nhắc nhở khi duyệt sai)"
Cohesion: 0.22
Nodes (8): Cách chạy / cách kiểm, Giới hạn còn lại, Kết quả QC, Quyết định đáng chú ý, REPORT — Sửa lỗi approval-gate (nhắc nhở khi duyệt sai), Đã làm gì, Đầu ra, Đề xuất tiếp theo

### Community 137 - "REPORT — Bộ công cụ export cấu hình Claude Code sang máy khác"
Cohesion: 0.22
Nodes (8): Cách chạy / cách kiểm, Giới hạn còn lại, Kết quả QC, Quyết định đáng chú ý, REPORT — Bộ công cụ export cấu hình Claude Code sang máy khác, Đã làm gì, Đầu ra, Đề xuất tiếp theo

### Community 138 - "Working log 2026-08-07"
Cohesion: 0.22
Nodes (8): 16:21 — Mở request siết QC + vòng fix cho lane quick, 16:24 — Lane full, phase analyze: kiểm kê + đọc code + interview vòng 1, 16:42 — Interview vòng 1 có đáp, mở vòng 2 vì đáp 7 xung đột đáp 1+2, 16:52 — Chốt knowledge + viết spec v1.0, chờ duyệt, 17:33, 17:34 — Viết plan, gọi tdq-reviewer, áp 17/17 finding, spec lên bản 1.1, 17:45, Working log 2026-08-07

### Community 139 - "tdq-workflow — Plugin Claude Code"
Cohesion: 0.22
Nodes (8): Cài đặt (chỉ trong repo/project), Cách hook điều khiển agent, Cấu trúc, Duyệt bằng chat thường, Dùng hằng ngày, Pipeline, Quy ước cứng, tdq-workflow — Plugin Claude Code

### Community 140 - "tavily.md"
Cohesion: 0.22
Nodes (7): Cost control, Search patterns, Tavily power usage, Tool selection, Sai lầm hay gặp, Thứ tự bắt buộc, Xử lý issue/lỗi do user báo

### Community 141 - "QuickQcApproveCliTest"
Cohesion: 0.22
Nodes (4): QuickQcApproveCliTest, Quyết định 9: bỏ QC vẫn phải để lại nguyên văn câu user., Phải từ chối bằng thông báo NÊU TÊN cờ, không phải bằng USAGE chung., N3: cờ --no-qc là đường opt-out DUY NHẤT, và phải để lại dấu vết.

### Community 142 - "Hướng dẫn tự cài tdq-workflow ở user-level (thủ công)"
Cohesion: 0.25
Nodes (7): 1. Cài qua local marketplace, 2. Đồng bộ rule working log ở `~/.claude/CLAUDE.md`, 3. Thêm instruction TDQ cho MỌI task vào `~/.claude/CLAUDE.md`, 4. Dùng ngoài Claude Code, 5. Gỡ, Hướng dẫn tự cài tdq-workflow ở user-level (thủ công), Lưu ý an toàn

### Community 143 - "2026-08-09-sua-mo-ta-skill-inventory"
Cohesion: 0.25
Nodes (7): 2026-08-09-sua-mo-ta-skill-inventory, Chỗ chưa rõ, Hiểu & kiến thức, Hỏi đáp, Mục tiêu, Nguyên văn, Phạm vi đoán

### Community 144 - "KNOWLEDGE — Search agent dùng agy cho advanced search (2026-07-31)"
Cohesion: 0.25
Nodes (7): Kiểm cổng, KNOWLEDGE — Search agent dùng agy cho advanced search (2026-07-31), Nguồn, Năng lực dùng được, Phương án đã loại + lý do, Quyết định đã chốt (interview 14:27 + probe), Ràng buộc

### Community 145 - "Knowledge — 2026-07-31-hybrid-deep-search"
Cohesion: 0.25
Nodes (7): Hiện trạng code (đọc 2026-07-31), Knowledge — 2026-07-31-hybrid-deep-search, Nguồn, Năng lực dùng được, Phương án đã loại, Quyết định đã chốt (từ request + interview), Ràng buộc

### Community 146 - "KNOWLEDGE — 2026-08-02-tdq-default-cleanup"
Cohesion: 0.25
Nodes (7): Cách tiếp cận, KNOWLEDGE — 2026-08-02-tdq-default-cleanup, Nguồn, Năng lực dùng được, Phương án đã loại, Quyết định đã chốt (user trả lời vòng 1), Ràng buộc

### Community 147 - "PLAN — Vá chặn oan do vân tay repo (0.3.2)"
Cohesion: 0.25
Nodes (7): Ngoài phạm vi (đã nêu lý do trong chat), P1 — `scripts/tdq_state.py`: vân tay chỉ tính file "thật", P2 — `hooks/scripts/stop_gate.py`, P3 — Log service (D), P4 — Doc & đóng gói 0.3.2, P5 — QC & report, PLAN — Vá chặn oan do vân tay repo (0.3.2)

### Community 148 - "PLAN — Mode implement "external" (Codex/Antigravity qua worktree) — HOÀN THÀNH (mode main, 2026-07-30 23:10; Q9 PENDING chờ user cài plugin codex)"
Cohesion: 0.25
Nodes (7): Definition of Done, Năng lực → task, P1 — Lõi script + unit test (repo, red → green từng task), P2 — State machine + hooks + doc tự sinh, P3 — Khuôn task + agents + skills + CLAUDE.md, P4 — Cài plugin + chạy thật + QC + đóng, PLAN — Mode implement "external" (Codex/Antigravity qua worktree) — HOÀN THÀNH (mode main, 2026-07-30 23:10; Q9 PENDING chờ user cài plugin codex)

### Community 149 - "PLAN — Tối ưu bộ plugin user-level: tier hoá + lazy-load (HOÀN THÀNH — QC PASS 9/9, 14:58)"
Cohesion: 0.25
Nodes (7): Definition of Done, Năng lực → task, P1 — Script `plugin_tiers.py` + test (trong repo, red → green từng task), P2 — Cài user-level, P3 — `~/.claude/CLAUDE.md`, P4 — QC & đóng, PLAN — Tối ưu bộ plugin user-level: tier hoá + lazy-load (HOÀN THÀNH — QC PASS 9/9, 14:58)

### Community 150 - "PLAN — Audit toàn bộ workflow TDQ, đề xuất tối ưu token/thời gian (vòng 3)"
Cohesion: 0.25
Nodes (7): Definition of Done, Năng lực → task, P1 — Hoàn thiện report & knowledge (đầu ra #1, #2, #3 spec §2), P2 — Nới trần report thành convention chung (đầu ra #4 spec §2), P3 — Log & test bắt buộc, PLAN — Audit toàn bộ workflow TDQ, đề xuất tối ưu token/thời gian (vòng 3), Quy tắc thi hành (áp cho mọi task)

### Community 151 - "Bằng chứng"
Cohesion: 0.25
Nodes (7): Bằng chứng, Không sửa (có chủ ý), Kết luận, Q7 — ba kịch bản audit, dựng lại nguyên trạng (bản cài 0.3.2), Q8 — hồi quy 0.3.1, Q9 — git treo quá 2 s, QC — Vá chặn oan do vân tay repo (0.3.2)

### Community 152 - "QC — Vá điểm mù verify-by-effect (0.3.1)"
Cohesion: 0.25
Nodes (7): Bằng chứng, Ghi chú lệch so với spec, Kết luận, Lỗi phát hiện trong QC và đã sửa, Q1, Q10 — smoke trên bản cài user-level 0.3.1 (`TDQ_PROJECT_DIR` đặt riêng từng lệnh), QC — Vá điểm mù verify-by-effect (0.3.1)

### Community 153 - "Vòng 1 (2026-08-05 03:2x) — đã hỏi, chờ trả lời"
Cohesion: 0.25
Nodes (7): Q1 — Bump lên mức nào?, Q2 — "Đầy đủ hơn" tới mức nào?, Q3 — Bundle mới đặt ở đâu, bundle/zip cũ xử lý sao?, Q4 — Repo copy: giữ `.git` không?, Q5 — Memory `.remember/` có đưa vào bundle không?, QUESTIONS — Bump version + export đầy đủ hơn, Vòng 1 (2026-08-05 03:2x) — đã hỏi, chờ trả lời

### Community 154 - "REPORT — Kiểm kê & tận dụng skill phụ trợ (tdq-workflow 0.3.3)"
Cohesion: 0.25
Nodes (7): Còn chờ user, Kết quả QC, Lệch so với spec (chi tiết + lý do ở file QC), REPORT — Kiểm kê & tận dụng skill phụ trợ (tdq-workflow 0.3.3), Vấn đề, Đã làm gì, Đầu ra

### Community 155 - "REPORT — Vá điểm mù verify-by-effect (tdq-workflow 0.3.1)"
Cohesion: 0.25
Nodes (7): Giới hạn còn lại, Kết quả QC, Quyết định đáng chú ý, REPORT — Vá điểm mù verify-by-effect (tdq-workflow 0.3.1), Vấn đề, Đã làm gì, Đầu ra

### Community 156 - "REPORT — Tối ưu time/token cho TDQ workflow"
Cohesion: 0.25
Nodes (7): Cảnh báo trung thực, Phát hiện cốt lõi, REPORT — Tối ưu time/token cho TDQ workflow, Sản phẩm, Điều cần user quyết, Đã làm gì, Đề xuất — 5 nhóm, 19 task

### Community 157 - "REPORT — Giảm over-engineer & over-test cho TDQ workflow"
Cohesion: 0.25
Nodes (7): Còn treo, Kết quả QC, Lệch plan, phải khai báo, REPORT — Giảm over-engineer & over-test cho TDQ workflow, Số đo trước/sau, Sự cố trong lúc làm, Đã làm

### Community 158 - "Research: 2026-08-04-export-claude-setup"
Cohesion: 0.25
Nodes (7): Research: 2026-08-04-export-claude-setup, Truy vấn 1 — Settings hierarchy (global/project/local), Truy vấn 2 — Cài lại plugin/marketplace trên máy mới, Truy vấn 3 — MCP config, secret trong `.mcp.json` / `~/.claude.json`, Truy vấn 4 — Backup/restore `~/.claude` giữa các máy (cộng đồng), Truy vấn 5 — Claude Code trên Windows: bắt buộc WSL2 hay hỗ trợ native?, Truy vấn 6 — Cài Codex CLI đa nền (macOS/Linux/Windows)

### Community 159 - "Brief deep search — LLM local tham số thấp làm engine code-agent (2026-07-31)"
Cohesion: 0.25
Nodes (7): Brief deep search — LLM local tham số thấp làm engine code-agent (2026-07-31), Câu hỏi, Dữ kiện đã có, Hướng từ phase 1, Luật, Ngữ cảnh, Tiêu chí rank

### Community 162 - "INSTRUCTIONS — Dựng bundle export cấu hình Claude Code"
Cohesion: 0.29
Nodes (6): Ghi log, INSTRUCTIONS — Dựng bundle export cấu hình Claude Code, Script làm gì, Sinh bundle, Điều script KHÔNG làm, Đo độ lệch giữa bundle và máy nguồn

### Community 163 - "Report — TDQWorkflow Plugin v0.1.0 — 2026-07-27"
Cohesion: 0.29
Nodes (6): Cách chạy / test, Kết quả, QC (docs/qc/), Quyết định đáng chú ý & giới hạn, Report — TDQWorkflow Plugin v0.1.0 — 2026-07-27, Đề xuất tiếp theo

### Community 164 - "Knowledge — 2026-07-31-audit-full-workflow"
Cohesion: 0.29
Nodes (6): Cách tiếp cận đã chọn, Knowledge — 2026-07-31-audit-full-workflow, Nguồn, Năng lực dùng được, Quyết định đã chốt (interview vòng 1 — questions/ cùng slug), Ràng buộc

### Community 165 - "Knowledge — 2026-08-03-skill-vao-goi-external"
Cohesion: 0.29
Nodes (6): Knowledge — 2026-08-03-skill-vao-goi-external, Nguồn, Năng lực dùng được, Phương án đã loại + lý do, Quyết định đã chốt (interview 2 vòng — xem questions/<slug>.md), Ràng buộc

### Community 166 - "Knowledge: 2026-08-04-export-claude-setup"
Cohesion: 0.29
Nodes (6): Khảo sát máy nguồn (đọc code/cấu hình thực tế), Kiểm cổng (3 câu hỏi bắt buộc trước khi sang spec), Knowledge: 2026-08-04-export-claude-setup, Loại trừ khỏi export (đã có căn cứ từ research + khảo sát), Năng lực dùng được, Quyết định đã chốt (từ vòng interview)

### Community 167 - "Bằng chứng"
Cohesion: 0.29
Nodes (6): Bằng chứng, Kết luận, Q1, Q12 — ghi chú lệch nhẹ so với spec, Q9 — smoke trên bản cài user-level (mọi lệnh đặt TDQ_PROJECT_DIR riêng), QC — Instruction hardening cho model yếu (0.3.0)

### Community 168 - "QC — Tối ưu plugin user-level: tier hoá + lazy-load"
Cohesion: 0.29
Nodes (6): Bằng chứng T2.6 — 3 case an toàn chạy tay trên máy thật, Bằng chứng T3.3 — audit CLAUDE.md (skill claude-md-improver), Ghi chú lệch (có chủ ý), Kết luận, QC — Tối ưu plugin user-level: tier hoá + lazy-load, Đối chiếu DoD spec §6 (vòng 1)

### Community 169 - "REPORT — Vá chặn oan do vân tay repo (tdq-workflow 0.3.2)"
Cohesion: 0.29
Nodes (6): Còn lại, Kết quả QC, REPORT — Vá chặn oan do vân tay repo (tdq-workflow 0.3.2), Vấn đề, Đã làm gì, Đầu ra

### Community 170 - "REPORT — Tối ưu bộ plugin user-level: tier hoá + lazy-load"
Cohesion: 0.29
Nodes (6): Còn chờ user, Hợp đồng skill đã thi hành, Kết quả QC — PASS 9/9 vòng 1, REPORT — Tối ưu bộ plugin user-level: tier hoá + lazy-load, Vấn đề, Đã làm gì

### Community 171 - "Request: Claude tự quyết implement mode, không hỏi user"
Cohesion: 0.29
Nodes (6): Bằng chứng thu được, Hướng fix đề xuất, Nguyên nhân (không phải bug code, là lỗ hổng thiết kế 0.1.3), Nguyên văn, Request: Claude tự quyết implement mode, không hỏi user, Unknowns cần user chốt

### Community 172 - "Request: state phải luôn nằm ở project root (chống "state bóng")"
Cohesion: 0.29
Nodes (6): Bằng chứng, Mong muốn, Nguyên nhân, Nguyên văn, Request: state phải luôn nằm ở project root (chống "state bóng"), Ràng buộc

### Community 173 - "RESEARCH — Search agent dùng agy (2026-07-31)"
Cohesion: 0.29
Nodes (6): Kết luận khả thi, RESEARCH — Search agent dùng agy (2026-07-31), Truy vấn 1: Gemini CLI headless còn dùng được không (bối cảnh chọn agy), Truy vấn 2: agy headless có tool search không (probe thật trên máy, 2026-07-31 14:20), Truy vấn 3: agy --json-schema headless (docs chính thức), Truy vấn 4: chống bịa citation với model yếu

### Community 174 - "Research — 2026-08-04-approval-gate-bug"
Cohesion: 0.29
Nodes (6): Kết luận rút ra cho hướng kỹ thuật, Research — 2026-08-04-approval-gate-bug, Truy vấn 1: Claude Code PreToolUse hook permissionDecision deny — chặn cứng theo pattern nào, Truy vấn 2: LLM agent bỏ qua instruction chèn trong context / tool output — failure mode, Truy vấn 3: Human-in-the-loop approval gate — chặn cứng vs nhắc mềm, Đối chiếu với lịch sử chính plugin (đọc code, không phải research ngoài nhưng liên quan)

### Community 175 - "Research: Giảm chi phí token/thời gian dài hạn cho agentic coding workflow"
Cohesion: 0.29
Nodes (6): Research: Giảm chi phí token/thời gian dài hạn cho agentic coding workflow, Truy vấn 1: prompt caching cost reduction agentic workflow best practices, Truy vấn 2: context window bloat từ hooks/subagents, cách giảm token usage, Truy vấn 3: subagent context isolation pattern, hiệu quả token đa-agent, Truy vấn 4: system prompt size best practice — CLAUDE.md, skills, token cost, Tổng hợp — nguyên tắc quan trọng nhất

### Community 176 - "RESEARCH — Bump version + export đầy đủ hơn"
Cohesion: 0.29
Nodes (6): Kết luận dùng cho spec, RESEARCH — Bump version + export đầy đủ hơn, Truy vấn 1 — Migrate cấu hình Claude Code sang máy mới, copy file nào, Truy vấn 2 — MCP server ở đâu, khôi phục thế nào bằng CLI, Truy vấn 3 — Marketplace local + cài plugin bằng CLI, Truy vấn 4 — Xác minh lại cú pháp trước khi ghi vào README template

### Community 177 - "Brief deep search — LLM local tham số thấp làm engine code-agent (2026-07-31)"
Cohesion: 0.29
Nodes (6): Brief deep search — LLM local tham số thấp làm engine code-agent (2026-07-31), Câu hỏi, Dữ kiện đã có, Luật, Ngữ cảnh, Tiêu chí rank

### Community 178 - "BRIEF — Vector database chạy local cho RAG (2026)"
Cohesion: 0.29
Nodes (6): BRIEF — Vector database chạy local cho RAG (2026), Câu hỏi, Dữ kiện đã có, Hướng từ phase 1, Ngữ cảnh, Tiêu chí rank

### Community 179 - "Chọn model & effort cho sub-agent"
Cohesion: 0.29
Nodes (6): Chọn model & effort cho sub-agent, Cảnh báo về `effort`, Hai nút chỉnh, hai phạm vi khác nhau, Luật override `model` khi gọi (tham số Agent tool), Mặc định theo vai (đã ghi vào frontmatter), Nguồn

### Community 180 - "Kiểm kê năng lực (bước B0)"
Cohesion: 0.29
Nodes (7): 4 lý do loại (đóng — cấm tự chế lý do khác), Các bước, Khuôn bảng (copy nguyên khối rồi điền), Kiểm kê năng lực (bước B0), Lane quick, Luật điền ô "Phán quyết", Số phận từng phán quyết ở các phase sau

### Community 181 - "KNOWLEDGE — instruction-hardening-7b (chốt trước khi viết spec)"
Cohesion: 0.33
Nodes (6): 1. Vấn đề cốt lõi, 2. Quyết định đã chốt, 3. Tiêu chí "model yếu đọc cũng làm đúng" (lint sẽ chấm), 4. Đánh đổi đã biết, 5. Chưa quyết (không chặn spec), KNOWLEDGE — instruction-hardening-7b (chốt trước khi viết spec)

### Community 182 - "KNOWLEDGE — Tối ưu plugin user-level + lazy-load"
Cohesion: 0.33
Nodes (5): Kiểm cổng, KNOWLEDGE — Tối ưu plugin user-level + lazy-load, Năng lực dùng được, Quyết định đã chốt (interview vòng 1 — xem ../questions/ cùng slug), Sự thật đã chốt (từ research + đo máy)

### Community 183 - "MINI-PLAN — Thực thi 5 task P0 tối ưu token"
Cohesion: 0.33
Nodes (5): Chốt từ interview, MINI-PLAN — Thực thi 5 task P0 tối ưu token, Rủi ro, Task, Validate cuối

### Community 184 - "QC — Kiểm kê & tận dụng skill phụ trợ (0.3.3)"
Cohesion: 0.33
Nodes (5): Bằng chứng Q9 — rà bảo mật `scripts/skill_inventory.py`, Ghi chú lệch so với spec (có chủ ý), Kết luận, Lỗi phát hiện trong QC và đã sửa, QC — Kiểm kê & tận dụng skill phụ trợ (0.3.3)

### Community 185 - "QC — Mode implement "external" (Codex/Antigravity qua worktree)"
Cohesion: 0.33
Nodes (5): Bảng DoD Q1–Q9 (T4.5, vòng 1), Bằng chứng T3.7 — audit CLAUDE.md (skill claude-md-improver), Ghi chú sai lệch có chủ đích (vòng 1), QC — Mode implement "external" (Codex/Antigravity qua worktree), Đính chính sau QC (23:45, request fix-agy-adddir-sync-agent)

### Community 186 - "QC — TDQ workflow là default tuyệt đối + bỏ mục superpower"
Cohesion: 0.33
Nodes (5): Backup CLAUDE.md (T2.1), Bảng QC Q1–Q6, QC — TDQ workflow là default tuyệt đối + bỏ mục superpower, QC vòng 1 — 5 fail phát hiện ở T4.1, đã fix (QC1.1–QC1.3), Đối chiếu §5 superpower (cũ) → chỗ thay thế trong plugin

### Community 187 - "QUESTIONS — Siết QC và vòng fix cho lane quick"
Cohesion: 0.33
Nodes (5): QUESTIONS — Siết QC và vòng fix cho lane quick, Vòng 1 — 2026-08-07 16:24, Vòng 2 — 2026-08-07 16:42, Đáp vòng 1 (2026-08-07 16:41) — nguyên văn: "1A; 2A; 3.A; 4.A; 5A; 6.A; 7.B …", Đáp vòng 2 (2026-08-07 16:46) — nguyên văn: "8A; 9A ; 10A; 11:A ; 12A"

### Community 188 - "Vòng 1 — 2026-08-08 21:5x"
Cohesion: 0.33
Nodes (5): Câu hỏi — 2026-08-08-giam-over-engineer-workflow, Câu hỏi đã trình, Trả lời của user, Vòng 1 — 2026-08-08 21:5x, Vòng 2 — tự trả lời, có nêu giả định trong spec

### Community 189 - "REPORT — Mode implement "external" (Codex/Antigravity qua worktree)"
Cohesion: 0.33
Nodes (5): Kết quả, QC (chi tiết trong file QC), REPORT — Mode implement "external" (Codex/Antigravity qua worktree), Việc user cần làm, Đề xuất tiếp

### Community 190 - "Report — Hybrid deep search 2 phase (tdq-workflow 0.6.0)"
Cohesion: 0.33
Nodes (5): Bằng chứng chính, Hạn chế / việc còn lại, Kết quả, Report — Hybrid deep search 2 phase (tdq-workflow 0.6.0), Token Claude E2E (usage từng agent)

### Community 191 - "REPORT — Workflow linh hoạt: gộp gate, quick đủ bước, lộ trình động"
Cohesion: 0.33
Nodes (5): File đã đổi, Kiểm chứng, Lưu ý, REPORT — Workflow linh hoạt: gộp gate, quick đủ bước, lộ trình động, Đã làm được gì

### Community 192 - "Report — Siết QC và vòng fix cho lane quick"
Cohesion: 0.33
Nodes (5): Commit, Giới hạn còn lại, Kết quả QC, Report — Siết QC và vòng fix cho lane quick, Đã làm

### Community 193 - "REQUEST — Hook = remind, bỏ skill tdq-approve, instruction/skills đủ chi tiết cho model yếu (7B)"
Cohesion: 0.33
Nodes (6): Câu hỏi chờ user, Hiểu ban đầu (first read), Nguyên văn yêu cầu, REQUEST — Hook = remind, bỏ skill tdq-approve, instruction/skills đủ chi tiết cho model yếu (7B), Ràng buộc đã biết, Việc liên quan đang mở (từ đợt rà soát 2026-07-28)

### Community 194 - "REQUEST — Kiểm kê & tận dụng skill phụ trợ"
Cohesion: 0.33
Nodes (5): Chỗ chưa rõ, Cách hiểu đầu tiên, Nguyên văn yêu cầu, REQUEST — Kiểm kê & tận dụng skill phụ trợ, Đã xác minh trước khi viết spec (turn phân tích)

### Community 195 - "requests/2026-07-31-hybrid-deep-search.md"
Cohesion: 0.33
Nodes (5): Bổ sung (user, 15:59 +07), Chốt thêm (user, 16:01 +07), Chỗ chưa rõ (sẽ interview nếu lane full), Cách hiểu đầu tiên, Nguyên văn yêu cầu (user, 15:53 +07)

### Community 196 - "REQUEST — Bump version + làm lại bản export đầy đủ hơn"
Cohesion: 0.33
Nodes (5): Chỗ chưa rõ (cần interview), Cách hiểu đầu tiên, Nguyên văn yêu cầu (2026-08-05 03:21), REQUEST — Bump version + làm lại bản export đầy đủ hơn, Số liệu drift đã đo sơ bộ (read-only, trước khi chốt lane)

### Community 197 - "Request: clone-setting-codex"
Cohesion: 0.33
Nodes (5): Chỗ chưa rõ (cần interview/research), Cách hiểu đầu tiên, Nguyên văn yêu cầu, Phạm vi đoán (chưa chốt), Request: clone-setting-codex

### Community 198 - "Request — tối ưu token/time workflow (vòng 2)"
Cohesion: 0.33
Nodes (5): Chỗ chưa rõ (cần interview), Cách hiểu, Nguyên văn yêu cầu, Request — tối ưu token/time workflow (vòng 2), Số liệu mở màn (đo lúc 00:43, 2 session gần nhất)

### Community 199 - "REQUEST — Siết QC và vòng fix cho lane quick"
Cohesion: 0.33
Nodes (5): Chỗ chưa rõ (cần interview), Cách hiểu đầu tiên, Hiện trạng đã xác minh (turn read-only trước đó), Nguyên văn yêu cầu của user, REQUEST — Siết QC và vòng fix cho lane quick

### Community 200 - "RESEARCH — Instruction/skills đủ chắc để model yếu đi đúng workflow"
Cohesion: 0.33
Nodes (6): Kết luận dùng cho spec, R1 — PreToolUse có nhận `additionalContext` không? (câu hỏi sống-còn của thiết kế 0.2.0), R2 — Instruction dạng văn xuôi KHÔNG phải cơ chế bảo đảm, R3 — Viết prompt/instruction cho model yếu (7B), R4 — Chuẩn viết skill của Claude Code (giới hạn thực tế khi "viết chi tiết hơn"), RESEARCH — Instruction/skills đủ chắc để model yếu đi đúng workflow

### Community 201 - "RESEARCH — Tối ưu plugin user-level + lazy-load"
Cohesion: 0.33
Nodes (5): RESEARCH — Tối ưu plugin user-level + lazy-load, Số liệu đo tại máy (2026-07-30), Truy vấn 1 — cơ chế enabledPlugins & scope, Truy vấn 2 — chi phí context của plugin/skill, Truy vấn 3 — lệnh quản lý plugin

### Community 202 - "Research — 2026-07-31-hybrid-deep-search"
Cohesion: 0.33
Nodes (5): Dữ liệu benchmark nội bộ (docs/tdq/research/search/, 2026-07-31), Ground truth model, Research — 2026-07-31-hybrid-deep-search, Truy vấn 1 — pattern orchestration đa agent cho search, Truy vấn 2 — hệ research đa agent của Anthropic (căn cứ chính)

### Community 203 - "Research — 2026-08-03-skill-vao-goi-external"
Cohesion: 0.33
Nodes (5): Hệ quả thiết kế, Research — 2026-08-03-skill-vao-goi-external, Truy vấn 1 (turn trước, request check-skill-clone-worktree): cơ chế nạp hướng dẫn codex/agy, Truy vấn 2: AGENTS.md best practices + model nhỏ, Truy vấn 3: instruction-following của model yếu

### Community 204 - "Brief: phiên bản Python 3 mới nhất"
Cohesion: 0.33
Nodes (5): Brief: phiên bản Python 3 mới nhất, Câu hỏi, Dữ kiện đã có, Ngữ cảnh, Tiêu chí rank

### Community 205 - "Brief: phiên bản Python 3 mới nhất"
Cohesion: 0.33
Nodes (5): Brief: phiên bản Python 3 mới nhất, Câu hỏi, Dữ kiện đã có, Ngữ cảnh, Tiêu chí rank

### Community 206 - "Brief: phiên bản npm mới nhất của 2 package"
Cohesion: 0.33
Nodes (5): Brief: phiên bản npm mới nhất của 2 package, Câu hỏi, Dữ kiện đã có, Ngữ cảnh, Tiêu chí rank

### Community 207 - "Brief: phiên bản Python 3 mới nhất"
Cohesion: 0.33
Nodes (5): Brief: phiên bản Python 3 mới nhất, Câu hỏi, Dữ kiện đã có, Ngữ cảnh, Tiêu chí rank

### Community 208 - "BRIEF — Vector database chạy local cho RAG (2026)"
Cohesion: 0.33
Nodes (5): BRIEF — Vector database chạy local cho RAG (2026), Câu hỏi, Dữ kiện đã có, Ngữ cảnh, Tiêu chí rank

### Community 209 - "Brief — clone-setting-codex (phase 2 đào sâu)"
Cohesion: 0.33
Nodes (5): Brief — clone-setting-codex (phase 2 đào sâu), Bối cảnh, Hướng từ phase 1 (route đã chốt cho phase 2), Luật evidence-only, Yêu cầu output

### Community 210 - "Brief — clone-setting-codex (phase 2 đào sâu)"
Cohesion: 0.33
Nodes (5): Brief — clone-setting-codex (phase 2 đào sâu), Bối cảnh, Hướng từ phase 1 (route đã chốt cho phase 2), Luật evidence-only, Yêu cầu output

### Community 211 - "remind"
Cohesion: 0.33
Nodes (6): already_reminded(), Nhắc Claude kèm MÃ mà KHÔNG chặn tool, rồi thoát.      Khuôn 3 dòng (spec §2.1):, Mã này đã nhắc trong turn hiện tại chưa (dedupe 1 lần/mã/turn).      `rows`: sổ, Ép về đúng trần: ≤3 dòng, ≤200 ký tự., remind(), trim()

### Community 213 - "make_repo"
Cohesion: 0.33
Nodes (4): make_claude_home(), make_repo(), Repo giả có `.git` thật, 1 file tracked, 1 file untracked bị gitignore., `~/.claude` giả: settings.json có key thật trong `env`, cùng vài file phụ.

### Community 217 - "PLAN (quick) — 2026-08-05-bump-sync-user"
Cohesion: 0.40
Nodes (4): DoD, Phạm vi, PLAN (quick) — 2026-08-05-bump-sync-user, Task

### Community 218 - "PLAN (quick) — 2026-08-05-dat-ten-subagent"
Cohesion: 0.40
Nodes (4): DoD, Phạm vi, PLAN (quick) — 2026-08-05-dat-ten-subagent, Task

### Community 219 - "QUICK — Format câu hỏi interview: mỗi option 1 dòng"
Cohesion: 0.40
Nodes (4): Definition of Done, Phạm vi, QUICK — Format câu hỏi interview: mỗi option 1 dòng, Task

### Community 220 - "Mini-plan — Rebuild bundle export để đồng bộ (quick)"
Cohesion: 0.40
Nodes (4): DoD, Mini-plan — Rebuild bundle export để đồng bộ (quick), Phạm vi, Task

### Community 221 - "Mini-plan — Validate lại bundle export (quick)"
Cohesion: 0.40
Nodes (4): DoD, Mini-plan — Validate lại bundle export (quick), Phạm vi, Task

### Community 222 - "QC — 2026-08-05-toi-uu-p0-p1-workflow"
Cohesion: 0.40
Nodes (4): Kiểm độc lập — agent `tdq-qc-tester` (TQC.1), Kết luận, QC — 2026-08-05-toi-uu-p0-p1-workflow, Tự kiểm (P1-P6)

### Community 223 - "QC — Siết QC và vòng fix cho lane quick"
Cohesion: 0.40
Nodes (4): Ghi chú (không FAIL, đã báo trong report), Q8 — kiểm độc lập, QC — Siết QC và vòng fix cho lane quick, Vòng fix

### Community 224 - "QUESTIONS — Interview request instruction-hardening-7b"
Cohesion: 0.40
Nodes (5): Giả định tôi tự chốt (nói rõ để bạn bác nếu sai), QUESTIONS — Interview request instruction-hardening-7b, Vòng 0 — intake, Vòng 1, Vòng 2

### Community 225 - "QUESTIONS — external-agent-mode"
Cohesion: 0.40
Nodes (4): Kết vòng interview, QUESTIONS — external-agent-mode, Vòng 1 (21:55) — 4 câu đổi kết quả, Vòng 2 (21:58) — 4 câu chốt nốt

### Community 226 - "QUESTIONS — 2026-08-02-tdq-default-cleanup"
Cohesion: 0.40
Nodes (4): QUESTIONS — 2026-08-02-tdq-default-cleanup, Trả lời (vòng 1 — 2026-08-02 11:35), Vòng 1 (chờ trả lời), Vòng 2 — không còn câu hỏi đổi kết quả

### Community 227 - "Questions: 2026-08-04-export-claude-setup"
Cohesion: 0.40
Nodes (4): Chốt (không còn câu hỏi nào làm đổi kết quả), Questions: 2026-08-04-export-claude-setup, Vòng 1 — 2026-08-04, Vòng 2 — 2026-08-04

### Community 228 - "Hỏi–đáp: clone-setting-codex"
Cohesion: 0.40
Nodes (4): Chốt phạm vi, Hỏi–đáp: clone-setting-codex, Vòng 1 (20:00, 2026-08-05), Vòng 2 (20:00, 2026-08-05) — xung đột 2.B × 6.B

### Community 229 - "reports/2026-07-31-agy-search-agent.md"
Cohesion: 0.40
Nodes (4): Cách dùng nhanh, Giới hạn / PENDING, Kết quả QC (chi tiết: docs/tdq/qc/2026-07-31-agy-search-agent.md), Đã làm

### Community 230 - "REPORT — TDQ workflow là default tuyệt đối + bỏ mục superpower"
Cohesion: 0.40
Nodes (4): Lưu ý, QC, REPORT — TDQ workflow là default tuyệt đối + bỏ mục superpower, Đã làm

### Community 231 - "REPORT — Cắt token thừa trong TDQ workflow"
Cohesion: 0.40
Nodes (4): Cần biết, Kiểm chứng, REPORT — Cắt token thừa trong TDQ workflow, Đã làm

### Community 232 - "REQUEST — Fix chặn oan `[TDQ:LOG]` khi log ghi qua shell"
Cohesion: 0.40
Nodes (4): Liên quan, Nguyên văn triệu chứng, REQUEST — Fix chặn oan `[TDQ:LOG]` khi log ghi qua shell, Vì sao là lane full

### Community 233 - "REQUEST — Fix agy không tạo file (--add-dir) + Claude tự bắt kết quả agent"
Cohesion: 0.40
Nodes (4): Chẩn đoán (có bằng chứng), Nguyên văn yêu cầu, Phạm vi dự kiến, REQUEST — Fix agy không tạo file (--add-dir) + Claude tự bắt kết quả agent

### Community 234 - "REQUEST — Tối ưu bộ plugin user-level theo ranking + lazy-load"
Cohesion: 0.40
Nodes (4): Chỗ chưa rõ (cần phân tích/hỏi), Cách hiểu đầu tiên, Nguyên văn yêu cầu, REQUEST — Tối ưu bộ plugin user-level theo ranking + lazy-load

### Community 235 - "REQUEST — Search agent dùng agy cho advanced search, tích hợp TDQ workflow"
Cohesion: 0.40
Nodes (4): Cách hiểu đầu tiên, Nguyên văn yêu cầu, REQUEST — Search agent dùng agy cho advanced search, tích hợp TDQ workflow, Rủi ro đã biết (từ probe)

### Community 236 - "REQUEST — Thực thi 5 task P0 của đề xuất tối ưu token"
Cohesion: 0.40
Nodes (4): Chỗ chưa rõ (cần hỏi), Cách hiểu đầu tiên, Nguyên văn yêu cầu, REQUEST — Thực thi 5 task P0 của đề xuất tối ưu token

### Community 237 - "REQUEST — Tối ưu thời gian + token cho TDQ workflow"
Cohesion: 0.40
Nodes (4): Cách hiểu đầu tiên, Nguyên văn yêu cầu, REQUEST — Tối ưu thời gian + token cho TDQ workflow, Số liệu thô ban đầu (đo tại thời điểm mở request)

### Community 238 - "Request: Làm TDQ workflow linh hoạt & bớt ma sát"
Cohesion: 0.40
Nodes (4): Chỗ chưa rõ (cần interview), Cách hiểu đầu tiên, Nguyên văn yêu cầu của user, Request: Làm TDQ workflow linh hoạt & bớt ma sát

### Community 239 - "Request: audit toàn bộ workflow — tối ưu token/time"
Cohesion: 0.40
Nodes (4): Chỗ chưa rõ, Cách hiểu ban đầu, Nguyên văn yêu cầu, Request: audit toàn bộ workflow — tối ưu token/time

### Community 240 - "REQUEST — Format câu hỏi interview: mỗi option 1 dòng"
Cohesion: 0.40
Nodes (4): Chỗ chưa rõ, Cách hiểu đầu tiên, Nguyên văn yêu cầu của user, REQUEST — Format câu hỏi interview: mỗi option 1 dòng

### Community 241 - "REQUEST — Brainstorm + spec triển khai P0+P1 tối ưu workflow & user-level Claude Code"
Cohesion: 0.40
Nodes (4): Bối cảnh, Cách hiểu đầu tiên, Nguyên văn yêu cầu, REQUEST — Brainstorm + spec triển khai P0+P1 tối ưu workflow & user-level Claude Code

### Community 242 - "Request: giảm over-engineer & over-test cho bộ workflow"
Cohesion: 0.40
Nodes (4): Chỗ chưa rõ (cần interview), Hiểu ban đầu, Nguyên văn, Request: giảm over-engineer & over-test cho bộ workflow

### Community 243 - "Research — 2026-07-31-audit-full-workflow"
Cohesion: 0.40
Nodes (4): Khảo sát nội bộ (đọc code turn analyze), Research — 2026-07-31-audit-full-workflow, Truy vấn 1 (tavily-primary, advanced): prompt engineering small local LLM instruction following limitations agentic workflow reliability, Truy vấn 2 (tavily-primary, advanced): multi-agent LLM pipeline failure modes state machine orchestration edge cases 2025

### Community 244 - "RESEARCH — 2026-08-02-tdq-default-cleanup"
Cohesion: 0.40
Nodes (4): Kết luận thiết kế, RESEARCH — 2026-08-02-tdq-default-cleanup, Truy vấn 1: enforce workflow mỗi prompt — hook vs CLAUDE.md, Truy vấn 2: viết description skill để luôn trigger

### Community 245 - "2.3 Thiết kế state file"
Cohesion: 0.40
Nodes (5): 2.3.1 Hai file, một nguồn sự thật, 2.3.2 Quy tắc đọc/ghi cho agent (nhúng vào `tdq-conventions` + `AGENTS.md`), 2.3.3 Yêu cầu kỹ thuật xử lý file, 2.3.4 Bảng quyết định phase (`PHASE_TABLE` — hằng trong code, doc trích lại), 2.3 Thiết kế state file

### Community 246 - "QC — kiểm chất lượng"
Cohesion: 0.40
Nodes (4): Chạy cái gì, Ghi kết quả, Khi FAIL, QC — kiểm chất lượng

### Community 247 - "TDQ Build — Implement → QC → Report"
Cohesion: 0.40
Nodes (5): Luật cứng (áp cho cả ba phase), Phần A — Implement (phase `implement`), Phần B — QC (phase `qc`), Phần C — Report (phase `report`), TDQ Build — Implement → QC → Report

### Community 248 - "Kịch bản đo carry-cost before/after"
Cohesion: 0.40
Nodes (4): Ghi kết quả, Kịch bản đo carry-cost before/after, Thao tác cố định (chạy y hệt cho cả 2 session before/after), Đo bằng `token_audit.py`

### Community 249 - "phases.md"
Cohesion: 0.40
Nodes (3): Bảng phase TDQ (tự sinh — KHÔNG sửa tay), Các bước, TDQ Status

### Community 250 - "Vòng interview"
Cohesion: 0.40
Nodes (5): Ghi lại, Hỏi cái gì, Hỏi thế nào, Khi nào dừng, Vòng interview

### Community 251 - "Chọn cỡ request: nhỏ, quick hay full"
Cohesion: 0.40
Nodes (5): Bảng quyết, Chọn cỡ request: nhỏ, quick hay full, Dòng tự nhận định, Khuôn câu hỏi (copy được), Luồng mỗi lane

### Community 252 - "TDQ Intake — mở request & phân tích"
Cohesion: 0.40
Nodes (5): Phần A — Mở request (phase `no_state`), Phần B — Phân tích (phase `analyze`, chỉ lane full), Phần C — Lane quick, TDQ Intake — mở request & phân tích, Tầng nhỏ — trả lời/sửa luôn, không mở request

### Community 255 - "QC — Smoke e2e (E1) — 2026-07-27"
Cohesion: 0.50
Nodes (3): 1. Chain test 2 lane (hook thật, chạy subprocess), 2. Headless CLI thật (`claude -p --plugin-dir .`), QC — Smoke e2e (E1) — 2026-07-27

### Community 256 - "QC — 2026-08-03-skill-vao-goi-external"
Cohesion: 0.50
Nodes (3): Ghi chú, QC — 2026-08-03-skill-vao-goi-external, Đầu ra §2 (9/9 tồn tại)

### Community 257 - "QC — workflow linh hoạt (gộp gate, lane quick đủ bước, lộ trình động)"
Cohesion: 0.50
Nodes (3): Ghi chú, Kết quả, QC — workflow linh hoạt (gộp gate, lane quick đủ bước, lộ trình động)

### Community 258 - "QC — Audit toàn bộ workflow TDQ, đề xuất tối ưu token/thời gian (vòng 3)"
Cohesion: 0.50
Nodes (3): Kiểm bổ sung (không nằm trong Q1-Q5 nhưng thuộc DoD), Kết luận, QC — Audit toàn bộ workflow TDQ, đề xuất tối ưu token/thời gian (vòng 3)

### Community 259 - "QC — Bump 0.7.0 + bộ export Claude Code"
Cohesion: 0.50
Nodes (3): Defect QC phát hiện, Kết luận, QC — Bump 0.7.0 + bộ export Claude Code

### Community 260 - "QC — Full claude export (multi-repo local dependency)"
Cohesion: 0.50
Nodes (3): Cộng thêm (ngoài bảng Q1–Q6), Kết luận, QC — Full claude export (multi-repo local dependency)

### Community 261 - "questions/2026-07-31-agy-search-agent.md"
Cohesion: 0.50
Nodes (3): Bổ sung từ user (14:34, không cần hỏi lại — yêu cầu rõ), Các điểm Claude chốt (không đổi kết quả, có lý do — user không cần quyết), Vòng 1 (14:27, đã chốt)

### Community 262 - "Questions — 2026-07-31-audit-full-workflow"
Cohesion: 0.50
Nodes (3): Không còn câu hỏi mở, Questions — 2026-07-31-audit-full-workflow, Vòng 1 (2026-07-31 17:3x, AskUserQuestion)

### Community 263 - "Questions — 2026-07-31-hybrid-deep-search"
Cohesion: 0.50
Nodes (3): Các câu đã chốt trước đó qua chat (15:53–16:01), Questions — 2026-07-31-hybrid-deep-search, Vòng 1 (2026-07-31 16:07 +07, AskUserQuestion)

### Community 264 - "Questions — 2026-08-03-check-external-assign-flow"
Cohesion: 0.50
Nodes (3): Questions — 2026-08-03-check-external-assign-flow, Vòng 1, Vòng 2 (chốt thiết kế)

### Community 265 - "Hỏi–đáp — 2026-08-03-skill-vao-goi-external"
Cohesion: 0.50
Nodes (3): Hỏi–đáp — 2026-08-03-skill-vao-goi-external, Vòng 1, Vòng 2 (follow-up vì va chạm ràng buộc "model cấp thấp")

### Community 266 - "QUESTIONS — tối ưu token/time workflow"
Cohesion: 0.50
Nodes (3): QUESTIONS — tối ưu token/time workflow, Vòng 1 (intake) — 2026-08-04, Vòng 2 (analyze) — 2026-08-04

### Community 267 - "Interview — 2026-08-04-workflow-linh-hoat"
Cohesion: 0.50
Nodes (3): Interview — 2026-08-04-workflow-linh-hoat, Vòng 1 (2026-08-04 20:36 → 20:39), Vòng 2 (2026-08-04 20:5x)

### Community 268 - "Hỏi–đáp: 2026-08-05-audit-toi-uu-workflow"
Cohesion: 0.50
Nodes (3): Hỏi–đáp: 2026-08-05-audit-toi-uu-workflow, Vòng 1 (lúc mở request, trước khi phân tích), Vòng 2 (sau khi audit xong, 11:18)

### Community 269 - "Câu hỏi — 2026-08-05-full-claude-export"
Cohesion: 0.50
Nodes (3): Câu hỏi — 2026-08-05-full-claude-export, Rà soát theo yêu cầu bổ sung (không cần hỏi thêm — đọc trực tiếp `~/.claude`), Vòng 1

### Community 270 - "Hỏi–đáp — tối ưu token vòng 2"
Cohesion: 0.50
Nodes (3): Hỏi–đáp — tối ưu token vòng 2, Vòng 1 (00:52), Vòng 2 (01:10)

### Community 271 - "REQUEST — Mode giao việc cho agent ngoài (codex/antigravity) trong TDQ workflow"
Cohesion: 0.50
Nodes (3): Cách hiểu đầu tiên, Nguyên văn yêu cầu, REQUEST — Mode giao việc cho agent ngoài (codex/antigravity) trong TDQ workflow

### Community 272 - "REQUEST — Sample Socket.IO chat để test mode external (codex + agy)"
Cohesion: 0.50
Nodes (3): Cách hiểu đầu tiên, Nguyên văn yêu cầu, REQUEST — Sample Socket.IO chat để test mode external (codex + agy)

### Community 273 - "REQUEST — Tự chọn theo đề xuất khi gặp chặn kỹ thuật giữa build"
Cohesion: 0.50
Nodes (3): Cách hiểu đầu tiên, Nguyên văn yêu cầu, REQUEST — Tự chọn theo đề xuất khi gặp chặn kỹ thuật giữa build

### Community 274 - "REQUEST — Check bump version + đồng bộ plugin repo ↔ user-level"
Cohesion: 0.50
Nodes (3): Cách hiểu đầu tiên, Nguyên văn yêu cầu, REQUEST — Check bump version + đồng bộ plugin repo ↔ user-level

### Community 275 - "REQUEST — Dòng duyệt plan gợi ý sai mode đã chốt"
Cohesion: 0.50
Nodes (3): Cách hiểu đầu tiên, Nguyên văn yêu cầu, REQUEST — Dòng duyệt plan gợi ý sai mode đã chốt

### Community 276 - "REQUEST — 2026-08-03-check-sync-sau-restart"
Cohesion: 0.50
Nodes (3): Cách hiểu đầu tiên, Nguyên văn, REQUEST — 2026-08-03-check-sync-sau-restart

### Community 277 - "REQUEST — 2026-08-03-recheck-sync-restart-2"
Cohesion: 0.50
Nodes (3): Cách hiểu đầu tiên, Nguyên văn, REQUEST — 2026-08-03-recheck-sync-restart-2

### Community 278 - "requests/2026-08-04-approval-gate-bug.md"
Cohesion: 0.50
Nodes (3): Cách hiểu đầu tiên, Ghi chú vận hành, Nguyên văn yêu cầu

### Community 279 - "REQUEST — 2026-08-05-bump-sync-user"
Cohesion: 0.50
Nodes (3): Cách hiểu đầu tiên, Nguyên văn user, REQUEST — 2026-08-05-bump-sync-user

### Community 280 - "Request: full claude export"
Cohesion: 0.50
Nodes (3): Hiểu ban đầu, Nguyên văn, Request: full claude export

### Community 281 - "Research — 2026-08-04-workflow-linh-hoat"
Cohesion: 0.50
Nodes (3): A. Đọc code (nội bộ), B. Research ngoài (tavily-primary, 2026-08-04), Research — 2026-08-04-workflow-linh-hoat

### Community 282 - "Brief — Công nghệ speech-to-text word-level realtime (2026)"
Cohesion: 0.50
Nodes (3): Brief — Công nghệ speech-to-text word-level realtime (2026), Câu hỏi, Yêu cầu bằng chứng

### Community 283 - "Brief — Công nghệ speech-to-text word-level realtime (2026)"
Cohesion: 0.50
Nodes (3): Brief — Công nghệ speech-to-text word-level realtime (2026), Câu hỏi, Yêu cầu bằng chứng

### Community 284 - "TDQ STATE (tự sinh — không sửa tay)"
Cohesion: 0.50
Nodes (3): TDQ STATE (tự sinh — không sửa tay), Việc tiếp theo, Đang ở đâu

### Community 285 - "Ghi nhận duyệt"
Cohesion: 0.50
Nodes (4): Ghi nhận duyệt, KHÔNG phải câu duyệt (phản ví dụ), Là câu duyệt khi có ĐỦ hai phần, Lệnh phải chạy NGAY khi nhận ra

### Community 286 - "Định tuyến việc → plugin"
Cohesion: 0.50
Nodes (3): Bảng định tuyến, Giao thức dùng, Định tuyến việc → plugin

### Community 287 - "Mã nhắc của hook"
Cohesion: 0.50
Nodes (4): Bảng 5 mã (danh sách đóng), Hook nhìn thấy thay đổi bằng cách nào, Mã nhắc của hook, Điểm chặn duy nhất

### Community 288 - "Khuôn plan"
Cohesion: 0.50
Nodes (3): Dòng `Mode thực thi`, Khuôn plan, Kiểm trước khi trình

### Community 289 - "Khuôn spec"
Cohesion: 0.50
Nodes (3): Checklist scope — trả lời được hết mới trình, Khuôn spec, Kiểm trước khi trình

## Knowledge Gaps
- **1625 isolated node(s):** `Luật cứng (áp cho cả ba phase)`, `Phần A — Implement (phase `implement`)`, `Phần B — QC (phase `qc`)`, `Phần C — Report (phase `report`)`, `Bảng phase TDQ (tự sinh — KHÔNG sửa tay)` (+1620 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **58 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TestState` connect `TestState` to `.test_reapprove_refreshes_sha256_after_file_changed`, `.test_reapprove_unchanged_file_stays_idempotent`, `.test_mode_external_bi_tu_choi`, `.test_approve_quick_moves_phase_to_implement`, `.test_row_age_ok_bad_ts_types`, `.test_init_set_reset_in_mot_dong_khong_json`, `.test_co_co_json_thi_in_lai_nguyen_state`, `TestProjectRootResolution`?**
  _High betweenness centrality (0.008) - this node is a cross-community bridge._
- **Why does `write_state()` connect `.stop` to `helper.py`?**
  _High betweenness centrality (0.008) - this node is a cross-community bridge._
- **What connects `Luật cứng (áp cho cả ba phase)`, `Phần A — Implement (phase `implement`)`, `Phần B — QC (phase `qc`)` to the rest of the system?**
  _1625 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `tdq_state.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05468215994531784 - nodes in this community are weakly interconnected._
- **Should `.stop` be split into smaller, more focused modules?**
  _Cohesion score 0.09722222222222222 - nodes in this community are weakly interconnected._
- **Should `.write` be split into smaller, more focused modules?**
  _Cohesion score 0.07086197778952935 - nodes in this community are weakly interconnected._
- **Should `.run_inv` be split into smaller, more focused modules?**
  _Cohesion score 0.08350168350168351 - nodes in this community are weakly interconnected._