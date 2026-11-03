# REPORT — hướng A hybrid: luật lý luận tiếng Anh, khuôn user-facing tiếng Việt (`2026-08-19-1616-huong-a-dich-hybrid` · lane full · mode main · 19 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P1 thêm rule R12 vào `doc_lint.py` — gate ngôn ngữ đầu ra, chỉ áp cho `docs/tdq` và
`docs/workinglog` · P2 phân loại 329 mã luật thành 38 `user-facing` / 291 `ly-luan`
(`docs/tdq/audit/ranh-gioi-luat.md`, script `scripts/luat_phan_loai.py`), thêm cột `neo bản mới`
vào bảng điểm neo để lưới khoá theo dõi được câu tiếng Anh · P3 viết lại 6 skill `tdq-*` cùng
toàn bộ `references/` theo thể lai · P4 đo token, sinh lại hai bản portable, chạy full suite.
**Kết quả:** token 44 file `skills/**.md` 100.189 → 68.843 (**-31,3%**) · trần lane full
92.470 → 62.989 (**-31,9%**) · khối "luôn nạp" 4.600 → 2.798 (-39,2%) · 329/329 điểm neo còn
hiệu lực, 38 mã user-facing vẫn nguyên tiếng Việt.
**Kiểm:** `tests/test_luat_skill.py` 11 pass/329 subtest · `test_doc_lint.py` 64 pass ·
`test_ranh_gioi.py` 15 pass · `test_build_portable.py` 41 pass/17 subtest · full suite
1057 pass, 1241 subtest, 25 fail đều là lỗi có sẵn của `test_skill_router.py::KhoTest` ·
`doc_lint.py skills docs/tdq docs/workinglog` 546 file, 0 vi phạm · QC PASS 13/13, 0 vòng fix.
**Đầu ra:** `docs/tdq/audit/do-hybrid.md` (số từng file) · `docs/tdq/audit/ranh-gioi-luat.md`
(bảng nhãn 329 mã) · `docs/tdq/qc/2026-08-19-1616-huong-a-dich-hybrid.md`.
**Giới hạn:** 25 test đỏ của `test_skill_router.py::KhoTest` là lỗi CÓ SẴN (skill `figma-*` của
plugin ngoài không mở được) — chạy trên cây `HEAD` ra đúng 25 fail, không thuộc phạm vi request
này · ba nợ nội dung phát hiện khi dịch nhưng cố ý KHÔNG sửa vì ngoài phạm vi: `bang-lech.md`
còn trỏ đường dẫn cũ `portable/AGENTS.md`, `tdq-check-status/references/report-template.md` còn
ghi "D1–D11" trong khi bảng đã có D12, và vài đoạn trùng nội dung giữa các file reference ·
`phases.md` + `user-facing-block.md` giữ 0% vì gần như chỉ chứa câu nói với user.
**Git:** chưa commit gì cho request này — không có commit gỡ chặn nào.

## Thời gian

| Phase | Treo tường | Model chạy | Số lần vào |
|---|---|---|---|
| idle | 0 giây | 0 giây | 1 |
| analyze | 9 phút | 8 phút | 1 |
| spec | 4 phút | 4 phút | 1 |
| plan | 4 phút | 4 phút | 1 |
| implement | 1 giờ 55 phút | 1 giờ 38 phút | 1 |
| qc | 4 phút | 4 phút | 1 |
| report | 0 giây | 0 giây | 1 |
| **Tổng** | **2 giờ 15 phút** | **1 giờ 58 phút** | |
