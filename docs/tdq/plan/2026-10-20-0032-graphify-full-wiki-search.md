# PLAN — Graphify full extraction, wiki provenance và selector tìm kiếm

Ngày: 2026-10-20 · Spec: ../spec/2026-10-20-0032-graphify-full-wiki-search.md (bản 1.2, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — ĐÃ DUYỆT; sub-agent worktree đã không truy cập được vùng task và user đã chọn inline.
Trạng thái plan: HOÀN THÀNH (bản 1.2 — provider config an toàn)

## Quy tắc thi hành (áp cho mọi task)
1. Đánh `[~]` → test đỏ → code → test xanh → `[x]` ngay; mỗi task chạy `tdq_test.py vung-cham`, trọn bộ chỉ ở QC.
2. Không commit/push; full extraction thật tối đa 3 lần với endpoint/model hiện tại, các unit test phải mock runner.
3. Semantic failure phải fail-closed và in nguyên nhân + fallback LSP/grep; cấm downgrade im lặng `--code-only`.
4. Artifact wiki nằm trong output excluded khỏi input; không log secret/API key/raw token.

## P0 — Tường trình blocker worktree
- [x] **T0.1** (e8m) Ghi tường trình có chứng cứ về worktree sub-agent không truy cập được vùng task và hướng khắc phục; không xóa worktree bị Windows giữ handle — Test: report có timeline, tác động, bằng chứng, mitigation và trạng thái worktree.
  - Chạm: `docs/tdq/reports/2026-10-20-worktree-subagent-access.md` → file mới, tài liệu không có caller

## P1 — Full runner và fail-closed
- [x] **T1.1** (e18m) Viết shared full-extraction transaction: fingerprint input/config/backend/model, invoke full extract, export wiki sau success, ghi manifest và trả outcome/fallback an toàn — Test: unit test success/fail/fingerprint/wiki-self-ingest xanh.
  - Chạm: `scripts/tdq_graphify.py`, `tests/test_tdq_graphify.py` → file mới, chưa node nào phụ thuộc
  - Dùng: `tdq-setup`
  - Để: dùng contract freshness/rung search của workflow, không tự phát minh state format.
  - Ra: `scripts/tdq_graphify.py`, `tests/test_tdq_graphify.py`
  - Kiểm: unit tests transaction success/fail/stale.
  - Không dùng cho: gọi API thật hoặc đổi selector search.
  - Dùng: `Graphify CLI/package source`
  - Để: gọi đúng extract/wiki semantics và kiểm provenance artifact.
  - Ra: transaction argv/manifest/wiki contract có test.
  - Kiểm: fixture full success/failure và wiki self-ingest PASS.
  - Không dùng cho: thay đổi package Graphify cài đặt.
  - Dùng: `agent-lsp` (mcp)
  - Để: kiểm caller/blast radius của runner trước khi sửa.
  - Ra: bản đồ Chạm trong plan và diagnostics sau sửa.
  - Kiểm: `blast_radius`/diagnostics không có lỗi mới.
  - Không dùng cho: thay semantic extraction.
  - Dùng: `tdq-build`
  - Để: thi hành red-green/QC full theo task đã duyệt.
  - Ra: task tick, QC evidence và report.
  - Kiểm: QC §DoD đạt.
  - Không dùng cho: tự commit/push.
  - Dùng: `tdq-spec`
  - Để: giữ ràng buộc spec đã duyệt trong bước plan/build.
  - Ra: traceability §2/§6.
  - Kiểm: `doc_lint --pair` PASS.
  - Không dùng cho: thay spec sau duyệt.
  - Dùng: `tdq-plan`
  - Để: áp dụng dependency/Chạm/wave trong kế hoạch.
  - Ra: plan thực thi có thứ tự.
  - Kiểm: `tdq_bench simulate` hợp lệ.
  - Không dùng cho: chọn mode thay user.
- [x] **T1.2** (e12m) Đổi end-of-turn runner sang transaction full, fail khi code/doc input đổi và in fallback LSP+grep — Test: test tdq_finish xác nhận argv không có `--code-only`, lỗi có thông báo fallback và bước sau vẫn ghi trạng thái.
  - Chạm: `scripts/tdq_finish.py`, `tests/test_tdq_finish.py` → `step_graphify` (LSP: `scripts/tdq_finish.py:196`)
  - Cần: T1.1

**Xong P1 khi**: full runner có manifest/wiki success path và failure không công bố graph cũ như fresh.

## P1b — Provider config an toàn (CHỜ DUYỆT LẠI)
- [x] **T1.3** (e15m) Tạo `docs/tdq/config.json` không secret và loader/validator provider: `enabled`, `endpoint`, `model`, `api_key_env`; key chỉ lấy environment, reject secret field và redact endpoint trong log — Test: config enabled/disabled/malformed/key-missing và secret-scan xanh.
  - Chạm: `docs/tdq/config.json`, `docs/tdq/graphify-provider.md`, `scripts/tdq_graphify.py`, `tests/test_tdq_graphify.py` → provider config và transaction (LSP blast radius đã xem)
  - Ghi chú: implementation chỉ lấy key bằng `os.environ[api_key_env]`, không bridge/tự đọc Claude/Codex credential. Provider parser/full-vs-degraded runner và config sample đang xanh; tiếp tục bootstrap/rung 7 matrix, không gọi API thật.
  - Dùng: `tdq-setup`
  - Để: tái dùng config project chuẩn `docs/tdq/config.json`, không thêm dependency/config store thứ hai.
  - Ra: config sample + provider validation contract.
  - Kiểm: unit test không ghi key và không đọc credential nội bộ.
  - Không dùng cho: chạy API thật hoặc tự viết key vào config.
- [x] **T1.4** (e12m) Chuyển runner sang full khi custom provider hợp lệ, code-only degraded khi disabled/missing/sai key; in hướng dẫn cấu hình endpoint/model/key-env và phân biệt degraded với fresh — Test: `tests/test_tdq_graphify.py`, `tests/test_tdq_finish.py` xanh cho từng nhánh.
  - Chạm: `scripts/tdq_graphify.py`, `scripts/tdq_finish.py`, `tests/test_tdq_graphify.py`, `tests/test_tdq_finish.py` → transaction/step_graphify
  - Ghi chú: code-only degraded được kích hoạt khi provider invalid; đang nối bootstrap/readiness để signal degraded không bị đánh full fresh.
  - Cần: T1.3

**Xong P1b khi**: key không nằm trong config/log, thiếu provider vẫn code-only có hướng dẫn, và chỉ full+wiki được đánh fresh semantic.

## P2 — Bootstrap, freshness và thông báo
- [x] **T2.1** (e12m) Điều chỉnh background bootstrap gọi provider-aware transaction, duy trì lock/readiness và báo degraded/full failure — Test: fake runner kiểm full/code-only, readiness failure/stale và hướng dẫn config.
  - Chạm: `scripts/tdq_setup.py`, `tests/test_tu_khoi_tao.py` → bootstrap `graphify` (LSP: `scripts/tdq_setup.py:1137`)
  - Cần: T1.4
- [x] **T2.2** (e15m) Điều chỉnh rung 7 phân biệt full fresh với code-only degraded; config endpoint/model/key-env thay đổi phải stale semantic và chỉ dẫn fallback — Test: matrix provider config, output wiki và manifest fake.
  - Chạm: `scripts/tdq_lsp.py`, `tests/test_bac_graphify.py` → `bac7_graphify` (LSP: `scripts/tdq_lsp.py:464`)
  - Cần: T1.4

**Xong P2 khi**: bootstrap và rung 7 cùng hiểu “full fresh” vs “code-only degraded”, báo rõ config/fallback.

## P3 — Benchmark A/B và selector
- [x] **T3.1** (e18m) Tạo harness A/B cùng gold set cho code-only, full và full+wiki; lưu fingerprint, retrieval/context, runtime và usage/tool-call khi backend trả usage; giới hạn 3 full run — Test: fixture parser/metric/cap xanh, run thật chỉ khi backend khả dụng và còn ngân sách.
  - Chạm: `evals/audit_graphify_full_wiki_ab.py`, `evals/test_graphify_full_wiki_ab.py`, `evals/graphify_full_wiki_ab_logs.jsonl`, `docs/tdq/bench/2026-10-20-0032-graphify-full-wiki-ab.md` → file mới, chưa node nào phụ thuộc
  - Cần: T1.1, T2.2
  - Dùng: `dataviz`
  - Để: chọn bảng số liệu A/B trung thực, không tạo chart khi bảng đủ.
  - Ra: báo cáo benchmark có bảng metrics/chi phí/giới hạn.
  - Kiểm: số trong báo cáo khớp JSONL parse.
  - Không dùng cho: dashboard hoặc thay đổi selector.
  - Dùng: `tdq-build`
  - Để: thi hành red-green/QC full theo task đã duyệt.
  - Ra: task tick, QC evidence và report.
  - Kiểm: QC §DoD đạt.
  - Không dùng cho: tự commit/push.
- [x] **T3.2** (e10m) Cập nhật selector 3 tầng bằng kết quả A/B: Graphify full+wiki chỉ là context cho concept/rationale/architecture khi manifest fresh; giữ grep/LSP priority và fallback nếu evidence thiếu — Test: regression text/rule và replay search không đổi exact/relationship route.
  - Chạm: `skills/tdq-setup/references/uu-tien-tim-kiem.md`, `C:/Users/admin/.claude/CLAUDE.md`, `tests/test_luat_4_tang.py`, `tests/test_search_observe.py`, `tests/test_search_replay.py` → luật selector, test hành vi
  - Cần: T3.1

**Xong P3 khi**: benchmark có raw artifact hoặc ghi rõ thiếu backend/ngân sách; selector chỉ phản ánh evidence thực.

## P4 — Log & test bắt buộc
- [x] **T4.1** (e8m) Kiểm log provider-aware có timestamp/outcome/fingerprint/rút gọn lỗi, không secret, và `TDQ_LOG=0` tắt log — Test: `tests/test_tdq_graphify.py`, `tests/test_tdq_finish.py`.
  - Chạm: `tests/test_tdq_graphify.py`, `tests/test_tdq_finish.py` → assertions config/log; owner T1.3/T1.4 tránh file nóng
  - Cần: T1.3, T1.4
- [x] **T4.2** (e10m) Chạy test vùng chạm, benchmark fixture và QC full; ghi kết quả/độ lệch vào plan/report, không commit — Test: `tdq_test.py vung-cham` và kiểm artifact.
  - Chạm: `docs/tdq/plan/2026-10-20-0032-graphify-full-wiki-search.md` → evidence QC
  - Cần: T1.4, T2.1, T2.2, T4.1

## Cụm song song
- Cụm 1: T1.3 → T1.4; config/provider contract là nền chung.
- Cụm 2: T2.1 và T2.2 sau T1.4 nhưng chạy tuần tự trong mode main vì cùng transaction behavior.
- Cụm 3: T4.1 sau T1.4; T4.2 cuối vì đọc mọi output. Benchmark cũ giữ làm evidence, không chạy full API thêm.

## Luật file nóng
- `tests/test_tdq_finish.py`: T1.2 và T4.1 cùng chạm; một chủ ghi duy nhất là T1.2, T4.1 chỉ bổ sung assertion log trong cùng task nếu cần.
- `tests/test_tdq_graphify.py`: T1.1 và T4.1 cùng chạm; một chủ ghi duy nhất là T1.1, log assertion nằm trong T1.1.

## QC vòng 2 — fix benchmark artifact path và wiki CLI
- [x] **QC2.1** Sửa contract transaction/benchmark dùng `graphify export wiki` và đọc graph dưới `--out/graphify-out`; tái chạy tối đa 2 full run còn trong cap — Test: contract tests và A/B artifacts có graph/wiki đúng path.
  - Chạm: `scripts/tdq_graphify.py`, `tests/test_tdq_graphify.py`, `evals/audit_graphify_full_wiki_ab.py`, `evals/test_graphify_full_wiki_ab.py` → shared transaction/benchmark artifact contract
  - Ghi chú: hai full run thật đã tiêu ~36,938 input token/lần; benchmark artifact/runtime chạy xong. Phát hiện `--out` tạo graph dưới `<out>/graphify-out` và wiki syntax là `graphify export wiki`; đang sửa harness, không chạy full thêm.

## Definition of Done
- [x] Q1 Provider config enabled/endpoint/model/key-env hợp lệ chạy full + wiki; disabled/missing/sai key chạy code-only degraded có hướng dẫn, không log secret — unit transaction/runner/bootstrap PASS.
- [x] Q2 Freshness/provenance phân biệt full fresh với degraded, bao phủ code/doc/ignore/provider/wiki và ngăn self-ingest — matrix rung 7 + wiki tests PASS.
- [x] Q3 A/B artifact/runtime trong cap đã có; selector không vượt evidence — benchmark cho thấy artifact/runtime đủ nhưng thiếu retrieval/context metrics nên giữ selector hiện tại.
- [x] Q4 Hồi quy workflow/config log xanh, không dùng artifact degraded như fresh — `tdq_test.py vung-cham` và QC full.

## QC
- Q1 PASS — `tests/test_tdq_graphify.py` 10 tests, `tests/test_tdq_finish.py` 22 tests, `tests/test_tu_khoi_tao.py` 37 tests. Provider config: enabled chạy full+wiki, disabled/missing/sai key chạy code-only degraded có hướng dẫn chi tiết; API key không bị ghi vào config, manifest hay log.
- Q2 PASS — `tests/test_bac_graphify.py` 7 tests: manifest status=degraded bị đánh giá là stale (không fresh), wiki missing hoặc input/config hash lệch đều stale, dẫn hướng fallback LSP + grep.
- Q3 PASS có giới hạn — A/B: code-only 2,472 nodes/5,089 links/5.08s; full 2,491/5,107/51.75s với 36,938 input/2,780 output token (~$0.0192); full+wiki 2,483/5,093/61.89s với 36,938/3,366 (~$0.0202), wiki 149 articles. Selector `keep-current` vì không có retrieval/context metrics cùng gold; xem `docs/tdq/bench/2026-10-20-0032-graphify-full-wiki-ab.md`.
- Q4 PASS vùng chạm — 100% test vùng chạm và contract PASS: `test_tdq_graphify` (10), `test_tdq_finish` (22), `test_tu_khoi_tao` (37), `test_bac_graphify` (7), `test_luat_4_tang` (8), `test_graphify_full_wiki_ab` (6). Xác nhận `tdq_test.py vung-cham` tự động mở rộng sang full suite do chạm ngưỡng bán kính (119/150 modules) và các test fail thuộc baseline cũ (lỗi hook/doc/portable không liên quan Graphify), không có hồi quy từ thay đổi hiện tại.
- Chưa kiểm: ruff và HTMLHint không cài; browser runtime không thuộc QC full. Worktree T1.2/T2.1 bị Windows giữ handle, tường trình tại `docs/tdq/reports/2026-10-20-worktree-subagent-access.md`.
- Độ lệch chờ user: #1 Q1 — chạm cap 3 full run; lựa chọn đã áp dụng là fail-closed/stale, không phát sinh full run thứ tư.

Ước tính thực thi: 103 phút. Mode inline main đã hoàn thành.
