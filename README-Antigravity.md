# TDQ-Workflow-Antigravity

Hệ sinh thái đóng gói và kiểm chứng **TDQ-Workflow (`v0.97.0` — nhánh `dev @ b423ee06`)** chạy **100% Native** trên **Google Antigravity** (`Windows PowerShell 5.1` + MCP + 6 Lifecycle Hooks + 6 Subagents + 12 Skills + 10 Two-Tier Rules), được biên dịch sạch không chỉnh sửa kho gốc (`ForAgentCode/TDQ-Workflow` giữ nguyên Read-Only).

## Cấu Trúc Workspace & Công Cụ Chính

- **`plugins/tdq-workflow/`** — Plugin Antigravity đã biên dịch hoàn chỉnh (`plugin.json`, `hooks.json`, `mcp_config.json`, `manifest.json`, `rules/`, `skills/`, `agents/`, `hooks/scripts/`, `scripts/`).
- **`.agents/plugins.json`** — Cấu hình discovery cục bộ trỏ `./plugins` để thử nghiệm trong workspace mà không chạm `~/.gemini/config/config.json`.
- **`tools/build_agy_plugin.py`** — Trình biên dịch từ kho gốc `ForAgentCode/TDQ-Workflow` sang `plugins/tdq-workflow/` kèm toàn bộ bản vá tương thích Antigravity + Windows (`tools/patches/`).
- **`tools/install_agy_plugin.py`** — Trình cài đặt an toàn vào `~/.gemini/config/plugins/tdq-workflow` (hỗ trợ `--dry-run`, `--target`, `--sync-local-mcp`).
- **`tools/run_full_verification.py`** — Bộ chạy kiểm chứng tổng lực `V1–V6` và xuất bằng chứng JSON thực nghiệm ra [`docs/verification_evidence.json`](./docs/verification_evidence.json).
- **`tests/`** — Bộ test `pytest` (`14/14 PASSED`) xác thực validator chính chủ, `EC-01..14`, `NEW-01..28`, stress test NTFS 8 tiến trình (`320/320` zero-loss), live `agent-lsp.exe` stdio JSON-RPC và E2E 10 bước toàn vòng đời.

## Lệnh Build, Kiểm Chứng & Cài Đặt Nhanh (PowerShell)

```powershell
# 1. Biên dịch lại plugin sạch từ mã nguồn của nhánh AntigravityBranch_Improve
$env:PYTHONDONTWRITEBYTECODE='1'; py -3 -B tools/build_agy_plugin.py

# 2. Chạy trình kiểm định chính chủ Antigravity & toàn bộ 14 tests kiểm chứng Antigravity
agy.EXE plugin validate plugins/tdq-workflow --strict --json
py -3 -B -m pytest tests/test_agy_plugin_validate.py tests/test_cli_fixes_new01_28.py tests/test_e2e_workflow.py tests/test_hooks_dual_protocol.py tests/test_ntfs_concurrency.py -v --basetemp=.pytest_tmp

# 3. Sinh báo cáo bằng chứng thực nghiệm JSON
$env:PYTHONDONTWRITEBYTECODE='1'; py -3 -B tools/run_full_verification.py

# 4. Cài đặt thử / đồng bộ vào plugin store người dùng (chưa bật mặc định)
py -3 tools/install_agy_plugin.py --dry-run
# py -3 tools/install_agy_plugin.py --sync-local-mcp
```

## Tài Liệu Kiểm Chứng & Báo Cáo Thực Nghiệm (`docs/`)

- **[docs/MASTER-VERIFICATION-CHECKLIST-AND-EVIDENCE.md](./docs/MASTER-VERIFICATION-CHECKLIST-AND-EVIDENCE.md)** — **Master Checklist 10 Phân Hệ (Đã Kiểm Chứng Thực Nghiệm):** Đối chiếu đầy đủ `7` companion extensions (live `65` Agent-LSP tools), host addons/manifests, `Soul` + `R1–R15` + `10` rules, `12` skills (`75` files) + `M01–M20`, `6` subagents, `6` hook events + `24` mã `TDQ:*`, `EC-01..EC-14` + `320/320` NTFS, `60+1` scripts + `7` excluded + `NEW-01..NEW-28`, chuỗi E2E 10 bước và bằng chứng bất biến upstream/global config.
- **[docs/TDQ-Antigravity-Audit-Dashboard.html](./docs/TDQ-Antigravity-Audit-Dashboard.html)** — **Dashboard Trực Quan v3.0 (Live Verified, Offline-Safe):** Nhúng trực tiếp số liệu từ `verification_evidence.json` với bộ lọc tìm kiếm nhanh và tra cứu 65 tools `agent-lsp`, `EC-01..14`, `NEW-01..28`, `M01..20`.
- **[docs/verification_evidence.json](./docs/verification_evidence.json)** — Dữ liệu bằng chứng JSON thô thu thập trực tiếp từ máy thật.
- **[docs/AUDIT-AND-PORTING-PLAN.md](./docs/AUDIT-AND-PORTING-PLAN.md)** — Đặc tả kiến trúc & lộ trình porting gốc v2.0.
- **`docs/research/` (`01` → `10`)** — 10 hồ sơ phân tích chuyên sâu và Deep Rescan 100% trước khi đóng gói.
