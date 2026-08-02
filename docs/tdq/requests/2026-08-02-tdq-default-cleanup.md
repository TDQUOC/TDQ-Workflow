# REQUEST — 2026-08-02-tdq-default-cleanup

## Nguyên văn yêu cầu
"hiện tại tôi thấy ko phải khi nào cũng dùng tdq-workflow tôi muốn set defualt là sẽ alway dùng tdq workflow, set trong intake và cả instruction claude user-level, bỏ intruction của superperpower đi"

## Cách hiểu đầu tiên
- Mục tiêu: TDQ workflow phải là default cho MỌI yêu cầu, không bị bỏ qua tùy hứng.
- Phạm vi đoán:
  1. Siết instruction trong `~/.claude/CLAUDE.md` §10: khẳng định tdq-intake là bắt buộc cho mọi request mới (kể cả câu hỏi/check nhỏ hay chỉ trừ pure Q&A — cần hỏi user).
  2. Siết skill `tdq-intake` (description + nội dung) để trigger mạnh hơn.
  3. Xóa §5 "Vận hành superpower" khỏi `~/.claude/CLAUDE.md`.
- Chỗ chưa rõ: câu hỏi thuần đọc/giải đáp (không đổi repo) có phải qua intake không; phần §5 có ý nào cần giữ lại (report file cho external agent?) hay bỏ trọn.
