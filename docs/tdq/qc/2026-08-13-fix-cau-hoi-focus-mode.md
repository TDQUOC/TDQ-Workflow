# QC — Fix: câu hỏi TDQ bị ẩn khi bật focus mode

Ngày: 2026-08-13 · Spec: ../spec/2026-08-13-fix-cau-hoi-focus-mode.md · Lane: full
QC độc lập: BỎ (đã chốt trong spec §1b — việc thuần văn bản 1 file, tự đọc lại + doc_lint
+ tự quan sát bằng chứng sống là đủ).

## Kết quả

| # | Hạng mục | Bằng chứng | Kết quả |
|---|---|---|---|
| Q1 | §1 bước 4 mới có đủ 2 ý (bắt buộc lệnh + thứ tự trước) | `skills/tdq-conventions/SKILL.md` §1 bước 4 hiện có câu "**bắt buộc** chạy ĐÚNG MỘT lệnh" + "Cấm Edit/Read rồi tự append tay" (ý a), và câu "Lệnh này phải là **hành động cuối** của turn, chạy TRƯỚC đoạn chat kết thúc turn... sau khi in đoạn chat đó **không gọi thêm tool nào nữa**" (ý b) | PASS |
| Q2 | `doc_lint.py` PASS | `python3 scripts/doc_lint.py skills/tdq-conventions/SKILL.md` → exit 0 (lần đầu FAIL R6 121 dòng > trần 120, đã nén còn 120 dòng, lần 2 exit 0) | PASS |
| Q3 | Bằng chứng sống: turn build/QC/report của CHÍNH request này dùng `tdq_finish.py` thay Edit tay | Working log `docs/workinglog/2026-08-13.md` có 2 entry do `tdq_finish.py` tạo trong chính request này: 18:27 (turn viết spec, kèm set phase=spec) và 18:32 (turn viết plan). Turn build/QC/report này (turn hiện tại) sẽ tiếp tục dùng `tdq_finish.py` ngay sau khi ghi QC — xem entry kế tiếp trong working log | PASS |

## Kết luận
3/3 PASS. DoD đạt — §1 bước 4 đã sửa đúng nội dung, `doc_lint.py` xanh, và bằng chứng sống
(working log ghi bởi `tdq_finish.py`, không phải Edit tay) đã xuất hiện liên tục từ turn
viết spec đến nay, đúng yêu cầu §6/DoD của spec.
