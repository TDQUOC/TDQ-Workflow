# Knowledge — 2026-08-03-check-external-assign-flow

## Năng lực dùng được
| Skill | Phán quyết | Lý do |
|---|---|---|
| tdq-build / tdq-plan / tdq-conventions | DÙNG (đọc) | Nguồn sự thật về flow external |
| graphify | KHÔNG | Câu hỏi cụ thể, đọc trực tiếp file nhanh hơn |
| tavily / research | KHÔNG | Thuần nội bộ, không có ẩn số bên ngoài |

## Phát hiện (nguồn: skills/tdq-build/SKILL.md dòng 53–87, 98–101)
1. **Giao TỪNG task, không giao cả plan 1 lần.** Vòng lặp mỗi task: phân độ khó → chọn model → soạn gói task riêng (`docs/tdq/external/<slug>/<task-id>.task.md`) → gọi runner (codex-runner/agy-runner) đồng bộ. Nhiều task độc lập có thể chạy song song, nhưng vẫn là mỗi lần gọi = 1 task.
2. **Verify theo TỪNG task ngay sau khi runner xong** (chạy lại lệnh test của task trong worktree), không phải chờ xong hết mới check tổng.
3. **Task fail → Claude TỰ implement (fallback), KHÔNG giao lại cho external.** Runner `engine-failed` hoặc verify fail → Claude tự làm task đó red→green trong worktree.
4. **Check tổng thể tồn tại nhưng nằm ở bước đóng worktree + QC**: kiểm engine không commit lạ, diff-check khớp `files_changed`, merge, chạy toàn suite; sau đó phase QC chạy đủ DoD. QC FAIL → thêm task fix vào plan (`## QC vòng N — fix`) — gần với ý "mini plan fix", nhưng task fix đi theo luật Phần A, và không có luật buộc giao lại cho external.

## Kết luận
Mô tả của user KHÔNG khớp thiết kế hiện tại ở 2 điểm: (a) giao từng task chứ không phải cả plan 1 lần; (b) fix khi sai do Claude tự làm (fallback), không "mini plan fix cho external fix". Điểm khớp một phần: có verify per-task + diff-check tổng + QC loop thêm task fix.

## Quyết định đã chốt (user, vòng interview 2026-08-03)
- **Đổi thiết kế** mode external lane full: giao TOÀN BỘ plan cho engine trong 1 lần gọi → Claude verify tổng thể → sai thì viết mini-plan fix giao lại external → lặp tối đa **2 vòng fix** → vẫn sai thì Claude tự làm phần còn lại (fallback).
- Model: dùng slug **`khó`** trong plan cho cả lần gọi (map TB/dễ không còn dùng ở lane full).
- Timeout: **540s × số task, trần 3600s**, vẫn override được qua `TDQ_EXTERNAL_TIMEOUT`.
- **Giữ nguyên**: quick lane external (1 gói 1 lần gọi như cũ), các bước an toàn đóng worktree (cấm engine commit, diff-check khớp files_changed + status --porcelain, chạy toàn suite trước merge), retry 3 attempt trong script, log service run.log, fallback khi engine hỏng.

## Bổ sung (user, 12:39): trigger qua subagent
- Lệnh trigger engine (external_task.py run …) KHÔNG do main conversation tự chạy — main giao cho **subagent runner** (codex-runner/agy-runner) chạy, để user dễ thấy tiến trình và dễ quản lý. Kiến trúc runner hiện tại giữ nguyên vai trò này; thiết kế mới chỉ đổi payload từ 1 task → 1 gói plan (và gói mini-plan fix ở các vòng fix).

## Phạm vi đụng tới (ước lượng)
- `scripts/external_task.py`: thêm chế độ giao cả plan (gói plan-packet, timeout scale, report tổng hoặc report per-task gộp).
- `skills/tdq-build/SKILL.md` mục "Nhánh external": viết lại vòng lặp → giao 1 lần + verify tổng + fix loop ≤2.
- `skills/tdq-plan/SKILL.md` mục "Chốt engine + model": còn 1 model (khó) cho lane full.
- `agents/` codex-runner, agy-runner: prompt/contract nhận gói plan.
- Schema report + tests liên quan.

## Kiểm cổng
- Phạm vi rõ: đổi flow giao việc external lane full như trên; output = code + skill + test cập nhật.
- Không cần model/download/cài đặt mới.
- QC: test suite hiện có + test mới cho chế độ plan-1-lần (parse, timeout, fix loop), E2E giả lập engine.

## Nguồn
- skills/tdq-build/SKILL.md (Nhánh external, Phần B QC)
- CLAUDE.md mục 9 ("giao TỪNG task cho engine ngoài")
