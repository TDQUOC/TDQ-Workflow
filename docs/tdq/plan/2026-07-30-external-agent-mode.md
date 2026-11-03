# PLAN — Mode implement "external" (Codex/Antigravity qua worktree) — HOÀN THÀNH (mode main, 2026-07-30 23:10; Q9 PENDING chờ user cài plugin codex)

Spec nguồn: ../spec/2026-07-30-external-agent-mode.md (v1.1, duyệt 22:16) · Ngày: 2026-07-30

Mode thực thi: main — task đụng chung `tdq_state.py` + hooks + 4 skill + portable
(phụ thuộc tuần tự chặt), nhiều bước ghi `~/.claude/` và E2E gọi CLI thật — worktree
không cô lập được các phần này.

## Năng lực → task

| Skill DÙNG (spec §3b) | Task |
|---|---|
| hook-development (plugin-dev) | T2.2 |
| agent-development (plugin-dev) | T3.2 |
| skill-development (plugin-dev) | T3.3–T3.5 |
| claude-md-improver (claude-md-management) | T3.7 |

## P1 — Lõi script + unit test (repo, red → green từng task)

- [x] **T1.1** Tạo `scripts/external_report_schema.json` (khóa bắt buộc: task_id,
  status done|blocked, files_changed[], test_cmd, test_result, notes; khóa TÙY CHỌN:
  `fallback` — nhận giá trị "claude" khi orchestrator tự làm) + hàm validate trong
  `scripts/external_task.py`. — Test: `tests/test_external_task.py::SchemaTest`
  (report đúng pass, thiếu khóa/enum sai fail, report có `fallback: claude` pass).
- [x] **T1.2** `external_task.py run --engine <codex|agy> --model <slug> --task-file
  <gói.md> --worktree <dir> --slug <slug>`: build đúng lệnh spec §3 (codex exec
  --cd/-m/--sandbox danger-full-access/--output-schema; agy -p/--model/--output-format
  json/--json-schema/--dangerously-skip-permissions, cwd=worktree), chạy engine, ghi
  report `docs/tdq/external/<slug>/<task-id>.json`, in report ra stdout, exit 0.
  Test dùng stub binary codex/agy (script tạm trong PATH, KHÔNG mạng).
  — Test: `RunTest::test_ok_codex` + `test_ok_agy` (nhánh a: JSON đúng → report đúng
  chỗ; assert stub nhận đủ flag).
- [x] **T1.3** Retry ≤2: attempt 2/3 gói task kèm nguyên văn lỗi trước đó (validate
  fail/stderr). — Test: `RetryTest` (nhánh b: sai schema lần 1 → lần 2 pass, đúng 2
  lần gọi; nhánh h: assert prompt lần 2 chứa lỗi lần 1).
- [x] **T1.4** Nhánh hỏng: cả 3 attempt hỏng → exit 1; timeout mỗi attempt (kill
  process, tính 1 attempt hỏng); binary không có trong PATH → exit 1 ngay có log;
  exit≠0 nhưng stdout JSON hợp lệ → tính hợp lệ kèm note. — Test: `FailTest`
  (nhánh c, d, f, g).
- [x] **T1.5** Log service: `docs/tdq/external/<slug>/run.log` dòng ISO-timestamp
  (lệnh + args, exit, attempt, report path; không ghi env); `TDQ_EXTERNAL_LOG=0` →
  không ghi; `TDQ_EXTERNAL_TIMEOUT` override và agy `--print-timeout` sinh từ CÙNG
  giá trị. — Test: `LogTest` (nhánh e, i).
- [x] **T1.6** `external_task.py parse-plan <plan-file>`: đọc dòng
  `Thực thi external: engine=<codex|agy> · khó=<slug> · TB=<slug> · dễ=<slug>`
  (TB/dễ được phép vắng: 1 tên = mọi task, 2 tên = TB dùng "khó") → in JSON; thiếu/dị
  dạng → exit 1. — Test: `ParsePlanTest` (nhánh j: 1/2/3 tên + dị dạng).
- [x] **T1.7** `scripts/external_models.py list <agy|codex>`: agy = parse
  `agy models`; codex = probe từng slug `CODEX_MODEL_CANDIDATES` (override env
  `TDQ_CODEX_MODELS`) bằng đúng lệnh
  `codex exec -m <slug> --sandbox read-only "reply with exactly: OK"` — PASS = exit 0
  (slug vào danh sách), FAIL = slug đó nhãn `(chưa xác minh)`; cache 7 ngày
  `~/.claude/cache/tdq-external-models.json`; mọi probe fail/offline → vẫn exit 0 +
  toàn nhãn `(chưa xác minh)`; log như T1.5. — Test: `tests/test_external_models.py`
  (stub 2 binary: list đúng, cache ghi/đọc, override env, nhánh mọi-probe-fail).

## P2 — State machine + hooks + doc tự sinh

(Lưu ý thứ tự: sau T2.1, `test_phase_table` ĐỎ là ĐÚNG dự kiến — xanh lại khi T2.3
sinh lại doc. Không phải lỗi.)

