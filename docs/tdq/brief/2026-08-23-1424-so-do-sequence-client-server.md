# BRIEF — sơ đồ dạng sequence, đóng khung client và server

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> có thể update lại mindmap sample theo các bước giải thuật như này nhưng mà ở sequence
> diagrame và có đóng khung cái nào ở client cái nào ở server không ? tôi cảm giác vậy sẽ dễ
> theo dõi và trực quan hơn, nhưng vaxn có thể xem script module

### Đọc lần đầu

**Mục tiêu.** Giữ nguyên nội dung giải thuật của sơ đồ v2, nhưng đổi cách TRÌNH BÀY sang dạng
sequence diagram, có đóng khung phân biệt phần chạy ở client và phần chạy ở server, mà vẫn đọc
được cặp `file::hàm` của từng bước.

**Phạm vi đoán.** Ba chỗ trong bản thiết kế v2 phải sửa lại:

1. Khuôn file sơ đồ ở mục 2 — cần thêm cách khai một bước thuộc tầng nào.
2. File mẫu `docs/tdq/mind-map/vi-du-login.md` — viết lại theo khuôn mới.
3. Lệnh `xem` ở mục 1 — đầu ra đổi từ danh sách bước sang sequence diagram có khung.

**Chỗ chưa rõ.** Điểm đánh đổi lớn nhất: viết tay thẳng bằng cú pháp mermaid `sequenceDiagram`
thì trực quan sẵn nhưng khó viết và khó cho máy đối chiếu; còn giữ khuôn một dòng một bước rồi
thêm một nhãn tầng, để `xem` dựng ra sequence diagram, thì dễ viết và máy vẫn tra được.

## Hiểu & kiến thức

Chưa viết — điền ở phase `analyze` nếu user chọn lane deep.

## Hỏi đáp

Chưa có — vòng phỏng vấn chạy ở phase `analyze`.
