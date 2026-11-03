# REPORT — 0.1.7: yêu cầu mới ⇒ state được đồng bộ lại

Ngày: 2026-07-28 · Lane full · Mode thực thi: main (user chọn khi duyệt plan) · QC: [PASS](../qc/2026-07-28-state-reset-on-new-request.md)

## Vấn đề
Chọn lane cho một yêu cầu MỚI nhưng state vẫn giữ request cũ → dòng mời duyệt và lệnh duyệt của user lệch nhau ("Sai lane"). Lưới an toàn Stop hook không bắt được vì chỉ đọc **1 message cuối** của transcript, mà message đó chưa kịp flush khi hook chạy.

## Đã làm
1. `scripts/tdq_state.py`: `init` = mở request mới, reset toàn bộ; cảnh báo `⚠️ Ghi đè …` ra stderr khi request cũ còn dở; thêm `previous_request`; `schema_version` 2 + `load()` bù khoá cho state cũ.
2. `hooks/scripts/stop_gate.py`: `turn_assistant_texts()` quét **cả lượt** (lùi tới prompt user thật, bỏ qua tool_result và Stop-hook feedback, tối đa 8 message) → miễn nhiễm transcript trễ; message chặn nêu rõ lệnh `init` và ý nghĩa reset.
3. `hooks/scripts/prompt_context.py`: mỗi prompt khi có request mở → 1 dòng "Request đang mở: … · lane · phase" + yêu cầu init lại nếu là yêu cầu mới.
4. `hooks/scripts/approve_gate.py`: message "Sai lane" (cả 2 nhánh) nêu tên request đang mở + lệnh `init <slug-mới> <lane>`.
5. `skills/tdq-start`, `skills/tdq-conventions`: init bắt buộc cho mọi yêu cầu mới ngay khi user chọn lane; request cũ còn dở → hỏi user trước khi đè; phân biệt `init` vs `reset`.
6. Test: +10 case (state 5, stop_gate 2, prompt_context 2, approve_gate 1); suite 67 → 77, all PASS. Bump 0.1.7, validate --strict PASS, cài user-level 0.1.7.

## Còn lại
- **Cần restart Claude Code** để session hiện tại dùng 0.1.7.
- Chưa commit (chờ user yêu cầu).
