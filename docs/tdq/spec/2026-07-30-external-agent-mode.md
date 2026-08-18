# SPEC — Mode implement "external": giao task cho Codex/Antigravity qua worktree

<!-- doc-lint: allow R10 — spec viết trước khi có luật ranh giới module -->

Ngày: 2026-07-30 · Bản: 1.1 (sau review 14 góp ý) · Request: ../requests/2026-07-30-external-agent-mode.md · Lane: full
Trạng thái: CHỜ DUYỆT
Nguồn quyết định: ../knowledge/2026-07-30-external-agent-mode.md (8 quyết định, 2 vòng interview)

## 1. Mục tiêu & phạm vi

- Mục tiêu: tdq-workflow có mode thực thi thứ 3 `external` (bên cạnh `main`, `subagent`)
  — Claude tạo worktree, giao TỪNG task của plan cho engine ngoài (Codex CLI hoặc
  Antigravity CLI) chạy headless, nhận report JSON theo schema cứng, verify, tick,
  merge. Thiết kế để model cấp thấp/context ngắn (cả engine ngoài lẫn Claude điều phối)
  chạy đúng và ổn định.
- Trong phạm vi:
  - Script `scripts/external_task.py` (chạy 1 task qua engine: build lệnh, timeout,
    validate schema, retry ≤2, log, report file) + `scripts/external_models.py`
    (liệt kê model available thật trên máy) + schema `scripts/external_report_schema.json`.
  - 2 custom subagent `agents/codex-runner.md`, `agents/agy-runner.md`.
  - Mở rộng state machine: `external` vào `VALID_MODES` + `PHASE_TABLE` (dòng cmd/
    checklist phase plan, USAGE) trong `scripts/tdq_state.py`; hooks nhắc mode
    (`prompt_context.py`, `edit_gate.py`, `_common.py`); sinh lại doc tự sinh
    `skills/tdq-conventions/references/phases.md` + đồng bộ `portable/`
    (`workflow/phases.md`, `workflow/03-plan.md`, `workflow/04-build.md`,
    `AGENTS.md`) và `skills/tdq-conventions/references/approval.md`.
  - Skill: `tdq-plan` (hỏi mode 3 lựa chọn; external → hỏi engine + trình list model
    thật, nhận 1–3 tên), `tdq-build` (nhánh external Phần A), `tdq-intake` Phần C
    (quick lane có external), `tdq-conventions` (mô tả mode + doc-tree thêm
    `docs/tdq/external/`), khuôn gói task
    `skills/tdq-build/references/external-task.md`.
  - `~/.claude/CLAUDE.md` §10: câu duyệt plan thêm `external`.
  - Hướng dẫn user cài plugin `codex@openai-codex` (luôn bật) — user gõ slash command.
  - Unit test cho mọi phần code + E2E chạy tay 1 task/engine.
- NGOÀI phạm vi:
  - Không viết plugin/marketplace mới; không dùng MCP; không đổi mode `main`/`subagent`.
  - Không quản lý quota/billing của ChatGPT/Google; không cài thêm CLI (đã có sẵn).
  - Không đổi cơ chế duyệt/gate hiện có ngoài việc nhận thêm giá trị mode.
  - Plugin codex-plugin-cc chỉ CÀI, không tích hợp vào mode external (dùng tay).

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Script chạy 1 task external (lệnh, schema, retry ≤2, log) | `scripts/external_task.py` | unit test stub-engine pass (Q4) |
| 2 | Script list model thật trên máy (agy + probe codex, cache) | `scripts/external_models.py` | unit test + chạy thật (Q5) |
| 3 | Schema report task | `scripts/external_report_schema.json` | `external_task.py` validate được (Q4) |
| 4 | 2 agent runner | `agents/codex-runner.md`, `agents/agy-runner.md` | tồn tại, đúng khuôn agent, nêu đúng lệnh script (Q7) |
| 5 | Mode `external` trong state (VALID_MODES + PHASE_TABLE + USAGE) + hooks nhắc + doc tự sinh + portable đồng bộ | `scripts/tdq_state.py`, `hooks/scripts/{prompt_context,edit_gate,_common}.py`, `skills/tdq-conventions/references/{phases,approval}.md`, `portable/…` | unit test mode external + test_phase_table + test_portable_sync (Q2, Q3) |
| 6 | Skill cập nhật: tdq-plan / tdq-build / tdq-intake / tdq-conventions + khuôn task; khuôn dòng máy-đọc trong plan: `Thực thi external: engine=<codex\|agy> · khó=<slug> · TB=<slug> · dễ=<slug>` | `skills/…` | doc_lint + grep nội dung + test parse dòng (Q7, Q4) |
| 7 | CLAUDE.md §10 nhận mode external | `~/.claude/CLAUDE.md` | grep (Q8) |
| 8 | Plugin codex cài, luôn bật | user-level (user gõ) | `/codex:setup` OK — bằng chứng chép vào QC (Q9) |
| 9 | E2E: 1 task thật qua codex + 1 qua agy trong worktree | `docs/tdq/external/<slug>/` | report JSON hợp lệ + test task pass + merge sạch (Q6) |

