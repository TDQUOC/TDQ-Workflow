# PLAN — Đổi tên mode thực thi + phân tích lý do đề xuất

Ngày: 2026-08-14 · Spec: ../spec/2026-08-14-doi-ten-mode-implement.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — 12 task nhưng dính chuỗi: nhãn chuẩn định nghĩa ở `tdq_state.py` rồi 6 chỗ khác chỉ đi chép lại, và 4 task cùng sửa `scripts/tdq_state.py` (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này.
3. Giá trị chuẩn trong state và `--mode` giữ nguyên `main|subagent`. Chỉ lớp hiển thị và
   lớp nhận đầu vào được đổi.

## Phase 1 — Lõi nhãn trong `scripts/tdq_state.py`

- [x] **T1.1** (n2 e6m) Thêm `MODE_LABELS` (`main` → `làm trực tiếp (inline implement)`,
  `subagent` → `giao trợ lý (sub-agent implement)`) và hàm `mode_label(mode)` theo đúng
  mẫu `lane_label`: là lớp hiển thị nên mode lạ trả lại nguyên chuỗi, `None` trả rỗng —
  Test: `pytest tests/test_mode_phase.py -q` với test mới kiểm 2 nhãn + mode lạ + None.
- [x] **T1.2** (n3 e10m) Thêm `MODE_ALIASES` (`main|inline|inline-implement|
  inline implement` → `main`; `subagent|sub-agent|sub agent|sub-agent-implement|
  sub-agent implement` → `subagent`) và `normalize_mode(raw)`; dùng nó ở cả hai đường
  nhập: cờ `--mode <giá trị>` và dạng gõ tắt `approve plan <mode>` — Test:
  `pytest tests/test_mode_phase.py -q` với test `--mode inline` → `implement_mode=main`,
  `--mode subagent` → `subagent`, `--mode xyz` → thoát khác 0.
- [x] **T1.3** (n2 e6m) Sửa checklist phase `mode` trong `PHASE_GUIDE`: hai dòng nghĩa
  dùng nhãn mới, và thêm một dòng buộc trình đoạn phân tích lý do lấy từ plan — Test:
  `python3 scripts/tdq_state.py next` ở phase `mode` in ra cả `inline implement` lẫn
  `sub-agent implement`.

## Phase 2 — Lớp hook

- [x] **T2.1** (n2 e6m) `hooks/scripts/_common.py`: `APPROVE_HINTS["mode"]` dùng nhãn
  mới, giữ nguyên thứ tự "plan đề xuất {mode}" ở đầu chuỗi để không bị cắt cụt, và
  `{mode}` in ra nhãn chứ không in giá trị trần — Test: `pytest tests/test_context_hooks.py
  tests/test_prompt_context.py -q`.
- [x] **T2.2** (n3 e8m) `hooks/scripts/prompt_context.py`: mở rộng regex `MODE` nhận
  `inline`, `sub-agent`, `sub agent` cùng biến thể có chữ `implement`, giữ biên từ `\b` —
  Test: `pytest tests/test_prompt_context.py -q` với test 4 chuỗi hợp lệ cộng ít nhất một
  câu nhiễu không được nhận.
- [x] **T2.3** (n1 e3m) `hooks/scripts/edit_gate.py`: chuỗi gợi ý `--mode <main|subagent>`
  nêu thêm tên mới cho người đọc — Test: `pytest tests/test_edit_gate.py -q`.

## Phase 3 — Khuôn skill và tài liệu

- [x] **T3.1** (n3 e10m) `skills/tdq-plan/SKILL.md` bước 6: thay khuôn khối hỏi mode bằng
  bản dùng nhãn mới, hai option mỗi dòng, phần đề xuất ở A. Khuôn nguyên văn dời sang
  `skills/tdq-plan/references/mode-gate.md` vì SKILL.md có trần 100 dòng (doc_lint R6) —
  Test: `grep -c "inline implement" skills/tdq-plan/SKILL.md` > 0 và `doc_lint.py` exit 0.
- [x] **T3.2** (n3 e8m) Thêm vào cùng bước 6 luật viết đoạn phân tích: 1–3 dòng ngay dưới
  hai option, bắt buộc nêu 4 căn cứ lấy từ plan (số task, task phụ thuộc nối tiếp, số file
  bị nhiều task cùng đụng, có nhãn `(mcp)` không) cộng đúng một câu vì sao không chọn
  phương án còn lại — Test: `grep -c "căn cứ" skills/tdq-plan/SKILL.md` > 0 và doc_lint 0.
- [x] **T3.3** (n2 e6m) Nhãn mới vào `skills/tdq-plan/references/plan-template.md` (mục
  `## Dòng Mode thực thi`) và `skills/tdq-build/SKILL.md` Phần A — Test:
  `grep -l "inline implement"` liệt kê đủ 2 file, doc_lint 0.

## Phase 4 — Kiểm cuối

- [x] **T4.1** (n1 e3m) Log service còn nguyên sau khi sửa `tdq_state.py` và hook — Test:
  gọi `_warn` mặc định ra 1 dòng có timestamp, `TDQ_LOG=0` ra 0 dòng.
- [x] **T4.2** (n1 e5m) Full suite một lần cộng doc_lint mọi file `.md` đã sửa — Test:
  `python3 -m pytest tests/ -q` không có `failed`; `doc_lint.py` exit 0.

- [x] **T4.3** (n1 e4m) Ghi nhớ quy ước nhãn mode vào bộ nhớ dài hạn — Test:
  `search_memories("nhãn mode inline implement", project="TDQWorkflow")` trả về fact vừa ghi.
  - Dùng: `mem0-memory` (mcp)
  - Để: ghi đúng 1 fact ngắn "mode thực thi giữ giá trị chuẩn main|subagent, nhãn hiển
    thị là làm trực tiếp (inline implement) / giao trợ lý (sub-agent implement)", nạp
    skill TRƯỚC bước đỏ. Agent ngoài không có skill system: đọc
    `~/.claude/skills/mem0-memory/SKILL.md` rồi làm theo.
  - Ra: một memory trong project `TDQWorkflow`, nội dung như trên.
  - Kiểm: `search_memories` với truy vấn "nhãn mode inline implement" trả về đúng fact đó.
  - Không dùng cho: chép nội dung spec/plan hay log phiên làm việc vào mem0.

Tổng: 4 phase · 12 task · ước tính 75 phút.

## Definition of Done

Trỏ về §6 của spec, mỗi dòng một lệnh kiểm:

- Q1 `mode_label('main')` và `mode_label('subagent')` in đúng 2 nhãn Việt hoá.
- Q2 `approve plan --mode inline` rồi `get implement_mode` in `main`.
- Q3 `approve plan --mode subagent` rồi `get implement_mode` in `subagent`.
- Q4 `looks_like_approval` trả `True` cho `main`, `subagent`, `inline implement`, `sub-agent`.
- Q5 `python3 scripts/tdq_state.py next` ở phase `mode` chứa cả 2 nhãn mới.
- Q6 `grep -c "inline implement" skills/tdq-plan/SKILL.md` > 0 và grep luật phân tích > 0.
- Q7 `grep -l "inline implement" plan-template.md skills/tdq-build/SKILL.md` ra đủ 2 file.
- Q8 `_warn` mặc định in 1 dòng timestamp, `TDQ_LOG=0` in 0 dòng.
- Q9 `python3 -m pytest tests/ -q` không có `failed`, số test ≥ 536.
- Q10 `python3 scripts/doc_lint.py <các file .md đã sửa>` exit 0.

## QC vòng 1 — fix

- [x] **QC1.1** Khuôn mới bảo user nhắn "A"/"B" nhưng `looks_like_approval(..., "mode")`
  chỉ nhận tên mode → prompt "A" bị coi là không rõ. Nhận thêm chữ cái A/B ở cổng mode:
  A = mode plan đề xuất, B = mode còn lại. Đọc câu trả lời gom vào hàm
  `mode_from_answer(prompt, planned)`, chỉ dùng ở nhánh cổng `mode` (nhánh `plan` vẫn chỉ
  đọc tên mode, vì chữ "A" trong câu duyệt plan không có nghĩa mode) — Test: `pytest tests/test_prompt_context.py -q`
  với ca "A", "B", và ca nhiễu "Ai làm cũng được" không được nhận.
