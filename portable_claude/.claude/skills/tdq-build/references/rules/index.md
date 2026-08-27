# Index of the per-language rule library

Soul: chất lượng > runtime > context cost <!-- i18n-allow: canonical Soul line -->.
Use the table in "What to do" to tell which language the file belongs to and which rule file to
load.

## Sources

This table is assembled from the research file of the set-soul-workflow request in
`docs/tdq/research/`. Each language's source URLs live in that language file's own "Sources"
section and are not repeated here.

## When it applies

- Whenever you write or change any source file: look the extension up in the table before
  typing code.
- Whenever you need to know which standard linter a language has: the check-command column is
  a list of suggestions to run by hand; there is no automatic scan step any more.

## The Intentionality rule

The definition of the Intentionality group, the three mandatory questions and the 59,6% figure
live in `chung.md` — that file is loaded BEFORE every language file, so nothing is repeated
here.

## Measurable thresholds

The shared numeric thresholds (cyclomatic, cognitive) also live in `chung.md`. A language file
adds its own threshold only where that language differs from the shared level (e.g. C++ uses
cognitive ≤ 25).

## What to do

Look up the extension → load [chung.md](chung.md) + exactly one language rule file → run the
linter command if the machine has it:

| Language | Extension | Rule file | Linter command |
|---|---|---|---|
| Python | `.py` | [python.md](python.md) | `ruff check <path>` |
| C# | `.cs` | [csharp.md](csharp.md) | `dotnet build` |
| TypeScript/JS | `.ts .tsx .js .jsx .mjs .cjs` | [typescript-js.md](typescript-js.md) | `eslint <path>` |
| Go | `.go` | [go.md](go.md) | `golangci-lint run <path>` |
| Rust | `.rs` | [rust.md](rust.md) | `cargo clippy` |
| C++ | `.cpp .cc .cxx .hpp .h` | [cpp.md](cpp.md) | `clang-tidy <path>` |
| HTML | `.html .htm` | [html.md](html.md) | `htmlhint <path>` |
| Bash | `.sh` | user scope: `~/.claude/skills/tdq-rules-bash/bash.md` | `shellcheck <path>` |

The three loading tiers (keeping context cheap without lowering quality):

1. **Always-loaded tier**: only this table plus `chung.md`.
2. **Per-job tier**: load exactly the language file matching the extension being edited;
   loading all 7 files while editing one language is banned.
3. **Off-table tier**: an extension not in the table → follow [them-ngon-ngu.md](them-ngon-ngu.md);
   inventing a rule or borrowing another language's rules is banned.

Linter missing on the machine → write "not checked yet", never write PASS, never install it
yourself.

## Self-check

- [ ] The table covers all 8 languages, each row with 4 columns: language, extension, rule file, linter command
- [ ] Every file in `rules/` (except this index) is named in this file
- [ ] No command in the linter column is an install command (pip install, npm i, brew install)

## RIGHT/WRONG examples

- RIGHT: editing `scripts/scan.py` → load `chung.md` + `python.md`, run `ruff check scripts/scan.py`.
- WRONG: hitting a `.kt` file (Kotlin, off-table) → grabbing Java or TS rules and applying them
  anyway. You must follow `them-ngon-ngu.md`: research 4 queries, present the draft, wait for the user to approve.
