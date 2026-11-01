# Kiểm chứng TDQ Workflow — tổng hợp bàn giao
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-10-31 · Request: `2026-10-27-1846-kiem-chung-tang-toc` · [QC](../qc/2026-10-27-1846-kiem-chung-tang-toc.md) · [Bản HTML](2026-10-27-1846-kiem-chung-tang-toc.html)

<!-- results -->
## Kết quả

Full fresh cuối: **3594 PASS, 8 skip, 3602 case**, 0 fail/error/xfail/xpass; đủ 3306 case gốc và thêm 296, không remap/missing/duplicate. Runner wall **1117.67 giây**; [result JSON](../cache/test-runs/c030d75ca44ab99e/e23f6ac6de544713b9cc3c68b5224dda/result.json) giữ số gốc 1117.6745853999746, [receipt](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/runs/QC-F1-final-after-QC3-20261031-6add68337dd44ca9b785b1603918f786/receipt.json) xác nhận quyền thường, guard sạch, cleanup complete. Source: `81c1946345d8495ef32dbb3924de801020c957c5599918b9c3d4317c5f3278ad`.

D1–D8 semantic PASS; D11 PASS trong phạm vi correctness/runtime/architecture, [QC độc lập](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/qc-final-user-waiver.md) có 0 finding chưa xử lý. D9/D10 **SKIPPED_USER** theo yêu cầu “có thể skip bench mà tổng hợp cho tôi ko?” và [waiver](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/benchmark-user-waiver-20261031.md). Các benchmark còn thiếu đã dừng; không kết luận phần trăm tăng tốc hoặc median giảm 20%.

[Runtime cuối](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/runtime-final.json): 6/6 smoke fixture bằng process thật đạt ngân sách 120 giây/scenario; nhãn raw là simulation. Thời gian dưới đây làm tròn 6 chữ số, số gốc nằm trong JSON.

| Scenario | Giây | Kết quả/phạm vi |
|---|---:|---|
| process-timeout | 3.422056 | PASS · simulation |
| process-cancel | 0.641515 | PASS · simulation |
| join | 5.785336 | PASS · simulation |
| owner-crash | 5.926354 | PASS · simulation |
| freshness | 5.685250 | PASS · simulation |
| transcript | 0.353202 | PASS · simulation |

<!-- raw-samples -->
## Mẫu thô và hồ sơ lịch sử

Các dòng sau là Full scope lịch sử, không phải bộ A/B đã chứng nhận. Cột source là prefix fingerprint của runner từng mẫu; raw JSON chứa key đầy đủ. Không gộp các source hoặc dùng các timing này suy ra hiệu quả của source bàn giao.

| Hồ sơ | Workers | Wall giây | Kết quả child/raw | Source key | Tình trạng bộ mẫu |
|---|---:|---:|---|---|---|
| [interrupted-20261031-1905](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/benchmark-full.interrupted-20261031-1905.json) | 1 | 1179.746893 | [INCOMPLETE: 3593 pass + 8 skip / 3601](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/raw-e29c206a/0/df7ed806ebc94b09b923d0e46534c589/result.json) | `2ebc8c54e2f2` | Ngắt; source/environment đổi; còn thiếu 5/6 mẫu |
| [parity-failed-20261031](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/benchmark-full.parity-failed-20261031.json) | 1 | 1113.663399 | [PASS: 3593 pass + 8 skip / 3601](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/raw-bbb9c700/0/8573a30b75c443dea3ef752a7f9e9abb/result.json) | `bb58af068eef` | Pair không đạt parity; còn thiếu 4/6 mẫu |
| [parity-failed-20261031](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/benchmark-full.parity-failed-20261031.json) | 2 | 610.233829 | [PASS: 3593 pass + 8 skip / 3601](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/raw-bbb9c700/1/fa7edc0fa9af4c6eb0bcdc584312c809/result.json) | `bb58af068eef` | Pair không đạt parity; còn thiếu 4/6 mẫu |
| [config-drift-QC3-20261031](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/benchmark-full.config-drift-QC3-20261031.json) | 1 | 1159.991913 | [PASS: 3594 pass + 8 skip / 3602](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/raw-5cc9afd1/0/839110b0b0b546c996ed9f55add3e439/result.json) | `6c21a4434b3b` | Child PASS; harness FAIL config_guard; còn thiếu 5/6 mẫu |

Giữ [receipt lượt ngắt](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/runs/benchmark-full-after-writers-stopped-20261031-5ed8df791a8c45e2a2376e6d27d5eea1/receipt.json), [receipt parity fail](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/runs/benchmark-full-second-confirmation-20261031-600569d1c8a04060afbab87731124f12/receipt.json) và [receipt config drift](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/runs/benchmark-full-final-after-QC3-9e893fa657584476a8a85ee20c8110ae/receipt.json). Pair cũ có 293 case khác metadata; QC3 đã sửa producer/fixture, nhưng không dùng lại mẫu cũ để chứng nhận parity source cuối.

<!-- limitations -->
## Giới hạn và thời gian ghi nhận

8 skip đều có reason/capability trong result: 3 symlink, 4 giới hạn POSIX/permission, 1 CLI không có argparse help. POSIX chưa được chứng nhận trên host thật. Runtime simulation không thay số đo toàn workflow/log thật; nhãn `PERFORMANCE_MET` chỉ nói ngân sách smoke. Ruff unavailable.

