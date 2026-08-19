# C++ rules

Soul: chất lượng > runtime > context cost. Load after `chung.md`; applies to
`.cpp .cc .cxx .hpp .h`.

## Nguồn

- C++ Core Guidelines (official repo, edited by Stroustrup & Sutter) —
  https://github.com/isocpp/CppCoreGuidelines (latest commit 2026-08-06, a living project) —
  focus: interfaces, resource/memory management, concurrency; following it yields statically
  type-safe code with no resource leaks.
- Original announcement at CppCon — https://isocpp.org/blog/2015/09/bjarne-stroustrup-announces-cpp-core-guidelines
  (2015) — the guidelines are deliberately written to be machine-enforceable; they ship with
  the GSL library (`not_null`…).
- LLVM Coding Standards — https://llvm.org/docs/CodingStandards.html — the style standard of
  the clang/clang-tidy ecosystem.

## Khi nào áp dụng

- Writing or changing any C++ file; a `.h` shared with C is still reviewed under this file.
- Before submitting: run the "Tự kiểm" section; if the machine lacks `clang-tidy`, write
  "chưa kiểm được".

## Luật Intentionality

1. **An interface must state its intent**: a pointer parameter that may not be null → use a
   type like `gsl::not_null` rather than a spoken note; units and constraints are expressed
   through types.
2. **Fuzzy resource ownership swallows errors**: bare `new`/`delete` scattered around says
   nothing about who owns what → RAII and smart pointers; leaking resources is exactly what
   the Core Guidelines target.
3. **Dead code**: unused variables, uncalled functions, unreachable branches — `clang-tidy`
   reports them → delete, never comment them out "for later".

## Ngưỡng đo được

- Cyclomatic ≤ 10 per function — per `chung.md`.
- Cognitive ≤ **25** per function — C++ is in the C family (C, C++, Objective-C), so it uses
  the widened level of 25 instead of 15; past 25 the function still gets split, never widened
  further.
- Minimum clang-tidy check set: the `cppcoreguidelines-*` group.

## Làm gì

1. Manage resources with RAII: acquire in the constructor, release in the destructor;
   ownership is expressed by smart pointers, never by bare `new`/`delete`.
2. Write self-describing interfaces: let types carry the constraint (`not_null`, a reference
   instead of a pointer where null is not valid).
3. Enable clang-tidy with the `cppcoreguidelines-*` check group in the repo's config.
4. Run `clang-tidy <đường dẫn>` and clear every warning from the enabled groups.

## Tự kiểm

- [ ] `clang-tidy` free of `cppcoreguidelines-*` warnings, or "chưa kiểm được" recorded
  because the machine lacks clang-tidy
- [ ] No bare `new`/`delete`; every resource has a clear RAII owner
- [ ] No function exceeds cyclomatic 10 or cognitive 25
- [ ] The 3 Intentionality questions in `chung.md` are answerable

## Ví dụ ĐÚNG/SAI

```cpp
// SAI — new trần, ai delete không rõ, con trỏ có thể null không nói:
Widget* make(Config* c) { return new Widget(c->size); }
// ĐÚNG — sở hữu rõ bằng unique_ptr, ràng buộc null nói bằng kiểu:
std::unique_ptr<Widget> TaoWidget(gsl::not_null<const Config*> cauHinh) {
    return std::make_unique<Widget>(cauHinh->size);
}
```
