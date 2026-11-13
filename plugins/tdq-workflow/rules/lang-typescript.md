---
trigger: glob
globs: "**/*.ts, **/*.tsx, **/*.js, **/*.jsx"
---

# TypeScript & JS Rules

- Call `open_document` via LSP before symbol queries on TS/JS projects.
- Keep strict types (`no any` in new contracts), validate runtime JSON schemas at module boundaries, dispose listeners cleanly.
