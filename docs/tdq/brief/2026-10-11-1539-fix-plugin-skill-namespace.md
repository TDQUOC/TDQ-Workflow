# BRIEF — Khắc phục lỗi Unknown skill tdq-intake do thiếu namespace plugin

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

User:
Báo Cáo Điều Tra: Nguyên Nhân Lỗi `Unknown skill: tdq-intake`
Khi Claude gọi tool `Skill` với tham số `{"skill": "tdq-intake", "args": ""}` trả về `Error: Unknown skill: tdq-intake`.
Nguyên nhân: Trong Claude Code và `@anthropic-ai/claude-agent-sdk`, các skill đi kèm plugin cài đặt qua marketplace hoặc plugin cục bộ được định danh bằng namespace `plugin:skill` (cụ thể là `tdq-workflow:tdq-intake`, `tdq-workflow:tdq-spec`, v.v.).
Trong khi đó, câu chữ trong `~/.claude/CLAUDE.md`, `scripts/tdq_setup.py` và hook `prompt_context.py` lại viết ngắn gọn là `tdq-intake`. Model máy móc gọi `tdq-intake` dẫn đến lỗi `Unknown skill`.

**Mục tiêu:**
- Chuẩn hóa chỉ dẫn trong `KHOI_HUONG_DAN` (`scripts/tdq_setup.py`, `~/.claude/CLAUDE.md`), `prompt_context.py` và các tài liệu liên quan: nêu rõ tên gọi skill đầy đủ theo namespace plugin `tdq-workflow:<skill>` (hoặc `<skill>` nếu cài cục bộ), hướng dẫn agent tra cứu đúng tên skill từ danh sách khả dụng trước khi gọi.
- Hỗ trợ và hướng dẫn giải pháp auto-alias / fallback nếu có thể.

## Hiểu & kiến thức

### Năng lực dùng được
| Kỹ năng / Công cụ | Nguồn | Phán quyết | Lý do |
|---|---|---|---|
| `tdq-setup` | plugin:tdq-workflow | DÙNG | Cập nhật logic ghim instruction vào `~/.claude/CLAUDE.md` |
| `tdq-conventions` | plugin:tdq-workflow | DÙNG | Quy tắc gọi skill và định danh namespace |
| Đã xét 15 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

### Phân tích chi tiết

#### 1. Cơ chế đăng ký Skill của Claude Code / Claude Agent SDK
- Khi cài đặt plugin `tdq-workflow` qua marketplace hoặc cục bộ, Claude Code tự động nạp các skill từ thư mục `skills/` và gán namespace dạng `<plugin-name>:<skill-name>`:
  - `tdq-workflow:tdq-intake`
  - `tdq-workflow:tdq-spec`
  - `tdq-workflow:tdq-plan`
  - `tdq-workflow:tdq-build`
  - `tdq-workflow:tdq-status`
  - `tdq-workflow:tdq-check-status`
  - `tdq-workflow:tdq-lean`
  - `tdq-workflow:tdq-conventions`
  - `tdq-workflow:tdq-setup`
- Trong system prompt của Claude Code, định nghĩa tool `Skill` quy định rõ:
  > `skill`: exact name from the listing, no leading slash. Plugin skills use `plugin:skill`.
  > Only names from the listing (or that the user typed explicitly) are valid. Do not guess names.

#### 2. Nguyên nhân lỗi `Unknown skill: tdq-intake`
- `KHOI_HUONG_DAN` trong `scripts/tdq_setup.py` (được đồng bộ vào `~/.claude/CLAUDE.md`) chỉ ghi:
  `Mọi yêu cầu mới từ người dùng BẮT BUỘC phải mở bằng skill tdq-intake...`
- Hook `prompt_context.py` nhắc:
  `[TDQ:INTAKE] No request is open — unless this prompt belongs to an intake round already running, open tdq-intake before doing anything else.`
- Vì thế, model gọi `Skill({ skill: "tdq-intake" })` thay vì `Skill({ skill: "tdq-workflow:tdq-intake" })`. Hệ thống Claude Code tra cứu danh sách skill và báo lỗi `Error: Unknown skill: tdq-intake`.

#### 3. Giải pháp khắc phục
1. **Trong `scripts/tdq_setup.py` (`KHOI_HUONG_DAN`) và `~/.claude/CLAUDE.md`:**
   Cập nhật câu chữ thành:
   `Mọi yêu cầu mới từ người dùng BẮT BUỘC phải mở bằng skill tdq-workflow:tdq-intake (hoặc tdq-intake nếu không dùng plugin) và chạy theo pipeline của TDQ Workflow (quick hoặc full)...`
2. **Trong hook `hooks/scripts/prompt_context.py`:**
   Cập nhật dòng nhắc `[TDQ:INTAKE]` thành:
   `[TDQ:INTAKE] No request is open — unless this prompt belongs to an intake round already running, open tdq-workflow:tdq-intake (or tdq-intake).`
   Đảm bảo độ dài chuỗi $\le 160$ ký tự để thỏa mãn ngân sách của `tests/test_prompt_context.py`.
3. **Trong tài liệu hướng dẫn (`docs/notes/user-level-install.md`):**
   Cập nhật các mẫu câu tham chiếu skill có tiền tố `tdq-workflow:`.
4. **Kiểm thử và xác nhận:**
   Chạy toàn bộ unit test, kiểm tra độ dài chuỗi nhắc nhở và tính nhất quán tài liệu.

### Lộ trình
- Chạy pipeline deep: `analyze` → `spec` (duyệt spec) → `plan` (duyệt plan) → `implement` → `qc` → `report`.
- Flow 1: Cập nhật `KHOI_HUONG_DAN` trong `scripts/tdq_setup.py`, đồng bộ `~/.claude/CLAUDE.md` và `docs/notes/user-level-install.md`.
- Flow 2: Cập nhật dòng nhắc `[TDQ:INTAKE]` trong `hooks/scripts/prompt_context.py` và cập nhật test nếu cần.
- Flow 3: Kiểm thử toàn diện test suite, token budget và mốc luật 0% drift.

## Hỏi đáp
- Vấn đề và nguyên nhân gốc rễ đã được điều tra và xác định chính xác 100%.
