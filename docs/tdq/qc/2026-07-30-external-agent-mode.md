# QC — Mode implement "external" (Codex/Antigravity qua worktree)

Ngày: 2026-07-30 · Plan: ../plan/2026-07-30-external-agent-mode.md · Vòng: 1

## Bằng chứng T3.7 — audit CLAUDE.md (skill claude-md-improver)

Rubric: mâu thuẫn nội bộ, tính hành-động-được, súc tích, đúng hiện trạng. Phạm vi:
§10 (2 dòng mới) đối chiếu toàn file — chỉ ÁP sửa trong §10 (trường "Không dùng cho").

| Góp ý audit | Xử lý |
|---|---|
| Dòng external mới trỏ `scripts/external_models.py` như path project-local — ở project khác script nằm trong plugin, model thấp sẽ tìm sai chỗ | ÁP: đổi thành "script `external_models.py` của plugin, chạy qua `${CLAUDE_PLUGIN_ROOT}/scripts/`" |
| §5 có câu cũ "hỏi người dùng có muốn tạo spec/plan cho codex hoặc antigravity thực thi không" — trùng/chồng khái niệm với mode external §10 (nay đã chính thức hoá) | KHÔNG SỬA (ngoài phạm vi §10 theo hợp đồng). Ghi nhận: nên gộp câu §5 về mode external trong một request dọn CLAUDE.md sau |
| §2 cấm branch bắt đầu `claude|antigravity|gemini|codex` — worktree external đặt `tdq-ext-<slug>` không phạm; engine bị cấm commit nên không đụng luật commit §2 | Không cần sửa — nhất quán |

(Các mục DoD Q1–Q9 bổ sung ở T4.5 — file này được append, không tạo mới đè.)

## Bảng DoD Q1–Q9 (T4.5, vòng 1)

| # | Hạng mục | Kết quả | Bằng chứng |
|---|---|---|---|
| Q1 | Toàn suite unit | PASS | `cd tests && python3 -m unittest discover .` → `Ran 285 tests … OK` (tăng so 242; +34 test external + 4 test E2E + khác) |
| Q2 | State nhận mode external | PASS | test_state.py: `approve plan --mode external` & `approve quick --mode external` → `implement_mode=external`, STATE.md mirror, `next`/USAGE/PHASE_TABLE nhắc external — nằm trong suite 285 OK; test_phase_table + test_portable_sync pass |
| Q3 | Hooks + doc tự sinh | PASS | test_context_hooks ("duyệt plan mode external" → `--mode external`) + test_edit_gate pass; grep `external` có trong phases.md (2 bản), approval.md (2 bản), 03-plan/04-build.md, portable/AGENTS.md |
| Q4 | external_task.py stub 10 nhánh a–j | PASS | tests/test_external_task.py 27 test (Schema/Run/Retry/Fail/Log/ParsePlan) — stub binary cô lập PATH, không mạng; trong suite 285 OK |
| Q5 | external_models.py thật trên máy | PASS | `list agy` = 11 slug khớp `agy models`; `list codex` probe thật: gpt-5.5, gpt-5.4, gpt-5.4-mini OK · gpt-5-codex, gpt-5.3-codex `(chưa xác minh)`; cache `~/.claude/cache/tdq-external-models.json` (328b); log `docs/tdq/external/models.log` |
| Q6 | E2E tay 2 engine | PASS | Codex: E2E-CODEX report validate=OK (run.log 22:59:34), engine tự tạo 2 file + test trong worktree, verify `Ran 2 tests OK`. Agy: engine trả report "done" nhưng KHÔNG tạo file (đo 2 model + accept-edits + pseudo-TTY) → verify bắt bịa, đi đúng đường FALLBACK: orchestrator tự implement, report `E2E-AGY.json` kèm `"fallback": "claude"`. Đóng worktree: `git log 873ee67..HEAD` RỖNG, `status --porcelain` = đúng 4 file của 2 report, mang về cây chính bằng copy (KHÔNG commit — user chưa yêu cầu), `python3 -m unittest tests.test_e2e_codex tests.test_e2e_agy` → `Ran 4 tests OK` tại repo chính, worktree + branch đã xoá |
| Q7 | Skill + agent + khuôn task | PASS | `doc_lint.py docs/tdq/spec` exit 0; `--pair spec plan` exit 0; grep `external` ≥1 trong 4 skill; agents codex-runner/agy-runner đúng frontmatter + chữ ký lệnh (RunnerAgentsTest pass) |
| Q8 | CLAUDE.md §10 | PASS | grep: câu duyệt "`duyệt plan mode main` — mode: main \| subagent \| external" + bullet Mode external có trong `~/.claude/CLAUDE.md` |
| Q9 | Plugin codex | PENDING (chờ user) | Claude không tự chạy được slash command. 4 lệnh đã trình cho user; chờ user dán output `/codex:setup` + `claude plugin list` |

## Ghi chú sai lệch có chủ đích (vòng 1)

- T1.2–T1.6: lõi `external_task.py` viết gộp tại T1.1 → các test T1.2–T1.6 là
  tests-after (vẫn kiểm hành vi thật bằng stub, đủ nhánh a–j). Không phải red-first thuần.
- Giới hạn engine đo được: agy 1.1.8 headless `-p` không thực thi tool sửa file (kể cả
  `--mode accept-edits`, `--dangerously-skip-permissions`, pseudo-TTY) — đã ghi cảnh báo
  vào tdq-plan bước "Chốt engine + model"; thiết kế verify+fallback xử lý đúng.
- Test E2E merge về repo chính có thêm 3 dòng chèn `sys.path` (suite repo chạy từ
  `tests/`); dòng import nguyên văn của gói task giữ nguyên.
- Round 1 codex bị HTTP 400 do schema có khóa optional → schema file bỏ `fallback`
  (OpenAI structured output đòi mọi property required); validator vẫn nhận `fallback`
  cho report do orchestrator ghi, và TỪ CHỐI khi engine tự phát (có test).

## Đính chính sau QC (23:45, request fix-agy-adddir-sync-agent)

Dòng Q6 và ghi chú "agy không thực thi tool sửa file" cần đọc kèm đính chính: agy CÓ
thực thi tool, nhưng ghi vào workspace scratch `~/.gemini/antigravity-cli/scratch/`
thay vì worktree (bằng chứng trong knowledge cùng slug). Đã fix bằng `--add-dir` trong
`external_task.py`; verify+fallback vòng QC này vẫn đúng vai trò (bắt được file không
xuất hiện trong worktree).
