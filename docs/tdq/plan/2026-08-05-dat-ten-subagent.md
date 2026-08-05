# PLAN (quick) — 2026-08-05-dat-ten-subagent

## Phạm vi

**In:**
- Nâng luật đặt tên sub-agent (`<model>-<effort>-<việc-kebab>`, vd `sonnet-low-research`,
  `opus-medium-fix-doc`) từ chỗ chỉ nạp trong TDQ build lên tầng **global**
  `~/.claude/CLAUDE.md`, để áp cho MỌI lần Claude gọi Agent tool, kể cả ngoài TDQ.
- Đồng bộ file nguồn `portable/claude-md/CLAUDE.md` (test khóa ≤3500 byte, giống hệt
  bản cài).
- Đổi định dạng ở `skills/tdq-conventions/SKILL.md` §9 từ `<model>-<effort>_ <mô tả>`
  sang `<model>-<effort>-<việc-kebab>` cho khớp luật global (tránh 2 luật lệch nhau).

**Out:** không sửa hook (không có `PreToolUse` matcher cho Agent/Task — không thể ép
bằng máy), không đổi bảng mặc định model/effort theo vai ở `subagent-tuning.md`.

## Task

- [x] **T1** Rút gọn dòng 44 `~/.claude/CLAUDE.md` (bỏ "sub-agent, ") + thêm dòng luật
  riêng `- Sub-agent: description mở đầu \`<model>-<effort>-<việc>\`, vd
  \`sonnet-low-research\`.` — Test: `wc -c ~/.claude/CLAUDE.md` ≤ 3500 → 3486 PASS.
- [x] **T2** Áp đúng thay đổi T1 vào `portable/claude-md/CLAUDE.md` (file nguồn trong
  repo) — Test: `diff` hai bản rỗng + `test_claude_md_core.py` (5 test) PASS.
- [x] **T3** Sửa `skills/tdq-conventions/SKILL.md` dòng 94-95: đổi ví dụ/định dạng sang
  `<model>-<effort>-<việc-kebab>` (vd `sonnet-low-research-doc`) — Test:
  `doc_lint.py` exit 0. Sửa thêm khoá test cũ `test_skill_docs.py::test_d1_...`
  (đang khoá format `_`) sang khoá format `-` mới.
- [x] **T4** Ghi working log + `graphify extract . --code-only` — Test: entry mới trong
  `docs/workinglog/2026-08-05.md`; graphify exit 0; full suite 585/585 PASS.

## DoD

- Cả 2 bản CLAUDE.md (global + portable) đồng nhất, ≤3500 byte, chứa luật sub-agent mới.
- `tdq-conventions/SKILL.md` §9 không còn định dạng cũ `_`.
- `doc_lint.py` exit 0 trên mọi file `.md` đổi; test suite liên quan PASS.
