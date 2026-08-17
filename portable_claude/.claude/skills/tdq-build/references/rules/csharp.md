# Rule C#

Soul: chất lượng > runtime > context cost. Nạp sau `chung.md`, áp cho mọi file `.cs`.

## Nguồn

- C# Coding Conventions (Code With Engineering Playbook, Microsoft) —
  https://microsoft.github.io/code-with-engineering-playbook/code-reviews/recipes/csharp —
  convention đặt tên và tổ chức code C#.
- Roslyn analyzers qua `.editorconfig` — https://johnnyreilly.com/eslint-your-csharp-in-vs-code-with-roslyn-analyzers —
  8 category chuẩn: Design, Documentation, Globalization, Reliability, Security, Style,
  Usage, SingleFile; bật mức báo qua `dotnet_analyzer_diagnostic.category-*.severity`.

## Khi nào áp dụng

- Viết hoặc sửa bất kỳ file `.cs` nào trong solution.
- Trước khi nộp: build lại để Roslyn analyzers chạy; máy thiếu `dotnet` thì ghi
  "chưa kiểm được".

## Luật Intentionality

1. **Tên sai chuẩn**: type, method, property viết `PascalCase`; biến cục bộ và tham số
   viết `camelCase`; tên phải nêu đúng việc, không viết tắt khó hiểu.
2. **Nuốt lỗi**: khối `catch { }` trống hay catch rồi chỉ `return` giấu bug — bắt đúng
   exception, log rồi xử lý hoặc `throw;` giữ stack trace.
3. **Code chết**: `using` thừa, biến không dùng, method private không ai gọi — nhóm
   Style/Usage của Roslyn báo → xoá.

## Ngưỡng đo được

- Cyclomatic ≤ 10, cognitive ≤ 15 mỗi method — theo `chung.md`; C# KHÔNG thuộc nhóm
  họ C được nới 25 (nhóm đó chỉ gồm C, C++, Objective-C).
- Mức analyzer: hai category Security và Reliability không được hạ dưới `warning`;
  muốn đổi phải ghi vào spec của request, sửa trong `.editorconfig`.

## Làm gì

1. Đặt tên theo convention: `PascalCase` cho public member/type, `camelCase` cho biến
   cục bộ và tham số.
2. Bật Roslyn analyzers trong `.editorconfig` của repo; chỉnh mức báo theo category
   bằng `dotnet_analyzer_diagnostic.category-<Category>.severity`.
3. Xử lý exception có chủ đích: bắt loại cụ thể, `throw;` thay vì `throw ex;` khi ném
   tiếp để giữ stack trace.
4. Chạy `dotnet build` và sửa hết warning của hai nhóm Security, Reliability trước
   khi nộp.

## Tự kiểm

- [ ] `dotnet build` sạch warning nhóm Security và Reliability, hoặc đã ghi
  "chưa kiểm được" khi máy thiếu dotnet
- [ ] Không `catch` trống, không `throw ex;` làm mất stack trace
- [ ] Không `using`/biến/method thừa
- [ ] Tên đúng PascalCase/camelCase và trả lời được 3 câu hỏi Intentionality ở `chung.md`

## Ví dụ ĐÚNG/SAI

```csharp
// SAI — tên mơ hồ, catch trống:
public int Proc(int[] a) {
    try { return a[0] / a.Length; } catch { }
    return 0;
}
// ĐÚNG — tên nêu việc, lỗi có chủ đích:
public int TinhTrungBinh(int[] cacSo) {
    if (cacSo.Length == 0)
        throw new ArgumentException("cacSo rỗng", nameof(cacSo));
    return cacSo.Sum() / cacSo.Length;
}
```
