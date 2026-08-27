# C++ rules

Soul: chất lượng > runtime > context cost <!-- i18n-allow: canonical Soul line -->. Load after `chung.md`; applies to
`.cpp .cc .cxx .hpp .h`.

## Sources

- C++ Core Guidelines (official repo, edited by Stroustrup & Sutter) —
  https://github.com/isocpp/CppCoreGuidelines (latest commit 2026-08-06, a living project) —
  focus: interfaces, resource/memory management, concurrency; following it yields statically
  type-safe code with no resource leaks.
- Original announcement at CppCon — https://isocpp.org/blog/2015/09/bjarne-stroustrup-announces-cpp-core-guidelines
  (2015) — the guidelines are deliberately written to be machine-enforceable; they ship with
  the GSL library (`not_null`…).
- LLVM Coding Standards — https://llvm.org/docs/CodingStandards.html — the style standard of
  the clang/clang-tidy ecosystem.

## When it applies

- Writing or changing any C++ file; a `.h` shared with C is still reviewed under this file.
- Before submitting: run the "Self-check" section; if the machine lacks `clang-tidy`, write
  "not checked yet".

## The Intentionality rule

1. **An interface must state its intent**: a pointer parameter that may not be null → use a
   type like `gsl::not_null` rather than a spoken note; units and constraints are expressed
   through types.
2. **Fuzzy resource ownership swallows errors**: bare `new`/`delete` scattered around says
   nothing about who owns what → RAII and smart pointers; leaking resources is exactly what
   the Core Guidelines target.
3. **Dead code**: unused variables, uncalled functions, unreachable branches — `clang-tidy`
   reports them → delete, never comment them out "for later".

## Measurable thresholds

- Cyclomatic ≤ 10 per function — per `chung.md`.
- Cognitive ≤ **25** per function — C++ is in the C family (C, C++, Objective-C), so it uses
  the widened level of 25 instead of 15; past 25 the function still gets split, never widened
  further.
- Minimum clang-tidy check set: the `cppcoreguidelines-*` group.

## What to do

1. Manage resources with RAII: acquire in the constructor, release in the destructor;
   ownership is expressed by smart pointers, never by bare `new`/`delete`.
2. Write self-describing interfaces: let types carry the constraint (`not_null`, a reference
   instead of a pointer where null is not valid).
3. Enable clang-tidy with the `cppcoreguidelines-*` check group in the repo's config.
4. Run `clang-tidy <path>` and clear every warning from the enabled groups.

## Self-check

- [ ] `clang-tidy` free of `cppcoreguidelines-*` warnings, or "not checked yet" recorded
  because the machine lacks clang-tidy
- [ ] No bare `new`/`delete`; every resource has a clear RAII owner
- [ ] No function exceeds cyclomatic 10 or cognitive 25
- [ ] The 3 Intentionality questions in `chung.md` are answerable

## RIGHT/WRONG examples

```cpp
// WRONG — bare new, no clear owner to delete, a possibly null pointer left unsaid:
Widget* make(Config* c) { return new Widget(c->size); }
// RIGHT — ownership stated by unique_ptr, the null constraint stated by the type:
std::unique_ptr<Widget> MakeWidget(gsl::not_null<const Config*> config) {
    return std::make_unique<Widget>(config->size);
}
```
