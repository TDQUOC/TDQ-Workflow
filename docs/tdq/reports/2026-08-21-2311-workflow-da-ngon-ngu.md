# REPORT — Rà quốc tế hoá cổng duyệt/góp ý (`2026-08-21-2311-workflow-da-ngon-ngu` · lane full · mode main · 14/14 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** dựng mốc suite + 12 mã kiểm K1–K12 đăng ký TRƯỚC khi đọc code · chấm 12 mã bằng bằng chứng `file:dòng` · chạy lượt phản chứng thử bác từng phán quyết · lập bảng 9 điểm khoá cứng · viết 8 đề xuất sửa, mỗi đề xuất kèm dòng tương thích ngược.
**Kết quả:** 12/12 mã có phán quyết + phản chứng · **8 mã CHƯA, 3 mã ĐẠT, 1 mã là số đo** · lượt phản chứng đổi phán quyết **2/12** mã (K4 hẹp lại còn "chữ cái trần, 1/4 cổng"; K10 từ "17 file / 26 lần" xuống "chỉ ~1 file thật sự khoá hành vi").
**Phát hiện chính:** cơ chế user muốn **đã có sẵn** — regex `LETTER` ở `hooks/scripts/prompt_context.py:50` — nhưng chỉ đấu vào cổng `mode`; ba cổng `spec`/`plan`/`quick` chết ở `:65 if not AGREE...: return False`. Vì `bash_gate.py:75` đọc lại cờ `matched` chứ không tự nhận diện, **sửa đúng một hàm là cả hai cổng cùng đổi**.
**Kiểm:** `pytest tests/ -q` → 37 failed · 1166 passed · 1369 subtests (bằng đúng mốc, 37 lỗi đều ở `tests/test_skill_router.py` và có từ trước request) · `doc_lint --pair` và `doc_lint <audit>` exit 0 · QC PASS 8/8 mục DoD + 4 mục cố định, không vòng fix.
**Đầu ra:** `docs/tdq/audit/da-ngon-ngu.md` (mốc · bảng tổng 12 mã · 12 khối bằng chứng · điểm khoá cứng · 8 đề xuất · kiểm cuối).
**Giới hạn:** request này là **rà soát, không sửa** (yêu cầu `2b` của user) — chưa dòng code nào đổi, 8 đề xuất Đ1–Đ8 cần một request implement riêng, làm theo thứ tự Đ1→Đ3 (regex) → Đ4→Đ5 (khuôn in) → Đ6→Đ7 (luật ngôn ngữ) → Đ8 (eval). Chưa đo hành vi model thật với câu tiếng Anh, vì lưới eval đa ngôn ngữ chính là thứ Đ8 đề xuất tạo.
**Git:** chưa commit gì; không có commit gỡ chặn nào.

## Thời gian

| Phase | Treo tường | Model chạy | Số lần vào |
|---|---|---|---|
| idle | 5 giây | 0 giây | 1 |
| analyze | 6 phút | 5 phút | 1 |
| spec | 2 phút | 2 phút | 1 |
| plan | 3 phút | 3 phút | 1 |
| implement | 13 phút | 13 phút | 1 |
| qc | 32 giây | 11 giây | 1 |
| report | 7 giây | 6 giây | 1 |
| **Tổng** | **26 phút** | **25 phút** | |
