# QC — Hợp lối code Ponytail vào TDQ-Workflow
Ngày: 2026-09-16 · Plan: ../plan/2026-09-16-1447-hop-ponytail-vao-tdq.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

9 hạng mục DoD + 4 hạng mục cố định QC-F1→F4 = 13 hạng mục.

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Ba đầu ra tồn tại và không rỗng | `wc -c` trên 3 đường dẫn | 30000 · 9496 · 4319 byte | PASS |
| Q2 | Phương án đúng 5 mục luồng, có dòng quyết định + giá | `grep -c '^## Luồng '` · `grep -c 'Quyết định:'` · `grep -c 'Giá phải trả:'` | 5 · 5 · 5 | PASS |
| Q3 | Trích dẫn `đường-dẫn:dòng` sai bằng 0 | trình kiểm T4.1 trên 3 đầu ra, rồi trên cả file QC này | `101 · sai 0` (3 đầu ra) và `109 · sai 0` (thêm file QC) | PASS |
| Q4 | Khẳng định cơ chế thiếu nhãn tin cậy bằng 0 | phép đếm T4.2 trên 3 đầu ra | `0 (cần 0)` | PASS |
| Q5 | Đầu ra 2 đủ khuôn luật | `grep -c '^## When it applies\|^## What to do\|^## Self-check'` · `grep -c '^Soul:'` · `grep -c 'RIGHT\|WRONG'` | 3 · 1 · 4 | PASS |
| Q6 | Đầu ra 2 không có tiếng Việt có dấu (dụng cụ đo đã sửa) | `python3 scripts/i18n_check.py <đầu ra 2>` | `0 Vietnamese line(s) in 1 file(s)`, exit 0 — `grep -cP` thô ra **2**, xem mục bằng chứng | PASS |
| Q7 | Đầu ra 1 có mục cổng duyệt riêng, đủ câu trước và câu sau | `grep -c 'Cổng duyệt riêng'` | 2 (mục lục + thân mục) | PASS |
| Q8 | Không file nào ngoài `docs/` bị đổi | `git diff --name-only main...HEAD \| grep -cv '^docs/'` và `git status --porcelain` | 0 và 0 | PASS |
| Q9 | Report ≤ 50 dòng | `wc -l` trên đầu ra 3 | 46 | PASS |
| QC-F1 | Toàn bộ suite, đối chiếu baseline `main` | `python3 -m unittest discover tests` trên nhánh và trên worktree `main` sạch | cả hai: `Ran 1802 … FAILED (failures=290, errors=4)`; tập tên test fail lệch **0** cả hai chiều | PASS |
| QC-F2 | Hồi quy vùng `Chạm:` | `grep -c 'Chạm:'` trên plan | 0 dòng `Chạm:` — không task nào sửa file mã nguồn, không có vùng để hồi quy | PASS |
| QC-F3 | Ràng buộc kiến trúc spec §5 | 3 dòng ràng buộc, mỗi dòng một phép kiểm | xem mục bằng chứng | PASS |
| QC-F4 | Clean code | — | `KHÔNG ÁP DỤNG — không sửa file code` | PASS |

## Bằng chứng

### Q3, Q4 (trình kiểm chạy trong scratchpad, không vào repo — điều kiện của Q8)
```
101 trích dẫn · hợp lệ 101 · sai 0      # 3 đầu ra — phạm vi Q3
109 trích dẫn · hợp lệ 109 · sai 0      # thêm cả file QC này
1. khang dinh co che thieu nhan tin cay: 0  (can 0)
2. dong tieng Viet co dau trong dau ra 2: 0  (can 0)
3. so dong report: 46  (can <= 50)
T4.2 PASS
```
Trình kiểm trích dẫn bắt được 7 lỗi thật trong report, 3 lỗi nữa trong chính file QC này (trích dẫn ghi tên file trần — dạng `soul.md` kèm số dòng, không có thư mục, nên máy không mở được) và 2 lỗi trước đó trong đầu ra 1+2 — đã sửa thành đường dẫn
đầy đủ rồi mới xanh. Đây là lý do phép kiểm này được viết sớm thay vì đọc bằng mắt.

### Q6 — hai số đo, không chỉ số đã đạt
```
$ grep -cP '[à-ỹÀ-Ỹ]' docs/tdq/knowledge/2026-09-16-1447-du-thao-luat-ponytail.md
2
$ grep -nP '[à-ỹÀ-Ỹ]' ...
3:Soul: chất lượng > runtime > context cost <!-- i18n-allow: canonical Soul line --> · root law: ...
39:`Tạo mới thay vì dùng <path> vì <reason>` <!-- i18n-allow: canonical note written into the plan -->
$ python3 scripts/i18n_check.py docs/tdq/knowledge/2026-09-16-1447-du-thao-luat-ponytail.md
0 Vietnamese line(s) in 1 file(s)   # exit 0
```
Cả hai dòng đều là dòng bắt buộc và đều mang `i18n-allow`, hệt cách
`skills/tdq-build/references/rules/chung.md:3` làm. Số 0 theo `grep` thô chỉ đạt được bằng cách
xoá dòng `Soul:` — thứ `soul.md` bắt buộc mọi file phải có. Dụng cụ đo sai thì sửa dụng cụ đo,
không sửa file để vừa dụng cụ; ghi chú sửa nằm ngay ở dòng Q6 của plan.

