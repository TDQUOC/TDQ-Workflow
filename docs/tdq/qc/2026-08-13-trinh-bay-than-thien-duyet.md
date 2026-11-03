# QC — Trình bày thân thiện ở mọi chỗ giao tiếp với user

Ngày: 2026-08-13 · Plan: ../plan/2026-08-13-trinh-bay-than-thien-duyet.md · 8 hạng mục DoD

## Q1 — Khuôn trình bày qua doc_lint — PASS

`python3 scripts/doc_lint.py skills/tdq-conventions/references/user-facing-block.md` → `exit=0`.

## Q2 — SKILL.md conventions trỏ tới khuôn và không vượt trần — PASS

`grep -c "user-facing-block" skills/tdq-conventions/SKILL.md` → `1` (≥ 1).
`wc -l` → `120` (≤ 120).

## Q3 — Bảng phase sinh ra có hàng `mode` — PASS

``python3 scripts/tdq_state.py phases-doc | grep -c '^| `mode`'`` → `1`.

## Q4 — Duyệt plan không kèm mode dừng ở phase `mode` — PASS

Trong project tạm: `approve plan --by "duyệt plan"` → `exit=0`, output
`✅ Đã ghi nhận user duyệt plan`. Đọc state: `phase= mode`, `implement_mode= None`,
`plan_approved= True`.

## Q5 — APPROVE_HINTS tách mode khỏi plan — PASS

`grep -n "APPROVE_HINTS" -A 14 hooks/scripts/_common.py`: khoá `"plan"` chỉ còn
`nhắn "duyệt plan"`, không chứa chữ `mode`; có khoá `"mode"` riêng nêu cả `main` lẫn
`subagent`; `approve_hint` in dòng `➤ Chọn cách làm:` cho khoá này.

## Q6 — tdq-plan giải thích đủ hai mode — PASS

`grep -c "subagent" skills/tdq-plan/SKILL.md` → `7` (≥ 1).
Hai dòng nghĩa tại dòng 84–85: `- A (đề xuất): main — tôi làm tuần tự…` và
`- B: subagent — tôi chia việc cho nhiều trợ lý chạy song song…`.

## Q7 — Test bảng phase — PASS

`python3 -m pytest tests/test_phase_table.py -q` → `8 passed, 20 subtests passed`.

## Q8 — Toàn bộ suite — PASS

`python3 -m pytest tests/ -q` → `520 passed, 206 subtests passed in 33.22s`, exit 0.
