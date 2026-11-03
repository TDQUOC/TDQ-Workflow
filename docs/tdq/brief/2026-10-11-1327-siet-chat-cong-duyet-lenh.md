# BRIEF — Siết chặt cổng duyệt buộc dùng đúng lệnh

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

User:
"okay bây giờ muốn mở request handle thêm là sẽ siết chặt các cổng duyệt buộc phải nhập đúng lệnh duyệt bằng vi hoặc en thay vì như hiện tại"

**Mục tiêu:**
- Hủy bỏ hoặc siết lại cơ chế duyệt bằng ngôn ngữ tự nhiên (như "làm đi", "tiến hành đi") đã thêm ở 0.61.0.
- Yêu cầu người dùng phải gõ ĐÚNG lệnh duyệt chính thức (có thể hỗ trợ cả tiếng Việt và tiếng Anh) tại các cổng duyệt (spec, plan, quick, mode).
- Tránh việc duyệt nhầm do hiểu sai câu nói thông thường.

**Phạm vi dự kiến:**
- `hooks/scripts/prompt_context.py` (nơi chứa regex kiểm tra câu lệnh duyệt).
- `skills/tdq-conventions/references/approval.md` (tài liệu quy định cổng duyệt).
- `tests/test_prompt_context.py` (cập nhật test theo rule mới).

## Hiểu & kiến thức
- Ở phiên bản `0.61.0`, tính năng duyệt bằng câu tự nhiên (như "làm đi", "tiến hành đi"...) đã được thêm qua Regex `ACTION_APPROVAL` trong `prompt_context.py` và cho phép vượt cổng khi đối tượng `target` là `spec` hoặc `plan`.
- Tuy nhiên, tính năng này gây hiểu lầm hoặc duyệt ngoài ý muốn đối với các câu giao tiếp thông thường.
- Giải pháp:
  1. Xoá regex `ACTION_APPROVAL` trong `hooks/scripts/prompt_context.py` và gỡ logic `if target in ("spec", "plan") and ACTION_APPROVAL.match(prompt)`.
  2. Xoá/điều chỉnh nội dung `## Natural action phrases as approval` trong `skills/tdq-conventions/references/approval.md` để trở về nguyên tắc: MỘT lệnh duyệt bắt buộc phải có ĐỦ 2 thành phần: Động từ duyệt (`AGREE`) + Đối tượng hoặc đại từ chỉ định (`OBJECT` / `PRONOUN`), HOẶC người dùng gõ số tuỳ chọn (ví dụ: `1a`).
  3. Cập nhật `tests/test_prompt_context.py` để đảm bảo hệ thống chặn đứng các câu ra lệnh cụt lủn không kèm đối tượng.
  4. Đảm bảo token budget & rules drift = 0.00%.

## Hỏi đáp
- User đã chốt qua yêu cầu mở request bằng "a" (chế độ nhanh).
