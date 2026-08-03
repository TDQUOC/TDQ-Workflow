# REPORT — Đổi thiết kế mode external: giao cả plan / theo phase

Ngày: 2026-08-03 · Spec: ../spec/2026-08-03-check-external-assign-flow.md · Plan: ../plan/2026-08-03-check-external-assign-flow.md · QC: ../qc/2026-08-03-check-external-assign-flow.md

## Đã làm gì
- Thêm `run-plan` vào `scripts/external_task.py`: giao CẢ gói plan/phase/fix 1 lần gọi, 2 attempt, timeout 540s×số task (trần 3600s, env override), report `plan-round-<n>.json` kind="plan", từ chối report thiếu `test_result` (engine phải tự verify vòng 1).
- Thêm `split-plan` (plan >6 task → chia gói ≤6 theo ranh giới phase) và `fix-rounds` (sổ `fix-rounds.json`, tối đa 2 vòng fix rồi bắt buộc fallback Claude).
- Schema report `external_report_schema.json` → oneOf (task đơn | plan) với discriminator `kind`.
- Viết lại luồng external trong `skills/tdq-build/SKILL.md` + khuôn gói `references/external-task.md` (3 khuôn: task đơn, gói plan/phase, gói fix) — verify 3 tầng: engine tự verify → Claude verify phase → Claude verify tổng; lệnh trigger LUÔN do subagent runner chạy.
- Cập nhật `agents/codex-runner.md` + `agents/agy-runner.md` (nhận gói, gọi `run-plan`), `skills/tdq-plan/SKILL.md` (1 model mức "khó" cho cả plan), đồng bộ `~/.claude/CLAUDE.md` mục 9 và bản portable 03-plan/04-build.
- Bổ sung 22 test mới (RunPlan/SplitPlan/FixRounds/PlanTimeout/PlanSchema/TwoPhaseE2E) + sửa test schema cũ.

## Đầu ra
| Đầu ra | Đường dẫn |
|---|---|
| Wrapper run-plan/split-plan/fix-rounds | scripts/external_task.py |
| Schema oneOf | scripts/external_report_schema.json |
| Luồng external mới | skills/tdq-build/SKILL.md, references/external-task.md |
| Runner nhận gói | agents/codex-runner.md, agents/agy-runner.md |
| Chốt 1 model | skills/tdq-plan/SKILL.md |
| Đồng bộ mô tả | ~/.claude/CLAUDE.md §9, portable/workflow/03-plan.md, 04-build.md |
| Test | tests/test_external_task.py |

## Cách chạy / cách kiểm
```
cd tests && python3 -m unittest            # toàn suite
python3 scripts/external_task.py split-plan <plan>   # xem cách chia gói
```

## Kết quả QC
Vòng 1: 9/9 hạng mục PASS (Q1 toàn suite 401 test OK) — chi tiết: ../qc/2026-08-03-check-external-assign-flow.md

## Quyết định đáng chú ý
- CHANGELOG bổ sung entry 0.6.2 còn thiếu (nợ từ hôm trước) để gỡ chặn test_docs_consistency — theo luật "chặn kỹ thuật → tự chọn".
- Đồng bộ luôn bản portable 03-plan/04-build (ngoài scope T4.2) vì test_portable_sync bắt lệch — tránh drift âm thầm.
- Không tự commit; không có commit gỡ chặn nào.

## Giới hạn còn lại
- E2E với engine thật (codex/agy chạy thật một plan) chưa chạy — QC dùng mock binary theo đúng scope spec.
- `test_result` chỉ bị bắt buộc khác rỗng, không kiểm nội dung output test thật — verify tầng 2 của Claude bù chỗ này.

## Đề xuất tiếp theo
- Chạy thử 1 request thật mode external lane full để kiểm flow end-to-end với engine thật.
