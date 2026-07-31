# QC — 2026-07-31-hybrid-deep-search (0.6.0)

Spec nguồn: `docs/tdq/spec/2026-07-31-hybrid-deep-search.md` §6. Run E2E:
`docs/tdq/research/search/2026-07-31-vectordb-local-rag/`.

| # | Hạng mục | Kết quả | Bằng chứng |
|---|---|---|---|
| Q1 | Unit suite | PASS | `python3 -m unittest discover -s tests` → `Ran 338 tests … OK` (326 → 338: 11 test mới của plan + 1 test QC1.1) |
| Q2 | Doc lint + pair | PASS | `doc_lint.py` từng file sửa + `--pair spec plan` exit 0 (chạy lại cuối turn build) |
| Q3 | E2E hybrid | PASS (token: vòng 1 FAIL → fix, xem dưới) | Slot trước merge: a1=53, a2=13, a3=11, a4=12, a5=13 findings, not_found=false cả 5; merge 1 lần → `merged.json` 31 findings + `report.md` |
| Q3-URL | URL sống 100% | PASS | curl 31/31 unique URL: 28×2xx/3xx, 2×403 (anti-bot, hợp lệ theo luật `url_alive`), 1×HEAD-404/GET-200 |
| Q3-spot | Spot-check 2 nguồn top | PASS | (1) tigerdata.com/blog/pgvector-vs-qdrant: extract chứa nguyên văn "Pgvectorscale took around 11.1 hours… Qdrant took only around 3.3 hours" + "1,589.79 QPS … 360.81 … 4.4" — khớp claim agent 3. (2) qdrant.tech/documentation/concepts/hybrid-queries/: extract chứa `fusion(Fusion.DBSF)` + `"query": { "rrf": {} }` + prefetch — khớp claim agent 5 |
| Q3-token | Tổng ≤250k | FAIL vòng 1 → fix QC1.1, re-measure PENDING reload | Vòng 1: a1=67.637 · a2=79.448 · a3=38.360 · a4=39.185 · a5=39.342 → tổng 263.972 (>250k ~5,6%). Nguyên nhân: wrapper search-runner nạp All-tools + dán JSON nguyên văn (đếm đôi). Fix: frontmatter `tools: Bash, Read` + contract trả tóm tắt. Agent def cache theo phiên → đo lại ở phiên mới (tiền lệ trigger 0.5.0) |
| Q4 | Default medium | PASS | grep `agent-{1,3,4,5}.log`: mọi dòng `attempt=1` đều `model=gemini-3.6-flash-medium` |
| Q5 | Escalation medium→high | PASS | unit `RetryEscalationTest` + `DefaultModelTest` xanh (trong 338); run thật không cần escalation (không có `flash-high` trong log) |
| Q6a | Degrade agent 1 hỏng | PASS | Drill scratchpad `2026-07-31-degrade-drill/`: agent 1 `--model` slug sai → exit 3 `engine-failed (preflight)`; scout mini 3 findings → merge OK → dòng degrade ghi SAU merge còn nguyên trong `run.log` |
| Q6bc | Doc 3 nhánh + scout-failed | PASS | Needles `DeepSearchDocTest.test_hybrid_flow_needles` xanh ("scout-failed", "cả hai hỏng", "SAU merge"…) |
| Q7 | Docs + version 0.6.0 | PASS | `docs_consistency` + `portable_sync` xanh trong suite; `plugin.json` version 0.6.0; CHANGELOG 0.6.0 |
| Q8 | Log service | PASS | Âm: drill `TDQ_SEARCH_LOG=0` không sinh `agent-*.log` (T4.1). Dương: log run E2E đủ trường, ISO timestamp (Q4 ở trên) |

## Ghi chú QC

- **Route chứa dấu phẩy**: route agent 1 phase 1 có dấu phẩy → wrapper `--routes` tách
  thành 3 route con. Vô hại (cả 3 chạy OK) nhưng quy ước mới: KHÔNG đặt dấu phẩy trong
  chuỗi route (phase 2 đã tuân thủ, dùng `+`/`:`).
- Drill Q6a dùng scout haiku cho rẻ; timestamp trong log drill của scout là tuần tự
  mô phỏng (chỉ drill, không phải run thật — log run E2E thật có timestamp thật).
- Trigger qua agent type `search-scout`: PENDING reload phiên mới (agent def cache),
  DoD cho phép — E2E dùng general-purpose + đúng prompt thân search-scout.md.
