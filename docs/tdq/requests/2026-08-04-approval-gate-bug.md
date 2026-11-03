# REQUEST — 2026-08-04-approval-gate-bug

## Nguyên văn yêu cầu
> hiện tại có khi claude trình bày plan/spec và yêu cầu duyệt tôi góp ý hoặc bổ
> sung chứ chưa duyệt thì có tình trạng claude tự động next turn sau khi bổ sung.
> tôi muốn detect issue và xử lí để không bị như này nữa

## Cách hiểu đầu tiên
- **Hiện tượng:** Sau khi Claude trình bày spec/plan và in dòng "➤ Duyệt: ... ·
  Góp ý: ...", nếu user trả lời bằng góp ý/bổ sung (KHÔNG phải câu duyệt tường
  minh như "duyệt spec"/"duyệt plan mode ..."), Claude đôi khi tự động coi đó là
  đã duyệt và tiến sang bước/skill kế tiếp (spec→plan, hoặc plan→build) thay vì
  sửa xong rồi trình lại và tiếp tục CHỜ.
- **Mục tiêu user muốn:** (1) phát hiện được các lần vi phạm gate này (kể cả
  đã xảy ra trong lịch sử hay tương lai), (2) có cơ chế XỬ LÝ để việc này không
  tái diễn — tức là cần một biện pháp chặn/ngăn ngừa cứng hơn là chỉ dựa vào
  Claude tự đọc luật trong skill mỗi lần.
- **Phạm vi đoán (cần xác nhận ở bước interview):**
  - Đây là vấn đề về hành vi của Claude khi thực thi skill `tdq-spec`/`tdq-plan`
    (đọc sai/áp sai luật approval.md), hay là vấn đề thiếu cơ chế kỹ thuật
    (hook/guard) để CHẶN CỨNG việc chuyển phase khi chưa có `spec_approved`/
    `plan_approved = true` trong `state.json`?
  - "Detect issue" nghĩa là: rà lại lịch sử hội thoại/state để tìm các lần đã
    xảy ra? Hay là dựng cơ chế phát hiện tự động (hook) cho các lần sau?
  - Phạm vi sửa: chỉ áp dụng cho gate spec/plan, hay cả gate "duyệt quick" và
    các điểm dừng khác (T4.4 hỏi commit, v.v.)?
- **Chưa rõ, cần hỏi:** đã liệt kê ở trên — cần vòng interview trước khi chốt
  hướng kỹ thuật (sửa skill vs. thêm hook chặn cứng vs. cả hai).

## Ghi chú vận hành
- Có request khác đang mở (`2026-08-04-export-claude-setup`, phase `report`,
  còn treo đúng 1 việc: hỏi user có commit `claude-export/` không — user chưa
  trả lời). Việc mở request mới này sẽ xoá state hiện tại của request đó (file
  tài liệu/report/plan đã ghi thì KHÔNG mất, chỉ mất tracking `phase` trong
  `state.json`). Đã hỏi user trước khi init — xem hội thoại.
