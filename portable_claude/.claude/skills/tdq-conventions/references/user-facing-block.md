# Khuôn khối nói với user

Áp cho **mọi** chỗ TDQ hỏi hoặc trình kết quả cho user. Người đọc là người dùng cuối,
không phải người trong nghề: họ cần biết đang xem cái gì, xem chi tiết ở đâu, và phải
trả lời thế nào.

## Mục lục

- Bảy chỗ phải dùng khuôn này
- Năm thành phần (đủ cả năm, đúng thứ tự)
- Bảy luật trang trí
- Luật cứng
- Ký hiệu được phép
- Ví dụ

## Bảy chỗ phải dùng khuôn này

Câu hỏi chọn pipeline · từng vòng interview · cổng duyệt spec · cổng duyệt plan ·
cổng chọn mode · cổng duyệt chế độ nhanh · câu hỏi commit cuối request.

## Năm thành phần (đủ cả năm, đúng thứ tự)

| # | Thành phần | Cấu trúc trình bày dùng |
|---|---|---|
| 1 | Câu dẫn | văn xuôi trần, không in đậm, không gạch đầu dòng |
| 2 | Nội dung | nhãn trường in đậm `**Nhãn:**` + gạch đầu dòng `- ` khi có từ 2 mục |
| 3 | Đường dẫn file | `Xem đầy đủ tại: ` để trần, đường dẫn bọc trong dấu nháy ngược |
| 4 | Đường kẻ ngăn | đúng một dòng `---`, trên và dưới mỗi bên một dòng trống |
| 5 | Khối trả lời | tiêu đề in đậm, một dòng trống, rồi dòng `➤` là dòng cuối cùng |

1. **Câu dẫn** — 1–2 câu nói rõ vừa làm xong gì và user đang được mời làm gì.
   Xưng hô "bạn", giọng trung tính. Không thuật ngữ nội bộ nếu không giải thích ngay.
2. **Nội dung** — tóm tắt thật, đủ để quyết mà không cần mở file. Câu ngắn, gạch đầu dòng.
3. **Đường dẫn file đầy đủ** — một dòng riêng, dạng `Xem đầy đủ tại: <đường dẫn>`.
   Bỏ dòng này khi khối không gắn với file nào.
4. **Đường kẻ ngăn** — một dòng `---` tách khối trả lời khỏi phần trên.
5. **Khối trả lời** — tiêu đề in đậm rồi tới dòng `➤`. Đây luôn là phần CUỐI tin nhắn,
   không có chữ nào ở dưới nó.

## Bảy luật trang trí

Chỉ dùng markdown mà cả ba mặt (terminal, app, extension) đều dựng được. Trang trí là
**thêm ký tự đánh dấu**, không phải viết lại chữ: bảy luật dưới đây không cho phép đổi,
xoá hay thêm từ nào của nội dung.

1. Nhãn trường in đậm, **dấu hai chấm nằm bên trong cặp sao**: `**Mục tiêu:** nội dung`.
   Đặt dấu hai chấm ra ngoài sẽ làm hỏng mọi phép tìm chuỗi `Mục tiêu:` đang chạy.
2. Một trường có từ 2 mục → mỗi mục một dòng, mở đầu bằng `- `. Dưới 2 mục thì để nguyên
   trên dòng nhãn, không tách gạch đầu dòng cho một mục lẻ.
3. Đường dẫn bọc trong dấu nháy ngược, phần dẫn `Xem đầy đủ tại: ` để trần — nhờ vậy
   dòng này vẫn khớp mọi phép tìm cũ.
4. Tên file, tên lệnh và con số trong phần nội dung bọc trong dấu nháy ngược.
5. Giữ đường kẻ `---`, trên và dưới đúng một dòng trống. Không thay bằng ký tự kẻ khác.
6. Danh sách lựa chọn giữ nguyên khuôn `- A (đề xuất): nội dung`, mỗi lựa chọn một dòng;
   chỉ được in đậm bên trong phần nội dung, không đụng vào phần `- A (đề xuất): `.
7. Dòng `➤` giữ nguyên từng byte và luôn là dòng cuối cùng của khối.

## Luật cứng

- **Không emoji** ở bất kỳ thành phần nào. Dấu `➤` giữ nguyên, nó không phải emoji.
- Có nhiều lựa chọn → mỗi lựa chọn **đúng một dòng**, khuôn `- A (đề xuất): nội dung`.
  Cấm gộp lựa chọn vào đoạn văn.
- Thuật ngữ chỉ người trong nghề hiểu (`mode`, `subagent`, `lane`, `phase`) → giải thích
  ngay tại chỗ bằng một mệnh đề ngắn, đừng bắt user tự tra.
- Khối trả lời nằm cuối cùng. In thêm bất cứ gì sau nó là phá khuôn.
- Turn còn chạy tiếp sau khi đã in khối này → in **lại nguyên văn 100%** ở message cuối
  (luật §1 mục 5 của [SKILL.md](../SKILL.md)).

## Ký hiệu được phép

Trong khối in ra cho user chỉ được dùng đúng sáu ký hiệu ngoài ASCII:

| Ký tự | Codepoint | Dùng để |
|---|---|---|
| `➤` | U+27A4 | mở dòng hướng dẫn trả lời, luôn ở dòng cuối |
| `·` | U+00B7 | ngăn hai vế ngang hàng trên cùng một dòng |
| `—` | U+2014 | ngăn phần giải thích khỏi phần được giải thích |
| `→` | U+2192 | chỉ hướng chuyển tiếp giữa hai trạng thái |
| `–` | U+2013 | nối hai đầu của một khoảng |
| `…` | U+2026 | cắt ngắn phần lặp lại trong ví dụ |

Ký tự nào không nằm trong bảng thì không được thêm vào, kể cả khi nhìn có vẻ vô hại.
`▸` bị loại đúng vì lý do đó. Nó chưa từng xuất hiện trong bất kỳ chuỗi nào của kho mã,
nên không có bằng chứng nó dựng đúng trên cả ba mặt. Bảng ký tự kẻ khung
(`─` `│` `├` `└` `┌` `┬` `┐`) cũng bị cấm: chúng đòi canh cột, mà bề rộng terminal thì
thay đổi. Máy kiểm hộ bằng `python3 scripts/scan_block_symbols.py --chi-khoi`.

## Ví dụ

Cùng một nội dung, khác nhau ở chỗ trang trí. Bản `Sau` không đổi một từ nào so với bản
`Trước` — chỉ thêm dấu in đậm, dấu nháy ngược và ngắt dòng.

### Trước

<!-- Khối "Trước" cố tình sai khuôn: nó là ví dụ đối chiếu, không phải mẫu để chép. -->

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

### Sau

```
Tôi đã viết xong spec cho yêu cầu của bạn.

**Mục tiêu:** <1–2 câu>.
**Đầu ra chính:** <gạch đầu dòng ngắn>.
**Rủi ro đáng chú ý:** <gạch đầu dòng ngắn>.

Xem đầy đủ tại: `docs/tdq/spec/<slug>.md`

---

**Bạn duyệt spec này chứ?**

➤ Duyệt: nhắn "duyệt spec" (duyệt xong tôi viết plan ngay) · Góp ý: nhắn trực tiếp
```
