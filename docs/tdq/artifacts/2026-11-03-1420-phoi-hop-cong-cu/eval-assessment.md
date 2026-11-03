# Đánh giá response-only
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Phạm vi và nguồn

32 trial CLI Claude Code thật, model quan sát `cc4`, 8 ca × 2 biến thể × 2 lần, thứ tự AB/BA. Mỗi trial dùng workspace/home/config riêng và không được cấp tool thực thi. Tệp corpus, response và trace giữ nguyên; hash response `9f858264e31d74a26d63acb7f2a64818c356e55967f09457b4fe0a7fca73f993`.

Scorer độc lập chấm nội dung câu trả lời theo required/forbidden trong corpus khóa. Đây là nhận định model-grader, không oracle tự động được chứng nhận, không chứng minh thực thi browser/native hoặc tốc độ hoàn thành task thật.

| Biến thể | Ca đạt toàn rubric | Tiêu chí required đạt | Khuyến nghị hành động cấm |
|---|---:|---:|---:|
| A — baseline | 6/16 | 40/54 | 0/16 |
| B — candidate | 14/16 | 52/54 | 0/16 |

Candidate trượt cả hai lần uncertain-delivery: quan sát và dừng an toàn nhưng không nêu retry hữu hạn theo tiến triển. Đây không phải bằng chứng gửi trùng; không đổi rubric hay tuning theo holdout để tăng điểm.

## Giới hạn

- Cả 32 trial gốc giữ `outcome_availability=unavailable`; không chèn điểm review vào record để vượt gate.
- Các trial dùng nguồn candidate trước sửa rollback/ACL cuối, nên không chứng nhận byte nguồn sau đó.
- Nguồn đưa vào instruction gồm luật và mã setup/hook; phép đo không tách riêng tác động từng thành phần.
- Không xác định provider billing; thiếu chi phí ghi unavailable, không ghi $0.
- Hai vòng lặp là mẫu nhỏ; chưa kết luận tăng hiệu quả phổ quát hay đảm bảo tốc độ.

## Kết luận

Có tín hiệu cải thiện nội dung kế hoạch trên mẫu đã khóa, nhưng chứng nhận eval cuối vẫn INCONCLUSIVE. Lệch Q7 #1 đã ghi bằng CLI; không suy waiver từ duyệt plan hoặc duyệt sửa evaluator.
