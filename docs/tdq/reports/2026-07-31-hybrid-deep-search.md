# Report — Hybrid deep search 2 phase (tdq-workflow 0.6.0)

## Kết quả

- Flow deep search nâng cấp lên hybrid 2 phase: Phase 1 = agent 1 `search-runner`
  (agy, route `tổng quát:`) ∥ agent 2 `search-scout` (Claude + Tavily, route `scout:`);
  tổng hợp `brief-phase2.md` (`## Hướng từ phase 1`, ≤3 route); Phase 2 =
  `split --start-agent 3` → ≤3 agent agy đào sâu; `merge` 1 lần gộp findings cả 2 phase.
- Default model agy: `gemini-3.6-flash-medium`, escalation `flash-high` (≤2 retry).
- Mới: `agents/search-scout.md`; cờ `--start-agent K` cho `split`; rewrite
  `deep-search.md` (3 nhánh degrade, scout-failed, ghi degrade SAU merge); sync
  `tavily.md`, `portable/workflow/06-deep-search.md`, §10 CLAUDE.md; version 0.6.0.

## Bằng chứng chính

- Suite: 338 test OK (thêm 12: default model, escalation, start-agent, needle scout,
  needle deep-search hybrid, contract runner QC1.1).
- E2E thật (`docs/tdq/research/search/2026-07-31-vectordb-local-rag/`): 5 slot đều có
  findings trước merge (53/13/11/12/13) → merged 31 findings; URL sống 31/31;
  spot-check 2 nguồn top khớp nguyên văn (tigerdata benchmark, qdrant hybrid-queries).
- Degrade drill: agent 1 slug sai → `engine-failed (preflight)`, flow vẫn ra route +
  kết quả từ scout, dòng degrade ghi SAU merge trong `run.log`.
- Log service: `TDQ_SEARCH_LOG=0` không sinh log; log thật đủ trường ISO,
  attempt đầu 100% `gemini-3.6-flash-medium`.

## Token Claude E2E (usage từng agent)

| Agent | Vai | Token |
|---|---|---|
| 1 | search-runner agy (tổng quát) | 67.637 |
| 2 | scout Claude + Tavily | 79.448 |
| 3–5 | search-runner agy (đào sâu) | 38.360 · 39.185 · 39.342 |
| **Tổng** | (mốc Run A 93,1k / Run B 189,4k) | **263.972** |

- Tiêu chí ≤250k: **FAIL vòng 1** (vượt ~5,6%) → QC1.1 đã fix wrapper search-runner
  (`tools: Bash, Read` + trả tóm tắt thay vì dán JSON nguyên văn — hết đếm đôi).
  Agent def cache theo phiên → đo lại ở phiên mới (PENDING reload, tiền lệ 0.5.0).

## Hạn chế / việc còn lại

- Trigger agent type `search-scout` + đo lại token: PENDING reload phiên mới.
- Quy ước mới: không đặt dấu phẩy trong chuỗi route (wrapper tách theo `,`).
- QC chi tiết: `docs/tdq/qc/2026-07-31-hybrid-deep-search.md`.
