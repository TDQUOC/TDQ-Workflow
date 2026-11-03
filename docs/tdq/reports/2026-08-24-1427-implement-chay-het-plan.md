# REPORT — cổng chặn kết lượt khi plan chưa chạy hết (`2026-08-24-1427-implement-chay-het-plan` · lane full · mode main · 12 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** thêm khoá `implement_pause` cùng hai lệnh `tam-hoan --ly-do` / `tiep-tuc` vào
`scripts/tdq_state.py` · thêm cổng `[TDQ:UNFINISHED]` vào `hooks/scripts/stop_gate.py`: đang ở
phase `implement` mà plan còn task hở thì `Stop` trả `decision: block` kèm `stop_hook_active:
false` nên chặn được cả những lượt lặp lại · bộ đếm ba lần không tiến triển hạ xuống nhắc
`[TDQ:STUCK]` để không kẹt vĩnh viễn · viết luật vào `tdq-build` và bảng phase · sinh lại hai
bản portable.
**Kết quả:** lượt không sửa file mà plan còn hở: trước đi lọt, nay bị chặn · đường dừng hợp lệ:
trước là im lặng, nay phải khai lý do và lý do đó được báo cho người dùng · test của
`stop_gate` 81 → 104.
**Kiểm:** `.venv/bin/pytest tests/ -q` cho 38 failed / 1545 passed — đúng bằng số đỏ nền ở mốc
`22fa2eb`, không sinh đỏ mới · `i18n_check` và `doc_lint` đều exit 0 · QC PASS 16/16 dòng DoD
cộng 4 hạng mục cố định, 0 vòng fix.
**Đầu ra:** `hooks/scripts/stop_gate.py` · `scripts/tdq_state.py` · `tests/test_implement_pause.py` ·
`tests/test_stop_gate.py` · `skills/tdq-build/SKILL.md` · `skills/tdq-conventions/references/phases.md`
· QC: `docs/tdq/qc/2026-08-24-1427-implement-chay-het-plan.md`
**Giới hạn:** cổng chỉ đọc checkbox của plan, nên một task tick `[x]` mà chưa làm thật thì cổng
không biết · 38 test đỏ có sẵn (kho skill plugin ngoài, worktree) vẫn để nguyên vì ngoài phạm vi
· một khiếm khuyết tự phát hiện đã sửa trong lúc làm: `phases.md` là file sinh ra từ hằng số
`PHASE_TABLE`, nên câu luật được đưa vào hằng số rồi sinh lại thay vì sửa tay.
**Git:** chưa commit gì.

## Thời gian

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 0s | 0s | 1 |
| analyze | 5 min | 5 min | 1 |
| spec | 31 min | 6 min | 1 |
| diagram | 3 min | 2 min | 1 |
| plan | 20 min | 5 min | 1 |
| implement | 17 min | 17 min | 1 |
| qc | 4 min | 4 min | 1 |
| report | 0s | 0s | 1 |
| **Total** | **1h 19min** | **39 min** | |
