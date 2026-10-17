# QUICK — Kiểm thử cross-platform macOS và Linux cho TDQ Workflow v0.73.0

**Ngày:** 2026-10-18 · Brief: ../brief/2026-10-18-0056-kiem-thu-cross-platform.md · Lane: quick
**Trạng thái:** HOÀN THÀNH
**Ước tính sẽ dùng skill:** tdq-status, tdq-conventions

## Phạm vi
- Trong: SSH macOS (100.105.75.71) & Linux (100.102.92.43), pull/cập nhật TDQ Workflow v0.73.0, tạo example project thực tế, chạy smoke test / test suite.
- NGOÀI: Sửa đổi mã nguồn hệ thống của máy từ xa ngoài phạm vi plugin TDQ.

## Task
- [x] **T1** Kết nối SSH và cập nhật TDQ Workflow v0.73.0 trên macOS (100.105.75.71) — Test: git pull / check version 0.73.0 thành công.
- [x] **T2** Tạo example project và chạy test thực tế trên macOS — Test: pytest tests/test_tcas_ast.py test_harvest.py test_soul_rules.py pass trên macOS.
- [x] **T3** Kết nối SSH và cập nhật TDQ Workflow v0.73.0 trên Linux (100.102.92.43) — Test: git pull / check version 0.73.0 thành công.
- [x] **T4** Tạo example project và chạy test thực tế trên Linux — Test: pytest pass trên Linux.
- [x] **T5** Tổng hợp báo cáo tương thích cross-platform (Windows, macOS, Linux).

## Definition of Done
- SSH thành công tới macOS và Linux.
- TDQ Workflow v0.73.0 đồng bộ và test suite cốt lõi (TCAS AST, Governed Harvest, Soul Rules, Hooks) đều PASS trên cả macOS và Linux.
- Có báo cáo kết quả chi tiết từng môi trường.

## QC
- [x] QC 1: SSH macOS (100.105.75.71) & cập nhật v0.73.0 -> PASS (Darwin ARM64, commit 31859a7).
- [x] QC 2: Test suite cốt lõi trên macOS -> PASS (15 passed, 26 subtests passed trong 0.07s).
- [x] QC 3: Tạo example project trên macOS (/tmp/example_project_tdq_macos) -> PASS (tdq_state init/next, tdq_harvest chạy hoàn hảo).
- [x] QC 4: SSH Linux (100.102.92.43) & clone/cập nhật v0.73.0 -> PASS (Ubuntu x86_64, commit 31859a7).
- [x] QC 5: Test suite cốt lõi trên Linux -> PASS (15 passed, 26 subtests passed trong 0.18s).
- [x] QC 6: Tạo example project trên Linux (/tmp/example_project_tdq_linux) -> PASS (tdq_state init/next, tdq_harvest chạy hoàn hảo).
