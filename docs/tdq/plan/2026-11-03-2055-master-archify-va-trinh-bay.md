# PLAN — Master kiến trúc Archify có luồng chi tiết

Ngày: 2026-11-04 · Spec: ../spec/2026-11-03-2055-master-archify-va-trinh-bay.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — ĐỀ XUẤT, user chốt ở cổng mode. Mô phỏng với hệ số agent 1.5 trên 8 task: main 16.3 phút, đội 10.2 phút, chênh 6.1 phút; đây là mô hình hiệu chuẩn lịch sử, không hứa wall-clock request. 3 task giao/5 task leader giữ, 3 wave; file nóng `tdq_archify.py` được xếp theo phụ thuộc, không giao đồng thời.
Trạng thái plan: CHỜ DUYỆT

## Quy tắc thi hành

- Chỉ làm master Archify; không sửa engine Archify ngoài repo, soul, setup, user-instruction hoặc style của spec/report/chat (request sau). Không thêm hook/phase/state key/dependency mới.
- Một task: đánh `[~]` trước, test đỏ thật, code nhỏ nhất, chạy vùng chạm, đánh `[x]` ngay sau PASS. Không commit/push khi chưa được user yêu cầu.
- Test state dùng `TDQ_PROJECT_DIR` trỏ fixture tạm, không sửa state request thật. Giữ no-op cho master current và last-good khi render fail. Mọi lỗi/fallback có log timestamp theo service có sẵn.
- Preview Before/After đã duyệt: `docs/tdq/spec/2026-11-03-2055-master-archify-va-trinh-bay-preview.html` + manifest; kiểm binding trước code, không sửa binding approved để che đổi thiết kế.

## Thiết kế Trước vs Sau

| Khía cạnh | Trước | Sau |
|---|---|---|
| Master | `index.html` tĩnh liệt kê 6 view rời, native node chỉ mở Passport/focus | master overview + thẻ/link cạnh sơ đồ, click mở modal diagram con đúng target trong cùng HTML |
| Freshness | `tdq_finish` mark stale; sync thủ công; candidate con ngoài fingerprint | kiểm model/candidate/child/source; request đổi source refresh+verify trước report, stale/fallback rõ nếu không dựng được |
| Evidence | graph call edge có thể bị diễn giải thành nghiệp vụ | bước flow có source file/test hoặc “chưa xác minh”; không tuyên bố runtime trace |

## P1 — Khóa phép đo và hợp đồng

- [x] **T1.1** (e8m) Lập eval-plan/corpus/baseline cho thay đổi skill/lifecycle trước code — Test: `python scripts/tdq_skill_eval.py plan --plan docs/tdq/artifacts/2026-11-03-2055-master-archify-va-trinh-bay/eval-plan.json`
  - Ra: corpus các ca master current/stale, drill-down, thiếu evidence, engine fail; snapshot baseline và ngưỡng chất lượng có provenance, không đánh đồng keyword test với hiệu quả model.
  - Dùng: `workflow-authoring`
  - Để: tổ chức review/QC độc lập hữu hạn sau khi có diff; không dùng Workflow ghi state/Git.
  - Ra: eval-plan và log accounting trong artifacts request.
  - Kiểm: plan CLI valid, nguồn baseline có hash và tất cả case có oracle.
  - Không dùng cho: chạy paid model hoặc tự waive eval.
- [x] **T1.2** (e14m) Red→green hợp đồng model cho master explainer/card/detail có target và evidence hợp lệ — Test: `python -m pytest tests/test_archify_model.py tests/test_archify_pipeline.py -q`
  - Chạm: `scripts/archify_model.py`, `scripts/tdq_archify.py`, `tests/test_archify_model.py`, `tests/test_archify_pipeline.py` → `validate_model`/`sync_master`, gọi từ CLI và tests (LSP refs + Graphify affected).
  - Cần: T1.1
  - Ra: model mở rộng tối thiểu, sai ID/path/target/source fail trước publish; giữ tương thích model 6 view cũ.
