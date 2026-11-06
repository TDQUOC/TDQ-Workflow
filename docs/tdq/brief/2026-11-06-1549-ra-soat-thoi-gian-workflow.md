# Brief — Rà soát thời gian TDQ Workflow
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> C:\Users\admin\Documents\Projects\ForAgentCode\Review-TDQWorkflow hãy fanoutsubagent resreach báo cáo trong đây và recheck lại và cho tôi đề xuất cải thiện rút ngắn thời gian xử lí của TDQ-Workflow, cho tôi report đề xuất và check xem cái nào nên đưa về optional thì hãy báo cho tôi thành báo cáo

Đọc lần đầu: chỉ nghiên cứu và viết báo cáo đề xuất; fanout subagents đọc hai report và artefact tại repo `Review-TDQWorkflow`, đối chiếu lại bằng chứng/giả định với TDQ-Workflow hiện hành. Phân biệt wall-clock, thời gian thực thi, thời gian người dùng chờ, model/API/tool partial; đề xuất ưu tiên giảm critical path và thành phần nên optional có guardrail. Không sửa hành vi workflow hay đổi chính sách trước duyệt.

## Hiểu & kiến thức

### Năng lực dùng được

| Công cụ/kỹ năng | Phán quyết | Vai trò |
|---|---|---|
| `tdq-intake`, `tdq-spec`, `tdq-plan`, `tdq-build` | NỀN | Pipeline full cho báo cáo nghiên cứu, không sửa runtime. |
| 3 Explore subagents | DÙNG | Độc lập kiểm runtime, optional, benchmark cohort; hoàn thành 3/3. |
| LSP, Graphify, Grep | DÙNG | Đối chiếu gọi `step_graphify`, impact 2 bước, tài liệu/telemetry. LSP check 7/8, smoke 3/3. |
| Archify | DÙNG | Paired Markdown + HTML report bắt buộc; check `ready=true`. |
| `tdq-lean` | KHÔNG — khác lĩnh vực | Không review diff code, chỉ đánh giá policy. |
| Setup/tavily/browser testing | KHÔNG — không cần thiết | Dữ liệu local, không cài hoặc thao tác UI sản phẩm. |

### Bảng đối chiếu vùng chạm

| Vùng | Phát hiện | Kết luận |
|---|---|---|
| `Review-TDQWorkflow/docs/tdq/reports/2026-11-05-1949-tdq-runtime-audit.md` | Read + 3 subagents | Runtime claim cần phân loại chứng cứ vs đề xuất; các số LSP outlier không tái hiện bằng ledger hiện hành. |
| `Review-TDQWorkflow/docs/tdq/reports/2026-11-05-2026-toi-uu-nam-muoi.md` + `timing.jsonl` | Read + phản biện | Quick n=3 không còn đủ nguồn (timing hiện n=2); 50% wall không được chứng nhận; active-agent chưa đo. |
| `scripts/tdq_finish.py:198-207,300-323` | LSP `find_references(step_graphify)` + Graphify `affected` + Grep | Rebuild Graphify đồng bộ mỗi lần finish thấy code đổi; 300s là timeout ceiling, không là duration đo. |
| `skills/tdq-build/references/report-template.md:31-34`, global CLAUDE.md | Grep + subagent | Markdown + Archify HTML bắt buộc cả hai lane; không tự đặt optional. |
| `skills/tdq-build/references/qc.md:91-100`, `skills/tdq-intake/references/quick-lane.md:31-40` | Grep + subagent | Full fresh bắt buộc ở mức full/ultra; B1 khảo sát 3 chiều quick bắt buộc; không cắt mặc định. |
| `hooks/scripts/search_observe.py`, `skills/tdq-intake/SKILL.md`, `skills/tdq-setup/SKILL.md` | Grep + subagent | Search telemetry hỗ trợ gate, không tắt theo lane; auto-setup mâu thuẫn yêu cầu consent cài mới, nên tách check-only và setup sau duyệt. |

### Quyết định và giới hạn

- Chỉ báo cáo đề xuất; không cài tool, không chạy benchmark, không giảm gate/QC hoặc sửa runtime. Độc lập 3 góc; tổng hợp giữ nguyên bất đồng.
- Chứng cứ kiểm: `Review-TDQWorkflow/docs/tdq/timing.jsonl:1-2` có 2 record, audit runtime 1.192,648s (API 942,715 partial; tool 55,997 partial; union 977,829 partial; unattributed 214,819 partial). Không đồng nhất với snapshot 977,98s hoặc 599,66s trong report giữa phiên.
- Report 50% cohort n=3 nói 14.116s wall, 4.494,8s union → 31,84% trần phần quan sát, nhưng n=3 không tái dựng từ timing hiện hành n=2. Mọi target giảm ≥50% cần đo cohort ≥10 request/bucket, không gán unknown là user/model.
- Full fresh lịch sử 857,25s (2026-11-05); gần đây 800,34s/4.187 ID (2026-11-06) theo `docs/tdq/reports/2026-11-06-1250-han-che-ngat-giua-plan.md:11`, trước bump 0.94.0. Không biến hai mẫu khác source thành benchmark speedup.
- LSP outlier 40,4m/62,8m/19h được report nêu nhưng ledger hiện 96 dòng, duration của hai start_lsp null; để UNCERTAIN, chưa chứng minh p95. Đo start cold/warm trước circuit breaker.
- Phân loại optional: Archify report HTML, approvals, QC full fresh, search telemetry guard là mandatory hiện hành; browser native cho UI bắt buộc, browser check của report nếu không chạy phải ghi fallback; Master sync theo manifest/freshness; model eval opt-in, workers=2/cache auto chỉ sau parity, auto-install chỉ sau consent.
- Nguồn chi tiết ở hai report gốc và paths trong bảng; không dùng transcript có thông tin cá nhân để trích ra report.

### Lộ trình

| Phase | Chạy? | Lý do |
|---|---|---|
| analyze → spec → plan → implement (viết report) → QC → report | CÓ | Full lane đã chọn; 2 cổng duyệt giữ nguyên dù chỉ nghiên cứu. |
| Subagents fanout | CÓ — 3/3 đã làm | Số liệu, policy optional, benchmark độc lập. |
| Benchmark/paid eval | BỎ | User yêu cầu report đề xuất, không triển khai đo mới tốn phút/model. |
| Source edit/release | BỎ | Không nằm trong yêu cầu. |

## Hỏi đáp

1. Pipeline: `1a` — full/deep. User không yêu cầu sửa runtime, chỉ report.
2. Không cần hỏi phạm vi khác: hai report ở thư mục Review và repo đích đã nêu đủ; đề xuất optional chứ không thay luật. QC `full` cho chất lượng tài liệu theo câu trả lời `1a`; không chạy full test vì không sửa code.
3. Không tự làm optional Archify report HTML trái global instruction; nếu user muốn đổi luật này cần request/chấp thuận riêng.
4. Không mở tài khoản/dịch vụ ngoài, không đổi permission hay cài dependency.

