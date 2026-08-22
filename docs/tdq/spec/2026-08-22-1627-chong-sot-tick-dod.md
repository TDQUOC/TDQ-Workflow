# SPEC — Chống sót tick dòng DoD lúc đóng sổ

Ngày: 2026-08-22 · Bản: 1.0 · Brief: ../brief/2026-08-22-1627-chong-sot-tick-dod.md · Lane: full
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

- Mục tiêu: lúc đóng sổ một request, nếu file plan còn ô tick chưa đánh trong mục
  `## Definition of Done` hoặc còn task chưa xong, máy phải NHẮC một dòng, thay vì trông
  vào trí nhớ của model. Đo được: hook `Stop` in ra mã `[TDQ:DOD]` đúng trong tình huống
  ấy và im lặng trong mọi tình huống còn lại.
- Trong phạm vi:
  - Bộ đếm ô tick riêng cho mục `## Definition of Done` của file plan.
  - Bộ đọc kết quả PASS/FAIL từ file `docs/tdq/qc/<slug>.md`.
  - Một nhắc mới `[TDQ:DOD]` ở hook `Stop`, chỉ chạy ở phase `report` và `idle`.
  - Sửa khuôn plan để dòng DoD viết CÓ ô tick.
  - Sửa bước đóng sổ của khuôn report cho khớp luật mới.
- NGOÀI phạm vi:
  - Hiệu năng, bảo mật, tính di động, khả năng mở rộng, tuân thủ pháp lý — không mặt nào
    chạm tới việc đếm ô tick trong file markdown nội bộ (chép từ brief `### Phạm vi đã chốt`).
  - CHẶN turn. Người dùng chốt chỉ NHẮC.
  - Sửa `_TASK_LINE` hay đổi hành vi của `plan_tick_state()`.
  - Tự động tick hộ. Máy chỉ nhắc, người tick.

## 1b. Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | việc thuần nội bộ trong workflow của chính repo này, không có nguồn ngoài nào trả lời được |
| Interview | CÓ | đã chạy: vòng scope + 5 câu chi tiết, ghi ở brief `## Hỏi đáp` |
| QC độc lập (agent) | CÓ | sửa hook chạy ở user scope, nhắc sai là nhắc mọi dự án |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Bộ đếm ô tick của mục DoD | `scripts/tdq_state.py` — hàm mới | plan có 15 ô DoD trống trả về tổng 15, xong 0; plan viết DoD không ô tick trả về tổng 0 |
| 2 | Bộ đọc kết quả file qc | `scripts/tdq_state.py` — hàm mới | file qc có 12 dòng PASS 0 dòng FAIL trả về đúng 12 và 0; không có file qc trả về "chưa có" |
| 3 | Nhắc `[TDQ:DOD]` ở hook Stop | `hooks/scripts/stop_gate.py` | phase `report`, DoD còn ô trống, qc toàn PASS → có đúng một dòng `[TDQ:DOD]`; đổi bất kỳ điều kiện nào → không có dòng nào |
| 4 | Khuôn plan viết DoD có ô tick | `skills/tdq-plan/references/plan-template.md` | mục Definition of Done của khuôn có ít nhất một dòng mở đầu bằng ô tick |
| 5 | Bước đóng sổ nêu rõ hai loại ô | `skills/tdq-build/references/report-template.md` | bước đóng sổ nhắc cả ô task lẫn ô DoD |
| 6 | Test chống hồi quy bộ đếm task | vùng test của tầng CLI | `plan_tick_state()` trên một plan có mục DoD ô tick vẫn trả về đúng số task như trước |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| dem | `scripts/tdq_state.py`, vùng test của tầng CLI | không | 1, 2, 6 |
| nhac | `hooks/scripts/stop_gate.py`, vùng test của tầng hook | dem | 3 |
| khuon | `skills/tdq-plan/references/plan-template.md`, `skills/tdq-build/references/report-template.md` | không | 4, 5 |

## 3. Cách tiếp cận & lý do

- Chọn: thêm HAI hàm đọc mới trong `scripts/tdq_state.py`, rồi cắm một nhánh nhắc mới vào
  đường `hints` sẵn có của `hooks/scripts/stop_gate.py`.
- Vì: `hints` là kênh `additionalContext`, in ra mà KHÔNG chặn turn — đúng mức mạnh người
  dùng chốt. Hai điểm chặn cứng `[TDQ:LOG]` và `[TDQ:TICK]` nằm ở nhánh khác, không đụng tới.
- Đã loại: nới `_TASK_LINE` — vì `plan_tick_state()` nuôi bốn chỗ
  (`stop_gate.py:168`, `edit_gate.py:162` ba cổng, `tdq_checkstatus.py:199`), cho dòng DoD
  lọt vào bộ đếm task sẽ làm `all_done` và ETA sai ở cả bốn chỗ.
- Đã loại: chặn turn khi còn ô trống — vì người dùng chốt mức B, chỉ nhắc.
- Đã loại: tự tick hộ khi qc toàn PASS — vì ô tick là lời tuyên bố của người làm, máy tick
  hộ thì ô tick hết còn là bằng chứng.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | skill khung đã chạy phase analyze |
