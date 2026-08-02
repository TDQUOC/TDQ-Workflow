---
name: tdq-build
description: Thực thi plan TDQ đã duyệt end-to-end trong một turn, chạy QC theo Definition of Done, rồi viết report và hỏi user về commit. Lane full, sau khi plan được duyệt.
---

# TDQ Build — Implement → QC → Report

Nạp [tdq-conventions](../tdq-conventions/SKILL.md). Yêu cầu `plan_approved = true`.
Skill này lo ba phase: `implement` → `qc` → `report`.

## Luật cứng (áp cho cả ba phase)

- **End-to-end trong MỘT turn.** Không dừng giữa chừng hỏi "có tiếp không". Chỉ dừng khi
  đổi phạm vi thật sự, thiếu/mơ hồ `implement_mode`, hoặc gặp chặn chỉ user gỡ được.
- **Chặn kỹ thuật → tự chọn đề xuất, không hỏi.** Gặp chặn kỹ thuật giữa build (worktree
  thiếu nền, dependency, conflict…) mà bạn đã có phương án đề xuất → TỰ CHỌN phương án đó.
  Ghi 1 dòng quyết định + lý do vào working log rồi làm tiếp. Được phép TỰ COMMIT để gỡ
  chặn (message mô tả thay đổi, KHÔNG push, liệt kê commit đó trong report).
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
   - `subagent`: gọi agent `tdq-implementer`, mỗi agent một git worktree. Tên branch không
     bắt đầu bằng `claude|antigravity|gemini|codex`. Merge worktree về và kiểm tra merge; dọn worktree thừa.
   - `external`: giao TỪNG task cho engine ngoài (codex | agy) trong MỘT worktree chung —
     làm theo mục "Nhánh external" bên dưới.
   Mode là thứ USER đã nói lúc duyệt. Thiếu mode, hoặc bạn nghĩ mode khác hợp hơn → **DỪNG và HỎI**.

2. Vòng lặp mỗi task:
   1. Báo 1 dòng: đang bắt đầu task nào.
   2. Task có khối `Dùng:` → NẠP skill đó ngay (theo trường `Nạp`), làm đúng trường `Để`,
      không lan sang việc ghi ở `Không dùng cho`. Không có khối → bỏ qua bước này.
   3. Đỏ: chạy check của task → xác nhận fail (hoặc viết test fail trước).
   4. Code: thay đổi nhỏ nhất mà đủ thoả task. Bám style code sẵn có.
   5. Xanh: chạy lại đến khi pass. Dán kết quả thật — cấm tuyên bố xong khi chưa chạy.
   6. Tick `- [x]` cho task đó trong plan NGAY.

3. Xong hết task: chạy toàn bộ test suite, append working log
   (`docs/workinglog/<hôm nay>.md`, cuối file): task đã xong, file đã đổi, kết quả test.
   Chạy cập nhật graphify nếu có cài.

Xong khi: mọi task trong plan đã tick `[x]` và test suite xanh.
Bước kế tiếp: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=qc`.

## Nhánh external (Phần A, mode external)

Bạn là ORCHESTRATOR: soạn gói task, gọi runner, verify, tick, merge. Engine ngoài chỉ code.

- **Chuẩn bị.** Đọc engine + model map bằng
  `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/external_task.py" parse-plan <plan>` (exit 1
  → plan thiếu dòng máy-đọc, quay lại tdq-plan). Tạo worktree dùng chung:
  `git worktree add ../tdq-ext-<slug> -b tdq-ext-<slug>`; ghi lại commit gốc
  `base=$(git rev-parse HEAD)` để kiểm về sau.
