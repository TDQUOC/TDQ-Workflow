# QC — Chống sót tick dòng DoD lúc đóng sổ
Ngày: 2026-08-22 · Plan: ../plan/2026-08-22-1627-chong-sot-tick-dod.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | bộ đếm DoD đếm đúng | `pytest tests/test_plan_tick.py -q -k dod` | 9 passed | PASS |
| Q2 | bỏ qua khuôn cũ | cùng lệnh Q1, ca `khuon_cu_khong_o_tick` | tổng 0 | PASS |
| Q3 | không lẫn ô task | cùng lệnh Q1, ca `khong_lan_o_tick_cua_task` | DoD 5, task 2 | PASS |
| Q4 | bộ đọc qc đếm đúng | `pytest tests/test_plan_tick.py -q -k qcket` | 5 passed | PASS |
| Q5 | chịu được thiếu file qc | cùng lệnh Q4, ca `thieu_file_thi_khong_nem_loi` | exists sai, không ném lỗi | PASS |
| Q6 | nhắc bắn đúng lúc | `pytest tests/test_stop_gate.py -q -k dod` | 11 passed | PASS |
| Q7 | im ở phase khác | cùng lệnh Q6, ca `im_o_phase_implement` | không có `[TDQ:DOD]` | PASS |
| Q8 | im khi DoD không ô tick | cùng lệnh Q6, ca `im_khi_khuon_cu_khong_co_o_tick` | không có `[TDQ:DOD]` | PASS |
| Q9 | im khi qc còn FAIL | cùng lệnh Q6, ca `im_khi_qc_con_fail` | không có `[TDQ:DOD]` | PASS |
| Q10 | nhắc nêu cả ô task | cùng lệnh Q6, ca `nhac_neu_ca_so_task_lan_so_o_dod` | `1 task(s)`, `2 DoD line(s)` | PASS |
| Q11 | không chặn turn | cùng lệnh Q6, ca `khong_chan_turn` | không có `"decision"` | PASS |
| Q12 | điểm chặn cũ không đổi | `pytest tests/test_stop_gate.py -q` | 60 passed | PASS |
| Q13 | bộ đếm task cũ không đổi | `pytest tests/test_plan_tick.py -q` | 25 passed | PASS |
| Q14 | khuôn plan đã đổi | đọc mục Definition of Done của khuôn | 2 dòng mở đầu bằng ô tick | PASS |
| Q15 | khuôn report đã đổi | đọc bước 8 của khuôn report | nêu cả hai loại ô | PASS |
| Q16 | log service | chạy hook ở tình huống nhắc, đọc stderr | dòng có timestamp và lý do | PASS |
| Q17 | luật ngôn ngữ | `i18n_check.py --kind comment/string/body` | 0 dòng vi phạm | PASS |
| Q18 | luật tài liệu | `doc_lint.py --pair <spec> <plan>` | exit 0 | PASS |
| Q19 | hồi quy | `pytest -q` một lần | 37 đỏ, đều ở `test_skill_router.py` | PASS |
| QC-F1 | full suite | `pytest -q` | 37 failed, 1308 passed, 1447 subtests | PASS |
| QC-F2 | hồi quy vùng chạm | pytest trên 12 file test của tầng CLI và tầng hook | 389 passed | PASS |
| QC-F3 | ràng buộc kiến trúc | đọc từng dòng ràng buộc ở spec §5 | không dòng nào vỡ | PASS |
| QC-F4 | clean code | trả lời 5 câu Self-check | 5 câu đều "có" | PASS |

## Bằng chứng

### Q16 log service
```
[2026-08-22T19:28:11+07:00] ℹ️ stop_gate: hint TDQ:DOD · dod=0/1 · task open=1 · qc=1 PASS/0 FAIL · plan=<thư mục tạm>/docs/tdq/plan/r1.md
{"hookSpecificOutput": {"hookEventName": "Stop", "additionalContext": "[TDQ:DOD] Closing the books with boxes still open: 1 task(s), 1 DoD line(s). QC passed — tick them in the plan."}}
```

### Q17 luật ngôn ngữ
Vòng đầu ĐỎ 4 dòng: đoạn văn tiếng Việt tôi viết dưới khối khuôn trong
`plan-template.md:138-141`. Thân skill phải viết tiếng Anh, chỉ khối khuôn mới được miễn
qua `i18n-allow`. Đã viết lại bằng tiếng Anh, chạy lại ra 0 dòng.

### Q19 hồi quy
```
37 failed, 1308 passed, 1447 subtests passed in 139.59s (0:02:19)
```
Đếm dòng `FAILED` ngoài `test_skill_router.py`: 0.

### QC-F2 hồi quy vùng chạm

Ba lượt chạy trên 14 file test của tầng CLI và tầng hook:

```
`tests/test_plan_tick.py tests/test_state.py tests/test_state_file.py tests/test_check_status.py
tests/test_edit_gate.py tests/test_stop_gate.py tests/test_turn_snapshot.py` → 240 passed, 76 subtests.
`tests/test_next.py tests/test_hook_resilience.py tests/test_gate_merge.py tests/test_mode_phase.py
tests/test_context_hooks.py` → 64 passed, 58 subtests.
`tests/test_luat_skill.py tests/test_ranh_gioi.py` → 26 passed, 329 subtests.
```

