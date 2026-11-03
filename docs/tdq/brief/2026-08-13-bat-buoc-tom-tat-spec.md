# BRIEF — Bắt buộc in tóm tắt spec trước dòng Duyệt

## Nguyên văn
- User (kèm ảnh chụp 1 lượt trước): sau khi trình spec chờ duyệt, chat chỉ in "Đã
  append working log. Spec đang chờ bạn duyệt:" rồi thẳng tới dòng `➤ Duyệt: nhắn
  "duyệt spec"` — KHÔNG có phần tóm tắt spec (mục tiêu/đầu ra/DoD/rủi ro) dù
  `tdq-spec/SKILL.md` bước 4 đã yêu cầu "tóm tắt spec ≤ 50 dòng" trước dòng đó.
- User: "phải có trình bày summary spec ra chứ".
- Tôi hỏi user muốn xử lý bằng cách nào (A: chỉ ghi nhớ / B: thêm hàng rào hook chặn
  thật). User chọn: "tôi muốn bổ sung trong skill/ instruction" — tức phương án thứ 3
  (không có trong 2 option ban đầu): SỬA CÂU CHỮ trong file skill để khó bị bỏ sót hơn,
  không phải chỉ ghi nhớ suông, cũng không phải thêm hook kỹ thuật mới.
- Cách hiểu đầu tiên: cần rà `tdq-spec/SKILL.md` bước 4 (và có thể `tdq-plan/SKILL.md`
  bước 5 tương tự — cùng mẫu "tóm tắt rồi in dòng Duyệt") — làm rõ hơn bằng câu chữ:
  tóm tắt là bước BẮT BUỘC, không được thay bằng câu thông báo suông kiểu "đang chờ
  bạn duyệt", và có thể thêm 1 câu tự-kiểm ngay trước khi DỪNG turn.
- Chỗ chưa rõ: (1) chỉ sửa `tdq-spec/SKILL.md` hay áp luôn cho `tdq-plan/SKILL.md` (có
  bước trình bày tương tự, cùng rủi ro bị bỏ sót)? (2) hình thức bổ sung: thêm 1 câu
  nhấn mạnh ngay bước 4, hay thêm hẳn 1 bước tự-kiểm (checklist) trước khi in dòng
  Duyệt?
