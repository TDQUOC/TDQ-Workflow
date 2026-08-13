---
name: tdq-plan
description: Biến spec thành plan checkbox, mỗi task một test: DỪNG chờ user duyệt plan, rồi hỏi cách chạy và build cùng turn. Dùng khi spec chế độ chuyên sâu đã duyệt.
---

# TDQ Plan

Nạp [tdq-conventions](../tdq-conventions/SKILL.md). Plan viết **tiếng Việt**.
Yêu cầu `spec_approved = true`. User duyệt spec xong là viết plan NGAY trong cùng turn.

## Các bước

1. **Chọn mode để ĐỀ XUẤT.** Cân hai phương án, ghi cái hợp nhất vào plan ở bước 2 kèm
   lý do; user chốt ở cổng `mode` (bước 6):
   - `main` — làm tuần tự ngay trong hội thoại này (plan nhỏ, task phụ thuộc chặt, đụng chung file).
   - `subagent` — giao agent `tdq-implementer`, mỗi agent một task, một git worktree (nền
     tảng Agent không báo cáo giữa chừng nên đơn vị giao việc phải nhỏ bằng đúng nhịp
     tick; main agent tick `[x]` ngay khi nhận báo cáo, trước khi gọi agent kế tiếp).
   Trên 6 task mà đụng file rời nhau → ĐỀ XUẤT `subagent`; đụng chung file hoặc phụ
   thuộc chặt → `main`.

2. **Viết** `docs/tdq/plan/<slug>.md` từ spec ĐÃ DUYỆT — khuôn đầy đủ ở
   [references/plan-template.md](references/plan-template.md).
   Bắt buộc có: header trạng thái + spec nguồn · **một dòng riêng** `Mode thực thi: <main|subagent> — <lý do>` ·
   các phase với task checkbox · task riêng cho log service và unit test · Definition of Done
   trỏ về §6 của spec, **mỗi dòng DoD kiểm được bằng một lệnh** (QC đếm hạng mục theo đúng
   số dòng này). Mỗi task đúng một việc + một cách kiểm đo được, kèm điểm `(nN)` và phút `(eNm)`:
   ```
   - [ ] **T1.1** (n3 e6m) <việc cụ thể> — Test: <lệnh hoặc tiêu chí pass>
   ```
   **Chấm cả `(nN)` và `eNm` ngay lúc viết task**, không chấm bù sau, và chấm đủ mọi task.
   `nN` là độ phức tạp tương đối 1–10, `eNm` là số phút LÀM (không tính lúc chờ duyệt).
   Thang mốc và luật chấm đầy đủ: mục cuối của plan-template. Đừng đệm giờ cho an toàn.
   **Luật nhãn `(mcp)` — bắt buộc ngay bước này:** task có khối `Dùng:` mà skill đó cần
   MCP tool lúc chạy → dòng `Dùng:` phải kết thúc bằng nhãn ` (mcp)` NGOÀI backtick.
   Nhãn này đánh dấu task buộc Claude tự làm, không giao sub-agent thiếu MCP.

3. **Tối ưu.** Cắt phần thừa, kiểm thứ tự phụ thuộc. Đối chiếu 2 luật ánh xạ: mỗi đầu ra
   spec §2 → ≥ 1 task; mỗi dòng `DÙNG` ở spec §3b → ≥ 1 khối hợp đồng đủ 5 trường
   (`Dùng/Để/Ra/Kiểm/Không dùng cho`) theo khuôn template. Tự kiểm bằng máy:
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/doc_lint.py" --pair <spec> <plan>` phải exit 0.
   Cần review sâu hơn thì user yêu cầu — khi đó mới gọi agent `tdq-reviewer` (tùy chọn).

4. **Đăng ký file vào state:**
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set plan_file=docs/tdq/plan/<slug>.md
   ```
   **Không** set `implement_mode` ở đây — trường đó chỉ được ghi khi ghi nhận duyệt.

5. **Trình bày & DỪNG.** Viết khối trình plan theo
   [user-facing-block.md](../tdq-conventions/references/user-facing-block.md) — đủ 5
   thành phần, khối duyệt nằm cuối tin nhắn, **không** hỏi mode ở đây:
   ```
   Tôi đã viết xong plan để thực hiện yêu cầu của bạn.

   Cách làm: <1–2 câu>.
   Khối lượng: <số phase>, <số task>, ước tính <tổng phút>.
   Kiểm thế nào: <số dòng DoD>, mỗi dòng một lệnh kiểm.

   Xem đầy đủ tại: docs/tdq/plan/<slug>.md

   ---

   **Bạn duyệt plan này chứ?**

   ➤ Duyệt: nhắn "duyệt plan" (duyệt xong tôi hỏi bạn một câu về cách chạy) · Góp ý: nhắn trực tiếp
   ```
   Phần nội dung ≤ 10 dòng, là tóm tắt THẬT — cấm thay bằng thông báo suông kiểu "đã ghi
   log, đang chờ duyệt". Trích nguyên một khuôn/mẫu văn bản làm ví dụ thì gắn nhãn ngay
   trước đoạn trích: "(khuôn mẫu — áp dụng cho các lần hỏi sau, không phải câu hỏi của
   turn này)". Rồi **kết thúc turn**. Góp ý → sửa, trình lại, chờ tiếp.

6. **User duyệt → ghi nhận NGAY, rồi hỏi cách chạy trong CÙNG turn:**
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" approve plan --by "<nguyên văn>"
   ```
   Câu duyệt đã kèm sẵn chữ `main`/`subagent` → thêm `--mode <main|subagent>` vào chính
   lệnh trên, **bỏ qua** cổng dưới đây và build luôn. Cấm hỏi lại thứ user vừa nói.
   Chưa nói mode → state dừng ở phase `mode`, in tiếp khối hỏi (vẫn theo
   [user-facing-block.md](../tdq-conventions/references/user-facing-block.md)) rồi DỪNG:
   ```
   Plan đã được duyệt. Còn một câu cuối: bạn muốn tôi chạy theo cách nào?

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
`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=implement`,
rồi sang [tdq-build](../tdq-build/SKILL.md) **NGAY trong cùng turn**.