## 3. Cách tiếp cận & lý do

- Chọn: **wrapper script làm lõi, agent làm vỏ mỏng.** `external_task.py` ôm toàn bộ
  phần dễ sai (build lệnh CLI đúng flag, timeout, parse/validate JSON, retry kèm
  feedback lỗi, log, ghi report) — agent runner (và cả model điều phối cấp thấp) chỉ
  cần: soạn gói task → chạy 1 lệnh → đọc JSON kết quả. Càng ít bước tự do, model thấp
  càng khó trượt (nguồn: research Q7 — schema cứng + task đơn mục tiêu + few-shot).
- Chữ ký CLI cố định của lõi:
  - `external_task.py run --engine <codex|agy> --model <slug> --task-file <gói.md>
    --worktree <dir> --slug <slug>` → chạy engine (tối đa 3 attempt), ghi report
    `docs/tdq/external/<slug>/<task-id>.json` + in report ra stdout; exit 0 = report
    hợp lệ, exit 1 = hỏng cả 3 attempt (orchestrator fallback).
  - `external_task.py parse-plan <plan-file>` → in JSON `{engine, models:{khó,TB,dễ}}`
    từ dòng `Thực thi external: …`; exit 1 nếu thiếu/dị dạng dòng đó.
  - Timeout mỗi attempt: mặc định 540 giây, đổi qua env `TDQ_EXTERNAL_TIMEOUT` (giây);
    `--print-timeout` của agy sinh từ CÙNG giá trị này. Runner phải gọi script bằng
    Bash `run_in_background` + poll (trần Bash tool 10 phút, không được chờ foreground).
- Lệnh engine (đã đo trên máy, research cùng slug):
  - Codex: `codex exec --cd <worktree> -m <model> --sandbox danger-full-access
    --output-schema <schema> "<gói task>"` (codex-cli 0.146.0, login ChatGPT).
  - Antigravity: `agy -p "<gói task>" --model <slug> --output-format json --json-schema
    <schema> --dangerously-skip-permissions --print-timeout 15m` chạy với cwd = worktree
    (agy 1.1.8, đã login).
  - Full access là lựa chọn của user (questions C4) — giảm thiểu: cwd = worktree,
    gói task cấm path ngoài worktree, Claude diff-check trước merge.
- Gói task (khuôn `external-task.md`): id + mục tiêu 1 câu + danh sách file cụ thể +
  lệnh test của task + ràng buộc (không commit, không đụng ngoài danh sách file trừ
  file mới nêu trong mục tiêu, ghi log) + 1 ví dụ report mẫu đúng schema.
- Phân bổ model theo map user cấp lúc duyệt plan: 1 tên = mọi task · 2 = [khó, dễ]
  (**TB dùng tên "khó"** — ghi cứng) · 3 = [khó, TB, dễ]. Luật phân độ khó ghi cứng
  trong tdq-plan: **khó** = đụng ≥3 file hoặc thuật toán/logic lõi; **dễ** = 1 file
  và là docs/config/rename/thay chuỗi; **TB** = còn lại.
- List model trình user lấy từ `external_models.py`: agy = parse `agy models`; codex =
  probe từng slug ứng viên bằng 1 lệnh exec "reply OK" ngắn — ứng viên là hằng
  `CODEX_MODEL_CANDIDATES` trong script, override được qua env `TDQ_CODEX_MODELS`
  (danh sách phẩy); kết quả cache 7 ngày tại `~/.claude/cache/tdq-external-models.json`
  (per-machine, không nằm trong repo). Mọi probe fail/offline → vẫn exit 0, in danh
  sách ứng viên kèm nhãn `(chưa xác minh)`.
- **Luồng quick lane external** (tdq-intake Phần C): mini-plan ≤10 dòng gộp sẵn dòng
  `Thực thi external: engine=<x> · khó=<slug>…` (đề xuất 1 model default từ list) →
  user duyệt "duyệt quick external …" → ghi nhận `approve quick --mode external` →
  vẫn bắt buộc worktree `tdq-ext-<slug>`, giao từng task, diff-check + merge như full;
  dòng `Thực thi external:` chép vào working log TRƯỚC khi implement (thay cho plan file).
- **Fallback phân vai rõ**: runner CHỈ chạy script và trả kết quả cấu trúc (kể cả
  fail); mọi quyết định fallback (retry đã nằm trong script; Claude tự implement) do
  ORCHESTRATOR — hội thoại chính chạy tdq-build — thực hiện trong worktree.
