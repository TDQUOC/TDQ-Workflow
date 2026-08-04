# Xử lý issue/lỗi do user báo

Áp dụng khi yêu cầu mới là **báo lỗi** chứ không phải làm tính năng: "chạy sai", "bị treo",
"kết quả không như mong đợi". Mục tiêu của triage: có đủ căn cứ để viết spec fix, không đoán.

## Thứ tự bắt buộc

1. **Đọc log trước tiên.** Chưa xem log thì chưa được đề xuất nguyên nhân. Nơi tìm log:
   log service của chính sản phẩm, `docs/workinglog/<ngày>.md`, output test gần nhất,
   transcript phiên trước trong `~/.claude/projects/<project>/`.
2. **Tái hiện.** Chạy đúng lệnh user chạy. Không tái hiện được → hỏi user lệnh, input,
   phiên bản, môi trường trước khi đi tiếp.
3. **Capture khi lỗi ở tầng giao diện.** Cần computer use để quay/chụp lại luồng thì lưu
   capture vào folder temp **trong repo**, kèm 1 dòng ghi chú thời điểm và bước tái hiện.
   Xoá capture sau khi đóng issue.
4. **Đóng khung vấn đề.** Viết ra: triệu chứng · nơi phát sinh (file:dòng) · điều kiện
   kích hoạt · phạm vi ảnh hưởng. Thiếu ô nào thì quay lại bước 1.
5. **Research cách fix.** Search theo lỗi nguyên văn và theo tên thư viện + phiên bản.
   Luật gọi search: [tavily.md](../../tdq-conventions/references/tavily.md).
6. **Chốt căn cứ rồi mới lập spec.** Spec fix phải nêu được nguyên nhân gốc, cách sửa,
   và test tái hiện lỗi (đỏ trước khi sửa).

## Sai lầm hay gặp

| Sai | Đúng |
|---|---|
| Sửa theo triệu chứng | Tìm nguyên nhân gốc rồi mới sửa |
| Sửa xong không có test | Viết test tái hiện lỗi, đỏ → xanh |
| Đoán nguyên nhân vì không có log | Bật log chi tiết, chạy lại, đọc log |
| Xoá capture/log ngay | Giữ đến khi issue đóng, ghi trong report |
