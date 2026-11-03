# REPORT — Cổng hỏi bằng chat, Next step nêu pha kế, đường kẻ cuối lượt (`2026-09-03-1220-gate-chat-va-next-pha` · lane full · mode main · 18/18 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P1 — luật cấm tool hỏi dạng popup chuyển lên tầng `tdq-conventions`, áp cho MỌI câu
hỏi chứ không riêng 7 cổng, cộng luật kết lượt ở `approval.md` và thành phần 6 (đường kẻ `---`
cuối lượt) ở `user-facing-block.md` · P2 — viết lại đủ 12 dòng `Next step:` trong 8 skill, mỗi
dòng nêu tên pha kế hoặc nói rõ pha không đổi kèm skill kế · P3 — `tests/test_luat_gate_chat.py`,
7 test khoá ba luật đó · P4 — dựng lại 3 bản portable.

**Kết quả:** luật cấm popup có mặt ở 1 file (`tdq-intake/references/interview.md`, phủ đúng 1
trong 7 cổng) → có mặt ở tầng mọi skill đều nạp, phủ mọi câu hỏi · dòng `Next step:` nêu được
pha kế: 0/12 → 12/12 · test khoá ba luật: 0 → 7.

**Kiểm:** `pytest -q` 100 failed / 1471 passed, đúng mốc đỏ 100 có sẵn từ trước ·
`doc_lint.py skills/` exit 0 · QC PASS 15/15 hạng mục (11 dòng DoD + QC-F1→F4), không defect nào
phải mở vòng fix · 3 bundle portable CLEAN 92 / 142 / 85 file.

**Đầu ra:** `docs/tdq/qc/2026-09-03-1220-gate-chat-va-next-pha.md` ·
`tests/test_luat_gate_chat.py` · `skills/tdq-conventions/{SKILL.md, references/user-facing-block.md,
references/approval.md}` · 12 dòng `Next step:` trong 8 skill. Không sửa file nào ngoài repo.

**Giới hạn:**
- Pha `diagram` bị bỏ khỏi lộ trình vì repo này không có: `PHASE_TABLE` không khai, `skills/`
  không có `tdq-diagram`. Bản skill mà host nạp thì có nhắc — đó là bản plugin khác. Theo repo.
- `doc_lint.py docs/` vẫn exit 1 vì 25 phát hiện trong `docs/archive/v0.1/`, và
  `test_luat_skill.py` vẫn đỏ 1 test (lệch neo 84/329 của `luat-hien-co.md`). Cả hai có sẵn
  trước việc này (kiểm bằng `git stash` và `git status`), dọn chúng nằm ngoài phạm vi spec.
- `tests/test_user_facing_block.py` phải sửa 3 chỗ vì nó khoá bản luật CŨ đúng ở hai câu mà yêu
  cầu này thay. Mỗi chỗ sửa có ghi chú ngày + lý do; luật 7 vẫn bắt được mọi thứ khác lọt xuống
  dưới khối, chỉ bóc đúng một dòng `---`.
- Lớp `Next step:` là DỰ PHÒNG theo đúng điều kiện user chốt: hook `[TDQ:NEXT]` vẫn là đường
  chính, dòng này chỉ gánh trên host không có hook (Gemini CLI, GitHub Copilot CLI, Aider).

**Git:** chưa commit gì. Nhánh `tdq-doi-ten-mode-implement` còn ôm cả phần
`skills/tdq-lsp-setup/references/lumen.md` làm từ lượt trước.

## Thời gian

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 0s | 0s | 1 |
| analyze | 10 min | 4 min | 1 |
| spec | 8 min | 7 min | 1 |
| plan | 20 min | 5 min | 1 |
| implement | 16 min | 16 min | 1 |
| qc | 2 min | 2 min | 1 |
| **Total** | **56 min** | **35 min** | |
