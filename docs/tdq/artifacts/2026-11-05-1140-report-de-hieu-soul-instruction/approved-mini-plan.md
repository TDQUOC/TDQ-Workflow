# QUICK — Báo cáo dễ hiểu kèm Archify HTML, Soul & Auto-pin User-Instruction

**Ngày:** 2026-11-05 · Brief: ../brief/2026-11-05-1140-report-de-hieu-soul-instruction.md · Lane: quick
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
**Trạng thái:** CHỜ DUYỆT
**Ước tính sẽ dùng skill:** tdq-workflow:tdq-build

## Phạm vi
- Bỏ B0: Đã có tiền lệ chạm cùng vùng (`2026-11-03-0715-express-report`, `2026-11-03-1420-phoi-hop-cong-cu`).
- Bỏ B2: Không có phụ thuộc/API bên ngoài repo cần research mới.
- Bỏ vòng phạm vi: Yêu cầu đã chỉ rõ 3 điểm chạm (Report + Archify HTML, Soul, Auto-pin User-Instruction).
- Trong: Chuẩn hóa `report-template.md`, `archify-lifecycle.md`, `tdq_state.py` (`phases.md`): luôn có cặp `reports/<slug>.md` + `reports/<slug>.html` đơn giản, dễ hiểu cho mọi người đọc, trực quan, đầy đủ 4 mục (**Trước request trạng thái/flow**, **Sau request**, **Đã test gì**, **Kết quả test ra sao**); đưa nguyên tắc trình bày đơn giản, dễ hiểu, ngắn gọn nhưng trực quan, đầy đủ thông tin vào `soul.md` + `SKILL.md`; cập nhật `KHOI_HUONG_DAN` trong `tdq_setup.py` + `docs/claude-md-mau.md` và tự động ghim vào `~/.claude/CLAUDE.md` cả khi cài mới (`main` & `--nen`) lẫn khi update version.
- NGOÀI: Không đổi engine Archify, không thêm hook mới, không đụng nội dung riêng của user ngoài `<!-- TDQ:TOOLS -->`.

## Task
- [ ] **T1** Chuẩn hóa phase `report` (Markdown + Archify HTML) bắt buộc 4 mục Trước/Sau/Đã test/Kết quả dễ hiểu, trực quan, đầy đủ thông tin — Test: `python -m pytest tests/test_report_visual.py -q`
  - Chạm: `skills/tdq-build/references/report-template.md`, `skills/tdq-build/references/archify-lifecycle.md`, `scripts/tdq_state.py`, `skills/tdq-conventions/references/phases.md`, `tests/test_report_visual.py`
- [ ] **T2** Đưa nguyên tắc trình bày đơn giản, dễ hiểu, ngắn gọn nhưng trực quan, đầy đủ thông tin vào Soul & Conventions — Test: `python -m pytest tests/test_soul_rules.py -q`
  - Chạm: `skills/tdq-conventions/references/soul.md`, `skills/tdq-conventions/SKILL.md`, `tests/test_soul_rules.py`
- [ ] **T3** Bổ sung chuẩn trình bày & report vào `KHOI_HUONG_DAN` (`tdq_setup.py`, `docs/claude-md-mau.md`) và tự động ghim vào `user-instruction` khi cài mới hoặc update — Test: `python -m pytest tests/test_claude_md_core.py tests/test_auto_update_setup.py tests/test_token_budget.py -q`
  - Chạm: `scripts/tdq_setup.py`, `docs/claude-md-mau.md`, `docs/tdq/token-budget.json`, `tests/test_claude_md_core.py`, `tests/test_auto_update_setup.py`

## Definition of Done
- [ ] Khuôn `report` và checklist `tdq_state.py` bắt buộc Markdown + Archify HTML dễ hiểu, trực quan, đủ 4 phần Trước/Sau/Đã test/Kết quả — `python -m pytest tests/test_report_visual.py -q`
- [ ] `soul.md` (< 150 dòng) và `tdq-conventions/SKILL.md` có quy tắc trình bày đơn giản, dễ hiểu, ngắn gọn, trực quan, đầy đủ thông tin — `python -m pytest tests/test_soul_rules.py -q`
- [ ] `KHOI_HUONG_DAN` đồng bộ `docs/claude-md-mau.md`, tự động ghim vào `CLAUDE.md` khi setup/update và pass khóa token — `python -m pytest tests/test_claude_md_core.py tests/test_auto_update_setup.py tests/test_token_budget.py -q`
<!-- tdq-archify-binding:start -->
<!-- manifest: 2026-11-05-1140-report-de-hieu-soul-instruction-flow.manifest.json -->
<!-- manifest_digest: 75d70098d1b7abea1c7e883fa76d6bfba37413f915811a765f45b394391aa5ba -->
<!-- tdq-archify-binding:end -->