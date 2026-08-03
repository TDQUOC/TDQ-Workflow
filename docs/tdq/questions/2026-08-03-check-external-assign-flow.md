# Questions — 2026-08-03-check-external-assign-flow

## Vòng 1
1. Chỉ báo cáo hiện trạng hay đổi thiết kế?
   - Đáp: **Đổi thiết kế** theo mô tả: giao cả plan 1 lần → Claude verify tổng → mini-plan fix giao lại external.

## Vòng 2 (chốt thiết kế)
1. Model cho cả lần gọi plan? → **Theo task khó nhất** (slug `khó` trong plan).
2. Số vòng mini-plan fix giao external trước khi Claude fallback? → **2 vòng**.
3. Timeout khi giao cả plan? → **Scale theo số task**: 540s × số task, có trần 3600s, chỉnh qua env.
4. Quick lane external + các bước an toàn đóng worktree (diff-check, cấm engine commit, toàn suite trước merge)? → **Giữ nguyên cả hai**, chỉ đổi cách giao việc lane full.
