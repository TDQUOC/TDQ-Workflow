# BRIEF — Kiểm tương thích bộ workflow với Claude Code / Codex / Antigravity

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay bây giờ tôi muốn bạn mở deep analysis và phân tích xem bộ workflow này có đảm bảo tương
> thích fully với claude code / codex / antigravity chưa? nếu chưa thì resreach version mới nhất
> cảu mỗi cái thì tôi cần update gì để nó hoạt động đúng

Đọc lần đầu: user muốn một bản phân tích tương thích cho 3 host, đối chiếu với tài liệu bản mới
nhất của từng host, và một danh sách việc cần sửa. Phạm vi đoán: 3 bundle portable +
`.claude-plugin/` + `hooks/hooks.json` + `scripts/build_portable.py`. Chỗ chưa rõ: user muốn dừng
ở BÁO CÁO phân tích, hay muốn đi tiếp spec/plan để sửa luôn.

## Hiểu & kiến thức

### Nguồn đã tra (2026-09-03)

| # | Nguồn | Dùng để kết luận điều gì |
|---|---|---|
| N1 | <https://learn.chatgpt.com/docs/hooks> | Codex: khoá tính năng đổi `codex_hooks` → `hooks`; danh sách 12 event; luật trust của `.codex/` |
| N2 | <https://learn.chatgpt.com/docs/config-file/config-reference> | Codex: `mcp_servers.<n>.env` là map giá trị, `env_vars` là mảng tên biến |
| N3 | <https://antigravity.google/docs/cli/plugins> | agy: cấu trúc plugin chuẩn `~/.gemini/antigravity-cli/plugins/<tên>/` + `plugin.json` bắt buộc |
| N4 | <https://antigravity.google/changelog> | agy: bug ghi hooks sai thư mục ĐÃ sửa — đường chính thức là `~/.gemini/config/hooks.json` |
| N5 | <https://medium.com/google-cloud/a-developers-guide-to-agent-hooks-in-antigravity-cli-4c1440febd11> | agy: hợp đồng PreToolUse dùng `allow_tool: false`; `command` phải là đường dẫn TUYỆT ĐỐI; danh sách tên tool để matcher |
| N6 | <https://github.com/manaflow-ai/cmux/issues/5358> | agy: payload sai (kể cả `{}`) → deny MỌI tool call, lỗi `invalid_args` |
| N7 | <https://code.claude.com/docs/en/plugins-reference> | Claude Code: schema `plugin.json` hiện tại, `${CLAUDE_PLUGIN_DATA}`, `userConfig`, hook type mới |

### Kết luận theo host

- **Claude Code — tương thích, không có lỗi chặn.** `plugin.json`, `marketplace.json`,
  `hooks/hooks.json` đều đúng schema hiện hành; 5 event đang dùng vẫn được hỗ trợ.
  Cơ hội (không bắt buộc): `userConfig` cho Tavily key thay vì biến môi trường,
  `${CLAUDE_PLUGIN_DATA}` cho state sống qua update, `displayName`/`$schema`.
- **Codex — chạy được nhưng có 2 điểm hỏng thật.** (a) `.codex/config.toml` sinh ra không có
  `[features] hooks = true`, nên trên bản còn mặc định tắt thì toàn bộ hook im lặng không chạy;
  (b) `env_vars` đang viết đúng kiểu mảng tên biến — hợp lệ, nhưng README không nói người dùng
  phải tự export biến, và không nhắc `.codex/` chỉ nạp khi project được trust.
- **Antigravity — rủi ro cao nhất, có 1 lỗi gần như chắc chắn làm hỏng session.**
  (a) `command` trong `config/hooks.json` viết `python3 "~/.gemini/..."` — dấu `~` nằm trong nháy
  kép KHÔNG được shell bung, và tài liệu agy đòi đường dẫn tuyệt đối; (b) payload deny đang dùng
  `{"decision":"deny"}` trong khi hợp đồng tài liệu hoá là `allow_tool: false`; (c) bundle vẫn
  rải config ra 6 đường dẫn đoán, trong khi agy nay đã có định dạng plugin chuẩn.

## Hỏi đáp

Chưa có — câu hỏi phạm vi đang chờ user trả lời ở chat.