- **Vòng lặp mỗi task** (đúng thứ tự plan):
  1. Phân độ khó task theo luật trong [tdq-plan](../tdq-plan/SKILL.md) mục "Chốt engine
     + model" → chọn model slug từ map khó/TB/dễ.
  2. Soạn gói task theo khuôn [references/external-task.md](references/external-task.md)
     vào `docs/tdq/external/<slug>/<task-id>.task.md` (mục tiêu 1 câu, kể tên file, 1 lệnh
     test, ràng buộc, report mẫu).
  3. Gọi agent `codex-runner` hoặc `agy-runner` theo engine — **ĐỒNG BỘ**
     (`run_in_background: false`) để turn build đứng chờ và TỰ tiếp tục ngay khi
     runner xong, không phụ thuộc notification xuyên turn/phiên (notification không
     sống qua restart phiên). Nhiều task độc lập có thể gọi nhiều agent đồng bộ trong
     cùng một message để chạy song song. Agent bên trong vẫn chạy
     `external_task.py run …` bằng Bash nền + poll (một attempt có thể tới 540s).
  4. Verify — không tin report suông: tự chạy lại đúng lệnh test của task trong worktree.
     Test pass → tick `- [x]` vào plan NGAY.
  5. Runner trả `engine-failed` (script exit 1) hoặc verify fail → FALLBACK: bạn TỰ
     implement task đó trong worktree (red→green như mode main) VÀ tự viết report
     `docs/tdq/external/<slug>/<task-id>.json` đúng schema kèm `"fallback": "claude"`.
- **Đóng worktree** (sau task cuối):
  1. Kiểm engine không commit lạ: `git -C ../tdq-ext-<slug> log --oneline <base>..HEAD`
     phải RỖNG (bạn tự commit thì tính riêng — engine bị cấm commit).
  2. Diff-check: `git -C ../tdq-ext-<slug> diff --stat` — danh sách file phải khớp hợp
     nhất `files_changed` của các report; file lạ → điều tra trước khi merge. Đối chiếu thêm `git -C <worktree> status --porcelain` để thấy cả file MỚI (untracked) — `diff --stat` chỉ thấy file đã track.
  3. Merge về branch chính, xử lý conflict, chạy toàn suite, rồi
     `git worktree remove ../tdq-ext-<slug>`.
- Log từng lần gọi engine nằm ở `docs/tdq/external/<slug>/run.log` (service tự bật,
  `TDQ_EXTERNAL_LOG=0` tắt) — dán vào QC khi cần bằng chứng.

## Phần B — QC (phase `qc`)

4. Chạy đủ Definition of Done của plan/spec: toàn bộ test suite, các validate, lint/build
   nếu có định nghĩa. Chi tiết cách kiểm: [references/qc.md](references/qc.md).
   Có thể gọi agent `tdq-qc-tester` cho một lượt kiểm độc lập.

5. Ghi `docs/tdq/qc/<slug>.md`: từng hạng mục DoD → PASS/FAIL kèm **bằng chứng**
   (lệnh + output thật). Không khẳng định thứ chưa chạy.

6. FAIL → quay lại plan, **không cần duyệt lại**: thêm task fix vào plan dưới
   `## QC vòng N — fix` theo đúng khuôn `- [ ] **QCn.1** <việc> — Test: <check>`, làm
   theo luật Phần A (red→green, tick ngay), rồi chạy lại QC. Lặp đến khi tất cả PASS.
   Chỉ kéo user vào khi bản fix đòi đổi phạm vi.

Xong khi: mọi hạng mục QC PASS và có bằng chứng trong file qc.
Bước kế tiếp: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=report`.

## Phần C — Report (phase `report`)

7. Viết `docs/tdq/reports/<slug>.md` — tiếng Việt, **≤ 50 dòng**. Khuôn:
   [references/report-template.md](references/report-template.md). Đo bằng `wc -l`,
   quá thì cắt gọn.

8. Đóng sổ: tick nốt checkbox còn sót, đổi header plan thành HOÀN THÀNH, append working
   log, chạy cập nhật graphify nếu có.

9. Trình report trong chat (nguyên văn hoặc tóm tắt ≤ 10 dòng + đường dẫn).

10. **Hỏi user có commit không** — bắt buộc, và không tự commit thành quả cuối (ngoại lệ
    duy nhất: commit gỡ chặn giữa build theo Luật cứng, phải liệt kê trong report). User đồng ý →
    commit message mô tả thay đổi, KHÔNG chứa "generated with …" hay trailer AI; tên
    branch theo quy ước.

Xong khi: report đã ghi và user đã được hỏi về commit.
Bước kế tiếp: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=idle`
(hoặc `reset` nếu user muốn xoá hẳn để sang request mới).
