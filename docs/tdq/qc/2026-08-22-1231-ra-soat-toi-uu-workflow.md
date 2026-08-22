# QC — rà soát tối ưu workflow sau đợt chuyển tiếng Anh

Ngày: 2026-08-22 · Spec: ../spec/2026-08-22-1231-ra-soat-toi-uu-workflow.md (bản 1.0, ĐÃ DUYỆT)
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Người kiểm: agent `tdq-qc-tester` chạy độc lập (spec §1b định tuyến CÓ), vòng 1 lúc 13:13.

## Vòng 1 — kết quả agent QC độc lập

| # | Hạng mục | Kết quả | Bằng chứng |
|---|---|---|---|
| Q1 | Công cụ dò trùng chạy được | PASS | `doc_dup.py --vung skills --vung agents` thoát 0, in 8 khối |
| Q2 | Log service | PASS | mặc định có timestamp ra stderr; `--quiet` và `TDQ_DUP_LOG=0` đều tắt; bảng vẫn ra stdout |
| Q3 | Bộ đếm token | PASS | chặn venv đếm → `EXIT=3` kèm câu "FORBIDDEN to estimate characters/4" |
| Q4 | Unit test | PASS | `pytest tests/test_doc_dup.py -q` → 21 passed |
| Q5 | Bốn mặt | PASS | `grep -c '^## Mặt'` → 4 |
| Q6 | Mọi con số có nguồn | **FAIL** | 12 lỗi: 6 con số lệch, 4 lệnh nguồn không chạy lại được, 2 chỗ dẫn sai dòng |
| Q7 | Top 10 đúng khuôn | PASS | 10 dòng, 6 cột, không ô trống |
| Q8 | Không đề xuất nào đổi luật | PASS | đọc từng dòng cột "luật gốc bị chạm": chỉ cách viết và chỗ đặt |
| Q9 | Không sửa file workflow | PASS | `git status --porcelain skills agents hooks` rỗng |
| Q10 | Luật ngôn ngữ ba tầng | PASS | `i18n_check.py` trên `scripts/doc_dup.py` → 0 dòng vi phạm |
| Q11 | Luật tài liệu | PASS một phần | spec, plan, audit đều thoát 0; report chưa tồn tại lúc kiểm |
| Q12 | Hồi quy | PASS | `pytest -q` → 37 đỏ, 100% nằm trong `tests/test_skill_router.py` |

Agent còn kiểm ngoài happy path, đều đạt: `--min-dong 0` thoát 2 · `--vung` trỏ đường
dẫn không tồn tại thoát 2 · thiếu `--vung` thoát 2 · thư mục rỗng thoát 0 · không có
TODO hay placeholder trong `scripts/doc_dup.py` và `tests/test_doc_dup.py`.

## Vòng fix — 12 lỗi của Q6

Vòng 1 trên 3 vòng trần. Tất cả đều là lỗi hồ sơ audit, không lỗi code.

| Lỗi | Sai ở đâu | Đã sửa thành |
|---|---|---|
| 1 | "11 khối mục lục" — lệnh nguồn ra 13 | 13 khối tổng, 11 khối xoá được, 764 token; 2 khối trong khuôn spec/plan phải giữ |
| 2 | Bảng 5 file nặng nhất ghi sai lệnh nguồn, thứ hạng lấy từ bộ ước lượng | đo lại bằng bộ đếm thật, thứ hạng đảo: plan-template 4.327 dẫn đầu; kèm lệnh chạy lại được |
| 3 | Khai "bộ đếm thật" cho số của `context_surface.py`, thực ra là 4 byte một token | thêm mục quy ước bộ đếm ở đầu hồ sơ, bảng ba tầng ghi rõ "ước lượng" |
| 4 | Cột token 3.323 / 764 / 130 không do lệnh grep sinh ra | đếm lại bằng bộ đếm thật: 3.105 / 1.270 / 124, kèm lệnh |
| 5 | "219 chú thích có kèm lý do" | 219 tổng, trong đó 208 có lý do và 11 đã trần; 3.105 → 1.533, delta 1.572 giữ nguyên |
| 6 | Bảng luật cứng 42/25 không kèm mẫu grep, không tái lập | định nghĩa 8 từ khoá và khoảng 20–80%, đo lại: 22 dòng, 11 nằm giữa (50%), kèm hai lệnh |
| 7 | Nguồn `step_audit` còn placeholder `<thư mục tạm>` | ghi rõ ba phiên `d64f9bf9` · `a08c5f39` · `67f134a1` |
| 8 | `find …/0.19.0 -name '*.md'` ra 498 | đổi thành `…/0.19.0/skills`, ra đúng 39, kèm lệnh đối chiếu repo ra 44 |
| 9 | Dẫn sai: dòng 137 dùng `in text` chứ không `in stripped` | ghi đúng cả hai dòng 121 và 137 |
| 10 | Phép kiểm Top-10 dòng 1 không chạy được (CLI nhận một `--kind`) | đổi thành vòng `for k in comment string body; do …; done` |
| 11 | Đầu ra §2 số 5 (report) chưa tồn tại | viết report sau QC, đúng thứ tự phase |
| 12 | Lệnh DoD Q2 trong plan sai dưới zsh MULTIOS | bọc `sh -c '…'`, chạy lại ra rỗng |

Số tổng của bảng Top 10 đổi theo lỗi 1 và 4: 4.962 → **5.098 token**, bằng 8,6% trần.

## Vòng 2 — kiểm lại sau fix

| # | Hạng mục | Kết quả | Bằng chứng |
|---|---|---|---|
| Q6 | Mọi con số có nguồn | PASS | chạy lại 12 lệnh nguồn của hồ sơ, mọi con số khớp: 8/472 · 59/1378 · 59.486 · 1.452/10.785/50.064 · 219/3.105/1.533 · 13 khối/1.270 · 6 dòng/124 · 22 và 11 · 39 và 44 |
| Q7 | Top 10 đúng khuôn | PASS | đếm lại: 10 dòng, 6 cột, không ô trống, tổng cột 2 = 5.098 = 8,6% |
| Q11 | Luật tài liệu | PASS | `doc_lint.py` trên audit thoát 0; `--pair` spec ↔ plan thoát 0; report lint lúc đóng turn |
| Q2 | Log service | PASS | `sh -c 'TDQ_DUP_LOG=0 python3 scripts/doc_dup.py --vung skills 2>&1 1>/dev/null' | wc -l` → 0 |
| Q9 | Không sửa file workflow | PASS | `git status --porcelain skills agents hooks` vẫn rỗng sau vòng fix |
| Q12 | Hồi quy | PASS | `pytest -q` → 37 đỏ, đúng mốc nền, toàn bộ trong `tests/test_skill_router.py` |

Ghi chú Q12: lần chạy đầu ra 38 đỏ. Đỏ thừa là `test_docs_consistency.py::test_no_ds_store`,
do Finder sinh ra 9 file `.DS_Store` trong phiên. Xoá chúng bằng
`find . -name .DS_Store -not -path "./.git/*" -delete` là về đúng 37. Không file nào của
repo bị đụng — `.DS_Store` nằm trong `.gitignore`.

## Kết luận

12 trên 12 hạng mục PASS sau một vòng fix. Trần 3 vòng chưa chạm.
