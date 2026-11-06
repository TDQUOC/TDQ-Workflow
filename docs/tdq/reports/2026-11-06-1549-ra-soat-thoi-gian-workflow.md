# REPORT — Rà soát thời gian TDQ Workflow (`2026-11-06-1549-ra-soat-thoi-gian-workflow` · lane full · mode subagent)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Trước request (trạng thái/flow):** Hai báo cáo Review đặt số lịch sử, snapshot, giả thuyết tăng tốc và đề xuất cắt bước cạnh nhau. Chưa có cohort đủ để kết luận giảm 50%; một số đề xuất optional trái hợp đồng TDQ hiện hành.

**Sau request (trạng thái/flow):** Có bảng kiểm claim và thứ tự thử nghiệm P0/P1/P2 bên dưới. Đây là **đề xuất**, chưa thay đổi runtime hoặc policy; HTML ghép cùng báo cáo đã qua Archify verify `current`.

## 1. Claim, chứng cứ và giới hạn

| Claim từ Review | Phán quyết | Chứng cứ đối chiếu |
|---|---|---|
| `tdq_finish` rebuild Graphify sau file code đổi | **CONFIRMED** về cơ chế, **UNCERTAIN** về thời gian tiết kiệm | `scripts/tdq_finish.py:198-207,300-323` gọi `graphify extract . --code-only` đồng bộ. 300s là timeout, **không phải duration**. LSP tìm caller; `graphify affected` không dùng làm bằng chứng mới vì readiness check báo bậc graphify thiếu. |
| Báo cáo quick n=3: wall 14.116s, observed union 4.494,8s | **CONFIRMED** phép chia 31,84%; **UNCERTAIN** cohort | `Review-TDQWorkflow/docs/tdq/reports/2026-11-05-2026-toi-uu-nam-muoi.md:15-24`; `Review-TDQWorkflow/docs/tdq/timing.jsonl:1-2` hiện chỉ có 2 record, không tái dựng được n=3. Không lấy 31,84% làm trần tốc độ thực của mọi quick request. |
| Audit Review 977,98s, bản tối ưu 599,66s wall | **CONFLICT** nếu hiểu là thời gian đóng request | `Review-TDQWorkflow/docs/tdq/reports/2026-11-05-1949-tdq-runtime-audit.md:100-102` và `2026-11-05-2026-toi-uu-nam-muoi.md:112-120` là snapshot; hai record đóng có wall lần lượt **1.192,648477s** và **854,820835s** (`Review-TDQWorkflow/docs/tdq/timing.jsonl:1-2`). Snapshot và số cuối là thời điểm khác nhau, không phải dữ liệu thay thế cho nhau. |
| LSP startup 40,4m/62,8m/19h và p95 rất cao | **UNCERTAIN** | `Review-TDQWorkflow/docs/tdq/reports/2026-11-05-1949-tdq-runtime-audit.md:24-30` nêu claim; ledger hiện còn không đủ duration hợp lệ để tái dựng phân vị. Đo lại cold/warm và log timeout riêng trước khi xếp mức savings. |
| Full suite 857,25s là cost hiện tại | **CONFLICT** về nhãn “hiện tại” | Đây là mẫu lịch sử `Review-TDQWorkflow/docs/tdq/reports/2026-11-05-1949-tdq-runtime-audit.md:38-42`; receipt gần hơn trước release 0.94.0 ghi **800,34s**, 4.180 passed, 7 skipped, 4.187 case ID tại `docs/tdq/reports/2026-11-06-1250-han-che-ngat-giua-plan.md:9-15`. Hai run khác revision; không tính speedup. |
| Model/user wait giải thích phần thời gian còn lại | **UNCERTAIN** | Record audit đóng: wall 1.192,648477s; API 942,715s partial, tool 55,997s partial, observed union 977,829s partial, unattributed 214,819477s partial; `model_giay=null` (`Review-TDQWorkflow/docs/tdq/timing.jsonl:1`). Các khoảng API/tool chồng lấp; không cộng hoặc gán unknown cho model/người dùng. |

## 2. Lộ trình giảm critical path — chưa đo mức tiết kiệm

