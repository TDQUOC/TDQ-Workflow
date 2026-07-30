# Khuôn report

`docs/tdq/reports/<slug>.md` — tiếng Việt, **≤ 50 dòng tổng cộng**. Kiểm bằng
`wc -l docs/tdq/reports/<slug>.md`.

```markdown
# REPORT — <tên việc>

Ngày: YYYY-MM-DD · Spec: ../spec/<slug>.md · Plan: ../plan/<slug>.md · QC: ../qc/<slug>.md

## Đã làm gì
- <3–6 gạch đầu dòng, mỗi dòng một kết quả cụ thể>

## Đầu ra
| Đầu ra | Đường dẫn |
|---|---|

## Cách chạy / cách kiểm
```
<lệnh cụ thể>
```

## Kết quả QC
<PASS bao nhiêu hạng mục, vòng thứ mấy, link file qc>

## Quyết định đáng chú ý
- <quyết định> — vì <lý do>

## Giới hạn còn lại
- <cái gì chưa làm, vì sao, ảnh hưởng gì>

## Đề xuất tiếp theo
- <nếu có>
```

## Kiểm trước khi trình

- ≤ 50 dòng (đo bằng `wc -l`).
- Mọi con số trong report đều lấy từ output thật, không ước lượng.
- Mục "giới hạn còn lại" nói thật những gì chưa xong — không giấu.
- Kết thúc bằng câu hỏi user có muốn commit không (hỏi trong chat, không viết trong file).
