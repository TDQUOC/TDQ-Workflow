# Ảnh user gửi kèm — cách đưa vào working log

Áp dụng khi turn có ảnh đính kèm **và** turn đó phải ghi working log (có đổi repo).
Làm TRƯỚC khi gọi `tdq_finish.py --log`.

## Các bước

1. Nguồn: đường dẫn cache `~/.claude/image-cache/<session-id>/<n>.<ext>`, đã hiện sẵn
   trong ngữ cảnh của chính turn đó.
2. Đích: `docs/workinglog/assets/<active_request hoặc "misc" nếu không có>/<n>.<ext>`.
   `n` = đếm số file đã có trong thư mục đích + 1. **Không** dùng lại số thứ tự của
   cache gốc — số đó thuộc về session, không thuộc về request.
3. Chèn `![<mô tả ngắn>](assets/<slug>/<n>.<ext>)` vào đúng vị trí liên quan trong chuỗi
   truyền cho `--log`, cạnh câu mô tả ảnh đó. Không bắt buộc đặt ở đầu chuỗi.

## Luật

- Áp dụng cho **mọi** ảnh user gửi kèm trong turn đổi repo. Không tự đánh giá "ảnh này
  chắc không liên quan" rồi bỏ qua.
- Ảnh **track trong git** như mọi file khác trong `docs/workinglog/` — không gitignore.
- Copy lỗi (file cache không còn) → báo user, đừng âm thầm bỏ qua.
