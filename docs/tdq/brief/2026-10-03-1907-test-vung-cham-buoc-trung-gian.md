# BRIEF — Chạy test vùng chạm ở bước trung gian, trọn bộ chỉ ở cổng phase

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> Okay mở request h5 đi

(user chốt thêm, 2026-10-03: "1a 2a" — đóng request nghiên cứu bằng commit + merge, chạy H5 ở
lane chuyên sâu.)

**Đọc lần đầu**

- Nguồn: hướng **H5** của báo cáo `docs/tdq/reports/2026-10-03-1101-nghien-cuu-nen-context.md`.
- Mục tiêu: bước trung gian của implement/qc chỉ chạy module test của vùng bị chạm (theo dòng
  `Chạm:` của plan); trọn bộ test chỉ chạy ở 2–3 cổng phase cố định. Giữ chất lượng nhờ cổng
  trọn bộ bắt buộc.
- Số đo làm căn cứ (báo cáo, mục "Thử nghiệm" T2.2 và "Bản đồ chi phí"):
  - trọn bộ 353,9 s cho 2.425 test; chạy ~7,4 lần mỗi request; trọn bộ chiếm 26% thời gian máy;
  - 10 module request 0732 chạm vào chạy hết 24,4 s (6,9% trọn bộ);
  - ước lượng tiết kiệm ≈ 1.240–1.780 s máy mỗi request;
  - 27 test đỏ khi chạy từ PowerShell vì gọi `true` (chỉ có trong Git Bash);
  - chạy song song chưa dùng được (test git dùng chung trạng thái) — thuộc H6, ngoài phạm vi.
- Phạm vi đoán: luật chạy test ở `skills/tdq-build/SKILL.md` ("EXACTLY ONCE"),
  `skills/tdq-plan/references/plan-template.md` ("sau mỗi phase chạy toàn bộ") và vòng sửa ở
  `skills/tdq-build/references/qc.md`; có thể một lệnh/script chọn module test từ dòng `Chạm:`.
- Ràng buộc biết trước: `plan-template.md` đang ở 3.497/3.500 token; `qc.md` 3.203/3.500.
- Thước đo thành công (từ báo cáo): số lần lệnh test ≥ 200 s mỗi request giảm từ 7,4 xuống 2–3;
  số lỗi cổng trọn bộ bắt được không giảm; số vòng sửa QC mỗi request không tăng.
- Chỗ chưa rõ (hỏi ở interview): 2–3 cổng là những cổng nào; chọn module bằng máy (script) hay
  bằng luật cho agent; sửa 27 test `true` hay chỉ chạy cổng trong Git Bash; áp cho lane quick không.

## Hiểu & kiến thức

### Năng lực dùng được

| Năng lực | Nguồn | Dùng? | Vì sao |
|---|---|---|---|
| `tdq-build`, `tdq-plan`, `tdq-conventions` | plugin:tdq-workflow | NỀN | chính là vùng sửa |
| `code-review`, `simplify` | built-in | CÓ | nếu có mã mới (script chọn module test) |
| `skill_inventory --loc "test unittest suite"` | script | đã chạy | không skill trên đĩa nào khớp |
| Research web | — | BỎ | việc thuần nội bộ; số đo đã có ở báo cáo 1101 |

### Mã và luật hiện có (đọc 2026-10-03)

Ba chỗ luật về chạy test, mâu thuẫn nhau:
- `skills/tdq-build/SKILL.md:129` — bước Green chỉ chạy **test của module**; `:136` — xong mọi
  task thì chạy trọn bộ **EXACTLY ONCE**.
- `skills/tdq-plan/references/plan-template.md:39` — quy tắc 3 "Sau mỗi phase: chạy toàn bộ test
  suite" — MỌI plan chép quy tắc này (kể cả 3 plan gần nhất), nên agent chạy trọn bộ sau mỗi phase.
- `skills/tdq-build/references/qc.md:80`, `:186` — QC-F1 chạy trọn bộ, và MỖI vòng sửa chạy lại
  trọn bộ. `qc.md:45` đã định nghĩa "vùng chạm = chỉ các module trên dòng `Chạm:` của plan".
- Hệ quả: xong implement chạy trọn bộ một lần, QC-F1 chạy lại ngay sau đó dù mã không đổi — hai lần
  liền nhau cho cùng một cây mã.
- Lane quick đã đúng: `quick-lane-qc.md:42` không chạy trọn bộ, chỉ test của từng task.

### Số đo theo request — nền đang dịch chuyển

`docs/tdq/research/2026-10-03-1101-do-noi-bo.md` §3.2, lần chạy trọn bộ ≥ 200 s mỗi request:
09-20: 8 · 09-21: 16 · 09-23: 5 · 09-27: 4 · 09-28-0910: 5 · 09-28-2324: 16 · **10-03-0015: 3 ·
10-03-0732: 2**. Trung bình 7,4 bị kéo lên bởi request cũ; hai request gần nhất (mode subagent,
leader chạy trọn bộ ở cổng) đã ở mức 2–3. Mức tiết kiệm so với cách làm HIỆN NAY nhỏ hơn con số
1.240–1.780 s của báo cáo (vốn tính từ trung bình 7,4). Giá trị còn lại: khoá luật cho khỏi trôi
về 8–16 lần, bỏ cặp chạy trùng implement→QC-F1, và giới hạn trọn bộ trong vòng sửa QC.

Phụ: trọn bộ đã chậm dần 284 s (09-20) → 363 s (10-03); `test_bench` một mình 72,8 s (20,5%).

