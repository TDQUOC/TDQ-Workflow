# PLAN — Trình bày lại full chat sau khi bị hook chặn

Ngày: 2026-08-13 · Spec: ../spec/2026-08-13-trinh-lai-sau-hook-chan.md · Lane: full
Trạng thái: HOÀN THÀNH
Mode thực thi: main — chỉ 2 file mã/tài liệu, các task đụng chung `hooks/scripts/stop_gate.py`
và phụ thuộc chặt (sửa chuỗi xong mới sửa được test), chia worktree tốn hơn làm thẳng.

## P1 — Sửa lời chặn của hook

- [x] **T1.1** (n2 e5m) Đổi `reason` của điểm chặn `[TDQ:LOG]` trong
  `hooks/scripts/stop_gate.py`: bỏ câu bảo tự thêm mục `## HH:MM`, thay bằng lệnh
  `tdq_finish.py`, nối thêm mệnh lệnh in LẠI NGUYÊN VĂN khối chat cuối — Test:
  `grep -c "in LẠI NGUYÊN VĂN" hooks/scripts/stop_gate.py` ra ≥ 1 và
  `grep -c "HH:MM" hooks/scripts/stop_gate.py` ra 0.
- [x] **T1.2** (n2 e4m) Nối mệnh lệnh in LẠI NGUYÊN VĂN vào `reason` của điểm chặn
  `[TDQ:TICK]` cùng file — Test: `grep -c "in LẠI NGUYÊN VĂN" hooks/scripts/stop_gate.py`
  ra đúng 2.
- [x] **T1.3** (n3 e8m) Thêm test `test_reprint_*` vào `tests/test_stop_gate.py`: kích hoạt
  từng điểm chặn, khẳng định `reason` chứa cụm `in LẠI NGUYÊN VĂN` và `len(reason) <= 300` —
  Test: `python3 -m pytest tests/test_stop_gate.py -k reprint` exit 0.
- [x] **T1.4** (n2 e6m) Chạy toàn bộ bộ test, sửa mọi chỗ so khớp cứng nguyên văn `reason`
  cũ (4 file có nhắc `stop_gate`) — Test: `python3 -m pytest tests/ -q` exit 0.

## P2 — Sửa quy ước

- [x] **T2.1** (n3 e8m) Thêm luật vào `skills/tdq-conventions/SKILL.md` §1 nêu đủ 3 ý:
  khi nào phải in lại (turn còn chạy tiếp sau khi đã in khối user-facing) · in lại
  NGUYÊN VĂN 100% khối đó · đặt SAU dòng `✓ [TDQ:<MÃ>]`. Giữ file trong trần 120 dòng của
  `doc_lint` R6, cắt chữ thừa ở §1 nếu cần — Test:
  `python3 scripts/doc_lint.py skills/tdq-conventions/SKILL.md` exit 0 và
  `wc -l < skills/tdq-conventions/SKILL.md` ≤ 120.

## P3 — QC & report

- [x] **T3.1** (n2 e6m) Chạy đủ 5 hạng mục QC theo §6 spec, ghi bằng chứng thật vào
  `docs/tdq/qc/2026-08-13-trinh-lai-sau-hook-chan.md` — Test: file tồn tại, có đúng 5 mục
  Q1–Q5, mỗi mục có lệnh + output thật.
- [x] **T3.2** (n1 e5m) Viết `docs/tdq/reports/2026-08-13-trinh-lai-sau-hook-chan.md`
  dài 10–20 dòng — Test: `wc -l` trong khoảng 10–20 và `doc_lint` exit 0.

## Ghi chú phạm vi

- Log service: BỎ theo spec §4 — không tạo runtime mới; đường log `_info` sẵn có trong
  `stop_gate.py` (dòng 138, 157) không bị đụng tới.
- Không đổi điều kiện chặn và thời điểm chặn của `stop_gate.py`, chỉ đổi câu chữ `reason`.
- Không sửa `edit_gate.py`, `bash_gate.py`, và các skill con `tdq-*`.

## Definition of Done

Trỏ về §6 spec, mỗi dòng kiểm được bằng đúng một lệnh:

- Q1: `grep -n "NGUYÊN VĂN" skills/tdq-conventions/SKILL.md` ra dòng luật mới, đọc lại đủ 3 ý.
- Q2: `python3 scripts/doc_lint.py skills/tdq-conventions/SKILL.md` exit 0.
- Q3: `grep -c "in LẠI NGUYÊN VĂN" hooks/scripts/stop_gate.py` ra đúng `2`.
- Q4: `python3 -m pytest tests/test_stop_gate.py -k reprint` exit 0.
- Q5: `python3 -m pytest tests/ -q` exit 0.
