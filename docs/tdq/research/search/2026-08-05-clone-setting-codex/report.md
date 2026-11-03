# Deep search report — 2026-08-05-clone-setting-codex

- Agent: 4 · finding sau dedup: 12 · route hỏng: 0
- Route KHÔNG có finding (rỗng/not_found): scout: clone-setting-to-codex Codex CLI config structure

| # | Claim | Nguồn | Route xác nhận | Score |
|---|---|---|---|---|
| 1 | Từ Codex 0.138.0 trở đi, Codex khuyến nghị sử dụng Permission Profiles với allow | https://developers.openai.com/codex/enterprise/managed-configuration | scout: enterprise MCP allowlist identity matching, permission profiles requirements.toml thay sandbox_mode Codex (1) | 10 |
| 2 | Chuẩn SKILL.md là một open standard (Agent Skills) cho phép đóng gói hướng dẫn,  | https://agentskills.io/home | Codex Agent Skills official docs SKILL.md tương đương Claude Code skills (1) | 10 |
| 3 | OpenAI Codex CLI sử dụng chuẩn Agent Skill chính thức với cấu trúc thư mục chứa  | https://agentskills.io/specification | Codex Agent Skills official docs SKILL.md tương đương Claude Code skills (1) | 10 |
| 4 | Field sandbox_mode cũ vẫn hỗ trợ tương thích ngược nhưng không hợp nhất (compose | https://developers.openai.com/codex/permissions | permission profiles requirements.toml thay sandbox_mode Codex (1) | 10 |
| 5 | config.toml có khối [hooks] chính thức dùng cùng schema event với hooks.json. | https://learn.chatgpt.com/docs/config-file/config-reference | scout: config.toml hooks key chính thức, scout: AGENTS.md discovery config keys, scout: hooks event list chính thức (1) | 9 |
| 6 | Plugin Codex có manifest bắt buộc .codex-plugin/plugin.json, kèm skills/, hooks/ | https://developers.openai.com/plugins/build/plugins | scout: plugin manifest structure chính thức, scout: plugin hooks cần user trust (1) | 9 |
| 7 | Top-level table trong config.toml phải là mcp_servers (snake_case), không phải m | https://github.com/openai/codex/commit/2e95e5602d5736ea5b3a41e89c20f9db0b820282 | scout: mcp_servers TOML key format chính thức (1) | 9 |
| 8 | Codex CLI hỗ trợ khai báo hooks thông qua file hooks.json hoặc khối inline [hook | https://developers.openai.com/codex | hooks.json schema field-by-field matcher command additionalContext (1) | 9 |
| 9 | config.toml chính thức hỗ trợ approval_policy, sandbox_mode, mcp_servers.*, feat | https://github.com/openai/codex/issues/17012 | scout: config.toml schema chính thức (1) | 8 |
| 10 | Global scope AGENTS.override.md/AGENTS.md tại ~/.codex/, project scope đi từ git | https://www.verdent.ai/guides/codex-agents-md-explained | scout: AGENTS.md discovery order chi tiết (1) | 6 |

(Chỉ hiện top 10/12 — đủ trong merged.json)

Sinh lúc: 2026-08-05T19:57:22+07:00 · rank tất định bằng code (route xác nhận → URL sống → có quote → score → thứ tự route).
