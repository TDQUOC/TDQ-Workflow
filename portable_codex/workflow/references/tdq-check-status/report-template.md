# Khuôn báo cáo check-status — 6 mục cố định

`scripts/tdq_checkstatus.py report` in ra đúng khuôn này. File đây là bản người đọc:
dùng để kiểm output có đủ mục không, và để agent ngoài (không chạy được script Python)
tự điền tay theo đúng thứ tự.

Sáu mục, đúng thứ tự này, không thêm không bớt:

1. `## Request` — slug, lane, phase, mode, mốc mở và mốc ghi cuối.
2. `## Bằng chứng trên đĩa` — bảng: từng tài sản, tick plan, git, working log.
3. `## Ca lệch phát hiện` — bảng mã D1–D11, mức, chi tiết, chẩn đoán.
4. `## Kết luận` — đúng một trong ba chữ, in đậm.
5. `## Lệnh vá đề xuất` — khối bash, chỉ hai họ `set` và `approve`.
6. `## Việc kế tiếp` — đúng một câu.

## Ví dụ điền sẵn (ca thật: đổi máy giữa phase implement)

Từ đây tới hết mục là output THẬT của bộ dò, chép nguyên văn.

# Check status — request đang dở

## Request

- Slug: `2026-08-16-1110-skill-check-status`
- Lane: full · Phase: `implement`
- Mode thực thi: main
- Mở lúc: 2026-08-16T11:11:07+07:00 · Ghi lần cuối: 2026-08-16T11:35:38+07:00

## Bằng chứng trên đĩa

| Nguồn | Thấy gì |
|---|---|
| brief | có, 117 dòng (docs/tdq/brief/2026-08-16-1110-skill-check-status.md) |
| spec | có, 165 dòng (docs/tdq/spec/2026-08-16-1110-skill-check-status.md) |
| plan | có, 225 dòng (docs/tdq/plan/2026-08-16-1110-skill-check-status.md) |
| qc | không có (docs/tdq/qc/2026-08-16-1110-skill-check-status.md) |
| reports | không có (docs/tdq/reports/2026-08-16-1110-skill-check-status.md) |
| plan tick | 15/28 xong · đang làm: T4.1 |
| git | tdq-doi-ten-mode-implement · 20 commit gần đây · 8 file bẩn |
| working log | docs/workinglog/2026-08-16.md · nhắc slug |

## Ca lệch phát hiện

| Mã | Mức | Chi tiết | Chẩn đoán |
|---|---|---|---|
| D10 | canh-bao | thiếu started_at | Mất mốc thời gian — bảng thời gian của report sẽ sai nếu không vá. |

## Kết luận

**VÁ RỒI TIẾP TỤC**

## Lệnh vá đề xuất

Chạy sau khi user gật ĐÚNG MỘT lần. Chỉ hai họ `set` và `approve`; không có lệnh nào
xoá hay ghi đè dữ liệu cũ.

```bash
python3 scripts/tdq_state.py set started_at=ISO_MỐC_MỞ_REQUEST
```

## Việc kế tiếp

Làm tiếp đúng task T4.1 trong plan (task duy nhất mang `[~]`).

## Ba mức kết luận

| Kết luận | Khi nào | Làm gì |
|---|---|---|
| `TIẾP TỤC ĐƯỢC` | không ca nào quá mức `ok` | báo một dòng rồi làm tiếp |
| `VÁ RỒI TIẾP TỤC` | có `canh-bao`, mọi ca đó đều có lệnh vá | hỏi một câu, gật thì vá rồi đi tiếp |
| `CẦN USER QUYẾT` | có ca `chan`, hoặc có `canh-bao` không lệnh vá nào chữa được | dừng, trình lựa chọn cho user |
