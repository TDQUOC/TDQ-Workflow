# Phase `implement` → `qc` → `report`

Yêu cầu `plan_approved = true`. Ba phase liên tiếp, làm end-to-end trong MỘT turn.

## Luật cứng (áp cho cả ba phase)

- **Vào build NGAY trong turn user duyệt plan, rồi chạy end-to-end trong MỘT turn.** Không
  bắt user nhắn thêm câu nào, không dừng giữa chừng hỏi "có tiếp không". Chỉ dừng khi đổi
  phạm vi thật sự, thiếu/mơ hồ `implement_mode`, hoặc gặp chặn chỉ user gỡ được.
- **Chặn kỹ thuật → tự chọn đề xuất, không hỏi.** Có sẵn phương án thì TỰ CHỌN, ghi 1
  dòng quyết định + lý do vào working log rồi làm tiếp. Được TỰ COMMIT để gỡ chặn
  (message mô tả thay đổi, KHÔNG push, liệt kê commit đó trong report).
  Chỉ dừng hỏi khi: đổi phạm vi spec/plan, việc phá hủy/khó đảo ngoài commit (đổi schema
  DB, xoá data, đổi API contract công khai), hoặc thiếu input chỉ user có.
- **Tick ngay.** Bắt đầu một task thì đánh `- [~]` cho task đó; test pass thì đổi thành
  `- [x]` TRƯỚC khi bắt task sau. Cấm gom tick cuối turn. Ba trạng thái: `[ ]` chưa làm ·
  `[~]` đang làm · `[x]` xong.
- **Điểm `(nN)` chỉ là metadata.** Giữ nguyên khi tick, không chấm lại giữa chừng — task
  `(n9)` tick y hệt task `(n1)`.
- **Red → green.** Mỗi task: chạy/viết check trước (phải fail), rồi code, rồi chạy lại đến pass.
- **Không placeholder.** Thiếu thông tin ở giai đoạn này nghĩa là phân tích hụt — nêu ra, đừng stub.
- **Chờ agent phụ (nếu harness hỗ trợ) thì chờ hết**, hoặc đặt trigger tự tiếp tục. Không
  kết thúc turn khi nó đang chạy.

## Phần A — Implement (phase `implement`)

1. Đọc `implement_mode` từ state và làm đúng theo:
   - `main`: tự làm tuần tự trong hội thoại này, theo đúng thứ tự task trong plan.
   - `subagent`: harness hỗ trợ gọi agent phụ thì giao mỗi phase độc lập cho một agent,
     mỗi agent một git worktree; merge về và kiểm tra merge, dọn worktree thừa. Harness
     không hỗ trợ → không có mode này, quay lại `main` và nói rõ với user.
   Mode là thứ USER đã nói lúc duyệt. Thiếu mode, hoặc bạn nghĩ mode khác hợp hơn → **DỪNG và HỎI**.

2. Vòng lặp mỗi task:
   1. Báo 1 dòng: đang bắt đầu task nào, và đánh `- [~]` cho task đó trong plan.
   2. Task có khối `Dùng:` trỏ tới năng lực nào đó → dùng đúng năng lực đó, làm đúng
      trường `Để`, không lan sang việc ghi ở `Không dùng cho`. Không có khối → bỏ qua.
   3. Đỏ: chạy check của task → xác nhận fail (hoặc viết test fail trước).
   4. Code: thay đổi nhỏ nhất mà đủ thoả task. Bám style code sẵn có.
   5. Xanh: chạy lại đến khi pass, chỉ chạy **test của module** đang sửa — full suite
      để dành, chạy đúng 1 lần ở QC. Dán kết quả thật, cấm tuyên bố xong khi chưa chạy.
   6. Đổi `- [~]` thành `- [x]` cho task đó trong plan NGAY.

3. Xong hết task: chạy full suite ĐÚNG MỘT LẦN. Rồi tự đóng sổ turn (không có lệnh gộp
   như `tdq_finish.py` ở bản portable này, làm tay 3 việc):
   - Lint nếu harness có công cụ lint tài liệu tương đương (`doc_lint.py` — chỉ khi đã
     copy sang project đích), không có thì bỏ qua bước này.
   - Append entry vào `docs/workinglog/<hôm nay>.md` (task xong, file đổi, kết quả test).
   - `python3 scripts/tdq_state.py set phase=qc`

