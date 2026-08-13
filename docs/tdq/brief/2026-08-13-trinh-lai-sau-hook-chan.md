# Brief — Trình bày lại full chat sau khi bị hook chặn

Ngày: 2026-08-13 · Lane: (chờ user chọn)

## Nguyên văn

> hiện tại vẫn còn issue này hãy mở request xử lí triệt để, có thể là nếu như bị hook
> chặn thì sau hook hãy trình bày lại full chat hoặc cách nào khả thi tối ưu hơn

Kèm ảnh chụp màn hình phiên trước, cho thấy:

- Turn mở request `doi-dong-nang-luc` in ra câu hỏi chọn pipeline **đầy đủ** (2–3 dòng
  tóm tắt việc + khối option A/B + khối giải thích nghĩa 2 pipeline).
- `stop_gate.py` chặn với `[TDQ:LOG]` vì working log chưa append.
- Turn chạy tiếp `tdq_finish.py`, rồi in đoạn text **mới, ngắn**:
  `✓ [TDQ:LOG] Đã ghi working log…` + `Đang chờ bạn chọn pipeline … trả lời "A" hoặc "B"`.
- Focus mode chỉ hiện **message text cuối cùng** → toàn bộ câu hỏi đầy đủ bị ẩn
  (`7 messages hidden (/focus to show)`). User chỉ còn thấy chuỗi "A" hoặc "B" trơ trọi,
  không biết A/B nghĩa là gì.

## Hiểu đầu tiên

- **Mục tiêu**: sau khi bị bất kỳ hook nào chặn, nội dung user-facing (câu hỏi/tóm tắt/
  `➤ Duyệt:`) phải xuất hiện **nguyên vẹn** ở message cuối turn, vì focus mode chỉ hiện
  message cuối.
- **Phạm vi đoán**: quy ước trong `skills/tdq-conventions/SKILL.md` (và có thể cả câu
  `reason` của `stop_gate.py`, để chính lời chặn tự ra lệnh "in lại full").
- **Khác gì request `fix-cau-hoi-focus-mode` trước**: lần trước fix ở hướng *phòng ngừa*
  (gọi `tdq_finish.py` trước khi in chat, để không bị chặn). Lần này fix ở hướng *chữa
  cháy*: đã bị chặn rồi thì phải in lại. Hai hướng bổ sung nhau, không thay thế.

## Hiểu & kiến thức

### Năng lực dùng được

Phân vân → DÙNG. Kiểm kê ngày 2026-08-13: bảng `skill_inventory.py` trên đĩa, cộng skill
built-in trong context. Không xoá bảng này kể cả khi không có dòng DÙNG nào.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-conventions, tdq-intake, tdq-spec, tdq-plan, tdq-build, tdq-status | plugin:tdq-workflow | NỀN | chính workflow đang chạy |
| Đã xét toàn bộ skill còn lại trong kiểm kê | user/plugin/built-in | KHÔNG | khác lĩnh vực — việc này sửa quy ước vận hành + hook nội bộ TDQ |

### Đọc code — cơ chế thật

- `hooks/scripts/stop_gate.py` là hook **Stop** duy nhất chặn: in
  `{"decision": "block", "reason": "[TDQ:LOG] …"}` (dòng 139-144) và `[TDQ:TICK]`
  (dòng 159-165). Stop chạy **sau** khi model đã in xong đoạn text cuối turn.
- `hooks/scripts/edit_gate.py` và `bash_gate.py` chặn ở **PreToolUse** — chặn giữa turn,
  model vẫn còn cơ hội in đoạn text cuối sau đó. **Không** gây ẩn nội dung.
- Suy ra: lỗi ẩn nội dung **chỉ** phát sinh ở đường `stop_gate.py` block (và, tổng quát
  hơn, ở mọi tình huống turn còn chạy tiếp sau khi đã in khối user-facing).
