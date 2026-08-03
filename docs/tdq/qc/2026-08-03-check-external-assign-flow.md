# QC — Đổi thiết kế mode external: giao cả plan / theo phase
Ngày: 2026-08-03 · Plan: ../plan/2026-08-03-check-external-assign-flow.md · Vòng: 1

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Toàn suite | `cd tests && python3 -m unittest` (repo dùng unittest, không có pytest) | `Ran 401 tests … OK` | PASS |
| Q2 | run-plan E2E mock | `python3 -m unittest test_external_task.RunPlanTest` | 8 test OK: report `plan-round-<n>.json`, 2 attempt, kind=plan bắt buộc, timeout scale (`--print-timeout 1050s` cho 2 task) | PASS |
| Q3 | parse-plan tương thích | `python3 -m unittest test_external_task.ParsePlanTest` | dòng cũ 3 model + dòng mới `khó=` đơn đều pass | PASS |
| Q4 | Doc lint | `doc_lint.py` trên spec, tdq-build/SKILL.md, tdq-plan/SKILL.md, references/external-task.md + `--pair spec plan` | exit 0 tất cả | PASS |
| Q5 | Quick lane không gãy | `python3 -m unittest test_external_task tests… + test_e2e_codex test_e2e_agy` | RunTest/RetryTest/FailTest nguyên trạng, e2e codex/agy `Ran 4 tests OK` | PASS |
| Q6 | Fix loop 2 vòng → fallback | `python3 -m unittest test_external_task.FixRoundsTest` | 2 fail → `next=fallback`, add vòng 3 bị chặn exit 1 nêu "fallback" | PASS |
| Q7 | Timeout scale theo gói | `python3 -m unittest test_external_task.PlanTimeoutTest` | 540×n, trần 3600, env override; gói fix dùng số task của gói fix (đếm `## TASK` trong file gói) | PASS |
| Q8 | Chia phase, gói ≤6, tuần tự | `python3 -m unittest test_external_task.SplitPlanTest test_external_task.TwoPhaseE2ETest` | 7 task→2 gói; ranh giới phase giữ; gói 2 chỉ giao sau khi report gói 1 done; blocked → không giao gói 2 | PASS |
| Q9 | Engine tự verify vòng 1 | `test_run_plan…test_empty_test_result_retries` | report task có `test_result` rỗng → bị từ chối, retry attempt 2 | PASS |

Kiểm bổ sung:
- Log service: `RunPlanTest.test_run_plan_logs_attempts` (run.log có `plan-round-1`, timestamp) + `test_run_plan_log_disabled` (`TDQ_EXTERNAL_LOG=0` tắt) — PASS.
- Không placeholder: `grep TODO|FIXME scripts/external_task.py` → 0 dòng.
- Hợp đồng skill (khối Dùng: graphify ở T5.3): `graphify extract . --code-only` exit 0, artifact `graphify-out/graph.json` tồn tại — PASS.
- Đồng bộ mô tả (đầu ra #9): `grep -rn "TỪNG task|MỘT task" skills/ ~/.claude/CLAUDE.md` → không còn; portable/workflow/03-plan.md + 04-build.md đã sync (test_portable_sync OK).

Kết luận vòng 1: 9/9 PASS — sang phase report.
