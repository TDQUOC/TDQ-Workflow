# PLAN — Audit tổng thể TDQ workflow 0.6.0 — HOÀN THÀNH

Ngày: 2026-07-31 · Spec: ../spec/2026-07-31-audit-full-workflow.md (bản 1.1, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — audit đụng chéo nhiều file khung, findings→fix phụ thuộc chặt; sample E2E tự gọi agent/engine song song bên trong.
Trạng thái plan: ĐÃ DUYỆT (user "duyệt plan mode main", 2026-07-31 17:51 +07)

## Năng lực → task

| Skill | Task | Đầu ra bắt buộc |
|---|---|---|
| tavily-best-practices | T2.1 | run-dir deep search mới với agent-2.json từ scout (Tavily) |
| graphify | T6.2 | `graphify extract . --code-only` chạy xong sau khi code đổi |

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo; T2.x khởi động NGAY đầu build (chạy nền song song với P1/P3) vì wall-clock là rủi ro chính của spec §5. Ngân sách cứng: S1 ≤ 30 phút, run deep search ≤ 25 phút — quá ngân sách → ghi finding, chuyển nhánh degrade/fallback theo luật sẵn có rồi đi tiếp.
2. Mỗi task: viết test/check trước (đỏ) → làm → xanh → tick `[x]` NGAY vào file này.
3. Gate suite-xanh-giữa-phase chỉ áp cho phase đổi code (P1, P4). P2/P3 chạy song song, miễn gate tuần tự; điều kiện chung: suite toàn phần xanh TRƯỚC khi vào P5.
4. Lệnh nào chạm state của workflow trong sample phải có `TDQ_PROJECT_DIR=<sandbox>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục `## QC vòng N — fix` (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. Findings ghi tập trung vào `docs/tdq/qc/2026-07-31-audit-full-workflow.md` mục Findings, format: `A<n> · <note> · nguyên nhân · S/M/L · trạng thái (fixed/T<x.y> | noted)`.

## P1 — Fix issue đã biết + khung sổ findings

- [x] **T1.1** Fix regex `r'`\\1`'` → `r'`\1`'` tại `scripts/tdq_state.py:576` — Test: test mới trong `tests/test_phase_table.py` assert output `phases-doc` không chứa literal `` `\1` `` VÀ 3 mục analyze/spec/plan chứa lệnh `python3 scripts/tdq_state.py` thật (đỏ trước fix, xanh sau)
- [x] **T1.2** Regenerate `skills/tdq-conventions/references/phases.md` + `portable/workflow/phases.md` bằng `phases-doc` — Test: `python3 scripts/tdq_state.py phases-doc | diff - skills/tdq-conventions/references/phases.md` exit 0; portable sync test trong suite xanh
- [x] **T1.3** Tạo khung `docs/tdq/qc/2026-07-31-audit-full-workflow.md` với mục Findings + ghi A1 (bug `\1`, nguyên nhân escape trong raw string, S, fixed/T1.1) — Test: `doc_lint.py` file qc exit 0; A1 đủ 4 trường

**Xong P1 khi**: suite toàn phần xanh, phases.md hết `\1`, sổ findings đã có A1.

## P2 — Hai việc chạy dài: deep search + S1 (khởi động NGAY đầu build, chạy nền)

- [x] **T2.1** Chạy 1 run deep search hybrid mới (đề tài thật, khác vectordb): slot 2 gọi qua Agent type `tdq-workflow:search-scout`, các slot agy qua `search-runner` — Test: run-dir mới đủ brief/brief-phase2/agent-*.json/merged.json/report.md; agent-2.json đúng format file agent
  - Dùng: `tavily-best-practices`
  - Nạp: gọi skill `tavily:tavily-best-practices` TRƯỚC khi launch scout (nếu turn build chưa nạp); scout là subagent, tự dùng tool tavily-primary theo agent def của nó.
  - Để: slot scout search rộng qua Tavily đúng luật layered (search → extract khi cần).
  - Ra: `docs/tdq/research/search/<run-id>/agent-2.json` ≥5 findings có URL.
  - Kiểm: `python3 -c "import json;d=json.load(open('<run-dir>/agent-2.json'));print(d['agent']==2, len(d['findings'])>=5)"` → `True True`.
  - Không dùng cho: các slot agy (1,3..) — chúng đi qua wrapper `search_task.py`, không gọi Tavily.
- [x] **T2.2** Ghi bảng token mọi slot thực chạy của T2.1 từ `<usage>` vào sổ findings + kết luận Q7 (≤250k) và Q8 (trigger scout) — Test: bảng có đủ mọi slot; tổng số học đúng; nếu >250k → mở task fix QC-loop
- [x] **T2.3** Dựng sandbox S1: git repo tạm trong scratchpad + project con có bug nhỏ thật (1 file python + 1 test fail) — Test: `git -C <sandbox> status` sạch; test con chạy fail đúng như cài
- [x] **T2.4** Chạy S1 quick external trọn vòng trong sandbox, `TDQ_PROJECT_DIR` trên từng lệnh state. Chuỗi: init → mini-plan → approve quick external (duyệt giả lập trong sandbox, như T4.1) → worktree `tdq-ext-<slug>` → gói task → agy-runner model `gpt-oss-120b-medium` (fallback `gemini-3.5-flash-low`) → verify → diff-check → merge — Test: chuỗi state đi đúng (`next` từng bước); test con pass sau merge; report JSON `validate_report()` in `[]`
- [x] **T2.5** Ghi findings S1 vào sổ: robustness contract với model thấp (task packet đủ tường minh? engine làm sai gì? fallback có kích hoạt đúng luật?) — Test: mỗi finding đủ 4 trường; phân loại rõ lỗi CONTRACT vs lỗi NĂNG LỰC model

**Xong P2 khi**: run-dir + bảng token + kết luận Q7/Q8 xong; S1 chạy hết vòng, findings đã ghi; sandbox S1 đã xoá sau khi trích bằng chứng.

## P3 — Review tĩnh chéo (chạy song song lúc chờ P2)

- [x] **T3.1** Review 6 SKILL.md + 13 references + CLAUDE.md §10 + portable/. Soi: mâu thuẫn luật; khoảng trống phase; chỗ dựa "model tự nhớ" thay vì máy ép; câu lệnh thiếu hoặc khó copy cho model thấp — Test: mục Findings có kết quả rà từng file (kể cả dòng "OK không issue"); mọi issue có trích dẫn file:dòng
- [x] **T3.2** Review 7 agent def theo trục MAST + trục model thấp (vai trò đơn trị? format output tường minh? có đường degrade?) — Test: như T3.1, đủ 7 agent
- [x] **T3.3** Review 7 script + 5 hook + `_common.py` + hooks.json + 2 sample script: exit code, nhánh lỗi, race/đường dẫn, thông điệp hook có kèm lệnh copy được không — Test: như T3.1, đủ danh sách file
- [x] **T3.4** Chốt danh sách issue S/M từ T3.1–T3.3 thành task fix cụ thể, append vào P4 — Test: mỗi issue S/M có đúng 1 task fix trong P4 với test riêng

**Xong P3 khi**: sổ findings phủ 100% danh sách file lớp 1; danh sách task fix P4 đã chốt.

## P4 — Sample S2 + fix issue S/M

- [x] **T4.1** Dựng sandbox S2 (git repo tạm riêng) và chạy full mini mode main: init full→analyze→spec→duyệt giả lập bằng chuỗi user thật→plan→duyệt→implement 1 task nhỏ→qc→report→idle — Test: chuỗi `next`/`approve` từng phase đúng bảng phase; các file docs/tdq/* sinh đủ trong sandbox
- [x] **T4.2** S2 nhánh sự cố 1 — approve mơ hồ: thử `approve spec --by "ok nhé"` và các câu KHÔNG phải duyệt theo `approval.md` — Test: đối chiếu hành vi với luật. Script vốn ghi mọi lần bị gọi (luật chặn nằm ở tầng skill); tầng máy không chặn được → ghi finding, kèm đánh giá tầng skill đủ rõ cho model thấp chưa
- [x] **T4.3** S2 nhánh sự cố 2 — init đè request dở: init request mới khi phase đang implement — Test: cảnh báo ghi-đè xuất hiện đúng; state cũ lưu vào `previous_request`
- [x] **T4.4** S2 nhánh sự cố 3 — engine hỏng → fallback: gói 1 task external trong sandbox với model slug sai, chạy với `TDQ_EXTERNAL_TIMEOUT=60` để không phá ngân sách wall-clock — Test: `external_task.py run` exit ≠0 sau retry; đường fallback Claude-tự-làm được ghi nhận finding đúng luật tdq-build
- [x] **T4.5** Fix các issue S/M đã chốt ở T3.4 VÀ từ findings E2E (T2.5, T4.2–T4.4). Danh sách task cụ thể append tại đây khi T3.4 xong — Test: mỗi fix có test riêng red→green; suite toàn phần xanh
  - [x] **T4.5.1** `scripts/tdq_state.py`: A6 (lane quick có terminal — phase=idle/report thì `phase_key` không trả "quick" nữa) + A18 (`_row_age_ok` chịu ts số/thiếu, không crash) — Test: test mới trong `tests/test_phase_table.py` + test `_row_age_ok` với ts int/None
  - [x] **T4.5.2** `scripts/external_task.py`: A4 (persist raw stdout mỗi attempt fail vào `<task-id>.attempt<N>.raw.txt`) + A12 (feedback retry kèm trích stdout attempt trước). Thêm A13 (engine `--print-timeout` = wrapper timeout − 30s, sàn 30s) + A24 (report ghi atomic) — Test: mở rộng `tests/test_external_task.py` red→green
  - [x] **T4.5.3** `scripts/search_task.py`: A4-mở-rộng (persist raw khi validate fail) + A7 (split cảnh báo khi route chứa `;` hoặc số route ≠ kỳ vọng, doc separator). Thêm A14 (schema load bọc lỗi, message rõ) + A15 (merge in số file agent bỏ qua; TẤT CẢ hỏng → exit 1) + A16 (copy brief atomic) — Test: mở rộng `tests/test_search_task.py` red→green
  - [x] **T4.5.4** A17: `external_models.py` + `external_task.py` neo dir output/log theo project dir (dùng resolver kiểu `resolve_project_dir`, tôn trọng `TDQ_PROJECT_DIR`), hết rắc dir theo cwd — Test: chạy từ cwd tạm, dir sinh đúng chỗ project
  - [x] **T4.5.5** `scripts/doc_lint.py`: A19 (path không tồn tại → báo lỗi + exit ≠0) + A20 (message tử tế thay traceback) — Test: test mới lint path ma exit ≠0
  - [x] **T4.5.6** `scripts/skill_inventory.py`: A23 dùng chung resolver project dir — Test: chạy từ cwd tạm với `TDQ_PROJECT_DIR` trỏ repo, kết quả không rỗng
  - [x] **T4.5.7** Hook: A22 truncation không cắt giữa inline-code (cắt tại biên từ trước backtick mở) + A21 `plugin_tiers.py` tách `_warn` khỏi công tắc log — Test: unit test truncation; A21 kiểm bằng chạy tay lệnh sai với PLUGIN_TIERS_LOG=0 thấy warn ra stderr
  - [x] **T4.5.8** 4 agent def runner/scout: A5 (viết lại đoạn chờ theo cơ chế thật — Bash nền, bị đánh thức; bỏ watcher `sleep` và "never end early") + A9 (bảng exit code 0/1/2/3, hành xử từng mã). Thêm A10 (scout khi cả 2 tavily chết: vẫn ghi agent-2.json với `scout-failed`) — Test: grep từng def có/không còn cụm bắt buộc; PENDING reload
  - [x] **T4.5.9** A11: thêm `tools:` read-only vào frontmatter `tdq-qc-tester.md` + `tdq-reviewer.md` — Test: grep frontmatter có dòng `tools:` không chứa Edit/Write; PENDING reload
  - [x] **T4.5.10** Docs đồng bộ: A25 (CLAUDE.md §10 sửa thời điểm chốt engine+model) + A26/A40 (cập nhật PHASE_TABLE quick + generator in path plugin-root, regenerate 2 phases.md) + A27/A28 (deep-search.md path plugin-root + định nghĩa run-dir). Thêm A29 (qc.md: sửa §3b trong QC phải approve spec lại 1 dòng) + A30 (copy external-task.md sang portable) + A31 (bỏ plugin-root trong portable approval.md). Thêm A32 (README portable bổ sung 3 file external) + A35 (định nghĩa "model default = slug đầu list") + A36 (tdq-spec thêm lệnh doc_lint single-file) — Test: doc_lint mọi file sửa exit 0; portable sync test + phase-table test xanh; grep xác nhận từng điểm
- [x] **T4.6** Ghi findings S2 + trạng thái fix vào sổ; xoá sandbox S2 — Test: findings đủ 4 trường; sandbox không còn trên đĩa

**Xong P4 khi**: 3 nhánh sự cố có kết luận; mọi issue S/M ở trạng thái fixed; suite xanh.

## P5 — Log & test bắt buộc

- [x] **T5.1** Kiểm log service từ log THẬT đã có (run.log/agent-*.log của run T2.1 + external run.log của S1/T4.4): đủ trường, timestamp ISO. Nhánh tắt log KHÔNG chạy run mới — viện dẫn unit test sẵn có (`tests/test_search_task.py` nhánh `TDQ_SEARCH_LOG=0`, `tests/test_external_task.py` nhánh `TDQ_EXTERNAL_LOG=0`) làm bằng chứng Q9 — Test: grep trường bắt buộc trong log thật pass; 2 unit test viện dẫn nằm trong suite xanh
- [x] **T5.2** Chạy đủ bộ kiểm cuối: `python3 -m unittest discover -s tests` + `doc_lint.py` mọi file docs đã sửa + `--pair spec plan` — Test: suite OK ≥ 338 + số test mới; lint exit 0

**Xong P5 khi**: cả hai task xanh.

## P6 — QC, report, đóng sổ

- [x] **T6.1** Điền bảng QC Q1–Q10 (spec §6) vào `qc/<slug>.md` với bằng chứng lệnh+output thật — Test: 10 hạng mục đều PASS (hoặc mở QC-loop); doc_lint exit 0
- [x] **T6.2** Viết report ≤50 dòng + append working log + `graphify extract . --code-only` — Test: `wc -l` ≤50; doc_lint exit 0; graphify chạy xong
  - Dùng: `graphify`
  - Nạp: skill user `~/.claude/skills/graphify/SKILL.md` (đã biết cách chạy CLI).
  - Để: cập nhật code graph sau các fix code của request.
  - Ra: `graphify-out/` cập nhật (mtime mới hơn lúc bắt đầu turn).
  - Kiểm: `graphify extract . --code-only` exit 0.
  - Không dùng cho: viết nội dung report/QC (tay Claude viết).
- [x] **T6.3** Trình report trong chat + hỏi user có commit không; `set phase=idle` sau khi hỏi — Test: câu hỏi commit đã in; state phase=idle

**Xong P6 khi**: report trình xong, user đã được hỏi commit, phase=idle.

## Definition of Done

Theo spec §6: Q1 suite ≥338+mới OK · Q2 doc_lint + pair exit 0 · Q3 findings đủ 4
trường, S/M có task đã tick · Q4 `phases-doc | ! grep -q '\1'` + test xanh · Q5 S1
trọn vòng + `validate_report()` in `[]` · Q6 S2 + 3 nhánh sự cố đúng luật · Q7 token
mọi slot thực chạy ≤250k · Q8 trigger `search-scout` chạy, agent-2.json đúng format ·
Q9 log service bật mặc định + biến tắt hoạt động · Q10 report ≤50 dòng. Fix vào
skill/agent/hook đang chạy → verify runtime ghi "PENDING reload", không tính fail.
