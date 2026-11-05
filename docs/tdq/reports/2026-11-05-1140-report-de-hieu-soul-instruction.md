# REPORT — Báo cáo dễ hiểu kèm Archify HTML, Soul & Auto-pin User-Instruction (`2026-11-05-1140-report-de-hieu-soul-instruction` · lane quick · mode main · 3 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Trước request (trạng thái/flow):** Khuôn `report-template.md` chỉ yêu cầu nén dòng bằng dấu `·`, chưa bắt buộc tách riêng 4 phần dễ hiểu cho mọi người đọc; `soul.md` và `tdq-conventions/SKILL.md` chưa khóa chuẩn trình bày dễ hiểu + trực quan + đầy đủ thông tin; khối `KHOI_HUONG_DAN` chưa có mục chuẩn trình bày/report và nhánh chạy nền `khoi_tao_nen` (`--nen`) chưa gọi `ghim_huong_dan_tool` vào `~/.claude/CLAUDE.md`.
**Sau request (trạng thái/flow):** Mọi report (`reports/<slug>.md` + `reports/<slug>.html`) bắt buộc viết đơn giản, dễ hiểu, trực quan, đầy đủ 4 phần (**Trước request**, **Sau request**, **Đã test gì**, **Kết quả test**); `soul.md` và `SKILL.md` khóa nguyên tắc luôn trình bày **đơn giản, dễ hiểu, ngắn gọn nhưng trực quan, đầy đủ thông tin**; `KHOI_HUONG_DAN` (`tdq_setup.py`, `docs/claude-md-mau.md`) tự động ghim vào `~/.claude/CLAUDE.md` cả khi cài mới (`tdq_setup.py` trực tiếp hoặc `--nen`) lẫn khi update phiên bản (`tu_dong_cap_nhat_khi_doi_phien_ban`). · **Đã làm:** T1 chuẩn hóa `report-template.md`, `archify-lifecycle.md`, `tdq_state.py`, `phases.md` · T2 cập nhật `soul.md`, `tdq-conventions/SKILL.md` · T3 cập nhật `tdq_setup.py`, `docs/claude-md-mau.md`, `token-budget.json` và ghim thật vào `~/.claude/CLAUDE.md`.
**Đã test gì:** (1) `python -m pytest tests/test_report_visual.py -q` (hợp đồng Report + Archify HTML 4 phần); (2) `python -m pytest tests/test_soul_rules.py -q` (luật gốc Soul < 150 dòng + Conventions); (3) `python -m pytest tests/test_claude_md_core.py tests/test_auto_update_setup.py tests/test_token_budget.py tests/test_docs_consistency.py tests/test_skill_shape.py -q` (khối `TDQ:TOOLS`, auto-pin khi `--nen`/update, trần token 62 file); (4) Smoke runtime ghim thật vào `CLAUDE.md` + đồng bộ `docs/architecture/index.html` + review độc lập `tdq-qc-tester`.
**Kết quả test:** `94 passed, 170 subtests passed in 6.69s` (0 failed); smoke runtime `SMOKE_RUNTIME_PIN: PASS, bytes= 8285`; `tdq_archify.py status` → `status="current", reasons=[]`; QC độc lập (`ad05e87ce0f2a12e4`) → `VERDICT: PASS everything (71 passed, 149 subtests passed, 0 defects)`. · **Kết quả:** Số phần bắt buộc trong Report dễ hiểu `0 → 4` · Độ dài `soul.md` `140 → 142 dòng (< 150)` · Đồng bộ auto-pin `CLAUDE.md` `2 đường (main/update) → 3 đường (main/update/--nen)` · **Kiểm:** `doc_lint` ok (6 file) · `khoa-token` ok (62 file) · QC PASS 6/6 mục (`muc_qc=ultra`).
**Đầu ra:** `skills/tdq-build/references/report-template.md`, `skills/tdq-build/references/archify-lifecycle.md`, `skills/tdq-conventions/references/soul.md`, `skills/tdq-conventions/SKILL.md`, `scripts/tdq_state.py`, `scripts/tdq_setup.py`, `docs/claude-md-mau.md` · **Archify HTML:** [docs/tdq/reports/2026-11-05-1140-report-de-hieu-soul-instruction.html](2026-11-05-1140-report-de-hieu-soul-instruction.html) · Backup: `~/.claude/CLAUDE.md` cập nhật nguyên tử qua `_thay_instruction` (giữ nguyên toàn bộ nội dung ngoài `<!-- TDQ:TOOLS -->`).
**Giới hạn:** Mở qua cổng LSP bằng `--bo-qua-lsp "cap nhat soul, report contract va managed user-instruction"` trên module `python:.`; thay đổi rule trong Express lane được kiểm bằng 94 unit/contract tests + QC ultra (`eval-waive` cho live paid-model trial).
**Lệch spec chờ duyệt:** không có
**Git:** chưa commit trên nhánh `feature/report-de-hieu-soul-instruction` (gốc: `dev`)

