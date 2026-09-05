# The request branch — five types, the commands, the naming rule

Used at steps 2 and 3b of [tdq-intake](../SKILL.md). Every request in lane `full` or `quick`
works on a branch of its own and merges back when the report is done. Tier `nhỏ` opens none.

## When it applies

The user has settled the lane and `init` has run, in a project that already has a git repo.
No repo → skip; the three state keys stay empty and step 11 of the report skips too.

## What to do

### The five types

| Loại | Dùng khi |
|---|---|
| `feature` | thêm hành vi mới |
| `bugfix` | thứ đã dựng chạy sai |
| `hotfix` | hỏng đang chặn việc ngay lúc này |
| `chore` | bump phiên bản, phụ thuộc, dọn dẹp — hành vi không đổi |
| `docs` | chỉ sửa tài liệu |

Propose the type inside the lane question of step 2, never as a second question. The user
answers one line and both are settled.

### The name

`<loại>/<mô tả>` — `<mô tả>` is the slug's kebab tail, no accents. Samples:
`feature/login-gui`, `bugfix/state-mat-nhanh-goc`, `hotfix/hook-treo-turn`,
`chore/bump-phien-ban`, `docs/kien-truc-module`. The separator is a forward slash and nothing
else: `git check-ref-format --branch` rejects the backslash form. The banned prefixes of
`tdq-conventions` §7 still apply.

### The commands

```
git status --porcelain                 # not empty → STOP, print the files, ask the user
git rev-parse --abbrev-ref HEAD        # this is nhanh_goc
git switch -c <loại>/<mô tả>
python3 "${CLAUDE_PROJECT_DIR}/.claude/tdq/scripts/tdq_state.py" set loai_request=<loại> nhanh_goc=<cũ> nhanh_request=<mới>
```

## Self-check

- `python3 "${CLAUDE_PROJECT_DIR}/.claude/tdq/scripts/tdq_state.py" get` shows all three keys filled.
- `git rev-parse --abbrev-ref HEAD` returns the branch just opened.
- `git status --porcelain` is empty — a dirty tree means step 3b was skipped wrongly.
