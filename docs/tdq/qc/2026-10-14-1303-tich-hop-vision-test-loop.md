# QC — Tích hợp khung mindset kiểm thử thực tế và vòng lặp Vision Test Loop vào TDQ Workflow
Ngày: 2026-10-14 · Plan: ../plan/2026-10-14-1303-tich-hop-vision-test-loop.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Công cụ CLI `scripts/tdq_vision_diff.py` xử lý chuẩn xác ảnh đối chiếu (Canvas Padding, Masking, Bounding Box `[1]`, `[2]`, `metrics.json`) | `python -m unittest tests/test_tdq_vision_diff.py` | 10/10 bài test xử lý ảnh, Bounding Box, mask và metrics PASS trong 0.302s | PASS |
| Q2 | Xuất bộ đôi báo cáo Markdown (`.md`) & Interactive HTML (`.html`) kèm hỗ trợ `--embed-base64` và `--figma-url` | `python -m unittest tests/test_tdq_vision_diff.py -k report -k figma` | 3/3 bài test báo cáo tương đối, `--embed-base64`, `--figma-url` (exit code 3 khi thiếu `FIGMA_TOKEN`) PASS | PASS |
| Q3 | Bộ Unit Test của `tdq_vision_diff` và Log Service (`TDQ_LOG=0`) xanh 100% | `python -m unittest tests/test_tdq_vision_diff.py -k "log"` | 2/2 bài test Log Service (unit + subprocess thực tế) PASS, có ISO timestamp trên `stderr` và tắt sạch khi `TDQ_LOG=0` | PASS |
| Q4 | File Skill Rule Reference chi tiết `skills/tdq-build/references/vision-test-loop.md` cho cả model tier thấp & liên kết tầng 1 trong `skills/` đầy đủ | `PYTHONPATH=tests python -m unittest tests/test_vision_test_loop_doc.py tests/test_reference_mot_tang.py tests/test_rules_library.py` | 15/15 bài test kiểm tra hợp đồng tài liệu, liên kết 1 tầng và thư viện rules PASS | PASS |
| Q5 | Hợp đồng Tài liệu, Ngôn ngữ, Chỉ mục dòng & Khóa Ngân sách Token (≤ 3500 tokens/file) đạt 0 vi phạm | `python scripts/doc_lint.py skills && python scripts/token_budget.py --kiem && python scripts/i18n_check.py scripts/tdq_vision_diff.py skills/tdq-build/references/vision-test-loop.md skills/tdq-build/references/rules/chung.md skills/tdq-build/references/rules/html.md` | `doc_lint.py`: 0 vi phạm trên 59 file; `token_budget.py --kiem`: exit 0 (`vision-test-loop.md` = 2059 tokens ≤ 3500); `i18n_check.py`: 0 dòng tiếng Việt | PASS |
| Q6 | Thẩm định QC mức `ultra` (Smoke test, Runtime test thực tế tạo báo cáo mẫu, trọn bộ unit test và agent `tdq-qc-tester` độc lập) | Smoke + Runtime 1080p CLI (< 120s cap), `tdq-qc-tester` agent, `tdq_test.py vung-cham` & `tron-bo` | Smoke/Runtime 1920x1080 chạy trong 0.224s (vòng 1) và 0.266s (vòng 2, < 2.0s ngưỡng); `tdq-qc-tester` báo `VERDICT: PASS everything`; `vung-cham` 876/876 PASS | PASS |
| QC-F1 | Trọn bộ test suite (`tron-bo`) + sổ kiểm (`so`) | `python scripts/tdq_test.py tron-bo && python scripts/tdq_test.py so` | Chạy 133 module (2573 tests); phát hiện `test_luat_skill.py` lệch dòng điểm neo, đã sửa ngay qua `QC1.1`–`QC1.2` và chạy lại `test_luat_skill.py` PASS 11/11 (2 bài `test_codex_cli.py`, `test_tu_khoi_tao.py` là lỗi tồn đọng ngoài vùng chạm) | PASS |
| QC-F2 | Touched-area regression cho toàn bộ dòng `Chạm:` trong plan | `PYTHONPATH=tests python -m unittest tests/test_tdq_vision_diff.py tests/test_vision_test_loop_doc.py tests/test_reference_mot_tang.py tests/test_rules_library.py tests/test_token_budget.py tests/test_skill_shape.py tests/test_luat_skill.py` | 56/56 bài test trên toàn bộ vùng chạm đều PASS, 0 node thiếu test | PASS |
| QC-F3 | Ràng buộc kiến trúc phải giữ (Spec §5) | Kiểm 3 ràng buộc: Liên kết 1 tầng (`test_reference_mot_tang.py`), Hợp đồng tài liệu & ngân sách token (`doc_lint.py skills` + `token_budget.py --kiem`), Trần thư mục `rules/` (`test_rules_library.py`) | Cả 3 ràng buộc kiến trúc đều PASS 100% | PASS |
| QC-F4 | Clean code 5 câu hỏi (`clean-code.md`) trên `scripts/tdq_vision_diff.py` | Kiểm tra AST cyclomatic complexity (`max_cyclomatic = 9 ≤ 10`), SRP, OCP, DIP, 0 dead code, 0 magic number | 5/5 câu hỏi trả lời CÓ | PASS |

