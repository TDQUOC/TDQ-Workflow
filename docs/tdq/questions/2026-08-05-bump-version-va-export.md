# QUESTIONS — Bump version + export đầy đủ hơn

## Vòng 1 (2026-08-05 03:2x) — đã hỏi, chờ trả lời

### Q1 — Bump lên mức nào?

Hiện `0.6.2` (2026-08-02). Sau đó có 5 commit tính năng chưa có entry CHANGELOG:
`f344377` workflow linh hoạt gộp gate · `1175980` audit token vòng 1 · `b41225f` tối ưu
token vòng 2 · (`465cf14` fix approval-gate, `5c8bf44` bộ export nằm trước 0.6.2? — không,
sau) → đề xuất **0.7.0** (minor, có tính năng mới + đổi luật report ≤10 dòng).

Đáp:

### Q2 — "Đầy đủ hơn" tới mức nào?

- (a) Chỉ vá 8 lỗi đã đo rồi sinh lại bundle bằng tay theo 7 bước cũ.
- (b) (a) + `scripts/claude_export.py build` — 1 lệnh sinh bundle, có test.
- (c) (b) + `claude_export.py check` đo drift bundle ↔ nguồn (chính câu hỏi "dirty bao nhiêu").

Đề xuất **(c)**.

Đáp:

### Q3 — Bundle mới đặt ở đâu, bundle/zip cũ xử lý sao?

Ghi đè `~/Documents/claude-code-export` hay tạo thư mục mới? `claude-code-export.zip`
(2,2 MB, 2026-08-04 16:07) xoá, giữ, hay sinh lại?

Đáp:

### Q4 — Repo copy: giữ `.git` không?

Hiện rsync loại `.git` → máy đích KHÔNG phải git repo → worktree lane external, hook
post-commit, `git status` trong build đều gãy. Đổi sang `git clone` thì bundle chỉ còn
**6,0 MB / 382 file tracked** thay vì 17 MB, lại có đủ history.

Đáp:

### Q5 — Memory `.remember/` có đưa vào bundle không?

Đang copy cả `~/.claude/.remember` lẫn `.remember/` trong repo — chứa nội dung công việc
thật (today-*.md, recent.md, core-memories.md). Giữ nguyên, lọc bớt, hay bỏ?

Đáp:
