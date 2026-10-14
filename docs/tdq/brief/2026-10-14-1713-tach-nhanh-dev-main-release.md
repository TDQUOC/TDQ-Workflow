# BRIEF — Tách nhánh dev để phát triển và nhánh main để phát hành sạch

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> "okay bây giờ tôi muốn phân tích là sẽ tách làm 2 nhánh 1 là dev: nhánh chính để develop, và nhánh main để release và ở nhánh man sẽ ko có docs cũng như cso file test dư thừa trong lúc dev "

### Đọc bước đầu

- **Mục tiêu:** Phân tích và thiết kế cơ chế tách quy trình Git của dự án thành 2 nhánh chính:
  1. Nhánh `dev`: nhánh làm việc và phát triển chính (chứa đầy đủ `docs/`, `tests/`, lịch sử thiết kế/workinglog/spec/plan/qc/report và công cụ phát triển nội bộ).
  2. Nhánh `main`: nhánh phát hành (release) gọn sạch để phân phối plugin/workflow — loại bỏ toàn bộ tài liệu phát triển nội bộ (`docs/`) và các file test/công cụ dư thừa trong lúc dev.
- **Phạm vi dự kiến:**
  - Cấu trúc nhánh Git (`dev` làm nhánh phát triển mặc định cho các nhánh request `feature/*`, `bugfix/*`, `chore/*`; `main` chỉ nhận bản phát hành sạch).
  - Danh sách chính xác các thư mục/file cần loại bỏ khi đóng gói sang `main` và những file bắt buộc phải giữ lại trên `main` để plugin Claude Code / Codex / OpenCode / Antigravity hoạt động bình thường.
  - Cơ chế đồng bộ/phát hành từ `dev` sang `main` để xuất cây thư mục sạch sang `main` mà không gây xung đột merge mỗi lần release.

## Hiểu & kiến thức

### Năng lực dùng được

| Nguồn | Tên | Khớp chỗ nào | Quyết định | Lý do |
|---|---|---|---|---|
|内置/MCP | `mcp__lsp__*` (`python`) | Tra cứu symbol và phụ thuộc import trong `scripts/*.py` | **dùng** | Xác định chính xác bao đóng bắc cầu (transitive closure) của các script runtime so với script dev-only |
| Repo script | `scripts/build_portable.py` | Đã có sẵn hằng số `EXCLUDE_DIRS` và `EXCLUDE_FILES` khi đóng gói bản portable | **dùng** | Tái sử dụng triết lý lọc cây thư mục phát hành, đặt lệnh `--sinh-main` ngay trong `scripts/build_portable.py` (Rung 2 `TDQ:GON`) |
| Repo script | `scripts/claude_export.py` | Đóng gói repo qua `git clone` (chỉ lấy tracked files) | **bỏ** | `claude_export.py` phục vụ xuất toàn bộ môi trường `~/.claude` sang máy khác, không phải công cụ cắt nhánh `dev -> main` |
| Skill ngoài | Các plugin UI/cloud trong phiên | Không liên quan đến thao tác Git branch/tree và đóng gói CLI Python | **bỏ** | Bài toán thuần Git plumbing & Python stdlib trong repo |

### Khảo sát hiện trạng mã nguồn & thống kê dung lượng (`git ls-files`)

