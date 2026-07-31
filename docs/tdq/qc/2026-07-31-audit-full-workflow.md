# QC — 2026-07-31-audit-full-workflow

Sổ findings tập trung của audit (plan quy tắc 7). Format mỗi dòng:
`A<n> · <note> · nguyên nhân · S/M/L · trạng thái (fixed/T<x.y> | noted)`.

## Findings

- A1 · phases-doc sinh literal backslash-1 thay vì lệnh thật ở 3 mục analyze/spec/plan (`skills/tdq-conventions/references/phases.md:40,48,56`) · replacement của `re.sub` tại `scripts/tdq_state.py:576` dùng raw string có escape thừa nên group reference thành text · S · fixed/T1.1
- A2 · phases-doc wrap đôi backtick khi item checklist đã tự chứa inline-code (mục analyze dòng 1) · `re.sub` wrap vô điều kiện mọi item khớp pattern `python3 .+` kể cả item đã có backtick · S · fixed/T1.1

## Bảng token deep search (T2.2)

Run `2026-07-31-local-llm-engine` (đề tài: LLM local ≤14B làm engine code-agent),
đủ 2 phase, không degrade, `routes_failed=[]`, merge 1 lần ra 34 findings.
Token đo từ `<usage>` subagent_tokens của TỪNG slot thực chạy:

| Slot | Agent type | Việc | Token |
|---|---|---|---|
| 1 | tdq-workflow:search-runner | phase 1 tổng quát (agy) | 11.702 |
| 2 | tdq-workflow:search-scout | phase 1 scout (Claude+Tavily) | 81.230 |
| 3 | tdq-workflow:search-runner | phase 2 Qwen3/Phi-4 | 11.736 |
| 4 | tdq-workflow:search-runner | phase 2 constrained decoding | 11.759 |
| 5 | tdq-workflow:search-runner | phase 2 runtime Apple Silicon | 11.699 |
| **Tổng** | | | **128.126** |

- **Q7 PASS**: 128.126 ≤ 250.000 (đủ mọi slot; slot agy nhẹ vì agy chạy ngoài,
  khớp tiền lệ 0.5.0).
- **Q8 PASS**: slot 2 gọi qua Agent type `tdq-workflow:search-scout` thành công
  (phiên mới sau reload), `agent-2.json` đúng format file agent: agent==2,
  13 findings có URL + `url_alive`, đủ khoá routes/routes_failed/not_found/queries_used.
- Ghi chú vận hành: route agent 1 chứa dấu phẩy bị wrapper tách thành 3 route
  (xem A7); không gây fail run này.

## Findings S1 — quick external model thấp (T2.5)

Vòng chạy: init quick → mini-plan (working log sandbox) → approve quick mode
external → worktree tdq-ext-s1-fix-percent → gói task T1 → agy `gpt-oss-120b-medium`
→ hỏng → fallback `gemini-3.5-flash-low` → verify → merge → idle. Bằng chứng:
run.log + T1.json lưu tại scratchpad `evidence-s1/` (sandbox đã xoá).

