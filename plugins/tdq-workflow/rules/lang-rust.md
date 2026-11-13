---
trigger: glob
globs: "**/*.rs"
---

# Rust Rules

- Avoid `.unwrap()` / `.expect()` in library or production paths; propagate `Result<T, E>` with clear context.
- Run `cargo check` and targeted `cargo test` on every task transition.
