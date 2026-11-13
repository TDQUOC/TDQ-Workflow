---
trigger: glob
globs: "**/*.sql"
---

# SQL & Migration Safety

- Wrap DDL/data migrations cleanly; never emit destructive `DROP`/`TRUNCATE` without explicit `pha-huy` pause confirmation.