- A3 · `gpt-oss-120b-medium` hỏng 3/3 attempt, validate FAIL "trường response không phải JSON"; `gemini-3.5-flash-low` cùng gói task pass ngay attempt 1, test 2/2 pass sau merge · lỗi NĂNG LỰC model (gói task đủ tường minh — model thấp hơn một bậc pass ngay); chuỗi retry→fallback hoạt động đúng luật · M · noted
- A4 · khi validate FAIL, wrapper không lưu raw output engine — dir external chỉ có task packet + run.log, không xem được model đã trả gì để sửa prompt · `external_task.py` chỉ ghi 1 dòng log validate=FAIL, không persist attempt output · M · fixed/T4.5 (lỗi CONTRACT — thiếu artifact debug)
- A5 · agy-runner 2/2 lần kết thúc turn khi wrapper còn chạy, sinh notification đôi, trái câu "never end early" trong def · contract agent def viết theo cơ chế poll không tồn tại trong harness (foreground sleep bị chặn; cơ chế thật: background Bash xong → agent được đánh thức) · M · fixed/T4.5 (lỗi CONTRACT)
- A6 · sau khi quick xong và `set phase=idle`, lệnh `next` vẫn hiện checklist quick — model thấp sẽ tưởng còn việc và lặp mini-plan · `phase_key` trả "quick" vô điều kiện khi lane=quick (`scripts/tdq_state.py:588`) · M · fixed/T4.5 (lỗi CONTRACT — state machine thiếu terminal cho lane quick)
- A7 · `--routes` split theo dấu phẩy không escape, không cảnh báo: route chứa phẩy bị tách làm 3 (agent 1 run này); dùng separator `;` lại thành 1 route (lần split đầu phase 2) · contract separator ngầm trong `search_task.py`, `deep-search.md` không nói · M · fixed/T4.5 (lỗi CONTRACT)
- A8 · worktree external sau verify chứa `__pycache__/` untracked làm diff-check porcelain nhiễu · engine/orchestrator chạy test sinh artifact Python · L · noted

## Review tĩnh lớp 1 (T3.1–T3.3)

### T3.2 — 7 agent def (candidates từ reviewer phụ, đã tự xác minh exit code + frontmatter)

- `agents/agy-runner.md`: ISSUE A5, A9
- `agents/codex-runner.md`: ISSUE A5, A9
- `agents/search-runner.md`: ISSUE A5, A9
- `agents/search-scout.md`: ISSUE A10
- `agents/tdq-implementer.md`: OK không issue
- `agents/tdq-qc-tester.md`: ISSUE A11
- `agents/tdq-reviewer.md`: ISSUE A11

(A5 mở rộng: áp cả 3 runner def — codex-runner.md:13,21 trùng nguyên văn agy-runner;
search-runner.md:14-16,26 còn watcher `sleep` bị harness chặn + 2 câu khẳng định
sai về cơ chế background/notification.)

- A9 · 3 runner def gộp mọi exit ≠ 0 thành `engine-failed` trong khi wrapper phân biệt exit 2 = sai cú pháp lệnh (`scripts/external_task.py:271-280`, `scripts/search_task.py:330-345`) và 3 = preflight fail (search) — agent gõ sai lệnh cũng bị orchestrator degrade oan · def viết thiếu nhánh exit code · M · fixed/T4.5
- A10 · search-scout không có đường lỗi khi CẢ tavily-primary lẫn backup chết: def chỉ định nghĩa `not_found` cho kết quả rỗng (`agents/search-scout.md:12`). Không nói có ghi agent-2.json không và trả marker gì — model thấp dễ trả tự do làm orchestrator không parse được · thiếu contract nhánh lỗi tool · M · fixed/T4.5
- A11 · tdq-qc-tester và tdq-reviewer cấm sửa file chỉ bằng lời dặn ("Never fix anything" / "Do NOT edit any file") nhưng frontmatter không có `tools:` → agent nhận All tools kể cả Edit/Write. Plugin đã có tiền lệ enforce bằng frontmatter (`agents/search-runner.md:4`) · ràng buộc dựa "model tự nhớ" thay vì máy ép · S · fixed/T4.5

### T3.3 — 7 script (candidates từ reviewer phụ, đã tự xác minh từng dòng trích dẫn)

- `scripts/tdq_state.py`: ISSUE A18, A24 (A1/A2/A6 đã ghi ở trên)
- `scripts/external_task.py`: ISSUE A12, A13, A16, A24 (A4 mở rộng)
- `scripts/search_task.py`: ISSUE A14, A15, A16, A17 (A4 mở rộng, A7 đã ghi)
- `scripts/external_models.py`: ISSUE A17
- `scripts/doc_lint.py`: ISSUE A19, A20
- `scripts/skill_inventory.py`: ISSUE A23
- `~/.claude/scripts/plugin_tiers.py`: ISSUE A21

