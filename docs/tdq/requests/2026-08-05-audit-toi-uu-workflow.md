# Request: audit toàn bộ workflow — tối ưu token/time

## Nguyên văn yêu cầu

> tôi muốn bạn phân tích và làm 1 round deep resreach toàn bộ workflow và instruction xem
> đã tối ưu đẻ save token/ time chưa? có issue gì có thể xảy ra và có hướng nào optimize
> không? nếu có hãy làm một bản report đề xuất cho tôi

## Cách hiểu ban đầu

- Đây là **vòng 3** của chuỗi tối ưu token/time (sau vòng 1
  `2026-08-04-toi-uu-token-workflow` — đo carry-cost + 19 đề xuất + P0; vòng 2
  `2026-08-05-toi-uu-token-vong-2` — spec/plan/implement, đã ✓ 21 task, giảm CLAUDE.md
  −73,6%, tokopt tổng hợp).
- Khác vòng trước: lần này phạm vi là **toàn bộ workflow và instruction** (không chỉ số
  đo carry-cost), tìm issue tiềm ẩn (không chỉ token — cả rủi ro vận hành/logic), và
  dừng lại ở **report đề xuất** — không yêu cầu spec/plan/implement ngay (khác vòng 2 nơi
  user nói rõ "lên spec/plan"). Nếu report tìm ra việc đáng làm, sẽ hỏi user có mở
  request mới để spec/plan hay không.
- Phạm vi đoán: rà toàn bộ skill `tdq-*` (SKILL.md + references), script
  `scripts/*.py`, hook (`settings.json`/prompt_context), CLAUDE.md (project +
  `~/.claude/CLAUDE.md`), và có thể đối chiếu dữ liệu carry-cost đã đo ở vòng 1/2 xem còn
  gì chưa fix.

## Chỗ chưa rõ

- Cần đo lại carry-cost bằng `token_audit.py` (dữ liệu mới nhất) hay chỉ đọc code/luật
  tĩnh?
- "Issue có thể xảy ra" — chỉ token/time, hay gồm cả đúng-sai logic/an toàn (vd:
  race-condition trong tdq_state.py, lint rule sai)?
- Output report: file trong `docs/tdq/` hay chỉ cần trả lời trong chat?
