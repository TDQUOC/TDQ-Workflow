# Trước vs Sau — Khắc phục Đứt Kết nối MCP Plugin trên Claude Desktop {#tong-quan}

@meta locale=vi

Bản thiết kế Trước/Sau cho request `2026-11-05-1247-sua-mcp-plugin-desktop` (lane `quick`). Giải quyết triệt để lỗi mất `.mcp.json` trong thư mục cache của plugin sau khi nâng cấp phiên bản (`0.89.0` -> `0.91.0`) và lỗi không nhận diện tiền tố `mcp__plugin_tdq-workflow_lsp__*` trên Claude Desktop.

## Luồng Trước và Sau khi Sửa {#truoc-sau}

@workflow id=truoc-sua title="Trước khi sửa (Hiện trạng lỗi)"
| update | claude plugin update tạo cache 0.91.0 mới | backend |
| matmcp | Mất .mcp.json trong cache 0.91.0 | database |
| lechregex | search_rules & hooks chỉ khớp mcp__lsp__* | security |
| gay | Desktop báo plugin:tdq-workflow:lsp đứt | frontend |
| update > matmcp | repo không lưu .mcp.json chứa key/path |
| matmcp > lechregex | strictPluginOnlyCustomization chặn global |
| lechregex > gay | gọi LSP plugin không mở khóa Grep |

@workflow id=sau-sua title="Sau khi sửa (Planned)"
| sync | tdq_setup tự đồng bộ .mcp.json vào cache | backend |
| allow | Tự mở permissions.allow cho MCP plugin | security |
| matcher | Regex & hooks khớp cả mcp__plugin_..._lsp | security |
| ok | Desktop nạp đủ 4 MCP qua mọi đợt update | frontend |
| sync > allow | chạy trong setup, --nen và auto-update |
| allow > matcher | không hỏi quyền lặp lại mỗi lần gọi |
| matcher > ok | mở khóa 10 lượt Grep đúng chuẩn 3 tầng |

Hiện trạng có chứng cứ:
- `C:/Users/admin/.claude/plugins/cache/tdq-local/tdq-workflow/0.89.0/.mcp.json` tồn tại (`True`), nhưng `0.90.0/.mcp.json` và `0.91.0/.mcp.json` đều không tồn tại (`False`).
- `scripts/search_rules.py:868` dùng `LSP = re.compile(r"(^|__|\.)lsp(__|\.)")` không khớp dấu `_` đơn trước `lsp` trong `mcp__plugin_tdq-workflow_lsp__find_symbol`.
- `hooks/hooks.json:76,85,105,116` chỉ khớp `mcp__lsp__.*`.
