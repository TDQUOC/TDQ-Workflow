# QC — Đánh giá độ chi tiết instruction TDQ Workflow cho model tier thấp và phương án tối ưu token context

Ngày: 2026-10-15 · Plan: ../plan/2026-10-15-1300-danh-gia-instruction-tier-thap.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Báo cáo RFC lưu tại `docs/kien-truc-instruction-lazy-load.md` hoàn chỉnh 5 phần lớn | `python scripts/doc_lint.py docs/kien-truc-instruction-lazy-load.md` | Tài liệu 200 dòng đạt 0 vi phạm lint; chứa đầy đủ 5 phần lớn: hiện trạng ~90k tokens, 7 điểm gãy, bài học vision-test-loop, 4 giải pháp kiến trúc, lộ trình 3 giai đoạn | PASS |
| Q2 | Hook `session_start.py` hoãn nạp thân luật gọn khi ở phase ngoài `implement` | `python -m unittest discover -s tests -p "test_context_hooks.py" -k "TestThanLuatKenhPhien"` | 9 tests OK; ở phase non-implement chỉ in 1 dòng tóm tắt (< 200 tokens); ở phase implement in đầy đủ thân luật | PASS |
| Q3 | Bộ test tự động hóa kiểm chứng cơ chế nạp context có điều kiện của `session_start.py` | `python -m unittest discover -s tests -p "test_context_hooks.py"` && `python -m unittest discover -s tests -p "test_log_kenh_luat.py"` | 48 tests OK (37 test context hooks + 11 test log kênh luật); ghi nhận đúng `so_dong` theo phase | PASS |
| Q4 | Hợp đồng tài liệu, chuẩn ngôn ngữ 3 tầng và khóa ngân sách token | `python scripts/doc_lint.py --pair docs/tdq/spec/2026-10-15-1300-danh-gia-instruction-tier-thap.md docs/tdq/plan/2026-10-15-1300-danh-gia-instruction-tier-thap.md && python scripts/token_budget.py --kiem` | 0 vi phạm pairing, 50/50 file khớp khóa ngân sách token | PASS |
| QC-F1 | Bộ unit test (mức `lite` chạy `vung-cham`) | `python scripts/tdq_test.py vung-cham --files hooks/scripts/session_start.py tests/test_context_hooks.py tests/test_log_kenh_luat.py` | 236 tests trong 17 modules chạy xanh 100% trong 46.091s | PASS |
| QC-F2 | Hồi quy vùng chạm trên toàn bộ các file hook và test | `python -m unittest discover -s tests -p "test_context_hooks.py"` && `python -m unittest discover -s tests -p "test_log_kenh_luat.py"` && `python -m unittest discover -s tests -p "test_kenh_luat_dedupe.py"` | Toàn bộ 62 tests thuộc 3 test modules chạm đều PASS 100% | PASS |
| QC-F3 | Ràng buộc kiến trúc trong Spec §5 (luật gọn nội hóa, ngôn ngữ 3 tầng) | `python scripts/doc_lint.py docs/kien-truc-instruction-lazy-load.md` | Giữ đúng luật gọn, chuỗi máy in ra trong hook bằng tiếng Anh cố định | PASS |
| QC-F4 | Tự kiểm 5 câu hỏi SOLID Clean Code (`skills/tdq-conventions/references/clean-code.md`) | Kiểm tra cấu trúc phân nhánh và trách nhiệm trong `hooks/scripts/session_start.py` | Cả 5 nguyên tắc SRP, OCP, LSP, ISP, DIP đều đạt | PASS |

## Bằng chứng

### Q1 & Q4
```
[2026-10-15T13:34:12] doc_lint: pairing 2026-10-15-1300-danh-gia-instruction-tier-thap.md ↔ 2026-10-15-1300-danh-gia-instruction-tier-thap.md
[2026-10-15T13:34:12] doc_lint: lint 1 file: kien-truc-instruction-lazy-load.md
[2026-10-15T13:34:12] doc_lint: done — 0 violation(s) total, exit 0
token_budget: 50 file · cap 3500 · docs\tdq\token-budget.json
```

### Q2 & Q3
```
.....................................
----------------------------------------------------------------------
Ran 37 tests in 6.368s

OK

...........
----------------------------------------------------------------------
Ran 11 tests in 4.112s

OK
```

### QC-F1
```
vung-cham: 3 changed file(s); selected 17/133 modules
Ran 236 tests in 46.091s
OK
[2026-10-15T13:37:23+07:00] tdq_test: vung-cham files=3 modules=17/133 fallback=none ok=True seconds=47.11
```

### QC-F2
```
test_context_hooks.py: 37 tests OK
test_log_kenh_luat.py: 11 tests OK
test_kenh_luat_dedupe.py: 14 tests OK
```
