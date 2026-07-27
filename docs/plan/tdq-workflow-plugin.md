# Plan — TDQWorkflow Plugin v0.1

- **Trạng thái**: HOÀN THÀNH (2026-07-27) — 19/19 task, DoD 5/5 PASS
- **Ngày**: 2026-07-27 · **Spec nguồn**: `docs/spec/tdq-workflow-plugin.md` v0.1.6 (ĐÃ DUYỆT)
- **Executor**: Claude tự thực thi, mode main-agent, **end-to-end trong 1 turn** sau khi plan được duyệt.

## Nguyên tắc thực thi
- Hook/script: python3 **thuần stdlib** (json, sys, os, re, hashlib, datetime) — không dependency ngoài. Test bằng `unittest` (stdlib), fixture stdin JSON tại `tests/fixtures/`, chạy `python3 -m unittest discover tests`.
- Skill/agent: chỉ dẫn nội bộ EN, mọi output cho user VI; tuân budget lazy load (spec mục 3.1).
- **Tick `[x]` NGAY khi vừa xong từng task (test/validate của task đó pass) — không gom chờ cuối phase/cuối turn**; xong mỗi phase chạy validate tổng của phase.
- Doc meta-build của repo này: QC → `docs/qc/`, report → `docs/reports/`, log → `docs/workinglog/`.
- Git: init branch `main`; tên branch/commit không phạm quy; kết thúc hỏi user trước khi commit.

## Phase A — Nền móng
- [x] **A1.** `git init` (branch `main`) + `.gitignore` (`__pycache__/`, `*.pyc`, `.pytest_cache/`, `docs/tdq/state.json`). — Validate: `git status` hoạt động, branch đúng.
- [x] **A2.** `.claude-plugin/plugin.json` (name `tdq-workflow`, v0.1.0) + khung thư mục `skills/ agents/ hooks/scripts/ scripts/ tests/`. — Validate: `claude plugin validate . --strict` PASS.
- [x] **A3.** `scripts/tdq_state.py`: get/set/reset, schema mặc định đúng spec mục 4, ghi atomic (temp + rename). — Test: roundtrip set/get; thiếu file → default; ghi đè an toàn.

## Phase B — Hooks + unit test (red/green từng script)
- [x] **B1.** `approve_gate.py` (`UserPromptExpansion` matcher `tdq-approve`). — Test: green `spec` hợp lệ → approved + path/sha256/timestamp; red `plan` khi spec chưa duyệt; red file chưa đăng ký / không tồn tại / rỗng → block, state không đổi; green `quick` đúng lane / red sai lane; sai arg → usage VI, state không đổi.
- [x] **B2.** `edit_gate.py` (`PreToolUse` Edit|Write|MultiEdit|NotebookEdit). — Test: red Edit `src/` khi full chưa duyệt (reason kèm lệnh duyệt); green Edit `docs/**`; red `docs/tdq/state.json` mọi lúc; quick: red chưa duyệt / red log chưa cập nhật sau duyệt (mtime ≤ `quick_approved_at`) / green log đã append; cảnh báo sha256 lệch sau duyệt; lane null → allow im lặng.
- [x] **B3.** `bash_gate.py` (`PreToolUse` Bash). — Test: red naming git phạm quy (`claude|antigravity|gemini|codex`) + commit msg "generated with…"; red Bash ghi state.json (`>`, `>>`, `tee`, `sed -i`, `mv/cp`); green đọc `cat`/`jq`; green lệnh thường.
- [x] **B4.** `session_start.py` + `prompt_context.py`. — Test: inject đúng theo state (full: 1 dòng phase; full/quick đang chờ duyệt: kèm lệnh duyệt); không request → im lặng exit 0; SessionStart ≤ 3 dòng + nhắc graphify khi thiếu.
- [x] **B5.** `stop_gate.py` (`Stop`). — Test: turn có thay đổi repo mà log hôm nay chưa cập nhật → block 1 lần kèm reason; `stop_hook_active` → không block lại; không thay đổi → im lặng.
- [x] **B6.** `hooks/hooks.json` nối 6 hook (đường dẫn `${CLAUDE_PLUGIN_ROOT}`). — Validate: plugin validate `--strict` PASS + toàn bộ unittest PASS.

## Phase C — Skills (10)
- [x] **C1.** `tdq-conventions` (`user-invocable: false`): quy ước doc/git/log/research + Tavily (spec mục 9); phần dài → `references/`.
- [x] **C2.** `tdq-start` (intake, ghi request, đề xuất + hỏi lane, flow quick mục 5.0) + `tdq-analyze` (interview loop, questions/research/knowledge, cấm placeholder).
- [x] **C3.** `tdq-spec` + `tdq-plan` (đăng ký `spec_file`/`plan_file` trước khi mời duyệt, gọi reviewer, hướng dẫn duyệt) + `tdq-implement` (2 mode main/subagent, worktree, tick plan, end-to-end 1 turn).
- [x] **C4.** `tdq-qc` (loop về plan không cần duyệt lại) + `tdq-report` (≤ 50 dòng) + `tdq-approve` (`disable-model-invocation: true`, `argument-hint: [spec|plan|quick]`) + `tdq-status`.
- [x] **Validate C**: plugin validate `--strict` PASS; check budget: description ≤ 2 dòng, body ≤ 500 dòng (`wc -l`, kết quả ghi vào QC).

## Phase D — Agents
- [x] **D1.** `agents/tdq-reviewer.md`, `tdq-implementer.md`, `tdq-qc-tester.md` (không khai báo hooks/permissionMode). — Validate: plugin validate PASS.

## Phase E — QC tổng + tài liệu
- [x] **E1.** Smoke e2e headless: `claude -p --plugin-dir .` trên project tạm (scratchpad), cả 2 lane full + quick → kết quả `docs/qc/`.
- [x] **E2.** Ước lượng token idle (metadata skills/agents + inject SessionStart/UserPromptSubmit, ~4 chars/token) < ~800 → `docs/qc/`.
- [x] **E3.** `README.md` (VI) + `docs/notes/user-level-install.md` (kèm hướng dẫn user tự đổi rule log user-level về `docs/workinglog/` — không tự cài user-level).
- [x] **E4.** Report cuối ≤ 50 dòng → `docs/reports/` + working log + **hỏi user có muốn commit không**.

## Definition of Done (theo spec mục 10)
1. `claude plugin validate . --strict` PASS.
2. Unittest hooks PASS đủ case red/green ở Phase B.
3. Smoke e2e 2 lane PASS.
4. Token budget idle đạt (< ~800).
5. Kết quả QC lưu `docs/qc/`.
