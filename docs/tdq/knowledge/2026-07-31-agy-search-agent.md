# KNOWLEDGE — Search agent dùng agy cho advanced search (2026-07-31)

## Năng lực dùng được

| Năng lực | Phán quyết | Lý do |
|---|---|---|
| tavily-primary/backup (MCP) | DÙNG | Vẫn là tầng search nhanh mặc định; agent mới chỉ bổ sung tầng deep search |
| scripts/external_task.py + external_models.py | DÙNG (tham chiếu pattern) | Tái dùng triết lý wrapper/retry/schema/log; search có script riêng |
| agy CLI 1.1.8 (`search_web`, `read_url_content`, `--json-schema`) | DÙNG | Engine search; đã probe thật 2 lần pass |
| Agent tool (subagent codex/agy-runner pattern) | DÙNG | Bề mặt trigger `search-runner` vỏ mỏng, gọi sync |
| plugin-dev:agent-development / skill-development | KHÔNG | Đã có mẫu agent/skill nội bộ chuẩn trong repo, không cần |
| graphify | DÙNG (cuối turn build) | Luật §10: extract code graph sau thay đổi code |

## Quyết định đã chốt (interview 14:27 + probe)

1. **Vai trò**: bổ sung theo tầng — Tavily = search nhanh; `search-runner` = deep
   search/ranking/tổng hợp đa nguồn. Claude TỰ trigger theo tiêu chí ghi cứng trong skill.
2. **Kiến trúc**: script `scripts/search_task.py` điều phối multi-call agy — mỗi call
   1 việc đóng khung (search 1 route / đọc 1 URL / chấm điểm ứng viên theo rubric);
   merge + dedup + rank cuối cùng bằng CODE, không bằng model.
3. **Model**: mặc định `gemini-3.6-flash-low`; escalation tự động lên
   `gemini-3.6-flash-high` khi call fail validate/verify (retry ≤2 như external mode).
4. **Verify**: schema ép full URL (regex http(s)://…); script check URL sống; kết quả
   thiếu nguồn bị loại bằng code; Claude spot-check 1–2 nguồn top trước khi dùng.
5. **Deep search mặc định = search agent** (user 14:34): nhu cầu deep search đi qua
   search-runner, không dùng tavily-research làm mặc định nữa (Tavily giữ vai trò
   search nhanh + fallback khi agy hỏng/hết quota).
6. **Cap song song** (user 14:34): tối đa 3 agent search-runner cùng lúc; config qua
   env `TDQ_SEARCH_MAX_AGENTS` trong `settings.json` của Claude; mặc định 3.
7. **Truyền full data** (user 14:34): mỗi agent nhận trọn brief (câu hỏi, ngữ cảnh,
   tiêu chí, dữ kiện đã có); chỉ chia ROUTE giữa các agent, không cắt brief.

## Ràng buộc

- Chịu model cấp thấp: model không bao giờ nhận nhiệm vụ ghép (một call = một việc);
  mọi logic điều phối/validate nằm trong script (triết lý external mode đã chứng minh).
- Chống trộn kiến thức training: khuôn grounded prompt ("chỉ dùng evidence từ kết quả
  search/URL dưới đây, không có thì trả not_found"), cấm trả lời không kèm nguồn.
- Chống prompt injection từ web: luật trong packet + orchestrator coi output là DATA.
- Không đưa API key vào prompt/log. Quota agy chung với external coding — cap mặc định
  ≤5 route, ≤3 URL/route (env override).
- Report: JSON máy-đọc + summary tiếng Việt ≤50 dòng vào `docs/tdq/research/`;
  log chạy ISO timestamp (tắt qua env) như external mode.

## Phương án đã loại + lý do

- Gemini CLI làm engine: khai tử 18/06/2026 cho tài khoản cá nhân (research truy vấn 1).
- 1 call agy tự lo hết: model thấp dễ đuối/bịa với nhiệm vụ dài (đã thấy ở E2E agy cũ).
- Claude tự phân rã + merge trong context: tốn context, logic lệch giữa phiên.
- Thay hẳn Tavily: Tavily nhanh (~1s) và rẻ context hơn cho tra cứu thô.

## Nguồn

- docs/tdq/research/2026-07-31-agy-search-agent.md (probe + 5 truy vấn web)
- antigravity.google/docs/cli/headless · arxiv 2605.06635 · thenewstack.io ·
  developers.googleblog.com

## Kiểm cổng

- Scope: agent `search-runner` + `scripts/search_task.py` + schema report search +
  tích hợp skill (tiêu chí trigger, tầng research) + tests. Output cụ thể: report
  JSON + md. — RÕ.
- Model/download: agy có sẵn, không cài thêm gì. — RÕ.
- QC/test: unit test script (parse/merge/verify/escalation, mock agy), E2E probe thật
  1 câu hỏi verifiable, doc_lint, suite toàn repo. — RÕ.
