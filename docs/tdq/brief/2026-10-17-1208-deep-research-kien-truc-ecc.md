# BRIEF — Nghiên cứu chuyên sâu toàn diện kiến trúc, tính năng và thuật toán của dự án ECC

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> "okay tôi muốn bạn deep resreach thật kĩ từng phần từng mảnh của ECC, bạn hãy đọc và phân tích và có thể spawn subagent (tối đa 20 con) để hỗ trợ review chi tiết từng phần của ECC và gửi report kiến trúc tính năng thuật toán của nó cho tôi"

### Đọc bước đầu

- **Mục tiêu**:
  1. Thực hiện một cuộc khảo sát và nghiên cứu sâu (Deep Research) đến từng mảnh ghép của dự án **ECC (Everything Claude Code)** (`ecc-universal` `v2.2.3`) tại `C:\Users\admin\Documents\ECC`.
  2. Huy động hệ thống 10 Subagent chạy song song để phân chia 10 vùng kiến trúc độc lập của ECC (~4.500 files) và mổ xẻ chi tiết từng phân hệ:
     - SA1: Triết lý cốt lõi (`SOUL.md`, `CLAUDE.md`, `AGENTS.md`, `the-shortform-guide.md`, `the-longform-guide.md`, `the-security-guide.md`).
     - SA2: Kiến trúc Rust / Core Engine thế hệ 2 (`ecc2/` - 21 files).
     - SA3: Hệ thống Agents & Subagents (`agents/` 71 files, `.agents/` 109 files).
     - SA4: Hệ thống Hooks & Runtime Interception (`hooks/` 9 files, `scripts/hooks/`).
     - SA5: Hệ thống Rules & Dynamic Contexts (`rules/` 122 files, `contexts/` 3 files, `config/`).
     - SA6: Kho Skills khổng lồ (`skills/` - 311 skills, 613 files: continuous-learning-v2, strategic-compact, eval-harness...).
     - SA7: Hệ thống Slash Commands & Orchestration (`commands/` 97 files, `legacy-command-shims/` 12 files, `workflows/`).
     - SA8: Core Src, Scripts & Dashboard (`src/` 23 files, `scripts/` 370 files, `ecc_dashboard.py`).
     - SA9: Kiến trúc Đa Nền Tảng (22+ IDE/Agent adapters: `.cursor`, `.opencode`, `.kiro`, `pi/` 208 files, `.pi/`, `manifests/`, `schemas/`).
     - SA10: Hệ thống Kiểm thử, Docker Sandbox & Bảo mật (`tests/` 497 files, `docker/` 333 files, `examples/` 67 files, `.github/workflows/` 13 files).
  3. Tổng hợp và xuất bản song song **Standalone HTML Dashboard Report** trực quan và **Báo cáo Markdown chuyên sâu** lưu tại `docs/tdq/reports/`, có bằng chứng mã nguồn cụ thể và Section đối chiếu ECC vs TDQ Workflow.

## Hiểu & kiến thức

### Năng lực dùng được

Phân vân → DÙNG. Kiểm kê ngày 2026-10-17: 9 skill trên đĩa, cộng skill built-in trong context. Không xoá bảng này kể cả khi không có dòng DÙNG nào.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| Agent | built-in | DÙNG | Fan-out 10 subagent phân tích chuyên sâu 10 phân hệ của ECC và kiểm định QC qua `tdq-qc-tester` |
| dataviz | built-in | DÙNG | Thiết kế biểu đồ SVG, bảng màu và stat tiles trong Standalone HTML Dashboard Report |
| tdq-intake | plugin:tdq-workflow | NỀN | mở request, phỏng vấn và chuyển phase |
| tdq-spec | plugin:tdq-workflow | NỀN | lập đặc tả kỹ thuật cho báo cáo kiến trúc ECC |
| tdq-plan | plugin:tdq-workflow | NỀN | lập kế hoạch phân tách task tổng hợp và xuất bản báo cáo |
| tdq-build | plugin:tdq-workflow | NỀN | thực thi biên soạn báo cáo và kiểm định QC |
| tdq-conventions | plugin:tdq-workflow | NỀN | quy tắc workflow, ngôn ngữ 3 tầng |
| tdq-status | plugin:tdq-workflow | NỀN | kiểm tra trạng thái tiến độ |
| tdq-lean | plugin:tdq-workflow | NỀN | bảo đảm cấu trúc báo cáo mạch lạc |
| tdq-setup | plugin:tdq-workflow | NỀN | kiểm tra LSP và môi trường |
| tdq-check-status | plugin:tdq-workflow | NỀN | phục hồi phiên khi có sự cố |
| Đã xét 14 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

