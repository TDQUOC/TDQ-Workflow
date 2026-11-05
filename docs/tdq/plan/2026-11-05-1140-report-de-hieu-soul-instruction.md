# QUICK — Báo cáo dễ hiểu kèm Archify HTML, Soul & Auto-pin User-Instruction

**Ngày:** 2026-11-05 · Brief: ../brief/2026-11-05-1140-report-de-hieu-soul-instruction.md · Lane: quick
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
**Trạng thái:** HOÀN THÀNH
**Ước tính sẽ dùng skill:** tdq-workflow:tdq-build

## Phạm vi
- Bỏ B0: Đã có tiền lệ chạm cùng vùng (`2026-11-03-0715-express-report`, `2026-11-03-1420-phoi-hop-cong-cu`).
- Bỏ B2: Không có phụ thuộc/API bên ngoài repo cần research mới.
- Bỏ vòng phạm vi: Yêu cầu đã chỉ rõ 3 điểm chạm (Report + Archify HTML, Soul, Auto-pin User-Instruction).
- Trong: Chuẩn hóa `report-template.md`, `archify-lifecycle.md`, `tdq_state.py` (`phases.md`): luôn có cặp `reports/<slug>.md` + `reports/<slug>.html` đơn giản, dễ hiểu cho mọi người đọc, trực quan, đầy đủ 4 mục (**Trước request trạng thái/flow**, **Sau request**, **Đã test gì**, **Kết quả test ra sao**); đưa nguyên tắc trình bày đơn giản, dễ hiểu, ngắn gọn nhưng trực quan, đầy đủ thông tin vào `soul.md` + `SKILL.md`; cập nhật `KHOI_HUONG_DAN` trong `tdq_setup.py` + `docs/claude-md-mau.md` và tự động ghim vào `~/.claude/CLAUDE.md` cả khi cài mới (`main` & `--nen`) lẫn khi update version.
- NGOÀI: Không đổi engine Archify, không thêm hook mới, không đụng nội dung riêng của user ngoài `<!-- TDQ:TOOLS -->`.

## Task
- [x] **T1** Chuẩn hóa phase `report` (Markdown + Archify HTML) bắt buộc 4 mục Trước/Sau/Đã test/Kết quả dễ hiểu, trực quan, đầy đủ thông tin — Test: `python -m pytest tests/test_report_visual.py -q`
  - Chạm: `skills/tdq-build/references/report-template.md`, `skills/tdq-build/references/archify-lifecycle.md`, `scripts/tdq_state.py`, `skills/tdq-conventions/references/phases.md`, `tests/test_report_visual.py`
- [x] **T2** Đưa nguyên tắc trình bày đơn giản, dễ hiểu, ngắn gọn nhưng trực quan, đầy đủ thông tin vào Soul & Conventions — Test: `python -m pytest tests/test_soul_rules.py -q`
  - Chạm: `skills/tdq-conventions/references/soul.md`, `skills/tdq-conventions/SKILL.md`, `tests/test_soul_rules.py`
- [x] **T3** Bổ sung chuẩn trình bày & report vào `KHOI_HUONG_DAN` (`tdq_setup.py`, `docs/claude-md-mau.md`) và tự động ghim vào `user-instruction` khi cài mới hoặc update — Test: `python -m pytest tests/test_claude_md_core.py tests/test_auto_update_setup.py tests/test_token_budget.py -q`
  - Chạm: `scripts/tdq_setup.py`, `docs/claude-md-mau.md`, `docs/tdq/token-budget.json`, `tests/test_claude_md_core.py`, `tests/test_auto_update_setup.py`

## Definition of Done
- [x] Khuôn `report` và checklist `tdq_state.py` bắt buộc Markdown + Archify HTML dễ hiểu, trực quan, đủ 4 phần Trước/Sau/Đã test/Kết quả — `python -m pytest tests/test_report_visual.py -q`
- [x] `soul.md` (< 150 dòng) và `tdq-conventions/SKILL.md` có quy tắc trình bày đơn giản, dễ hiểu, ngắn gọn, trực quan, đầy đủ thông tin — `python -m pytest tests/test_soul_rules.py -q`
- [x] `KHOI_HUONG_DAN` đồng bộ `docs/claude-md-mau.md`, tự động ghim vào `CLAUDE.md` khi setup/update và pass khóa token — `python -m pytest tests/test_claude_md_core.py tests/test_auto_update_setup.py tests/test_token_budget.py -q`

## QC
- Q1 test từng task (`T1` + `T2` + `T3`): PASS — `python -m pytest tests/test_report_visual.py tests/test_soul_rules.py tests/test_claude_md_core.py tests/test_auto_update_setup.py tests/test_token_budget.py -q` → `71 passed, 149 subtests passed in 5.83s`
- Q2 DoD "Khuôn `report` và checklist `tdq_state.py` bắt buộc Markdown + Archify HTML dễ hiểu, trực quan, đủ 4 phần Trước/Sau/Đã test/Kết quả": PASS — `python -m pytest tests/test_report_visual.py -q` → `4 passed in 0.07s`
- Q3 DoD "`soul.md` (< 150 dòng) và `tdq-conventions/SKILL.md` có quy tắc trình bày đơn giản, dễ hiểu, ngắn gọn, trực quan, đầy đủ thông tin": PASS — `python -m pytest tests/test_soul_rules.py -q` → `6 passed, 7 subtests passed in 0.10s` (`soul.md` = 142 dòng)
- Q4 DoD "`KHOI_HUONG_DAN` đồng bộ `docs/claude-md-mau.md`, tự động ghim vào `CLAUDE.md` khi setup/update và pass khóa token": PASS — `python -m pytest tests/test_claude_md_core.py tests/test_auto_update_setup.py tests/test_token_budget.py -q` → `61 passed, 142 subtests passed in 5.94s`
- Q5 Smoke & Runtime (`muc_qc=ultra`): PASS — `tdq_setup.ghim_huong_dan_tool` ghim thật vào `~/.claude/CLAUDE.md` và thư mục tạm (`SMOKE_RUNTIME_PIN: PASS, bytes= 8285`), `tdq_archify.py status` → `status="current", reasons=[]`
- Q6 Independent QC Review (`tdq-qc-tester` `ad05e87ce0f2a12e4`): PASS — `71 passed, 149 subtests passed, 0 blocking findings`
<!-- tdq-archify-binding:start -->
<!-- manifest: 2026-11-05-1140-report-de-hieu-soul-instruction-flow.manifest.json -->
<!-- manifest_digest: 75d70098d1b7abea1c7e883fa76d6bfba37413f915811a765f45b394391aa5ba -->
<!-- tdq-archify-binding:end -->