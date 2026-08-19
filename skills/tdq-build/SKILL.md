---
name: tdq-build
description: Thực thi trọn plan TDQ đã duyệt trong một turn, chạy QC bám DoD, viết report rồi hỏi về commit. Dùng khi plan chế độ chuyên sâu vừa duyệt.
---

# TDQ Build — Implement → QC → Report

Nạp [tdq-conventions](../tdq-conventions/SKILL.md). Yêu cầu `plan_approved = true`.
Skill này lo ba phase: `implement` → `qc` → `report`.

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
  `[~]` đang làm · `[x]` xong. Dấu `[~]` là thứ duy nhất cho biết đang đứng ở đâu khi
  người ngoài (status line, user, agent khác) nhìn vào file plan giữa chừng.
- **Ước tính `(eNm)` chỉ là metadata.** Task có thể mang số phút Claude tự ước tính để
  thực thi ngay sau mã task (`- [ ] **T1.1** (e12m) việc — Test: ...`). ETA cả plan = tổng
  `eNm` các task chưa xong. Giữ nguyên khi tick, không chấm lại giữa chừng, và nó KHÔNG
  đổi luật tick ở trên — task `(e60m)` tick y hệt task `(e5m)`. Task không có ước tính
  cũng hợp lệ.
- **Red → green.** Mỗi task: chạy/viết check trước (phải fail), rồi code, rồi chạy lại đến pass.
- **Rule ngôn ngữ.** Sắp viết/sửa file mã nguồn → mở
  [references/rules/index.md](references/rules/index.md), tra đuôi file, nạp `chung.md`
  + đúng MỘT file ngôn ngữ. Cấm nạp cả bộ khi chỉ sửa một ngôn ngữ.
- **Không placeholder.** Thiếu thông tin ở giai đoạn này nghĩa là phân tích hụt — nêu ra, đừng stub.
- **Chờ subagent thì chờ hết**, hoặc đặt trigger tự tiếp tục. Không kết thúc turn khi nó đang chạy.

## Phần A — Implement (phase `implement`)

1. Đọc `implement_mode` từ state và làm đúng theo:
   - `main` (nhãn user thấy: "làm trực tiếp (inline implement)"): tự làm HẾT trong hội
     thoại này, nhưng theo đúng thứ tự cụm của plan và vẫn ghi lý do giữ cho từng task.
     Doctrine leader áp cho mọi mode: [references/team-mode.md](references/team-mode.md).
   - `subagent` (nhãn user thấy: "giao trợ lý (sub-agent implement)"): bạn là LEADER của
     một đội. **Bước 0 — trước khi gõ dòng code đầu tiên: phân công CẢ plan**
     (`python3 scripts/tdq_team.py phan-cong` rồi `kiem-ke`). Sau đó lặp từng đợt.
     `cum` lấy đợt kế tiếp; `mo <task>` mở nhánh + worktree cho từng task.
     Gọi `tdq-implementer` cho MỌI task của đợt trong MỘT response — nhiều lệnh Task
     trong một response nghĩa là chúng chạy đồng thời. Đánh `[>]` cho các task vừa giao.
     Nhận báo cáo thì `kiem` rồi `hop`, tick `[x]` NGAY, `don`, rồi quay lại `cum`.
     Mặc định là GIAO. Chỉ được giữ task lại khi khớp đúng một nhóm trong tập lý do
     đóng (bảng tra ở `team-mode.md`); bịa nhóm ngoài tập đó thì `kiem-ke` exit khác 0.
     Trong lúc đợt đang chạy,
     leader làm các task `tu_lam` của cùng đợt.
     Luật đầy đủ (bảng tra quyết định, khuôn prompt giao việc, ví dụ ĐÚNG/SAI, tự kiểm):
     [references/team-mode.md](references/team-mode.md) — **BẮT BUỘC mở đọc trước khi
     phân công; cấm làm theo trí nhớ.**
   Mode là thứ USER đã nói lúc duyệt. Thiếu mode, hoặc bạn nghĩ mode khác hợp hơn → **DỪNG và HỎI**.

2. Vòng lặp mỗi task (mode `subagent`: mỗi vòng ứng với đúng 1 lần gọi `tdq-implementer`):
   1. Báo 1 dòng: đang bắt đầu task nào, và đánh `- [~]` cho task đó trong plan.
      Mode `subagent`: task giao cho agent con mang dấu `- [>]` (được nhiều task cùng lúc);
      `- [~]` chỉ dành cho task LEADER tự làm và vẫn chỉ được đúng một.
   2. Task có khối `Dùng:` → NẠP skill đó ngay (theo trường `Nạp`), làm đúng trường `Để`,
      không lan sang việc ghi ở `Không dùng cho`. Không có khối → bỏ qua bước này.
   3. Đỏ: chạy check của task → xác nhận fail (hoặc viết test fail trước).
   4. Code: thay đổi nhỏ nhất đủ thoả task, bám style sẵn có. **Tìm rồi mới tạo:**
      sắp tạo file/class/hàm/hằng MỚI → một lượt `graphify query "<tên>"` hoặc grep tên
      + 2 đồng nghĩa; thấy thứ gần giống vẫn tạo → ghi vào task trong plan
      `Tạo mới thay vì dùng <đường dẫn> vì <lý do>`. Không tìm mà tạo = lỗi dù test xanh.
   5. Xanh: chạy lại đến khi pass, chỉ chạy **test của module** đang sửa — full suite
      để dành, chạy đúng 1 lần ở QC. Dán kết quả thật, cấm tuyên bố xong khi chưa chạy.
   6. Đổi `- [~]` thành `- [x]` cho task đó trong plan NGAY — mode `subagent` thì main
      agent tick ngay khi nhận báo cáo của agent con VÀ `hop` xong, không đợi các task khác.
      (nhắc lại có chủ ý — bản gốc ở mục `## Luật cứng` cùng file này.)

3. Xong hết task: chạy full suite ĐÚNG MỘT LẦN, rồi đóng sổ turn bằng MỘT lệnh
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_finish.py" --files <file .md vừa sửa> --log "<task xong, file đổi, kết quả test>" --phase qc`
   — lint đúng file, append working log, set phase, graphify: 4 việc trong 1 call.

Xong khi: mọi task trong plan đã tick `[x]` và test suite xanh.
Bước kế tiếp: lệnh `tdq_finish.py … --phase qc` ở mục 3 (đã set phase luôn).

## Phần B — QC (phase `qc`)

Ba bước thi hành — từ đếm hạng mục theo DoD tới vòng fix khi FAIL — nằm ở
[references/qc.md](references/qc.md) mục `## Ba bước thi hành`. **BẮT BUỘC mở file đó và
đọc hết ba bước trước khi chạy hạng mục đầu tiên; cấm làm theo trí nhớ.** Cùng file đó có
luôn khuôn file qc và luật trần 3 vòng fix.

Xong khi: mọi hạng mục QC PASS và có bằng chứng trong file qc.
Bước kế tiếp: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=report`.

## Phần C — Report (phase `report`)

Bốn bước thi hành — từ viết report tới hỏi user có commit không — nằm ở
[references/report-template.md](references/report-template.md) mục `## Bốn bước thi hành`.
**BẮT BUỘC mở file đó và đọc hết bốn bước trước khi viết report; cấm làm theo trí nhớ.**
Cùng file đó có luôn khuôn report và khối hỏi commit nguyên văn.

Xong khi: report đã ghi và user đã được hỏi về commit.
Bước kế tiếp: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=idle`
(hoặc `reset` nếu user muốn xoá hẳn để sang request mới).
