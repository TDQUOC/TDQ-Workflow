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

5. **Trình bày & DỪNG.** Viết khối trình plan theo
   [references/user-facing-block.md](references/user-facing-block.md) — câu dẫn xưng
   "bạn", tóm tắt ≤ 10 dòng (số phase/task, mode bạn ĐỀ XUẤT + lý do, DoD), dòng
   `Xem đầy đủ tại: docs/tdq/plan/<slug>.md`, đường kẻ ngăn, rồi khối duyệt ở cuối:
   ```
   **Bạn duyệt plan này chứ?**

   ➤ Duyệt: nhắn "duyệt plan" (duyệt xong tôi hỏi bạn một câu về cách chạy) · Góp ý: nhắn trực tiếp
   ```
   Rồi **kết thúc turn**. Góp ý → sửa, trình lại, chờ tiếp.

6. **User duyệt → ghi nhận NGAY, rồi hỏi cách chạy trong CÙNG turn:**
   ```
   python3 scripts/tdq_state.py approve plan --by "<nguyên văn>"
   ```
   Câu duyệt đã kèm sẵn chữ `main`/`subagent` → thêm `--mode <main|subagent>` vào chính
   lệnh trên và build luôn, không hỏi lại thứ user vừa nói.
   Chưa nói mode → state dừng ở phase `mode`, hỏi tiếp bằng khối riêng:
   ```
   - A (đề xuất): main — tôi làm tuần tự ngay trong cuộc trò chuyện này, bạn theo dõi được từng bước.
   - B: subagent — tôi chia việc cho nhiều trợ lý chạy song song, nhanh hơn nhưng bạn chỉ thấy báo cáo từng chặng.

   ---

   **Bạn chọn cách nào?**

   ➤ Trả lời: nhắn "main" hoặc "subagent" (chọn xong tôi bắt tay làm ngay) · Góp ý: nhắn trực tiếp
   ```
   User trả lời → chạy lại lệnh trên kèm `--mode <main|subagent>` rồi build LUÔN cùng
   turn. Mode chốt là mode user NÓI (khác đề xuất cũng được); cấm tự chọn thay user.

Xong khi: `plan_approved = true` và `implement_mode` khác rỗng.
Bước kế tiếp: đổi header plan thành ĐÃ DUYỆT, chạy
`python3 scripts/tdq_state.py set phase=implement`, rồi sang [04-build.md](04-build.md)
**NGAY trong cùng turn**.
