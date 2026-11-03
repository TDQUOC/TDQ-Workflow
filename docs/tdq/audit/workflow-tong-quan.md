# Tổng quan workflow TDQ (bản 0.36.0)

Ngày: 2026-09-01 · Nguồn: đọc thẳng `scripts/tdq_state.py`, `hooks/`, `skills/`, `scripts/doc_lint.py`
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Tài liệu này mô tả workflow đúng như code đang chạy, sau khi pha sơ đồ mind map bị gỡ ở
bản 0.36.0. Bảng pha sinh máy nằm ở `python3 scripts/tdq_state.py phases-doc`; ở đây là
bản đọc cho người, kèm hai thứ bảng đó không nói: đường đi thật của một request và các
lớp kiểm tra.

## 1. Các pha hiện tại

8 pha hợp lệ trong `VALID_PHASES`: `idle`, `analyze`, `spec`, `plan`, `mode`, `implement`,
`qc`, `report`. `PHASE_ORDER` thêm hai mục không phải pha đặt được: `no_state` (chưa có
request nào) và `quick` (nhãn của cả lane nhanh).

| Pha | Vào khi | Việc duy nhất | Lệnh đi tiếp |
|---|---|---|---|
| `no_state` | Chưa có request | Hỏi user chọn lane, mở request | `tdq_state.py init <slug> <nhanh\|chuyen-sau>` |
| `analyze` | Request mở, lane chuyên sâu | Đọc code, research, interview đến hết mơ hồ | `set phase=spec` |
| `spec` | Phân tích xong | Viết spec, trình, DỪNG chờ duyệt | `approve spec --by "<nguyên văn>"` |
| `plan` | `spec_approved = true` | Viết plan kèm mode ĐỀ XUẤT, trình, DỪNG | `approve plan --by "<nguyên văn>"` |
| `mode` | Plan duyệt nhưng chưa chốt mode | Giải thích 2 mode, hỏi user | `approve plan --mode <main\|subagent>` |
| `implement` | Plan duyệt và mode đã chốt | Làm hết plan trong một turn, tick `[~]` → `[x]` | `set phase=qc` |
| `qc` | Implement xong | Chạy Definition of Done, ghi bằng chứng, sửa cái fail | `set phase=report` |
| `report` | QC PASS | Viết report ngắn rồi hỏi user về commit | `set phase=idle` |
| `idle` | Xong, hoặc chưa mở request | Chờ request mới | `init <slug> <lane>` |
| `quick` | `lane = quick` | Cả lane nhanh gói trong một pha | `approve quick [--no-qc] --by "..."` |

Pha `diagram` đã bị gỡ ngày 2026-09-01. State cũ mang `phase=diagram` tự nâng về `spec`
kèm cảnh báo; ba lệnh cũ (`approve diagram`, `diagram add`, `diagram list`) thoát khác 0
với thông điệp nói rõ pha đã gỡ.

## 2. Workflow xử lí một request thế nào

### 2.1 Mở request

Mọi prompt mới khi chưa có request nào mở (`active_request` rỗng hoặc `phase = idle`) đều
phải vào skill `tdq-intake`. Prompt đến giữa lúc request đang chạy thì thuộc về request
đó — không lồng request mới.

Trước khi mở, intake cân tầng `nhỏ`: sửa tại chỗ, không mở request, chỉ khi đủ CẢ 4 điều
kiện — hành vi sản phẩm không đổi (hoặc đúng một chỗ hiển nhiên), không thêm/xoá file
nguồn, không chạm hook/state/cổng duyệt, và xong trong một turn không có gì để user quyết.
Vỡ một điều kiện giữa chừng thì DỪNG và mở request bình thường.

Mở request gồm: ghi `docs/tdq/brief/<slug>.md` (slug `YYYY-MM-DD-HHMM-<kebab>`), chạy
`tdq_lsp.py kiem` kiểm 6 bậc lớp tìm kiếm, rồi HỎI user chọn lane. Chỉ user chọn lane.

### 2.2 Lane nhanh (`quick`)

Một pha, một file, một cổng duyệt. Chín bước: phân tích → viết mini spec/plan gộp vào
`docs/tdq/plan/<slug>.md` (≤ 40 dòng) → trình tóm tắt ≤ 10 dòng → DỪNG chờ duyệt →
`approve quick` → ghi working log TRƯỚC khi động code → implement trong một turn → QC theo
từng dòng DoD (bật mặc định) → vòng fix nếu FAIL (trần 3 vòng) → hỏi user về commit.

### 2.3 Lane chuyên sâu (`full`)

`analyze → spec → plan → mode → implement → qc → report → idle`. Ba cổng dừng chờ user:
duyệt spec, duyệt plan, chốt mode chạy. Quy tắc gộp gate: duyệt spec xong viết plan ngay
trong turn đó; duyệt plan xong hỏi mode ngay turn đó. Câu duyệt đã nói sẵn mode thì ghi cả
hai và vào thẳng build.

