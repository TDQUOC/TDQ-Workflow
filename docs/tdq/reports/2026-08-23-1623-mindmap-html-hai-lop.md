# REPORT — công cụ sơ đồ giải thuật: script chạy được, phase bắt buộc trước plan, trang HTML hai lớp (`2026-08-23-1623-mindmap-html-hai-lop` · lane full · mode subagent · 25 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P1 viết thật `scripts/tdq_mindmap.py` với 5 lệnh (`sinh`/`kiem`/`lien-he`/`doi-chieu`/`xem`) · P2 `scripts/mindmap_render.py` dựng trang một feature HAI LỚP (lớp nghiệp vụ người duyệt + lớp chi tiết mỗi function một step, sinh từ `graph.json`) và trang tổng `--tong` gom theo `@nhánh` kèm lưới phụ thuộc · P2 chèn phase `diagram` vào `tdq_state.py` với cổng chặn `set phase=plan` khi còn sơ đồ chưa duyệt · P3 skill `tdq-diagram` mới, ba file skill cũ dẫn vào phase mới · P4 log service, test, vá phủ test.
**Kết quả:** phase workflow 10 → 11 (`diagram` chen giữa `spec` và `plan`) · skill 5 → 6 · test suite 1444 → 1498 xanh (thêm 54 test mới) · test đỏ 44 → 38, đối chiếu tập đỏ với mốc `7e3bbd0` ra RỖNG phía mới → **0 hồi quy**, 6 đỏ cũ thành xanh.
**Kiểm:** `pytest tests/ -q` → `38 failed, 1498 passed, 1484 subtests passed` (38 đỏ đều là nợ có sẵn: 37 ca `test_skill_router` lệch bản kiểm kê kho skill plugin ngoài, 1 ca `test_bench`) · hồi quy vùng đã chạm 14 tệp → `460 passed, 537 subtests` · `doc_lint`/`i18n_check` exit 0 · QC 29/29 mục PASS (25 dòng DoD + 4 mục cố định), 2 defect phủ test đã vá trong vòng fix 1.
**Đầu ra:** `scripts/tdq_mindmap.py` · `scripts/mindmap_render.py` · `skills/tdq-diagram/SKILL.md` · `docs/tdq/mind-map/{dang-nhap,mua-hang}.md` + `index.html` · QC: `docs/tdq/qc/2026-08-23-1623-mindmap-html-hai-lop.md`.
**Giới hạn:**
- 38 test đỏ có sẵn từ trước request vẫn còn — ngoài phạm vi, không sửa; cần một request riêng.
- Lỗi khung: khối `[TDQ:TEAM]` trong `hooks/edit_gate.py` (~dòng 114) THIẾU phép miễn `.tdq-worktrees/` mà khối `[TDQ:TICK]` (~dòng 159) đã có → sub-agent trong worktree bị chặn oan. Chưa sửa, ngoài phạm vi plan.
- Ma sát `plan_sha`: mỗi lần tick task là bản đồ phân công hết hạn, phải chạy lại `tdq_team.py phan-cong` sau MỖI tick. Nên tự làm mới trong `tdq_team.py`.
- Xung đột luật i18n: 8 dòng tiếng Việt (luật định tuyến tìm kiếm LSP) ở `skills/tdq-intake/SKILL.md:54-55`, `references/analyze-full.md:20-21`, `skills/tdq-plan/SKILL.md:48-49`, `skills/tdq-spec/SKILL.md:30-31` KHÔNG đánh dấu `i18n-allow` được vì `tests/test_tdq_lsp_skill.py` so nguyên văn từng ký tự. Có sẵn từ trước (`git show HEAD:… `), cần luật hoà giải.
- T4.5 (gọi tool `mcp__lsp__*` thật để xác nhận dòng nhắc lumen đã hết) vẫn treo — phiên này không có tool đó.
**Đội hình:** 17/23 task giao cho sub-agent, 6 task leader giữ với lý do thuộc tập đóng (`file-luat` ×4, `vung-khoa` ×1, `mcp` ×1); `kiem-ke` 0 vấn đề; worktree đã dọn sạch.
**Phát sinh giữa implement:** 6 task thêm ngoài plan gốc — T1.5 (`kiem` nhận nhiều đường dẫn, chỉ lộ khi dùng thật), T2.7/T2.8 (lint + bảng phase), T4.4a-d (dọn vi phạm doc_lint do đợt này thêm chữ vào skill, khai `tdq-diagram` vào hai bảng kiểm kê, vá test đỏ do chèn phase, và hai ca eval còn chuỗi `set phase=plan` không qua cổng sơ đồ — ca cuối do một sub-agent phát hiện ngoài vùng của nó).
**Git:** CHƯA commit kết quả cuối. Trong lúc build có các commit gỡ chặn kỹ thuật của quy trình worktree: `f986139`, `9bbdfa3`, `f4427f0`, `7c69a8d`, `c09c64d`, `252682f` cùng hai merge `--no-ff` từ nhánh tích hợp. Chưa push commit nào.

## Thời gian

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 0s | 0s | 1 |
| analyze | 1h 06min | 7 min | 1 |
| spec | 41 min | 5 min | 1 |
| plan | 8 min | 7 min | 1 |
| implement | 1h 29min | 1h 14min | 1 |
| qc | 27 min | 22 min | 1 |
| report | 10s | 7s | 1 |
| **Total** | **3h 52min** | **1h 56min** | |
