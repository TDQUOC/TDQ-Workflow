# REPORT — Điều tra và khắc phục lỗi LSP search gate và tdq_team clean (`2026-10-15-0958-dieu-tra-loi-lsp-search-team-clean` · lane full · mode subagent · 4 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P1 nâng cấp `scripts/tdq_team.py` hỗ trợ lệnh `clean [task]` nhận tham số task tùy chọn (báo `already cleaned` và thoát 0 nếu đã dọn bởi merge; dọn worktree task nếu còn; dọn toàn bộ slug nếu không truyền task) và chuẩn hóa hướng dẫn dọn dẹp worktree trong `skills/tdq-build/SKILL.md` · P2 nâng cấp `scripts/search_rules.py` và `hooks/scripts/search_gate.py` tự động phát hiện ngôn ngữ dự án (`typescript`, `python`, `go`, `rust`...) để in đúng `language_id` thực tế thay vì gán cứng `e.g. python`, đồng thời gợi ý `mcp__lsp__list_symbols` khi grep trong file cụ thể · P3 cập nhật quy trình cơ học 3 bước khởi tạo/sử dụng LSP (`start_lsp` đầu phiên, `open_document` cho TS/JS, và tra cứu symbol) vào `KHOI_HUONG_DAN` (`CLAUDE.md`), `skills/tdq-setup/references/uu-tien-tim-kiem.md`, đồng bộ `docs/claude-md-mau.md` và khóa `docs/tdq/token-budget.json` · P4 kiểm chứng log service, chuẩn ngôn ngữ 3 tầng và bộ test vùng chạm.
**Kết quả:** Lỗi CLI `exit 2: unrecognized arguments: <task>` được loại bỏ hoàn toàn: `clean T1.1` thoát `0` và xử lý an toàn · Thông báo chặn `[TDQ:SEARCH]` chuyển từ gán cứng `e.g. python` sang tự động điền `language_id = "typescript"` (kèm lưu ý `open_document` cho TS/JS) và tự gợi ý `list_symbols` cho file cụ thể, ngăn ngừa agent rơi vào bẫy đoán mò regex `a|b|c` · Khối ghim `KHOI_HUONG_DAN` đạt 21 dòng (≤ 25 dòng).
**Kiểm:** Toàn bộ 131 tests thuộc 7 module chạm (`test_claude_md_core.py`, `test_luat_skill.py`, `test_tdq_setup_skill.py`, `test_team_mode.py`, `test_search_rules.py`, `test_search_gate.py`, `test_tdq_setup.py`) PASS 100% · `doc_lint.py` 0 vi phạm · `token_budget.py --kiem` 50/50 file khớp khóa · `i18n_check.py` 0 vi phạm · QC PASS 4/4 mục DoD (`Q1`–`Q4`) và 4/4 mục cố định (`QC-F1`–`QC-F4`) ở mức `lite`.
**Đầu ra:** `scripts/tdq_team.py` · `scripts/search_rules.py` · `hooks/scripts/search_gate.py` · `scripts/tdq_setup.py` · `skills/tdq-setup/references/uu-tien-tim-kiem.md` · `skills/tdq-build/SKILL.md` · `docs/claude-md-mau.md` · `tests/test_team_mode.py` · `tests/test_search_rules.py` · `tests/test_search_gate.py` · `tests/test_tdq_setup.py` · `tests/test_claude_md_core.py` · `docs/tdq/qc/2026-10-15-0958-dieu-tra-loi-lsp-search-team-clean.md` · Backup: không có.
**Giới hạn:** Không thay đổi thuật toán nhận diện regex đoán mò hay cửa sổ 10 lượt mở khóa grep.
**Lệch spec chờ duyệt:** không có.
**Git:** chưa commit (đang ở nhánh `bugfix/dieu-tra-loi-lsp-search-team-clean`).

## Thời gian

Request `2026-10-15-0958-dieu-tra-loi-lsp-search-team-clean` · lane full · opened at 2026-10-15T10:57:47+07:00

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 0s | — | 1 |
| analyze | 43 min | — | 1 |
| spec | 6 min | — | 1 |
| plan | 2 min | — | 1 |
| implement | 43 min | — | 1 |
| qc | 12 min | — | 1 |
| report | 1s | — | 1 |
| **Total** | **1h 46min** | **—** | |

Model column is `—`: the transcript of this session could not be read.