Ở `implement`, mode `main` chạy tuần tự trong hội thoại chính; mode `subagent` giao từng
task rời nhau cho `tdq-implementer` chạy song song trong worktree riêng, trần 4 nhánh.

### 2.4 Chỉ user duyệt

Duyệt bằng chat thường, và ghi vào state CHỈ qua `scripts/tdq_state.py` — cấm sửa
`docs/tdq/state.json` bằng tay. Câu chữ mơ hồ thì hỏi lại, cấm tự suy diễn là đã duyệt.

## 3. Các lớp kiểm tra

### 3.1 Hook — 5 script, lớp chặn cứng

| Hook | Bám vào | Chặn cứng hay chỉ nhắc |
|---|---|---|
| `session_start.py` | SessionStart | Nhắc: bơm luật TDQ và trạng thái request vào đầu phiên |
| `prompt_context.py` | UserPromptSubmit | Nhắc: chèn `[TDQ:NEXT]`, `[TDQ:APPROVE]` theo pha hiện tại |
| `edit_gate.py` | PreToolUse Edit/Write | CHẶN: pha `implement`/`qc` mà plan không có task nào `[~]` thì mọi sửa ngoài `docs/` và `tests/` bị từ chối |
| `bash_gate.py` | PreToolUse Bash | CHẶN/nhắc: chặn ghi thẳng `state.json`, nhắc `[TDQ:OUTPUT]` khi lệnh đổ nguyên nội dung vào context |
| `stop_gate.py` | Stop | CHẶN: `[TDQ:LOG]` khi repo đổi mà chưa ghi working log; `[TDQ:UNFINISHED]` khi plan còn task mở; `[TDQ:TICK]` khi turn sửa code mà checkbox không đổi |

`tests/**` được miễn ở `edit_gate` để viết được test đỏ trước. Lối thoát hợp lệ duy nhất
khi `[TDQ:UNFINISHED]` chặn là `tdq_state.py tam-hoan --ly-do "<lý do>"`, và lý do đó hiện
cho user thấy.

### 3.2 Cổng trong state — chặn cứng, thoát khác 0

- Vào `plan`: đòi `spec_approved = true` (`_chan_spec_chua_duyet`).
- Vào `qc`: đòi sổ worktree không còn dòng nào mở (`_chan_worktree_con_mo`).
- `set phase=<tên lạ>`: từ chối; riêng `diagram` báo rõ pha đã gỡ thay vì lỗi cú pháp.

### 3.3 doc_lint — 12 luật hình dạng tài liệu

`python3 scripts/doc_lint.py <đường dẫn>` — thoát 1 khi có vi phạm, 0 khi sạch, 2 khi sai
cú pháp. R1–R7 soi tài liệu chỉ dẫn trong `skills/` (đánh số bước liên tục, lệnh copy dán
được, có điều kiện dừng, không từ mơ hồ, trần 500 dòng…). R8–R12 soi sản phẩm: kiểm kê
năng lực trong spec, hình dạng file luật, ranh giới module, spec không chứa lệnh kiểm, và
file viết cho user phải bằng tiếng Việt. Thư mục trong `OUTPUT_DIRS` (`docs/tdq`,
`docs/workinglog`…) chỉ chịu ràng buộc hẹp, vì đó là bản ghi chứ không phải tài liệu chỉ dẫn.

### 3.4 Bộ test và QC

`python3 -m pytest tests/ -q` chạy toàn bộ. Mốc đỏ hiện tại là 101 fail — mọi request đối
chiếu với mốc này, số fail không được lớn hơn và không file mới nào được vào bảng lỗi.

QC lane chuyên sâu: agent độc lập `tdq-qc-tester` chạy lại từng dòng DoD, chỉ đọc và chạy
lệnh, không được sửa file, trả PASS/FAIL kèm bằng chứng thật. FAIL thì thêm task fix vào
plan, sửa, chạy lại — không cần duyệt lại. QC lane nhanh: một kiểm cho mỗi dòng DoD, bằng
chứng ghi thẳng vào mục `## QC` của chính file plan.

### 3.5 Kiểm bản phát hành

`python3 scripts/build_portable.py` sinh 3 bundle (`portable_claude`, `portable_codex`,
`antigravity_portable`); `python3 scripts/tdq_checkportable.py check --root <thư mục>` đối
chiếu từng file với manifest và in `CLEAN` khi khớp.

### 3.6 Cuối mỗi turn

`python3 scripts/tdq_finish.py --files <file> --log "<tóm tắt>"` làm một lượt: lint, ghi
working log, đo thời gian pha, và chạy `graphify extract . --code-only` khi có file code đổi.