### Quy mô thực tế và Tổng hợp phát hiện từ 10 Subagents trên ECC (`C:\Users\admin\Documents\ECC`)

1. **SA1 — Triết lý cốt lõi & 3 Guides (`SOUL.md`, `AGENTS.md`, `the-shortform-guide.md`, `the-longform-guide.md`, `the-security-guide.md`)**:
   - Định vị: *"The Agent Harness Operating System"* (`Optimize the context window. Persist everything else.`).
   - Vòng lặp 7 bước: `plan -> test -> implement -> review -> verify -> remember -> improve`.
   - 5 Nguyên tắc bất biến: Agent-First, Test-Driven (`>= 80%` coverage), Security-First, Immutability (CRITICAL), Plan Before Execute.
   - Kinh tế học Context: Cắt giảm từ 6 MCP mặc định xuống còn 1 (`chrome-devtools`), ưu tiên CLI + Skills; định tuyến model 3 tầng (`haiku` / `sonnet` / `opus`); nén chiến lược ở ngưỡng 50% ngữ cảnh.
   - Bảo mật (`the-security-guide.md`): Phân tích `CVE-2025-59536`, `CVE-2026-21852`, Snyk ToxicSkills (36% nhiễm độc), Simon Willison's Lethal Trifecta và 6 trụ cột phòng thủ (Jailbox KVM, Unicode/BiDi Sanitization, Least Agency, Observability, Process-Group Kill Switch + 30s Dead-Man Switch, Unreviewed Memory Vault).
2. **SA2 — Engine Thế Hệ 2 `ecc2/` (Rust Control Plane, 21 files)**:
   - TUI Control Plane (`ratatui` + `crossterm` + `tokio` + `rusqlite` + `git2`) điều phối đa phiên làm việc trên 10+ harnesses (`Claude`, `Codex`, `OpenCode`, `Gemini`, `Cursor`, `Kiro`, `Trae`, `Zed`, `FactoryDroid`, `Windsurf`).
   - Actor `DbWriter` tách biệt luồng ghi SQLite với luồng đọc `stdout`/`stderr`; đồng bộ TUI bằng con trỏ đơn điệu (monotonic cursor).
   - Daemon 7 pha: phục hồi crash qua PID check, heartbeat, lịch cron, remote dispatch, cân bằng tải đội ngũ (`coordinate_backlog_cycle` với `chronic_saturation_streak`), auto-merge worktree.
   - Chấm điểm rủi ro 4 chiều: $\text{Score} = \text{clamp}(\text{BaseTool} + \text{FileSensitivity} + \text{BlastRadius} + \text{Irreversibility}, 0.0, 1.0)$ với ngưỡng `0.35 / 0.60 / 0.85`.
   - Worktree Shared Dependency Symlink Cache: băm SHA-256 lockfiles để symlink `node_modules`, `target`, `.venv` từ repo gốc; tự ngắt symlink khi lockfile thay đổi.
   - Bounded Harness Eval (`harness_eval.rs`): địa chỉ hóa cấu hình bằng SHA-256 trên JSON chuẩn hóa + `PromotionPolicy` (`min_samples`, `min_mean_delta`, `min_win_rate`) kèm SQLite atomic rollback.
3. **SA3 — Hệ thống Agents (`agents/` 71 files & `.agents/` 109 files)**:
   - 71 agents chia 10 nhóm chuyên môn; phân bổ model: `opus` (4 agents — 5.6%), `sonnet` (61 agents — 85.9%), `haiku` (6 agents — 8.5%). 100% có `## Prompt Defense Baseline`.
   - Cơ chế Pre-Report Gate & 12 False Positives trong `code-reviewer`; GAN Harness (`gan-planner`, `gan-generator`, `gan-evaluator` với công thức $0.3\text{Design} + 0.2\text{Originality} + 0.3\text{Craft} + 0.2\text{Functionality} \ge 7.0$).
   - `.agents/` (109 files): Bản chiếu sang Codex CLI gồm 46 skills + `agents/openai.yaml`.