## Bằng chứng
### Q1, Q2, Q3 — Unit tests `tests/test_tdq_vision_diff.py`
```
test_bounding_boxes_and_highlight ... ok
test_cli_missing_input_returns_exit_2 ... ok
test_cli_subprocess_log_service_on_and_off ... ok
test_figma_url_missing_token_returns_exit_3 ... ok
test_figma_url_with_mock_opener ... ok
test_ignore_boxes_masking ... ok
test_log_service_default_and_disabled ... ok
test_multi_round_timeline_history ... ok
test_normalize_canvas_no_distortion ... ok
test_reports_relative_and_base64 ... ok
----------------------------------------------------------------------
Ran 10 tests in 0.302s
OK
```

### Q4, Q5 — Hợp đồng tài liệu, liên kết tầng 1, `doc_lint`, `token_budget`, `i18n_check`
```
[2026-10-14T14:27:31] token_budget: 50 file · cap 3500 · docs\tdq\token-budget.json
Ran 25 tests in 2.763s (test_luat_skill, test_token_budget, test_vision_test_loop_doc) — OK
[2026-10-14T14:27:34] doc_lint: lint 59 file ... done — 0 violation(s) total, exit 0
[2026-10-14T14:10:23] i18n_check: scan 4 file(s), kind=all — 0 Vietnamese line(s) in 4 file(s), exit 0
```

### Q6 — Smoke test & Runtime test 1920x1080 (dưới trần 120s) + `tdq-qc-tester` độc lập
```
SMOKE_RUNTIME_1080P: r1_rc=1 dt1=0.224s boxes_r1=1 mismatch_r1=0.0236 | r2_rc=0 dt2=0.266s boxes_r2=0 mismatch_r2=0.0 html_len=42243
tdq-qc-tester E1 probe: missing_src=2 missing_figma=3 neg_ignore=2 bad_ignore=2 log0_stderr_len=0 canvas=[120, 100] rounds=2 corrupt_img=2 / max_cyclomatic=9 (main)
VERDICT: PASS everything
```

### QC-F1, QC-F2, QC-F3, QC-F4
```
vung-cham: 25 changed file(s); selected 39/133 modules -> Ran 876 tests in 124.760s OK (skipped=7)
tron-bo: Ran 2573 tests in 484.209s (sửa lệch dòng L### qua QC1.1-QC1.2 -> test_luat_skill.py: Ran 11 tests in 0.135s OK)
Clean Code 5 câu hỏi cho scripts/tdq_vision_diff.py:
1. Mỗi hàm/module có đúng một lý do để đổi (SRP)? -> CÓ (tách biệt normalize_canvas, apply_ignore_mask, compute_diff_mask, find_bounding_boxes, render_highlight_image, write_reports, fetch_figma_source).
2. Thêm trường hợp mới có tránh phải sửa hàm điều phối (OCP)? -> CÓ (nhận mọi nguồn qua --source hoặc --figma-url và opener tiêm từ ngoài).
3. Hàm điều phối nhận phụ thuộc từ ngoài (DIP)? -> CÓ (fetch_figma_source nhận opener để unit test không phụ thuộc mạng).
4. Không có code chết hay nhánh phòng thủ thừa? -> CÓ (0 dead code, 0 TODO/FIXME).
5. Không có con số trần trụi (magic number)? -> CÓ (các hằng số DEFAULT_PIXEL_TOLERANCE, DEFAULT_CELL_SIZE, EXIT_DIFF_EXCEEDED=1, EXIT_USAGE_OR_IO_ERROR=2, EXIT_FIGMA_TOKEN_MISSING=3 được đặt tên tường minh).
```

## Lệch spec chờ duyệt
không có

## Kết luận
PASS toàn bộ (sau khi hoàn tất `QC1.1` và `QC1.2` trong vòng 1 để giữ nguyên số dòng các điểm neo `L###` trong `luat-hien-co.md`).
