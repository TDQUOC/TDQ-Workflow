---
trigger: glob
globs: "**/*.ps1, **/*.sh"
---

# Windows PowerShell 5.1 & Shell Rules

- Prefer PowerShell 5.1 compatible syntax (`;` separators, `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8`, no `&&` assumptions in PS 5.1) or Python stdlib CLIs (`py -3`).
