# 2026-08-09-sua-mo-ta-skill-inventory

## Nguyên văn

> okay ổn đáy mở request làm A đi

Chốt phương án A đã trình ở turn trước trong cùng phiên:

> **A (đề xuất): vá parser + cắt có nhận biết trigger** — ~25 dòng, xoá 18 dòng
> description rỗng (bug YAML block scalar `description: |` trúng nguyên cụm
> firecrawl/tavily), phủ lại 146 skill mất trigger. Tốn thêm 3k token/intake,
> không state.

Bối cảnh dẫn tới yêu cầu (đo thật trên 268 SKILL.md ở máy user, turn trước):

- `scripts/skill_inventory.py` cắt description ở `DESC_MAX = 60` (dòng 27, áp ở dòng 131).
- Description trung vị dài 358 ký tự → 60 ký tự chỉ giữ 17%.
- 211/268 skill có cụm trigger (`use when` / `whenever` / `when the user`);
  **146/211 (69%) trigger nằm sau ký tự thứ 60** → mất tín hiệu định tuyến ở ~55% skill.
- Lấy "câu đầu tiên" thay vì cắt 60 còn tệ hơn (79% trigger nằm sau câu đầu).
- Parser frontmatter không đọc được YAML block scalar `description: |` → **18 skill
  description RỖNG**: 10 skill firecrawl, 7 skill tavily, `mongodb-search-and-ai`.

### Mục tiêu

Bảng kiểm kê năng lực (bước B0 của tdq-intake) phải mang đủ tín hiệu để phán quyết
DÙNG/KHÔNG/NỀN mà không phải mở từng `SKILL.md`.

### Phạm vi đoán

- Sửa `scripts/skill_inventory.py`: (1) parser đọc được block scalar; (2) rút gọn có
  nhận biết trigger thay vì cắt cụt 60 ký tự.
- Cập nhật `tests/test_skill_inventory.py`.
- Có thể phải chỉnh con số/ví dụ trong `skills/tdq-intake/references/skill-inventory.md`
  nếu khuôn bảng nhắc tới độ dài description.

### Chỗ chưa rõ

- Trần độ dài mới cho mỗi dòng (đề xuất ~110 ký tự) — cần user chốt hay để mặc định.
- Có bump version plugin trong turn này không.

## Hiểu & kiến thức

## Hỏi đáp
