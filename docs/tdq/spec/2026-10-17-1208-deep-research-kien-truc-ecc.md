# SPEC — Báo cáo Nghiên cứu Chuyên sâu Toàn diện Kiến trúc, Tính năng & Giải thuật của ECC (`ecc-universal` `v2.2.3`)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

- **Request**: `2026-10-17-1208-deep-research-kien-truc-ecc`
- **Lane**: `full`
- **Version**: `1.0`
- **Ngày**: `2026-10-17`

## 1. Mục tiêu & Phạm vi

### 1.1. Mục tiêu
Biên soạn và xuất bản bộ đôi báo cáo kỹ thuật chuyên sâu (**Standalone HTML Dashboard Report** trực quan + **Báo cáo Markdown** đầy đủ) phân tích toàn diện kiến trúc, tính năng, cơ chế bảo mật và các giải thuật cốt lõi của dự án **ECC (`Everything Claude Code` / `ecc-universal` `v2.2.3`, ~4.500 files)** tại `C:\Users\admin\Documents\ECC`, kèm Section đối chiếu trực diện với **TDQ Workflow (`v0.71.0`)** và đề xuất các giải thuật tinh hoa có thể học hỏi.

### 1.2. Trong phạm vi (In-Scope)
1. **Xuất bản Báo cáo Markdown chuyên sâu** tại `docs/tdq/reports/2026-10-17-1208-deep-research-kien-truc-ecc.md` bao phủ 11 chương (10 phân hệ kiến trúc của ECC từ SA1–SA10 + Chương 11 So sánh đối chiếu ECC vs TDQ Workflow & Top 10 tinh hoa học hỏi).
2. **Xuất bản Standalone HTML Dashboard Report** tại `docs/tdq/reports/2026-10-17-1208-deep-research-kien-truc-ecc.html` hoạt động độc lập 100% offline (inline CSS + JS + SVG), hỗ trợ Dark/Light mode, điều hướng sticky sidebar, bộ lọc tìm kiếm nhanh, các sơ đồ kiến trúc SVG (System Architecture, Hook Lifecycle, ECC2 Rust Control Plane, Continuous Learning v2 Homunculus, TCAS Collision Avoidance, Multi-Harness Transpiler), công thức toán học/giải thuật rõ ràng và bảng đối chiếu ECC vs TDQ Workflow.
3. **Kiểm chứng tự động bằng bộ kiểm thử của dự án** xác minh sự tồn tại, cấu trúc HTML/SVG hợp lệ, độ phủ đầy đủ 10 phân hệ SA1–SA10 + đối chiếu TDQ Workflow, và tính chính xác của các số liệu/đường dẫn mã nguồn thực tế trong cả 2 báo cáo.

### 1.3. Ngoài phạm vi (Out-of-Scope)
- Không sửa đổi bất kỳ tệp nào bên trong kho mã nguồn `C:\Users\admin\Documents\ECC`.
- Không sửa đổi logic runtime của các hooks/scripts hiện tại của TDQ Workflow trong request này (request này thuần túy xuất bản báo cáo nghiên cứu sâu và kiểm chứng chất lượng báo cáo).

## 2. Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Research web | BỎ | Toàn bộ mã nguồn ECC đã nằm sẵn trên đĩa tại `C:\Users\admin\Documents\ECC` và đã được 10 subagent mổ xẻ đầy đủ |
| Interview | CÓ | Đã hoàn tất 1 vòng phỏng vấn chốt định dạng báo cáo đầu ra (`1a`), trọng tâm đối chiếu (`2a`) và mức QC (`3a` = `ultra`) |
| QC độc lập | CÓ | Thẩm định độc lập ở mức `ultra` qua `tdq-qc-tester` |

## 2b. Ranh giới module

Bảng ranh giới module dưới đây xác định các thành phần được tạo mới và mối liên hệ kiểm chứng trong repo:

