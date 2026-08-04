# Research — 2026-08-04-workflow-linh-hoat

## A. Đọc code (nội bộ)

| Nơi | Điều rút ra |
|---|---|
| `skills/tdq-spec/SKILL.md:9,21-24,48` | Có luật cứng "Không bao giờ viết spec và plan trong cùng một turn"; bước 2 gọi agent `tdq-reviewer`; kết skill yêu cầu sang tdq-plan ở **turn mới**. |
| `skills/tdq-plan/SKILL.md:9,13-23,39-43` | Bước 1 HỎI mode thực thi TRƯỚC khi viết plan (một lượt hỏi riêng); bước 3 gọi `tdq-reviewer`; luật "Không viết cùng turn với spec". |
| `skills/tdq-build/SKILL.md:8-9` | Build đã chạy end-to-end implement→qc→report trong 1 turn; không có rào turn giữa plan và implement ngoài văn bản skill. |
| `skills/tdq-intake/SKILL.md:88-96` (Phần C) | Lane quick: "Chỉ interview khi thật sự chưa rõ", không có bước research/web search, không tạo `research/`, `questions/`. |
| `skills/tdq-intake/references/interview.md:21-31` | Cách hỏi hiện tại: 2–4 phương án, "(Đề xuất)" đứng đầu, dùng AskUserQuestion nếu có. Chưa có luật "câu cuối hỏi bổ sung". |
| `scripts/tdq_state.py:412-534` (`PHASE_TABLE`) | Nguồn sự thật duy nhất của phase; `spec.forbidden` chứa "Viết plan trong cùng turn với spec"; `plan.checklist[0]` = hỏi mode riêng. `phases.md` tự sinh từ đây (`phases-doc`). |
| `hooks/scripts/prompt_context.py:72-116` | `pending` tính theo prompt của user: quick / spec / plan. Vì mỗi lần duyệt vẫn là một prompt riêng, việc gộp spec→plan và plan→build **không** phá hook này. |
| `hooks/scripts/bash_gate.py:44,55-93` | `NEXT_PHASE_TARGET = {"plan": "spec", "implement": "plan"}`: chạy `set phase=plan` trong cùng turn với `approve spec` vẫn hợp lệ vì signal `spec` có `matched=True`. Gộp turn KHÔNG kích chặn. |
| `hooks/scripts/stop_gate.py:136-157` | Chỉ chặn khi repo đổi mà working log chưa append. Gộp turn không ảnh hưởng. |
| `scripts/doc_lint.py:21-32` | Trần dòng: intake 120, spec 100, plan 100, build 150, conventions 120 — thêm nội dung phải nằm trong trần hoặc chuyển sang `references/`. |
| `tests/test_skill_shape.py:32`, `tests/test_portable_sync.py:16-20` | Test khoá `tdq-reviewer.md` phải có `tools:` chỉ-đọc (⇒ giữ file agent thì test vẫn xanh); `portable/workflow/0{1..4}-*.md` phải khớp từng bước với skill tương ứng ⇒ mọi thay đổi bước phải sync portable. |

## B. Research ngoài (tavily-primary, 2026-08-04)

**Truy vấn 1:** "Claude Code subagent frontmatter model field reasoning effort thinking configuration"

- Nguồn: https://code.claude.com/docs/en/sub-agents (bảng "supported frontmatter fields", fetch trực tiếp).
  - `model` — `sonnet` | `opus` | `haiku` | `fable` | model ID đầy đủ (vd `claude-opus-5`) | `inherit`. **Mặc định `inherit`.**
  - `effort` — "Effort level when this subagent is active. Overrides the session effort level. Default: inherits from session. Options: `low`, `medium`, `high`, `xhigh`, `max`; available levels depend on the model."
  - Với **plugin subagent**, các trường bị bỏ qua là `permissionMode`, `mcpServers`, `hooks` — `model` và `effort` KHÔNG nằm trong danh sách bỏ qua ⇒ agent của plugin tdq-workflow dùng được cả hai.
- Nguồn: https://code.claude.com/docs/en/model-config — "Skill and subagent frontmatter: set `effort` in a skill or subagent markdown file to override the effort level when that skill or subagent runs". Thứ tự ưu tiên: env var > frontmatter (khi skill/subagent active) > mức của phiên > mặc định model.

**Truy vấn 2:** giới hạn per-invocation (cùng lượt search)

- https://github.com/anthropics/claude-code/issues/25669 và /issues/43083: **Agent tool KHÔNG có tham số `effort`** (chỉ `model`, `prompt`, `subagent_type`, …); đây đang là feature request mở. Khớp với schema Agent tool thấy trong phiên này (`model`, `isolation`, `run_in_background`, `subagent_type`, `prompt`, `description` — không có `effort`).

**Điều rút ra (quyết định thiết kế):**
1. Chỉnh **model** thì làm được cả hai chiều: mặc định tĩnh trong frontmatter + override động qua tham số `model` của Agent tool mỗi lần gọi.
2. Chỉnh **thinking/effort** hiện chỉ làm được **tĩnh trong frontmatter** từng agent. Muốn "động" thì phải tách agent thành nhiều biến thể (vd `tdq-implementer` effort=high vs `tdq-implementer-lite` effort=low) — đổi lại là tăng số file agent.
3. Đặt `effort` trong frontmatter đè lên mức effort của phiên ⇒ đặt sai sẽ khiến agent nặng chạy nông hơn mong đợi ngay cả khi user đang để phiên ở mức cao.
