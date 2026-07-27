---
name: tdq-status
description: Show current TDQ workflow status (request, lane, phase, pending approvals) and the exact next step. Use when the user asks where the workflow stands.
---

# TDQ Status

Read state, report in VIETNAMESE, ≤ 10 dòng.

1. Run: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" get`
   - No state / no `active_request` → "Chưa có request TDQ nào đang chạy. Dùng tdq-start để bắt đầu." and stop.

2. Report:
   - Request + lane + phase hiện tại.
   - Spec: ✔ đã duyệt (kèm thời điểm) / ⏳ chờ duyệt / — chưa có. Tương tự cho plan (lane full) hoặc quick approval (lane quick).
   - Nếu spec đã duyệt: so sánh sha256 hiện tại của `spec_file` với `spec_sha256` — lệch thì cảnh báo "spec đã đổi sau khi duyệt, cần duyệt lại".
   - Nếu phase implement/qc: đếm `- [x]` / tổng `- [ ]`+`- [x]` trong plan file → tiến độ.

3. End with the exact next action, e.g.:
   - Chờ duyệt → in đúng dòng `➤ Để duyệt: gõ /tdq-workflow:tdq-approve <spec|plan|quick> · Góp ý: nhắn trực tiếp`
   - Đang implement → "Tiếp tục tdq-implement: còn N task."
   - Phase report xong → "Workflow đã hoàn tất; bắt đầu request mới bằng tdq-start."