| Module | Vùng file | Phụ thuộc vào | Được gọi bởi | Trách nhiệm |
|---|---|---|---|---|
| `markdown-report` | `docs/tdq/reports/2026-10-17-1208-deep-research-kien-truc-ecc.md` | Dữ liệu kiểm chứng từ `C:\Users\admin\Documents\ECC` và `docs/tdq/brief/2026-10-17-1208-deep-research-kien-truc-ecc.md` | Người dùng đọc trực tiếp, trình kiểm thử của dự án | Tài liệu kỹ thuật Markdown chuyên sâu 11 chương (10 phân hệ ECC + So sánh TDQ Workflow) dùng để lưu trữ, tra cứu và grep |
| `html-dashboard-report` | `docs/tdq/reports/2026-10-17-1208-deep-research-kien-truc-ecc.html` | `markdown-report` (đồng bộ số liệu & giải thuật), nguyên tắc thiết kế từ skill `dataviz` | Trình duyệt của người dùng, trình kiểm thử của dự án | Bảng điều khiển báo cáo tương tác độc lập (Dark/Light theme, sơ đồ kiến trúc SVG, thẻ KPI, bộ lọc tìm kiếm, bảng công thức giải thuật và ma trận đối chiếu ECC vs TDQ) |

## 3. Đầu ra đo được & Phương pháp tiếp cận

### 3.1. Đầu ra đo được
1. **Tệp Báo cáo Markdown (`docs/tdq/reports/2026-10-17-1208-deep-research-kien-truc-ecc.md`)**:
   - Đầy đủ **11 chương chuyên sâu**:
     - **Chương 1 (SA1)**: Triết lý cốt lõi (`SOUL.md`, `AGENTS.md`), vòng lặp 7 bước, Kinh tế học Context (MCP pruning, model routing, strategic compaction 50%) và 6 trụ cột Bảo mật (`the-security-guide.md`, `CVE-2025-59536`, `CVE-2026-21852`, Lethal Trifecta, Jailbox, Kill Switch).
     - **Chương 2 (SA2)**: Engine thế hệ mới `ecc2/` bằng Rust (`ratatui`, `tokio`, `rusqlite`, `git2`) — Kiến trúc Actor `DbWriter`, Daemon 7 pha với `chronic_saturation_streak`, công thức chấm điểm rủi ro 4 chiều $\text{Score} \in [0, 1]$, Worktree Shared Dependency Symlink Cache theo SHA-256 lockfiles, và Bounded Harness Evaluation (`PromotionPolicy`).
     - **Chương 3 (SA3)**: Hệ thống 71 Agents (`agents/`) & 109 files Codex Projection (`.agents/`) — Phân tích 10 nhóm chuyên môn, tỷ lệ phân bổ model (`opus` 5.6%, `sonnet` 85.9%, `haiku` 8.5%), `Prompt Defense Baseline`, Pre-Report Gate & 12 False Positives của `code-reviewer`, và công thức chấm điểm GAN Harness ($0.3D + 0.2O + 0.3C + 0.2F \ge 7.0$).
     - **Chương 4 (SA4)**: Hệ thống Hooks & Runtime Gate (`hooks/`, `scripts/hooks/`) — 7 Lifecycle Events, 24 entries + 18 sub-hooks, sidecar `hooks.metadata.json` (12-char SHA-256 fingerprint), In-process Dispatcher (`require().run()`), Batch Format/Typecheck ở `Stop`, giải thuật GateGuard Fact-Forcing, bộ quét từ vựng shell `scanShell` ($24L+4096$), và 6 kỹ thuật Cross-Platform đặc trị lỗi Windows.
     - **Chương 5 (SA5)**: Hệ thống 122 Rules (`rules/`), `contexts/` & `config/` — Kiến trúc kế thừa 3 tầng (Common $\to$ 15 Languages $\to$ 6 Frameworks), `project-stack-mappings.json` (19 stacks) và `github-native-coordination.json`.
     - **Chương 6 (SA6)**: Kho 311 Skills (`skills/` — 613 files) — Giải thuật `continuous-learning-v2` (Homunculus, Instinct confidence decay, gom cụm Szymkiewicz-Simpson Overlap Coefficient $\ge 0.5$), `strategic-compact`, `plankton-code-quality`, `eval-harness` (`pass@k` vs `pass^k`), `skill-comply` (`_check_temporal_order`), `operator-approval-loop`.
     - **Chương 7 (SA7)**: Hệ thống 97 Slash Commands, 12 Legacy Shims & Native Workflows — Phân loại 13 nhóm chức năng, 5 mẫu kết nối Command $\to$ Skill/Agent/Workflow/Script, giải thuật `orch-pipeline` và `workflows/orch-review.workflow.js` (Fan-out $\to$ Barrier Dedup $\to$ Adversarial Skeptic Verify `confidence >= 0.8` fail-closed).
     - **Chương 8 (SA8)**: Core `src/` (23 Python files), `scripts/` (370 files) & `ecc_dashboard.py` — LLM Abstraction Layer (`src/llm/`), 6-tier Package Manager detection, 4-tier Session Matching, WASM SQLite State Store, Memory Vault (`O_NOFOLLOW` + hardlink), và công thức toán học **TCAS Multi-Agent Proximity & Collision Avoidance** ($R(a,b) = 1 - \prod (1 - \omega_i r_i)$).
     - **Chương 9 (SA9)**: Kiến trúc Đa Nền Tảng (22+ Harnesses), `.pi/` vs `pi/core/` (208 files offline), `manifests/` (10 files) & `schemas/` (17 files) — Pipeline 5 giai đoạn của `install-apply.js`, Canonical Agent IR (`ecc.agent-ir.v1`), chuỗi 6 mã băm SHA-256 (`Cryptographic Digest Chain`) và Static AST Dependency Closure (`validate-carrier-closure.js`).
     - **Chương 10 (SA10)**: Kiểm thử (497 files), Docker Empirical Lab (`docker/` 333 files), `examples/` (67 files) & Bảo mật Chuỗi cung ứng CI/CD — Runner cô lập, 5-Arm Benchmark `complex-eval` (`cases`..`cases4`), `gateguard-effectiveness`, `scan-supply-chain-iocs.js`, `pr-burst-guard.yml`, SLSA Level 3.
     - **Chương 11**: Bảng đối chiếu toàn diện **ECC (`v2.2.3`) vs TDQ Workflow (`v0.71.0`)** trên 10 trục kiến trúc + **Top 10 tính năng/giải thuật tinh hoa nhất của ECC** mà TDQ Workflow có thể chọn lọc học hỏi.
