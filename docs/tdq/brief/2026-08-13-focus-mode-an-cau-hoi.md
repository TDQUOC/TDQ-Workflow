# Brief — Câu hỏi bị ẩn khi bật focus mode

## Nguyên văn
User: "mở request mới hiện tại có issue sau khi dùng tdqworkflow mà nếu dùng mode view
focus của claude code thì không thấy câu hỏi ví dụ như ở hình 1 [ảnh: transcript terminal
với các dòng "N messages hidden (/focus to show)" xen giữa vài dòng trạng thái ngắn] hãy
check issue và báo cáo cho tôi nguyên nhân vấn đề".

Cách hiểu đầu tiên: khi Claude Code chạy ở chế độ "focus mode" (chỉ hiển thị tin nhắn văn
bản CUỐI CÙNG của mỗi response, ẩn phần còn lại dưới "N messages hidden"), câu hỏi
lane/interview do TDQ workflow đặt ra đôi khi bị ẩn — user chỉ thấy một dòng tóm tắt ngắn
cuối turn thay vì câu hỏi thật. Mục tiêu: xác định nguyên nhân kỹ thuật, báo cáo — CHƯA
yêu cầu sửa.

Phạm vi đoán: liên quan cơ chế hook `stop_gate.py` (chặn Stop khi repo đổi mà working log
chưa cập nhật) tương tác với cách focus mode chọn "tin nhắn cuối" để hiển thị.

Chỗ chưa rõ: cần đọc code `stop_gate.py` + hiểu chính xác focus mode định nghĩa "final
text message" theo response nào (có tính cả các bước hook block → model tiếp tục hay
không).

## Hiểu & kiến thức

### Kiểm kê năng lực
Không có skill nội bộ nào khớp việc điều tra 1 hành vi hiển thị của CLI Claude Code +
tương tác với hook trong project này — thuần đọc code + research tài liệu chính thức.

### Đọc code
- `hooks/scripts/stop_gate.py`: điểm CHẶN duy nhất là "repo đổi mà working log hôm nay
  chưa append" (`decision: "block"` kèm `reason` dài). Hook này chạy ở **Stop event** —
  tức cuối MỖI turn có tool call. Vì gần như mọi turn trong dự án đều đổi repo (ghi brief/
  spec/plan/skill...) và câu hỏi lane/interview luôn in TRƯỚC khi kịp append log, hook này
  chặn Stop ngay sau khi câu hỏi đã hiện — buộc model gọi thêm Edit (ghi log) rồi in thêm
  1 đoạn text MỚI để kết turn (thường là câu tóm tắt ngắn, kiểu "Đã bổ sung log... đang
  chờ trả lời").
- `docs/workinglog/2026-08-11.md` (20:26, 20:33): xác nhận user đã bật
  `"viewMode": "focus"` (CLI) và `"claudeCode.focusView": true` (VS Code extension) —
  đúng theo tài liệu chính thức, không phải cấu hình lạ.

### Research (tavily-primary qua agent claude-code-guide)
- **Focus mode hoạt động THEO TỪNG TURN**, không theo từng đoạn text: "Focus view hides
  tool activity behind an expandable per-turn summary... shows: last prompt, one-line
  tool-call summary, subagent count, **final response (the last text message in the
  turn)**." — [code.claude.com/docs/en/commands.md], xác nhận thêm ở thông báo release
  v2.1.221.
- 1 turn = từ lúc nhận prompt user tới khi Stop event THẬT SỰ hoàn tất (không bị hook nào
  `block` nữa) — hook `block` không mở turn mới, mà buộc model tiếp tục SINH THÊM nội
  dung trong CÙNG turn logic đó.
- Hệ quả khớp đúng hiện tượng user báo: câu hỏi lane/interview in ra TRƯỚC khi
  `stop_gate.py` chặn không phải là "final response" của turn (vì turn chưa kết thúc ở
  đó) — nó bị gộp vào phần "tool activity" ẩn sau "N messages hidden", user chỉ thấy dòng
  tóm tắt ngắn được in SAU khi ghi log xong.
- Đã có tiền lệ: bug tương tự (ẩn cả nội dung có ý nghĩa, không chỉ tool log) từng được
  báo lên Anthropic ở phiên bản cũ hơn (GitHub Issue #50894 — "hid all assistant text
  emitted between tool calls").
- KHÔNG tìm thấy tài liệu chính thức mô tả riêng case "Stop hook block → additionalContext"
  có được tính là tiếp tục cùng final response hay không — nhưng hành vi quan sát được
  (per-turn, chỉ hiện đoạn cuối) đã đủ giải thích hiện tượng, không cần chi tiết đó.

## Chốt kiến thức
Nguyên nhân: cơ chế `stop_gate.py` (bắt buộc, đúng thiết kế — chống quên ghi log) tình cờ
xung đột với đơn vị hiển thị của focus mode (chỉ hiện dòng cuối MỖI turn). Turn nào vừa
hỏi user vừa bị chặn Stop (hầu hết mọi turn có brief/spec/plan mới) → câu hỏi luôn bị gập
ẩn, chỉ dòng tóm tắt ghi-log-xong hiện ra. Đây là hạn chế TƯƠNG TÁC giữa 2 tính năng đều
đúng thiết kế riêng lẻ (hook TDQ + focus mode CLI), không phải bug ở 1 phía. Việc này CHỈ
điều tra + báo cáo theo đúng yêu cầu user — chưa đề xuất sửa (fix khả dĩ, nếu user muốn ở
lần khác: đổi thứ tự — ghi log TRƯỚC khi in câu hỏi cần dừng chờ, để câu hỏi luôn là dòng
cuối turn).

### Lộ trình
| Bước | Chạy? | Vì sao |
|---|---|---|
| Research | Đã chạy (agent claude-code-guide) | Cần xác nhận cơ chế focus mode có nguồn chính thức, không đoán |
| Interview | Bỏ | Không còn chỗ mơ hồ ảnh hưởng kết quả — đã đọc code + có nguồn xác nhận |
| Spec/Plan | Chạy (rút gọn) | Deliverable là báo cáo chẩn đoán, không sửa code — spec chỉ mô tả nội dung báo cáo + DoD đọc lại |
| QC riêng | Bỏ | Không có code để test; QC = tự đọc lại đối chiếu nguồn |

## Hỏi đáp
Không có câu hỏi cần hỏi user — đủ dữ kiện đọc code + research để chốt nguyên nhân.
