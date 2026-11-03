# Bundle portable Antigravity
@nhánh: Cổng TDQ > Bundle portable Antigravity

B1 · Chạy target sinh bundle từ nguồn skills/hooks/agents/scripts (?)
B2 · Sinh cây antigravity_portable/: skill, hook, config (hook/permissions/mcp), README, manifest (?)
B3 · Người dùng copy nguyên nội dung vào mọi path ứng viên global của agy đã biết (?)
B4 · Agy khởi động, tự nạp skill/hook/permissions/MCP theo path nó đọc được trên máy đó (?)
B5 · Người dùng tự-kiểm bằng /skills, /mcp, /permissions xem đã nạp đúng chưa (?)
B5! · không thấy nạp ở path đang dùng thì đối chiếu path ứng viên khác đã cài kèm trong bundle (?)
B6 · Agy sắp chạy một tool call, gọi hook PreToolUse (?)
B7 · Hook đọc JSON stdin, khớp lệnh với 2 case cấm: tên branch/commit sai luật, ghi thẳng state.json qua shell (?)
B7! · khớp 1 trong 2 case cấm thì trả decision deny kèm lý do, chặn cứng ngay lúc gõ lệnh (?)
B8 · Không khớp case cấm, hoặc input parse lỗi, thì trả decision allow — không chặn lệnh hợp lệ, không crash khi agy đổi schema (?)
B9 · Agy định kết thúc lượt, gọi hook Stop (?)
B10 · Hook đọc state request đang mở và hiệu ứng thật trên đĩa (turn ledger + git status), port y hệt 3 điều kiện của stop_gate.py: TDQ:LOG, TDQ:TICK, TDQ:UNFINISHED (?)
B10! · một trong 3 điều kiện chưa qua thì trả decision continue, ép loop không dừng sớm; đủ MAX_STREAK lần không tiến triển thì hạ xuống nhắc, thôi chặn (?)
B11 · Cả 3 điều kiện đã qua thì không chặn, agy được kết lượt bình thường (?)
