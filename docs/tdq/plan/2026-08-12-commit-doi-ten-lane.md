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
- [x] **T2** (n3 e8m) Commit 1 (feature): mọi file của request đổi nhãn (`scripts/`, `hooks/`, `skills/`, `portable/`, `README.md`, `tests/`, `docs/tdq/*`, `graphify-out/`), KHÔNG kèm `plugin.json`/`CHANGELOG.md` — Test: `git show --stat HEAD | grep -c 'plugin.json\|CHANGELOG'` → `0`
- [x] **T3** (n3 e6m) Commit 2 (bump): đúng 2 file `plugin.json` + `CHANGELOG.md`, message `tdq-workflow 0.11.4 — nhãn chế độ nhanh/chuyên sâu cho hai lane` — Test: `git show --stat HEAD --name-only | tail -4` chỉ có 2 file đó
- [x] **T4** (n1 e4m) Kiểm sau commit: không commit nào chứa tên AI hay "Co-Authored-By"; cây làm việc không còn file mã nguồn dirty — Test: `git log -2 --format='%s%n%b' | grep -ci 'claude\|generated\|co-authored'` → `0`

## Definition of Done
- `python3 -m pytest tests/ -q` xanh.
- `git log --oneline -2` cho đúng 2 commit mới, commit bump nằm trên.
- `git show --stat HEAD` chỉ liệt kê `plugin.json` và `CHANGELOG.md`.
- `git log -2 --format='%s%n%b' | grep -ci 'claude\|generated\|co-authored'` → `0`.
- `git status --porcelain` không còn file mã nguồn dirty (chỉ còn tài liệu TDQ của
  chính request này).
- Không có commit nào được push: `git status -sb` báo branch đi trước remote.

## QC
- Q1 test từng task (T1–T4): PASS — chạy đúng lệnh `Test:` của từng task; bằng chứng ở Q2–Q7.
- Q2 DoD "full-suite xanh": PASS — `python3 -m pytest tests/ -q` → `493 passed, 178 subtests passed in 34.92s`
- Q3 DoD "2 commit mới, bump nằm trên": PASS — `git log --oneline -3` → `2ed5810` bump trên `efa462b` feature, dưới là `4ce02ea` cũ
- Q4 DoD "commit bump chỉ 2 file": PASS — `git show --stat HEAD --name-only` → `.claude-plugin/plugin.json`, `CHANGELOG.md`
- Q5 DoD "message sạch tên AI": PASS — `git log -2 ... | grep -ci 'claude|generated|co-authored'` → `0`
- Q6 DoD "không còn mã nguồn dirty": PASS — `git status --porcelain` chỉ còn plan của chính request này + `graphify-out/*` do hook rebuild chạy SAU commit
- Q7 DoD "không push": PASS — `git status -sb` → `## tdq-plan-uoc-tinh-phut`, không có phần `...origin/`, tức branch chưa từng đẩy lên remote
