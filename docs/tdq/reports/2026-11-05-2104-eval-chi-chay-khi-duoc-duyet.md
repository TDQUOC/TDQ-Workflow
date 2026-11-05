# Báo cáo — Eval chỉ bật khi người dùng đồng ý

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Trước request (trạng thái/flow):** Plan chạm skill/hook/plugin thì gate eval tự chặn `implement` nếu thiếu eval-plan, chặn `report` nếu thiếu chứng cứ; phải gọi `eval-waive` mới miễn được.

**Sau request (trạng thái/flow):** Eval mặc định tắt. Chỉ khi người dùng yêu cầu và đồng ý, `tdq_state.py eval-enable --by "<lời người dùng>"` ghi người đồng ý/thời điểm vào state; lúc đó hai gate mới kiểm plan và chứng cứ như cũ. `eval-waive` đã bỏ; state cũ có khóa `eval_waiver` vẫn đọc được. Agent không tự đề xuất eval.

**Đã test gì:** 10 test gate (lệnh mới, đầu vào thiếu, gate tắt/bật, state cũ); hồi quy vùng chạm; một lượt full fresh toàn repo trước khi bump version; kiểm chỉ mục, ngân sách token, cấu trúc spec/plan, diff CI và hợp đồng eval. Sau bump, kiểm hai manifest cùng `0.93.0`, Changelog khớp và chạy riêng test đóng gói/gate. [Chi tiết QC](../qc/2026-11-05-2104-eval-chi-chay-khi-duoc-duyet.md).

**Kết quả test:** Gate **10 đạt**; vùng chạm **2.068 đạt, 2 bỏ qua**, 1.150 subtests/412,34 giây; full fresh trước bump **4.168 đạt, 7 bỏ qua**, 2.724 subtests/788,96 giây. Full có **4.175 case ID**: 4.168 đạt + 7 bỏ qua; subtests không cộng thêm. Receipt full `details_complete=true`, `executed=1`, `reused=0`, `joined=0`, nguồn trước/sau trùng ở thời điểm chạy. Sau bump: **48 đạt, 4 subtests** trong test đóng gói/gate; không chạy lại full. Một lượt vùng chạm đầu FAIL do ngân sách token lỗi thời và nguồn đổi giữa lúc chạy; đã sửa rồi chạy lại PASS.

**Đầu ra:** `scripts/tdq_state.py`, 7 file luật, test gate và tài liệu QC · [Bản HTML trực quan](2026-11-05-2104-eval-chi-chay-khi-duoc-duyet.html).

**Giới hạn:** `eval: chưa kích hoạt (opt-in)` cho request này; **0 model trials**, không có kết luận hiệu quả model. `bo_sot=0` nhưng `radius_complete=false`, không coi là chứng nhận bán kính đầy đủ. Full fresh xác nhận nguồn trước bump; sau bump chỉ chạy test đóng gói/gate, không tuyên bố full fresh cho bản `0.93.0`. Preview spec planned đã stale sau khi sửa nguồn; báo cáo HTML mới dùng nguồn working-tree, không coi preview là nghiệm thu. Chưa kiểm browser native cho HTML; chỉ kiểm render/binding tĩnh.

**Lệch spec chờ duyệt:** Không có.

**Git:** Commit triển khai `00417c75`, `9065302b`, `181233e4`, `65ef78c5`; cập nhật tài liệu cuối và bump `0.93.0` sẽ commit theo yêu cầu. Chưa merge, chưa push.

## Thời gian

Request `2026-11-05-2104-eval-chi-chay-khi-duoc-duyet` · lane full · opened at 2026-11-05T21:17:27+07:00

| Phase | Wall clock | API request | Tool wait | Background job | Observed union | Unattributed | Times entered |
|---|---|---|---|---|---|---|---|
| idle | 4s | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| analyze | 3 min | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| spec | 8 min | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| plan | 33 min | 2 min [partial] | 31s [partial] | — [unavailable] | 3 min [partial] | 30 min [partial] | 1 |
| qc | 21 min | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| Total | 1h 05min | 2 min [partial] | 31s [partial] | — [unavailable] | 3 min [partial] | 1h 02min [partial] |  |

Model compute time is unavailable (`model_giay=null`). API includes network/provider latency; tool time is host wait. Observed metrics may overlap; unattributed time is not assumed user/model time.
Transcript attribution: project_window. Complete covers selected supported observations only.
- api_request_seconds: missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema
- tool_call_seconds: conflicts,unknown_events,unreadable_or_uncertain_source
- background_job_seconds: schema_has_no_confirmed_lifecycle
- observed_union_seconds: conflicts,unknown_events,unreadable_or_uncertain_source;missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema
- unattributed_seconds: wall_minus_observed_union;conflicts,unknown_events,unreadable_or_uncertain_source;missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema

## Thân PR (soạn sẵn)

**Tóm tắt:** Eval chuyển sang opt-in có ghi lời đồng ý; bỏ waiver tự miễn, giữ gate cũ khi đã kích hoạt.
**Trước/Sau:** Preview planned `../spec/2026-11-05-2104-eval-chi-chay-khi-duoc-duyet-preview.html` đã stale sau implement; chỉ dùng xem thiết kế, không làm chứng cứ runtime.
**Đã kiểm:** Gate 10 passed; vùng chạm 2.068 passed/2 skipped; full fresh 4.168 passed/7 skipped.
**Rủi ro hồi quy:** Gate bật nhưng thiếu plan/chứng cứ vẫn chặn, test gate và full suite giữ luồng này; chưa có model trial.
<!-- tdq-archify-binding:start -->
<!-- manifest: 2026-11-05-2104-eval-chi-chay-khi-duoc-duyet.manifest.json -->
<!-- manifest_digest: 485c5301d52ea964e757e0227eb331f97e81a5c5e010d5649726f4fce91d3f8f -->
<!-- tdq-archify-binding:end -->