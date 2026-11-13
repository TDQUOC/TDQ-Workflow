---
trigger: glob
globs: "**/*.py"
---

# Python Rules (PEP 8 / UTF-8 / Stdlib & Logging)

- Import `utf8_io` or pass `encoding='utf-8'` on every file open.
- Set `creationflags=subprocess.CREATE_NO_WINDOW` on Windows subprocess calls; never use `shell=True` with untrusted inputs.
- Annotate boundary functions, keep functions <= 50 lines, wrap atomic writes cleanly with retry on Windows `PermissionError`.
