# REPORT — Eval chất lượng skill và plugin TDQ (`2026-11-01-1854-eval-chat-luong-skill` · lane full · mode subagent · 13 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P0 verifier fail-closed & evidence index · P1 contract thuần (`tdq_eval_contract.py`) + 2 adapter Windows (`tdq_eval_hosts.py`) · P2 CLI entry point (`tdq_skill_eval.py`) + tích hợp `tdq_eval.py` + corpus chuẩn (`corpus.json`) · P3 cổng workflow state (`tdq_state.py`) + đóng gói phát hành (`build_portable.py`, `skill-eval.md`, `token-budget.json`) · P4 kiểm định logging và regression e2e 11 ca biên · P5 Full suite, runtime smoke 4 kịch bản và review độc lập.
**Kết quả:** 5 cải tiến eval hoàn tất · phân loại target skill/hook/plugin chặt chẽ · từ chối đủ 4/4 ca lệch danh tính đối chứng · 3 nhóm metrics trigger/outcome/efficiency độc lập · không quy thiếu chi phí thành $0.00 · preflight native không gọi model · 3949 test passed trong Full suite · 4/4 runtime scenarios PASS trong 1.68s.
**Kiểm:** `python3 -m pytest -q tests/test_tdq_eval_contract.py tests/test_tdq_eval_hosts.py tests/test_tdq_skill_eval.py tests/test_skill_quality_corpus.py tests/test_eval_workflow_gate.py tests/test_eval_logging.py tests/test_eval_contracts_e2e.py` (422 passed) · doc_lint 0 vi phạm · token_budget 60 file đạt · QC PASS 10/10 mục DoD.
**Đầu ra:** `scripts/tdq_eval_contract.py` · `scripts/tdq_eval_hosts.py` · `scripts/tdq_skill_eval.py` · `evals/skill-quality/corpus.json` · `skills/tdq-build/references/skill-eval.md` · Backup: không có ngoài repo.
**Giới hạn:** Báo cáo mẫu ghi nhận nhãn `synthetic/offline`, chưa chạy phiên model LLM trả phí nào trong request này; 11 worktree cũ và 3 subtest test_archify_e2e do Windows browser startup handshake được bảo toàn nguyên trạng và lưu receipt đầy đủ.
**Lệch spec chờ duyệt:** không có
**Git:** Nhánh `codex/eval-chat-luong-skill` gồm các commit triển khai kỹ thuật thuần túy, không có attribution trailer.

## Thời gian

Request `2026-11-01-1854-eval-chat-luong-skill` · lane full · opened at 2026-11-01T18:57:21+07:00

| Phase | Wall clock | API request | Tool wait | Background job | Observed union | Unattributed | Times entered |
|---|---|---|---|---|---|---|---|
| idle | 44s | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| analyze | 28 min | — [partial] | 13s [partial] | — [unavailable] | 13s [partial] | 28 min [partial] | 1 |
| spec | 10 min | 2 min [partial] | 13s [partial] | — [unavailable] | 2 min [partial] | 8 min [partial] | 1 |
| plan | 9 min | 5 min [partial] | 15s [partial] | — [unavailable] | 5 min [partial] | 4 min [partial] | 1 |
| mode | 2 min | 35s [partial] | 2s [partial] | — [unavailable] | 37s [partial] | 1 min [partial] | 1 |
| implement | 2h 52min | 2h 12min [partial] | 1h 46min [partial] | — [unavailable] | 2h 52min [partial] | 52s [partial] | 1 |
| qc | 3 min | 3 min [partial] | 2 min [partial] | — [unavailable] | 3 min [partial] | 0s [partial] | 1 |
| report | 59s | 55s [partial] | 29s [partial] | — [unavailable] | 59s [partial] | 0s [partial] | 1 |
| Total | 3h 46min | 2h 23min [partial] | 1h 49min [partial] | — [unavailable] | 3h 04min [partial] | 43 min [partial] |  |

Model compute time is unavailable (`model_giay=null`). API includes network/provider latency; tool time is host wait. Observed metrics may overlap; unattributed time is not assumed user/model time.
Transcript attribution: project_window. Complete covers selected supported observations only.
- api_request_seconds: missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema
- tool_call_seconds: conflicts,missing_pairs,unknown_events,unreadable_or_uncertain_source
- background_job_seconds: schema_has_no_confirmed_lifecycle
- observed_union_seconds: conflicts,missing_pairs,unknown_events,unreadable_or_uncertain_source;missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema
- unattributed_seconds: wall_minus_observed_union;conflicts,missing_pairs,unknown_events,unreadable_or_uncertain_source;missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema
