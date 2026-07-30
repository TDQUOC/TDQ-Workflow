# RESEARCH — external-agent-mode

Ngày: 2026-07-30 · Engine search: tavily-primary (7 truy vấn, 2 đợt: 21:13 khả thi + 21:50 chi tiết)

## Đợt 1 (21:13) — khả thi tổng quát

### Q1: "use OpenAI Codex CLI as subagent inside Claude Code delegate tasks"
- Nguồn: github.com/openai/codex-plugin-cc · community.openai.com (Introducing Codex Plugin
  for Claude Code) · medium @markchen69 · simonwillison.net/2026/Mar/16/codex-subagents
- Rút ra: OpenAI có plugin CHÍNH CHỦ cho Claude Code: `/codex:review`,
  `/codex:adversarial-review`, `/codex:rescue|transfer|status|result|cancel`; subagent
  `codex:codex-rescue` Claude gọi tự chủ được; chạy qua Codex CLI + app server local,
  dùng chung auth ChatGPT; hỗ trợ `--background/--wait/--resume`.

### Q2: "codex exec non-interactive headless"
- Nguồn: learn.chatgpt.com/docs/non-interactive-mode (chính chủ) · developersdigest.tech
- Rút ra: `codex exec "<task>"` chạy headless; `--json` (JSONL); mặc định sandbox
  read-only → cần `--sandbox workspace-write` để sửa file; `--full-auto` đã deprecated;
  resume session được; stdout = câu trả lời cuối, stderr = tiến trình.

### Q3: "Google Antigravity CLI headless"
- Nguồn: antigravity.google/docs/cli/headless (chính chủ) · realpython.com/antigravity-cli
- Rút ra: `agy -p "<task>" --output-format json|stream-json --json-schema <schema|file>
  --print-timeout 10m --model <slug> --effort low|med|high --agent <tên> --continue |
  --conversation <id> --dangerously-skip-permissions`. Antigravity CLI thay Gemini CLI
  (6/2026), config ở `~/.gemini/`. KHÔNG có plugin chính chủ cho Claude Code.

### Q4: "codex mcp-server Claude Code"
- Nguồn: github.com/cexll/codex-mcp-server · reddit r/ClaudeCode
- Rút ra: hướng MCP khả dụng (`codex mcp-server` built-in) nhưng cộng đồng phản hồi
  CHẬM hơn subagent thuần; pattern được khen: custom subagent .md hướng dẫn gọi CLI
  qua Bash với đủ flag.

## Đợt 2 (21:50) — chi tiết cho build

### Q5: cách cài codex-plugin-cc
- Nguồn: README chính chủ github.com/openai/codex-plugin-cc
- Rút ra: `/plugin marketplace add openai/codex-plugin-cc` → `/plugin install
  codex@openai-codex` → `/reload-plugins` → `/codex:setup`. Yêu cầu Node ≥18.18,
  ChatGPT sub hoặc API key. (Slash command = user gõ, Claude không tự chạy được.)

### Q6: model slug Codex hiện hành
- Nguồn: verdent.ai/guides/gpt-5-codex-model-names-explained · reddit r/LLMDevs
  (đợt retire 23/07/2026) · blakecrosley.com/blog/codex-vs-claude-code-2026 ·
  aibuilderclub.com/blog/codex-cli-guide-2026
- Rút ra: sau 23/07/2026 các slug gpt-5.x-codex cũ retire; slug dùng được:
  `gpt-5.5` (mặc định ChatGPT-auth, đắt nhất), `gpt-5.4`, `gpt-5.4-mini` (rẻ/nhanh,
  hợp subagent), `gpt-5-codex` (coding chuyên, 400K ctx — API). LƯU Ý: đăng nhập
  ChatGPT bị giới hạn model (nhiều forum báo "model not supported with ChatGPT
  account") → phải THỬ THẬT trên máy trước khi chốt danh sách. Có `--oss` cho model
  local. Reasoning effort chỉnh qua config `model_reasoning_effort`.

### Q7: thiết kế prompt cho model cấp thấp/context ngắn
- Nguồn: developers.openai.com/api/docs/guides/prompt-engineering · cộng đồng
- Rút ra (chắt lọc): (1) schema output ép cứng — cả 2 CLI đều hỗ trợ JSON schema
  (`--json-schema` của agy; `--output-schema` file của codex exec) → parse máy, không
  đoán; (2) task nhỏ, một mục tiêu, kể tên file cụ thể, không bắt tự khám phá repo;
  (3) few-shot 1 ví dụ report chuẩn; (4) vai + giới hạn "không làm gì ngoài task";
  (5) retry có giới hạn khi output sai schema.

## Đo thực tế trên máy (21:50)

- `codex-cli 0.146.0-alpha.3.1` (ChatGPT.app) — `codex login status` = "Logged in
  using ChatGPT". Flag: `-m/--model`, `-s read-only|workspace-write|danger-full-access`,
  `--oss`, schema file cho câu trả lời cuối.
- `agy 1.1.8` (~/.local/bin) — đã đăng nhập. `agy models`: gemini-3.6-flash-{high,
  medium,low}, gemini-3.5-flash-{high,medium,low}, gemini-3.1-pro-{high,low},
  claude-sonnet-4-6, claude-opus-4-6-thinking, gpt-oss-120b-medium (11 slug).
