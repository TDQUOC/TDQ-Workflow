# REPORT — Bỏ cổng clean code, thay bằng luật SOLID (`2026-08-16-1300-bo-cong-clean-code` · lane full · mode main · 18 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P1 viết `skills/tdq-conventions/references/clean-code.md` — 5 nguyên tắc SOLID,
mỗi luật hai bản đọc (khi có class / khi chỉ có hàm-module), ví dụ ĐÚNG-SAI trỏ file thật,
checklist 5 câu · P2 §11 conventions nạp luật, trần dòng skill 130→133, `doc_lint` R9 phủ
thêm `clean-code.md` · P3 gỡ cổng hỏi khỏi `tdq-spec/SKILL.md` (bước 1b) và
`spec-template.md` (dòng `Clean code: BẬT|TẮT` + mục `## Khuôn hỏi clean code`) · P4 thêm
hạng mục cố định QC-F4 vào cả `skills/tdq-build/references/qc.md` và
`portable/workflow/references/qc.md` · P5 dọn `rules/chung.md` + `rules/index.md`, xoá
`scripts/code_rule_scan.py` + 2 test của nó · P6 bù độ phủ test · P7 phát hành 0.22.0.

**Kết quả:** clean code từ **cổng hỏi 1 lượt/request + 1 script phụ thuộc linter máy** →
**luật thường trực nạp mỗi turn** · code xoá 138 dòng script + 159 dòng test · test 687 →
704 (mất 7 test của script cũ, bù 23 test mới) · trần dòng `tdq-conventions` 130 → 133.

**Kiểm:** `python3 -m pytest -q` → **704 passed, 377 subtests**, 0 đỏ · `doc_lint` exit 0
trên 12 file đã sửa và trên toàn `docs/tdq/spec/*.md` · QC **19/19 PASS** sau 1 vòng fix
(agent `tdq-qc-tester` tìm 4 defect: 2 lệnh QC viết sai trong spec §6, và — quan trọng
hơn — checklist LSP/OCP chỉ hỏi bản đọc cho hàm, bỏ sót ca có class kế thừa; đã sửa cả 4).

**Đầu ra:** `skills/tdq-conventions/references/clean-code.md` ·
`tests/test_clean_code_rule.py` · `docs/tdq/qc/2026-08-16-1300-bo-cong-clean-code.md`.

**Giới hạn:** Bỏ script scan là bỏ phần `## Tự kiểm` dạng **lệnh** của clean code — soul
nguyên tắc 3 cho phép, nhưng luật phân xử #2 ưu tiên luật kiểm được bằng lệnh. Bù bằng
`doc_lint` R9 + 21 test khoá HÌNH DẠNG file luật; phần PHÁN ĐOÁN (code có thật sạch không)
giờ dựa vào model tự trả lời 5 câu, không có lệnh nào chấm hộ. Chuỗi `code_rule_scan` còn
2 dòng trong `tests/test_clean_code_rule.py` — là chốt chặn hồi quy, cố ý giữ.

**Git:** chưa commit. Không có commit gỡ chặn nào trong lượt build này.

## Thời gian

| Phase | Treo tường | Model chạy | Số lần vào |
|---|---|---|---|
| idle | 0 giây | 0 giây | 1 |
| analyze | 8 phút | 8 phút | 1 |
| spec | 4 phút | 3 phút | 1 |
| plan | 3 phút | 2 phút | 1 |
| implement | 14 phút | 14 phút | 1 |
| qc | 7 phút | 7 phút | 1 |
| report | 5 giây | 0 giây | 1 |
| **Tổng** | **36 phút** | **36 phút** | |
