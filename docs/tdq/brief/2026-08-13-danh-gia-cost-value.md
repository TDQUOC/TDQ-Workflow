# BRIEF — Đánh giá cost/value từng thành phần tdq-workflow

Ngày: 2026-08-13 · Slug: 2026-08-13-danh-gia-cost-value

## Nguyên văn

> không tôi muốn check lại là nếu bộ này chạy trong thực tiễn, còn biết bộ portable của
> cái này được tạo ra để share và instal ở project level cho những máy khác, nên loại
> portable ra, ngoài ra khi phân tích điểm nghẽn không chỉ ở performance và context cost,
> mỗi cái phải phân tích rõ vai trò của nó tốn gì, đóng góp gì, có vai trò, giá trị thế
> nào, và phân tích lên bài toán là nó giá trị và cost đó có đáng không? do vẫn phải đảm
> bảo chất lượng cuối, nên nếu cần hãy phân tích lại và report lại

### Cách hiểu đầu tiên

Mục tiêu: làm lại phần PHÂN TÍCH của request `2026-08-13-ra-soat-toi-uu-llm` theo một
khung khác. Số đo cũ vẫn dùng lại được, cái phải làm lại là cách luận.

Ba điều chỉnh user yêu cầu:

1. **Loại `portable/` khỏi phạm vi.** Nó là bản đóng gói CỐ Ý để share và cài ở
   project level trên máy khác. Nên "trùng lặp với portable" không phải khuyết điểm,
   cũng không phải nợ bảo trì cần gỡ — báo cáo cũ xếp nó thành cơ hội #4 là sai khung.
2. **Đổi khung phân tích.** Không chỉ đo cost (mili-giây, token). Mỗi thành phần phải
   trả lời đủ: tốn gì · đóng góp gì · vai trò trong việc giữ chất lượng cuối · và kết
   luận cost đó có ĐÁNG không.
3. **Ràng buộc cứng: chất lượng cuối không được giảm.** Một thành phần đắt mà là thứ
   giữ chất lượng thì kết luận phải là GIỮ, không phải cắt.

Phạm vi đoán: 6 skill + references, 3 agent, 6 hook script, `docs/claude-md-mau.md`,
`scripts/` trên đường chạy mỗi turn. Đầu ra là một báo cáo mới, không sửa file sản phẩm.

Chỗ chưa rõ (đưa vào interview): đơn vị phân tích là gì (từng file hay từng cơ chế),
có cần đo thêm số mới hay dùng lại số cũ, và báo cáo mới thay thế hay bổ sung báo cáo cũ.

## Hiểu & kiến thức

(chờ phase analyze)

## Hỏi đáp

(chờ phase analyze)
