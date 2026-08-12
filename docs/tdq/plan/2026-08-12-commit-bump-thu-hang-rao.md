# QUICK — Commit phần siết tick + bump 0.11.3

Ngày: 2026-08-12 · Brief: ../brief/2026-08-12-commit-bump-thu-hang-rao.md · Lane: quick
Trạng thái: CHỜ DUYỆT
Năng lực: không có

Chốt từ interview: bump `0.11.3` (1B) · chỉ commit local, KHÔNG push (2A) ·
tách 2 commit: feature rồi bump (3A) · `graphify-out/` đi kèm commit 1.

## Phạm vi
- Trong: viết mục CHANGELOG `0.11.3`; bump `.claude-plugin/plugin.json`; 2 commit trên
  branch hiện tại `tdq-plan-uoc-tinh-phut`; kiểm lại cây làm việc sạch và test xanh.
- NGOÀI: push lên remote; tạo tag; mở PR; đổi `marketplace.json`; đồng bộ cache plugin
  ở `~/.claude`; đụng lại mã của request trước.

## Task
- [x] **T1** Viết mục `## 0.11.3 — 2026-08-12` vào đầu `CHANGELOG.md` (dưới dòng "Mới
  nhất trên cùng"), nêu: TDQ:TICK chặn thật, miễn trừ `tests/**`, quick lane học `[~]`,
  bất biến deny thu hẹp — Test: `head -12 CHANGELOG.md | grep -c '0.11.3'` → `1`
- [x] **T2** Bump `.claude-plugin/plugin.json` `0.11.2` → `0.11.3` — Test: `python3 -c "import json;print(json.load(open('.claude-plugin/plugin.json'))['version'])"` → `0.11.3`
- [x] **T3** Chạy lại full-suite + doc_lint trước khi commit — Test: `python3 -m pytest tests/ -q` xanh và `python3 scripts/doc_lint.py CHANGELOG.md` không lỗi
- [x] **T4** Commit 1 (feature): mọi file của request siết tick + `graphify-out/` +
  `docs/` + `docs/tdq/STATE.md`, KHÔNG kèm `plugin.json`/`CHANGELOG.md` — Test: `git show --stat HEAD | grep -c 'plugin.json\|CHANGELOG'` → `0`
- [x] **T5** Commit 2 (bump): đúng 2 file `plugin.json` + `CHANGELOG.md`, message
  `tdq-workflow 0.11.3 — hàng rào tick chặn thật ở lane quick` — Test: `git show --stat HEAD --name-only | tail -5` chỉ có 2 file đó
- [x] **T6** Kiểm sau commit: cây làm việc chỉ còn file do chính turn này sinh ra (plan,
  brief, working log); không có commit nào chứa tên AI hay "Co-Authored-By" — Test: `git log -2 --format='%s%n%b' | grep -ci 'claude\|generated\|co-authored'` → `0`

## Definition of Done
- `python3 -m pytest tests/ -q` — toàn bộ test xanh.
- `python3 -c "...json..."` in đúng `0.11.3`; `head -12 CHANGELOG.md` có mục `0.11.3`.
- `git log --oneline -2` cho đúng 2 commit mới, commit bump nằm trên.
- `git show --stat HEAD` chỉ liệt kê `plugin.json` và `CHANGELOG.md`.
- `git log -2 --format='%s%n%b' | grep -ci 'claude\|generated\|co-authored'` → `0`.
- `git status --porcelain` không còn file mã nguồn nào dirty (chỉ còn tài liệu TDQ của
  chính request này).
- Bài thử hàng rào: trong lúc làm, mỗi task lần lượt mang `[~]` rồi `[x]`; không lần nào
  plan nhảy thẳng từ `[ ]` sang `[x]` hàng loạt.

## QC
- Q1 test từng task (T1–T6): PASS — chạy đúng lệnh `Test:` của từng task, xem Q2–Q7.
- Q2 DoD "toàn bộ test xanh": PASS — `python3 -m pytest tests/ -q` → `479 passed, 140 subtests passed in 44.57s`
- Q3 DoD "version 0.11.3 + CHANGELOG": PASS — `json...['version']` → `0.11.3`; `head -12 CHANGELOG.md | grep -c '0.11.3'` → `1`
- Q4 DoD "2 commit mới, bump nằm trên": PASS — `git log --oneline -3` → `4ce02ea` bump trên `63203b3` feature, dưới là `c06569c` cũ
- Q5 DoD "commit bump chỉ 2 file": PASS — `git show --stat HEAD --name-only` → `.claude-plugin/plugin.json`, `CHANGELOG.md`
- Q6 DoD "message không dính tên AI": PASS — `git log -2 --format='%s%n%b' | grep -ci 'claude|generated|co-authored'` → `0`
- Q7 DoD "không còn file mã nguồn dirty": PASS — `git status --porcelain` chỉ còn plan của chính request này + `graphify-out/*` do hook rebuild chạy sau commit
- Q8 DoD "bài thử hàng rào": PASS — lần sửa `CHANGELOG.md` đầu tiên (chưa tick) bị deny với `[TDQ:TICK]`; sau khi đánh `[~]` T1 thì qua. Sáu task lần lượt `[ ] → [~] → [x]`, không lần nào nhảy hàng loạt.