| tdq-conventions | plugin:tdq-workflow | NỀN | quy ước chung |
| tdq-spec | plugin:tdq-workflow | NỀN | phase spec |
| tdq-plan | plugin:tdq-workflow | NỀN | phase plan |
| tdq-build | plugin:tdq-workflow | NỀN | phase implement, qc, report |
| Đã xét 214 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: hai hàm mới dùng đúng `_info`/`_warn` sẵn có của
  `tdq_state.py`, nhánh nhắc mới ghi một dòng `_info` nêu lý do nhắc, tắt được y hệt các
  nhánh cũ.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code viết ra bám 5 nguyên tắc SOLID theo
  `skills/tdq-conventions/references/clean-code.md`, và bám rule ngôn ngữ trong
  `skills/tdq-build/references/rules/`. Luật này luôn áp, không có cổng bật/tắt.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ:

- "`hooks/` được gọi `scripts/`; `scripts/` **không** được import `hooks/`" — việc này chạm
  ở `stop_gate.py` import từ `tdq_state`, đúng chiều cho phép.
- "Chỉ `scripts/tdq_state.py` được ghi `docs/tdq/state.json`; mọi nơi khác chỉ đọc qua CLI"
  — hai hàm mới chỉ ĐỌC file plan và file qc, không ghi state.
- "2026-07-29: hook chỉ nhắc và kiểm bằng hiệu ứng thật, không trả `deny` vì lý do chưa
  duyệt" — nhắc mới đi đường `additionalContext`, không trả `deny`.
- "File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/`" — không tạo file code mới.
- Node Hub: không chạm `main()`, `cli()`, `log()`, `cmd_build()`, `Changelog`.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Nhắc nhầm ở plan cũ viết DoD không ô tick | mọi dự án bị nhắc thừa mỗi turn | tổng ô DoD bằng 0 → im lặng tuyệt đối |
| Nhắc nhầm khi QC chưa chạy xong | nhắc lúc chưa tới lúc tick | chỉ nhắc khi file qc tồn tại, có ≥1 dòng PASS và 0 dòng FAIL |
| Nhắc lặp mỗi turn ở phase idle | phiền | chỉ nhắc khi request còn active, và trần 4 dòng 300 ký tự của hook giữ nguyên |
| Hai hàm mới làm chậm mọi turn | runtime | chỉ đọc hai file markdown, và chỉ đọc khi phase đã là `report`/`idle` |
| Sửa `tdq_state.py` làm vỡ bộ đếm task cũ | bốn chỗ dùng nó cùng sai | đầu ra 6 khoá hành vi cũ trước khi thêm hàm mới |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Bộ đếm DoD đếm đúng | plan có N ô tick trong mục DoD, M ô đã đánh `[x]` → hàm trả về đúng N và M |
| Q2 | Bộ đếm DoD bỏ qua khuôn cũ | plan viết DoD không ô tick → tổng bằng 0 |
| Q3 | Bộ đếm DoD không lẫn ô task | plan vừa có ô task vừa có ô DoD → hàm chỉ đếm ô nằm trong mục DoD |
| Q4 | Bộ đọc qc đếm đúng | file qc có P dòng PASS và F dòng FAIL → trả về đúng P và F |
| Q5 | Bộ đọc qc chịu được thiếu file | không có file qc → trả về trạng thái "chưa có", không ném lỗi |
| Q6 | Nhắc bắn đúng lúc | phase `report`, DoD còn ô trống, qc toàn PASS → đầu ra hook chứa `[TDQ:DOD]` |
| Q7 | Nhắc im ở phase khác | cùng dữ liệu nhưng phase `implement` → đầu ra không chứa `[TDQ:DOD]` |
| Q8 | Nhắc im khi DoD không có ô tick | tổng ô DoD bằng 0 → đầu ra không chứa `[TDQ:DOD]` |
| Q9 | Nhắc im khi qc chưa PASS hết | file qc có ≥1 dòng FAIL → đầu ra không chứa `[TDQ:DOD]` |
| Q10 | Nhắc nêu cả ô task còn sót | còn task chưa `[x]` → dòng nhắc nêu cả số task lẫn số ô DoD |
| Q11 | Không chặn turn | mọi tình huống nhắc đều KHÔNG có `"decision": "block"` trong đầu ra |
| Q12 | Điểm chặn cũ không đổi | `[TDQ:LOG]` và `[TDQ:TICK]` vẫn chặn đúng như trước |
| Q13 | Bộ đếm task cũ không đổi | `plan_tick_state()` trên plan có mục DoD ô tick trả về đúng số task như trước |
| Q14 | Khuôn plan đã đổi | mục Definition of Done của khuôn plan có dòng mở đầu bằng ô tick |
| Q15 | Khuôn report đã đổi | bước đóng sổ nhắc cả ô task lẫn ô DoD |
| Q16 | Log service | dòng `_info` của nhánh nhắc mới có timestamp và nêu lý do nhắc |
| Q17 | Luật ngôn ngữ ba tầng | mã và chuỗi máy in ra viết tiếng Anh, không dòng vi phạm |
| Q18 | Luật tài liệu | spec, plan, qc, report đều lint sạch |
| Q19 | Hồi quy | toàn bộ test suite giữ đúng mốc nền 37 đỏ, không đỏ mới |

DoD: đủ 19 hạng mục trên PASS, mỗi hạng mục có bằng chứng là lệnh thật kèm đầu ra thật
trong `docs/tdq/qc/2026-08-22-1627-chong-sot-tick-dod.md`.

## 7. Câu hỏi còn mở

Không còn.
