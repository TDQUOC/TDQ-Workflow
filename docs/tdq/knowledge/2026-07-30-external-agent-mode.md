# KNOWLEDGE — external-agent-mode

Ngày: 2026-07-30 · Trạng thái: analyze ĐÓNG (2 vòng interview, 8 câu) → phase spec

## Năng lực dùng được (B0 — bảng phán quyết)

Nguồn: `skill_inventory.py` (31 skill trên đĩa) + built-in trong context.

| Skill | Phán quyết | Lý do |
|---|---|---|
| plugin-dev:agent-development | DÙNG | viết 2 custom agent codex-runner/agy-runner đúng khuôn |
| plugin-dev:skill-development | DÙNG | sửa skill tdq-plan/tdq-build thêm mode external |
| plugin-dev:hook-development | DÙNG | nếu phải nới hooks gate (prompt_context/edit_gate nhận mode mới) |
| claude-md-management:claude-md-improver | DÙNG | audit CLAUDE.md §10 sau khi thêm mode |
| tdq-* (6 skill) | NỀN | chính là workflow đang chạy |
| tavily-* (cả 8, gồm tavily-cli) + tavily-best-practices | NỀN | research (đã dùng) |
| graphify | NỀN | cập nhật graph cuối turn |
| plugin-dev:plugin-structure, command-development, mcp-integration, plugin-settings | KHÔNG | không tạo plugin/command/MCP mới — mở rộng plugin sẵn có |
| skill-creator, remember, frontend-design, playground, writing-hookify-rules, mcp-server-dev (3), tavily-cli | KHÔNG | ngoài phạm vi (nén) |

## Sự thật đã xác minh trên máy

- `codex-cli 0.146.0-alpha.3.1`, login ChatGPT OK · `agy 1.1.8`, login OK, 11 model slug.
- Chọn model: CÓ ở cả hai — codex `-m <model>` (+ `--oss` local, effort qua config);
  agy `--model <slug> --effort low|medium|high` (slug đã gồm mức effort với flash).
- Headless + JSON schema output: CÓ ở cả hai (codex `--output-schema`, agy `--json-schema`).
- Sandbox: codex có 3 mức thật (read-only/workspace-write/danger-full-access);
  agy KHÔNG có sandbox FS — chỉ có permission rules hoặc `--dangerously-skip-permissions`.
- tdq-workflow hiện tại: `VALID_MODES = ("main", "subagent")` trong `scripts/tdq_state.py:29`;
  mode nhắc trong `hooks/scripts/prompt_context.py:28`, `edit_gate.py:69`, `_common.py:24`;
  skill `tdq-plan` (hỏi mode), `tdq-build` (rẽ nhánh theo mode), agent `tdq-implementer`
  (khuôn worktree + report cấu trúc — mẫu tốt cho external).

## Quyết định đã chốt (8, từ questions cùng slug)

1. **Kiến trúc**: 2 custom subagent `codex-runner`/`agy-runner` (trong plugin
   tdq-workflow) — nhận gói task, gọi `codex exec` / `agy -p` headless qua Bash,
   validate JSON schema, retry, trả kết quả cấu trúc. Plugin codex-plugin-cc vẫn cài
   cho user dùng tay.
2. **Model**: hỏi mỗi lần duyệt plan. Claude fetch list model available THẬT trên máy
   (agy: `agy models`; codex: probe slug ứng viên bằng lệnh exec tí hon, cache) →
   trình list → user trả 1–3 tên: 1=default · 2=[khó, dễ] · 3=[khó, TB, dễ]; Claude
   phân độ khó từng task và phân bổ.
3. **Auto engine** (khi user nói auto): code/refactor/test → codex; research/docs/UI
   → agy; hòa → codex. Ghi cứng tiêu chí trong skill.
4. **Quyền**: FULL ACCESS cả hai (user chốt, đã cảnh báo): codex
   `--sandbox danger-full-access`, agy `--dangerously-skip-permissions`. Giảm thiểu:
   cwd = worktree, Claude diff-check trước merge (QC).
5. **Tier plugin codex**: luôn bật (không vào on_demand §11).
6. **Lane**: external dùng được ở CẢ quick lẫn full.
7. **Granularity**: giao TỪNG TASK đơn (1 lần gọi CLI = 1 task, mục tiêu đơn, kể tên
   file, schema report cứng, 1 ví dụ mẫu) — cốt lõi thiết kế cho model cấp thấp/
   context ngắn; worktree dùng chung cho cả phase.
8. **Fallback**: mỗi task retry ≤ 2 (kèm feedback lỗi), vẫn hỏng → Claude tự
   implement task đó trong worktree, ghi chú report. Không dừng giữa turn.

## Phương án đã loại

- Codex qua plugin /codex:rescue cho mode external (2 đường không đồng nhất) — C1b.
- MCP server (chậm, thêm tầng) — C1c.
- Model cố định / auto theo cỡ task (user muốn tự cấp list mỗi plan) — C2a,b.
- Auto engine theo quota (khó đo) — C3b.
- Agy read-only xuất patch (chậm; user chấp nhận rủi ro full access) — C4b.

## Kiểm cổng

- Phạm vi cuối: RÕ — (1) user cài plugin codex (slash command, Claude hướng dẫn);
  (2) 2 agent runner + helper script probe/list model + khuôn gói task & report;
  (3) `external` vào VALID_MODES + hooks nhắc mode + tdq-plan/tdq-build/tdq-intake
  (quick) + tdq-conventions; (4) CLAUDE.md §10 cập nhật; (5) log service cho runner.
- Model/download: KHÔNG cài mới (codex 0.146.0 + agy 1.1.8 đã sẵn, đã login).
- QC/test: unit (state mode external, hooks regex, helper script), lint/--pair,
  E2E chạy tay 1 task thật qua codex + 1 qua agy (bằng chứng vào qc/), diff-check.

## Nguồn

Xem `../research/2026-07-30-external-agent-mode.md` (7 truy vấn + đo máy).

## Đính chính 23:45 (sau chẩn đoán sâu, có bằng chứng)

Kết luận cũ "agy 1.1.8 headless không thực thi tool sửa file" là **SAI**. Sự thật:
headless mode dùng workspace "CLI Project" tại `~/.gemini/antigravity-cli/scratch/`
làm gốc, bỏ qua cwd — mọi file E2E-AGY/S2/probe đều được agy tạo ĐỦ trong scratch
(bằng chứng: `scratch/sample-chat/public/index.html`, `scratch/scripts/samples/e2e_agy.py`,
cli.log ghi tool-call thật). Fix đã probe PASS: thêm `--add-dir <worktree>` (path tuyệt
đối) vào lệnh agy — wrapper `external_task.py` đã cập nhật. Ghi chú phụ: global config
`~/.gemini` inject workflow riêng của user vào agy; gói task giữ câu "bỏ qua workflow
đã cấu hình" khi cần ép model chỉ làm task.
