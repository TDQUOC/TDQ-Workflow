# QUICK — Khắc phục đứt kết nối MCP của Plugin `tdq-workflow` trên Claude Desktop

**Ngày:** 2026-11-05 · Brief: ../brief/2026-11-05-1247-sua-mcp-plugin-desktop.md · Lane: quick
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
**Trạng thái:** HOÀN THÀNH
**Ước tính sẽ dùng skill:** tdq-workflow:tdq-build

## Phạm vi
- Bỏ B0: Đã có tiền lệ chạm cùng vùng (`scripts/tdq_setup.py`, `scripts/search_rules.py`, `hooks/hooks.json`).
- Bỏ B2: Không có phụ thuộc/API bên ngoài repo cần research mới.
- Bỏ vòng phạm vi: Đã xác định chính xác 2 nguyên nhân gốc rễ (mất `.mcp.json` khi nâng version plugin cache và lệch matcher `mcp__plugin_tdq-workflow_lsp__*`).
- Trong: Tự động đồng bộ `mcpServers` từ `~/.claude.json` vào `<plugin_cache>/.mcp.json` và mở `permissions.allow` (`mcp__plugin_tdq-workflow_lsp__*`, `mcp__plugin_tdq-workflow_chrome-devtools__*`) mỗi khi cài đặt, chạy nền `--nen` hoặc auto-update plugin; mở rộng regex `LSP` trong `scripts/search_rules.py` và matcher trong `hooks/hooks.json` để nhận diện `mcp__plugin_tdq-workflow_lsp__*`; khôi phục ngay `.mcp.json` cho bản `0.91.0` trên máy.
- NGOÀI: Không lưu API key vào git repo, không thêm hook item mới làm lệch tổng 14 hook.

## Task
- [x] **T1** Mở rộng regex `LSP` trong `scripts/search_rules.py` và matcher trong `hooks/hooks.json` để nhận cả `mcp__lsp__*` lẫn `mcp__plugin_tdq-workflow_lsp__*` — Test: `python -m pytest tests/test_search_rules.py tests/test_search_observe.py tests/test_lsp_gate.py tests/test_subagent_start.py -q`
  - Chạm: `scripts/search_rules.py`, `hooks/hooks.json`, `tests/test_search_rules.py`, `tests/test_search_observe.py`
- [x] **T2** Tự động đồng bộ `.mcp.json` vào cache plugin và quyền `permissions.allow` trong `scripts/tdq_setup.py` khi setup/update/chạy nền — Test: `python -m pytest tests/test_auto_update_setup.py tests/test_tdq_setup.py -q`
  - Chạm: `scripts/tdq_setup.py`, `tests/test_auto_update_setup.py`

## Definition of Done
- [x] Tool `mcp__plugin_tdq-workflow_lsp__*` khớp matcher trong `hooks/hooks.json` và được `search_rules.la_goi_khai_niem` ghi nhận mở khóa Grep — `python -m pytest tests/test_search_rules.py tests/test_search_observe.py tests/test_lsp_gate.py tests/test_subagent_start.py -q`
- [x] `tdq_setup.py` tự động đồng bộ `.mcp.json` sang thư mục cache plugin active + cập nhật `permissions.allow` khi cài/update/chạy nền, và file `~/.claude/plugins/cache/tdq-local/tdq-workflow/0.91.0/.mcp.json` trên máy có đủ 4 server — `python -m pytest tests/test_auto_update_setup.py tests/test_tdq_setup.py -q`

## QC
- Q1 test từng task (`T1` + `T2`): PASS — `python -m pytest tests/test_search_rules.py tests/test_search_observe.py tests/test_lsp_gate.py tests/test_subagent_start.py tests/test_auto_update_setup.py tests/test_tdq_setup.py -q` → `206 passed, 4 subtests passed in 10.97s`
- Q2 DoD "Tool `mcp__plugin_tdq-workflow_lsp__*` khớp matcher trong `hooks/hooks.json` và được `search_rules.la_goi_khai_niem` ghi nhận mở khóa Grep": PASS — `python -m pytest tests/test_search_rules.py tests/test_search_observe.py tests/test_lsp_gate.py tests/test_subagent_start.py -q` → `142 passed, 4 subtests passed in 9.80s`
- Q3 DoD "`tdq_setup.py` tự động đồng bộ `.mcp.json` sang thư mục cache plugin active + cập nhật `permissions.allow` khi cài/update/chạy nền, và file `~/.claude/plugins/cache/tdq-local/tdq-workflow/0.91.0/.mcp.json` trên máy có đủ 4 server": PASS — `python -m pytest tests/test_auto_update_setup.py tests/test_tdq_setup.py -q` → `64 passed in 1.24s`, `0.91.0/.mcp.json` có đủ `lsp`, `chrome-devtools`, `tavily-primary`, `tavily-backup`
- Q4 Smoke & Runtime (`muc_qc=ultra`): PASS — `python scripts/tdq_lsp.py check` → bậc 4 ĐẠT (2 mục trong allow: `mcp__lsp__*` và `mcp__plugin_tdq-workflow_lsp__*`), smoke 3 tầng grep, LSP, graphify đều ĐẠT
- Q5 Independent QC Review (`tdq-qc-tester`): PASS vòng 2 — vòng 1 phát hiện `mcp__other_lsp__find_symbol` bị nhận nhầm là LSP; `QC1.1` chuyển regex sang allowlist, rồi review độc lập xác nhận `206 passed, 4 subtests passed`, server giả → `None`, server plugin hợp lệ → `lsp:find_symbol`, 0 defect còn lại.

## QC vòng 1 — fix
- [x] **QC1.1** Chỉ nhận diện `mcp__lsp__*`, `mcp__plugin_tdq-workflow_lsp__*` hoặc `lsp.*`; từ chối server có tên chứa `lsp` nhưng không thuộc TDQ — Test: `python -m pytest tests/test_search_rules.py tests/test_search_observe.py tests/test_lsp_gate.py tests/test_subagent_start.py tests/test_auto_update_setup.py tests/test_tdq_setup.py -q` → `206 passed, 4 subtests passed in 10.75s`
<!-- tdq-archify-binding:start -->
<!-- manifest: 2026-11-05-1247-sua-mcp-plugin-desktop-flow.manifest.json -->
<!-- manifest_digest: 4fd29347509029ded923341b571d9c796f54560693e83ac685da2f76b1bb725e -->
<!-- tdq-archify-binding:end -->