# TDQ Workflow — bản portable (agent nào cũng chạy được)

**Harness này KHÔNG có hook.** Không ai nhắc bạn cả. Vì vậy:

> Đầu mỗi turn tự chạy `python3 scripts/tdq_state.py next` và làm đúng việc nó in ra.

Đó là luật số một. Mọi luật còn lại nằm dưới đây. Output cho user: **tiếng Việt**.

## Pipeline

```
Intake ──► Analysis ──► Spec ──► Plan ──► Implement ──► QC ──► Report
 (lane?)   (interview)  [DUYỆT]  [DUYỆT]  (1 turn,      (loop   (~10-20 dòng)
                                           tick ngay)    plan)
Chế độ nhanh: Analysis (+search/interview khi cần) ──► mini-plan gộp 1 file ──►
            [DUYỆT] ──► ghi log ──► Implement ──► QC (mặc định BẬT)
```

Duyệt spec → viết plan NGAY trong cùng turn. Duyệt plan (kèm mode) → build NGAY trong
cùng turn. Không bắt user nhắn thêm câu nào chỉ để đi tiếp.

Chi tiết từng phase (đọc file tương ứng với phase đang ở, đừng đọc hết một lượt):

| Phase | File |
|---|---|
| `no_state`, `analyze`, chế độ nhanh | [workflow/01-intake.md](workflow/01-intake.md) |
| `spec` | [workflow/02-spec.md](workflow/02-spec.md) |
| `plan` | [workflow/03-plan.md](workflow/03-plan.md) |
| `implement`, `qc`, `report` | [workflow/04-build.md](workflow/04-build.md) |

Bảng phase đầy đủ (vào khi / việc duy nhất / lệnh chuyển tiếp / xong khi / cấm):
[workflow/phases.md](workflow/phases.md) — file **tự sinh** từ hằng `PHASE_TABLE` trong
`scripts/tdq_state.py`, không sửa tay. Sinh lại: `python3 scripts/tdq_state.py phases-doc > workflow/phases.md`.

## 1. Giao thức một turn (bắt buộc, đúng thứ tự)

1. Đầu turn: chạy `python3 scripts/tdq_state.py next`.
2. Làm đúng việc của phase đó — không làm trước việc của phase sau.
3. Repo có thay đổi → append entry vào `docs/workinglog/<hôm nay>.md` **trong cùng turn**.
4. Cuối turn: chạy lệnh chuyển tiếp của phase (nếu điều kiện "Xong khi" đã đạt).

Xong khi: phase mới đã ghi vào state và working log đã có entry của turn này.
Bước kế tiếp: file phase tương ứng trong bảng trên.

## 2. State

- Đọc/ghi state **chỉ** qua CLI: `python3 scripts/tdq_state.py <next|get|set|approve|init|reset>`.
  Cấm sửa tay `docs/tdq/state.json` và `docs/tdq/STATE.md` (mirror tự sinh, chỉ để đọc).
- `next` = câu trả lời cho "giờ làm gì". `get <key>` = đọc một trường.
- `init <slug> <quick|full>` = **mở request mới**, xoá sạch mọi trường cũ (lane, phase,
  spec/plan file, mọi dấu duyệt, implement_mode), lưu slug cũ vào `previous_request`.
  Chạy cho MỌI yêu cầu mới ngay khi user chốt lane. Request cũ còn dở → nói rõ
  slug/phase sẽ mất rồi **hỏi user trước**.
- `reset` chỉ khi user đóng hẳn request. Muốn thử nghiệm workflow thì chạy vào project
  rác: đặt `TDQ_PROJECT_DIR=/tmp/...` ngay trên chính lệnh đó (cấm dùng `||` fallback).
- Mọi trục trặc của state chỉ là cảnh báo (exit 0). Exit 2 = gõ sai cú pháp lệnh.
- Project root xác định theo thứ tự: `TDQ_PROJECT_DIR` → git root → thư mục gần nhất có
  `docs/tdq/state.json` → thư mục hiện tại.

## 3. Ghi nhận duyệt

User duyệt bằng chat thường — không có cú pháp bắt buộc, không có gate chặn user.
Dấu hiệu duyệt, phản ví dụ, và lệnh phải chạy: [workflow/references/approval.md](workflow/references/approval.md).

