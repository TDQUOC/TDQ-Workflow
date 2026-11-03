# REPORT — Lưu & nhúng ảnh đính kèm vào working log (`2026-08-13-luu-anh-workinglog` · lane full · mode main · 3 task tick đủ)

Đã làm: P1 thêm quy ước ảnh vào `skills/tdq-conventions/SKILL.md` §6 (copy từ image-cache
sang `docs/workinglog/assets/<slug>/<n>.<ext>`, track git, chèn markdown vào chuỗi `--log`,
áp dụng mọi ảnh trong turn đổi repo) + `doc_lint.py` · P2 test bằng chứng cơ chế (file PNG
mẫu + dòng markdown thật trong working log).
Kết quả: 0 dòng code Python đổi (không cần sửa `tdq_finish.py` — script đã ghi verbatim
chuỗi `--log`) · 1 quy ước mới trong `tdq-conventions` §6.
Kiểm: `doc_lint.py skills/tdq-conventions/SKILL.md` exit 0 (1 lần FAIL R5 câu quá dài, đã
sửa) · full suite `pytest -q` 499 passed/178 subtests (không giảm) · QC 3/3 mục DoD PASS
(`docs/tdq/qc/2026-08-13-luu-anh-workinglog.md`).
Đầu ra: `skills/tdq-conventions/SKILL.md` (quy ước) · bằng chứng
`docs/workinglog/assets/2026-08-13-luu-anh-workinglog/1.png` + dòng embed trong
`docs/workinglog/2026-08-13.md` (16:54).
Giới hạn: chưa có cơ chế tự động dọn ảnh cũ/nén ảnh (ngoài phạm vi, đã ghi rõ ở spec §1
NGOÀI phạm vi); rủi ro riêng tư (screenshot nhạy cảm bị commit git) được user chấp nhận
lúc duyệt câu hỏi 1, không có bước giảm thiểu tự động.
Git: chưa commit.
