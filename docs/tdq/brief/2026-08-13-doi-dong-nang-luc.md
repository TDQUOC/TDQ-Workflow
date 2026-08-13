# Brief — Đổi dòng "Năng lực" thành "ước tính sẽ dùng skill"

## Nguyên văn
User (kèm ảnh chụp output chế độ nhanh của một project khác dùng tdq-workflow — dự án
game Unity, đoạn tóm tắt plan có dòng "Năng lực: không có"): "đổi chỗ nnawg lực là : ước
tính sẽ dùng skill: cho thân thiện người dùng mở request cho cái này".

Cách hiểu đầu tiên: đổi nhãn dòng "Năng lực: <skill>/không có" trong tóm tắt chế độ nhanh
(Phần C bước 3 của `tdq-intake/SKILL.md`) thành cách gọi khác — "ước tính sẽ dùng skill:"
— cho thân thiện/dễ hiểu hơn với người dùng khi mở request.

Phạm vi đoán: chỉ đổi CÂU CHỮ nhãn (label), không đổi logic chọn skill hay giá trị hiển
thị (vẫn liệt kê skill sẽ dùng hoặc "không có").

Chỗ chưa rõ:
1. Chỉ đổi ở chế độ nhanh (Phần C bước 3, dòng duy nhất hiện có) hay còn chỗ tương tự ở
   chế độ chuyên sâu (spec §3b "Năng lực & công cụ" là bảng, không phải 1 dòng — có đổi
   nhãn cột/tiêu đề bảng đó không)?
2. Từ "ước tính" có đúng ý không, hay user muốn một cách diễn đạt khác (vd bỏ hẳn chữ
   "ước tính", chỉ ghi "Sẽ dùng skill: ...")?
3. Ảnh đính kèm là output của PROJECT KHÁC (game Unity) — không phải file trong repo
   TDQWorkflow này. Xác nhận: đây là yêu cầu sửa TEMPLATE/SKILL dùng chung của
   tdq-workflow (áp dụng cho mọi project cài plugin), không phải sửa riêng gì trong repo
   TDQWorkflow?

## Hiểu & kiến thức

## Hỏi đáp
