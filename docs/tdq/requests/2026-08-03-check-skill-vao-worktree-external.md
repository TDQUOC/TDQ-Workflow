# Request — 2026-08-03-check-skill-vao-worktree-external

Nguyên văn: "okay bây giờ ở mode external tôi muốn check giúp tôi là ví dụ trong plan, spec đã có biết sẽ dùng skill đó cho task đó thì đã có phương thức move skills đó vô worktree để external có skill để dùng chưua?"

Cách hiểu đầu tiên:
- Mục tiêu: kiểm tra và báo cáo — khi plan/spec đã khai báo task dùng skill (khối `Dùng:`/bảng §3b), luồng external hiện tại có cơ chế nào đưa skill đó vào worktree `tdq-ext-<slug>` để engine ngoài (codex/agy) đọc và dùng được không.
- Phạm vi đoán: đọc skills/tdq-build (nhánh external), khuôn gói external-task.md, scripts/external_task.py, cấu trúc worktree — thuần check, chưa sửa gì.
- Chỗ chưa rõ: không — câu hỏi check/report.
