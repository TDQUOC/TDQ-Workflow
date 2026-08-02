# 03 — Plan

Phase `plan`. Plan viết **tiếng Việt**. Yêu cầu `spec_approved = true`.
**Không** viết cùng turn với spec.

## Các bước

1. **HỎI user chọn mode thực thi — trước khi viết plan.** Không bao giờ tự chọn.
   Hỏi bằng chat, đúng ba phương án, cái bạn khuyên đặt trước và ghi `(Đề xuất)`,
   mỗi cái 1–2 dòng lý do:
   - `main` — làm tuần tự ngay trong hội thoại này (plan nhỏ, task phụ thuộc chặt, đụng chung file).
   - `subagent` — giao cho agent thực thi riêng, mỗi agent một git worktree (nhiều phase độc lập, chạy song song được).
   - `external` — giao TỪNG task cho engine ngoài Codex CLI / Antigravity CLI (agy) trong
     một worktree chung; hợp khi task rõ ràng, tự chứa, muốn tiết kiệm quota chính.
   User chọn external → làm tiếp mục "Chốt engine + model" bên dưới TRƯỚC khi viết plan.
   Chờ user trả lời.

2. **Viết** `docs/tdq/plan/<slug>.md` từ spec ĐÃ DUYỆT.
   Khuôn đầy đủ: [references/plan-template.md](references/plan-template.md).
   Bắt buộc có: header trạng thái + spec nguồn · **một dòng riêng** `Mode thực thi: <main|subagent|external> — <lý do>` ·
   các phase với task checkbox · task riêng cho log service và unit test · Definition of Done trỏ về §6 của spec.
   Mode external → thêm ngay dưới dòng mode MỘT dòng máy-đọc đúng khuôn (xem mục
   "Chốt engine + model"). Mỗi task đúng một việc + một cách kiểm đo được:
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
   ở bước 1 + lý do, DoD; external thì kèm engine + model map), rồi in đúng dòng:
   ```
   ➤ Duyệt: nhắn "duyệt plan mode <mode user đã chọn ở bước 1>" (đổi được: main|subagent|external) · Góp ý: nhắn trực tiếp
   ```
   Rồi **kết thúc turn**. Góp ý → sửa, trình lại, chờ tiếp.

6. **User duyệt → ghi nhận NGAY:**
   ```
   python3 scripts/tdq_state.py approve plan --mode <main|subagent|external> --by "<nguyên văn>"
   ```
   Mode chốt là mode user NÓI lúc duyệt (đổi ý so với bước 1 cũng được).
   User duyệt mà không nói mode → **HỎI**, đừng tự chọn.

## Chốt engine + model (chỉ mode external)

Làm đủ 3 bước, theo đúng thứ tự — kết quả là MỘT dòng máy-đọc trong plan:

1. **Engine.** Hỏi user chọn `codex` | `antigravity` | `auto`. Luật auto (ghi cứng):
   đa số task là code/refactor/test → codex; đa số là research/docs/UI → agy; hòa → codex.
   "auto" phải được RESOLVE thành đúng MỘT engine cho CẢ plan ngay tại đây — dòng
   máy-đọc và mọi thứ sau nó không bao giờ chứa chữ "auto".
   Lưu ý agy (đã fix 2026-07-30): headless mặc định ghi file vào workspace scratch
   `~/.gemini/antigravity-cli/scratch/` thay vì worktree — wrapper `external_task.py`
   đã tự thêm `--add-dir <worktree>` nên agy ghi đúng chỗ; không cần né agy nữa.
2. **Trình list model THẬT rồi nhận 1–3 tên.** Chạy
   `python3 scripts/external_models.py list <codex|agy>`
   và trình nguyên văn danh sách (slug có nhãn `(chưa xác minh)` vẫn trình, nói rõ nghĩa).
   User trả 1–3 tên THEO LIST: 1 tên = mọi task · 2 tên = [khó, dễ] (TB dùng tên "khó")
   · 3 tên = [khó, TB, dễ].
3. **Ghi dòng máy-đọc** ngay dưới dòng `Mode thực thi:` trong plan — đúng khuôn, một dòng:
   ```
   Thực thi external: engine=<codex|agy> · khó=<slug> · TB=<slug> · dễ=<slug>
   ```
   (1 tên → chỉ ghi `khó=`; 2 tên → ghi `khó=` và `dễ=`. Kiểm bằng
   `python3 scripts/external_task.py parse-plan <plan>` exit 0.)

**Luật phân độ khó từng task** (04-build sẽ dùng khi giao việc — ghi cứng, không cảm tính):
- **khó**: task đụng ≥ 3 file, hoặc thuật toán/logic lõi của sản phẩm.
- **dễ**: task đụng đúng 1 file và thuộc loại docs/config/rename/thay chuỗi.
- **TB**: mọi task còn lại.

Xong khi: `plan_approved = true` và `implement_mode` khác rỗng.
Bước kế tiếp: đổi header plan thành ĐÃ DUYỆT, chạy
`python3 scripts/tdq_state.py set phase=implement`, rồi sang [04-build.md](04-build.md).
