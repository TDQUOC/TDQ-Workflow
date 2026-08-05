# 04 — Build: Implement → QC → Report

Yêu cầu `plan_approved = true`. File này lo ba phase: `implement` → `qc` → `report`.

## Luật cứng (áp cho cả ba phase)

- **Vào build NGAY trong turn user duyệt plan, rồi chạy end-to-end trong MỘT turn.** Không
  bắt user nhắn thêm câu nào, không dừng giữa chừng hỏi "có tiếp không". Chỉ dừng khi đổi
  phạm vi thật sự, thiếu/mơ hồ `implement_mode`, hoặc gặp chặn chỉ user gỡ được.
- **Chặn kỹ thuật → tự chọn đề xuất, không hỏi.** Gặp chặn kỹ thuật giữa build (worktree
  thiếu nền, dependency, conflict…) mà bạn đã có phương án đề xuất → TỰ CHỌN phương án
  đó. Ghi 1 dòng quyết định + lý do vào working log rồi làm tiếp. Được phép TỰ COMMIT để
  gỡ chặn (message mô tả thay đổi, KHÔNG push, liệt kê commit đó trong report).
  Chỉ còn dừng hỏi khi: đổi phạm vi spec/plan, hành động phá hủy/khó đảo ngoài commit,
  hoặc thiếu input chỉ user có.
- **Tick ngay.** Test của một task pass là sửa file plan đánh `- [x]` cho task đó TRƯỚC
  khi bắt task sau. Cấm gom tick cuối turn.
- **Red → green.** Mỗi task: chạy/viết check trước (phải fail), rồi code, rồi chạy lại đến pass.
- **Không placeholder.** Thiếu thông tin ở giai đoạn này nghĩa là phân tích hụt — nêu ra, đừng stub.
- **Chờ subagent thì chờ hết**, hoặc đặt trigger tự tiếp tục. Không kết thúc turn khi nó đang chạy.

## Phần A — Implement (phase `implement`)

1. Đọc `implement_mode` từ state và làm đúng theo:
   - `main`: tự làm tuần tự trong hội thoại này, theo đúng thứ tự task trong plan.
   - `subagent`: giao mỗi nhóm task cho một agent thực thi riêng, mỗi agent một git
     worktree. Tên branch không bắt đầu bằng `claude|antigravity|gemini|codex`.
     Merge worktree về và kiểm tra merge; dọn worktree thừa.
   - `external`: giao CẢ PLAN (hoặc từng gói phase nếu plan lớn) cho engine ngoài
     (codex | agy) trong MỘT worktree chung — làm theo mục "Nhánh external" bên dưới.
   Mode là thứ USER đã nói lúc duyệt. Thiếu mode, hoặc bạn nghĩ mode khác hợp hơn → **DỪNG và HỎI**.

2. Vòng lặp mỗi task:
   1. Báo 1 dòng: đang bắt đầu task nào.
   2. Đỏ: chạy check của task → xác nhận fail (hoặc viết test fail trước).
   3. Code: thay đổi nhỏ nhất mà đủ thoả task. Bám style code sẵn có.
   4. Xanh: chạy lại đến khi pass. Dán kết quả thật — cấm tuyên bố xong khi chưa chạy.
      Chỉ chạy **test của module** đang sửa; full suite chỉ chạy đúng 1 lần ở QC.
   5. Tick `- [x]` cho task đó trong plan NGAY.

3. Xong hết task: chạy full suite ĐÚNG MỘT LẦN, rồi đóng sổ turn bằng MỘT lệnh
   `python3 scripts/tdq_finish.py --files <file .md vừa sửa> --log "<tóm tắt>" --phase qc`
   — lint đúng file, append `docs/workinglog/<hôm nay>.md`, set phase, cập nhật code graph.
   Nội dung log: task đã xong, file đã đổi, kết quả test.

Xong khi: mọi task trong plan đã tick `[x]` và test suite xanh.
Bước kế tiếp: `python3 scripts/tdq_state.py set phase=qc`.

