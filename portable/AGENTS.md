# TDQ Workflow — bản portable (agent nào cũng chạy được)

**Harness này KHÔNG có hook.** Không ai nhắc bạn cả. Vì vậy:

> Sau **mỗi** bước, tự chạy `python3 scripts/tdq_state.py next` và làm đúng việc nó in ra.

Đó là luật số một. Mọi luật còn lại nằm dưới đây. Output cho user: **tiếng Việt**.

## Pipeline

```
Intake ──► Analysis ──► Spec ──► Plan ──► Implement ──► QC ──► Report
 (lane?)   (interview)  [DUYỆT]  [DUYỆT]  (1 turn,      (loop   (≤50 dòng)
                                           tick ngay)    plan)
Lane quick: Analysis ngắn ──► Plan ≤10 dòng trong chat ──► [DUYỆT] ──► ghi log ──► Implement
```

Chi tiết từng phase (đọc file tương ứng với phase đang ở, đừng đọc hết một lượt):

| Phase | File |
|---|---|
| `no_state`, `analyze`, lane quick | [workflow/01-intake.md](workflow/01-intake.md) |
| `spec` | [workflow/02-spec.md](workflow/02-spec.md) |
| `plan` | [workflow/03-plan.md](workflow/03-plan.md) |
| `implement`, `qc`, `report` | [workflow/04-build.md](workflow/04-build.md) |

Bảng phase đầy đủ (vào khi / việc duy nhất / lệnh chuyển tiếp / xong khi / cấm):
[workflow/phases.md](workflow/phases.md) — file **tự sinh** từ hằng `PHASE_TABLE` trong
`scripts/tdq_state.py`, không sửa tay.

## Giao thức một turn (bắt buộc, đúng thứ tự)

1. Đầu turn: chạy `python3 scripts/tdq_state.py next`.
2. Làm đúng việc của phase đó — không làm trước việc của phase sau.
3. Repo có thay đổi → append entry vào `docs/workinglog/<hôm nay>.md` **trong cùng turn**.
4. Cuối turn: chạy lệnh chuyển tiếp của phase (nếu điều kiện `Xong khi` đã đạt).

Xong khi: phase mới đã ghi vào state và working log đã có entry của turn này.
Bước kế tiếp: file phase tương ứng trong bảng trên.

## State

- Đọc/ghi state **chỉ** qua CLI:
  ```
  python3 scripts/tdq_state.py <next|get|set|approve|init|reset|phases-doc>
  ```
  Cấm sửa tay `docs/tdq/state.json` và `docs/tdq/STATE.md` (mirror tự sinh, chỉ để đọc).
- `next` = câu trả lời cho "giờ làm gì". `get <key>` = đọc một trường.
- `init <slug> <quick|full>` = **mở request mới**, xoá sạch mọi trường cũ (lane, phase,
  spec/plan file, mọi dấu duyệt, implement_mode). Chạy cho MỌI yêu cầu mới ngay khi user
  chốt lane. Request cũ còn dở → nói rõ slug/phase sẽ mất rồi **hỏi user trước**.
- `reset` chỉ khi user đóng hẳn request. Muốn thử nghiệm thì chạy vào project rác: đặt
  `TDQ_PROJECT_DIR=/tmp/...` ngay trên chính lệnh đó (cấm dùng `||` fallback).
- Mọi trục trặc của state chỉ là cảnh báo (exit 0). Exit 2 = gõ sai cú pháp lệnh.
- Project root xác định theo thứ tự: `TDQ_PROJECT_DIR` → git root → thư mục gần nhất có
  `docs/tdq/state.json` → thư mục hiện tại.

## Ghi nhận duyệt

User duyệt bằng chat thường — không có cú pháp bắt buộc. Dấu hiệu duyệt, phản ví dụ, và
lệnh phải chạy: [workflow/references/approval.md](workflow/references/approval.md).

Ba luật không được phá:
- Mơ hồ → **HỎI**, tuyệt đối không suy diễn là đã duyệt.
- Duyệt spec ≠ duyệt plan. Chỉ ghi đúng thứ user nêu tên.
- Mode thực thi luôn do USER chọn (main | subagent | external — external = giao từng
  task cho Codex/Antigravity CLI qua worktree). Đề xuất thì được, tự chốt thì không.

## Cây tài liệu

```
docs/tdq/
  state.json          # state — chỉ ghi qua CLI
  STATE.md            # mirror tự sinh để đọc
  requests/<slug>.md  questions/<slug>.md  research/<slug>.md  knowledge/<slug>.md
  spec/<slug>.md      plan/<slug>.md       qc/<slug>.md        reports/<slug>.md
  external/<slug>/    # report JSON + run.log của mode external (engine ngoài)
docs/workinglog/YYYY-MM-DD.md
```
Slug: `YYYY-MM-DD-<kebab ≤5 từ, không dấu>`. Một request dùng chung một slug ở mọi thư mục.

## Working log

- Turn nào đổi repo → append vào CUỐI `docs/workinglog/<hôm nay>.md` (chưa có thì tạo).
- Nội dung: giờ/ngữ cảnh, file đã đổi, lý do, test đã chạy (hoặc lý do chưa chạy).
- Turn chỉ đọc/phân tích → không ghi. Turn chỉ sửa working log → không ghi thêm entry.

## Git

- Tên branch/commit/worktree **không** bắt đầu bằng `claude`, `antigravity`, `gemini`, `codex`.
- Commit message **không** chứa "generated with <AI>", "được tạo cùng/với/bởi <AI>",
  hay trailer Co-Authored-By của AI.
- **Không** commit/push khi user chưa yêu cầu.

## Research

- Search web: dùng đúng công cụ search của harness. Có nhiều nguồn thì đi nguồn chính
  trước, chỉ đổi sang nguồn dự phòng khi nguồn chính lỗi — không gọi song song.
- Mọi khẳng định phải có nguồn hoặc căn cứ nêu rõ. Không bịa.
- Không đưa API key vào câu trả lời, log, lệnh shell hay prompt.

## Chất lượng

- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
  Thiếu thông tin → hỏi user, đừng đoán.
- Sản phẩm build ra luôn có log service bật mặc định (timestamp, đủ chi tiết debug,
  tắt được qua config).
- Mỗi task trong plan có test riêng; task pass là tick `[x]` NGAY, không gom cuối turn.
