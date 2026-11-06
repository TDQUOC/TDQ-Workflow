# Báo cáo — Giảm dừng giữa plan trên Claude Code

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Trước request (trạng thái/flow):** Plan còn task thì Stop hook nhắc làm tiếp ba lần; lần bốn chỉ báo kẹt chung rồi cho dừng. Khi mở lại session, anchor có task đang làm/đã giao nhưng không chỉ task đầu còn mở.

**Sau request (trạng thái/flow):** Stop nhắc mã task và `Test:` tương ứng (tối đa 300 ký tự); sau ba lần plan không tiến triển, báo số task và việc cần kiểm trước retry, vẫn cho dừng để tránh lặp. Resume/compact chỉ đúng task `[~]` hoặc đầu `[ ]`; task `[>]` đang giao thì bảo chờ, không chạy trùng. Lệch nhỏ bám spec đã duyệt, ghi `lech add` và làm tiếp; commit giữa chừng chỉ để gỡ blocker. `/goal` là lựa chọn người dùng tự xác nhận/bật, không phải cơ chế TDQ tự kích hoạt.

**Đã test gì:** Test đỏ→xanh cho Stop, resume và luật; hồi quy vùng chạm Stop/SessionStart/luật; một full fresh toàn repo; kiểm `doc_index.py`, `token_budget.py`, bản đồ đội, Antigravity và CI không đổi. [QC chi tiết](../qc/2026-11-06-1250-han-che-ngat-giua-plan.md).

**Kết quả test:** Stop **116 passed, 23 subtests**; SessionStart/PromptContext **94 passed, 146 subtests**; luật **29 passed, 329 subtests**. Full fresh **4.180 passed, 7 skipped**, 2.724 subtests, **4.187 case ID**, 793,74 giây pytest/800,34 giây runner; receipt `PASS`, `details_complete=true`, nguồn trước/sau trùng, executed fresh. Hai lượt vùng chạm Stop trước đó INCOMPLETE do Ruff ghi `.ruff_cache` song song; lượt cuối PASS (379 passed). Không dùng lượt INCOMPLETE làm verdict.

**Đầu ra:** `hooks/scripts/stop_gate.py`, `hooks/scripts/session_start.py`, `skills/tdq-build/SKILL.md`, test và QC · [HTML trực quan](2026-11-06-1250-han-che-ngat-giua-plan.html).

**Giới hạn:** Hook chỉ chạy lúc host phát Stop/SessionStart, không cứu API/tool treo giữa lượt; sau ba lần vẫn hạ cấp, không bảo đảm plan luôn xong. `/goal 1a` người dùng đã bật là điều kiện không đo được, không tính bằng chứng hoàn tất. `bo_sot=0` nhưng `radius_complete=false`. `eval: chưa kích hoạt (opt-in)`; chưa có model trial, chưa đo hiệu quả model nhỏ ngoài thực địa. HTML được verify tĩnh, chưa kiểm browser native.

**Lệch spec chờ duyệt:** Không có.

**Git:** Chưa commit thay đổi của request, chưa merge về `dev`, chưa push.

## Thời gian

Request `2026-11-06-1250-han-che-ngat-giua-plan` · lane full · opened at 2026-11-06T12:56:13+07:00

| Phase | Wall clock | API request | Tool wait | Background job | Observed union | Unattributed | Times entered |
|---|---|---|---|---|---|---|---|
| idle | 11s | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| analyze | 8 min | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| spec | 13 min | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| plan | 43 min | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| qc | 14 min | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] | 1 |
| Total | 1h 18min | — [partial] | — [partial] | — [unavailable] | — [partial] | — [partial] |  |

Model compute time is unavailable (`model_giay=null`). API includes network/provider latency; tool time is host wait. Observed metrics may overlap; unattributed time is not assumed user/model time.
Transcript attribution: project_window. Complete covers selected supported observations only.
- api_request_seconds: missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema;no_confirmed_span_in_window
- tool_call_seconds: conflicts,unknown_events,unreadable_or_uncertain_source;no_confirmed_span_in_window
- background_job_seconds: schema_has_no_confirmed_lifecycle
- observed_union_seconds: conflicts,unknown_events,unreadable_or_uncertain_source;missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema;no_confirmed_span_in_window
- unattributed_seconds: wall_minus_observed_union;conflicts,unknown_events,unreadable_or_uncertain_source;missing_pairs,unknown_events,unreadable_or_uncertain_source,unsupported_source_schema;no_confirmed_span_in_window

## Thân PR (soạn sẵn)

**Tóm tắt:** Stop/resume nhắc đúng task khi plan còn việc; giữ lối thoát an toàn sau ba lần không tiến triển, bổ sung luật lệch nhỏ và `/goal` tùy chọn.
**Trước/Sau:** Preview planned `../spec/2026-11-06-1250-han-che-ngat-giua-plan-preview.html` có thể stale sau sửa mã; không dùng làm bằng chứng runtime.
**Đã kiểm:** 116 Stop passed; 94 context passed; 29 luật passed; full fresh 4.180 passed/7 skipped.
**Rủi ro hồi quy:** Hint sai khi plan hỏng, block lặp; test giữ fallback, pause, task `[>]`, trần 3 và reset khi tick.
<!-- tdq-archify-binding:start -->
<!-- manifest: 2026-11-06-1250-han-che-ngat-giua-plan.manifest.json -->
<!-- manifest_digest: d40da62728cc7645268f6e5a610c97244d2014ea0d3c9a72d848bba34255adf6 -->
<!-- tdq-archify-binding:end -->