2. **Tệp Standalone HTML Dashboard Report (`docs/tdq/reports/2026-10-17-1208-deep-research-kien-truc-ecc.html`)**:
   - Giao diện Dashboard kỹ thuật chuẩn mực (áp dụng skill `dataviz`), hỗ trợ chuyển đổi Dark/Light theme, mục lục điều hướng nổi, thanh tìm kiếm/lọc theo phân hệ, tối thiểu 4 sơ đồ SVG trực quan hóa kiến trúc & thuật toán của ECC, các hộp công thức toán học (TCAS, ECC2 Risk Score, Instinct Overlap, GAN Rubric, `pass@k`/`pass^k`), bảng tra cứu có thể lọc và ma trận đối chiếu ECC vs TDQ Workflow.

### 3.2. Phương pháp tiếp cận & Lý do
- Tổ chức nội dung theo cấu trúc phân tầng từ **Triết lý & Kinh tế học Context (SA1)** $\to$ **Kiến trúc Điều khiển & Thực thi (SA2, SA3, SA4, SA8)** $\to$ **Tri thức, Quy tắc & Kỹ năng (SA5, SA6, SA7)** $\to$ **Phân phối Đa nền tảng & Kiểm định Thực nghiệm (SA9, SA10)** $\to$ **Đối chiếu & Đề xuất cho TDQ Workflow**.
- Mọi nhận định và giải thuật đều trích dẫn đường dẫn chính xác tới tệp mã nguồn của ECC (`C:\Users\admin\Documents\ECC\...`) và TDQ Workflow.

## 3b. Năng lực & công cụ

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

## 4. Yêu cầu thường trực (Standing Requirements)

