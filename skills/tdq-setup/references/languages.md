# The 30 languages agent-lsp covers

Copied from `docs/reference/language-support.md` of the upstream repo at v0.18.0
(<https://github.com/blackwell-systems/agent-lsp>). Every row carries its server and the command
that installs it, so a missing rung 3 turns straight into a command to ask the user about.

**Status** — `stable` = every Tier 1 tool passes upstream CI. `experimental` = the server works
but the CI result is informational. `flaky` = passes, but not reliably.

| Language | Language server | Install | Status |
|---|---|---|---|
| TypeScript | `typescript-language-server` | `npm i -g typescript-language-server typescript` | stable |
| JavaScript | `typescript-language-server` | `npm i -g typescript-language-server typescript` | stable |
| Python | `pyright-langserver` | `npm i -g pyright` | stable |
| Go | `gopls` | `go install golang.org/x/tools/gopls@latest` | stable |
| Rust | `rust-analyzer` | `rustup component add rust-analyzer` | stable |
| Java | `jdtls` | download from <https://download.eclipse.org/jdtls/snapshots/> | flaky (cold-start indexing) |
| C | `clangd` | `brew install llvm` (macOS) / `apt install clangd` | stable |
| C++ | `clangd` | `brew install llvm` (macOS) / `apt install clangd` | stable |
| C# | `csharp-ls` | `dotnet tool install -g csharp-ls` | stable |
| Ruby | `solargraph` | `gem install solargraph` | stable |
| PHP | `intelephense` | `npm i -g intelephense` | stable |
| Kotlin | `kotlin-language-server` | download from <https://github.com/fwcd/kotlin-language-server/releases> | stable |
| Lua | `lua-language-server` | `brew install lua-language-server` | stable |
| Swift | `sourcekit-lsp` | ships with Xcode or the Swift toolchain | stable (macOS runner) |
| Zig | `zls` | download from <https://github.com/zigtools/zls/releases>, matching the Zig version | stable |
| Scala | `metals` | `cs install metals` (Coursier) | experimental |
| Gleam | `gleam` (built-in LSP) | download from <https://github.com/gleam-lang/gleam/releases> | stable |
| Elixir | `elixir-ls` | download from <https://github.com/elixir-lsp/elixir-ls/releases> | experimental |
| Clojure | `clojure-lsp` | download from <https://github.com/clojure-lsp/clojure-lsp/releases> | stable |
| Dart | `dart language-server` | ships with the Dart SDK (`brew install dart`) | stable |
| Nix | `nil` | download from <https://github.com/oxalica/nil/releases> | experimental |
| Terraform | `terraform-ls` | download from <https://releases.hashicorp.com/terraform-ls/> | stable |
| SQL | `sqls` | `go install github.com/sqls-server/sqls@latest` | stable (needs a running database) |
| Prisma | `prisma-language-server` | `npm i -g @prisma/language-server` | experimental |
| MongoDB | `mongodb-language-server` | `npm i -g @mongodb-js/mongodb-language-server` | experimental |
| CSS | `vscode-css-language-server` | `npm i -g vscode-langservers-extracted` | stable |
| HTML | `vscode-html-language-server` | `npm i -g vscode-langservers-extracted` | stable |
| JSON | `vscode-json-language-server` | `npm i -g vscode-langservers-extracted` | stable |
| YAML | `yaml-language-server` | `npm i -g yaml-language-server` | stable |
| Dockerfile | `docker-langserver` | `npm i -g dockerfile-language-server-nodejs` | stable |

## What rung 3 actually asks for

The ladder does not ask for all 30. It sniffs the file extensions present in the project and asks
only for the languages that project really uses, with a language under 3 files treated as noise.
YAML and JSON stay out of the sniff entirely: they sit in nearly every repo, so asking for their
server every time would be noise rather than a finding.

The four servers this workflow keeps installed by default are Python, TypeScript/JavaScript, C#
and Lua — the stacks the user works in. The rest get installed the day a project needs them.

## Not every tool works for every language

Tier 1 — `start_lsp`, `open_document`, `get_diagnostics`, `inspect_symbol` — passes upstream CI
for all 30. The 34 Tier 2 tools vary: Java answers hover and call hierarchy but not the symbol
tools, Zig fails workspace symbol, Elixir fails document symbols, YAML and JSON have no notion of
"go to definition". An empty result is therefore not always proof the symbol is absent. That is
exactly the case the fallback layer exists for — see
[uu-tien-tim-kiem.md](uu-tien-tim-kiem.md).

Full matrix per tool and per language: `docs/reference/language-support.md` in the upstream repo.
