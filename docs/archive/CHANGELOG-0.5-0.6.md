# Changelog lưu trữ — 0.5.0 → 0.6.2

Tách khỏi `CHANGELOG.md` ngày 2026-08-14 để file chính giữ trong trần 500 dòng của `doc_lint` R6.

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