Bằng chứng đã tự chạy: A18 tái hiện crash thật `TypeError: fromisoformat: argument
must be str` khi gọi `_row_age_ok({'ts': 123})`; A19 chạy doc_lint với path không
tồn tại → exit 0; A22 xác nhận hằng MAX_CHARS=240 + cắt chuỗi tại dòng 104-105.

- A12 · retry attempt sau chỉ được feed message lỗi (`## LỖI LẦN TRƯỚC`), không kèm trích stdout attempt trước — model thấp không biết mình đã trả sai chỗ nào · `external_task.py:176` chỉ nối `last_error` vào prompt · M · fixed/T4.5
- A13 · wrapper timeout == engine `--print-timeout` (cùng giá trị, `external_task.py:128,183`) → race: engine bị kill đúng lúc đang in report; process con engine có thể mồ côi sau TimeoutExpired · hai timeout không so le, không cleanup process group · M · fixed/T4.5
- A14 · schema load ở module-level không bọc try (`search_task.py:93-94`) → thiếu/hỏng file schema là traceback thô ngay khi import, mọi subcommand chết kể cả `--help` · thiếu guard tải tài nguyên · M · fixed/T4.5
- A15 · `merge` nuốt mọi file agent hỏng qua except rộng (`search_task.py:534-539`) → TẤT CẢ agent hỏng vẫn exit 0 với merged rỗng, orchestrator tưởng run thành công · except không đếm/không báo số file bỏ qua · M · fixed/T4.5
- A16 · copy brief vào run-dir kiểu check-rồi-copy không atomic (`search_task.py:348-351`) · TOCTOU giữa exists() và copy · S · fixed/T4.5
- A17 · `external_models.py:47,81` và `external_task.py:73,169` tạo dir `docs/tdq/external/` + log tại `os.getcwd()` — chạy từ cwd lạ (worktree, home) là rắc dir rác sai chỗ · path neo theo cwd thay vì project dir · M · fixed/T4.5
- A18 · `_row_age_ok` crash `TypeError` khi `ts` là số (epoch) → kéo chết 4 hook đọc state · `fromisoformat` nhận thẳng giá trị không kiểm type · M · fixed/T4.5
- A19 · doc_lint nhận path không tồn tại → bỏ qua im lặng, exit 0 — CI/QC tưởng lint pass trong khi chưa lint gì · vòng lặp file skip path thiếu mà không set fail · M · fixed/T4.5
- A20 · `Doc.__init__` mở file không bọc lỗi → FileNotFoundError traceback thô thay vì message lint tử tế · thiếu handle IO · S · fixed/T4.5
- A21 · plugin_tiers khi PLUGIN_TIERS_LOG=0 thì `_warn` cũng câm (gate chung `_log_on()`) → lỗi thật bị nuốt không dấu vết · warn và log info chung một công tắc · M · fixed/T4.5
- A22 · hook approve cắt dòng ở MAX_CHARS=240 giữa chừng lệnh → model thấp copy lệnh cụt · truncation không tránh vùng inline-code · M · fixed/T4.5
- A23 · skill_inventory dùng `os.getcwd()` (`:144`) thay vì resolve_project_dir như tdq_state — chạy ngoài project ra kết quả rỗng lệch · không tái dùng resolver sẵn có · S · fixed/T4.5
- A24 · ghi report/state kiểu open-write thường (`external_task.py:210-211`) trong khi codebase đã có mẫu `_atomic_write` (`tdq_state.py:205`) → crash giữa chừng để lại JSON cụt · không dùng atomic write sẵn có · S · fixed/T4.5
- (A4 mở rộng: `search_task.py` cùng lỗi không persist raw stdout khi validate FAIL — fix chung một task với external_task.)

### T3.1 — skills + references + portable + CLAUDE.md §10 (candidates từ reviewer phụ, đã tự xác minh 10/10 điểm S/M bằng grep/sed dòng trích dẫn)

