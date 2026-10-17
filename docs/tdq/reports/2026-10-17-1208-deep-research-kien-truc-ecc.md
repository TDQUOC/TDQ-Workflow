# Báo Cáo Nghiên Cứu Chuyên Sâu Kiến Trúc Everything Claude Code (`ecc-universal` `v2.2.3`) & Đối Chiếu Tinh Hoa Với `TDQ Workflow` (`v0.71.0`)

- **Mã hồ sơ báo cáo**: `2026-10-17-1208-deep-research-kien-truc-ecc`
- **Đối tượng giải phẫu**: Dự án `ecc-universal` (`Everything Claude Code` — phiên bản `v2.2.3`) tại `C:\Users\admin\Documents\ECC`
- **Đối tượng đối chiếu**: Dự án `TDQ Workflow` (`v0.71.0`) tại `C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow`
- **Quy mô định lượng toàn kho `ECC` (`v2.2.3`)**: Xấp xỉ `~4.500` files, bao gồm:
  - `311` skills (`613` files trong `skills/`)
  - `71` agents (`agents/`) + `109` files chiếu sang OpenAI Codex CLI (`.agents/`)
  - `97` slash commands hoạt động + `12` legacy shims (`109` files trong `commands/`)
  - `122` rules (`9.525` dòng Markdown trong `rules/` chia 3 tầng) + `3` contexts (`contexts/`) + `2` cấu hình định tuyến (`config/`)
  - `21` Rust source files trong `ecc2/` (Control Plane thế hệ 2)
  - `23` Python files trong `src/` + `370` Node/Shell/Python scripts trong `scripts/`
  - `208` files trong gói độc lập `pi/core/` + adapter trực tiếp `.pi/`
  - `10` manifests (`manifests/`) + `17` JSON schemas (`schemas/`)
  - `497` test files (`tests/`) + `333` docker files (`docker/`) + `67` examples (`examples/`) + `13` GitHub Actions workflows (`.github/workflows/`)

---

## Tóm Tắt Điều Hành (Executive Summary)

Dự án `Everything Claude Code` (`ecc-universal` `v2.2.3`) không đơn thuần là một bộ sưu tập prompt hay cấu hình mẫu, mà được thiết kế như một **"The Agent Harness Operating System"** (Hệ điều hành lớp vỏ điều phối Agent) với khẩu hiệu kiến trúc xuyên suốt: *"Optimize the context window. Persist everything else."*

Báo cáo kỹ thuật này trình bày kết quả giải phẫu toàn diện 10 phân hệ kiến trúc cốt lõi (`SA1` đến `SA10`) của `ECC` từ tầng triết lý bảo mật, mặt phẳng điều khiển Rust bất đồng bộ `ecc2`, mạng lưới `71` agents và `311` skills, cơ chế chặn runtime `GateGuard` và bộ quét từ vựng shell `scanShell`, giải thuật chống va chạm đa agent `TCAS`, quy trình thẩm định đối kháng `orch-review`, chuỗi băm toàn vẹn 6 mắt xích `Cryptographic Digest Chain`, cho đến phòng thí nghiệm thực nghiệm `333` files Docker và `497` files kiểm thử. Trên cơ sở đó, Chương 11 thực hiện đối chiếu trực diện 10 trục kiến trúc giữa `ECC` (`v2.2.3`) và `TDQ Workflow` (`v0.71.0`), đồng thời đúc kết **Top 10 tính năng và giải thuật tinh hoa** có thể chọn lọc chuyển giao sang `TDQ Workflow`.

### Bảng Tổng Hợp 10 Phân Hệ Kiến Trúc (`SA1` .. `SA10`)

| Mã phân hệ | Tên phân hệ kiến trúc | Đường dẫn trọng tâm | Quy mô định lượng | Giải thuật / Cơ chế cốt lõi |
| :--- | :--- | :--- | :--- | :--- |
| **`SA1`** | Triết lý cốt lõi, Kinh tế học Context & 6 Trụ cột Bảo mật | `SOUL.md`, `AGENTS.md`, `the-security-guide.md`, `the-shortform-guide.md`, `the-longform-guide.md` | 5 tài liệu nền tảng + 6 trụ cột phòng thủ | Vòng lặp 7 bước, cắt giảm 6 MCP xuống 1, định tuyến model 3 tầng (`haiku`/`sonnet`/`opus`), nén chiến lược 50%, vá `CVE-2025-59536` & `CVE-2026-21852` |
| **`SA2`** | Engine Thế Hệ 2 `ecc2/` (Rust Control Plane) | `ecc2/Cargo.toml`, `ecc2/src/` | `21` Rust files, hỗ trợ 10+ `HarnessKind` | Actor `DbWriter` tách luồng SQLite, Daemon 7 pha, Chấm điểm rủi ro 4 chiều, Worktree SHA-256 Lockfile Symlink Cache, Bounded Harness Evaluation |
| **`SA3`** | Hệ thống Agents & Codex Projection | `agents/`, `.agents/` | `71` agents (`agents/`) + `109` files (`.agents/`) | Phủ 100% `Prompt Defense Baseline`, `Pre-Report Gate` lọc 12 False Positives, vòng lặp đối kháng `GAN Harness` ($\text{Score}_{\text{GAN}} \ge 7.0$) |
| **`SA4`** | Hệ thống Hooks, `GateGuard` & `scanShell` | `hooks/`, `scripts/hooks/`, `scripts/lib/` | `9` hook configs + `24` entries + `18` sub-hooks | In-process dispatcher `require().run()`, Batch Format/Typecheck ở `Stop`, `GateGuard` Fact-Forcing, `scanShell` ($24L+4096$), 6 kỹ thuật đặc trị Windows |
| **`SA5`** | Hệ thống Rules 3 Tầng, Contexts & Config | `rules/`, `contexts/`, `config/` | `122` rules (`9.525` dòng), `3` contexts, `2` configs | Kế thừa 3 tầng (Common 10 files $\to$ 15 Languages 76 files $\to$ 6 Frameworks 35 files), nạp lười theo `paths:`, nhận diện 19 stacks |
| **`SA6`** | Kho Skills & Học Liên Tục Homunculus | `skills/` | `311` skills (`613` files: 269 đơn, 42 đa file) | `continuous-learning-v2` (Instinct confidence $[0.3, 0.9]$), gom cụm `Szymkiewicz-Simpson` ($\ge 0.5$), `eval-harness` ($\text{pass}@k$ vs $\text{pass}^k$) |
| **`SA7`** | Slash Commands, Legacy Shims & Native Workflows | `commands/`, `workflows/` | `97` active commands + `12` legacy shims | `plan-orchestrate` Fail-Closed, `orch-pipeline` 4 cỡ, `orch-review` 3 giai đoạn (Fan-out $\to$ Barrier Dedup $\to$ Adversarial Skeptic Verify) |
| **`SA8`** | Core Python `src/`, `scripts/` & `TCAS` | `src/`, `scripts/`, `ecc_dashboard.py` | `23` Python files + `370` scripts | `ToolExecutor` ẩn stack trace, 6-tier PM detection, Memory Vault `O_NOFOLLOW`, chống va chạm đa agent `TCAS` $R(a,b)$ |
| **`SA9`** | Đa Nền Tảng (22+ Harnesses), IR & Schemas | `.pi/`, `pi/core/`, `manifests/`, `schemas/` | `208` files `pi/core/`, `10` manifests, `17` schemas | Trình cài 5 pha, `Canonical Agent IR`, `Cryptographic Digest Chain` 6 tầng SHA-256, `Static AST Dependency Closure` |
| **`SA10`** | Hệ thống Kiểm thử, Docker Lab & CI/CD Security | `tests/`, `docker/`, `examples/`, `.github/workflows/` | `497` tests, `333` docker files, `67` examples, `13` workflows | Cô lập `HOME`/`USERPROFILE` mỗi test, 5-Arm Benchmark (`187` files), GateGuard Lab (`119` files), ghim 40-char SHA, SLSA Level 3 |

### Sơ Đồ Kiến Trúc Tổng Thể `ecc-universal` (`v2.2.3`)

```
+---------------------------------------------------------------------------------------------------+
|                        TẦNG TRIẾT LÝ, QUY TẮC & KINH TẾ HỌC NGỮ CẢNH (SA1, SA5)                   |
|  SOUL.md / AGENTS.md  |  122 Rules (9.525 dòng, 3 tầng)  |  3 Contexts  |  6 Trụ Cột Bảo Mật      |
+-------------------------------------------------+-------------------------------------------------+
                                                  |
         +----------------------------------------+----------------------------------------+
         v                                        v                                        v
+---------------------------------+  +------------------------------------+  +----------------------+
| MẶT PHẲNG ĐIỀU PHỐI TRI THỨC    |  | MẶT PHẲNG CỔNG RUNTIME & HOOKS     |  | ENGINE THẾ HỆ 2      |
| (SA3, SA6, SA7)                 |  | (SA4, SA8)                         |  | (SA2: ecc2/ 21 files)|
| - 71 Agents + .agents/ (109)    |  | - In-Process Hook Dispatcher       |  | - Rust Tokio + TUI   |
| - 311 Skills (613 files)        |  | - GateGuard Fact-Forcing           |  | - DbWriter Actor     |
| - 97 Commands + 12 Shims        |  | - scanShell (24L + 4096 steps)     |  | - Daemon 7 Pha       |
| - GAN Harness & orch-review     |  | - Batch Format/Typecheck @ Stop    |  | - Risk Score 4 Chiều |
| - Homunculus Szymkiewicz-Simpson|  | - TCAS Proximity R(a,b)            |  | - Worktree Symlink   |
+----------------+----------------+  +-----------------+------------------+  +-----------+----------+
                 |                                     |                                 |
                 +-------------------------------------+---------------------------------+
                                                       v
+---------------------------------------------------------------------------------------------------+
|               TẦNG BIÊN DỊCH ĐA NỀN TẢNG, ĐÓNG GÓI & KIỂM ĐỊNH THỰC NGHIỆM (SA9, SA10)            |
|  Canonical Agent IR (ecc.agent-ir.v1) -> 22+ Harnesses  |  pi/core/ (208 files)  |  17 Schemas    |
|  Cryptographic Digest Chain (6 SHA-256 links)           |  497 Tests + 333 Docker Empirical Files |
+---------------------------------------------------------------------------------------------------+
```

---

## Mục Lục

