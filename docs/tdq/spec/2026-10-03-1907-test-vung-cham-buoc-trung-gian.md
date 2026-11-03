# SPEC — Chạy test vùng chạm + bán kính ảnh hưởng ở bước trung gian, trọn bộ chỉ ở 2 cổng

Ngày: 2026-10-03 · Bản: 1.1 · Brief: ../brief/2026-10-03-1907-test-vung-cham-buoc-trung-gian.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: ĐÃ DUYỆT (2026-10-03, "duyệt spec", bản 1.1)

## Mục lục

- 1. Mục tiêu & phạm vi
- 1b. Lộ trình
- 2. Đầu ra cụ thể
- 2b. Ranh giới module
- 3. Cách tiếp cận & lý do
- 3b. Năng lực & công cụ
- 4. Yêu cầu bắt buộc
- 5. Ràng buộc & rủi ro
- 6. QC & Definition of Done
- 7. Câu hỏi còn mở
- Thay đổi so với bản 1.0

## 1. Mục tiêu & phạm vi

- Mục tiêu: một luật chạy test duy nhất, không mâu thuẫn, có máy giữ: bước trung gian chạy test
  của **vùng chạm + bán kính ảnh hưởng**; trọn bộ test chỉ chạy ở **2 cổng** (QC-F1, và sau vòng
  sửa QC cuối nếu có sửa). Không để thứ đã chạy ổn bị vỡ mà không ai thấy.
- Trong phạm vi:
  - script mới `scripts/tdq_test.py`: tính bán kính ảnh hưởng từ tập file bị sửa, chạy các module
    đó, rơi về trọn bộ khi bán kính lớn hoặc không tính được; chạy trọn bộ và ghi sổ;
  - `next` ở phase implement/qc nhắc khi số lần trọn bộ đã vượt số cổng;
  - sổ **bán kính bỏ sót**: QC-F1 đỏ ở module mà bán kính trước đó không chọn → ghi lại; report
    in số lần bỏ sót của request — căn cứ để quay lại kiểm theo phase nếu khác 0;
  - gỡ mâu thuẫn luật ở `skills/tdq-build/SKILL.md`, `skills/tdq-plan/references/plan-template.md`,
    `skills/tdq-build/references/qc.md`;
  - sửa các test gọi lệnh `true` để chạy được từ mọi shell (đo được 26 fail + 1 error khi gọi từ
    PowerShell);
  - quyết định kiến trúc trong `docs/kien-truc.md`; CHANGELOG + bump bản.
- NGOÀI phạm vi:
  - chạy test song song (hướng H6 — test git dùng chung trạng thái);
  - làm nhanh từng test (`test_bench` 72,8 s);
  - lane quick — đã chỉ chạy test của từng task (`quick-lane-qc.md`);
  - mọi cổng duyệt của user giữ nguyên;
  - không chặn cứng bằng hook: `next` nhắc, không deny.

