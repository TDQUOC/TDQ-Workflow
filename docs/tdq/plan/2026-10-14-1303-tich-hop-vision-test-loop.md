# PLAN — Tích hợp khung mindset kiểm thử thực tế và vòng lặp Vision Test Loop vào TDQ Workflow

Ngày: 2026-10-14 · Spec: ../spec/2026-10-14-1303-tich-hop-vision-test-loop.md (bản 1.1, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — tdq_bench.py simulate đo 4 task / 2 đợt: subagent 6.1 phút so với main 8.1 phút (lợi 2.0 phút ở hệ số agent 1.5)
Trạng thái plan: HOÀN THÀNH

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Xây dựng công cụ CLI `scripts/tdq_vision_diff.py` & Unit Tests
- P2 — Xây dựng Skill Rule Reference chi tiết cho cả model tier thấp (`vision-test-loop.md`)
- P3 — Liên kết tầng 1 trong `skills/`, cập nhật chỉ mục dòng & khóa ngân sách token
- P4 — Log & test bắt buộc
- Cụm song song
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Mỗi bước: `tdq_test.py vung-cham`; trọn bộ chỉ ở QC.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — Xây dựng công cụ CLI `scripts/tdq_vision_diff.py` & Unit Tests

- [x] **T1.1** (e12m) Xây dựng `scripts/tdq_vision_diff.py` và bộ unit test `tests/test_tdq_vision_diff.py` (TDD đỏ → xanh): chuẩn hóa kích thước bằng Canvas Padding (`normalize_canvas`), loại trừ vùng động (`apply_ignore_mask` với `--ignore-boxes`), gom cụm sai lệch trên lưới ô và vẽ Bounding Box đỏ đánh số `[1]`, `[2]` lên `diff_highlight.png`, xuất `metrics.json`, render bộ đôi báo cáo `<slug>.md` và `<slug>.html` từ template tĩnh dựng sẵn (mặc định đường dẫn tương đối + cờ `--embed-base64`), hỗ trợ `--figma-url` (trả exit code `3` khi thiếu `FIGMA_TOKEN`). `Tạo mới thay vì dùng scripts/tdq_test.py vì tdq_test.py là trình điều phối chạy unittest theo bán kính vùng chạm, còn tdq_vision_diff.py là công cụ xử lý ảnh Pillow và render báo cáo thị giác độc lập` — Test: `python -m unittest tests/test_tdq_vision_diff.py`
  - Chạm: `scripts/tdq_vision_diff.py`, `tests/test_tdq_vision_diff.py` → file mới, chưa node nào phụ thuộc

**Xong P1 khi**: `python -m unittest tests/test_tdq_vision_diff.py` chạy xanh 100% các bài test xử lý ảnh, Bounding Box, báo cáo `.md`/`.html` và `--figma-url`.

## P2 — Xây dựng Skill Rule Reference chi tiết cho cả model tier thấp (`vision-test-loop.md`)

- [x] **T2.1** (e10m) Tạo file `skills/tdq-build/references/vision-test-loop.md` và bài test kiểm tra hợp đồng `tests/test_vision_test_loop_doc.py` (TDD đỏ → xanh): thiết kế hướng dẫn từng bước cơ học cho cả model tier thấp gồm Bảng quyết định kích hoạt (Trigger Decision Table cho mockup, wireframe, screenshot mẫu, prototype HTML/web, Figma), công thức kịch bản 3 tầng (`Given - When - Then`), bảng 6 Anti-Patterns cấm kỵ (`ANTI-1`..`ANTI-6`) kèm ví dụ `WRONG vs RIGHT`, 6 bước Vision Test Loop copy-pasteable, bảng ánh xạ hộp đỏ `[1]`, `[2]` sang thuộc tính CSS/HTML, trần 3 vòng auto-fix + dừng sớm, Reviewer Sub-agent (trần 1 lượt feedback), kịch bản Human-in-the-loop và Checklist tự kiểm (`Self-check`). `Tạo mới thay vì dùng skills/tdq-build/references/rules/html.md vì người dùng yêu cầu rõ một file skill rule reference chi tiết cho cả model tier thấp và thư mục con references/rules/ bị khóa trần 10 file < 150 dòng` — Test: `python -m unittest tests/test_vision_test_loop_doc.py`
  - Chạm: `skills/tdq-build/references/vision-test-loop.md`, `tests/test_vision_test_loop_doc.py` → file mới, chưa node nào phụ thuộc

**Xong P2 khi**: `tests/test_vision_test_loop_doc.py` chạy xanh và `python scripts/doc_lint.py skills/tdq-build/references/vision-test-loop.md` đạt 0 vi phạm R1–R7.

## P3 — Liên kết tầng 1 trong `skills/`, cập nhật chỉ mục dòng & khóa ngân sách token

- [x] **T3.1** (e4m) Cập nhật liên kết tầng 1 tới `references/vision-test-loop.md` trong `skills/tdq-build/SKILL.md`, `skills/tdq-spec/SKILL.md`, `skills/tdq-build/references/qc.md` và `skills/tdq-build/references/rules/chung.md` — Test: `python -m unittest tests/test_reference_mot_tang.py`
  - Chạm: `skills/tdq-build/SKILL.md`, `skills/tdq-spec/SKILL.md`, `skills/tdq-build/references/qc.md`, `skills/tdq-build/references/rules/chung.md`
  - Cần: T1.1, T2.1
- [x] **T3.2** (e4m) Cập nhật liên kết tới `vision-test-loop.md` trong `skills/tdq-build/references/rules/html.md`, `skills/tdq-spec/references/spec-template.md`; chạy `scripts/doc_index.py --tat-ca` và `scripts/token_budget.py` để khóa `docs/tdq/token-budget.json` — Test: `python scripts/doc_lint.py skills && python scripts/token_budget.py --kiem`
  - Chạm: `skills/tdq-build/references/rules/html.md`, `skills/tdq-spec/references/spec-template.md`, `docs/tdq/token-budget.json`
  - Cần: T3.1

**Xong P3 khi**: `doc_lint.py skills`, `token_budget.py --kiem`, `test_reference_mot_tang.py` và `test_rules_library.py` đều xanh 100%.

## P4 — Log & test bắt buộc

- [x] **T4.1** (e4m) Kiểm chứng Log service bật mặc định của `scripts/tdq_vision_diff.py` (xuất ISO timestamp ra `stderr`, tắt hoàn toàn qua `TDQ_LOG=0`) và kiểm tra ngôn ngữ `i18n_check.py` trên toàn bộ file chạm — Test: `python -m unittest tests/test_tdq_vision_diff.py tests/test_vision_test_loop_doc.py && python scripts/i18n_check.py scripts/tdq_vision_diff.py skills/tdq-build/references/vision-test-loop.md skills/tdq-build/references/rules/chung.md skills/tdq-build/references/rules/html.md`
  - Chạm: `tests/test_tdq_vision_diff.py`, `tests/test_vision_test_loop_doc.py`
  - Cần: T3.2

**Xong P4 khi**: Log service test xanh và `i18n_check.py` đạt 0 vi phạm.

## Cụm song song

- **Đợt 1 (Song song được)**: `T1.1` (chạm `scripts/tdq_vision_diff.py`, `tests/test_tdq_vision_diff.py`) và `T2.1` (chạm `skills/tdq-build/references/vision-test-loop.md`, `tests/test_vision_test_loop_doc.py`) — không giao vùng file.
- **Đợt 2 (Tuần tự sau Đợt 1)**: `T3.1` (liên kết `skills/` và khóa `token-budget.json`).
- **Đợt 3 (Tuần tự sau Đợt 2)**: `T4.1` (kiểm chứng log service và `i18n_check.py`).

## Definition of Done

- [x] Q1 Công cụ CLI `scripts/tdq_vision_diff.py` xử lý chuẩn xác ảnh đối chiếu (Canvas Padding, Masking, Bounding Box `[1]`, `[2]`, `metrics.json`) — `python -m unittest tests/test_tdq_vision_diff.py`
- [x] Q2 Xuất bộ đôi báo cáo Markdown (`.md`) & Interactive HTML (`.html`) kèm hỗ trợ `--embed-base64` và `--figma-url` — `python -m unittest tests/test_tdq_vision_diff.py -k "report or figma or base64"`
- [x] Q3 Bộ Unit Test của `tdq_vision_diff` và Log Service (`TDQ_LOG=0`) xanh 100% — `python -m unittest tests/test_tdq_vision_diff.py -k "log"`
- [x] Q4 File Skill Rule Reference chi tiết `skills/tdq-build/references/vision-test-loop.md` cho cả model tier thấp & liên kết tầng 1 trong `skills/` đầy đủ — `python -m unittest tests/test_vision_test_loop_doc.py tests/test_reference_mot_tang.py tests/test_rules_library.py`
- [x] Q5 Hợp đồng Tài liệu, Ngôn ngữ, Chỉ mục dòng & Khóa Ngân sách Token (≤ 3500 tokens/file) đạt 0 vi phạm — `python scripts/doc_lint.py skills && python scripts/token_budget.py --kiem && python scripts/i18n_check.py scripts/tdq_vision_diff.py skills/tdq-build/references/vision-test-loop.md skills/tdq-build/references/rules/chung.md skills/tdq-build/references/rules/html.md`
- [x] Q6 Thẩm định QC mức `ultra` (Smoke test, Runtime test thực tế tạo báo cáo mẫu, trọn bộ unit test và agent `tdq-qc-tester` độc lập) PASS 100% — `python scripts/tdq_test.py tron-bo`

## QC vòng 1 — fix

- [x] **QC1.1** (e2m) Giữ nguyên số dòng các điểm neo `L###` trong `skills/tdq-spec/SKILL.md` và `skills/tdq-build/references/qc.md` khi gắn liên kết `vision-test-loop.md` — Test: `python -m unittest tests/test_luat_skill.py`
  - Chạm: `skills/tdq-spec/SKILL.md`, `skills/tdq-build/references/qc.md`
- [x] **QC1.2** (e2m) Giữ nguyên số dòng các điểm neo `L###` trong `skills/tdq-build/references/rules/chung.md` và khóa lại `docs/tdq/token-budget.json` — Test: `python -m unittest tests/test_luat_skill.py tests/test_token_budget.py`
  - Chạm: `skills/tdq-build/references/rules/chung.md`, `docs/tdq/token-budget.json`
