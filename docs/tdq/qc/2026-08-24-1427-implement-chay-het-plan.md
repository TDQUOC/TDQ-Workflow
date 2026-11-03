# QC — cổng chặn kết lượt khi plan chưa chạy hết

Ngày: 2026-08-24 · Plan: ../plan/2026-08-24-1427-implement-chay-het-plan.md
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Quan sát chạy thật (T2.5)

Dựng repo tạm, state phase `implement`, plan hai task còn hở, bơm payload `Stop` với
`stop_hook_active: true` hai lượt liên tiếp. Cả hai lượt đều trả `decision: block` mang mã
`[TDQ:UNFINISHED]` và `stop_hook_active: false`. Tức hợp đồng hook đúng như tài liệu chính
thức mô tả: cờ chống lặp do Claude Code đặt, hook trả lại `false` thì cổng được nạp đạn lại.
Nguồn tài liệu: https://code.claude.com/docs/en/hooks

Chạy tiếp `tam-hoan --ly-do "thử đường dừng hợp lệ"` rồi bơm lại payload: không còn
`decision`, chỉ còn một dòng log in đúng lý do đã khai. Đường dừng hợp lệ hoạt động.

## Bảng kiểm — 16 dòng DoD + 4 hạng mục cố định

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Chặn ca chính | `pytest tests/test_stop_gate.py -k unfinished_chan_ca_chinh` | 1 passed | PASS |
| Q2 | Nội dung payload chặn | `... -k unfinished_noi_dung` | 1 passed | PASS |
| Q3 | Chặn lặp, `stop_hook_active: false` | `... -k unfinished_chan_lap` | 4 passed | PASS |
| Q4 | Tràn ba lần → hạ xuống nhắc | `... -k unfinished_tran` | 2 passed, 3 subtests | PASS |
| Q5 | Có `implement_pause` → không chặn | `... -k unfinished_tam_hoan` | 1 passed | PASS |
| Q6 | Task `[>]` → không chặn | `... -k unfinished_subagent` | 1 passed | PASS |
| Q7 | Ngoài phase implement → không chặn | `... -k unfinished_ngoai_phase` | 1 passed | PASS |
| Q8 | Plan xong hết → không chặn | `... -k unfinished_plan_xong` | 1 passed | PASS |
| Q9 | Thiếu bằng chứng → không chặn | `... -k unfinished_thieu_bang_chung` | 1 passed | PASS |
| Q10 | CLI `tam-hoan`/`tiep-tuc` | `pytest tests/test_implement_pause.py -k tam_hoan` | 2 passed | PASS |
| Q11 | Hai cổng cũ nguyên vẹn | `pytest tests/test_stop_gate.py -q` | 104 passed, 23 subtests | PASS |
| Q12 | Hai file luật nêu cổng mới | `grep -l "TDQ:UNFINISHED" skills/tdq-build/SKILL.md skills/tdq-conventions/references/phases.md` | trả về đủ hai file | PASS |
| Q13 | Mỗi lần chặn in một dòng log | `... -k unfinished_log` | 2 passed | PASS |
| Q14 | Sạch lỗi ngôn ngữ | `python3 scripts/i18n_check.py hooks/scripts/stop_gate.py scripts/tdq_state.py` | 0 line(s), exit 0 | PASS |
| Q15 | Hai bản portable mang hook mới | `build_portable.py` rồi `grep -c` | exit 0, cả hai bản đếm 5 | PASS |
| Q16 | Không có test đỏ MỚI so mốc `22fa2eb` | `.venv/bin/pytest tests/ -q` | 38 failed, 1545 passed — đúng bằng số đỏ nền | PASS |
| QC-F1 | Toàn bộ bộ test | `.venv/bin/pytest tests/ -q > /tmp/qc-run.log` | 38 failed, 1545 passed, 1507 subtests | PASS |
| QC-F2 | Hồi quy vùng chạm | 11 file test của `stop_gate`/`tdq_state`/phase/hook | 267 passed, 135 subtests | PASS |
| QC-F3 | Ràng buộc kiến trúc (spec §5) | xem bằng chứng dưới | 3/3 giữ nguyên | PASS |
| QC-F4 | Clean code, 5 câu tự soát | xem bằng chứng dưới | 5/5 "có" | PASS |

## Bằng chứng

### Q16 / QC-F1 — số đỏ nền

```
38 failed, 1545 passed, 1507 subtests passed in 140.99s
```

Đối chiếu mốc: `git stash` toàn bộ thay đổi rồi chạy lại hai file đỏ duy nhất
(`tests/test_bench.py`, `tests/test_skill_router.py`) cho `38 failed` — y hệt. Toàn bộ test đỏ
là đỏ sẵn (kho skill của plugin ngoài và thư mục worktree), không dính gì tới yêu cầu này.

### QC-F2 — hồi quy vùng chạm

```
267 passed, 135 subtests passed in 19.35s
```

Gồm `test_stop_gate.py`, `test_implement_pause.py`, `test_state*.py`, `test_mode_phase.py`,
`test_phase_table.py`, `test_quick_qc.py`, `test_context_hooks.py`, `test_hook_resilience.py`.

### QC-F3 — ba ràng buộc kiến trúc

1. *Hook chỉ nhắc, kiểm bằng hiệu ứng thật, không `deny` vì "chưa duyệt"* — cổng mới đọc
   checkbox THẬT trên đĩa (`plan_tick_state`) và dùng `decision: block` của `Stop`, không phải
   `deny` của `PreToolUse`. GIỮ.
2. *`hooks/` gọi được `scripts/`, chiều ngược lại thì không* — `grep` import trong
   `scripts/tdq_state.py` không có `hooks`. GIỮ.
3. *Chú thích và chuỗi máy in ra của `hooks/` + `scripts/` viết tiếng Anh* —
   `i18n_check.py` trả 0 dòng trên cả hai file. GIỮ.

### QC-F4 — clean code, 5 câu tự soát

1. Tên nói đúng việc? Có — `unfinished_reason`, `_chan_chua_xong`, `_streak_bump`.
2. Một hàm một việc? Có — quyết định (`unfinished_reason`, thuần) tách khỏi tác dụng phụ
   (`_chan_chua_xong` in ra, `_streak_bump` ghi đĩa).
3. Không lặp code? Có — đường im lặng dùng lại `load`/`plan_tick_state` sẵn có.
4. Không thừa? Có — mọi nhánh đều có test tương ứng, không có TODO/FIXME/mock.
5. Lỗi được xử đúng chỗ? Có — `_streak_bump` nuốt `OSError` thành cảnh báo để đĩa hỏng không
   làm treo mọi lượt; các đường thiếu bằng chứng đều im lặng đi qua.

## Kết luận

PASS toàn bộ: 16 dòng DoD và 4 hạng mục cố định đều PASS, không có vòng fix nào.
Một khiếm khuyết phát hiện trong QC đã sửa ngay trong phase implement: `phases.md` là file
SINH RA từ `PHASE_TABLE`, nên câu luật mới được đưa vào hằng số trong `scripts/tdq_state.py`
rồi sinh lại, thay vì sửa tay.
