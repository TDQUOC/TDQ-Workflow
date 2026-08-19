# QUICK — nhận mã task có chữ sau số (T2A.1, T2.4b)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Ngày:** 2026-08-19 · Brief: ../brief/2026-08-19-1544-doc-ma-task-co-chu.md · Lane: quick
**Trạng thái:** CHỜ DUYỆT
**Ước tính sẽ dùng skill:** không có

## Phạm vi
- Trong: nới ba regex mã task (`_TASK_LINE`, `_TASK`, `_TASK_REF`) để nhận chữ nằm
  sau số; test khoá; đồng bộ hai bản portable.
- Trong: chốt hướng NỚI thay vì siết. Sáu task mang mã lạ đã nằm trong plan lịch sử;
  bỏ sót im lặng làm hỏng cổng chống ngừng, còn báo lỗi lint chỉ đổi lỗi này thành
  lỗi khác mà vẫn không đọc được plan cũ.
- NGOÀI: thêm luật lint về khuôn mã task; đổi khuôn plan trong skill.
- NGOÀI: sửa sáu plan cũ cho khớp khuôn — chúng là hồ sơ đã đóng, không sửa lại.

## Task
- [x] **T1** Test đỏ trong `tests/test_team_mode.py`: `doc_plan` đọc được task mã
  `T2A.1` và `T2.4b`; `Cần: T2A.1` vào đúng đồ thị phụ thuộc; `plan_tick_state` đếm
  đủ task và bật `has_doing` khi `[~]` nằm trên task mã lạ — Test:
  `python3 -m pytest tests/test_team_mode.py -q` đỏ đúng 3 ca mới
  - Chạm: `tests/test_team_mode.py`
- [x] **T2** Nới lớp ký tự thành `[A-Za-z][A-Za-z0-9.]*` cho `_TASK_LINE` và `_TASK`;
  `_TASK_REF` thành `\bT\d+[A-Za-z]*\.\d+[a-z]?\b` — Test: ba ca của T1 xanh
  - Chạm: `scripts/tdq_state.py`, `scripts/tdq_team.py`
  - Cần: T1
- [x] **T3** Chạy `python3 scripts/build_portable.py` — Test:
  `python3 -m pytest tests/test_build_portable.py -q` xanh
  - Chạm: `portable_claude/.claude/tdq/scripts/tdq_team.py`, `portable_codex/scripts/tdq_team.py`
  - Cần: T2

## Definition of Done
- `python3 -m pytest tests/test_team_mode.py tests/test_state.py tests/test_stop_gate.py tests/test_edit_gate.py tests/test_bench.py tests/test_uu_tien_song_song.py -q` xanh.
- `python3 -m pytest tests/test_build_portable.py -q` xanh.
- Quét `docs/tdq/plan/*.md` bằng regex mới: đọc ra 1254 task (mốc cũ 1248), không còn
  mã nào bị bỏ sót; `doc_plan` trên file `huong-c` ra đủ 14 task.
- `python3 scripts/doc_lint.py` trên plan và brief của request này thoát 0.

## QC
- Q1 test từng task: PASS — `pytest tests/test_team_mode.py -q -k MaTaskCoChu` đỏ
  `3 failed` trước khi sửa, sau khi sửa cả file `113 passed, 21 subtests passed`.
  T3: `pytest tests/test_build_portable.py -q` → `41 passed, 17 subtests`.
- Q2 DoD "6 file test hồi quy xanh": PASS — `286 passed, 83 subtests passed in 66.07s`.
- Q3 DoD "test_build_portable xanh": PASS — `41 passed, 17 subtests passed in 2.90s`.
- Q4 DoD "quét plan ra 1254 task, không còn mã bị bỏ sót, `huong-c` ra 14": PASS một
  phần, có đính chính. Đọc ra **1257** task — chênh 3 vì chính plan này thêm 3 task
  (1254 + 3). `huong-c` ra đúng **14** task. Sáu mã trong phạm vi (`T2A.1`…`T2B.2`,
  `T2.4b`) đã đọc được hết. Nhưng vế "không còn mã nào bị bỏ sót" viết quá rộng: xem
  mục dưới.
- Q5 DoD "doc_lint plan + brief thoát 0": PASS — `tổng 0 vi phạm, exit 0`.

## Phát hiện — 47 dòng task theo khuôn TIỀN sử vẫn ngoài tầm regex
Năm plan từ 2026-07-28 tới 2026-08-05 dùng khuôn mã hoàn toàn khác khuôn hiện hành:
`**1 — A4a**`, `**1.1.**`, `**T1.1 (A)**`, `**QC-1**`. Tổng 47 dòng.

Không nới regex cho chúng, có chủ ý. Chúng là hồ sơ đã đóng, không plan nào trong số
đó còn được cổng tick hay `mo-phong` đọc. Nới tới mức nuốt được `**1 — A4a**` thì
regex hết khả năng phân biệt task với dòng đậm bất kỳ, đổi một lỗi im lặng lấy một
lỗi im lặng khác. Khuôn fix vòng QC hiện hành (`**QC1.1**`) đã khớp regex mới.
