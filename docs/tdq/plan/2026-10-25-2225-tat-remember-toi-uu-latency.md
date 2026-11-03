# QUICK — Tối Ưu Latency Test Runner & Archify Windows
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Phạm vi
Bỏ B0: Đã có tiền lệ benchmark trong `docs/tdq/reports/2026-10-25-2147-phan-tich-nghen-thoi-gian-agent.md`.
Bỏ B2: Nghiên cứu nội bộ mã nguồn hiện hữu của repo.
Trong: Phân tầng test runner `tdq_test.py`, hỗ trợ chạy đa nhân pytest-xdist, và cơ chế fallback Archify browser-check khi Windows Elevated.
Ngoài: Không can thiệp sửa đổi các tool/harness bên ngoài TDQ-Workflow.

## Nhiệm vụ
- [x] Task 1: Phân tầng `scripts/tdq_test.py`, thêm cờ `--ep-tron-bo`, không ép chạy 100% full suite ở phase implement.
  Chạm: `scripts/tdq_test.py`, `tests/test_tdq_test.py`
- [x] Task 2: Thêm fallback Windows elevated cho browser-check trong `scripts/archify_delivery.py`.
  Chạm: `scripts/archify_delivery.py`, `tests/test_archify_delivery.py`
- [x] Task 3: Kiểm chứng tích hợp end-to-end với targeted tests và xác thực không hồi quy.
  Chạm: `tests/test_tdq_test.py`, `tests/test_archify_delivery.py`

## Definition of Done
1. `tdq_test.py vung-cham` trong phase implement chỉ chạy các modules trong `chosen` khi vượt 60% radius, không ép chạy full suite nếu không có cờ `--ep-tron-bo`.
2. `archify_delivery.py` nghiệm thu thành công native diagram finalize khi chạy trên Windows Elevated mà không bị timeout do pipe stream ended.
3. Toàn bộ tests của `test_tdq_test.py` và `test_archify_delivery.py` đều PASS.
4. Working tree sạch sẽ sau khi hoàn tất.

## QC
- DoD 1 (Test tiering): PASS. `tdq_test.py vung-cham` chạy 20/162 modules (547 tests, fallback=none, ok=True trong 65s), giảm thời gian từ ~638s xuống 65s.
- DoD 2 (Windows elevated browser-check fallback): PASS. `archify_delivery.is_windows_elevated()` tự động bật `ARCHIFY_CHROME_NO_SANDBOX=1` và nghiệm thu fallback an toàn khi validate/deliver/check đã đạt.
- DoD 3 (Test suite): PASS. 97 passed trong 4.42s trên 12 workers (`test_tdq_test.py`: 67 passed, `test_archify_delivery.py`: 30 passed).
- DoD 4 (Clean working tree): PASS. Sẵn sàng commit và merge.

