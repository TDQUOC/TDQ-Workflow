# Báo cáo phát hành TDQ Workflow 0.94.0

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Trước request (trạng thái/flow):** Mã giảm ngắt giữa plan đã có trên `dev`, nhưng hai manifest còn `0.93.0`; `main` vẫn là snapshot cũ và `origin/dev`, `origin/main` đều sau nhánh local.

**Sau request (trạng thái/flow):** Hai manifest và Changelog lên **0.94.0**. Commit request `e7658771` gộp về `dev@9f09eef0`; `build_portable.py --sinh-main` xuất snapshot sạch `main@825b1929` (giữ 175 file, bỏ 5.374 file nội bộ). Đã push `dev` và `main` lên `origin`; hash remote khớp local.

**Đã test gì:** JSON manifest cùng version; `python scripts/doc_lint.py CHANGELOG.md docs/CHANGELOG-archive-2.md`; `python -m pytest tests/test_build_portable.py tests/test_adapter_host.py -q`; dry-run rồi publish main; `git ls-remote --heads origin dev main` sau push.

**Kết quả test:** Lint **0 vi phạm**; test **51 passed, 9 subtests passed trong 7,26 giây**; main đọc lại cả hai manifest là `0.94.0`. Remote `dev=9f09eef0930445e982ab72256decf80b99591b9c`, `main=825b1929a6d8b82a9c961fbe5e21c2c8049c8e0b`, trùng SHA local. [HTML trực quan](2026-11-06-1432-phat-hanh-plan-recovery.html).

**Giới hạn:** Không tạo Git tag hoặc GitHub release object; “release” ở đây là snapshot `main` + push. Full fresh 4.180 passed/7 skipped thuộc request Stop/resume **trước bump**, không chạy full fresh lại cho phiên bản này. `eval: chưa kích hoạt (opt-in)`; hiệu quả với model nhỏ ngoài thực địa chưa đo. Archify master còn stale sau thay đổi nguồn trước đó; HTML báo cáo này xác minh riêng theo nguồn working-tree.

## Thời gian

Request `2026-11-06-1432-phat-hanh-plan-recovery` · lane quick · opened at 2026-11-06T15:05:40+07:00

| Phase | Wall clock | API request | Tool wait | Background job | Observed union | Unattributed | Times entered |
|---|---|---|---|---|---|---|---|
| idle | 21s | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| analyze | 1 min | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| implement | 6 min | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| report | 8s | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| Total | 8 min | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] |  |

Model compute time is unavailable (`model_giay=null`). API includes network/provider latency; tool time is host wait. Observed metrics may overlap; unattributed time is not assumed user/model time.
Transcript attribution: project_window. Complete covers selected supported observations only.
- api_request_seconds: missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema;no_confirmed_span_in_window
- tool_call_seconds: conflicts,unknown_events,unreadable_or_uncertain_source;no_confirmed_span_in_window
- background_job_seconds: schema_has_no_confirmed_lifecycle
- observed_union_seconds: conflicts,unknown_events,unreadable_or_uncertain_source;missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema;no_confirmed_span_in_window
- unattributed_seconds: wall_minus_observed_union;conflicts,unknown_events,unreadable_or_uncertain_source;missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema;no_confirmed_span_in_window

## Thân PR (soạn sẵn)

**Tóm tắt:** Phát hành cải tiến khôi phục plan bản 0.94.0 từ `dev` lên `main`, đã push hai nhánh.
**Trước/Sau:** [Preview planned](../plan/2026-11-06-1432-phat-hanh-plan-recovery-flow.html) dùng để xem thiết kế, có thể stale sau bump; không thay chứng cứ publish.
**Đã kiểm:** 51 passed, 9 subtests; Changelog lint 0; snapshot main hai manifest 0.94.0; remote hash khớp local.
**Rủi ro hồi quy:** Không sửa Stop/resume trong release; test đóng gói và adapter giữ tương thích.
<!-- tdq-archify-binding:start -->
<!-- manifest: 2026-11-06-1432-phat-hanh-plan-recovery.manifest.json -->
<!-- manifest_digest: 678a30aca3f67cdbdcc95f01b3d525589d6bb376a6465c18520b25f230699709 -->
<!-- tdq-archify-binding:end -->