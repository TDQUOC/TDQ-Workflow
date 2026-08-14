# QC — 2026-08-14-set-soul-workflow

Ngày: 2026-08-14 · Plan: ../plan/2026-08-14-set-soul-workflow.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Soul đủ 3 tầng đúng thứ tự | `pytest tests/ -q -k thu_tu` | 4 passed | PASS |
| Q2 | Skill nền + portable trỏ soul | `grep -c soul` 2 file | mỗi file đúng 1 dòng | PASS |
| Q3 | Rà soát đủ 28 file | `grep -c '^|'` file biên bản | 30 dòng = 2 header + 28 file | PASS |
| Q4 | Chỉ mục khớp số file rule | `pytest -k chi_muc` | 1 passed | PASS |
| Q5 | 7 file ngôn ngữ đủ khuôn | `pytest -k khuon_ngon_ngu` | 1 passed, 11 subtests | PASS |
| Q6 | URL trong rule có thật | `pytest -k nguon` | 3 passed, 3 subtests | PASS |
| Q7 | Script chạy thật | `code_rule_scan.py --tat-ca` | exit 0, PASS 0 · LỖI 0 · CHƯA 57 | PASS |
| Q8 | Script không tự cài | `grep -nE 'pip install\|npm i\|apt-get'` | không match (exit 1) | PASS |
| Q9 | Log service | chạy có / không `--im` | 2 dòng stderr timestamp / 0 dòng | PASS |
| Q10 | Câu hỏi clean code | `pytest -k clean_code_gate` | 1 passed | PASS |
| Q11 | Hai bản qc.md khớp | `pytest -k qc_dong_bo` | 1 passed | PASS |
| Q12 | M1–M5 có mặt | `pytest -k co_che_m` | 1 passed, 5 subtests | PASS |
| Q13 | Test đỏ được khi phá | đổi `QC-F2`→`QC-XX` bản portable | 1 failed → khôi phục → 596 passed | PASS |
| Q14 | Token tầng luôn nạp | Python `len()` 6 SKILL.md | 27.462 ≤ trần 27.464 ký tự | PASS |
| Q15 | Toàn bộ suite | `python3 -m pytest tests/ -q` | 596 passed, 306 subtests | PASS |
| Q16 | Lint tài liệu | `doc_lint.py` qc + plan + biên bản | exit 0 | PASS |
| Q17 | R9 đúng khuôn, đúng phạm vi | `pytest -k r9` | 5 passed | PASS |
| Q18 | Model Haiku làm theo được | agent Haiku soát bản cắt đáp án | nêu đúng 5/5 lỗi, 0 câu hỏi | PASS |
| Q19 | 5 khuôn tài liệu có dòng Soul | `pytest -k khuon_tai_lieu` | 1 passed, 5 subtests | PASS |
| Q20 | Tài liệu request mở có Soul | `pytest -k soul_request_dang_mo` | 1 passed, 3 subtests | PASS |

Ba hạng mục cố định: QC-F1 = Q15 (suite tươi sau Q13). QC-F2: plan không có dòng
`Chạm:` — mọi task tạo file mới hoặc sửa tài liệu, đúng luật bỏ dòng → 0 phép kiểm.
QC-F3: spec 1.2 §5 chưa có khối "Ràng buộc kiến trúc phải giữ" — khối đó là sản phẩm
M2 của chính request này, spec viết trước khi khuôn ra đời → 0 phép kiểm. Spec §4
không có dòng `Clean code:` (cổng cũng mới sinh ở request này); Q7 đã scan toàn repo.

## Bằng chứng chọn lọc

- Q13: sửa `- QC-F2 — hồi quy vùng chạm` thành `- QC-XX …` trong
  `portable/workflow/references/qc.md` → `FAILED …::QcDongBo::test_qc_dong_bo`
  ("khối QC-F ở bản skill và bản portable phải khớp nguyên văn"); khôi phục nguyên văn
  → full suite `596 passed, 306 subtests passed in 36.73s`.