- [x] **T1.3** (e18m) Red→green master HTML overview + thẻ flow mở diagram con qua Archify explainer sẵn có — Test: `python -m pytest tests/test_archify_pipeline.py tests/test_archify_e2e.py -q`
  - Chạm: `scripts/tdq_archify.py`, `tests/test_archify_pipeline.py`, `tests/test_archify_e2e.py` → `_render_views_to_staging`, `_generate_index_html`, `sync_master`; callers CLI/tests.
  - Cần: T1.2
  - Ra: `docs/architecture/index.html` từ bundle staging/atomic, không chèn `onclick` vào native SVG; chỉ thẻ/link cạnh overview; focus/modal/đóng do engine explainer.
  - Dùng: `Archify `explainer` + `tdq_archify.py`
  - Để: dựng thẻ/link và modal native từ schema đã có; adapter xử lý staging/manifest.
  - Ra: master HTML và receipt finalize trong bundle staging.
  - Kiểm: candidate/target validate và render PASS, browser mở diagram con đúng ID.
  - Không dùng cho: sửa engine Archify hoặc tự viết onclick lên SVG native.
  - Dùng: `tdq-browser-test` (mcp)
  - Để: kiểm browser thật thẻ/card, modal, bàn phím/focus, console/network sau khi render fixture; preflight Chrome CDP.
  - Ra: screenshot/receipt fixture an toàn trong artifacts request.
  - Kiểm: browser mở đúng diagram con, Escape trả focus, console/network không lỗi; timeout smoke theo QC ultra.
  - Không dùng cho: gửi source project lên dịch vụ ngoài, Gemini/Zalo hoặc đổi permission.

## P2 — Freshness và workflow lifecycle

- [x] **T2.1** (e12m) Red→green fingerprint của candidate con và source trong master, đồng bộ readback sau publish — Test: `python -m pytest tests/test_archify_artifacts.py tests/test_archify_pipeline.py -q`
  - Chạm: `scripts/archify_artifacts.py`, `scripts/tdq_archify.py`, `tests/test_archify_artifacts.py`, `tests/test_archify_pipeline.py` → `check_manifest`, `check_master_status`, `sync_master` (Graphify affected: CLI/status/finish).
  - Cần: T1.3
  - Ra: đổi model/candidate/child/source -> stale; sửa source đồng thời render -> không claim current; lỗi giữ last-good.
- [x] **T2.2** (e12m) Red→green cổng refresh+verify trước report/merge, `tdq_finish` chỉ check stale; fallback minh bạch khi engine thiếu — Test: `python -m pytest tests/test_archify_finish.py tests/test_archify_workflow_contract.py tests/test_context_hooks.py -q`
  - Chạm: `scripts/tdq_finish.py`, `skills/tdq-build/references/archify-lifecycle.md`, `tests/test_archify_finish.py`, `tests/test_archify_workflow_contract.py`, `tests/test_context_hooks.py` → `step_archify` gọi `mark_stale`; không thêm hook/state key; cập nhật cổng `report`/`idle`.
  - Cần: T2.1
  - Ra: request chạm source không báo report/master current khi thiếu sync+verify; lỗi log theo service có sẵn; không thay modal/render ở task này.
  - Dùng: `tdq-build`
  - Để: buộc lifecycle hiện có đi qua refresh/verify trước report, giữ đúng phase và QC.
  - Ra: quy tắc master trong `archify-lifecycle.md` và test contract.
  - Kiểm: ca stale/current/engine fail trong test chạy thật; không tự ghi status current.
  - Không dùng cho: thêm event/hook hoặc thay TDQ state schema.

## P3 — Model thật và QC ultra

- [x] **T3.1** (e15m) Viết master model/candidate nguồn TDQ hiện tại, chỉ flow có chứng cứ; sync và verify bundle — Test: `python scripts/tdq_archify.py status`
  - Chạm: `docs/tdq/models/master.model.json`, `docs/tdq/models/overview.json`, `docs/architecture/index.html`, `docs/architecture/manifest.json` → master hiện 6 view; thêm flow detail theo source, không vẽ login giả trong TDQ repo.
  - Cần: T2.2
  - Ra: master HTML current với thẻ flow, diagram con có source; docs-only fixture không có code flow; status source-bound.
  - Dùng: `LSP + Graphify + Grep` (mcp)
  - Để: truy flow thật, source và test; kiểm Graphify freshness trước khi lấy edge.
  - Ra: mapping bước→file/line/test trong model/candidate, không gán nghĩa login giả.
  - Kiểm: mỗi bước được kiểm bằng nguồn hiện tại; dữ liệu thiếu ghi “chưa xác minh”.
  - Không dùng cho: suy parameter lineage/HTTP/security từ `calls` edge.
- [x] **T3.2** (e16m) QC độc lập DoD Q1–Q6, browser desktop/mobile và hồi quy trọn bộ nguồn cuối — Test: `python scripts/tdq_test.py tron-bo`
  - Cần: T3.1
  - Dùng: `tdq-browser-test` (mcp)
  - Để: kiểm master HTML đã render ở browser desktop/mobile, thẻ/modal/focus/console/network.
  - Ra: receipt UI + QC độc lập trong artifacts, kết quả full suite có `details_complete=true`.
  - Kiểm: toàn DoD có evidence, không dùng click-only để báo PASS.
  - Không dùng cho: screenshot desktop riêng tư, thay setting Chrome hoặc tắt sandbox.
  - Dùng: `workflow-authoring`
  - Để: QC độc lập hữu hạn theo từng DoD, đọc diff/root đúng, không sửa state/Git.
  - Ra: findings đã xác minh và accounting; nếu thiếu nhánh thì INCOMPLETE.
  - Kiểm: mọi finding có file/line và input→failure hoặc xác nhận không có lỗi; không dự đoán agent chưa xong.
  - Không dùng cho: tự ghi QC PASS hoặc tự miễn eval.

## P4 — Báo cáo

- [~] **T4.1** (e7m) Báo cáo nghiệm thu Markdown + HTML Archify với Before/After và giới hạn thật — Test: `python scripts/tdq_archify.py verify --document docs/tdq/reports/2026-11-03-2055-master-archify-va-trinh-bay.md --manifest docs/tdq/reports/2026-11-03-2055-master-archify-va-trinh-bay.manifest.json`
  - Cần: T3.2
  - Ra: report có timing thật, eval verdict, master current hay stale và lý do; không gộp preview planned với runtime.

## Cụm song song & file nóng

Chuỗi dữ liệu: T1.1 → T1.2 → T1.3 → T2.1 → T2.2 → T3.1 → T3.2 → T4.1. File nóng `scripts/tdq_archify.py` và `tests/test_archify_pipeline.py`: T1.2/T1.3/T2.1 có chủ ghi theo wave; không giao đồng thời. QC read-only có thể chạy khi source đã ổn định. Không gọi `tdq_team merge` nếu cần commit khi user chưa yêu cầu; leader giữ diff và kiểm tích hợp không commit.

## Definition of Done

- [x] Q1 Master có overview + thẻ flow đúng target, click/modal/keyboard/focus/console đạt — `python -m pytest tests/test_archify_pipeline.py tests/test_archify_e2e.py -q`
- [x] Q2 Chi tiết có evidence, thiếu ghi chưa xác minh, không bịa flow — `python -m pytest tests/test_archify_model.py tests/test_archify_pipeline.py -q`
- [x] Q3 Source/model/candidate/child đổi là stale, sync+verify mới current, lỗi giữ last-good — `python -m pytest tests/test_archify_artifacts.py tests/test_archify_pipeline.py -q`
- [x] Q4 Finish check và report/merge refresh hoặc fallback minh bạch, không thêm hook — `python -m pytest tests/test_archify_finish.py tests/test_archify_workflow_contract.py -q`
- [x] Q5 Docs-only/rỗng và engine lỗi an toàn, không dependency/permission mới — `python -m pytest tests/test_archify_pipeline.py tests/test_archify_distribution.py -q`
- [x] Q6 Preview planned, full regression và eval đúng provenance — `python scripts/tdq_test.py tron-bo` + report eval có source-bound; không chạy trọn bộ lần thừa chỉ để tick.

Dự kiến tổng 102 phút tác vụ, không gồm chờ user. Mọi ngưỡng số giữ theo spec đã duyệt, không thêm cap suy đoán.
