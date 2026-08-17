---
name: tdq-check-status
description: Khôi phục request TDQ đang dở: đọc thẳng đĩa, báo cáo, tiếp tục sau một lần user gật. Dùng khi session cũ chết, khi đổi máy, hoặc khi agent khác vừa làm hộ một phase.
---

# TDQ Check Status — dò request đang dở rồi tiếp tục

Nạp [tdq-conventions](../tdq-conventions/SKILL.md). Skill này KHÔNG thuộc phase nào: gọi
được ở bất kỳ phase nào, kể cả khi `state.json` sai hoặc thiếu.

Khác [tdq-status](../tdq-status/SKILL.md): `tdq-status` báo nhanh state đang khai gì.
Skill này đối chiếu state với ĐĨA rồi khôi phục — nặng hơn, chỉ dùng khi mất ngữ cảnh.

## Luật cứng — không mất dữ liệu

- **Đĩa là bằng chứng, `state.json` là lời khai.** Lệch nhau thì tin đĩa.
- **Cấm tuyệt đối** `tdq_state.py` với lệnh con `init` hay `reset`, cấm xoá hay ghi đè
  brief/spec/plan/qc/report đã có. Hai lệnh đó xoá sạch request đang mở.
- Chỉ được chạy lệnh vá thuộc đúng hai họ: `tdq_state.py set …` và `tdq_state.py approve …`.
- **Một cổng gật duy nhất.** Trình báo cáo → chờ user gật → chạy hết lệnh vá → đi tiếp.
  Không hỏi lần hai, cũng không tự chạy khi user chưa gật.
- Kết luận `CẦN USER QUYẾT` thì DỪNG, trình câu hỏi, cấm tự đoán ý user.
- **`state.json` hỏng KHÁC không có state.** Hỏng mà đĩa còn spec/plan là ca D1 mức `chan`:
  trình cho user, xin dựng lại state. Coi nó như "chưa có request" là mất cả request.

## Các bước

1. Chạy bộ dò (chỉ đọc, không ghi gì):
   ```
   python3 "${CLAUDE_PROJECT_DIR}/.claude/tdq/scripts/tdq_checkstatus.py" report
   ```
   Cần dữ liệu máy đọc thì thêm `--json`. Script tự dò project root; ép bằng `--project`.

2. Đọc output. Nó đã đúng khuôn 6 mục của
   [references/report-template.md](references/report-template.md) — in lại nguyên văn cho
   user, không tóm tắt lại theo ý mình, không thêm phán đoán ngoài bảng.

3. Tra từng mã ca lệch trong [references/bang-lech.md](references/bang-lech.md) để hiểu
   ý nghĩa và giới hạn của nó. Bảng đó là nguồn duy nhất; cấm tự nghĩ thêm chẩn đoán.

4. Rẽ theo đúng dòng `## Kết luận`:
   - `TIẾP TỤC ĐƯỢC` → báo một dòng rồi làm tiếp việc ở mục `## Việc kế tiếp`.
   - `VÁ RỒI TIẾP TỤC` → in khối `## Lệnh vá đề xuất` và hỏi user đúng một câu:
     "Chạy các lệnh vá này rồi tiếp tục?" **DỪNG chờ user.**
   - `CẦN USER QUYẾT` → in các ca mức `chan`, nêu lựa chọn theo khuôn option của
     conventions, **DỪNG chờ user**. Cấm chạy lệnh vá nào.

5. User gật ở bước 4 → chạy nguyên văn từng lệnh trong khối lệnh vá, theo đúng thứ tự.
   Lệnh nào không thuộc hai họ `set`/`approve` thì KHÔNG chạy và báo lại — đó là lỗi của
   bộ dò, không phải việc để tự sửa tay.

6. Chạy lại bước 1 một lần để xác nhận kết luận đã lên `TIẾP TỤC ĐƯỢC`.

7. Bàn giao đúng phase đang đứng, theo
   [phases.md](../tdq-conventions/references/phases.md):
   - `analyze` / `spec` → [tdq-spec](../tdq-spec/SKILL.md); phase có cổng duyệt thì
     trình lại đúng cổng đó rồi DỪNG chờ user duyệt.
   - `plan` → [tdq-plan](../tdq-plan/SKILL.md), cũng dừng ở cổng duyệt plan.
   - `implement` / `qc` / `report` → [tdq-build](../tdq-build/SKILL.md), chạy tiếp ngay.
     Ở `implement`, vào đúng task mà báo cáo chỉ ra là đang `[~]`.

Xong khi: user đã đọc báo cáo, mọi lệnh vá cần chạy đã chạy, và skill của phase đúng
đã được nạp để làm tiếp.
Bước kế tiếp: skill ở bước 7 tương ứng với phase hiện tại.
