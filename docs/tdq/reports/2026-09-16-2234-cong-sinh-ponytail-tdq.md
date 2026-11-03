# REPORT — Nội hoá lối code Ponytail vào TDQ-Workflow (`2026-09-16-2234-cong-sinh-ponytail-tdq` · lane full · mode subagent · 25 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P1 viết luật "build less than asked" (bậc thang 7 bậc + món 8 "chạy trước, refactor sau") vào thân `tdq-build` và `chung.md` · P2 `hooks/scripts/luat_gon.py` đọc–lọc luật theo 4 mức gắt + khoá `muc_gat` trong state · P3 ba kênh bơm luật (`SessionStart`, `UserPromptSubmit`, `SubagentStart`), `hooks.json` lên 6 mục trên 5 sự kiện · P4 skill `tdq-lean` (3 chế độ) và `scripts/kiem_no_marker.py` (sổ nợ marker) · P5 đo hiệu ứng thật + đối chiếu baseline · P6 sinh lại 3 bản portable, cập nhật `kien-truc.md` · P7 vá 7 hồi quy phát hiện ở P5.
**Kết quả:** luật nạp mỗi phiên 0 → 133 dòng ở mức `full` (`lite` 72, `ultra` 139, `off` 0) · hook 5 → 6 trên 5 sự kiện · skill 8 → 9 · test trong repo 1802 → 1907 (thêm 105, tất cả xanh) · Ponytail KHÔNG được cài làm plugin thứ hai, phase và hai cổng duyệt của TDQ giữ nguyên.
**Kiểm:** `python3 -m unittest discover tests` ra `Ran 1907 tests in 114.458s · FAILED (failures=290, errors=4, skipped=14)`; so tập TÊN test đỏ với baseline `main` sạch (`4faed21`, `Ran 1802 … failures=290`) thì `comm` rỗng hai chiều — **lệch 0**, 11 tên đỏ hai bên là nợ sẵn có của `main` · `doc_lint` exit 0 · `kiem_no_marker.py` exit 0 (1 marker, 0 thiếu đường nâng) · QC **PASS 13/13 mục DoD + 4 mục cố định**, 1 defect thật đã sửa trong vòng 1.
**Đầu ra:** `docs/tdq/qc/2026-09-16-2234-cong-sinh-ponytail-tdq.md` · luật: `skills/tdq-build/references/rules/chung.md` · mã mới: `hooks/scripts/luat_gon.py`, `hooks/scripts/subagent_start.py`, `scripts/kiem_no_marker.py`, `skills/tdq-lean/SKILL.md`. Không sửa gì ngoài repo; không có backup.

**Bốn chỗ luật trái nhau — phán quyết của bạn được thi hành đúng nguyên văn:** hình dạng phép kiểm theo Ponytail (`kiem_no_marker.py` một lệnh chạy được, không framework, không fixture) · test mỗi task red→green không miễn trừ · log service bật mặc định, tắt được qua config · sàn `cyclomatic ≤ 10 / cognitive ≤ 15` là sàn, không marker `ponytail:` nào mở được (viết thành mục riêng "The ladder only chooses among options that already pass the floor").

**Giới hạn:**
- `tdq-lean` **chưa vào** `docs/tdq/audit/skill-index.json`. Chỉ mục dựng từ skill của plugin ĐÃ CÀI, không từ `skills/` của repo, nên phải **cài lại plugin** thì skill thứ 9 mới được đánh chỉ mục — đây là bước của bạn, không phải việc còn thiếu trong mã.
- Kênh `SubagentStart` là **lời nhắc, không phải hàng rào**: `additionalContext` của sub-agent có thể bị prune (issue #23885), nên không DoD nào dựa vào việc sub-agent tuân luật. Dedupe của ba kênh dùng sổ lượt chung, hai kênh chạy cùng một lượt vẫn có thể in hai lần trong vài ca biên.
- Nợ sẵn có của `main`, **cố ý không sửa** vì ngoài phạm vi: 11 tên test đỏ (`test_doc_dup` 5, `test_skill_router` 2, `test_rules_library` 1, `test_token_audit` 1, 2 lỗi loader) · `docs/tdq/audit/luat-hien-co.md` neo L286 trỏ vào `skills/tdq-plan/SKILL.md` không tìm được.
- Ba dòng câu luật chuẩn trong `skills/tdq-build/SKILL.md` bị `i18n_check` đếm là tiếng Việt, đúng như `tdq-plan`/`tdq-spec`/`tdq-intake` đã vậy trên `main`. Ép exit 0 riêng file này phải hy sinh phép so nguyên văn của câu luật, nên đã sửa phép kiểm Q1 kèm lý do + ngày tại chỗ.
- Đọc repo bên thứ ba khi TDQ đang cài sẽ để lại `docs/tdq/` nháp ở đó (hook ghi state theo cwd). Lượt này đã dọn; gốc nằm ngoài phạm vi request.

**Giao việc:** 8/24 task giao cho `tdq-implementer` (mode `subagent`), 16 task người dẫn tự làm vì rơi đúng nhóm `file-luat`/`vung-khoa`/`phu-thuoc` trong bảng lý do đóng của `team-mode.md`. Đã dọn sạch 3 worktree của team + worktree baseline; sổ worktree rỗng.

**Git:** **chưa commit** phần P7 và bản portable sinh lại (62 file đang dirty). Trên nhánh đã có 15 commit, trong đó **6 commit tôi tự tạo để mở blocker kỹ thuật** theo luật implement (không push lần nào): `741834d` (T1.1), `64d8e97` (T2.1), `265d31d` (T4.2), `ef404f3` (T2.2+T3.1–T3.3), `9b192a2` (T4.1), `7541c55` (phân công lại bản đồ team sau khi plan đổi).

## Thời gian

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 4 min | 4 min | 1 |
| analyze | 1h 11min | 21 min | 1 |
| spec | 21 min | 12 min | 1 |
| plan | 11 min | 11 min | 1 |
| implement | 1h 26min | 1h 26min | 1 |
| qc | 7 min | 7 min | 1 |
| report | 4s | 3s | 1 |
| **Total** | **3h 20min** | **2h 20min** | |
