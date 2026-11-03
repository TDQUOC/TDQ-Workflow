# REPORT — Mode subagent thành mô hình đội (`2026-08-17-1828-subagent-team-implement` · lane full · mode main · 28/28 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P1 thêm dấu tick thứ tư `[>]` (đã giao agent con) vào `tdq_state` · P2 viết
`scripts/tdq_team.py` — leader phân công CẢ plan trước, chia đợt theo vùng file, mở
nhánh/worktree, dò xung đột bằng `git merge-tree`, hợp tuần tự, dọn sạch · P3 nới hook
`edit_gate` cho nhiều `[>]` nhưng thêm chặn `[TDQ:TEAM]` khi leader tự gõ code của task
đã hứa giao, thêm ca lệch D12 cho check-status · P4 viết lại luật ở `tdq-build`,
`tdq-plan`, `mode-gate`, `tdq-conventions` + `agents/tdq-implementer.md` · P5 test và
bundle · P6 QC 23 hạng mục.

**Kết quả:** test 767 → 839 passed (394 subtests) · mode `subagent` từ "mỗi lần đúng 1
task, chờ xong mới giao tiếp" → phát cả một đợt trong MỘT response, leader làm task
`tu_lam` song song · chống lách luật từ lời hứa trong văn bản → 3 lớp máy kiểm: bản đồ
`docs/tdq/team/<slug>.json` trên đĩa, `kiem-ke` exit khác 0 khi bịa lý do, hook chặn tay
leader; 4 nhóm lý do giữ task là tập ĐÓNG (`phu-thuoc`, `vung-khoa`, `mcp`, `file-luat`).

**Kiểm:** `pytest tests/ -q` → 839 passed, 394 subtests · `doc_lint` mọi file sửa và
`--pair` spec-plan đều exit 0 · hai bundle portable `SẠCH` (79 và 124 file) · QC 23/23
PASS, trong đó Q23 do agent `tdq-qc-tester` chạy độc lập — agent nêu 5 defect, đã vá hết
trong 1 vòng fix (trần 3) và khoá bằng 5 test mới; chi tiết ở file QC.

**Đầu ra:** `scripts/tdq_team.py` · `skills/tdq-build/references/team-mode.md` ·
`docs/tdq/qc/2026-08-17-1828-subagent-team-implement.md`. Không sửa gì ngoài repo.

**Giới hạn:** mô hình đội mới chỉ chạy thử trên plan mẫu trong repo git tạm, chưa chạy
thật một request end-to-end ở mode `subagent` — lần dùng thật đầu tiên nên xem kỹ output
`cum` và `kiem`. Tốc độ thực tế phụ thuộc plan có khai `Chạm:` đầy đủ hay không: plan
thiếu dòng đó thì task rơi vào `vung-khoa` và leader phải tự làm.

**Lệch so với spec:** trần dòng `tdq-conventions/SKILL.md` nâng 133 → 143 trong
`SKILL_LINE_LIMITS` (`scripts/doc_lint.py`), kèm comment lý do — hai luật mới ở §1 là luật
tầng runtime, phải nạp mỗi turn.

**Git:** chưa commit gì trong request này. Nhánh `tdq-doi-ten-mode-implement` còn 2 commit
cũ chưa push (`a107c55`, `6031ce1`) từ request trước.

## Thời gian

| Phase | Treo tường | Model chạy | Số lần vào |
|---|---|---|---|
| idle | 0 giây | 0 giây | 1 |
| analyze | 14 phút | 14 phút | 1 |
| spec | 26 phút | 11 phút | 1 |
| plan | 2 phút | 2 phút | 1 |
| implement | 28 phút | 28 phút | 1 |
| qc | 19 phút | 10 phút | 1 |
| report | 4 giây | 0 giây | 1 |
| **Tổng** | **1 giờ 28 phút** | **1 giờ 04 phút** | |
