# BRIEF — Tự động cập nhật setup khi phát hiện version mới qua SessionStart

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

User:
"Okay mở request handle thêm hook là chekc nếu có update version mới thì sẽ auto update những phần có trong setup với dạng by pass permission để đảm bảo update đc dependecy và intruction cho những người đã cỉa bản cũ mà ko cần phải chạy thủ công skill setup lại aps dụng cho cả claude và codex và pump version và commit"

**Mục tiêu:**
Trong hook `SessionStart` (cho Claude Code và cả Codex), tự động kiểm tra xem plugin có phiên bản mới hơn phiên bản đã chạy setup lần trước hay không.
Nếu phát hiện version mới (hoặc lần đầu):
- Tự động chạy cập nhật những phần trong `tdq_setup.py` (cập nhật instruction `CLAUDE.md`, khai báo MCP server / hook cho Codex, cập nhật dependency / servers cần thiết).
- Lưu lại mốc phiên bản đã setup tại `docs/tdq/.tdq-version-stamp.json` hoặc file cache tương ứng.
- Hoạt động tự động, êm dịu, không đòi hỏi user phải tự chạy lại thủ công lệnh setup.
- Sau khi hoàn thành, pump version và commit.

## Hiểu & kiến thức
- Hiện trạng: Khi plugin nâng version (ví dụ từ 0.60 lên 0.61 hay 0.62), người dùng đã cài bản cũ khi pull bản mới về nếu không chạy `tdq_setup.py` thì instruction trong `~/.claude/CLAUDE.md` hoặc cấu hình MCP/hook Codex vẫn là bản cũ.
- Giải pháp:
  1. Trong `hooks/scripts/session_start.py` (chạy trên Claude Code) và logic tương đương cho Codex (thông qua `tdq_setup.py` / `session_start`), so sánh version hiện tại của plugin (đọc từ `plugin.json` của `.claude-plugin` hoặc `.codex-plugin`) với version đã ghi nhận lần trước trong stamp.
  2. Khi version mới hơn $\rightarrow$ tự động chạy các bước setup cần thiết (hoặc gọi `tdq_setup.py` đồng bộ instruction và cấu hình không tương tác) và cập nhật version stamp.
  3. Hoàn tất kiểm thử, cập nhật CHANGELOG, bump version và commit.

## Hỏi đáp
- User đã chốt yêu cầu và lệnh duyệt nhanh.
