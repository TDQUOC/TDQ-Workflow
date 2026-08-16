# Check status — dò request đang dở rồi tiếp tục (mọi phase)

Bản portable của skill `tdq-check-status`, cùng số bước với bản `skills/`. Dùng khi mất
ngữ cảnh: session cũ chết, đổi sang máy khác, hoặc một agent khác vừa làm hộ một phase.

## Luật cứng — không mất dữ liệu

- **Đĩa là bằng chứng, `state.json` là lời khai.** Lệch nhau thì tin đĩa.
- **Cấm tuyệt đối** hai lệnh con xoá sạch request đang mở của `tdq_state.py`
  (lệnh khởi tạo lại và lệnh đặt về mặc định), cấm xoá hay ghi đè
  brief/spec/plan/qc/report đã có.
- Chỉ được chạy lệnh vá thuộc đúng hai họ: `tdq_state.py set …` và `tdq_state.py approve …`.
- **Một cổng gật duy nhất.** Trình báo cáo → chờ user gật → chạy hết lệnh vá → đi tiếp.
- Kết luận `CẦN USER QUYẾT` thì DỪNG, trình câu hỏi, cấm tự đoán ý user.

## Các bước

1. Chạy bộ dò (chỉ đọc, không ghi gì):
   ```
   python3 scripts/tdq_checkstatus.py report
   ```
   Cần dữ liệu máy đọc thì thêm `--json`. Harness không chạy được Python thì đọc tay
   `docs/tdq/state.json`, `docs/tdq/{brief,spec,plan,qc,reports}/<slug>.md`, `git log -20`,
   `git status --short` và working log hôm nay, rồi tự chấm theo bảng ở mục dưới.

2. Đọc output. Nó đã đúng khuôn 6 mục — in lại nguyên văn cho user, không tóm tắt lại
   theo ý mình, không thêm phán đoán ngoài bảng. Sáu mục: `## Request` ·
   `## Bằng chứng trên đĩa` · `## Ca lệch phát hiện` · `## Kết luận` ·
   `## Lệnh vá đề xuất` · `## Việc kế tiếp`.

3. Tra từng mã ca lệch trong bảng D1–D11 ở mục cuối file này để hiểu ý nghĩa và giới
   hạn của nó. Bảng đó là nguồn duy nhất; cấm tự nghĩ thêm chẩn đoán.

4. Rẽ theo đúng dòng `## Kết luận`:
   - `TIẾP TỤC ĐƯỢC` → báo một dòng rồi làm tiếp việc ở mục `## Việc kế tiếp`.
   - `VÁ RỒI TIẾP TỤC` → in khối `## Lệnh vá đề xuất` và hỏi user đúng một câu:
     "Chạy các lệnh vá này rồi tiếp tục?" **DỪNG chờ user.**
   - `CẦN USER QUYẾT` → in các ca mức `chan`, nêu lựa chọn theo khuôn option của
     `AGENTS.md`, **DỪNG chờ user**. Cấm chạy lệnh vá nào.

5. User gật ở bước 4 → chạy nguyên văn từng lệnh trong khối lệnh vá, theo đúng thứ tự.
   Lệnh nào không thuộc hai họ `set`/`approve` thì KHÔNG chạy và báo lại.

6. Chạy lại bước 1 một lần để xác nhận kết luận đã lên `TIẾP TỤC ĐƯỢC`.

7. Bàn giao đúng phase đang đứng, theo [phases.md](phases.md):
   - `analyze` / `spec` → [02-spec.md](02-spec.md); phase có cổng duyệt thì trình lại
     đúng cổng đó rồi DỪNG chờ user duyệt.
   - `plan` → [03-plan.md](03-plan.md), cũng dừng ở cổng duyệt plan.
   - `implement` / `qc` / `report` → [04-build.md](04-build.md), chạy tiếp ngay.
     Ở `implement`, vào đúng task mà báo cáo chỉ ra là đang `[~]`.

Xong khi: user đã đọc báo cáo, mọi lệnh vá cần chạy đã chạy, và tài liệu phase đúng đã
được mở để làm tiếp.
Bước kế tiếp: file ở bước 7 tương ứng với phase hiện tại.

## Bảng 11 ca lệch D1–D11

Ba mức: `ok` chỉ để biết · `canh-bao` nên vá trước khi đi tiếp · `chan` phải để user quyết.
Cột lệnh vá là MẪU. Chỗ viết hoa gạch dưới phải thay bằng giá trị thật trước khi chạy.
Mọi lệnh đều mở đầu bằng `python3 scripts/tdq_state.py`; ở đây rút gọn cho gọn bảng.
Luật gốc về state và cổng duyệt nằm ở `AGENTS.md` mục State và mục Ghi nhận duyệt.

| Mã | Dấu hiệu | Mức | Lệnh vá mẫu |
|---|---|---|---|
| D1 | không đọc được request nào (không có, phase = idle, hoặc state hỏng) | ok / `chan` khi state hỏng mà đĩa còn spec/plan | — |
| D2 | phase trong state lệch bằng chứng đĩa | canh-bao | `set phase=PHASE_ĐÚNG` |
| D3 | sha256 của spec lệch với lúc duyệt | chan | — |
| D4 | nhiều hơn một task mang dấu `[~]` | canh-bao | — |
| D5 | file đăng ký trong state nhưng mất trên đĩa | chan | — |
| D6 | cờ duyệt bật nhưng thiếu người duyệt hoặc mốc duyệt | canh-bao | `approve TARGET --by "CÂU_DUYỆT"` |
| D7 | có commit git mới hơn `updated_at` của state | canh-bao | — |
| D8 | working log hôm nay không nhắc slug đang mở | ok | — |
| D9 | `schema_version` cũ hơn bản hiện tại | canh-bao | `set schema_version=BẢN_HIỆN_TẠI` |
| D10 | thiếu `started_at` hoặc `phase_history` rỗng | canh-bao, riêng chỉ rỗng `phase_history` là ok | `set started_at=ISO_MỐC_MỞ_REQUEST` |
| D11 | có `state.json` lạc chỗ ngoài project root | chan | — |

## Giới hạn đã biết

- D3 với plan chỉ ở mức `ok`: mỗi lần tick một task là plan đổi sha, nên lệch sha ở plan
  là chuyện hằng ngày. Đổi phạm vi plan phải nhìn bằng mắt.
- D7 đọc tối đa 20 commit gần nhất, để `report` giữ dưới 2,0 giây.
- Request mồ côi (có file trong `docs/tdq/**` nhưng state không mở) nằm NGOÀI phạm vi.
- Không đọc transcript của session cũ: transcript không đi theo repo khi đổi máy.
