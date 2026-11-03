# SPEC — Graphify full extraction, wiki provenance và selector tìm kiếm

Ngày: 2026-10-20 · Bản: 1.2 · Brief: ../brief/2026-10-20-0029-cap-nhat-tim-kiem-graphify.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

## Mục lục

- 1. Mục tiêu & phạm vi
- 1b. Lộ trình
- 2. Đầu ra cụ thể
- 2b. Ranh giới module
- 3. Cách tiếp cận & lý do
- 3b. Năng lực & công cụ
- 4. Yêu cầu bắt buộc
- 5. Ràng buộc & rủi ro
- 6. QC & Definition of Done
- 7. Câu hỏi còn mở

## 1. Mục tiêu & phạm vi
- Mục tiêu: chạy full extraction đồng bộ khi custom provider được bật và hợp lệ; xuất wiki derived có provenance; thông báo rõ/fallback LSP + grep khi full lỗi. Nếu provider bị tắt hoặc thiếu config/key, chạy code-only có cảnh báo hướng dẫn cấu hình full + wiki.
- Trong phạm vi: config plugin không secret cho custom provider (`enabled`, endpoint, model, key-env name); `tdq_finish`, bootstrap setup, rung freshness, test/hook/rule 3 tầng, artifact wiki tách input, telemetry thời gian/cost khả dụng, benchmark A/B trước quyết định selector.
- NGOÀI phạm vi: lưu API key vào repo/config; tự đọc credential nội bộ Claude/Codex; thay LSP/grep; dùng wiki generated làm source oracle; đẩy/publish hoặc thay đổi API/dữ liệu người dùng.

## 1b. Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Analysis + interview | CÓ | Đã chốt full, fail-closed, thông báo, wiki và QC full. |
| Research web | BỎ | Semantics extract/wiki có trong package cài cục bộ; không có ẩn số ngoài repo. |
| Spec → plan | CÓ | User duyệt spec là duyệt route; plan xác định file/test và benchmark cụ thể. |
| Benchmark A/B | CÓ | Quy tắc selector chỉ đổi sau số liệu code-only/full/full+wiki cùng gold set. |
| Implement | CÓ | Sửa runner, readiness/freshness, wiki export, thông báo, tests và rule. |
| QC full | CÓ | Test vùng chạm, fail-closed, provenance/freshness và benchmark artifact. |
| QC độc lập (agent) | BỎ | Không thêm khả năng kiểm backend/cost khi không chạy API; QC full vùng chạm là đủ. |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Config provider không secret, runner chọn full hoặc code-only degraded và thông báo hướng dẫn | `docs/tdq/config.json`, `scripts/tdq_graphify.py`, runner liên quan | Test config enabled/disabled/missing key; không secret trong file/log; lệnh/fallback đúng. |
| 2 | Bootstrap và rung 7 theo dõi code-only vs full corpus/doc/wiki freshness | `scripts/tdq_setup.py`, `scripts/tdq_lsp.py` | Test thay code, doc, ignore/config/model marker làm stale; degraded không được đánh full fresh. |
| 3 | Wiki derived tách corpus, provenance/freshness và chặn self-ingest | `scripts/`, `graphify-out/wiki/`, tests | Test output wiki có manifest/nguồn; export không được index trở lại input. |
| 4 | Benchmark A/B và báo cáo selector | `evals/`, `docs/tdq/bench/`, rule 3 tầng | Cùng gold ghi retrieval, context, token/tool-call nếu đo được; selector không đổi nếu evidence chưa đủ. |
| 5 | Quy tắc tìm kiếm và tests phản ánh vai trò Graphify full+wiki | `skills/tdq-setup/`, `C:/Users/admin/.claude/CLAUDE.md`, tests | Test text/hook đúng selector và fallback; không đổi LSP/grep priority sai loại truy vấn. |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 |
|---|---|---|---|
| Provider & runner | config provider và runner full/degraded | Readiness | 1 |
| Readiness | `scripts/tdq_finish.py`, `scripts/tdq_setup.py`, `scripts/tdq_lsp.py`, tests riêng | Provider & runner | 2 |
| Wiki provenance | script runner, `tests/` riêng | Provider & runner, readiness | 3 |
| Benchmark & selector | `evals/`, `docs/tdq/bench/`, `skills/tdq-setup/`, `tests/` rule | Provider & runner | 4, 5 |

