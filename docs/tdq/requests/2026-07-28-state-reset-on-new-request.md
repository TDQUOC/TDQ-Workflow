# Request: chọn lane cho yêu cầu mới phải reset/đồng bộ lại state

**Ngày:** 2026-07-28 · **Lane:** full

## Nguyên văn
> hiện tại khi chọn quick dù claude trình bày nhưng ko xử lí lại state khiến cho conflict như ảnh, tôi muốn là khi chọn quick hãy full cho yêu cầu thì sẽ mặc định update lại state (bao gồm request, lan, phase, specfile,...)

Ảnh kèm: session `insightfaceserverv2`, state đang là request `2026-07-28-kiosk-pose-guidance` (lane full, phase implement, plan_approved true); Claude trình mini-plan lane quick cho một yêu cầu MỚI (hologram label) nhưng không init lại state → user gõ `/tdq-workflow:tdq-approve quick` → gate chặn "Sai lane: request đang ở lane full".

## Bằng chứng (transcript thật)
`~/.claude/projects/-Users-truongdinhquoc-Documents-insightfaceserverv2/8294af46-….jsonl`
- idx 2206 (10:48:28Z): assistant in mini-plan lane quick, kết thúc bằng dòng `➤ Để duyệt: gõ \`/tdq-workflow:tdq-approve quick\` · Góp ý: nhắn trực tiếp`.
- idx 2207 (cùng giây): Stop hook chỉ chặn vì **working log**, KHÔNG chặn dòng mời duyệt sai lane.
- idx 2221 (10:49:21Z): approve_gate chặn "Sai lane".
- Replay chính chuỗi đó vào `stop_gate.py` bản 0.1.5 (state lane=full) → **block đúng**. Vậy script không sai; tại thời điểm hook chạy, message cuối **chưa được ghi vào transcript** nên `last_assistant_text()` đọc trượt (đọc phải message trước đó).

## Nguyên nhân
1. **Không có bước đồng bộ state khi mở yêu cầu mới.** `tdq-start` bảo "init bắt buộc", nhưng chỉ là chỉ thị skill; khi đang có request khác mở dở, Claude trình plan thẳng mà không init → state lệch với việc đang làm.
2. **Lưới an toàn (stop_gate) đọc transcript chỉ 1 message cuối** → trễ/trượt khi transcript chưa flush; lỗi lọt tới tay user.
3. Message chặn của approve_gate khi sai lane chưa đưa lệnh sửa cụ thể (slug + lane) để user/Claude xử lý ngay.

## Mong muốn của user
Chọn lane (quick hoặc full) cho một yêu cầu mới ⇒ **mặc định cập nhật lại toàn bộ state**: `active_request`, `lane`, `phase`, `spec_file`, `plan_file`, các field duyệt, `implement_mode`.

## Ràng buộc
- Không được nới lỏng gate duyệt: mọi field duyệt vẫn chỉ do lệnh user set qua approve_gate.
- Không tự ý xoá tiến độ của request đang mở còn dở dang — phải hỏi user trước khi ghi đè.
