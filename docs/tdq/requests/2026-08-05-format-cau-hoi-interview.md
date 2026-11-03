# REQUEST — Format câu hỏi interview: mỗi option 1 dòng

Ngày: 2026-08-05 10:31 · Slug: `2026-08-05-format-cau-hoi-interview`

## Nguyên văn yêu cầu của user

> tôi muốn bạn phân tích và chỉnh sửa lại chỗ question trong workflow sẽ hiển thị mỗi
> option trả lời 1 đòng ví dụ câu hỏi 1:
> - A (đề xuất): nội dung
> - B : nội dung

Kèm 1 ảnh chụp màn hình: vòng interview của request `2026-08-05-bump-version-va-export`,
5 câu hỏi trình bày dạng đoạn văn liền mạch, các option nhét chung một dòng
(`(a) … · (b) … · (c) …`) nên đọc rất khó.

## Cách hiểu đầu tiên

Mục tiêu: đổi LUẬT trình bày câu hỏi interview trong bộ workflow TDQ, để mọi vòng hỏi
sau này đều xuống dòng từng option theo khuôn `- A (đề xuất): nội dung`.

Phạm vi đoán (chờ user xác nhận):

- `skills/tdq-intake/references/interview.md` — khuôn mẫu chuẩn hiện đang ghi dạng
  `a) … (Đề xuất) — hệ quả`, đây là chỗ sửa chính.
- `portable/workflow/01-intake.md` bước 4 — bản portable đang mô tả bằng lời, không có
  khuôn mẫu; phải đồng bộ cùng luật.
- Câu bắt buộc cuối vòng ("Bạn muốn bổ sung thêm gì không?") và câu hỏi chốt lane ở
  Phần A cũng là câu hỏi có option → nhiều khả năng phải theo cùng khuôn.
- Test đảm bảo khuôn không trôi: có thể thêm vào `tests/test_skill_docs.py`.

## Chỗ chưa rõ

1. Nhãn option: chữ HOA `A/B/C` (như ví dụ user viết) hay giữ `a) b) c)` viết thường?
2. Chữ đề xuất: `(đề xuất)` thường như user gõ, hay `(Đề xuất)` hoa như luật hiện tại?
3. Áp cho mọi câu hỏi có option (gồm chốt lane, câu cuối vòng, hỏi duyệt) hay chỉ
   riêng vòng interview ở phase analyze?
4. Có bắt buộc mỗi option kèm 1 câu hệ quả không, hay chỉ cần nội dung ngắn?
5. Có cần test tự động chặn việc quay về kiểu đoạn văn không?
