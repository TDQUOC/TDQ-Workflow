# Bảng 12 ca lệch D1–D12

Bản người đọc của hằng `CA_LECH` trong `scripts/tdq_checkstatus.py`. Một test khoá hai
nơi cho khớp mã và mức, nên sửa một bên là bên kia đỏ ngay.

Luật gốc về state, cổng duyệt và ai được ghi gì nằm ở
[tdq-conventions](../../tdq-conventions/SKILL.md) — bảng này chỉ TRỎ về đó, không chép lại.
Agent ngoài Claude Code đọc `portable/AGENTS.md` mục State và mục Ghi nhận duyệt.

Ba mức: `ok` chỉ để biết · `canh-bao` nên vá trước khi đi tiếp · `chan` phải để user quyết.
Cột lệnh vá là MẪU. Chỗ viết hoa gạch dưới phải thay bằng giá trị thật trước khi chạy.
Mọi lệnh đều mở đầu bằng `python3 scripts/tdq_state.py`; ở đây rút gọn cho gọn bảng.

| Mã | Dấu hiệu | Mức | Chẩn đoán | Lệnh vá mẫu |
|---|---|---|---|---|
| D1 | không đọc được request nào (không có, phase = idle, hoặc state hỏng) | ok | Đĩa trống thì mở request mới bằng tdq-intake; đĩa còn spec/plan thì CẤM chạy `init`, khôi phục state trước. | — (không lệnh nào chữa được) |
| D2 | phase trong state lệch bằng chứng đĩa | canh-bao | Phase khai trong state không khớp thứ đã có trên đĩa. | `set phase=PHASE_ĐÚNG` |
| D3 | sha256 của spec lệch với lúc duyệt (plan lệch chỉ là `ok`) | chan | File đã sửa sau khi duyệt — cần user duyệt lại, cấm tự approve. | — (không lệnh nào chữa được) |
| D4 | nhiều hơn một task mang dấu `[~]` | canh-bao | Không xác định được chỗ dừng: chỉ một task được phép `[~]`. | — (không lệnh nào chữa được) |
| D5 | file đăng ký trong state nhưng mất trên đĩa | chan | Mất tài sản của request — khôi phục file trước, đừng đi tiếp. | — (không lệnh nào chữa được) |
| D6 | cờ duyệt bật nhưng thiếu `*_approved_by` hoặc `*_approved_at` | canh-bao | Không truy được ai duyệt — xin user nhắc lại câu duyệt rồi ghi lại. | `approve TARGET --by "CÂU_DUYỆT_NGUYÊN_VĂN_CỦA_USER"` |
| D7 | có commit git mới hơn `updated_at` của state | canh-bao | Ai đó (agent khác/máy khác) đã làm việc mà state chưa ghi nhận. | — (không lệnh nào chữa được) |
| D8 | working log hôm nay không nhắc slug đang mở | ok | Chưa có dòng log nào cho request này hôm nay — bình thường nếu vừa mở. | — (không lệnh nào chữa được) |
| D9 | `schema_version` cũ hơn bản hiện tại | canh-bao | State do bản plugin cũ ghi — nâng schema trước khi đọc tiếp. | `set schema_version=4` |
| D10 | thiếu `started_at` hoặc `phase_history` rỗng | canh-bao | Mất mốc thời gian — bảng thời gian của report sẽ sai nếu không vá. | `set started_at=ISO_MỐC_MỞ_REQUEST` |
| D11 | có `state.json` lạc chỗ ngoài project root | chan | Hai state cùng sống: hook ghi một nơi, model đọc một nơi khác. | — (không lệnh nào chữa được) |
| D12 | có task mang dấu `[>]`: đã giao agent con mà chưa hợp nhánh về | ok | Việc còn nằm ở nhánh riêng — dò xung đột rồi hợp về nhánh tích hợp. | `tdq_team.py kiem TASK` rồi `tdq_team.py hop TASK` |

## Giới hạn đã biết

- D3 với plan chỉ ở mức `ok`: mỗi lần tick một task là plan đổi sha, nên lệch sha ở plan
  là chuyện hằng ngày. Đổi phạm vi plan phải nhìn bằng mắt, bảng này không bắt được.
- D7 đọc tối đa 20 commit gần nhất, để `report` giữ dưới 2,0 giây.
- Request mồ côi (có file trong `docs/tdq/**` nhưng state không mở) nằm NGOÀI phạm vi:
  bộ dò chỉ lo request đang mở trong state.
- Không đọc transcript của session cũ: transcript không đi theo repo khi đổi máy.
- Giá trị `schema_version` trong lệnh vá D9 lấy từ hằng `SCHEMA_HIEN_TAI` của
  `scripts/tdq_checkstatus.py`, tức bản schema hiện tại của plugin. Bảng này in ra con
  số của lúc sinh file; chạy `report` để lấy con số thật.
- D12 chỉ có ở mode `subagent`. Dấu `[>]` là "đã giao cho agent con", KHÔNG phải lỗi —
  nó chỉ trả lời câu "việc đang nằm ở đâu". Nhiều `[>]` cùng lúc là chuyện bình thường
  của mode đội; ngược lại nhiều `[~]` vẫn là ca D4 vì chỉ leader mới mang dấu `[~]`.
- D10 chỉ đề xuất lệnh vá khi thiếu `started_at`. Riêng `phase_history` rỗng thì không
  lệnh nào dựng lại được lịch sử, nên ca đó hạ xuống mức `ok`.
