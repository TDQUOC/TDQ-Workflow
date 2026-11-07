# QC — Tối ưu thời gian xử lý TDQ Workflow
Ngày: 2026-11-07 · Plan: ../plan/2026-11-07-0928-toi-uu-runtime-toan-dien.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Baseline receipts & partial label | `python -c "import json,pathlib; p=pathlib.Path('docs/tdq/artifacts/2026-11-07-0928-toi-uu-runtime-toan-dien/baseline.json'); x=json.loads(p.read_text(encoding='utf-8')); assert x.get('source_fingerprint') and x.get('environment') and x.get('samples')"` | exit 0; file exists, fingerprint & samples valid | PASS |
| Q2 | P0 health, graph freshness, receipt invalidation | `python -m unittest discover -s tests -p "test_auto_update_setup.py"; python -m unittest discover -s tests -p "test_tdq_lsp.py"; python -m unittest tests.test_tdq_finish; pytest tests/test_tdq_test_receipt.py tests/test_tdq_test_process.py` | 16 tests auto_update PASS, 32 tests tdq_lsp PASS, 23 tests tdq_finish PASS, 134 passed 1 skipped pytest | PASS |
| Q3 | P1 parity workers/cache & semantic hook | `pytest tests/test_tdq_runtime_bench.py -k "not test_full_pytest_suite"; python -m unittest discover -s tests -p "test_search_observe.py"; python -m unittest discover -s tests -p "test_read_gate.py"; python -m unittest discover -s tests -p "test_search_gate.py"` | 20 passed bench, 27 passed search_observe, 17 passed read_gate, 34 passed search_gate | PASS |
| Q4 | P2 batch read/route | `python scripts/doc_lint.py skills/tdq-intake/SKILL.md skills/tdq-intake/references/quick-lane.md skills/tdq-build/references/runtime-speed.md; python -m unittest discover -s tests -p "test_compliance_protocol.py"` | doc_lint 0 lỗi, 16 passed compliance tests | PASS |
| Q5 | Report MD + HTML verify | `python scripts/tdq_archify.py verify --document docs/tdq/reports/2026-11-07-0928-toi-uu-runtime-toan-dien.md --manifest docs/tdq/reports/2026-11-07-0928-toi-uu-runtime-toan-dien.manifest.json` | status=current, binding.valid=true, manifest.status=current | PASS |

## Lệch spec chờ duyệt

Không có.

## Kết luận

PASS toàn bộ 5/5 mục Definition of Done.
