# REPORT — phân tích ý tưởng sơ đồ giải thuật trước khi code (`2026-08-23-1125-diagram-giai-thuat-mind-map` · lane full · mode main · 12 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P1 chốt lược đồ dữ liệu 14 trường + ví dụ login bốn lớp · P2 trả lời sáu câu, kèm mục phản biện ba điểm yếu và bảng đối chiếu năm công cụ · P3 hai file mẫu JSON và HTML tự chứa · P4 lint, QC, ghi mem0.
**Kết quả:** báo cáo 246 dòng (trần 250) · 6/6 mục đánh số · 3 điểm yếu tự nêu · 0 tham chiếu ngoài trong HTML.
**Kiểm:** `doc_lint.py` trên báo cáo + spec + plan + QC → 0 vi phạm, exit 0 · `tdq_lsp.py kiem` → 6/6 bậc ĐẠT · QC 13/13 PASS, không defect, không vòng sửa.
**Đầu ra:** `docs/tdq/knowledge/2026-08-23-diagram-truoc-khi-code.md` · `docs/tdq/mind-map/vi-du-login.json` · `docs/tdq/mind-map/vi-du-login.html` · `docs/tdq/qc/2026-08-23-1125-diagram-giai-thuat-mind-map.md`
**Kết luận chính:** nên thêm bước sơ đồ, nhưng KHÔNG thêm phase mới — lớp giải thuật vào `§2c` của spec, lớp function flow gắn vào dòng `Chạm:` sẵn có của plan, cây tổng sinh sau build bằng một script stdlib duy nhất.
**Giới hạn:** request này dừng ở báo cáo, chưa build `scripts/tdq_mindmap.py` và chưa sửa skill nào · file HTML chưa được nhìn tận mắt trong trình duyệt vì tab Chrome không mở được `file://`, chỉ kiểm tĩnh (parse sạch, 0 tài nguyên ngoài) · điểm yếu 3 trong báo cáo nói rõ: chưa có số đo cho chính loại sơ đồ nghiệp vụ viết tay này.
**Git:** chưa commit.

## Thời gian

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 0s | 0s | 1 |
| analyze | 13 min | 13 min | 1 |
| spec | 6 min | 2 min | 1 |
| plan | 12 min | 7 min | 1 |
| implement | 13 min | 12 min | 1 |
| report | 1s | 0s | 1 |
| **Total** | **44 min** | **39 min** | |
