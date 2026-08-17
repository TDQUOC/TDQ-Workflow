# Rule Go

Soul: chất lượng > runtime > context cost. Nạp sau `chung.md`, áp cho mọi file `.go`.

## Nguồn

- Effective Go — https://go.dev/doc/effective_go — đặt tên MixedCaps, gofmt, doc comment.
- Google Go Style Guide — https://google.github.io/styleguide/go — chuẩn style bổ sung.
- GDS Way Go — https://gds-way.digital.cabinet-office.gov.uk/manuals/programming-languages/go.html —
  khuyên `golangci-lint` làm meta-linter (gồm `staticcheck`, `errcheck`, `gosec`,
  `revive`; `golint` đã deprecated), `go vet` chạy trong CI.
- Uber Go Style Guide — https://github.com/uber-go/guide/blob/master/style.md — bộ linter
  tối thiểu: errcheck, goimports, revive, govet, staticcheck.

## Khi nào áp dụng

- Viết hoặc sửa bất kỳ file `.go` nào, gồm cả `_test.go`.
- Trước khi nộp: chạy mục "Tự kiểm"; máy thiếu `golangci-lint` thì thử `go vet ./...`,
  thiếu cả hai thì ghi "chưa kiểm được".

## Luật Intentionality

1. **Tên sai chuẩn**: Go dùng `MixedCaps`/`mixedCaps`, không dùng gạch dưới; định danh
   exported viết hoa chữ đầu và phải có doc comment bắt đầu bằng chính tên đó.
2. **Nuốt lỗi**: bỏ qua `err` là lỗi nặng nhất trong Go — `errcheck` bắt mọi lời gọi
   trả error mà không kiểm; muốn bỏ thật thì viết `_ = f()` kèm comment lý do.
3. **Code chết**: compiler Go đã chặn import và biến cục bộ không dùng; phần còn lại
   (hàm không ai gọi, nhánh không thể tới) do `staticcheck` báo → xoá.

## Ngưỡng đo được

- Cyclomatic ≤ 10, cognitive ≤ 15 mỗi hàm — theo `chung.md`; `gocyclo` không có default
  chung nên lấy thẳng mức 10 của TDQ, không tự chọn mức khác.
- Bộ linter tối thiểu phải bật: errcheck, govet, staticcheck (theo Uber Go Style Guide).

## Làm gì

1. Format bằng `gofmt`/`goimports` trước khi nộp — code chưa format coi như chưa xong.
2. Kiểm `err` NGAY sau lời gọi trả về nó; trả lỗi lên trên thì kèm ngữ cảnh cho biết
   thao tác nào hỏng.
3. Định danh exported nào cũng có doc comment bắt đầu bằng tên (`// TinhTong tính…`).
4. Giữ interface nhỏ, nhận interface trả struct khi hợp với code sẵn có của repo.
5. Chạy `golangci-lint run <đường dẫn>` (fallback: `go vet ./...`) và sửa hết lỗi.

## Tự kiểm

- [ ] `golangci-lint run` hoặc `go vet` sạch, hoặc đã ghi "chưa kiểm được"
- [ ] Không lời gọi nào bỏ `err` mà thiếu comment lý do
- [ ] Code đã qua `gofmt`; exported có doc comment đúng khuôn
- [ ] Trả lời được 3 câu hỏi Intentionality trong `chung.md`

## Ví dụ ĐÚNG/SAI

```go
// SAI — bỏ err, tên có gạch dưới:
func read_cfg(p string) []byte {
    b, _ := os.ReadFile(p)
    return b
}
// ĐÚNG — err được kiểm và kèm ngữ cảnh:
// DocConfig đọc file config tại duongDan.
func DocConfig(duongDan string) ([]byte, error) {
    b, err := os.ReadFile(duongDan)
    if err != nil {
        return nil, fmt.Errorf("đọc config %s: %w", duongDan, err)
    }
    return b, nil
}
```
