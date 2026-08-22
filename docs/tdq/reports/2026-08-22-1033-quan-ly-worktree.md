# REPORT — Quản lý vòng đời worktree của workflow (`2026-08-22-1033-quan-ly-worktree` · lane full · mode main · 29 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** module sổ thuần dữ liệu `tdq_worktree_registry.py` (không gọi git, 4 lý do chặn + 1 lý do thêm ở vòng fix, mỗi lý do kèm phương án chạy được) · `tdq_team.py` có lệnh mới `soat`/`soat --don` quét mọi worktree của mọi request, `mo` ghi sổ trước khi tạo thư mục, `hop` tự dọn khi đủ ba điều kiện · chặn `set phase=qc` khi sổ còn dòng mở · hook nhắc một dòng `[TDQ:WORKTREE]` mỗi turn · luật viết vào `team-mode.md`, hai cây portable dựng lại.
**Kết quả:** worktree sau khi merge tự biến mất thay vì nằm lại ăn disk · worktree không dọn được luôn in khối `NOT CLEANED UP YET` với phương án gỡ được thật (đo bằng test chạy đúng lệnh in ra) · ngưỡng cảnh báo 500 MB tổng / 7 ngày mỗi worktree.
**Kiểm:** `pytest tests/test_team_mode.py -q` → 144 passed · `test_state`+`test_context_hooks`+`test_worktree_registry` → 99 passed · full suite → 37 đỏ (đúng mốc nền, toàn bộ ở `tests/test_skill_router.py`) / 1259 passed · `doc_lint` 0 vi phạm · `i18n_check` ba kind 0 dòng · portable CLEAN 85 + 130 · QC PASS 20/20 hạng mục DoD, 16 khiếm khuyết agent QC bắt được qua 2 lượt thì 15 đã sửa (F1–F15), 3 vòng fix đúng trần.
**Đầu ra:** `scripts/tdq_worktree_registry.py` · `scripts/tdq_team.py` · `scripts/tdq_state.py` · `hooks/scripts/prompt_context.py` · `skills/tdq-build/references/team-mode.md` · sổ chạy thật: `docs/tdq/worktrees.json` + `.md` (đã gitignore).
**Giới hạn:** (1) `worktrees.md` sinh bằng tiếng Anh chứ không theo `doc_lang` như spec §4 — theo tiền lệ `docs/tdq/STATE.md`; dòng spec §4 cần sửa ở lần cập nhật spec sau, không sửa trong request này vì §4 có đánh số, sửa sẽ vỡ sha đã duyệt. (2) KM-5 chưa sửa: `soat --don` gỡ worktree `tich-hop` giữa sóng rồi `_bao_dam_tich_hop` dựng lại — churn, không mất việc, `hop` kế tiếp vẫn rc=0. (3) Ngưỡng 500 MB / 7 ngày là số chốt lúc duyệt spec, chưa hiệu chỉnh theo dữ liệu dùng thật.
**Git:** chưa commit gì — không gặp chặn kỹ thuật nào phải tự gỡ.

## Thời gian

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 3s | 0s | 1 |
| analyze | 7 min | 6 min | 1 |
| spec | 7 min | 4 min | 1 |
| plan | 5 min | 4 min | 1 |
| implement | 17 min | 17 min | 1 |
| qc | 50 min | 28 min | 1 |
| report | 1s | 0s | 1 |
| **Total** | **1h 26min** | **1h 04min** | |
