# QUICK — Sửa Hook Session Start Tránh Bơm Toàn Bộ Luật Khi Idle

**Ngày:** 2026-10-25 · Brief: ../brief/2026-10-25-2340-sua-hook-session-start.md · Lane: quick
**Trạng thái:** ĐÃ DUYỆT
**Ước tính sẽ dùng skill:** không có

## Phạm vi
- Bỏ scope round: sửa lỗi tại 1 vị trí mã nguồn, không phân nhánh phạm vi.
- Bỏ B0: hook session_start đã có tiền lệ triển khai trong docs/tdq/report/.
- Bỏ B2: không phụ thuộc thư viện hay công nghệ ngoài repo.
- Trong: sửa `hooks/scripts/session_start.py`; cập nhật test `tests/test_log_kenh_luat.py`.
- NGOÀI: không sửa các hook khác (`subagent_start.py`, `prompt_context.py`).

## Task
- [x] **T1** Sửa điều kiện nạp luật trong `hooks/scripts/session_start.py` thành `nap_day_du = (pha == "implement")`.
  Chạm: `hooks/scripts/session_start.py`
  Test: `python -m unittest discover -s tests -p "test_log_kenh_luat.py"`
- [x] **T2** Thêm unit test SessionStart khi không có active_request chỉ xuất 1 dòng pointer và so_dong=1.
  Chạm: `tests/test_log_kenh_luat.py`
  Test: `python -m unittest discover -s tests -p "test_log_kenh_luat.py"`

## Definition of Done
- Test log kênh luật pass: `python -m unittest discover -s tests -p "test_log_kenh_luat.py"`
- Test token budget pass: `python -m unittest discover -s tests -p "test_token_budget.py"`
- SessionStart chạy khi không có active_request chỉ in 1 dòng pointer, không bơm thân luật.

## QC
- Q1 test từng task: PASS — `python -m unittest discover -s tests -p "test_log_kenh_luat.py"` → Ran 12 tests in 4.983s, OK
- Q2 DoD "Test log kênh luật pass": PASS — `python -m unittest discover -s tests -p "test_log_kenh_luat.py"` → 12/12 test ĐẠT
- Q3 DoD "Test token budget pass": PASS — `python -m unittest discover -s tests -p "test_token_budget.py"` → Ran 8 tests in 2.514s, OK
- Q4 DoD "SessionStart chạy khi không có active_request chỉ in 1 dòng pointer, không bơm thân luật": PASS — kiểm tra môi trường tạm không có active_request chỉ ra 1 dòng pointer `[TDQ:GON]... full ladder loads during phase implement`, không có dòng thân luật.
- Q5 Smoke & Runtime (mức ultra): PASS — test cả 2 kịch bản (idle/no-request và implement), kịch bản implement vẫn bơm đầy đủ 65 dòng luật, kịch bản idle chỉ xuất 1 dòng pointer.
- Q6 QC độc lập (`tdq-qc-tester`): PASS — subagent `tdq-qc-tester` kiểm tra độc lập git diff, chạy toàn bộ test và đối soát biên, kết luận: `VERDICT: PASS everything`.
