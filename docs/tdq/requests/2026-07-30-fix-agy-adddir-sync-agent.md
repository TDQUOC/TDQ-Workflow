# REQUEST — Fix agy không tạo file (--add-dir) + Claude tự bắt kết quả agent

Ngày: 2026-07-30 23:40 · Slug: 2026-07-30-fix-agy-adddir-sync-agent

## Nguyên văn yêu cầu

> okay hiện tại có 2 vấn đề, nãy giờ dã trigger dc agy nhưng agy ko tạo đc gì cả,
> tôi cần biết lí do va phương án xử lí, và vấn ddeef thứ 2 là khi agent code xong,
> claude ko tự bắt mà phải chừo tôi hỏi, tôi muốn cllaude tự bắt và tiếp tục task
> hoặc report thay vì phải chờ tôi hỏi nhắc

## Chẩn đoán (có bằng chứng)

1. **agy KHÔNG hỏng — ghi nhầm chỗ.** Log `~/.gemini/antigravity-cli/cli.log` +
   thư mục scratch chứng minh: headless mode dùng workspace "CLI Project" tại
   `~/.gemini/antigravity-cli/scratch/` làm gốc, bỏ qua cwd. Mọi file "biến mất"
   (E2E-AGY, S2, probe) đều nằm ĐỦ trong scratch: `scratch/sample-chat/public/index.html`,
   `scratch/scripts/samples/e2e_agy.py`… Kết luận trước đó ("agy không thực thi tool")
   là SAI — tool chạy, path sai gốc.
   **Fix đã probe PASS**: thêm `--add-dir <worktree>` → agy ghi đúng thư mục đích.
   Phụ: global config ~/.gemini inject workflow riêng của user (scratch có
   `docs/superpowers/workinglog/…`) — prompt gói task cần giữ câu "bỏ qua workflow đã
   cấu hình".
2. **Claude không tự bắt kết quả agent**: chuỗi notification (wrapper xong → runner
   dậy → main Claude được báo) ĐÃ chạy đúng 2 nhịp đầu, nhưng user restart Claude
   giữa chừng → notification đang chờ của phiên cũ mất theo phiên. Fix: orchestrator
   gọi Agent ĐỒNG BỘ (`run_in_background: false`) — turn build giữ nguyên và tự tiếp
   tục ngay khi runner xong, không phụ thuộc notification xuyên turn/phiên.

## Phạm vi dự kiến

`scripts/external_task.py` (+tests) · `agents/{codex,agy}-runner.md` ·
`skills/tdq-plan|tdq-build/SKILL.md` + portable · knowledge/qc external-agent-mode
(đính chính) · retest S2 thật bằng agy.
