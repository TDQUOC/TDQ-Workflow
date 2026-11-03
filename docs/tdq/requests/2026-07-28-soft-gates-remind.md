# Request: bỏ hard gate → nhắc nhở, duyệt bằng chat tự nhiên

**Ngày:** 2026-07-28 · **Lane:** full

## Nguyên văn
> van con loi, toi muốn bạn nới lỏng ra thành remind và nhắc nhở claude tuân theo. ko hard gate để hạn chế
> lỗi bất tiện. và tôi muốn khi duyệt sẽ duyệt chat bình thường, ví dụ duyệt spec, duyệt plan thực thi mode main,...

Ảnh kèm: user gõ `/tdq-workflow:tdq-approve quick` lần thứ hai → bị chặn "Quick plan đã được duyệt lúc
18:16:51 rồi" (lần đầu đã ghi nhận thành công); trước đó session dừng giữa chừng vì đọc nhầm state bóng.

## Lựa chọn của user (interview 18:32)
1. Lane: **full**.
2. Mức chặn: **giữ Stop hook remind (block 1 lần/turn để ép working log + tick plan), bỏ toàn bộ deny** ở PreToolUse.
3. Duyệt: **Claude tự ghi nhận** khi user nói duyệt trong chat — bỏ lớp hook duyệt.

## Vấn đề với thiết kế hiện tại (0.1.8)
- 3 lớp deny cứng (`edit_gate`, `bash_gate`, `approve_gate`) biến mọi sai lệch state thành **bế tắc**: user
  gõ đúng vẫn bị từ chối, Claude không được phép tự sửa, phải nhờ session khác gỡ.
- Duyệt phải gõ đúng slash command + đúng cú pháp mode → sai một chữ là mất lượt.
- Duyệt lần hai bị coi là lỗi (block) thay vì "đã duyệt rồi, đi tiếp".

## Căn cứ kỹ thuật
Tài liệu hook Claude Code (https://code.claude.com/docs/en/hooks): PreToolUse hỗ trợ
`hookSpecificOutput.permissionDecision: "allow"` **kèm** `additionalContext` → nhắc mà không chặn;
Stop hỗ trợ `{"decision":"block","reason":…}` (giữ) và cả `hookSpecificOutput.additionalContext` (nhắc mềm).

## Ràng buộc
- Vẫn phải có dấu vết ai duyệt cái gì lúc nào (state + working log), dù không còn gate.
- Không được để Claude tự suy diễn là đã duyệt khi user chưa nói rõ.
