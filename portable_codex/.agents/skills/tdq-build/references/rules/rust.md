# Rule Rust

Soul: chất lượng > runtime > context cost. Nạp sau `chung.md`, áp cho mọi file `.rs`.

## Nguồn

- Thảo luận rust-lang.org — https://users.rust-lang.org/t/is-there-something-like-rust-core-guidelines-like-c-core-guidelines/113850 —
  **Rust KHÔNG có "Core Guidelines"** tương đương C++: triết lý Rust là để compiler +
  `cargo clippy` (hàng trăm lint) + `rustfmt` thực thi convention thay cho văn bản mô tả;
  "Rust API Guidelines" là tài liệu gần nhất (URL chính thức chưa có trong research nên
  chỉ ghi tên, không bịa link).

## Khi nào áp dụng

- Viết hoặc sửa bất kỳ file `.rs` nào trong crate, gồm cả test và example.
- Trước khi nộp: chạy mục "Tự kiểm"; máy thiếu `cargo` thì ghi "chưa kiểm được".

## Luật Intentionality

1. **Tên sai chuẩn**: hàm/biến `snake_case`, type/trait `PascalCase`, hằng
   `SCREAMING_SNAKE_CASE` — compiler tự warn khi lệch; tên phải nêu đúng việc.
2. **Panic thay cho xử lý lỗi là nuốt lỗi kiểu Rust**: `.unwrap()`/`.expect()` rải trong
   code sản phẩm biến lỗi xử lý được thành crash — dùng `Result` + toán tử `?`; unwrap
   chỉ chấp nhận trong test hoặc khi bất biến đã được chứng minh ngay cạnh đó.
3. **Code chết**: compiler warn `dead_code`/`unused`; đừng dập warning bằng
   `#[allow(...)]` khi chưa ghi lý do một dòng ngay trên attribute.

## Ngưỡng đo được

- Cyclomatic ≤ 10, cognitive ≤ 15 mỗi hàm — theo `chung.md`; Rust KHÔNG thuộc nhóm họ C
  được nới 25.
- Mức warning: code nộp phải sạch warning của compiler và của `cargo clippy` ở mức
  mặc định; muốn allow lint nào phải ghi lý do vào spec của request.

## Làm gì

1. Format bằng `rustfmt` (qua `cargo fmt`) trước khi nộp.
2. Hàm nào có thể hỏng thì trả `Result<T, E>`; lan truyền lỗi bằng `?`, thêm ngữ cảnh
   ở biên nơi gọi; cấm `unwrap` ngoài test.
3. Item public (`pub`) có doc comment `///` một dòng nêu việc.
4. Ưu tiên borrow (`&str`, `&[T]`) ở tham số thay vì sở hữu khi hàm chỉ đọc dữ liệu.
5. Chạy `cargo clippy` và sửa hết warning; compiler warning cũng phải về 0.

## Tự kiểm

- [ ] `cargo clippy` sạch warning, hoặc đã ghi "chưa kiểm được" khi máy thiếu cargo
- [ ] Không `unwrap`/`expect` ngoài test khi thiếu ghi chú bất biến
- [ ] Không `#[allow(...)]` thiếu lý do; không code chết
- [ ] Trả lời được 3 câu hỏi Intentionality trong `chung.md`

## Ví dụ ĐÚNG/SAI

```rust
// SAI — unwrap trong code sản phẩm, tên không nói việc:
fn get(p: &str) -> String {
    std::fs::read_to_string(p).unwrap()
}
// ĐÚNG — Result + ?, tên nêu việc:
fn doc_config(duong_dan: &str) -> Result<String, std::io::Error> {
    let noi_dung = std::fs::read_to_string(duong_dan)?;
    Ok(noi_dung)
}
```
