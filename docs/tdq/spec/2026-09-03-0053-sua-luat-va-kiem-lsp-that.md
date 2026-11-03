# SPEC — Sửa luật thứ tự tìm kiếm và bắt kiểm LSP hoạt động thật

Ngày: 2026-09-03 · Bản: 1.0 · Brief: ../brief/2026-09-03-0053-sua-luat-va-kiem-lsp-that.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

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

## 1. Mục tiêu & phạm vi

- Mục tiêu: (a) thay luật "BẮT BUỘC gọi song song LSP + lumen ở mọi truy vấn ký hiệu code"
  bằng luật chọn lớp **theo loại truy vấn**, đúng theo số đo của báo cáo `2026-09-03-0017`;
  (b) làm cho thang kiểm **không thể báo ĐẠT khi chỉ mục liên file đang chết** — thêm một bậc
  kiểm cấu hình gốc import và một bước kiểm bằng hiệu ứng thật ở intake.
- Trong phạm vi: file luật gốc `uu-tien-tim-kiem.md`; 5 chỗ móc; `tdq-lsp-setup/SKILL.md`;
  bậc 7 trong `scripts/tdq_lsp.py`; bước kiểm hiệu ứng trong `tdq-intake`; hai file test;
  dựng lại 3 bundle portable.
- NGOÀI phạm vi: không sửa `pyrightconfig.json` đã có; không tự sinh cấu hình cho repo nào;
  không đụng `docs/kien-truc.md`; không đổi bậc 1–6 đang có; không đổi `danh-thuc`/`nha`.

## 1b. Lộ trình

