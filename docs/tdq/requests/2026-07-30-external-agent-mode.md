# REQUEST — Mode giao việc cho agent ngoài (codex/antigravity) trong TDQ workflow

Ngày: 2026-07-30 21:47 · Trạng thái: chờ user chọn lane

## Nguyên văn yêu cầu

> okay tôi muốn cài plugin codex và antigravity để + viết 2 custom subagent
> codex-runner/agy-runner gắn vào TDQ workflow như một mode giao việc, bổ sung
> thêm là sẽ bổ sung thêm một mode ở chế độ implement là 3th subagent implement
> bên cạnh main và sub agent, và ở 3th subagent implement thì sẽ tạo worktree và
> asign task cho codex/antigravity (sẽ hỏi người dùng muốn chọn cái nào hay để
> claude tự động chọn) nhưng tôi muốn bạn phân tích xem liệu có thể chọn model
> nào được không? và hãy phân tích để tổ chức chi tiết đến mức một model cấp
> thấp (ví dụ model local, context legnth thấp cũng có thể hoạot động đúng và
> ổn định)

## Cách hiểu đầu tiên

Mục tiêu:
1. Cài plugin chính chủ `codex-plugin-cc` (marketplace openai-codex) cho Codex;
   Antigravity không có plugin → tích hợp qua CLI headless `agy -p`.
2. Viết 2 custom subagent cho Claude Code: `codex-runner` và `agy-runner` —
   wrap `codex exec` / `agy -p` (headless, JSON output, report ra file).
3. Mở rộng plugin tdq-workflow: mode implement thứ 3 **external** bên cạnh
   `main` và `subagent` — tạo worktree, assign task cho codex/agy; khi duyệt
   plan user chọn engine (codex | antigravity | auto để Claude tự chọn).
4. Phân tích: có chọn được model cho từng engine không (`codex -m …`,
   `agy --model/--effort` — nghiên cứu sơ bộ turn trước cho thấy CÓ).
5. Thiết kế instruction/task-format đủ chi tiết, rõ ràng, ít context để model
   cấp thấp (local, context ngắn) chạy đúng và ổn định.

Phạm vi đoán (chờ chốt ở analyze):
- Đụng: `~/.claude/settings.json` (plugin), `.claude/agents/` hoặc `agents/`
  của plugin tdq-workflow, skill `tdq-plan`/`tdq-build`, `scripts/tdq_state.py`
  (mode mới), hooks gate, CLAUDE.md §10, test.
- Task giao cho engine ngoài phải report kết quả thành file (luật §5 CLAUDE.md).

Chỗ chưa rõ (sẽ interview nếu lane full):
- Auth codex/agy trên máy đã sẵn chưa; phiên bản CLI.
- "Plugin antigravity": xác nhận không có plugin chính chủ → dùng subagent wrap.
- Mode external áp cho cả lane quick hay chỉ full.
- Chính sách chọn model mặc định cho từng engine; tiêu chí "auto".
- Mức sandbox/permission cho engine ngoài trong worktree.
