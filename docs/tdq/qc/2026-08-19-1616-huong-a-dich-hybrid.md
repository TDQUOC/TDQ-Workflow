# QC — Hướng A: dịch skill sang thể lai (hybrid)
Ngày: 2026-08-19 · Plan: ../plan/2026-08-19-1616-huong-a-dich-hybrid.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Chín hạng mục theo chín dòng DoD, cộng bốn hạng mục cố định QC-F1→F4.

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | rule ngôn ngữ bắt đúng | `.venv/bin/python3 -m pytest tests/test_doc_lint.py -q` | `64 passed in 2.73s` | PASS |
| Q2 | không báo oan | `python3 scripts/doc_lint.py docs/tdq docs/workinglog` | thoát 0 | PASS |
| Q3 | bảng phân loại phủ đủ | `.venv/bin/python3 -m pytest tests/test_ranh_gioi.py -q` | `15 passed in 0.13s` | PASS |
| Q4 | lưới không rỗng | ba phép thử ở T2.6, chép trong plan mục `## Bằng chứng T2.6` | ca xoá luật ra đúng `L005 (skills/tdq-build/SKILL.md:30)` | PASS |
| Q5 | điểm neo còn hiệu lực | `.venv/bin/python3 -m pytest tests/test_luat_skill.py -q` | `11 passed, 329 subtests passed` | PASS |
| Q6 | ngôn ngữ đúng chỗ | soát bảng ranh giới + test `test_ma_user_facing_khong_duoc_doi_neo` | 38 mã user-facing, 291 mã ly-luan; không mã user-facing nào có neo mới | PASS |
| Q7 | tiết kiệm token | `python3 scripts/skill_tokens.py --theo-phase` và đo từng file | 100.189 → 68.843 token (-31,3%); trần lane full 92.470 → 62.989 (-31,9%) | PASS |
| Q8 | ba bản đồng bộ | `.venv/bin/python3 -m pytest tests/test_build_portable.py -q` | `41 passed, 17 subtests passed` | PASS |
| Q9 | không nới lưới cũ | `git diff -- tests/ \| grep -c "^+.*skip"` | `0` | PASS |
| F1 | full suite | `cd tests && ../.venv/bin/python3 -m pytest -q` | `25 failed, 1057 passed, 1241 subtests passed` — 25 fail đều thuộc `test_skill_router.py::KhoTest`, có sẵn trước request | PASS |
| F2 | hồi quy vùng chạm | pytest 14 file test của các module trong `Chạm:` | `401 passed, 556 subtests passed` | PASS |
| F3 | ràng buộc kiến trúc | bốn phép ở mục Bằng chứng dưới | cả bốn giữ nguyên | PASS |
| F4 | clean code | năm câu tự kiểm của `clean-code.md` | năm câu đều "có" | PASS |

## Bằng chứng

### Q2 — gate ngôn ngữ đầu ra không báo oan

`python3 scripts/doc_lint.py docs/tdq docs/workinglog` thoát 0. Chạy rộng hơn cho cả
`skills/`: `doc_lint: lint 546 file … tổng 0 vi phạm, exit 0`.

### Q4 — lưới bắt được luật biến mất

Ba phép thử đã chạy ở T2.6 và chép nguyên văn trong plan, mục `## Bằng chứng T2.6`:
xoá một luật → đỏ đúng mã `L005`; khai neo mới cho mã `user-facing` → đỏ đúng
`test_ma_user_facing_khong_duoc_doi_neo`; viết lại sang tiếng Anh kèm neo mới đúng → xanh,
rồi xoá chính câu tiếng Anh đó → đỏ, vẫn nêu đúng `L005`.

### Q6 — ngôn ngữ đúng chỗ

329 mã luật, mỗi mã một nhãn trong `docs/tdq/audit/ranh-gioi-luat.md`: 38 `user-facing`,
291 `ly-luan`. Test `test_ma_user_facing_khong_duoc_doi_neo` chặn mọi mã `user-facing`
mang neo mới; lưới chính vẫn dò câu tiếng Việt cũ của đúng 38 mã đó, nên chúng còn nguyên
tiếng Việt trong skill. Hai file `phases.md` và `user-facing-block.md` giữ nguyên 0% token
đổi vì gần như chỉ chứa khuôn câu nói với user.

### Q7 — số token

Chi tiết từng file: `docs/tdq/audit/do-hybrid.md`. Đo bằng `anthropic-tokenizer` trong
`.venv-tokens/`, so bản `HEAD` với cây làm việc trong đúng một lần gọi bộ đếm.

### F1 — full suite

25 hạng mục đỏ đều nằm trong `test_skill_router.py::KhoTest::test_moi_duong_dan_khac_rong_deu_mo_duoc`
(các skill `figma-*` của plugin ngoài không mở được). Chạy chính file đó trên cây `HEAD`
lấy bằng `git archive HEAD` cũng ra `25 failed, 18 passed` — lỗi có sẵn, không do request này.

### F3 — bốn ràng buộc kiến trúc

1. "File code MỚI nằm trong `scripts/` hoặc `hooks/`": file mới duy nhất là
   `scripts/luat_phan_loai.py` (cộng hai bản sao do `build_portable.py` sinh ra).
2. "`skills/` chỉ nhắc tên lệnh của `scripts/`, cấm chép nội dung script": `git diff -- skills/`
   không thêm dòng nào bắt đầu bằng `def `/`class `/`import `/`subprocess.` — đếm được 0.
3. "`portable_*` SINH bằng `build_portable.py`, không sửa tay": chạy lại script rồi
   `tests/test_build_portable.py` xanh 41 test.
4. "`scripts/` không import `hooks/`": `grep -rn "^import hooks\|^from hooks" scripts/*.py`
   không ra dòng nào.

### F4 — năm câu tự kiểm clean code

File code đụng trong request: `scripts/doc_lint.py` (thêm rule R12) và
`scripts/luat_phan_loai.py` (mới).

- SRP: có — `R12` là một hàm kiểm riêng, `luat_phan_loai.py` chỉ lo phân loại nhãn.
- OCP: có — thêm ngôn ngữ hay nhãn mới chỉ cần thêm dòng dữ liệu, không mở thân hàm.
- LSP: có — mọi nhánh `return` của hàm mới trả cùng kiểu và cùng giao ước lỗi.
- ISP: có — không tham số nào truyền vào mà không dùng.
- DIP: có — dùng lại cổng đọc file và log service sẵn có của `doc_lint.py`, không tự viết lại.

## Kết luận

**PASS** — 13/13 hạng mục PASS, không có vòng fix.
