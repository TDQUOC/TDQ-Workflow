# 03 — Plan

Phase `plan`. Plan viết **tiếng Việt**. Yêu cầu `spec_approved = true`.
**Không** viết cùng turn với spec.

## Các bước

1. **HỎI user chọn mode thực thi — trước khi viết plan.** Không bao giờ tự chọn.
   Hỏi bằng chat, đúng hai phương án, cái bạn khuyên đặt trước và ghi `(Đề xuất)`,
   mỗi cái 1–2 dòng lý do:
   - `main` — làm tuần tự ngay trong hội thoại này (plan nhỏ, task phụ thuộc chặt, đụng chung file).
   - `subagent` — giao cho agent thực thi riêng, mỗi agent một git worktree (nhiều phase độc lập, chạy song song được).
   Chờ user trả lời.

2. **Viết** `docs/tdq/plan/<slug>.md` từ spec ĐÃ DUYỆT.
   Khuôn đầy đủ: [references/plan-template.md](references/plan-template.md).
   Bắt buộc có: header trạng thái + spec nguồn · **một dòng riêng** `Mode thực thi: <main|subagent> — <lý do>` ·
   các phase với task checkbox · task riêng cho log service và unit test · Definition of Done trỏ về §6 của spec.
   Mỗi task đúng một việc + một cách kiểm đo được:
   ```
   - [ ] **T1.1** <việc cụ thể> — Test: <lệnh hoặc tiêu chí pass>
   ```

3. **Tối ưu + nhờ review.** Cắt phần thừa, kiểm thứ tự phụ thuộc. Đối chiếu 2 luật ánh xạ:
   mỗi đầu ra spec §2 → ≥ 1 task; mỗi dòng `DÙNG` ở spec §3b → ≥ 1 khối hợp đồng đủ 6
   trường (`Dùng/Nạp/Để/Ra/Kiểm/Không dùng cho`) theo khuôn template. Tự kiểm bằng máy:
   `python3 scripts/doc_lint.py --pair <spec> <plan>` phải exit 0 (không có file đó thì
   đối chiếu tay từng khối). Nhờ một lượt review độc lập trên file plan, áp dụng góp ý đúng.

4. **Đăng ký file vào state:**
   ```
   python3 scripts/tdq_state.py set plan_file=docs/tdq/plan/<slug>.md
   ```
   **Không** set `implement_mode` ở đây — trường đó chỉ được ghi khi ghi nhận duyệt.

5. **Trình bày & DỪNG.** Chat: tóm tắt plan ≤ 10 dòng (số phase/task, mode user đã chọn
   ở bước 1 + lý do, DoD), rồi in đúng dòng:
   ```
   ➤ Duyệt: nhắn "duyệt plan mode main" (hoặc subagent) · Góp ý: nhắn trực tiếp
   ```
   Rồi **kết thúc turn**. Góp ý → sửa, trình lại, chờ tiếp.

6. **User duyệt → ghi nhận NGAY:**
   ```
   python3 scripts/tdq_state.py approve plan --mode <main|subagent> --by "<nguyên văn>"
   ```
   Mode chốt là mode user NÓI lúc duyệt (đổi ý so với bước 1 cũng được).
   User duyệt mà không nói mode → **HỎI**, đừng tự chọn.

Xong khi: `plan_approved = true` và `implement_mode` khác rỗng.
Bước kế tiếp: đổi header plan thành ĐÃ DUYỆT, chạy
`python3 scripts/tdq_state.py set phase=implement`, rồi sang [04-build.md](04-build.md).
