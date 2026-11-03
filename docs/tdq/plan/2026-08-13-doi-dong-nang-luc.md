# QUICK — Đổi nhãn dòng "Năng lực" thành "Ước tính sẽ dùng skill"

Ngày: 2026-08-13 · Brief: ../brief/2026-08-13-doi-dong-nang-luc.md · Lane: quick
Trạng thái: CHỜ DUYỆT
Năng lực: không có

## Phạm vi
- Trong: đổi đúng nhãn `Năng lực:` → `Ước tính sẽ dùng skill:` ở 3 chỗ user-facing của
  chế độ nhanh (express): `skills/tdq-intake/SKILL.md:88`,
  `skills/tdq-intake/references/quick-lane.md:25`,
  `skills/tdq-intake/references/skill-inventory.md:68`. Không đổi giá trị hiển thị
  (vẫn `<skill sẽ DÙNG, hoặc "không có">`).
- NGOÀI: không đổi heading `### Năng lực dùng được` trong brief/spec §3b (chế độ chuyên
  sâu) — đó là tên trường cấu trúc tài liệu, khác dòng tóm tắt 1-liner của chế độ nhanh.

## Task
- [x] **T1** Đổi nhãn ở đúng 3 vị trí trên — Test: `grep -rn "^Năng lực:" skills/tdq-intake/`
  → rỗng; `grep -rln "Ước tính sẽ dùng skill" skills/tdq-intake/SKILL.md
  skills/tdq-intake/references/quick-lane.md skills/tdq-intake/references/skill-inventory.md`
  → đủ 3 file.
- [x] **T2** `doc_lint.py` trên 3 file đã sửa — Test:
  `python3 scripts/doc_lint.py skills/tdq-intake/SKILL.md
  skills/tdq-intake/references/quick-lane.md
  skills/tdq-intake/references/skill-inventory.md` → exit 0

## Definition of Done
- `grep -rn "^Năng lực:" skills/tdq-intake/` → rỗng (không còn nhãn cũ ở 3 vị trí này).
- `python3 scripts/doc_lint.py <3 file trên>` → exit 0.

## QC
- Q1 test từng task: PASS — T1 `grep -rn "^Năng lực:" skills/tdq-intake/` → rỗng;
  `grep -rln "Ước tính sẽ dùng skill" <3 file>` → đủ 3 file. T2
  `python3 scripts/doc_lint.py skills/tdq-intake/SKILL.md
  skills/tdq-intake/references/quick-lane.md
  skills/tdq-intake/references/skill-inventory.md` → exit 0.
- Q2 DoD "grep nhãn cũ rỗng": PASS — cùng lệnh T1, output rỗng.
- Q3 DoD "doc_lint exit 0": PASS — cùng lệnh T2, exit 0.
