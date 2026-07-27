---
name: tdq-report
description: Write the final Vietnamese report (max 50 lines) for a completed TDQ request, close out state, and ask the user about committing.
---

# TDQ Report

Read [tdq-conventions](../tdq-conventions/SKILL.md). Runs after QC passes, phase `report`.

## Steps

1. **Write** `docs/tdq/reports/<slug>.md` — VIETNAMESE, **≤ 50 dòng tổng cộng**:
   - Kết quả: đã build gì, output ở đâu (đường dẫn)
   - Cách chạy/test: lệnh cụ thể
   - Kết quả QC: tóm tắt PASS + link `docs/tdq/qc/<slug>.md`
   - Quyết định đáng chú ý & giới hạn còn lại (nếu có)
   - Việc đề xuất tiếp theo (nếu có)
   Đo bằng `wc -l` — nếu > 50 dòng, cắt gọn đến khi đạt.

2. **Close out:** tick nốt checkbox plan còn lại (nếu QC round nào chưa tick), đổi trạng thái header plan → HOÀN THÀNH, append working log entry (END of file), graphify update nếu có.

3. **Present** the report content in chat (VI, nguyên văn hoặc tóm tắt ≤ 10 dòng + đường dẫn).

4. **Ask about commit** (mandatory, do NOT commit on your own): hỏi user có muốn commit không. If yes: commit message VI/EN mô tả thay đổi, KHÔNG chứa "generated with …"/AI trailers; branch name rules apply. Then `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=idle` (or `reset` if the user wants a clean slate for the next request).
