# MINI-PLAN — Report trực quan chuẩn cho cả hai lane
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Ngày: 2026-11-03 · Lane: quick · Trạng thái: HOÀN THÀNH

## Phạm vi
- In: Express chuyển `implement/QC → report → idle`; Deep và Express dùng Markdown + HTML Archify report chuẩn.
- Out: không thêm phase/state key/cổng duyệt/renderer/worktree role; không đổi preview thiết kế đã duyệt.
- Bỏ B0: state/report/Archify đã có tiền lệ và component tái dùng.
- Bỏ B2: không có API, thư viện hoặc hành vi ngoài repo chưa biết.
- Before/After: `docs/tdq/plan/2026-11-03-0715-express-report-flow.html`.

## Task
- [x] T1 Red: khóa Express `phase=report`, một approval gate, context không đóng sớm.
  - Chạm: `tests/test_phase_table.py`, `tests/test_context_hooks.py`, `tests/test_quick_qc.py`
  - Test: `python -m pytest tests/test_phase_table.py tests/test_context_hooks.py tests/test_quick_qc.py -q`
- [x] T2 Green: phase/report transition và luật Express dùng report chung.
  - Chạm: `scripts/tdq_state.py`, `skills/tdq-intake/SKILL.md`, `skills/tdq-intake/references/quick-lane.md`, `skills/tdq-conventions/references/phases.md`
  - Test: test T1 xanh + `python scripts/tdq_state.py phases-doc`
- [x] T3 Red→green: report Markdown + HTML Archify bắt buộc cho cả hai lane, evidence thực tế và fallback trung thực.
  - Chạm: `skills/tdq-build/references/report-template.md`, `skills/tdq-build/references/archify-lifecycle.md`, `tests/test_report_visual.py`
  - Test: `python -m pytest tests/test_report_visual.py -q`
- [x] QC1.1 Red→green: chặn Quick đóng `idle` trước `report` ở CLI; tránh lách phase mới.
  - Chạm: `scripts/tdq_state.py`, `tests/test_state.py`
  - Test: `python -m pytest tests/test_state.py -q -k quick_report_transition`

## Definition of Done
- [x] Q1 Express hiển thị `quick_analyze → quick → report → idle`; không chuyển trực tiếp `quick → idle`.
- [x] Q2 Quick vẫn chỉ `CONG_THEO_LANE["quick"] == ("quick",)`; report không approval mới.
- [x] Q3 Cả hai lane tạo `reports/<slug>.md` và `reports/<slug>.html`; HTML có Before/After thực tế, task/DoD, QC, đầu ra, giới hạn.
- [x] Q4 HTML dùng Archify hiện có; lỗi tool dùng fallback ghi rõ, không link output thiếu/stale.
- [x] Q5 Phase docs sinh từ `PHASE_TABLE`; test vùng chạm, doc lint và token budget xanh.

## QC
- Q1 PASS — `python -m pytest tests/test_state.py -q -k quick_report_transition`: 1 pass; `phase_key`: quick_analyze → quick → report → idle; CLI chặn `implement → idle`.
- Q2 PASS — `python -m pytest tests/test_phase_table.py -q`: Quick giữ một gate; report không có approve target.
- Q3 PASS — `python -m pytest tests/test_report_visual.py -q`: 3 pass; report chung được quy định cho hai lane, Markdown + HTML độc lập. HTML của request này được dựng trong phase report.
- Q4 PASS — `python scripts/tdq_archify.py check`: ready=true; `archify-lifecycle.md` dùng `working-tree` hợp lệ, fallback ghi rõ nếu lỗi/stale.
- Q5 PASS — `python -m pytest tests/test_report_visual.py tests/test_state.py tests/test_phase_table.py tests/test_context_hooks.py tests/test_quick_qc.py tests/test_tdq_archify.py tests/test_archify_artifacts.py -q`: 220 passed, 58 subtests; `doc_lint.py` 0 lỗi; `token_budget.py --kiem` xanh; phases.md khớp generator.
- QC ultra smoke: `python -m pytest tests/test_e2e_chain.py tests/test_context_hooks.py tests/test_tdq_archify.py -q`: 85 passed, 18 subtests.
- Eval mechanism: 8 A/B trials, baseline 3/4 pass, candidate 4/4 pass; `check_eval_gate(..., stage='pre_report')`: PASS complete_evidence. Trial source tại `docs/tdq/artifacts/2026-11-03-0715-express-report/`.
- QC độc lập: agent trong worktree rỗng báo FAIL do không thấy diff/plan; giới hạn phạm vi cách ly, không phải bằng chứng sản phẩm FAIL. Kiểm lại tại root bằng các lệnh trên.
- Preview Trước/Sau đã duyệt hiện stale do plan tick và mã nguồn thay đổi; giữ nguyên preview, không liên kết như chứng cứ hiện tại.
<!-- tdq-archify-binding:start -->
<!-- manifest: 2026-11-03-0715-express-report-flow.manifest.json -->
<!-- manifest_digest: 2a2db8dbc687e99c35d95fa13155c96fb9afba2ef1742c473183b220e8769c99 -->
<!-- tdq-archify-binding:end -->