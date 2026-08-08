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

Không hỏi: thứ đọc code là biết, thứ đã có trong mục `## Nguyên văn` của brief, thứ chỉ là sở
thích trình bày.

## Hỏi thế nào

Mỗi câu hỏi kèm **2–4 phương án cụ thể**. **Luôn hỏi bằng danh sách trong chat** — không
dùng AskUserQuestion, để user đọc được toàn bộ phương án cùng lúc và trả lời mở.

Khuôn bắt buộc, dán đúng dạng này:

```
<số>. <Câu hỏi>
- A (đề xuất): <phương án> — <hệ quả 1 dòng>
- B: <phương án> — <hệ quả 1 dòng>
- C: <phương án> — <hệ quả 1 dòng>
```

Luật khuôn:

- Mỗi option đúng **1 dòng riêng**, mở đầu bằng `- ` rồi nhãn chữ HOA `A`/`B`/`C`/`D`.
- **Cấm gộp** nhiều option vào một dòng hay nhét vào đoạn văn dạng `(a) … · (b) …`.
- Phương án bạn khuyên luôn là **A** và mang nhãn `(đề xuất)`; các option khác không có nhãn.
- Sau nhãn là dấu `:` rồi nội dung. Hệ quả nối bằng ` — `, giữ trong cùng dòng đó.
- Nhiều câu hỏi trong một vòng → đánh số câu `1.`, `2.` và mỗi câu có bảng option riêng.
- Câu hỏi chốt lane, chốt mode, hỏi commit cũng theo đúng khuôn này.

**Câu cuối mỗi vòng là bắt buộc**, kể cả khi chỉ có 1 câu hỏi:

```
<số>. Bạn muốn bổ sung thêm gì không?
- A (đề xuất): Không, đủ rồi — làm tiếp đi.
- B: Có — tôi nói thêm.
```

Phương án đóng không bao giờ phủ hết ý user; câu này là chỗ để user thêm ý.

## Ghi lại

Mọi hỏi–đáp vào brief mục `## Hỏi đáp`: câu hỏi, các phương án, user chọn gì
(nguyên văn), ngày giờ.

## Khi nào dừng

Dừng khi đọc lại danh sách câu hỏi mà mọi câu còn lại đều **không** làm đổi sản phẩm.
Còn một câu làm đổi → hỏi tiếp vòng nữa. Cấm chuyển sang viết spec khi còn chỗ phải đoán.
