---
name: tdq-build
description: Thực thi plan TDQ đã duyệt end-to-end trong một turn, chạy QC theo Definition of Done, viết report rồi hỏi user về commit. Lane full, ngay sau khi plan duyệt.
---

# TDQ Build — Implement → QC → Report

Nạp [tdq-conventions](../tdq-conventions/SKILL.md). Yêu cầu `plan_approved = true`.
Skill này lo ba phase: `implement` → `qc` → `report`.

## Luật cứng (áp cho cả ba phase)

- **Vào build NGAY trong turn user duyệt plan, rồi chạy end-to-end trong MỘT turn.** Không
  bắt user nhắn thêm câu nào, không dừng giữa chừng hỏi "có tiếp không". Chỉ dừng khi đổi
  phạm vi thật sự, thiếu/mơ hồ `implement_mode`, hoặc gặp chặn chỉ user gỡ được.
- **Chặn kỹ thuật → tự chọn đề xuất, không hỏi.** Gặp chặn kỹ thuật giữa build (worktree
  thiếu nền, dependency, conflict…) mà bạn đã có phương án đề xuất → TỰ CHỌN phương án đó.
  Ghi 1 dòng quyết định + lý do vào working log rồi làm tiếp. Được phép TỰ COMMIT để gỡ
  chặn (message mô tả thay đổi, KHÔNG push, liệt kê commit đó trong report).
  Chỉ còn dừng hỏi khi: đổi phạm vi spec/plan, hành động phá hủy/khó đảo ngoài commit
  (ví dụ: đổi schema DB, xoá data, đổi API contract công khai), hoặc thiếu input chỉ
  user có.
- **Tick ngay.** Test của một task pass là sửa file plan đánh `- [x]` cho task đó TRƯỚC
  khi bắt task sau. Cấm gom tick cuối turn.
- **Red → green.** Mỗi task: chạy/viết check trước (phải fail), rồi code, rồi chạy lại đến pass.
- **Không placeholder.** Thiếu thông tin ở giai đoạn này nghĩa là phân tích hụt — nêu ra, đừng stub.
- **Chờ subagent thì chờ hết**, hoặc đặt trigger tự tiếp tục. Không kết thúc turn khi nó đang chạy.

## Phần A — Implement (phase `implement`)

1. Đọc `implement_mode` từ state và làm đúng theo:
   - `main`: tự làm tuần tự trong hội thoại này, theo đúng thứ tự task trong plan.
   - `subagent`: gọi agent `tdq-implementer`, mỗi agent một git worktree (tên branch theo
     conventions §7). Merge worktree về và kiểm tra merge; dọn worktree thừa.
   Mode là thứ USER đã nói lúc duyệt. Thiếu mode, hoặc bạn nghĩ mode khác hợp hơn → **DỪNG và HỎI**.

2. Vòng lặp mỗi task:
   1. Báo 1 dòng: đang bắt đầu task nào.
   2. Task có khối `Dùng:` → NẠP skill đó ngay (theo trường `Nạp`), làm đúng trường `Để`,
      không lan sang việc ghi ở `Không dùng cho`. Không có khối → bỏ qua bước này.
   3. Đỏ: chạy check của task → xác nhận fail (hoặc viết test fail trước).
   4. Code: thay đổi nhỏ nhất mà đủ thoả task. Bám style code sẵn có.
   5. Xanh: chạy lại đến khi pass, chỉ chạy **test của module** đang sửa — full suite
      để dành, chạy đúng 1 lần ở QC. Dán kết quả thật, cấm tuyên bố xong khi chưa chạy.
   6. Tick `- [x]` cho task đó trong plan NGAY.

3. Xong hết task: chạy full suite ĐÚNG MỘT LẦN, rồi đóng sổ turn bằng MỘT lệnh
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_finish.py" --files <file .md vừa sửa> --log "<task xong, file đổi, kết quả test>" --phase qc`
   — lint đúng file, append working log, set phase, graphify: 4 việc trong 1 call.

Xong khi: mọi task trong plan đã tick `[x]` và test suite xanh.
Bước kế tiếp: lệnh `tdq_finish.py … --phase qc` ở mục 3 (đã set phase luôn).

## Phần B — QC (phase `qc`)

4. Chạy đủ Definition of Done của plan/spec: toàn bộ test suite, các validate, lint/build
   nếu có định nghĩa. Chi tiết cách kiểm: [references/qc.md](references/qc.md).
   Có thể gọi agent `tdq-qc-tester` cho một lượt kiểm độc lập.

5. Ghi `docs/tdq/qc/<slug>.md`: từng hạng mục DoD → PASS/FAIL kèm **bằng chứng**
   (lệnh + output thật). Không khẳng định thứ chưa chạy.

6. FAIL → quay lại plan, **không cần duyệt lại**: thêm task fix vào plan dưới
   `## QC vòng N — fix` theo đúng khuôn `- [ ] **QCn.1** <việc> — Test: <check>`, làm
   theo luật Phần A (red→green, tick ngay), rồi chạy lại QC. Lặp đến khi tất cả PASS.
   Chỉ kéo user vào khi bản fix đòi đổi phạm vi.

Xong khi: mọi hạng mục QC PASS và có bằng chứng trong file qc.
Bước kế tiếp: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=report`.

## Phần C — Report (phase `report`)

7. Viết `docs/tdq/reports/<slug>.md` — tiếng Việt, KHÔNG giới hạn cứng số dòng, khuyến
   nghị ~10-20 dòng. Khuôn: [references/report-template.md](references/report-template.md).

8. Đóng sổ: tick nốt checkbox còn sót, đổi header plan thành HOÀN THÀNH, rồi chạy
   `tdq_finish.py --files <file vừa sửa> --log "<tóm tắt report>"` (working log + graphify).

9. Trình report trong chat (nguyên văn hoặc tóm tắt ngắn gọn + đường dẫn).

10. **Hỏi user có commit không** — bắt buộc, không tự commit thành quả cuối (ngoại lệ duy
    nhất: commit gỡ chặn giữa build theo Luật cứng, phải liệt kê trong report). User đồng ý
    → message mô tả thay đổi, KHÔNG chứa "generated with …" hay trailer AI; branch theo quy ước.

Xong khi: report đã ghi và user đã được hỏi về commit.
Bước kế tiếp: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=idle`
(hoặc `reset` nếu user muốn xoá hẳn để sang request mới).
