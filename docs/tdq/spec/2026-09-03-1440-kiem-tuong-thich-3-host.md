# SPEC — Sửa tương thích bộ workflow với Claude Code 2.x / Codex 0.149 / Antigravity 1.1.11

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Brief: ../brief/2026-09-03-1440-kiem-tuong-thich-3-host.md · Phiên bản: 1

## 1. Mục tiêu & phạm vi

Đưa 3 đường cài của repo về đúng cơ chế THẬT của bản host đang chạy trên máy này, kiểm bằng
hiệu ứng chứ không bằng tài liệu: `codex-cli 0.149.0-alpha.4.3` và `agy 1.1.11`.

**Trong phạm vi**
- `antigravity_portable/` — dựng lại theo layout agy 1.1.11 thật.
- `portable_codex/` — bổ sung bước trust hook và bước export biến môi trường.
- `.claude-plugin/plugin.json` — thêm `userConfig`, `displayName`; state dùng `${CLAUDE_PLUGIN_DATA}`.
- `scripts/build_portable.py` — nơi sinh ra cả 3 bundle.
- `scripts/tdq_checkportable.py` — luật `check` phải bắt được đúng layout mới.

**Ngoài phạm vi**
- Không đổi logic workflow (phase, gate, luật duyệt).
- Không xoay Tavily key đang lộ trong lịch sử git.
- Không đụng `portable_claude/` ngoài phần `${CLAUDE_PLUGIN_DATA}`.

## 2. Đầu ra cụ thể

| # | Đầu ra | Đo bằng |
|---|---|---|
| O1 | `antigravity_portable/` sinh ra theo layout plugin thật của agy | `agy plugin list` in ra `tdq-workflow` |
| O2 | Bundle agy không còn ghi đè `~/.gemini/antigravity-cli/settings.json` | `grep -c settings.json` trong README = 0 ở mục cài |
| O3 | `portable_codex/README.md` có bước trust hook theo hash | có mục `## Trust hook` + lệnh `/hooks` |
| O4 | `plugin.json` khai `userConfig` cho 2 biến Tavily và `displayName` | `claude plugin validate .` exit 0 |
| O5 | `tdq_checkportable.py check` hiểu layout agy mới | chạy trên `antigravity_portable` ra `CLEAN` |
| O6 | Test khoá 5 điểm tương thích trên | bộ test tương thích host chạy xanh |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc |
|---|---|---|
| Bộ sinh bundle | `scripts/build_portable.py` | đọc `skills/`, `hooks/`, `scripts/`, `.claude-plugin/plugin.json` |
| Bộ kiểm bundle | `scripts/tdq_checkportable.py` | đọc `<bundle>/manifest.json` do bộ sinh ghi |
| Bundle agy | `antigravity_portable/**` | sinh ra hoàn toàn từ bộ sinh, không sửa tay |
| Bundle codex | `portable_codex/**` | như trên |
| Kê khai plugin | `.claude-plugin/plugin.json` | Claude Code đọc trực tiếp |

Ranh giới cứng: mọi file trong 3 thư mục bundle là ĐẦU RA. Sửa phải sửa ở bộ sinh rồi dựng lại.

## 3. Cách tiếp cận & lý do

Ba phát hiện kiểm bằng hiệu ứng trên chính máy này đảo ngược một phần giả định của brief:

1. **Codex 0.149 đã bật hook mặc định.** `~/.codex/config.toml` không có khoá `hooks` trong
   `[features]`, nhưng vẫn có hàng chục mục `[hooks.state."...:pre_tool_use:0:0"]`. Vậy việc
   thêm `[features] hooks = true` là thừa. Rào thật là **trust theo hash**: mỗi hook chỉ chạy
   sau khi được duyệt, và `trusted_hash` ghim NỘI DUNG — nên mỗi lần dựng lại bundle là mất
   trust, phải duyệt lại. README hiện không nói gì về việc này.
2. **Layout agy trong bundle sai hoàn toàn với agy 1.1.11.** Không một đường nào trong 6 đường
   bundle đang rải là có thật trên máy: `~/.gemini/antigravity-cli/{skills,plugins}`,
   `~/.gemini/skills`, `~/.gemini/antigravity/skills` đều không tồn tại. Layout thật là
   `~/.gemini/config/plugins/<tên>/{plugin.json, skills/}` + bật trong
   `~/.gemini/config/config.json` khoá `plugins.<tên>.enabled`, thêm thư mục skill ngoài qua
   `~/.gemini/config/skills.json`.
