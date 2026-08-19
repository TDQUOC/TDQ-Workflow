# C# rules

Soul: chất lượng > runtime > context cost. Load after `chung.md`; applies to every `.cs` file.

## Nguồn

- C# Coding Conventions (Code With Engineering Playbook, Microsoft) —
  https://microsoft.github.io/code-with-engineering-playbook/code-reviews/recipes/csharp —
  naming and code organisation conventions for C#.
- Roslyn analyzers via `.editorconfig` — https://johnnyreilly.com/eslint-your-csharp-in-vs-code-with-roslyn-analyzers —
  8 standard categories: Design, Documentation, Globalization, Reliability, Security, Style,
  Usage, SingleFile; severity is set through `dotnet_analyzer_diagnostic.category-*.severity`.

## Khi nào áp dụng

- Writing or changing any `.cs` file in the solution.
- Before submitting: rebuild so the Roslyn analyzers run; if the machine lacks `dotnet`, write
  "chưa kiểm được".

## Luật Intentionality

1. **Off-standard names**: types, methods and properties use `PascalCase`; locals and
   parameters use `camelCase`; a name must state the work, with no cryptic abbreviations.
2. **Swallowing errors**: an empty `catch { }`, or a catch that merely `return`s, hides bugs —
   catch the specific exception, log it, then handle it or `throw;` to keep the stack trace.
3. **Dead code**: extra `using`s, unused variables, private methods nobody calls — Roslyn's
   Style/Usage groups report them → delete.

## Ngưỡng đo được

- Cyclomatic ≤ 10, cognitive ≤ 15 per method — per `chung.md`; C# is NOT part of the C family
  allowed 25 (that group is only C, C++, Objective-C).
- Analyzer severity: the Security and Reliability categories must never drop below `warning`;
  changing that has to be recorded in the request's spec and edited in `.editorconfig`.

## Làm gì

1. Name per the conventions: `PascalCase` for public members/types, `camelCase` for locals and
   parameters.
2. Enable the Roslyn analyzers in the repo's `.editorconfig`; set per-category severity with
   `dotnet_analyzer_diagnostic.category-<Category>.severity`.
3. Handle exceptions deliberately: catch the specific type, and use `throw;` rather than
   `throw ex;` when rethrowing, so the stack trace survives.
4. Run `dotnet build` and clear every Security and Reliability warning before submitting.

## Tự kiểm

- [ ] `dotnet build` free of Security and Reliability warnings, or "chưa kiểm được" recorded
  because the machine lacks dotnet
- [ ] No empty `catch`, no `throw ex;` destroying the stack trace
- [ ] No unused `using`/variable/method
- [ ] Names follow PascalCase/camelCase and the 3 Intentionality questions in `chung.md` are answerable

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
