# MINI-PLAN — Tự động cập nhật (auto-update) plugin tdq-workflow trong Claude Code
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Phạm vi
Bỏ B0: Đã có tiền lệ chỉnh sửa setup và session_start trong các request trước.
Bỏ B2: Lệnh CLI Claude Code đã được kiểm chứng hoạt động trực tiếp.
Trong: Nâng cấp auto-update plugin trong `scripts/tdq_setup.py`, hook `session_start.py`, và unit test.
Ngoài: Không can thiệp vào các plugin khác ngoài `tdq-workflow`.

## Nhiệm vụ
- [x] Task 1: Nâng cấp `scripts/tdq_setup.py` hỗ trợ auto-update từ marketplace/remote và repo nguồn (thêm hàm check remote, CLI flag `--update-plugin`, chống downgrade version stamp).
  Chạm: `scripts/tdq_setup.py`
- [x] Task 2: Cập nhật `hooks/scripts/session_start.py` tích hợp kiểm tra update ngầm định kỳ (detached throttle) và phát hiện version nguồn mới.
  Chạm: `hooks/scripts/session_start.py`
- [x] Task 3: Bổ sung unit tests kiểm chứng cơ chế auto-update, throttle mốc thời gian và CLI runner trong `tests/test_auto_update_setup.py`.
  Chạm: `tests/test_auto_update_setup.py`

## Định nghĩa hoàn thành (DoD)
1. `python -m unittest tests/test_auto_update_setup.py` đạt 100% PASS (0 failure, 0 error).
2. `python scripts/tdq_setup.py --kiem-archify` hoặc dry-run hook hoạt động bình thường, không gây lỗi cú pháp hay suy thoái.
3. Chạy `python -m unittest tests/test_mcp_first_auto_setup.py` đạt PASS.
4. Working tree sạch sẽ sau khi hoàn tất, không bị ghi đè ngược version stamp `docs/tdq/.tdq-phat-hanh.json`.

## QC
- DoD 1: PASS — 11/11 tests in `tests/test_auto_update_setup.py` đạt 100% PASS (0.163s).
- DoD 2: PASS — `python scripts/tdq_setup.py --kiem-archify` in ra "archify · ĐẠT (Node.js v24.21.0 (>= 18) · Archify tại C:\Users\admin\Documents\archify\archify\bin\archify.mjs)" và dry-run hook `hooks/scripts/session_start.py` chạy thành công.
- DoD 3: PASS — 6/6 tests in `tests/test_mcp_first_auto_setup.py` đạt 100% PASS.
- DoD 4: PASS — `docs/tdq/.tdq-phat-hanh.json` giữ vững version 0.82.0, không bị downgrade.
Phán quyết QC: ĐẠT TOÀN DIỆN (4/4 DoD).
