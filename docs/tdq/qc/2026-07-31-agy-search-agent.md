# QC — 2026-07-31-agy-search-agent

Chạy 2026-07-31 15:10–15:25 (+07:00), mode main. DoD: spec §6.

| # | Hạng mục | Kết quả | Bằng chứng |
|---|---|---|---|
| Q1 | Unit suite toàn repo | PASS | `cd tests && python3 -m unittest discover .` → `Ran 326 tests … OK`; 41 test mới trong `test_search_task.py` (≥10) |
| Q2 | Doc lint + pair | PASS | `doc_lint.py --pair spec plan` → exit 0; `doc_lint.py` 7 file docs sửa (deep-search, tavily, tdq-intake, search-runner, portable ×3) → exit 0 |
| Q3 | E2E thật 2 fact npm | PASS | Run `2026-07-31-npm-versions`: split 2 route → 2 agent → merge. Ground truth `npm view`: typescript 7.0.2, @anthropic-ai/claude-code 2.1.220. Assert máy: "T81_OK: 4 findings, mọi fact khớp npm view, mọi URL sống". Agent 2 (route github) trả `not_found=true` — không bịa. Schema hợp lệ (script validate khi chạy) |
| Q4 | Cap agent + config | PASS | `MAX_AGENTS=1` → 1 agent nhận hết 3 route; `=3` với 4 route → đúng 3 agent round-robin; `=rác` → stderr "không hợp lệ … dùng default 3" + split như default. Unit `SplitTest` + `EnvTest` xanh |
| Q5 | Escalation + retry | PASS | Unit `RetryEscalationTest`: JSON hỏng → retry dùng `gemini-3.6-flash-high` + prompt chứa "## LỖI LẦN TRƯỚC"; 3 lần hỏng → exit 1 `engine-failed` |
| Q6 | Verbatim / engine-failed / fallback | PASS | Slug sai 2 lần liên tiếp → exit 3 + "⚠️ engine-failed (preflight): model slug không có trên máy: slug-khong-ton-tai" cả 2 lần, không bịa. Sau đó chuyển Tavily trả lời brief, report demo `research/search/2026-07-31-failpath-demo/report.md` có mục "fallback tavily". Verbatim: agent-1.json đọc nguyên văn qua wrapper |
| Q7 | Tầng search cập nhật đúng | PASS | tavily.md khai "Tavily = FAST tier, deep search mặc định = search-runner, fallback khi engine-failed ≥2"; deep-search.md có luật spot-check 1–2 nguồn top + fallback ≥2 engine-failed; CLAUDE.md §10 có dòng deep search qua search-runner + cap env; doc_lint R8 spec exit 0 |
| Q8 | Log service | PASS | `agent-1.log`/`run.log` run npm-versions: ISO timestamp + đủ trường (agent/agy/route/call/attempt/model/exit/findings/secs, dòng merge cuối). Run `2026-07-31-mini-run-nolog` với `TDQ_SEARCH_LOG=0` → không sinh agent-1.log |

## QC vòng 2 — trigger search-runner qua Agent tool (2026-07-31 15:25–15:35)

- Lần 1+2 FAIL: agent chạy wrapper `run_in_background` rồi kết thúc turn chờ
  notification → background task bị KILL (run-dir chỉ còn brief.md, không còn
  process agy). Lần 2 vẫn lỗi vì định nghĩa agent được cache từ đầu phiên.
- Fix QC2.1: `agents/search-runner.md` chuyển sang pattern tất định — wrapper nền
  ghi marker `agent-<k>.exit`, agent BẮT BUỘC chạy watcher foreground chặn turn
  đến khi marker xuất hiện. Có hiệu lực từ phiên/reload kế tiếp.
- Lần 3 PASS (SendMessage ép chạy foreground): run `2026-07-31-trigger-test` —
  agent trả JSON verbatim, exit 0, 2 findings score 10, URL sống, merge OK
  (`merged.json`: 1 finding sau dedup). Q3/Q6 đóng PENDING.

Kèm DoD: plugin.json `0.5.0` (grep OK) + CHANGELOG mục 0.5.0; settings.json project
env TDQ_SEARCH_* (assert json OK); report + working log + graphify ở T8.4.
