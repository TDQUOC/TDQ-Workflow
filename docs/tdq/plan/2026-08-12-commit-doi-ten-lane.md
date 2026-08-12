# QUICK — Commit phần đổi nhãn lane + bump 0.11.4

Ngày: 2026-08-12 · Brief: ../brief/2026-08-12-commit-doi-ten-lane.md · Chế độ: nhanh (express)
Trạng thái: CHỜ DUYỆT
Năng lực: không có

Chốt: commit local, KHÔNG push · tách 2 commit (feature → bump) · `graphify-out/` đi
kèm commit feature · branch hiện tại `tdq-plan-uoc-tinh-phut`.

## Phạm vi
- Trong: chạy lại full-suite trước khi commit; 2 commit; kiểm cây làm việc và message.
- NGOÀI: push, tag, PR, `marketplace.json`, đồng bộ cache plugin `~/.claude`, sửa lại mã
  của request trước.

## Task
- [x] **T1** (n1 e3m) Chạy full-suite + `doc_lint` trước khi commit — Test: `python3 -m pytest tests/ -q` xanh và `python3 scripts/doc_lint.py CHANGELOG.md` exit 0
- [~] **T2** (n3 e8m) Commit 1 (feature): mọi file của request đổi nhãn (`scripts/`, `hooks/`, `skills/`, `portable/`, `README.md`, `tests/`, `docs/tdq/*`, `graphify-out/`), KHÔNG kèm `plugin.json`/`CHANGELOG.md` — Test: `git show --stat HEAD | grep -c 'plugin.json\|CHANGELOG'` → `0`
- [ ] **T3** (n3 e6m) Commit 2 (bump): đúng 2 file `plugin.json` + `CHANGELOG.md`, message `tdq-workflow 0.11.4 — nhãn chế độ nhanh/chuyên sâu cho hai lane` — Test: `git show --stat HEAD --name-only | tail -4` chỉ có 2 file đó
- [ ] **T4** (n1 e4m) Kiểm sau commit: không commit nào chứa tên AI hay "Co-Authored-By"; cây làm việc không còn file mã nguồn dirty — Test: `git log -2 --format='%s%n%b' | grep -ci 'claude\|generated\|co-authored'` → `0`

## Definition of Done
- `python3 -m pytest tests/ -q` xanh.
- `git log --oneline -2` cho đúng 2 commit mới, commit bump nằm trên.
- `git show --stat HEAD` chỉ liệt kê `plugin.json` và `CHANGELOG.md`.
- `git log -2 --format='%s%n%b' | grep -ci 'claude\|generated\|co-authored'` → `0`.
- `git status --porcelain` không còn file mã nguồn dirty (chỉ còn tài liệu TDQ của
  chính request này).
- Không có commit nào được push: `git status -sb` báo branch đi trước remote.