4. **SA4 — Hệ thống Hooks & Runtime Gate (`hooks/` 9 files, `scripts/hooks/`)**:
   - 7 Lifecycle Events, 24 entries cấp cao + 18 sub-hooks. Sidecar `hooks.metadata.json` gắn SHA-256 fingerprint 12 ký tự.
   - Gộp tiến trình qua `pre-bash-dispatcher.js` và `posttooluse-dispatcher.js` (chạy in-process bằng `require().run()`, tiết kiệm 50–100ms/hook).
   - Batch Format & Typecheck ở `Stop` (`post-edit-accumulator.js` + `stop-format-typecheck.js`).
   - GateGuard Fact-Forcing (`gateguard-fact-force.js`): prior-search credit, AST trivial-edit bypass, sibling collapse, denial dampening sau 3 lần, và bộ phân tích lệnh hủy diệt Bash/PowerShell (`-EncodedCommand` UTF-16LE Base64).
   - Bộ quét từ vựng shell hữu hạn `scanShell` (`block-no-verify.js`) với ngân sách $24L + 4096$.
   - Kỹ thuật Cross-Platform Windows: lọc WSL `bash.exe` stub, lọc `AppInstallerPythonRedirector.exe`, truyền token qua biến môi trường `ECC_LINTER_TOKEN_i` với `windowsVerbatimArguments: true` (vá `CVE-2024-27980`), cắt NTFS `::$DATA`, so sánh `dev + ino` 64-bit.
5. **SA5 — Hệ thống Rules (`rules/` 122 files), `contexts/` (3 files) & `config/` (2 files)**:
   - Kế thừa 3 tầng: Common (10 files, 564 dòng) $\to$ Language (15 ngôn ngữ, 76 files, 5.291 dòng) $\to$ Framework/Domain (6 frameworks, 35 files, 3.525 dòng).
   - `config/project-stack-mappings.json` (19 stacks) và `config/github-native-coordination.json`.
6. **SA6 — Kho 311 Skills (`skills/` — 613 files)**:
   - 269 single-file skills + 42 multi-file executable skill packages trên 9 miền.
   - Giải thuật `continuous-learning-v2` (Homunculus): `observe.sh` $\to$ `observations.jsonl` $\to$ Instincts (`confidence` $0.3..0.9$, decay $-0.02$/tuần) $\to$ gom cụm bằng hệ số Szymkiewicz-Simpson Overlap Coefficient ($\ge 0.5$) để `/evolve` thành Skill/Command/Agent.
   - `strategic-compact` & `context-budget`, `plankton-code-quality`, `eval-harness` (`pass@k` vs `pass^k`), `skill-comply` (kiểm tra thứ tự thời gian `_check_temporal_order`), `operator-approval-loop` (SQLite epoch rotation).
7. **SA7 — Hệ thống 97 Slash Commands, 12 Legacy Shims & Native Workflows (`commands/`, `workflows/`)**:
   - Phân loại 109 command files vào 13 nhóm; 5 mẫu kết nối Command $\to$ Skill/Agent/Workflow/Script.
   - Giải thuật `orch-pipeline` (Right-sizing 4 mức + 2 cổng duyệt) và `workflows/orch-review.workflow.js` (Fan-out 3 chiều $\to$ Barrier Dedup theo `evidence` $\to$ Adversarial Skeptic Verify với ngưỡng `confidence >= 0.8` fail-closed).
8. **SA8 — Core `src/` (23 files), `scripts/` (370 files) & `ecc_dashboard.py`**:
   - `src/llm/`: Provider-agnostic LLM Abstraction Layer (`LLMProvider`, `ReActAgent`, `ToolExecutor` che lỗi nội bộ bằng `GENERIC_TOOL_FAILURE`, `strip_reasoning`).
   - `scripts/`: 6-tier Package Manager detection, 4-tier Session Matching, WASM SQLite State Store (`sql.js`), Memory Vault (`O_NOFOLLOW` + hardlink create-only), và giải thuật **TCAS Multi-Agent Collision Avoidance** ($R(a,b) = 1 - \prod (1 - \omega_i r_i)$ kết hợp Szymkiewicz-Simpson line overlap, BFS import graph $\gamma=0.5$, và LCA tree distance).
