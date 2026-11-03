# Brief: Kiểm thử cross-platform macOS và Linux cho TDQ Workflow v0.73.0

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> "tôi có một máy macos 100.105.75.71 user tdq pass 1772 và máy linux ở 100.102.92.43 user admin pass 1 hoặc tdq pass 1 hãy thử ssh vào và update plugin và test xem có hoạt động ổn trên cross plaftform không?"

### Đọc hiểu ban đầu:
- **Mục tiêu**: SSH vào hai môi trường máy chủ từ xa (macOS `100.105.75.71` và Linux `100.102.92.43`), thực hiện cập nhật plugin TDQ-Workflow lên phiên bản mới nhất v0.73.0 và kiểm thử cross-platform toàn diện (tests, hooks, commands, lsp/setup).
- **Phạm vi dự kiến**:
  1. Kiểm tra kết nối SSH tới macOS (`tdq@100.105.75.71`) và Linux (`admin@100.102.92.43` hoặc `tdq@100.102.92.43`).
  2. Xác định vị trí cài đặt plugin TDQ-Workflow trên macOS và Linux (thường trong `~/.claude/plugins/` hoặc repo git clone).
  3. Cập nhật mã nguồn/plugin lên v0.73.0 (git pull / claude plugin update).
  4. Chạy smoke test và unit tests (`tdq_setup.py`, pytest) trên từng nền tảng để thẩm định tính tương thích đa nền tảng (POSIX, bash hooks, permissions).
  5. Báo cáo kết quả kiểm thử chi tiết.
- **Điểm chưa rõ**: Cần xác nhận phương thức cập nhật trên hai máy (git repo clone cục bộ hay qua lệnh `/plugin update` của Claude CLI).

## Hiểu & kiến thức

(Sẽ điền sau khi chốt lane và phỏng vấn nếu chọn deep pipeline)

## Hỏi đáp

(Sẽ điền trong quá trình trao đổi)
