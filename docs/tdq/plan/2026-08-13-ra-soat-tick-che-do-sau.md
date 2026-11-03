# PLAN — Bịt 3 lỗ hổng tick checkbox ở chế độ chuyên sâu

Ngày: 2026-08-13 · Spec: ../spec/2026-08-13-ra-soat-tick-che-do-sau.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — thay đổi liên đới chặt: đổi 2 điều kiện chặn trong `edit_gate.py`
phải khớp test cùng lúc, đổi luật giao subagent phải khớp đồng thời cả 3 file tài liệu
(`tdq-build/SKILL.md`, `tdq-plan/SKILL.md`, `agents/tdq-implementer.md`); việc nhỏ, chia
subagent dễ lệch câu chữ giữa 3 file. (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite của module đang sửa, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — `plan_tick_state` báo thêm `doing_count`
- [x] **T1.1** (n2 e5m) Thêm field `doing_count` (đếm `dang` — số task `[~]`) vào dict trả
  về của `plan_tick_state` trong `scripts/tdq_state.py` — Test: `.venv/bin/python -m pytest tests/test_plan_tick.py -q`
- [x] **T1.2** (n2 e5m) Viết test mới trong `tests/test_plan_tick.py` kiểm `doing_count`
  đúng giá trị ở cả 3 ca (0 task `[~]`, 1 task `[~]`, ≥2 task `[~]`) — Test: `.venv/bin/python -m pytest tests/test_plan_tick.py -q`

**Xong P1 khi**: `pytest tests/test_plan_tick.py -q` xanh, field `doing_count` tồn tại và đúng.

## P2 — Chặn "nhiều task cùng `[~]`" (Gap B)
- [x] **T2.1** (n3 e8m) Thêm điều kiện `tick["doing_count"] > 1` vào đúng khối kiểm
  `TDQ:TICK` sẵn có trong `hooks/scripts/edit_gate.py` (tái dùng message hiện có, thêm 1
  dòng lý do "nhiều task cùng [~]") — Test: `.venv/bin/python -m pytest tests/test_edit_gate.py -q -k doing`
- [x] **T2.2** (n2 e6m) Viết test mới trong `tests/test_edit_gate.py::TickBlockTest`
  (2 task cùng `[~]` → sửa mã nguồn bị `deny` kèm `TDQ:TICK`; đúng 1 task `[~]` → không
  bị chặn bởi ca này, giữ hành vi cũ) — Test: `.venv/bin/python -m pytest tests/test_edit_gate.py -q -k doing`

**Xong P2 khi**: `pytest tests/test_edit_gate.py -q -k doing` xanh; các test `TickBlockTest`
cũ (`da_co_dau_nga_thi_im`, …) vẫn xanh.

## P3 — Chặn "sửa liên tiếp không tick" (Gap A, đếm streak)
- [x] **T3.1** (n6 e15m) Trong `hooks/scripts/edit_gate.py`, mỗi lần cho qua một lần sửa
  mã nguồn hợp lệ (không phải `tests/**`, đúng 1 task `[~]`) → ghi thêm
  `observe(cwd, payload, "code_edit", path=rel_target, plan_sha=tick["sha"])` vào sổ turn
  — Test: `.venv/bin/python -m pytest tests/test_edit_gate.py -q -k streak`
- [x] **T3.2** (n5 e12m) Đếm số dòng `code_edit` trong sổ turn có `plan_sha` TRÙNG
  `tick["sha"]` hiện tại; đủ 3 lần liên tiếp (chưa tick từ đó tới giờ) → `block()` lần sửa
  thứ 4 với mã `TDQ:TICK` (thông báo riêng: "đã sửa 3 lần liên tiếp mà chưa tick, đóng task
  trước khi sửa tiếp") — Test: `.venv/bin/python -m pytest tests/test_edit_gate.py -q -k streak`
- [x] **T3.3** (n3 e8m) Viết test mới: 3 lần sửa liên tiếp không tick → lần 4 bị chặn; tick
  xong (`plan_sha` đổi) → streak reset về 0, lần sửa kế tiếp không bị chặn; sửa trong
  `tests/**` không tính vào streak — Test: `.venv/bin/python -m pytest tests/test_edit_gate.py -q -k streak`

**Xong P3 khi**: `pytest tests/test_edit_gate.py -q -k streak` xanh.

## P4 — Luật giao subagent theo từng task (Gap C)
- [x] **T4.1** (n3 e8m) Đổi `skills/tdq-build/SKILL.md` — Phần A bước 1 (mô tả mode
  `subagent`) và "Vòng lặp mỗi task": mỗi lần gọi `tdq-implementer` giao ĐÚNG 1 task, main
  agent tick `[x]` ngay khi nhận báo cáo, TRƯỚC khi gọi agent cho task kế tiếp — Test: đọc
  lại file, không còn cụm "phase/task-group" ở phần mô tả subagent
- [x] **T4.2** (n2 e5m) Đổi `skills/tdq-plan/SKILL.md` bước 1 (mô tả 2 mode): câu
  "mỗi agent một git worktree (nhiều phase độc lập...)" → "mỗi agent một task, một git
  worktree" — Test: đọc lại file, câu mô tả subagent khớp câu ở T4.1
- [x] **T4.3** (n2 e5m) Đổi `agents/tdq-implementer.md`: `description` frontmatter và câu
  mở đầu từ "one assigned phase/task-group" → "one assigned task"; giữ nguyên luật cấm tự
  tick khi plan ngoài worktree — Test: đọc lại file, không còn cụm "phase/task-group"

**Xong P4 khi**: cả 3 file cùng nói "1 task/1 lần gọi agent, tick ngay sau báo cáo" (QC Q5).

## P5 — Log & test bắt buộc
Log: BỎ — việc này sửa hook nội bộ (`edit_gate.py`, `tdq_state.py`) và tài liệu markdown,
không tạo runtime service mới; log hiện có của hook giữ nguyên.
- [x] **T5.1** (n2 e6m) Chạy gộp test 2 file vừa đổi + không hồi quy `stop_gate` — Test:
  `.venv/bin/python -m pytest tests/test_edit_gate.py tests/test_plan_tick.py tests/test_stop_gate.py -q`

**Xong P5 khi**: lệnh trên xanh toàn bộ.

## Definition of Done
Trỏ về §6 của spec `2026-08-13-ra-soat-tick-che-do-sau.md`.

| # | Hạng mục | Lệnh kiểm | PASS khi |
|---|---|---|---|
| Q1 | Chặn nhiều task `[~]` | `.venv/bin/python -m pytest tests/test_edit_gate.py -q -k doing` | Test mới xanh |
| Q2 | Chặn sửa liên tiếp không tick | `.venv/bin/python -m pytest tests/test_edit_gate.py -q -k streak` | Test mới xanh |
| Q3 | `doing_count` đúng | `.venv/bin/python -m pytest tests/test_plan_tick.py -q` | Xanh, gồm test mới |
| Q4 | Không phá test cũ `edit_gate`/`stop_gate` | `.venv/bin/python -m pytest tests/test_edit_gate.py tests/test_stop_gate.py -q` | Toàn bộ xanh |
| Q5 | Tài liệu subagent nhất quán | Đọc `tdq-build/SKILL.md`, `tdq-plan/SKILL.md`, `agents/tdq-implementer.md` | Cả 3 cùng nói "1 task/1 lần gọi, tick ngay" |
| Q6 | Full suite không hồi quy | `.venv/bin/python -m pytest -q` | Xanh, không giảm số test so với trước |
