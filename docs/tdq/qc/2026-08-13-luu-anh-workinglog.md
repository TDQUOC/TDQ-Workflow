# QC — Lưu & nhúng ảnh đính kèm vào working log

Spec: ../spec/2026-08-13-luu-anh-workinglog.md · Plan: ../plan/2026-08-13-luu-anh-workinglog.md

| # | Hạng mục kiểm | Lệnh/cách kiểm | Kết quả |
|---|---|---|---|
| Q1 | `tdq-conventions/SKILL.md` §6 có đủ 3 chốt (git, phạm vi áp dụng, tên/thư mục) | Đọc lại đoạn quy ước mới (dòng ~75-83) | **PASS** — có đủ: "track trong git ... không gitignore", "Áp dụng cho mọi ảnh user gửi kèm trong turn đổi repo, không cần tự đánh giá 'có liên quan'", đích `docs/workinglog/assets/<active_request hoặc "misc">/<n>.<ext>` |
| Q2 | `doc_lint.py` pass | `python3 scripts/doc_lint.py skills/tdq-conventions/SKILL.md` | **PASS** — exit 0 (1 lần FAIL ban đầu do câu 62 từ vượt R5, đã tách câu, lần 2 exit 0) |
| Q3 | Cơ chế hoạt động đúng thực nghiệm | `test -f docs/workinglog/assets/2026-08-13-luu-anh-workinglog/1.png` (PASS) và `grep -q '!\[test\]' docs/workinglog/2026-08-13.md` (PASS) | **PASS** — file PNG mẫu (1x1, hợp lệ theo `file`) tồn tại đúng path quy ước; dòng `![test](assets/2026-08-13-luu-anh-workinglog/1.png)` đã nằm trong working log 16:54, do chính `tdq_finish.py --log` ghi verbatim, không cần sửa script |

Full suite: `python3 -m pytest -q` → 499 passed, 178 subtests passed (không giảm so với
trước, không có test mới vì việc thuần văn bản quy ước — không có runtime để test).

## Kết luận
3/3 hạng mục DoD PASS. Không có vòng fix. Việc thuần sửa 1 file quy ước
(`tdq-conventions/SKILL.md`), không đụng code Python — không có unit test riêng theo
đúng spec §4 (Log service: BỎ, Test: QC thủ công thay unit test).
