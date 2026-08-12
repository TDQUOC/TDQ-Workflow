## Nguyên văn

User hỏi: "hi hãy check repo này cho tôi và cho tôi biết liệu có thể install workflow này ở
project-level và tạo instruction ở project level để mà hướng claude code/codex hoạt động
theo workflow này không? expect turn này cần phân tích, chưa chỉnh sửa gì"

Sau khi phân tích (xem turn trước), đưa 2 hướng:
- A: chỉ Claude Code
- B: cả Claude Code lẫn Codex

User chọn **B**.

Mục tiêu: làm cho plugin `tdq-workflow` dùng được ở **project-level** (không cần user-level
install) cho CẢ hai harness:
1. Claude Code — đã có sẵn đường (`--plugin-dir` hoặc marketplace scope project + block
   instruction trong `docs/notes/user-level-install.md` mục 3 dán vào `CLAUDE.md` root
   project đích) → việc còn lại chủ yếu là viết lại tài liệu cho đúng scope "project" thay
   vì "user-level" (tài liệu hiện tại thiên về user-level).
2. Codex — **chưa có đường**: thư mục `portable/` (AGENTS.md + portable/workflow/) đã bị
   xoá ở bản 0.10.0 (do gỡ mode `external`). Mục 4 của `user-level-install.md` đang trỏ tới
   thư mục không còn tồn tại → tài liệu lỗi thời. Cần dựng lại bản tương đương cho Codex:
   Codex dùng `AGENTS.md` làm file instruction gốc (tương tự CLAUDE.md), không có hook nên
   không có gate/nhắc `[TDQ:*]` — chỉ có thể dựa vào instruction chủ động đọc
   `scripts/tdq_state.py next` đầu mỗi turn.

Phạm vi đoán ban đầu (cần chốt ở Phần B):
- Có viết lại toàn bộ nội dung skill (`tdq-intake`, `tdq-spec`, ...) dưới dạng file phẳng
  cho Codex, hay chỉ dịch phần cốt lõi (giao thức next/approve/log) vào 1 AGENTS.md?
- Đặt ở đâu trong repo: khôi phục `portable/` hay đặt path khác?
- Cách đồng bộ nội dung để không lệch giữa skills/ (Claude Code) và bản Codex — file
  generate tự động hay tay?
- `scripts/tdq_state.py` có phụ thuộc gì vào biến môi trường riêng của Claude Code
  (`${CLAUDE_PLUGIN_ROOT}`) cần thay bằng path tương đối/tuyệt đối cho Codex không?

Chỗ chưa rõ: cỡ việc (nhỏ/quick hay full) — đây có vẻ là việc full vì đụng thiết kế lại
một phần kiến trúc dự án (khôi phục cơ chế đa-harness đã bị gỡ), ảnh hưởng nhiều file, cần
test đồng bộ (giống `test_portable_sync.py` cũ).

## Hiểu & kiến thức

(điền ở Phần B)

## Hỏi đáp

(điền ở Phần B)
