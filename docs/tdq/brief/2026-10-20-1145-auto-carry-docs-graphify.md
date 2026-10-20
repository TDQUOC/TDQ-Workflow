# BRIEF — Tự Động Mang Theo & Merge File Docs và Graphify Khi Đổi Nhánh (`2026-10-20-1145-auto-carry-docs-graphify`)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

"okay tôi muốn mở request handle là nếu cần mở nhánh hoặc merge và dirty ở docs hoặc graphify thì được auto mang theo/ comit/ merge không cân hỏi người dùng"

## Hiểu & kiến thức

### 1. Phân tích hiện trạng & Giải pháp
1. **Hiện trạng mở nhánh (`tdq-intake` bước 3b & `nhanh-request.md`)**:
   - Quy tắc hiện hành chỉ cho phép tự động chuyển nhánh mang theo file dirty khi `git status --porcelain` chỉ chứa `docs/**`, `*.md`, `logs/**`, `*.log`.
   - Các file thuộc `graphify-out/**` (như `graphify-out/graph.json`, `graphify-out/tdq-full-manifest.json`, `graphify-out/wiki/**`) nếu có thay đổi dirty thì bị coi là ngoài phạm vi docs/log, khiến Agent phải dừng lại hỏi người dùng không cần thiết.

2. **Hiện trạng merge và đóng request (`tdq-build` bước 11 & `report-template.md`)**:
   - Khi hợp nhất nhánh request về nhánh gốc, nếu còn file dirty ở `docs/` hoặc `graphify-out/`, hệ thống có thể bị chặn bởi git switch hoặc đòi hỏi xác nhận lặp đi lặp lại.

3. **Giải pháp chuẩn hóa**:
   - **Mở rộng vùng tự động mang theo (Auto-carry zone)**: Quy định rõ ràng trong cả `tdq-intake` bước 3b, `nhanh-request.md`, `report-template.md` và `KHOI_HUONG_DAN` (`CLAUDE.md`): Khi working tree dirty nhưng CHỈ thuộc:
     - `docs/**` (tài liệu, brief, spec, plan, qc, report, state, log)
     - `*.md` (các file markdown)
     - `logs/**`, `*.log`
     - `graphify-out/**` (đồ thị graph.json, manifest, wiki)
     → **TỰ ĐỘNG mang theo / commit / merge**, tuyệt đối không dừng lại hỏi người dùng.
   - Chỉ khi nào có dirty ở **mã nguồn thực thi** (`scripts/`, `src/`, `hooks/`, `tests/`...) thì Agent mới dừng lại để hỏi ý kiến người dùng.

### 2. Năng lực & công cụ
- `tdq-intake`: Cập nhật quy tắc mở nhánh tự động mang theo `docs` và `graphify-out`.
- `tdq-build`: Cập nhật bước 11 merge tự động commit/mang theo `docs` và `graphify-out`.
- `tdq-setup`: Cập nhật `KHOI_HUONG_DAN` ghim vào `CLAUDE.md`.

## Hỏi đáp
- Không có câu hỏi còn mở. Phạm vi hoàn toàn rõ ràng.
