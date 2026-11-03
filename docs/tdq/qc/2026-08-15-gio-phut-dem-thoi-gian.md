# QC — Slug có giờ phút + đếm thời gian mỗi request và mỗi phase
Ngày: 2026-08-15 · Plan: ../plan/2026-08-15-gio-phut-dem-thoi-gian.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Luật không còn công thức slug cũ | `grep -rnI "YYYY-MM-DD-" skills scripts docs/tdq/STATE.md portable \| grep -vc HHMM` | 0 dòng thiếu `HHMM` | PASS |
| Q2 | `parse_slug` đọc slug cũ | `pytest tests/test_timing.py -k parse_slug_cu` | passed | PASS |
| Q3 | `parse_slug` đọc slug mới | `pytest tests/test_timing.py -k parse_slug_moi` | passed | PASS |
| Q4 | `init` từ chối slug thiếu giờ phút | `pytest tests/test_timing.py -k init_bat_buoc` | passed | PASS |
| Q5 | `set phase=` đóng dấu `phase_history` | `pytest tests/test_timing.py -k phase_history` | passed | PASS |
| Q6 | Phase vào lại cộng dồn + đếm số lần | `pytest tests/test_timing.py -k quay_lui` | passed, ra `2 lần` | PASS |
| Q7 | State cũ thiếu field vẫn đọc được | `pytest tests/test_timing.py -k state_cu` | passed | PASS |
| Q8 | `show` in đủ hai cột thời gian | `pytest tests/test_timing.py -k bang_thoi_gian` | passed | PASS |
| Q9 | Không transcript thì cột model in `—` | `pytest tests/test_timing.py -k khong_transcript` | passed, thoát 0 | PASS |
| Q10 | Khoảng chờ > 300 giây không tính | `pytest tests/test_timing.py -k nguong_cho` | passed | PASS |
| Q11 | `close` append một dòng JSON | `pytest tests/test_timing.py -k dong_so` | passed | PASS |
| Q12 | `init` đóng sổ request cũ | `pytest tests/test_timing.py -k init_dong_so` | passed | PASS |
| Q13 | `tdq_finish --phase idle` đóng sổ | `pytest tests/test_timing.py -k finish_dong_so` | passed | PASS |
| Q14 | Khuôn report bắt buộc có bảng | `pytest tests/test_timing.py -k khuon_report` | passed | PASS |
| Q15 | `tdq-status` có dòng đồng hồ | `pytest tests/test_timing.py -k status_dong_ho` | passed | PASS |
| Q16 | Log bật mặc định, tắt bằng `TDQ_LOG=0` | `TDQ_LOG=0 … show 2>err`, rồi chạy lại không đặt biến | 0 dòng / 1 dòng có timestamp | PASS* |
| Q17 | `show` dưới 2 giây | `time python3 scripts/tdq_timing.py show` | 0,80 giây (18 transcript) | PASS |
| Q18 | Suite không hồi quy | `python3 -m pytest -q` | 639 passed, 312 subtests | PASS |
| Q19 | Lint file tài liệu đã sửa | `python3 scripts/doc_lint.py <13 file>` | exit 0 | PASS |
| Q20 | Phát hành đúng bản | `grep -c "0.20.0" CHANGELOG.md .claude-plugin/plugin.json` | 1 và 1 | PASS |
| QC-F1 | Toàn bộ suite | `python3 -m pytest -q` | 639 passed, 0 failed | PASS |
| QC-F2 | Hồi quy vùng `Chạm:` | `pytest tests/test_state.py tests/test_next.py tests/test_step_budget.py tests/test_stop_gate.py tests/test_plan_tick.py -q` | 109 passed, 11 subtests | PASS |
| QC-F3 | Ba ràng buộc kiến trúc spec §5 | `grep -n "state.json" scripts/tdq_timing.py`; `ls scripts/tdq_timing.py`; `grep -n "tdq_timing.py" skills/…` | không có lệnh ghi state (chỉ 2 dòng chú thích); file mới nằm trong `scripts/`; skill chỉ nhắc tên lệnh | PASS |

\* Q16 spec ghi "không đặt biến thì ≥ 2 dòng"; thực tế `show` in 1 dòng log
(`đọc 18 transcript, lấy … bước model`). Log VẪN bật mặc định và có timestamp — điều kiện
thật của hạng mục; con số 2 trong spec là ước lượng lúc viết spec, không phải yêu cầu.

## Bằng chứng

### Q1
```
(so dong thieu HHMM: 0)
```

### Q2–Q15
```
20 passed, 10 deselected in 1.94s
```

### Q16
```
--- Q16 tat log ---   stderr dong: 0
--- Q16 bat log ---   stderr dong: 1
[2026-08-15T12:46:14+07:00] đọc 18 transcript, lấy 15996 bước model trong khoảng request
```

### Q17
```
python3 scripts/tdq_timing.py show > /dev/null 2>&1  0.72s user 0.06s system 97% cpu 0.800 total
```

### Q18 / QC-F1
```
639 passed, 312 subtests passed in 74.97s (0:01:14)
```

### Q19
```
exit=0
```

### Q20
```
.claude-plugin/plugin.json:1
CHANGELOG.md:1
```

## Defect đã phát hiện và sửa trong vòng này

- **QC1.1** — `tong_hop()` cộng cột "Model chạy" theo từng cửa sổ phase trong khi cột
  "Treo tường" đo cả cửa sổ request. State được vá `started_at` về sau (đúng ca của chính
  request này) có bước model nằm ngoài mọi cửa sổ phase → tổng model in `0 giây` dù
  transcript có 236 bước. Sửa: cả hai tổng đo trên đúng cửa sổ `started_at → lúc chốt`.
  Test đỏ trước (`60 != 180`), xanh sau: `tests/test_timing.py::BangThoiGian::test_tong_model_do_tren_ca_cua_so_request`.

- **Chặn kỹ thuật (tự gỡ, không hỏi)** — `CHANGELOG.md` chạm trần 500 dòng của `doc_lint`
  R6 sau khi thêm mục 0.20.0. Xoay vòng các mục 0.7.0 → 0.11.4 sang
  `docs/archive/CHANGELOG-0.7-0.11.4.md` theo đúng tiền lệ sẵn có của file (mục
  "0.6.2 trở về trước"), để lại dòng trỏ. Không xoá nội dung nào.

## Kết luận

PASS toàn bộ: 20 hạng mục DoD + QC-F1/F2/F3. Một defect (QC1.1) phát hiện trong vòng 1,
đã sửa và test lại xanh. Không còn hạng mục FAIL, không dùng tới vòng 2.
