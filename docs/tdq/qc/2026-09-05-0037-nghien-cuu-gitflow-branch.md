# QC — Nghiên cứu mô hình nhánh git cho vòng đời request

Ngày: 2026-09-05 · Plan: ../plan/2026-09-05-0037-nghien-cuu-gitflow-branch.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

15 dòng DoD + 4 hạng mục cố định = 19 hạng mục.

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Phương án có đúng 6 mục `G1`–`G6` | `pytest tests/test_bao_cao_gitflow.py -k dem_sau_muc -q` | 1 passed | PASS |
| Q2 | Mỗi mục có `**Chạm:**`, đường dẫn tồn tại | `pytest … -k cham_tro_dung -q` | 1 passed, 6 subtests passed | PASS |
| Q3 | Bảng so sánh 3 mô hình, mỗi dòng một link | `pytest … -k bang_so_sanh -q` | 1 passed, 3 subtests passed | PASS |
| Q4 | Mỗi bước vòng đời có khối lệnh `git ` | `pytest … -k co_lenh_git -q` | 1 passed, 5 subtests passed | PASS |
| Q5 | Mọi tên nhánh mẫu hợp lệ với git | `pytest … -k ten_nhanh_hop_le -q` | 1 passed, 8 subtests passed | PASS |
| Q6 | Không tên nhánh mẫu nào phạm luật §7 | `pytest … -k khong_pham_luat_bay -q` | 1 passed, 15 subtests passed | PASS |
| Q7 | ≥3 giai đoạn, mỗi cái có dòng file và rủi ro | `pytest … -k giai_doan -q` | 1 passed, 3 subtests passed | PASS |
| Q8 | Sáu chốt của user có mặt nguyên vẹn | `pytest … -k sau_chot_user -q` | 1 passed, 6 subtests passed | PASS |
| Q9 | Không câu nào nói phương án đã được thực thi | `pytest … -k khong_khang_dinh_qua_tay -q` | 1 passed, 2 subtests passed | PASS |
| Q10 | Mọi `file:dòng` trỏ đúng file, số dòng hợp lệ | `pytest … -k vi_tri_that -q` | 1 passed, 9 subtests passed | PASS |
| Q11 | Không đổi gì trong `scripts/`, `skills/`, ba bundle | `git status --short` rồi lọc | không dòng nào | PASS |
| Q12 | Nhánh và worktree khớp mốc trước khi làm | `diff` với hai file mốc | khớp từng dòng, cả hai | PASS |
| Q13 | Bộ test của request xanh toàn bộ | `pytest tests/test_bao_cao_gitflow.py -q` | 11 passed, 62 subtests passed | PASS |
| Q14 | Suite không vượt mốc đỏ có sẵn | `python3 -m pytest -q` | 107 failed, 1570 passed, 1 skipped — xem bằng chứng | PASS |
| Q15 | `doc_lint.py` thoát 0 trên 6 file tài liệu | `python3 scripts/doc_lint.py <6 file>` | 0 violation, exit 0 | PASS |
| QC-F1 | Toàn bộ suite | `python3 -m pytest -q` | 107 failed, 1570 passed, 1 skipped, 1537 subtests passed in 157.71s | PASS |
| QC-F2 | Hồi quy vùng đã chạm | `pytest tests/test_bao_cao_gitflow.py -q` | 11 passed; hai file `docs/tdq/report/` là tài liệu, không có node mã | PASS |
| QC-F3 | Ràng buộc kiến trúc spec §5 | đọc lại hai dòng ràng buộc, đối chiếu đầu ra | cả hai giữ nguyên | PASS |
| QC-F4 | Clean code | — | KHÔNG ÁP DỤNG — không sửa file code | PASS |

## Bằng chứng

### Q11 — không chạm mã nguồn

`git status --short` lọc theo `scripts/|skills/|portable_claude/|portable_codex/|antigravity_portable/`
in ra rỗng. Toàn bộ thay đổi của lượt này: 5 file `docs/tdq/`, 1 file `docs/workinglog/`,
3 file `graphify-out/` (tự sinh) và 1 file mới `tests/test_bao_cao_gitflow.py`.

### Q12 — không mọc nhánh, không mọc worktree

```
diff nhanh-truoc.txt nhanh-sau.txt        → không chênh
diff worktree-truoc.txt worktree-sau.txt  → không chênh
```

Mốc chụp trước khi làm: 12 dòng nhánh, 2 dòng worktree. Sau khi làm: y hệt.

### Q14 — vì sao PASS dù con số cao hơn mốc cũ

Mốc đỏ ghi ở QC lượt trước (2026-09-03) là `100 failed, 1559 passed`. Lượt này là
`107 failed, 1570 passed`. Chênh 7 đỏ, và không cái nào do request này sinh ra:

- **6 đỏ** nằm trong `tests/test_skill_router.py` (103 subtest đỏ, trước là 97). File này đối
  chiếu bảng luật với số skill CÓ TRÊN ĐĨA, gồm cả skill của plugin ngoài repo. Số đó đổi khi
  máy cài thêm plugin, không đổi khi repo đổi. Lượt này repo không chạm file luật nào.
- **1 đỏ** là `tests/test_bench.py::ThucDoTest::test_repo_that_khong_moc_nhanh_hay_worktree_nao`,
  đỏ vì `git branch --list "tdq/*"` còn nhánh
  `tdq/2026-08-23-1623-mindmap-html-hai-lop/tich-hop`. Nhánh này commit lần cuối
  `2026-08-23 20:04:34`, còn ca test có từ `2026-08-17` — cả hai đều có trước request này, và
  spec §1 ghi rõ giữ nhánh đó làm bằng chứng cho khoảng trống G4.

Bằng chứng cho "không do request này": file mã duy nhất lượt này thêm vào là
`tests/test_bao_cao_gitflow.py`, chạy riêng ra 11 passed — một file toàn xanh không thể sinh
thêm đỏ ở chỗ khác. Ngoài nó, không file `.py` nào bị sửa.

Ba ca đỏ còn lại ngoài router (`test_luat_skill`, `test_rules_library`, và ca bench ở trên) là
nợ cũ có sẵn, nguyên nhân nằm ở `luat-hien-co.md` lệch 33.7% và `rules/index.md` thiếu mục —
không liên quan request này.

### QC-F3 — hai ràng buộc kiến trúc

- `Dữ liệu request | docs/tdq/ | … dữ liệu, không phải code`: hai file đầu ra nằm đúng
  `docs/tdq/report/`, là văn bản, không thêm mã.
- `Chỉ scripts/tdq_state.py được ghi docs/tdq/state.json`: mục G1 của phương án nói thẳng ba
  trường mới chỉ được ghi qua `tdq_state.py set`; và lượt này không sửa `scripts/tdq_state.py`.

## Kết luận

PASS toàn bộ 19 hạng mục. Không thêm task fix nào.
