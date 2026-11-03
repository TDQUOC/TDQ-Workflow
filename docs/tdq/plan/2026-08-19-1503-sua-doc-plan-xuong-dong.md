# QUICK — doc_plan giữ sub-bullet khi mô tả task xuống dòng

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Ngày:** 2026-08-19 · Brief: ../brief/2026-08-19-1503-sua-doc-plan-xuong-dong.md · Lane: quick
**Trạng thái:** CHỜ DUYỆT
**Ước tính sẽ dùng skill:** không có

## Phạm vi
- Trong: `doc_plan()` nhận dòng nối tiếp THỤT LỀ của mô tả task, nối vào đúng mục
  text trước đó thay vì đóng task; test khoá hành vi; đồng bộ hai bản portable.
- Trong: giữ nguyên cách đóng task hiện tại — dòng KHÔNG thụt lề (heading, `---`,
  đoạn văn) vẫn đóng task. Đây là hàng rào duy nhất ngăn văn xuôi sau danh sách task
  bị hút vào task cuối.
- NGOÀI: lint cảnh báo plan mô tả nhiều dòng; đổi khuôn plan; đổi `tdq_bench.py`.
- Bối cảnh: lỗi hiện là TIỀM ẨN, đo trên 1245 task đang có thì chưa mất dòng nào
  (chi tiết ở mục đính chính trong brief). Sửa để nó không cắn về sau.

## Task
- [x] **T1** Test đỏ trong `tests/test_team_mode.py`: plan có task mô tả 2 dòng vẫn
  đọc đủ `Chạm:`/`Cần:`; thêm ca dòng nối tiếp mang backtick đường dẫn phải vào
  `vung_file`; thêm ca heading không thụt lề vẫn đóng task — Test:
  `python3 -m pytest tests/test_team_mode.py -q` đỏ đúng 3 ca mới
  - Chạm: `tests/test_team_mode.py`
- [x] **T2** Sửa `doc_plan()`: dòng thụt lề không phải bullet thì nối vào phần tử
  cuối của `text` (cách nhau một dấu cách), không đặt `hien_tai = None` — Test: ba ca
  của T1 xanh
  - Chạm: `scripts/tdq_team.py`
  - Cần: T1
- [x] **T3** Chạy `python3 scripts/build_portable.py` để hai bản portable mang cùng
  bộ đọc — Test: `python3 -m pytest tests/test_build_portable.py -q` xanh
  - Chạm: `portable_claude/.claude/tdq/scripts/tdq_team.py`, `portable_codex/scripts/tdq_team.py`
  - Cần: T2

## Definition of Done
- `python3 -m pytest tests/test_team_mode.py tests/test_bench.py tests/test_uu_tien_song_song.py -q` xanh.
- `python3 -m pytest tests/test_build_portable.py -q` xanh.
- Đọc lại toàn bộ `docs/tdq/plan/*.md`: số task = 1245 và số dòng `Chạm:`/`Cần:` đọc
  ra không giảm so với mốc trước khi sửa (83 và 36).
- `python3 scripts/doc_lint.py` trên file plan và brief của request này thoát 0.

## QC
- Q1 test từng task: PASS — `.venv/bin/python3 -m pytest tests/test_team_mode.py -q -k DongNoiTiep`
  → trước khi sửa `3 failed, 1 passed`; sau khi sửa cả file `110 passed, 21 subtests passed`.
  T3: `pytest tests/test_build_portable.py -q` → `41 passed, 17 subtests passed`.
- Q2 DoD "test_team_mode + test_bench + test_uu_tien_song_song xanh": PASS —
  `157 passed, 80 subtests passed in 26.82s`.
- Q3 DoD "test_build_portable xanh": PASS — `41 passed, 17 subtests passed in 1.34s`.
- Q4 DoD "1245 task, số `Chạm:`/`Cần:` không giảm": PASS — đo lại ra
  `task=1248 cham=119 can=51`. Chênh 3 task là 3 task của chính plan này (1245 + 3).
  Hai số kia TĂNG chứ không giảm: 83 → 119 và 36 → 51.
- Q5 DoD "doc_lint plan + brief thoát 0": PASS — `tổng 0 vi phạm, exit 0`.

## Đo lại mức ảnh hưởng — đính chính lần hai
Lần đo trong brief nói "0 dòng bị mất" là SAI: regex kiểm chứng thiếu cờ `re.M` nên
`^` chỉ khớp đầu chuỗi, đếm ra 0 ở mọi file. Đo lại bằng chính `tdq_team.py` bản
`git HEAD` so với bản đã sửa: **60 dòng `Chạm:`/`Cần:` bị nuốt trên 10 file plan**.
Sau khi sửa còn 9 dòng, tất cả nằm ở một file và do một lỗi KHÁC (xem dưới).

## Phát hiện ngoài phạm vi — mã task `T2A.1` vô hình
`_TASK` (`scripts/tdq_team.py:33`) dùng `\*\*([A-Za-z]+[0-9.]*)\*\*`, không khớp mã có
chữ nằm sau số. File `docs/tdq/plan/2026-08-19-0121-huong-c-nap-reference.md` khai 14
task, `doc_plan` chỉ thấy 9 — mất trọn `T2A.1`…`T2B.2`. `_TASK_REF` (`\bT\d+\.\d+\b`)
cũng không nhận mã này nên `Cần: T2A.1` thành phụ thuộc rỗng. Chưa sửa: nằm ngoài
phạm vi đã duyệt.
