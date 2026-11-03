# REPORT — Tích hợp Ultracode vào TDQ Workflow (`2026-11-02-1957-tich-hop-ultracode` · lane full · mode subagent · plan/DoD đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** `_ultracode` modifier cho express/deep mà không đổi state lane · Express finite auto-route · Deep optional spec/plan review/implement · shared prompt/host/completion contract · Edit/Bash mutation gates · TDQ-owned team worktree · QC/eval quality-first.
**Kết quả:** 3.991 test PASS · 5 SKIP · 0 FAIL · 2.530 subtest ở vòng full trước fix và full receipt cuối 3.991/5/0 · gate regression 91 test + 73 subtest · module từng fail chạy lại 50 test + 58 subtest.
**Kiểm:** doc lint PASS · token budget 61 file PASS · Ruff `bash_gate.py` PASS · visual 4 sơ đồ >0, console 0 lỗi · QC độc lập tìm defect rồi fix · Q1–Q11 và QC-F1–F4 PASS.
**Đầu ra:** `skills/tdq-conventions/references/ultracode.md` · routing ở intake/spec/plan/build · gate ở `edit_gate.py`/`bash_gate.py` · test routing/contract · runtime/eval receipts · HTML/PNG Trước/Sau.
**Giới hạn:** interactive implementer không có Workflow tool và model request `cc1` bị runtime map sang `cc4`; ghi UNSUPPORTED + structured fallback. `claude -p` chỉ PARTIAL. Agent SDK chưa cài nên UNSUPPORTED. Không có token ceiling; route vẫn hữu hạn.
**Sự cố đã xử lý:** dọn worktree T4.1 chạy reset nhầm checkout chính làm mất tracked diff và làm rỗng plan; đã phục hồi từ spec/evidence, tái chạy tests/lint/token/full suite; không mất dữ liệu cuối.
**Lệch spec chờ duyệt:** không có.
**Git:** chưa commit; nhánh `feat/tich-hop-ultracode`, gốc `dev`.

## Thời gian

Request mở 2026-11-02T19:58:33+07:00. Timing chi tiết không khả dụng từ `tdq_timing.py show` trong lượt resume (chỉ in header); không ước lượng thay số đo.

## Thân PR (soạn sẵn)

**Tóm tắt:** Thêm `_ultracode` như modifier của express/deep, tích hợp Workflow có kiểm soát mà không thêm lane/state/phase; TDQ giữ độc quyền approval, state và Git.
**Trước/Sau:** `docs/tdq/spec/2026-11-02-1957-tich-hop-ultracode-preview.html`.
**Đã kiểm:** full receipt PASS 3.991 test, 5 skip, 0 failure; gate/routing/contract tests; lint/token/Ruff; browser 4 panels.
**Rủi ro hồi quy:** Bash gate chỉ deny subagent mutation trước implement; main agent/implement giữ behavior cũ; read redirect noise có negative tests; runtime unsupported fail-closed và fallback.
