# REPORT — TDQ 0.2.0: hard gate → nhắc nhở, duyệt bằng chat tự nhiên

Ngày: 2026-07-28 · Lane full · Mode: main · Trạng thái: **HOÀN THÀNH**
[request](../requests/2026-07-28-soft-gates-remind.md) · [spec](../spec/2026-07-28-soft-gates-remind.md) · [plan](../plan/2026-07-28-soft-gates-remind.md) · [QC](../qc/2026-07-28-soft-gates-remind.md)

## Vấn đề

0.1.8 có 3 lớp deny cứng (`edit_gate`, `bash_gate`, `approve_gate`). Mọi sai lệch state biến thành bế tắc: user gõ đúng lệnh duyệt vẫn bị từ chối ("đã duyệt rồi", "thiếu mode", "sai lane"), Claude lại không được phép sửa state → phải nhờ session khác gỡ. Đúng cú pháp trở thành điều kiện để làm việc.

## Đã đổi gì

1. **Duyệt bằng chat thường.** "duyệt spec", "ok plan mode main", "duyệt quick" — Claude nhận diện và ghi vào state bằng `tdq_state.py approve <target> [--mode …] --by "<nguyên văn>"`. Duyệt lại lần hai in thông báo và exit 0, không còn là lỗi.
2. **Hook chỉ nhắc.** `edit_gate`/`bash_gate` luôn trả `permissionDecision: "allow"` kèm `additionalContext` (theo doc hook Claude Code). Không còn thao tác nào bị từ chối vì trạng thái workflow.
3. **Xoá hẳn lớp gate duyệt.** `hooks/scripts/approve_gate.py` và mục `UserPromptExpansion` bị bỏ; `/tdq-workflow:tdq-approve` còn lại như phím tắt, ý nghĩa y hệt câu nói.
4. **stop_gate còn đúng một lý do block**: repo đổi mà `docs/workinglog/<ngày>.md` chưa cập nhật. Toàn bộ phần kiểm "dòng mời duyệt" (từng chặn nhầm turn hợp lệ vì transcript trễ) đã bỏ.
5. **State schema 3**: thêm `spec/plan/quick_approved_by` (cắt 200 ký tự), bỏ `PROTECTED_KEYS`, `load()` bù khoá cho state cũ nên không cần migrate tay.
6. **Skills + README** đổi sang lời mời tự nhiên `➤ Duyệt: nhắn "duyệt plan mode main" …`; `tdq-conventions` có mục mới **Ghi nhận duyệt** (dấu hiệu duyệt, bắt buộc `--by`, mơ hồ thì HỎI, không tự duyệt thay user).

## Kết quả kiểm

- 65 test PASS (0.1.8 có 83 test; 18 test của `approve_gate` và nhánh invite bị xoá cùng code, các test deny còn lại đổi sang assert `allow` + `additionalContext`).
- `grep '"deny"' hooks/ scripts/` sạch · `validate --strict` PASS · plugin user-level lên **0.2.0**.
- 4 mục smoke trên bản cài đều đạt (chi tiết trong QC §3).

## Điều gì KHÔNG còn được bảo vệ (đánh đổi user đã chọn)

- Không còn bảo chứng kỹ thuật "chỉ user mới duyệt được": state duyệt nay do Claude ghi. Thay thế bằng dấu vết — `*_approved_by` lưu nguyên văn câu user (đối chiếu được với transcript) + entry working log mỗi lần duyệt + quy tắc "mơ hồ thì hỏi".
- Không còn chặn Claude sửa code trước khi duyệt, ghi tay `state.json`, hay commit khi user chưa yêu cầu — tất cả chỉ còn là lời nhắc.
- Nếu về sau Claude trôi khỏi lời nhắc, bước siết tiếp theo là `permissionDecision: "ask"` (hỏi user tại chỗ), **không** quay lại `deny`.

## Cần lưu ý

Session đang chạy phải **restart** mới nạp hook 0.2.0; session cũ vẫn chạy gate cứng 0.1.8.
