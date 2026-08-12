# Phase `plan`

Plan viết **tiếng Việt**. Yêu cầu `spec_approved = true`. User duyệt spec xong là viết
plan NGAY trong cùng turn.

## Các bước

1. **Chọn mode để ĐỀ XUẤT — không hỏi riêng một lượt.** Cân hai phương án, chốt cái hợp
   nhất làm đề xuất, ghi thẳng vào plan ở bước 2 kèm lý do; user đổi được lúc duyệt:
   - `main` — làm tuần tự ngay trong hội thoại này (plan nhỏ, task phụ thuộc chặt, đụng chung file).
   - `subagent` — giao cho agent phụ nếu harness hỗ trợ gọi agent, mỗi agent một git
     worktree (nhiều phase độc lập, chạy song song được). Harness không hỗ trợ gọi
     agent phụ → chỉ còn `main`, nói rõ lý do.
   Plan trên 6 task mà các phase đụng file rời nhau → mặc định ĐỀ XUẤT `subagent`
   (nếu harness hỗ trợ); đụng chung file hoặc phụ thuộc chặt → `main`. User vẫn là
   người chốt mode.

2. **Viết** `docs/tdq/plan/<slug>.md` từ spec ĐÃ DUYỆT.
   Khuôn đầy đủ: [references/plan-template.md](references/plan-template.md).
   Bắt buộc có: header trạng thái + spec nguồn · **một dòng riêng**
   `Mode thực thi: <main|subagent> — <lý do>` · các phase với task checkbox · task
   riêng cho log service và unit test (bỏ nếu việc không có runtime) · Definition of
   Done trỏ về §6 của spec, **mỗi dòng DoD phải kiểm được bằng một lệnh**.
   Mỗi task đúng một việc + một cách kiểm đo được, kèm điểm độ phức tạp `(nN)`:
   ```
   - [ ] **T1.1** (n3) <việc cụ thể> — Test: <lệnh hoặc tiêu chí pass>
   ```
   **Chấm điểm `(nN)` ngay lúc viết task**, không chấm bù sau: 1–10 là độ phức tạp
   **tương đối**, KHÔNG phải số phút (xem thang neo mốc trong plan-template). Phân vân
   giữa hai mốc → lấy mốc thấp; hoàn toàn không biết → 5. Điểm là tuỳ chọn (thiếu thì
   coi như 5), nhưng plan mới thì chấm đủ mọi task.
   Task có khối `Dùng:` mà cần công cụ ngoài (search/API) lúc chạy → dòng `Dùng:` phải
   kết thúc bằng nhãn ` (mcp)` ngoài backtick — đánh dấu task buộc bạn tự làm, không
   giao agent phụ thiếu công cụ đó.

3. **Tối ưu.** Cắt phần thừa, kiểm thứ tự phụ thuộc. Đối chiếu 2 luật ánh xạ: mỗi đầu
   ra spec §2 → ≥ 1 task; mỗi dòng `DÙNG` ở spec §3b → ≥ 1 khối hợp đồng đủ 5 trường
   (`Dùng/Để/Ra/Kiểm/Không dùng cho`) theo khuôn plan-template.

4. **Đăng ký file vào state:**
   ```
   python3 scripts/tdq_state.py set plan_file=docs/tdq/plan/<slug>.md
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
   python3 scripts/tdq_state.py approve plan --mode <main|subagent> --by "<nguyên văn>"
   ```
   Mode chốt là mode user NÓI lúc duyệt (khác đề xuất cũng được). User duyệt mà không
   nói mode → **HỎI**, đừng tự chọn, mỗi option một dòng theo khuôn
   [references/interview.md](references/interview.md). Ghi nhận xong thì build LUÔN
   trong cùng turn — không bắt user nhắn thêm câu nào.

Xong khi: `plan_approved = true` và `implement_mode` khác rỗng.
Bước kế tiếp: đổi header plan thành ĐÃ DUYỆT, chạy
`python3 scripts/tdq_state.py set phase=implement`, rồi sang [04-build.md](04-build.md)
**NGAY trong cùng turn**.
