# Mốc trước khi quốc tế hoá

Ngày: 2026-08-22 · Request: 2026-08-21-2351-quoc-te-hoa-workflow · Task: T1.1

## Test suite

`python3 -m pytest tests/ -q` → **37 failed, 1166 passed, 1369 subtests passed** (88s).
Toàn bộ 37 lỗi nằm ở `tests/test_skill_router.py` và đã đỏ TRƯỚC request này.
Mốc so sánh ở T9.2: không được có lỗi mới ngoài 37 lỗi này.

## Dòng chứa ký tự tiếng Việt theo tầng

| Tầng | Số file | Tổng dòng | Dòng có tiếng Việt |
|---|---|---|---|
| `skills/**/*.md` | 44 | 3681 | 1105 |
| `hooks/**/*.py` | 6 | 1021 | 331 |
| `scripts/**/*.py` | 26 | 11392 | 2768 |
| `tests/**/*.py` | 55 | 14469 | 2222 |
| `evals/**` | 24 | 643 | 239 |
| `agents/*.md` | 3 | 108 | 22 |
| `docs/kien-truc.md` | 1 | 50 | 30 |
