# Nghiệm thu Khắc phục Đứt Kết nối MCP Plugin trên Claude Desktop (`2026-11-05-1247-sua-mcp-plugin-desktop`) {#tong-quan}

@meta locale=vi

Báo cáo nghiệm thu cho request `2026-11-05-1247-sua-mcp-plugin-desktop` (lane `quick`, mức QC `ultra`, 2/2 task hoàn tất). Đã khắc phục dứt điểm nguyên nhân mất file `.mcp.json` trong thư mục cache của plugin khi tự động cập nhật phiên bản, đồng thời mở rộng nhận diện tiền tố công cụ `mcp__plugin_tdq-workflow_lsp__*` trong Hook, Search Gate và phân quyền permissions.

## 1. Trước và Sau Request (Trạng thái & Luồng) {#truoc-sau}

@workflow id=truoc-sua title="Trước khi sửa (Hiện trạng lỗi)"
| update | claude plugin update tạo cache 0.91.0 mới | backend |
| matmcp | Mất .mcp.json trong cache 0.91.0 | database |
| lechregex | search_rules & hooks chỉ khớp mcp__lsp__* | security |
| gay | Desktop báo plugin:tdq-workflow:lsp đứt | frontend |
| update > matmcp | repo không lưu .mcp.json chứa key/path |
| matmcp > lechregex | strictPluginOnlyCustomization chặn global |
| lechregex > gay | gọi LSP plugin không mở khóa Grep |

@workflow id=sau-sua title="Sau khi sửa (Trạng thái & Flow mới)"
| sync | tdq_setup tự đồng bộ .mcp.json vào cache | backend |
| allow | Tự mở permissions.allow cho MCP plugin | security |
| matcher | Regex & hooks khớp cả mcp__plugin_..._lsp | security |
| ok | Desktop nạp đủ 4 MCP qua mọi đợt update | frontend |
| sync > allow | chạy trong setup, --nen và auto-update |
| allow > matcher | không hỏi quyền lặp lại mỗi lần gọi |
| matcher > ok | mở khóa 10 lượt Grep đúng chuẩn 3 tầng |

- **Trước request:** Khi plugin được cập nhật từ bản `0.89.0` lên `0.90.0` và `0.91.0`, thư mục cache mới được tạo từ git repo không có file `.mcp.json`. Claude Desktop với cờ `strictPluginOnlyCustomization: ["mcp"]` chặn nạp từ `~/.claude.json`, nên toàn bộ MCP plugin bị đứt. Regex và matcher chỉ nhận `mcp__lsp__*`.
- **Sau request — Đồng bộ cache:** `scripts/tdq_setup.py` có `dong_bo_mcp_plugin_cache`. Hàm này đọc `mcpServers` từ `~/.claude.json` và đồng bộ sang `.mcp.json` của cache plugin active khi cài đặt, chạy nền `--nen` hoặc auto-update phiên bản mới.
- **Sau request — Phân quyền:** `scripts/tdq_setup.py` tự bổ sung `mcp__plugin_tdq-workflow_lsp__*` và `mcp__plugin_tdq-workflow_chrome-devtools__*` vào `permissions.allow` trong `~/.claude/settings.json`.
- **Sau request — Nhận diện tool:** `scripts/search_rules.py` và `hooks/hooks.json` nhận diện chính xác cả `mcp__lsp__*` lẫn `mcp__plugin_tdq-workflow_lsp__*`. Regex allowlist từ chối server không thuộc TDQ dù tên có chứa `lsp`.
- **Sau request — Khôi phục tức thời:** File `.mcp.json` cho plugin `0.91.0` trên máy đã được khôi phục, gồm 4 server: `lsp`, `chrome-devtools`, `tavily-primary`, `tavily-backup`.

## 2. Đã Test Gì & Kết Quả Test Thực Tế {#kiem-thu}

@workflow id=luong-test title="Chuỗi Kiểm thử & Kết quả"
| t1 | Test matcher regex & hook observer | backend |
| t2 | Test tự động đồng bộ cache & allow | database |
| smoke | Smoke kiểm tra đĩa thật & bậc 4 LSP | frontend |
| review | Subagent QC độc lập ultra audit | security |
| t1 > t2 | 142 passed trong suite search rules/observe |
| t2 > smoke | 64 passed trong auto update & setup |
| smoke > review | 0.91.0/.mcp.json có 4 server, bậc 4 ĐẠT |

- **Đã test T1:** Kiểm thử nhận diện tool `mcp__plugin_tdq-workflow_lsp__*` mở khóa Grep và khớp các hook events (`tests/test_search_rules.py`, `tests/test_search_observe.py`, `tests/test_lsp_gate.py`, `tests/test_subagent_start.py`).
- **Đã test T2:** Kiểm thử hàm đồng bộ `dong_bo_mcp_plugin_cache` và cấp quyền permissions trong `scripts/tdq_setup.py` (`tests/test_auto_update_setup.py`, `tests/test_tdq_setup.py`).
- **Đã test Smoke & Runtime:** Chạy trực tiếp `dong_bo_mcp_plugin_cache()` trên máy thật, kiểm tra file cache `0.91.0/.mcp.json` và chạy `python scripts/tdq_lsp.py check` xác nhận bậc 4 quyền tool đạt.
- **Đã test QC Ultra Độc lập:** Subagent `tdq-qc-tester` rà soát toàn bộ diff và chạy lại các bài kiểm. Vòng 1 phát hiện server giả `mcp__other_lsp__find_symbol` bị nhận nhầm. `QC1.1` đổi regex sang allowlist, sau đó vòng 2 xác nhận PASS.
- **Kết quả suite:** Toàn bộ **206 passed, 4 subtests passed, 0 failures** trên 6 tệp test liên quan sau `QC1.1`.
- **Kết quả cache & quyền:** Cache plugin `0.91.0/.mcp.json` tồn tại và có đủ 4 server. Bậc 4 quyền tool trong `tdq_lsp.py check` có 2 allow rules hợp lệ: `mcp__lsp__*` và `mcp__plugin_tdq-workflow_lsp__*`.
- **Kết quả an toàn:** Server không thuộc TDQ có tên chứa `lsp` không thể mở khóa Grep. QC độc lập vòng 2 xác nhận `VERDICT: PASS everything`, 0 defect còn lại.
