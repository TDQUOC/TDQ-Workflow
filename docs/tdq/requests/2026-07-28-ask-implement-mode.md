# Request: Claude tự quyết implement mode, không hỏi user

**Ngày:** 2026-07-28
**Nguồn:** user báo sau khi restart đầy đủ (đã chạy plugin 0.1.4)

## Nguyên văn
> hiện tại sau khi restart đầy đủ thì tôi thấy vẫn không hỏi phương thức implement mà tự set main vào state luôn, tôi cần bạn detect và xác định nguyên nhân để lên chiến lược fix

## Bằng chứng thu được
Project `insightfaceserverv2`, request `2026-07-28-responsive-mobile-tablet` (lane full):
- `docs/tdq/state.json`: `plan_approved: true` @ 13:29:17, `implement_mode: "main"`, `phase: implement`.
- `docs/tdq/plan/2026-07-28-responsive-mobile-tablet.md:17-18` chứa `**Mode thực thi: main**` + lý do — **do Claude tự viết**, nằm giữa thân plan.
- Gate `approve_gate.py:91-97` hoạt động đúng thiết kế 0.1.3: regex đọc mode từ file plan đã duyệt → ghi vào state.

## Nguyên nhân (không phải bug code, là lỗ hổng thiết kế 0.1.3)
1. `skills/tdq-plan/SKILL.md` bước 1 & 4 chỉ yêu cầu plan **có** dòng mode + "đề xuất" trong summary; không có bước nào bắt Claude HỎI user chọn mode.
2. `approve_gate.py` không phân biệt được mode do user chọn hay Claude tự chọn — chỉ kiểm tra dòng tồn tại.
3. `approve_gate.py:107-109` in `"do NOT ask again"` → củng cố hành vi không hỏi.
4. Lane quick không có khái niệm mode; `implement_mode` không thuộc `PROTECTED_KEYS` (`scripts/tdq_state.py:18-22`) nên vẫn set được tự do.

0.1.3 chặn được "set mode lén qua state" nhưng chưa chặn "tự quyết mode rồi nhét vào plan".

## Hướng fix đề xuất
- **A** — `tdq-plan` bắt buộc hỏi tường minh (2 lựa chọn main/subagent + đề xuất) TRƯỚC khi ghi dòng mode vào plan.
- **B** — Mode nằm trong chính lệnh duyệt: `/tdq-workflow:tdq-approve plan main|subagent`; gate lấy mode từ command args (chữ user gõ), plan chỉ ghi đề xuất.
- **C** — A + B.

## Unknowns cần user chốt
- Chọn hướng A/B/C.
- Lane xử lý: quick hay full.
