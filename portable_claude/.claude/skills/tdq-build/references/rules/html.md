# Rule HTML

Soul: chất lượng > runtime > context cost. Nạp sau `chung.md`, áp cho `.html .htm`.

## Nguồn

- W3C Markup Validation Service — https://validator.w3.org/ — validator chính thức của
  W3C; bản Nu không dựa DTD cho HTML5: https://validator.w3.org/nu (dùng bản này cho
  trang mới).
- HTMLHint — danh mục rule chính thức https://htmlhint.com/rules/ — rule có ID cụ thể:
  `doctype-first`, `doctype-html5`, `head-script-disabled`, `alt-require`, `id-unique`,
  `input-requires-label`, `attr-no-duplication`, `title-require`, `src-not-empty`.

## Khi nào áp dụng

- Viết hoặc sửa file `.html`/`.htm`, kể cả template và trang tĩnh trong docs.
- JS nằm trong thẻ `<script>` của trang thì soát theo `typescript-js.md`, không theo
  file này.

## Luật Intentionality

1. **Thẻ phải nói đúng vai trò**: dùng phần tử ngữ nghĩa đúng việc thay vì chồng `div`;
   thẻ và thuộc tính sai chuẩn là markup không nói được ý cho máy đọc.
2. **Thiếu alt/label là giấu ý với người dùng**: mọi `img` có `alt` (`alt-require`),
   mọi `input` có `label` (`input-requires-label`) — thiếu là chặn cả accessibility
   lẫn máy hiểu trang.
3. **Trùng lặp là mâu thuẫn ý**: `id` phải duy nhất (`id-unique`), thuộc tính không
   lặp trong một thẻ (`attr-no-duplication`), `src` không để trống (`src-not-empty`).

## Ngưỡng đo được

- HTML không có cyclomatic/cognitive — ngưỡng của file này là **0 lỗi validator** và
  **0 lỗi HTMLHint** trên bộ rule đã liệt kê ở mục Nguồn.
- Trang mới bắt buộc doctype HTML5 (`doctype-html5`) và doctype đứng đầu file
  (`doctype-first`).

## Làm gì

1. Mở đầu file bằng `<!DOCTYPE html>`; trang có `<title>` (`title-require`).
2. Không đặt `<script>` trong `<head>` trừ khi bắt buộc (`head-script-disabled`) —
   script chặn render để cuối `<body>`.
3. Viết đủ cặp thuộc tính trong ngoặc kép; mọi `img` có `alt`, mọi `input` có `label`,
   `id` không trùng.
4. Trang public thì validate qua https://validator.w3.org/nu trước khi giao.
5. Chạy `htmlhint <đường dẫn>` với bộ rule ở mục Nguồn; máy thiếu htmlhint thì ghi
   "chưa kiểm được".

## Tự kiểm

- [ ] `htmlhint` sạch lỗi trên bộ rule đã chọn, hoặc đã ghi "chưa kiểm được"
- [ ] Doctype HTML5 đứng đầu file; có `title`
- [ ] Mọi `img` có `alt`; mọi `input` có `label`; `id` duy nhất
- [ ] Trả lời được 3 câu hỏi Intentionality trong `chung.md`

## Ví dụ ĐÚNG/SAI

```html
<!-- SAI — thiếu doctype, img không alt, id trùng: -->
<div id="a"><img src="logo.png"></div>
<div id="a"><input type="text"></div>
<!-- ĐÚNG — doctype đầu file, alt và label đầy đủ, id duy nhất: -->
<!DOCTYPE html>
<img src="logo.png" alt="Logo TDQ">
<label for="ten">Tên</label><input id="ten" type="text">
```
