# REQUEST — Sample Socket.IO chat để test mode external (codex + agy)

Ngày: 2026-07-30 23:14 · Slug: 2026-07-30-sample-socketio-chat-external

## Nguyên văn yêu cầu

> hãy lập một sample ví dụ như code một serevr socket io simple + chat web để test
> codex và agy để make sure claude có thể trigger và khởi chạy 2 code agent đó

## Cách hiểu đầu tiên

- Mục tiêu: dùng một bài toán thật (server Socket.IO đơn giản + trang chat web) làm
  sample để chạy mode external THẬT — lần này qua đúng đường **agent runner**
  (`codex-runner`, `agy-runner`) chứ không gọi script tay như E2E trước.
- Điều cần chứng minh: Claude trigger được 2 agent đó (Agent tool), agent tự chạy
  `external_task.py run` nền + poll, engine code trong worktree, verify + fallback đúng.
- Phạm vi đoán: 1 server Node (socket.io) + 1 trang web chat tĩnh + test/validate;
  chia ≥2 task để mỗi engine nhận ≥1 task.
- Chỗ chưa rõ / ràng buộc biết trước:
  - 2 agent runner mới tạo CHƯA nạp vào phiên này → cần `/reload-plugins` (user gõ)
    trước khi test trigger, hoặc chấp nhận test ở phiên sau.
  - Giới hạn đã đo: agy 1.1.8 headless không sửa được file → task giao agy dự kiến
    rơi vào fallback (đó cũng là một phần cần demo).
  - Node/npm có sẵn trên máy chưa — cần kiểm.
