# QUICK — Spec không giữ lệnh kiểm, băm bỏ vùng sổ sách

**Ngày:** 2026-08-18 · Brief: ../brief/2026-08-18-2205-spec-khong-ghi-lenh-kiem.md · Lane: quick
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
**Trạng thái:** HOÀN THÀNH
**Ước tính sẽ dùng skill:** không có

## Phạm vi
- Trong: băm spec/plan bỏ vùng sổ sách đầu file, dùng CHUNG một hàm cho cả CLI lẫn hook
- Trong: luật mới cấm spec ghi đường dẫn test và cờ lệnh trong §6, chỉ áp cho spec từ 2026-08-19
- Trong: cập nhật khuôn spec và `qc.md` cho khớp cơ chế mới
- NGOÀI: Đ3 (nới quyền tự duyệt) và Đ4 (dời cổng duyệt sau reviewer) — user đã loại
- NGOÀI: sửa 42 spec cũ hay rải dòng miễn trừ lint vào chúng

## Task
- [x] **T1** Hàm `sha256_noi_dung(path)` băm từ heading `##` đầu tiên trở đi (không có heading thì băm cả file); `spec_sha256`/`plan_sha256` dùng nó — Chạm: `scripts/tdq_state.py`, `tests/test_state.py` — Test: `python3 -m pytest tests/test_state.py -q -k sha` xanh, có ca "đổi dòng Trạng thái thì sha KHÔNG đổi" và ca "đổi nội dung §1 thì sha ĐỔI"
- [x] **T2** Hook so băm gọi đúng hàm của T1 thay vì băm cả file — Chạm: `hooks/scripts/prompt_context.py`, `tests/test_prompt_context.py` — Test: `python3 -m pytest tests/test_prompt_context.py -q -k sha` xanh, ca sửa header không sinh `[TDQ:APPROVE]`
- [x] **T3** Rule R11: spec lane full từ 2026-08-19 trở đi không được ghi `tests/test_*` hay cờ `-k` trong §6 — Chạm: `scripts/doc_lint.py`, `tests/test_doc_lint.py` — Test: `python3 -m pytest tests/test_doc_lint.py -q -k r11` xanh, có fixture bẩn + sạch + ca spec cũ không bị bắt
- [x] **T4** Khuôn spec: §6 chỉ ghi điều kiện PASS, nói rõ lệnh kiểm nằm ở plan — Chạm: `skills/tdq-spec/references/spec-template.md` — Test: `python3 scripts/doc_lint.py skills/tdq-spec/references/spec-template.md` exit 0 và `grep -c "lệnh kiểm" <file>` ≥ 1
- [x] **T5** `qc.md` bỏ đoạn dặn chịu đựng sha lệch, thay bằng luật mới — Chạm: `skills/tdq-build/references/qc.md` — Test: `grep -c "làm sha256 lệch" skills/tdq-build/references/qc.md` ra 0, `doc_lint` file đó exit 0
- [x] **T7** (phát hiện lúc làm T2) `tdq_checkstatus` cũng tự băm để so ca lệch D3 — phải dùng chung hàm của T1, không thì D3 kêu oan mọi request — Chạm: `scripts/tdq_checkstatus.py`, `tests/test_check_status.py` — Test: `python3 -m pytest tests/test_check_status.py -q -k d3` xanh, có ca sửa dòng sổ sách KHÔNG ra D3
- [x] **T6** Đồng bộ portable + chạy suite — Chạm: `portable_claude/`, `portable_codex/` — Test: `python3 scripts/build_portable.py` rồi `python3 -m pytest -q` 0 đỏ

## Definition of Done
- Sửa dòng `Trạng thái`/`Bản` của spec đã duyệt KHÔNG còn sinh cảnh báo `[TDQ:APPROVE]`
- Sửa nội dung mục đánh số của spec VẪN sinh cảnh báo — cổng an toàn không bị vô hiệu
- Spec mới ghi `tests/test_*` hoặc `-k` trong §6 thì `doc_lint` exit khác 0; 42 spec cũ vẫn exit 0
- `python3 -m pytest -q` 0 đỏ và `git status --short portable_claude portable_codex` ổn định qua hai lần build

## QC

| # | Hạng mục | Kết quả | Bằng chứng |
|---|---|---|---|
| Q1 | Sửa dòng sổ sách của spec đã duyệt không sinh `[TDQ:APPROVE]` | PASS | Dựng repo thử ở scratchpad, duyệt spec rồi đổi `Trạng thái`+`Bản`: hook đếm được 0 cảnh báo |
| Q2 | Sửa nội dung mục đánh số vẫn sinh cảnh báo | PASS | Cùng repo thử, thêm một câu vào §1: hook ra 1 cảnh báo `[TDQ:APPROVE]` |
| Q3 | Spec mới ghi lệnh kiểm thì lint chặn; spec cũ không bị bắt | PASS | File slug 2026-08-20 báo `[R11] spec ghi đường dẫn file test`, exit 1; `doc_lint.py docs/tdq/spec` trên 58 spec sẵn có exit 0 |
| Q4 | Suite xanh, portable ổn định | PASS | `python3 -m pytest -q` 988 passed, 1239 subtests; hai lần `build_portable.py` cho cùng một `git status --short` |
| Q5 | Lệnh `Test:` của từng task chạy được | PASS | T1 6 passed · T2 2 passed · T3 5 passed · T7 2 passed · T4 lint exit 0 và `grep -c "lệnh kiểm"` ra 4 · T5 `grep -c "làm sha256 lệch"` ra 0, lint exit 0 |

Lệch so với luật lane: quick từ 3 task tách rời trở lên thì được sinh agent con, nhưng phiên
này có chỉ thị cấm gọi Agent tool nên toàn bộ T1–T7 làm inline ở main.
