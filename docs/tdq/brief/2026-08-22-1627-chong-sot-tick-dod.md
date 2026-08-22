# BRIEF — Chống sót thao tác tick dòng DoD lúc đóng sổ

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-08-22 · Slug: `2026-08-22-1627-chong-sot-tick-dod`

## Nguyên văn

> tôi muốn mở request nhắc để ko bị cái này nữa trong tdq-workflow

Kèm ảnh chụp một phiên khác (request `2026-08-22-1351-detect-tam-slot-checkdiem`, KHÔNG
nằm trong repo này) cho thấy đoạn hội thoại:

> "quán DoD ... 15 dòng Definition of Done (Q1-Q15) dù QC đã xác nhận PASS cả 15. Sửa ngay."
> "Đã tick đủ 15/15 dòng DoD `[x]` — tất cả đều có bằng chứng PASS trong
> `docs/tdq/qc/2026-08-22-1351-detect-tam-slot-checkdiem.md`, chỉ là sót thao tác tick lúc
> đóng sổ. Bạn vẫn muốn commit chứ, hay cần xem lại gì thêm trước?"

### Đọc lần đầu

**Mục tiêu:** thêm cơ chế trong tdq-workflow để không còn tình trạng QC đã PASS đủ bằng
chứng nhưng các dòng Definition of Done vẫn để `[ ]` lúc đóng sổ, khiến user phải tự phát
hiện và bắt sửa.

**Phạm vi đoán:** điểm đóng sổ của một request — `scripts/tdq_finish.py`,
`scripts/doc_lint.py`, và luật đóng sổ trong `skills/tdq-build/references/qc.md` cùng
`skills/tdq-build/references/report-template.md`. Có thể chạm cả hook.

**Chỗ chưa rõ:**
- Chặn hay chỉ cảnh báo? Chặn nhầm thì mọi request đều tắc ở bước đóng sổ.
- Chặn ở đâu: `tdq_finish.py` lúc đóng turn, `doc_lint.py` lúc lint, hay hook?
- Đối tượng kiểm là dòng DoD trong plan, trong spec §6, hay bảng trong file qc?
- Làm sao máy biết "QC đã PASS" để đối chiếu với checkbox chưa tick?
- Có áp cho cả lane quick (mini-plan) không, hay chỉ lane full?
- Ngoài dòng DoD, có mở rộng sang checkbox task `[ ]`/`[~]` còn sót không?

## Hiểu & kiến thức

### Năng lực dùng được

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | skill khung đang chạy phase analyze |
| tdq-conventions | plugin:tdq-workflow | NỀN | quy ước chung, nạp đầu mọi skill |
| tdq-spec | plugin:tdq-workflow | NỀN | phase spec kế tiếp |
| tdq-plan | plugin:tdq-workflow | NỀN | phase plan kế tiếp |
| tdq-build | plugin:tdq-workflow | NỀN | phase implement, qc, report |
| tdq-status | plugin:tdq-workflow | KHÔNG | khác lĩnh vực — chỉ báo trạng thái, không chạm luật đóng sổ |
| Đã xét 213 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

### Đã đọc code — gốc rễ tìm được

Chốt chặn tick HIỆN CÓ nằm ở `hooks/scripts/stop_gate.py`, mã `TDQ:TICK` (dòng 165–180).
Nó chặn khi: turn này có sửa code, VÀ phase thuộc `implement`/`qc`, VÀ sha của file plan
không đổi trong turn. Nghĩa là nó bắt "sửa code mà quên tick", không bắt "đóng sổ mà còn
ô chưa tick".

Bộ đếm checkbox là `plan_tick_state()` trong `scripts/tdq_state.py` (dòng 588). Nó chỉ
đếm dòng khớp mẫu `_TASK_LINE` ở dòng 585:

`^\s*-\s*\[( |~|x|>)\]\s*\*\*([A-Za-z][A-Za-z0-9.]*)\*\*`

Mẫu này BẮT BUỘC có mã task in đậm ngay sau ô tick. Một dòng DoD kiểu
`- [ ] Q1 công cụ chạy được — <lệnh>` KHÔNG khớp, nên bộ đếm không thấy nó. Hệ quả:
`all_done` vẫn báo True dù 15 dòng DoD còn để trống. Đây khớp đúng với ảnh user gửi.

Khuôn plan hiện tại trong repo này ghi DoD KHÔNG có ô tick (`- Q1 … — <lệnh>`), xem
`skills/tdq-plan/references/plan-template.md` mục `## Definition of Done`. Dự án trong
ảnh dùng ô tick cho DoD. Hai kiểu viết đang song song tồn tại, và bộ đếm không hiểu kiểu
thứ hai.

