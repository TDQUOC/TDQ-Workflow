---
trigger: glob
globs: "**/*.go"
---

# Go Rules

- Handle all returned errors explicitly (`if err != nil`); never discard errors silently with `_`.
- Run `go test ./...` per task; keep packages cohesive and race-clean (`-race` in QC).