| Ưu tiên | Thử nghiệm, cơ chế | Điều kiện promote; rollback |
|---|---|---|
| **P0** | Đo SessionStart và LSP cold/warm theo repo, language, host; sau đó thử stamp-only maintenance và circuit breaker có health proof. Tránh startup/doctor lặp trên đường nóng mà vẫn kiểm kết nối thật. | AB/BA 20–30 lần, ghi p50/p95, timeout và false-healthy; chỉ bật nếu decision tương đương 100%, p95 giảm và không bỏ LSP gate. Lỗi freshness → quay doctor fresh; `Review-TDQWorkflow/docs/tdq/reports/2026-11-05-2026-toi-uu-nam-muoi.md:48-54`. |
| **P0** | Đo riêng thời gian Graphify extract trong `tdq_finish`; thí điểm stale marker + rebuild trước truy vấn/QC khi có bảo đảm freshness, thay vì rebuild đồng bộ sau mỗi code turn. | So p50/p95 close-out, graph age và miss trên các repo; phát hiện miss/stale → quay per-turn rebuild. 300s chỉ là ceiling (`scripts/tdq_finish.py:198-207,300-323`). |
| **P0** | Tránh full suite bị vô hiệu do sửa source giữa run: source fingerprint/writer barrier trước một full fresh cuối; test vùng chạm cho vòng sửa. | Đo số receipt invalid, rerun và wall; deadlock hoặc bỏ sót thay đổi → tắt barrier, chạy lại fresh. Giữ hợp đồng full fresh ở QC full/ultra (`skills/tdq-build/references/qc.md:91-100`). |
| **P1** | Thử `--workers 2` và `--reuse auto` chỉ trên scope hermetic; không bật toàn cục. | Workers: ≥3 cặp AB/BA/AB, parity 100%, median giảm ≥20%, p95/flake không xấu; cache: ≥3 triplet off/cold/warm, fingerprint/evidence tương đương. Fail → `--workers 1 --fresh --reuse off` (`skills/tdq-build/references/runtime-speed.md:27-68`). |
| **P1** | Instrument hook ledger/read/search I/O và thử tail/index thay full parse; tách check-only khỏi setup có cài đặt. | p50/p95 hook thấp hơn, quyết định gate tương đương 100%; mismatch → full parse. Setup mutating chỉ sau người dùng duyệt, không tự động cài (`hooks/scripts/search_observe.py`; `skills/tdq-intake/SKILL.md`; `skills/tdq-setup/SKILL.md`). |
| **P2** | Batch các Read độc lập; dùng tier `nhỏ` đúng 4 điều kiện, quick cho thay đổi rõ. Không ghép spec+plan hay bỏ gate mặc định. | ≥10 request mỗi bucket cùng host/model/lane/task-family, so median active/critical path khi **đã instrument**, rework, defect và unknown; xấu đi → lane/gate cũ (`skills/tdq-intake/references/quick-lane.md:26-40`). |

**Quy tắc đo:** Không cộng phần trăm giữa các hàng vì các đường nóng chồng nhau. Mục tiêu “giảm 50%” chỉ là giả thuyết; chỉ công bố wall reduction khi cohort trước/sau đủ so sánh, user wait được tách, và QC/reopen/defect không tăng. `active-agent` hiện chưa instrument (`Review-TDQWorkflow/docs/tdq/reports/2026-11-05-2026-toi-uu-nam-muoi.md:5-24,74-94`).

## 3. Cái gì optional?

| Phân loại | Thành phần | Quyết định hiện hành / điều kiện |
|---|---|---|
| **Bắt buộc** | Spec/plan approval provenance ở lane full, DoD/stop safety, search gate, QC full fresh khi chọn full/ultra, cặp báo cáo Markdown + Archify HTML | **Không** chuyển optional chỉ để nhanh. `skills/tdq-build/references/qc.md:91-100`; `skills/tdq-build/references/report-template.md:31-34`; `skills/tdq-intake/references/quick-lane.md:31-40`. |
| **Có điều kiện theo việc** | Browser native test cho UI; Master architecture sync theo manifest/freshness; B0/B2 trong quick theo trigger; Graphify code rebuild khi file code đổi | Browser UI không bỏ khi UI thay đổi. Browser check cho **report HTML** nếu không chạy phải công khai fallback, không nhận như đã test; Master không sync mù. B1 quick vẫn khảo sát ba chiều. |
| **Optional sẵn có** | Model eval, `--workers 2`, cache `--reuse auto`, `/goal` | Eval chỉ khi người dùng yêu cầu và đồng ý; workers/cache sau parity; `/goal` do người dùng tự bật. Không biến tùy chọn thành mặc định bằng báo cáo này. |
| **Chờ request/duyệt riêng** | Chuyển báo cáo HTML, search telemetry/gate hoặc full fresh thành optional; gộp deep gate; auto-install dependency | **Bác bỏ ở request này.** Search telemetry liên quan chứng cứ gate nên cần semantic-equivalence test, không tắt theo lane tùy ý; setup mutating cần consent. Báo cáo Review đề xuất điều kiện hóa HTML tại `2026-11-05-1949-tdq-runtime-audit.md:46-71`, trái hợp đồng hiện hành. |

