# QUESTIONS — 2026-08-05-toi-uu-p0-p1-workflow

## Vòng 1 (2026-08-05 13:35)

### Q1 (P0-4) — hard-block hay soft-block task `(mcp)` khi mode external?
Trả lời: **A** — chốt hard-block, sửa `quick-lane.md` khớp `tdq-build/SKILL.md`.

### Q2 (P1-1) — rút gọn nạp cứng cho quick lane: cắt được `tdq-intake` rõ ràng,
`tdq-conventions` không có ranh giới quick/full rõ để tách an toàn. Làm tới đâu?
Trả lời: **A** — chỉ làm `tdq-intake/SKILL.md`, để `tdq-conventions` nguyên.

### Q3 (P1-2) — đồng bộ ngưỡng digest ≤1.500 ký tự lặp ở 8 file agent (không tự "nạp"
được lẫn nhau vì là system-prompt độc lập) + bug thật ở `lane-decision.md` (tự định
nghĩa khuôn câu hỏi riêng thay vì theo `interview.md`).
Trả lời: **A** — sửa bug `lane-decision.md` + thêm test canh khớp số 1.500 giữa 8 file.

### Q4 (P1-3) — sửa `stop_gate.py` scope theo turn thay vì toàn working tree: rủi ro
thật chỉ khi 2 phiên Claude Code cùng chạy trên 1 worktree chính. Sửa sâu (track file
theo turn) hay chỉ ghi chú rủi ro?
Trả lời: **A** — chỉ ghi chú rủi ro vào `reminder-codes.md`, không đổi code `stop_gate.py`.

### Q5 (P1-4) — thêm ví dụ cụ thể (đổi schema DB, xoá data, đổi API contract công khai)
vào nhóm "chặn cần dừng hỏi" của Luật cứng `tdq-build/SKILL.md`?
Trả lời: **A** — có, thêm 3 ví dụ.

### Q6 (P1-12) — đo carry-cost before/after theo kịch bản chuẩn hoá cần 2 session sạch,
không tự động hoá được trong 1 lần chạy script. Chỉ thiết kế kịch bản đo (để chạy sau)
hay bỏ hẳn khỏi spec round này?
Trả lời: **A** — chỉ thiết kế kịch bản đo round này, không tự chạy đo thật.

## Thông báo (không phải câu hỏi, chỉ cần xác nhận đã đọc)
P1-8 và P1-9 hoá ra **đã làm xong ở vòng 2** (audit ghi sai/lỗi thời) — sẽ loại khỏi
task list, chỉ đính chính trong report.