## 3. Cách tiếp cận & lý do
- Chọn: config `docs/tdq/config.json` chỉ lưu `GRAPHIFY_CUSTOM_PROVIDER` gồm `enabled`, `endpoint`, `model`, `api_key_env`; key chỉ đọc từ environment có tên được cấu hình. Runner xác thực config/key trước transaction.
- Khi provider enabled và endpoint/model/key hợp lệ: detect input → full extract qua OpenAI-compatible provider → wiki export → manifest fingerprint → fresh. Lỗi trong nhánh này fail-closed, in fallback LSP + grep.
- Khi provider disabled, config thiếu/sai hoặc environment thiếu key: chỉ extract code-only, in thông báo nêu config/env còn thiếu và ví dụ an toàn; manifest ghi degraded, không được coi full graph/wiki fresh.
- Vì: `--code-only` bỏ semantic docs nhưng vẫn là fallback cục bộ khả dụng; key không được ghi repo/config/log. Wiki chỉ tạo sau community analysis và là derived output, nên phải loại khỏi corpus input.
- Selector giữ nguyên theo loại truy vấn: grep cho token chính xác; LSP cho relation/type/rename; chỉ full+wiki fresh mới là context cho khái niệm/rationale/architecture cùng grep và xác minh source. Không đảo selector trước evidence retrieval/context đầy đủ.
- Đã loại: tự đọc credential nội bộ Claude/Codex; ghi key vào config; dùng code-only degraded như full fresh; tuyên bố wiki cải thiện chất lượng chưa benchmark.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `tdq-intake` | plugin:tdq-workflow | NỀN | Đã mở request và khảo sát. |
| `tdq-spec` | plugin:tdq-workflow | DÙNG | Soạn/duyệt spec này. |
| `tdq-plan` | plugin:tdq-workflow | DÙNG | Chia file chạm/test sau duyệt spec. |
| `tdq-build` | plugin:tdq-workflow | DÙNG | Triển khai và QC full sau duyệt plan. |
| `tdq-setup` | plugin:tdq-workflow | DÙNG | Readiness/freshness rung 7. |
| agent-lsp | MCP | DÙNG | Xác minh symbol/blast radius trước sửa. |
| Graphify CLI/package source | môi trường | DÙNG | Extract/wiki semantics và benchmark artifact. |
| `dataviz` | built-in | DÙNG | Trình bày benchmark nếu có bảng/HTML. |
| Đã xét 1 skill khác | built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc
- Log service bật mặc định: mỗi run ghi timestamp, mode (full/code-only-degraded), provider endpoint đã redaction, model, input fingerprint, duration, outcome, wiki status và lỗi rút gọn; giảm qua `TDQ_LOG=0`.
- Config không chứa API key/token; validator từ chối value/field có tên secret không được phép. Hướng dẫn chỉ nêu tên biến môi trường, không in giá trị.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng; full success/fail và code-only degraded mô phỏng bằng runner fake, không gọi API thật trong unit test.
- Code bám SOLID và rule Python; mọi thay đổi selector giữ fallback khi graph/wiki stale hoặc không dựng được.

## 5. Ràng buộc & rủi ro
Ràng buộc kiến trúc phải giữ:
- `hooks/` được gọi `scripts/`; `scripts/` không import `hooks/` — runner/freshness nằm ở scripts.
- `skills/` chỉ nhắc tên lệnh của scripts, cấm chép logic — rule mô tả selector, logic freshness nằm ở scripts.
- Chỉ `scripts/tdq_state.py` được ghi `docs/tdq/state.json` — trạng thái request không ghi tay.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Custom endpoint/key sai hoặc thiếu | full không chạy, semantic docs cũ | code-only degraded + thông báo chính xác toggle/endpoint/model/key-env cần điền; không đánh fresh full. |
| Key trong config/log | lộ credential | config schema không có key field; validator/test/redaction cấm ghi value. |
| Full extract chậm/chi phí cao | kết thúc turn tăng runtime/token | toggle tắt provider dùng code-only; log time/cost khả dụng; benchmark trước selector. |
| Wiki tự ingest hoặc stale | rationale giả, graph phình | output tách corpus; manifest fingerprint và test self-ingest. |
| Graph docs đầy nhiễu | context không chính xác | không đổi selector trước benchmark; LSP/grep giữ priority theo loại truy vấn. |
| Secret API | rò log | chỉ log trạng thái backend/model, không log key/token raw. |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS | Đo trước | Dự phòng nếu trượt |
|---|---|---|---|---|
| Q1 | Provider config & runner | Enabled + endpoint/model/key-env hợp lệ chạy full không `--code-only`; disabled/missing/sai key chạy code-only degraded, báo hướng dẫn, không log secret | Baseline runner chỉ bridge Claude env; 0 config custom provider | Giữ code-only degraded và selector không dùng wiki/full stale. |
| Q2 | Freshness/provenance | Thay đổi code/doc/ignore/provider endpoint/model/wiki-input đều stale; artifact output không thành input; degraded không được ghi fresh full | Baseline rung 7 chỉ so code mtime; 0 marker wiki | Bỏ artifact wiki khỏi selector khi provenance thiếu. |
| Q3 | Benchmark A/B | Ba cấu hình cùng gold ghi P/R/F1, P@5/MRR, context, runtime và số tool/token nếu backend trả usage | Baseline code-only sample: scorer P@5 0.200, R@5 0.833, MRR@10 0.554; CLI F1 0.250 | Selector giữ nguyên; báo evidence thiếu, không suy diễn. |
| Q4 | Hồi quy workflow | Unit/regression vùng chạm xanh; lỗi semantic hiện trực tiếp và không dùng graph cũ như fresh | Baseline full suite gần nhất chưa chạy cho request; QC full yêu cầu `tdq_test` tính bán kính | Sửa tối đa 3 vòng; quá cap pause `tran-qc`. |

DoD: config provider không secret quyết định full vs code-only degraded; full + wiki chỉ fresh khi fingerprint/provenance đủ; config/key thiếu có hướng dẫn và không tin semantic artifact cũ; lỗi full khi provider hợp lệ vẫn fail-closed LSP+grep; benchmark quyết định selector bằng evidence; không thay LSP/grep priority; test/rule/docs cập nhật và QC full xanh.

## 7. Câu hỏi còn mở

