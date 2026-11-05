# REPORT — Khắc phục Đứt kết nối MCP Plugin trên Claude Desktop (`2026-11-05-1247-sua-mcp-plugin-desktop` · lane quick · mode main · 2 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Trước request (trạng thái/flow):** Claude Desktop chạy với `strictPluginOnlyCustomization: ["mcp"]`, chỉ nạp MCP từ `<plugin_cache>/.mcp.json`; cache plugin `0.89.0` có file này nhưng cache `0.90.0`/`0.91.0` mất file sau update. `scripts/search_rules.py` và `hooks/hooks.json` chỉ nhận `mcp__lsp__*`, nên tool `mcp__plugin_tdq-workflow_lsp__*` không kích hoạt Search Gate/Hook đúng chuẩn.
**Sau request (trạng thái/flow):** `scripts/tdq_setup.py` có `dong_bo_mcp_plugin_cache`, tự đọc `mcpServers` từ `~/.claude.json`, ghi nguyên tử `.mcp.json` vào cache plugin active và mở `permissions.allow` cho LSP/Chrome MCP plugin khi cài đặt, chạy nền `--nen`, auto-update và setup bù. `scripts/search_rules.py` + `hooks/hooks.json` nhận cả `mcp__lsp__*` và `mcp__plugin_tdq-workflow_lsp__*`. · **Đã làm:** T1 sửa matcher/search recognition · T2 tự đồng bộ MCP cache + permissions; khôi phục ngay `0.91.0/.mcp.json` trên máy với 4 server.
**Đã test gì:** (1) `tests/test_search_rules.py`, `tests/test_search_observe.py`, `tests/test_lsp_gate.py`, `tests/test_subagent_start.py` kiểm regex/matcher Hook; (2) `tests/test_auto_update_setup.py`, `tests/test_tdq_setup.py` kiểm đồng bộ cache/permissions; (3) smoke thật `dong_bo_mcp_plugin_cache()` và `tdq_lsp.py check`; (4) QC độc lập `tdq-qc-tester`.
**Kết quả test:** `206 passed, 4 subtests passed, 0 failed`; cache `~/.claude/plugins/cache/tdq-local/tdq-workflow/0.91.0/.mcp.json` tồn tại và có `lsp`, `chrome-devtools`, `tavily-primary`, `tavily-backup`; rung 4 LSP đạt và có 2 allow rules (`mcp__lsp__*`, `mcp__plugin_tdq-workflow_lsp__*`). QC độc lập vòng 1 phát hiện server giả có chữ `lsp` bị nhận nhầm; `QC1.1` chuyển regex sang allowlist (`mcp__lsp__*`, `mcp__plugin_tdq-workflow_lsp__*`, `lsp.*`) và QC độc lập vòng 2 xác nhận `VERDICT: PASS everything`, 0 defect. · **Kết quả:** cache MCP plugin thiếu sau update `có → tự khôi phục` · matcher plugin `không nhận → nhận đầy đủ nhưng không nhận nhầm server khác` · **Kiểm:** `tdq_lsp.py check` smoke 3 tầng PASS · QC ultra PASS.
**Đầu ra:** `scripts/tdq_setup.py`, `scripts/search_rules.py`, `scripts/tdq_lsp.py`, `hooks/hooks.json` · **Archify HTML:** [docs/tdq/reports/2026-11-05-1247-sua-mcp-plugin-desktop.html](2026-11-05-1247-sua-mcp-plugin-desktop.html)
**Giới hạn:** Mở qua cổng LSP bằng `--bo-qua-lsp "sua loi dong bo .mcp.json plugin cache va matcher tool MCP plugin"` trên module `python:.`; đứt kết nối ở phiên Desktop đang mở vẫn cần người dùng reconnect `/mcp` hoặc restart Desktop sau khi cache đã được khôi phục. Eval live paid-model không cần thiết cho bugfix cấu hình/hook, ghi `eval-waive` theo lane Express.
**Lệch spec chờ duyệt:** không có
**Git:** chưa commit trên nhánh `bugfix/sua-mcp-plugin-desktop` (gốc: `dev`)

## Thời gian

Request `2026-11-05-1247-sua-mcp-plugin-desktop` · lane quick · opened at 2026-11-05T12:58:54+07:00

| Phase | Wall clock | API request | Tool wait | Background job | Observed union | Unattributed | Times entered |
|---|---|---|---|---|---|---|---|
| idle | 1s | — [partial] | 1s [partial] | — [unavailable] | 1s [partial] | 0s [partial] | 1 |
| analyze | 2 min | 1 min [partial] | 7s [partial] | — [unavailable] | 1 min [partial] | 1 min [partial] | 1 |
| implement | 17 min | 8 min [partial] | 2 min [partial] | — [unavailable] | 9 min [partial] | 8 min [partial] | 1 |
| report | 8s | 4s [partial] | 4s [partial] | — [unavailable] | 8s [partial] | 0s [partial] | 1 |
| Total | 19 min | 9 min [partial] | 2 min [partial] | — [unavailable] | 10 min [partial] | 9 min [partial] |  |

Model compute time is unavailable (`model_giay=null`). API includes network/provider latency; tool time is host wait. Observed metrics may overlap; unattributed time is not assumed user/model time.

## Thân PR (soạn sẵn)

**Tóm tắt:** Khôi phục tự động MCP plugin sau mỗi cài đặt/cập nhật bằng cách đồng bộ `.mcp.json` vào cache active, đồng thời nhận diện đúng tool MCP được Claude Desktop prefix và mở permissions cần thiết.
**Trước/Sau:** [docs/tdq/plan/2026-11-05-1247-sua-mcp-plugin-desktop-flow.html](../plan/2026-11-05-1247-sua-mcp-plugin-desktop-flow.html)
**Đã kiểm:**
- `python -m pytest tests/test_search_rules.py tests/test_search_observe.py tests/test_lsp_gate.py tests/test_subagent_start.py tests/test_auto_update_setup.py tests/test_tdq_setup.py -q` → `206 passed, 4 subtests passed`
- `python scripts/tdq_lsp.py check` → bậc 4 quyền tool và smoke grep/LSP/graphify đạt
**Rủi ro hồi quy:** Claude Desktop cần reconnect `/mcp` hoặc restart để nạp file `.mcp.json` vừa khôi phục vào phiên đang mở; cache version mới sẽ tự đồng bộ ở lần setup/update sau.
<!-- tdq-archify-binding:start -->
<!-- manifest: 2026-11-05-1247-sua-mcp-plugin-desktop.manifest.json -->
<!-- manifest_digest: 2e8d979478eb5bc65745bb9b2b166eacbbd9d053a5ad77d9005035b4a6ffcf93 -->
<!-- tdq-archify-binding:end -->