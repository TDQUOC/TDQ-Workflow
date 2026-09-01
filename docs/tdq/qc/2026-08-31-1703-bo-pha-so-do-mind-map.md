# QC — bỏ pha sơ đồ mind map khỏi quy trình TDQ

Ngày: 2026-09-01 · Plan: ../plan/2026-08-31-1703-bo-pha-so-do-mind-map.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Mốc trước khi sửa

Lệnh: `python3 -m pytest tests/ -q` trên cây làm việc trước task T1.2 (2026-09-01 18:44).

```
101 failed, 1642 passed, 1454 subtests passed in 217.51s
```

Phân bố lỗi theo file (đếm cả `FAILED` và `SUBFAILED`):

| File test | Số lỗi |
|---|---|
| tests/test_skill_router.py | 97 |
| tests/test_rules_library.py | 1 |
| tests/test_luat_skill.py | 1 |
| tests/test_doc_lint.py | 1 |
| tests/test_bench.py | 1 |

Đây là mốc so sánh cho Q14: sau khi sửa, số lỗi không được lớn hơn 101 và không file mới
nào xuất hiện trong bảng trên.

## Kết quả QC

Chạy bởi agent QC độc lập (`tdq-qc-tester`), hai vòng, chỉ đọc và chạy lệnh.

Vòng 1 — FAIL 3 mục:

- Q3 hỏng thật: nhánh cũ ở cổng vào pha `plan` chỉ soi danh sách sơ đồ; gỡ pha sơ đồ mà không
  thay thế thì cổng rỗng, plan viết được trước khi user duyệt spec. Đúng rủi ro spec đã nêu.
- Q10/Q11 không thoát 0: 25 vi phạm R5/R2/R8 ở `docs/archive/v0.1/` và 2 vi phạm R5 ở `skills/`,
  cả 5 file byte y hệt HEAD → nợ lint có sẵn, không do request này.

Sửa ở P9: `T9.1` thêm `_chan_spec_chua_duyet` (gọi khi `set phase=plan`) kèm test nhánh nghịch
`test_vao_plan_bi_chan_khi_spec_chua_duyet`; `T9.2` thu hẹp lời kiểm Q10/Q11 về đúng phạm vi
request và ghi rõ nợ cũ.

Vòng 2 — PASS toàn bộ Q1..Q17:

| Mục | Bằng chứng |
|---|---|
| Q1, Q4, Q5 | `set phase=diagram`, `approve diagram`, `diagram add|list` đều thoát 2, thông điệp nói rõ pha đã gỡ |
| Q2, Q16 | `pytest tests/test_next.py -q` 8 passed; `tests/test_e2e_chain.py -q` 2 passed |
| Q3 | spec chưa duyệt → `set phase=plan` thoát 2, pha không đổi; duyệt spec rồi → thoát 0 |
| Q6, Q7, Q8 | state cũ có `diagrams` / `phase=diagram` nạp được, bảng trạng thái hết dòng Diagrams |
| Q9, Q12, Q13 | file đã xoá; `grep -rn` trên `skills/` im lặng |
| Q10, Q11 | `doc_lint.py docs/tdq` và 4 skill đã dọn đều thoát 0 |
| Q14 | `pytest tests/ -q` = 101 failed, 1450 passed — bằng mốc T1.1, không file mới trong bảng lỗi |
| Q15 | `tdq_checkportable.py check` CLEAN 90 / 138 / 83 cho 3 bundle |
| Q17 | `doc_lint.py CHANGELOG.md` thoát 0; mục 0.36.0 nêu việc gỡ pha và cổng plan chặn thật |

Ghi nhận mức thấp, không chặn phát hành: thông điệp 3 lệnh cũ viết bằng tiếng Anh ("removed")
thay vì "đã gỡ" như câu chữ Q4/Q5; `_fail` in không kèm timestamp — nợ có sẵn, `git show HEAD`
xác nhận giống hệt bản cũ.
