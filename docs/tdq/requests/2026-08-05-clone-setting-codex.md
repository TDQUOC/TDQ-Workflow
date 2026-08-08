# Request: clone-setting-codex

## Nguyên văn yêu cầu
> hi tôi đang muốn bạn brainstoming để phân tihcs, search đẻ phân tích tạo skill
> clone-setting-to-codex để clone all setting, config, kill (skill), plugin to codex

## Cách hiểu đầu tiên
- User muốn có một **skill mới** tên `clone-setting-to-codex` trong hệ Claude Code
  plugin của TDQWorkflow (hoặc ~/.claude), dùng để **đồng bộ/clone** toàn bộ:
  settings (settings.json, keybindings, permissions...), config (CLAUDE.md, MCP
  server config...), skills, và plugins — từ Claude Code sang **Codex CLI** (OpenAI
  Codex), một AI coding CLI khác đã được TDQ dùng làm "external engine" (thấy
  `codex-runner` agent, `external_task.py`).
- Trước khi thiết kế skill: cần **research** cấu trúc config/skill/plugin của Codex
  CLI (Codex có khái niệm tương đương "skill"/"plugin" không? format config ở đâu:
  `~/.codex/...`? AGENTS.md? custom instructions?) để biết cái gì map được, cái gì
  không map được 1:1.

## Phạm vi đoán (chưa chốt)
- Nguồn: toàn bộ `~/.claude/` (settings.json, CLAUDE.md, skills, plugins, MCP
  config, keybindings...) + có thể cả cấu hình project-level (`.claude/` trong repo).
- Đích: cấu trúc tương ứng bên Codex CLI — **cần research để biết chính xác** Codex
  hỗ trợ gì (system prompt/AGENTS.md, MCP config, custom tool/plugin equivalent...).
- Kết quả mong đợi: một **skill** (không phải script một lần) để lặp lại việc clone
  này khi cần đồng bộ.

## Chỗ chưa rõ (cần interview/research)
1. "Clone to codex" nghĩa là port 1 lần, hay là skill chạy lại được nhiều lần
   (sync liên tục)?
2. Phạm vi nguồn: chỉ `~/.claude/*` global, hay cả project-level `.claude/`?
3. Cần xử lý phần không map được (vd MCP server Claude-only, hook Claude-only)
   như thế nào — bỏ qua, cảnh báo, hay convert gần đúng?
4. Codex CLI đang được cài ở đâu trên máy user, đã có cấu hình sẵn chưa (để biết
   có ghi đè hay merge)?
