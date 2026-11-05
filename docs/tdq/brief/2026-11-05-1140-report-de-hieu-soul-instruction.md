# Brief — Báo cáo dễ hiểu kèm Archify HTML và chuẩn trình bày ngắn gọn trong Soul / User-Instruction
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> tôi muốn update cho phase report, là luôn làm bản report dễ hiểu cho người mọi người đọc đều có thể hiểu, bổ sung thêm archify html vào, và nếu có update thì phải có report dễ hiểu là trước request trạng thái/flow thế noà, sau request thế nào, đã test gì, và kết quả test ra được cái gì, set soul cho tdq-workflow và cho cả instruction claude code là luôn tình bày đơn giản dễ hiểu ngắn gọn, nếu người dùng cài tdq hoặc update thì auto bổ sung vào user-instruction luôn
>
> 1a bổ sung thêm là đơn giản dễ hiểu nhưng phaiir trực quan, đầy đủ thông tin

**Đọc lần đầu (First reading):**
- **Mục tiêu:**
  1. Chuẩn hóa **phase `report`** (cả Markdown và **Archify HTML** đi kèm): luôn viết bằng ngôn ngữ đơn giản, dễ hiểu cho mọi người đọc, nhưng **trực quan và đầy đủ thông tin**; khi có cập nhật thì bắt buộc trình bày rõ 4 phần: **(a) Trước request trạng thái/flow thế nào**, **(b) Sau request thế nào**, **(c) Đã test những gì**, và **(d) Kết quả test thực tế ra sao**.
  2. Cập nhật **Soul của TDQ-Workflow** (`skills/tdq-conventions/references/soul.md` và `skills/tdq-conventions/SKILL.md`): bổ sung nguyên tắc luôn trình bày đơn giản, dễ hiểu, ngắn gọn nhưng trực quan và đầy đủ thông tin.
  3. Cập nhật **managed user-instruction của Claude Code** (`scripts/tdq_setup.py` `KHOI_HUONG_DAN` + `docs/claude-md-mau.md`): khi người dùng cài mới (`tdq_setup.py`, kể cả `--nen`) hoặc update phiên bản (`tu_dong_cap_nhat_khi_doi_phien_ban` qua `SessionStart`), tự động ghim/cập nhật quy tắc trình bày đơn giản, dễ hiểu, ngắn gọn, trực quan, đầy đủ thông tin và chuẩn report Trước/Sau + Đã test/Kết quả + Archify HTML vào `~/.claude/CLAUDE.md` mà giữ nguyên nội dung ngoài block `<!-- TDQ:TOOLS -->`.

## Hiểu & kiến thức

- **Bỏ B0:** Đã có tiền lệ chạm cùng vùng (`docs/tdq/reports/2026-11-03-0715-express-report.md`, `docs/tdq/reports/2026-11-03-1420-phoi-hop-cong-cu.md`).
- **Bỏ B2:** Không có phụ thuộc/API bên ngoài repo cần research mới.
- **Khảo sát 3 chiều (B1 — Grep + Graphify + Read):**
  - `skills/tdq-conventions/references/soul.md` (140 dòng, trần `test_soul_rules.py` < 150 dòng) và `skills/tdq-conventions/SKILL.md`: chứa nguyên tắc cốt lõi của TDQ-Workflow.
  - `skills/tdq-build/references/report-template.md` và `skills/tdq-build/references/archify-lifecycle.md`: định nghĩa cấu trúc `docs/tdq/reports/<slug>.md` và `docs/tdq/reports/<slug>.html` cho cả 2 lane (`quick` và `full`).
  - `scripts/tdq_state.py` (`PHASE_TABLE["report"]`) và `skills/tdq-conventions/references/phases.md`: in checklist cho phase `report`.
  - `scripts/tdq_setup.py` (`KHOI_HUONG_DAN`, `ghim_huong_dan_tool`, `thuc_hien_setup_bu`, `khoi_tao_nen`) và `docs/claude-md-mau.md`: quản lý khối `<!-- TDQ:TOOLS --> ... <!-- /TDQ:TOOLS -->` trong `~/.claude/CLAUDE.md`. Lưu ý `khoi_tao_nen` (`--nen`, chạy tự động khi `SessionStart` phát hiện cài mới) hiện chưa gọi `ghim_huong_dan_tool` — bổ sung gọi an toàn trong `khoi_tao_nen` để cả cài mới chạy nền lẫn `tdq_setup.py` trực tiếp và `tu_dong_cap_nhat_khi_doi_phien_ban` khi nâng version đều tự động cập nhật `user-instruction`.
  - Ràng buộc kiểm thử: `tests/test_soul_rules.py` (`soul.md` < 150 dòng), `tests/test_claude_md_core.py` (`KHOI_HUONG_DAN` khớp nguyên văn `docs/claude-md-mau.md`, `MAX_BYTES`), `tests/test_report_visual.py`, `tests/test_token_budget.py` (`python scripts/khoa_token.py` cập nhật sau khi đổi rule).

## Hỏi đáp

- **Câu 1 (Chọn pipeline):** Người dùng chọn `1a` (chế độ nhanh — express) và bổ sung: *"bổ sung thêm là đơn giản dễ hiểu nhưng phaiir trực quan, đầy đủ thông tin"*.
