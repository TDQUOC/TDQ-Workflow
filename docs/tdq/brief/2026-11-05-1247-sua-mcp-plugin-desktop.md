# Brief — Chẩn đoán & Khắc phục đứt kết nối MCP của Plugin `tdq-workflow` trên Claude Desktop
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> hiện tại đang có vấn đề về mcp của plugin hyax check xem tại sao và report cho tôi nguyên nhân và liệu có đề xuất xử lí ko?
>
> 1a sửa luôn giúp tôi

**Đọc lần đầu (First reading):**
- **Mục tiêu:** Sửa dứt điểm lỗi mất kết nối các MCP server của plugin `tdq-workflow` (`plugin:tdq-workflow:lsp`, `chrome-devtools`, `tavily-primary`, `tavily-backup`) trên Claude Desktop sau khi plugin tự động nâng cấp (`0.89.0` → `0.90.0` → `0.91.0`), đồng thời mở rộng nhận diện tiền tố `mcp__plugin_tdq-workflow_lsp__*` trong Hook/Search Gate và `permissions.allow`.

## Hiểu & kiến thức

- **Bỏ B0:** Đã có tiền lệ chạm cùng vùng (`scripts/tdq_setup.py`, `scripts/search_rules.py`, `hooks/hooks.json`).
- **Bỏ B2:** Không có phụ thuộc/API bên ngoài repo cần research mới.
- **Khảo sát 3 chiều (B1 — Graphify + Grep + Read):**
  1. `scripts/tdq_setup.py`:
     - `tu_dong_cap_nhat_plugin_user` (dòng 665) và `thuc_hien_cap_nhat_remote` (dòng 811) gọi `claude plugin update tdq-workflow@tdq-local -s user -y`, tạo thư mục cache version mới (`~/.claude/plugins/cache/tdq-local/tdq-workflow/<version>`) từ git repo. Vì git repo không chứa `.mcp.json`, file `.mcp.json` đã có ở `0.89.0` không được mang sang `0.90.0` và `0.91.0`.
     - Giải pháp: bổ sung hàm `dong_bo_mcp_plugin_cache(home=None, duong_cau_hinh="~/.claude.json", cham_may=None)` đọc `mcpServers` từ `~/.claude.json` và ghi nguyên tử `.mcp.json` vào `installPath` của plugin `tdq-workflow@*` (scope `user`) trong `~/.claude/plugins/installed_plugins.json`, đồng thời đảm bảo `permissions.allow` trong `~/.claude/settings.json` có `mcp__lsp__*`, `mcp__plugin_tdq-workflow_lsp__*`, `mcp__plugin_tdq-workflow_chrome-devtools__*`. Gọi tự động trong `kiem_plugin_user`, `tu_dong_cap_nhat_plugin_user`, `thuc_hien_cap_nhat_remote`, `thuc_hien_setup_bu`, và `khoi_tao_nen`.
  2. `scripts/search_rules.py` (dòng 868) & `hooks/hooks.json` (dòng 76, 85, 105, 116):
     - Regex `LSP = re.compile(r"(^|__|\.)lsp(__|\.)")` không khớp `mcp__plugin_tdq-workflow_lsp__find_symbol` vì trước `lsp` là `_` đơn. Đổi thành `re.compile(r"(^|__|_|\.)lsp(__|\.)")`.
     - Trong `hooks/hooks.json` (và `.codex/hooks.json` nếu có), cập nhật matcher `mcp__lsp__(start_lsp|blast_radius)` → `mcp__(plugin_tdq-workflow_)?lsp__(start_lsp|blast_radius)` và `mcp__lsp__.*` → `mcp__(plugin_tdq-workflow_)?lsp__.*` (giữ nguyên đúng 14 hook items để pass `test_subagent_start.py`).

## Hỏi đáp

- **Câu 1 (Chọn pipeline):** Người dùng chọn `1a` (`"1a sửa luôn giúp tôi"` — chế độ nhanh express).