### QC-F3 ràng buộc kiến trúc
- `hooks/` gọi `scripts/`, không ngược lại — `stop_gate.py` import từ `tdq_state`, đúng chiều.
- Chỉ `tdq_state.py` ghi `state.json` — ba hàm mới chỉ đọc file markdown, không ghi state.
- Hook chỉ nhắc, không trả `deny` vì lý do chưa duyệt — nhánh mới đi đường
  `additionalContext`, Q11 khoá điều này bằng test.
- File code mới phải nằm trong `scripts/` hoặc `hooks/` — không tạo file code mới.
- Node Hub — không chạm `main()` của `tdq_state.py`, `cli()`, `log()`, `cmd_build()`,
  `Changelog`. Có thêm một lệnh gọi trong `main()` của `stop_gate.py`, đây là hàm cục bộ
  của hook, không phải node Hub cùng tên.

### QC-F4 clean code
- SRP: có. Ba hàm mới mỗi hàm đọc đúng một nguồn — mục DoD của plan, bảng file qc, ô tick
  task. `_dod_hint()` chỉ quyết định có nhắc hay không.
- OCP: có. Thêm một cửa im lặng nữa chỉ là thêm một câu `if ... return []`, không phải mở
  thân hàm cũ.
- LSP: có. Cả ba hàm mới trả về dict cùng bộ khoá ở mọi nhánh, kể cả nhánh lỗi; không hàm
  nào ném lỗi ra ngoài.
- ISP: có. Mọi tham số truyền vào đều được dùng.
- DIP: có. Đi qua `load()`, `_plan_path()` và `_TASK_LINE` sẵn có, không viết lại chi tiết.
  Chính vì vậy `_plan_path()` được TÁCH ra từ `plan_tick_state()` thay vì chép đoạn dò
  đường dẫn lần thứ hai.

## Kết luận
PASS toàn bộ 19 hạng mục DoD cộng 4 hạng mục cố định, sau đúng một lần sửa (luật ngôn ngữ
ở Q17). Trần 3 vòng chưa chạm. QC độc lập bằng agent đang chạy song song theo spec §1b.

## QC vòng 2 — đối chiếu với QC độc lập (agent)

Agent `tdq-qc-tester` chạy song song theo spec §1b, xác nhận 18/19 hạng mục PASS bằng lệnh
tự chạy, FAIL đúng một hạng mục là Q17 (lệnh ghi trong plan sai cú pháp, không phải mã sai),
và nêu thêm 8 defect. Tất cả đã sửa trong vòng này — vòng 1/3 của trần fix.

| # | Defect agent nêu | Mức | Cách sửa | Kiểm | Kết quả |
|---|---|---|---|---|---|
| D1 | đủ 4 nhắc khác thì `[TDQ:DOD]` bị `hints[:MAX_LINES]` cắt mất | TB | xếp nhắc đóng sổ lên ĐẦU danh sách (`hints[:0] =`) | `pytest tests/test_stop_gate.py -q -k dod` | PASS |
| D2 | plan/qc không phải UTF-8 → hook `Stop` rc=1 kèm traceback | TB | ba bộ đọc mới bắt thêm `UnicodeDecodeError` | `pytest tests/test_plan_tick.py -q -k utf` | PASS |
| D3 | hai mục `## Definition of Done` thì chỉ đếm mục đầu | Thấp | `_dod_section` gom mọi mục, không dừng ở mục đầu | `pytest tests/test_plan_tick.py -q -k trung` | PASS |
| D4 | biến thể tiêu đề (`## definition of done (19)`) → mất lưới | Thấp | so khớp không phân biệt hoa thường, cho phép đuôi | `pytest tests/test_plan_tick.py -q -k biento` | PASS |
| D5 | tiêu đề DoD nằm trong khối rào vẫn bị đếm | Thấp | bỏ qua toàn bộ dòng trong khối rào ``` hoặc ~~~ | `pytest tests/test_plan_tick.py -q -k rao` | PASS |
| D6 | ô kết quả qc là `SKIP` bị bỏ qua → `all_pass` sai | Thấp | thêm bộ đếm `pending`, `all_pass` đòi `pending == 0` | `pytest tests/test_plan_tick.py -q -k qcket` | PASS |
| D7 | Q17: `--kind` không cộng dồn và bắt buộc có đường dẫn | Thấp | viết lại dòng Q17 thành ba lần chạy, mỗi lần một kind | chạy nguyên văn ba lệnh | PASS |
| D8 | `luat-hien-co.md` L309/L310 lệch 1 dòng | Thấp | sửa `147/156` thành `148/157` | `pytest tests/test_luat_skill.py -q` | PASS |

Ghi chú phạm vi: `plan_tick_state()` KHÔNG bắt thêm `UnicodeDecodeError` — hàm đó nằm trong
luật cấm chạm của plan (quy tắc 7, điều kiện Q13), và lỗi ném ở đó có sẵn từ trước, không
phải hồi quy của request này. Ghi lại đây làm nợ kỹ thuật, không sửa lén.

Sau vòng 2: `pytest tests/test_plan_tick.py -q` 32 xanh, `tests/test_stop_gate.py -q` 61 xanh,
full suite giữ đúng 37 đỏ mốc nền trong `test_skill_router.py`, `doc_lint --pair` thoát 0.