9. **SA9 — Kiến trúc Đa Nền Tảng (22+ Harnesses), `pi/` (208 files), `manifests/` (10 files), `schemas/` (17 files)**:
   - Pipeline 5 giai đoạn của `install-apply.js`, Canonical Agent IR (`ecc.agent-ir.v1`), `.pi/` (Zero-copy live adapter) vs `pi/core/` (208 files curated 100% offline).
   - 17 JSON Schemas + Cryptographic Digest Chain (6 mã băm SHA-256) + Static AST Dependency Closure (`validate-carrier-closure.js`).
10. **SA10 — Hệ thống Kiểm thử (`tests/` 497 files), Docker Lab (`docker/` 333 files), `examples/` (67 files) & CI/Security**:
    - Custom isolated test runner `tests/run-all.js` + `windows-test-env.js`.
    - Docker 5-Arm Preregistered Benchmark (`complex-eval` `cases`..`cases4`) và `gateguard-effectiveness` multi-turn simulator.
    - Bảo mật chuỗi cung ứng: 13 GitHub workflows với SHA-pinned actions, `scan-supply-chain-iocs.js` (chống Shai-Hulud IOCs), `pr-burst-guard.yml`, và SLSA Level 3 provenance.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Research web | BỎ | Toàn bộ mã nguồn ECC đã nằm sẵn trên đĩa tại `C:\Users\admin\Documents\ECC` và đã được 10 subagent mổ xẻ đầy đủ |
| Interview | CÓ | Đã hoàn tất 1 vòng phỏng vấn chốt định dạng báo cáo đầu ra (`1a`), trọng tâm đối chiếu (`2a`) và mức QC (`3a` = `ultra`) |
| QC độc lập | CÓ | Thẩm định độc lập ở mức `ultra` qua `tdq-qc-tester` |

## Hỏi đáp

### Vòng 1 (2026-10-17 12:30)

1. **Định dạng Báo cáo đầu ra bạn mong muốn**:
   - A (đề xuất): Xuất bản song song cả **Standalone HTML Dashboard Report** trực quan (có biểu đồ kiến trúc SVG, bảng tra cứu, Dark/Light mode) VÀ **Báo cáo Markdown chuyên sâu** lưu tại `docs/tdq/reports/`.
   - B: Chỉ xuất bản 1 file Standalone HTML Dashboard Report duy nhất.
   - C: Chỉ xuất bản 1 file Báo cáo Markdown thuần túy.
   - **Trả lời**: `1a` (Xuất bản song song cả Standalone HTML Dashboard Report và Báo cáo Markdown chuyên sâu).
2. **Trọng tâm phân tích ngoài Kiến trúc, Tính năng & Giải thuật của ECC**:
   - A (đề xuất): Có — Bổ sung thêm 1 Section chuyên biệt **So sánh đối chiếu ECC vs TDQ Workflow** và rút ra **Top các tính năng/giải thuật tinh hoa nhất** của ECC mà TDQ có thể học hỏi.
   - B: Không — Chỉ thuần túy mô tả kiến trúc, tính năng và thuật toán nội tại của ECC.
   - **Trả lời**: `2a` (Có bổ sung Section So sánh đối chiếu ECC vs TDQ Workflow và Top tính năng/giải thuật tinh hoa).
3. **Mức QC (chất lượng kiểm định cho request này)**:
   - A (đề xuất): `ultra` — DoD + kiểm tra toàn vẹn số liệu/đường dẫn + thẩm định độc lập qua `tdq-qc-tester`.
   - B: `full`
   - C: `lite`
   - **Trả lời**: `3a` (`ultra`).
4. **Bạn muốn bổ sung thêm gì không?**
   - A (đề xuất): Không, đủ rồi — làm tiếp đi.
   - B: Có — tôi nói thêm.
   - **Trả lời**: `4a` (Không, đủ rồi — làm tiếp đi).