- [x] **T2.1** `scripts/tdq_state.py`: thêm `external` vào `VALID_MODES`, USAGE,
  `PHASE_TABLE` (CHỈ SỬA row hiện có — `test_all_phases_covered` khóa cứng 9 key,
  không thêm key mới), chuỗi literal `"Mode không hợp lệ (main|subagent)."` ở
  `_parse_approve_args` (~dòng 796); `_common.py` câu nhắc duyệt plan thêm external.
  — Test: `tests/test_state.py` thêm case `approve plan --mode external` VÀ
  `approve quick --mode external` → `implement_mode=external`; mirror STATE.md +
  `next` in đủ 3 mode.
- [x] **T2.2** `hooks/scripts/prompt_context.py` (regex MODE) + `edit_gate.py`
  (chuỗi nhắc mode) nhận external. — Test: `tests/test_context_hooks.py` +
  `test_edit_gate.py` case câu "duyệt plan mode external" được nhận diện.
  - Dùng: hook-development
  - Nạp: gọi Skill `plugin-dev:hook-development` trước khi sửa 2 hook script
  - Để: sửa đúng chỗ nhận diện mode trong hook, không phá contract exit-0/soft-gate
  - Ra: 2 hook script nhận diện đủ 3 mode
  - Kiểm: lệnh test của T2.2 pass
  - Không dùng cho: hooks user-level trong `~/.claude/settings.json` (ngoài phạm vi)
- [x] **T2.3** Sinh lại doc tự sinh: `tdq_state.py phases-doc` →
  `skills/tdq-conventions/references/phases.md` + bản portable
  `portable/workflow/phases.md`; sửa `references/approval.md`, `portable/AGENTS.md`.
  (`portable/workflow/{03-plan,04-build}.md` KHÔNG sửa ở đây — đồng bộ cùng lúc với
  SKILL.md tại T3.3/T3.4 vì `test_portable_sync` so khớp từng dòng.) — Test:
  `python3 -m unittest tests.test_phase_table` pass; grep `external` ≥1 trong
  `phases.md` (2 bản), `approval.md`, `AGENTS.md`.

## P3 — Khuôn task + agents + skills + CLAUDE.md

- [x] **T3.1** Viết khuôn gói task `skills/tdq-build/references/external-task.md`:
  id, mục tiêu 1 câu, danh sách file, lệnh test, ràng buộc (không commit, không path
  ngoài worktree, log), 1 ví dụ report mẫu đúng schema. — Test: grep đủ 6 mục trong
  file; ví dụ mẫu validate pass bằng `SchemaTest` helper.
- [x] **T3.2** Viết `agents/codex-runner.md` + `agents/agy-runner.md` (vỏ mỏng):
  nhận gói task → chạy `external_task.py run …` bằng Bash `run_in_background` + poll
  → đọc report JSON → trả kết quả cấu trúc; KHÔNG tự quyết fallback (trả fail cấu
  trúc cho orchestrator). — Test: 2 file tồn tại, frontmatter name/description hợp lệ,
  grep chữ ký lệnh khớp spec §3 trong cả 2 file.
  - Dùng: agent-development
  - Nạp: gọi Skill `plugin-dev:agent-development` trước khi viết 2 agent
  - Để: đúng khuôn frontmatter + system prompt agent của Claude Code
  - Ra: `agents/codex-runner.md`, `agents/agy-runner.md`
  - Kiểm: lệnh test của T3.2 pass
  - Không dùng cho: agents tdq-implementer/qc-tester/reviewer sẵn có (không đổi)
- [x] **T3.3** Skill `tdq-plan`: bước hỏi mode thành 3 lựa chọn; nếu external → hỏi
  engine (codex|antigravity|auto — luật auto: code/refactor/test→codex,
  research/docs/UI→agy, hòa→codex), chạy `external_models.py list`, trình list model
  thật, nhận 1–3 tên (1=mọi task · 2=[khó, dễ], TB dùng "khó" · 3=[khó, TB, dễ]),
  luật độ khó (khó=≥3 file hoặc logic lõi; dễ=1 file docs/config/rename; TB=còn lại),
  ghi dòng `Thực thi external: …` vào plan. "auto" được tdq-plan RESOLVE thành đúng
  1 engine cho CẢ plan (theo đa số task, hòa→codex) TRƯỚC khi ghi dòng — dòng máy-đọc
  và `parse-plan` không bao giờ chứa chữ "auto". Đồng bộ `portable/workflow/03-plan.md`
  cùng lúc. — Test: grep từng đoạn (3 mode, luật auto, luật độ khó, dòng máy-đọc)
  trong SKILL.md; `python3 -m unittest tests.test_portable_sync` pass.
  - Dùng: skill-development
  - Nạp: gọi Skill `plugin-dev:skill-development` trước khi sửa các SKILL.md T3.3–T3.5
  - Để: giữ đúng khuôn skill (description trigger, progressive disclosure, ≤500 dòng)
  - Ra: 4 SKILL.md cập nhật (tdq-plan, tdq-build, tdq-intake, tdq-conventions)
  - Kiểm: lệnh test của T3.3, T3.4, T3.5 pass
  - Không dùng cho: viết skill mới ngoài 4 skill trên
