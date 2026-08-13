---
name: tdq-spec
description: Viết spec tiếng Việt cho request TDQ, đăng ký vào state, trình rồi DỪNG chờ duyệt; duyệt xong viết plan cùng turn. Dùng khi chế độ chuyên sâu xong analyze.
---

# TDQ Spec

Nạp [tdq-conventions](../tdq-conventions/SKILL.md). Spec viết **tiếng Việt**.

## Các bước

1. **Viết** `docs/tdq/spec/<slug>.md` từ `docs/tdq/brief/<slug>.md`.
   Khuôn đầy đủ: [references/spec-template.md](references/spec-template.md).
   Mục bắt buộc: mục tiêu & phạm vi (in/out) · **Lộ trình** (chép từ brief: phase
   nào chạy, phase nào bỏ, skill nào dùng, vì sao — user duyệt spec là duyệt luôn
   lộ trình) · đầu ra đo đếm được · cách tiếp cận + lý do ·
   năng lực & công cụ (§3b — chép bảng phán quyết từ brief, máy kiểm bằng doc_lint R8) ·
   yêu cầu bắt buộc (log service bật mặc định, không placeholder, test cho từng phần) ·
   ràng buộc & rủi ro · phạm vi QC + Definition of Done · câu hỏi còn mở.
   Mục "câu hỏi còn mở" PHẢI rỗng — còn câu hỏi thì quay lại phase `analyze`.

2. **Tự review.** Đọc lại tìm chỗ hổng/mâu thuẫn, sửa. Chạy máy kiểm
   (R8 kiểm §3b): `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/doc_lint.py" docs/tdq/spec/<slug>.md`
   đến khi exit 0.
   Cần review sâu hơn thì user yêu cầu — khi đó mới gọi agent `tdq-reviewer` (tùy chọn).

3. **Đăng ký file vào state:**
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set spec_file=docs/tdq/spec/<slug>.md
   ```

4. **Trình bày & DỪNG.** Trong chat: tóm tắt spec ≤ 50 dòng (mục tiêu, đầu ra, DoD,
   rủi ro chính). Tự kiểm trước khi in dòng Duyệt: tin nhắn phải CHỨA tóm tắt thật —
   không được thay bằng câu thông báo suông kiểu "đã ghi log, đang chờ duyệt"; thiếu
   thì viết bổ sung ngay. Đầu ra của spec là chính một khuôn/mẫu văn bản (vd khuôn câu
   hỏi A/B) → cần trích nguyên khối đó làm ví dụ thì gắn nhãn rõ ngay trước đoạn trích.
   Nhãn dạng "(khuôn mẫu — áp dụng cho các lần hỏi sau, không phải câu hỏi của turn
   này)". Mục đích: đọc lại transcript không nhầm là đang hỏi lại. Ngay dưới tóm tắt in
   đúng dòng:
   ```
   ➤ Duyệt: nhắn "duyệt spec" (duyệt xong viết plan ngay) · Góp ý: nhắn trực tiếp
   ```
   Rồi **kết thúc turn**. Không viết plan, không sửa code. User góp ý thay vì duyệt →
   sửa spec, tăng số bản, trình lại, chờ tiếp.

5. **User duyệt → ghi nhận NGAY:**
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" approve spec --by "<nguyên văn câu user>"
   ```
   Mơ hồ thì HỎI — luật đầy đủ ở
   [approval.md](../tdq-conventions/references/approval.md).

Xong khi: `spec_approved = true` và `spec_file` trỏ đúng file đã trình.
Bước kế tiếp: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=plan`
rồi sang [tdq-plan](../tdq-plan/SKILL.md) **NGAY trong cùng turn** — không bắt user
nhắn thêm câu nào.
