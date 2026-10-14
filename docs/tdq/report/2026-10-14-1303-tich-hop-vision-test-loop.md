# REPORT — Tích hợp khung mindset kiểm thử thực tế và vòng lặp Vision Test Loop vào TDQ Workflow (`2026-10-14-1303-tich-hop-vision-test-loop` · lane full · mode subagent · 7 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P1 xây dựng `scripts/tdq_vision_diff.py` & `tests/test_tdq_vision_diff.py` (chuẩn hóa kích thước bằng Canvas Padding không méo tỷ lệ, loại trừ vùng động `--ignore-boxes`, gom cụm BFS vẽ Bounding Box đỏ `[1]`, `[2]` lên `diff_highlight.png`, xuất `metrics.json`, render bộ đôi báo cáo `<slug>.md` và `<slug>.html` tương tác với Split Slider / Onion-Skin / Blink 2Hz / Bounding Box Explorer / Multi-round Timeline, hỗ trợ đường dẫn tương đối mặc định + `--embed-base64`, hỗ trợ `--figma-url` trả exit code `3` khi thiếu `FIGMA_TOKEN`) · P2 xây dựng file Skill Rule Reference chi tiết `skills/tdq-build/references/vision-test-loop.md` cho cả model tier thấp (Bảng quyết định kích hoạt cho mockup/wireframe/screenshot/prototype/Figma, công thức kịch bản 3 tầng `Given - When - Then`, 6 Anti-Patterns `ANTI-1`..`ANTI-6` kèm ví dụ `WRONG vs RIGHT`, 6 bước Vision Test Loop copy-pasteable, bảng ánh xạ hộp đỏ `[1]`, `[2]` sang CSS, trần 3 vòng auto-fix + dừng sớm `< 0.2%`, Reviewer Sub-agent trần 1 lượt, kịch bản Human-in-the-loop và `Self-check`) · P3–P4 liên kết tầng 1 trong `skills/`, khóa `docs/tdq/token-budget.json` và kiểm chứng Log Service (`TDQ_LOG=0`) + `i18n_check.py`.
**Kết quả:** Thời gian xử lý ảnh 1920x1080 trên `tdq_vision_diff.py` đạt `0.224s` (vòng 1) và `0.266s` (vòng 2, dưới xa ngưỡng 2.0s) · Ngân sách token `skills/tdq-build/references/vision-test-loop.md` = `2059 tokens` (≤ 3500 tokens/file) · Unit test riêng `test_tdq_vision_diff.py` + `test_vision_test_loop_doc.py`: `0 → 16 bài test PASS (0.488s)`.
**Kiểm:** `python scripts/tdq_test.py vung-cham` → `Ran 876 tests in 124.760s OK (skipped=7)` · `doc_lint.py skills` → `0 violation(s) total, exit 0` · `token_budget.py --kiem` → `exit 0` · `i18n_check.py` → `0 Vietnamese line(s) in 4 file(s)` · QC mức `ultra`: PASS 6/6 mục DoD + `tdq-qc-tester` độc lập báo `VERDICT: PASS everything` (đã sửa 2 task `QC1.1`–`QC1.2` để giữ nguyên số dòng các điểm neo `L###` trong `test_luat_skill.py`).
**Đầu ra:** `scripts/tdq_vision_diff.py`, `skills/tdq-build/references/vision-test-loop.md`, `tests/test_tdq_vision_diff.py`, `tests/test_vision_test_loop_doc.py`, `skills/tdq-build/SKILL.md`, `skills/tdq-spec/SKILL.md`, `skills/tdq-build/references/qc.md`, `skills/tdq-build/references/rules/chung.md`, `skills/tdq-build/references/rules/html.md`, `skills/tdq-spec/references/spec-template.md`, `docs/tdq/token-budget.json` · Backup: không có.
**Giới hạn:** Không tích hợp visual diff vào GitHub Actions / GitLab CI hay Pixel-to-DOM mapping tự động (đã loại ở ngoài phạm vi §1 theo chốt của người dùng).
**Lệch spec chờ duyệt:** không có
**Git:** Đã tạo các commit mở khóa worktree `6f20ef8`, `03b7dd2`, `ba9f4b8`, `794188e`, `14d7071` trên nhánh request `feature/tich-hop-vision-test-loop`; chưa commit phần hoàn thiện QC/docs cuối cùng và chưa gộp vào `main`.

## Thời gian

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 7s | — | 1 |
| analyze | 9 min | — | 1 |
| spec | 15 min | — | 1 |
| plan | 5 min | — | 1 |
| implement | 35 min | — | 1 |
| qc | 19 min | — | 1 |
| report | 9s | — | 1 |
| **Total** | **1h 23min** | **—** | |
