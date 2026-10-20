# QC — Nâng Cấp Khảo Sát Code 3 Chiều & Bảo Toàn Chủ Đích Refactor
Ngày: 2026-10-20 · Plan: ../plan/2026-10-20-1355-nang-cap-khao-sat-3-chieu-refactor.md · Vòng: 1 · Mức QC: `full`
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Gate tìm kiếm mở khóa trong Analyze | `python3 tests/test_khao_sat_3_chieu.py` & `python3 tests/test_search_gate.py` | Khi phase là `analyze`/`quick_analyze`/`spec`, các lệnh grep được cho phép tự do không bị deny; test coverage 6/6 và 34/34 | PASS |
| Q2 | Hàng rào Implement giữ nguyên | `python3 tests/test_khao_sat_3_chieu.py` & `python3 tests/test_search_replay.py` | Khi phase là `implement`, search_gate vẫn duy trì quy tắc 3 tầng chuẩn; replay 63 events bắt 11 vi phạm chính xác 100% | PASS |
| Q3 | Ngoại lệ Refactor cho Rung 1 | `python3 tests/test_khao_sat_3_chieu.py` & `python3 scripts/doc_lint.py skills/tdq-build/references/rules/chung.md` | `chung.md` chứa ngoại lệ bảo toàn Clean Architecture/SOLID khi người dùng yêu cầu Refactor; doc_lint 0 violation(s) | PASS |
| Q4 | Bảng Hiện trạng Trước vs Sau & Đồng bộ | `python3 scripts/doc_lint.py skills/tdq-spec/references/spec-template.md skills/tdq-plan/references/plan-template.md` & `python3 tests/test_claude_md_core.py` | `spec-template.md`, `plan-template.md`, `CLAUDE.md`, `docs/claude-md-mau.md` có khối so sánh Trước vs Sau và bảng 3 chiều | PASS |
| QC-F1 | Trọn suite vùng chạm | `python3 tests/test_khao_sat_3_chieu.py`, `tests/test_search_gate.py`, `tests/test_search_rules.py`, `tests/test_search_observe.py`, `tests/test_search_replay.py`, `tests/test_codex_search_gate.py`, `tests/test_tdq_setup.py`, `tests/test_build_portable.py`, `tests/test_claude_md_core.py`, `tests/test_doc_index.py`, `tests/test_docs_consistency.py` | Toàn bộ các suite kiểm thử trọng yếu đều đạt 100% PASS không lỗi | PASS |
| QC-F2 | Hồi quy vùng chạm | `python3 tests/test_search_gate.py` & `python3 tests/test_search_replay.py` | Kiểm tra toàn bộ vùng tương tác PreToolUse và replay session không xuất hiện hồi quy | PASS |
| QC-F3 | Ràng buộc kiến trúc | `python3 tests/test_kien_truc.py` | Đảm bảo đúng kiến trúc phân lớp, không vòng lặp phụ thuộc | PASS |
| QC-F4 | Clean code | `python3 scripts/doc_lint.py` trên toàn bộ tài liệu đã sửa | 0 violations (R5 độ dài câu <= 40 từ, R6 độ dài dòng, R13 token budget <= 3500) | PASS |

## Bằng chứng kiểm thử chi tiết

### Q1 — Gate tìm kiếm mở khóa trong Analyze
```
python3 tests/test_khao_sat_3_chieu.py
Ran 6 tests in 0.001s · OK

python3 tests/test_search_gate.py
Ran 34 tests in 2.858s · OK
- test_phase_analyze_cho_phep_grep_tu_do: PASS (không bị chặn)
- test_grep_tu_do_trong_cac_pha_khao_sat: PASS ("free code search in exploration phase")
```

### Q2 — Hàng rào Implement giữ nguyên
```
python3 tests/test_search_replay.py
Ran 11 tests in 0.309s · OK
- search_replay: 63 events · 21 searches · denied 11 · false denials 0 · leaks 0
- test_grep_kiem_soat_trong_pha_implement: PASS (chặn trước concept query và chặn guess-list quá quota)
```

### Q3 — Ngoại lệ Refactor cho Rung 1
```
python3 scripts/doc_lint.py skills/tdq-build/references/rules/chung.md
[doc_lint] lint 1 file: chung.md
[doc_lint] done — 0 violation(s) total, exit 0
Nội dung ngoại lệ: "Chủ đích Refactor & Mở rộng Kiến trúc: Khi người dùng yêu cầu Refactor, tái cấu trúc hoặc áp dụng Clean Architecture/SOLID: cấu trúc sạch và tính mở rộng đứng TRÊN luật phẫu thuật 1 dòng tối thiểu. Cấm tự ý ép gộp các layer, service, adapter hợp lý thành hàm phẳng nếu làm vỡ thiết kế mong muốn."
```

### Q4 — Bảng Hiện trạng Trước vs Sau & Đồng bộ
```
python3 scripts/doc_lint.py skills/tdq-spec/references/spec-template.md skills/tdq-plan/references/plan-template.md
[doc_lint] done — 0 violation(s) total, exit 0

python3 tests/test_claude_md_core.py
Ran 12 tests in 0.008s · OK (đồng bộ nguyên văn giữa tdq_setup.py, CLAUDE.md và docs/claude-md-mau.md)
```

### QC-F1 & QC-F4 — Suite & Linter
```
- tests/test_khao_sat_3_chieu.py: 6/6 PASS
- tests/test_search_gate.py: 34/34 PASS
- tests/test_search_rules.py: 76/76 PASS
- tests/test_search_observe.py: 24/24 PASS
- tests/test_search_replay.py: 11/11 PASS
- tests/test_codex_search_gate.py: 16/16 PASS
- tests/test_tdq_setup.py: 43/43 PASS
- tests/test_build_portable.py: 37/37 PASS
- tests/test_claude_md_core.py: 12/12 PASS
- tests/test_doc_index.py: 26/26 PASS
- tests/test_docs_consistency.py: 8/8 PASS
- doc_lint: 0 violations trên tất cả file tài liệu đã cập nhật.
```
