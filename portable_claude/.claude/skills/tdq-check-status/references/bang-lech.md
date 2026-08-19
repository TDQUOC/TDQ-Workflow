# Bảng 12 ca lệch D1–D12

Human-readable mirror of constant `CA_LECH` in `scripts/tdq_checkstatus.py`. A test locks the
two places to the same codes and the same levels, so editing one side turns the other red.

The root rules on state, approval gates and who may write what live in
[tdq-conventions](../../tdq-conventions/SKILL.md) — this table only POINTS there, it copies
nothing. An agent outside Claude Code reads `portable/AGENTS.md`, sections State and
Ghi nhận duyệt.

Three levels: `ok` for information only · `canh-bao` should be patched before moving on ·
`chan` must be decided by the user.
The patch-command column is a TEMPLATE. Every UPPERCASE_UNDERSCORED slot must be replaced
with the real value before running.
Every command starts with `python3 scripts/tdq_state.py`; it is shortened here to keep the
table narrow.

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

- D3 on the plan is only level `ok`: every task tick changes the plan's sha, so a sha drift on
  the plan is an everyday event. A change in the plan's SCOPE has to be seen by eye — this
  table cannot catch it.
- D7 reads at most the 20 most recent commits, to keep `report` under 2,0 seconds.
- Orphan requests (files under `docs/tdq/**` with no open request in the state) are OUT OF
  SCOPE: the detector only handles the request the state has open.
- It does not read an old session's transcript: a transcript does not travel with the repo
  when the machine changes.
- The `schema_version` value in patch D9 comes from constant `SCHEMA_HIEN_TAI` of
  `scripts/tdq_checkstatus.py`, i.e. the plugin's current schema. This table prints the number
  as of the day the file was generated; run `report` to get the real one.
- D12 only exists in mode `subagent`. The mark `[>]` means "handed to a sub-agent", it is NOT
  an error — it only answers "where does the work sit right now". Several `[>]` at once is
  normal in team mode; several `[~]`, by contrast, is still case D4, because only the leader
  ever carries `[~]`.
- D10 proposes a patch command only when `started_at` is missing. An empty `phase_history`
  cannot be rebuilt by any command, so that case is lowered to level `ok`.
