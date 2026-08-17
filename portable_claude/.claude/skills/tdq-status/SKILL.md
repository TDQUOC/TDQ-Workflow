---
name: tdq-status
description: Báo trạng thái TDQ hiện tại (request, lane, phase, mode thực thi, ai đã duyệt gì) và bước kế tiếp chính xác. Dùng khi user hỏi workflow đang ở đâu.
---

# TDQ Status

Đọc state, báo bằng **tiếng Việt** (nhắc lại có chủ ý — bản gốc ở
`skills/tdq-conventions/SKILL.md`), ≤ 10 dòng. Chỉ đọc, không ghi gì vào state.

## Các bước

1. Chạy hai lệnh (gộp vào MỘT lần gọi Bash bằng `&&`):
   ```
   python3 "${CLAUDE_PROJECT_DIR}/.claude/tdq/scripts/tdq_state.py" next --brief
   python3 "${CLAUDE_PROJECT_DIR}/.claude/tdq/scripts/tdq_state.py" get
   ```
   Đang có request → chạy thêm `python3 "${CLAUDE_PROJECT_DIR}/.claude/tdq/scripts/tdq_timing.py" status`
   (gộp vào cùng lần gọi Bash) để lấy dòng đồng hồ: phase hiện tại đã chạy bao lâu và cả
   request tốn bao lâu. Lệnh này chỉ đọc, không ghi state.
   Luôn dùng `next --brief` (121 ký tự) — chỉ bỏ `--brief` (1.350 ký tự) khi thật sự
   cần checklist đầy đủ của phase, vì output đó bị mang vác lại ở mọi API call sau.
   Chưa có `active_request` → báo "Chưa có request TDQ nào đang chạy." kèm bước mở
   request mới, rồi dừng.

2. Báo các mục sau (một dòng mỗi mục):
   - Request + lane + phase hiện tại.
   - `implement_mode`: mode user đã chốt (chưa có thì ghi "chưa chốt").
   - Spec: **đã duyệt** (kèm `spec_approved_at` và `spec_approved_by`) / **chờ duyệt** / — chưa có.
     Tương tự cho plan (`plan_approved_by`) hoặc quick (`quick_approved_by`) tuỳ lane.
   - Spec đã duyệt → so sha256 hiện tại của `spec_file` với `spec_sha256`; lệch thì cảnh
     báo "spec đã đổi sau khi duyệt, cần duyệt lại".
   - Phase `implement`/`qc` → đếm `- [x]` trên tổng số task trong plan file → tiến độ.
   - Đồng hồ: in nguyên dòng `⏱ …` mà `tdq_timing.py status` trả về (phase hiện tại đã
     tốn bao lâu treo tường / model, và cả request tốn bao lâu).

3. Kết bằng bước kế tiếp, lấy nguyên văn dòng "Việc tiếp theo" và "Lệnh" từ output `next`.
   Đang chờ duyệt thì in kèm: `➤ Duyệt: nhắn "duyệt <spec|plan|quick>" · Góp ý: nhắn trực tiếp`.
   Cả phần trả lời user theo khuôn chung ở
   [user-facing-block.md](../tdq-conventions/references/user-facing-block.md) — nhãn
   trường in đậm, dòng `➤` nằm cuối.

Mất ngữ cảnh (session mới, đổi máy, agent khác vừa làm hộ một phase) hoặc state lệch đĩa
→ dừng ở đây, chuyển sang [tdq-check-status](../tdq-check-status/SKILL.md) để khôi phục.

Xong khi: user đọc xong biết đang ở đâu và việc kế tiếp là gì.
Bước kế tiếp: skill tương ứng với phase đang ở — xem
[phases.md](../tdq-conventions/references/phases.md).