## Nhánh external (Phần A, mode external)

Bạn là ORCHESTRATOR: soạn gói, gọi engine, verify, tick, merge. Engine ngoài chỉ code.
Lane full giao CẢ PLAN một lần (chia gói phase khi plan lớn); quick lane vẫn dùng
`run` một task. Gói task đơn quick CŨNG chép skill vào cuối gói bằng `skill-dump`
và cũng sinh AGENTS.md (task quick dùng skill cần MCP: đã chặn external từ lúc duyệt).

- **Chuẩn bị.** Đọc engine + model bằng
  `python3 scripts/external_task.py parse-plan <plan>` (exit 1 → plan thiếu dòng máy-đọc,
  quay lại 03-plan). Lane full dùng model mức `khó` cho mọi gói. Tạo worktree dùng chung:
  `git worktree add ../tdq-ext-<slug> -b tdq-ext-<slug>`; ghi lại commit gốc
  `base=$(git rev-parse HEAD)` để kiểm về sau. Sinh `AGENTS.md` ở ROOT worktree — chép
  nguyên văn khối fence trong khuôn agents-md.md của bộ này; codex/agy tự nạp.
- **Chia gói.** LUÔN chạy `python3 scripts/external_task.py split-plan <plan>` — kể cả
  plan ≤6 task — vì script tách task `(mcp)` thành gói `"mcp": true` riêng và trả danh
  sách `skills` mỗi gói. Gói `"mcp": true` KHÔNG giao engine: bạn TỰ làm các task đó
  trong worktree (red→green như mode main), đúng vị trí. Gói thường ≤6 task theo ranh
  giới phase; gói sau CHỈ giao khi gói trước qua verify phase.
- **Vòng lặp mỗi gói (gói thường):**
  1. Soạn gói theo khuôn GÓI PLAN của [references/external-task.md](references/external-task.md)
     vào `docs/tdq/external/<slug>/plan-round-<n>.task.md`. Gói gồm: mọi task (mục tiêu,
     file, 1 lệnh test/task), ràng buộc, report mẫu `kind="plan"`. Mục BẮT BUỘC "tự verify":
     engine chạy test từng task, ghi `test_result` thật — verify tầng 1. CUỐI gói:
     chạy `python3 scripts/external_task.py skill-dump <các skill của gói>`. Dán
     nguyên văn output vào mục `## SKILL …` (xem khuôn).
  2. Chạy nền và chờ xong:
     `python3 scripts/external_task.py run-plan --engine <codex|agy> --model <slug> --task-file <gói> --worktree ../tdq-ext-<slug> --slug <slug> --round <n> --plan-file <plan>`
     Cờ `--plan-file` bảo script đối chiếu gói với khối `Dùng:` của plan; thiếu skill
     chỉ cảnh báo + ghi `run.log`, vẫn chạy engine.
     (timeout gói = 540s × số task, trần 3600s, tối đa 2 attempt — đừng chạy foreground
     có trần thời gian). KHÔNG kết thúc turn khi script đang chạy — chờ trong turn (poll)
     để tự tiếp tục verify/tick ngay khi xong.
  3. **Verify PHASE (tầng 2)** — không tin report suông: tự chạy lại lệnh test của TỪNG
     task trong gói tại worktree + đối chiếu `files_changed`. Task pass → tick `- [x]`
     vào plan NGAY; task fail/thiếu → ghi vào danh sách chờ fix.
- **Verify TỔNG (tầng 3, sau gói cuối):** chạy toàn bộ test suite trong worktree +
  diff-check + `status --porcelain`. Tất cả pass → đóng worktree.
