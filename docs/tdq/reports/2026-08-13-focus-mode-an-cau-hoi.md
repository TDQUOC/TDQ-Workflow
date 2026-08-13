# Report — Câu hỏi TDQ bị ẩn khi bật focus mode

Ngày: 2026-08-13 · Spec: ../spec/2026-08-13-focus-mode-an-cau-hoi.md · Plan: ../plan/2026-08-13-focus-mode-an-cau-hoi.md

## 1. Hiện tượng quan sát
User bật `"viewMode": "focus"` (CLI, xem `docs/workinglog/2026-08-11.md` mục 20:26) và
`"claudeCode.focusView": true` (VS Code extension, mục 20:33). Trong transcript, câu hỏi
lane/interview do TDQ workflow đặt ra không hiện trực tiếp — thay vào đó terminal in các
dòng "N messages hidden (/focus to show)" xen giữa vài dòng trạng thái ngắn (vd "Đã bổ
sung log... đang chờ trả lời"). User phải bấm `/focus` để tắt mới đọc lại được câu hỏi
thật.

## 2. Cơ chế gây ra
**Nguồn 1 — code repo, `hooks/scripts/stop_gate.py:9`**: "Điểm CHẶN duy nhất: repo đổi mà
working log hôm nay chưa được cập nhật." Hàm `main()` (dòng 107-188) chạy ở **Stop event**
— cuối MỖI turn có tool call. Khi repo đã đổi (ghi brief/spec/plan/skill...) mà
`docs/workinglog/<ngày>.md` chưa được append, hook trả về:
```python
{"decision": "block", "reason": "[TDQ:LOG] Turn này đổi repo (...) nhưng ... chưa được append. ..."}
```
(dòng 139-144). Đây là hành vi ĐÚNG THIẾT KẾ — chống quên ghi log, không phải bug.

Trong quy trình TDQ, câu hỏi lane/interview luôn được in TRƯỚC khi kịp ghi log (per
`skills/tdq-intake/SKILL.md` bước 2: "**DỪNG chờ user trả lời**" ngay sau câu hỏi). Vì
gần như mọi turn mở request/viết spec/plan đều đổi repo, `stop_gate.py` chặn Stop ngay
sau khi câu hỏi đã hiện — buộc model gọi thêm Edit (ghi log) rồi in thêm MỘT ĐOẠN TEXT
MỚI để kết turn (thường là câu tóm tắt ngắn, kiểu "Đã bổ sung mục ... đang chờ bạn trả
lời").

**Nguồn 2 — research chính thức (agent `claude-code-guide`, qua `tavily-primary` +
`code.claude.com/docs/en/commands.md`, xác nhận thêm bởi thông báo release Claude Code
v2.1.221)**: Focus mode hoạt động theo **đơn vị 1 turn**, không theo từng đoạn text —
"Focus view hides tool activity behind an expandable per-turn summary... shows: last
prompt, one-line tool-call summary, subagent count, **final response (the last text
message in the turn)**." Một turn = từ lúc nhận prompt user tới khi Stop event THẬT SỰ
hoàn tất (không còn hook nào `block`) — hook `block` không mở turn mới, chỉ buộc model
sinh thêm nội dung trong CÙNG turn logic.

**Kết hợp 2 nguồn**: câu hỏi in trước lúc `stop_gate.py` chặn KHÔNG PHẢI "dòng cuối turn"
(vì turn chưa kết thúc ở đó) — nên bị gộp vào phần "tool activity" mà focus mode ẩn sau
"N messages hidden". Chỉ dòng tóm tắt in SAU khi ghi log xong mới là "final response",
mới hiện ra. Đây là xung đột giữa 2 cơ chế đều đúng thiết kế riêng lẻ (hook TDQ chống
quên log × focus mode chỉ hiện dòng cuối), không phải bug ở một phía.

**Tiền lệ đã biết**: một bug tương tự (ẩn cả nội dung có ý nghĩa, không chỉ tool log)
từng được cộng đồng báo lên Anthropic ở bản Claude Code cũ hơn — GitHub Issue #50894
("hid all assistant text emitted between tool calls"), cho thấy đây là rủi ro đã biết của
kiểu thiết kế "chỉ hiện dòng cuối turn".

**Giới hạn của kết luận**: tài liệu chính thức KHÔNG mô tả chi tiết việc `additionalContext`
từ một Stop hook bị `block` có được tính là "tiếp tục cùng response" hay "mở response
mới" ở tầng implementation nội bộ — nhưng hành vi quan sát được (per-turn, chỉ hiện dòng
cuối) đã đủ giải thích hiện tượng user báo, không cần chi tiết đó.

## 3. Gợi ý hướng khắc phục (chưa triển khai)
Đổi thứ tự trong các skill TDQ (`tdq-intake`, `tdq-spec`, `tdq-plan`, `tdq-build`...): ghi
working log TRƯỚC khi in câu hỏi/khối chờ duyệt cần DỪNG, thay vì ghi log SAU. Khi đó câu
hỏi luôn là đoạn text cuối cùng của turn → focus mode sẽ hiện đúng câu hỏi thay vì dòng
tóm tắt ngắn. Rủi ro cần cân nhắc nếu làm: phải đảm bảo nội dung log ghi trước vẫn phản
ánh đúng trạng thái turn (một số thông tin, như dòng "đang chờ duyệt", chỉ biết được sau
khi đã quyết định có hỏi hay không) — cần thiết kế lại thứ tự bước trong từng skill, không
chỉ đổi vị trí 1 lệnh.

## Kết luận
Nguyên nhân đã xác định rõ, có nguồn (code repo + tài liệu chính thức + tiền lệ GitHub
Issue). KHÔNG có code nào bị sửa trong request này — đúng phạm vi user yêu cầu (điều tra +
báo cáo). Việc sửa (nếu user muốn) cần mở request mới.

Git: chưa commit.