## Thời gian

Request `2026-11-05-1140-report-de-hieu-soul-instruction` · lane quick · opened at 2026-11-05T11:47:30+07:00

| Phase | Wall clock | API request | Tool wait | Background job | Observed union | Unattributed | Times entered |
|---|---|---|---|---|---|---|---|
| idle | 1s | — [partial] | 1s [partial] | — [unavailable] | 1s [partial] | 0s [partial] | 1 |
| analyze | 3 min | 2 min [partial] | 8s [partial] | — [unavailable] | 2 min [partial] | 1s [partial] | 1 |
| implement | 20 min | 8 min [partial] | 2 min [partial] | — [unavailable] | 9 min [partial] | 11 min [partial] | 1 |
| report | 14s | 7s [partial] | 7s [partial] | — [unavailable] | 14s [partial] | 0s [partial] | 1 |
| Total | 23 min | 10 min [partial] | 2 min [partial] | — [unavailable] | 12 min [partial] | 11 min [partial] |  |

Model compute time is unavailable (`model_giay=null`). API includes network/provider latency; tool time is host wait. Observed metrics may overlap; unattributed time is not assumed user/model time.
Transcript attribution: project_window. Complete covers selected supported observations only.
- api_request_seconds: missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema
- tool_call_seconds: conflicts,missing_pairs,unknown_events,unreadable_or_uncertain_source
- background_job_seconds: schema_has_no_confirmed_lifecycle
- observed_union_seconds: conflicts,missing_pairs,unknown_events,unreadable_or_uncertain_source;missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema
- unattributed_seconds: wall_minus_observed_union;conflicts,missing_pairs,unknown_events,unreadable_or_uncertain_source;missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema

## Thân PR (soạn sẵn)

**Tóm tắt:** Chuẩn hóa phase `report` luôn xuất cặp Markdown + Archify HTML dễ hiểu cho mọi người đọc, trực quan và đầy đủ 4 phần (Trước request, Sau request, Đã test gì, Kết quả test); bổ sung nguyên tắc trình bày vào `soul.md` và tự động ghim vào `~/.claude/CLAUDE.md` khi cài mới hoặc update TDQ-Workflow.
**Trước/Sau:** [docs/tdq/plan/2026-11-05-1140-report-de-hieu-soul-instruction-flow.html](../plan/2026-11-05-1140-report-de-hieu-soul-instruction-flow.html)
**Đã kiểm:**
- `python -m pytest tests/test_report_visual.py tests/test_soul_rules.py tests/test_claude_md_core.py tests/test_auto_update_setup.py tests/test_token_budget.py tests/test_docs_consistency.py tests/test_skill_shape.py -q` → `94 passed, 170 subtests passed in 6.69s`
- `python scripts/tdq_archify.py status` → `status="current", reasons=[]`
**Rủi ro hồi quy:** Khối `<!-- TDQ:TOOLS -->` trong `~/.claude/CLAUDE.md` tăng kích thước (~420 byte); đã nâng trần `MAX_BYTES` trong `tests/test_claude_md_core.py` lên `12500` và khóa nguyên văn với `docs/claude-md-mau.md`.
<!-- tdq-archify-binding:start -->
<!-- manifest: 2026-11-05-1140-report-de-hieu-soul-instruction.manifest.json -->
<!-- manifest_digest: ac951e3dca0a4213eb6e6cd30eff9b43672c2dbe11add1a9c8a0f921698156ed -->
<!-- tdq-archify-binding:end -->