## 1b. Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | việc thuần nội bộ; số đo ở báo cáo 1101 + phép đo trước ở brief |
| Vòng phạm vi | BỎ | phạm vi đã khoanh ở báo cáo 1101 (H5) |
| Interview chi tiết | CÓ | 6 câu + 1 bổ sung của user |
| Soát lỗi `code-review` + rút gọn `simplify` | CÓ | có mã mới và sửa luật mọi request sau dùng |
| QC độc lập (agent) | BỎ | mức `full` |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Bán kính ảnh hưởng: từ tập file sửa → tập module test (dò tên/đường dẫn file trong test + import bắc cầu qua `scripts/`, `hooks/scripts/` + test QUÉT thư mục cha của file sửa bằng `os.walk`/`glob`/`listdir`) | `scripts/tdq_test.py` → `ban_kinh()` | test trên các ca đã đo ở brief + ca quét thư mục |
| 2 | Lệnh `tdq_test.py vung-cham [--files …]`: không có `--files` thì lấy file đổi từ git so với nhánh gốc; chạy các module trong MỘT tiến trình; bán kính ≥ ngưỡng hoặc không tính được → trọn bộ | `scripts/tdq_test.py` | test |
| 3 | Lệnh `tdq_test.py tron-bo`: chạy trọn bộ, ghi một dòng sổ (thời điểm, phase, kết quả, giây) | `scripts/tdq_test.py`, sổ `docs/tdq/.tdq-test.jsonl` (gitignore) | test |
| 4 | `next` ở implement/qc nhắc khi số lần trọn bộ của request vượt số cổng | `scripts/tdq_state.py` → `render_next` | test |
| 4b | Sổ bán kính bỏ sót: mỗi lần `vung-cham` ghi tập module đã chọn; `tron-bo` đỏ ở module chưa từng được chọn trong request → ghi một dòng "bỏ sót"; lệnh in số lần bỏ sót cho report | `scripts/tdq_test.py`, sổ `docs/tdq/.tdq-test.jsonl` | test |
| 5 | Luật một nguồn: bước trung gian = `vung-cham`; trọn bộ = 2 cổng; xong implement KHÔNG chạy trọn bộ riêng (QC-F1 là lần đó) | `skills/tdq-build/SKILL.md`, `skills/tdq-plan/references/plan-template.md`, `skills/tdq-build/references/qc.md` | test luật + `grep` |
| 6 | Test chạy được từ mọi shell: không còn test nào gọi lệnh `true` của shell | các file test liên quan | trọn bộ từ PowerShell 0 fail |
| 7 | Quyết định kiến trúc có ngày; CHANGELOG; bump 0.57.0 | `docs/kien-truc.md`, `CHANGELOG.md`, 2 `plugin.json` | `grep` |

## 2b. Ranh giới module