- **Log service**: Giữ nguyên cơ chế ghi nhật ký chuẩn của TDQ Workflow (`docs/workinglog/2026-10-17.md` và `docs/tdq/timing.jsonl`); quá trình kiểm chứng tự động không sinh tệp rác ra ngoài thư mục tạm.
- **Cấm placeholder**: Tuyệt đối không dùng `TODO`, `TBD`, `...` rút gọn làm mất nội dung trong cả báo cáo Markdown và báo cáo HTML. Tất cả 10 phân hệ SA1–SA10 và Chương 11 phải được trình bày trọn vẹn.
- **Kiểm thử cho từng phần**: Mọi yêu cầu đầu ra (Markdown 11 chương, HTML hợp lệ + SVG + Dark/Light mode + Search filter, công thức giải thuật, bảng đối chiếu TDQ) đều phải có điều kiện PASS tự động rõ ràng.

## 5. Ràng buộc & Rủi ro

- **Ràng buộc dữ liệu thực tế**: Mọi con số thống kê (71 agents, 311 skills / 613 files, 97 active commands + 12 legacy shims, 122 rules, 21 files `ecc2/`, 17 schemas, 10 manifests, 497 files kiểm thử, 333 docker files) phải khớp chính xác với kết quả kiểm đếm trên đĩa tại `C:\Users\admin\Documents\ECC`.
- **Ràng buộc Standalone HTML**: Tệp HTML không được phụ thuộc CDN ngoài (font hệ thống + inline CSS/SVG/JS) để mở trực tiếp trên mọi trình duyệt kể cả khi không có mạng.
- **Rủi ro kích thước tệp lớn**: Do bao phủ toàn bộ 10 phân hệ chuyên sâu, tệp Markdown và HTML sẽ có dung lượng lớn; cần tổ chức bố cục rõ ràng, có mục lục neo (anchor links), thanh tìm kiếm trực tiếp và phân tách mạch lạc.

## 6. Phạm vi QC & Định nghĩa hoàn thành (Definition of Done)

### Phạm vi QC (`muc_qc = ultra`)
- Chạy bộ kiểm thử tự động của dự án qua `python3 scripts/tdq_test.py --silent`.
- Chạy `doc_lint.py` trên các tài liệu workflow (`brief`, `spec`, `plan`, `qc`, `report`).
- Triệu hồi subagent độc lập `tdq-workflow:tdq-qc-tester` ở pha `qc` để thẩm định chéo nội dung báo cáo Markdown & HTML so với mã nguồn thực tế tại `C:\Users\admin\Documents\ECC`.

### Definition of Done (DoD)
- [x] Tệp `docs/tdq/reports/2026-10-17-1208-deep-research-kien-truc-ecc.md` tồn tại, trình bày đầy đủ 11 chương (10 phân hệ SA1–SA10 + Chương 11 So sánh ECC vs TDQ Workflow & Top 10 đề xuất học hỏi), kèm đầy đủ công thức giải thuật và đường dẫn chứng cứ mã nguồn.
- [x] Tệp `docs/tdq/reports/2026-10-17-1208-deep-research-kien-truc-ecc.html` tồn tại, tự thân 100% (inline CSS/JS/SVG, không phụ thuộc CDN), parse HTML không lỗi, có Dark/Light mode, tìm kiếm tức thời, tối thiểu 4 sơ đồ SVG kiến trúc/giải thuật và đầy đủ nội dung 11 phần.
- [x] Các điều kiện kiểm thử tự động về cấu trúc DOM/SVG, độ phủ 11 chương, sự hiện diện của các giải thuật trọng tâm (`TCAS`, `Szymkiewicz-Simpson`, `GateGuard`, `scanShell`, `ecc2`, `orch-review`, `Cryptographic Digest Chain`) đều đạt PASS.
- [x] Toàn bộ bộ kiểm thử của repo chạy qua `python3 scripts/tdq_test.py --silent` đạt PASS, và `tdq-qc-tester` độc lập trả về phán quyết PASS.

## 7. Câu hỏi mở

*(Trống — toàn bộ câu hỏi đã được chốt tại Vòng 1 trong Brief).*
