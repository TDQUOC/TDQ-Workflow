# QC — Mở nhánh git theo từng request
Ngày: 2026-09-05 · Plan: ../plan/2026-09-05-0833-gitflow-nhanh-theo-request.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

18 dòng DoD + 4 hạng mục cố định QC-F1..QC-F4 = 22 hạng mục.

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | `default_state()` đủ ba khoá mới, schema 5 | `pytest -q -k ba_khoa_moi` | 1 passed, 3 subtests | PASS |
| Q2 | File schema 4 nạp lên không mất khoá | `pytest -q -k doc_schema_4` | 1 passed, 9 subtests | PASS |
| Q3 | Ba khoá ghi/đọc được qua CLI | `pytest -q -k ghi_doc_qua_cli` | 2 passed | PASS |
| Q4 | Đề xuất loại nằm trong câu hỏi chọn lane | `pytest -q -k de_xuat_loai` | 1 passed, 5 subtests | PASS |
| Q5 | Bước mở nhánh chỉ ở lane `full`/`quick` | `pytest -q -k mo_nhanh_dung_lane` | 1 passed, 3 subtests | PASS |
| Q6 | Có bước `git status` và cách xử lý repo bẩn | `pytest -q -k repo_ban` | 1 passed | PASS |
| Q7 | Bước 10 đủ hai nhánh trả lời, mỗi nhánh có lệnh git | `pytest -q -k buoc_muoi` | 1 passed, 2 subtests | PASS |
| Q8 | `## 7. Git` đủ 5 loại, giữ 4 gạch đầu dòng cũ | `pytest -q -k luat_ten_nhanh` | 1 passed, 9 subtests | PASS |
| Q9 | Tên nhánh mẫu qua `git check-ref-format` | `pytest -q -k ten_nhanh_hop_le` | 1 passed, 5 subtests | PASS |
| Q10 | Không tên nhánh mẫu nào mang tiền tố bị cấm | `pytest -q -k khong_tien_to_cam` | 1 passed, 5 subtests | PASS |
| Q11 | `tdq_team.py` không còn tạo nhánh tích hợp riêng | `pytest -q -k khong_nhanh_tich_hop` | 1 passed | PASS |
| Q12 | Vòng `mo` → `hop` → `don` sạch nhánh và worktree | `pytest -q -k vong_doi_day_du` | 1 passed | PASS |
| Q13 | Ba bundle CLEAN | `tdq_checkportable.py check --root <mỗi bundle>` | CLEAN 94 / 145 / 87 file | PASS |
| Q14 | Repo thật không mọc nhánh hay worktree | `diff` với mốc chụp trước khi làm | worktree khớp; nhánh chỉ lệch đúng phần đã xoá có chủ đích | PASS |
| Q15 | Nhánh mồ côi hết ở local và `origin` | `git branch -a \| grep -c tich-hop` | `0` | PASS |
| Q16 | Bộ test của request xanh toàn bộ | `pytest -q` ba file gitflow | 18 passed, 54 subtests | PASS |
| Q17 | Suite không vượt mốc đỏ có sẵn | `pytest -q` một lần | 105 failed / 1590 passed, mốc đỏ HEAD 112 failed / 1539 passed | PASS |
| Q18 | `doc_lint.py` exit 0 trên brief/spec/plan/qc/report | `doc_lint.py <5 file>` | 0 violation, exit 0 | PASS |
| QC-F1 | Toàn bộ suite | `pytest -q > /tmp/qc-run.log` | 105 failed, 1590 passed, 1 skipped | PASS |
| QC-F2 | Hồi quy vùng `Chạm:` theo 4 module | pytest theo từng module | M1 122 · M2 124 · M3 184 · M4 81, không ca nào đỏ | PASS |
| QC-F3 | Ràng buộc kiến trúc spec §5 | đọc mã + `grep` | cả hai dòng còn giữ | PASS |
| QC-F4 | Clean code — 5 câu tự kiểm | đọc lại mã đã sửa | 5/5 "có" | PASS |

## Bằng chứng

