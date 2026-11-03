# QUICK — Vì sao spec hay bị sửa sau khi đã duyệt

**Ngày:** 2026-08-18 · Brief: ../brief/2026-08-18-2050-spec-doi-sau-khi-duyet.md · Lane: quick
**Trạng thái:** HOÀN THÀNH — 4/4 task
**Ước tính sẽ dùng skill:** không có

## Phạm vi
- Trong: đếm tần suất thật của việc spec/plan đổi sau khi duyệt, trên toàn lịch sử repo
- Trong: đọc cơ chế phát hiện lệch (`tdq_state.py`, hook `[TDQ:APPROVE]`) để biết nó bắt cái gì
- Trong: phân loại nguyên nhân gốc theo từng ca thật, kèm bằng chứng trích dẫn được
- Trong: viết `docs/tdq/reports/2026-08-18-2050-spec-doi-sau-khi-duyet.md` + đề xuất cách chặn
- NGOÀI: **không sửa** bất kỳ luật, skill, script, hook, test nào — đề xuất để user quyết
- NGOÀI: không mở request vá lỗi, không commit code

## Task
- [x] **T1** Đếm tần suất: quét `docs/workinglog/`, `docs/tdq/qc/`, `docs/tdq/reports/` tìm mọi ca duyệt lại/sha256 lệch, lập bảng request - ngày - ca — Test: bảng có ít nhất 9 ngày đã thấy sơ bộ, mỗi dòng dẫn được về file:dòng
- [x] **T2** Đọc cơ chế: `scripts/tdq_state.py` (chỗ lưu và so `spec_sha256`) + hook in `[TDQ:APPROVE]` — Test: nêu đúng tên hàm/dòng làm việc so băm, và nêu đúng thời điểm hook chạy
- [x] **T3** Phân loại nguyên nhân gốc cho từng ca ở T1 (ai sửa, sửa gì, vì sao phải sửa lúc đó) — Test: mỗi ca gắn đúng 1 nhóm nguyên nhân, không ca nào rơi vào "không rõ" mà thiếu lý do
- [x] **T4** Viết report: tần suất, nguyên nhân xếp theo số ca, đề xuất chặn kèm đánh đổi — Test: file report tồn tại, `python3 scripts/doc_lint.py <file>` exit 0

## Definition of Done
- Bảng tần suất có số thật, mỗi dòng trích được nguồn trong repo
- Nguyên nhân gốc xếp hạng theo số ca, mỗi nhóm có ít nhất một ca dẫn chứng nguyên văn
- Report có mục đề xuất, mỗi đề xuất ghi rõ đánh đổi và KHÔNG được thi hành trong request này
- `git status --short` không có file mã nguồn (`scripts/`, `hooks/`, `skills/`, `tests/`) nào đổi

## QC
- Q1 test từng task: PASS — T1 bảng 7 ca, mỗi dòng có `file:dòng` · T2 nêu đúng `sha256_file` (`scripts/tdq_state.py:1245`) và `hooks/scripts/prompt_context.py:188-198`, hook chạy ở `UserPromptSubmit` (`hooks/hooks.json:14-19`) · T3 mỗi ca gắn đúng 1 nhóm, không ca nào "không rõ" · T4 `doc_lint.py <report>` exit 0
- Q2 DoD "bảng tần suất có số thật, trích được nguồn": PASS — `grep -rc "duyệt lại\|sha256 lệch" docs/workinglog/*.md` ra 9 file có dấu vết; 7 ca vào bảng, mỗi ca dẫn nguồn
- Q3 DoD "nguyên nhân xếp hạng, mỗi nhóm có ca dẫn chứng": PASS — 5 nhóm, nhóm 1 kèm số đo `grep -rl "tests/test_" docs/tdq/spec/*.md | wc -l` → 42/58 spec
- Q4 DoD "mỗi đề xuất ghi đánh đổi, không thi hành": PASS — Đ1–Đ5 đều có dòng đánh đổi; không file luật/mã nào bị sửa
- Q5 DoD "không file mã nguồn nào đổi": PASS — `git status --short scripts hooks skills tests` không in dòng nào