- Q9: `code_rule_scan.py tests/samples/python_5_loi.py` → stderr đúng 2 dòng
  `[2026-08-14T23:49:13] bắt đầu quét 1 file…` / `…xong — 1 file có rule, 0 lỗi`;
  thêm `--im` → stderr rỗng, stdout vẫn đủ 3 dòng kết quả.
- Q14: đo bằng `len()` từng file (phương pháp mốc T0.1); `token_audit.py` đo chi phí
  transcript phiên, không đo SKILL.md — ghi chú tại plan T7.2.
- Q7/Q18: output đầy đủ ở hai mục phía dưới file này.

## Kết luận

PASS toàn bộ 20/20 hạng mục + 3 hạng mục cố định, vòng 1, không cần vòng fix.
Nợ môi trường (không phải defect): máy thiếu `ruff` nên lint Python thật chưa chạy
được tại chỗ — script báo đúng CHƯA KIỂM ĐƯỢC, đã nêu ở report.

## Kết quả chạy thật `code_rule_scan.py --tat-ca` (T5.3)

Chạy 2026-08-14T23:23 trên chính repo này (614 file git quản lý, 57 file khớp bảng rule):

```
KẾT QUẢ QUÉT RULE
hooks/scripts/_common.py · Python · CHƯA KIỂM ĐƯỢC — thiếu ruff
hooks/scripts/bash_gate.py · Python · CHƯA KIỂM ĐƯỢC — thiếu ruff
hooks/scripts/edit_gate.py · Python · CHƯA KIỂM ĐƯỢC — thiếu ruff
… (57 dòng, toàn bộ là Python, cùng ghi chú "thiếu ruff")
PASS: 0 · LỖI: 0 · CHƯA KIỂM ĐƯỢC: 57
```

- Máy chưa cài ruff → script báo đúng CHƯA KIỂM ĐƯỢC thay vì PASS khống, exit 0
  (không phải LỖI). Ba trạng thái phân biệt rõ ở dòng tổng.
- Nhánh PASS/LỖI đã chứng minh bằng test giả lập trong
  `tests/test_code_rule_scan.py` (4 passed).
- Log stderr: `[2026-08-14T23:23:19] bắt đầu quét 614 file (bảng rule: 17 đuôi)` →
  `[2026-08-14T23:23:20] xong — 57 file có rule, 0 lỗi`.

## Vòng QC độc lập (T8.2 — agent `tdq-qc-tester`, chạy lại lệnh thật)

Bảng phán quyết của agent (mỗi dòng: hạng mục · phán quyết · bằng chứng agent tự chạy):

- Q1 PASS `4 passed` · Q2 PASS grep soul = 1/file · Q3 PASS bảng rà soát 28 dòng ·
  Q4 PASS `1 passed` · Q5 PASS `1 passed, 11 subtests` · Q6 PASS `3 passed, 3 subtests` ·
  Q7 PASS exit 0, `PASS: 0 · LỖI: 0 · CHƯA KIỂM ĐƯỢC: 57` · Q8 PASS grep rỗng ·
  Q9 PASS log timestamp / `--im` stderr 0 byte · Q10–Q12 PASS (`co_che_m` 5 subtests) ·
  Q14 PASS sát ngưỡng (27.462/27.464 ký tự) · Q15 PASS `596 passed, 306 subtests` ·
  Q16 PASS doc_lint 7 file exit 0 · Q17 PASS `5 passed` · Q19 PASS `1 passed, 5 subtests` ·
  Q20 PASS `1 passed, 3 subtests` · Q13, Q18: để vòng QC chính.
- Phát hiện thêm của agent: (1) máy này thiếu `ruff` nên 57 file Python "CHƯA KIỂM ĐƯỢC"
  — script báo đúng trạng thái, nhưng lint tĩnh thật chưa từng chạy trên máy này, cần nêu
  trong report; (2) biên Q14 chỉ còn dư 2 ký tự — lần sửa SKILL.md sau phải đo lại;
  (3) không TODO/FIXME/stub trong 3 script đã soát; (4) không lệch giữa lời khai trong
  plan/QC và kết quả agent tự chạy.
- VERDICT của agent: PASS toàn bộ hạng mục kiểm được, không defect chức năng.
