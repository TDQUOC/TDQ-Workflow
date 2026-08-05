# QUESTIONS — Format câu hỏi interview

Request: ../requests/2026-08-05-format-cau-hoi-interview.md · Lane: quick

## Vòng 1 — 2026-08-05 10:36

Chốt sẵn từ chính ví dụ user gõ, không hỏi lại: nhãn option chữ HOA `A/B/C`, chữ
`(đề xuất)` viết thường, dấu `:` ngăn nhãn với nội dung, mỗi option đúng 1 dòng.

1. Áp khuôn mới cho những câu hỏi nào?
   - A (đề xuất): mọi câu hỏi có option — vòng interview, chốt lane, câu mở cuối vòng, hỏi mode/commit.
   - B: chỉ vòng interview ở phase analyze, các chỗ khác giữ nguyên.

2. Còn giữ `AskUserQuestion` không? Luật hiện tại ghi "dùng AskUserQuestion nếu có".
   - A (đề xuất): bỏ hẳn, luôn hỏi bằng danh sách trong chat — khớp quyết định trước đó "câu hỏi dạng mở cuối turn".
   - B: giữ ưu tiên AskUserQuestion, chỉ đổi khuôn cho nhánh hỏi trong chat.

3. Có thêm test chặn khuôn bị trôi không?
   - A (đề xuất): có, 1 ca trong `tests/test_skill_docs.py` kiểm khuôn còn nguyên ở skill + bản portable.
   - B: không, chỉ sửa tài liệu.

4. Bạn muốn bổ sung thêm gì không?
   - A (đề xuất): Không, đủ rồi — làm tiếp đi.
   - B: Có — tôi nói thêm.

Trả lời của user (10:38, nguyên văn): "duyệt quick" — duyệt mini-plan đã nói rõ dựng
trên 3 phương án đề xuất, tức chốt **1A · 2A · 3A**. Câu 4 không được nói thêm gì.
