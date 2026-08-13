---
name: tdq-conventions
description: Quy ước chung của TDQ workflow (một-turn, state, duyệt, mã nhắc của hook, git, working log, research). Được các skill tdq-* khác nạp, không gọi trực tiếp.
user-invocable: false
---

# TDQ Conventions

Luật dùng chung cho mọi phase. Skill khác trỏ về file này thay vì chép lại.
Mọi output cho user viết **tiếng Việt**.

## 1. Giao thức một turn (bắt buộc, làm đúng thứ tự)

1. Đầu turn: hook đã in `[TDQ:NEXT]` → dùng luôn nội dung đó, **không chạy lại**
   `tdq_state.py next`; chỉ chạy `next` khi trong ngữ cảnh chưa có dòng đó.
2. Làm đúng việc của phase đó — không làm trước việc của phase sau.
3. Thấy dòng `[TDQ:<MÃ>]` do hook chèn vào ngữ cảnh → **làm việc trong đó TRƯỚC**
   mọi việc khác, xong in `✓ [TDQ:<MÃ>] <đã làm gì>`. Danh sách mã:
   [references/reminder-codes.md](references/reminder-codes.md).
4. Cuối turn có đổi repo: **bắt buộc** chạy ĐÚNG MỘT lệnh
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_finish.py" --files <file vừa sửa> --log "<tóm tắt>" --phase <phase mới>`
   — lint đúng file → append working log → set phase → graphify. **Cấm Edit/Read rồi tự
   append tay** vào working log, kể cả khi bị `stop_gate.py` chặn (block nghĩa là "chưa gọi
   lệnh", không phải "gọi lệnh khác để né"). Lệnh này phải là **hành động cuối** của turn,
   chạy TRƯỚC đoạn chat kết thúc turn (tóm tắt/câu hỏi/`➤ Duyệt:`/báo lỗi vượt trần); sau
   khi in đoạn chat đó **không gọi thêm tool nào nữa**, để nó luôn là "final response" thật.
5. **Turn còn chạy tiếp sau khi đã in khối user-facing** (bị hook chặn, tự phát hiện sót
   việc, lỗi tool) → message cuối phải in **LẠI NGUYÊN VĂN 100%** khối đó. Gồm tóm tắt,
   câu hỏi, ĐỦ option, dòng `➤ Duyệt:`. Đặt NGAY SAU dòng `✓ [TDQ:<MÃ>]`. Lý do: focus mode
   chỉ hiện message cuối. Tóm tắt lại hay trỏ ngược ("xem câu hỏi ở trên") đều làm user
   mất sạch câu hỏi và option. Cấm rút gọn, cấm trỏ ngược.

Xong khi: phase mới đã ghi vào state và working log đã có entry của turn này.
Bước kế tiếp: theo cột "lệnh chuyển tiếp" trong [references/phases.md](references/phases.md).

## 2. Bảng phase

Bảng đầy đủ (vào khi / việc duy nhất / lệnh chuyển tiếp / xong khi / cấm):
[references/phases.md](references/phases.md) — file **tự sinh** từ hằng `PHASE_TABLE`
trong `scripts/tdq_state.py`. Không chép lệnh sang chỗ khác, không sửa tay file đó.

## 3. State

- Đọc/ghi state **chỉ** qua CLI: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" <next|get|set|approve|init|reset>`.
  Cấm sửa tay `docs/tdq/state.json` và `docs/tdq/STATE.md` (mirror tự sinh, chỉ để đọc).
- `next` = câu trả lời cho "giờ làm gì". `get <key>` = đọc một trường.
- `init <slug> <quick|full>` = **mở request mới**, xoá sạch mọi trường cũ (lane, phase,
  spec/plan file, mọi dấu duyệt, implement_mode), lưu slug cũ vào `previous_request`.
  Chạy cho MỌI yêu cầu mới khi user chốt lane; request cũ còn dở → nói rõ slug/phase sẽ mất rồi **hỏi user trước**.
- `reset` chỉ khi user đóng hẳn request. Muốn thử nghiệm workflow thì chạy vào project
  rác: đặt `TDQ_PROJECT_DIR=/tmp/...` ngay trên chính lệnh đó (cấm dùng `||` fallback).
- Mọi trục trặc của state chỉ là cảnh báo (exit 0). Exit 2 = gõ sai cú pháp lệnh.

## 4. Ghi nhận duyệt

User duyệt bằng chat thường — không có cú pháp bắt buộc, không có gate chặn user.
Dấu hiệu duyệt, phản ví dụ, và lệnh phải chạy: [references/approval.md](references/approval.md).

Ba luật không được phá:
- Mơ hồ → **HỎI**, tuyệt đối không suy diễn là đã duyệt.
- Duyệt spec ≠ duyệt plan. Chỉ ghi đúng thứ user nêu tên.
- Mode thực thi luôn do USER chọn (main | subagent). Đề xuất thì được, tự chốt thì không.

## 5. Cây tài liệu

```
docs/tdq/
  state.json + STATE.md   # state ghi qua CLI; STATE.md là mirror tự sinh, chỉ đọc
  brief/<slug>.md     research/<slug>.md   spec/<slug>.md
  plan/<slug>.md      qc/<slug>.md         reports/<slug>.md
docs/workinglog/YYYY-MM-DD.md
```
Slug: `YYYY-MM-DD-<kebab ≤5 từ, không dấu>`. Một request dùng chung một slug ở mọi thư mục.
`brief/` gộp yêu cầu + kiến thức + hỏi đáp vào một file, đúng 3 mục: `## Nguyên văn`,
`## Hiểu & kiến thức`, `## Hỏi đáp`.

## 6. Working log

- Turn nào đổi repo → `tdq_finish.py --log` append vào CUỐI `docs/workinglog/<hôm nay>.md`:
  giờ, file đổi, lý do, test đã chạy. Cách hook nhận biết: [reminder-codes.md](references/reminder-codes.md).
- Turn chỉ đọc/phân tích → không ghi. Turn chỉ sửa working log → không ghi thêm entry.
- **Ảnh user gửi kèm.** Turn có ảnh đính kèm VÀ phải ghi working log → copy ảnh vào
  `docs/workinglog/assets/` rồi chèn link vào chuỗi `--log`, TRƯỚC khi gọi `tdq_finish.py`.
  Đường dẫn, cách đánh số, luật đầy đủ: [references/worklog-images.md](references/worklog-images.md).

## 7. Git

- Tên branch/commit/worktree **không** bắt đầu bằng `claude`, `antigravity`, `gemini`, `codex`.
- Commit message **không** chứa "generated with <AI>", "được tạo cùng/với/bởi <AI>",
  hay trailer Co-Authored-By của AI.
- **Không** commit/push khi user chưa yêu cầu.

## 8. Research

- Search web: `tavily-primary` trước, luôn luôn. Failover và mẫu dùng nâng cao:
  [references/tavily.md](references/tavily.md).
- Mọi khẳng định phải có nguồn hoặc căn cứ nêu rõ. Không bịa.
- Không đưa API key vào câu trả lời, log, lệnh shell hay prompt.

## 9. Sub-agent

- `description` mỗi lần gọi Agent theo dạng `<model>-<effort>-<việc-kebab>` (vd
  `sonnet-low-research-doc`) — nhìn tên là biết model và effort đang chạy.
- Bảng model/effort mặc định theo vai + luật override:
  [references/subagent-tuning.md](references/subagent-tuning.md).

## 10. Tiết kiệm context (bắt buộc)

Mỗi tool call đọc lại toàn bộ context, nên output thừa tốn token ở MỌI lượt sau.
Luật gộp tool call, đọc vừa đủ, giao việc nặng cho subagent:
[references/context-budget.md](references/context-budget.md).

## 11. Chất lượng

- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
  Thiếu thông tin → hỏi user, đừng đoán.
- Sản phẩm build ra luôn có log service bật mặc định (timestamp, đủ chi tiết debug, tắt được qua config).
- Mỗi task trong plan có test riêng; task pass là tick `[x]` NGAY, không gom cuối turn.
