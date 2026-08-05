# Changelog

Mới nhất trên cùng. Ngày theo múi giờ máy phát hành.

## 0.7.0 — 2026-08-05

Workflow linh hoạt: gộp gate spec → plan → build trong cùng turn, lane quick vẫn đủ
bước tư duy, bỏ vòng review máy giữa spec và plan.

Tối ưu token 2 vòng: `token_audit.py` sửa lỗi đếm theo dòng JSONL (lệch +62%) · CLAUDE.md
lõi rút còn 3,2 KB và đẩy luật chi tiết sang `skills/*/references`. Bookkeeping cuối turn
gộp về `tdq_finish.py`, digest sub-agent có trần, 10 LSP chuyển sang nạp theo yêu cầu.

Report của request rút trần từ 50 xuống 10 dòng.

Bộ export sang máy khác đổi từ 7 bước tay sang `scripts/claude_export.py` với 2 lệnh
`build` và `check`. Bản copy repo lấy bằng `git clone` (giữ `.git`, chỉ file tracked) ·
cấu hình MCP đi kèm để khôi phục bằng `claude mcp add-json`. Manifest ghi phiên bản
plugin + commit SHA + sha256 từng file, còn `check` đo độ lệch giữa bundle và máy nguồn.

`approve spec|plan` nay ghi lại được khi file đã sửa sau lần duyệt trước. sha256 và dấu
duyệt được làm mới thay vì bỏ qua · cảnh báo "đã đổi sau khi duyệt" không còn treo vĩnh
viễn sau khi QC sửa spec. File không đổi thì lệnh vẫn là no-op như cũ.

## 0.6.2 — 2026-08-02

Intake default tuyệt đối (mọi prompt mới → tdq-intake), hint duyệt plan theo mode
động, tự chọn đề xuất khi gặp chặn kỹ thuật giữa build (được tự commit gỡ chặn,
không push).

## 0.6.1 — 2026-07-31

Audit toàn diện 0.6.0: 44 findings (A1–A44), 33 issue S/M fix có test riêng,
harden contract cho model cấp thấp; QC Q1–Q10 PASS, suite 367 test.

### Fix
- `tdq_state.py`: literal `\1` + wrap đôi backtick trong `phases-doc`; terminal
  state cho lane quick (idle không lặp checklist); `phases-doc [--plugin-root]`
  sinh 2 bản phases.md (skills plugin-root ↔ portable relative); `_row_age_ok`
  chịu timestamp số.
- `external_task.py`: persist raw output engine khi validate FAIL; retry feed
  trích stdout attempt trước; timeout wrapper/engine so le (A13); atomic write
  report; dir neo project-dir thay vì cwd (cùng `external_models.py`).
- `search_task.py`: guard load schema; `merge` báo `agents_skipped` thay vì nuốt
  file hỏng; cảnh báo separator route chứa `;`; copy brief atomic; raw persist.
- `doc_lint.py`: path không tồn tại → exit 2 thay vì im lặng pass; lỗi IO ra
  message tử tế. `skill_inventory.py` dùng resolver project-dir chung.
- Hook: truncation không cắt giữa inline-code; `plugin_tiers.py` warn luôn ra
  stderr kể cả khi tắt log.

### Đổi
- 4 agent def runner/scout viết lại theo cơ chế chờ thật (Bash nền → đánh thức),
  bảng exit code 0/1/2/3, nhánh `scout-failed`; `tdq-qc-tester`/`tdq-reviewer`
  khóa `tools:` read-only (cần reload plugin).
- Docs đồng bộ: thời điểm chốt engine+model (CLAUDE.md §10 ↔ tdq-plan), run-dir
  định nghĩa trong deep-search.md, portable bổ sung external-task.md + 3 file
  scripts trong README, tdq-spec thêm lệnh doc_lint single-file.

## 0.6.0 — 2026-07-31

Deep search nâng thành flow hybrid 2 phase: phase 1 = agent `search-scout`
(Claude + Tavily) chạy song song `search-runner` (agy) đi rộng nắm hướng;
phase 2 = `search-runner` đào sâu theo ≤3 route Claude chốt; merge chung 1 lần.

### Thêm
- **`agents/search-scout.md`**: slot Claude scout cố định (agent 2, route `scout:`) —
  search rộng qua tavily-primary, ghi `agent-2.json` đúng format file agent
  (url_alive/not_found/queries_used), trả 3–5 route gợi ý cho phase 2.