Chỗ duy nhất hiện nhắc việc này là một câu văn xuôi ở
`skills/tdq-build/references/report-template.md` bước 8: "tick any leftover checkbox" —
tức đang trông vào trí nhớ của model, không có máy nào kiểm.

Request `2026-08-22-1351-detect-tam-slot-checkdiem` trong ảnh KHÔNG có trong repo này;
nó chạy ở một bản khác. Nên việc ở đây là sửa luật chung, không sửa hồ sơ của nó.

### Bối cảnh đã rõ, không hỏi lại

- tdq-workflow là công cụ user dùng thật hằng ngày, không phải thử nghiệm.
- Một người bảo trì.
- Chốt chặn chạy ở user scope, chặn nhầm là chặn mọi request của mọi dự án.

### Phạm vi đã chốt

- Mặt CHỌN: độ tin cậy của chốt chặn · phạm vi đối tượng kiểm · trải nghiệm lúc bị nhắc · khả năng bảo trì và kiểm thử
- Mặt LOẠI: hiệu năng · bảo mật · tính di động · khả năng mở rộng · tuân thủ pháp lý — không mặt nào chạm tới việc đếm ô tick trong file markdown nội bộ
- Bối cảnh: công cụ dùng thật hằng ngày, một người bảo trì, chốt chặn chạy ở user scope nên chặn nhầm là chặn mọi dự án
- Mức đầu tư suy ra: VỪA — làm kỹ bộ đếm và test, nhưng cơ chế chỉ NHẮC chứ không chặn (user chọn B), nên không cần đường gỡ chặn hay cờ bỏ qua

## Hỏi đáp

| # | Hỏi | User chốt |
|---|---|---|
| 1 | Khuôn DoD viết thế nào | A — DoD bắt buộc có ô tick, máy đếm được |
| 2 | Máy lấy đâu ra "QC đã PASS" | A — đọc file qc, đếm dòng PASS, so với số ô DoD đã tick |
| 3 | Câu nhắc hiện ở đâu | A — hook `Stop`, thêm mã `[TDQ:DOD]` |
| 4 | Nhắc ở phase nào | A — `report` và lúc chuyển sang `idle` |
| 5 | Có kiểm cả ô task còn sót không | A — có, cùng một câu nhắc |
| 6 | Mạnh tới đâu | B — chỉ NHẮC, không chặn |

### Điều chỉnh kỹ thuật so với câu 1

Câu 1A ban đầu ghi "nới `_TASK_LINE`". Sau khi truy người dùng của nó thì KHÔNG làm vậy.
`plan_tick_state()` nuôi bốn chỗ: `hooks/scripts/stop_gate.py:168`, `hooks/scripts/edit_gate.py:162`
(ba cổng), `scripts/tdq_checkstatus.py:199`. Cho dòng DoD lọt vào bộ đếm task sẽ làm `all_done`
và ETA sai ở cả bốn chỗ. Thay bằng một bộ đếm RIÊNG, chỉ quét trong mục `## Definition of Done`.
Ý người dùng chốt (DoD có ô tick, máy đếm được) giữ nguyên.

### Lộ trình

| Bước | Việc | Ra cái gì |
|---|---|---|
| 1 | Bộ đếm ô tick của mục DoD trong plan | hàm mới trong `scripts/tdq_state.py` + unit test |
| 2 | Bộ đọc kết quả PASS/FAIL từ file qc | hàm mới trong `scripts/tdq_state.py` + unit test |
| 3 | Nhắc `[TDQ:DOD]` ở hook `Stop`, chỉ phase `report` và lúc sang `idle` | sửa `hooks/scripts/stop_gate.py` + test |
| 4 | Khuôn plan: DoD viết có ô tick | sửa `skills/tdq-plan/references/plan-template.md` |
| 5 | Bước đóng sổ trong report nêu rõ tick cả DoD lẫn task | sửa `skills/tdq-build/references/report-template.md` |
| 6 | Test chống hồi quy: bộ đếm task cũ không đổi hành vi | test trên `plan_tick_state` |

### Ba câu cổng

1. Còn chỗ nào mơ hồ đủ để đổi kết quả? Không — sáu câu đã chốt, khuôn DoD và điểm bắn đã rõ.
2. Có việc nào chưa biết làm thế nào? Không — cả ba file cần sửa đều đã đọc, đã biết dòng nào.
3. Có rủi ro nào chưa gọi tên? Có một: nhắc nhầm ở request cũ (plan viết DoD kiểu không ô tick).
   Xử: không thấy ô tick nào trong mục DoD thì im lặng, không nhắc.
