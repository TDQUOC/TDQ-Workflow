# SPEC — Đo trước ở spec, implement chạy hết plan trong một lượt

Ngày: 2026-10-03 · Bản: 1.0 · Brief: ../brief/2026-10-03-0732-do-truoc-lam-mot-turn.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: ĐÃ DUYỆT (2026-10-03, "Duyệt spec")

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

- Mục tiêu: (1) mọi ngưỡng số trong DoD của một spec mới mang số đo hoặc ước lượng có nguồn, cùng
  phương án dự phòng chọn sẵn, TRƯỚC khi spec được duyệt — máy từ chối duyệt khi thiếu; (2) đã vào
  `implement`/`qc` thì một ngưỡng trượt không còn là lý do dừng: agent áp phương án dự phòng, ghi
  lệch, làm hết plan trong lượt đó và chỉ hỏi user ở report.
- Trong phạm vi:
  - luật lint R14 cho `docs/tdq/spec/` + cổng `approve spec` gọi nó;
  - khuôn §6 của spec thêm 2 cột `Đo trước`, `Dự phòng nếu trượt` + hướng dẫn đo;
  - lệnh `tdq_state.py lech` (ghi / liệt kê / duyệt / bác lệch spec) + hiển thị ở QC và report;
  - `pause` chỉ nhận 4 loại bất khả kháng (`--loai`);
  - hook nhắc `[TDQ:ASK]` khi `AskUserQuestion` được gọi ở phase `implement`/`qc` (chỉ nhắc);
  - sửa luật dừng ở `tdq-build`, `tdq-conventions`, `phases.md`, `qc.md`, `report-template.md`;
  - lời chặn của `stop_gate.py` và `agy_stop_gate.py` nêu `--loai`;
  - quyết định kiến trúc trong `docs/kien-truc.md`; CHANGELOG + bump bản.
- NGOÀI phạm vi:
  - không chặn `AskUserQuestion` (user chọn "chỉ nhắc");
  - không sửa `plan-template.md` (3.497/3.500 token — xem §5);
  - không áp R14 lên 103 spec cũ (mốc ngày, xem §3);
  - lane `quick` không có §6 dạng bảng → không áp R14; luật dừng mới vẫn áp cho quick;
  - Codex không có `AskUserQuestion` → không có hook nhắc tương đương; luật trong skill vẫn áp.

## 1b. Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | việc thuần nội bộ, không có ẩn số bên ngoài |
| Vòng phạm vi | BỎ | câu hỏi đầu đã chốt cả bốn mặt |
| Interview chi tiết | CÓ | một vòng, 4 câu, hết câu hỏi |
| Soát lỗi `code-review` + rút gọn `simplify` | CÓ | sửa luật dừng và cổng duyệt của mọi request sau |
| QC độc lập (agent) | BỎ | mức QC `full`, không phải `ultra` |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Luật R14: hàng §6 có ngưỡng số phải có `Đo trước` và `Dự phòng nếu trượt` không rỗng | `scripts/doc_lint.py` | test đỏ trên hàng `≤ 200 MB` thiếu cột; xanh khi đủ; im với spec trước mốc |
| 2 | `approve spec` từ chối khi R14 đỏ; `--bo-qua-do "<lý do>"` ghi lý do vào state | `scripts/tdq_state.py` | test: spec thiếu đo → exit ≠ 0, `spec_approved` vẫn false |
| 3 | Khuôn §6 thêm 2 cột + hướng dẫn "đo thế nào, biên bao nhiêu" | `skills/tdq-spec/references/spec-template.md`, `spec-template-huong-dan.md`, `skills/tdq-spec/SKILL.md` | bản khuôn chép ra qua được R14 |
| 4 | Lệnh `lech add/list/duyet/bac` lưu `lech_spec` trong state | `scripts/tdq_state.py` | test vòng đời một lệch |
| 5 | `pause --loai <mat-truy-cap\|pha-huy\|dau-vao-user\|tran-qc> --ly-do` — thiếu/sai loại thì từ chối | `scripts/tdq_state.py` | test 4 loại nhận, `doi-spec` bị từ chối |
| 6 | Hook nhắc `[TDQ:ASK]` trên `AskUserQuestion` ở `implement`/`qc` | `hooks/scripts/ask_gate.py`, `hooks/hooks.json`, `_common.CODES` | test: nhắc ở implement, im ở spec/analyze, không bao giờ deny |
| 7 | Lời chặn `[TDQ:UNFINISHED]` nêu `pause --loai` | `hooks/scripts/stop_gate.py`, `hooks/scripts/agy_stop_gate.py` | test chuỗi lời chặn |
| 8 | Luật dừng mới: gỡ "đổi phạm vi spec/plan"; lệch → dự phòng + `lech` + làm tiếp | `skills/tdq-build/SKILL.md`, `skills/tdq-conventions/SKILL.md`, `references/phases.md` | `grep` không còn "scope change" là lý do dừng; test luật |
| 9 | QC ghi "PASS (lệch, chờ duyệt)"; report liệt kê lệch và hỏi duyệt; bác → task fix, quay lại implement | `skills/tdq-build/references/qc.md`, `report-template.md` | test luật đọc chuỗi |
| 10 | `next` ở phase report in các lệch chưa duyệt | `scripts/tdq_state.py` (`PHASE_TABLE`/`render_next`) | test |
| 11 | Mã `TDQ:ASK` trong bảng mã | `skills/tdq-conventions/references/reminder-codes.md` | test bảng ↔ `CODES` |
| 12 | Quyết định kiến trúc có ngày | `docs/kien-truc.md` | dòng 2026-10-03 |
| 13 | CHANGELOG, bump 0.56.0; bộ dựng portable vẫn đúng (layout sinh tại máy đích, không nằm trong repo) | `CHANGELOG.md`, 2 `plugin.json` | test bộ dựng portable xanh |

