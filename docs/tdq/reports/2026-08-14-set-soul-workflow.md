# REPORT — Set soul cho bộ workflow (`2026-08-14-set-soul-workflow` · lane full · mode main · 35 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** soul 3 tầng, skill nền + portable trỏ về · rà 28 file theo soul (biên bản 28
dòng, 2 chỗ SỬA đã sửa) · thư viện rule code (thư mục `rules/` 10 file, 7 ngôn ngữ + chỉ
mục) · scanner `scripts/code_rule_scan.py` 3 trạng thái, log timestamp tắt được `--im` ·
cổng clean code trong spec · đồng bộ khối QC-F hai bản qc.md · cơ chế M1–M5 chống nợ
kiến trúc (hồ sơ kiến trúc, ràng buộc spec, tìm-rồi-mới-tạo, dòng `Chạm:`, QC-F1→F3) ·
nghiệm thu bằng Haiku thật + một lượt QC độc lập.
**Kết quả:** suite 596 passed + 306 subtests (giữ mốc ≥574 của spec, thêm 12 test mới) ·
token 6 SKILL.md 26.664 → 27.462 ký tự — +200 token, đúng trần +200.
**Kiểm:** `pytest tests/ -q` → 596 passed · doc_lint exit 0 · QC vòng 1 PASS 20/20 + 3
hạng mục cố định (bằng chứng trong file QC) · QC độc lập (sonnet) PASS 18/18 hạng mục
kiểm được · Haiku nêu đúng 5/5 lỗi mẫu, không hỏi lại.
**Đầu ra:** skills/tdq-conventions/references/soul.md · skills/tdq-build/references/rules/ ·
scripts/code_rule_scan.py · docs/tdq/qc/2026-08-14-set-soul-workflow.md
**Giới hạn:** máy thiếu `ruff` nên 57 file Python chỉ đạt "CHƯA KIỂM ĐƯỢC" — lint tĩnh
thật chưa chạy tại chỗ, là nợ môi trường, cài ruff rồi chạy lại scanner là xong · biên
token chỉ còn dư 2 ký tự — lần sửa SKILL.md kế tiếp phải đo lại trước khi thêm chữ.
**Git:** chưa commit — build không cần commit gỡ chặn nào.
