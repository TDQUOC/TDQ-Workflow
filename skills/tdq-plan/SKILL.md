---
name: tdq-plan
description: Biến spec thành plan checkbox, mỗi task một test: DỪNG chờ user duyệt plan, rồi hỏi cách chạy và build cùng turn. Dùng khi spec chế độ chuyên sâu đã duyệt.
---

# TDQ Plan

Nạp [tdq-conventions](../tdq-conventions/SKILL.md). Plan viết **tiếng Việt**
(nhắc lại có chủ ý — bản gốc ở `skills/tdq-conventions/SKILL.md`).
Yêu cầu `spec_approved = true`. User duyệt spec xong là viết plan NGAY trong cùng turn.

## Các bước

1. **Chọn mode để ĐỀ XUẤT.** Cân hai phương án, ghi cái hợp nhất vào plan ở bước 2 kèm
   lý do; user chốt ở cổng `mode` (bước 6):
   - `main` — nhãn hiển thị "làm trực tiếp (inline implement)": làm tuần tự ngay trong
     hội thoại này (plan nhỏ, task phụ thuộc chặt, đụng chung file).
   - `subagent` — nhãn hiển thị "giao trợ lý (sub-agent implement)": nhiều trợ lý chạy
     song song, bạn làm leader chia cả plan thành từng đợt, mỗi agent một worktree, phần
     không tách được thì tự làm. Luật: `tdq-build/references/team-mode.md`.
   Trên 6 task mà đụng file rời nhau → ĐỀ XUẤT `subagent`; đụng chung file hoặc phụ
   thuộc chặt → `main`.

2. **Viết** `docs/tdq/plan/<slug>.md` từ spec ĐÃ DUYỆT — khuôn đầy đủ ở
   [references/plan-template.md](references/plan-template.md).
   Bắt buộc có: header trạng thái + spec nguồn · **một dòng riêng** `Mode thực thi: <main|subagent> — <lý do>` ·
   các phase với task checkbox · task riêng cho log service và unit test · Definition of Done
   trỏ về §6 của spec, **mỗi dòng DoD kiểm được bằng một lệnh** (QC đếm hạng mục theo đúng
   số dòng này). Mỗi task đúng một việc + một cách kiểm đo được, kèm ước tính phút `(eNm)`:
   ```
   - [ ] **T1.1** (e6m) <việc cụ thể> — Test: <lệnh hoặc tiêu chí pass>
   ```
   **Mọi task tạo/sửa file mã nguồn phải có dòng `Chạm:` ngay dưới nó**, liệt kê đường
   dẫn file trong backtick: vừa là bản đồ ảnh hưởng, vừa là thứ `tdq_team.py phan-cong`
   đọc để chia đợt song song. Khuôn: 2 mục `Chạm:`/`Cụm song song` của plan-template.
   **Chấm `eNm` ngay lúc viết task**, đủ mọi task, không chấm bù sau và đừng đệm giờ cho
   an toàn. `eNm` là số phút agent TỰ THỰC THI task (không tính lúc chờ duyệt); ETA cả
   plan = tổng `eNm` các task chưa xong. Luật chấm đầy đủ: mục cuối plan-template.
   **Luật nhãn `(mcp)`:** task có khối `Dùng:` mà skill đó cần MCP tool lúc chạy → dòng
   `Dùng:` kết thúc bằng ` (mcp)` NGOÀI backtick: task đó buộc Claude tự làm.

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

   **Cách làm:** <1–2 câu>.
   **Khối lượng:** <số phase>, <số task>, ước tính <tổng phút>.
   **Kiểm thế nào:** <số dòng DoD>, mỗi dòng một lệnh kiểm.

   Xem đầy đủ tại: `docs/tdq/plan/<slug>.md`

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
   Câu duyệt đã kèm sẵn tên mode (`main`/`inline`, `subagent`/`sub-agent`) → thêm
   `--mode <giá trị đó>` vào chính lệnh trên, **bỏ qua** cổng dưới đây và build luôn.
   Cấm hỏi lại thứ user vừa nói.
   Chưa nói mode → state dừng ở phase `mode`, in khối hỏi rồi DỪNG. Khuôn nguyên văn —
   hai option "làm trực tiếp (inline implement)" và "giao trợ lý (sub-agent implement)",
   mỗi option một dòng, đề xuất luôn ở A — nằm ở
   [references/mode-gate.md](references/mode-gate.md).
   Ngay dưới hai option phải có đoạn **"Vì sao đề xuất"** dài 1–3 dòng. Cấm nói chung
   chung: đủ 4 căn cứ đọc từ chính plan (số task, chuỗi phụ thuộc, số file bị nhiều task
   cùng đụng, có nhãn `(mcp)` không), kết bằng một câu vì sao không chọn phương án còn
   lại. Luật đầy đủ kèm ví dụ ở cùng file mode-gate.md.
   Hai tên gọi là **nhãn hiển thị**; state vẫn ghi `main`/`subagent`
   (`MODE_LABELS`/`MODE_ALIASES` trong `scripts/tdq_state.py`).
   User trả lời → chạy lại lệnh trên kèm `--mode <main|subagent>` rồi build LUÔN cùng
   turn. Mode chốt là mode user NÓI (khác đề xuất cũng được); cấm tự chọn thay user.

Xong khi: `plan_approved = true` và `implement_mode` khác rỗng.
Bước kế tiếp: đổi header plan thành ĐÃ DUYỆT, chạy
`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=implement`,
rồi sang [tdq-build](../tdq-build/SKILL.md) **NGAY trong cùng turn**.
