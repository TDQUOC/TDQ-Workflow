# Report — 2026-07-31-agy-search-agent

Deep search agent qua agy CLI, tích hợp TDQ workflow, chịu được model cấp thấp.
Lane full, mode main, hoàn thành 2026-07-31.

## Đã làm
- `scripts/search_task.py` (split/run/merge): mọi logic dễ hỏng nằm trong code.
  Gồm: cap song song, chia route round-robin, retry ≤2 escalation flash-low→
  flash-high (đính lỗi cũ vào prompt), preflight model, check URL sống HEAD→GET,
  dedup URL chuẩn hoá, rank tất định (route → URL sống → quote → score), log ISO.
- `scripts/search_report_schema.json`: nguồn duy nhất luật URL + schema report
  (bắt buộc evidence_quote, source_url có path, score 0–10).
- Agent `agents/search-runner.md`: vỏ mỏng chạy script, trả JSON verbatim.
- Tầng search: `deep-search.md` (trigger ≥2 dấu hiệu, brief FULL data, fallback
  Tavily khi engine-failed ≥2), cập nhật `tavily.md`, tdq-intake B3, CLAUDE.md §10,
  `portable/workflow/06-deep-search.md`.
- Config: `.claude/settings.json` env TDQ_SEARCH_* (MAX_AGENTS=3 mặc định);
  plugin 0.5.0 + CHANGELOG.

## Kết quả QC (chi tiết: docs/tdq/qc/2026-07-31-agy-search-agent.md)
- Q1–Q8 PASS. Suite 326 test OK (41 test mới cho search_task). doc_lint + pair exit 0.
- E2E thật: 2 fact npm (typescript 7.0.2, claude-code 2.1.220) — merged.json khớp
  100% `npm view`, mọi URL sống; route không tìm được trả `not_found=true`, không bịa.
- Fail-path: slug sai 2 lần → engine-failed cả 2, chuyển Tavily + ghi "fallback tavily".
- Log service bật mặc định, `TDQ_SEARCH_LOG=0` tắt thật.

## Giới hạn / PENDING
- Trigger qua Agent tool: PASS (QC vòng 2, run `2026-07-31-trigger-test`). Bug
  "chờ notification giết background task" đã fix trong search-runner.md
  (watcher foreground) — hiệu lực từ phiên/reload kế tiếp.
- Nguồn redirect (vertexaisearch) của agy vẫn được nhận nếu URL sống — orchestrator
  nên spot-check nguồn top theo luật deep-search.md trước khi dùng.

## Cách dùng nhanh
1. Trigger đủ ≥2 dấu hiệu → viết brief FULL data thành file.
2. `python3 scripts/search_task.py split --routes "r1,r2,…"` → giao mỗi assignment
   cho 1 agent search-runner (sync).
3. `python3 scripts/search_task.py merge <run-dir>` → đọc merged.json + report.md,
   spot-check 1–2 nguồn top.
