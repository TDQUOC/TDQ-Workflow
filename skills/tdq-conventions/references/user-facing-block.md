# Khuôn khối nói với user

Áp cho **mọi** chỗ TDQ hỏi hoặc trình kết quả cho user. Người đọc là người dùng cuối,
không phải người trong nghề: họ cần biết đang xem cái gì, xem chi tiết ở đâu, và phải
trả lời thế nào.

## Bảy chỗ phải dùng khuôn này

Câu hỏi chọn pipeline · từng vòng interview · cổng duyệt spec · cổng duyệt plan ·
cổng chọn mode · cổng duyệt chế độ nhanh · câu hỏi commit cuối request.

## Năm thành phần (đủ cả năm, đúng thứ tự)

1. **Câu dẫn** — 1–2 câu nói rõ vừa làm xong gì và user đang được mời làm gì.
   Xưng hô "bạn", giọng trung tính. Không thuật ngữ nội bộ nếu không giải thích ngay.
2. **Nội dung** — tóm tắt thật, đủ để quyết mà không cần mở file. Câu ngắn, gạch đầu dòng.
3. **Đường dẫn file đầy đủ** — một dòng riêng, dạng `Xem đầy đủ tại: <đường dẫn>`.
   Bỏ dòng này khi khối không gắn với file nào.
4. **Đường kẻ ngăn** — một dòng `---` tách khối trả lời khỏi phần trên.
5. **Khối trả lời** — tiêu đề in đậm rồi tới dòng `➤`. Đây luôn là phần CUỐI tin nhắn,
   không có chữ nào ở dưới nó.

## Luật cứng

- **Không emoji** ở bất kỳ thành phần nào. Dấu `➤` giữ nguyên, nó không phải emoji.
- Có nhiều lựa chọn → mỗi lựa chọn **đúng một dòng**, khuôn `- A (đề xuất): nội dung`.
  Cấm gộp lựa chọn vào đoạn văn.
- Thuật ngữ chỉ người trong nghề hiểu (`mode`, `subagent`, `lane`, `phase`) → giải thích
  ngay tại chỗ bằng một mệnh đề ngắn, đừng bắt user tự tra.
- Khối trả lời nằm cuối cùng. In thêm bất cứ gì sau nó là phá khuôn.
- Turn còn chạy tiếp sau khi đã in khối này → in **lại nguyên văn 100%** ở message cuối
  (luật §1 mục 5 của [SKILL.md](../SKILL.md)).

## Ví dụ

```
Tôi đã viết xong spec cho yêu cầu của bạn.

Mục tiêu: <1–2 câu>.
Đầu ra chính: <gạch đầu dòng ngắn>.
Rủi ro đáng chú ý: <gạch đầu dòng ngắn>.

Xem đầy đủ tại: docs/tdq/spec/<slug>.md

---

**Bạn duyệt spec này chứ?**

➤ Duyệt: nhắn "duyệt spec" (duyệt xong tôi viết plan ngay) · Góp ý: nhắn trực tiếp
```