- **`search_task.py split --start-agent N`** (default 1): phase 2 đánh số agent từ 3
  để chung run-dir với phase 1, merge một lần cuối.

### Đổi
- Default model agy: `gemini-3.6-flash-low` → **`gemini-3.6-flash-medium`**
  (escalation giữ flash-high, ≤2 retry).
- `deep-search.md` viết lại theo flow hybrid: slot cố định phase 1 (ngoại lệ luật
  split), mục `## Hướng từ phase 1` + `brief-phase2.md`, 3 nhánh degrade
  (agent 1 hỏng / scout-failed / cả hai hỏng), luôn chạy đủ 2 phase.
- `tavily.md`, `portable/workflow/06-deep-search.md`, CLAUDE.md §10 đồng bộ flow mới.

## 0.5.0 — 2026-07-31

Deep search mặc định đi qua agent `search-runner` + agy CLI: mọi logic dễ hỏng
(cap, retry/escalation, schema, URL sống, dedup, rank tất định, log) nằm trong
`scripts/search_task.py`; model cấp thấp chỉ nhận từng việc nhỏ đã đóng khung.

### Thêm
- **`scripts/search_task.py`** (`split` / `run` / `merge`): chia route round-robin theo
  cap `TDQ_SEARCH_MAX_AGENTS`; mỗi route 1 lần search + đọc sâu ≤N URL qua agy
  `--json-schema`; retry ≤2 với escalation model + đính lỗi cũ vào prompt; check URL
  sống (HEAD→GET); merge dedup theo URL chuẩn hoá, rank tất định (route xác nhận →
  URL sống → có quote → score); log per-agent ISO timestamp, `TDQ_SEARCH_LOG=0` tắt.
- **`scripts/search_report_schema.json`**: schema report bắt buộc evidence quote +
  `source_url` có path; nguồn duy nhất của luật URL.
- **Agent `search-runner`** (vỏ mỏng chạy script) + tài liệu
  `references/deep-search.md` (luật trigger ≥2 dấu hiệu, brief FULL data,
  fallback Tavily khi `engine-failed` ≥2 lần); tầng search ghi ở `tavily.md`,
  `tdq-intake` B3 và `portable/workflow/06-deep-search.md`.
- **`.claude/settings.json`** (project): env block TDQ_SEARCH_* mặc định.

## 0.3.3 — 2026-07-29

Workflow trước đây không hề rà soát skill phụ trợ đang có (audit: điểm mù, không phải
giới hạn kỹ thuật). Bản này thêm bước kiểm kê năng lực bắt buộc, thiên lệch về phía DÙNG,
viết máy móc đủ cho model nhỏ chạy local.

### Thêm
- **`scripts/skill_inventory.py`**: quét skill trên đĩa từ đúng 3 nguồn (user, project,
  plugin đang bật — gộp `enabledPlugins` 3 tầng settings, chỉ đọc `installPath`, bỏ entry
  `scope: project` của project khác, cấm quét cache). Luôn in 2 dòng nhắc chép thêm skill
  built-in (thứ không tồn tại trên đĩa). Log service qua `TDQ_LOG`.
- **Bước B0 ở `tdq-intake`**: kiểm kê năng lực trước khi đọc code; bảng phán quyết
  (khuôn ở `references/skill-inventory.md`) lưu vào `knowledge/<slug>.md`. Quy tắc máy
  chạy được: xét 100% bắt buộc · loại chỉ bằng 4 lý do đóng · **phân vân → DÙNG**.
  Lane quick: mini-plan bắt buộc có dòng `Năng lực:`.
- **Spec §3b "Năng lực & công cụ"** (bảng phán quyết `DÙNG/KHÔNG/NỀN`) trong khuôn spec.
- **Hợp đồng skill 6 trường trong plan** (`Dùng/Nạp/Để/Ra/Kiểm/Không dùng cho`): mỗi dòng
  `DÙNG` ở spec phải nở thành khối hợp đồng ở mức task — không còn "ghi tên rồi implement mù".
  `tdq-build` nạp skill theo trường `Nạp` TRƯỚC bước đỏ; QC chạy trường `Kiểm` thật.
