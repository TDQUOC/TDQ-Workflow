# PLAN — Vá Lỗ Hổng Gate 3 Tầng

Ngày: 2026-11-08 · Spec: ../spec/2026-11-08-1207-va-lo-hong-edit-gate-3-tang.md (bản 1.1, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — ĐỀ XUẤT: 3 task nhỏ, T1 và T2 cùng sửa họ test hook + T3 chạm `tdq_state.py` dùng chung; briefing sub-agent tốn hơn tự làm. Người dùng chốt khi duyệt.
Trạng thái plan: HOÀN THÀNH.

## Quy tắc thi hành

- Spec §2/§6 đứng trên plan. Tick `[~]` trước khi sửa, `[x]` ngay khi test xanh. Test đỏ thật trước sửa, không fake red.
- Mỗi task chạy test vùng chạm; full fresh `tdq_test.py --workers 1 --fresh --reuse off` chỉ ở QC.
- Không commit/push cho tới khi hỏi ở cuối.

## Thiết kế Trước vs Sau

| Trước | Sau |
|---|---|
| `edit_gate`: còn cổng chờ → `remind` (allow), Edit chạy | → `block` (deny), Edit không chạy |
| `bash_gate`: không signal → im; signal lệch → `remind_force` (allow) | Có `turn_start` mà không signal `matched=True` → `block`; không `turn_start` → `remind_force` như cũ |
| `quick-lane.md` bước 2 + `PHASE_TABLE["quick_analyze"]` bảo `set phase=implement` trước duyệt | Giữ `analyze` tới khi `approve quick` (CLI tự đẩy `implement`) |

## P1 — Tầng hook

- [x] **T1** (e15m) `edit_gate.py`: nhánh `TDQ:APPROVE` đổi `remind` → `block`; thông điệp: cổng chờ · "trình rồi KẾT THÚC lượt, chờ user" · "không tự chạy approve"; giữ `goi_y_mode()` — Test: `python -m unittest tests.test_edit_gate tests.test_codex_edit_gate`
  - Chạm: `hooks/scripts/edit_gate.py`, `tests/test_edit_gate.py` → 4 test `assert_remind(..."[TDQ:APPROVE]"...)` đổi sang kỳ vọng deny; thêm test docs/** vẫn im và đã duyệt đủ thì không deny (LSP refs `cong_dang_cho`).
  - Dùng: Python unittest + `tdq_test.py`
  - Để: đỏ→xanh 4 test APPROVE trước khi sửa hook, rồi chạy vùng chạm.
  - Ra: `tests/test_edit_gate.py` xanh với kỳ vọng deny.
  - Kiểm: `python scripts/tdq_test.py vung-cham`
  - Không dùng cho: thay full fresh ở QC.
- [x] **T2** (e25m) `bash_gate.py`: `_check_signal_mismatch` → chuẩn hoá target (`nhanh|express`→`quick`; `approve plan` nhận signal `plan` hoặc `mode`); signal khớp → im; ngược lại có `turn_start` trong `rows` → `block`, không có → `remind_force`; log `_info` nguồn/target — Test: `python -m unittest tests.test_bash_gate tests.test_compliance_protocol`
  - Chạm: `hooks/scripts/bash_gate.py`, `tests/test_bash_gate.py` → 3 test `assert_remind` APPROVE đổi sang deny khi có `turn_start`; giữ `test_failopen_no_signal_row` (không `turn_start`); thêm test ca play3clone (có `turn_start`, không signal) và một-prompt-một-cổng (signal `spec` khớp, `approve plan` bị deny).
  - Cần: T1
  - Dùng: `Grep / Read / Edit`
  - Để: đọc `turn_rows`/`turn_start` có sẵn, sửa đúng hàm `_check_signal_mismatch`.
  - Ra: `hooks/scripts/bash_gate.py` chặn tự duyệt.
  - Kiểm: `python -m unittest tests.test_bash_gate`
  - Không dùng cho: đọc transcript JSONL.
  - Tiến độ: chặn khi có `turn_start` xong (5 test đỏ→xanh). Phát hiện thêm: `set phase=implement` của vòng fix QC (plan đã duyệt từ trước, không có signal) sẽ bị chặn nhầm → bỏ qua kiểm khi cổng đích đã duyệt; test vòng fix xanh. Vùng chạm 274 test OK.

## P2 — Tầng quy trình

- [x] **T3** (e15m) Bỏ `set phase=implement` trước duyệt: `quick-lane.md` bước 2 → "giữ phase analyze, sang bước 3"; `PHASE_TABLE["quick_analyze"]["cmd"]` → không còn `set phase=implement`; sinh lại `phases.md` bằng `phases-doc` — Test: `python -m unittest tests.test_phase_table tests.test_state_phase tests.test_quick_qc`
  - Chạm: `skills/tdq-intake/references/quick-lane.md`, `scripts/tdq_state.py`, `skills/tdq-conventions/references/phases.md` → hàng `quick_analyze` (LSP refs `phase_row`).
  - Cần: T2

## P3 — QC & report

- [x] **T4** (e20m) QC Q1–Q5: full fresh, lint, report MD + HTML 4 phần — Test: `python scripts/doc_lint.py docs/tdq/reports/2026-11-08-1207-va-lo-hong-edit-gate-3-tang.md`
  - Cần: T1, T2, T3
  - Dùng: `Archify`
  - Để: render report Trước/Sau theo kết quả test thật.
  - Ra: `docs/tdq/reports/2026-11-08-1207-va-lo-hong-edit-gate-3-tang.md` + `.html`, `docs/tdq/qc/2026-11-08-1207-va-lo-hong-edit-gate-3-tang.md`.
  - Kiểm: `python scripts/tdq_test.py --workers 1 --fresh --reuse off`
  - Không dùng cho: chứng nhận hành vi host không có hook UserPromptSubmit.

## QC vòng 1 — fix

Full fresh 4202 test: 4 đỏ, đều do thay đổi có chủ đích (result `docs/tdq/cache/test-runs/3df348232a8e68c3/d56a8e76f2b34798a4d0af8a6fd61c49/result.json`).

- [x] **F1** (e5m) `test_e2e_chain` full + quick: bước "trước duyệt sửa src vẫn chạy" đổi sang kỳ vọng deny — Test: `python -m unittest tests.test_e2e_chain`
  - Chạm: `tests/test_e2e_chain.py`
- [x] **F2** (e5m) Sinh lại chỉ mục dòng `quick-lane.md` — Test: `python -m unittest tests.test_doc_index`
  - Chạm: `skills/tdq-intake/references/quick-lane.md`
- [x] **F3** (e10m) Dựng lại số dòng `luat-hien-co.md` (lệch 19/329 > 5%) — Test: `python -m unittest tests.test_luat_skill`
  - Chạm: `docs/tdq/audit/luat-hien-co.md`

## Cụm song song & file nóng

- Một cụm tuần tự: T1→T2 cùng họ test hook và `TDQ:APPROVE`; T3 chạm `tdq_state.py` dùng chung mọi hook. Leader làm cả, không giao sub-agent.

## Px — Log & test bắt buộc

- Log `_info` khi `bash_gate` block (target, có/không `turn_start`). Test đỏ thật trước sửa; vùng chạm mỗi task; full fresh một lần ở QC. Working log `docs/workinglog/2026-11-08.md` mỗi mốc.

## Definition of Done

- [x] Q1 Edit ngoài `docs/` khi còn cổng chờ → deny; `docs/**` và đã duyệt đủ → không deny — `python -m unittest tests.test_edit_gate`
- [x] Q2 Ca play3clone (có `turn_start`, không signal) `approve spec` → deny; signal khớp → im; không `turn_start` → chỉ nhắc — `python -m unittest tests.test_bash_gate`
- [x] Q3 Signal `spec` khớp mà `approve plan` cùng prompt → deny — `python -m unittest tests.test_bash_gate`
- [x] Q4 Không còn `set phase=implement` trước duyệt quick; lint 0 lỗi — `python scripts/doc_lint.py skills/tdq-intake/references/quick-lane.md skills/tdq-conventions/references/phases.md`
- [x] Q5 Full fresh xanh; report MD + HTML đủ 4 phần — `python scripts/tdq_test.py --workers 1 --fresh --reuse off`

Ước tính 75 phút agent + thời gian full suite, không gồm chờ duyệt.