### QC-F1 — 294 test đỏ là nợ có sẵn, không phải do lượt này
```
nhánh feature/hop-ponytail-vao-tdq : Ran 1802 tests ... FAILED (failures=290, errors=4, skipped=14)
worktree main sạch                 : Ran 1802 tests ... FAILED (failures=290, errors=4, skipped=15)
chỉ có ở nhánh này: 0    chỉ có ở main: 0
```
284 trong 290 là cùng một test `test_skill_router.test_moi_duong_dan_khac_rong_deu_mo_duoc`:
kho `docs/tdq/audit/skill-index.json` commit lần cuối `31bab09` ngày 2026-08-18, ghi đường dẫn
dưới `/Users/truongdinhquoc/.claude/skills/…` trong khi home hiện tại là `/Users/tdq` — kho cũ
sau khi đổi máy, dựng lại bằng `python3 scripts/skill_router.py --dung-kho` là hết. Lượt này
không sửa file đó (`git status --porcelain` trên nó trả về rỗng). Nợ này đưa vào report.

### QC-F3 — ba ràng buộc kiến trúc của spec §5
| Ràng buộc | Phép kiểm | Kết quả |
|---|---|---|
| `docs/kien-truc.md:49` — soul là luật gốc, đổi soul phải có user duyệt | đầu ra 1 có mục cổng duyệt riêng cho câu sửa `skills/tdq-build/references/rules/chung.md:22`; không file nào trong `skills/` bị đổi | `git status --porcelain` không có đường dẫn `skills/` — PASS |
| `docs/kien-truc.md:51` — luật trong `skills/` viết tiếng Anh, tài liệu cho user theo `doc_lang` | đầu ra 2 tiếng Anh (`i18n_check` exit 0), đầu ra 1 và 3 tiếng Việt (`doc_lint` R12 exit 0) | PASS |
| `docs/kien-truc.md:13` — `portable_*` là SINH, không sửa tay | luồng 4 đi qua `scripts/build_portable.py`, và lượt này không sửa file nào trong `portable_*` | PASS |

Ràng buộc 2 phải trả giá: `scripts/doc_lint.py:585` (R12) đòi file làm cho người dùng viết tiếng Việt,
còn đầu ra 2 cố ý tiếng Anh — hai luật va nhau thật. Xử bằng cơ chế miễn trừ một-đoạn của chính
doc_lint (`scripts/doc_lint.py:134`), 10 marker, mỗi marker ghi lý do; KHÔNG nới `doc_lint.py`,
vì quy tắc thi hành số 4 chặn mọi file ngoài `docs/` và một luật đúng không nên nới vì một file.
Task `QC1.1` của vòng 1 ghi lại việc này; sau đó `doc_lint` trên cả 4 file exit 0.

### Phát hiện NGOÀI phạm vi Q3 — 9 trích dẫn tên trần trong spec, cố ý không sửa
Q3 chỉ đo 3 file đầu ra. Chạy trình kiểm rộng ra cả spec và plan thì: plan có 2 trích dẫn tên
trần (cùng một chỗ trỏ tới `chung.md` dòng 22) — đã sửa thành đường dẫn đầy đủ, vì sửa tick/ghi chú trong plan là việc
bình thường của phase implement và không đổi ý định. Spec còn **9 trích dẫn sai trên 11**
(`11 trích dẫn · hợp lệ 2 · sai 9`) và **cố ý giữ nguyên**: spec đã ĐƯỢC DUYỆT, và theo
`skills/tdq-build/references/qc.md:74` đổi nội dung spec làm dịch sha nên hook đòi duyệt lại.
Sửa lặng lẽ một file đã duyệt là việc tệ hơn 9 trích dẫn khó bấm. Đây là việc cho request sau,
hoặc bạn nói một câu là tôi sửa kèm xin duyệt lại.

## Kết luận
PASS toàn bộ 13/13 hạng mục, vòng 1, không có vòng fix thứ hai.
Hai dụng cụ đo bị sửa trong lượt (T1.5 số đích của `build_portable.py`, Q6 cách đo tiếng Việt) và
một tiêu chí được ghi rõ là vượt-rỗng (T4.3) — cả ba đều sửa theo số đo, có ghi chú ngày tại chỗ.
Nợ kỹ thuật mang sang report: 294 test đỏ có sẵn từ kho `skill-index.json` cũ.
