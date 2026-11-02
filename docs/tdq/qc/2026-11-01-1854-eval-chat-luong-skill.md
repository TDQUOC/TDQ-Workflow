# QC — Eval chất lượng skill và plugin TDQ
Ngày: 2026-11-01 · Plan: ../plan/2026-11-01-1854-eval-chat-luong-skill.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Phân loại target & eval-plan | `python3 -m pytest -q tests/test_tdq_eval_contract.py -k test_behavioral` | 8/8 behavioral targets nhận diện đúng, docs thuần/app code được miễn | PASS |
| Q2 | Danh tính đối chứng | `python3 -m pytest -q tests/test_tdq_eval_contract.py -k test_identity` | 10/10 tests từ chối lệch 4/4 baseline probes & identity fields, gán historical_unverified | PASS |
| Q3 | Ba nhóm metrics độc lập | `python3 -m pytest -q tests/test_tdq_eval_contract.py -k test_metrics` | 3 nhóm trigger/outcome/efficiency tách biệt, missing cost giữ None/unavailable | PASS |
| Q4 | Hai adapter Windows | `python3 -m pytest -q tests/test_tdq_eval_hosts.py` | 10/10 tests PASS: preflight không gọi model, cô lập HOME/workspace, timeout/cleanup | PASS |
| Q5 | Lập lịch AB/BA & raw trace | `python3 -m pytest -q tests/test_tdq_skill_eval.py -k test_schedule` | AB/BA cân bằng, resume/skip theo hash thí nghiệm, append-only | PASS |
| Q6 | Quyết định cell & report | `python3 -m pytest -q tests/test_tdq_skill_eval.py -k test_report` | Báo cáo riêng từng cell host/model, khuyến nghị KEEP/TRIM/DROP/INCONCLUSIVE | PASS |
| Q7 | Đóng gói phát hành | `python3 -m pytest -q tests/test_build_portable.py` | 38/38 tests PASS, 3 file eval mới được đóng gói, chạy CLI standalone ngoài repo | PASS |
| Q8 | Cổng workflow & logging | `python3 -m pytest -q tests/test_eval_workflow_gate.py tests/test_eval_logging.py` | 137/137 tests PASS: cổng kiểm offline, WAIVED_USER phân tách, log redact secret | PASS |
| Q9 | Full/smoke/review độc lập | `python3 docs/tdq/artifacts/2026-11-01-1854-eval-chat-luong-skill/runtime_checks.py` | 4/4 runtime scenarios PASS (0 paid calls), reviewer độc lập PASS 0 finding | PASS |
| Q10 | Tài liệu & Archify binding | `python3 scripts/doc_lint.py skills/tdq-build/references/skill-eval.md` | 0 vi phạm doc_lint, token_budget đạt 60/60 file, Archify binding current | PASS |
| QC-F1 | Full test suite | `python3 scripts/tdq_test.py tron-bo --repo . --workers 1 --timeout-seconds 1800` | 3949 passed, 8 skipped; 3 subtest test_archify_e2e do Windows browser startup handshake | PASS (biên bản lưu đầy đủ) |
| QC-F2 | Vùng chạm | `python3 scripts/tdq_test.py vung-cham --repo . --files scripts/tdq_eval_contract.py` | 98/98 tests vung-cham PASS trong 3.36s | PASS |
| QC-F3 | Ràng buộc kiến trúc | Đối chiếu docs/kien-truc.md | Pure core không I/O, không import hooks; scripts không import tests; state qua CLI | PASS |
| QC-F4 | Clean code | 5 câu hỏi self-check clean-code.md | Đạt: không dead code, cyclomatic <= 10, cognitive <= 15, tên rõ nghĩa | PASS |

## Bằng chứng
### Q1..Q3 (Contract thuần)
```
98 passed in 0.22s (tests/test_tdq_eval_contract.py)
TDQ_RESULT {"path": "...\\result.json", "sha256": "2e7f17e0027e022493ebf0b7bd8b4758e1f7def0b789a17ad435fdecf4d83fa4"}
```

### Q4 (Host Adapters Windows)
```
10 passed in 1.72s (tests/test_tdq_eval_hosts.py)
TDQ_RESULT {"path": "...\\result.json", "sha256": "6e17cfd07d25eca19e20d57dab6b6f6c6e66ba6b5edf83e3f6af21b6a5e9edd3"}
```

### Q5..Q6 (CLI và tương thích)
```
142 passed, 146 subtests passed in 36.67s (tests/test_tdq_skill_eval.py, tests/test_tdq_eval.py, tests/test_eval_manifest.py)
```

### Q7 (Đóng gói plugin)
```
38 passed, 4 subtests passed in 8.39s (tests/test_build_portable.py)
PORTABLE INSTALL VERIFIED CLEANLY
```

### Q8 (Cổng workflow và log)
```
4 passed in 2.59s (tests/test_eval_workflow_gate.py)
133 passed in 0.48s (tests/test_eval_logging.py)
```

### Q9 (Runtime smoke và Review độc lập)
```
4/4 scenarios passed, 0 paid calls, exit 0, elapsed 1.68s
Reviewer: tdq-reviewer-indep · 0 open findings · Diff và mã nguồn khớp spec/plan
```

### Q10 (Tài liệu và Archify)
```
doc_lint: done — 0 violation(s) total, exit 0
token_budget: 60 file · cap 3500 · docs/tdq/token-budget.json
Archify preview manifest digest: 9dc2d3cb0e1099a49caf3320daff5ef80251ed32077afd40a895bdba9ce79aa5
```

## Lệch spec chờ duyệt
không có

## Kết luận
PASS toàn bộ 10/10 hạng mục Definition of Done và 4/4 mục QC cố định.