- **Fix loop (≤2 vòng, đếm bằng `fix-rounds.json`):** còn task fail sau verify →
  soạn gói MINI-PLAN FIX theo khuôn GÓI FIX (kèm "task đã PASS — không làm lại" và
  "file cấm sửa"). Ghi sổ:
  `python3 scripts/external_task.py fix-rounds add --slug <slug> --tasks <ids> --result fail`.
  Giao lại qua `run-plan --round <n+1>`, verify lại như
  tầng 2/3. `fix-rounds status` trả `fallback` (đủ 2 vòng) hoặc script exit 1 →
  FALLBACK: bạn TỰ implement các task còn lại trong worktree (red→green như mode main)
  VÀ tự viết report `docs/tdq/external/<slug>/<task-id>.json` đúng schema kèm
  `"fallback": "claude"`.
- **Đóng worktree** (sau task cuối):
  1. Xóa `AGENTS.md` (và mọi file skill chép tạm) khỏi worktree TRƯỚC khi diff-check —
     file phục vụ engine, không được lọt vào diff merge về repo.
  2. Kiểm engine không commit lạ: `git -C ../tdq-ext-<slug> log --oneline <base>..HEAD`
     phải RỖNG (bạn tự commit thì tính riêng — engine bị cấm commit).
  3. Diff-check: `git -C ../tdq-ext-<slug> diff --stat` — danh sách file phải khớp hợp
     nhất `files_changed` của các report; file lạ → điều tra trước khi merge. Đối chiếu thêm `git -C <worktree> status --porcelain` để thấy cả file MỚI (untracked) — `diff --stat` chỉ thấy file đã track.
  4. Merge về branch chính, xử lý conflict, chạy toàn suite, rồi
     `git worktree remove ../tdq-ext-<slug>`.
- Log từng lần gọi engine: `docs/tdq/external/<slug>/run.log` (`TDQ_EXTERNAL_LOG=0` tắt).

## Phần B — QC (phase `qc`)

4. Chạy đủ Definition of Done của plan/spec: toàn bộ test suite, các validate, lint/build
   nếu có định nghĩa. Chi tiết cách kiểm: [references/qc.md](references/qc.md).
   Có agent kiểm độc lập thì gọi thêm một lượt.

5. Ghi `docs/tdq/qc/<slug>.md`: từng hạng mục DoD → PASS/FAIL kèm **bằng chứng**
   (lệnh + output thật). Không khẳng định thứ chưa chạy.

6. FAIL → quay lại plan, **không cần duyệt lại**: thêm task fix vào plan dưới
   `## QC vòng N — fix` theo đúng khuôn `- [ ] **QCn.1** <việc> — Test: <check>`, làm
   theo luật Phần A (red→green, tick ngay), rồi chạy lại QC. Lặp đến khi tất cả PASS.
   Chỉ kéo user vào khi bản fix đòi đổi phạm vi.

Xong khi: mọi hạng mục QC PASS và có bằng chứng trong file qc.
Bước kế tiếp: `python3 scripts/tdq_state.py set phase=report`.

## Phần C — Report (phase `report`)

7. Viết `docs/tdq/reports/<slug>.md` — tiếng Việt, KHÔNG giới hạn cứng số dòng, khuyến
   nghị ~10-20 dòng. Khuôn: [references/report-template.md](references/report-template.md).

8. Đóng sổ: tick nốt checkbox còn sót, đổi header plan thành HOÀN THÀNH, rồi chạy
   `tdq_finish.py --files <file vừa sửa> --log "<tóm tắt report>"` — append working
   log, chạy cập nhật code graph nếu có.

9. Trình report trong chat (nguyên văn hoặc tóm tắt ngắn gọn + đường dẫn).

10. **Hỏi user có commit không** — bắt buộc, không tự commit thành quả cuối (ngoại lệ duy
    nhất: commit gỡ chặn giữa build theo Luật cứng, phải liệt kê trong report). User đồng ý
    → message mô tả thay đổi, KHÔNG chứa "generated with …" hay trailer AI; branch theo quy ước.

Xong khi: report đã ghi và user đã được hỏi về commit.
Bước kế tiếp: `python3 scripts/tdq_state.py set phase=idle`
(hoặc `reset` nếu user muốn xoá hẳn để sang request mới).
