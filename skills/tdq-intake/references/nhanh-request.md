# The request branch — five types, the commands, the naming rule

Used at steps 2 and 3b of [tdq-intake](../SKILL.md). Every request in lane `full` or `quick`
works on a branch of its own and merges back when the report is done. Tier `nhỏ` opens none. <!-- i18n-allow -->

## When it applies

The user has settled the lane and `init` has run, in a project that already has a git repo.
No repo → skip; the three state keys stay empty and step 11 of the report skips too.

## What to do

### The five types

| Loại | Dùng khi | <!-- i18n-allow -->
|---|---|
| `feature` | thêm hành vi mới | <!-- i18n-allow -->
| `bugfix` | thứ đã dựng chạy sai | <!-- i18n-allow -->
| `hotfix` | hỏng đang chặn việc ngay lúc này | <!-- i18n-allow -->
| `chore` | bump phiên bản, phụ thuộc, dọn dẹp — hành vi không đổi | <!-- i18n-allow -->
| `docs` | chỉ sửa tài liệu | <!-- i18n-allow -->

Propose the type inside the lane question of step 2, never as a second question. The user
answers one line and both are settled.

### The name

`<loại>/<mô tả>` — `<mô tả>` is the slug's kebab tail, no accents. Samples: <!-- i18n-allow -->
`feature/login-gui`, `bugfix/state-mat-nhanh-goc`, `hotfix/hook-treo-turn`,
`chore/bump-phien-ban`, `docs/kien-truc-module`. The separator is a forward slash and nothing
else: `git check-ref-format --branch` rejects the backslash form. The banned prefixes of
`tdq-conventions` §7 still apply.

### The commands

```
git status --porcelain                 # dirty but ONLY docs/logs → switch and carry along. ANY other dirty file → STOP
git rev-parse --abbrev-ref HEAD        # this is nhanh_goc (normally `dev`)
git switch -c <loại>/<mô tả> <!-- i18n-allow -->
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set loai_request=<loại> nhanh_goc=<cũ> nhanh_request=<mới> <!-- i18n-allow -->
```

### Two-branch model (`dev` and `main`)

- `dev` is the primary development branch (`nhanh_goc`): it keeps the full working tree including `docs/`, `tests/`, `evals/`, `graphify-out/`, and internal tooling. Open request branches from `dev` and merge them back into `dev`.
- `main` is the clean release branch (runtime plugin files only, without `docs/`, `tests/`, or dev-only scripts). Publish `dev` onto `main` without touching the working tree via:
  ```
  python3 "${CLAUDE_PLUGIN_ROOT}/scripts/build_portable.py" --sinh-main --nguon dev --nhanh-dich main
  ```

## Self-check

- `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" get` shows all three keys filled.
- `git rev-parse --abbrev-ref HEAD` returns the branch just opened.
- `git status --porcelain` is empty (or contains only carried-over docs/logs) — a dirty tree of other files means step 3b was skipped wrongly.
