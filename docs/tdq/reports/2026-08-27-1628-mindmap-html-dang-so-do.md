# REPORT — mind-map HTML trình bày dạng sơ đồ luồng (`2026-08-27-1628-mindmap-html-dang-so-do` · lane full · mode main · 15/15 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P1 `build_flow_model` gom `B<n>`/`B<n>!` thành cặp quyết định · P2 `wrap_label` + `layout_flow` cho hộp tự cao theo chữ, không chồng lấn · P3 bộ helper SVG dùng chung + `render_flow_svg`, sơ đồ đứng TRƯỚC `<ol class="steps">` trong khối cuộn ngang · P4 trang tổng có cây nhánh SVG (ô feature bọc `<a href>`, ô thiếu file nét đứt + mờ) và lưới phụ thuộc chuyển sang helper chung · P5 log service + test.
**Kết quả:** trang feature: chỉ có danh sách bước phẳng → có sơ đồ hộp/hình thoi/mũi tên phía trên · trang tổng: chỉ danh sách link lồng nhau → có sơ đồ cây 17 node / 13 cạnh, danh sách link cũ giữ nguyên bên dưới · nhãn lưới phụ thuộc: cắt cụt `label[:34]` → giữ đủ từng ký tự · 8 file HTML render lại, exit 0.
**Kiểm:** `pytest tests/test_mindmap_render.py -q` 88 pass · toàn repo `61 failed, 1642 passed, 1494 subtests` — đúng bằng con số trước khi sửa, đối chứng bằng `git stash` (lỗi có sẵn ở doc-lint, `test_bench.py`, skill-inventory, không liên quan) · i18n_check 0 dòng, không `TODO`/`FIXME` · QC PASS 13/13 hạng mục DoD + 4 hạng mục cố định, không vòng fix nào.
**Đầu ra:** `scripts/mindmap_render.py` · `tests/test_mindmap_render.py` · 8 file trong `docs/tdq/mind-map/` · `docs/tdq/qc/2026-08-27-1628-mindmap-html-dang-so-do.md`
**Giới hạn:**
- Plan viết "5 file sơ đồ thật" nhưng thư mục có **7** — test đổi thành `>= 5` và duyệt hết cả 7, không bỏ file nào.
- Tiêu chí P1 "kết quả không chứa chuỗi `<`" không thoả được vì mô tả thật có `B<n>`; thay bằng kiểm danh sách tiền tố thẻ SVG cố định + khẳng định `desc` còn nguyên văn.
- Q12 ghi lệnh `python3 scripts/i18n_check.py` không tham số, chạy vậy script exit 2 (usage); đã chạy `python3 scripts/i18n_check.py scripts/mindmap_render.py` → exit 0.
- Ngắt dòng chữ vẫn là ước lượng theo số ký tự (SVG tĩnh không đo được bề rộng font thật); hệ số `FLOW_CHAR_W = 7.2` cố ý rộng để lệch thì hộp cao thêm chứ không cắt chữ.
- Sửa `scripts/mindmap_render.py` làm 3 bản portable lệch; đã chạy `python3 scripts/build_portable.py` (exit 0) cho khớp lại.
**Git:** chưa commit gì — không gặp chặn kỹ thuật nào nên không có commit tự phát.

## Thời gian

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 0s | 0s | 1 |
| analyze | 3h 29min | 4 min | 1 |
| spec | 14 min | 2 min | 1 |
| diagram | 5 min | 5 min | 1 |
| plan | 8 min | 7 min | 1 |
| implement | 21 min | 21 min | 1 |
| qc | 8 min | 8 min | 1 |
| report | 7s | 7s | 1 |
| **Total** | **4h 24min** | **48 min** | |
