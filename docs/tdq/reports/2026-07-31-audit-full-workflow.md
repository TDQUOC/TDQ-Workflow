# REPORT — Audit toàn diện tdq-workflow 0.6.0

Ngày: 2026-07-31 · Spec: ../spec/2026-07-31-audit-full-workflow.md · Plan: ../plan/2026-07-31-audit-full-workflow.md · QC: ../qc/2026-07-31-audit-full-workflow.md

## Đã làm gì
- Review tĩnh toàn workflow (7 script, 7 agent def, skills + portable + CLAUDE.md §10): 44 findings A1–A44, trong đó 33 issue S/M đã fix, 11 noted/pass có lý do.
- 2 sample E2E thật: S1 quick external model thấp (retry→fallback đúng luật) + S2 full mini với 3 nhánh sự cố (approve mơ hồ, init đè, engine hỏng).
- Harden contract cho model thấp: exit-code table trong 4 runner/scout def, cơ chế chờ Bash nền thật, raw-output persist khi validate FAIL, terminal state lane quick, warning separator route, truncation không cắt inline-code.
- Chốt 2 mục PENDING 0.6.0: token deep search 128.126 ≤ 250k; trigger Agent type `search-scout` chạy đúng.
- Đồng bộ docs 2 bản (skills plugin-root ↔ portable relative) qua generator `phases-doc [--plugin-root]` + portable sync tests.

## Đầu ra
| Đầu ra | Đường dẫn |
|---|---|
| Sổ findings A1–A44 + bảng QC Q1–Q10 | docs/tdq/qc/2026-07-31-audit-full-workflow.md |
| Fix code | scripts/{tdq_state,external_task,external_models,search_task,doc_lint,skill_inventory}.py, hooks/scripts/prompt_context.py |
| Agent def viết lại | agents/{agy-runner,codex-runner,search-runner,search-scout,tdq-qc-tester,tdq-reviewer}.md |
| Docs đồng bộ | skills/tdq-{intake,spec}/SKILL.md, references/{deep-search,phases,qc}.md, portable/* |
| Test mới | tests/ (367 test, tăng từ 338) |

## Cách chạy / cách kiểm
```
python3 -m unittest discover -s tests
python3 scripts/doc_lint.py --pair docs/tdq/spec/<slug>.md docs/tdq/plan/<slug>.md
```

## Kết quả QC
Q1–Q10 PASS vòng 1, bằng chứng lệnh + output thật trong file QC.

## Quyết định đáng chú ý
- Chỉ harden contract, không thêm engine local mới — theo phạm vi user chốt.
- A3/A42 để noted không fix: lỗi năng lực model và thiết kế chủ đích (rào nằm ở tầng skill), có đánh giá kèm.
- Sửa CLAUDE.md §10 (thời điểm chốt engine+model, câu deep-search) để hết mâu thuẫn với skill và pass lint R5.

## Giới hạn còn lại
- Agent def sửa ở T4.5.8/T4.5.9 cần reload plugin ở phiên mới mới có hiệu lực đầy đủ.
- 6 điểm L (A33/A34/A37/A38/A39/A41) chỉ noted, chưa fix — ảnh hưởng thấp.

## Đề xuất tiếp theo
- Bump version plugin + changelog 0.6.1 khi commit đợt fix này.
- Đợt sau xử lý gộp 6 điểm L nếu muốn sạch tuyệt đối.
