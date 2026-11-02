# REPORT — Spec có sơ đồ Trước/Sau, subagent chỉ đọc, DoD bám nghiệp vụ (`2026-11-02-1157-nang-cap-spec-subagent` · lane full · mode main · 13 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P1 nhánh chặn subagent trong `hooks/scripts/edit_gate.py` (payload có `agent_id`, phase ∉ {implement, qc}, ngoài `docs/` → `deny` `TDQ:TEAM`) · P2 luật "Cơ chế hiện tại vs Sau" do HTML explainer dẫn ở cả 2 pipeline (pipeline nhanh bỏ ngưỡng 2 module), luật subagent mọi phase trong `subagent-tuning.md` + `reminder-codes.md`, câu luật DoD ở §6, khối "Thân PR (soạn sẵn)" ở mẫu report · P3 QC + 3 task fix (QC1.1 bỏ `lane` 0×0 + `@meta locale=en`, QC1.2 docstring + Mermaid dự phòng, QC2.1 `muc-luc-dong` + marker + neo L140 + 26 số dòng `luat-hien-co.md`).
**Kết quả:** `scripts/` đổi 0 → 0 file · test vùng chạm 199 passed, 382 subtests (14,64 s) · trọn suite 3960 passed, 10 skipped, 2518 subtests (3 failed ở `test_archify_e2e`, chạy riêng 2/2 passed 15,30 s) · smoke hook thật 485 ms · token `spec-template.md` 3477 → 3476 / 3500.
**Kiểm:** `pytest` 14 file vùng chạm 199 passed · `doc_lint` 0 lỗi · `doc_index --kiem --tat-ca` 0 lệch · QC PASS 10/10 mục DoD (Q6 kèm lệch #1), 3 defect vòng QC đã sửa, QC độc lập PASS 6/6.
**Đầu ra:** `hooks/scripts/edit_gate.py` · 10 file luật trong `skills/` · 4 file test (`tests/test_luat_subagent_pr.py` mới) · HTML mẫu `docs/tdq/spec/2026-11-02-1157-nang-cap-spec-subagent-preview.html` + ảnh `docs/tdq/qc/2026-11-02-1157-nang-cap-spec-subagent-preview.png`.
**Giới hạn:** (1) request mở qua `--bo-qua-lsp "cap nhat quy chuan spec archify va subagent"` do `python:. → CHUA_KIEM`; (2) subagent ghi qua shell (`Bash`/`PowerShell`) chưa bị nhánh `edit_gate` bắt (`ponytail:` đã ghi); (3) chưa kiểm runtime trong một phiên Claude Code thật vì phiên này nạp hook từ cache plugin 0.85.1, không từ repo.
**Lệch spec chờ duyệt:** `#1 · Q6 · ngưỡng "tron-bo 0 failed" → đo được "3960 passed, 10 skipped, 2518 subtests; 3 failed là test_archify_e2e (native Chrome updater IPC 0x5 khi chạy giữa suite; chạy riêng 2/2 passed 15,30 s trên cả dev và nhánh này)" · phương án đã áp: không sửa test cũ ngoài phạm vi`
**Git:** chưa commit (nhánh `feat/nang-cap-spec-subagent`, gốc `dev`).

## Thời gian

Request `2026-11-02-1157-nang-cap-spec-subagent` · lane full · opened at 2026-11-02T12:03:05+07:00

| Phase | Wall clock | API request | Tool wait | Background job | Observed union | Unattributed | Times entered |
|---|---|---|---|---|---|---|---|
| idle | 7s | 4s [partial] | 3s [partial] | — [unavailable] | 7s [partial] | 0s [partial] | 1 |
| analyze | 9 min | 6 min [partial] | 1 min [partial] | — [unavailable] | 6 min [partial] | 3 min [partial] | 1 |
| spec | 1h 27min | 4 min [partial] | 31s [partial] | — [unavailable] | 5 min [partial] | 1h 22min [partial] | 1 |
| plan | 20 min | 4 min [partial] | 24s [partial] | — [unavailable] | 4 min [partial] | 15 min [partial] | 1 |
| implement | 18 min | 6 min [partial] | 12 min [partial] | — [unavailable] | 18 min [partial] | 2s [partial] | 1 |
| qc | 48 min | 11 min [partial] | 14 min [partial] | — [unavailable] | 25 min [partial] | 24 min [partial] | 1 |
| report | 14s | 11s [partial] | 2s [partial] | — [unavailable] | 13s [partial] | 1s [partial] | 1 |
| Total | 3h 02min | 31 min [partial] | 28 min [partial] | — [unavailable] | 58 min [partial] | 2h 04min [partial] |  |

Model compute time is unavailable (`model_giay=null`). API includes network/provider latency; tool time is host wait. Observed metrics may overlap; unattributed time is not assumed user/model time.
Transcript attribution: project_window. Complete covers selected supported observations only.
- api_request_seconds: missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema
- tool_call_seconds: conflicts,missing_pairs,unknown_events,unreadable_or_uncertain_source
- background_job_seconds: schema_has_no_confirmed_lifecycle
- observed_union_seconds: conflicts,missing_pairs,unknown_events,unreadable_or_uncertain_source;missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema
- unattributed_seconds: wall_minus_observed_union;conflicts,missing_pairs,unknown_events,unreadable_or_uncertain_source;missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema

## Thân PR (soạn sẵn)

**Tóm tắt:** Spec và mini-plan sửa thứ đã có mở bằng một trang HTML Archify (`explainer`) gồm sơ đồ Trước và Sau, chữ chỉ phụ trợ; main agent được mở subagent chỉ đọc ở mọi phase và `edit_gate` chặn subagent sửa project trước phase `implement` (`TDQ:TEAM`); §6 buộc truy về nghiệp vụ, report thêm khối thân PR.
**Trước/Sau:** `docs/tdq/spec/2026-11-02-1157-nang-cap-spec-subagent-preview.html` (ảnh: `docs/tdq/qc/2026-11-02-1157-nang-cap-spec-subagent-preview.png`).
**Đã kiểm:**
- `python -m pytest tests/test_edit_gate.py -q` → 40 passed, 3 subtests
- `python -m pytest tests/test_spec_template.py tests/test_archify_workflow_contract.py tests/test_luat_subagent_pr.py tests/test_khao_sat_3_chieu.py -q` → 27 passed, 4 subtests
- `python -m pytest <14 file vùng chạm> -q` → 199 passed, 382 subtests (14,64 s)
- `python scripts/tdq_test.py tron-bo` → 3960 passed, 10 skipped, 2518 subtests (3 failed ở `test_archify_e2e` do Chrome updater IPC khi chạy giữa suite; chạy riêng → 2 passed in 15,30 s)
- `python docs/tdq/artifacts/2026-11-02-1157-nang-cap-spec-subagent/smoke_edit_gate.py` → SMOKE PASS (485 ms)
**Rủi ro hồi quy:** Luồng `edit_gate` của main agent và của `codex_edit_gate` không có trường `agent_id` nên không đi vào nhánh mới; giữ bởi 36 test cũ của `test_edit_gate.py`, `test_codex_edit_gate.py`, `test_compliance_protocol.py` (0 dòng test cũ bị xoá). Các neo luật cũ giữ bởi `test_luat_skill.py` (329 subtests).
