# Nợ phụ thuộc

Sinh bởi `scripts/tdq_setup.py`. Mỗi dòng là một món setup KHÔNG tự xử lý được — vì lệnh của nó
nằm ngoài danh sách đã khai, vì nó cần quyền của người, hoặc vì nó hỏng theo cách máy không đoán
được. Xử xong thì xoá dòng đó đi; file này chỉ có nghĩa khi nó rỗng dần.

Ghi kèm tên máy vì một món có thể thiếu trên máy này mà đủ trên máy khác.

- 2026-09-28 · DESKTOP-QNBEKDT · bản mẫu instruction trỏ tới skill `mem0-memory` — máy này không có nó
- 2026-09-28 · DESKTOP-QNBEKDT · scripts/tdq_setup.py + tdq_no.py: 122 dòng chú thích/chuỗi in ra còn tiếng Việt, lệch quyết định ngôn ngữ 3 tầng 2026-08-22 (tầng 1-2 phải tiếng Anh). Không có test nào gác i18n trên scripts/, và repo đang lẫn sẵn: tdq_lsp.py 161 dòng, tdq_state.py 42 dòng. Cần một request dọn chung, không dọn lẻ một file.
- 2026-10-02 · DESKTOP-QNBEKDT · reindex lumen không xong ở bước kết turn: over 120s
- 2026-10-07 · DESKTOP-QNBEKDT · bậc 5 (sức khoẻ lumen): lệnh nằm ngoài danh sách phụ thuộc đã khai — `lumen index C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow`
- 2026-10-07 · DESKTOP-QNBEKDT · bậc 8 (đồ thị graphify): lệnh có ký tự của shell — không chạy chuỗi ghép, hãy khai từng lệnh một — `cd C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow && graphify extract . --code-only`
- 2026-10-07 · DESKTOP-QNBEKDT · tầng LSP không trả lời được: agent-lsp doctor
- 2026-10-07 · DESKTOP-QNBEKDT · tầng lumen không trả lời được: Error: load config: config: servers[0]: host is required
- 2026-10-07 · DESKTOP-QNBEKDT · tầng lumen không trả lời được: tree-sitter failed to allocate 4640392 bytes