1. **Thống kê toàn bộ 1,472 files (~19.8 MB) đang được Git track trên `HEAD`:**
   - **Nhóm tài liệu & lịch sử phát triển nội bộ:**
     - `docs/`: **1,103 files (~14,218.5 KB ≈ 13.9 MB)** — gồm `docs/tdq/{brief,spec,plan,qc,reports,audit,bench}`, `docs/workinglog/`, `docs/canvas/`. Chiếm **74.9% tổng số file** và **71.8% dung lượng** repo.
     - `CHANGELOG-archive.md`: **1 file (25.0 KB)** — lịch sử changelog cũ đã lưu trữ.
   - **Nhóm kiểm thử, đánh giá & đồ thị phân tích nội bộ:**
     - `tests/`: **177 files (1,540.6 KB ≈ 1.50 MB)** — bộ unittest nội bộ của repo.
     - `graphify-out/`: **3 files (2,400.2 KB ≈ 2.34 MB)** — cache đồ thị phân tích mã nguồn của chính repo TDQ-Workflow.
     - `evals/`: **32 files (27.6 KB)** — dữ liệu kịch bản đánh giá nội bộ.
     - `.taskmaster/`: **4 files (16.9 KB)** — cấu hình taskmaster cũ.
     - `tools_kiem/`: **1 file (6.7 KB)** — `dem_da_nen_tang.py`.
     - `.github/workflows/test.yml`: **1 file (2.3 KB)** — chạy `python -m unittest discover tests` trên GitHub Actions.
     - `pyrightconfig.json`: **1 file (0.2 KB)**.
   - **Phân tích phụ thuộc AST (`import`) trong `scripts/` (48 files, 981.1 KB):**
     - **35 script runtime (cần giữ trên `main`)**: Bao đóng bắc cầu từ các lệnh được gọi trong `skills/`, `hooks/`, `.claude-plugin/`, `.codex-plugin/`, `.opencode/` gồm: `build_portable.py`, `claude_export.py`, `context_surface.py`, `doc_lint.py`, `kiem_no_marker.py`, `lsp_module.py`, `plugin_tiers.py`, `scan_block_symbols.py`, `search_replay.py`, `search_rules.py`, `setup_status.py`, `setup_status_render.py`, `skill_inventory.py`, `skill_tokens.py`, `step_audit.py`, `tdq_bench.py`, `tdq_checkportable.py`, `tdq_checkstatus.py`, `tdq_codex.py`, `tdq_codex_mcp.py`, `tdq_finish.py`, `tdq_lsp.py`, `tdq_no.py`, `tdq_setup.py`, `tdq_state.py`, `tdq_team.py`, `tdq_ten_lenh.py`, `tdq_test.py`, `tdq_timing.py`, `tdq_vision_diff.py`, `tdq_vungfile.py`, `tdq_worktree_registry.py`, `token_audit.py`, `token_budget.py`, `utf8_io.py`.
     - **13 file thuần dev/canvas/audit trong `scripts/` (không có bất kỳ caller nào từ runtime skills/hooks)**: `canvas_a4_ch4_ch7.py`, `canvas_a4_rebuild.py`, `canvas_draw.py`, `canvas_layout_apply.py`, `canvas_move_block.py`, `check_canvas_layout.py`, `doc_dup.py`, `doc_index.py`, `i18n_check.py`, `luat_phan_loai.py`, `skill_router.py`, `tdq_eval.py`, và `scripts/samples/transcript-step-audit.jsonl`.
   - **Nhóm lõi Runtime Plugin bắt buộc giữ trên `main`:**
     - Manifest & host wrappers: `.claude-plugin/` (2 files), `.codex-plugin/` (1 file), `.opencode/` (2 files), `.agents/` (1 file), `.claude/` (1 file), `.codex/` (2 files).
     - Nội dung plugin: `skills/` (59 files), `agents/` (3 files), `hooks/` (17 files), `portable_src/` (1 file), `claude-export/` (5 files), `scripts/` runtime (35 files).
     - Gốc repo: `README.md`, `CHANGELOG.md`, `.gitignore`, `.gitattributes`, `.graphifyignore`, `.env.example`.
     - **Tổng kích thước nhánh `main` sau khi làm sạch:** Chỉ còn **136 files (~1.15 MB)** — giảm **90.8% số lượng file** và **93.5% dung lượng** so với nhánh `dev`.

2. **Phân tích các bài toán kỹ thuật khi tách `dev` và `main`:**
   - **Bài toán 1 — Xung đột `modify/delete` nếu dùng `git merge` thông thường:**
     - Giải quyết bằng **Git Plumbing Snapshot (`git commit-tree`)** tích hợp vào `scripts/build_portable.py --sinh-main`: đọc danh sách tracked blobs từ nhánh nguồn (`dev`) qua `git ls-tree -r -z <nguon>`, lọc bỏ các thư mục/file dev-only, nạp vào một `GIT_INDEX_FILE` tạm (`git update-index --index-info`), sinh `tree_sha` bằng `git write-tree`, và tạo commit trên nhánh đích (`main`) nối tiếp parent `<main_head>` (nếu `main` đã là chuỗi release hoặc tạo commit mới kèm `from dev@<short_sha>`). Nếu cây thư mục sau khi lọc trùng khớp hoàn toàn `tree_sha` hiện tại của `main`, lệnh tự động báo `no change` (idempotent, không đẻ commit rỗng).
   - **Bài toán 2 — Nhánh gốc mặc định (`nhanh_goc`) khi làm việc trên `dev`:**
     - Trong `scripts/tdq_test.py`, bổ sung hàm `nhanh_goc_mac_dinh(repo)` kiểm tra sự tồn tại của `refs/heads/dev` trong repo (nếu có thì dùng `dev`, nếu không thì fallback `main`) khi `state.json` không có khóa `nhanh_goc`.

### Lý do bỏ qua Scope round riêng

- Yêu cầu của người dùng đã xác định rõ bài toán duy nhất (tách nhánh `dev` để phát triển và nhánh `main` để release sạch không chứa `docs/` và file test/dev dư thừa). Do đó bỏ qua vòng hỏi Scope round tách rời và gộp luôn 4 câu hỏi chốt thiết kế + mức QC vào 1 vòng phỏng vấn duy nhất.

### Phạm vi đã chốt