## 2b. Ranh giới module

Lấy theo import thật: `tdq_state.py` là hub (gọi từ mọi hook), `doc_lint.py` độc lập, hook mới
chỉ import `_common` + `tdq_state`.

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| lint | `scripts/doc_lint.py` + test đi kèm | không | 1 |
| state | `scripts/tdq_state.py`, `scripts/tdq_ten_lenh.py` + test đi kèm | lint | 2, 4, 5, 10 |
| hook | `hooks/scripts/ask_gate.py`, `hooks/scripts/_common.py`, `hooks/hooks.json`, `hooks/scripts/stop_gate.py`, `hooks/scripts/agy_stop_gate.py` + test đi kèm | state | 6, 7 |
| luat | `skills/tdq-build/**`, `skills/tdq-conventions/**`, `skills/tdq-spec/**`, `docs/kien-truc.md`, `docs/tdq/token-budget.json` + test đi kèm | state, hook | 3, 8, 9, 11, 12 |
| phat-hanh | `CHANGELOG.md`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` | luat | 13 |

## 3. Cách tiếp cận & lý do

- Chọn: **đo ở spec, máy giữ cổng duyệt; lệch lúc chạy thì có đường ghi thay cho đường dừng.**
  - R14 nhận ngưỡng số trong hàng `| Qn |` của §6: so sánh (`≤ ≥ < > tối đa tối thiểu không quá
    ít nhất dưới trên`) đi kèm một số khác 0 và 1, hoặc một số kèm đơn vị (`MB GB KB % ms giây phút
    token ký tự dòng`). `≥ 1`, `= 0` là phép tồn tại/vắng mặt, không phải ngưỡng.
  - R14 chỉ áp cho spec có slug từ `2026-10-03-0732` trở đi — spec cũ là hồ sơ, không sửa lại.
  - `approve spec` gọi hàm R14 trực tiếp (`scripts/` → `scripts/`, hợp luật import).
  - `lech` lưu vào state chứ không vào plan: plan là file user đã duyệt; state là nơi máy đọc
    được cho `next`, QC và report.
- Vì: ca 232 MB là lỗi THIẾU ĐO, không phải lỗi thiếu ý chí — ước lượng installer chỉ cần đọc
  kích thước bộ cài WebView2 offline. Bắt nó ở spec rẻ hơn mọi cách xử lý ở implement. Còn khi
  vẫn trượt, phương án đã chọn sẵn ở cột `Dự phòng` biến câu hỏi thành một việc làm.
- Đã loại:
  - Chặn `AskUserQuestion` ở implement — user chọn chỉ nhắc.
  - Áp R14 cho mọi spec cũ — 138 hàng ở 103 spec sẽ đỏ hồi tố mà không ai sửa.
  - Thêm cột dự phòng vào khuôn plan — `plan-template.md` 3.497/3.500 token; dự phòng gắn với
    ngưỡng nên thuộc spec §6.
  - Ghi lệch thẳng vào plan bằng tay — không kiểm được bằng máy.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-spec, tdq-plan, tdq-build, tdq-conventions | plugin:tdq-workflow | NỀN | khung đang chạy, đồng thời là vùng sửa |
| code-review | built-in | DÙNG | soát lỗi đúng-sai trước QC |
| simplify | built-in | DÙNG | rút gọn trùng lặp sau soát lỗi |
| Đã xét 13 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: `ask_gate.py` và các nhánh mới của `tdq_state.py`/`doc_lint.py` log
  ISO timestamp ra stderr, tắt bằng `TDQ_LOG=0`.
- Không placeholder, không TODO stub.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code bám SOLID theo `skills/tdq-conventions/references/clean-code.md` và rule Python trong
  `skills/tdq-build/references/rules/`. Mã, chú thích, chuỗi máy in ra bằng tiếng Anh.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ:
- `scripts/` không import `hooks/` — `approve spec` gọi R14 trong `scripts/doc_lint.py`.
- Mọi deny đi qua `_common.block()` — `ask_gate.py` không deny, chỉ `_common.remind()`.
- 2026-07-29: không hook nào chặn vì "chưa duyệt" — cổng mới nằm ở LỆNH duyệt, không ở hook.
- Mỗi điểm chặn mới cần dòng quyết định có ngày — `approve spec` từ chối là một điểm chặn mới.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| R14 bắt oan một số không phải ngưỡng (số phiên bản, số task) | spec đúng bị từ chối duyệt | chỉ quét cột điều kiện của hàng `Qn`; bỏ 0 và 1; test với 10 hàng lấy từ spec thật; lối `--bo-qua-do` |
| Agent điền "Đo trước" cho có ("ước lượng: ổn") | cổng thành thủ tục | R14 đòi trong ô có một con số; hướng dẫn nêu nguồn + biên |
| Gỡ "đổi phạm vi" khỏi danh sách dừng làm agent tự đổi phạm vi lớn | làm ngoài ý user | lệch chỉ áp cho NGƯỠNG đã có dự phòng; thêm/bớt đầu ra §2 vẫn là "đầu vào chỉ user có" |
| Token file luật vượt trần 3.500 | `doc_lint` R13 đỏ | đo trước ở §6 Q15 |
| Đổi chuỗi lời chặn làm vỡ test cũ của stop gate | suite đỏ | sửa test cùng task |

## 6. QC & Definition of Done

Cột `Đo trước` và `Dự phòng nếu trượt` dùng đúng khuôn mới — spec này tự áp luật nó đặt ra.

| # | Hạng mục kiểm | Điều kiện PASS | Đo trước | Dự phòng nếu trượt |
|---|---|---|---|---|
| Q1 | R14 bắt ngưỡng thiếu đo | hàng `Installer ≤ 200 MB` thiếu 2 cột → R14 đỏ | — | — |
| Q2 | R14 im khi đủ cột | cùng hàng có `Đo trước: 212 MB + ~20 MB` và `Dự phòng` → xanh | — | — |
| Q3 | R14 không bắt phép tồn tại | `≥ 1 test`, `0 failure`, `= 0 dòng` → không bị coi là ngưỡng | — | — |
| Q4 | R14 không hồi tố | `doc_lint docs/tdq/spec` trên 103 spec cũ → 0 lỗi R14 | 0 lỗi (mốc slug `2026-10-03-0732` loại hết spec cũ) | — |
| Q5 | Độ chính xác trên spec thật | trong 10 hàng mẫu có ngưỡng từ spec cũ, R14 nhận đúng ≥ 9 | bộ nhận diện thử: 138/1.086 hàng ở 103 spec, mẫu 14 hàng đọc tay không thấy bắt oan | thu hẹp đơn vị/so sánh; ghi lệch |
| Q6 | `approve spec` từ chối | spec thiếu đo → exit ≠ 0, `spec_approved` false | — | — |
| Q7 | Lối thoát có lý do | `approve spec --bo-qua-do "<lý do>"` → duyệt, lý do nằm trong state | — | — |
| Q8 | Vòng đời lệch | `lech add` → `list` → `duyet`/`bac`; trạng thái đúng từng bước | — | — |
| Q9 | `pause` phân loại | 4 loại được nhận; thiếu `--loai` hoặc `doi-spec` → từ chối | — | — |
| Q10 | Hook nhắc | `AskUserQuestion` ở implement/qc → `[TDQ:ASK]`; ở spec → im; không bao giờ deny | — | — |
| Q11 | Lời chặn Stop | `[TDQ:UNFINISHED]` nêu `pause --loai` ở cả `stop_gate` và `agy_stop_gate` | — | — |
| Q12 | Luật dừng | không file luật nào còn cho dừng vì "đổi phạm vi spec/plan"; 4 loại có mặt ở `tdq-build` và `tdq-conventions` | — | — |
| Q13 | QC/report thấy lệch | `next` ở phase report in mọi lệch chưa duyệt; `qc.md` và `report-template.md` có luật | — | — |
| Q14 | Kiến trúc | `kien-truc.md` có dòng 2026-10-03; `TDQ:ASK` trong `CODES` và bảng mã; `scripts/` không import `hooks/` | — | — |
| Q15 | Trần token | mỗi file luật sửa ≤ 3.500 token | `qc.md` 2.959 · `report-template.md` 1.901 · `phases.md` 1.792 · `reminder-codes.md` 1.389 · `spec-template.md` 2.512 · `spec-template-huong-dan.md` 1.035 — phần thêm dự kiến ≤ 300 token/file | dời phần có điều kiện sang file em, như 0.54.0 |
| Q16 | Trọn bộ test | `python -m unittest discover tests` xanh | lần chạy gần nhất: 2.336 test OK, 346 s | — |
| Q17 | Ba hệ | trọn bộ test trên Windows; macOS/Linux khi máy bật | hai máy không trả lời ping lúc 02:45 hôm nay | ghi nợ có lý do, như request trước |

DoD: 13 đầu ra ở §2 có thật · Q1–Q16 PASS, Q17 cho phép để ngỏ macOS/Linux kèm lý do · `doc_lint`
xanh trên `skills/` và trên chính spec này · `i18n_check` xanh trên file mã mới · working log mọi
lượt · CHANGELOG có mục 0.56.0.

## 7. Câu hỏi còn mở

(rỗng)
