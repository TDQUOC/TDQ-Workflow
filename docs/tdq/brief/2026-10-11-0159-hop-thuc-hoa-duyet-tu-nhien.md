# BRIEF — Hợp thức hóa câu duyệt tự nhiên (làm đi, tiến hành)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

User:
"Okay tôi muốn check là có ghi nhận tình trạng là khi duyệt plan spec thì người dùng có thể tiếp tục theo kiểu là okay làm đi để by pass bước duyệt hãy check xem nguyên nhân tại sao và cho tôi đề xuất khắc phục"
"Hướng A"
"1a nhưng đảm bảo là nếu ngoài cổng chờ có câu hỏi cần confirm thì sẽ ko work kiểu câu hành động mà cần trả lời câu hỏi xong r mới confirm"

**Mục tiêu:**
Hợp thức hóa các câu lệnh hành động dứt khoát tự nhiên ("làm đi", "tiến hành đi", "triển đi", "go ahead"...) thành câu duyệt hợp lệ khi đang có đúng một cổng chờ duyệt (`spec`, `plan`, hoặc `quick`).
Đồng thời đảm bảo: nếu ngoài cổng duyệt còn có câu hỏi cần trả lời hoặc confirm (chọn mode, câu hỏi phỏng vấn/làm rõ, câu hỏi có phương án), câu hành động trần sẽ KHÔNG được duyệt mà phải trả lời câu hỏi trước.

**Phạm vi:**
- Trong:
  1. `hooks/scripts/prompt_context.py`: Thêm nhận diện câu hành động dứt khoát cho `spec`, `plan`, `quick`. Chặn câu hành động khi có câu hỏi confirm hoặc tại cổng `mode`.
  2. `skills/tdq-conventions/references/approval.md`: Cập nhật quy tắc duyệt tự nhiên theo ngữ cảnh và ngoại lệ khi có câu hỏi cần confirm.
  3. `tests/test_prompt_context.py`: Bổ sung unit tests cho câu hành động dứt khoát (match khi chỉ có gate, reject khi có question/mode/confirm).
- Ngoài: Chuyển sang hard-gate block sửa code trong `edit_gate.py` (user đã chốt chọn Hướng A soft/tự nhiên).

## Hiểu & kiến thức
- Hiện trạng: `looks_like_approval()` bắt buộc từ đồng thuận phải đi kèm `OBJECT` (`spec`, `plan`, `quick`) hoặc `PRONOUN` (`cái này`, `cái đó`, `this`). Câu trần như "làm đi", "triển đi" bị coi là không hợp lệ.
- Yêu cầu mới:
  1. Khi đang chờ cổng duyệt (`target in ("spec", "plan", "quick")`), các câu lệnh hành động dứt khoát độc lập (`ACTION_APPROVAL`: "làm đi", "tiến hành đi", "triển đi", "go ahead", "tiến hành", "làm luôn", "chạy đi") được coi là duyệt hợp lệ.
  2. Tuyệt đối KHÔNG áp dụng cho cổng `mode`: tại cổng `mode`, người dùng phải chọn phương thức cụ thể (`main` hoặc `subagent`), câu hành động không chỉ ra được mode nên phải hỏi lại.
  3. Nếu câu nói chứa nghi vấn, phủ định, hoặc điều kiện/confirm (`nhưng`, `confirm`, `xác nhận`, `?`, `nếu`...) $\rightarrow$ `QUESTION` regex chặn lại, không duyệt.
  4. Nếu có câu hỏi cần confirm/lựa chọn khác, câu hành động trần không được phép bypass mà phải yêu cầu trả lời trước.

## Hỏi đáp
- Pipeline: User đã chọn 1a (chế độ nhanh / express).
