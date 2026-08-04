# Request: 2026-08-04-export-claude-setup

## Nguyên văn yêu cầu
> hãy recheck toàn bộ claude code và phân tích để lên spec tạo một bản export đầy đủ có đầy đủ manifest và những dependency + readme đầy đủ chi tiết để có thể setup claude code ở máy khác có thể hoạt động y chang máy này (với những dependency cần cài đặt online thì kèm hướng dẫn, những cái local thì tạo clone trong folder export luôn)

## Cách hiểu đầu tiên
- Mục tiêu: rà soát toàn bộ cấu hình Claude Code hiện tại trên máy này (global
  `~/.claude/` + project-level `.claude/` trong các repo đang dùng, đặc biệt
  `TDQWorkflow`) rồi lên **spec** (chưa code) cho một quy trình/script export
  đóng gói đầy đủ để clone sang máy khác và Claude Code hoạt động **y hệt**.
- Phạm vi đoán (cần xác nhận ở vòng interview):
  - "Toàn bộ Claude Code" gồm: settings.json (global + project + local),
    plugins đã cài (marketplace nào, plugin nào, phiên bản), MCP server config
    (bao gồm cả server cần API key), agents/commands/skills custom, hooks,
    keybindings, statusline, CLAUDE.md (global + project), memory
    (`.remember/`), plugin-tiers.json, và các project-level `.claude/`
    (không chỉ TDQWorkflow, hay chỉ project hiện tại?).
  - "Manifest đầy đủ" = liệt kê version, nguồn cài (marketplace URL/npm/pip),
    checksum? hay chỉ danh sách tên+version+nguồn.
  - "Dependency cài online" = các CLI ngoài (node, python, gh, docker...),
    MCP server cần network, marketplace plugin cần `claude plugin marketplace
    add` — sẽ liệt kê kèm hướng dẫn cài, không tự động cài.
  - "Local thì clone luôn" = các thứ nằm trên máy (repo project, custom
    scripts, plugin cài dev-mode từ local path...) — copy nguyên file vào
    folder export để máy kia có sẵn, không cần tải lại.
  - Output cuối: có phải là script thực thi (export.sh / import.sh) hay chỉ
    tài liệu spec mô tả cấu trúc export + README hướng dẫn thủ công? (cần hỏi)
  - Có cần xử lý secret/API key trong config không (loại trừ, hay để user tự
    điền lại)?
- Việc này ảnh hưởng toàn hệ thống Claude Code, không chỉ 1 file/module nhỏ,
  có nhiều ẩn số cần recheck kỹ + hỏi user nhiều điểm quyết định → đề xuất lane
  **full**.
