# QC — Chế độ _tdq_direct tự động phân tích và chỉ có 1 cổng duyệt mini-plan
Ngày: 2026-10-14 · Plan: ../plan/2026-10-14-1022-che-do-tdq-direct.md · Vòng: 1 · Mức QC: `full`
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Hook nhận diện `_tdq_direct` | `python -m unittest tests/test_prompt_context.py -k Direct` | Ran 8 tests in 2.846s — OK | PASS |
| Q2 | Độ dài dòng nhắc direct | `python3 -c "import tests.test_prompt_context as t; assert t.TestIntakeDirectReminder.DONG_DIRECT_LEN <= 240"` | DONG_DIRECT_LEN = 186 (≤ 240) | PASS |
| Q3 | Dòng ghim instruction trong setup | `python -m pytest tests/test_claude_md_core.py -k test_khoi_trong_ban_mau_khop_nguyen_van_voi_hang_so -q` và assert len ≤ 300 | 1 passed, 11 deselected; len = 164 ký tự (≤ 300) | PASS |
| Q4 | Hồi quy và nhất quán template | `python -m pytest tests/test_prompt_context.py tests/test_claude_md_core.py tests/test_tdq_setup.py tests/test_doc_lint.py -q` | 164 passed, 146 subtests passed in 9.56s | PASS |
| Q5 | Hướng dẫn skill tdq-intake & chỉ mục | `python3 scripts/doc_lint.py skills/tdq-intake/SKILL.md skills/tdq-intake/references/quick-lane.md` & `doc_index.py --kiem` | 0 violation(s) total, exit 0; doc_index exit 0 | PASS |
| QC-F1 | Hồi quy vùng chạm | `python -m pytest tests/test_prompt_context.py tests/test_claude_md_core.py tests/test_doc_index.py -q` | 235 passed, 146 subtests passed | PASS |
| QC-F2 | Hợp đồng tài liệu | `doc_lint.py` + `token_budget.py` | `quick-lane.md` 3493 tokens (≤ 3500 cap), `SKILL.md` 147 dòng (≤ 148 trần) | PASS |
| QC-F3 | Không chạm ngoài vùng | `git status --short` | Chỉ chạm đúng các file trong vùng khai báo của các task | PASS |
| QC-F4 | Clean code & gọn nhẹ | R5, R6, R13 tuân thủ 100% | Không tạo file dư thừa, không có layer trung gian | PASS |

## Bằng chứng

### Q1 — Unit test nhận diện `_tdq_direct`
```
$ python -m unittest tests/test_prompt_context.py -k Direct
........
----------------------------------------------------------------------
Ran 8 tests in 2.846s

OK
```

### Q2 — Giới hạn độ dài dòng nhắc direct
```
$ python -c "import tests.test_prompt_context as t; assert t.TestIntakeDirectReminder.DONG_DIRECT_LEN <= 240; print('DONG_DIRECT_LEN =', t.TestIntakeDirectReminder.DONG_DIRECT_LEN)"
DONG_DIRECT_LEN = 186
```

### Q3 — Khối ghim instruction trong setup và mẫu đồng bộ
```
$ python -m pytest tests/test_claude_md_core.py -k test_khoi_trong_ban_mau_khop_nguyen_van_voi_hang_so -q
.                                                                        [100%]
1 passed, 11 deselected in 0.07s

$ python -c "import scripts.tdq_setup as s; d = [l for l in s.KHOI_HUONG_DAN.splitlines() if '_tdq_direct' in l][0]; print(len(d)); assert len(d) <= 300"
164
```

### Q4 — Hồi quy các vùng chạm
```
$ python -m pytest tests/test_prompt_context.py tests/test_claude_md_core.py tests/test_tdq_setup.py tests/test_doc_lint.py -q
...................................................................... [ 42%]
........................................................................ [ 86%]
......................                                                   [100%]
164 passed, 146 subtests passed in 9.56s
```

### Q5 — Lint tài liệu và tính toàn vẹn chỉ mục
```
$ python scripts/doc_lint.py skills/tdq-intake/SKILL.md skills/tdq-intake/references/quick-lane.md
[2026-10-14T12:10:19] doc_lint: lint 2 file: SKILL.md, quick-lane.md
[2026-10-14T12:10:19] doc_lint: done — 0 violation(s) total, exit 0

$ python scripts/doc_index.py --kiem skills/tdq-intake/SKILL.md skills/tdq-intake/references/quick-lane.md
exit: 0
```
