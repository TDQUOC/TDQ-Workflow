# QC — Khắc phục lỗi Unknown skill tdq-intake do thiếu namespace plugin
Ngày: 2026-10-11 · Plan: ../plan/2026-10-11-1539-fix-plugin-skill-namespace.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Namespace skill trong setup, hook, docs | `git grep "tdq-workflow:tdq-intake" scripts/tdq_setup.py hooks/scripts/prompt_context.py docs/notes/user-level-install.md` | Có mặt đầy đủ trong cả 3 vị trí | PASS |
| Q2 | Test hook prompt_context | `pytest tests/test_prompt_context.py -q` | 37 passed, 114 subtests passed, chuỗi intake $\le 160$ chars | PASS |
| Q3 | Test auto-update setup | `pytest tests/test_auto_update_setup.py -q` | 6 passed | PASS |
| Q4 | Test lint, luật và cấu trúc | `pytest tests/test_doc_lint.py tests/test_docs_consistency.py tests/test_luat_skill.py tests/test_skill_shape.py -q` | 102 passed, 345 subtests passed, drift 0.00% | PASS |

## Bằng chứng
### Q1
```
$ git grep "tdq-workflow:tdq-intake" scripts/tdq_setup.py hooks/scripts/prompt_context.py docs/notes/user-level-install.md
docs/notes/user-level-install.md:- Mọi yêu cầu mới → skill `tdq-workflow:tdq-intake` (hoặc `tdq-intake` nếu cài cục bộ): tóm tắt, đề xuất lane kèm lý do và hỏi người dùng chọn **quick** (việc nhỏ, rõ) hay **full** (Analysis → Spec → Plan → Implement → QC → Report). Xem trạng thái: skill `tdq-workflow:tdq-status` (hoặc `tdq-status`).
hooks/scripts/prompt_context.py:              "already running, open tdq-workflow:tdq-intake (or tdq-intake).")
scripts/tdq_setup.py:- Mọi yêu cầu mới từ người dùng BẮT BUỘC phải mở bằng skill `tdq-workflow:tdq-intake` (hoặc `tdq-intake` nếu cài cục bộ) và chạy theo pipeline của TDQ Workflow (quick hoặc full). Tuyệt đối KHÔNG tự ý chuyển sang plan mode của harness (`EnterPlanMode`) khi nhận yêu cầu.
```

### Q2
```
$ pytest tests/test_prompt_context.py -q
37 passed, 114 subtests passed in 3.46s
```

### Q3
```
$ pytest tests/test_auto_update_setup.py -q
6 passed in 0.13s
```

### Q4
```
$ pytest tests/test_doc_lint.py tests/test_docs_consistency.py tests/test_luat_skill.py tests/test_skill_shape.py -q
102 passed, 345 subtests passed in 4.25s
```

## Lệch spec chờ duyệt
không có

## Kết luận
PASS toàn bộ
