---
name: tdq-status
description: Báo trạng thái TDQ hiện tại (request, lane, phase, mode thực thi, ai đã duyệt gì) và bước kế tiếp chính xác. Dùng khi user hỏi workflow đang ở đâu.
---

# TDQ Status

Đọc state, báo bằng **tiếng Việt**, ≤ 10 dòng. Chỉ đọc, không ghi gì vào state.

## Các bước

1. Chạy hai lệnh:
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" next
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" get
   ```
   Chưa có `active_request` → báo "Chưa có request TDQ nào đang chạy." kèm bước mở
   request mới, rồi dừng.

2. Báo các mục sau (một dòng mỗi mục):
   - Request + lane + phase hiện tại.
   - `implement_mode`: mode user đã chốt (chưa có thì ghi "chưa chốt").
   - Spec: ✔ đã duyệt (kèm `spec_approved_at` và `spec_approved_by`) / ⏳ chờ duyệt / — chưa có.
     Tương tự cho plan (`plan_approved_by`) hoặc quick (`quick_approved_by`) tuỳ lane.
   - Spec đã duyệt → so sha256 hiện tại của `spec_file` với `spec_sha256`; lệch thì cảnh
     báo "spec đã đổi sau khi duyệt, cần duyệt lại".
   - Phase `implement`/`qc` → đếm `- [x]` trên tổng số task trong plan file → tiến độ.

3. Kết bằng bước kế tiếp, lấy nguyên văn dòng "Việc tiếp theo" và "Lệnh" từ output `next`.
   Đang chờ duyệt thì in kèm: `➤ Duyệt: nhắn "duyệt <spec|plan|quick>" · Góp ý: nhắn trực tiếp`.

Xong khi: user đọc xong biết đang ở đâu và việc kế tiếp là gì.
Bước kế tiếp: skill tương ứng với phase đang ở — xem
[phases.md](../tdq-conventions/references/phases.md).