### Đo trước — bán kính ảnh hưởng (nguyên mẫu, 2026-10-03, bản sao tạm, đã xoá)

Nguyên mẫu chọn module test bị ảnh hưởng bởi một tập file sửa: test nhắc tên file bị sửa, hoặc
nhắc một module mà chuỗi import bắc cầu (`scripts/`, `hooks/scripts/`, phân tích AST) chạm tới
file bị sửa. 126 module test; 65 module chèn `sys.path` và nhiều test gọi hook/script qua tiến
trình con — nên chỉ dò import là bỏ sót, phải dò cả tên file.

| Tập sửa | Module chọn | Thời gian (chạy lẻ từng module, bản sao) |
|---|---|---|
| cả request 0732 (21 file mã + luật) | 112 / 126 | — |
| `scripts/tdq_state.py` (hub) | 96 | 334 s — ≈ trọn bộ 353,9 s, không lợi |
| `scripts/doc_lint.py` / `scripts/tdq_ten_lenh.py` | 96 / 102 | (cùng cụm hub — tdq_state import chúng) |
| `hooks/scripts/_common.py` | 38 | — |
| `skills/tdq-build/SKILL.md` | 37 | — (dư: dò theo tên `SKILL.md` khớp mọi skill → cần dò theo đường dẫn) |
| `hooks/hooks.json` | 13 | — |
| `hooks/scripts/stop_gate.py` | 11 | 29 s (−92%) |
| `skills/tdq-build/references/qc.md` | 7 | 22 s (−94%) |
| `scripts/tdq_bench.py`, `hooks/scripts/ask_gate.py` (lá) | 2 | — |

Hệ quả cho thiết kế:
- Task chạm cụm hub (`tdq_state`, `doc_lint`, `tdq_ten_lenh`) → bán kính ≈ trọn bộ. Khi bán kính
  vượt một ngưỡng tỉ lệ, chạy trọn bộ trong MỘT tiến trình (rẻ hơn chạy lẻ ~96 lần khởi động).
- Task chạm file lá hoặc file luật → 7–13 module, 20–30 s thay vì ~354 s.
- Dò file luật phải theo ĐƯỜNG DẪN tương đối, không theo tên trần (tránh `SKILL.md` khớp mọi skill).
- Không tính được chắc chắn (file không thuộc `scripts/`, `hooks/`, `skills/`, `tests/`) → trọn bộ.

### Đã chốt

- Trọn bộ chỉ ở 2 cổng: QC-F1 (thay cho lần "xong implement") và sau vòng sửa QC cuối nếu có sửa.
- Bước trung gian: `tdq_test.py vung-cham` chạy vùng chạm + bán kính ảnh hưởng; bán kính lớn hoặc
  không tính được → trọn bộ một tiến trình.
- `tdq_test.py tron-bo` ghi sổ mỗi lần chạy trọn bộ; `next` nhắc khi vượt số cổng.
- Sửa 27 test gọi `true` để chạy được ở mọi shell.
- Giữ nguyên lane quick (đã chỉ chạy test của task) và mọi cổng duyệt của user.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Research web | BỎ | việc thuần nội bộ; số đo ở báo cáo 1101 và phép đo trước ở trên |
| Vòng phạm vi | BỎ | phạm vi đã khoanh ở báo cáo 1101 (H5) |
| Interview chi tiết | CÓ | 6 câu + 1 bổ sung của user, hết câu hỏi |
| Spec → plan | CÓ | khung bất biến |
| Soát lỗi `code-review` + rút gọn `simplify` | CÓ | có mã mới (`tdq_test.py`) và sửa luật mà mọi request sau dùng |
| QC độc lập (agent) | BỎ | mức `full` |

Luồng: (1) script `tdq_test.py` (bán kính + trọn bộ + sổ) · (2) luật 2 cổng ở 3 file + `next` nhắc
· (3) sửa 27 test `true`.

## Hỏi đáp

Vòng phạm vi: BỎ — phạm vi đã khoanh ở báo cáo 1101 (hướng H5).

| # | Câu hỏi | Trả lời (2026-10-03) |
|---|---|---|
| 1 | Nền đã dịch (2 request gần nhất chỉ 2–3 lần trọn bộ) — làm tiếp? | **A** — làm tiếp, mục tiêu là KHOÁ LUẬT; báo cáo ghi tiết kiệm so với cả nền cũ lẫn nền mới |
| 2 | Trọn bộ ở cổng nào? | **A** — 2 cổng: QC-F1 (tính luôn cho "xong implement") + sau vòng sửa QC cuối nếu có sửa |
| 3 | Cưỡng chế? | **A** — luật + script `tdq_test.py` (`vung-cham`, `tron-bo` ghi sổ); `next` nhắc khi vượt số cổng |
| 4 | 27 test gọi `true` | **A** — sửa test để không phụ thuộc shell |
| 5 | Mức QC | **A** — `full` |
| 6 | Bổ sung | **Có**: "ngoài vùng chạm thì tính toán nếu có vùng có khả năng bị ảnh hưởng thì cũng check lại để đảm bảo ko gây lỗi thứ đã chạy ổn" |

Hiểu câu 6: bước trung gian chạy test của **vùng chạm + bán kính ảnh hưởng** — mọi module test
có đường import (trực tiếp hoặc bắc cầu) tới file bị sửa, và mọi test đọc theo đường dẫn file
luật/dữ liệu bị sửa. Không tính được chắc chắn (import động, file lạ) → chạy trọn bộ: thà chậm
còn hơn bỏ sót — đúng soul "chất lượng > runtime".
