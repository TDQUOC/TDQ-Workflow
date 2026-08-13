# Kịch bản đo carry-cost before/after

Dùng khi cần so sánh mức tốn token của TDQ workflow trước/sau một đợt chuẩn hoá
(ví dụ: đợt tách skill P1-P4 của `2026-08-05-toi-uu-p0-p1-workflow`). Đo bằng
`scripts/token_audit.py` trên transcript thật — không ước lượng bằng mắt.

## Thao tác cố định (chạy y hệt cho cả 2 session before/after)

Dùng một project thử tách biệt (không phải repo chính) để không lẫn log:

1. Mở request quick mẫu: nhắn `"sửa 1 dòng comment trong file test.py"` (task nhỏ,
   không cần research/interview thật để giữ kịch bản lặp lại được).
2. Trả lời câu hỏi chế độ: chọn chế độ nhanh (express).
3. Duyệt mini-plan: nhắn `"duyệt nhanh"`.
4. Để Claude implement 1 task giả (sửa đúng 1 dòng comment), chạy validate.
5. Trả lời "không, đủ rồi" cho câu hỏi bổ sung cuối interview (nếu có).
6. Kết thúc session ngay sau khi báo cáo kết quả — không hỏi thêm gì khác.

Ghi lại session id (hoặc thời điểm bắt đầu/kết thúc) của mỗi lần chạy để tách
đúng transcript ra đo.

## Đo bằng `token_audit.py`

```bash
python3 scripts/token_audit.py --transcript-dir ~/.claude/projects/<project-slug> --sessions 1 --top 5
```

- `--transcript-dir` trỏ đúng thư mục chứa `*.jsonl` của project thử (đường dẫn
  gồm cả path project đã bị Claude Code chuyển thành slug gạch ngang).
- `--sessions 1` chỉ đo session vừa chạy kịch bản, tránh lẫn với session khác.
- `--top 5` in thêm 5 tool output đắt nhất — hữu ích khi cần biết phần nào tốn.

Chạy lệnh trên cho cả session **before** (chưa áp đợt chuẩn hoá) và session
**after** (đã áp), rồi so 2 output: tổng equiv-input token, tỷ lệ cache/baseline,
tỷ lệ bookkeeping — xem cột nào giảm và giảm bao nhiêu %.

## Ghi kết quả

Dán nguyên văn 2 bảng output (before/after) vào report hoặc QC, kèm % giảm tổng
equiv-input token — đây là bằng chứng carry-cost, không phải ước lượng.