- [x] **T3.4** Skill `tdq-build` nhánh external (Phần A): tạo worktree
  `tdq-ext-<slug>`; mỗi task = soạn gói task theo khuôn → gọi runner đúng engine →
  verify: tự chạy lại lệnh test của task trong worktree → tick; runner/script fail
  (exit 1) → orchestrator TỰ implement task đó trong worktree VÀ tự viết report kèm
  `fallback: claude`; xong hết, kiểm bằng lệnh nguyên văn:
  `git -C <worktree> log --oneline <base>..HEAD` phải RỖNG (engine cấm commit) và
  diff-check = `git -C <worktree> diff --stat` so khớp danh sách `files_changed` của
  các report → merge → dọn worktree. Đồng bộ `portable/workflow/04-build.md` cùng lúc.
  — Test: grep các bước (worktree, run_in_background, verify, fallback, `log
  --oneline`, `diff --stat`, merge) trong SKILL.md;
  `python3 -m unittest tests.test_portable_sync` pass.
- [x] **T3.5** Skill `tdq-intake` Phần C: mini-plan quick được chọn external (gộp dòng
  `Thực thi external:` + 1 model default từ list), duyệt
  `approve quick --mode external`, chép dòng `Thực thi external:` vào working log
  TRƯỚC khi implement, vẫn worktree + diff-check + merge; skill `tdq-conventions`:
  mô tả 3 mode + doc-tree thêm `docs/tdq/external/`. — Test: grep external trong 2
  SKILL.md; grep cụm "working log" trong đoạn quick-external của tdq-intake; grep
  `external/` trong đoạn doc-tree.
- [x] **T3.6** `~/.claude/CLAUDE.md` §10: câu duyệt plan liệt kê 3 mode + 1 dòng mô tả
  mode external. — Test: grep `duyệt plan mode` và `external` trong `~/.claude/CLAUDE.md`.
- [x] **T3.7** Audit CLAUDE.md sau sửa, áp góp ý hợp lý, ghi kết quả vào QC. — Test:
  mục audit trong file QC có bảng góp ý + cách xử lý.
  - Dùng: claude-md-improver
  - Nạp: gọi Skill `claude-md-management:claude-md-improver` sau T3.6
  - Để: soát mâu thuẫn §10 mới với phần còn lại của CLAUDE.md
  - Ra: bảng góp ý + diff đã áp trong `docs/tdq/qc/<slug>.md`
  - Kiểm: lệnh test của T3.7 pass
  - Không dùng cho: sửa các mục CLAUDE.md ngoài §10

## P4 — Cài plugin + chạy thật + QC + đóng

- [x] **T4.1** Chạy thật `external_models.py list agy` và `list codex` trên máy
  (mạng thật, có probe + cache). — Test: agy ≥1 slug khớp `agy models`; codex ra danh
  sách probe OK hoặc nhãn `(chưa xác minh)`; output + đường cache chép vào QC (Q5).
- [x] **T4.2** E2E tay 2 engine trong worktree `tdq-ext-2026-07-30-external-agent-mode`:
  task codex = viết `scripts/samples/e2e_codex.py` (hàm `add`) +
  `tests/test_e2e_codex.py`; task agy = tương tự `e2e_agy`; gói task ghi NGUYÊN VĂN
  dòng import `from scripts.samples.e2e_codex import add` (tương ứng `e2e_agy`) và
  lệnh test `python3 -m unittest tests.test_e2e_codex` chạy từ root worktree; mỗi
  task đi đủ pipeline gói task → runner → report JSON pass schema → verify test →
  diff-check + `git log` sạch → merge. — Test: 2 report hợp lệ,
  `python3 -m unittest tests.test_e2e_codex tests.test_e2e_agy` OK sau merge,
  bằng chứng vào QC (Q6).
- [x] **T4.3** Hướng dẫn user cài plugin codex bằng đúng 4 lệnh
  (`/plugin marketplace add openai/codex-plugin-cc` → `/plugin install
  codex@openai-codex` → `/reload-plugins` → `/codex:setup`) — Claude không tự chạy
  được slash command; chờ user dán kết quả. — Test: output `/codex:setup` OK +
  `claude plugin list` có `codex@openai-codex` bật, chép vào QC (Q9; mục này được
  phép PENDING nếu user chưa thao tác — ghi rõ trong QC).
- [x] **T4.4** Toàn suite + lint: `python3 -m unittest discover tests` OK (số test
  tăng so 242); `doc_lint.py docs/tdq/spec` + `--pair <spec> <plan>` exit 0. — Test:
  3 lệnh exit 0 (Q1, Q7).
- [x] **T4.5** QC file `docs/tdq/qc/<slug>.md` bảng đủ 9 mục Q1–Q9 kèm bằng chứng +
  report `docs/tdq/reports/<slug>.md` ≤ 50 dòng + working log + graphify. — Test:
  QC đủ 9 dòng PASS/FAIL(/PENDING Q9); `wc -l` report ≤ 50.

## Definition of Done

Theo đúng spec §6 (Q1–Q9) — file QC T4.5 đối chiếu từng mục.
