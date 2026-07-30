# 04 — Build: Implement → QC → Report

Yêu cầu `plan_approved = true`. File này lo ba phase: `implement` → `qc` → `report`.

## Luật cứng (áp cho cả ba phase)

- **End-to-end trong MỘT turn.** Không dừng giữa chừng hỏi "có tiếp không". Chỉ dừng khi
  đổi phạm vi thật sự, thiếu/mơ hồ `implement_mode`, hoặc gặp chặn chỉ user gỡ được.
- **Tick ngay.** Test của một task pass là sửa file plan đánh `- [x]` cho task đó TRƯỚC
  khi bắt task sau. Cấm gom tick cuối turn.
- **Red → green.** Mỗi task: chạy/viết check trước (phải fail), rồi code, rồi chạy lại đến pass.
- **Không placeholder.** Thiếu thông tin ở giai đoạn này nghĩa là phân tích hụt — nêu ra, đừng stub.
- **Chờ subagent thì chờ hết**, hoặc đặt trigger tự tiếp tục. Không kết thúc turn khi nó đang chạy.

## Phần A — Implement (phase `implement`)

1. Đọc `implement_mode` từ state và làm đúng theo:
   - `main`: tự làm tuần tự trong hội thoại này, theo đúng thứ tự task trong plan.
   - `subagent`: giao mỗi nhóm task cho một agent thực thi riêng, mỗi agent một git
     worktree. Tên branch không bắt đầu bằng `claude|antigravity|gemini|codex`.
     Merge worktree về và kiểm tra merge; dọn worktree thừa.
   Mode là thứ USER đã nói lúc duyệt. Thiếu mode, hoặc bạn nghĩ mode khác hợp hơn → **DỪNG và HỎI**.

2. Vòng lặp mỗi task:
   1. Báo 1 dòng: đang bắt đầu task nào.
   2. Đỏ: chạy check của task → xác nhận fail (hoặc viết test fail trước).
   3. Code: thay đổi nhỏ nhất mà đủ thoả task. Bám style code sẵn có.
   4. Xanh: chạy lại đến khi pass. Dán kết quả thật — cấm tuyên bố xong khi chưa chạy.
   5. Tick `- [x]` cho task đó trong plan NGAY.

3. Xong hết task: chạy toàn bộ test suite, append working log
   (`docs/workinglog/<hôm nay>.md`, cuối file): task đã xong, file đã đổi, kết quả test.
   Chạy cập nhật code graph nếu project có dùng.

Xong khi: mọi task trong plan đã tick `[x]` và test suite xanh.
Bước kế tiếp: `python3 scripts/tdq_state.py set phase=qc`.

## Phần B — QC (phase `qc`)

4. Chạy đủ Definition of Done của plan/spec: toàn bộ test suite, các validate, lint/build
   nếu có định nghĩa. Chi tiết cách kiểm: [references/qc.md](references/qc.md).
   Có agent kiểm độc lập thì gọi thêm một lượt.

5. Ghi `docs/tdq/qc/<slug>.md`: từng hạng mục DoD → PASS/FAIL kèm **bằng chứng**
   (lệnh + output thật). Không khẳng định thứ chưa chạy.

6. FAIL → quay lại plan, **không cần duyệt lại**: thêm task fix vào plan dưới
   `## QC vòng N — fix` theo đúng khuôn `- [ ] **QCn.1** <việc> — Test: <check>`, làm
   theo luật Phần A (red→green, tick ngay), rồi chạy lại QC. Lặp đến khi tất cả PASS.
   Chỉ kéo user vào khi bản fix đòi đổi phạm vi.

Xong khi: mọi hạng mục QC PASS và có bằng chứng trong file qc.
Bước kế tiếp: `python3 scripts/tdq_state.py set phase=report`.

## Phần C — Report (phase `report`)

7. Viết `docs/tdq/reports/<slug>.md` — tiếng Việt, **≤ 50 dòng**. Khuôn:
   [references/report-template.md](references/report-template.md). Đo bằng `wc -l`,
   quá thì cắt gọn.

8. Đóng sổ: tick nốt checkbox còn sót, đổi header plan thành HOÀN THÀNH, append working
   log, chạy cập nhật code graph nếu có.

9. Trình report trong chat (nguyên văn hoặc tóm tắt ≤ 10 dòng + đường dẫn).

10. **Hỏi user có commit không** — bắt buộc, và tuyệt đối không tự commit. User đồng ý →
    commit message mô tả thay đổi, KHÔNG chứa "generated with …" hay trailer AI; tên
    branch theo quy ước.

Xong khi: report đã ghi và user đã được hỏi về commit.
Bước kế tiếp: `python3 scripts/tdq_state.py set phase=idle`
(hoặc `reset` nếu user muốn xoá hẳn để sang request mới).
