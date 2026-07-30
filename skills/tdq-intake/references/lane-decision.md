# Chọn lane: quick hay full

Bạn **đề xuất**, user **quyết**. Luôn hỏi, kể cả khi thấy quá rõ.

## Bảng quyết

| Dấu hiệu | quick | full |
|---|---|---|
| Thời lượng ước tính | < ~1 giờ | > ~1 giờ |
| Số file đụng tới | 1–3 | nhiều, hoặc chưa biết |
| Yêu cầu đã rõ chưa | rõ, không phải hỏi gì | còn chỗ mơ hồ / cần research |
| Rủi ro nếu sai | thấp, dễ hoàn tác | cao: dữ liệu, bảo mật, API công khai, tiền |
| Có thiết kế mới không | không, chỉ sửa/thêm nhỏ | có kiến trúc/luồng mới |
| Cần model/hạ tầng mới | không | có |

Có **bất kỳ** ô nào rơi vào cột full → đề xuất **full**.

## Luồng mỗi lane

- **quick**: phân tích ngắn → mini-plan ≤10 dòng trong chat → user duyệt → ghi working
  log → implement → validate → báo cáo ngắn.
- **full**: phân tích + interview → spec (chờ duyệt) → plan (chờ duyệt) → implement →
  QC → report.

## Khuôn câu hỏi (copy được)

```
Tóm tắt: <2–3 dòng việc user muốn>
Đề xuất: lane <quick|full> — <lý do gắn với chính việc này>
Bạn muốn chạy lane nào: quick hay full?
```

Đang giữa chừng mà thấy chọn sai lane? Nói rõ vì sao, đề xuất đổi, **hỏi user** rồi mới
chạy lại `init` với lane mới.
