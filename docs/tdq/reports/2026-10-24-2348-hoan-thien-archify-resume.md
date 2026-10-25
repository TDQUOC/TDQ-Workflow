# Bàn giao để tiếp tục request Archify

Ngày 2026-10-25. User chọn `1a 2a` và yêu cầu request cũ có thể continue, request mới chỉ đề xuất, chưa fix.

- Request cũ: 2026-10-24-2348-hoan-thien-archify, full, implement, paused; KHÔNG hoàn thành hoặc nghiệm thu.
- Nhánh: feature/hoan-thien-archify; nhánh gốc: feature/nghien-cuu-tich-hop-archify. Không commit/push/merge mới khi tách.
- Snapshot state đầy đủ: `docs/tdq/2026-10-24-2348-hoan-thien-archify.resume.json`. Xuất bằng `tdq_state.py get`, đã đối chiếu JSON bằng state gốc trước init; giữ descriptor/hash/thời điểm duyệt spec/plan và mode subagent.
- Plan/QC/report giữ nguyên các đường dẫn mang slug request cũ. T5.2 đang [~], Q8 chưa tick; QC2.1 đã [x].
- Suite cuối đã kết thúc, không còn chạy nền: 2974 tests, 9 failures, 1 error, 10 skipped. 10 lỗi còn lại được đối chứng baseline; không gọi toàn repo PASS.
- Giữ nguyên 6 worktree dirty dưới `.tdq-worktrees/2026-10-24-2348-hoan-thien-archify/` và các bản nguồn/test chưa commit trên working tree. Đổi nhánh cho tài liệu không phải đã commit hoặc đã hợp nhất chúng.

## Cách tiếp tục sau request phân tích

1. Kiểm tra git status, branch và đối soát các file dirty trước chuyển về nhánh Archify; không restore/clean cưỡng bức.
2. Lưu state của request phân tích trước khi thay active request. Khôi phục trạng thái Archify thông qua API `scripts/tdq_state.py` (load/save với kiểm concurrent update), không chép trực tiếp đè state.json; snapshot chỉ là đầu vào khôi phục, không cấp duyệt mới.
3. Kiểm lại digest spec/plan và evidence thực tế. Không tự ghi lời duyệt mới thay user; nếu nội dung thiết kế thay đổi thì cần duyệt lại.
4. Sau khi xác nhận snapshot và nhánh đúng, dùng `tdq_state.py resume`. Tiếp tục T5.2/Q8 và giải quyết gate worktree bảo toàn dữ liệu; không tick xong chỉ vì request phân tích đã hoàn tất.
5. Request phân tích chỉ đưa phương án 10 issue. Hoàn tất tài liệu không đồng nghĩa đã sửa lỗi nền; triển khai sửa phải được người dùng cho phép riêng.