- Focus mode của harness chỉ hiển thị **message text cuối cùng** của mỗi response. Bị
  chặn → model in thêm text mới → text cũ tụt xuống, bị gập vào `N messages hidden`.

### Vì sao fix trước chưa đủ

Request `2026-08-13-fix-cau-hoi-focus-mode` chỉ thêm luật **phòng ngừa** (gọi
`tdq_finish.py` trước khi in chat). Luật đó không có cơ chế máy ép buộc; ngay trong phiên
đó đã quên 2 lần và bị `stop_gate.py` chặn. Cần thêm lớp **chữa cháy**: đã bị chặn rồi
thì đoạn text cuối phải tự đủ nghĩa.

### Hướng giải pháp đang cân nhắc

| Hướng | Nội dung | Ưu | Nhược |
|---|---|---|---|
| V1 | Quy ước trong `tdq-conventions/SKILL.md`: bị chặn → in LẠI nguyên văn khối user-facing | rẻ, 1 file | không có máy ép |
| V2 | Sửa `reason` của `stop_gate.py` để chính lời chặn ra lệnh "in lại nguyên văn, cấm tóm tắt" | lệnh đến đúng lúc bị chặn, khó lơ | đụng hook, `reason` có trần 300 ký tự (`MAX_CHARS`) |
| V3 | V1 + V2 | phòng ngừa + chữa cháy + nhắc đúng lúc | phải sửa 2 file, cần cắt chữ cho vừa trần |

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Research web | BỎ | Thuần nội bộ: hành vi focus mode đã nêu trong system prompt, cơ chế hook đã đọc thẳng mã nguồn |
| Interview | XONG (1 vòng, 3 câu, user chọn 1A 2A 3A) | Không còn câu nào làm đổi kết quả |
| spec → plan → implement → report | CÓ | Khung bất biến |
| QC độc lập bằng agent `tdq-qc-tester` | BỎ | 2 file, kiểm bằng `doc_lint` + test đơn vị cho hook là đủ; QC ở main tự chạy được |
| Chia subagent lúc implement | BỎ | 2 file liên quan chặt nhau, chia ra tốn hơn làm thẳng |

## Hỏi đáp

### Vòng 1 — 2026-08-13 19:03 · user trả lời 19:04: **"1A 2A 3A"**

1. Chọn hướng nào?
- A (đề xuất): V3 — vừa ghi quy ước ở `tdq-conventions`, vừa sửa lời chặn của
  `stop_gate.py` để nó tự ra lệnh in lại
- B: V1 — chỉ ghi quy ước, không đụng hook
- C: V2 — chỉ sửa lời chặn của hook

2. Khi in lại thì in tới đâu?
- A (đề xuất): nguyên văn 100% khối user-facing (tóm tắt + câu hỏi + toàn bộ option +
  dòng `➤ Duyệt:`), đặt SAU dòng `✓ [TDQ:<MÃ>]`
- B: rút gọn — chỉ in lại phần câu hỏi + option, bỏ phần tóm tắt việc
- C: in lại nguyên văn nhưng đặt TRƯỚC dòng `✓ [TDQ:<MÃ>]`

3. Phạm vi luật mới rộng tới đâu?
- A (đề xuất): tổng quát — MỌI lần turn còn chạy tiếp sau khi đã in khối user-facing
  (hook chặn, tự phát hiện thiếu việc, lỗi tool) đều phải in lại nguyên văn
- B: hẹp — chỉ áp khi bị `stop_gate.py` chặn

**Chốt:** 1A = làm V3 (sửa cả quy ước lẫn hook). 2A = in lại nguyên văn 100%, đặt SAU
dòng `✓ [TDQ:<MÃ>]`. 3A = luật áp tổng quát cho mọi lần turn còn chạy tiếp sau khi đã in
khối user-facing, không riêng `stop_gate.py`.

Không còn câu hỏi nào làm đổi kết quả → đủ điều kiện sang phase `spec`.
