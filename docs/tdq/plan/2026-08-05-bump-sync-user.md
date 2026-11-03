# PLAN (quick) — 2026-08-05-bump-sync-user

## Phạm vi

**In:**
- Bump `.claude-plugin/plugin.json` `version` 0.7.0 → 0.8.0 + thêm mục CHANGELOG.md
  tóm tắt 2 batch việc kể từ 0.7.0: audit token vòng 3 + 16 đề xuất P0/P1 workflow
  (`f14d16b`), luật đặt tên sub-agent nâng lên global CLAUDE.md.
- Sync cache user-level đúng quy trình đã ghi ở `docs/notes/user-level-install.md`:
  `claude plugin marketplace update tdq-local` rồi
  `claude plugin update tdq-workflow@tdq-local` — xác nhận `installed_plugins.json`
  đổi từ `0.6.2` sang `0.8.0`.
- Commit (bump version + CHANGELOG); `installed_plugins.json`/cache nằm ngoài repo
  nên không commit được, chỉ xác minh bằng lệnh đọc.

**Out:** không đổi nội dung tính năng nào khác trong turn này (chỉ version/changelog).

## Task

- [x] **T1** Sửa `.claude-plugin/plugin.json` version → `0.8.0` — Test:
  `grep '"version"' .claude-plugin/plugin.json` = `0.8.0` PASS.
- [x] **T2** Thêm mục `## 0.8.0 — 2026-08-05` vào đầu `CHANGELOG.md`, tóm tắt 2 batch
  việc (audit+P0/P1 workflow, luật sub-agent global) — Test: `doc_lint.py CHANGELOG.md`
  exit 0 PASS (kèm sửa 1 câu dài R5 tồn tại sẵn từ mục 0.3.2 để lint sạch cả file).
- [x] **T3** Chạy `claude plugin marketplace update tdq-local` rồi
  `claude plugin update tdq-workflow@tdq-local` — Test:
  `installed_plugins.json` `tdq-workflow@tdq-local.version` = `0.8.0` PASS (từ 0.6.2).
- [x] **T4** Ghi working log + `graphify extract . --code-only`, chạy full test suite
  — Test: entry mới trong `docs/workinglog/2026-08-05.md`; suite 585/585 PASS.
- [x] **T5** Commit (`.claude-plugin/plugin.json`, `CHANGELOG.md` + file working
  log/graphify) theo đúng quy ước git (không AI trailer) — Test: `git log -1
  --oneline` phản ánh đúng.

## DoD

- `plugin.json` = 0.8.0, CHANGELOG có mục mới, lint sạch.
- Cache user-level (`installed_plugins.json`) phản ánh 0.8.0.
- Test suite PASS, đã commit.
