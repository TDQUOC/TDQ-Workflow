# Research — 2026-08-03-skill-vao-goi-external

## Truy vấn 1 (turn trước, request check-skill-clone-worktree): cơ chế nạp hướng dẫn codex/agy
- Nguồn: verdent.ai/guides/codex-agents-md-explained · learn.chatgpt.com/docs/agent-configuration/agents-md · antigravity.google/docs/cli/best-practices · dev.to/arindam_1729 (Antigravity CLI hands-on)
- Rút ra: codex tự nạp chuỗi AGENTS.md (global `~/.codex/` + project-root→cwd, 1 file/thư mục, override trước). agy auto-parse `AGENTS.md`/`GEMINI.md` ở workspace root khi startup; có Agent Skills native: `.agents/skills/` (per-workspace) và `~/.gemini/antigravity-cli/skills/` (global). Wrapper ta chạy codex `--cd <worktree>`, agy `--add-dir <worktree>` → AGENTS.md đặt ở ROOT worktree là cả 2 engine tự thấy.

## Truy vấn 2: AGENTS.md best practices + model nhỏ
- Nguồn: philschmid.de/writing-good-agents · aihero.dev/a-complete-guide-to-agents-md · agents.md · news.ycombinator.com/item?id=47034087
- Rút ra: giữ NGẮN (đồng thuận <300 dòng; HumanLayer <60 dòng) — mọi dòng vào mọi prompt. Model nhỏ/không-thinking bám được ÍT lệnh hơn hẳn frontier (~150–200 với frontier, ít hơn nhiều với model nhỏ). Progressive disclosure: AGENTS.md chỉ trỏ tài liệu task-specific, không nhét hết. Kiểm tra deterministic (test/lint chặn) đáng tin hơn kỳ vọng model "tôn trọng" hướng dẫn.

## Truy vấn 3: instruction-following của model yếu
- Nguồn: kay-rottmann.de/en/blog/prompt-engineering-fundamentals · vector-labs.ai (LLM reliability) · thomas-wiegold.com (Levy/Jacoby/Goldberg 2024)
- Rút ra: lệnh phải mệnh lệnh, một việc, bounded; context dài làm GIẢM chất lượng (suy giảm từ ~3k token; sweet spot 150–300 từ). Prompt không phải chiến lược reliability — cần verification layer ngoài prompt (khớp verify 3 tầng đang có). → Với model cấp thấp: nhúng trích đoạn NGẮN đúng task vào gói > chép nguyên skill dài; luật phân nhánh phải máy-kiểm, không nhờ engine tự phán đoán.

## Hệ quả thiết kế
1. Nhánh nhúng: trích đoạn ngắn, mệnh lệnh, per-task, nằm trong gói (chắc nhất, hợp model thấp).
2. Nhánh AGENTS.md: chỉ quy ước xuyên task, trần dòng cứng (~≤60), sinh lúc chuẩn bị worktree, dọn trước diff-check/merge.
3. Nhánh MCP: nhận diện bằng máy (danh sách/luật cứng), loại task khỏi gói từ bước chia — không để engine "thử".
4. Mọi nhánh đều dựa verify tầng 2/3 + QC trường `Kiểm` làm lưới cuối, không tin lời hứa của engine.