D12 gate gốc còn yêu cầu benchmark nên chưa được gọi PASS; component `verify_report` kiểm nội dung/link/browser theo waiver riêng. Kiểm browser bằng Chrome DevTools MCP ở viewport desktop 1440×900 và mobile 375×812; xem [bằng chứng trình duyệt](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/report-browser.json) và [kết quả kiểm phạm vi tổng hợp](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/summary-scope-validation.json). Đây là viewport trình duyệt, không phải kiểm trên thiết bị vật lý.

[Timing output](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/timing-report-summary.txt) dưới đây được giữ nguyên. Wall có cả thời gian chờ và phần chưa quy nguồn; không gọi 98 giờ implement là CPU/compute hoặc công sức model.

Request `2026-10-27-1846-kiem-chung-tang-toc` · lane full · opened at 2026-10-27T19:02:05+07:00

| Phase | Wall clock | API request | Tool wait | Background job | Observed union | Unattributed | Times entered |
|---|---|---|---|---|---|---|---|
| idle | 5s | — [partial] | 1s [partial] | — [unavailable] | 1s [partial] | 4s [partial] | 1 |
| analyze | 9 min | — [partial] | 1 min [partial] | — [unavailable] | 1 min [partial] | 8 min [partial] | 1 |
| spec | 26 min | — [partial] | 34s [partial] | — [unavailable] | 34s [partial] | 26 min [partial] | 1 |
| plan | 8 min | — [partial] | 13s [partial] | — [unavailable] | 13s [partial] | 7 min [partial] | 1 |
| mode | 56s | — [partial] | 2s [partial] | — [unavailable] | 2s [partial] | 54s [partial] | 1 |
| implement | 98h 46min | — [partial] | 3h 18min [partial] | — [unavailable] | 3h 18min [partial] | 95h 27min [partial] | 1 |
| Total | 99h 29min | — [partial] | 3h 20min [partial] | — [unavailable] | 3h 20min [partial] | 96h 08min [partial] |  |

Model compute time is unavailable (`model_giay=null`). API includes network/provider latency; tool time is host wait. Observed metrics may overlap; unattributed time is not assumed user/model time.
Transcript attribution: project_window. Complete covers selected supported observations only.
- api_request_seconds: missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema;no_confirmed_span_in_window
- tool_call_seconds: conflicts,missing_pairs,unknown_events,unreadable_or_uncertain_source
- background_job_seconds: schema_has_no_confirmed_lifecycle
- observed_union_seconds: conflicts,missing_pairs,unknown_events,unreadable_or_uncertain_source;missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema
- unattributed_seconds: wall_minus_observed_union;conflicts,missing_pairs,unknown_events,unreadable_or_uncertain_source;missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema

<!-- before-after -->
## Trước và sau

| Module | Trước | Sau và giới hạn |
|---|---|---|
| O1 — manifest/result | Đếm tổng hợp, Full cũ có nguy cơ thiếu hàm pytest | Từng case/phase/subtest có ID và verdict; đối chiếu đủ baseline. |
| O2 — process/helper | Worker tự động, fixture và cleanup chưa đủ cô lập | Mặc định 1 worker; temp riêng, timeout/cancel có ownership; tokenizer portable. |
| O3 — receipt/join | Chạy lặp, thiếu proof để reuse | Fingerprint, eligibility default-deny, lease/nonce và provenance executed/reused/joined; correctness đã kiểm. |
| O4 — readiness/batch | Lặp probe/đọc tuần tự | Cache phần tĩnh opt-in, live checks giữ nguyên; batch chỉ các read độc lập. |
| O5 — transcript | Parse lại toàn bộ | Cache trace từng file sau hash toàn bytes; tính lại filter/dedup/quality, giữ trạng thái partial. |
| O6 — đo A/B | Chưa có bộ mẫu đủ đại diện | Có CLI/verifier và lưu mẫu thô; D9/D10 SKIPPED_USER, chưa chứng nhận hiệu quả. |
| O7 — QC/bàn giao | Evidence phân tán | Full và runtime bind source, QC độc lập, MD/HTML và kiểm browser/link theo phạm vi điều chỉnh. |

QC1 sửa project anchor của helper, cô lập Archify/browser, UTF-8/scanner binary và registry luật batch. QC2 sửa fixture sinh token lock để không dùng repo/HOME thật. QC3 giữ metadata subtest canonical trước xdist và reason sau hook; sắp thứ tự nhánh, dùng nhãn payload ổn định, giữ đủ scenario/assertion.

<!-- recommendations -->
## Khuyến nghị

Giữ **1 worker**, reuse/readiness/transcript cache **off**. Các đường opt-in đã có kiểm correctness nhưng lợi ích hiệu năng chưa được chứng nhận. Nếu cần đánh giá sau này, đo bộ mẫu mới trên cùng source và môi trường; không lấy mẫu lịch sử làm kết luận. [DoD D1–D8](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/dod-checks-final-QC3.json), [QC máy đọc](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/qc-final-user-waiver.json), [receipt runtime](../artifacts/2026-10-27-1846-kiem-chung-tang-toc/runs/runtime-final-after-QC3-ed06898fbca3436baf4a965c036e004a/receipt.json).

<!-- rollback -->
## Tắt tối ưu và quay về fresh

```sh
python scripts/tdq_test.py tron-bo --repo . --workers 1 --fresh --reuse off --timeout-seconds 1800
```
Giữ `--readiness-cache off` cho setup/LSP và `--transcript-cache off` cho timing. Không cần xóa cache hoặc sửa cấu hình cá nhân. Git chưa commit/push/merge; nhánh giữ `bugfix/kiem-chung-tang-toc`.
