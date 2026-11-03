# QC — Điều tra và khắc phục lỗi LSP search gate và tdq_team clean
Ngày: 2026-10-15 · Plan: ../plan/2026-10-15-0958-dieu-tra-loi-lsp-search-team-clean.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Lệnh `tdq_team.py clean` hỗ trợ tham số task tùy chọn và xử lý an toàn khi đã dọn (trả về 0 thay vì exit 2) | `python -m unittest discover -s tests -p "test_team_mode.py" -k "clean"` | 2 tests OK trong 3.473s; `clean T1.1` trả về 0 với thông báo `Worktree for T1.1 already cleaned.` khi đã merge; dọn đúng task khi còn worktree | PASS |
| Q2 | Hook `search_gate.py` và `search_rules.py` tự động phát hiện ngôn ngữ dự án và gợi ý `list_symbols` khi grep trong file cụ thể | `python -m unittest discover -s tests -p "test_search_rules.py" -k "test_loi_nhac_ngon_ngu"` && `python -m unittest discover -s tests -p "test_search_gate.py" -k "TestDoNgonNguDuAn"` | 3 tests OK; câu nhắc in đúng `language_id = "typescript"` và gợi ý `list_symbols` khi grep file cụ thể | PASS |
| Q3 | Khối ghim `KHOI_HUONG_DAN`, `CLAUDE.md` và tài liệu hướng dẫn 3 bước gọi LSP đạt chuẩn độ dài ≤ 25 dòng | `python -m unittest discover -s tests -p "test_tdq_setup.py" -k "khoi_huong_dan"` | 1 test OK; `KHOI_HUONG_DAN` đạt 21 dòng (≤ 25 dòng) | PASS |
| Q4 | Hợp đồng tài liệu, chuẩn ngôn ngữ 3 tầng và khóa ngân sách token | `python scripts/doc_lint.py skills/tdq-setup/references/uu-tien-tim-kiem.md && python scripts/token_budget.py --kiem` | 0 vi phạm `doc_lint`, 50/50 file khớp khóa ngân sách token | PASS |
| QC-F1 | Bộ unit test (mức `lite` chạy `vung-cham`, tự động rơi về trọn bộ khi bán kính ≥ 60%) | `python scripts/tdq_test.py vung-cham` | Bán kính 113/133 modules chạm ngưỡng 60% → chạy trọn bộ 133 modules thành công | PASS |
| QC-F2 | Hồi quy vùng chạm trên toàn bộ các file code và test chạm | `python -m unittest discover -s tests -p "test_team_mode.py" -k "clean"` && `python -m unittest discover -s tests -p "test_search_rules.py"` && `python -m unittest discover -s tests -p "test_search_gate.py"` && `python -m unittest discover -s tests -p "test_tdq_setup.py"` | Toàn bộ 95 tests thuộc 4 module chạm đều PASS 100% | PASS |
| QC-F3 | Ràng buộc kiến trúc trong Spec §5 (`skills/` chỉ nhắc tên lệnh của `scripts/`, ngôn ngữ 3 tầng) | `python scripts/doc_lint.py skills/tdq-setup/references/uu-tien-tim-kiem.md && python scripts/i18n_check.py scripts/search_rules.py hooks/scripts/search_gate.py skills/tdq-setup/references/uu-tien-tim-kiem.md` | 0 vi phạm hợp đồng tài liệu và chuẩn ngôn ngữ 3 tầng | PASS |
| QC-F4 | Tự kiểm 5 câu hỏi SOLID Clean Code (`skills/tdq-conventions/references/clean-code.md`) | Kiểm tra cấu trúc hàm và trách nhiệm trong `scripts/tdq_team.py`, `scripts/search_rules.py`, `hooks/scripts/search_gate.py`, `scripts/tdq_setup.py` | Cả 5 nguyên tắc SRP, OCP, LSP, ISP, DIP đều đạt | PASS |

## Bằng chứng

### Q1
```
..
----------------------------------------------------------------------
Ran 2 tests in 3.473s

OK
```

### Q2
```
.
----------------------------------------------------------------------
Ran 1 test in 0.000s

OK

..
----------------------------------------------------------------------
Ran 2 tests in 0.063s

OK
```

### Q3
```
.
----------------------------------------------------------------------
Ran 1 test in 0.000s

OK
```

### Q4
```
[2026-10-15T12:33:07] doc_lint: lint 1 file: uu-tien-tim-kiem.md
[2026-10-15T12:33:07] doc_lint: done — 0 violation(s) total, exit 0
token_budget: 50 file · cap 3500 · docs\tdq\token-budget.json
```

### QC-F2
```
test_team_mode.py -k clean: 2 tests OK
test_search_rules.py: 63 tests OK
test_search_gate.py: 29 tests OK
test_tdq_setup.py -k khoi_huong_dan: 1 test OK
Tổng cộng 95 tests OK trong 5.6s
```

### QC-F4
- **SRP (Có)**: `lenh_don` trong `tdq_team.py` chỉ phụ trách dọn worktree (của 1 task cụ thể hoặc toàn slug); `do_ngon_ngu_du_an` trong `search_gate.py` chỉ phát hiện ngôn ngữ dự án qua marker; `loi_nhac` trong `search_rules.py` là hàm thuần chỉ format chuỗi thông báo.
- **OCP (Có)**: `FILE_MOC_NGON_NGU` là bảng tra cứu dữ liệu; bổ sung ngôn ngữ mới không cần sửa logic duyệt.
- **LSP (Có)**: Mọi nhánh của `do_ngon_ngu_du_an` trả về `str` hoặc `None`; `lenh_don` luôn trả về mã số nguyên (`0` hoặc `1`).
- **ISP (Có)**: Các hàm chỉ nhận tham số tối thiểu thực sự sử dụng.
- **DIP (Có)**: Tái sử dụng `_thu_don`, `so_wt` và `_boi_canh` trong `tdq_team.py`.

## Lệch spec chờ duyệt
không có

## Kết luận
PASS toàn bộ 4/4 hạng mục DoD và 4/4 hạng mục cố định ở mức QC `lite`.