Chép từ brief `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | 2 truy vấn đã trả lời đủ; phần còn lại là ràng buộc nội bộ repo |
| Interview | CÓ (xong) | 7 câu, user đã chốt 1a 2a 3a 4a 5a 6a 7a |
| diagram | CÓ | bắt buộc ở lane full; luồng "mở request → kiểm thang → kiểm hiệu ứng → vào việc" |
| Chia sub-agent | BỎ | các phần phụ thuộc nhau theo chuỗi: câu luật → 5 chỗ móc → test |
| QC độc lập (agent) | CÓ | request này chính là luật "đừng tin thang tự báo ĐẠT"; tự chấm là mắc lại đúng bẫy đó |
| Deep review | BỎ | không có thuật toán hay đánh đổi kiến trúc cần review riêng |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Câu luật mới, phân lớp theo loại truy vấn | `skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md` §1 | blockquote §1 nêu đủ 3 lớp, mỗi lớp gắn một loại truy vấn |
| 2 | Bảng "loại truy vấn → lớp nào trước", kèm số đo thật | cùng file, §2 | mỗi dòng có con số lấy từ báo cáo `2026-09-03-0017` |
| 3 | Câu luật mới chép nguyên văn vào 5 chỗ móc | `tdq-intake` ×2, `tdq-spec`, `tdq-plan`, `tdq-build` | phép kiểm khớp-từng-chữ giữa 5 chỗ móc và bản gốc chạy xanh |
| 4 | Bậc 7 — kiểm cấu hình gốc import theo ngôn ngữ | `scripts/tdq_lsp.py` | `kiem` in 7 dòng; repo này ĐẠT nhờ `pyrightconfig.json`; xoá file đó đi thì bậc 7 THIẾU và exit 3 |
| 5 | Bước kiểm bằng hiệu ứng thật ở intake | `skills/tdq-intake/SKILL.md` bước 1b | có mô tả cách đối chiếu LSP vs grep và điều kiện ĐẠT |
| 6 | Bảng thang 7 bậc cập nhật | `skills/tdq-lsp-setup/SKILL.md` | bảng có dòng bậc 7, nêu rõ nhóm A cảnh báo / nhóm B chặn |
| 7 | Test cho bậc 7 và cho câu luật mới | vùng test của module M4 (§2b) | không vượt mốc đỏ 101 fail; test mới xanh |
| 8 | 3 bundle portable dựng lại | `portable_claude/`, `portable_codex/`, `antigravity_portable/` | `python3 scripts/build_portable.py` chạy xong, `tdq_checkportable.py` không báo lệch |
| 9 | Sơ đồ luồng kiểm | `docs/tdq/diagram/<slug>.md` | phase diagram sinh, user xem được |
| 10 | Báo cáo | `docs/tdq/report/<slug>.md` | `doc_lint.py docs/tdq/report` thoát 0 |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| M1 luật | `skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md`, `skills/tdq-lsp-setup/SKILL.md` | không | 1, 2, 6 |
| M2 chỗ móc | `skills/tdq-intake/SKILL.md`, `skills/tdq-intake/references/analyze-full.md`, `skills/tdq-spec/SKILL.md`, `skills/tdq-plan/SKILL.md`, `skills/tdq-build/SKILL.md` | M1 (chép nguyên văn câu của M1) | 3, 5 |
| M3 thang | `scripts/tdq_lsp.py` | M1 (bậc 7 phải khớp mô tả ở bảng thang) | 4 |
| M4 test | `tests/` — hai file khoá thang và khoá luật; plan chỉ đích danh | M1, M2, M3 | 7 |
| M5 bundle | `portable_claude/`, `portable_codex/`, `antigravity_portable/` | M1, M2, M3 (sinh từ ba module đó) | 8 |

Ranh giới lấy từ ngữ nghĩa thật, không từ tên thư mục: `test_tdq_lsp_skill.py` đọc file luật
gốc và 5 chỗ móc (`GOC`, `CHO_MOC` dòng 14–23), nên M4 phụ thuộc M1 và M2 dù nằm khác cây thư
mục; `build_portable.py` sinh 3 bundle từ `skills/`+`hooks/`+`agents/`+`scripts/`, nên M5 phụ
thuộc M1, M2, M3. Không hai module nào khai chung một đường dẫn.

## 3. Cách tiếp cận & lý do

**Chọn — phần luật (M1, M2).** Thay câu bắt buộc-gọi-song-song bằng một câu ngắn nêu nguyên
tắc chọn lớp theo loại truy vấn, kèm trỏ về bảng đầy đủ ở file gốc (lựa chọn **7a**). Câu dự
kiến, sẽ chốt từng chữ lúc implement:

> Đối tượng tìm là ký hiệu code (hàm, class, biến, kiểu) → chọn lớp theo LOẠI truy vấn: quan
> hệ và đổi tên dùng `mcp__lsp__*`; tên chính xác đã biết dùng grep; khái niệm mơ hồ dùng
> lumen; chưa chắc thuộc loại nào thì gọi song song rồi gộp. Bảng đầy đủ kèm số đo:
> `skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md`.

Vì: báo cáo `2026-09-03-0017` đo được LSP phủ 15/15 file ở truy vấn quan hệ với 0 dương tính
giả, trong khi grep phủ 100 % nhưng precision 67 %; ở tên chính xác grep nhanh hơn ~30–60 lần
và cũng đủ 100 %; ở khái niệm mơ hồ LSP xếp đích hạng 13/62. Ba loại truy vấn có ba lớp thắng
khác nhau — một thứ tự tuyến tính duy nhất không mô tả nổi.

Đã loại — chép cả bảng vào 5 chỗ móc (7b): 5 chỗ phình ra và dễ trôi khỏi bản gốc.

**Chọn — phần thang (M3).** Bậc 7 dùng lại `do_ngon_ngu(project)` đã có, tra một bảng
`LANG_CONFIG` mới: ngôn ngữ → danh sách file mốc → nhóm A hay B. Nhóm B thiếu → THIẾU, exit 3;
nhóm A thiếu → chỉ cảnh báo (lựa chọn **4a**). Thiếu thì **chỉ in nội dung cấu hình cần tạo và
xin phép**, không tự ghi (lựa chọn **6a**).

Vì: research cho thấy nhóm B (Python, TS/JS, Lua, C/C++) có cấu hình tuỳ chọn nên hỏng âm
thầm — đúng cái bẫy đã cắn repo này; nhóm A thiếu file mốc thì dự án không build được, đã tự
lộ, chặn thêm là vô ích.

Đã loại — script tự sinh cấu hình (6b): trái luật cứng "script chỉ chẩn đoán" của
`tdq-lsp-setup`, và nội dung `extraPaths` phụ thuộc cách repo bố trí, đoán sai còn tệ hơn thiếu.

**Chọn — phần kiểm hiệu ứng (M2, ở intake bước 1b).** Sau khi thang ĐẠT, agent chọn **một hàm
bất kỳ đang có trong repo**, gọi `mcp__lsp__find_references`, rồi grep chính ký hiệu đó; ĐẠT
khi số file LSP phủ **≥** số file grep tìm được (lựa chọn **5a**). Chạy **một lần mỗi request**,
ngay ở intake (lựa chọn **2a**).

Vì: đây là phép kiểm duy nhất bắt được lỗi 7 % ↔ 100 % — mọi bậc kiểm sự tồn tại đều báo ĐẠT
suốt thời gian repo hỏng. Không neo vào file/dòng cố định nên code đổi không làm đỏ giả.

Đã loại — "LSP trả khác rỗng là ĐẠT" (5c): đúng bằng mức đã để lọt lỗi, vì 13 caller cũng khác
rỗng. Đã loại — neo cố định vào một hàm mốc (5b): phải bảo trì cái mốc.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-lsp-setup | plugin:tdq-workflow | DÙNG | đầu ra 1, 2, 6 — chính là skill bị sửa |
| tdq-intake | plugin:tdq-workflow | NỀN | skill khung đang chạy; cũng là nơi thêm đầu ra 5 |
| tdq-conventions | plugin:tdq-workflow | NỀN | luật git, log, tick, QC áp cho cả request |
| tdq-diagram | plugin:tdq-workflow | DÙNG | đầu ra 9 |
| tdq-spec / tdq-plan / tdq-build | plugin:tdq-workflow | DÙNG | vừa là phase kế tiếp, vừa là 3 trong 5 chỗ móc phải sửa |
| tdq-qc-tester (agent) | plugin:tdq-workflow | DÙNG | QC độc lập ở §6, theo lộ trình §1b |
| Đã xét 217 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực — `skill_inventory.py --loc` giữ 0 dòng |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: `scripts/tdq_lsp.py` đã có `_log()`/`_log_enabled()`; bậc 7 ghi
  log theo đúng khuôn `bậc N … → ĐẠT/THIẾU` như 6 bậc hiện có, không thêm cơ chế log mới.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code viết ra bám 5 nguyên tắc SOLID theo `skills/tdq-conventions/references/clean-code.md`,
  và bám rule ngôn ngữ trong `skills/tdq-build/references/rules/`.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md`, chỉ dòng việc này chạm tới):