1. [Chương 1 (`SA1`) — Triết Lý Cốt Lõi, Kinh Tế Học Context & 6 Trụ Cột Bảo Mật](#chương-1-sa1--triết-lý-cốt-lõi-kinh-tế-học-context--6-trụ-cột-bảo-mật)
2. [Chương 2 (`SA2`) — Engine Thế Hệ 2 `ecc2/` (Rust Control Plane, 21 Files)](#chương-2-sa2--engine-thế-hệ-2-ecc2-rust-control-plane-21-files)
3. [Chương 3 (`SA3`) — Hệ Thống `71` Agents (`agents/`) & `109` Files Codex Projection (`.agents/`)](#chương-3-sa3--hệ-thống-71-agents-agents--109-files-codex-projection-agents)
4. [Chương 4 (`SA4`) — Hệ Thống Hooks, `GateGuard` Fact-Forcing & Bộ Quét `scanShell`](#chương-4-sa4--hệ-thống-hooks-gateguard-fact-forcing--bộ-quét-scanshell)
5. [Chương 5 (`SA5`) — Hệ Thống `122` Rules (`rules/`), `contexts/` (3 Files) & `config/` (2 Files)](#chương-5-sa5--hệ-thống-122-rules-rules-contexts-3-files--config-2-files)
6. [Chương 6 (`SA6`) — Kho `311` Skills (`skills/` — `613` Files) & Giải Thuật Học Liên Tục](#chương-6-sa6--kho-311-skills-skills--613-files--giải-thuật-học-liên-tục)
7. [Chương 7 (`SA7`) — Hệ Thống `97` Slash Commands, `12` Legacy Shims & Native Workflows](#chương-7-sa7--hệ-thống-97-slash-commands-12-legacy-shims--native-workflows)
8. [Chương 8 (`SA8`) — Core `src/` (`23` Python Files), `scripts/` (`370` Files) & Giải Thuật `TCAS`](#chương-8-sa8--core-src-23-python-files-scripts-370-files--giải-thuật-tcas)
9. [Chương 9 (`SA9`) — Kiến Trúc Đa Nền Tảng (22+ Harnesses), `pi/core/` (`208` Files), `manifests/` & `schemas/`](#chương-9-sa9--kiến-trúc-đa-nền-tảng-22-harnesses-picore-208-files-manifests--schemas)
10. [Chương 10 (`SA10`) — Hệ Thống Kiểm Thử (`497` Files), Docker Empirical Lab (`333` Files) & Bảo Mật Chuỗi Cung Ứng CI/CD](#chương-10-sa10--hệ-thống-kiểm-thử-497-files-docker-empirical-lab-333-files--bảo-mật-chuỗi-cung-ứng-cicd)
11. [Chương 11 — Đối Chiếu Toàn Diện `ECC` (`v2.2.3`) vs `TDQ Workflow` (`v0.71.0`) & Top 10 Tinh Hoa Đề Xuất Học Hỏi](#chương-11--đối-chiếu-toàn-diện-ecc-v223-vs-tdq-workflow-v0710--top-10-tinh-hoa-đề-xuất-học-hỏi)

---

## Chương 1 (`SA1`) — Triết Lý Cốt Lõi, Kinh Tế Học Context & 6 Trụ Cột Bảo Mật

Phân hệ `SA1` định hình nền tảng tư tưởng và biên giới an toàn cho toàn bộ kho mã nguồn thông qua 5 tài liệu gốc: `SOUL.md`, `AGENTS.md`, `the-shortform-guide.md`, `the-longform-guide.md` và `the-security-guide.md`.

### 1.1. Định Vị "The Agent Harness Operating System" & Vòng Lặp 7 Bước (`SOUL.md`, `AGENTS.md`)

Trong `SOUL.md` và `AGENTS.md`, `ECC` xác lập rằng cửa sổ ngữ cảnh (context window) là tài nguyên khan hiếm nhất kiểu RAM khả biến, trong khi đĩa cứng, cơ sở dữ liệu trạng thái và hệ thống kiểm soát phiên bản mới là bộ nhớ bền vững:
- **Châm ngôn kiến trúc**: *"Optimize the context window. Persist everything else."*
- **Chu trình vận hành chuẩn 7 bước**:
  ```
  plan -> test -> implement -> review -> verify -> remember -> improve
  ```
- **5 Nguyên tắc bất biến (Non-Negotiable Invariants)**:
  1. **Agent-First**: Mọi tác vụ phức tạp đều phải phân tách và ủy quyền cho subagent chuyên biệt có phạm vi hẹp thay vì nhồi nhét vào một phiên hội thoại đơn lẻ.
  2. **Test-Driven (`RED -> GREEN -> IMPROVE`)**: Bắt buộc viết kiểm thử thất bại trước, triển khai tối thiểu để vượt qua kiểm thử, rồi mới tái cấu trúc; duy trì độ bao phủ kiểm thử $\ge 80\%$.
  3. **Security-First**: Không bao giờ đánh đổi an toàn lấy tiện lợi; mọi đầu vào từ file, PR diff, log hay trang web đều bị coi là dữ liệu không đáng tin cậy (untrusted content).
  4. **Immutability (CRITICAL)**: Luôn tạo đối tượng/bản ghi mới thay vì biến đổi trạng thái tại chỗ (in-place mutation), giúp ngăn ngừa lỗi rò rỉ trạng thái ngầm giữa các bước điều phối.
  5. **Plan Before Execute**: Bắt buộc lập kế hoạch kiến trúc và xác định rõ danh sách file chịu ảnh hưởng trước khi chạm vào mã nguồn.

### 1.2. Kinh Tế Học Context (`the-shortform-guide.md`, `the-longform-guide.md`)

Hai tài liệu hướng dẫn thực chiến phân tích chi phí ẩn của các kết nối công cụ và đề xuất 3 cơ chế tiết kiệm ngữ cảnh:
1. **Cắt giảm MCP mặc định từ 6 xuống còn 1 (`chrome-devtools`)**: Mỗi MCP server bật sẵn thường bơm hàng chục định nghĩa JSON schema của tool vào system prompt ở mỗi lượt gọi. Bằng cách tắt các MCP thừa và chuyển sang dùng CLI kết hợp Skills nạp theo yêu cầu, `ECC` tiết kiệm từ **15.000 đến 40.000 tokens** system prompt mỗi lượt.
2. **Định tuyến Model 3 tầng (3-Tier Model Routing)**:
   - `haiku`: Dành cho tác vụ tìm kiếm nhanh, tra cứu tài liệu, dọn dẹp mã chết hoặc sinh khung boilerplate đơn giản.
   - `sonnet`: Gánh vác **85.9%** khối lượng công việc kỹ thuật (triển khai tính năng, viết kiểm thử, review mã nguồn theo ngôn ngữ).
   - `opus`: Dành riêng cho các quyết định kiến trúc vĩ mô, lập kế hoạch đa bước phức tạp và thẩm định bảo mật chuyên sâu.
3. **Nén chiến lược (`strategic-compact`) ở ngưỡng 50%**: Thay vì đợi cơ chế `auto-compact` tự động kích hoạt ở mức 95% dung lượng context (thời điểm chất lượng suy luận của LLM đã suy giảm do hiện tượng *lost-in-the-middle* và dễ xảy ra nén cụt giữa chừng một thao tác sửa code), `ECC` chủ động nhắc nén tại các điểm chuyển giao pha логиc (ví dụ sau khi chốt xong kế hoạch hoặc sau khi hoàn tất một cụm task) ngay khi ngữ cảnh vượt ngưỡng **50%**.

### 1.3. Hồ Sơ Mối Đe Dọa & 6 Trụ Cột Bảo Mật (`the-security-guide.md`)

Tài liệu `the-security-guide.md` mổ xẻ các lỗ hổng thực tế đã xuất hiện trong hệ sinh thái Coding Agent:
- **`CVE-2025-59536`**: Lỗ hổng thực thi mã từ xa (RCE) thông qua việc kẻ tấn công cài cắm cấu hình hook hoặc lệnh khởi chạy độc hại bên trong tệp `.claude/settings.json` của một kho mã nguồn vừa clone về.
- **`CVE-2026-21852`**: Lỗ hổng đánh cắp khóa xác thực (API key exfiltration) bằng cách ghi đè biến môi trường `ANTHROPIC_BASE_URL` trỏ về máy chủ thu thập của kẻ tấn công trong cấu hình dự án.
- **Snyk ToxicSkills Report**: Thống kê thực nghiệm chỉ ra tới **36%** số lượng skill do cộng đồng chia sẻ tự do có chứa các mẫu prompt injection ẩn hoặc hành vi tải script ngoài kiểm soát.
- **Tam giác tử thần của Simon Willison (Lethal Trifecta)**: Khi một Agent hội tụ đủ 3 yếu tố: *(1) Quyền truy cập dữ liệu riêng tư (Private Data)* + *(2) Đọc nội dung không đáng tin cậy (Untrusted Content)* + *(3) Khả năng giao tiếp ra bên ngoài (External Communication)*, hệ thống chắc chắn đối mặt nguy cơ rò rỉ dữ liệu nếu chỉ dựa vào lời dặn trong prompt.

Để hóa giải Tam giác tử thần, `ECC` thiết lập **6 Trụ cột Phòng thủ (6 Defense Pillars)**:
1. **Jailbox KVM microVM Isolation**: Cô lập môi trường thực thi của agent trong máy ảo hạng nhẹ cấp phần cứng KVM hoặc container rootless không có quyền mạng ngoài danh sách trắng.
2. **Unicode & BiDi Tag Sanitization**: Quét và loại bỏ các ký tự điều khiển hướng văn bản hai chiều (`\u202A` đến `\u202E`, `\u2066` đến `\u2069`), ký tự độ rộng bằng không (zero-width spaces/joiners) và khối Unicode Tags dùng để giấu chỉ thị độc hại vô hình trước mắt người duyệt.
3. **Least Agency Approval Boundaries**: Thu hẹp quyền hạn tool tối thiểu theo từng vai trò agent; mọi thao tác vượt ngưỡng rủi ro đều phải qua cổng phê duyệt tường minh của con người.
4. **Deep Observability**: Ghi nhật ký bất biến mọi lời gọi công cụ, đầu vào/đầu ra và chấm điểm rủi ro theo thời gian thực.
5. **Process-Group Kill Switch & 30s Heartbeat Dead-Man Switch**: Khi hủy tác vụ hoặc mất nhịp tim quá **30 giây**, hệ thống phát tín hiệu `kill(-pgid, SIGKILL)` tới toàn bộ nhóm tiến trình (process group) thay vì chỉ giết tiến trình cha, ngăn chặn triệt để các tiến trình con mồ côi tiếp tục chạy ngầm.
6. **Unreviewed Memory Vault**: Mọi tri thức tự động học được từ phiên làm việc phải nằm trong vùng cách ly (quarantine) chưa được phép nạp vào system prompt cho đến khi được kiểm duyệt an toàn.

---

## Chương 2 (`SA2`) — Engine Thế Hệ 2 `ecc2/` (Rust Control Plane, 21 Files)

Phân hệ `SA2` nằm tại thư mục `ecc2/` (gồm `21` tệp mã nguồn Rust) đóng vai trò là mặt phẳng điều khiển tốc độ cao (Control Plane), quản lý vòng đời phiên làm việc, giám sát rủi ro, điều phối worktree và đánh giá thực nghiệm đa harness.

### 2.1. Ngăn Xếp Kỹ Thuật (`ecc2/Cargo.toml`) & Đa Trình Điều Khiển (`HarnessKind`)

Tệp `ecc2/Cargo.toml` khai báo kiến trúc hệ thống không phụ thuộc runtime thông dịch:
- **Giao diện TUI**: `ratatui 0.30` kết hợp `crossterm 0.29` dựng bảng điều khiển thời gian thực trên terminal.
- **Runtime bất đồng bộ**: `tokio 1` (multi-threaded) quản lý luồng I/O, tiến trình con và bộ định thời.
- **Lưu trữ bền vững & Git**: `rusqlite 0.40` (bundled SQLite) và `git2 0.21` (libgit2 bindings) + `clap 4` cho CLI.
- **Hỗ trợ 10+ `HarnessKind`**: Định nghĩa kiểu liệt kê chuẩn hóa giao thức điều khiển cho `Claude`, `Codex`, `OpenCode`, `Gemini`, `Cursor`, `Kiro`, `Trae`, `Zed`, `FactoryDroid` và `Windsurf`.

### 2.2. Kiến Trúc Actor `DbWriter` & Đồng Bộ Luồng Đọc/Ghi (`ecc2/src/session/runtime.rs`)

Một vấn đề kinh điển khi giám sát nhiều tiến trình agent song song là hiện tượng khóa ghi SQLite (`SQLITE_BUSY`) làm nghẽn luồng async đọc `stdout`/`stderr` của tiến trình con. Trong `ecc2/src/session/runtime.rs`, `ECC` giải quyết triệt để bằng mô hình **Actor `DbWriter` chuyên biệt**:
- Toàn bộ thao tác ghi cơ sở dữ liệu được đóng gói thành thông điệp `DbWriteCmd` đẩy qua kênh không giới hạn `tokio::sync::mpsc::unbounded_channel<DbWriteCmd>`, kèm kênh phản hồi một lần `oneshot::Sender` khi cần xác nhận đồng bộ.
- Một OS thread riêng biệt giữ kết nối ghi duy nhất tới SQLite (chế độ WAL), tuần tự rút `DbWriteCmd` và thực thi giao dịch mà không bao giờ làm chặn (block) các task Tokio đang đọc luồng xuất chuẩn của agent.
- Bộ định thời nhịp tim (Heartbeat ticker) được cấu hình với chính sách `MissedTickBehavior::Delay` để tránh dồn nhịp bão hòa khi hệ thống chịu tải cao.
- Giao diện TUI đọc dữ liệu thông qua cơ chế con trỏ tăng đơn điệu `SessionOutputBatch` (monotonic sequence cursor), chỉ nạp phần chênh lệch mới xuất hiện thay vì truy vấn lại toàn bộ lịch sử phiên.

### 2.3. Vòng Lặp Daemon 7 Pha (`ecc2/src/session/daemon.rs`)

Trình chạy ngầm trong `ecc2/src/session/daemon.rs` vận hành chu kỳ điều phối khép kín gồm **7 pha tuần tự**:
1. **`resume_crashed_sessions`**: Đối chiếu danh sách phiên đang ở trạng thái `running` trong SQLite với bảng tiến trình hệ điều hành (`kill -0 <pid>` trên Unix hoặc `tasklist /FI "PID eq ..."` trên Windows) để phát hiện tiến trình chết bất thường và tự động khôi phục hoặc đánh dấu lỗi.
2. **`check_sessions`**: Kiểm tra thời hạn nhịp tim (heartbeat timeout) và đối chiếu mức tiêu thụ token/chi phí thực tế với ngân sách trần (budget ceiling) của từng phiên.
3. **`maybe_run_due_schedules`**: Kích hoạt các tác vụ định kỳ theo lịch cron đã đăng ký.
4. **`maybe_run_remote_dispatch`**: Xử lý hàng đợi điều phối từ xa và các yêu cầu Computer Use.
5. **`coordinate_backlog_cycle`**: Thuật toán cân bằng tải thông minh cho đội ngũ agent:
   - Ưu tiên tái phân bổ công việc giữa các worker sẵn có thông qua cờ `prefers_rebalance_first` trước khi quyết định sinh thêm worker mới.
   - Theo dõi chuỗi bão hòa liên tiếp `chronic_saturation_streak`: khi đạt ngưỡng `>= 3` chu kỳ quá tải liên tiếp, hệ thống bật chế độ hạ nhiệt `dispatch_cooloff_active` (tạm ngưng nhận thêm task mới); khi chạm ngưỡng `>= 5`, hệ thống nâng cờ `operator_escalation_required` để báo động cho người vận hành can thiệp.
6. **`maybe_auto_merge_ready_worktrees`**: Tự động kiểm tra và hợp nhất các worktree đã hoàn thành kiểm thử và không có xung đột.
7. **`maybe_auto_prune_inactive_worktrees`**: Thu hồi và dọn dẹp các worktree không còn hoạt động quá thời gian quy định để giải phóng dung lượng đĩa.

### 2.4. Giải Thuật Chấm Điểm Rủi Ro 4 Chiều (`ecc2/src/observability/mod.rs`)

Mọi thao tác công cụ trong `ecc2` đều được lượng hóa rủi ro theo thời gian thực tại `ecc2/src/observability/mod.rs` bằng công thức cộng tuyến tính có kẹp biên trên 4 chiều độc lập:

$$\text{Score} = \text{clamp}(\text{BaseTool} + \text{FileSensitivity} + \text{BlastRadius} + \text{Irreversibility}, 0.0, 1.0)$$

Bảng phân rã trọng số chi tiết của 4 thành phần:
- **Chiều 1 — $\text{BaseTool}$ (Bản chất công cụ)**:
  - Thực thi lệnh hệ thống `bash`: `+0.20`
  - Ghi đè hoặc sửa nhiều chỗ `write` / `multiedit`: `+0.15`
  - Sửa đổi cục bộ `edit`: `+0.10`
  - Các công cụ tra cứu/khác: `+0.05`
- **Chiều 2 — $\text{FileSensitivity}$ (Độ nhạy cảm của tệp đích)**:
  - Tệp bí mật/xác thực (`.env`, `.pem`, khóa chứa `secret`, `token`, `credential`): `+0.25`
  - Tệp cấu hình hạ tầng & phụ thuộc dùng chung (`Cargo.toml`, `package.json`, `.github/workflows`, `migration`): `+0.15`
- **Chiều 3 — $\text{BlastRadius}$ (Bán kính ảnh hưởng)**:
  - Thao tác phát tán hoặc phá hủy diện rộng (`push --force`, tác động trực tiếp `origin main`, `rm -rf /`): `+0.35`
  - Thao tác quét đệ quy hàng loạt (`**`, `--recursive`, kết hợp `xargs`): `+0.25`
- **Chiều 4 — $\text{Irreversibility}$ (Mức độ không thể đảo ngược)**:
  - Xóa vĩnh viễn không qua thùng rác hoặc hủy lịch sử (`rm -rf`, `git reset --hard`, `drop table`, `truncate`): `+0.45`
  - Thao tác ghi đè khó khôi phục mức trung bình: `+0.40`

Điểm số $\text{Score} \in [0.0, 1.0]$ được so khớp với cấu trúc ngưỡng `RiskThresholds`:
- $\text{Score} \ge 0.35$ (`review`): Đánh dấu cảnh báo để hậu kiểm trên bảng điều khiển.
- $\text{Score} \ge 0.60$ (`confirm`): Tạm dừng tiến trình và yêu cầu người vận hành xác nhận tường minh.
- $\text{Score} \ge 0.85$ (`block`): Chặn cứng ngay lập tức và từ chối thực thi lệnh.

### 2.5. Quản Trị Git Worktree & Shared Dependency Symlink Cache (`ecc2/src/worktree/mod.rs`)

Mô-đun `ecc2/src/worktree/mod.rs` cung cấp ba cơ chế kỹ thuật giúp hàng chục worktree chạy song song mà không làm đầy ổ cứng hay hỏng cây thư mục làm việc:
1. **Kiểm tra xung đột không chạm đĩa (In-Memory Conflict Detection)**: Sử dụng lệnh `git merge-tree --write-tree <base> <branch>` để tính toán cây hợp nhất trực tiếp trong bộ nhớ đối tượng Git mà không cần checkout hay làm bẩn working tree hiện tại.
2. **Thao tác Hunk-level Staging**: Cho phép stage, unstage hoặc hoàn tác từng khối thay đổi (hunk) độc lập bằng cách trích xuất bản vá cục bộ và chạy `git apply --cached` (hoặc thêm cờ `-R` để đảo ngược).
3. **Shared Dependency Symlink Cache theo SHA-256 Lockfiles**:
   - Trước khi khởi tạo môi trường cho worktree mới, hệ thống tính mã băm SHA-256 trên tổ hợp tệp khai báo phụ thuộc của 3 hệ sinh thái:
     - **Node.js**: `package.json` kết hợp với `pnpm-lock.yaml`, `bun.lockb`, `yarn.lock` hoặc `package-lock.json`.
     - **Rust**: `Cargo.toml` kết hợp `Cargo.lock`.
     - **Python**: `.venv` kết hợp `uv.lock` hoặc `poetry.lock`.
   - Nếu mã băm SHA-256 trong worktree trùng khớp tuyệt đối với nhánh gốc, `ecc2` tạo liên kết mềm (symlink / directory junction) cho các thư mục nặng (`node_modules`, `target`, `.venv`) trỏ thẳng về kho đệm gốc.
   - Ngay khi phát hiện agent trong worktree sửa đổi bất kỳ tệp lockfile nào làm đổi mã băm SHA-256, hệ thống tự động **ngắt symlink (materialize/unlink)** và khởi tạo thư mục phụ thuộc riêng biệt để tránh làm nhiễm bẩn các worktree anh em.

### 2.6. Đánh Giá Thực Nghiệm Có Biên Giới (`ecc2/src/harness_eval.rs`)

Để tránh việc tinh chỉnh prompt/rule theo cảm tính, `ecc2/src/harness_eval.rs` cài đặt khung đánh giá định lượng **Bounded Harness Evaluation**:
- Mỗi cấu hình thử nghiệm được biểu diễn bằng `CandidateSpec`, chuẩn hóa đệ quy mọi khóa JSON thông qua cấu trúc cây có thứ tự `BTreeMap` rồi lấy mã băm định danh SHA-256, gắn kèm danh sách tham chiếu vết thực thi (`trace_refs`) và bằng chứng kiểm định (`evidence_refs`).
- Hàm `evaluate_paired` chạy bắt cặp cấu hình hiện tại (baseline) và cấu hình ứng viên (candidate) trên cùng tập bài toán với cùng hạt giống ngẫu nhiên (`seed`).
- Một ứng viên chỉ được thăng cấp khi thỏa mãn đồng thời cả 3 điều kiện trong `PromotionPolicy`: số mẫu tối thiểu `min_samples`, độ lệch điểm trung bình tối thiểu `min_mean_delta`, và tỷ lệ thắng đối đầu `min_win_rate`. Nếu sau khi áp dụng mà bước `health_check` thất bại, hệ thống thực hiện **SQLite atomic rollback** để khôi phục nguyên trạng cấu hình cũ.

---

## Chương 3 (`SA3`) — Hệ Thống `71` Agents (`agents/`) & `109` Files Codex Projection (`.agents/`)

Phân hệ `SA3` cung cấp đội ngũ chuyên gia ảo được chuẩn hóa cao độ, bao gồm `71` định nghĩa agent gốc trong `agents/` và `109` tệp ánh xạ sang định dạng OpenAI Codex CLI trong `.agents/`.

### 3.1. Phân Bố 10 Nhóm Chuyên Môn & Tỷ Lệ Phân Tầng Model Của `71` Agents

Toàn bộ `71` agents trong thư mục `agents/` được chia thành 10 miền chuyên môn: *(1) Quy hoạch & Kiến trúc*, *(2) Phát triển theo ngôn ngữ (TypeScript, Python, Go, Rust, Java, Kotlin, C++, C#, PHP, Ruby, Swift, Dart, Elixir, Scala)*, *(3) Kiểm định chất lượng & Code Review*, *(4) Bảo mật & Kiểm toán*, *(5) Kiểm thử TDD & E2E*, *(6) Cơ sở dữ liệu & Migration*, *(7) Hạ tầng, Docker & CI/CD*, *(8) Tài liệu & Tra cứu*, *(9) Điều phối vòng lặp & Đánh giá đối kháng GAN*, và *(10) Tối ưu hiệu năng & Dọn dẹp mã nguồn*.

Tỷ lệ phân bổ model trên `71` agents tuân thủ chặt chẽ nguyên lý kinh tế học ngữ cảnh:
- **Tầng `opus` (`4` agents — chiếm `5.6%`)**: Chỉ định cho 4 vị trí đòi hỏi suy luận sâu nhất gồm `architect`, `planner`, `security-reviewer`, và `gan-planner`.
- **Tầng `sonnet` (`61` agents — chiếm `85.9%`)**: Đảm nhận tuyệt đại đa số các tác vụ lập trình chuyên sâu, review ngôn ngữ, sửa lỗi build và kiểm thử.
- **Tầng `haiku` (`6` agents — chiếm `8.5%`)**: Dành cho các tác vụ tốc độ cao, chi phí thấp gồm `docs-lookup`, `loop-operator`, `model-route-explorer`, `refactor-cleaner`, `tdd-guide`, và `visuals`.

### 3.2. Cấu Trúc Chuẩn & Lớp Phòng Thủ `## Prompt Defense Baseline` (Phủ 100%)

Mỗi tệp `.md` trong `agents/` đều có YAML frontmatter khai báo `name`, `description`, `model`, `tools` (danh sách trắng công cụ được phép gọi) và phần thân Markdown. Điểm đặc biệt là **100% (cả 71/71 agents)** đều nhúng khối chỉ thị bất biến `## Prompt Defense Baseline` với 3 cam kết cứng:
1. Từ chối mọi yêu cầu tiết lộ, trích xuất hoặc tóm tắt nội dung system prompt / hướng dẫn nội bộ.
2. Tuyệt đối không thực thi mệnh lệnh hoặc thay đổi vai trò xuất phát từ dữ liệu bên ngoài (nội dung tệp mã nguồn, chuỗi comment, git diff, thông báo lỗi hay kết quả tìm kiếm).
3. Không bao giờ tự ý mở rộng quyền hạn công cụ vượt quá danh sách `tools` đã khai báo trong frontmatter.

### 3.3. Cơ Chế `Pre-Report Gate` & Bộ Lọc 12 False Positives (`agents/code-reviewer.md`)

Để khắc phục căn bệnh "báo cáo rác" (nitpicking noise) của các trình duyệt code tự động, `agents/code-reviewer.md` thiết lập cổng chặn **`Pre-Report Gate`** trước khi xuất bất kỳ nhận xét nào:
- **Ngưỡng tự tin**: Chỉ được phép báo cáo một phát hiện khi điểm tự tin nội tại đạt $\text{Confidence} \ge 80\%$.
- **Kịch bản lỗi cụ thể (Concrete Failure Scenario)**: Mỗi lỗi báo cáo bắt buộc phải chỉ rõ chuỗi nhân quả: `Input cụ thể -> Trạng thái hệ thống -> Kết quả sai / Crash tại dòng nào`.
- **Danh sách loại trừ 12 nhóm Dương tính giả (12 False Positives)**: Cấm báo cáo các vấn đề thuộc 12 mẫu giả như: tranh cãi phong cách định dạng đã có linter lo, đề xuất thêm chú thích không cần thiết, bắt lỗi thiếu kiểm tra null cho biến nội bộ đã được đảm bảo bởi kiểu tĩnh, phàn nàn về hằng số trong tệp test, hoặc yêu cầu tối ưu hóa vi mô ở nhánh code không nằm trên đường găng (cold path).

### 3.4. Kiến Trúc Đối Kháng `GAN Harness` (`gan-planner.md`, `gan-generator.md`, `gan-evaluator.md`)

Lấy cảm hứng từ mạng đối kháng sinh (Generative Adversarial Networks), bộ ba agent `gan-planner.md`, `gan-generator.md` và `gan-evaluator.md` tách bạch hoàn toàn người làm và người chấm cho các tác vụ thiết kế giao diện và ứng dụng phức tạp:
- `gan-planner` chuyển yêu cầu ngắn gọn của người dùng thành bản đặc tả giàu chiều sâu mỹ thuật và kỹ thuật.
- `gan-generator` xây dựng sản phẩm hoàn chỉnh theo đặc tả.
- `gan-evaluator` đóng vai giám khảo độc lập, kiểm tra sản phẩm chạy thực tế và chấm điểm theo công thức trọng số 4 trục:

$$\text{Score}_{\text{GAN}} = 0.30 \times \text{Design} + 0.20 \times \text{Originality} + 0.30 \times \text{Craft} + 0.20 \times \text{Functionality} \ge 7.0$$

- **Luật cắt lỗ nghiêm ngặt (Hard Floor & Iteration Cap)**:
  - Để đạt chuẩn xuất xưởng, tổng điểm $\text{Score}_{\text{GAN}}$ phải đạt từ `7.0` trở lên trên thang 10.
  - **Luật sàn cứng (Hard Veto)**: Nếu bất kỳ một trục thành phần nào trong 4 trục (`Design`, `Originality`, `Craft`, `Functionality`) có điểm `< 5.0`, toàn bộ bản dựng bị đánh trượt ngay lập tức bất kể điểm trung bình có lớn hơn `7.0` hay không.
  - Vòng lặp phản hồi giữa Generator và Evaluator giới hạn tối đa **3 iterations** để tránh lặp vô tận.

### 3.5. Cây Chiếu `.agents/` (`109` Files) Sang OpenAI Codex CLI

Thư mục `.agents/` chứa `109` files là bản chiếu tự động (projection) gồm 46 gói kỹ năng trọng yếu được đóng gói chuẩn cho OpenAI Codex CLI. Mỗi gói bao gồm tệp hướng dẫn kèm tệp cấu hình `agents/openai.yaml` định nghĩa rõ giao diện hiển thị (`interface`) và chính sách kích hoạt ngầm (`policy.allow_implicit_invocation`), giúp cùng một kho tri thức vận hành mượt mà trên cả Claude Code lẫn Codex.

---

## Chương 4 (`SA4`) — Hệ Thống Hooks, `GateGuard` Fact-Forcing & Bộ Quét `scanShell`

Phân hệ `SA4` (`hooks/` gồm `9` files cấu hình, `scripts/hooks/` và `scripts/lib/`) là lớp cưỡng chế kỷ luật thời gian thực (Runtime Enforcement Layer), đảm bảo agent không thể bỏ qua quy tắc ngay cả khi LLM quên chỉ thị trong prompt.

### 4.1. Kiến Trúc 7 Lifecycle Events & Định Danh Sidecar `hooks/hooks.metadata.json`

Hệ thống hook của `ECC` bao phủ toàn bộ vòng đời phiên làm việc qua các sự kiện: `PreToolUse`, `UserPromptSubmit`, `PreCompact`, `SessionStart`, `PostToolUse`, `PostToolUseFailure`, `Stop` và `SessionEnd`, với tổng cộng **24 entries cấp cao** điều phối **18 sub-hooks** chuyên biệt.

Để quản lý tính tương thích đa hệ điều hành, tệp sidecar `hooks/hooks.metadata.json` gắn cho mỗi hook một mã vân tay **`fingerprint` dài 12 ký tự hex** (trích từ mã băm SHA-256 của bộ ba chuẩn hóa `(event, matcher, command)`), đi kèm các trường điều khiển:
- `platforms`: Danh sách hệ điều hành hỗ trợ (`darwin`, `linux`, `win32`).
- `BrokenOn`: Ghi nhận các môi trường bị lỗi đã biết để trình cài đặt tự động vô hiệu hóa.
- `defaultEnabled` và `timeout`: Kiểm soát bật/tắt mặc định và thời gian chờ tối đa cho từng hook.

### 4.2. Gộp Tiến Trình In-Process Dispatcher & Batch Format/Typecheck Ở Pha `Stop`

Một cải tiến hiệu năng quan trọng của `ECC` là loại bỏ chi phí khởi tạo tiến trình con lặp lại:
1. **In-Process Dispatcher (`scripts/hooks/pre-bash-dispatcher.js`, `posttooluse-dispatcher.js`, `run-with-flags.js`)**:
   - Thay vì để harness gọi 6–8 lệnh `node script.js` riêng rẽ cho mỗi sự kiện `PreToolUse` hoặc `PostToolUse`, một tiến trình điều phối duy nhất nạp trực tiếp các mô-đun con vào bộ nhớ bằng lệnh `require(scriptPath).run(rawInput)`.
   - Cơ chế này tiết kiệm **50–100ms độ trễ** trên mỗi lần gọi tool. Nếu gặp một script thế hệ cũ chưa xuất hàm `.run()`, bộ điều phối tự động chuyển tiếp an toàn về `child_process.spawnSync`.
2. **Tích lũy & Kiểm tra theo lô ở pha `Stop` (`post-edit-accumulator.js` + `stop-format-typecheck.js`)**:
   - Khi agent sửa file bằng `Edit` hoặc `Write`, hook `post-edit-accumulator.js` không chạy trình kiểm tra kiểu ngay mà chỉ ghi nhận đường dẫn tệp vào tệp trạng thái tạm `.claude/.edited-files-<session>.json`.
   - Chỉ khi agent kết thúc lượt trả lời (sự kiện `Stop`), `stop-format-typecheck.js` mới đọc danh sách tệp đã chạm, gom nhóm theo từng tệp cấu hình `tsconfig.json` gần nhất và chạy Biome/Prettier cùng `tsc --noEmit` **một lần duy nhất cho cả lô**, vừa giữ code sạch vừa không làm gián đoạn mạch suy nghĩ của agent.

### 4.3. Giải Thuật `GateGuard` Fact-Forcing (`scripts/hooks/gateguard-fact-force.js`)

`GateGuard` là cổng chặn thông minh ở sự kiện `PreToolUse` nhằm ngăn chặn hành vi "đoán mò sửa đại" (blind editing) trước khi khảo sát mã nguồn:
- **Phân loại 5 nhóm mục tiêu (5 Target Buckets)**: Mỗi thao tác sửa file được phân vào 1 trong 5 nhóm: `new-file` (tạo tệp mới), `config-doc` (sửa cấu hình/tài liệu), `test-harness` (sửa tệp kiểm thử), `Single-file source` (sửa mã nguồn đơn lẻ) và `Multi-file source` (sửa mã nguồn liên kết nhiều tệp).
- **Cơ chế Prior-Search Credit (Tín dụng tra cứu trước)**: Nếu trong phiên hiện tại agent đã thực hiện ít nhất một lệnh tìm kiếm (`Grep`, `Glob`) hoặc đã đọc (`Read`) $\ge 1$ tệp mã nguồn liên quan, `GateGuard` cấp tín dụng thông qua để không làm phiền agent.
- **AST Trivial-Edit Bypass (Miễn trừ sửa đổi nhỏ)**: Nếu bản sửa đổi chỉ chạm $\le 5$ dòng và không làm thay đổi cấu trúc chữ ký hàm/lớp xuất khẩu (non-structural edit), `GateGuard` cho phép đi thẳng.
- **Sibling Collapse (Gộp tệp anh em)**: Khi đã đọc một tệp trong cùng thư mục mô-đun, quyền tiếp cận được mở rộng hợp lý cho các tệp anh em cùng cụm.
- **Denial Dampening (Giảm chấn từ chối chống Deadlock)**: Nếu một agent bị `GateGuard` chặn liên tiếp **3 lần** trên cùng một mục tiêu, lần thứ 4 hệ thống tự động hạ mức phản hồi từ `block` (chặn cứng) xuống `warn` (cảnh báo cho qua) để tránh làm treo cứng toàn bộ vòng lặp tự hành.
- **Phân tích lệnh hủy diệt Đa Shell**: Giải mã cả chuỗi lệnh PowerShell bị mã hóa ẩn qua cờ `-EncodedCommand` (chuẩn UTF-16LE Base64) trước khi đối chiếu danh sách đen.

### 4.4. Bộ Quét Từ Vựng Shell Hữu Hạn `scanShell` (`scripts/hooks/block-no-verify.js` & `scripts/lib/shell-scan.js`)

Các bộ lọc dựa trên biểu thức chính quy (regex) thông thường rất dễ bị qua mặt bởi việc chèn biến, subshell hoặc báo nhầm (false positive) khi chuỗi `--no-verify` nằm bên trong nội dung tin nhắn commit (`git commit -m "fix --no-verify bug"`). Để giải quyết bài toán này, `scripts/lib/shell-scan.js` cài đặt bộ phân tích từ vựng trạng thái hữu hạn **`scanShell`**:
- **Ngân sách tính toán hữu hạn chống ReDoS**: Giới hạn số bước lặp tối đa theo độ dài chuỗi đầu vào $L$:
  $$\text{MaxSteps} = 24L + 4096$$
- **Bóc tách ngữ cảnh chính xác**:
  - Phân biệt rõ chuỗi nằm trong dấu nháy đơn `'...'`, nháy kép `"..."`, và nội dung khối **heredoc** (`<<EOF ... EOF` hoặc `<<-'EOF'`) để không bao giờ bắt nhầm văn bản mô tả làm cờ lệnh.
  - Đệ quy bóc tách các cấu trúc lồng nhau: subshell `$(...)`, dấu huyền `` `...` ``, lệnh bọc `env -S`, `sudo`, `xargs`, `sh -c`, `bash -c`.
- **Chặn triệt để hành vi vượt rào Git Hooks**: Phát hiện mọi biến thể của `--no-verify`, cờ viết tắt `-n` trong `git commit`, hành vi ghi đè đường dẫn hook `git -c core.hooksPath=...`, hoặc dùng `sed s///e` để thực thi lệnh ngầm.

### 4.5. Sáu Kỹ Thuật Cross-Platform Đặc Trị Lỗi Windows

Môi trường Windows 11 đặt ra nhiều cạm bẫy hệ thống mà `ECC` đã xử lý triệt để qua 6 kỹ thuật trong `scripts/lib/`:
1. **Lọc WSL `System32\bash.exe` Stub (`windows-bash.js`)**: Trên máy Windows bật tính năng WSL nhưng chưa cài bản phân phối Linux nào, tệp `C:\Windows\System32\bash.exe` vẫn tồn tại nhưng khi gọi sẽ treo hoặc trả lỗi. `windows-bash.js` kiểm tra và loại bỏ stub này để ưu tiên tuyệt đối **Git Bash (`usr\bin\bash.exe`)**.
2. **Lọc `WindowsApps\python3.exe` Store Redirector**: Phát hiện và bỏ qua tệp giả `AppInstallerPythonRedirector.exe` trong thư mục `Microsoft\WindowsApps` vốn tự động mở Microsoft Store thay vì chạy Python thật.
3. **Vá lỗ hổng `CVE-2024-27980` bằng Env-Token Invocation**: Khi gọi các tệp `.cmd`/`.bat` trên Windows, `cmd.exe` có thể bị tấn công chèn tham số (argument injection). `ECC` truyền đường dẫn và đối số qua biến môi trường tạm `%ECC_LINTER_TOKEN_0%`, `%ECC_LINTER_TOKEN_1%` kết hợp cờ `windowsVerbatimArguments: true` trong `spawnSync`, vô hiệu hóa hoàn toàn việc diễn giải ký tự đặc biệt của `cmd.exe`.
4. **Cắt bỏ NTFS Alternate Data Streams (`::$DATA`)**: Chuẩn hóa đường dẫn trên Windows bằng cách tước bỏ hậu tố luồng dữ liệu phụ `::$DATA` để kẻ tấn công không thể lách qua bộ lọc đuôi tệp nhạy cảm (ví dụ `.env::$DATA`).
5. **Định danh Kho Mã Nguồn bằng `dev + ino` 64-bit (`BigInt`)**: Sử dụng `fs.statSync(path, { bigint: true })` lấy cặp chỉ số thiết bị và inode 64-bit (`dev`, `ino`) nhằm định danh chính xác tệp/thư mục bất chấp sự khác biệt hoa/thường (case-insensitive) hay đường dẫn 8.3 rút gọn (`PROGRA~1`) trên Windows.
6. **Chặn Phình Transcript 89% (Zero-Echo Hook Stdout)**: Các hook thế hệ cũ thường in lại toàn bộ `rawInput` ra `stdout`, làm kích thước tệp lịch sử phiên phình to gấp nhiều lần. `ECC` chuẩn hóa quy tắc chỉ xuất JSON quyết định tối thiểu khi cần can thiệp, giúp giảm **89% dung lượng transcript**.

---

## Chương 5 (`SA5`) — Hệ Thống `122` Rules (`rules/`), `contexts/` (3 Files) & `config/` (2 Files)

Phân hệ `SA5` tổ chức tri thức quy chuẩn lập trình thành cấu trúc phân cấp để chỉ nạp đúng những quy tắc liên quan tới tệp đang mở.

### 5.1. Kiến Trúc Kế Thừa 3 Tầng Của `122` Rules (`9.525` Dòng Markdown)

Thư mục `rules/` chứa tổng cộng **`122` tệp quy tắc** với **`9.525` dòng** văn bản kỹ thuật, chia thành 3 tầng kế thừa rõ rệt:

| Tầng kế thừa | Thư mục / Phạm vi | Số lượng tệp | Số dòng | Cơ chế kích hoạt vào Context |
| :--- | :--- | :--- | :--- | :--- |
| **Tầng 1 — Common Baseline** | `rules/common/` (`coding-style`, `security`, `testing`, `git-workflow`, `agents`, `performance`, `patterns`, `hooks`, `development-workflow`, `memory`) | `10` files (+ `1` `README.md` gốc = `11`) | `564` dòng (`+145` dòng README) | Luôn nạp mặc định (Always-on) làm nền tảng kỷ luật chung |
| **Tầng 2 — Language Specific** | `rules/<lang>/` cho **15 ngôn ngữ**: TypeScript, Python, Go, Rust, Java, Kotlin, C++, C#, PHP, Ruby, Swift, Dart, Scala, Elixir, SQL | `76` files | `5.291` dòng | Nạp lười (Lazy-loaded) tự động khi chạm tệp khớp mẫu glob `paths:` trong YAML frontmatter |
| **Tầng 3 — Framework / Domain** | `rules/<framework>/` cho **6 frameworks**: Next.js, React, FastAPI, Django, Spring Boot, NestJS | `35` files | `3.525` dòng | Nạp lười khi dự án khớp dấu vân tay framework và đường dẫn tệp tương ứng |
| **Tổng cộng** | Toàn bộ cây `rules/` | **`122` files** | **`9.525` dòng** | Tiết kiệm >85% lượng token quy tắc ở mỗi phiên làm việc |

Nhờ cơ chế khai báo `paths:` (ví dụ `paths: ["**/*.rs", "Cargo.toml"]` cho Rust hoặc `paths: ["**/*.py", "pyproject.toml"]` cho Python), một phiên làm việc chỉ sửa mã Python sẽ chỉ nạp `564` dòng Common + ~`350` dòng Python rules, hoàn toàn không tốn ngữ cảnh cho hơn 8.500 dòng quy tắc của 14 ngôn ngữ và 6 frameworks còn lại.

### 5.2. Ba Chế Độ Ngữ Cảnh Động (`contexts/`) & Cấu Hình Định Tuyến (`config/`)

- **Ba tệp chuyển trạng thái trong `contexts/`**:
  - `contexts/dev.md`: Tối ưu hóa cho pha viết code và kiểm thử nhanh (ưu tiên hành động, giữ log gọn).
  - `contexts/review.md`: Chuyển tâm thế sang thẩm định khắt khe, kiểm tra bảo mật, rò rỉ tài nguyên và biên lỗi.
  - `contexts/research.md`: Tối ưu cho pha khảo sát kiến trúc, đọc hiểu sâu và lập sơ đồ luồng dữ liệu trước khi chạm vào code.
- **Tự động nhận diện 19 ngăn xếp qua `config/project-stack-mappings.json`**: Ánh xạ các tệp chỉ báo trong kho mã nguồn (như `next.config.js`, `manage.py`, `pom.xml`, `mix.exs`, `pubspec.yaml`) sang danh sách rules, agents và skills cần kích hoạt cho **19 ngăn xếp công nghệ** khác nhau.
- **Điều phối Đa Agent qua `config/github-native-coordination.json`**: Quy định giao thức phân chia công việc không xung đột dựa trên nhãn GitHub Issues (`agent:claimed`, `agent:in-progress`, `agent:review-ready`) kết hợp quy ước đặt tên nhánh và worktree cô lập `wt/<issue-number>-<agent-id>`.

---

## Chương 6 (`SA6`) — Kho `311` Skills (`skills/` — `613` Files) & Giải Thuật Học Liên Tục

Phân hệ `SA6` là kho tàng quy trình tác nghiệp lớn nhất của `ECC` với **`311` skills** chứa trong **`613` files** dưới thư mục `skills/`.

### 6.1. Cấu Trúc Phân Bố `311` Skills Trên 9 Miền Kỹ Thuật

Trong tổng số `311` skills:
- **`269` Single-File Skills (`86.5%`)**: Mỗi skill gói gọn trong một tệp `SKILL.md` duy nhất chứa quy trình từng bước, danh sách kiểm tra và mẫu mã chuẩn.
- **`42` Multi-File Executable Skill Packages (`13.5%`)**: Các gói kỹ năng phức tạp đi kèm thư mục con chứa scripts thực thi, tài liệu tham chiếu (`references/`), bộ kiểm thử riêng và cấu hình daemon.
- **9 Miền kỹ thuật bao phủ**: *(1) Quản trị ngữ cảnh & Bộ nhớ học liên tục*, *(2) Ngôn ngữ & Framework chuyên sâu*, *(3) Bảo mật, SAST & Pentest*, *(4) Kiểm thử TDD, E2E & Đánh giá Benchmark*, *(5) Cơ sở dữ liệu, ORM & Tối ưu truy vấn*, *(6) DevOps, Docker, Kubernetes & Cloud*, *(7) Thiết kế UI/UX, Frontend & Mobile*, *(8) Khoa học dữ liệu, ML & LLM Engineering*, và *(9) Điều phối quy trình, Nghiên cứu & Tự động hóa doanh nghiệp*.

### 6.2. Giải Thuật Học Liên Tục `continuous-learning-v2` (Homunculus)

Gói kỹ năng `skills/continuous-learning-v2/` (còn gọi là kiến trúc **Homunculus**) giải quyết bài toán làm sao để agent tự rút kinh nghiệm qua từng phiên làm việc mà không làm ô nhiễm system prompt bằng các ghi chú rác:

1. **Luồng thu thập sự kiện cô lập theo dự án (`observe.sh`)**:
   - Mọi thao tác gọi công cụ, lỗi xảy ra và cách sửa lỗi của người dùng/agent được ghi nối tiếp vào tệp `observations.jsonl` nằm tại thư mục băm riêng của từng dự án: `~/.claude/homunculus/projects/<project-hash>/observations.jsonl`.
2. **Mô hình Đơn vị Tri thức Nguyên tử — `Instinct`**:
   - Thay vì viết thẳng vào một tệp bộ nhớ chung, mỗi quy luật rút ra được đúc thành một **Instinct** (bản năng nguyên tử) gồm điều kiện kích hoạt (`trigger`), hành động khuyến nghị (`action`), miền áp dụng (`domain`) và điểm tin cậy **`confidence` $\in [0.3, 0.9]$**:
     - Khởi tạo ban đầu ở mức trung tính: $\text{confidence}_0 = 0.50$.
     - Mỗi lần mẫu hành vi được tái xác nhận thành công trong thực tế: cộng thêm $+0.05$ (kẹp trần tại $0.90$).
     - Mỗi lần bị người dùng bác bỏ hoặc gây lỗi: trừ đi $-0.10$.
     - **Phân rã theo thời gian (Temporal Decay)**: Mỗi tuần không được kích hoạt, điểm tin cậy tự động giảm $-0.02$; nếu tụt xuống dưới ngưỡng sàn $0.30$, instinct bị thu hồi.
     - **Pending TTL 30 ngày**: Các instinct mới sinh đang ở trạng thái chờ duyệt (`pending`) nếu quá **30 ngày** không được xác nhận sẽ tự động bị xóa bỏ để tránh tích tụ rác.
3. **Giải thuật Gom cụm Tiến hóa (`/evolve`) bằng Hệ số Szymkiewicz-Simpson**:
   - Khi số lượng instincts tích lũy đủ lớn, lệnh `/evolve` chuẩn hóa tập từ khóa kích hoạt $T_A, T_B$ của từng cặp instinct và tính **Hệ số trùng lặp Szymkiewicz-Simpson (Overlap Coefficient)**:

     $$\text{Overlap}(T_A, T_B) = \frac{|T_A \cap T_B|}{\min(|T_A|, |T_B|)} \ge 0.5 \quad \text{với điều kiện } |T_A \cap T_B| \ge 2$$

   - Hai instinct có $\text{Overlap}(T_A, T_B) \ge 0.5$ và có ít nhất 2 từ khóa chung sẽ được nối cạnh trên đồ thị tương đồng.
   - Khi một thành phần liên thông (cụm) hội tụ đủ **$\ge 3$ instincts** và có điểm tin cậy trung bình **$\text{avg\_confidence} \ge 0.70$**, hệ thống tự động tổng hợp cụm đó thành một **Skill**, **Slash Command** hoặc **Agent** hoàn chỉnh.
   - Lệnh `/promote` cho phép thăng cấp một instinct từ phạm vi cục bộ dự án (`project-scoped`) lên phạm vi toàn cục (`global`) khi và chỉ khi instinct đó xuất hiện độc lập ở **$\ge 2$ dự án khác nhau** với **$\text{avg\_confidence} \ge 0.80$**.

### 6.3. Các Giải Thuật Skill Tiêu Biểu Khác

- **`plankton-code-quality`**: Tự động bắt lỗi định dạng/lint sau khi sửa code và triệu hồi subagent phân tầng (`haiku` cho lỗi cú pháp đơn giản, `sonnet` cho lỗi logic phức tạp) để âm thầm sửa sạch trước khi trả kết quả.
- **`eval-harness`**: Phân biệt rạch ròi hai thước đo toán học khi đánh giá agent trên $n$ lần chạy thử với $c$ lần thành công ở kích thước mẫu $k$:
  - **Năng lực khám phá ($\text{pass}@k$)** — xác suất có ít nhất 1 lần giải đúng trong $k$ lần thử (phù hợp khi có bộ lọc kiểm thử đi kèm):
    $$\text{pass}@k = 1 - \frac{\binom{n-c}{k}}{\binom{n}{k}}$$
  - **Độ tin cậy sản xuất ($\text{pass}^k$)** — xác suất cả $k$ lần chạy độc lập đều thành công tuyệt đối (thước đo sống còn cho quy trình tự động hóa nơi người dùng kỳ vọng 100% ổn định):
    $$\text{pass}^k = \left(\frac{c}{n}\right)^k$$
- **`skill-comply`**: Kiểm toán viên tự động đọc vết thực thi (execution trace) và dùng hàm `_check_temporal_order` để xác minh agent có thực sự tuân thủ thứ tự các bước trong `SKILL.md` (ví dụ: viết test trước khi viết code) hay chỉ giả vờ báo cáo đã làm.
- **`operator-approval-loop`**: Quản lý cổng phê duyệt từ xa thông qua SQLite với cơ chế xoay vòng kỷ nguyên (`epoch rotation`) và mã sử dụng một lần nhằm chống tấn công phát lại (replay attack).

---

## Chương 7 (`SA7`) — Hệ Thống `97` Slash Commands, `12` Legacy Shims & Native Workflows

Phân hệ `SA7` (`commands/` gồm `109` files: `97` lệnh đang hoạt động + `12` tệp chuyển tiếp tương thích ngược; cùng thư mục `workflows/`) là giao diện điều khiển nhanh dành cho lập trình viên.

### 7.1. Phân Loại 13 Nhóm Chức Năng & 5 Mẫu Kết Nối Điều Phối

`97` lệnh hoạt động và `12` legacy shims được tổ chức thành 13 nhóm chức năng: Lập kế hoạch & Điều phối (`plan`, `plan-orchestrate`, `orch-pipeline`), Phát triển TDD (`tdd`), Review & Kiểm toán (`code-review`, `orch-review`, `security-scan`), Sửa lỗi Build/Test (`build-fix`), Học liên tục (`learn`, `instinct-status`, `evolve`, `promote`), Quản lý ngữ cảnh (`compact-strategic`, `context-budget`), Đa agent & Worktree (`multi-plan`, `multi-execute`, `worktree-clean`), Ngôn ngữ chuyên biệt (Go, Python, Rust, TS...), Kiểm thử E2E, Tài liệu, Refactor, Đánh giá Harness và Tiện ích hệ thống.

Mỗi slash command kết nối xuống tầng thực thi theo 1 trong 5 mẫu chuẩn: *(1) Command $\to$ Single Agent*, *(2) Command $\to$ Skill Package*, *(3) Command $\to$ Native JS Workflow (`workflows/*.workflow.js`)*, *(4) Command $\to$ CLI Script*, hoặc *(5) Multi-Command Chain (Chuỗi lệnh nối tiếp có cổng kiểm tra)*.

### 7.2. Cơ Chế Scope-Carrying vs Fail-Closed Trong `plan-orchestrate` & `orch-pipeline`

- **`plan-orchestrate` (Fail-Closed Scope Enforcement)**: Khi chuyển từ bản kế hoạch sang giai đoạn thực thi, lệnh này bóc tách danh sách tệp mục tiêu (`target_files`) từ kế hoạch để truyền phạm vi (`Scope-Carrying`) cho các worker. Nếu bản kế hoạch mơ hồ không chỉ định được danh sách tệp cụ thể, quy trình lập tức dừng khẩn cấp theo nguyên tắc **Fail-Closed** thay vì cho phép agent tự do sửa toàn bộ kho mã.
- **`orch-pipeline` (Right-Sizing 4 Cấp Độ & Security Trigger)**:
  - Tự động định cỡ quy trình theo quy mô thay đổi: `tiny` (1–2 files, bỏ qua bước kiến trúc rườm rà), `medium` (3–8 files), `large` (9–20 files, tách đợt song song), và `xl` (>20 files, bắt buộc chia pha kiến trúc).
  - **Security Trigger tự động**: Bất kể quy mô là `tiny` hay `xl`, nếu đường dẫn tệp hoặc nội dung diff chạm vào các từ khóa nhạy cảm (`auth`, `jwt`, `crypto`, `password`, `.env`, `permission`, `sql`), hệ thống tự động chèn bước thẩm định bắt buộc của `security-reviewer` vào đường ống cùng 2 cổng duyệt của con người.

### 7.3. Giải Thuật Thẩm Định Đối Kháng 3 Giai Đoạn `orch-review` (`workflows/orch-review.workflow.js`)

Tệp `workflows/orch-review.workflow.js` cài đặt một trong những giải thuật kiểm định mã nguồn sắc bén nhất của `ECC`, gồm **3 giai đoạn nối tiếp**:

```
                  +---> [Reviewer 1: Correctness] ---+
                  |                                  |
[Git Diff Input] -+---> [Reviewer 2: Security]    ---+--> [Barrier Dedup] --> [Adversarial Skeptic] --> [Final Report]
                  |                                  |    key: file::norm     Fail-Closed Filter:
                  +---> [Reviewer 3: Performance] ---+                        drop ONLY IF
                                                                              isReal===false && conf>=0.8
```

1. **Giai đoạn 1 — Parallel Fan-out (Phân tán song song 3 chiều)**:
   - Cùng một bản thay đổi được gửi song song cho 3 nhánh chuyên gia độc lập: nhánh kiểm tra tính đúng đắn logic (`correctness`), nhánh rà soát lỗ hổng bảo mật (`security`), và nhánh đánh giá hiệu năng/độ phức tạp thuật toán (`performance`).
2. **Giai đoạn 2 — Barrier Deduplication (Hợp nhất khử trùng lặp tại rào chắn)**:
   - Khi cả 3 nhánh hoàn tất, bộ gom tại rào chắn chuẩn hóa bằng chứng mã nguồn (loại bỏ khoảng trắng thừa, ký tự xuống dòng và chữ hoa/thường) rồi tạo khóa định danh duy nhất:
     $$\text{DedupKey} = \texttt{\$\{file\}::\$\{normalize(evidence)\}}$$
   - Các phát hiện trùng khóa từ nhiều nhánh được gộp làm một và giữ mức độ nghiêm trọng (`severity`) cao nhất.
3. **Giai đoạn 3 — Adversarial Skeptic Verification (Thẩm định đối kháng theo nguyên tắc Fail-Closed)**:
   - Thay vì tin ngay kết quả của các Reviewer, mỗi phát hiện sau khi khử trùng lặp được chuyển giao cho một **Skeptic Agent (Người phản biện hoài nghi)** độc lập với nhiệm vụ duy nhất: đọc mã nguồn thực tế để tìm bằng chứng chứng minh phát hiện đó là *báo động giả (false positive)*.
   - **Quy tắc lọc Fail-Closed bảo toàn an toàn**: Một phát hiện chỉ bị loại bỏ khỏi báo cáo cuối cùng khi và chỉ khi Skeptic chứng minh được nó là giả với độ tự tin rất cao:
     $$\text{Drop}(f) \iff (\text{verdict.isReal} === \texttt{false}) \land (\text{verdict.confidence} \ge 0.80)$$
   - Nếu Skeptic không chắc chắn ($\text{confidence} < 0.80$), gặp lỗi phân tích hoặc xác nhận $\text{isReal} === \texttt{true}$, phát hiện đó **bắt buộc được giữ lại**. Thiết kế này vừa cắt bỏ được các lỗi bắt bẻ vô căn cứ, vừa đảm bảo không bao giờ vô tình xóa mất một lỗ hổng bảo mật thật.

---

## Chương 8 (`SA8`) — Core `src/` (`23` Python Files), `scripts/` (`370` Files) & Giải Thuật `TCAS`

Phân hệ `SA8` bao gồm nhân thực thi Python trong `src/` (`23` files), hệ thống `370` kịch bản tiện ích trong `scripts/`, bảng điều khiển `ecc_dashboard.py` và bộ định tuyến chống va chạm đa agent `TCAS`.

### 8.1. Lớp Trừu Tượng Đa Nhà Cung Cấp `src/llm/` & Che Giấu Lỗi `GENERIC_TOOL_FAILURE`

Thư mục `src/` (`23` Python files) cung cấp bộ khung điều khiển LLM độc lập nhà cung cấp:
- **`LLMProvider` & `ReActAgent`**: Chuẩn hóa giao tiếp vòng lặp suy luận — hành động (Reason + Act) trên nhiều backend LLM khác nhau.
- **`strip_reasoning`**: Bộ lọc tách biệt hoàn toàn khối suy nghĩ nội tâm (`<think>...</think>`) ra khỏi phần phản hồi chính thức để giữ sạch lịch sử hội thoại và không làm hỏng bộ phân tích cú pháp JSON ở các bước sau.
- **`ToolExecutor` chống rò rỉ thông tin hệ thống**: Khi một công cụ gặp ngoại lệ nội bộ (unhandled exception), thay vì trả nguyên vẹn stack trace chứa đường dẫn tệp nhạy cảm của máy chủ hoặc biến cục bộ vào ngữ cảnh của LLM, `ToolExecutor` ghi log chi tiết vào luồng kiểm toán nội bộ và chỉ trả về mã lỗi chuẩn hóa **`GENERIC_TOOL_FAILURE`** cho mô hình.

### 8.2. Quản Trị Hạ Tầng Trong `scripts/` (`370` Files) & Memory Vault `O_NOFOLLOW`

Hệ thống `370` scripts cung cấp các cơ chế nền tảng cho toàn bộ vòng đời chạy:
1. **Nhận diện Package Manager 6 tầng ưu tiên (`scripts/lib/package-manager.js`)**: Tự động chọn đúng công cụ (`pnpm`, `bun`, `yarn`, `npm`) theo thứ tự ưu tiên nghiêm ngặt: *(1) Trường `packageManager` trong `package.json`* $\to$ *(2) Tệp khóa lockfile hiện diện trong dự án* $\to$ *(3) Tệp cấu hình `.ecc-pm`* $\to$ *(4) Biến môi trường `ECC_PACKAGE_MANAGER`* $\to$ *(5) Cấu hình toàn cục `~/.claude/package-manager.json`* $\to$ *(6) Fallback an toàn về `npm`*.
2. **Đối sánh phiên 4 tầng (`4-tier Session Matching`) kèm `STALE-REPLAY GUARD`**: Khớp nối chính xác trạng thái phiên theo `session_id` $\to$ `transcript_path` $\to$ `cwd + branch` $\to$ `recent timestamp`, đồng thời chặn việc phát lại các bản ghi trạng thái cũ đã hết hạn.
3. **WASM SQLite State Store (`sql.js`)**: Sử dụng bản biên dịch WebAssembly thuần JavaScript của SQLite giúp mọi script Node.js truy vấn cơ sở dữ liệu quan hệ mà không cần biên dịch native C++ addon (`node-gyp`), loại bỏ hoàn toàn lỗi cài đặt trên các máy Windows thiếu Visual Studio Build Tools.
4. **Memory Vault chống tấn công Symlink / TOCTOU**: Khi đọc/ghi vào kho bộ nhớ cách ly, hệ thống mở tệp với cờ **`O_NOFOLLOW`** (từ chối đi theo liên kết mềm do kẻ tấn công tráo đổi) và thực hiện ghi nguyên tử thông qua tệp tạm kết hợp **`fs.linkSync`** (atomic hardlink) trước khi `unlink`, triệt tiêu khe hở thời gian kiểm tra — thời gian sử dụng (*Time-Of-Check to Time-Of-Use*).

### 8.3. Giải Thuật `TCAS` Multi-Agent Proximity & Collision Avoidance (`scripts/lib/agent-proximity/distance.js`)

Khi nhiều agent cùng hoạt động đồng thời trên một kho mã nguồn, việc chỉ kiểm tra xem hai agent có chạm cùng một tên tệp hay không là chưa đủ (vì Agent A sửa hàm xuất khẩu ở tệp `auth.ts` có thể làm gãy tức thì Agent B đang gọi hàm đó ở tệp `checkout.ts`). Lấy cảm hứng từ **Hệ thống cảnh báo va chạm hàng không TCAS (Traffic Collision Avoidance System)**, tệp `scripts/lib/agent-proximity/distance.js` định nghĩa công thức đo khoảng cách rủi ro va chạm tổng hợp $R(a, b) \in [0.0, 1.0]$ giữa hai tập thay đổi của Agent $a$ và Agent $b$:

$$R(a, b) = 1 - \prod_{i \in \{\text{overlap}, \text{dep}, \text{tree}\}} (1 - \omega_i \cdot r_i)$$

Trong đó công thức tích phần bù xác suất kết hợp 3 nguồn rủi ro với trọng số $\omega_i$:
1. **Rủi ro đụng độ dòng mã trực tiếp — $r_{\text{overlap}}$ (Trọng số $\omega_{\text{overlap}} = 1.0$)**:
   - Đo bằng hệ số trùng lặp **Szymkiewicz-Simpson** trên tập các dòng mã (hoặc vùng cửa sổ dòng lân cận) mà hai agent đang sửa trong cùng một tệp:
     $$r_{\text{overlap}}(L_a, L_b) = \frac{|L_a \cap L_b|}{\min(|L_a|, |L_b|)}$$
2. **Rủi ro lan truyền trên đồ thị phụ thuộc — $r_{\text{dep}}$ (Trọng số $\omega_{\text{dep}} = 0.90$)**:
   - Hệ thống dựng đồ thị có hướng từ các câu lệnh `import` / `require` trong dự án và dùng thuật toán tìm kiếm theo chiều rộng (**BFS**) để tìm khoảng cách đường đi ngắn nhất $d \ge 1$ giữa các tệp của Agent $a$ và Agent $b$. Điểm rủi ro suy giảm theo hàm mũ của khoảng cách bước nhảy:
     $$r_{\text{dep}}(d) = \gamma = 0.5^{d-1}$$
   - Nếu hai tệp import trực tiếp nhau ($d = 1$), $r_{\text{dep}} = 0.5^0 = 1.0$, đóng góp $\omega_{\text{dep}} \cdot r_{\text{dep}} = 0.90$ vào tổng rủi ro ngay cả khi hai agent không chạm chung bất kỳ tệp nào!
3. **Rủi ro lân cận trên cây thư mục — $r_{\text{tree}}$ (Trọng số $\omega_{\text{tree}} = 0.25$)**:
   - Tính khoảng cách dựa trên độ sâu của **Tổ tiên chung gần nhất (Lowest Common Ancestor — LCA)** trên cây thư mục dự án, phản ánh khả năng hai tệp cùng thuộc một mô-đun nghiệp vụ.

**Ba ngưỡng điều tiết giao thông của `TCAS`**:
- **`clear` ($R(a, b) < 0.35$)**: Vùng không phận an toàn, hai agent tiếp tục thực thi tốc độ tối đa.
- **`advisory` ($0.35 \le R(a, b) < 0.70$)**: Cảnh báo lưu ý (Traffic Advisory — TA), thông báo cho mỗi agent biết vùng tệp lân cận mà đồng đội đang sửa để tránh mở rộng phạm vi.
- **`resolution` ($R(a, b) \ge 0.70$)**: Báo động va chạm (Resolution Advisory — RA), hệ thống tự động phát mệnh lệnh điều phối **`hold`** (tạm dừng agent có độ ưu tiên thấp hơn) hoặc **`steer`** (điều hướng lại thứ tự task) để ngăn chặn xung đột merge trước khi nó xảy ra.

---

## Chương 9 (`SA9`) — Kiến Trúc Đa Nền Tảng (22+ Harnesses), `pi/core/` (`208` Files), `manifests/` & `schemas/`

Phân hệ `SA9` biến `ECC` từ một bộ cấu hình gắn chặt với một công cụ duy nhất thành một trình biên dịch cấu hình đa đích hỗ trợ hơn **22+ Agent Harnesses** khác nhau.

### 9.1. Pipeline 5 Giai Đoạn Của `scripts/install-apply.js` & Biểu Diễn Trung Gian `Canonical Agent IR`

Trình cài đặt và đồng bộ hóa `scripts/install-apply.js` vận hành theo đường ống **5 giai đoạn nguyên tử**:
```
[1. Resolve Manifest] -> [2. Validate Schema & Digest] -> [3. Transpile IR] -> [4. Atomic Stage] -> [5. Apply & Record State]
```
Trái tim của Giai đoạn 3 là định dạng biểu diễn trung gian **`Canonical Agent IR` (`ecc.agent-ir.v1`)**:
- Mọi tệp định nghĩa trong `agents/`, `rules/`, `skills/` và `commands/` được phân tích cú pháp về một cấu trúc cây trung gian chuẩn hóa `ecc.agent-ir.v1` độc lập hoàn toàn với cú pháp của từng IDE.
- Từ `ecc.agent-ir.v1`, các bộ sinh mã (target emitters) biên dịch ra định dạng đích cho **22+ nền tảng**: `Claude Code` (`.claude/`), `Cursor` (`.cursor/rules/*.mdc`), `OpenCode` (`.opencode/`), `OpenAI Codex` (`.agents/` & `AGENTS.md`), `Kiro` (`.kiro/`), `Windsurf` (`.windsurfrules`), `Zed`, `Antigravity`, `Pi` (`.pi/` & `pi/core/`), `Trae`, `Gemini CLI`, `Aider`, `Continue`, `Cline`, `Roo Code`, `FactoryDroid`, `GitHub Copilot`...

### 9.2. Sự Khác Biệt Kiến Trúc Giữa `.pi/` (Zero-Copy Live Adapter) Và `pi/core/` (`208` Files Offline Bundle)

Đối với hệ sinh thái Pi Coding Agent, `ECC` duy trì song song hai mô hình triển khai:
- **`.pi/` (Zero-Copy Live Adapter)**: Dành cho nhà phát triển làm việc trực tiếp trong kho `ECC`; sử dụng các tệp cầu nối mỏng trỏ thẳng vào mã nguồn gốc, mọi chỉnh sửa có hiệu lực tức thì mà không cần bước đóng gói.
- **`pi/core/` (`208` Files Self-Contained Offline Package)**: Là gói phân phối độc lập hoàn toàn (100% offline, zero external runtime dependencies), được bảo vệ bởi hai cơ chế kiểm định tự động:
  1. **Partition Completeness Check**: Đảm bảo mọi tài nguyên được tham chiếu trong các thành phần của `pi/core/` đều đã được sao chép đầy đủ vào bên trong gói `208` files, không có bất kỳ đường dẫn nào thoát ra ngoài thư mục bao.
  2. **Static Safety Scanner**: Quét tĩnh toàn bộ mã nguồn trong `pi/core/`, cấm tuyệt đối việc sử dụng `eval()`, `new Function()`, hoặc gọi `child_process` trái phép ngoài danh sách kiểm soát.

### 9.3. Hệ Thống `10` Manifests, `17` JSON Schemas, `Cryptographic Digest Chain` & `Static AST Dependency Closure`

Tính toàn vẹn cấu trúc của toàn bộ kho mã được khóa chặt bởi `10` tệp kê khai trong `manifests/`, `17` lược đồ kiểm tra kiểu trong `schemas/` và hai giải thuật bảo chứng:

1. **Chuỗi Băm Mật Mã 6 Mắt Xích — `Cryptographic Digest Chain`**:
   Để đảm bảo không có bất kỳ tệp quy tắc hay script nào bị sửa đổi ngầm (tampering) hoặc lệch phiên bản giữa lúc đóng gói và lúc cài đặt vào máy người dùng, `ECC` thiết lập chuỗi 6 mã băm SHA-256 nối kết nhau:
   $$\text{Source Digest} \xrightarrow{\text{SHA-256}} \text{IR Digest} \xrightarrow{\text{SHA-256}} \text{Manifest Digest} \xrightarrow{\text{SHA-256}} \text{Bundle Digest} \xrightarrow{\text{SHA-256}} \text{Lockfile Digest} \xrightarrow{\text{SHA-256}} \text{Install Receipt}$$
   Khi người dùng chạy lệnh cập nhật hoặc kiểm tra sức khỏe (`ecc doctor`), trình cài đặt đối chiếu `Install Receipt` tại máy đích ngược lên chuỗi `Cryptographic Digest Chain`; nếu một tệp cấu hình đã được người dùng chỉnh sửa tay cục bộ, mã băm lệch sẽ giúp hệ thống nhận biết ngay để bảo vệ phần sửa đổi của người dùng thay vì ghi đè mù quáng.

2. **Bao Đóng Phụ Thuộc AST Tĩnh — `Static AST Dependency Closure` (`scripts/ci/validate-carrier-closure.js`)**:
   Một lỗi phổ biến khi trích xuất một tập con hooks/scripts sang dự án của người dùng là tệp `hook-a.js` được copy đi nhưng tệp tiện ích ` ../lib/helper-b.js` mà nó `require()` lại bị bỏ sót. Script `scripts/ci/validate-carrier-closure.js` phân tích cây cú pháp trừu tượng (AST) của mọi tệp JavaScript/TypeScript được liệt kê trong manifest, duyệt đệ quy toàn bộ đồ thị lệnh `require()`, `import`, và đường dẫn script con để chứng minh **tính đóng toán học (carrier closure)**: mọi nút phụ thuộc bắt buộc phải thuộc tập tệp được đóng gói.

---

## Chương 10 (`SA10`) — Hệ Thống Kiểm Thử (`497` Files), Docker Empirical Lab (`333` Files) & Bảo Mật Chuỗi Cung Ứng CI/CD

Phân hệ `SA10` biến mọi tuyên bố kiến trúc của `ECC` thành các phép đo thực nghiệm có thể kiểm chứng độc lập thông qua `497` tệp kiểm thử (`tests/`), `333` tệp phòng thí nghiệm Docker (`docker/`), `67` tệp ví dụ (`examples/`) và `13` quy trình CI/CD (`.github/workflows/`).

### 10.1. Trình Chạy Kiểm Thử Cô Lập Đa Luồng (`tests/` — `497` Files)

Với `497` tệp kiểm thử bao phủ từ unit test cho từng hàm băm, bộ quét `scanShell`, tính khoảng cách `TCAS`, cho tới integration test của trình cài đặt đa nền tảng:
- **`tests/run-all.js` & `tests/helpers/windows-test-env.js`**: Mỗi tệp kiểm thử khi khởi chạy đều được cấp phát một thư mục tạm riêng biệt đóng vai trò làm `HOME`, `USERPROFILE`, `APPDATA` và `XDG_CONFIG_HOME` giả lập.
- Thiết kế cô lập môi trường 100% này đảm bảo hai lợi ích sống còn: *(1) Chạy song song hàng trăm tệp test trên tất cả các nhân CPU mà không bao giờ xảy ra tranh chấp tệp `~/.claude/settings.json`* và *(2) Không bao giờ làm hỏng cấu hình thật trên máy của lập trình viên đang chạy test*.

### 10.2. Phòng Thí Nghiệm Thực Nghiệm Docker (`docker/` — `333` Files)

Thư mục `docker/` chứa `333` files không dùng để triển khai web app thông thường mà là một **Phòng thí nghiệm đo đạc hành vi Agent (Empirical Agent Lab)** gồm 3 cụm chính:
1. **`docker/context-profiles/` (Môi trường hộp cát siêu cứng)**:
   - Chạy dưới quyền người dùng không đặc quyền `USER 1000:1000` (rootless).
   - Cắt toàn bộ kết nối mạng `network_mode: none`, thu hồi toàn bộ quyền nhân Linux `cap_drop: ALL`, và gắn hệ thống tệp gốc ở chế độ chỉ đọc `read_only: true` (chỉ mở `tmpfs` có giới hạn dung lượng cho thư mục làm việc tạm).
2. **`docker/complex-eval/` (`187` Files — 5-Arm Preregistered Benchmark)**:
   - Thiết kế thí nghiệm đối chứng **5 nhánh (5-Arm Benchmark)** đã đăng ký trước giả thuyết (`cases`, `cases1`, `cases2`, `cases3`, `cases4`), so sánh hiệu quả giải quyết các bài toán kỹ thuật phức tạp giữa: *(Arm 0) Bare Prompt không cấu hình* $\to$ *(Arm 1) Chỉ có Rules* $\to$ *(Arm 2) Rules + Skills* $\to$ *(Arm 3) Rules + Hooks* $\to$ *(Arm 4) Full ECC Harness*.
3. **`docker/gateguard-effectiveness/` (`119` Files — Mô phỏng hội thoại đa lượt)**:
   - Chứa `119` tệp kịch bản và bộ khung đánh giá định lượng tỷ lệ agent tuân thủ nguyên tắc "đọc khảo sát mã nguồn trước khi sửa" khi bật và tắt `GateGuard`, cung cấp số liệu thực nghiệm chứng minh cơ chế `Prior-Search Credit` và `Denial Dampening`.

### 10.3. Bảo Mật Chuỗi Cung Ứng CI/CD (`.github/workflows/` — `13` Files)

Để bảo vệ chính kho mã nguồn `ECC` trước các cuộc tấn công chuỗi cung ứng phần mềm:
- **Ghim cứng 40-char Commit SHA (`scripts/ci/validate-workflow-security.js`)**: Mọi GitHub Action bên thứ ba trong cả `13` tệp workflow đều bắt buộc phải ghim bằng mã băm commit SHA dài đúng **40 ký tự hex** (ví dụ `actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683`), cấm tuyệt đối việc dùng thẻ khả biến như `@v4` hay `@main` vốn có thể bị kẻ tấn công chiếm quyền điều hướng.
- **Quét chỉ báo thỏa hiệp chuỗi cung ứng (`scripts/ci/scan-supply-chain-iocs.js`)**: Tự động quét toàn bộ cây phụ thuộc và mã nguồn để phát hiện các dấu hiệu tấn công chuỗi cung ứng đã biết (như chiến dịch mã độc **Shai-Hulud IOCs**, các webhook thu thập dữ liệu bất thường, hoặc các đoạn mã `preinstall` / `postinstall` khả nghi trong `package.json`).
- **Chống ngập lụt PR tự động (`pr-burst-guard.yml`)**: Giám sát tốc độ mở Pull Request và đóng băng tự động nếu phát hiện dấu hiệu bot spam hoặc tấn công làm cạn kiệt tài nguyên CI.
- **Chứng thực nguồn gốc SLSA Level 3 Provenance**: Bản phát hành chính thức của `ECC` đi kèm chứng chỉ nguồn gốc mật mã chuẩn **SLSA Level 3**, cho phép người dùng xác minh gói cài đặt được sinh ra từ đúng commit nguồn trên máy chủ build chính thống.

---

## Chương 11 — Đối Chiếu Toàn Diện `ECC` (`v2.2.3`) vs `TDQ Workflow` (`v0.71.0`) & Top 10 Tinh Hoa Đề Xuất Học Hỏi

Phần này đặt hai kiến trúc lên bàn cân kỹ thuật công tâm: một bên là **`ECC` (`v2.2.3`)** — hệ điều hành đa nền tảng quy mô lớn (~4.500 files), và một bên là **`TDQ Workflow` (`v0.71.0`)** — bộ khung điều phối quy trình kỹ thuật kỷ luật cao, tinh gọn, được tối ưu hóa dựa trên đo đạc thực nghiệm (`tdq_bench.py`) và triết lý Karpathy.

### 11.1. Bảng Đối Chiếu 10 Trục Kiến Trúc Giữa `ECC` (`v2.2.3`) Và `TDQ Workflow` (`v0.71.0`)

| Trục đối chiếu | `Everything Claude Code` (`ECC` `v2.2.3`) | `TDQ Workflow` (`v0.71.0`) | Nhận định & Bổ khuyết lẫn nhau |
| :--- | :--- | :--- | :--- |
| **1. Định vị & Triết lý cốt lõi** | *"The Agent Harness OS"*: Bao phủ chiều rộng với `311` skills, `122` rules (15 ngôn ngữ, 6 frameworks) và biên dịch ra 22+ harnesses. | Chuyên sâu điều phối đường ống kỷ luật cao (`intake -> spec -> plan -> implement -> qc -> report`), ngôn ngữ 3 tầng, quy tắc Karpathy (`ANTI-1..6`, `Surgical Changes`, `Simplicity First`). | `TDQ Workflow` mạnh hơn ở tính chặt chẽ của cổng duyệt từng pha và chống over-engineering; `ECC` mạnh hơn ở độ rộng thư viện tri thức đa ngôn ngữ. |
| **2. Quản trị Trạng thái & Tiến trình** | Phức hợp 2 tầng: Engine Rust `ecc2` dùng Actor `DbWriter` SQLite + tầng Node.js dùng WASM SQLite (`sql.js`) và JSON files. | Tinh gọn thuần Python chuẩn (`scripts/tdq_state.py`), lưu vết trực tiếp vào `docs/tdq/STATE.md` (dễ đọc cho cả người và máy) kèm `docs/tdq/timing.jsonl`. | `TDQ Workflow` không cần bước build phức tạp, dễ gỡ lỗi bằng mắt thường; `ECC` chịu tải cao tốt hơn khi chạy daemon hàng chục phiên ngầm. |
| **3. Kiến trúc Hooks & Độ trễ** | Gộp tiến trình qua In-Process Dispatcher (`require().run()`) tiết kiệm 50–100ms/call; tích lũy tệp sửa đổi để chạy Format/Typecheck 1 lần ở sự kiện `Stop`. | Các hook Python chuyên biệt kiểm soát cổng pha (`phase gate`), cưỡng chế bộ tìm kiếm 3 tầng và bảo vệ ranh giới vùng tệp worktree. | `TDQ Workflow` có thể học kỹ thuật In-Process Dispatcher và gom kiểm tra tĩnh về pha `Stop` của `ECC` để giảm độ trễ mỗi lượt gọi tool. |
| **4. Cổng Kiểm soát Đọc trước khi Sửa** | `GateGuard` Fact-Forcing: chia 5 nhóm tệp, cấp `Prior-Search Credit`, miễn trừ sửa nhỏ $\le 5$ dòng (`Trivial-Edit Bypass`) và giảm chấn `Denial Dampening` sau 3 lần chặn. | Bộ tìm kiếm 3 tầng (`LSP -> graphify -> grep`): gọi LSP mở khóa 10 lượt grep, định tuyến rõ theo loại câu hỏi (tên chính xác, vỡ lan kiến trúc, khái niệm mơ hồ). | `TDQ Workflow` vượt trội ở chiều sâu công cụ tra cứu ngữ nghĩa (LSP + đồ thị `graphify`); `ECC` khéo léo ở cơ chế giảm chấn chống kẹt (`Denial Dampening`). |
| **5. Điều phối Đa Agent & Chống xung đột** | Kết hợp 3 cơ chế: giải thuật khoảng cách `TCAS` $R(a,b)$ (Line Overlap + Import BFS + Tree LCA), nhãn GitHub Issues và cân bằng tải trong `ecc2` daemon. | Công cụ `scripts/tdq_team.py` chia đợt (`assign`, `open`, `check`, `merge`, `resolve`), khóa cứng danh sách tệp `Chạm:` trên từng worktree và chặn ghi ngoài vùng ngay lập tức. | Cách khóa cứng vùng tệp `Chạm:` của `TDQ Workflow` đảm bảo tính tất định khi merge; công thức `TCAS` $R(a,b)$ của `ECC` giúp phát hiện thêm phụ thuộc bắc cầu qua đồ thị `import`. |
| **6. Kiểm định Chất lượng & Review** | Quy trình `orch-review` 3 bước (Fan-out 3 chiều $\to$ Barrier Dedup $\to$ Adversarial Skeptic Verify Fail-Closed) + vòng lặp đối kháng `GAN Harness` ($\text{Score}_{\text{GAN}} \ge 7.0$). | Bộ kiểm tra tài liệu `doc_lint.py` (R1–R12), `tdq-reviewer` duyệt Spec/Plan, và 3 mức QC (`lite`/`full`/`ultra`) bởi `tdq-qc-tester` độc lập kiểm tra lại từng lệnh `Test:`. | Cơ chế kiểm tra lại lệnh `Test:` thật bằng `tdq_team.py check` của `TDQ Workflow` rất thực chất; bước `Adversarial Skeptic` của `ECC` là lớp lọc nhiễu xuất sắc cho code review. |
| **7. Học Liên tục & Bộ nhớ** | Hệ thống Homunculus (`continuous-learning-v2`): ghi `observations.jsonl`, chấm điểm `Instinct` $[0.3, 0.9]$ có phân rã thời gian và gom cụm bằng hệ số `Szymkiewicz-Simpson`. | Hệ thống `MEMORY.md` chỉ mục tinh gọn kết hợp nhật ký `docs/workinglog/YYYY-MM-DD.md` và đúc kết trực tiếp các bài học thực nghiệm vào `references/` của từng skill. | Cách lưu bộ nhớ của `TDQ Workflow` minh bạch, không bị nhiễu tự động; giải thuật gom cụm `Szymkiewicz-Simpson` của `ECC` rất hữu ích để quét định kỳ `workinglog/`. |
| **8. Bảo mật Runtime & Shell** | Bộ quét từ vựng `scanShell` ($\text{MaxSteps}=24L+4096$), vá `CVE-2024-27980` qua env-token, lọc Unicode/BiDi tags, `O_NOFOLLOW` Memory Vault và 6支柱 bảo mật. | Cưỡng chế duyệt cổng trực tiếp trong chat (cấm tự chuyển mode), cấm tuyệt đối attribution trailer, cô lập vùng chạm worktree và kiểm soát chặt quyền subagent. | Bộ quét `scanShell` và 6 kỹ thuật đặc trị lỗi Windows của `ECC` là những mảnh ghép kỹ thuật cấp thấp rất đáng tích hợp vào tầng bảo vệ lệnh shell của `TDQ Workflow`. |
| **9. Đóng gói Đa Nền Tảng & Toàn vẹn** | `Canonical Agent IR` biên dịch ra 22+ đích, chuỗi băm 6 tầng `Cryptographic Digest Chain` và kiểm tra bao đóng phụ thuộc AST `validate-carrier-closure.js`. | Cấu trúc Plugin chuẩn của Claude Code kết hợp trình đồng bộ và hỗ trợ chế độ chạy song hành trên OpenAI Codex qua `scripts/tdq_codex.py`. | Giải thuật kiểm tra bao đóng AST (`Static AST Dependency Closure`) của `ECC` có thể áp dụng ngay để kiểm tra tự động tính toàn vẹn của gói plugin `TDQ Workflow` trước mỗi lần bump version. |
| **10. Kinh tế học Context** | Nạp lười `122` rules theo `paths:`, cắt giảm MCP thừa (tiết kiệm 15k–40k tokens), định tuyến model 3 tầng và nén chiến lược ở ngưỡng 50%. | Kỹ thuật `muc-luc-dong` (đọc đúng dải dòng cần thiết), quy tắc tham chiếu tối đa 1 tầng, tối ưu hóa `luat_gon` và `muc_gat` đã được kiểm chứng bằng `tdq_bench.py`. | Cả hai dự án đều coi tối ưu hóa cửa sổ ngữ cảnh là nguyên lý sống còn; `TDQ Workflow` tiến xa hơn ở việc nén chính văn bản quy tắc thông qua đo đạc benchmark định lượng. |

---

### 11.2. Top 10 Tính Năng & Giải Thuật Tinh Hoa Của `ECC` Đề Xuất Chọn Lọc Học Hỏi Cho `TDQ Workflow`

Dựa trên nguyên tắc **`Simplicity First`** và **`Surgical Changes`** của `TDQ Workflow` (chỉ tiếp thu những cơ chế giải quyết bài toán thật với chi phí bảo trì thấp nhất, không bê nguyên sự cồng kềnh đa nền tảng của `ECC`), dưới đây là **10 tinh hoa kỹ thuật giá trị nhất** được đề xuất chuyển giao có chọn lọc:

#### 1. Gộp Tiến Trình Hook In-Process Dispatcher & Dồn Kiểm Tra Tĩnh Về Pha `Stop`
- **Nguồn từ `ECC`**: `scripts/hooks/pre-bash-dispatcher.js`, `post-edit-accumulator.js` và `stop-format-typecheck.js` (`SA4`).
- **Ứng dụng cho `TDQ Workflow`**: Gom các bước kiểm tra quy tắc ở `PreToolUse` / `PostToolUse` vào một điểm nhập Python duy nhất nạp sẵn mô-đun trong bộ nhớ; đồng thời chỉ ghi nhận danh sách file đã sửa trong lúc làm việc và dồn các phép kiểm tra nặng (`doc_lint.py`, kiểm tra cú pháp/kiểu) chạy một lần ở cuối lượt trả lời (`Stop`), giúp tăng tốc độ phản hồi của mỗi tool call.

#### 2. Cơ Chế Giảm Chấn `Denial Dampening` & Miễn Trừ Sửa Nhỏ `Trivial-Edit Bypass`
- **Nguồn từ `ECC`**: `scripts/hooks/gateguard-fact-force.js` (`SA4`).
- **Ứng dụng cho `TDQ Workflow`**: Trong cơ chế cưỡng chế bộ tìm kiếm 3 tầng (`LSP -> graphify -> grep`), bổ sung luật miễn trừ nhanh cho các thao tác sửa đổi nhỏ phi cấu trúc ($\le 5$ dòng trong tệp cấu hình/tài liệu) và cơ chế giảm chấn tự động chuyển từ chặn cứng sang cảnh báo nếu subagent bị kẹt lặp lại quá 3 lần trên một tình huống biên hợp lệ.

#### 3. Công Thức Khoảng Cách Phụ Thuộc `TCAS` ($R(a, b)$) Bổ Trợ Cho `tdq_team.py assign`
- **Nguồn từ `ECC`**: `scripts/lib/agent-proximity/distance.js` (`SA8`).
- **Ứng dụng cho `TDQ Workflow`**: Hiện tại `tdq_team.py` kiểm tra tính rời nhau (disjoint) của danh sách tệp `Chạm:` giữa các task chạy song song. Bằng cách bổ sung thành phần khoảng cách ngắn nhất trên đồ thị `import` ($r_{\text{dep}} = 0.5^{d-1}$), `tdq_team.py` có thể cảnh báo sớm khi hai task tuy chạm hai tệp khác nhau nhưng tệp của Task A lại `import` trực tiếp tệp của Task B ($d=1$), giúp xếp lịch chia đợt (`CỤM`) an toàn hơn nữa.

#### 4. Worktree Shared Dependency Symlink Cache Theo Mã Băm SHA-256 Lockfiles
- **Nguồn từ `ECC`**: `ecc2/src/worktree/mod.rs` (`SA2`).
- **Ứng dụng cho `TDQ Workflow`**: Khi `tdq_team.py open` tạo các worktree cô lập trong `.tdq-worktrees/<slug>/<task>`, tự động tính SHA-256 của tệp lockfile (`package-lock.json`, `pnpm-lock.yaml`, `uv.lock`, `Cargo.lock`) và tạo symlink/junction cho `.venv`, `node_modules`, `target` từ thư mục gốc nếu lockfile không đổi. Cải tiến này giúp các `tdq-implementer` chạy lệnh `Test:` tức thì mà không tốn thời gian hay dung lượng đĩa để cài lại thư viện.

#### 5. Bước Phản Biện Đối Kháng `Adversarial Skeptic Verification` (Fail-Closed `confidence >= 0.80`)
- **Nguồn từ `ECC`**: `workflows/orch-review.workflow.js` và `agents/code-reviewer.md` (`SA3`, `SA7`).
- **Ứng dụng cho `TDQ Workflow`**: Nâng cấp quy trình của `tdq-reviewer` và `tdq-qc-tester` bằng cổng lọc `Pre-Report Gate` (bắt buộc nêu kịch bản lỗi cụ thể `Input -> State -> Wrong Output`) kèm bước tự phản biện Fail-Closed: chỉ giữ lại các phát hiện có bằng chứng mã nguồn xác thực và loại bỏ các nhận xét bắt bẻ phong cách có độ tự tin thấp.

#### 6. Bộ Quét Từ Vựng Shell Hữu Hạn `scanShell` ($\text{MaxSteps} = 24L + 4096$)
- **Nguồn từ `ECC`**: `scripts/lib/shell-scan.js` và `scripts/hooks/block-no-verify.js` (`SA4`).
- **Ứng dụng cho `TDQ Workflow`**: Thay thế các biểu thức chính quy đơn giản kiểm tra lệnh shell bằng máy trạng thái từ vựng hữu hạn có khả năng bỏ qua nội dung nằm trong chuỗi nháy đơn/kép và khối heredoc (`<<EOF`), đồng thời bóc tách được lệnh nguy hiểm hoặc cờ `--no-verify` ẩn bên trong `$(...)`, `env -S`, `xargs` hay `git -c core.hooksPath=...`.

#### 7. Kiểm Tra Bao Đóng Phụ Thuộc Tĩnh `Static AST Dependency Closure`
- **Nguồn từ `ECC`**: `scripts/ci/validate-carrier-closure.js` (`SA9`).
- **Ứng dụng cho `TDQ Workflow`**: Viết một bài kiểm thử tĩnh trong `tests/` quét toàn bộ cây `import` của các tệp Python trong `scripts/` và các đường dẫn tham chiếu chéo trong `skills/*/SKILL.md` cùng `hooks/hooks.json`, đảm bảo mọi tệp được gọi đều tồn tại trong gói phát hành trước khi đẩy phiên bản mới lên kho đệm plugin.

#### 8. Lượng Hóa Điểm Rủi Ro Thao Tác 4 Chiều (`BaseTool + FileSensitivity + BlastRadius + Irreversibility`)
- **Nguồn từ `ECC`**: `ecc2/src/observability/mod.rs` (`SA2`).
- **Ứng dụng cho `TDQ Workflow`**: Áp dụng hàm chấm điểm rủi ro 4 chiều $\text{Score} \in [0.0, 1.0]$ vào hook giám sát lệnh của `TDQ Workflow` để phân biệt chính xác giữa lệnh đọc/chạy test thông thường ($\text{Score} < 0.35$) với các lệnh chạm tệp nhạy cảm hoặc không thể đảo ngược ($\text{Score} \ge 0.85$), giúp bảo vệ cây mã nguồn mà không làm gián đoạn các thao tác an toàn.

#### 9. Gom Cụm Kinh Nghiệm Bằng Hệ Số `Szymkiewicz-Simpson` Trên Nhật Ký `workinglog/`
- **Nguồn từ `ECC`**: `skills/continuous-learning-v2/` (`SA6`).
- **Ứng dụng cho `TDQ Workflow`**: Sử dụng hệ số trùng lặp $\text{Overlap}(T_A, T_B) = \frac{|T_A \cap T_B|}{\min(|T_A|, |T_B|)} \ge 0.5$ trong công cụ `tdq-lean` hoặc script phân tích định kỳ để quét các mục ghi chép trong `docs/workinglog/YYYY-MM-DD.md` và `docs/tdq/timing.jsonl`, tự động phát hiện các mẫu vướng mắc lặp lại từ 3 lần trở lên để đề xuất chuẩn hóa thành quy tắc trong `references/`.

#### 10. Sáu Kỹ Thuật Đặc Trị Lỗi Hệ Điều Hành Windows 11
- **Nguồn từ `ECC`**: `scripts/lib/windows-bash.js` và bộ công cụ bảo vệ đường dẫn Windows (`SA4`).
- **Ứng dụng cho `TDQ Workflow`**: Tích hợp trực tiếp các chốt chặn thực chiến trên Windows 11 vào `scripts/tdq_setup.py` và các script chạy hook: lọc bỏ stub `System32\bash.exe` khi WSL rỗng, lọc bỏ redirector `WindowsApps\python3.exe`, tước hậu tố luồng dữ liệu phụ NTFS `::$DATA`, và định danh tệp bằng cặp chỉ số `dev + ino` 64-bit để miễn nhiễm với lỗi lệch hoa/thường trên hệ thống tệp NTFS.

---

## Kết Luận Tổng Hợp

Cuộc giải phẫu toàn diện dự án `ecc-universal` (`Everything Claude Code` `v2.2.3`) cho thấy sức mạnh thực sự của một hệ thống điều phối Agent hiện đại không nằm ở độ dài của lời nhắc (prompt length), mà nằm ở **các cơ chế cưỡng chế tất định ngoài mô hình (deterministic out-of-model guardrails)**: từ việc cô lập luồng ghi SQLite bằng Actor `DbWriter` trong `ecc2`, lượng hóa rủi ro 4 chiều, tính toán khoảng cách va chạm `TCAS` trên đồ thị phụ thuộc, quét từ vựng shell với ngân sách hữu hạn `scanShell`, cho đến quy trình thẩm định đối kháng Fail-Closed trong `orch-review` và chuỗi băm mật mã 6 mắt xích `Cryptographic Digest Chain`.

Khi kết hợp các giải thuật cơ học tinh hoa này vào khung quy trình kỷ luật cao, tinh gọn và bám sát triết lý Karpathy của **`TDQ Workflow` (`v0.71.0`)**, hệ thống sẽ đạt được sự cân bằng lý tưởng giữa **tốc độ thực thi tối đa**, **tiết kiệm ngữ cảnh triệt để** và **độ an toàn kỹ thuật tuyệt đối**.
