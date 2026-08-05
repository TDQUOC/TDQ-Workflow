# Nhánh external (Phần A, mode external)

Nạp file này khi `implement_mode=external`. Không nạp cho mode `main`/`subagent`.

Bạn là ORCHESTRATOR: soạn gói, gọi runner, verify, tick, merge. Engine ngoài chỉ code.
Lane full giao CẢ PLAN một lần (chia gói phase khi plan lớn); quick lane vẫn dùng
`run` một task. Gói task đơn quick CŨNG chép skill vào cuối gói bằng `skill-dump`
và cũng sinh AGENTS.md (task quick dùng skill cần MCP: tdq-intake đã chặn external
từ lúc duyệt). Lệnh trigger engine LUÔN do subagent runner chạy — main không tự
chạy `external_task.py run-plan`.

- **Chuẩn bị.** Đọc engine + model bằng
  `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/external_task.py" parse-plan <plan>` (exit 1
  → plan thiếu dòng máy-đọc, quay lại tdq-plan). Lane full dùng model mức `khó` cho mọi
  gói. Tạo worktree dùng chung: `git worktree add ../tdq-ext-<slug> -b tdq-ext-<slug>`;
  ghi lại commit gốc `base=$(git rev-parse HEAD)` để kiểm về sau. Sinh `AGENTS.md` ở
  ROOT worktree — chép nguyên văn khối fence trong
  [agents-md.md](agents-md.md); codex/agy tự nạp.
- **Chia gói.** LUÔN chạy `external_task.py split-plan <plan>` — kể cả plan ≤6 task —
  vì script tách task `(mcp)` thành gói `"mcp": true` riêng và trả danh sách `skills`
  mỗi gói. Gói `"mcp": true` KHÔNG giao engine: bạn TỰ làm các task đó trong worktree
  (red→green như mode main), đúng vị trí. Gói thường ≤6 task theo ranh giới phase;
  mỗi gói = 1 lần gọi runner trong 1 turn, gói sau CHỈ giao khi gói trước qua verify.
- **Vòng lặp mỗi gói (gói thường):**
  1. Soạn gói theo khuôn GÓI PLAN của [external-task.md](external-task.md)
     vào `docs/tdq/external/<slug>/plan-round-<n>.task.md`. Gói gồm: mọi task (mục tiêu,
     file, 1 lệnh test/task), ràng buộc, report mẫu `kind="plan"`. Mục BẮT BUỘC
     "tự verify": engine chạy lệnh test từng task, ghi `test_result` thật — đây là
     verify tầng 1; script tự retry khi test_result rỗng. CUỐI gói: chạy
     `external_task.py skill-dump <các skill trong "skills" của gói>` và dán nguyên
     văn output vào sau mục Report mẫu (mục `## SKILL …` — xem khuôn).
  2. Gọi agent `codex-runner` hoặc `agy-runner` — **ĐỒNG BỘ** (`run_in_background: false`)
     để turn build đứng chờ và TỰ tiếp tục khi runner xong (notification không sống qua
     restart phiên). Agent bên trong chạy `external_task.py run-plan …` bằng Bash nền +
     poll — timeout gói = 540s × số task (trần 3600s), tối đa 2 attempt → một lần gọi
     runner có thể tới 2×3600s. Bảo runner thêm `--plan-file <plan>` vào lệnh
     `run-plan` — script đối chiếu gói với khối `Dùng:` của plan; thiếu skill chỉ
     CẢNH BÁO + ghi `run.log`, vẫn chạy engine.
  3. **Verify PHASE (tầng 2)** — không tin report suông: tự chạy lại lệnh test của TỪNG
     task trong gói tại worktree + đối chiếu `files_changed`. Task pass → tick `- [x]`
     vào plan NGAY; task fail/thiếu → ghi vào danh sách chờ fix.
- **Verify TỔNG (tầng 3, sau gói cuối):** chạy toàn bộ test suite trong worktree +
  diff-check + `status --porcelain`. Tất cả pass → đóng worktree.
- **Fix loop (≤2 vòng, đếm bằng `fix-rounds.json`):** còn task fail sau verify →
  soạn gói MINI-PLAN FIX theo khuôn GÓI FIX, kèm "task đã PASS — không làm lại" và
  "file cấm sửa". Ghi sổ: `external_task.py fix-rounds add --slug <slug> --tasks <ids>
  --result fail`. Giao lại runner qua `run-plan --round <n+1>`, verify lại như tầng 2/3.
  `fix-rounds status` trả `fallback` (đã đủ 2 vòng) hoặc runner hỏng (exit 1) →
  FALLBACK: bạn TỰ implement các task còn lại trong worktree (red→green như mode main)
  VÀ tự viết report `docs/tdq/external/<slug>/<task-id>.json` đúng schema kèm
  `"fallback": "claude"`. Verify 3 tầng tóm gọn: engine tự verify → Claude verify
  phase → Claude verify tổng.
- **Đóng worktree** (sau task cuối):
  1. Xóa `AGENTS.md` (và mọi file skill chép tạm) khỏi worktree TRƯỚC khi diff-check —
     file phục vụ engine, không được lọt vào diff.
  2. Gộp phần kiểm còn lại vào 1 lượt bằng `&&`: engine không commit lạ (`log --oneline`
     phải RỖNG, engine bị cấm commit), diff-check (khớp hợp nhất `files_changed` của các
     report, file lạ → điều tra trước khi merge). Thêm status để thấy cả file
     MỚI/untracked mà `diff --stat` bỏ sót:
     `rm -f ../tdq-ext-<slug>/AGENTS.md && git -C ../tdq-ext-<slug> log --oneline <base>..HEAD && git -C ../tdq-ext-<slug> diff --stat && git -C ../tdq-ext-<slug> status --porcelain`
  3. Merge về branch chính, xử lý conflict, chạy toàn suite, rồi
     `git worktree remove ../tdq-ext-<slug>`.
- Log từng lần gọi engine nằm ở `docs/tdq/external/<slug>/run.log` (service tự bật,
  `TDQ_EXTERNAL_LOG=0` tắt) — dán vào QC khi cần bằng chứng.
