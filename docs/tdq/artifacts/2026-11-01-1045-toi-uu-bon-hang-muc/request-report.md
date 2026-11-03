# REPORT — Tối ưu bốn hạng mục (2026-11-01-1045-toi-uu-bon-hang-muc)

Soul: chất lượng > runtime > context cost · lane full · mode subagent

Source SHA256: 6f03e5bec06c11ed1bc7d9c14609d09ce9f3b55f2fc0b069057c80cce97543bc
Input SHA256: ec60b7816e0f7efc06f5b4784e3fd3f5c3ea0adf604ddbbeaac8cff700e7d7d2

<!-- results -->
## Kết quả

Đã triển khai bốn hạng mục: validation calibration sớm; timeout và ownership tiến trình Codex; giảm công việc lặp trong kiểm thuần; Top20 case/module cùng export offline JSON/MD/HTML. Full: 3657 PASS, 8 SKIP, 3665 case; giữ đủ 3602 case baseline và thêm 63 case. Wall 1030.256894399994 giây; tổng execution phases 1018.7496596999772 giây, hai đại lượng được tách riêng.

<!-- before-after -->
## Thay đổi đã đo

11 ca kiểm thuần có 0 lời gọi subprocess/calibration/Git sau chuyển đổi; mapping giữ 43 assertion anchors. Bốn integration thực vẫn có 403/3/39/18 lời gọi subprocess được observer Python ghi nhận. Đây là audit Python, không phải đếm mọi lần OS tạo tiến trình; không suy ra phần trăm tăng tốc Full.

<!-- raw-samples -->
## Runtime và nguồn số liệu

Bốn scenario thực: calibration-valid 11.3050513s; reject-early 0.3452787s, không đo và không tạo output; timeout-cleanup 2.7218578s với timeout 2s, descendants hết và HOME được dọn; report-offline 1.2800396s, không gọi runner. Mỗi scenario có cap 120s; timeout có ngưỡng 8s gồm cleanup. Calibration dùng private true.cmd fixture trên Windows; không phải kiểm mô hình từ xa.

<!-- limitations -->
## Giới hạn và trạng thái

Benchmark A/B D9/D10 giữ SKIPPED_USER; chưa chứng nhận phần trăm hiệu năng, POSIX hay thiết bị vật lý. Giữ worker1/cacheoff. Các receipt FAIL trung gian vẫn được bảo toàn, chỉ receipt cuối đúng source được dùng chứng nhận. Guard chỉ bỏ qua giá trị usageCount/lastUsedAt đã duyệt; cấu trúc/type/presence và cấu hình khác vẫn được bảo vệ. Metadata workflow còn phase=implement do 11 worktree cũ dirty; không xóa dữ liệu hoặc bypass guard. Chưa commit/push; nhánh codex/toi-uu-bon-hang-muc.

<!-- recommendations -->
## Đề xuất tiếp theo

Dùng Top20 từ mỗi result để chọn vùng tối ưu tiếp; tiếp tục ưu tiên loại bỏ công việc lặp ở kiểm thuần và giữ integration thật. Chưa bật worker/cache mặc định khi chưa có A/B phù hợp. Review độc lập, kết quả Q1–Q8 và browser được lưu riêng, liên kết bên dưới; metadata blocker không được trình bày thành workflow đã đóng.

<!-- rollback -->
## Vận hành và rollback

Đọc report offline bằng python scripts/tdq_test.py report --result <result.json> --out-prefix <prefix>. Kiểm bảo thủ dùng python scripts/tdq_test.py tron-bo --workers 1 --fresh --reuse off. Chưa tạo commit triển khai mới nên chưa có commit rollback; preimages theo task trong integration-backup/, chỉ hoàn nguyên đúng file thuộc request sau khi đối chiếu diff, giữ dữ liệu người dùng.

## Bằng chứng

- [Top20 HTML](slow-tests.html)
- [Top20 Markdown](slow-tests.md)
- [Raw Full result](final-result.json)
- [Full kiểm chứng](QC-F1-check.json)
- [Runtime evidence](runtime.json)
- [Work counters](final-work-proof.json)
- [Case/assertion mapping](case-mapping.json)
- [Workflow blocker](phase-transition-blocker.json)
- [Ngoại lệ đã duyệt](telemetry-exception-approved.md)
- [Review độc lập](independent-qc.md)

## Thời gian

Bảng dưới được chép nguyên output tdq_timing.py show; các giá trị partial/unavailable không được suy đoán.

Request `2026-11-01-1045-toi-uu-bon-hang-muc` · lane full · opened at 2026-11-01T10:50:35+07:00

| Phase | Wall clock | API request | Tool wait | Background job | Observed union | Unattributed | Times entered |
|---|---|---|---|---|---|---|---|
| idle | 14s | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| analyze | 6 min | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| spec | 4 min | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| plan | 12 min | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| mode | 1 min | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| implement | 5h 08min | — [partial] | 18 min [partial] | — [unavailable] | 18 min [partial] | 4h 51min [partial] | 1 |
| Total | 5h 31min | — [partial] | 18 min [partial] | — [unavailable] | 18 min [partial] | 5h 14min [partial] |  |

Model compute time is unavailable (`model_giay=null`). API includes network/provider latency; tool time is host wait. Observed metrics may overlap; unattributed time is not assumed user/model time.
Transcript attribution: project_window. Complete covers selected supported observations only.
- api_request_seconds: missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema;no_confirmed_span_in_window
- tool_call_seconds: conflicts,missing_pairs,unknown_events,unreadable_or_uncertain_source
- background_job_seconds: schema_has_no_confirmed_lifecycle
- observed_union_seconds: conflicts,missing_pairs,unknown_events,unreadable_or_uncertain_source;missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema
- unattributed_seconds: wall_minus_observed_union;conflicts,missing_pairs,unknown_events,unreadable_or_uncertain_source;missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema
