# Request — 2026-08-03-skill-vao-goi-external

Nguyên văn: "okay hãy đi full cho khuyến nghị hybrid của bạn đi, nhưng hãy phân tích chắc chắn để đảm bảo hoạt động đúng kể cả ở model cấp thấp"

Cách hiểu đầu tiên:
- Mục tiêu: hiện thực hóa khuyến nghị hybrid từ request `2026-08-03-check-skill-clone-worktree`: đưa skill mà plan/spec khai báo (khối `Dùng:`) tới engine ngoài trong mode external theo 3 nhánh — (1) quy ước xuyên task → AGENTS.md root worktree (codex tự nạp; agy auto-parse) (+ cân nhắc `.agents/skills/` cho agy); (2) hướng dẫn 1 task → nhúng trích đoạn vào gói; (3) skill MCP tool → loại task khỏi gói, Claude tự làm.
- Ràng buộc đặc biệt user nêu: phải hoạt động đúng KỂ CẢ với model cấp thấp — nghĩa là trích đoạn/AGENTS.md phải ngắn, mệnh lệnh, không dựa vào suy luận; luật phân nhánh phải máy-kiểm được, không cảm tính.
- Phạm vi đoán: sửa skills/tdq-build (nhánh external + khuôn gói), có thể external_task.py (dọn/loại task MCP), doc_lint/test, portable sync.
- Chỗ chưa rõ: nguồn trích đoạn (ai chắt lọc), cách nhận diện skill MCP bằng máy, dọn AGENTS.md trước merge — sẽ interview.

Lane: full (user chốt ngay trong prompt).