3. **`settings.json` của bundle agy là file NGUY HIỂM.** Bundle bảo copy đè
   `~/.gemini/antigravity-cli/settings.json`, nhưng file thật đang giữ `model`, `colorScheme`,
   `trustedWorkspaces` của người dùng và KHÔNG có mục `permissions` nào. Copy đè là mất cấu hình
   người dùng mà chẳng được thêm hàng rào nào.

Vì vậy cách làm: đóng gói agy theo đúng chuẩn plugin (bỏ hẳn kiểu rải đoán), bỏ file
`settings.json` khỏi bundle, và chuyển phần Codex từ "sửa config" sang "viết đúng thủ tục trust".

## 3b. Năng lực & công cụ

| Năng lực cần | Có sẵn? | Phán quyết | Ghi chú |
|---|---|---|---|
| Sinh bundle portable | `scripts/build_portable.py` | DÙNG | thêm nhánh layout agy mới |
| Kiểm bundle | `scripts/tdq_checkportable.py` | DÙNG | mở rộng luật cho layout mới |
| Kiểm bằng hiệu ứng trên host thật | `codex`, `agy` có trên máy | DÙNG | chỉ chạy lệnh ĐỌC (`plugin list`, `--version`) |
| Kê khai plugin Claude | `claude plugin validate` | DÙNG | cổng kiểm O4 |
| Lint tài liệu | `scripts/doc_lint.py` | DÙNG | mọi file `.md` sửa |

## 4. Yêu cầu thường trực

- Log service bật sẵn: mọi script sửa giữ nguyên khuôn log `[timestamp] mức · nội dung`.
- Không placeholder, không bịa đường dẫn — mọi đường dẫn phải đã kiểm bằng `ls` trên máy này.
- Mỗi phần sửa có unit test riêng.
- Không bao giờ in giá trị API key; chỉ in TÊN biến.

## 5. Ràng buộc & rủi ro

- **Ràng buộc kiến trúc 1:** không sửa tay file trong 3 thư mục bundle; sửa ở bộ sinh.
- **Ràng buộc kiến trúc 2:** không ghi ra ngoài repo. Lệnh cài agy/codex chỉ được IN RA cho
  người dùng chạy, trừ `tdq_checkportable.py --trust` vốn đã có sẵn cơ chế backup.
- **Rủi ro 1:** layout agy đọc được từ MỘT máy. Bản agy khác có thể khác. Giảm bằng cách để
  README nêu cách tự kiểm (`agy plugin list`, `/hooks`) thay vì khẳng định cứng.
- **Rủi ro 2:** hợp đồng payload PreToolUse của agy (`allow_tool: false` so với
  `decision: "deny"`) chưa được tài liệu chính thức của Google xác nhận, chỉ có nguồn bên thứ ba
  và một issue thực địa. Giảm bằng cách phát cả hai khoá trong cùng một payload deny.
- **Rủi ro 3:** mốc đỏ có sẵn 100 test. Không được tăng.

## 6. QC & Definition of Done

- [ ] `antigravity_portable/` có `plugin.json` hợp lệ và cây `skills/` đúng chuẩn agy.
- [ ] README agy hướng dẫn đúng 3 đường: thư mục plugin, bật trong `config.json`, `skills.json`.
- [ ] Bundle agy không còn file `config/settings.json`.
- [ ] Payload deny của `agy_pretooluse_gate.py` chứa cả `allow_tool` và `decision`.
- [ ] Mọi `command` trong hooks agy là đường dẫn tuyệt đối đã bung `~`.
- [ ] `portable_codex/README.md` có mục trust hook và mục export biến môi trường.
- [ ] `plugin.json` có `displayName` + `userConfig`; `claude plugin validate` exit 0.
- [ ] `tdq_checkportable.py check` ra `CLEAN` trên cả 3 bundle.
- [ ] Bộ test tương thích host chạy xanh.
- [ ] `pytest -q` không quá 100 đỏ.
- [ ] `doc_lint.py` exit 0 trên mọi file `.md` đã sửa.

## 7. Câu hỏi mở

Không còn.
