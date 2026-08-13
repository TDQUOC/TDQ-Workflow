# QC — Bịt 3 lỗ hổng tick checkbox ở chế độ chuyên sâu

Ngày: 2026-08-13 · Plan: ../plan/2026-08-13-ra-soat-tick-che-do-sau.md

| # | Hạng mục | Lệnh | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Chặn nhiều task `[~]` | `.venv/bin/python -m pytest tests/test_edit_gate.py -q -k doing` | `2 passed, 25 deselected` | PASS |
| Q2 | Chặn sửa liên tiếp không tick (streak=3) | `.venv/bin/python -m pytest tests/test_edit_gate.py -q -k streak` | `3 passed, 24 deselected` | PASS |
| Q3 | `doing_count` đúng | `.venv/bin/python -m pytest tests/test_plan_tick.py -q` | `10 passed` | PASS |
| Q4 | Không phá test cũ `edit_gate`/`stop_gate` | `.venv/bin/python -m pytest tests/test_edit_gate.py tests/test_stop_gate.py -q` | `69 passed` | PASS |
| Q5 | Tài liệu subagent nhất quán | Đọc `skills/tdq-build/SKILL.md`, `skills/tdq-plan/SKILL.md`, `agents/tdq-implementer.md` | Cả 3 cùng nói "1 task/1 lần gọi agent, tick `[x]` ngay khi nhận báo cáo, trước khi gọi agent kế tiếp"; `agents/tdq-implementer.md` đổi "one assigned phase/task-group" → "one assigned task" | PASS |
| Q6 | Full suite không hồi quy | `.venv/bin/python -m pytest -q` | `499 passed, 178 subtests passed` (so với 457 passed/140 subtests trước loạt vá lane nhanh+chuyên sâu — tăng do các test mới, không có test nào biến mất) | PASS |

**DoD**: Q1–Q6 đều PASS, đủ bằng chứng ở trên. Không có vòng fix — mọi task đỏ→xanh
ngay ở lần đầu, không có hạng mục FAIL nào phải quay lại plan.
