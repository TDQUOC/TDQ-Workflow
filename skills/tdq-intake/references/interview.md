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

**Câu chốt vòng là có điều kiện** — chỉ ghi khi vòng đó có ít nhất một câu hỏi (kể cả
khi chỉ có đúng 1 câu). Vòng không có câu hỏi nào thì không dựng vòng interview rỗng chỉ
để hỏi câu này: đi thẳng sang bước sau.

```
<số>. Bạn muốn bổ sung thêm gì không?
- A (đề xuất): Không, đủ rồi — làm tiếp đi.
- B: Có — tôi nói thêm.
```

**Dòng hướng dẫn trả lời** — ngay dưới bảng option cuối cùng của mỗi vòng, thêm đúng 1
khối ngắn (nguyên tắc + 1 ví dụ trung tính) giúp người mới đỡ bỡ ngỡ, biết gõ gì thì
được gì:

```
_Trả lời bằng chữ cái (vd: "A"), hoặc gõ thẳng câu tự nhiên khớp ý bạn chọn (vd: "chọn
phương án A") — cả hai đều được hiểu như nhau._
```

Chỉ 1 khối, không lặp lại cho từng câu hỏi khi có nhiều câu trong cùng vòng — đặt ở
cuối, sau option cuối cùng. Ví dụ trong khối này luôn trung tính (không gắn cứng vào
1 câu hỏi cụ thể như lane/mode) vì file này dùng chung cho mọi loại câu hỏi khuôn A/B/C.

Phương án đóng không bao giờ phủ hết ý user; câu này là chỗ để user thêm ý.

## Ghi lại

Mọi hỏi–đáp vào brief mục `## Hỏi đáp`: câu hỏi, các phương án, user chọn gì
(nguyên văn), ngày giờ.

## Khi nào dừng

Dừng khi đọc lại danh sách câu hỏi mà mọi câu còn lại đều **không** làm đổi sản phẩm.
Còn một câu làm đổi → hỏi tiếp vòng nữa. Cấm chuyển sang viết spec khi còn chỗ phải đoán.
