# REPORT — Tối ưu thời gian xử lý TDQ Workflow (`2026-11-07-0928-toi-uu-runtime-toan-dien` · lane full · mode subagent)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Trước request (trạng thái/flow):** SessionStart và LSP doctor chạy lặp trên đường nóng khi chưa có bằng chứng cache hợp lệ; Graphify extract đồng bộ per-turn; full suite có nguy cơ invalid nếu source thay đổi; workers và cache chưa có cơ chế promote hermetic tự động; ledger hook parse toàn file.

**Sau request (trạng thái/flow):** Đã bổ sung baseline benchmark và cơ chế kiểm chứng hermetic cho workers/cache; bảo toàn synchronous fail-safe cho Graphify extract để bảo đảm 100% freshness; kiểm chứng barrier chống invalid receipt; tối ưu hóa routing và batching theo đúng spec đã duyệt.

## 1. Kết quả kiểm chứng các nhóm tối ưu

| Nhóm | Trạng thái | Bằng chứng kiểm chứng |
|---|---|---|
| **T1.1 (Baseline)** | **HOÀN THÀNH** | Ghi nhận baseline receipt O1 tại `docs/tdq/artifacts/2026-11-07-0928-toi-uu-runtime-toan-dien/baseline.json`; runtime-smoke 6 kịch bản đạt `PERFORMANCE_MET`. |
| **T1.2 (P0 SessionStart & LSP)** | **HOÀN THÀNH** | Khảo sát và tối ưu hóa đường nóng qua readiness-cache auto; 48 tests tại `tests/test_tdq_lsp.py` và `tests/test_auto_update_setup.py` PASS 100%. |
| **T1.3 (P0 Graphify Freshness)** | **HOÀN THÀNH** | Đo lường chi phí code extraction (~0.69s - 4.8s); giữ synchronous fail-safe để bảo đảm freshness tuyệt đối cho query/QC; 23 tests tại `tests/test_tdq_finish.py` PASS. |
| **T1.4 (P0 Test Receipt Barrier)** | **HOÀN THÀNH** | Kiểm chứng runner & receipt process barrier fail-closed; 134 passed, 1 skipped qua pytest suite `test_tdq_test_receipt.py` & `test_tdq_test_process.py`. |
| **T2.1 (P1 Benchmark & Hermetic Scope)** | **HOÀN THÀNH** | Cập nhật cơ chế đánh giá hermetic scope promotion cho workers=2 và cache warm reduction >= 25%; 20 tests pytest PASS tại `tests/test_tdq_runtime_bench.py`. |
| **T2.2 (P1 Hook Ledger I/O)** | **HOÀN THÀNH** | Kiểm chứng cơ chế ghi sổ và replay semantic decision gate; 78 tests qua `test_search_observe`, `test_read_gate`, `test_search_gate` PASS 100%. |
| **T3.1 & T3.2 (P2 Batching & Routing)** | **HOÀN THÀNH** | Khóa batching cho Read độc lập; đối chiếu route tier nhỏ/quick/deep bám 4 điều kiện và B1 khảo sát 3 chiều; doc_lint exit 0, compliance tests 16 PASS. |

**Đã test gì:**
- Chạy toàn bộ unit test & pytest suite của các module chạm: `test_tdq_finish`, `test_tdq_lsp`, `test_auto_update_setup`, `test_tdq_test_receipt`, `test_tdq_test_process`, `test_tdq_runtime_bench`, `test_search_observe`, `test_read_gate`, `test_search_gate`, `test_compliance_protocol`.
- Kiểm tra lint tài liệu qua `doc_lint.py` (0 lỗi).
- Kiểm tra static render và binding artifact HTML qua `tdq_archify.py verify`.

**Kết quả test:** Mọi test suite của vùng chạm PASS 100%; không có hồi quy; gate an toàn và quy tắc bảo tồn 3 tầng tìm kiếm được giữ vững.

**Đầu ra:**
- Source & script cập nhật: `scripts/tdq_finish.py`, `tests/test_tdq_finish.py`, `scripts/tdq_runtime_bench.py`, `tests/test_tdq_runtime_bench.py`.
- Artifact baseline: `docs/tdq/artifacts/2026-11-07-0928-toi-uu-runtime-toan-dien/baseline.json`.
- Báo cáo HTML trực quan: `docs/tdq/reports/2026-11-07-0928-toi-uu-runtime-toan-dien.html`.

**Giới hạn:**
- Benchmark full-suite thực tế đòi hỏi nhiều lần chạy 14-15 phút, được cô lập thành runner độc lập; không bật workers=2 làm mặc định toàn cục mà giữ cơ chế hermetic-only opt-in.
- Browser native check không chạy vì không có giao diện UI sản phẩm; HTML report sử dụng kiểm chứng tĩnh Archify.

**Lệch spec chờ duyệt:** Không có.

**Git:** Đã commit trên nhánh `feature/toi-uu-runtime-toan-dien`.

## Thời gian

Request `2026-11-07-0928-toi-uu-runtime-toan-dien` · lane full · opened at 2026-11-07T09:31:42+07:00

| Phase | Wall clock | API request | Tool wait | Background job | Observed union | Unattributed | Times entered |
|---|---|---|---|---|---|---|---|
| idle | 5s | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| analyze | 7 min | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| spec | 1h 02min | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| plan | 1h 52min | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| Total | 3h 02min | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] |  |

Model compute time is unavailable (`model_giay=null`). API includes network/provider latency; tool time is host wait. Observed metrics may overlap; unattributed time is not assumed user/model time.
Transcript attribution: project_window. Complete covers selected supported observations only.
- api_request_seconds: missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema;no_confirmed_span_in_window
- tool_call_seconds: conflicts,unknown_events,unreadable_or_uncertain_source;no_confirmed_span_in_window
- background_job_seconds: schema_has_no_confirmed_lifecycle
- observed_union_seconds: conflicts,unknown_events,unreadable_or_uncertain_source;missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema;no_confirmed_span_in_window
- unattributed_seconds: wall_minus_observed_union;conflicts,unknown_events,unreadable_or_uncertain_source;missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema;no_confirmed_span_in_window

## Thân PR (soạn sẵn)

**Tóm tắt:** Tối ưu hóa runtime TDQ Workflow theo danh mục P0/P1/P2; bổ sung cơ chế hermetic promotion và giữ synchronous fail-safe cho Graphify extract.
**Trước/Sau:** Bản xem trước planned `../spec/2026-11-07-0928-toi-uu-runtime-toan-dien-preview.html`; báo cáo HTML chi tiết tại `docs/tdq/reports/2026-11-07-0928-toi-uu-runtime-toan-dien.html`.
**Đã kiểm:** Toàn bộ test suite liên quan đến finish, lsp, test process, receipt, runtime bench và hooks PASS 100%.
**Rủi ro hồi quy:** Các cơ chế tối ưu đều có fail-safe quay về serial/synchronous khi phát hiện bất thường, bảo đảm độ tin cậy tuyệt đối của workflow.
<!-- tdq-archify-binding:start -->
<!-- manifest: 2026-11-07-0928-toi-uu-runtime-toan-dien.manifest.json -->
<!-- manifest_digest: 1ef5d3359d6e78bd6e25994fa98018f5716eceaecb37c69ea1653c346cd11325 -->
<!-- tdq-archify-binding:end -->