- Auto engine (user nói "auto" lúc duyệt): task code/refactor/test → codex;
  research/docs/UI → agy; hòa → codex. Ghi cứng trong tdq-plan.
- Fallback: mỗi task retry ≤2 (lần 2, 3 kèm nguyên văn lỗi/validate fail vào gói task);
  vẫn hỏng → Claude tự implement task đó ngay trong worktree, ghi `fallback: claude`
  vào report. Không dừng giữa turn.
- Đã loại (questions C1–C4): codex qua /codex:rescue (2 đường không đồng nhất) · MCP
  (chậm) · model cố định/auto theo cỡ (user muốn cấp list mỗi plan) · auto theo quota
  (khó đo) · agy read-only xuất patch (user chấp nhận full access).

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| agent-development | plugin:plugin-dev | DÙNG | viết `agents/codex-runner.md`, `agents/agy-runner.md` đúng khuôn |
| skill-development | plugin:plugin-dev | DÙNG | sửa 4 skill tdq-* thêm mode external |
| hook-development | plugin:plugin-dev | DÙNG | sửa 3 hook script nhận mode external |
| claude-md-improver | plugin:claude-md-management | DÙNG | audit CLAUDE.md sau khi sửa §10 |
| tdq-build | plugin:tdq-workflow | NỀN | workflow đang chạy |
| tdq-conventions | plugin:tdq-workflow | NỀN | workflow đang chạy |
| tdq-intake | plugin:tdq-workflow | NỀN | workflow đang chạy |
| tdq-plan | plugin:tdq-workflow | NỀN | workflow đang chạy |
| tdq-spec | plugin:tdq-workflow | NỀN | workflow đang chạy |
| tdq-status | plugin:tdq-workflow | NỀN | workflow đang chạy |
| tavily-best-practices | plugin:tavily | NỀN | research đã dùng ở analyze |
| tavily-cli | plugin:tavily | NỀN | research đã dùng ở analyze |
| tavily-crawl | plugin:tavily | NỀN | research đã dùng ở analyze |
| tavily-dynamic-search | plugin:tavily | NỀN | research đã dùng ở analyze |
| tavily-extract | plugin:tavily | NỀN | research đã dùng ở analyze |
| tavily-map | plugin:tavily | NỀN | research đã dùng ở analyze |
| tavily-research | plugin:tavily | NỀN | research đã dùng ở analyze |
| tavily-search | plugin:tavily | NỀN | research đã dùng ở analyze |
| graphify | user | NỀN | cập nhật graph cuối turn có đổi code |
| plugin-structure | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| command-development | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| mcp-integration | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| plugin-settings | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| skill-creator | plugin:skill-creator | KHÔNG | spec §3 đã chọn cách khác tốt hơn (agent/skill-development của plugin-dev) |
| remember | plugin:remember | KHÔNG | khác lĩnh vực |
| frontend-design | plugin:frontend-design | KHÔNG | khác lĩnh vực |
| playground | plugin:playground | KHÔNG | khác lĩnh vực |
| writing-hookify-rules | plugin:hookify | KHÔNG | spec §3 đã chọn cách khác tốt hơn (hook-development của plugin-dev) |
| build-mcp-app | plugin:mcp-server-dev | KHÔNG | khác lĩnh vực |
| build-mcp-server | plugin:mcp-server-dev | KHÔNG | khác lĩnh vực |
| build-mcpb | plugin:mcp-server-dev | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: `external_task.py` và `external_models.py` ghi
  `docs/tdq/external/<slug>/run.log` (ISO timestamp, lệnh + args đã chạy, exit code,
  số attempt, đường dẫn report); KHÔNG ghi biến môi trường vào log (2 CLI không nhận
  key qua flag nên args an toàn); tắt bằng env `TDQ_EXTERNAL_LOG=0`.
- Không placeholder; report của engine phải là JSON qua validate schema, không chép tay.
- Mỗi phần code có unit test riêng, cả suite chạy bằng
  `python3 -m unittest discover tests`. Test KHÔNG gọi mạng/CLI thật: stub 2 binary
  `codex`/`agy` giả bằng script tạm trong PATH của test.
- Branch/worktree đặt tên `tdq-ext-<slug>` — không bắt đầu bằng
  `claude|antigravity|gemini|codex` (quy ước repo).
- Engine ngoài không được commit; Claude là người duy nhất merge sau diff-check.
  Kiểm được: trước merge, `git log` của worktree không có commit mới nào so với lúc
  tạo (engine chỉ để lại thay đổi chưa commit) — thuộc bước diff-check Q6.