Theo import thật: `tdq_test.py` mới chỉ đọc file và gọi `unittest`; `tdq_state.py` (hub) đọc sổ
của nó để nhắc; các file luật không import gì.

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| test-runner | `scripts/tdq_test.py`, `.gitignore` + test đi kèm | không | 1, 2, 3 |
| state | `scripts/tdq_state.py` + test đi kèm | test-runner | 4 |
| luat | `skills/tdq-build/**`, `skills/tdq-plan/references/plan-template.md`, `docs/kien-truc.md`, `docs/tdq/token-budget.json` | test-runner | 5, 7 |
| test-shell | các file test đang gọi `true` | không | 6 |
| phat-hanh | `CHANGELOG.md`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` | luat | 7 |

## 3. Cách tiếp cận & lý do

- Chọn: **bán kính tính bằng máy, rơi về trọn bộ khi không chắc.**
  - Bán kính = test có nhắc đường dẫn tương đối hoặc tên module của file bị sửa, cộng mọi module có
    chuỗi import bắc cầu (AST) tới file đó trong `scripts/`, `hooks/scripts/`. Phải dò cả tên vì
    nhiều test gọi hook/script qua tiến trình con, không import. File luật dò theo ĐƯỜNG DẪN tương
    đối, không theo tên trần (tên `SKILL.md` khớp mọi skill → chọn dư 37 module).
  - Test QUÉT cả thư mục (gọi `os.walk`/`glob`/`listdir` trên một đường dẫn dựng từ thư mục
    `skills`, `hooks`, `scripts`, `agents`, `tests`) được chọn khi file sửa nằm trong thư mục đó —
    dò bằng AST, không bằng chữ. Đây là điểm mù của bản 1.0: những test này không nhắc tên file
    nào (ví dụ `test_luat_dung.py` duyệt mọi file trong `skills/`).
  - Sổ bán kính bỏ sót biến "bán kính có đủ không" thành số đo được ở mỗi request, thay vì tin.
  - Bán kính ≥ 60% số module test, hoặc có file sửa nằm ngoài `scripts/ hooks/ skills/ tests/
    agents/` → chạy trọn bộ trong một tiến trình: rẻ hơn khởi động ~96 lần, và an toàn hơn.
  - Chạy các module đã chọn trong MỘT tiến trình (`unittest` loader), không mỗi module một lần.
- Vì: phép đo trước ở brief — file lá/luật chỉ cần 7–13 module (22–29 s thay vì 353,9 s); cụm hub
  (`tdq_state`, `doc_lint`, `tdq_ten_lenh`) thật sự chạm 96–102 module, nên ở đó trọn bộ là đúng chứ
  không phải lãng phí. User yêu cầu kiểm cả vùng có khả năng bị ảnh hưởng — bán kính làm đúng việc đó.
- Hai cổng thay vì "sau mỗi phase": xong implement và QC-F1 chạy trên cùng một cây mã — một lần là đủ.
- Đã loại:
  - Chỉ chạy module trên dòng `Chạm:` — bỏ sót test gọi qua tiến trình con và vùng ảnh hưởng (user
    yêu cầu kiểm cả vùng đó).
  - Dùng `graphify affected` / LSP blast radius — LSP đang trượt smoke trên máy này, graphify chỉ
    phủ `scripts/ hooks/`, không phủ `tests/` (`.graphifyignore`); một script tự chứa không phụ
    thuộc tầng nào.
  - Chặn cứng bằng hook khi chạy trọn bộ quá số cổng — user chọn nhắc; chặn test là chặn kiểm tra.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-build, tdq-plan, tdq-conventions | plugin:tdq-workflow | NỀN | khung đang chạy, đồng thời là vùng sửa |
| code-review | built-in | DÙNG | soát lỗi đúng-sai `tdq_test.py` và phần sửa `tdq_state.py` |
| simplify | built-in | DÙNG | rút gọn sau soát lỗi |
| Đã xét 13 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: `tdq_test.py` log ISO timestamp ra stderr (tập file sửa, số module
  chọn, lý do rơi về trọn bộ, giây chạy), tắt bằng `TDQ_LOG=0`.
- Không placeholder, không TODO stub.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code bám SOLID (`skills/tdq-conventions/references/clean-code.md`) và rule Python ở
  `skills/tdq-build/references/rules/`. Mã, chú thích, chuỗi máy in ra bằng tiếng Anh.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ:
- `scripts/` không import `hooks/` — `tdq_test.py` chỉ ĐỌC mã nguồn `hooks/scripts/` bằng AST,
  không import.
- Hook không chặn vì "chưa duyệt" (2026-07-29) — việc này không thêm hook chặn nào.
- Trần 3.500 token mỗi file luật; `plan-template.md` đang 3.497 → quy tắc 3 chỉ được viết lại cho
  bằng hoặc ngắn hơn. `tdq-build/SKILL.md` 173/174 dòng (R6).

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Bán kính bỏ sót một test (đọc file theo cách lạ) | lỗi lộ muộn ở QC-F1, sửa tốn hơn; sản phẩm cuối vẫn qua trọn bộ | dò cả test quét thư mục; cổng trọn bộ QC-F1 bắt buộc; không tính được → trọn bộ; sổ bỏ sót đo số lần lọt ở mỗi request |
| Lỗi gây ở P1 lộ ra muộn (không còn trọn bộ sau mỗi phase) | P2, P3 xây trên lỗi, tốn thêm vòng sửa QC | task chạm cụm hub vẫn chạy trọn bộ ngay ở bước đó (bán kính ≥ 60%); bán kính rộng hơn luật hiện tại (chỉ module đang sửa) |
| Bán kính chọn dư | chậm hơn mong đợi, không sai | ngưỡng 60% rơi về một tiến trình trọn bộ |
| Plan cũ còn chép quy tắc "sau mỗi phase chạy toàn bộ" | agent làm theo plan cũ | chỉ ảnh hưởng plan đã viết; khuôn mới không còn câu đó |
| Sửa test `true` làm đổi ý nghĩa test | test không còn kiểm điều nó kiểm | thay bằng lệnh tương đương luôn thoát 0 qua `sys.executable`, đọc kỹ từng ca |
| Viết lại quy tắc 3 làm `plan-template.md` vượt trần | R13 đỏ | đo trước ở §6 Q10; dời phần giải thích sang file em |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS | Đo trước | Dự phòng nếu trượt |
|---|---|---|---|---|
| Q1 | Bán kính đúng ở ca đã đo | file lá chọn 2 module; `stop_gate.py` chọn ~11; `qc.md` chọn ~7; `tdq_state.py` → trọn bộ | nguyên mẫu ở brief: 2 · 11 · 7 · 96 module | ghi lệch, chỉnh cách dò, không nới ngưỡng |
| Q2 | Không bỏ sót test gọi qua tiến trình con | test gọi `run_hook("stop_gate.py")` được chọn khi `stop_gate.py` đổi | nguyên mẫu chọn theo tên file — đã thấy ca này trong 11 module | thêm luật dò; giữ fallback trọn bộ |
| Q3 | Dò file luật theo đường dẫn | đổi `skills/tdq-build/SKILL.md` không chọn test chỉ nhắc `skills/tdq-spec/SKILL.md` | nguyên mẫu dò theo tên trần chọn 37 module (dư) | rơi về trọn bộ cho file luật |
| Q3b | Test quét thư mục được chọn | đổi một file trong `skills/` chọn mọi test duyệt `skills/` (ví dụ `test_luat_dung.py`); đổi file trong `hooks/scripts/` không kéo các test chỉ duyệt `skills/` | đếm thô bằng regex: 6–12 test duyệt `skills/`, 0 test duyệt `hooks/` | dò theo AST; không chắc → trọn bộ cho file luật |
| Q4 | Rơi về trọn bộ đúng lúc | bán kính tối thiểu 60% số module, hoặc có file ngoài 5 thư mục → trọn bộ một tiến trình | hub chọn 96/126 = 76% · `_common` 38/126 = 30% | chỉnh ngưỡng theo số đo mới, ghi lệch |
| Q5 | Bước trung gian nhanh với file lá/luật | `vung-cham` cho `stop_gate.py` chạy không quá 60 s | chạy lẻ 11 module: 29 s; một tiến trình còn nhanh hơn | ghi lệch kèm số đo |
| Q6b | Sổ bán kính bỏ sót | `tron-bo` đỏ ở module chưa từng được `vung-cham` chọn trong request → đúng một dòng "bỏ sót"; đỏ ở module đã chọn → không ghi; lệnh in tổng số lần bỏ sót | — | — |
| Q6 | Sổ trọn bộ | mỗi lần `tron-bo` thêm đúng một dòng sổ; `next` nhắc khi vượt 2 lần (3 khi có vòng sửa) | — | — |
| Q7 | Luật một nguồn | không file luật nào còn câu "sau mỗi phase chạy toàn bộ" hay chạy trọn bộ ở mỗi vòng sửa; 3 file cùng nói 2 cổng | — | — |
| Q8 | Chạy từ mọi shell | trọn bộ gọi từ PowerShell: 0 fail, 0 error | hiện 26 fail + 1 error (test_bench 3, test_team_mode 9, test_team_chong_conflict, test_gitflow_doi, test_timing) | ghi lệch từng test còn lại kèm lý do |
| Q9 | Trọn bộ xanh | `python -m unittest discover tests` từ Git Bash xanh | lần chạy gần nhất 2.425 test OK, 353,9 s | — |
| Q10 | Trần token | mỗi file luật sửa không quá 3.500 token; `tdq-build/SKILL.md` không quá 174 dòng | `plan-template.md` 3.497 · `qc.md` 3.203 · `tdq-build/SKILL.md` 173 dòng | dời phần giải thích sang file em tầng 1 |
| Q11 | Kiến trúc | `scripts/` không import `hooks/`; `kien-truc.md` có dòng 2026-10-03 cho việc này | — | — |
| Q12 | Tiết kiệm được báo trung thực | report ghi tiết kiệm so với nền cũ (TB 7,4 lần/request) và nền mới (2–3 lần) | nền: 59 lần / 8 request; 2 request gần nhất 3 và 2 lần | — |

DoD: 8 đầu ra ở §2 có thật (1–7 và 4b) · Q1–Q12 cùng Q3b, Q6b PASS · `doc_lint` xanh trên `skills/` và trên spec này ·
`i18n_check` xanh trên file mã mới · working log mọi lượt · CHANGELOG có mục 0.57.0.

## 7. Câu hỏi còn mở

(rỗng)

## Thay đổi so với bản 1.0

User hỏi spec có làm giảm độ chính xác khi phát triển bằng workflow không, rồi chọn "1a" (2026-10-03):
- Bán kính tính thêm test quét thư mục cha của file sửa — đóng điểm mù của 1.0 (§2 dòng 1, §3, Q3b).
- Sổ bán kính bỏ sót: QC-F1 đỏ ở module bán kính không chọn → ghi lại, report in số lần (§2 dòng 4b, Q6b).
- Bảng rủi ro nói rõ cái giá: sản phẩm cuối vẫn qua trọn bộ; cái mất là phát hiện sớm ở giữa các phase.
