---
name: tdq-plan
description: Biến spec đã duyệt thành plan checkbox, mỗi task một test: DỪNG chờ user duyệt kèm mode, duyệt xong build cùng turn. Dùng khi spec chế độ chuyên sâu đã duyệt.
---

# TDQ Plan

Nạp [tdq-conventions](../tdq-conventions/SKILL.md). Plan viết **tiếng Việt**.
Yêu cầu `spec_approved = true`. User duyệt spec xong là viết plan NGAY trong cùng turn.

## Các bước

1. **Chọn mode để ĐỀ XUẤT — không hỏi riêng một lượt.** Cân hai phương án, chốt cái hợp
   nhất làm đề xuất, ghi thẳng vào plan ở bước 2 kèm lý do; user đổi được lúc duyệt:
   - `main` — làm tuần tự ngay trong hội thoại này (plan nhỏ, task phụ thuộc chặt, đụng chung file).
   - `subagent` — giao cho agent `tdq-implementer`, mỗi agent một task, một git worktree
     (nền tảng Agent không có báo cáo giữa chừng nên đơn vị giao việc phải nhỏ bằng đúng
     nhịp tick; main agent tick `[x]` ngay khi nhận báo cáo, trước khi gọi agent kế tiếp).
   Plan trên 6 task mà các task đụng file rời nhau → mặc định ĐỀ XUẤT `subagent`;
   đụng chung file hoặc phụ thuộc chặt → `main`. User vẫn là người chốt mode.

2. **Viết** `docs/tdq/plan/<slug>.md` từ spec ĐÃ DUYỆT.
   Khuôn đầy đủ: [references/plan-template.md](references/plan-template.md).
   Bắt buộc có: header trạng thái + spec nguồn · **một dòng riêng** `Mode thực thi: <main|subagent> — <lý do>` ·
   các phase với task checkbox · task riêng cho log service và unit test · Definition of Done
   trỏ về §6 của spec, **mỗi dòng DoD phải kiểm được bằng một lệnh** (QC đếm hạng mục theo
   đúng số dòng này).
   Mỗi task đúng một việc + một cách kiểm đo được, kèm điểm độ phức tạp `(nN)` và
   ước tính phút `(eNm)`:
   ```
   - [ ] **T1.1** (n3 e6m) <việc cụ thể> — Test: <lệnh hoặc tiêu chí pass>
   ```
   **Chấm điểm `(nN)` ngay lúc viết task**, không chấm bù sau: 1–10 là độ phức tạp
   **tương đối**, KHÔNG phải số phút. Neo theo mốc tham chiếu trong plan-template
   (1 = sửa một dòng · 5 = một hàm mới có test · 10 = đổi công thức lõi). Phân vân
   giữa hai mốc → lấy mốc thấp; hoàn toàn không biết → 5. Điểm là tuỳ chọn (thiếu thì
   bộ đọc coi như 5), nhưng plan mới thì chấm đủ mọi task.
   **Chấm phút `eNm` cùng lúc, không chấm bù sau**: đơn vị là PHÚT (nguyên, 1–999),
   viết trong cùng khối ngoặc sau điểm — `(n5 e12m)`. Ước tính thời gian LÀM, không
   tính lúc chờ user duyệt hay interview. Đừng đệm thêm cho an toàn: status line có
   hệ số hiệu chỉnh học từ lịch sử, đệm tay làm nó học sai. `eNm` tuỳ chọn (thiếu thì
   quy đổi từ điểm), nhưng plan mới thì chấm đủ mọi task — ETA lấy con số này làm
   tín hiệu chính.
   **Luật nhãn `(mcp)` — bắt buộc ngay bước này:** task có khối `Dùng:` mà skill đó
   cần MCP tool lúc chạy → dòng `Dùng:` phải kết thúc bằng nhãn ` (mcp)` NGOÀI
   backtick (khuôn trong plan-template). Nhãn này đánh dấu task buộc Claude tự làm,
   không giao sub-agent thiếu MCP.

3. **Tối ưu.** Cắt phần thừa, kiểm thứ tự phụ thuộc. Đối chiếu 2 luật ánh xạ:
   mỗi đầu ra spec §2 → ≥ 1 task; mỗi dòng `DÙNG` ở spec §3b → ≥ 1 khối hợp đồng đủ 5
   trường (`Dùng/Để/Ra/Kiểm/Không dùng cho`) theo khuôn template. Tự kiểm bằng máy:
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/doc_lint.py" --pair <spec> <plan>` phải exit 0.
   Cần review sâu hơn thì user yêu cầu — khi đó mới gọi agent `tdq-reviewer` (tùy chọn).

4. **Đăng ký file vào state:**
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set plan_file=docs/tdq/plan/<slug>.md
   ```
   **Không** set `implement_mode` ở đây — trường đó chỉ được ghi khi ghi nhận duyệt.

5. **Trình bày & DỪNG.** Chat: tóm tắt plan ≤ 10 dòng (số phase/task, mode bạn ĐỀ XUẤT
   + lý do, DoD). Tự kiểm trước khi in dòng Duyệt: tin nhắn phải CHỨA tóm tắt thật —
   không được thay bằng câu thông báo suông kiểu "đã ghi log, đang chờ duyệt"; thiếu
   thì viết bổ sung ngay. Rồi in đúng dòng:
   ```
   ➤ Duyệt: nhắn "duyệt plan mode <mode đề xuất>" (đổi được: main|subagent — duyệt xong build ngay) · Góp ý: nhắn trực tiếp
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
