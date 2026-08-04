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
4. Cuối turn có đổi repo: chạy ĐÚNG MỘT lệnh
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_finish.py" --files <file vừa sửa> --log "<tóm tắt>" --phase <phase mới>`
   — lint đúng file → append working log → set phase → graphify. **Cấm Read lại** file
   working log rồi tự append: lệnh này đã append sẵn.

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
- Mode thực thi luôn do USER chọn (main | subagent | external — external = giao từng
  task cho engine ngoài codex/agy qua worktree). Đề xuất thì được, tự chốt thì không.

## 5. Cây tài liệu

```
docs/tdq/
  state.json + STATE.md   # state ghi qua CLI; STATE.md là mirror tự sinh, chỉ đọc
  requests/<slug>.md  questions/<slug>.md  research/<slug>.md  knowledge/<slug>.md
  spec/<slug>.md      plan/<slug>.md       qc/<slug>.md        reports/<slug>.md
  external/<slug>/    # mode external: gói task, report JSON từng task, run.log
docs/workinglog/YYYY-MM-DD.md
```
Slug: `YYYY-MM-DD-<kebab ≤5 từ, không dấu>`. Một request dùng chung một slug ở mọi thư mục.

## 6. Working log

- Turn nào đổi repo → `tdq_finish.py --log` append vào CUỐI `docs/workinglog/<hôm nay>.md`:
  giờ/ngữ cảnh, file đã đổi, lý do, test đã chạy (hoặc lý do chưa chạy).
- Turn chỉ đọc/phân tích → không ghi. Turn chỉ sửa working log → không ghi thêm entry.

## 7. Git

- Tên branch/commit/worktree **không** bắt đầu bằng `claude`, `antigravity`, `gemini`, `codex`.
- Commit message **không** chứa "generated with <AI>", "được tạo cùng/với/bởi <AI>",
  hay trailer Co-Authored-By của AI.
- **Không** commit/push khi user chưa yêu cầu.

## 8. Research

- Search web: `tavily-primary` trước, luôn luôn; lỗi kết nối/xác thực/timeout/quota/tool
  mới gọi `tavily-backup` đúng một lần. `WebSearch` chỉ sau khi cả hai hỏng VÀ user duyệt.
- Mẫu dùng nâng cao: [references/tavily.md](references/tavily.md).
- Mọi khẳng định phải có nguồn hoặc căn cứ nêu rõ. Không bịa.
- Không đưa API key vào câu trả lời, log, lệnh shell hay prompt.

## 9. Sub-agent

- Chọn `model` vừa đủ cho task (tham số `model` của Agent tool đè frontmatter); `effort`
  cố định theo vai trong frontmatter.
- `description` mỗi lần gọi Agent theo dạng `<model>-<effort>_ <mô tả>` (vd
  `sonnet-low_ research doc`) — nhìn tên là biết model và effort đang chạy.
- Không đổi `model` hay `effort` giữa chừng một phase build; muốn đổi thì đổi từ phase sau.
- Bảng mặc định theo vai + luật override: [references/subagent-tuning.md](references/subagent-tuning.md).

## 10. Tiết kiệm context (bắt buộc)

Mỗi tool call = 1 API call = model đọc lại TOÀN BỘ context: output `n` ký tự tốn
`n/4 × số API call còn lại` — **carry-cost**. Đo: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/token_audit.py" --sessions 2 --top 8`.

- **Gộp tool call.** Biết trước 2–5 tool call độc lập (Bash, Read, Grep) → phát hết
  trong CÙNG MỘT LƯỢT; nhiều lệnh Bash độc lập thì gộp bằng `&&`. Tách khi cần khoanh vùng lỗi.
- **Lint đúng file.** Chạy `doc_lint.py` trên ĐÚNG file vừa sửa, cấm truyền cả thư mục
  (`docs/tdq`): lint thư mục in ~8.000 ký tự lỗi của file cũ, không liên quan.
- **CLI im lặng.** `tdq_state.py init|set|reset` mặc định in 1 dòng; chỉ thêm `--json`
  khi thật sự cần soi state. `next --brief` thay cho `next` trừ khi cần checklist đầy đủ.
- **Đọc vừa đủ.** File trên 200 dòng: `grep -n` định vị rồi Read theo `offset`/`limit`.
  Cấm `cat` (dùng Read), cấm `grep -A5 -B5` khi `-c`/`-l` đã đủ trả lời.
- **Việc nặng giao subagent.** Research web và đọc ≥4 file giao agent riêng — agent có
  context window riêng, chỉ trả digest về hội thoại chính.

## 11. Chất lượng

- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
  Thiếu thông tin → hỏi user, đừng đoán.
- Sản phẩm build ra luôn có log service bật mặc định (timestamp, đủ chi tiết debug, tắt được qua config).
- Mỗi task trong plan có test riêng; task pass là tick `[x]` NGAY, không gom cuối turn.
