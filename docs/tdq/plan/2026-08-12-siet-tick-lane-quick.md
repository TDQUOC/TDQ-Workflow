# QUICK — Siết luật tick checkbox cho lane quick

Ngày: 2026-08-12 · Brief: ../brief/2026-08-12-siet-tick-lane-quick.md · Lane: quick
Trạng thái: CHỜ DUYỆT
Năng lực: không có

## Phạm vi
- Trong: dạy dấu `[~]` ở đường quick (`PHASE_TABLE["quick"]`, `quick-lane.md`,
  `tdq-intake/SKILL.md` Phần C bước 7); nâng `TDQ:TICK` trong `edit_gate.py` từ nhắc
  thành chặn (`permissionDecision: "deny"`), miễn trừ `tests/**`; test kèm theo.
- NGOÀI: `stop_gate.py` và lỗ hổng bulk-tick trong-một-turn; luật tick lane full
  (`tdq-build`); đổi khuôn plan lane full; bump phiên bản plugin.

## Task
- [x] **T1** Thêm hàm `block()` vào `hooks/scripts/_common.py` (PreToolUse deny, ghi
  `turn_log_append` kind `block`, KHÔNG dedupe — chặn phải lặp tới khi tick) — Test: `python3 -m pytest tests/test_edit_gate.py -q`
- [x] **T2** `edit_gate.py`: nhánh `TDQ:TICK` gọi `block()` thay `remind()`, bỏ qua khi
  `rel_target` nằm trong `tests/`; thông điệp deny có đường thoát (`set phase=idle` khi
  request đã đóng); sửa docstring "KHÔNG chặn" cho đúng — Test: `python3 -m pytest tests/test_edit_gate.py -q`
- [x] **T3** `tests/test_edit_gate.py`: đổi `TickRemindTest` sang kỳ vọng deny, thêm ca
  sửa `tests/foo.py` KHÔNG bị chặn, ca `[~]` và ca `all_done` vẫn qua — Test: `python3 -m pytest tests/test_edit_gate.py -q`
- [x] **T4** `scripts/tdq_state.py` PHASE_TABLE["quick"]: dòng implement thành "đánh
  `[~]` khi bắt đầu task, red→green, đổi `[x]` NGAY khi pass"; thêm `forbidden` cấm gom
  tick cuối turn — Test: `python3 -m pytest tests/test_phase_table.py tests/test_plan_tick.py tests/test_quick_qc.py -q`
- [x] **T5** `skills/tdq-intake/references/quick-lane.md`: khuôn mini-plan ghi 3 trạng
  thái checkbox, mục "Vòng fix" và bảng so sánh nhắc `[~]`; `tdq-intake/SKILL.md` Phần C
  bước 7 nói rõ tick từng task — Test: `python3 scripts/doc_lint.py`

## Definition of Done
- `python3 -m pytest tests/ -q` — toàn bộ test xanh.
- `python3 scripts/doc_lint.py` — không lỗi.
- `grep -n '\[~\]' skills/tdq-intake/references/quick-lane.md` — có kết quả.
- `grep -n '\[~\]' scripts/tdq_state.py | grep -n 'quick' -c` hoặc đọc PHASE_TABLE["quick"]
  — checklist quick có dấu `[~]`.
- Chạy tay `edit_gate.py` với state phase=implement, plan không có `[~]`, target
  `scripts/x.py` → JSON có `"permissionDecision": "deny"`; target `tests/x.py` → không deny.

## QC vòng 1 — fix
- [x] **QC1.1** `tests/test_compliance_protocol.py` T2.11 cấm chuỗi `"deny"` trong mọi
  file `hooks/` + `scripts/` — bất biến này có trước quyết định chặn của user. Thu hẹp:
  cấm `transcript_path` như cũ, `"deny"` chỉ được phép trong `hooks/scripts/_common.py`
  (hàm `block()`) — Test: `python3 -m pytest tests/test_compliance_protocol.py -q`

## QC vòng 2 — fix
- [x] **QC2.1** `trim()` cắt thông điệp deny ở 200 ký tự làm mất chính lệnh thoát
  (`…→ td…`). Rút gọn 3 dòng của TDQ:TICK để lệnh `set phase=idle` hiện đủ — Test: chạy tay
  `edit_gate.py` với plan chưa tick → chuỗi `set phase=idle` xuất hiện nguyên vẹn

## QC
- Q1 test từng task (T1–T5, QC1.1, QC2.1): PASS — `python3 -m pytest tests/test_edit_gate.py tests/test_phase_table.py tests/test_plan_tick.py tests/test_quick_qc.py tests/test_compliance_protocol.py -q` → `70 passed`
- Q2 DoD "toàn bộ test xanh": PASS — `python3 -m pytest tests/ -q` → `479 passed, 140 subtests passed in 31.60s`
- Q3 DoD "doc_lint không lỗi": PASS — `doc_lint.py` trên `quick-lane.md`, `tdq-intake/SKILL.md`, plan → không in lỗi
- Q4 DoD "`[~]` trong quick-lane.md": PASS — `grep -c '\[~\]'` → `7`
- Q5 DoD "checklist quick có `[~]`": PASS — `PHASE_TABLE['quick']` có 1 dòng chứa `[~]`; `forbidden` chứa "gom tick"
- Q6 DoD "chạy tay edit_gate": PASS — `scripts/x.py` → `"permissionDecision": "deny"` kèm lệnh thoát `set phase=idle` nguyên vẹn; `tests/x.py` → rỗng; `docs/ghi.md` → rỗng
- Q7 phụ (ngoài DoD, do user hỏi): PASS — project không có `docs/tdq/state.json` → hook in rỗng, không chặn