- **`doc_lint.py` rule R8** (spec phải có §3b hợp lệ; file trong `spec/` chỉ chịu R8) và
  **`doc_lint.py --pair <spec> <plan>`** (đối chiếu hợp đồng, thiếu trường nào nêu tên
  trường đó). 4 spec cũ miễn trừ bằng `<!-- doc-lint: allow R8 -->`.
- `PHASE_TABLE`: checklist `analyze` + `quick` nhắc bước kiểm kê; `phases.md` sinh lại.
- Portable đồng bộ: agent ngoài không có skill system → xét công cụ tương đương như skill,
  dòng `DÙNG` ghi thêm `tương đương: <cách làm>`.

## 0.3.2 — 2026-07-29

Audit 0.3.1 phát hiện chính vân tay repo lại đẻ ra một kiểu chặn oan mới, nặng hơn
lỗi mà 0.3.1 vá. Bản này sửa hết.

### Sửa
- **Turn read-only không còn bị chặn.** 0.3.1 so vân tay TOÀN repo nhưng chỉ loại
  trừ `docs/tdq/` lúc đặt tên file, nên chính việc hook append sổ turn sau khi chụp
  ảnh đầu turn cũng làm vân tay đổi → mọi file bẩn có sẵn bị lôi ra làm vật tế thần,
  kể cả trong turn chỉ đọc hoặc chỉ ghi state. Nay `docs/tdq/` và `docs/workinglog/`
  bị loại trừ ngay từ **pathspec của git**, dùng chung cho cả quyết định lẫn đặt tên.
- **`touch` file untracked không còn bị chặn**: file untracked ≤256 KB được lấy dấu
  bằng **nội dung** thay vì `size:mtime` (ngân sách đọc 4 MB mỗi lần lấy vân tay).
- **Windows**: tiền tố vùng loại trừ viết bằng `/` cứng — dùng `os.path.join` thì
  thành `docs\tdq` và bộ lọc im lặng ngừng hoạt động.
- `stop_gate` lấy dòng `turn_start` **mới nhất** thay vì dòng đầu tiên: sổ turn còn
  sót dòng của turn trước thì mốc so sánh có thể cũ tới 6 giờ.
- Trần số file untracked lấy dấu đếm đúng **số file** (trước đây cắt theo số dòng
  `git status`); danh sách path đầu turn nâng trần 100 → 400.
- Path file untracked được stat theo **gốc repo**, không theo cwd (porcelain in path
  theo gốc) — chạy workflow từ thư mục con không còn bỏ lọt.

### Thêm
- Log service cho hook (§6): `git` timeout / không chạy được → ghi cảnh báo kèm
  timestamp ra stderr; mỗi quyết định chặn ghi rõ nguồn bằng chứng và path. Tắt bằng
  `TDQ_LOG=0`.

## 0.3.1 — 2026-07-29

Vá điểm mù của verify-by-effect: sổ turn chỉ thấy hành động đi qua tool Edit/Write,
nên mọi thay đổi qua shell đều vô hình với nó.

### Sửa
- **Hết chặn oan `[TDQ:LOG]`**: append working log bằng `cat >>`, `tee`, `sed -i`,
  heredoc… giờ được công nhận. Trước đây chỉ tool Edit/Write mới ghi được `log_written`,
  nên turn hợp lệ vẫn bị Stop chặn.
- **Hết bỏ lọt chiều ngược lại**: sửa repo hoàn toàn bằng shell (không qua Edit) trước
  đây không sinh `observe edit` nên Stop im lặng dù chưa ghi log; nay vẫn bị đòi.

### Thêm
- `tdq_state.py`: `today_log_rel()`, `repo_status_digest()`, `repo_status_paths()`,
  `turn_snapshot()` — vân tay gồm cả `git status --porcelain -uall` lẫn `git diff HEAD`
  (porcelain không đổi khi sửa tiếp một file vốn đã `M`).
- `prompt_context` ghi một dòng `turn_start` vào sổ turn (không in ra context, không
  tốn token của model); `stop_gate` so lại lúc kết turn.

### Ghi chú
- Không có dòng `turn_start`, project không phải git repo, hoặc `git` lỗi/timeout 2 s →
  rơi về đúng hành vi 0.3.0.
- Thay đổi trong `docs/tdq/` (state, sổ turn) không tính là "đổi repo".
- `bash_gate.py` **không** đổi: cố đoán lệnh shell bằng regex vừa không đủ vừa dễ cấp
  bằng chứng giả.