Xong khi: mọi task trong plan đã tick `[x]` và test suite xanh.
Bước kế tiếp: Phần B ngay bên dưới, cùng turn.

## Phần B — QC (phase `qc`)

4. **Số hạng mục QC = số dòng Definition of Done**, cộng đúng một lần chạy full suite.
   Mỗi dòng DoD một phép kiểm bằng lệnh; không thêm hạng mục ngoài DoD.
   Chi tiết: [references/qc.md](references/qc.md). Việc lớn hoặc rủi ro cao mà harness
   hỗ trợ gọi agent phụ → gọi thêm một agent cho một lượt kiểm độc lập.

5. Ghi `docs/tdq/qc/<slug>.md`: từng hạng mục DoD → PASS/FAIL kèm **bằng chứng**
   (lệnh + output thật). Không khẳng định thứ chưa chạy.

6. FAIL → quay lại plan, **không cần duyệt lại**: thêm task fix vào plan dưới
   `## QC vòng N — fix` theo đúng khuôn `- [ ] **QCn.1** <việc> — Test: <check>`, làm
   theo luật Phần A (red→green, tick ngay). Rồi chạy lại hạng mục đã FAIL cộng hạng mục
   mà bản fix có thể làm hỏng, cộng full suite. Trần 3 vòng; vượt trần thì DỪNG, báo user.
   Chỉ kéo user vào giữa chừng khi bản fix đòi đổi phạm vi.

Xong khi: mọi hạng mục QC PASS và có bằng chứng trong file qc.
Bước kế tiếp: `python3 scripts/tdq_state.py set phase=report`.

## Phần C — Report (phase `report`)

7. Viết `docs/tdq/reports/<slug>.md` — tiếng Việt, KHÔNG giới hạn cứng số dòng, khuyến
   nghị ~10-20 dòng; dài hơn thì nói rõ vì sao thay vì cắt bớt sự thật. Dồn mỗi mục
   thành MỘT dòng, ngăn ý bằng dấu `·`, số liệu lấy nguyên từ output thật. Khuôn:
   ```markdown
   # REPORT — <tên việc> (`<slug>` · lane <lane> · mode <mode> · <n> task tick đủ)

   Đã làm: <P1 …> · <P2 …> · <P3 …>
   Kết quả: <chỉ số> <trước> → <sau> · <chỉ số> <trước> → <sau>
   Kiểm: <lệnh test + kết quả> · <lint> · QC <PASS x/y mục DoD, defect đã sửa>
   Đầu ra: <đường dẫn file chính> · Backup: <đường dẫn, nếu có sửa ngoài repo>
   Giới hạn: <cái gì chưa làm, vì sao, ảnh hưởng gì>
   Git: <chưa commit / commit nào đã tạo>
   ```
   Mọi con số lấy từ output thật, không ước lượng. Dòng "Giới hạn" không được bỏ trống
   khi còn việc dang dở — nói thật, không giấu.

8. Đóng sổ: tick nốt checkbox còn sót, đổi header plan thành HOÀN THÀNH, append entry
   vào working log tóm tắt report (không có lệnh gộp, làm tay).

9. Trình report trong chat (nguyên văn hoặc tóm tắt ngắn gọn + đường dẫn).

10. **Hỏi user có commit không** — bắt buộc, không tự commit thành quả cuối (ngoại lệ duy
    nhất: commit gỡ chặn giữa build theo Luật cứng, phải liệt kê trong report). User đồng ý
    → message mô tả thay đổi, KHÔNG chứa "generated with …" hay trailer AI; branch theo quy ước.

Xong khi: report đã ghi và user đã được hỏi về commit.
Bước kế tiếp: `python3 scripts/tdq_state.py set phase=idle`
(hoặc `reset` nếu user muốn xoá hẳn để sang request mới).
