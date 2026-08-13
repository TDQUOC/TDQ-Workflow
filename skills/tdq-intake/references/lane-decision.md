# Chọn cỡ request: nhỏ, chế độ nhanh (express) hay chế độ chuyên sâu (deep)

Bạn **đề xuất**, user **quyết**. Luôn hỏi, kể cả khi thấy quá rõ.
Ngoại lệ duy nhất là tầng `nhỏ`: đủ 4 điều kiện ở [SKILL.md](../SKILL.md) thì làm luôn,
không mở request, không hỏi lane.

## Dòng tự nhận định

Mọi request mới tự đánh giá NỘI BỘ theo dạng dưới đây trước khi hỏi lane — đây là căn cứ
để chọn phương án đề xuất A/B, **không in ra chat**:

```
Cỡ: <nhỏ|quick|full> · Cần: <research | interview | subagent | QC độc lập | skill ngoài | không>
```

Cột `Cần` chỉ liệt kê thứ CÓ THỂ bỏ. Thứ luôn chạy thì không liệt kê, để đánh giá gọn.
Không có thứ nào tuỳ chọn thì coi như `Cần: không`.

## Bảng quyết

| Dấu hiệu | chế độ nhanh (express) | chế độ chuyên sâu (deep) |
|---|---|---|
| Thời lượng ước tính | < ~1 giờ | > ~1 giờ |
| Số file đụng tới | 1–3 | nhiều, hoặc chưa biết |
| Yêu cầu đã rõ chưa | rõ, không phải hỏi gì | còn chỗ mơ hồ / cần research |
| Rủi ro nếu sai | thấp, dễ hoàn tác | cao: dữ liệu, bảo mật, API công khai, tiền |
| Có thiết kế mới không | không, chỉ sửa/thêm nhỏ | có kiến trúc/luồng mới |
| Cần model/hạ tầng mới | không | có |

Có **bất kỳ** ô nào rơi vào cột chế độ chuyên sâu (deep) → đề xuất **chế độ chuyên sâu (deep)**.

## Luồng mỗi lane

- **chế độ nhanh (express)**: phân tích (+ search/interview khi cần) → mini-spec/plan gộp 1 file, tóm tắt
  ≤10 dòng trong chat → user duyệt (1 gate) → ghi working log → implement → validate →
  báo cáo ngắn. Chi tiết: [quick-lane.md](quick-lane.md).
- **chế độ chuyên sâu (deep)**: phân tích + interview → spec (chờ duyệt, duyệt xong viết plan ngay cùng
  turn) → plan (chờ duyệt kèm mode, duyệt xong build ngay cùng turn) → implement →
  QC → report.

## Khuôn câu hỏi (copy được)

Đúng khuôn [interview.md](interview.md) — option mỗi dòng riêng, phương án đề xuất
luôn ở `A`. Không in dòng `Cỡ:/Cần:`; gọi "lane" là "pipeline" khi hỏi user; ngay dưới 2
option luôn có khối giải thích ngắn nghĩa 2 pipeline (cố định, không đổi theo việc):

```
Tóm tắt: <2–3 dòng việc user muốn>
1. Bạn muốn chạy pipeline nào?
- A (đề xuất): chế độ nhanh (express) — <lý do gắn với chính việc này>
- B: chế độ chuyên sâu (deep) — <lý do gắn với chính việc này>

_chế độ nhanh (express): làm gọn, ít vòng hỏi, hợp việc nhỏ/đã rõ. chế độ chuyên sâu
(deep): phân tích + hỏi kỹ trước khi làm, hợp việc phức tạp hoặc rủi ro cao._

_Trả lời bằng chữ cái (vd: "A"), hoặc gõ thẳng câu tự nhiên khớp ý bạn chọn — cả hai
đều được hiểu như nhau._
```

Đang giữa chừng mà thấy chọn sai lane? Nói rõ vì sao, đề xuất đổi, **hỏi user** rồi mới
chạy lại `init` với lane mới.
