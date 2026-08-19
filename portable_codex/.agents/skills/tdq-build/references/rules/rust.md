# Rust rules

Soul: chất lượng > runtime > context cost. Load after `chung.md`; applies to every `.rs` file.

## Nguồn

- rust-lang.org discussion — https://users.rust-lang.org/t/is-there-something-like-rust-core-guidelines-like-c-core-guidelines/113850 —
  **Rust has NO "Core Guidelines"** equivalent to C++: the Rust philosophy is to let the
  compiler + `cargo clippy` (hundreds of lints) + `rustfmt` enforce conventions instead of a
  prose document; the "Rust API Guidelines" is the closest thing (its official URL is not in
  the research file, so only the name is given, no invented link).

## Khi nào áp dụng

- Writing or changing any `.rs` file in the crate, tests and examples included.
- Before submitting: run the "Tự kiểm" section; if the machine lacks `cargo`, write
  "chưa kiểm được".

## Luật Intentionality

1. **Off-standard names**: functions/variables `snake_case`, types/traits `PascalCase`,
   constants `SCREAMING_SNAKE_CASE` — the compiler warns on drift by itself; a name must state
   the work it does.
2. **Panicking instead of handling errors is Rust's way of swallowing them**: `.unwrap()`/
   `.expect()` scattered through production code turns a handleable error into a crash — use
   `Result` plus the `?` operator; unwrap is acceptable only in tests, or where the invariant
   is proven right beside it.
3. **Dead code**: the compiler warns `dead_code`/`unused`; never silence a warning with
   `#[allow(...)]` without a one-line reason directly above the attribute.

## Ngưỡng đo được

- Cyclomatic ≤ 10, cognitive ≤ 15 per function — per `chung.md`; Rust is NOT in the C family
  allowed 25.
- Warning level: submitted code must be free of compiler warnings and of default-level
  `cargo clippy` warnings; allowing any lint requires a reason in the request's spec.

## Làm gì

1. Format with `rustfmt` (through `cargo fmt`) before submitting.
2. A function that can fail returns `Result<T, E>`; propagate with `?` and add context at the
   calling boundary; `unwrap` outside tests is banned.
3. Public items (`pub`) carry a one-line `///` doc comment stating the job.
4. Prefer borrows (`&str`, `&[T]`) in parameters over ownership when the function only reads.
5. Run `cargo clippy` and fix every warning; compiler warnings must also reach 0.

## Tự kiểm

- [ ] `cargo clippy` warning-free, or "chưa kiểm được" recorded because the machine lacks cargo
- [ ] No `unwrap`/`expect` outside tests without an invariant note
- [ ] No `#[allow(...)]` without a reason; no dead code
- [ ] The 3 Intentionality questions in `chung.md` are answerable

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
