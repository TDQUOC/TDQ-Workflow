# Request — 2026-08-03-check-skill-clone-worktree

Nguyên văn: "vậy hãy check xem nếu plan/spec có skill thì việc tạo một skill clone trong workftree mà external chạy thì có đảm bảo hơn việc external có skill để dùng ko?"

Cách hiểu đầu tiên:
- Mục tiêu: đánh giá phương án "clone skill vào worktree external" (copy SKILL.md/tài liệu skill mà plan/spec khai báo vào worktree `tdq-ext-<slug>`) — có đảm bảo engine ngoài dùng được skill hơn hiện trạng không, so với các phương án khác (nhúng trích đoạn vào gói, trỏ đường dẫn, loại task MCP khỏi gói).
- Phạm vi đoán: phân tích khả năng đọc/tuân theo của codex/agy với file trong worktree, giới hạn từng loại skill (CLI/hướng dẫn/MCP), chi phí context, rủi ro rác worktree khi merge — thuần phân tích + khuyến nghị, không sửa.
- Chỗ chưa rõ: không.
