# BRIEF — Vì sao spec hay bị sửa sau khi đã duyệt

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> commit và mở request mới tôi muốn biết tại sao lại hay xảy ra vụ này
>
> (làm rõ ở vòng hỏi: "vụ này" = spec/plan bị sửa SAU khi user đã duyệt → sha256 lệch →
> phải xin duyệt lại giữa chừng)
>
> 1A 2A tôi cần phân tích để tạo report cho tôi chưa tự ý sửa gì

### Cách hiểu đầu tiên

Mục tiêu: tìm NGUYÊN NHÂN GỐC của việc spec đổi sau khi đã duyệt, tần suất thật, và
đề xuất cách chặn — nhưng **chỉ phân tích và viết report**, không sửa luật, không sửa
code trong request này.

Phạm vi user chốt: lane quick, đầu ra là một file report cho user đọc.

## Hiểu & kiến thức

Dấu vết sơ bộ (đọc lúc mở request, sẽ kiểm lại kỹ khi làm):
`grep -rc "duyệt lại|sha256 lệch" docs/workinglog/*.md` ra 9 ngày có dấu vết, tổng 11 lần
nhắc — tức không phải sự cố cá biệt của request hôm nay.

Cơ chế liên quan đã có trong repo: `scripts/tdq_state.py` lưu `spec_sha256` lúc duyệt;
hook nhắc `[TDQ:APPROVE]` khi băm hiện tại lệch băm đã duyệt.

Vòng scope: **BỎ** — user đã chốt cả mặt (nguyên nhân + tần suất), phạm vi (chỉ phân tích)
và đầu ra (report), không còn ẩn số làm đổi kết quả.

## Hỏi đáp

**Vòng làm rõ (2026-08-18)**

1. "Vụ này" là vụ nào: **1A** — spec/plan bị sửa sau khi duyệt, sha256 lệch, phải duyệt lại.
2. Pipeline: **2A** — chế độ nhanh.
3. Ràng buộc user nêu thêm: chỉ phân tích để tạo report, **chưa tự ý sửa gì**.