## 0.3.0 — 2026-07-29

Mục tiêu: bộ instruction đủ chi tiết để **model nhỏ chạy local** cũng đi đúng workflow,
và hook chuyển hẳn sang vai "nhắc + kiểm bằng hiệu ứng thật".

### Thêm
- **Ledger mỗi turn** `docs/tdq/.tdq-turn.jsonl`: hook ghi dòng `remind` (đã nhắc mã nào)
  và `observe` (hiệu ứng thật: sửa file, ghi log, gọi CLI state). `stop_gate` đối chiếu
  hai bên — agent in `✓` mà không có hiệu ứng thật thì không qua được.
- **5 mã nhắc đóng**: `TDQ:NEXT`, `TDQ:APPROVE`, `TDQ:LOG`, `TDQ:STATE`, `TDQ:GIT`
  (1 lần/mã/turn).
- `tdq_state.py next [--brief]` — trả lời "giờ làm gì" theo phase, kèm checklist.
- `tdq_state.py phases-doc` — **sinh** `references/phases.md` từ hằng `PHASE_TABLE`;
  doc phase không còn viết tay, có test khoá đồng bộ.
- `scripts/doc_lint.py` (R1–R7): bước đánh số liên tục, lệnh copy-paste được, có
  `Xong khi:`/`Bước kế tiếp:`, cấm từ mơ hồ, câu ≤ 40 từ, trần độ dài, bắt buộc link
  mẫu output.
- **Bản portable** `portable/AGENTS.md` + `portable/workflow/` cho agent ngoài Claude Code,
  có test chống lệch bước so với skills.
- Test mới: `test_doc_lint`, `test_token_budget`, `test_portable_sync`,
  `test_skill_shape`, `test_hook_resilience`, `test_docs_consistency`.

### Đổi
- **Skill 10 → 6.** Bảng ánh xạ:

  | Cũ | Mới |
  |---|---|
  | `tdq-start`, `tdq-analyze` | `tdq-intake` |
  | `tdq-implement`, `tdq-qc`, `tdq-report` | `tdq-build` |
  | `tdq-approve` | bỏ hẳn — duyệt bằng chat thường |
  | `tdq-spec`, `tdq-plan`, `tdq-status`, `tdq-conventions` | giữ tên, viết lại theo dạng bước đánh số |

- Thân skill gọn lại, chi tiết đẩy sang `references/` (chỉ nạp khi cần).
- State schema v3: thêm `implement_mode`, `*_approved_by`, `previous_request`;
  mirror `docs/tdq/STATE.md` tự sinh để đọc.
- Ngân sách token có test đo thật (SessionStart ≤ 12 dòng/600 ký tự, UserPromptSubmit
  ≤ 3/240, PreToolUse ≤ 3/200, Stop ≤ 4/300, STATE.md ≤ 30 dòng, `next` ≤ 20 dòng).
- Exit code của CLI: mọi trục trặc state là cảnh báo (exit 0); exit 2 chỉ khi sai cú pháp.
- `docs/tdq/state.json` không còn bị `.gitignore`; thay bằng `docs/tdq/.tdq-turn.jsonl`.
- Doc v0.1 chuyển vào `docs/archive/v0.1/`.

### Bỏ
- Skill `tdq-approve` và mọi gate chặn tool vì lý do "chưa duyệt".
- Hook không còn đọc transcript và không còn trả `deny`.

## 0.2.0 — 2026-07-28

- Chuyển gate duyệt từ **chặn** sang **nhắc**: chưa duyệt mà sửa file ngoài `docs/` thì
  hook đính lời nhắc vào ngữ cảnh thay vì từ chối tool.
- Duyệt bằng chat thường; state lưu nguyên văn câu user duyệt.
- Điểm chặn duy nhất còn lại: chưa append working log thì không kết thúc turn được.
- Lưu sha256 của spec lúc duyệt để phát hiện spec trôi sau khi duyệt.

## 0.1.6 — 2026-07-28

- `implement_mode` do **user** quyết; nới nhận diện dòng mode lúc duyệt.

## 0.1.4 — 2026-07-28

- Siết gate duyệt: chỉ user được gõ lệnh approve, agent không được đụng `state.json`.

## 0.1.0 — 2026-07-27

- Bản đầu: 10 skill, 6 hook, 3 agent, 49 test.
