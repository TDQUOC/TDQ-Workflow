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

- **quick**: phân tích (+ search/interview khi cần) → mini-spec/plan gộp 1 file, tóm tắt
  ≤10 dòng trong chat → user duyệt (1 gate) → ghi working log → implement → validate →
  báo cáo ngắn. Chi tiết: [quick-lane.md](quick-lane.md).
- **full**: phân tích + interview → spec (chờ duyệt, duyệt xong viết plan ngay cùng
  turn) → plan (chờ duyệt kèm mode, duyệt xong build ngay cùng turn) → implement →
  QC → report.

## Khuôn câu hỏi (copy được)

Đúng khuôn [interview.md](interview.md) — option mỗi dòng riêng, phương án đề xuất
luôn ở `A`:

```
Tóm tắt: <2–3 dòng việc user muốn>
1. Bạn muốn chạy lane nào?
- A (đề xuất): quick — <lý do gắn với chính việc này>
- B: full — <lý do gắn với chính việc này>
```

Đang giữa chừng mà thấy chọn sai lane? Nói rõ vì sao, đề xuất đổi, **hỏi user** rồi mới
chạy lại `init` với lane mới.
