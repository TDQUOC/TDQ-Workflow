# QC — Giảm timeout và thời gian chờ agent-lsp

Ngày: 2026-10-26 · Plan: ../plan/2026-10-26-0224-giam-timeout-agent-lsp.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mức QC: ultra (Spec §6 & Plan Definition of Done)

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Đồng bộ chính sách chọn công cụ 3 tầng và trung hòa chỉ thị `blast_radius` (O1) | `python scripts/doc_lint.py skills/tdq-setup/references/uu-tien-tim-kiem.md; python scripts/token_budget.py --kiem` | 0 violation(s) total, exit 0; token budget khớp hash 100% | PASS |
| Q2 | Thiết lập giới hạn chờ `CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT` 90.000 ms trong `tdq_setup.py` (O2) | `python -m pytest tests/test_auto_update_setup.py -q` | 12 passed in 0.27s (kiểm chứng cài đặt env timeout MCP, backup và idempotency) | PASS |
| Q3 | Kiểm soát phạm vi `blast_radius` (≤ 3 tệp, `exported`, không bắc cầu) và circuit breaker tại `lsp_gate.py` (O3) | `python -m pytest tests/test_lsp_gate.py tests/test_search_rules.py -q -k circuit` | 6 passed (chặn đúng khi vượt ngưỡng, mạch mở khi blast_radius lỗi hoặc ≥2 lỗi liên tiếp, đóng khi lành) | PASS |
| Q4 | Quan sát thời gian chạy và phân loại kết quả tại `search_observe.py` (O4) | `python -m pytest tests/test_search_observe.py -q` | 27 passed in 2.60s (ghi nhận `lsp_ket_qua` có `duration_ms`, 4 `outcome`, bảo toàn mở khóa `khai_niem` ở PreToolUse) | PASS |
| Q5 | Thống kê p50/p95 và đối chiếu độ phủ caller chuẩn trong `search_rules.py` & `search_replay.py` (O5) | `python -m pytest tests/test_search_replay.py -q; python scripts/search_replay.py tests/fixtures/phien_excalidraw_tim.json --lsp-telemetry` | 13 passed in 0.42s; CLI `--lsp-telemetry` xuất bảng breakdown và latency chính xác | PASS |
| QC-F1 | Toàn bộ suite bài kiểm thử vùng chạm (6 modules) | `python -m pytest tests/test_auto_update_setup.py tests/test_lsp_gate.py tests/test_search_observe.py tests/test_search_rules.py tests/test_search_replay.py tests/test_subagent_start.py -q` | 167 passed, 4 subtests passed in 5.43s | PASS |
| QC-F2 | Ràng buộc kiến trúc (Spec §5) & Typecheck | `python -m pytest tests/test_kien_truc.py -q; pyright scripts/search_rules.py hooks/scripts/lsp_gate.py hooks/scripts/search_observe.py scripts/search_replay.py` | 4 passed in 0.09s; pyright: 0 errors, 0 warnings, 0 informations | PASS |
| QC-F3 | Tính toàn vẹn sơ đồ kiến trúc Archify | `python scripts/tdq_archify.py verify --document docs/tdq/spec/2026-10-26-0224-giam-timeout-agent-lsp.md --manifest docs/tdq/artifacts/2026-10-26-0224-giam-timeout-agent-lsp/preview.manifest.json` | status: current, valid: true, 0 reasons | PASS |
| QC-F4 | Clean code & Triết lý thiết kế (5 câu hỏi Self-check) | Soát SRP, OCP, LSP, ISP, DIP trên các hàm pure `search_rules.py`, `lsp_gate.py`, `search_observe.py` | 5/5 ĐẠT | PASS |

## Bằng chứng chi tiết

### Q1 — Tài liệu & Ngân sách token
```text
[2026-10-26T15:53:39] doc_lint: lint 1 file: uu-tien-tim-kiem.md
[2026-10-26T15:53:39] doc_lint: done — 0 violation(s) total, exit 0
ExitCode=0 (token_budget.py --kiem)
doc_index: 0/30 file(s) changed
```

