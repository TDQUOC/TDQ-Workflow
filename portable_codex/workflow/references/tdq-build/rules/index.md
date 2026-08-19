# Index of the per-language rule library

Soul: chất lượng > runtime > context cost.
Use the table in "Làm gì" to tell which language the file belongs to and which rule file to
load.

## Nguồn

This table is assembled from the research file of the set-soul-workflow request in
`docs/tdq/research/`. Each language's source URLs live in that language file's own "Nguồn"
section and are not repeated here.

## Khi nào áp dụng

- Whenever you write or change any source file: look the extension up in the table before
  typing code.
- Whenever you need to know which standard linter a language has: the check-command column is
  a list of suggestions to run by hand; there is no automatic scan step any more.

## Luật Intentionality

The definition of the Intentionality group, the three mandatory questions and the 59,6% figure
live in `chung.md` — that file is loaded BEFORE every language file, so nothing is repeated
here.

## Ngưỡng đo được

The shared numeric thresholds (cyclomatic, cognitive) also live in `chung.md`. A language file
adds its own threshold only where that language differs from the shared level (e.g. C++ uses
cognitive ≤ 25).

## Làm gì

Look up the extension → load [chung.md](chung.md) + exactly one language rule file → run the
linter command if the machine has it:

| Ngôn ngữ | Đuôi file | File rule | Lệnh linter |
|---|---|---|---|
| Python | `.py` | [python.md](python.md) | `ruff check <đường dẫn>` |
| C# | `.cs` | [csharp.md](csharp.md) | `dotnet build` |
| TypeScript/JS | `.ts .tsx .js .jsx .mjs .cjs` | [typescript-js.md](typescript-js.md) | `eslint <đường dẫn>` |
| Go | `.go` | [go.md](go.md) | `golangci-lint run <đường dẫn>` |
| Rust | `.rs` | [rust.md](rust.md) | `cargo clippy` |
| C++ | `.cpp .cc .cxx .hpp .h` | [cpp.md](cpp.md) | `clang-tidy <đường dẫn>` |
| HTML | `.html .htm` | [html.md](html.md) | `htmlhint <đường dẫn>` |

The three loading tiers (keeping context cheap without lowering quality):

1. **Always-loaded tier**: only this table plus `chung.md`.
2. **Per-job tier**: load exactly the language file matching the extension being edited;
   loading all 7 files while editing one language is banned.
3. **Off-table tier**: an extension not in the table → follow [them-ngon-ngu.md](them-ngon-ngu.md);
   inventing a rule or borrowing another language's rules is banned.

Linter missing on the machine → write "chưa kiểm được", never write PASS, never install it
yourself.

## Tự kiểm

- [ ] The table covers all 7 languages, each row with 4 columns: language, extension, rule file, linter command
- [ ] Every file in `rules/` (except this index) is named in this file
- [ ] No command in the linter column is an install command (pip install, npm i, brew install)

## Ví dụ ĐÚNG/SAI

- ĐÚNG: editing `scripts/scan.py` → load `chung.md` + `python.md`, run `ruff check scripts/scan.py`.
- SAI: hitting a `.kt` file (Kotlin, off-table) → grabbing Java or TS rules and applying them
  anyway. You must follow `them-ngon-ngu.md`: research 4 queries, trình nháp, chờ user duyệt.
