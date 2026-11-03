# Checkpoint — Kiểm chứng và tăng tốc TDQ Workflow

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Cập nhật: 2026-10-27T22:20:26+07:00. Hoàn tất 15/24 task. Chưa chứng nhận DoD cuối hoặc phần trăm tăng tốc.

Full đầu tiên trước QC1: 3579 case, 3411 pass, 158 fail, 10 skip; harness 877.400 giây. Đủ 3306 case gốc + 273 mới. Source guard sạch, config guard FAIL. Sau sửa vẫn cần Full đạt.

## Kết quả module

| Task | Output | Gate |
|---|---|---|
| T1.2 | 75 passed, 67 subtests passed in 6.62s | Đạt gate module |
| T2.1 | 109 passed in 47.61s | Đạt gate module |
| T3.1 | 121 passed, 15 subtests passed in 110.60s (0:01:50) | Đạt gate module |
| T3.2 | 16 passed in 61.20s (0:01:01) | Đạt gate module |
| T4.1 | 12 passed in 3.93s | Đạt gate module |
| T4.2 | 252 passed, 1 skipped, 33 subtests passed in 170.82s (0:02:50) | Đạt gate module |
| QC-F1 | 3411 pass / 158 fail / 10 skip (case chuẩn hóa, trước QC1) | Chưa đạt gate |
| QC1.1 | 513 passed, 2 skipped, 215 subtests passed in 180.79s (0:03:00) | Chưa đạt gate |
| QC1.2 | 2 passed, 2 subtests passed in 14.76s | Đạt gate module |
| QC1.3 | 57 passed, 34 subtests passed in 62.99s (0:01:02) | Chưa đạt gate |
| QC1.4 | 22 passed, 329 subtests passed in 0.54s | Đạt gate module |

## Điểm chặn

.claude.json thay đổi trong một số khoảng test. Chưa xác định writer; guard toàn file được giữ nguyên. Cần môi trường ổn định để chứng nhận và chạy Full/benchmark cuối.

Chrome native từng lỗi startup/CDP; acceptance chạy native bằng Edge qua --archify-chrome đã thành công. Không đổi sandbox flags. Master kiến trúc vẫn là snapshot trước QC1, cần refresh sau source freeze.

## Còn phải làm

Full fresh; runtime từng kịch bản 120 giây; ba cặp Full A/B; ba bộ off/cold/warm mỗi cache và log thật; QC độc lập cuối; DoD và báo cáo nghiệm thu.

## Bản chi tiết

[Mở checkpoint HTML](checkpoint.html). Nội dung HTML có bảng trước/sau, đề xuất, ngưỡng, giới hạn, rollback và liên kết raw receipt.
