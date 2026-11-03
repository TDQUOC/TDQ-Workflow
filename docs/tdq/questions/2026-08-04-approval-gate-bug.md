# Questions — 2026-08-04-approval-gate-bug

## Vòng 1 (AskUserQuestion, sau khi đọc code + research)

**Q1. Cơ chế xử lý: thêm gate cứng (chặn thật) hay chỉ siết nhắc nhở?**
- Đề xuất của Claude: gate cứng dựa trên tín hiệu đã có (`looks_like_approval()` —
  đọc payload thô, không phải transcript, nên không lặp lại lỗi đã khiến gate cứng cũ
  (v0.1.4–0.1.6) bị bỏ ở v0.3.0).
- **User chọn: Chỉ siết soft-reminder** — dù đã thấy rõ rủi ro nêu trong option
  ("đã có nhắc rồi mà Claude vẫn bỏ qua được — không giải quyết gốc rễ").

**Q2. Phạm vi áp dụng: chỉ spec/plan, hay cả các điểm dừng duyệt khác?**
- **User chọn: Spec + Plan + Quick** (cả 3 field `_approved` chính trong state.json).
  Không mở rộng sang điểm dừng tự do (vd hỏi commit T4.4).

**Q3. "Detect issue" — có cần rà lại lịch sử các lần đã xảy ra không?**
- **User chọn: Không cần** — chỉ lo ngăn ngừa lần sau. Lý do kỹ thuật: sổ turn chỉ giữ
  log 6 giờ, rà xa hơn phải đọc transcript cũ (kiến trúc hiện tại tránh dùng vì từng gây
  lỗi).

Không còn câu hỏi nào làm thay đổi kết quả sau vòng này — đã đủ để chốt kiến thức
(`docs/tdq/knowledge/2026-08-04-approval-gate-bug.md`) và chuyển sang viết spec.