**Đã test gì:** Ba phản biện độc lập ở analyze (runtime, optional, benchmark); kiểm hai report Review và 2 timing record; phép chia `4494.8/14116*100`; LSP caller `step_graphify`; `tdq_lsp.py check`; đọc source/policy; lint và Archify render/verify tại QC. Không chạy benchmark hay full suite do phạm vi chỉ tài liệu. Mode subagent: team map giao **1/4 task**, giữ 3 task theo luật `vung-khoa`/`mcp`; 3 Explore subagents đã fanout ở analyze.

**Kết quả test:** Phép chia **31,84%** đạt; 2/2 timing record đọc được; LSP check **7/8** (Graphify thiếu), không dùng graph stale làm chứng cứ; lint **0 lỗi**, Archify render static gates đạt và verify `current`, QC tài liệu **4/4 DoD**. Không có kết quả đo speedup hoặc thử nghiệm model nhỏ từ request này.

**Giới hạn:** Ledger LSP/cohort n=3 không đủ tái dựng; timing partial, background unavailable và model compute null; không kiểm browser native cho HTML; số suite gần đây vẫn trước 0.94.0. `eval: chưa kích hoạt (opt-in)`. Không sửa source, runtime hoặc repo Review.

**Lệch spec chờ duyệt:** Không có. **Git:** Chưa commit/push.

## Thời gian

Request `2026-11-06-1549-ra-soat-thoi-gian-workflow` · lane full · opened at 2026-11-06T15:51:54+07:00

| Phase | Wall clock | API request | Tool wait | Background job | Observed union | Unattributed | Times entered |
|---|---|---|---|---|---|---|---|
| idle | 0s | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| analyze | 5 min | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| spec | 6h 14min | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| plan | 11 min | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| Total | 6h 30min | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] |  |

Model compute time is unavailable (`model_giay=null`). API includes network/provider latency; tool time is host wait. Observed metrics may overlap; unattributed time is not assumed user/model time.
Transcript attribution: project_window. Complete covers selected supported observations only.
- api_request_seconds: missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema;no_confirmed_span_in_window
- tool_call_seconds: conflicts,unknown_events,unreadable_or_uncertain_source;no_confirmed_span_in_window
- background_job_seconds: schema_has_no_confirmed_lifecycle
- observed_union_seconds: conflicts,unknown_events,unreadable_or_uncertain_source;missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema;no_confirmed_span_in_window
- unattributed_seconds: wall_minus_observed_union;conflicts,unknown_events,unreadable_or_uncertain_source;missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema;no_confirmed_span_in_window

## Thân PR (soạn sẵn)

**Tóm tắt:** Phân biệt số đo hiện hành với snapshot/lịch sử; đề xuất benchmark có guardrail trước khi tối ưu LSP, Graphify, full-suite retries và hook.
**Trước/Sau:** Preview planned `../spec/2026-11-06-1549-ra-soat-thoi-gian-workflow-preview.html`; report HTML thể hiện kết luận nghiên cứu, không chứng nhận hiệu năng.
**Đã kiểm:** 2 timing record, ratio 31,84%, source/policy đối chiếu; lint 0 lỗi, Archify verify `current`; full suite và browser native không chạy theo phạm vi tài liệu.
**Rủi ro hồi quy:** Nếu triển khai stale graph, cache, parallel hoặc cắt gate trước parity có thể tăng false PASS/flake; chưa có runtime thay đổi trong request này.
<!-- tdq-archify-binding:start -->
<!-- manifest: 2026-11-06-1549-ra-soat-thoi-gian-workflow.manifest.json -->
<!-- manifest_digest: f084679cb3ee00992ef66be1c7bb6ac16fefc2db7ec30cc5a84e4b39485f391b -->
<!-- tdq-archify-binding:end -->