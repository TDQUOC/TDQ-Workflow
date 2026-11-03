# REPORT — Rà soát tối ưu workflow sau đợt chuyển tiếng Anh (`2026-08-22-1231-ra-soat-toi-uu-workflow` · lane full · mode main · 19/19 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P1 viết `scripts/doc_dup.py` + 21 unit test (dò đoạn trùng, đếm token bằng bộ đếm thật) · P2 đo bốn mặt context cost, trùng lặp, runtime, chất lượng bản dịch · P3 bảng top 10 đề xuất kèm token tiết kiệm và phép kiểm · P4 kiểm log, test, i18n, doc_lint, không đụng file workflow.
**Kết quả:** phát hiện chặn — runtime nạp plugin 0.19.0 (2026-08-15) trong khi repo đã 0.28.0, thiếu 5 file skill và `tdq-build/SKILL.md` cache vẫn tiếng Việt, nên đợt chuyển tiếng Anh CHƯA hề chạy thật · trần một request lane full 59.486 token, top 10 đề xuất cắt được 5.098 token = 8,6% · trùng lặp 8 khối/472 token ở ngưỡng 3 dòng, 59 khối/1.378 token ở ngưỡng 2 dòng · runtime 1,04 tool call mỗi turn, tức luật gom tool call gần như không được áp · 11/22 dòng luật cứng nằm giữa file, vùng research nói mất 30–50% tuân thủ.
**Kiểm:** `pytest tests/test_doc_dup.py -q` 21 passed · full suite 37 đỏ đúng mốc nền, toàn bộ trong `tests/test_skill_router.py` · `i18n_check.py` ba kind trên `scripts hooks skills agents` ra 0 · `doc_lint.py` trên spec, plan, audit, qc đều thoát 0 · QC độc lập (agent `tdq-qc-tester`) 12/12 PASS sau một vòng fix — vòng 1 FAIL Q6 với 12 lỗi số liệu, đã sửa hết, tổng bảng đổi 4.962 → 5.098.
**Đầu ra:** `docs/tdq/audit/2026-08-22-toi-uu-workflow.md` · `scripts/doc_dup.py` · `tests/test_doc_dup.py` · `docs/tdq/qc/2026-08-22-1231-ra-soat-toi-uu-workflow.md`. Backup: không sửa gì ngoài repo.
**Giới hạn:** hồ sơ chỉ ĐỀ XUẤT, chưa áp một đề xuất nào — user chốt phạm vi như vậy · token tiết kiệm của 6 trên 10 dòng là ước lượng từ đo mẫu, chỉ dòng 1, 4, 8 là số đếm thật trên toàn bộ dòng bị đụng · số ba tầng nạp (1.452 / 10.785 / 50.064) lấy từ `context_surface.py` vốn ước lượng 4 byte một token, hồ sơ ghi rõ chỗ nào ước lượng chỗ nào đếm thật · chưa gỡ bản plugin cũ 0.19.0, việc đó nằm ngoài phạm vi vì phải cài lại plugin.
**Git:** chưa commit gì. Có xoá 9 file `.DS_Store` do Finder sinh ra để test `test_no_ds_store` về đúng mốc nền — các file này nằm trong `.gitignore`, không phải file của repo.

## Thời gian

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 0s | 0s | 1 |
| analyze | 12 min | 12 min | 1 |
| spec | 1 min | 17s | 1 |
| plan | 4 min | 4 min | 1 |
| implement | 24 min | 24 min | 1 |
| qc | 16 min | 5 min | 1 |
| report | 8s | 7s | 1 |
| **Total** | **58 min** | **46 min** | |