## 5. Ràng buộc & rủi ro

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Full access cho engine (lựa chọn user) — agy không sandbox FS | ghi/xoá ngoài worktree | gói task cấm path ngoài + diff-check toàn repo + git log worktree không commit lạ. **Rủi ro tồn dư user đã chấp nhận**: engine ghi NGOÀI repo ($HOME…) là vô hình với git, không kiểm được |
| ChatGPT auth giới hạn model codex, slug đổi theo đợt retire | `-m` bị từ chối | probe slug thật (`CODEX_MODEL_CANDIDATES` + override `TDQ_CODEX_MODELS`) + cache 7 ngày; list trình user chỉ gồm slug probe OK |
| codex-cli đang bản alpha (0.146.0-alpha) | flag đổi giữa các bản | unit test build-lệnh + E2E tay; lỗi flag → báo trong log, fallback Claude |
| Engine treo/quá chậm; trần Bash tool 10 phút | kẹt turn / bị giết oan giữa chừng | timeout mỗi attempt 540s mặc định (`TDQ_EXTERNAL_TIMEOUT`, agy `--print-timeout` cùng nguồn); runner gọi script qua `run_in_background` + poll; quá timeout → tính 1 attempt hỏng |
| Model thấp trả sai schema nhiều lần | tốn quota | retry ≤2 rồi Claude tự làm (quyết định C8); số attempt ghi log |
| Probe model codex tốn quota nhỏ | phí | mỗi probe 1 lệnh "reply OK" ngắn; cache 7 ngày `~/.claude/cache/tdq-external-models.json` (per-machine, ngoài repo) |
| Quick lane external thêm bước hỏi | chậm việc nhỏ | mini-plan gộp sẵn dòng `Thực thi external:` với 1 model default, user duyệt 1 câu |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Toàn suite unit | `python3 -m unittest discover tests` | OK, có thêm test mới cho external (đếm tăng so 242) |
| Q2 | State nhận mode external | test: `approve plan --mode external` VÀ `approve quick --mode external` + mirror STATE.md + PHASE_TABLE/USAGE nhắc external | `implement_mode=external` cả 2 đường; mirror + `next` in external; test_phase_table & test_portable_sync pass với doc sinh lại |
| Q3 | Hooks + doc tự sinh nhắc external | test regex + grep external trong 3 hook script, `references/{phases,approval}.md`, `portable/workflow/{phases,03-plan,04-build}.md`, `portable/AGENTS.md` | mọi chỗ liệt kê mode đều có đủ 3 mode |
| Q4 | `external_task.py` với engine stub (không mạng) | unit: stub codex/agy trả (a) JSON đúng (b) sai schema→retry→đúng (c) hỏng cả 3 attempt (d) timeout (e) `TDQ_EXTERNAL_LOG=0` (f) binary không có trong PATH (g) exit≠0 nhưng stdout JSON hợp lệ (h) attempt 2/3 kèm nguyên văn lỗi trước đó trong prompt (i) `TDQ_EXTERNAL_TIMEOUT` override + agy `--print-timeout` cùng giá trị (j) `parse-plan` đúng/dị dạng | từng nhánh assert đúng mô tả; (c)(f) exit 1 + log đủ attempt; (h) assert nội dung prompt stub nhận được |
| Q5 | `external_models.py` thật trên máy | chạy `list agy` và `list codex`; unit stub nhánh "mọi probe fail" | agy ≥1 slug khớp `agy models`; codex trả danh sách probe OK hoặc nhãn `(chưa xác minh)`; cache ghi đúng `~/.claude/cache/` — output chép vào QC |
| Q6 | E2E tay 2 engine | 1 task nhỏ thật/engine trong worktree `tdq-ext-<slug>` | report JSON pass schema, test task pass, diff-check sạch, `git log` worktree không commit lạ, merge không conflict — bằng chứng vào QC |
| Q7 | Skill + agent + khuôn task | `doc_lint.py docs/tdq/spec` + `--pair` + grep `external` trong 4 skill; 2 agent tồn tại đúng khuôn frontmatter và nêu đúng chữ ký lệnh `external_task.py run` | lint exit 0; grep ≥1/skill; agent nêu lệnh khớp chữ ký §3 |
| Q8 | CLAUDE.md §10 | grep pattern `duyệt plan mode` và `external` trong `~/.claude/CLAUDE.md` | câu duyệt plan liệt kê đủ 3 mode |
| Q9 | Plugin codex | user gõ đúng 4 lệnh: `/plugin marketplace add openai/codex-plugin-cc` → `/plugin install codex@openai-codex` → `/reload-plugins` → `/codex:setup` (Claude chỉ hướng dẫn, không tự chạy được) | output `/codex:setup` OK chép vào QC; `claude plugin list` có `codex@openai-codex` bật — DoD mục này CHỜ user thao tác |

DoD: Q1–Q9 PASS, report `docs/tdq/reports/<slug>.md` ≤ 50 dòng, working log ghi đủ.

## 7. Câu hỏi còn mở

(RỖNG — 8 quyết định đã chốt ở knowledge, 2 vòng interview.)
