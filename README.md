# TDQ-Workflow — Hệ Điều Hành Spec-Driven & Kiến Trúc Tương Tác Cho AI Coding Agents

![Version](https://img.shields.io/badge/version-0.84.0-2563eb?style=for-the-badge)
![Tests](https://img.shields.io/badge/tests-2977%20passed-16a34a?style=for-the-badge)
![Search](https://img.shields.io/badge/search-3--tier%20LSP%20%C2%B7%20Graphify%20%C2%B7%20Grep-0d9488?style=for-the-badge)
![Visual BA](https://img.shields.io/badge/archify-2--tier%20Personal%20BA%20%26%20Master%20Map-7c3aed?style=for-the-badge)
![Hosts](https://img.shields.io/badge/hosts-Claude%20%C2%B7%20Codex%20%C2%B7%20OpenCode%20%C2%B7%20Antigravity-ea580c?style=for-the-badge)

**TDQ-Workflow** biến AI Agent từ một công cụ sinh mã tự phát thành một **Kỹ sư Phần mềm & Chuyên gia Phân tích Nghiệp vụ (Personal BA)** làm đúng ngay từ lần triển khai đầu tiên.

Mọi yêu cầu đều đi qua chu trình kỷ luật: **Khảo sát 3 chiều (LSP + Graphify + Grep) → Phỏng vấn → Đặc tả & Archify HTML → Bạn duyệt bằng chat**. Sau đó, hệ thống lập **Kế hoạch Red-Green → Thực thi qua Git Worktree → Kiểm định QC Loop → Báo cáo nghiệm thu**.

---

## Mục lục

1. [Điểm Khác Biệt Cốt Lõi (6 Trụ Cột Bất Biến)](#1-điểm-khác-biệt-cốt-lõi-6-trụ-cột-bất-biến)
2. [Bản Đồ Kiến Trúc Tương Tác (Master Map & Personal BA)](#2-bản-đồ-kiến-trúc-tương-tác-master-map--personal-ba)
3. [Chu Trình Pipeline (Deep, Express & Direct)](#3-chu-trình-pipeline-deep-express--direct)
4. [Hướng Dẫn Setup & Cài Đặt Dependencies Từ A–Z](#4-hướng-dẫn-setup--cài-đặt-dependencies-từ-az)
5. [Cài Đặt Plugin Trên 4 Nền Tảng (Hosts)](#5-cài-đặt-plugin-trên-4-nền-tảng-hosts)
6. [Cơ Chế Hook Giám Sát & Verify-by-Effect](#6-cơ-chế-hook-giám-sát--verify-by-effect)
7. [Cấu Trúc Kho Mã Nguồn](#7-cấu-trúc-kho-mã-nguồn)
8. [Sử Dụng Hằng Ngày & Quy Trình Phát Hành](#8-sử-dụng-hằng-ngày--quy-trình-phát-hành)

---

## 1. Điểm Khác Biệt Cốt Lõi (6 Trụ Cột Bất Biến)

| Trụ cột | Vấn đề của AI thông thường | Giải pháp của TDQ-Workflow |
|---|---|---|
| **1. Tam Giác Khảo Sát 3 Chiều** | Chỉ `grep` chuỗi văn bản, bỏ sót nơi gọi ngầm và làm vỡ module liên đới | Kết hợp **LSP** (ngữ nghĩa compiler), **Graphify** (quét vỡ lan 2 bước nhảy trên đồ thị AST) và **Grep** (quét nhanh diện rộng) |
| **2. Personal BA với Archify 2-Tier** | Viết đặc tả dài dòng khó đọc, kiến trúc thực tế lệch khỏi tài liệu | Tự động dựng sơ đồ **HTML tương tác** trước cổng duyệt Spec/Plan và duy trì **Master Map** toàn dự án tự đánh dấu `stale` khi code đổi |
| **3. Verify-by-Effect (Không tin lời khai)** | Agent báo "đã test xanh, đã ghi log" nhưng thực tế chưa chạy lệnh | 13 Lifecycle Hooks chụp vân tay SHA-256 trên đĩa từ đầu lượt và đối chiếu hiệu ứng thật tại cổng `Stop` |
| **4. Kỷ Luật Red → Green & Bán Kính Test** | Viết hàng trăm dòng code xong mới chạy test hoặc chạy toàn bộ suite gây chậm | Mỗi task có 1 test đỏ trước khi sửa; giữa các bước chỉ chạy `tdq_test.py vung-cham` (vùng chạm + bán kính AST), trọn bộ chạy đúng tại cổng QC |
| **5. Đội Ngũ Sub-Agent Cô Lập Worktree** | Nhiều agent sửa chung cây thư mục gây ghi đè và xung đột ngầm | `tdq_team.py` chia kế hoạch thành từng đợt (`wave`), phát hiện va chạm AST (TCAS) và cấp worktree riêng cho từng task |
| **6. Kiểm Thử Thị Giác 5 Lớp (DevTools MCP)** | Chỉ nhìn chuỗi HTML tĩnh rồi kết luận giao diện đạt | Tích hợp Chrome DevTools MCP kiểm tra 5 lớp: cây DOM/A11y, Responsive Desktop/Mobile, tương tác Hover/Fill, Console/Network 0 lỗi và CSS Cascade |

---

## 2. Bản Đồ Kiến Trúc Tương Tác (Master Map & Personal BA)

Dự án tích hợp sẵn hệ thống trực quan hóa kiến trúc 2 tầng bằng động cơ **Archify**:

- **Tầng Dự Án — Master Architecture Portal:** Mở trực tiếp [`docs/architecture/index.html`](docs/architecture/index.html) trên trình duyệt để khám phá 4 bản đồ tương tác của `TDQ-Workflow`:
  1. [`overview.html`](docs/architecture/overview.html) — Kiến trúc tổng thể 6 tầng (4 Host Adapters, 11 Skills, 6 Agents, 13 Hooks, 43 CLI Scripts, State Ledger).
  2. [`pipeline-lifecycle.html`](docs/architecture/pipeline-lifecycle.html) — Vòng đời thực thi Spec-Driven, mô phỏng chọn Mode và điều phối Đội ngũ qua Git Worktree.
  3. [`search-and-archify.html`](docs/architecture/search-and-archify.html) — Tam Giác Tìm Kiếm 3 Tầng (LSP, Graphify, Grep) và động cơ xuất bản Archify 4 cổng.
  4. [`hooks-and-gates.html`](docs/architecture/hooks-and-gates.html) — Chuỗi 13 Lifecycle Hooks trên 6 sự kiện và cơ chế đối chiếu hiệu ứng `Verify-by-Effect`.
- **Tầng Nhiệm Vụ — Task BA Preview:** Mỗi yêu cầu mới ở chế độ chuyên sâu hoặc nhanh đều sinh bản xem trước HTML gắn mã băm hai chiều với tài liệu Spec/Plan trước khi viết code.

```bash
# Kiểm tra độ tươi (freshness) của Master Map so với mã nguồn hiện tại
python3 scripts/tdq_archify.py status --project .

# Đồng bộ và xuất bản lại Master Map khi kiến trúc thay đổi
python3 scripts/tdq_archify.py sync-master --model docs/tdq/models/master.model.json --project . --out docs/architecture
```

---

## 3. Chu Trình Pipeline (Deep, Express & Direct)

```text
[Chế độ Chuyên sâu — Deep (full)]
Intake ──► Analyze (3-Tier Search + Interview) ──► Spec + Archify HTML ──► [BẠN DUYỆT SPEC]
       ──► Plan + Simulate Mode ──► [BẠN DUYỆT PLAN & MODE]
       ──► Implement (Main / Sub-agent Worktrees, Tick [~]→[x] tức thì)
       ──► QC Loop (lite / full / ultra) ──► Report & Hỏi Commit

[Chế độ Nhanh — Express (quick)]
Intake ──► Quick Analyze ──► Mini-Plan ≤10 dòng (+ Flow HTML khi chạm nhiều module) ──► [BẠN DUYỆT NHANH] ──► Implement & QC

[Chế độ Trực tiếp — _tdq_direct]
Gõ kèm từ khóa "_tdq_direct" trong prompt ──► Tự động khảo sát & lập Mini-Plan ngay, chỉ dừng ở 1 cổng duyệt duy nhất.
```

**Duyệt tự nhiên ngay trong khung chat:** Bạn chỉ cần nhắn `"duyệt spec"`, `"duyệt plan"`, `"1a"` hoặc `"duyệt nhanh"` — không bao giờ bị làm phiền bởi hộp thoại popup. Hệ thống lưu nguyên văn câu duyệt kèm chữ ký `sha256` của tài liệu vào `docs/tdq/state.json`.

---

## 4. Hướng Dẫn Setup & Cài Đặt Dependencies Từ A–Z

### 4.1. Thiết lập tự động chỉ với 1 câu lệnh (Khuyên dùng)

`TDQ-Workflow` cung cấp công cụ tự phục hồi môi trường (`Self-healing Setup`). Sau khi tải kho mã về máy, bạn chỉ cần chạy:

```bash
python3 scripts/tdq_setup.py
# Trên Windows nếu chưa có lệnh python3, chạy bằng:
python scripts/tdq_setup.py
```

Lệnh trên sẽ **tự động kiểm tra và cài đặt cả 8 bậc công cụ** mà không cần cấu hình thủ công:
1. Tạo shim `python3` trên Windows nếu máy chỉ có `python` hoặc `py -3`.
2. Kiểm tra và cài đặt binary `agent-lsp` cùng cấu hình MCP server `lsp` trong `~/.claude.json` và `.codex/config.toml`.
3. Dò ngôn ngữ của dự án hiện tại và cài đặt Language Server tương ứng (`pyright`, `typescript-language-server`...).
4. Cấp quyền `mcp__lsp__*` vào danh sách cho phép để không bật thông báo hỏi quyền mỗi lần tra cứu.
5. Kiểm tra xung đột hook với các plugin bên ngoài.
6. Kiểm tra tệp mốc cấu hình gốc import (`pyproject.toml`, `tsconfig.json`, `package.json`...).
7. Kiểm tra công cụ đồ thị `graphify` và độ mới của `graphify-out/graph.json`.
8. Chạy thử nghiệm khói (Smoke Test) cả 3 tầng tìm kiếm (`grep`, `LSP`, `graphify`) và kiểm tra động cơ `archify`.

### 4.2. Danh sách Dependencies & Cài đặt thủ công từng phần

Nếu bạn muốn tự chuẩn bị môi trường trên máy mới hoặc máy chủ CI/CD, dưới đây là bảng yêu cầu chi tiết:

| Thành phần | Phiên bản yêu cầu | Vai trò trong TDQ-Workflow | Lệnh cài đặt thủ công |
|---|---|---|---|
| **Python** | `>= 3.10` (khuyên dùng `3.11+`) | Chạy toàn bộ 43 CLI scripts và 13 Lifecycle Hooks (thuần stdlib) | Tải từ `python.org` hoặc `winget install Python.Python.3.13` / `brew install python` |
| **Node.js** | `>= 18.0.0` (khuyên dùng `20+`) | Chạy động cơ trực quan hóa `archify`, `pyright` và `chrome-devtools-mcp` | Tải từ `nodejs.org` hoặc `winget install OpenJS.NodeJS.LTS` / `brew install node` |
| **agent-lsp** | `>= 0.19.0` | Máy chủ MCP nối AI với Language Server của 30+ ngôn ngữ | `curl -fsSL https://raw.githubusercontent.com/blackwell-systems/agent-lsp/main/install.sh \| sh` (hoặc chạy `python scripts/tdq_setup.py`) |
| **Language Servers** | Theo ngôn ngữ dự án | Cung cấp định nghĩa, nơi gọi và kiểm tra kiểu chính xác | Python: `npm i -g pyright`<br>TS/JS: `npm i -g typescript typescript-language-server` |
| **graphify** | Bản mới nhất | Dựng đồ thị AST cục bộ và tính bán kính vỡ lan `affected --depth 2` | `pip install graphifyy` (hoặc `uv tool install graphifyy`), sau đó chạy `graphify extract . --code-only` |
| **archify** | `>= 3.2.0` | Động cơ kiểm định bố cục và xuất bản sơ đồ HTML tương tác | Đặt gói `archify` tại `~/Documents/archify` hoặc khai biến môi trường `ARCHIFY_ROOT=/đường/dẫn/tới/archify` trong `.env` |
| **Chrome DevTools MCP** | Tuỳ chọn (cho UI/UX Audit) | Kiểm thử giao diện 5 lớp trực tiếp trên trình duyệt thật qua cổng 9222 | Tự động cấu hình và khởi chạy bằng `python3 scripts/tdq_devtool_mcp.py setup` và `python3 scripts/tdq_devtool_mcp.py launch` |

### 4.3. Các lệnh kiểm tra sức khỏe hệ thống

```bash
# 1. Kiểm tra 8 bậc tìm kiếm (LSP + Graphify + Grep)
python3 scripts/tdq_lsp.py check

# 2. Kiểm tra môi trường Node.js & gói Archify
python3 scripts/tdq_archify.py check

# 3. Kiểm tra tính khả chuyển trên máy hiện tại
python3 scripts/tdq_checkportable.py check
```

---

## 5. Cài Đặt Plugin Trên 4 Nền Tảng (Hosts)

Mọi nền tảng đều đọc **cùng một thư mục `skills/` duy nhất** thông qua lớp adapter mỏng:

| Host | Adapter trong Repo | Lệnh cài đặt nhanh |
|---|---|---|
| **Claude Code** | `.claude-plugin/` | `/plugin marketplace add TDQUOC/TDQ-Workflow` rồi `/plugin install tdq-workflow@tdq-local` |
| **Codex** | `.agents/plugins/marketplace.json` + `.codex-plugin/plugin.json` | `codex plugin marketplace add TDQUOC/TDQ-Workflow` rồi `codex plugin add tdq-workflow@tdq-local` |
| **OpenCode** | `.opencode/plugins/tdq-workflow.js` | Khai báo trong `opencode.json` (xem chi tiết tại [`.opencode/INSTALL.md`](.opencode/INSTALL.md)) |
| **Antigravity** | Sinh trực tiếp vào `~/.gemini/config/plugins/tdq-workflow/` | `python3 scripts/build_portable.py --sinh-agy` |

### Cấu hình tự động cập nhật cho Claude Code

Thêm khối sau vào `.claude/settings.json` của dự án để tự động nhận bản cập nhật mới:

```json
{
  "extraKnownMarketplaces": {
    "tdq-local": {
      "source": { "source": "github", "repo": "TDQUOC/TDQ-Workflow" },
      "autoUpdate": true
    }
  },
  "enabledPlugins": { "tdq-workflow@tdq-local": true }
}
```

Chạy thẳng từ thư mục cục bộ khi phát triển: `claude --plugin-dir /đường/dẫn/tới/TDQ-Workflow`.

---

## 6. Cơ Chế Hook Giám Sát & Verify-by-Effect

Hệ thống gồm 13 hooks lắng nghe trên 6 sự kiện vòng đời, kết hợp giữa lời nhắc điều hướng và cổng chặn bảo vệ:

| Mã kiểm soát | Khi nào xuất hiện | Cơ chế xử lý của Agent |
|---|---|---|
| `TDQ:NEXT` | Đầu mỗi phiên hoặc đầu mỗi lượt làm việc | Đọc pha hiện tại và thực hiện đúng bước tiếp theo trong bảng pha |
| `TDQ:SEARCH` | Gọi `grep` tìm mã nguồn khi chưa tra cứu tầng khái niệm | **Chặn cứng (Deny):** Buộc gọi `mcp__lsp__*` hoặc `graphify` trước để mở cửa sổ 10 lượt `grep` |
| `TDQ:LSP` | Gọi `start_lsp` thiếu `language_id` hoặc sai thư mục gốc | **Chặn cứng (Deny):** Buộc truyền đủ cặp `(root_dir, language_id)` |
| `TDQ:APPROVE` | Người dùng vừa nhắn duyệt hoặc agent chạm code khi chưa duyệt | Ghi nhận phê duyệt qua `tdq_state.py approve` trước khi làm việc tiếp |
| `TDQ:TICK` | Sửa liên tiếp 3 lần mà chưa cập nhật tiến độ trong file Plan | Mở file Plan, đánh dấu `[~]` hoặc `[x]` ngay khi bài kiểm của task đạt xanh |
| `TDQ:WORKTREE` | Còn nhánh con trong `.tdq-worktrees/` chưa dọn sau khi chạy Team Mode | Chạy `python3 scripts/tdq_team.py sweep` để đối soát và thu hồi worktree |
| `TDQ:STATE` | Cố tình ghi đè `docs/tdq/state.json` bằng lệnh shell | Chỉ được phép cập nhật trạng thái thông qua CLI `scripts/tdq_state.py` |
| `TDQ:LOG` | Kết thúc lượt có thay đổi tệp nhưng chưa ghi nhật ký `docs/workinglog/` | **Chặn cổng Stop:** Buộc gọi `python3 scripts/tdq_finish.py --files ... --log "..."` |

---

## 7. Cấu Trúc Kho Mã Nguồn

| Thư mục | Vai trò & Thành phần |
|---|---|
| `skills/` (11) | `tdq-intake`, `tdq-spec`, `tdq-plan`, `tdq-build`, `tdq-lean`, `tdq-status`, `tdq-check-status`, `tdq-conventions`, `tdq-setup`, `tdq-browser-research`, `tdq-browser-test` |
| `agents/` (6) | `tdq-reviewer`, `tdq-implementer`, `tdq-qc-tester`, `tdq-refactor-cleaner`, `tdq-security-reviewer`, `tdq-build-resolver` |
| `hooks/` (13 trên 6 sự kiện) | `session_start`, `subagent_start`, `prompt_context`, `search_observe` (2 sự kiện), `edit_gate`, `bash_gate`, `read_gate`, `search_gate`, `lsp_gate`, `ask_gate`, `lsp_post_observe`, `stop_gate` |
| `scripts/` (43) | Tầng CLI lõi: `tdq_state.py`, `tdq_finish.py`, `tdq_test.py`, `tdq_team.py`, `tdq_archify.py`, `archify_delivery.py`, `archify_model.py`, `archify_artifacts.py`, `tdq_lsp.py`, `tdq_setup.py`, `doc_lint.py`, `token_budget.py`, `build_portable.py`... |
| `docs/architecture/` | Cổng thông tin **Master Map** (`index.html`, 4 bản đồ tương tác `.html` và `manifest.json`) |
| `docs/tdq/` | Hồ sơ theo từng request (`brief/`, `spec/`, `plan/`, `qc/`, `reports/`, `state.json`, `token-budget.json`) |
| `tests/` | Hơn 2.970 bài kiểm tự động khóa toàn bộ hợp đồng CLI, Hooks, Archify, Đa nền tảng và Luật ngôn ngữ |

---

## 8. Sử Dụng Hằng Ngày & Quy Trình Phát Hành

### Các lệnh CLI thường dùng

```bash
# Xem trạng thái request đang mở và bước kế tiếp
python3 scripts/tdq_state.py next

# Chạy kiểm thử thông minh theo vùng chạm + bán kính phụ thuộc AST
python3 scripts/tdq_test.py vung-cham

# Chạy toàn bộ bộ kiểm thử tại cổng QC
python3 scripts/tdq_test.py tron-bo

# Khóa sổ cuối lượt: kiểm tra khóa token + lint tài liệu + ghi workinglog + đánh dấu độ tươi Master Map
python3 scripts/tdq_finish.py --files <danh-sách-file> --log "<tóm tắt công việc>"
```

### Quy trình Bump Version & Phát hành

1. Cập nhật cùng một số `version` trong `.claude-plugin/plugin.json` và `.codex-plugin/plugin.json`.
2. Ghi mục thay đổi mới lên đầu tệp `CHANGELOG.md` (giữ tổng số dòng dưới 500 theo luật R6).
3. Chạy `python3 scripts/build_portable.py --sinh-main` để xuất bản nhánh `main` tinh gọn từ nhánh phát triển `dev`.