- *"`skills/` chỉ được nhắc tên lệnh của `scripts/`, cấm chép nội dung script vào skill — hai
  bản chép tay sẽ lệch nhau và không có phép kiểm nào bắt được."* — việc này chạm ở bảng thang
  trong `tdq-lsp-setup/SKILL.md`: bảng chỉ được mô tả bậc 7 làm gì, **cấm chép bảng
  `LANG_CONFIG`** từ `tdq_lsp.py` sang.
- *"Luật bản ngoài `portable_*` SINH bằng `scripts/build_portable.py`, không sửa tay."* — việc
  này chạm ở M5: chỉ chạy lệnh sinh, không mở file trong 3 bundle ra sửa.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| `test_cau_goc_du_ba_lop` khoá thứ tự `mcp__lsp__` < `lumen` < `grep`, câu mới đổi thứ tự | test đỏ ngay khi sửa câu luật | task M4 sửa test **cùng lượt** với M1; test mới kiểm "đủ 3 lớp + mỗi lớp gắn một loại truy vấn" thay vì kiểm thứ tự chữ |
| Bậc 7 chặn (exit 3) có thể chặn cả repo nhóm B đang chạy bình thường ở máy khác | user không mở được request mới | bậc 7 in đúng nội dung file cần tạo; và tài liệu nói rõ đây là cảnh báo có thật, không phải dương tính giả |
| Bảng `LANG_CONFIG` phải khớp đúng 27 khoá của `LANG_SERVER` | ngôn ngữ lọt bảng → bậc 7 nổ `KeyError` | test khoá hai bảng cùng bộ khoá |
| Bước kiểm hiệu ứng là luật mềm, không hook chặn | agent có thể bỏ qua | ghi là **lỗi QC** giống các luật mềm khác; bằng chứng phải nằm trong brief |
| Sửa `skills/` mà quên dựng lại 3 bundle | bản portable lệch bản gốc | `tdq_checkportable.py` nằm trong DoD |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Câu luật mới có ở đủ 5 chỗ móc, khớp từng chữ | `test_tdq_lsp_skill.py` xanh |
| Q2 | Câu luật mới nêu đủ 3 lớp, mỗi lớp gắn đúng một loại truy vấn | test mới xanh; đọc lại §1 file gốc thấy đủ 3 cặp |
| Q3 | Bậc 7 ĐẠT trên repo này | `kiem` in 7 dòng, bậc 7 ĐẠT, tổng 7/7, exit 0 |
| Q4 | Bậc 7 bắt được lỗi thật | tạm đổi tên `pyrightconfig.json` → bậc 7 THIẾU và exit 3; đổi tên lại → ĐẠT |
| Q5 | Bậc 7 phân đúng nhóm | repo giả lập chỉ có file Go không `go.mod` → cảnh báo, không chặn |
| Q6 | Bảng `LANG_CONFIG` phủ đúng bộ khoá của `LANG_SERVER` | test so hai bộ khoá xanh |
| Q7 | Bước kiểm hiệu ứng có mặt ở intake và mô tả đủ để làm theo | đọc `tdq-intake/SKILL.md` bước 1b thấy cách đối chiếu và điều kiện ĐẠT |
| Q8 | Không hồi quy | `pytest tests/ -q` không vượt mốc **101 fail / 1453 pass**, không file đỏ mới |
| Q9 | 3 bundle khớp bản gốc | `tdq_checkportable.py` không báo lệch |
| Q10 | Tài liệu sạch | `doc_lint.py` thoát 0 trên spec, plan, report |
| Q11 | QC độc lập | agent `tdq-qc-tester` chấm PASS toàn bộ DoD |

DoD: đủ 10 đầu ra ở §2; Q1–Q11 PASS; `git status --porcelain` không còn file rác ngoài các
vùng đã khai ở §2b; báo cáo nêu rõ trạng thái thang trước (6/6 ĐẠT trong khi độ phủ 7 %) và sau.

## 7. Câu hỏi còn mở

(Rỗng.)