Ba luật không được phá:
- Mơ hồ → **HỎI**, tuyệt đối không suy diễn là đã duyệt.
- Duyệt spec ≠ duyệt plan. Chỉ ghi đúng thứ user nêu tên.
- Mode thực thi luôn do USER chọn (`main` | `subagent`). Đề xuất thì được, tự chốt thì không.

## 4. Cây tài liệu

```
docs/tdq/
  state.json + STATE.md   # state ghi qua CLI; STATE.md là mirror tự sinh, chỉ đọc
  brief/<slug>.md     research/<slug>.md   spec/<slug>.md
  plan/<slug>.md      qc/<slug>.md         reports/<slug>.md
docs/workinglog/YYYY-MM-DD.md
```
Slug: `YYYY-MM-DD-<kebab ≤5 từ, không dấu>`. Một request dùng chung một slug ở mọi thư
mục. `brief/` gộp yêu cầu + kiến thức + hỏi đáp vào một file, đúng 3 mục:
`## Nguyên văn`, `## Hiểu & kiến thức`, `## Hỏi đáp`.

## 5. Working log

- Turn nào đổi repo → append vào CUỐI `docs/workinglog/<hôm nay>.md` (chưa có thì tạo).
- Nội dung: giờ/ngữ cảnh, file đã đổi, lý do, test đã chạy (hoặc lý do chưa chạy).
- Turn chỉ đọc/phân tích → không ghi. Turn chỉ sửa working log → không ghi thêm entry.

## 6. Git

- Tên branch/commit/worktree **không** bắt đầu bằng `claude`, `antigravity`, `gemini`, `codex`.
- Commit message **không** chứa "generated with <AI>", "được tạo cùng/với/bởi <AI>",
  hay trailer Co-Authored-By của AI.
- **Không** commit/push khi user chưa yêu cầu.

## 7. Research

- Search web: dùng đúng công cụ search của harness. Có nhiều nguồn thì đi nguồn chính
  trước, chỉ đổi sang nguồn dự phòng khi nguồn chính lỗi — không gọi song song.
- Mọi khẳng định phải có nguồn hoặc căn cứ nêu rõ. Không bịa.
- Không đưa API key vào câu trả lời, log, lệnh shell hay prompt.

## 8. Chất lượng

- Soul — luật gốc đứng trên mọi luật: chất lượng > runtime > context cost. Hạ chất
  lượng để đổi lấy tốc độ hay token là sai. Hai luật đá nhau → luật phục vụ tầng cao
  hơn thắng. Bản gốc: `skills/tdq-conventions/references/soul.md` (repo TDQWorkflow).
- Luật một lượt — tầng runtime, KHÔNG phải luật tiết kiệm token. Sắp phát từ 2 tool call
  trở lên mà không call nào cần kết quả của call kia → phát hết trong CÙNG MỘT LƯỢT.
  Lệnh shell độc lập nối bằng `&&`. Cấm gộp ở 4 ca: bước đỏ → bước xanh của TDD; đang
  khoanh vùng lỗi; lệnh phá hủy hoặc khó đảo; lệnh sau cần kết quả lệnh trước.
  Thông tin còn đủ trong context thì đừng đọc lại file. Nhưng đây là luật MỀM. BẮT BUỘC
  đọc lại khi: context đã bị nén; lần trước chỉ đọc một phần; file có thể đã đổi; sắp sửa
  chính file đó; nhớ không chắc. Nghi ngờ thì đọc lại — chất lượng đứng trên runtime.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật. Thiếu
  thông tin → hỏi user, đừng đoán.
- Sản phẩm build ra luôn có log service bật mặc định (timestamp, đủ chi tiết debug, tắt
  được qua config). Việc thuần tài liệu (không tạo runtime) thì ghi rõ "Log: BỎ — vì...".
- Mỗi task trong plan có test riêng; task pass là tick `[x]` NGAY, không gom cuối turn.

## Không có ở bản portable này

So với plugin Claude Code, bản này **không có**: hook nhắc `[TDQ:*]`, và `tdq_finish.py`
gộp 4 việc trong 1 lệnh — bạn tự làm từng bước: lint, append log, set phase. Cũng không
có sub-agent chuyên biệt (`tdq-implementer`/`tdq-qc-tester`/`tdq-reviewer`). Mode
`subagent` vẫn dùng được khi harness hỗ trợ gọi agent phụ, tự áp luật tương đương.
Mọi phần khác của workflow (lane, gate duyệt, QC, DoD) giữ nguyên hành vi.
