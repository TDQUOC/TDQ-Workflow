---
name: tdq-plan
description: Biến spec đã duyệt thành plan tiếng Việt checkbox, mỗi task một test, đề xuất mode; DỪNG chờ user duyệt kèm mode, duyệt xong build ngay cùng turn. Lane full.
---

# TDQ Plan

Nạp [tdq-conventions](../tdq-conventions/SKILL.md). Plan viết **tiếng Việt**.
Yêu cầu `spec_approved = true`. User duyệt spec xong là viết plan NGAY trong cùng turn.

## Các bước

1. **Chọn mode để ĐỀ XUẤT — không hỏi riêng một lượt.** Cân ba phương án, chốt cái hợp
   nhất làm đề xuất, ghi thẳng vào plan ở bước 2 kèm lý do; user đổi được lúc duyệt:
   - `main` — làm tuần tự ngay trong hội thoại này (plan nhỏ, task phụ thuộc chặt, đụng chung file).
   - `subagent` — giao cho agent `tdq-implementer`, mỗi agent một git worktree (nhiều phase độc lập, chạy song song được).
   - `external` — giao CẢ PLAN (chia gói theo phase khi plan lớn) cho engine ngoài
     Codex CLI / Antigravity CLI (agy) trong một worktree chung; hợp khi task rõ ràng,
     tự chứa, muốn tiết kiệm quota Claude.
   Plan trên 6 task → mặc định ĐỀ XUẤT `subagent`, giao theo phase (cụm file rời nhau),
   để hội thoại chính không phải giữ hết chi tiết; user vẫn là người chốt mode.
   Đề xuất external → làm mục "Chốt engine + model" bên dưới TRƯỚC khi viết plan
   (engine + model là thứ DUY NHẤT phải hỏi user ở phase này).

2. **Viết** `docs/tdq/plan/<slug>.md` từ spec ĐÃ DUYỆT.
   Khuôn đầy đủ: [references/plan-template.md](references/plan-template.md).
   Bắt buộc có: header trạng thái + spec nguồn · **một dòng riêng** `Mode thực thi: <main|subagent|external> — <lý do>` ·
   các phase với task checkbox · task riêng cho log service và unit test · Definition of Done trỏ về §6 của spec.
   Mode external → thêm ngay dưới dòng mode MỘT dòng máy-đọc đúng khuôn (xem mục
   "Chốt engine + model"). Mỗi task đúng một việc + một cách kiểm đo được:
   ```
   - [ ] **T1.1** <việc cụ thể> — Test: <lệnh hoặc tiêu chí pass>
   ```
   **Luật nhãn `(mcp)` — bắt buộc ngay bước này:** task có khối `Dùng:` mà skill đó
   cần MCP tool lúc chạy → dòng `Dùng:` phải kết thúc bằng nhãn ` (mcp)` NGOÀI
   backtick, đúng cú pháp chuẩn spec §1 (khuôn trong plan-template). Nhãn này là
   thứ `split-plan` đọc bằng máy để giữ task lại cho Claude khi mode external —
   thiếu nhãn là engine ngoài nhận task không chạy nổi.

3. **Tối ưu.** Cắt phần thừa, kiểm thứ tự phụ thuộc. Đối chiếu 2 luật ánh xạ:
   mỗi đầu ra spec §2 → ≥ 1 task; mỗi dòng `DÙNG` ở spec §3b → ≥ 1 khối hợp đồng đủ 6
   trường (`Dùng/Nạp/Để/Ra/Kiểm/Không dùng cho`) theo khuôn template. Tự kiểm bằng máy:
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/doc_lint.py" --pair <spec> <plan>` phải exit 0.
   Cần review sâu hơn thì user yêu cầu — khi đó mới gọi agent `tdq-reviewer` (tùy chọn).

4. **Đăng ký file vào state:**
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set plan_file=docs/tdq/plan/<slug>.md
   ```
   **Không** set `implement_mode` ở đây — trường đó chỉ được ghi khi ghi nhận duyệt.

5. **Trình bày & DỪNG.** Chat: tóm tắt plan ≤ 10 dòng (số phase/task, mode bạn ĐỀ XUẤT
   + lý do, DoD; external thì kèm engine + model map), rồi in đúng dòng:
   ```
   ➤ Duyệt: nhắn "duyệt plan mode <mode đề xuất>" (đổi được: main|subagent|external) · Góp ý: nhắn trực tiếp
   ```
   Rồi **kết thúc turn**. Góp ý → sửa, trình lại, chờ tiếp.

6. **User duyệt → ghi nhận NGAY:**
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" approve plan --mode <main|subagent|external> --by "<nguyên văn>"
   ```
   Mode chốt là mode user NÓI lúc duyệt (khác đề xuất cũng được).
   User duyệt mà không nói mode → **HỎI**, đừng tự chọn.
   Ghi nhận xong thì build LUÔN trong cùng turn — không bắt user nhắn thêm câu nào.

## Chốt engine + model (chỉ mode external)

Làm đủ 3 bước, theo đúng thứ tự — kết quả là MỘT dòng máy-đọc trong plan:

1. **Engine.** Hỏi user chọn `codex` | `antigravity` | `auto`. Luật auto (ghi cứng):
   đa số task là code/refactor/test → codex; đa số là research/docs/UI → agy; hòa → codex.
   "auto" phải được RESOLVE thành đúng MỘT engine cho CẢ plan ngay tại đây — dòng
   máy-đọc và mọi thứ sau nó không bao giờ chứa chữ "auto".
   Lưu ý agy (đã fix 2026-07-30): headless mặc định ghi file vào workspace scratch
   `~/.gemini/antigravity-cli/scratch/` thay vì worktree — wrapper `external_task.py`
   đã tự thêm `--add-dir <worktree>` nên agy ghi đúng chỗ; không cần né agy nữa.
2. **Trình list model THẬT rồi nhận ĐÚNG 1 tên.** Chạy
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/external_models.py" list <codex|agy>`
   và trình nguyên văn danh sách (slug có nhãn `(chưa xác minh)` vẫn trình, nói rõ nghĩa).
   Lane full giao CẢ GÓI plan một lần (`run-plan`) nên chỉ dùng MỘT model cho mọi gói —
   khuyên user chọn model đủ sức cho task khó nhất của plan.
3. **Ghi dòng máy-đọc** ngay dưới dòng `Mode thực thi:` trong plan — đúng khuôn, một dòng:
   ```
   Thực thi external: engine=<codex|agy> · khó=<slug>
   ```
   (Tương thích: dòng cũ có thêm `· TB=<slug> · dễ=<slug>` vẫn parse được, nhưng lane
   full chỉ dùng giá trị `khó=`. Kiểm bằng
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/external_task.py" parse-plan <plan>` exit 0.)

Xong khi: `plan_approved = true` và `implement_mode` khác rỗng.
Bước kế tiếp: đổi header plan thành ĐÃ DUYỆT, chạy
`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=implement`,
rồi sang [tdq-build](../tdq-build/SKILL.md) **NGAY trong cùng turn**.