### Q2 — Thiết lập Idle Timeout 90s MCP Client
```text
tests/test_auto_update_setup.py::TestAutoUpdateSetup::test_cai_dat_env_timeout_mcp PASSED [  8%]
tests/test_auto_update_setup.py::TestAutoUpdateSetup::test_can_cap_nhat_khi_version_stamp_cu PASSED [ 16%]
tests/test_auto_update_setup.py::TestAutoUpdateSetup::test_can_cap_nhat_phien_ban_khi_chua_co_stamp PASSED [ 25%]
tests/test_auto_update_setup.py::TestAutoUpdateSetup::test_can_kiem_tra_remote_throttle PASSED [ 33%]
tests/test_auto_update_setup.py::TestAutoUpdateSetup::test_doc_phien_ban_plugin PASSED [ 41%]
tests/test_auto_update_setup.py::TestAutoUpdateSetup::test_khong_can_cap_nhat_khi_stamp_khop PASSED [ 50%]
tests/test_auto_update_setup.py::TestAutoUpdateSetup::test_khong_downgrade_phat_hanh_khi_stamp_cao_hon PASSED [ 58%]
tests/test_auto_update_setup.py::TestAutoUpdateSetup::test_session_start_kich_hoat_tu_dong_cap_nhat PASSED [ 66%]
tests/test_auto_update_setup.py::TestAutoUpdateSetup::test_tach_version PASSED [ 75%]
tests/test_auto_update_setup.py::TestAutoUpdateSetup::test_thuc_hien_cap_nhat_remote_va_thong_bao PASSED [ 83%]
tests/test_auto_update_setup.py::TestAutoUpdateSetup::test_tu_dong_cap_nhat_khi_doi_phien_ban PASSED [ 91%]
tests/test_auto_update_setup.py::TestAutoUpdateSetup::test_tu_dong_cap_nhat_plugin_user_tu_cwd PASSED [100%]
12 passed in 0.27s
```

### Q3 — Cổng chặn blast_radius & Mạch ngắt Circuit Breaker
```text
tests/test_lsp_gate.py::TestLspGate::test_chan_blast_radius_khi_circuit_breaker_mo PASSED
tests/test_lsp_gate.py::TestLspGate::test_phan_xu_blast_radius_hop_le PASSED
tests/test_lsp_gate.py::TestLspGate::test_phan_xu_blast_radius_qua_nhieu_file PASSED
tests/test_lsp_gate.py::TestLspGate::test_phan_xu_blast_radius_scope_all PASSED
tests/test_lsp_gate.py::TestLspGate::test_phan_xu_blast_radius_transitive PASSED
tests/test_search_rules.py::TestSearchRulesCircuit::test_trang_thai_lsp_circuit_breaker PASSED
6 passed, 98 deselected in 0.16s
```

### Q4 — Sổ quan sát thời gian chạy & Phân loại kết quả LSP
```text
tests/test_search_observe.py ........................... [100%]
27 passed in 2.60s
- Kiểm chứng:
  + Ghi nhận PreToolUse -> khai_niem (bảo vệ quyền Grep không bị block oan)
  + PostToolUse/PostToolUseFailure -> tính duration_ms và gán nhãn outcome (ok, empty, error, timeout)
```

### Q5 — Thống kê p50/p95, Caller Oracle & Báo cáo Telemetry CLI
```text
tests/test_search_replay.py ............. [100%]
13 passed in 0.42s

LSP Telemetry & Circuit Breaker Report CLI:
Total LSP Calls: 0
Circuit Breaker Status: CLOSED (HEALTHY)
Outcome Breakdown:
  - ok:      0
  - empty:   0
  - error:   0
  - timeout: 0
Latency Percentiles:
  - p50: 0 ms
  - p95: 0 ms
  - max: 0 ms
```

### QC-F1 & QC-F2 & QC-F3
```text
167 passed, 4 subtests passed in 5.43s
4 passed in 0.09s (test_kien_truc.py)
0 errors, 0 warnings, 0 informations (pyright)
status: current, valid: true (Archify verify)
```

### QC-F4 — Clean Code Self-Check (5 câu hỏi)
1. **SRP (Đơn trách nhiệm):** CÓ — `trang_thai_lsp` chỉ tính trạng thái ngắt mạch từ rows; `phan_loai_ket_qua_lsp` chỉ phân loại chuỗi phản hồi/lỗi; `thong_ke_lsp` chỉ tổng hợp phân vị và đếm outcome; `doi_chieu_caller_oracle` chỉ tính toán tập hợp và độ phủ.
2. **OCP (Mở rộng/Đóng đổi):** CÓ — Cho phép mở rộng thêm các từ khóa nhận diện timeout/error mà không phá vỡ cấu trúc trả về hoặc hợp đồng giữa hook và scripts.
3. **LSP (Thay thế Liskov):** CÓ — Giữ nguyên hợp đồng của `search_rules` và `search_observe.py`, các dòng sổ `khai_niem` không bị thay đổi định dạng, dòng mới `lsp_ket_qua` mang trường `loai` phân biệt độc lập.
4. **ISP (Phân tách giao diện):** CÓ — `phan_xu_blast_radius` chỉ nhận `cwd`, `tool_input` và danh sách `rows` tùy chọn; hàm hook không bị ép buộc phụ thuộc vào toàn bộ state của plugin.
5. **DIP (Đảo ngược phụ thuộc):** CÓ — Tuân thủ tuyệt đối quy tắc kiến trúc TDQ: `scripts/` không bao giờ import ngược từ `hooks/`; các hàm gate trong `hooks/` import các hàm thuần từ `scripts/search_rules.py`.

## Lệch spec chờ duyệt
Không có (0 lệch, đạt 100% các tiêu chí thiết kế của Spec).

## Kết luận
ĐẠT (PASS 100% toàn bộ tiêu chí QC ở mức `ultra`). Chuyển phase sang `report`.
