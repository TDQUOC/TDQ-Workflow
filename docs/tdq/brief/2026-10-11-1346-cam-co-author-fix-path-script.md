# BRIEF — Nghiêm cấm Co-Authored-By và chuẩn hóa đường dẫn script plugin

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

User:
"okay bây giờ mở request xử lí 2 vấn đề như hình, 1 là nghiêm cấm Co-Authored-By 2 là có rất nhiều khi gọi script sai chỗ"

Kèm hình chụp 2 lỗi thực tế:
1. Model tự ý chèn `Co-Authored-By: Claude Code <noreply@anthropic.com>` vào lệnh `git commit`.
2. Khi chạy trong repo khác (`claudecodeui`), skill gọi lệnh `python3 scripts/tdq_lsp.py check` mà không có tiền tố `${CLAUDE_PLUGIN_ROOT}/`, dẫn đến lỗi `can't open file ...\scripts\tdq_lsp.py: [Errno 2] No such file or directory`.

**Mục tiêu:**
1. Nghiêm cấm tuyệt đối `Co-Authored-By`:
   - Ghi quy tắc cấm `Co-Authored-By` và attribution trailer vào `~/.claude/CLAUDE.md` qua `scripts/tdq_setup.py` (vì instruction của user trong `CLAUDE.md` được ưu tiên ghi đè system reminder của harness).
   - Rào thêm trong conventions (`skills/tdq-conventions/SKILL.md`) và template report (`skills/tdq-build/references/report-template.md`).
2. Chuẩn hóa đường dẫn script trong mọi skill:
   - Quét toàn bộ `skills/` thay thế các lệnh gọi `python3 scripts/...` thành `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/..."` để chạy an toàn trên bất kỳ repo nào của người dùng.

## Hiểu & kiến thức

### Năng lực dùng được
| Kỹ năng / Công cụ | Nguồn | Phán quyết | Lý do |
|---|---|---|---|
| `tdq-setup` | plugin | DÙNG | Cập nhật logic ghim instruction vào `~/.claude/CLAUDE.md` |
| `tdq-conventions` | plugin | DÙNG | Quy tắc Git và quy chuẩn gọi script |
| `tdq-intake`, `tdq-build`, `tdq-plan`, `tdq-setup`, `tdq-check-status` | plugin | DÙNG | Chuẩn hóa đường dẫn `${CLAUDE_PLUGIN_ROOT}` trong các file skill/reference |

### Phân tích chi tiết

#### Vấn đề 1: Tránh chèn Co-Authored-By
- Cơ chế của harness Claude Code: Harness tự động chèn `<system-reminder>` yêu cầu kết thúc commit bằng `Co-Authored-By: Claude Code <noreply@anthropic.com>`. Tuy nhiên, chính harness cũng ghi chú rõ:
  > "the user's own instructions about these lines, such as a CLAUDE.md or memory rule, take precedence over this reminder, but do not add attribution lines this reminder leaves out"
- Như vậy, giải pháp triệt để và hiệu quả nhất là đưa lệnh cấm này vào phần chỉ dẫn cấp người dùng (`~/.claude/CLAUDE.md`) do `scripts/tdq_setup.py` tự động sinh ra và đồng bộ. Khi có luật này, Claude Code sẽ ưu tiên tuân thủ instruction của user và tuyệt đối không thêm dòng `Co-Authored-By`.
- Đồng thời cập nhật `skills/tdq-conventions/SKILL.md` mục 7 và `skills/tdq-build/references/report-template.md` mục 10 để nêu đích danh `Co-Authored-By: Claude Code <noreply@anthropic.com>`.

#### Vấn đề 2: Lỗi đường dẫn khi gọi script từ project khác
- Khi người dùng cài đặt TDQ Workflow làm plugin toàn cục hoặc repo plugin riêng, biến môi trường `${CLAUDE_PLUGIN_ROOT}` trỏ tới thư mục gốc của plugin.
- Trong nhiều skill và reference hiện tại, một số lệnh chỉ ghi là `python3 scripts/tdq_lsp.py` hoặc `python3 scripts/tdq_team.py` thay vì dùng biến môi trường `${CLAUDE_PLUGIN_ROOT}`.
- Khi agent thực thi trong repo của người dùng (ví dụ: `claudecodeui`), thư mục `scripts/` không tồn tại ở repo đó dẫn đến lỗi `[Errno 2] No such file or directory`.
- Cần rà soát và chuẩn hóa toàn bộ các câu lệnh trong `skills/` thành `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/<ten_script>.py"`.

### Lộ trình
- Chạy pipeline deep: `analyze` → `spec` (duyệt spec) → `plan` (duyệt plan) → `implement` → `qc` → `report`.
- Flow 1: Cấm `Co-Authored-By` trong `CLAUDE.md`, conventions và template report.
- Flow 2: Chuẩn hóa toàn bộ đường dẫn script trong thư mục `skills/` có prefix `"${CLAUDE_PLUGIN_ROOT}/"`.
- Flow 3: Kiểm thử toàn diện test suite, đảm bảo 0% drift và token budget hợp lệ.

## Hỏi đáp
- Vấn đề và phạm vi đã rõ ràng qua ảnh chụp thực tế và yêu cầu người dùng.
