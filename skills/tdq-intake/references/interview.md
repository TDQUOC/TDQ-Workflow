# Vòng interview

Mục tiêu: không còn câu hỏi nào mà câu trả lời khác nhau sẽ dẫn tới sản phẩm khác nhau.

## Hỏi cái gì

Chỉ hỏi câu **làm đổi kết quả**. Với mỗi hạng mục dưới đây, tự trả lời được thì thôi,
không tự trả lời được thì hỏi:

- Phạm vi: cái gì nằm trong, cái gì dứt khoát nằm ngoài.
- Đầu ra: file/màn hình/API cụ thể nào; đo "xong" bằng gì.
- Dữ liệu: nguồn, khối lượng, định dạng, dữ liệu nhạy cảm.
- Lỗi & biên: hỏng thì hành xử ra sao, ai thấy lỗi.
- Hiệu năng & quy mô: ngưỡng chấp nhận được.
- Tương thích: phiên bản, hệ điều hành, phụ thuộc sẵn có.
- Vận hành: chạy ở đâu, ai bảo trì, log/monitor thế nào.

Không hỏi: thứ đọc code là biết, thứ đã có trong `requests/<slug>.md`, thứ chỉ là sở
thích trình bày.

## Hỏi thế nào

Mỗi câu hỏi kèm **2–4 phương án cụ thể**, mỗi phương án 1 dòng tóm tắt hệ quả, phương
án bạn khuyên đặt **đầu tiên** và ghi `(Đề xuất)`. Dùng AskUserQuestion nếu có; không có
thì hỏi bằng danh sách đánh số trong chat.

```
1. <Câu hỏi>
   a) <Phương án A> (Đề xuất) — <hệ quả 1 dòng>
   b) <Phương án B> — <hệ quả 1 dòng>
```

## Ghi lại

Mọi hỏi–đáp vào `docs/tdq/questions/<slug>.md`: câu hỏi, các phương án, user chọn gì
(nguyên văn), ngày giờ.

## Khi nào dừng

Dừng khi đọc lại danh sách câu hỏi mà mọi câu còn lại đều **không** làm đổi sản phẩm.
Còn một câu làm đổi → hỏi tiếp vòng nữa. Cấm chuyển sang viết spec khi còn chỗ phải đoán.
