# Chỉ mục thư viện rule theo ngôn ngữ

Soul: chất lượng > runtime > context cost.
Tra bảng ở mục "Làm gì" để biết file đang sửa thuộc ngôn ngữ nào và nạp file rule nào.

## Nguồn

Bảng này ghép từ file research của request set-soul-workflow trong `docs/tdq/research/`.
URL gốc của từng ngôn ngữ nằm ngay trong mục "Nguồn" của từng file rule, không chép lại đây.

## Khi nào áp dụng

- Khi viết hoặc sửa bất kỳ file mã nguồn nào: tra bảng theo đuôi file trước khi gõ code.
- Khi muốn biết ngôn ngữ đang sửa có linter chuẩn nào: cột lệnh kiểm trong bảng là
  danh sách gợi ý, chạy tay khi cần, không có bước scan tự động nào nữa.

## Luật Intentionality

Định nghĩa nhóm lỗi Intentionality, ba câu hỏi bắt buộc và số 59,6% nằm trong
`chung.md` — file đó nạp TRƯỚC mọi file ngôn ngữ, không lặp lại nội dung ở đây.

## Ngưỡng đo được

Ngưỡng số dùng chung (cyclomatic, cognitive) cũng nằm trong `chung.md`. File ngôn ngữ
chỉ ghi thêm ngưỡng riêng khi ngôn ngữ đó khác mức chung (vd C++ dùng cognitive ≤ 25).

## Làm gì

Tra đuôi file → nạp `chung.md` + đúng một file rule ngôn ngữ → chạy lệnh linter nếu máy có:

| Ngôn ngữ | Đuôi file | File rule | Lệnh linter |
|---|---|---|---|
| Python | `.py` | python.md | `ruff check <đường dẫn>` |
| C# | `.cs` | csharp.md | `dotnet build` |
| TypeScript/JS | `.ts .tsx .js .jsx .mjs .cjs` | typescript-js.md | `eslint <đường dẫn>` |
| Go | `.go` | go.md | `golangci-lint run <đường dẫn>` |
| Rust | `.rs` | rust.md | `cargo clippy` |
| C++ | `.cpp .cc .cxx .hpp .h` | cpp.md | `clang-tidy <đường dẫn>` |
| HTML | `.html .htm` | html.md | `htmlhint <đường dẫn>` |

Luật ba tầng nạp (giữ context rẻ mà không hạ chất lượng):

1. **Tầng luôn nạp**: chỉ bảng này + `chung.md`.
2. **Tầng theo việc**: nạp đúng file ngôn ngữ khớp đuôi file đang sửa; cấm nạp cả 7
   file khi chỉ sửa một ngôn ngữ.
3. **Tầng ngoài bảng**: đuôi file không có trong bảng → làm theo `them-ngon-ngu.md`,
   cấm tự bịa rule hay mượn rule ngôn ngữ khác.

Linter không có trên máy → ghi "chưa kiểm được", cấm ghi PASS, cấm tự cài đặt.

## Tự kiểm

- [ ] Bảng có đủ 7 ngôn ngữ, mỗi dòng đủ 4 cột: ngôn ngữ, đuôi, file rule, lệnh linter
- [ ] Mọi file trong thư mục `rules/` (trừ chỉ mục này) được nhắc tên trong file này
- [ ] Không lệnh nào trong cột linter là lệnh cài đặt (pip install, npm i, brew install)

## Ví dụ ĐÚNG/SAI

- ĐÚNG: sửa `scripts/scan.py` → nạp `chung.md` + `python.md`, chạy `ruff check scripts/scan.py`.
- SAI: gặp file `.kt` (Kotlin, ngoài bảng) → lấy rule Java hay TS áp bừa. Phải theo
  `them-ngon-ngu.md`: research 4 truy vấn, trình nháp, chờ user duyệt.
