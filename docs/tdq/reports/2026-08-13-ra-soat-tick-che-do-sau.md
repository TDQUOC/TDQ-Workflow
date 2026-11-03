# REPORT — Bịt 3 lỗ hổng tick checkbox ở chế độ chuyên sâu (`2026-08-13-ra-soat-tick-che-do-sau` · lane full · mode main · 11 task tick đủ)

Đã làm: P1 thêm `doing_count` vào `plan_tick_state` · P2 chặn "nhiều task cùng `[~]`" trong
`edit_gate.py` · P3 đếm streak (ngưỡng 3 lần sửa liên tiếp không tick) qua sổ turn, chặn
lần thứ 4 · P4 đổi luật giao subagent xuống 1 task/lần gọi ở `tdq-build/SKILL.md` +
`tdq-plan/SKILL.md` + `agents/tdq-implementer.md` · P5 chạy test gộp, log BỎ (không tạo
runtime mới).
Kết quả: gap A (đứng `[~]` xuyên suốt) → chặn ở lần sửa thứ 4 · gap B (nhiều `[~]` cùng
lúc) → chặn ngay · gap C (subagent batch-tick) → đơn vị giao việc còn 1 task, tick real-time.
Kiểm: `pytest -q` 499 passed, 178 subtests (trước 457 passed/140 subtests — tăng do test
mới, không mất test nào) · `doc_lint.py --pair` PASS · QC 6/6 mục DoD PASS, không vòng fix.
Đầu ra: `hooks/scripts/edit_gate.py`, `scripts/tdq_state.py`, `skills/tdq-build/SKILL.md`,
`skills/tdq-plan/SKILL.md`, `agents/tdq-implementer.md`, `tests/test_edit_gate.py`,
`tests/test_plan_tick.py`.
Giới hạn: chỉ đổi luật/tài liệu — chưa có lần build subagent thật nào chạy qua để kiểm
thực tế "1 task/1 lần gọi" trên agent thật (chỉ kiểm bằng đọc lại 3 file tài liệu, QC Q5).
Ngưỡng streak=3 chưa thử trên task thật có nhiều vòng sửa nhỏ hợp lệ — nếu chặn oan thì
tăng ngưỡng ở vòng fix sau, đã ghi rõ trong spec §5.
Git: chưa commit — 8 file đổi (2 hook/script, 2 test, 3 doc skill/agent, 1 plan).
