# QUICK — stop_gate nêu đúng cổng duyệt của lane

**Ngày:** 2026-08-18 · Brief: ../brief/2026-08-18-2305-stop-gate-keu-oan-lane.md · Lane: quick
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
**Trạng thái:** HOÀN THÀNH
**Ước tính sẽ dùng skill:** không có

## Phạm vi
- Trong: một hàm chung `cong_dang_cho(state)` trong `tdq_state`, trả cổng chưa duyệt ĐÚNG theo lane
- Trong: `stop_gate` và `edit_gate` cùng gọi hàm đó — hôm nay mỗi bên tự chọn cổng theo cách riêng
- Trong: test khoá hình dạng cho cả hai hook
- NGOÀI: các mã nhắc khác của `stop_gate` (TICK, LOG, GIT) và điểm chặn working log
- Giữ nguyên khi lane rỗng/lạ: rơi về đúng danh sách cũ `spec → plan → quick`, không im lặng
- BỎ vòng scope: lỗi thuần nội bộ, một dòng code, không có ẩn số ngoài

## Task
- [x] **T1** Hàm `cong_dang_cho(state)`: lane quick → `quick` nếu chưa duyệt; lane full → `spec` rồi `plan`; lane rỗng/lạ → như cũ; duyệt đủ → `None` — Chạm: `scripts/tdq_state.py`, `tests/test_state.py` — Test: `python3 -m pytest tests/test_state.py -q -k cong` xanh, có ca lane quick đã duyệt trả `None`
- [x] **T2** `stop_gate` gọi `cong_dang_cho` thay danh sách cứng — Chạm: `hooks/scripts/stop_gate.py`, `tests/test_stop_gate.py` — Test: `python3 -m pytest tests/test_stop_gate.py -q` xanh, có ca lane quick + `quick_approved=True` thì IM LẶNG, và ca lane quick chưa duyệt thì nhắc chữ `quick`
- [x] **T3** `edit_gate` gọi cùng hàm đó, bỏ nhánh if/elif tự chọn cổng — Chạm: `hooks/scripts/edit_gate.py`, `tests/test_edit_gate.py` — Test: `python3 -m pytest tests/test_edit_gate.py -q` xanh, hành vi nhắc không đổi
- [x] **T4** Đồng bộ portable + chạy suite — Chạm: `portable_claude/`, `portable_codex/` — Test: `python3 scripts/build_portable.py` rồi `python3 -m pytest -q` 0 đỏ

## Definition of Done
- Lane quick đã duyệt (`quick_approved = true`) thì `stop_gate` KHÔNG còn in `[TDQ:APPROVE] spec …`
- Lane quick chưa duyệt vẫn bị nhắc, và câu nhắc gọi đúng tên cổng `quick`
- Lane full giữ nguyên hành vi cũ: chưa duyệt spec thì nhắc `spec`, duyệt spec rồi thì nhắc `plan`
- Luật chọn cổng chỉ nằm ở MỘT chỗ: `grep -c "\"spec\", \"plan\", \"quick\"" hooks/scripts/*.py` ra 0
- `python3 -m pytest -q` 0 đỏ và portable ổn định qua hai lần build

## QC
- Q1 test từng task: PASS — T1 `pytest tests/test_state.py -k cong` → 7 passed · T2 `pytest tests/test_stop_gate.py` → 49 passed · T3 `pytest tests/test_edit_gate.py` → 32 passed · T4 `pytest -q` → 999 passed
- Q2 DoD "Lane quick đã duyệt thì stop_gate KHÔNG còn in `[TDQ:APPROVE] spec …`": PASS — repo thử ở scratchpad, `approve quick` rồi gọi hook Stop → output rỗng
- Q3 DoD "Lane quick chưa duyệt vẫn bị nhắc, gọi đúng tên cổng `quick`": PASS — cùng repo thử, trước khi duyệt → `[TDQ:APPROVE] quick vẫn chưa được ghi nhận duyệt …`
- Q4 DoD "Lane full giữ nguyên hành vi cũ": PASS — `test_lane_full_giu_nguyen_thu_tu_spec_roi_plan` (duyệt spec rồi thì nhắc `plan`) và 2 ca full sẵn có đều xanh
- Q5 DoD "Luật chọn cổng chỉ nằm ở MỘT chỗ": PASS — `grep -c '"spec", "plan", "quick"' hooks/scripts/*.py` ra 0 ở cả 6 file
- Q6 DoD "pytest 0 đỏ, portable ổn định": PASS — 999 passed, 1239 subtests; hai lần `build_portable.py` cho cùng một `git status --short`

Ghi chú: `edit_gate` khi lane rỗng/lạ trước đây im lặng, nay nhắc cổng `spec` — đổi có chủ ý
cho khớp `stop_gate`, đã khoá bằng `test_lane_hong_van_nhac_thay_vi_im_lang`.
Lệch luật lane: quick cho phép giao agent con từ 3 task tách rời, nhưng phiên này có chỉ thị
cấm gọi Agent tool nên T1–T4 làm inline ở main.
