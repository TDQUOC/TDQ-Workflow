# QC — Nghiêm cấm Co-Authored-By và chuẩn hóa đường dẫn script plugin
Ngày: 2026-10-11 · Plan: ../plan/2026-10-11-1346-cam-co-author-fix-path-script.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Lệnh gọi script trong `skills/` | `git grep "python3 scripts/" skills/` | 0 kết quả trần, toàn bộ dùng `${CLAUDE_PLUGIN_ROOT}` | PASS |
| Q2 | Cấm Co-Authored-By | `git grep "Co-Authored-By" scripts/tdq_setup.py skills/tdq-conventions/SKILL.md docs/notes/user-level-install.md` | Có điều luật cấm trong `tdq_setup.py`, conventions, install docs | PASS |
| Q3 | Line count và drift | `pytest tests/test_skill_shape.py tests/test_luat_skill.py -q` | 23 passed, 331 subtests passed, 0.00% drift | PASS |
| Q4 | Unit test suite | `pytest tests/test_doc_lint.py tests/test_docs_consistency.py tests/test_luat_skill.py tests/test_skill_shape.py tests/test_prompt_context.py tests/test_auto_update_setup.py -q` | 139 passed, 459 subtests passed | PASS |

## Bằng chứng
### Q1
```
$ git grep "python3 scripts/" skills/
(0 matches)
```

### Q2
```
$ git grep "Co-Authored-By" scripts/tdq_setup.py skills/tdq-conventions/SKILL.md docs/notes/user-level-install.md
docs/notes/user-level-install.md:- Tên branch/commit/worktree không bắt đầu bằng `claude|antigravity|gemini|codex`. Tuyệt đối KHÔNG thêm dòng `Co-Authored-By: Claude Code...` hoặc bất kỳ attribution trailer nào vào commit message hay PR body; chỉ commit/push khi người dùng yêu cầu.
scripts/tdq_setup.py:- Tuyệt đối KHÔNG thêm dòng `Co-Authored-By: Claude Code...` hoặc bất kỳ attribution trailer nào vào git commit message hoặc PR body. Mọi commit và PR chỉ chứa nội dung kỹ thuật thuần túy do người dùng và agent trao đổi."""
skills/tdq-conventions/SKILL.md:- Commit messages and PR bodies **never** contain "generated with <AI>", any translation, or "Co-Authored-By: Claude Code...".
```

### Q3
```
$ pytest tests/test_skill_shape.py tests/test_luat_skill.py -q
.......................                                                 [100%]
23 passed, 331 subtests passed in 0.29s
```

### Q4
```
$ pytest tests/test_doc_lint.py tests/test_docs_consistency.py tests/test_luat_skill.py tests/test_skill_shape.py tests/test_prompt_context.py tests/test_auto_update_setup.py -q
139 passed, 459 subtests passed in 7.67s
```

## Lệch spec chờ duyệt
không có

## Kết luận
PASS toàn bộ
