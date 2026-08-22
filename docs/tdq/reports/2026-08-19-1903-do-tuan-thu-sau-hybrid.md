# REPORT — Đo độ tuân thủ luật sau khi chuyển bộ skill sang lai (`2026-08-19-1903-do-tuan-thu-sau-hybrid` · lane full · mode main · 17 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P1 chốt thiết kế thống kê TRƯỚC khi chạy (đơn vị = cặp `(ca, mã luật)`, 3 lần/nhánh, kiểm định dấu chính xác một phía, ngưỡng 0,05) · P2 bộ chấm tất định 17 mã luật + 10 ca thật, mỗi phép kiểm có cặp mẫu ĐẠT/VI PHẠM · P3 chạy 60 phiên agent thật trong hộp cát riêng, xen kẽ hai nhánh · P4 file audit sinh thẳng từ bản ghi + lưới hồi quy chạy lại bằng một lệnh · P5 log service tắt được qua `TDQ_EVAL_LOG`.
**Kết quả:** bộ mã đăng ký trước — 28 phép kiểm, 4 nghiêng xấu · 3 nghiêng tốt · 21 hoà → **p = 0,5000, CHƯA ĐỦ BẰNG CHỨNG** rằng bộ lai tuân thủ kém hơn · không mã nào sụt cứng · bộ đầy đủ 51 phép kiểm (thêm 4 mã chọn sau khi thấy số, chỉ để tham khảo) p = 0,6047 · chi phí 37,82 USD/60 phiên (dự trù 105–120, trần 70) · 0 phiên lỗi, 0 lần chạy lại.
**Kiểm:** `pytest tests/test_tdq_eval.py -q` 109 passed / 139 subtests, 0 skip · full suite 1167 passed, 25 failed đều ở `test_skill_router.py` (đã dựng worktree HEAD xác nhận đỏ sẵn, không do việc này) · `doc_lint` 0 vi phạm · QC 12/13 PASS, Q4 FAIL.
**Đầu ra:** `docs/tdq/audit/do-tuan-thu.md` (bảng số, cặp lệch, hai giá trị p, độ nhạy) · `scripts/tdq_eval.py` · `evals/tuan-thu/` (lưới hồi quy 10 ca, ở lại repo) · `docs/tdq/bench/tuan-thu/` (60 bản ghi) · `docs/tdq/qc/2026-08-19-1903-do-tuan-thu-sau-hybrid.md`.
**Giới hạn:** Q4 trượt vế "mỗi ca ≥ 3 mã" ở đúng ca `duyet-spec-mo-ho` (2 mã) — turn đúng luật của ca đó là DỪNG và hỏi, không ghi gì, nên không mã nào khác áp được; user chốt dừng đo nên để nguyên, ai chạy lại lưới sau này cần biết · 51 phép kiểm chỉ đủ độ nhạy thấy sụt LỚN, chênh vài điểm phần trăm nằm trong nhiễu · "chưa đủ bằng chứng" KHÔNG đồng nghĩa hai bộ ngang nhau · 6 lỗi của chính bộ đo (F1–F7) đều phát hiện nhờ chấm lại transcript đã lưu, không tốn thêm phiên nào.
**Git:** chưa commit — không có commit gỡ chặn nào trong request này.

## Thời gian

| Phase | Treo tường | Model chạy | Số lần vào |
|---|---|---|---|
| idle | 0 giây | 0 giây | 1 |
| analyze | 16 phút | 16 phút | 1 |
| spec | 1 giờ 25 phút | 6 phút | 1 |
| plan | 3 giờ 02 phút | 3 phút | 1 |
| implement | 2 giờ 19 phút | 1 giờ 24 phút | 1 |
| qc | 44 giờ 58 phút | 6 phút | 1 |
| report | 0 giây | 0 giây | 1 |
| **Tổng** | **52 giờ 02 phút** | **1 giờ 55 phút** | |
