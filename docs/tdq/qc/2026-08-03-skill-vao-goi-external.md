# QC — 2026-08-03-skill-vao-goi-external

Ngày chạy: 2026-08-03 (23:1x, sau khi tick đủ 16 task). Mode: main.

| # | Hạng mục | Lệnh | Kết quả | Verdict |
|---|---|---|---|---|
| Q1 | Toàn suite | `python3 -m unittest` (từ `tests/`) | `Ran 439 tests in 42.976s OK` | PASS |
| Q2 | `skill-dump` | `python3 -m unittest test_external_task.SkillDumpTest` (trong Q1) | Nguyên văn body + references đúng thứ tự, frontmatter bỏ, skill ma exit 1 | PASS |
| Q3 | `split-plan` mcp + skills | `test_external_task.SplitPlanMcpTest` (trong Q1) | Task `(mcp)` giữa phase → 3 gói đúng thứ tự, khóa `skills` đúng | PASS |
| Q4 | Warning `run-plan` | `test_external_task.RunPlanFileWarningTest` + `CheckPacketSkillsTest` (trong Q1) | Thiếu skill → cảnh báo stderr timestamp + `run.log`, engine vẫn chạy; đủ → im lặng; không flag → không đối chiếu | PASS |
| Q5 | Khuôn AGENTS.md | `test_skill_docs.AgentsMdTemplateTest` (trong Q1) | Fence 39 dòng ≤60, đủ cụm: `tests/`, red→green, không commit, format report | PASS |
| Q6 | Contract skill docs | `test_skill_docs` (11 test, trong Q1) | tdq-build 6 cụm + 2 runner `--plan-file`; tdq-plan + template luật `(mcp)`; khuôn gói `## SKILL` cuối cả 2 khuôn; quick lane 2 cụm | PASS |
| Q7 | doc_lint spec + plan | `python3 scripts/doc_lint.py docs/tdq/spec/<slug>.md` rồi `--pair <spec> <plan>` | `spec exit=0`, `pair exit=0` | PASS |
| Q8 | Portable sync | `test_portable_sync` + `test_skill_docs.PortableExternalSyncTest` (trong Q1) | 03-plan có luật `(mcp)`; 04-build đủ 5 cụm external mới | PASS |
| Q9 | Graph | `graphify extract . --code-only` | `graphify exit=0` (3 file re-extract) | PASS |

## Đầu ra §2 (9/9 tồn tại)
1. `skill-dump` + resolver 3 tầng: `scripts/external_task.py` (skill_roots/resolve_skill/skill_dump).
2. `split-plan` mcp + khóa skills + parse_dung_lines: `scripts/external_task.py`.
3. `check_packet_skills` + `run-plan --plan-file` (warning, vẫn chạy): `scripts/external_task.py`.
4. Khuôn AGENTS.md: `skills/tdq-build/references/agents-md.md` (fence 39 dòng).
5. Khuôn gói mục `## SKILL` cuối: `skills/tdq-build/references/external-task.md` (cả 2 khuôn).
6. Nhánh external tdq-build + 2 runner: `skills/tdq-build/SKILL.md`, `agents/{codex,agy}-runner.md`.
7. Luật nhãn `(mcp)` tdq-plan: `skills/tdq-plan/SKILL.md` + `references/plan-template.md`.
8. Portable sync: `portable/workflow/03-plan.md`, `04-build.md`.
9. Unit test: `tests/test_skill_docs.py` (mới) + 8 class mới trong `tests/test_external_task.py`; suite 401 → 439.

## Ghi chú
- Log service 3 đường (skill-dump/split-plan/warning run-plan) kiểm hợp nhất ở `LogServiceUnifiedTest`, có công tắc `TDQ_EXTERNAL_LOG=0`.
- Không skip test mới; không commit nào phát sinh trong build.
