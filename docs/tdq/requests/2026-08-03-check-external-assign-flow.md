# Request 2026-08-03-check-external-assign-flow

## Nguyên văn
"tôi muốn bạn check và báo cáo lại cho tôi là ở mode implement external có đang hoạt động theo cách: asign toàn bộ plan cho external implement trong 1 lần gọi và khi external báo cáo xong thì claude sẽ check tổng thể lại đẻ make sure external làm đúng nếu sai ở đâu thì biết lại mini plan fix cho external fix"

## Cách hiểu đầu tiên
- Mục tiêu: đọc lại cơ chế mode external (tdq-build, external_task.py, runner agents) và báo cáo xem flow hiện tại là giao TOÀN BỘ plan 1 lần hay giao từng task; và Claude có bước verify tổng + mini-plan fix loop không.
- Phạm vi: chỉ đọc + báo cáo, không sửa code.
- Chưa rõ: không có — câu hỏi thuần kiểm tra.
