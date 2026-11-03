# PLAN — Hybrid deep search 0.6.0 (scout ∥ agy tổng quát → agy đào sâu)

Ngày: 2026-07-31 · Spec: ../spec/2026-07-31-hybrid-deep-search.md (bản 1.1, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — task đụng chung `search_task.py` + `deep-search.md`, phụ thuộc chặt; E2E phải spawn agent search từ hội thoại chính.
Trạng thái plan: HOÀN THÀNH (duyệt "duyệt plan mode main" 2026-07-31 16:45; build + QC xong 2026-07-31; token Q3 re-measure PENDING reload — QC1.2)

## Năng lực → task

| Skill | Task | Đầu ra bắt buộc |
|---|---|---|
| tavily-search | T5.1 | `agent-2.json` của scout có findings từ tavily-search, parse được |
| tavily-extract | T5.2 (+ luật scout lấy quote trong needles T2.1) | 2 dòng spot-check nguồn top ghi trong QC file |
| tavily-best-practices | T2.4 | mục luật scout trong `deep-search.md`, needles test xanh |
| graphify | T6.3 | code graph rebuild sau turn build (lệnh exit 0) |

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: viết test trước (đỏ) → code → test xanh → tick `[x]` NGAY vào file này.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — search_task.py: default model + start-agent (đầu ra #1, #2)
- [x] **T1.1** Test đỏ: default model là `gemini-3.6-flash-medium`, escalation giữ `gemini-3.6-flash-high`; cập nhật `RetryEscalationTest` khớp chain medium→high — Test: `cd tests && python3 -m unittest test_search_task -k DefaultModel -k RetryEscalation` FAIL trước khi sửa code
- [x] **T1.2** Đổi `DEFAULT_MODEL` thành flash-medium; đồng bộ docstring, USAGE và comment nội bộ (dòng ~136) — Test: 2 nhóm test ở T1.1 xanh; `grep -c "flash-low" scripts/search_task.py` = 0 trên TOÀN file
- [x] **T1.3** Test đỏ: `split --start-agent 3` với 3 route → agent 3,4,5; thiếu flag → 1,2,3; giá trị rác → exit 2 — Test: test mới trong `SplitTest` FAIL trước khi sửa
- [x] **T1.4** Thêm flag `--start-agent N` (default 1) cho `split`, cập nhật USAGE + docstring — Test: test T1.3 xanh; `python3 scripts/search_task.py` in USAGE chứa `--start-agent`

**Xong P1 khi**: `cd tests && python3 -m unittest test_search_task` OK, ≥4 test mới xanh.

## P2 — Agent scout + doc quy ước (đầu ra #3, #4)
- [x] **T2.1** Test đỏ `SearchScoutAgentTest`: needles khuôn agent scout — route `scout:`, ghi `agent-2.json` format file agent (url_alive/not_found/queries_used), final message 3–5 route gợi ý, luật dùng tavily-extract lấy quote khi cần, log `agent-2.log`, tôn trọng `TDQ_SEARCH_LOG=0` — Test: test mới FAIL khi chưa có file agent
- [x] **T2.2** Viết `agents/search-scout.md` (vỏ mỏng như search-runner) — Test: `SearchScoutAgentTest` xanh
- [x] **T2.3** Test đỏ needles mới trong `DeepSearchDocTest` cho flow hybrid: 2 phase, slot cố định 1/2 (ngoại lệ luật split), đọc-để-điều-phối vs merge-bằng-lệnh, `brief-phase2.md`, `--start-agent 3`, merge 1 lần cuối, 3 nhánh degrade + định nghĩa scout-failed, dòng degrade ghi vào report/`run.log` SAU merge (merge mở run.log mode "w" nên ghi trước là mất) — Test: needles FAIL trước khi viết lại doc
- [x] **T2.4** Viết lại `skills/tdq-conventions/references/deep-search.md` theo flow hybrid spec §3 — Test: needles T2.3 xanh
  - Dùng: `tavily-best-practices`
  - Nạp: gọi skill `tavily-best-practices` TRƯỚC bước viết luật scout của task này. Agent ngoài không có skill system: đọc SKILL.md của plugin tavily rồi làm theo.
  - Để: chốt luật query/số kết quả/extract cho scout trong deep-search.md đúng khuyến nghị Tavily.
  - Ra: mục luật scout trong `skills/tdq-conventions/references/deep-search.md`.
  - Kiểm: `cd tests && python3 -m unittest test_search_task -k DeepSearchDoc` OK.
  - Không dùng cho: viết luật agy/wrapper (phần đó theo code search_task.py, không theo Tavily).
- [x] **T2.5** doc_lint 2 file mới sửa — Test: `python3 scripts/doc_lint.py agents/search-scout.md skills/tdq-conventions/references/deep-search.md` exit 0

**Xong P2 khi**: suite OK; doc_lint exit 0.

## P3 — Docs khớp + version 0.6.0 (đầu ra #5, #6)
- [x] **T3.1** Cập nhật `skills/tdq-conventions/references/tavily.md`, `portable/workflow/06-deep-search.md`, CLAUDE.md §10 (1 dòng hybrid) — Test: test portable_sync + docs_consistency xanh; doc_lint các file sửa exit 0
- [x] **T3.2** Bump `.claude-plugin/plugin.json` + `CHANGELOG.md` lên 0.6.0 — Test: test changelog↔plugin.json xanh; `grep '"version": "0.6.0"' .claude-plugin/plugin.json` khớp

**Xong P3 khi**: suite OK, version 0.6.0 nhất quán.

## P4 — Log & test bắt buộc
- [x] **T4.1** Log service: run nháp 1 route với `TDQ_SEARCH_LOG=0` không sinh agent log (nửa âm của Q8; nửa dương đọc log run E2E ở T5.3) — Test: run nháp xong, không tồn tại `agent-*.log` mới
- [x] **T4.2** Toàn suite + lint cặp — Test: `cd tests && python3 -m unittest discover .` OK (≥332, có ≥6 test mới); `python3 scripts/doc_lint.py --pair docs/tdq/spec/2026-07-31-hybrid-deep-search.md docs/tdq/plan/2026-07-31-hybrid-deep-search.md` exit 0

**Xong P4 khi**: suite + lint xanh toàn bộ.

## P5 — E2E hybrid + QC (đầu ra #7; Q3, Q4, Q6, Q8-dương)
- [x] **T5.1** Chạy E2E hybrid 1 topic thật: phase 1 = agent 1 search-runner (route `tổng quát:`) ∥ agent 2 scout (general-purpose + đúng prompt thân search-scout.md — agent type mới PENDING reload); tổng hợp `brief-phase2.md`; phase 2 = `split --start-agent 3` → ≤3 search-runner; `merge` 1 lần — Test: mỗi loại slot ≥1 finding trong `agent-<k>.json` TRƯỚC merge (not_found → điều tra + rerun 1 lần, vẫn rỗng → FAIL); `merged.json` + `report.md` tồn tại
  - Dùng: `tavily-search`
  - Nạp: scout (agent 2) gọi tool MCP `tavily-primary` search TRƯỚC khi ghi findings; failover backup theo tavily.md.
  - Để: scout search rộng nắm hướng, sinh findings + 3–5 route gợi ý cho phase 2.
  - Ra: `docs/tdq/research/search/<run-id>/agent-2.json` + `agent-2.log`.
  - Kiểm: `python3 -c "import json;d=json.load(open('<run-dir>/agent-2.json'));assert d['findings']"` exit 0.
  - Không dùng cho: search của agent agy (slot 1, 3..5 — agy tự search qua wrapper).
- [x] **T5.2** QC Q3 phần còn lại: URL sống 100% trong `merged.json` — PASS = 2xx/3xx **hoặc 403/405** (đúng luật `url_alive` chấp nhận anti-bot); spot-check 2 nguồn top; token Claude từng agent (từ usage task-notification) ghi vào report, tổng ≤250k — Test: curl các URL đạt điều kiện trên; 2 dòng spot-check khớp nội dung nguồn; số token có trong report
  - Dùng: `tavily-extract`
  - Nạp: orchestrator gọi tool MCP `tavily-primary` extract khi spot-check, SAU khi merge xong.
  - Để: lấy nội dung 2 nguồn top đối chiếu quote/claim trong merged.json.
  - Ra: 2 dòng spot-check trong `docs/tdq/qc/2026-07-31-hybrid-deep-search.md`.
  - Kiểm: nội dung extract chứa ý đã claim (ghi PASS/FAIL kèm trích đoạn).
  - Không dùng cho: check URL sống hàng loạt (việc đó dùng curl như wrapper).
- [x] **T5.3** QC Q4 + Q8-dương: grep `agent-*.log` của run T5.1 — Test: mọi call attempt đầu dùng `gemini-3.6-flash-medium`; log đủ trường ISO timestamp
- [x] **T5.4** QC Q6a: run nháp giả lập agent 1 engine-failed (slug sai) — Test: flow vẫn ra route + kết quả từ scout; report hoặc `run.log` (ghi SAU merge) có 1 dòng degrade
- [x] **T5.5** Viết `docs/tdq/qc/2026-07-31-hybrid-deep-search.md` (Q1–Q8 + bằng chứng) và `docs/tdq/reports/2026-07-31-hybrid-deep-search.md` ≤50 dòng — Test: doc_lint 2 file exit 0; report ≤50 dòng

**Xong P5 khi**: Q1–Q8 PASS trong QC file, đầu ra #1–#7 có bằng chứng.

## QC vòng 1 — fix (token E2E 263.972 > 250k)
- [x] **QC1.1** Giảm token wrapper search-runner: frontmatter giới hạn `tools: Bash, Read` + contract trả TÓM TẮT (agent · exit · số findings · not_found · đường dẫn file) thay vì dán JSON nguyên văn — Test: needle test mới (không còn "verbatim", có tools restriction) red → green; suite xanh
- [x] **QC1.2** Ghi nhận đo lại token: vòng 1 = 263.972 (a1 67.637 · a2 79.448 · a3 38.360 · a4 39.185 · a5 39.342) FAIL; fix QC1.1 chỉ ăn ở phiên mới (agent def cache) → re-measure PENDING reload, tiền lệ 0.5.0 — Test: QC file có mục này kèm số liệu

## P6 — Đóng turn
- [x] **T6.1** Rà soát plan không còn `[ ]` sót (tick đã làm NGAY từng task theo quy tắc 2); cập nhật header plan trạng thái — Test: không còn `[ ]` ngoài task bị loại có ghi lý do
- [x] **T6.2** Append working log `docs/workinglog/2026-07-31.md` — Test: entry mới có timestamp + file đổi + kiểm đã chạy
- [x] **T6.3** Rebuild code graph — Test: `graphify extract . --code-only` exit 0
  - Dùng: `graphify`
  - Nạp: skill graphify đã cài mức user; chạy CLI trực tiếp cuối turn build.
  - Để: cập nhật knowledge graph sau khi code đổi (CLAUDE.md §10).
  - Ra: graph artifacts do graphify sinh (thư mục graphify của repo).
  - Kiểm: lệnh exit 0, không error trong output.
  - Không dùng cho: phân tích code thay cho việc đọc file trong các task trước.

## Definition of Done
Trỏ về §6 spec 1.1 — PASS đủ:
- Q1 suite: `cd tests && python3 -m unittest discover .` OK, ≥6 test mới (T1.1, T1.3, T2.1, T2.3).
- Q2 lint: doc_lint từng file sửa + `--pair spec plan` exit 0 (T2.5, T3.1, T4.2, T5.5).
- Q3 E2E: mỗi loại slot ≥1 finding trước merge, URL sống 100% (2xx/3xx/403/405), spot-check 2 nguồn, token ≤250k (T5.1, T5.2).
- Q4 default medium ở attempt đầu (T5.3) · Q5 escalation medium→high unit (T1.1).
- Q6 degrade: (a) run nháp T5.4; (b)(c) needles doc T2.3/T2.4.
- Q7 version 0.6.0 + portable khớp (T3.1, T3.2) · Q8 log service (T4.1 âm + T5.3 dương).
- Report ≤50 dòng, working log ghi đủ; trigger agent type `search-scout` PENDING reload (tiền lệ 0.5.0).
