# BRIEF — cho lane nhanh có pha analyze

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> Vậy nếu tôi muốn là lane quick cũng có pha analysis thì sao?

Đọc lần đầu:

- Mục tiêu: lane nhanh có bước phân tích rõ ràng như lane chuyên sâu, thay vì gộp chìm vào
  bước 1 của 9 bước hiện tại.
- Phạm vi đoán: `scripts/tdq_state.py` (bảng pha, cổng), `skills/tdq-intake/SKILL.md` +
  `references/quick-lane.md`, hook `prompt_context`/`stop_gate`, `skills/tdq-conventions/
  references/phases.md`, bộ test.
- Chỗ chưa rõ (quyết định luôn hình dạng việc):
  1. Muốn một pha `analyze` THẬT trong state (đặt được `phase=analyze` khi lane quick,
     có cổng chặn sang bước sau) hay chỉ muốn phân tích thành bước có tên, có sản phẩm
     ghi ra file, nhưng vẫn nằm trong pha `quick`?
  2. Phân tích của lane nhanh có đẻ file `brief/<slug>.md` riêng không, hay vẫn gộp vào
     mini spec/plan một file như hiện nay?
  3. Có thêm cổng dừng chờ user sau phân tích không? Thêm là lane nhanh mất tính "một cổng
     duyệt duy nhất".

## Hiểu & kiến thức

(chờ pha analyze)

## Hỏi đáp

(chờ pha analyze)
