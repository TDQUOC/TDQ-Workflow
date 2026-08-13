# QC — Trình bày lại full chat sau khi bị hook chặn

Ngày: 2026-08-13 · Plan: ../plan/2026-08-13-trinh-lai-sau-hook-chan.md
Kết quả chung: 5/5 PASS, không có vòng fix.

## Q1 — Luật mới có trong quy ước, đủ 3 ý — PASS

Lệnh: `grep -n "NGUYÊN VĂN" skills/tdq-conventions/SKILL.md`

```
28:   việc, lỗi tool) → message cuối phải in **LẠI NGUYÊN VĂN 100%** khối đó. Gồm tóm tắt,
```

Đọc lại §1 mục 5 (dòng 27–31): đủ 3 ý — khi nào phải in lại (turn còn chạy tiếp sau khi
đã in khối user-facing: hook chặn, sót việc, lỗi tool) · in LẠI NGUYÊN VĂN 100% gồm tóm
tắt, câu hỏi, đủ option, dòng `➤ Duyệt:` · đặt NGAY SAU dòng `✓ [TDQ:<MÃ>]`.

## Q2 — File quy ước sạch lint — PASS

Lệnh: `python3 scripts/doc_lint.py skills/tdq-conventions/SKILL.md` → không in gì, `exit=0`.
Kèm: `wc -l < skills/tdq-conventions/SKILL.md` → `118` (trần R6 là 120).

## Q3 — Cả hai điểm chặn đều mang mệnh lệnh in lại — PASS

Lệnh: `grep -c "in LẠI NGUYÊN VĂN" hooks/scripts/stop_gate.py` → `2`
(một cho `[TDQ:LOG]` dòng 146, một cho `[TDQ:TICK]` dòng 167).

## Q4 — Test riêng cho hành vi in lại — PASS

Lệnh: `python3 -m pytest tests/test_stop_gate.py -k reprint -q`

```
....                                                                     [100%]
4 passed, 42 deselected in 0.16s
```

## Q5 — Toàn bộ test suite xanh — PASS

Lệnh: `python3 -m pytest tests/ -q`

```
503 passed, 178 subtests passed in 34.63s
```
