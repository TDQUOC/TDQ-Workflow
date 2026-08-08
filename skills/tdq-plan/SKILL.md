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
   Plan trên 6 task mà các phase đụng file rời nhau → mặc định ĐỀ XUẤT `subagent`;
   đụng chung file hoặc phụ thuộc chặt → `main`. User vẫn là người chốt mode.

2. **Viết** `docs/tdq/plan/<slug>.md` từ spec ĐÃ DUYỆT.
   Khuôn đầy đủ: [references/plan-template.md](references/plan-template.md).
   Bắt buộc có: header trạng thái + spec nguồn · **một dòng riêng** `Mode thực thi: <main|subagent> — <lý do>` ·
   các phase với task checkbox · task riêng cho log service và unit test · Definition of Done trỏ về §6 của spec.
   Mỗi task đúng một việc + một cách kiểm đo được:
   ```
   - [ ] **T1.1** <việc cụ thể> — Test: <lệnh hoặc tiêu chí pass>
   ```
   **Luật nhãn `(mcp)` — bắt buộc ngay bước này:** task có khối `Dùng:` mà skill đó
   cần MCP tool lúc chạy → dòng `Dùng:` phải kết thúc bằng nhãn ` (mcp)` NGOÀI
   backtick (khuôn trong plan-template). Nhãn này đánh dấu task buộc Claude tự làm,
   không giao sub-agent thiếu MCP.

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
   + lý do, DoD), rồi in đúng dòng:
   ```
   ➤ Duyệt: nhắn "duyệt plan mode <mode đề xuất>" (đổi được: main|subagent) · Góp ý: nhắn trực tiếp
   ```
   Rồi **kết thúc turn**. Góp ý → sửa, trình lại, chờ tiếp.

6. **User duyệt → ghi nhận NGAY:**
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" approve plan --mode <main|subagent> --by "<nguyên văn>"
   ```
   Mode chốt là mode user NÓI lúc duyệt (khác đề xuất cũng được).
   User duyệt mà không nói mode → **HỎI**, đừng tự chọn, mỗi option một dòng theo khuôn
   [interview.md](../tdq-intake/references/interview.md).
   Ghi nhận xong thì build LUÔN trong cùng turn — không bắt user nhắn thêm câu nào.

Xong khi: `plan_approved = true` và `implement_mode` khác rỗng.
Bước kế tiếp: đổi header plan thành ĐÃ DUYỆT, chạy
`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=implement`,
rồi sang [tdq-build](../tdq-build/SKILL.md) **NGAY trong cùng turn**.