Per-file: tdq-intake (A34-ghi-chú, A35), tdq-spec + spec-template (A36), tdq-plan
(A25, ghi chú antigravity→agy), tdq-build (ghi chú graphify), tdq-status (ghi chú
mode). Tiếp: deep-search.md (A27, A28), phases.md cả 2 bản (A26, A40), qc.md cả 2
bản (A29). Portable: AGENTS.md + reminder-codes.md (ghi chú orphan), README.md
(A32), approval.md (A31), 04-build.md (A30), 02-spec.md vs spec-template (ghi
chú). Các file còn lại: OK không issue.

- A25 · thời điểm chốt engine+model mâu thuẫn: CLAUDE.md §10 nói "chốt lúc duyệt", tdq-plan SKILL bắt chốt TRƯỚC khi viết plan (`skills/tdq-plan/SKILL.md:20`) · hai doc cùng thẩm quyền nói hai thời điểm · M · fixed/T4.5
- A26 · dòng in duyệt quick lệch nhau: intake có vế "(giao engine ngoài: \"duyệt quick external\")", bảng phases quick không có (`skills/tdq-intake/SKILL.md:84` vs `phases.md:81` cả 2 bản) · PHASE_TABLE chưa cập nhật theo intake · M · fixed/T4.5
- A27 · deep-search.md dùng path tương đối `scripts/search_task.py` ở 3 chỗ (`:56,:60,:84`) trong khi mọi lệnh skill khác dùn prefix plugin-root — plugin cài ngoài project copy-paste fail · path không nhất quán · M · fixed/T4.5
- A28 · deep-search.md bắt "lưu brief vào run-dir" nhưng không định nghĩa run-dir ở đâu (bản portable và search-runner.md có) · thiếu 1 dòng định nghĩa · M · fixed/T4.5
- A29 · qc.md bước 6 bắt sửa spec §3b ĐÃ DUYỆT → lệch `spec_sha256` → hook + tdq-status lập tức đòi duyệt lại: làm đúng QC thì tự kích kẹt duyệt · quy trình QC không tính drift-check · S · fixed/T4.5
- A30 · portable 04-build.md tham chiếu `references/external-task.md` nhưng file KHÔNG tồn tại trong portable — mode external portable không có schema report · thiếu file khi sync portable · S · fixed/T4.5
- A31 · portable approval.md:37 còn `${CLAUDE_PLUGIN_ROOT}` — harness ngoài không có biến này, lệnh nở thành path sai · sót khi port · M · fixed/T4.5
- A32 · portable README bước copy thiếu `external_task.py`, `external_models.py`, `external_report_schema.json` mà 03-plan/04-build cần · danh sách copy không cập nhật theo mode external · M · fixed/T4.5
- A35 · quick external nói "model default lấy từ lệnh list" nhưng `external_models.py list` chỉ in slug trần, không đánh dấu default · khái niệm default không định nghĩa · M · fixed/T4.5
- A36 · spec skill tuyên bố "máy kiểm bằng doc_lint R8" nhưng quy trình spec không có LỆNH lint nào chạy được (chỉ phase plan có `--pair`) · thiếu bước chạy lint single-file · M · fixed/T4.5
- A40 · khối "Lệnh nguyên văn" trong phases.md (bản skills) in path tương đối, mâu thuẫn conventions §1 bắt dùng plugin-root — bản copy-được lại là bản sai path · generator phases-doc không nhận prefix · M · fixed/T4.5
- Ghi nhận L (noted, không fix đợt này): reminder-codes.md orphan trong portable mâu thuẫn "KHÔNG có hook" (A33) · intake dòng 33 lệnh bị tỉnh lược "..." (A34) · graphify không ghi lệnh cụ thể trong tdq-build (A37) · mapping antigravity→agy không tường minh (A38) · portable spec-template thiếu ghi chú "tương đương:" (A39) · tdq-status in dòng duyệt plan thiếu vế mode (A41).

## Findings S2 — full mini + 3 nhánh sự cố (T4.1–T4.4)