- **Trong phạm vi (In-scope):**
  1. Bổ sung chức năng phát hành nhánh `main` sạch (`--sinh-main`, kèm `--nguon`, `--nhanh-dich`, `--dry-run`) vào `scripts/build_portable.py` dùng Git plumbing (`git ls-tree`, `git update-index`, `git write-tree`, `git commit-tree`, `git update-ref`).
  2. Lọc triệt để trên nhánh `main` release (theo lựa chọn 2A): loại bỏ các thư mục cấp gốc `docs/`, `tests/`, `evals/`, `graphify-out/`, `.taskmaster/`, `tools_kiem/`, `.github/`, các file cấp gốc `CHANGELOG-archive.md`, `pyrightconfig.json`, thư mục `scripts/samples/` và 12 file script thuần dev/canvas/audit trong `scripts/` (`canvas_a4_ch4_ch7.py`, `canvas_a4_rebuild.py`, `canvas_draw.py`, `canvas_layout_apply.py`, `canvas_move_block.py`, `check_canvas_layout.py`, `doc_dup.py`, `doc_index.py`, `i18n_check.py`, `luat_phan_loai.py`, `skill_router.py`, `tdq_eval.py`). Giữ nguyên toàn bộ 35 script runtime và cấu trúc plugin đa host.
  3. Tổ chức lịch sử commit trên `main` theo chuỗi commit snapshot release độc lập (lựa chọn 3A — ghi rõ `from dev@<short_sha>` trong commit message, không gắn parent vào nhánh `dev` để tránh kéo theo lịch sử blob của `docs/` và `tests/`).
  4. Cập nhật `scripts/tdq_test.py` để tự nhận diện nhánh gốc `dev` (nếu repo có `refs/heads/dev`) trước khi fallback về `main`.
  5. Cập nhật `skills/tdq-intake/references/nhanh-request.md` và `docs/kien-truc.md` ghi nhận quy ước 2 nhánh `dev` (develop) và `main` (release sạch).
  6. Viết đầy đủ unit test trên repo Git tạm cho cả logic lọc đường dẫn, tạo snapshot release `--sinh-main` (gồm `--dry-run`, idempotent khi không đổi, bảo toàn working tree đang đứng ở `dev`) và nhận diện nhánh gốc `dev` trong `tdq_test.py`.
- **Ngoài phạm vi (Out-of-scope):**
  - Không thay đổi cấu trúc gói Antigravity/Claude/Codex portable hiện có của `build_portable.py`.
  - Không xóa `docs/` hay `tests/` trên nhánh `dev` hoặc nhánh phát triển hiện tại.
- **Mức QC đã chốt:** `full` (lựa chọn 4A).

### Lộ trình

- `analyze` → `spec` → `plan` → `mode` → `implement` → `qc` → `idle` (pipeline `full` chuẩn, không bỏ bước nào).
- Các luồng tính năng:
  1. `build-release`: Mở rộng `scripts/build_portable.py` với `--sinh-main` và bộ lọc cây Git release sạch + unit test trong `tests/test_build_portable.py`.
  2. `base-branch-detect`: Cập nhật `scripts/tdq_test.py` tự động ưu tiên nhánh gốc `dev` khi tồn tại + unit test trong `tests/test_tdq_test.py`.
  3. `workflow-branch-docs`: Cập nhật `skills/tdq-intake/references/nhanh-request.md` và `docs/kien-truc.md` về mô hình 2 nhánh `dev` (develop) / `main` (release).

## Hỏi đáp

### Vòng 1 (2026-10-14 17:22)

1. **Phạm vi thực thi trong request này**:
   - A (đề xuất): Làm trọn gói (viết script phát hành `dev -> main` + unit test + tạo nhánh `dev` giữ đủ toàn bộ file + cập nhật nhánh `main` sạch khi hoàn tất)
   - B: Chỉ viết script phát hành + cập nhật quy ước và test trên repo tạm, chưa chạy lệnh cắt nhánh `main` thật
   - **Trả lời nguyên văn:** `1a`
2. **Mức độ lọc bỏ file dư thừa trên nhánh `main` (release)**:
   - A (đề xuất): Làm sạch triệt để (~135 files còn lại) — loại bỏ `docs/`, `tests/`, `evals/`, `graphify-out/`, `.taskmaster/`, `tools_kiem/`, `.github/`, `CHANGELOG-archive.md`, `pyrightconfig.json` VÀ 13 file script thuần dev/canvas/audit trong `scripts/` (giữ nguyên đủ 35 script runtime)
   - B: Loại bỏ các thư mục/file cấp gốc dành cho dev nhưng giữ nguyên toàn bộ thư mục `scripts/` (48 files)
   - C: Chỉ loại bỏ `docs/`, `tests/` và `graphify-out/`
   - **Trả lời nguyên văn:** `2A`
3. **Cách tổ chức lịch sử commit trên nhánh `main` khi release từ `dev`**:
   - A (đề xuất): Chuỗi commit release độc lập trên `main` (mỗi lần release tạo 1 commit snapshot sạch nối tiếp `main` cũ, ghi rõ `from dev@<sha>` trong commit message)
   - B: Commit trên `main` có 2 parents (`main` cũ + `dev` hiện tại)
   - **Trả lời nguyên văn:** `3A`
4. **Mức kiểm thử chất lượng (QC) cho request này**:
   - A (đề xuất): Mức tiêu chuẩn (`full`)
   - B: Mức tối đa (`ultra`)
   - C: Mức cơ bản (`lite`)
   - **Trả lời nguyên văn:** `4A`
5. **Bạn muốn bổ sung thêm gì không?**
   - A (đề xuất): Không, đủ rồi — làm tiếp đi.
   - B: Có — tôi nói thêm.
   - **Trả lời nguyên văn:** `5A`