### Q1–Q12
```
ba_khoa_moi :: 1 passed, 17 deselected, 3 subtests passed
doc_schema_4 :: 1 passed, 17 deselected, 9 subtests passed
ghi_doc_qua_cli :: 2 passed, 16 deselected
de_xuat_loai :: 1 passed, 17 deselected, 5 subtests passed
mo_nhanh_dung_lane :: 1 passed, 17 deselected, 3 subtests passed
repo_ban :: 1 passed, 17 deselected
buoc_muoi :: 1 passed, 17 deselected, 2 subtests passed
luat_ten_nhanh :: 1 passed, 17 deselected, 9 subtests passed
ten_nhanh_hop_le :: 1 passed, 17 deselected, 5 subtests passed
khong_tien_to_cam :: 1 passed, 17 deselected, 5 subtests passed
khong_nhanh_tich_hop :: 1 passed, 17 deselected
vong_doi_day_du :: 1 passed, 17 deselected
```

### Q13
```
CLEAN    94 file(s) match the manifest
CLEAN    145 file(s) match the manifest
CLEAN    87 file(s) match the manifest
```

### Q14
`git worktree list` trùng khít mốc chụp. `git branch -a` lệch đúng ba dòng, không dòng nào là
nhánh mới mọc: mất `tdq/2026-08-23-1623-mindmap-html-hai-lop/tich-hop` ở local và ở
`remotes/origin/`, thêm dòng hiển thị `remotes/origin/HEAD -> origin/main` do `git fetch --prune`.

### Q15
```
$ git branch -a | grep -c 'tich-hop'
0
```

### Q16
```
18 passed, 54 subtests passed in 2.29s
```

### Q17
```
105 failed, 1590 passed, 1 skipped, 1591 subtests passed in 109.64s
FAILED tests/test_rules_library.py::ChiMuc::test_chi_muc
FAILED tests/test_skill_router.py::KhoTest::test_so_ban_ghi_khop_skill_inventory
```
Mốc đỏ có sẵn, đo trong worktree tách riêng ở `HEAD`: `112 failed, 1539 passed, 16 skipped`.
Hai ca đỏ còn lại đều có sẵn từ trước và không dính việc này: `index.md` của thư viện rule thiếu
`bash.md`; kho router ghi 224 bản trong khi máy này quét ra 284 skill.

### QC-F2
```
M1 state:       122 passed, 39 subtests passed
M2 luật & khuôn: 124 passed, 359 subtests passed
M3 đội:         184 passed, 1 skipped, 23 subtests passed
M4 bundle:      81 passed, 17 subtests passed
```
M2 đỏ 1 ca ở lần chạy đầu — `test_luat_skill.py::test_so_dong_ghi_trong_bang_van_tro_dung_cho`,
độ lệch số dòng 122/329 (37.1%) so với 111/329 (33.7%) ở `HEAD`. Đây là nợ có sẵn mà các sửa đổi
của lượt này làm nặng thêm, nên đã dựng lại cột số dòng (task QC1.1 trong plan): dò được đúng một
vị trí cho cả 329 neo, cập nhật 122 dòng, ca này xanh. Không node nào thiếu test.

### QC-F3
- `CLI | scripts/ | ...` — mã mới chỉ nằm trong `scripts/tdq_state.py` và `scripts/tdq_team.py`,
  không sinh thư mục hay tầng nào mới.
- `Chỉ scripts/tdq_state.py được ghi docs/tdq/state.json` — ba khoá mới chỉ được ghi qua CLI
  `tdq_state.py set`; `tdq_team.py` gọi `tdq_state.load(project, heal=False)` để ĐỌC, không ghi.

### QC-F4
- SRP — có. `_nhanh_hien_tai` chỉ đọc tên nhánh; `_thay_doi_da_theo_doi` chỉ lọc thay đổi đã
  theo dõi; `_nhanh_tich_hop` chỉ chọn tên nhánh gom.
- OCP — có. Thêm một loại request là thêm một dòng trong bảng của
  `skills/tdq-intake/references/nhanh-request.md`, không phải mở thân hàm nào.
- LSP — có. `_nhanh_tich_hop` mọi nhánh `return` đều trả về `str`; `_thay_doi_da_theo_doi` luôn
  trả về `str` (rỗng nghĩa là sạch), không có nhánh nào trả `None`.
- ISP — có. `_nhanh_tich_hop(project, slug)` dùng cả hai tham số: `project` để nạp state,
  `slug` cho tên dự phòng.
- DIP — có. Tra nhánh request đi qua `tdq_state.load` chứ không tự đọc `state.json`; mọi lệnh git
  vẫn đi qua helper `_git` sẵn có.

## Kết luận
PASS toàn bộ 22/22 hạng mục. Một task fix QC1.1 đã thêm vào plan và làm xong trong vòng 1.