Sandbox git riêng tại scratchpad `s2-sandbox` (đã xoá sau T4.6). Vòng chạy T4.1:
init full → analyze → spec → approve spec → plan → approve plan mode main →
implement 1 task → qc → report → idle; chuỗi `next`/`approve` từng phase khớp
bảng phase, docs/tdq/* sinh đủ trong sandbox. Ba nhánh sự cố:

- A42 · T4.2: tầng MÁY chấp nhận `approve spec --by "ok nhé"` — script ghi state vô điều kiện, không phán xét ngôn ngữ · thiết kế chủ đích: luật nhận diện câu duyệt nằm ở tầng skill (`approval.md` có bảng phản ví dụ tường minh, đủ rõ cho model thấp; máy chỉ lưu vết `--by` để đối chiếu) · M · noted (đúng thiết kế, đã đánh giá rào tầng skill đủ)
- A43 · T4.3: init request mới khi phase đang implement → cảnh báo ghi-đè in đúng, state cũ lưu vào `previous_request` — guard hoạt động đúng thiết kế · không có lỗi · L · pass
- A44 · T4.4: model slug sai (`model-khong-ton-tai`) → `external_task.py run` hỏng 3/3 attempt, exit 1, validate FAIL "trường response không phải JSON" (run.log 18:18:13→18:18:44, TDQ_EXTERNAL_TIMEOUT=60), đường fallback Claude-tự-làm ghi nhận đúng luật tdq-build · chuỗi retry→exit 1→fallback đúng contract; điểm yếu debug (không lưu raw output) chính là A4 · M · pass (fix debug-artifact theo A4/A12 tại T4.5, verify bằng unit test external_task)

---

## Bảng QC Q1–Q10 (T6.1)

| Q | Kết quả | Bằng chứng (lệnh + output thật) |
|---|---|---|
| Q1 | PASS | `python3 -m unittest discover -s tests` → `Ran 367 tests ... OK` (≥ 338 + test mới) |
| Q2 | PASS | `doc_lint.py` 20 file docs đã sửa (skills, portable, agents, CLAUDE.md, spec/plan/qc) → exit 0; `--pair spec plan` → exit 0 |
| Q3 | PASS | tally 4 trường: 24 `M·fixed` + 9 `S·fixed` + 2 `M·noted` (A3 năng lực model, A42 by-design có đánh giá rào) + 1 `M·pass` (A44); mọi S/M có task fix T4.5.x đã tick |
| Q4 | PASS | `phases-doc \| grep -c '\\1'` → 0 (không còn literal `\1`); test_phase_table xanh trong suite |
| Q5 | PASS | evidence-s1/run.log 5 dòng đủ trường; `validate_report(T1.json)` → `[]`; kết luận contract-vs-năng-lực tại A3 (model thấp hơn 1 bậc pass ngay attempt 1) |
| Q6 | PASS | S2: chuỗi init→…→idle khớp bảng phase; 3 nhánh sự cố A42/A43/A44 đúng luật (mục Findings S2) |
| Q7 | PASS | run `2026-07-31-local-llm-engine`: tổng token 5 slot = 128.126 ≤ 250.000 (bảng T2.2) |
| Q8 | PASS | slot 2 gọi qua Agent type `tdq-workflow:search-scout`; agent-2.json đúng format (13 findings, url_alive, đủ khoá) |
| Q9 | PASS | run.log deep-search: 50 dòng ISO, 24 dòng call đủ trường agent/route/attempt/model/exit/secs, 4 dòng summary đủ trường; evidence-s1 5/5 đủ trường; nhánh tắt log: `tests/test_search_task.py:530` (`TDQ_SEARCH_LOG=0`) + `tests/test_external_task.py:303` (`TDQ_EXTERNAL_LOG=0`) nằm trong suite xanh |
| Q10 | PASS | `wc -l docs/tdq/reports/2026-07-31-audit-full-workflow.md` → 41 ≤ 50; doc_lint exit 0 |

Ghi chú vận hành: T4.5.8/T4.5.9 sửa agent def (runner/scout/qc-tester/reviewer) —
hiệu lực đầy đủ sau khi reload plugin ở phiên mới.
