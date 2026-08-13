# Brief — Rà soát luật tick ở chế độ chuyên sâu và cơ chế stop_gate

Ngày: 2026-08-13

## Nguyên văn

> A — mở request mới để rà lại luật tick ở **chế độ chuyên sâu** và cơ chế `stop_gate`

Đây là phần còn lại của loạt việc bắt đầu từ nghi vấn của user ở phiên trước ("task ở
lane nhanh không được tick ngay khi xong, gom tick vào cuối"). Phần chế độ nhanh đã làm
xong và commit: `023eeaf` (thêm trạng thái `[~]`), `63203b3`/`4ce02ea` (hàng rào tick
chuyển từ nhắc sang chặn ở `edit_gate.py`).

### Cách hiểu đầu tiên

- Mục tiêu: xác định cùng một lỗ hổng "gom tick cuối turn" còn tồn tại ở chế độ **chuyên
  sâu** hay không, và `stop_gate` có đủ sức bắt hay không; nếu có lỗ thì bịt.
- Nghi vấn đã thấy khi đọc code, cần kiểm chứng:
  1. `hooks/scripts/stop_gate.py:152-165` chỉ so `plan_sha` đầu turn với cuối turn —
     **đổi bất kỳ là qua**. Tick 5 task một lượt ngay trước khi kết thúc turn vẫn lọt.
  2. Điều kiện `tick["sha"] == snap["plan_sha"]` khiến hàng rào im lặng khi plan có đổi
     vì lý do khác (sửa chữ, thêm mục QC) dù checkbox đứng yên.
  3. `edit_gate.py:97-105` chặn khi *không có* `[~]`, nhưng không chặn ca ngược lại:
     nhiều task cùng mang `[~]` — thứ mà `PHASE_TABLE` liệt vào mục `forbidden`.
  4. Chế độ chuyên sâu chạy nhiều turn và có thể chạy qua subagent
     (`tdq-implementer`) — cần xác định hook có áp lên subagent hay không.
- Phạm vi đoán: `hooks/scripts/stop_gate.py`, `hooks/scripts/edit_gate.py`,
  `scripts/tdq_state.py` (`plan_tick_state`, `turn_snapshot`, `PHASE_TABLE`),
  `skills/tdq-build/SKILL.md`, `tests/test_stop_gate.py`, `tests/test_plan_tick.py`.
- Chỗ chưa rõ: có muốn siết tới mức "mỗi turn phải có ít nhất một task đổi trạng thái"
  hay chỉ vá các ca lọt rõ ràng.

## Hiểu & kiến thức

### Năng lực dùng được

Chạy `python3 scripts/skill_inventory.py` — toàn bộ skill liệt kê ra đều thuộc mảng
Unity/Figma/Canva/Adobe/… không skill nào áp cho việc sửa hook Python + tài liệu markdown
nội bộ. **Không dùng skill nào ngoài built-in.**

### Ba lỗ hổng đã xác nhận (đọc code, không suy đoán)

- **A — "một `[~]` đứng yên xuyên suốt".** `hooks/scripts/edit_gate.py:97-100` chỉ kiểm
  tra tồn tại ÍT NHẤT MỘT task `[~]` (biến `has_doing`), không kiểm tra đúng task đang
  code. `hooks/scripts/stop_gate.py:152-165` chỉ đòi `plan_sha` cuối turn KHÁC đầu turn
  (đổi bất kỳ), không đòi đổi đúng nhịp. → agent có thể tick T1 một lần, giữ nguyên khi
  code ngầm T1–T5, rồi tick loạt cuối turn — vẫn qua cả hai hàng rào.
- **B — thiếu hàng rào cho "nhiều task cùng `[~]`".** `PHASE_TABLE["quick"]["forbidden"]`
  và `["full"]["forbidden"]` ở `scripts/tdq_state.py:582,653` liệt việc này là cấm, nhưng
  không dòng code nào đếm `dang` (số task `[~]`) và chặn khi `dang > 1`. Thuần văn bản.
- **C — subagent mode không có hàng rào thật (nặng nhất, khớp hiện tượng user quan sát).**
  `skills/tdq-build/SKILL.md` phần A bước 1 giao CẢ MỘT NHÓM task cho một agent
  `tdq-implementer` (một worktree riêng). `agents/tdq-implementer.md:16` cấm subagent tự
  tick nếu plan nằm ngoài worktree của nó — chỉ báo cáo, "main agent tick ngay khi nhận
  báo cáo". Nhưng nền tảng Agent không hỗ trợ báo cáo giữa chừng — subagent chỉ trả ĐÚNG
  MỘT báo cáo cuối cùng sau khi xong hết phần được giao → main agent tick một loạt N task
  cùng lúc lúc nhận báo cáo. Đây là nguồn gốc thật của hiện tượng "trống rồi bung hết" mà
  user thấy khi dùng mode subagent.

### Quyết định đã chốt (user chọn A cho cả 4 câu hỏi)

1. Vá cả 3 lỗ hổng A, B, C trong request này.
2. Vá C: đổi luật giao việc subagent — mỗi lần gọi `tdq-implementer` chỉ giao ĐÚNG 1
   task (không giao cả nhóm); main agent tick `[x]` ngay sau khi agent đó trả kết quả,
   trước khi gọi agent cho task tiếp theo. Đánh đổi: nhiều lượt gọi agent hơn (chậm hơn),
   nhưng tick bám sát tiến độ thật — đúng tinh thần "tick ngay" vốn đã là luật cứng của
   `tdq-build/SKILL.md`.
3. Vá A: thêm bộ đếm "số lần sửa file mã nguồn kể từ lần checkbox đổi gần nhất" vào sổ
   turn (`docs/tdq/.tdq-turn.jsonl`); vượt ngưỡng (đề xuất 3 lần sửa mà plan chưa tick
   thêm) → `edit_gate` chặn tiếp tới khi tick. Ngưỡng 3 chọn vì khớp trần "vòng fix" đã
   dùng ở nơi khác trong hệ thống — nếu quá chặt (task nhỏ, nhiều sửa nhỏ trong 1 task)
   thì tăng ngưỡng ở lượt QC sau.
4. Vá B: thêm điều kiện chặn trong `edit_gate` — đếm `dang` (task mang `[~]`) > 1 thì
   chặn, buộc đóng task cũ (`[x]`) trước khi mở task mới.

### Phương án đã loại

- Vá C bằng cách đọc log riêng của subagent giữa chừng (phương án B ở câu 2) — bị loại vì
  phức tạp hơn, cần cơ chế đọc file agent con ghi ra mà không chờ nó xong; chưa rõ nền
  tảng có hỗ trợ đáng tin cậy. User chọn A (giao từng task một) — đơn giản, dùng đúng cơ
  chế Agent tool sẵn có, không cần hạ tầng mới.
- Không vá gì (câu 1 phương án C) — bị loại, user muốn vá thật.

### Lộ trình

| Bước/phase | CÓ/BỎ | Vì sao |
|---|---|---|
| Phân tích (đã xong) | CÓ | Đã đọc đủ code, xác nhận 3 lỗ hổng, chốt cách vá — bắt buộc. |
| Research ngoài | BỎ | Thuần nội bộ (hook Python + tài liệu markdown), không ẩn số bên ngoài. |
| Spec | CÓ | Đổi hành vi hook (đụng gate chặn) + đổi luật giao việc subagent — cần văn bản duyệt trước khi code, không phải "sửa hiển nhiên". |
| Plan | CÓ | Nhiều file đổi (2 hook, `tdq_state.py`, `tdq-build/SKILL.md`, `tdq-implementer.md`, test) — cần task rời có test riêng. |
| Mode thực thi | main | Các thay đổi liên đới chặt (đổi hook A/B phải khớp test cùng lúc; đổi luật C phải khớp cả skill+agent doc) — chia subagent dễ lệch, việc nhỏ đủ làm tuần tự. |
| QC độc lập bằng agent `tdq-qc-tester` | BỎ | Việc không lớn/không rủi ro cao theo tiêu chí ở `tdq-build/references/qc.md`; QC bám DoD trong plan là đủ. |
| Report | CÓ | Bắt buộc theo khung TDQ chuyên sâu. |

## Hỏi đáp

1. Ưu tiên vá lỗ nào trong turn này?
   - A (đề xuất): vá cả 3 — cùng một mạch lỗi "tick không phản ánh tiến độ thật".
   - B: chỉ vá C (subagent).
   - C: chỉ dừng ở báo cáo, không vá gì thêm.
   User chọn: **A** — vá cả 3. (2026-08-13 14:18)

2. Vá lỗ hổng C bằng cách nào?
   - A (đề xuất): mỗi agent `tdq-implementer` chỉ nhận đúng 1 task/lần gọi; main agent
     tick ngay sau mỗi lần agent trả kết quả.
   - B: giữ giao theo nhóm, subagent ghi log riêng theo từng task, main agent đọc log
     giữa chừng để tick.
   User chọn: **A** — giao từng task một. (2026-08-13 14:18)

3. Vá lỗ hổng A bằng cách nào?
   - A (đề xuất): đếm số lần sửa code kể từ lần tick gần nhất, vượt ngưỡng thì chặn tiếp.
   - B: không vá.
   User chọn: **A**. (2026-08-13 14:18)

4. Vá lỗ hổng B bằng cách nào?
   - A (đề xuất): chặn trong `edit_gate` khi có > 1 task cùng mang `[~]`.
   - B: giữ nguyên chỉ ở tài liệu.
   User chọn: **A**. (2026-08-13 14:18)
